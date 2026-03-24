import { describe, it, expect, mock, afterAll, beforeAll, beforeEach, afterEach, spyOn } from 'bun:test'
import { Hono } from 'hono'
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import path from 'node:path'
import os from 'node:os'
import * as yamlStore from '../../server/services/yaml-store.ts'
import * as configValidator from '../../server/services/config-validator.ts'
import * as ipc from '../../server/ipc.ts'

// Create a real temp directory for "valid path" tests
const tmpDir = mkdtempSync(path.join(os.tmpdir(), 'nw-test-'))

// Import routes — spyOn patches are set up in beforeEach
const { configRoutes } = await import('../../server/routes/config.ts')

function makeApp() {
  const app = new Hono()
  app.route('/', configRoutes)
  return app
}

// Spy declarations
let readTargetsSpy: ReturnType<typeof spyOn>
let writeTargetsSpy: ReturnType<typeof spyOn>
let readYamlFileSpy: ReturnType<typeof spyOn>
let writeYamlFileSpy: ReturnType<typeof spyOn>
let loadOrCreateAppConfigSpy: ReturnType<typeof spyOn>
let writeAppConfigSpy: ReturnType<typeof spyOn>
let withWriteLockSpy: ReturnType<typeof spyOn>
let validateConfigSaveSpy: ReturnType<typeof spyOn>
let sendToWorkerSpy: ReturnType<typeof spyOn>

beforeAll(() => {
  // No temp targets YAML needed — withWriteLock is mocked via spyOn
})

afterAll(() => {
  rmSync(tmpDir, { recursive: true, force: true })
})

beforeEach(() => {
  readTargetsSpy = spyOn(yamlStore, 'readTargets').mockResolvedValue({})
  writeTargetsSpy = spyOn(yamlStore, 'writeTargets').mockResolvedValue(undefined)
  readYamlFileSpy = spyOn(yamlStore, 'readYamlFile').mockResolvedValue({})
  writeYamlFileSpy = spyOn(yamlStore, 'writeYamlFile').mockResolvedValue(undefined)
  loadOrCreateAppConfigSpy = spyOn(yamlStore, 'loadOrCreateAppConfig').mockResolvedValue({
    host: '127.0.0.1',
    port: 3200,
    schedule: { enabled: false, self_repair_before: true },
    max_concurrent_runs: 1 as const,
    plugins_dir: '/tmp/plugins',
  })
  writeAppConfigSpy = spyOn(yamlStore, 'writeAppConfig').mockResolvedValue(undefined)
  // withWriteLock: execute the callback (mimics real behavior without file writes)
  withWriteLockSpy = spyOn(configValidator, 'withWriteLock').mockImplementation(async (_file: string, fn: () => Promise<unknown>) => fn())
  validateConfigSaveSpy = spyOn(configValidator, 'validateConfigSave').mockResolvedValue({ valid: true, step: 'ready' as const })
  sendToWorkerSpy = spyOn(ipc, 'sendToWorker').mockReturnValue(false)
})

afterEach(() => {
  readTargetsSpy.mockRestore()
  writeTargetsSpy.mockRestore()
  readYamlFileSpy.mockRestore()
  writeYamlFileSpy.mockRestore()
  loadOrCreateAppConfigSpy.mockRestore()
  writeAppConfigSpy.mockRestore()
  withWriteLockSpy.mockRestore()
  validateConfigSaveSpy.mockRestore()
  sendToWorkerSpy.mockRestore()
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
