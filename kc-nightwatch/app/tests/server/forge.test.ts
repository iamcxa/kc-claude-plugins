import { describe, it, expect, beforeEach, afterEach, spyOn } from 'bun:test'
import { Hono } from 'hono'
import * as yamlStore from '../../server/services/yaml-store.ts'

// ============================================================
// Spy declarations
// ============================================================
let readYamlFileSpy: ReturnType<typeof spyOn>

// Import routes — spyOn patches in beforeEach
const { forgeRoutes } = await import('../../server/routes/forge.ts')

// ============================================================
// Test app
// ============================================================
const testApp = new Hono()
testApp.route('/', forgeRoutes)

describe('forge api', () => {
  beforeEach(() => {
    readYamlFileSpy = spyOn(yamlStore, 'readYamlFile').mockImplementation(async () => null)
  })

  afterEach(() => {
    readYamlFileSpy.mockRestore()
  })

  it('GET /api/forge/results returns 200 when self-repair YAML is missing', async () => {
    readYamlFileSpy.mockImplementation(async () => null)
    const res = await testApp.request('/api/forge/results')
    expect(res.status).toBe(200)
    const data = await res.json() as { forge_result: null; run_date: null; stale: boolean }
    expect(data.forge_result).toBeNull()
    expect(data.run_date).toBeNull()
    expect(data.stale).toBe(true)
  })

  it('GET /api/forge/results returns forge_result from YAML data', async () => {
    readYamlFileSpy.mockImplementation(async () => ({
      run_date: '2026-03-25T00:00:00Z',
      forge_result: { status: 'pass', branch: null, details: '0 FAIL' },
    }))
    const res = await testApp.request('/api/forge/results')
    expect(res.status).toBe(200)
    const data = await res.json() as { forge_result: { status: string; branch: null; details: string } }
    expect(data.forge_result).not.toBeNull()
    expect(data.forge_result?.status).toBe('pass')
    expect(data.forge_result?.details).toBe('0 FAIL')
  })

  it('GET /api/forge/results returns stale: true when run_date > 36 hours ago', async () => {
    const threeDaysAgo = new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
    readYamlFileSpy.mockImplementation(async () => ({
      run_date: threeDaysAgo,
      forge_result: { status: 'pass', branch: null, details: 'ok' },
    }))
    const res = await testApp.request('/api/forge/results')
    const data = await res.json() as { stale: boolean }
    expect(data.stale).toBe(true)
  })

  it('GET /api/forge/results returns stale: false when run_date < 36 hours ago', async () => {
    const oneHourAgo = new Date(Date.now() - 3600000).toISOString()
    readYamlFileSpy.mockImplementation(async () => ({
      run_date: oneHourAgo,
      forge_result: { status: 'pass', branch: null, details: 'ok' },
    }))
    const res = await testApp.request('/api/forge/results')
    const data = await res.json() as { stale: boolean }
    expect(data.stale).toBe(false)
  })

  it('GET /api/forge/results returns stale: true when run_date is missing', async () => {
    readYamlFileSpy.mockImplementation(async () => ({
      forge_result: { status: 'fail', branch: 'fix', details: 'err' },
    }))
    const res = await testApp.request('/api/forge/results')
    const data = await res.json() as { stale: boolean; run_date: null }
    expect(data.stale).toBe(true)
    expect(data.run_date).toBeNull()
  })

  it('GET /api/forge/results returns forge_result: null when YAML has no forge_result field', async () => {
    readYamlFileSpy.mockImplementation(async () => ({
      run_date: '2026-03-25T00:00:00Z',
    }))
    const res = await testApp.request('/api/forge/results')
    const data = await res.json() as { forge_result: null; run_date: string }
    expect(data.forge_result).toBeNull()
    expect(data.run_date).toBe('2026-03-25T00:00:00Z')
  })
})
