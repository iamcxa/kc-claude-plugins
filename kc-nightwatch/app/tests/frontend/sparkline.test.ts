import { describe, it, expect } from 'bun:test'

// Test the pure helper functions from sparkline.ts
// We re-implement them here to test the logic without requiring Preact/DOM.
// If these functions are ever refactored out of the component, import directly.

function tooltipStyle(idx: number, total: number, width: number): Record<string, string> {
  if (idx === 0) return { left: '0px', transform: 'none' }
  if (idx === total - 1) return { right: '0px', left: 'auto', transform: 'none' }
  const x = (idx / (total - 1)) * width
  return { left: `${x}px`, transform: 'translateX(-50%)' }
}

function formatTooltipValue(v: number): string {
  return `${Math.round(v * 100)}%`
}

function pointSpacingFor(count: number, width: number): number {
  return count > 1 ? width / (count - 1) : width
}

describe('tooltipStyle', () => {
  it('returns left-anchored style for first point (idx=0)', () => {
    const style = tooltipStyle(0, 5, 80)
    expect(style.left).toBe('0px')
    expect(style.transform).toBe('none')
  })

  it('returns right-anchored style for last point (idx=total-1)', () => {
    const style = tooltipStyle(4, 5, 80)
    expect(style.right).toBe('0px')
    expect(style.left).toBe('auto')
    expect(style.transform).toBe('none')
  })

  it('returns centered style for middle point', () => {
    const style = tooltipStyle(2, 5, 80)
    expect(style.left).toBe('40px')
    expect(style.transform).toBe('translateX(-50%)')
  })

  it('returns correct x position for idx=1 of 5 at width 80', () => {
    const style = tooltipStyle(1, 5, 80)
    // x = (1 / (5-1)) * 80 = 20
    expect(style.left).toBe('20px')
    expect(style.transform).toBe('translateX(-50%)')
  })

  it('returns correct x position for idx=3 of 5 at width 80', () => {
    const style = tooltipStyle(3, 5, 80)
    // x = (3 / (5-1)) * 80 = 60
    expect(style.left).toBe('60px')
    expect(style.transform).toBe('translateX(-50%)')
  })

  it('handles 2-point sparkline: idx=0 is left-anchored', () => {
    const style = tooltipStyle(0, 2, 80)
    expect(style.left).toBe('0px')
    expect(style.transform).toBe('none')
  })

  it('handles 2-point sparkline: idx=1 is right-anchored', () => {
    const style = tooltipStyle(1, 2, 80)
    expect(style.right).toBe('0px')
    expect(style.left).toBe('auto')
    expect(style.transform).toBe('none')
  })
})

describe('formatTooltipValue', () => {
  it('formats 0.75 as "75%"', () => {
    expect(formatTooltipValue(0.75)).toBe('75%')
  })

  it('rounds 0.123 to "12%"', () => {
    expect(formatTooltipValue(0.123)).toBe('12%')
  })

  it('formats 1.0 as "100%"', () => {
    expect(formatTooltipValue(1.0)).toBe('100%')
  })

  it('formats 0.0 as "0%"', () => {
    expect(formatTooltipValue(0.0)).toBe('0%')
  })

  it('rounds 0.999 to "100%"', () => {
    expect(formatTooltipValue(0.999)).toBe('100%')
  })

  it('rounds 0.505 to "51%"', () => {
    expect(formatTooltipValue(0.505)).toBe('51%')
  })
})

describe('pointSpacing calculation', () => {
  it('computes correct spacing for 5 points at width 80', () => {
    // 80 / (5-1) = 20
    expect(pointSpacingFor(5, 80)).toBe(20)
  })

  it('computes correct spacing for 2 points at width 80', () => {
    // 80 / (2-1) = 80
    expect(pointSpacingFor(2, 80)).toBe(80)
  })

  it('returns full width for single point', () => {
    expect(pointSpacingFor(1, 80)).toBe(80)
  })

  it('computes correct spacing for 10 points at width 100', () => {
    // 100 / (10-1) ≈ 11.11
    expect(pointSpacingFor(10, 100)).toBeCloseTo(11.11, 1)
  })
})
