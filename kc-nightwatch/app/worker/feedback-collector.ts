import { log } from '../shared/logger.ts'
import type { FeedbackEntry, RunSummaryAction } from '../shared/types.ts'

interface CollectionResult {
  entries: FeedbackEntry[]
  errors: string[]
}

/**
 * Collect implicit feedback by checking PR merge status via gh CLI.
 * Called before each run to update feedback for previously-acted signals.
 */
export async function collectImplicitFeedback(
  actions: Array<{ action: RunSummaryAction; target: string; run_id: string }>,
  appendFn: (entry: FeedbackEntry) => Promise<void>
): Promise<CollectionResult> {
  const result: CollectionResult = { entries: [], errors: [] }

  for (const { action, target, run_id } of actions) {
    if (!action.pr_url) continue

    try {
      const prStatus = await checkPrStatus(action.pr_url)
      if (!prStatus) continue // Still open or unknown

      const entry: FeedbackEntry = {
        signal_id: action.signal_id,
        target,
        run_id,
        verdict: prStatus,
        source: 'pr_status',
        submitted_at: new Date().toISOString(),
      }

      await appendFn(entry)
      result.entries.push(entry)
      log.info({
        component: 'feedback-collector',
        msg: `PR feedback: ${action.pr_url} = ${prStatus}`,
      })
    } catch (err) {
      result.errors.push(`Failed to check ${action.pr_url}: ${String(err)}`)
      log.warn({
        component: 'feedback-collector',
        msg: `PR check failed: ${action.pr_url} — ${String(err)}`,
      })
    }
  }

  return result
}

/**
 * Check PR status via gh CLI.
 * Returns 'accepted' if merged, 'rejected' if closed without merge, null if still open.
 */
export async function checkPrStatus(prUrl: string): Promise<'accepted' | 'rejected' | null> {
  try {
    // Extract owner/repo and PR number from URL
    // Format: https://github.com/owner/repo/pull/123
    const match = prUrl.match(/github\.com\/([^/]+\/[^/]+)\/pull\/(\d+)/)
    if (!match) return null

    const [, repo, prNumber] = match

    const proc = Bun.spawn(['gh', 'pr', 'view', prNumber!, '--repo', repo!, '--json', 'state,mergedAt'], {
      stdout: 'pipe',
      stderr: 'pipe',
    })

    const stdout = await new Response(proc.stdout).text()
    await proc.exited

    if (proc.exitCode !== 0) return null

    const data = JSON.parse(stdout) as { state: string; mergedAt: string | null }

    if (data.state === 'MERGED' || data.mergedAt) return 'accepted'
    if (data.state === 'CLOSED') return 'rejected'
    return null // Still OPEN
  } catch {
    return null
  }
}

/**
 * Check Linear issue status.
 * For Phase 3, this is a placeholder. Full Linear MCP integration deferred to Phase 4.
 * Returns null (unresolved) for now — can be wired to Linear MCP when available.
 */
export async function checkLinearStatus(_issueUrl: string): Promise<'accepted' | 'rejected' | null> {
  // Phase 3 placeholder — Linear MCP integration in Phase 4
  return null
}
