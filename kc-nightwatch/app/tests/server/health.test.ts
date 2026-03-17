import { describe, it, expect } from 'bun:test'
import { Hono } from 'hono'
import { healthRoutes } from '../../server/routes/health.ts'
import { setWorkerStatus } from '../../server/ipc.ts'

const app = new Hono()
app.route('/', healthRoutes)

describe('GET /health', () => {
  it('returns degraded when worker is offline', async () => {
    setWorkerStatus('offline')
    const res = await app.request('/health')
    const body = await res.json() as Record<string, unknown>
    expect(body.worker).toBe('offline')
    expect(body.status).toBe('degraded')
  })

  it('returns ok when worker is online', async () => {
    setWorkerStatus('online')
    const res = await app.request('/health')
    const body = await res.json() as Record<string, unknown>
    expect(body.worker).toBe('online')
    expect(body.status).toBe('ok')
  })
})
