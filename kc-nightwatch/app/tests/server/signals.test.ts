import { describe, it, expect, beforeEach, afterEach, spyOn } from 'bun:test'
import { Hono } from 'hono'
import type { Run, RunSummary, CalibrationData } from '../../shared/types.ts'
import * as runStore from '../../server/services/run-store.ts'
import * as feedbackStore from '../../server/services/feedback-store.ts'

// ============================================================
// Spy declarations
// ============================================================
let listRunsSpy: ReturnType<typeof spyOn>
let getRunSpy: ReturnType<typeof spyOn>
let getCalibrationDataSpy: ReturnType<typeof spyOn>

// Import routes — spyOn patches in beforeEach
const { signalsRoutes } = await import('../../server/routes/signals.ts')

// ============================================================
// Test app
// ============================================================
const testApp = new Hono()
testApp.route('/', signalsRoutes)

// ============================================================
// Mock helpers
// ============================================================
function makeRun(id: string): Run {
  return {
    id,
    target: 'plugin-a',
    mode: 'production',
    trigger: 'manual',
    status: 'completed',
    log_path: `/tmp/${id}.jsonl`,
    started_at: '2026-03-25T00:00:00Z',
  }
}

function makeSummary(actions: RunSummary['per_target'][string]['actions']): RunSummary {
  return {
    targets_active: 1,
    targets_skipped: 0,
    total_signals: actions.length,
    total_actions: actions.length,
    errors: 0,
    per_target: {
      'plugin-a': {
        monitors: {},
        pipeline: { found: actions.length, after_dedup: actions.length, after_confidence_filter: actions.length, after_cooldown: actions.length, classified: {}, executed: {} },
        actions,
        indicator_baseline: {},
        implementation_outcomes: [],
        pre_assessment: '',
        post_assessment: '',
      },
    },
  }
}

const emptyCalibration: CalibrationData[] = []

describe('signals api', () => {
  beforeEach(() => {
    listRunsSpy = spyOn(runStore, 'listRuns').mockImplementation(async () => [])
    getRunSpy = spyOn(runStore, 'getRun').mockImplementation(async () => null)
    getCalibrationDataSpy = spyOn(feedbackStore, 'getCalibrationData').mockImplementation(async () => emptyCalibration)
  })

  afterEach(() => {
    listRunsSpy.mockRestore()
    getRunSpy.mockRestore()
    getCalibrationDataSpy.mockRestore()
  })

  it('GET /api/signals/priority returns 200', async () => {
    const res = await testApp.request('/api/signals/priority')
    expect(res.status).toBe(200)
  })

  it('returns empty array when no runs', async () => {
    listRunsSpy.mockImplementation(async () => [])
    const res = await testApp.request('/api/signals/priority')
    const data = await res.json() as unknown[]
    expect(Array.isArray(data)).toBe(true)
    expect(data.length).toBe(0)
  })

  it('returns items sorted descending by score', async () => {
    const run = makeRun('run-001')
    // quality: high confidence (1.0), reject_rate=0.0 → score=1.0
    // coverage: medium confidence (0.6), reject_rate=0.0 → score=0.6
    // docs: low confidence (0.3), reject_rate=0.0 → score=0.3
    listRunsSpy.mockImplementation(async () => [run])
    getRunSpy.mockImplementation(async () => ({
      ...run,
      summary: makeSummary([
        { signal_id: 's1', type: 'proposal', summary: '', indicator: 'quality', assessment: { closer_to_north_star: 'yes', confidence: 'high', reasoning: '' } },
        { signal_id: 's2', type: 'proposal', summary: '', indicator: 'coverage', assessment: { closer_to_north_star: 'yes', confidence: 'medium', reasoning: '' } },
        { signal_id: 's3', type: 'proposal', summary: '', indicator: 'docs', assessment: { closer_to_north_star: 'yes', confidence: 'low', reasoning: '' } },
      ]),
    }))
    getCalibrationDataSpy.mockImplementation(async () => emptyCalibration)

    const res = await testApp.request('/api/signals/priority')
    const data = await res.json() as Array<{ indicator: string; score: number }>
    expect(data.length).toBe(3)
    expect(data[0].indicator).toBe('quality')
    expect(data[1].indicator).toBe('coverage')
    expect(data[2].indicator).toBe('docs')
    // Sorted descending
    expect(data[0].score).toBeGreaterThanOrEqual(data[1].score)
    expect(data[1].score).toBeGreaterThanOrEqual(data[2].score)
  })

  it('score is confidence_weight x (1 - reject_rate)', async () => {
    // all high confidence (weight=1.0), reject_rate=0.3 → score = 1.0 * 0.7 = 0.7
    const run = makeRun('run-001')
    listRunsSpy.mockImplementation(async () => [run])
    getRunSpy.mockImplementation(async () => ({
      ...run,
      summary: makeSummary([
        { signal_id: 's1', type: 'proposal', summary: '', indicator: 'code-quality', assessment: { closer_to_north_star: 'yes', confidence: 'high', reasoning: '' } },
      ]),
    }))
    getCalibrationDataSpy.mockImplementation(async () => [
      { indicator: 'code-quality', total_feedback: 10, reject_count: 3, reject_rate: 0.3, current_threshold: 0.45, history: [0.3] },
    ])

    const res = await testApp.request('/api/signals/priority')
    const data = await res.json() as Array<{ indicator: string; score: number; confidence_weight: number; reject_rate: number }>
    expect(data.length).toBe(1)
    expect(data[0].score).toBeCloseTo(0.7, 2)
    expect(data[0].confidence_weight).toBeCloseTo(1.0, 2)
    expect(data[0].reject_rate).toBeCloseTo(0.3, 2)
  })

  it('caps at 30 runs', async () => {
    // Mock 35 runs
    const runs = Array.from({ length: 35 }, (_, i) => makeRun(`run-${i.toString().padStart(3, '0')}`))
    listRunsSpy.mockImplementation(async () => runs)
    let getRuncallCount = 0
    getRunSpy.mockImplementation(async (id: string) => {
      getRuncallCount++
      const run = runs.find(r => r.id === id)
      if (!run) return null
      return { ...run, summary: makeSummary([]) }
    })

    await testApp.request('/api/signals/priority')
    expect(getRuncallCount).toBeLessThanOrEqual(30)
  })

  it('indicators without calibration data get reject_rate 0', async () => {
    const run = makeRun('run-001')
    listRunsSpy.mockImplementation(async () => [run])
    getRunSpy.mockImplementation(async () => ({
      ...run,
      summary: makeSummary([
        { signal_id: 's1', type: 'proposal', summary: '', indicator: 'unknown-indicator', assessment: { closer_to_north_star: 'yes', confidence: 'high', reasoning: '' } },
      ]),
    }))
    getCalibrationDataSpy.mockImplementation(async () => emptyCalibration)

    const res = await testApp.request('/api/signals/priority')
    const data = await res.json() as Array<{ indicator: string; reject_rate: number; score: number; confidence_weight: number }>
    expect(data.length).toBe(1)
    expect(data[0].reject_rate).toBe(0)
    // score = confidence_weight * (1 - 0) = confidence_weight
    expect(data[0].score).toBeCloseTo(data[0].confidence_weight, 2)
  })

  it('confidence weights: high=1.0, medium=0.6, low=0.3', async () => {
    const run = makeRun('run-001')
    listRunsSpy.mockImplementation(async () => [run])
    getRunSpy.mockImplementation(async () => ({
      ...run,
      summary: makeSummary([
        { signal_id: 's1', type: 'proposal', summary: '', indicator: 'high-ind', assessment: { closer_to_north_star: 'yes', confidence: 'high', reasoning: '' } },
        { signal_id: 's2', type: 'proposal', summary: '', indicator: 'medium-ind', assessment: { closer_to_north_star: 'yes', confidence: 'medium', reasoning: '' } },
        { signal_id: 's3', type: 'proposal', summary: '', indicator: 'low-ind', assessment: { closer_to_north_star: 'yes', confidence: 'low', reasoning: '' } },
      ]),
    }))
    getCalibrationDataSpy.mockImplementation(async () => emptyCalibration)

    const res = await testApp.request('/api/signals/priority')
    const data = await res.json() as Array<{ indicator: string; confidence_weight: number }>
    const byIndicator = Object.fromEntries(data.map(d => [d.indicator, d.confidence_weight]))
    expect(byIndicator['high-ind']).toBeCloseTo(1.0, 2)
    expect(byIndicator['medium-ind']).toBeCloseTo(0.6, 2)
    expect(byIndicator['low-ind']).toBeCloseTo(0.3, 2)
  })
})
