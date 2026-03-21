import { Hono } from 'hono'
import { randomUUID } from 'node:crypto'
import { readTargets, writeTargets, loadOrCreateAppConfig } from '../services/yaml-store.ts'
import { listRuns, getRun, appendRun } from '../services/run-store.ts'
import { sendToWorker, workerStatus, getLastWorkerState } from '../ipc.ts'
import type { Run, Target } from '../../shared/types.ts'
import { MIN_SCHEDULE_INTERVAL_HOURS } from '../../shared/constants.ts'

export const apiRoutes = new Hono()

// GET /api/targets — list all targets
apiRoutes.get('/api/targets', async (c) => {
  const targets = await readTargets()
  return c.json(Object.values(targets))
})

// GET /api/targets/:name — single target
apiRoutes.get('/api/targets/:name', async (c) => {
  const targets = await readTargets()
  const target = targets[c.req.param('name')]
  if (!target) return c.json({ error: 'not found' }, 404)
  return c.json(target)
})

// POST /api/runs — trigger a run
apiRoutes.post('/api/runs', async (c) => {
  if (workerStatus !== 'online') return c.json({ error: 'worker offline' }, 503)
  const body = await c.req.json<{ target: string; mode: Run['mode']; custom_prompt?: string; self_repair?: boolean }>()
  const run: Run = {
    id: randomUUID(),
    target: body.target,
    mode: body.mode,
    trigger: 'manual',
    status: 'queued',
    queued_at: new Date().toISOString(),
    custom_prompt: body.custom_prompt,
    log_path: '',
  }
  run.log_path = `runs/${run.id}/log.jsonl`
  await appendRun(run)
  sendToWorker({ type: 'enqueue', run })
  return c.json({ run_id: run.id }, 202)
})

// GET /api/worker/state — current queue snapshot (polling endpoint for frontend)
apiRoutes.get('/api/worker/state', (c) => {
  return c.json(getLastWorkerState())
})

// GET /api/runs — list runs (filterable by status + target)
apiRoutes.get('/api/runs', async (c) => {
  const status = c.req.query('status')
  const target = c.req.query('target')
  const runs = await listRuns({ status: status ?? undefined, target: target ?? undefined })
  return c.json(runs)
})

// GET /api/runs/:id — single run detail
apiRoutes.get('/api/runs/:id', async (c) => {
  const run = await getRun(c.req.param('id'))
  if (!run) return c.json({ error: 'not found' }, 404)
  return c.json(run)
})

// DELETE /api/runs/:id — cancel a run
apiRoutes.delete('/api/runs/:id', async (c) => {
  if (workerStatus === 'offline_permanent') return c.json({ error: 'worker offline' }, 503)
  const ok = sendToWorker({ type: 'cancel', run_id: c.req.param('id') })
  return c.json({ ok })
})

// PUT /api/targets/:name — update target config with per-target schedule override validation (D-13)
apiRoutes.put('/api/targets/:name', async (c) => {
  const name = c.req.param('name')
  const body = await c.req.json<Partial<Target>>()

  // D-13: Reject if schedule.interval_hours is below minimum (defense in depth — also enforced in scheduler)
  if (body.schedule?.interval_hours !== undefined) {
    if (body.schedule.interval_hours < MIN_SCHEDULE_INTERVAL_HOURS) {
      return c.json(
        {
          error: `interval_hours ${body.schedule.interval_hours} is below minimum ${MIN_SCHEDULE_INTERVAL_HOURS} hours (${Math.round(MIN_SCHEDULE_INTERVAL_HOURS * 60)} minutes)`,
        },
        400
      )
    }
  }

  const targets = await readTargets()
  if (!targets[name]) return c.json({ error: 'target not found' }, 404)

  // Merge schedule override into existing target
  if (body.schedule) {
    targets[name].schedule = { ...targets[name].schedule, ...body.schedule }
  }

  await writeTargets(targets)

  // Trigger scheduler restart with updated targets — worker will reload targets and rebuild all per-target timers (D-10)
  const config = await loadOrCreateAppConfig()
  sendToWorker({ type: 'schedule', config: config.schedule })

  return c.json(targets[name])
})

// POST /api/webhook — external trigger (optional target + mode)
apiRoutes.post('/api/webhook', async (c) => {
  if (workerStatus !== 'online') return c.json({ error: 'worker offline' }, 503)
  const body = await c.req.json<{ target?: string; mode?: Run['mode'] }>().catch(() => ({} as { target?: string; mode?: Run['mode'] }))
  const run: Run = {
    id: randomUUID(),
    target: body.target ?? '__all__',
    mode: body.mode ?? 'production',
    trigger: 'webhook',
    status: 'queued',
    queued_at: new Date().toISOString(),
    log_path: '',
  }
  run.log_path = `runs/${run.id}/log.jsonl`
  await appendRun(run)
  sendToWorker({ type: 'enqueue', run })
  return c.json({ run_id: run.id }, 202)
})
