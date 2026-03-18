import { describe, it, expect } from 'bun:test'
import type { IndicatorBaseline } from '../../shared/types.ts'

describe('indicator baseline', () => {
  it('IndicatorBaseline has required fields', () => {
    const baseline: IndicatorBaseline = {
      value: 85,
      measurement: 'percent',
      trend: 'improving',
    }
    expect(baseline.value).toBe(85)
    expect(baseline.measurement).toBe('percent')
    expect(baseline.trend).toBe('improving')
  })

  it('trend can be improving, stable, or degrading', () => {
    const trends: IndicatorBaseline['trend'][] = ['improving', 'stable', 'degrading']
    for (const trend of trends) {
      const b: IndicatorBaseline = { value: 50, measurement: 'count', trend }
      expect(['improving', 'stable', 'degrading']).toContain(b.trend)
    }
  })

  it('previous_value is optional', () => {
    const withPrev: IndicatorBaseline = { value: 90, measurement: '%', previous_value: 85, trend: 'improving' }
    const withoutPrev: IndicatorBaseline = { value: 90, measurement: '%', trend: 'stable' }
    expect(withPrev.previous_value).toBe(85)
    expect(withoutPrev.previous_value).toBeUndefined()
  })

  it('trend arrow mapping is consistent', () => {
    const arrows: Record<string, string> = {
      improving: '\u2191',  // up arrow
      degrading: '\u2193',  // down arrow
      stable: '\u2192',     // right arrow
    }
    expect(arrows.improving).toBe('\u2191')
    expect(arrows.degrading).toBe('\u2193')
    expect(arrows.stable).toBe('\u2192')
  })
})
