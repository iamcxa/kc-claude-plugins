import { describe, it, expect, afterEach } from 'bun:test'
import { Hono } from 'hono'
import { scheduleRoutes } from '../../server/routes/schedule.ts'
import { setWorkerStatus } from '../../server/ipc.ts'
import { writeYamlFile } from '../../server/services/yaml-store.ts'
import { stringify } from 'yaml'
import os from 'node:os'
import path from 'node:path'

// Use a temp file for schedule tests to avoid touching real config
const TEST_CONFIG_PATH = path.join(os.tmpdir(), `nightwatch-app-test-${Date.now()}.yaml`)

const app = new Hono()
app.route('/', scheduleRoutes)

async function writeTestConfig(schedule: Record<string, unknown>) {
  await writeYamlFile(TEST_CONFIG_PATH, {
    host: '127.0.0.1',
    port: 3200,
    max_concurrent_runs: 1,
    plugins_dir: '/tmp/.claude/plugins/local',
    schedule,
  })
}

afterEach(async () => {
  // Clean up temp file
  try {
    await Bun.file(TEST_CONFIG_PATH).exists() && await Bun.spawn(['rm', '-f', TEST_CONFIG_PATH]).exited
  } catch { /* ignore */ }
})

describe('GET /api/schedule', () => {
  it('returns schedule object from config', async () => {
    await writeTestConfig({ enabled: true, interval_hours: 4, self_repair_before: true })

    const res = await app.request('/api/schedule', {
      headers: { 'X-Config-Path': TEST_CONFIG_PATH },
    })
    expect(res.status).toBe(200)
    const body = await res.json() as Record<string, unknown>
    expect(body.enabled).toBeDefined()
  })
})

describe('PUT /api/schedule', () => {
  it('validates and updates schedule config', async () => {
    await writeTestConfig({ enabled: false, self_repair_before: true })

    const res = await app.request('/api/schedule', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'X-Config-Path': TEST_CONFIG_PATH },
      body: JSON.stringify({ enabled: true, interval_hours: 6, self_repair_before: true }),
    })
    expect(res.status).toBe(200)
    const body = await res.json() as Record<string, unknown>
    expect(body.enabled).toBe(true)
    expect(body.interval_hours).toBe(6)
  })
})
