import { describe, it, expect } from 'bun:test'
import type { CalibrationData } from '../../shared/types.ts'

// Test the pure helper functions from calibration-table.ts
// We re-implement them here to test the logic without requiring Preact/DOM.
// If these functions are ever refactored out of the component, import directly.

function sortByRejectRate(data: CalibrationData[]): CalibrationData[] {
  return [...data].sort((a, b) => b.reject_rate - a.reject_rate)
}

function formatThreshold(threshold: number | null, nullReason?: string): string {
  if (threshold === null) return nullReason ?? 'Accumulating data'
  return `${Math.round(threshold * 100)}%`
}

describe('sortByRejectRate', () => {
  it('sorts descending by reject_rate', () => {
    const data: CalibrationData[] = [
      { indicator: 'a', total_feedback: 10, reject_count: 2, reject_rate: 0.2, current_threshold: null, history: [] },
      { indicator: 'b', total_feedback: 10, reject_count: 8, reject_rate: 0.8, current_threshold: null, history: [] },
      { indicator: 'c', total_feedback: 10, reject_count: 5, reject_rate: 0.5, current_threshold: null, history: [] },
    ]
    const sorted = sortByRejectRate(data)
    expect(sorted[0].reject_rate).toBe(0.8)
    expect(sorted[1].reject_rate).toBe(0.5)
    expect(sorted[2].reject_rate).toBe(0.2)
  })

  it('returns empty array for empty input', () => {
    expect(sortByRejectRate([])).toHaveLength(0)
  })

  it('returns single element array unchanged', () => {
    const data: CalibrationData[] = [
      { indicator: 'a', total_feedback: 5, reject_count: 1, reject_rate: 0.2, current_threshold: null, history: [] },
    ]
    const sorted = sortByRejectRate(data)
    expect(sorted).toHaveLength(1)
    expect(sorted[0].indicator).toBe('a')
  })

  it('does not mutate the original array', () => {
    const data: CalibrationData[] = [
      { indicator: 'a', total_feedback: 10, reject_count: 2, reject_rate: 0.2, current_threshold: null, history: [] },
      { indicator: 'b', total_feedback: 10, reject_count: 8, reject_rate: 0.8, current_threshold: null, history: [] },
    ]
    const original = [...data]
    sortByRejectRate(data)
    expect(data[0].indicator).toBe(original[0].indicator)
    expect(data[1].indicator).toBe(original[1].indicator)
  })

  it('handles equal reject_rate values', () => {
    const data: CalibrationData[] = [
      { indicator: 'a', total_feedback: 10, reject_count: 5, reject_rate: 0.5, current_threshold: null, history: [] },
      { indicator: 'b', total_feedback: 10, reject_count: 5, reject_rate: 0.5, current_threshold: null, history: [] },
    ]
    const sorted = sortByRejectRate(data)
    expect(sorted).toHaveLength(2)
    expect(sorted[0].reject_rate).toBe(0.5)
    expect(sorted[1].reject_rate).toBe(0.5)
  })
})

describe('formatThreshold', () => {
  it('returns threshold_null_reason when threshold is null', () => {
    expect(formatThreshold(null, 'Accumulating data (5/10)')).toBe('Accumulating data (5/10)')
  })

  it('returns "Accumulating data" fallback when null and no reason', () => {
    expect(formatThreshold(null, undefined)).toBe('Accumulating data')
  })

  it('returns percentage string for a value', () => {
    expect(formatThreshold(0.45, undefined)).toBe('45%')
  })

  it('rounds to integer percentage', () => {
    expect(formatThreshold(0.123, undefined)).toBe('12%')
  })

  it('rounds 0.999 to 100%', () => {
    expect(formatThreshold(0.999, undefined)).toBe('100%')
  })

  it('returns 0% for zero threshold', () => {
    expect(formatThreshold(0, undefined)).toBe('0%')
  })

  it('ignores nullReason when threshold is provided', () => {
    expect(formatThreshold(0.45, 'some reason')).toBe('45%')
  })
})
