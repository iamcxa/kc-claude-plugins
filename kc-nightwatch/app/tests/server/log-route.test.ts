import { describe, it, expect, beforeAll, afterAll, mock } from 'bun:test'
import { Hono } from 'hono'
import { mkdirSync, writeFileSync, rmSync, existsSync } from 'node:fs'
import path from 'node:path'

// Mock IPC to prevent SSE routes from trying to subscribe to worker IPC in test context
mock.module('../../server/ipc.ts', () => ({
  subscribeToRun: () => () => {},
  subscribeGlobal: () => () => {},
  workerStatus: 'offline',
  getLastWorkerState: () => ({ queue: [], active: [] }),
  lastHeartbeatAt: null,
  workerProc: null,
  setWorkerProc: () => {},
  setWorkerStatus: () => {},
  fanOutLogEvent: () => {},
  closeRunSubscribers: () => {},
  broadcastGlobal: () => {},
  handleWorkerMessage: () => {},
  sendToWorker: () => false,
  startHeartbeatWatchdog: () => setInterval(() => {}, 99999),
}))

// Import streamRoutes AFTER mocking IPC
const { streamRoutes } = await import('../../server/routes/stream.ts')

// Test UUID and path setup — uses real RUNS_DIR so the route can resolve the file
const RUNS_DIR = path.resolve(import.meta.dir, '../../../runs')
const TEST_RUN_ID = '00000000-0000-0000-0000-000000000099'
const testRunDir = path.join(RUNS_DIR, TEST_RUN_ID)

const SAMPLE_LINES = [
  '{"type":"system","subtype":"init","session_id":"test-session"}',
  '{"type":"assistant","subtype":"text","text":"Starting Phase 1..."}',
  '{"type":"tool_use","name":"Bash","id":"tool-001","input":{"command":"echo hello"}}',
  '{"type":"result","result":"Run complete","stop_reason":"end_turn"}',
]

beforeAll(() => {
  mkdirSync(testRunDir, { recursive: true })
  writeFileSync(path.join(testRunDir, 'log.jsonl'), SAMPLE_LINES.join('\n') + '\n')
})

afterAll(() => {
  rmSync(testRunDir, { recursive: true, force: true })
})

function makeApp() {
  const app = new Hono()
  app.route('/', streamRoutes)
  return app
}

describe('GET /api/runs/:id/log', () => {
  it('returns 200 with lines array for existing log', async () => {
    const res = await makeApp().request(`/api/runs/${TEST_RUN_ID}/log`)
    expect(res.status).toBe(200)
    const body = await res.json() as { lines: string[] }
    expect(Array.isArray(body.lines)).toBe(true)
    expect(body.lines.length).toBeGreaterThan(0)
  })

  it('returns 404 for non-existent run', async () => {
    const res = await makeApp().request('/api/runs/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/log')
    expect(res.status).toBe(404)
    const body = await res.json() as { error: string }
    expect(body.error).toBe('log not found')
  })

  it('returns 400 for invalid run ID format', async () => {
    const res = await makeApp().request('/api/runs/not-a-uuid/log')
    expect(res.status).toBe(400)
    const body = await res.json() as { error: string }
    expect(body.error).toBe('invalid run id')
  })

  it('returns raw JSONL strings, not parsed objects', async () => {
    const res = await makeApp().request(`/api/runs/${TEST_RUN_ID}/log`)
    const body = await res.json() as { lines: string[] }
    // Each line should be a string (raw JSONL), not a parsed object
    for (const line of body.lines) {
      expect(typeof line).toBe('string')
      // Should be valid JSON when parsed
      expect(() => JSON.parse(line)).not.toThrow()
    }
  })
})
