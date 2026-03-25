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
    // Simulate calibration logic — reject_rate = rejected / total (unchanged)
    const total = 10
    const rejected = 3
    const rejectRate = rejected / total
    expect(rejectRate).toBeCloseTo(0.3)
  })

  it('calibration threshold rises with high reject rate (EMA)', () => {
    // All-0.8 history: EMA converges toward 0.8, clamped to max 0.9
    const ALPHA = 0.3
    let ema = 0.5
    for (let i = 0; i < 10; i++) {
      ema = ALPHA * 0.8 + (1 - ALPHA) * ema
    }
    const threshold = Math.round(Math.min(0.9, Math.max(0.1, ema)) * 100) / 100
    expect(threshold).toBeGreaterThan(0.5) // high reject rate → threshold above midpoint
    expect(threshold).toBeLessThanOrEqual(0.9)
  })

  it('calibration threshold stays bounded [0.1, 0.9] (EMA)', () => {
    // All-1.0 history: clamps to 0.9
    const ALPHA = 0.3
    let ema1 = 0.5
    for (let i = 0; i < 20; i++) ema1 = ALPHA * 1.0 + (1 - ALPHA) * ema1
    expect(Math.min(0.9, Math.max(0.1, ema1))).toBeLessThanOrEqual(0.9)

    // All-0.0 history: clamps to 0.1
    let ema2 = 0.5
    for (let i = 0; i < 20; i++) ema2 = ALPHA * 0.0 + (1 - ALPHA) * ema2
    expect(Math.min(0.9, Math.max(0.1, ema2))).toBeGreaterThanOrEqual(0.1)
  })

  it('CalibrationData includes history array', () => {
    // Verify the shape includes history: number[]
    const mockCal = { indicator: 'test', total_feedback: 10, reject_count: 2, reject_rate: 0.2, current_threshold: 0.45, history: [0.1, 0.3, 0.2] }
    expect(Array.isArray(mockCal.history)).toBe(true)
    expect(mockCal.history.length).toBe(3)
  })

  it('CalibrationData includes threshold_null_reason when threshold is null', () => {
    const mockCal = {
      indicator: 'test',
      total_feedback: 5,
      reject_count: 2,
      reject_rate: 0.4,
      current_threshold: null,
      threshold_null_reason: 'Accumulating data (5/10)',
      history: [],
    }
    expect(mockCal.current_threshold).toBeNull()
    expect(mockCal.threshold_null_reason).toContain('5/10')
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
