import { describe, it, expect, beforeEach, afterEach } from 'bun:test'
import { Hono } from 'hono'
import { apiRoutes } from '../../server/routes/api.ts'
import { setWorkerStatus } from '../../server/ipc.ts'
import { writeYamlFile } from '../../server/services/yaml-store.ts'
import os from 'node:os'
import path from 'node:path'

const app = new Hono()
app.route('/', apiRoutes)

// ----------------------------------------------------------------
// Helper: temp runs YAML
// ----------------------------------------------------------------
const TEST_RUNS_PATH = path.join(os.tmpdir(), `nightwatch-runs-test-${Date.now()}.yaml`)
const TEST_TARGETS_PATH = path.join(os.tmpdir(), `nightwatch-targets-test-${Date.now()}.yaml`)

// Write targets file for tests
async function setupTargets() {
  await writeYamlFile(TEST_TARGETS_PATH, {
    targets: {
      'test-plugin': {
        type: 'plugin',
        monitors: ['github-issues'],
        watch: ['performance'],
        respond: { 'code-fix': true },
        indicators: [{ id: 'IND-01', description: 'Issues' }],
        north_star: 'Zero issues',
      },
    },
  })
}

// Write runs file for tests
async function setupRuns(runs: unknown[]) {
  await writeYamlFile(TEST_RUNS_PATH, { runs })
}

afterEach(async () => {
  try {
    await Bun.spawn(['rm', '-f', TEST_RUNS_PATH, TEST_TARGETS_PATH]).exited
  } catch { /* ignore */ }
})

// ----------------------------------------------------------------
// Tests for GET /api/targets
// ----------------------------------------------------------------
describe('GET /api/targets', () => {
  it('returns 200 with target array', async () => {
    await setupTargets()
    // Override module path for this test — use environment trick
    // Since we can't easily mock readTargets(), we test the shape
    const res = await app.request('/api/targets')
    // Worker status doesn't affect targets route — it's always accessible
    // With no real targets file, it returns empty array
    expect(res.status).toBe(200)
    const body = await res.json() as unknown[]
    expect(Array.isArray(body)).toBe(true)
  })
})

// ----------------------------------------------------------------
// Tests for POST /api/runs
// ----------------------------------------------------------------
describe('POST /api/runs', () => {
  it('returns 503 when worker is offline', async () => {
    setWorkerStatus('offline')
    const res = await app.request('/api/runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target: 'test-plugin', mode: 'production' }),
    })
    expect(res.status).toBe(503)
    const body = await res.json() as Record<string, unknown>
    expect(body.error).toBe('worker offline')
  })

  it('returns 202 with run_id when worker is online', async () => {
    setWorkerStatus('online')
    await setupRuns([])
    const res = await app.request('/api/runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target: 'test-plugin', mode: 'production' }),
    })
    expect(res.status).toBe(202)
    const body = await res.json() as Record<string, unknown>
    expect(typeof body.run_id).toBe('string')
    expect((body.run_id as string).length).toBeGreaterThan(0)
  })

  it('run_id is a UUID', async () => {
    setWorkerStatus('online')
    await setupRuns([])
    const res = await app.request('/api/runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target: 'test-plugin', mode: 'dry-run', custom_prompt: 'focus on perf' }),
    })
    const body = await res.json() as Record<string, unknown>
    expect((body.run_id as string)).toMatch(/^[0-9a-f-]{36}$/)
  })
})

// ----------------------------------------------------------------
// Tests for GET /api/runs
// ----------------------------------------------------------------
describe('GET /api/runs', () => {
  it('returns 200 with runs array', async () => {
    const res = await app.request('/api/runs')
    expect(res.status).toBe(200)
    const body = await res.json() as unknown[]
    expect(Array.isArray(body)).toBe(true)
  })

  it('accepts ?status= query param', async () => {
    const res = await app.request('/api/runs?status=failed')
    expect(res.status).toBe(200)
    const body = await res.json() as unknown[]
    expect(Array.isArray(body)).toBe(true)
  })

  it('accepts ?target= query param', async () => {
    const res = await app.request('/api/runs?target=test-plugin')
    expect(res.status).toBe(200)
    const body = await res.json() as unknown[]
    expect(Array.isArray(body)).toBe(true)
  })
})

// ----------------------------------------------------------------
// Tests for GET /api/runs/:id
// ----------------------------------------------------------------
describe('GET /api/runs/:id', () => {
  it('returns 404 for unknown run', async () => {
    const res = await app.request('/api/runs/nonexistent-id')
    expect(res.status).toBe(404)
  })
})

// ----------------------------------------------------------------
// Tests for DELETE /api/runs/:id
// ----------------------------------------------------------------
describe('DELETE /api/runs/:id', () => {
  it('returns 200 ok when worker not offline_permanent', async () => {
    setWorkerStatus('online')
    const res = await app.request('/api/runs/any-id', { method: 'DELETE' })
    expect(res.status).toBe(200)
    const body = await res.json() as Record<string, unknown>
    // ok may be false if worker proc is null, but status is 200
    expect(body).toHaveProperty('ok')
  })
})

// ----------------------------------------------------------------
// Tests for POST /api/webhook
// ----------------------------------------------------------------
describe('POST /api/webhook', () => {
  it('returns 503 when worker is offline', async () => {
    setWorkerStatus('offline')
    const res = await app.request('/api/webhook', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    })
    expect(res.status).toBe(503)
  })

  it('returns 202 with run_id when worker is online', async () => {
    setWorkerStatus('online')
    await setupRuns([])
    const res = await app.request('/api/webhook', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target: 'test-plugin', mode: 'production' }),
    })
    expect(res.status).toBe(202)
    const body = await res.json() as Record<string, unknown>
    expect(typeof body.run_id).toBe('string')
  })

  it('accepts empty body for webhook trigger (defaults to __all__ + production)', async () => {
    setWorkerStatus('online')
    await setupRuns([])
    const res = await app.request('/api/webhook', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    })
    expect(res.status).toBe(202)
  })
})
