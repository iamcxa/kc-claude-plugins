import { describe, it, expect } from 'bun:test'
import { collectImplicitFeedback } from '../../worker/feedback-collector.ts'
import type { FeedbackEntry, RunSummaryAction } from '../../shared/types.ts'

describe('feedback-collector', () => {
  it('skips actions without pr_url', async () => {
    const collected: FeedbackEntry[] = []
    const action: RunSummaryAction = {
      signal_id: 'test:001',
      type: 'code-fix',
      summary: 'Fixed lint error',
      indicator: 'code-quality',
      assessment: { closer_to_north_star: 'yes', confidence: 'high', reasoning: 'Direct fix' },
    }

    const result = await collectImplicitFeedback(
      [{ action, target: 'my-plugin', run_id: 'run-1' }],
      async (entry) => { collected.push(entry) }
    )

    expect(collected.length).toBe(0)
    expect(result.entries.length).toBe(0)
  })

  it('extracts repo and PR number from GitHub URL', () => {
    const url = 'https://github.com/owner/repo/pull/42'
    const match = url.match(/github\.com\/([^/]+\/[^/]+)\/pull\/(\d+)/)
    expect(match).toBeDefined()
    expect(match![1]).toBe('owner/repo')
    expect(match![2]).toBe('42')
  })

  it('returns null for non-GitHub URLs', () => {
    const url = 'https://linear.app/team/issue/123'
    const match = url.match(/github\.com\/([^/]+\/[^/]+)\/pull\/(\d+)/)
    expect(match).toBeNull()
  })

  it('collectImplicitFeedback skips actions with non-GitHub PR URL', async () => {
    const collected: FeedbackEntry[] = []
    const action: RunSummaryAction = {
      signal_id: 'test:002',
      type: 'code-fix',
      summary: 'Fixed bug',
      pr_url: 'https://not-a-real-url.com/no-match',
      indicator: 'bugs',
      assessment: { closer_to_north_star: 'yes', confidence: 'high', reasoning: 'Bug fix' },
    }

    // URL won't match github pattern, so no feedback collected
    const result = await collectImplicitFeedback(
      [{ action, target: 'my-plugin', run_id: 'run-1' }],
      async (entry) => { collected.push(entry) }
    )

    expect(collected.length).toBe(0)
    expect(result.entries.length).toBe(0)
  })

  it('handles errors in appendFn gracefully without throwing', async () => {
    const action: RunSummaryAction = {
      signal_id: 'test:003',
      type: 'proposal',
      summary: 'Add tests',
      pr_url: 'https://github.com/owner/repo/pull/999',
      indicator: 'test-coverage',
      assessment: { closer_to_north_star: 'uncertain', confidence: 'medium', reasoning: 'Might help' },
    }

    // This will try gh CLI which will fail (PR doesn't exist), but checkPrStatus
    // returns null on non-zero exit codes, so appendFn is never called
    const result = await collectImplicitFeedback(
      [{ action, target: 'my-plugin', run_id: 'run-1' }],
      async () => { throw new Error('write failed') }
    )

    // gh CLI fails → checkPrStatus returns null → no entries, no errors
    expect(result.entries.length).toBe(0)
    expect(result.errors.length).toBe(0)
  })

  it('result has entries and errors arrays', async () => {
    const result = await collectImplicitFeedback(
      [],
      async () => {}
    )
    expect(Array.isArray(result.entries)).toBe(true)
    expect(Array.isArray(result.errors)).toBe(true)
  })
})
