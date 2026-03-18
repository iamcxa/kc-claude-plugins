import { describe, it, expect } from 'bun:test'

describe('reject rate calibration logic', () => {
  function computeThreshold(rejectRate: number): number {
    return Math.min(0.9, Math.max(0.1, 0.5 + (rejectRate - 0.5) * 0.5))
  }

  it('50% reject rate keeps default threshold of 0.5', () => {
    expect(computeThreshold(0.5)).toBeCloseTo(0.5)
  })

  it('high reject rate (70%) raises threshold', () => {
    expect(computeThreshold(0.7)).toBeCloseTo(0.6)
  })

  it('low reject rate (20%) lowers threshold', () => {
    expect(computeThreshold(0.2)).toBeCloseTo(0.35)
  })

  it('zero reject rate gives 0.25 threshold', () => {
    expect(computeThreshold(0)).toBeCloseTo(0.25)
  })

  it('100% reject rate gives 0.75 threshold', () => {
    expect(computeThreshold(1.0)).toBeCloseTo(0.75)
  })

  it('threshold is clamped to [0.1, 0.9]', () => {
    // Even extreme values stay in range
    expect(computeThreshold(-1)).toBeGreaterThanOrEqual(0.1)
    expect(computeThreshold(2)).toBeLessThanOrEqual(0.9)
  })
})
