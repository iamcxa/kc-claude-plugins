import path from 'node:path'
import os from 'node:os'
import { readYamlFile, writeYamlFile } from './yaml-store.ts'
import { log } from '../../shared/logger.ts'
import type { FeedbackEntry, CalibrationData } from '../../shared/types.ts'

export const FEEDBACK_YAML_PATH = path.join(os.homedir(), '.claude/kc-plugins-config/nightwatch-feedback.yaml')

interface FeedbackStore {
  explicit_feedback?: FeedbackEntry[]
  pr_feedback?: FeedbackEntry[]
  linear_feedback?: FeedbackEntry[]
  slack_feedback?: FeedbackEntry[]
  pr_review_feedback?: FeedbackEntry[]
}

export async function appendFeedback(entry: FeedbackEntry): Promise<void> {
  const data = await readYamlFile<FeedbackStore>(FEEDBACK_YAML_PATH) ?? {}
  const key = entry.source === 'user' ? 'explicit_feedback'
    : entry.source === 'pr_status' ? 'pr_feedback'
    : entry.source === 'linear_status' ? 'linear_feedback'
    : entry.source === 'slack_reaction' ? 'slack_feedback'
    : entry.source === 'pr_review' ? 'pr_review_feedback'
    : 'linear_feedback'  // fallback
  if (!data[key]) data[key] = []
  data[key]!.push(entry)
  await writeYamlFile(FEEDBACK_YAML_PATH, data)
  log.info({ component: 'feedback', msg: `Feedback appended: ${entry.signal_id} = ${entry.verdict} (${entry.source})` })
}

export async function getFeedbackForRun(runId: string): Promise<FeedbackEntry[]> {
  const data = await readYamlFile<FeedbackStore>(FEEDBACK_YAML_PATH) ?? {}
  const all = [
    ...(data.explicit_feedback ?? []),
    ...(data.pr_feedback ?? []),
    ...(data.linear_feedback ?? []),
    ...(data.slack_feedback ?? []),
    ...(data.pr_review_feedback ?? []),
  ]
  return all.filter(f => f.run_id === runId)
}

export async function getFeedbackForSignal(signalId: string): Promise<FeedbackEntry[]> {
  const data = await readYamlFile<FeedbackStore>(FEEDBACK_YAML_PATH) ?? {}
  const all = [
    ...(data.explicit_feedback ?? []),
    ...(data.pr_feedback ?? []),
    ...(data.linear_feedback ?? []),
    ...(data.slack_feedback ?? []),
    ...(data.pr_review_feedback ?? []),
  ]
  return all.filter(f => f.signal_id === signalId)
}

const MIN_FEEDBACK_FOR_THRESHOLD = 10
const ALPHA = 0.3  // hardcoded per D-05
const HISTORY_WINDOW = 30  // cap at 30 runs per D-01 — used in slice(-30) below

/**
 * Build per-run reject rate history for a given indicator.
 * Only includes runs where the indicator had feedback.
 */
function buildHistory(
  sortedRunIds: string[],
  runByIndicator: Map<string, Map<string, { total: number; rejected: number }>>,
  indicator: string,
): number[] {
  const history: number[] = []
  for (const runId of sortedRunIds) {
    const runCounts = runByIndicator.get(runId)
    if (!runCounts) continue
    const counts = runCounts.get(indicator)
    if (!counts || counts.total === 0) continue
    history.push(Math.round((counts.rejected / counts.total) * 100) / 100)
  }
  return history
}

export async function getCalibrationData(): Promise<CalibrationData[]> {
  const data = await readYamlFile<FeedbackStore>(FEEDBACK_YAML_PATH) ?? {}
  const all = [
    ...(data.explicit_feedback ?? []),
    ...(data.pr_feedback ?? []),
    ...(data.linear_feedback ?? []),
    ...(data.slack_feedback ?? []),
    ...(data.pr_review_feedback ?? []),
  ]

  // Skip entries with empty/falsy run_id (defensive)
  const valid: typeof all = []
  for (const entry of all) {
    if (!entry.run_id) {
      log.warn({ component: 'feedback', msg: `Skipping malformed feedback entry (missing run_id): ${entry.signal_id}` })
      continue
    }
    valid.push(entry)
  }

  // Build run timestamps: run_id → earliest submitted_at
  const runTimestamps = new Map<string, string>()
  for (const entry of valid) {
    const existing = runTimestamps.get(entry.run_id)
    if (!existing || entry.submitted_at < existing) {
      runTimestamps.set(entry.run_id, entry.submitted_at)
    }
  }

  // Sort run_ids chronologically, take last 30 (D-01)
  const sortedRunIds = Array.from(runTimestamps.entries())
    .sort((a, b) => a[1].localeCompare(b[1]))
    .map(([runId]) => runId)
    .slice(-30)  // HISTORY_WINDOW = 30 cap per D-01

  // Build per-run per-indicator counts
  // runByIndicator: Map<run_id, Map<indicator, {total, rejected}>>
  const runByIndicator = new Map<string, Map<string, { total: number; rejected: number }>>()
  for (const entry of valid) {
    const indicator = entry.signal_id.split(':')[0] ?? entry.target
    if (!runByIndicator.has(entry.run_id)) {
      runByIndicator.set(entry.run_id, new Map())
    }
    const runMap = runByIndicator.get(entry.run_id)!
    const current = runMap.get(indicator) ?? { total: 0, rejected: 0 }
    current.total++
    if (entry.verdict === 'rejected') current.rejected++
    runMap.set(indicator, current)
  }

  // Build all-time per-indicator totals
  const indicatorAllTime = new Map<string, { total: number; rejected: number }>()
  for (const entry of valid) {
    const indicator = entry.signal_id.split(':')[0] ?? entry.target
    const current = indicatorAllTime.get(indicator) ?? { total: 0, rejected: 0 }
    current.total++
    if (entry.verdict === 'rejected') current.rejected++
    indicatorAllTime.set(indicator, current)
  }

  const results: CalibrationData[] = []
  for (const [indicator, { total, rejected }] of indicatorAllTime) {
    const rejectRate = total > 0 ? rejected / total : 0
    const history = buildHistory(sortedRunIds, runByIndicator, indicator)

    if (total < MIN_FEEDBACK_FOR_THRESHOLD) {
      // D-04: minimum N gate — not enough data for reliable threshold
      results.push({
        indicator,
        total_feedback: total,
        reject_count: rejected,
        reject_rate: Math.round(rejectRate * 100) / 100,
        current_threshold: null,
        threshold_null_reason: `Accumulating data (${total}/10)`,
        history,
      })
    } else {
      // D-03: EMA threshold — compute over per-run rate history
      // D-05: alpha=0.3, starting value 0.5
      let emaThreshold = 0.5
      for (const rate of history) {
        emaThreshold = ALPHA * rate + (1 - ALPHA) * emaThreshold
      }
      // D-06: clamp to [0.1, 0.9]
      const clampedThreshold = Math.round(Math.min(0.9, Math.max(0.1, emaThreshold)) * 100) / 100

      results.push({
        indicator,
        total_feedback: total,
        reject_count: rejected,
        reject_rate: Math.round(rejectRate * 100) / 100,
        current_threshold: clampedThreshold,
        history,
      })
    }
  }

  return results
}

export async function writeFeedbackTrends(targetName: string, journalDir: string): Promise<void> {
  const calibration = await getCalibrationData()
  const targetCalibration = calibration.filter(c =>
    c.indicator.toLowerCase().includes(targetName.toLowerCase()) || c.total_feedback > 0
  )
  if (targetCalibration.length === 0) return

  const trendsPath = path.join(journalDir, 'feedback-trends.md')
  const lines = [
    `# Feedback Trends (${new Date().toISOString().split('T')[0]})`,
    '',
    '| Indicator | Total | Rejected | Reject Rate | Threshold |',
    '|-----------|-------|----------|-------------|-----------|',
    ...targetCalibration.map(c =>
      `| ${c.indicator} | ${c.total_feedback} | ${c.reject_count} | ${(c.reject_rate * 100).toFixed(0)}% | ${c.current_threshold !== null ? (c.current_threshold * 100).toFixed(0) + '%' : 'N/A'} |`
    ),
    '',
  ]
  await Bun.write(trendsPath, lines.join('\n'))
  log.info({ component: 'feedback', msg: `Feedback trends written to ${trendsPath}` })
}
