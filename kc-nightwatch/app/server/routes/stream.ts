import { Hono } from 'hono'
import { streamSSE } from 'hono/streaming'
import { subscribeToRun } from '../ipc.ts'

export const streamRoutes = new Hono()

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
