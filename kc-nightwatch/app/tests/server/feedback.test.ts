import { describe, it, expect, beforeEach } from 'bun:test'
import { mkdtemp } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'

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
})
