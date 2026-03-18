import { Hono } from 'hono'
import { loadOrCreateAppConfig, writeAppConfig } from '../services/yaml-store.ts'
import { sendToWorker } from '../ipc.ts'
import type { ScheduleConfig } from '../../shared/types.ts'

export const scheduleRoutes = new Hono()

// GET /api/schedule — current scheduler state
scheduleRoutes.get('/api/schedule', async (c) => {
  const config = await loadOrCreateAppConfig()
  return c.json(config.schedule)
})

// PUT /api/schedule — update scheduler config
scheduleRoutes.put('/api/schedule', async (c) => {
  const body = await c.req.json<Partial<ScheduleConfig>>()
  const config = await loadOrCreateAppConfig()
  const updated: ScheduleConfig = {
    enabled: body.enabled ?? config.schedule.enabled,
    interval_hours: body.interval_hours ?? config.schedule.interval_hours,
    self_repair_before: body.self_repair_before ?? config.schedule.self_repair_before,
  }
  config.schedule = updated
  await writeAppConfig(config)
  sendToWorker({ type: 'schedule', config: updated })
  return c.json(updated)
})
