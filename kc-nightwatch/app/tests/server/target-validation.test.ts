import { describe, it, expect, mock, afterAll, beforeAll } from 'bun:test'
import { Hono } from 'hono'
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import path from 'node:path'
import os from 'node:os'

// Create a real temp directory for "valid path" tests
const tmpDir = mkdtempSync(path.join(os.tmpdir(), 'nw-test-'))

// Temp targets YAML path — used by mock and route
const tmpTargetsYaml = path.join(os.tmpdir(), 'nw-test-targets.yaml')

// Mock yaml-store — override TARGETS_YAML_PATH to point to a temp file
// Note: real signature is withWriteLock(file: string, fn: () => Promise<T>)
mock.module('../../server/services/yaml-store.ts', () => ({
  readTargets: mock(async () => ({})),
  writeTargets: mock(async () => {}),
  readYamlFile: mock(async () => ({})),
  writeYamlFile: mock(async () => {}),
  loadOrCreateAppConfig: mock(async () => ({ schedule: { enabled: false } })),
  writeAppConfig: mock(async () => {}),
  TARGETS_YAML_PATH: tmpTargetsYaml,
}))

// Mock config-validator — withWriteLock should just execute the callback
// Note: real signature is withWriteLock(file: string, fn: () => Promise<T>)
mock.module('../../server/services/config-validator.ts', () => ({
  validateConfigSave: mock(async () => ({ valid: true })),
  withWriteLock: mock(async (_file: string, fn: () => Promise<unknown>) => fn()),
}))

// Mock ipc — sendToWorker used for config-changed notification
mock.module('../../server/ipc.ts', () => ({
  sendToWorker: mock(() => {}),
}))

// Import routes AFTER mocking
const { configRoutes } = await import('../../server/routes/config.ts')

function makeApp() {
  const app = new Hono()
  app.route('/', configRoutes)
  return app
}

beforeAll(() => {
  // Initialize temp targets file with one pre-existing target for PUT tests
  writeFileSync(tmpTargetsYaml, 'targets:\n  my-target:\n    type: plugin\n    path: /tmp\n')
})

afterAll(() => {
  rmSync(tmpDir, { recursive: true, force: true })
  try { rmSync(tmpTargetsYaml) } catch { /* ignore */ }
})

describe('POST /api/config/targets/add — path validation', () => {
  it('returns 400 when path is empty string', async () => {
    const res = await makeApp().request('/api/config/targets/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'target-empty-path', target: { path: '' } }),
    })
    expect(res.status).toBe(400)
    const body = await res.json() as { error: string }
    expect(body.error).toBe('path is required')
  })

  it('returns 400 when path is missing (undefined)', async () => {
    const res = await makeApp().request('/api/config/targets/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'target-no-path', target: { type: 'plugin' } }),
    })
    expect(res.status).toBe(400)
    const body = await res.json() as { error: string }
    expect(body.error).toBe('path is required')
  })

  it('returns 400 when path does not exist on disk', async () => {
    const res = await makeApp().request('/api/config/targets/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'target-bad-path', target: { path: '/nonexistent/path/abc123' } }),
    })
    expect(res.status).toBe(400)
    const body = await res.json() as { error: string }
    expect(body.error).toContain('path does not exist')
  })

  it('accepts valid existing path', async () => {
    const res = await makeApp().request('/api/config/targets/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'target-valid-path', target: { path: tmpDir } }),
    })
    // Should NOT be 400 — path validation passes
    expect(res.status).not.toBe(400)
  })
})

describe('PUT /api/config/targets/:name — path validation', () => {
  it('returns 400 when path is empty string', async () => {
    const res = await makeApp().request('/api/config/targets/my-target', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target: { path: '' } }),
    })
    expect(res.status).toBe(400)
    const body = await res.json() as { error: string }
    expect(body.error).toBe('path is required')
  })

  it('returns 400 when path does not exist on disk', async () => {
    const res = await makeApp().request('/api/config/targets/my-target', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target: { path: '/nonexistent/path/xyz789' } }),
    })
    expect(res.status).toBe(400)
    const body = await res.json() as { error: string }
    expect(body.error).toContain('path does not exist')
  })

  it('accepts valid existing path', async () => {
    const res = await makeApp().request('/api/config/targets/my-target', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target: { path: tmpDir } }),
    })
    expect(res.status).not.toBe(400)
  })
})
