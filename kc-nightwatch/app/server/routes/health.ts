import { Hono } from 'hono'
import { workerStatus, lastHeartbeatAt } from '../ipc.ts'

export const healthRoutes = new Hono()

healthRoutes.get('/health', (c) => {
  const isOnline = workerStatus === 'online'
  return c.json({
    status: isOnline ? 'ok' : 'degraded',
    worker: workerStatus,
    last_heartbeat: lastHeartbeatAt,
    uptime: process.uptime(),
  }, isOnline ? 200 : 200)
})
