import type { Run, ScheduleConfig } from '../shared/types.ts'
import { log } from '../shared/logger.ts'
import { randomUUID } from 'node:crypto'
import { SCHEDULER_RUNS_ALL_TARGET } from '../shared/constants.ts'

let schedulerTimer: ReturnType<typeof setInterval> | null = null
let nextRunAt: number | null = null

export function startScheduler(
  config: ScheduleConfig,
  enqueue: (run: Run) => void
): void {
  stopScheduler()
  if (!config.enabled || !config.interval_hours) {
    log.info({ component: 'worker', msg: 'Scheduler disabled or no interval set' })
    return
  }
  const intervalMs = config.interval_hours * 3_600_000
  nextRunAt = Date.now() + intervalMs
  log.info({ component: 'worker', msg: `Scheduler started: every ${config.interval_hours}h. Next run at ${new Date(nextRunAt).toISOString()}` })
  schedulerTimer = setInterval(() => {
    nextRunAt = Date.now() + intervalMs
    log.info({ component: 'worker', msg: 'Scheduled interval triggered — enqueuing run' })
    const runId = randomUUID()
    const run: Run = {
      id: runId,
      target: SCHEDULER_RUNS_ALL_TARGET,
      mode: config.self_repair_before ? 'self-repair' : 'production',
      trigger: 'interval',
      status: 'queued',
      log_path: `runs/${runId}/log.jsonl`,
    }
    enqueue(run)
  }, intervalMs)
}

export function stopScheduler(): void {
  if (schedulerTimer) {
    clearInterval(schedulerTimer)
    schedulerTimer = null
    log.info({ component: 'worker', msg: 'Scheduler stopped' })
  }
  nextRunAt = null
}

export function getNextRunAt(): number | null {
  return nextRunAt
}
