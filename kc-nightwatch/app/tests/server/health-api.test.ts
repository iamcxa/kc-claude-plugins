import { describe, it, expect, mock, beforeEach } from 'bun:test'
import { Hono } from 'hono'
import type { Run, RunSummary, CalibrationData } from '../../shared/types.ts'

// ============================================================
// Mocks — must precede health-api import
// ============================================================

const mockRun1: Run = {
  id: 'run-001',
  target: 'my-plugin',
  mode: 'production',
  trigger: 'manual',
  status: 'completed',
  log_path: '/tmp/run-001.jsonl',
  started_at: '2026-03-17T00:00:00Z',
}
const mockRun2: Run = {
  id: 'run-002',
  target: 'my-plugin',
  mode: 'production',
  trigger: 'interval',
  status: 'completed',
  log_path: '/tmp/run-002.jsonl',
  started_at: '2026-03-18T00:00:00Z',
}
const mockRun3: Run = {
  id: 'run-003',
  target: 'my-plugin',
  mode: 'production',
  trigger: 'interval',
  status: 'completed',
  log_path: '/tmp/run-003.jsonl',
  started_at: '2026-03-19T00:00:00Z',
}

const mockSummary1: RunSummary = {
  targets_active: 1,
  targets_skipped: 0,
  total_signals: 2,
  total_actions: 1,
  errors: 0,
  per_target: {
    'my-plugin': {
      monitors: {},
      pipeline: { found: 2, after_dedup: 2, after_confidence_filter: 2, after_cooldown: 2, classified: {}, executed: {} },
      actions: [
        { signal_id: 'sig-001', type: 'proposal', summary: 'Add X', indicator: 'quality', assessment: { closer_to_north_star: 'yes', confidence: 'high', reasoning: '' } },
      ],
      indicator_baseline: {
        quality: { value: 70, measurement: 'score', trend: 'improving' },
        coverage: { value: 55, measurement: '%', trend: 'stable' },
      },
      implementation_outcomes: [],
      pre_assessment: '',
      post_assessment: '',
    },
  },
}

const mockSummary2: RunSummary = {
  targets_active: 1,
  targets_skipped: 0,
  total_signals: 1,
  total_actions: 1,
  errors: 0,
  per_target: {
    'my-plugin': {
      monitors: {},
      pipeline: { found: 1, after_dedup: 1, after_confidence_filter: 1, after_cooldown: 1, classified: {}, executed: {} },
      actions: [
        { signal_id: 'sig-002', type: 'proposal', summary: 'Fix Y', indicator: 'coverage', assessment: { closer_to_north_star: 'yes', confidence: 'high', reasoning: '' } },
      ],
      indicator_baseline: {
        quality: { value: 75, measurement: 'score', trend: 'improving' },
        coverage: { value: 60, measurement: '%', trend: 'improving' },
      },
      implementation_outcomes: [],
      pre_assessment: '',
      post_assessment: '',
    },
  },
}

const mockSummary3: RunSummary = {
  targets_active: 1,
  targets_skipped: 0,
  total_signals: 1,
  total_actions: 0,
  errors: 0,
  per_target: {
    'my-plugin': {
      monitors: {},
      pipeline: { found: 1, after_dedup: 1, after_confidence_filter: 1, after_cooldown: 1, classified: {}, executed: {} },
      actions: [],
      indicator_baseline: {
        quality: { value: 80, measurement: 'score', trend: 'improving' },
        coverage: { value: 58, measurement: '%', trend: 'degrading' },
      },
      implementation_outcomes: [],
      pre_assessment: '',
      post_assessment: '',
    },
  },
}

const mockCalibrationData: CalibrationData[] = [
  { indicator: 'quality', total_feedback: 10, reject_count: 2, reject_rate: 0.2, current_threshold: 0.45 },
  { indicator: 'coverage', total_feedback: 5, reject_count: 3, reject_rate: 0.6, current_threshold: 0.55 },
]

// Control variables for mock behavior
let mockRunsResult: Run[] = [mockRun3, mockRun2, mockRun1]
let mockRunMap: Record<string, RunSummary> = {
  'run-001': mockSummary1,
  'run-002': mockSummary2,
  'run-003': mockSummary3,
}
let mockCalibration: CalibrationData[] = mockCalibrationData

const mockListRuns = mock(async (filter?: { status?: string; target?: string }) => {
  if (filter?.target) return mockRunsResult.filter(r => r.target === filter.target)
  return mockRunsResult
})

const mockGetRun = mock(async (id: string) => {
  const run = mockRunsResult.find(r => r.id === id)
  if (!run) return null
  return { ...run, summary: mockRunMap[id] }
})

const mockGetCalibrationData = mock(async () => mockCalibration)

mock.module('../../server/services/run-store.ts', () => ({
  listRuns: mockListRuns,
  getRun: mockGetRun,
}))

mock.module('../../server/services/feedback-store.ts', () => ({
  getCalibrationData: mockGetCalibrationData,
}))

// Import after mocks are registered
const { healthApiRoutes } = await import('../../server/routes/health-api.ts')

// ============================================================
// Test app
// ============================================================
const testApp = new Hono()
testApp.route('/', healthApiRoutes)

describe('health api', () => {
  beforeEach(() => {
    // Reset to defaults
    mockRunsResult = [mockRun3, mockRun2, mockRun1]
    mockRunMap = {
      'run-001': mockSummary1,
      'run-002': mockSummary2,
      'run-003': mockSummary3,
    }
    mockCalibration = mockCalibrationData
    mockListRuns.mockClear()
    mockGetRun.mockClear()
    mockGetCalibrationData.mockClear()
  })

  it('GET /api/health/:target returns 200', async () => {
    const res = await testApp.request('/api/health/my-plugin')
    expect(res.status).toBe(200)
  })

  it('response has correct TargetHealthData shape', async () => {
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as Record<string, unknown>
    expect(data).toHaveProperty('target')
    expect(data).toHaveProperty('health')
    expect(data).toHaveProperty('indicators')
    expect(data).toHaveProperty('reject_rate')
    expect(data).toHaveProperty('acceptance_rate')
    expect(data).toHaveProperty('runs_analyzed')
  })

  it('target field matches the route param', async () => {
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { target: string }
    expect(data.target).toBe('my-plugin')
  })

  it('indicators object contains history arrays from last 10 runs', async () => {
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { indicators: Record<string, { history: number[] }> }
    expect(data.indicators).toHaveProperty('quality')
    expect(Array.isArray(data.indicators.quality.history)).toBe(true)
    expect(data.indicators.quality.history.length).toBeGreaterThan(0)
  })

  it('indicator history is in chronological order (oldest first)', async () => {
    // run-001 (oldest): quality=70, run-002: quality=75, run-003 (newest): quality=80
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { indicators: Record<string, { history: number[] }> }
    const qualityHistory = data.indicators.quality.history
    // Should be [70, 75, 80] in chronological order
    expect(qualityHistory[0]).toBe(70)
    expect(qualityHistory[qualityHistory.length - 1]).toBe(80)
  })

  it('health field is improving when majority of indicators trend improving', async () => {
    // Summary3 (latest/wins) has quality=improving, coverage=degrading — tied, but let's check all runs
    // quality improves across all 3 runs, coverage: stable->improving->degrading
    // Latest trends: quality=improving (3 runs), coverage=degrading (latest run)
    // => 1 improving vs 1 degrading => stable
    // Let's use a scenario where all indicators are improving:
    mockRunMap = {
      'run-001': {
        ...mockSummary1,
        per_target: {
          'my-plugin': {
            ...mockSummary1.per_target['my-plugin']!,
            indicator_baseline: {
              quality: { value: 70, measurement: 'score', trend: 'improving' },
              coverage: { value: 55, measurement: '%', trend: 'improving' },
            },
          },
        },
      },
      'run-002': {
        ...mockSummary2,
        per_target: {
          'my-plugin': {
            ...mockSummary2.per_target['my-plugin']!,
            indicator_baseline: {
              quality: { value: 75, measurement: 'score', trend: 'improving' },
              coverage: { value: 60, measurement: '%', trend: 'improving' },
            },
          },
        },
      },
      'run-003': {
        ...mockSummary3,
        per_target: {
          'my-plugin': {
            ...mockSummary3.per_target['my-plugin']!,
            indicator_baseline: {
              quality: { value: 80, measurement: 'score', trend: 'improving' },
              coverage: { value: 65, measurement: '%', trend: 'improving' },
            },
          },
        },
      },
    }
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { health: string }
    expect(data.health).toBe('improving')
  })

  it('health field is stable when no clear majority', async () => {
    // 1 improving + 1 degrading = stable
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { health: string }
    // quality=improving (latest), coverage=degrading (latest) → tied → stable
    expect(data.health).toBe('stable')
  })

  it('runs_analyzed reflects actual number of runs found', async () => {
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { runs_analyzed: number }
    expect(data.runs_analyzed).toBe(3)
  })

  it('runs_analyzed caps at 10', async () => {
    // Create 15 runs
    const manyRuns: Run[] = Array.from({ length: 15 }, (_, i) => ({
      id: `run-${i.toString().padStart(3, '0')}`,
      target: 'my-plugin',
      mode: 'production' as const,
      trigger: 'manual' as const,
      status: 'completed' as const,
      log_path: `/tmp/run-${i}.jsonl`,
      started_at: new Date(2026, 2, i + 1).toISOString(),
    }))
    mockRunsResult = manyRuns
    mockRunMap = {}
    for (const r of manyRuns) {
      mockRunMap[r.id] = mockSummary1
    }
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { runs_analyzed: number }
    expect(data.runs_analyzed).toBeLessThanOrEqual(10)
  })

  it('empty run history returns runs_analyzed: 0, health: stable, indicators empty', async () => {
    mockRunsResult = []
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { runs_analyzed: number; health: string; indicators: Record<string, unknown> }
    expect(data.runs_analyzed).toBe(0)
    expect(data.health).toBe('stable')
    expect(Object.keys(data.indicators).length).toBe(0)
  })

  it('reject_rate comes from getCalibrationData aggregated across indicators', async () => {
    // calibration: quality reject_rate=0.2 (10 feedback), coverage reject_rate=0.6 (5 feedback)
    // avg = (0.2 + 0.6) / 2 = 0.4
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { reject_rate: number }
    expect(data.reject_rate).toBeCloseTo(0.4, 1)
  })

  it('acceptance_rate computed from calibration feedback (accepted / total)', async () => {
    // total_feedback = 10+5=15, reject_count = 2+3=5
    // acceptance_rate = (15-5)/15 ≈ 0.67
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { acceptance_rate: number }
    expect(data.acceptance_rate).toBeGreaterThan(0)
    expect(data.acceptance_rate).toBeLessThanOrEqual(1)
  })

  it('returns acceptance_rate 0 when no calibration data', async () => {
    mockCalibration = []
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { acceptance_rate: number; reject_rate: number }
    expect(data.acceptance_rate).toBe(0)
    expect(data.reject_rate).toBe(0)
  })

  it('response includes per_indicator_rates with per-indicator data', async () => {
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { per_indicator_rates: Record<string, { rate: number; history: number[] }> }
    expect(data).toHaveProperty('per_indicator_rates')
    expect(data.per_indicator_rates).toHaveProperty('quality')
    expect(data.per_indicator_rates).toHaveProperty('coverage')
  })

  it('per_indicator_rates entries have history arrays with length >= 2', async () => {
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { per_indicator_rates: Record<string, { rate: number; history: number[] }> }
    for (const [, entry] of Object.entries(data.per_indicator_rates)) {
      expect(Array.isArray(entry.history)).toBe(true)
      expect(entry.history.length).toBeGreaterThanOrEqual(2)
    }
  })

  it('per_indicator_rates is empty when no calibration data', async () => {
    mockCalibration = []
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { per_indicator_rates: Record<string, unknown> }
    expect(Object.keys(data.per_indicator_rates).length).toBe(0)
  })

  it('per_indicator_rates rate matches calibration reject_rate', async () => {
    const res = await testApp.request('/api/health/my-plugin')
    const data = await res.json() as { per_indicator_rates: Record<string, { rate: number; history: number[] }> }
    // quality reject_rate = 0.2, coverage reject_rate = 0.6
    expect(data.per_indicator_rates.quality.rate).toBeCloseTo(0.2, 2)
    expect(data.per_indicator_rates.coverage.rate).toBeCloseTo(0.6, 2)
  })
})
