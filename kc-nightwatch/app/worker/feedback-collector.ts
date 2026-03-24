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
 * Parse review verdict from a list of GitHub reviews.
 * Pure function — no I/O, easy to test.
 *
 * Rules:
 *   D-17: Latest review per reviewer wins (deduplicate by submittedAt)
 *   D-03: CHANGES_REQUESTED from any reviewer overrides all others → 'rejected'
 *         APPROVED beats COMMENTED → 'accepted'
 *         COMMENTED with no APPROVED → 'uncertain'
 *         DISMISSED is skipped (not counted)
 */
export function parseReviewVerdict(
  reviews: Array<{ author: { login: string }; state: string; submittedAt: string }>
): 'accepted' | 'rejected' | 'uncertain' | null {
  if (!reviews.length) return null

  // D-17: Latest review per reviewer
  const byReviewer = new Map<string, { state: string; submittedAt: string }>()
  for (const r of reviews) {
    const existing = byReviewer.get(r.author.login)
    if (!existing || r.submittedAt > existing.submittedAt) {
      byReviewer.set(r.author.login, r)
    }
  }

  // D-03: Cross-reviewer aggregation — CHANGES_REQUESTED wins (strongest signal)
  let verdict: 'accepted' | 'rejected' | 'uncertain' | null = null
  for (const { state } of byReviewer.values()) {
    if (state === 'CHANGES_REQUESTED') return 'rejected'
    if (state === 'APPROVED') verdict = 'accepted'
    else if (state === 'COMMENTED' && verdict === null) verdict = 'uncertain'
    // DISMISSED: skip (not counted)
  }
  return verdict
}

/**
 * Fetch PR reviews from GitHub via gh CLI and return a verdict.
 * Returns null for non-GitHub URLs, CLI errors, or no actionable reviews.
 */
export async function checkPrReviews(
  prUrl: string
): Promise<'accepted' | 'rejected' | 'uncertain' | null> {
  try {
    const match = prUrl.match(/github\.com\/([^/]+\/[^/]+)\/pull\/(\d+)/)
    if (!match) return null
    const [, repo, prNumber] = match

    const proc = Bun.spawn(
      ['gh', 'pr', 'view', prNumber!, '--repo', repo!, '--json', 'reviews'],
      { stdout: 'pipe', stderr: 'pipe' }
    )
    const stdout = await new Response(proc.stdout).text()
    await proc.exited
    if (proc.exitCode !== 0) return null

    const data = JSON.parse(stdout) as {
      reviews: Array<{ author: { login: string }; state: string; submittedAt: string }>
    }
    return parseReviewVerdict(data.reviews)
  } catch {
    return null
  }
}

/**
 * Collect PR review feedback for a set of actions with PR URLs.
 * Mirrors collectImplicitFeedback signature (fire-and-forget, never throws).
 * Source is 'pr_review'; verdict is the 3-state result from parseReviewVerdict.
 */
export async function collectPrReviewFeedback(
  actions: Array<{ action: RunSummaryAction; target: string; run_id: string }>,
  appendFn: (entry: FeedbackEntry) => Promise<void>
): Promise<CollectionResult> {
  const result: CollectionResult = { entries: [], errors: [] }

  for (const { action, target, run_id } of actions) {
    if (!action.pr_url) continue

    try {
      const reviewVerdict = await checkPrReviews(action.pr_url)
      if (!reviewVerdict) continue

      const entry: FeedbackEntry = {
        signal_id: action.signal_id,
        target,
        run_id,
        verdict: reviewVerdict,
        source: 'pr_review',
        submitted_at: new Date().toISOString(),
      }

      await appendFn(entry)
      result.entries.push(entry)
      log.info({
        component: 'feedback-collector',
        msg: `PR review feedback: ${action.pr_url} = ${reviewVerdict}`,
      })
    } catch (err) {
      result.errors.push(`Failed to check reviews for ${action.pr_url}: ${String(err)}`)
      log.warn({
        component: 'feedback-collector',
        msg: `PR review check failed: ${action.pr_url} — ${String(err)}`,
      })
    }
  }

  return result
}

/**
 * Check Linear issue status via GraphQL API.
 * Replaces Phase 3 placeholder with real implementation.
 * Returns null if no LINEAR_API_KEY, invalid URL, or issue still in progress.
 */
export async function checkLinearStatus(issueUrl: string): Promise<'accepted' | 'rejected' | null> {
  const apiKey = process.env.LINEAR_API_KEY
  if (!apiKey) return null  // graceful skip — no API key configured

  // Extract issue identifier from Linear URL
  // Format: https://linear.app/{team}/issue/{ID} (e.g., linear.app/team/issue/SC-123)
  const match = issueUrl.match(/linear\.app\/[^/]+\/issue\/([A-Z]+-\d+)/)
  if (!match) return null

  const issueId = match[1]
  const query = `{ issue(id: "${issueId}") { state { type } } }`

  try {
    const res = await fetch('https://api.linear.app/graphql', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': apiKey,  // NOTE: Linear personal API keys do NOT use Bearer prefix
      },
      body: JSON.stringify({ query }),
    })
    const data = await res.json() as { data?: { issue?: { state?: { type?: string } } } }
    const stateType = data?.data?.issue?.state?.type
    if (stateType === 'completed') return 'accepted'
    if (stateType === 'cancelled') return 'rejected'
    return null  // started, triage, backlog, unstarted = still in progress
  } catch {
    return null
  }
}
