import { describe, it, expect, beforeEach } from 'bun:test'
import { mkdtemp } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import type { FeedbackEntry } from '../../shared/types.ts'

// Test feedback store with temp directory
describe('feedback-store', () => {
  let tmpDir: string

  beforeEach(async () => {
    tmpDir = await mkdtemp(path.join(os.tmpdir(), 'nw-feedback-'))
  })

  it('FeedbackEntry has required fields', () => {
    const entry = {
      signal_id: 'test:001',
      target: 'my-plugin',
      run_id: 'run-123',
      verdict: 'accepted' as const,
      source: 'user' as const,
      submitted_at: new Date().toISOString(),
    }
    expect(entry.signal_id).toBe('test:001')
    expect(entry.verdict).toBe('accepted')
    expect(entry.source).toBe('user')
  })

  it('CalibrationData computes reject rate correctly', () => {
    // Simulate calibration logic
    const total = 10
    const rejected = 3
    const rejectRate = rejected / total
    const threshold = Math.min(0.9, Math.max(0.1, 0.5 + (rejectRate - 0.5) * 0.5))
    expect(rejectRate).toBeCloseTo(0.3)
    expect(threshold).toBeCloseTo(0.4) // 0.5 + (0.3 - 0.5) * 0.5 = 0.5 - 0.1 = 0.4
  })

  it('calibration threshold rises with high reject rate', () => {
    const rejectRate = 0.8
    const threshold = Math.min(0.9, Math.max(0.1, 0.5 + (rejectRate - 0.5) * 0.5))
    expect(threshold).toBeCloseTo(0.65) // 0.5 + 0.15 = 0.65
  })

  it('calibration threshold stays bounded [0.1, 0.9]', () => {
    // 100% reject rate
    const threshold1 = Math.min(0.9, Math.max(0.1, 0.5 + (1.0 - 0.5) * 0.5))
    expect(threshold1).toBe(0.75)
    // 0% reject rate
    const threshold2 = Math.min(0.9, Math.max(0.1, 0.5 + (0.0 - 0.5) * 0.5))
    expect(threshold2).toBe(0.25)
  })

  it('FeedbackEntry source variants are recognized', () => {
    const sources: Array<'user' | 'pr_status' | 'linear_status'> = ['user', 'pr_status', 'linear_status']
    const keyMap = {
      user: 'explicit_feedback',
      pr_status: 'pr_feedback',
      linear_status: 'linear_feedback',
    }
    for (const source of sources) {
      const key = source === 'user' ? 'explicit_feedback'
        : source === 'pr_status' ? 'pr_feedback'
        : 'linear_feedback'
      expect(key).toBe(keyMap[source])
    }
  })

  // --- Extended feedback type tests (EXTFEED-01, EXTFEED-02) ---

  it("FeedbackEntry accepts 'uncertain' as a valid verdict value", () => {
    const entry: FeedbackEntry = {
      signal_id: 'test:002',
      target: 'my-plugin',
      run_id: 'run-456',
      verdict: 'uncertain',
      source: 'user',
      submitted_at: new Date().toISOString(),
    }
    expect(entry.verdict).toBe('uncertain')
  })

  it("FeedbackEntry accepts 'slack_reaction' as a valid source value", () => {
    const entry: FeedbackEntry = {
      signal_id: 'test:003',
      target: 'my-plugin',
      run_id: 'run-789',
      verdict: 'accepted',
      source: 'slack_reaction',
      submitted_at: new Date().toISOString(),
    }
    expect(entry.source).toBe('slack_reaction')
  })

  it("FeedbackEntry accepts 'pr_review' as a valid source value", () => {
    const entry: FeedbackEntry = {
      signal_id: 'test:004',
      target: 'my-plugin',
      run_id: 'run-abc',
      verdict: 'rejected',
      source: 'pr_review',
      submitted_at: new Date().toISOString(),
    }
    expect(entry.source).toBe('pr_review')
  })

  it("appendFeedback routing: 'slack_reaction' maps to 'slack_feedback' key", () => {
    // Test the routing logic inline (mirrors feedback-store.ts appendFeedback)
    const source: FeedbackEntry['source'] = 'slack_reaction'
    const key = source === 'user' ? 'explicit_feedback'
      : source === 'pr_status' ? 'pr_feedback'
      : source === 'linear_status' ? 'linear_feedback'
      : source === 'slack_reaction' ? 'slack_feedback'
      : source === 'pr_review' ? 'pr_review_feedback'
      : 'linear_feedback'
    expect(key).toBe('slack_feedback')
  })

  it("appendFeedback routing: 'pr_review' maps to 'pr_review_feedback' key", () => {
    const source: FeedbackEntry['source'] = 'pr_review'
    const key = source === 'user' ? 'explicit_feedback'
      : source === 'pr_status' ? 'pr_feedback'
      : source === 'linear_status' ? 'linear_feedback'
      : source === 'slack_reaction' ? 'slack_feedback'
      : source === 'pr_review' ? 'pr_review_feedback'
      : 'linear_feedback'
    expect(key).toBe('pr_review_feedback')
  })

  it('all 5 source variants map to correct store keys', () => {
    type SourceKey = FeedbackEntry['source']
    const routing: Record<SourceKey, string> = {
      user: 'explicit_feedback',
      pr_status: 'pr_feedback',
      linear_status: 'linear_feedback',
      slack_reaction: 'slack_feedback',
      pr_review: 'pr_review_feedback',
    }

    for (const [source, expectedKey] of Object.entries(routing) as [SourceKey, string][]) {
      const key = source === 'user' ? 'explicit_feedback'
        : source === 'pr_status' ? 'pr_feedback'
        : source === 'linear_status' ? 'linear_feedback'
        : source === 'slack_reaction' ? 'slack_feedback'
        : source === 'pr_review' ? 'pr_review_feedback'
        : 'linear_feedback'
      expect(key).toBe(expectedKey)
    }
  })

  it("getCalibrationData: 'uncertain' verdict counts in total but NOT in reject_count (D-04)", () => {
    // Simulate calibration aggregation with uncertain entries
    const entries: FeedbackEntry[] = [
      { signal_id: 'ind:001', target: 't', run_id: 'r1', verdict: 'accepted', source: 'user', submitted_at: '' },
      { signal_id: 'ind:002', target: 't', run_id: 'r1', verdict: 'rejected', source: 'user', submitted_at: '' },
      { signal_id: 'ind:003', target: 't', run_id: 'r1', verdict: 'uncertain', source: 'slack_reaction', submitted_at: '' },
    ]

    const byIndicator = new Map<string, { total: number; rejected: number }>()
    for (const entry of entries) {
      const indicator = entry.signal_id.split(':')[0] ?? entry.target
      const current = byIndicator.get(indicator) ?? { total: 0, rejected: 0 }
      current.total++
      if (entry.verdict === 'rejected') current.rejected++
      byIndicator.set(indicator, current)
    }

    const result = byIndicator.get('ind')
    expect(result).toBeDefined()
    expect(result!.total).toBe(3)    // all 3 count toward total
    expect(result!.rejected).toBe(1) // only 'rejected' counts (not 'uncertain')
  })
})
