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
}

export async function appendFeedback(entry: FeedbackEntry): Promise<void> {
  const data = await readYamlFile<FeedbackStore>(FEEDBACK_YAML_PATH) ?? {}
  const key = entry.source === 'user' ? 'explicit_feedback'
    : entry.source === 'pr_status' ? 'pr_feedback'
    : 'linear_feedback'
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
  ]
  return all.filter(f => f.run_id === runId)
}

export async function getFeedbackForSignal(signalId: string): Promise<FeedbackEntry[]> {
  const data = await readYamlFile<FeedbackStore>(FEEDBACK_YAML_PATH) ?? {}
  const all = [
    ...(data.explicit_feedback ?? []),
    ...(data.pr_feedback ?? []),
    ...(data.linear_feedback ?? []),
  ]
  return all.filter(f => f.signal_id === signalId)
}

export async function getCalibrationData(): Promise<CalibrationData[]> {
  const data = await readYamlFile<FeedbackStore>(FEEDBACK_YAML_PATH) ?? {}
  const all = [
    ...(data.explicit_feedback ?? []),
    ...(data.pr_feedback ?? []),
    ...(data.linear_feedback ?? []),
  ]

  // Group by indicator (derived from signal_id pattern: "indicator-name:signal-type")
  const byIndicator = new Map<string, { total: number; rejected: number }>()

  for (const entry of all) {
    // Extract indicator from signal_id (format: "indicator-name:..." or use target as fallback)
    const indicator = entry.signal_id.split(':')[0] ?? entry.target
    const current = byIndicator.get(indicator) ?? { total: 0, rejected: 0 }
    current.total++
    if (entry.verdict === 'rejected') current.rejected++
    byIndicator.set(indicator, current)
  }

  const results: CalibrationData[] = []
  for (const [indicator, { total, rejected }] of byIndicator) {
    const rejectRate = total > 0 ? rejected / total : 0
    // Threshold: start at 0.5, adjust based on reject rate
    // High reject rate (>0.7) → raise threshold (be more selective)
    // Low reject rate (<0.3) → lower threshold (accept more signals)
    const currentThreshold = Math.min(0.9, Math.max(0.1, 0.5 + (rejectRate - 0.5) * 0.5))
    results.push({
      indicator,
      total_feedback: total,
      reject_count: rejected,
      reject_rate: Math.round(rejectRate * 100) / 100,
      current_threshold: Math.round(currentThreshold * 100) / 100,
    })
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
      `| ${c.indicator} | ${c.total_feedback} | ${c.reject_count} | ${(c.reject_rate * 100).toFixed(0)}% | ${(c.current_threshold * 100).toFixed(0)}% |`
    ),
    '',
  ]
  await Bun.write(trendsPath, lines.join('\n'))
  log.info({ component: 'feedback', msg: `Feedback trends written to ${trendsPath}` })
}
