/**
 * Tests for worker/scheduler.ts — SCHED-01 (interval scheduler)
 */

import { describe, it, expect, afterEach } from 'bun:test'
import { startScheduler, stopScheduler, getNextRunAt } from '../../worker/scheduler.ts'
import type { Run, ScheduleConfig } from '../../shared/types.ts'

afterEach(() => {
  stopScheduler()
})

const makeRun = (): Run => ({
  id: 'scheduled-run',
  target: '__all__',
  mode: 'production',
  trigger: 'interval',
  status: 'queued',
  log_path: '',
})

describe('startScheduler — disabled config', () => {
  it('does nothing when enabled=false', () => {
    const config: ScheduleConfig = { enabled: false, self_repair_before: false }
    const enqueued: Run[] = []
    startScheduler(config, (r) => enqueued.push(r))
    expect(getNextRunAt()).toBeNull()
    expect(enqueued.length).toBe(0)
  })

  it('does nothing when interval_hours is missing (undefined)', () => {
    const config: ScheduleConfig = { enabled: true, self_repair_before: false }
    const enqueued: Run[] = []
    startScheduler(config, (r) => enqueued.push(r))
    expect(getNextRunAt()).toBeNull()
    expect(enqueued.length).toBe(0)
  })
})

describe('startScheduler — enabled config', () => {
  it('sets nextRunAt when started with valid config', () => {
    const before = Date.now()
    const config: ScheduleConfig = { enabled: true, interval_hours: 2, self_repair_before: false }
    const enqueued: Run[] = []
    startScheduler(config, (r) => enqueued.push(r))
    const nextRun = getNextRunAt()
    expect(nextRun).not.toBeNull()
    expect(nextRun!).toBeGreaterThan(before)
    // nextRunAt should be ~2 hours from now
    expect(nextRun!).toBeGreaterThanOrEqual(before + 2 * 3_600_000 - 100)
    expect(nextRun!).toBeLessThanOrEqual(before + 2 * 3_600_000 + 100)
  })

  it('fires callback after interval (using very short interval for testing)', async () => {
    // 0.001 hours = 3600ms — too slow for unit test
    // Use 1/360000 hours ≈ 0.01ms = still 10ms. Go lower: 1/3600000 hours = 1ms
    // The smallest meaningful value: 1ms interval via fractional hours
    const ONE_MS_IN_HOURS = 1 / 3_600_000
    const config: ScheduleConfig = { enabled: true, interval_hours: ONE_MS_IN_HOURS, self_repair_before: false }
    const enqueued: Run[] = []
    startScheduler(config, (r) => enqueued.push(r))
    // Wait for timer to fire at least once (1ms interval, wait 50ms)
    await new Promise(r => setTimeout(r, 50))
    expect(enqueued.length).toBeGreaterThanOrEqual(1)
    // Enqueued run should have target '__all__'
    expect(enqueued[0]!.target).toBe('__all__')
    expect(enqueued[0]!.trigger).toBe('interval')
    expect(enqueued[0]!.status).toBe('queued')
  })

  it('replaces existing timer when called again (stopScheduler + restart)', () => {
    const config1: ScheduleConfig = { enabled: true, interval_hours: 1, self_repair_before: false }
    const config2: ScheduleConfig = { enabled: true, interval_hours: 2, self_repair_before: false }
    const enqueued: Run[] = []

    startScheduler(config1, (r) => enqueued.push(r))
    const first = getNextRunAt()

    startScheduler(config2, (r) => enqueued.push(r))
    const second = getNextRunAt()

    // Second timer replaces first; nextRunAt should be ~2h not ~1h
    expect(second).not.toBeNull()
    expect(second!).toBeGreaterThan(first! + 3_600_000 - 100)
  })
})

describe('stopScheduler', () => {
  it('clears nextRunAt', () => {
    const config: ScheduleConfig = { enabled: true, interval_hours: 1, self_repair_before: false }
    startScheduler(config, () => {})
    expect(getNextRunAt()).not.toBeNull()
    stopScheduler()
    expect(getNextRunAt()).toBeNull()
  })

  it('is idempotent — calling twice does not throw', () => {
    expect(() => {
      stopScheduler()
      stopScheduler()
    }).not.toThrow()
  })
})

describe('getNextRunAt', () => {
  it('returns null before any scheduler starts', () => {
    // afterEach calls stopScheduler, so this should be null
    expect(getNextRunAt()).toBeNull()
  })

  it('returns null after stopScheduler', () => {
    const config: ScheduleConfig = { enabled: true, interval_hours: 1, self_repair_before: false }
    startScheduler(config, () => {})
    stopScheduler()
    expect(getNextRunAt()).toBeNull()
  })
})
