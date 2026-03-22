import { randomUUID } from 'node:crypto'
import { log } from '../shared/logger.ts'
import type { RunSummaryAction, Run, OutcomeRecord } from '../shared/types.ts'
import { queryOutcomes, appendOutcome } from '../server/services/outcome-store.ts'

export interface AutoActionResult {
  recorded: number
  skipped_dedup: number
  skipped_mode: boolean
  errors: string[]
}

/**
 * Record PR and Linear issue outcomes from a completed run into outcomes.yaml.
 *
 * AUTO-01: Records PR outcomes (pr_url present in RunSummaryAction)
 * AUTO-02: Records Linear issue outcomes (linear_url present in RunSummaryAction)
 * D-02: dry-run and self-repair modes produce NO outcome records
 * D-08: PR dedup — check outcomes.yaml + gh pr list for same branch
 * D-09: Linear dedup — check outcomes.yaml for existing open outcome with same signal+target
 * D-10: Dedup runs BEFORE recording, never create then check
 */
export async function recordRunOutcomes(
  run: Run,
  perTarget: Record<string, { actions: RunSummaryAction[] }>,
): Promise<AutoActionResult> {
  const result: AutoActionResult = { recorded: 0, skipped_dedup: 0, skipped_mode: false, errors: [] }

  // D-02: dry-run and self-repair modes do NOT record outcomes
  if (run.mode !== 'production') {
    result.skipped_mode = true
    log.info({ component: 'auto-action', msg: `Skipping outcome recording — mode is '${run.mode}'` })
    return result
  }

  for (const [targetName, targetData] of Object.entries(perTarget)) {
    for (const action of targetData.actions ?? []) {
      // Record PR outcome if pr_url present
      if (action.pr_url) {
        try {
          const isDup = await isDuplicate(action.signal_id, targetName, 'pr', action.branch)
          if (isDup) {
            result.skipped_dedup++
            log.info({
              component: 'auto-action',
              msg: `Skipping PR outcome — duplicate for signal ${action.signal_id} on target ${targetName}`,
            })
          } else {
            const record: OutcomeRecord = {
              id: randomUUID(),
              type: 'pr',
              target: targetName,
              signal_id: action.signal_id,
              run_id: run.id,
              url: action.pr_url,
              branch: action.branch,
              status: 'open',
              created_at: new Date().toISOString(),
            }
            await appendOutcome(record)
            result.recorded++
          }
        } catch (err) {
          const msg = `Failed to record PR outcome for signal ${action.signal_id}: ${String(err)}`
          result.errors.push(msg)
          log.warn({ component: 'auto-action', msg })
        }
      }

      // Record Linear issue outcome if linear_url present
      if (action.linear_url) {
        try {
          const isDup = await isDuplicate(action.signal_id, targetName, 'linear_issue')
          if (isDup) {
            result.skipped_dedup++
            log.info({
              component: 'auto-action',
              msg: `Skipping Linear outcome — duplicate for signal ${action.signal_id} on target ${targetName}`,
            })
          } else {
            const record: OutcomeRecord = {
              id: randomUUID(),
              type: 'linear_issue',
              target: targetName,
              signal_id: action.signal_id,
              run_id: run.id,
              url: action.linear_url,
              status: 'open',
              created_at: new Date().toISOString(),
            }
            await appendOutcome(record)
            result.recorded++
          }
        } catch (err) {
          const msg = `Failed to record Linear outcome for signal ${action.signal_id}: ${String(err)}`
          result.errors.push(msg)
          log.warn({ component: 'auto-action', msg })
        }
      }
    }
  }

  log.info({
    component: 'auto-action',
    msg: `Outcome recording complete: ${result.recorded} recorded, ${result.skipped_dedup} skipped (dedup)`,
  })
  return result
}

/**
 * D-08/D-09: Check if an outcome already exists to prevent duplicates.
 * D-10: Dedup runs BEFORE create.
 *
 * For PRs: checks outcomes.yaml for existing open outcome with same signal+target+type.
 *          Secondary: checks gh pr list --head {branch} for externally-created PRs.
 * For Linear: checks outcomes.yaml only (no external API).
 */
async function isDuplicate(
  signalId: string,
  target: string,
  type: 'pr' | 'linear_issue',
  branch?: string,
): Promise<boolean> {
  // Primary check: outcomes.yaml for existing open outcome with same signal+target+type
  const existing = await queryOutcomes({ target, type, status: 'open' })
  if (existing.some(o => o.signal_id === signalId)) return true

  // D-08 secondary: for PRs with a branch, check GitHub for externally-created PRs on same branch
  if (type === 'pr' && branch) {
    try {
      const proc = Bun.spawn(['gh', 'pr', 'list', '--head', branch, '--json', 'url', '--limit', '1'], {
        stdout: 'pipe',
        stderr: 'pipe',
      })
      const stdout = await new Response(proc.stdout).text()
      await proc.exited
      if (proc.exitCode === 0) {
        const prs = JSON.parse(stdout) as Array<{ url: string }>
        if (prs.length > 0) return true  // PR already exists on this branch
      }
    } catch {
      // gh CLI unavailable — fall through to outcomes-only dedup
    }
  }

  return false
}
