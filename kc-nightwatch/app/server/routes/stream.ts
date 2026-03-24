import { Hono } from 'hono'
import { streamSSE } from 'hono/streaming'
import { subscribeToRun, subscribeGlobal } from '../ipc.ts'
import path from 'node:path'

export const streamRoutes = new Hono()

const RUNS_DIR = path.resolve(import.meta.dir, '../../../runs')

// GET /api/runs/:id/log — fetch completed run log as raw JSONL lines
streamRoutes.get('/api/runs/:id/log', async (c) => {
  const runId = c.req.param('id')

  // Validate runId format (UUID) to prevent path traversal
  if (!/^[0-9a-f-]{36}$/i.test(runId)) {
    return c.json({ error: 'invalid run id' }, 400)
  }

  const logPath = path.join(RUNS_DIR, runId, 'log.jsonl')
  const exists = await Bun.file(logPath).exists()
  if (!exists) {
    return c.json({ error: 'log not found' }, 404)
  }

  const text = await Bun.file(logPath).text()
  const lines = text.split('\n').filter(Boolean)
  return c.json({ lines })
})

// GET /api/runs/:id/stream — SSE fan-out for real-time log streaming
streamRoutes.get('/api/runs/:id/stream', (c) => {
  const runId = c.req.param('id')
  return streamSSE(c, async (stream) => {
    const unsub = subscribeToRun(runId, stream, c.req.raw.signal)

    // 60s keepalive ping — prevents idle connection timeout
    const pingTimer = setInterval(() => {
      void stream.writeSSE({ data: '', event: 'ping' })
    }, 60_000)

    // Max 35 min (safety.yaml max_runtime_minutes = 30, plus buffer)
    await stream.sleep(35 * 60_000)

    clearInterval(pingTimer)
    unsub()
  })
})

// GET /api/events — global SSE for lifecycle events (brief-ready, config-changed)
streamRoutes.get('/api/events', (c) => {
  return streamSSE(c, async (stream) => {
    const unsub = subscribeGlobal(stream, c.req.raw.signal)
    const pingTimer = setInterval(() => {
      void stream.writeSSE({ data: '', event: 'ping' })
    }, 60_000)
    // 1 hour max connection
    await stream.sleep(60 * 60_000)
    clearInterval(pingTimer)
    unsub()
  })
})
