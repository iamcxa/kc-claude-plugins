import type { Run, ScheduleConfig, Target } from '../shared/types.ts'
import { log } from '../shared/logger.ts'
import { randomUUID } from 'node:crypto'
import { MIN_SCHEDULE_INTERVAL_HOURS } from '../shared/constants.ts'

// Per-target timer map (D-08) — replaces single schedulerTimer
const schedulerTimers: Map<string, ReturnType<typeof setInterval>> = new Map()
const nextRunAtMap: Map<string, number> = new Map()

/**
 * Start independent scheduler timers for each target (D-08, D-09, D-10).
 * Each target reads target.schedule?.interval_hours ?? globalConfig.interval_hours.
 * Timers below MIN_SCHEDULE_INTERVAL_HOURS are skipped with a warning (D-14).
 * Always calls stopAllSchedulers() first to prevent timer leaks (D-11, Pitfall 3).
 */
export function startPerTargetSchedulers(
  config: ScheduleConfig,
  targets: Record<string, Target>,
  enqueue: (run: Run) => void
): void {
  stopAllSchedulers()
  if (!config.enabled) {
    log.info({ component: 'scheduler', msg: 'Scheduler disabled — no timers created' })
    return
  }

  const globalInterval = config.interval_hours
  for (const [name, target] of Object.entries(targets)) {
    // D-09: per-target interval with global fallback
    const hours = target.schedule?.interval_hours ?? globalInterval
    if (!hours) {
      log.info({ component: 'scheduler', msg: `Target '${name}': no interval configured — skipping` })
      continue
    }

    // D-14: minimum interval enforcement at scheduler level
    if (hours < MIN_SCHEDULE_INTERVAL_HOURS) {
      log.warn({
        component: 'scheduler',
        msg: `Target '${name}': interval ${hours}h is below minimum ${MIN_SCHEDULE_INTERVAL_HOURS}h — skipping timer`,
      })
      continue
    }

    const intervalMs = hours * 3_600_000
    nextRunAtMap.set(name, Date.now() + intervalMs)
    log.info({
      component: 'scheduler',
      msg: `Target '${name}': scheduler started — every ${hours}h. Next at ${new Date(Date.now() + intervalMs).toISOString()}`,
    })

    const timer = setInterval(() => {
      nextRunAtMap.set(name, Date.now() + intervalMs)
      log.info({ component: 'scheduler', msg: `Scheduled interval fired for target '${name}'` })
      const runId = randomUUID()
      const run: Run = {
        id: runId,
        target: name,  // per-target, not __all__ — each target gets its own run
        mode: config.self_repair_before ? 'self-repair' : 'production',
        trigger: 'interval',
        status: 'queued',
        queued_at: new Date().toISOString(),
        log_path: `runs/${runId}/log.jsonl`,
      }
      enqueue(run)
    }, intervalMs)
    schedulerTimers.set(name, timer)
  }

  if (schedulerTimers.size === 0 && config.enabled) {
    log.info({ component: 'scheduler', msg: 'Scheduler enabled but no targets have valid intervals — no timers created' })
  }
}

/**
 * Stop all per-target scheduler timers (D-11).
 * Clears the full Map to prevent timer leaks (Pitfall 3).
 */
export function stopAllSchedulers(): void {
  if (schedulerTimers.size > 0) {
    log.info({ component: 'scheduler', msg: `Stopping ${schedulerTimers.size} scheduler timer(s)` })
  }
  for (const timer of schedulerTimers.values()) clearInterval(timer)
  schedulerTimers.clear()
  nextRunAtMap.clear()
}

/**
 * Get the next scheduled run time for a specific target.
 * Returns null if target has no active timer.
 */
export function getNextRunAtForTarget(targetName: string): number | null {
  return nextRunAtMap.get(targetName) ?? null
}

/**
 * Get all next-run-at timestamps (for IPC state reporting).
 */
export function getAllNextRunAt(): Record<string, number> {
  return Object.fromEntries(nextRunAtMap)
}

// ============================================================
// Deprecated aliases — backward compatibility for worker/index.ts imports
// These will be removed once Task 2 updates worker/index.ts imports
// ============================================================

/** @deprecated Use startPerTargetSchedulers() instead */
export function startScheduler(config: ScheduleConfig, enqueue: (run: Run) => void): void {
  log.warn({ component: 'scheduler', msg: 'startScheduler() is deprecated — use startPerTargetSchedulers()' })
  startPerTargetSchedulers(config, {}, enqueue)
}

/** @deprecated Use stopAllSchedulers() instead */
export const stopScheduler = stopAllSchedulers

/** @deprecated Use getNextRunAtForTarget() instead. Returns earliest next-run-at across all targets. */
export function getNextRunAt(): number | null {
  const values = [...nextRunAtMap.values()]
  return values.length > 0 ? Math.min(...values) : null
}
