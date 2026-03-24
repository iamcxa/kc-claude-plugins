import { describe, it, expect, beforeEach, afterEach, spyOn } from 'bun:test'
import { Hono } from 'hono'
import type { OutcomeRecord } from '../../shared/types.ts'
import * as outcomeStore from '../../server/services/outcome-store.ts'

// Test fixtures
const makeRecord = (overrides: Partial<OutcomeRecord> = {}): OutcomeRecord => ({
  id: 'test-id-1',
  type: 'pr',
  target: 'e2e-pipeline',
  signal_id: 'sig-001',
  run_id: 'run-001',
  url: 'https://github.com/org/repo/pull/42',
  branch: 'kc-nightwatch/2026-03-22-e2e-pipeline-fixes',
  status: 'open',
  created_at: '2026-03-22T10:00:00.000Z',
  ...overrides,
})

const RECORDS: OutcomeRecord[] = [
  makeRecord({ id: 'r-1', target: 'e2e-pipeline', type: 'pr', status: 'open' }),
  makeRecord({ id: 'r-2', target: 'e2e-pipeline', type: 'linear_issue', status: 'merged', url: 'https://linear.app/team/issue/SC-1' }),
  makeRecord({ id: 'r-3', target: 'kc-plugin-forge', type: 'pr', status: 'open' }),
  makeRecord({ id: 'r-4', target: 'kc-plugin-forge', type: 'linear_issue', status: 'closed', url: 'https://linear.app/team/issue/SC-2' }),
]

// Spy declarations
let queryOutcomesSpy: ReturnType<typeof spyOn>
let readOutcomesSpy: ReturnType<typeof spyOn>
let appendOutcomeSpy: ReturnType<typeof spyOn>

// Import routes
const { outcomesRoutes } = await import('../../server/routes/outcomes.ts')

// Create a test app that mounts the routes
function makeApp() {
  const app = new Hono()
  app.route('/', outcomesRoutes)
  return app
}

describe('GET /api/outcomes', () => {
  beforeEach(() => {
    queryOutcomesSpy = spyOn(outcomeStore, 'queryOutcomes').mockImplementation(async (filter: { target?: string; type?: string; status?: string } = {}) => {
      let records = [...RECORDS]
      if (filter.target) records = records.filter(r => r.target === filter.target)
      if (filter.type) records = records.filter(r => r.type === filter.type)
      if (filter.status) records = records.filter(r => r.status === filter.status)
      return records
    })
    readOutcomesSpy = spyOn(outcomeStore, 'readOutcomes').mockResolvedValue([...RECORDS])
    appendOutcomeSpy = spyOn(outcomeStore, 'appendOutcome').mockResolvedValue(undefined)
  })

  afterEach(() => {
    queryOutcomesSpy.mockRestore()
    readOutcomesSpy.mockRestore()
    appendOutcomeSpy.mockRestore()
  })

  it('returns all outcomes when no filters provided', async () => {
    const app = makeApp()
    const res = await app.request('/api/outcomes')
    expect(res.status).toBe(200)
    const body = await res.json() as OutcomeRecord[]
    expect(Array.isArray(body)).toBe(true)
    expect(body.length).toBe(4)
  })

  it('filters by target when target query param is provided', async () => {
    const app = makeApp()
    const res = await app.request('/api/outcomes?target=e2e-pipeline')
    expect(res.status).toBe(200)
    const body = await res.json() as OutcomeRecord[]
    expect(body.every((r: OutcomeRecord) => r.target === 'e2e-pipeline')).toBe(true)
    expect(body.length).toBe(2)
  })

  it('filters by both type and status query params', async () => {
    const app = makeApp()
    const res = await app.request('/api/outcomes?type=pr&status=open')
    expect(res.status).toBe(200)
    const body = await res.json() as OutcomeRecord[]
    expect(body.every((r: OutcomeRecord) => r.type === 'pr' && r.status === 'open')).toBe(true)
  })
})

describe('GET /api/outcomes/:id/status', () => {
  beforeEach(() => {
    queryOutcomesSpy = spyOn(outcomeStore, 'queryOutcomes').mockImplementation(async (filter: { target?: string; type?: string; status?: string } = {}) => {
      let records = [...RECORDS]
      if (filter.target) records = records.filter(r => r.target === filter.target)
      if (filter.type) records = records.filter(r => r.type === filter.type)
      if (filter.status) records = records.filter(r => r.status === filter.status)
      return records
    })
    readOutcomesSpy = spyOn(outcomeStore, 'readOutcomes').mockResolvedValue([...RECORDS])
    appendOutcomeSpy = spyOn(outcomeStore, 'appendOutcome').mockResolvedValue(undefined)
  })

  afterEach(() => {
    queryOutcomesSpy.mockRestore()
    readOutcomesSpy.mockRestore()
    appendOutcomeSpy.mockRestore()
  })

  it('returns { status } for existing record id', async () => {
    const app = makeApp()
    const res = await app.request('/api/outcomes/r-1/status')
    expect(res.status).toBe(200)
    const body = await res.json() as { status: string }
    expect(body).toHaveProperty('status')
    expect(body.status).toBe('open')
  })

  it('returns 404 for non-existent id', async () => {
    const app = makeApp()
    const res = await app.request('/api/outcomes/does-not-exist/status')
    expect(res.status).toBe(404)
    const body = await res.json() as { error: string }
    expect(body).toHaveProperty('error')
  })
})
