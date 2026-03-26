import { describe, it, expect, spyOn, beforeEach, afterEach } from 'bun:test'
import { Hono } from 'hono'
import type { Run, RunSummary } from '../../shared/types.ts'
import * as runStore from '../../server/services/run-store.ts'

// ============================================================
// Test: signal-priority service + route
// ============================================================

describe('computePriorityScore', () => {
  it('returns 1.0 for high confidence + yes alignment', async () => {
    const { computePriorityScore } = await import('../../server/services/signal-priority.ts')
    const score = computePriorityScore({ assessment: { confidence: 'high', closer_to_north_star: 'yes', reasoning: '' } })
    expect(score).toBe(1.0)
  })

  it('returns 0.0 for low confidence + no alignment', async () => {
    const { computePriorityScore } = await import('../../server/services/signal-priority.ts')
    const score = computePriorityScore({ assessment: { confidence: 'low', closer_to_north_star: 'no', reasoning: '' } })
    expect(score).toBe(0.0)
  })

  it('returns 0.67 for high confidence + uncertain alignment', async () => {
    const { computePriorityScore } = await import('../../server/services/signal-priority.ts')
    const score = computePriorityScore({ assessment: { confidence: 'high', closer_to_north_star: 'uncertain', reasoning: '' } })
    expect(score).toBe(0.5)
  })

  it('returns 0.67 for medium confidence + yes alignment', async () => {
    const { computePriorityScore } = await import('../../server/services/signal-priority.ts')
    const score = computePriorityScore({ assessment: { confidence: 'medium', closer_to_north_star: 'yes', reasoning: '' } })
    expect(score).toBe(0.67)
  })

  it('returns rounded value to 2 decimal places', async () => {
    const { computePriorityScore } = await import('../../server/services/signal-priority.ts')
    const score = computePriorityScore({ assessment: { confidence: 'medium', closer_to_north_star: 'uncertain', reasoning: '' } })
    // 0.67 * 0.5 = 0.335 → rounds to 0.34
    expect(score).toBe(0.34)
  })
})

describe('computePriorities', () => {
  it('sorts actions by score descending', async () => {
    const { computePriorities } = await import('../../server/services/signal-priority.ts')
    const actions = [
      { signal_id: 'low-sig', type: 'proposal', summary: '', indicator: '', assessment: { confidence: 'low' as const, closer_to_north_star: 'yes' as const, reasoning: '' } },
      { signal_id: 'high-sig', type: 'proposal', summary: '', indicator: '', assessment: { confidence: 'high' as const, closer_to_north_star: 'yes' as const, reasoning: '' } },
      { signal_id: 'med-sig', type: 'proposal', summary: '', indicator: '', assessment: { confidence: 'medium' as const, closer_to_north_star: 'yes' as const, reasoning: '' } },
    ]
    const result = computePriorities(actions)
    expect(result[0].signal_id).toBe('high-sig')
    expect(result[1].signal_id).toBe('med-sig')
    expect(result[2].signal_id).toBe('low-sig')
  })

  it('uses signal_id as tie-breaker for equal scores', async () => {
    const { computePriorities } = await import('../../server/services/signal-priority.ts')
    const actions = [
      { signal_id: 'z-sig', type: 'proposal', summary: '', indicator: '', assessment: { confidence: 'high' as const, closer_to_north_star: 'yes' as const, reasoning: '' } },
      { signal_id: 'a-sig', type: 'proposal', summary: '', indicator: '', assessment: { confidence: 'high' as const, closer_to_north_star: 'yes' as const, reasoning: '' } },
    ]
    const result = computePriorities(actions)
    expect(result[0].signal_id).toBe('a-sig')
    expect(result[1].signal_id).toBe('z-sig')
  })

  it('returns entries with correct shape', async () => {
    const { computePriorities } = await import('../../server/services/signal-priority.ts')
    const actions = [
      { signal_id: 'sig-001', type: 'proposal', summary: '', indicator: '', assessment: { confidence: 'high' as const, closer_to_north_star: 'yes' as const, reasoning: '' } },
    ]
    const result = computePriorities(actions)
    expect(result).toHaveLength(1)
    expect(result[0]).toMatchObject({
      signal_id: 'sig-001',
      score: 1.0,
      confidence: 'high',
      closer_to_north_star: 'yes',
    })
  })

  it('handles empty action list', async () => {
    const { computePriorities } = await import('../../server/services/signal-priority.ts')
    expect(computePriorities([])).toEqual([])
  })
})

// ============================================================
// API route: GET /api/signals/priority
// ============================================================

describe('GET /api/signals/priority', () => {
  const mockRun: Run = {
    id: 'run-001',
    target: 'my-plugin',
    mode: 'production',
    trigger: 'manual',
    status: 'completed',
    log_path: '/tmp/run-001.jsonl',
    started_at: '2026-03-27T00:00:00Z',
  }

  const mockSummary: RunSummary = {
    targets_active: 1,
    targets_skipped: 0,
    total_signals: 2,
    total_actions: 2,
    errors: 0,
    per_target: {
      'my-plugin': {
        monitors: {},
        pipeline: { found: 2, after_dedup: 2, after_confidence_filter: 2, after_cooldown: 2, classified: {}, executed: {} },
        actions: [
          { signal_id: 'sig-low', type: 'proposal', summary: 'Low priority action', indicator: 'quality',
            assessment: { confidence: 'low', closer_to_north_star: 'yes', reasoning: '' }, pr_url: undefined, linear_url: undefined, branch: undefined },
          { signal_id: 'sig-high', type: 'code-fix', summary: 'High priority action', indicator: 'quality',
            assessment: { confidence: 'high', closer_to_north_star: 'yes', reasoning: '' }, pr_url: undefined, linear_url: undefined, branch: undefined },
        ],
        indicator_baseline: {},
        implementation_outcomes: [],
        pre_assessment: '',
        post_assessment: '',
      }
    }
  }

  let getRun: ReturnType<typeof spyOn>

  beforeEach(() => {
    getRun = spyOn(runStore, 'getRun').mockResolvedValue({ ...mockRun, summary: mockSummary })
  })

  afterEach(() => {
    getRun.mockRestore()
  })

  async function makeApp() {
    const { signalPriorityRoutes } = await import('../../server/routes/signal-priority.ts')
    const app = new Hono()
    app.route('/', signalPriorityRoutes)
    return app
  }

  it('returns 400 when run_id is missing', async () => {
    const app = await makeApp()
    const res = await app.request('/api/signals/priority')
    expect(res.status).toBe(400)
    const body = await res.json() as { error: string }
    expect(body.error).toContain('run_id')
  })

  it('returns 404 when run not found', async () => {
    getRun.mockResolvedValueOnce(null)
    const app = await makeApp()
    const res = await app.request('/api/signals/priority?run_id=nonexistent')
    expect(res.status).toBe(404)
  })

  it('returns priority entries sorted descending by score', async () => {
    const app = await makeApp()
    const res = await app.request('/api/signals/priority?run_id=run-001')
    expect(res.status).toBe(200)
    const body = await res.json() as Array<{ signal_id: string; score: number }>
    expect(body).toHaveLength(2)
    // high-priority signal should come first
    expect(body[0].signal_id).toBe('sig-high')
    expect(body[1].signal_id).toBe('sig-low')
    // high=1.0, low=0.33
    expect(body[0].score).toBe(1.0)
    expect(body[1].score).toBe(0.33)
  })

  it('returns empty array when run has no actions', async () => {
    getRun.mockResolvedValueOnce({
      ...mockRun,
      summary: { ...mockSummary, per_target: { 'my-plugin': { ...mockSummary.per_target['my-plugin'], actions: [] } } }
    })
    const app = await makeApp()
    const res = await app.request('/api/signals/priority?run_id=run-001')
    expect(res.status).toBe(200)
    const body = await res.json() as unknown[]
    expect(body).toHaveLength(0)
  })

  it('returns empty array when run has no summary', async () => {
    getRun.mockResolvedValueOnce({ ...mockRun, summary: undefined })
    const app = await makeApp()
    const res = await app.request('/api/signals/priority?run_id=run-001')
    expect(res.status).toBe(200)
    const body = await res.json() as unknown[]
    expect(body).toHaveLength(0)
  })
})
