import { describe, it, expect } from 'bun:test'
import {
  HEARTBEAT_INTERVAL_MS,
  HEARTBEAT_TIMEOUT_MS,
  MAX_WORKER_RESTARTS,
  RESULT_FORCE_KILL_DELAY_MS,
  KEEP_RUNS_COUNT,
  MIN_SCHEDULE_INTERVAL_HOURS,
} from '../../shared/constants.ts'

describe('constants', () => {
  it('heartbeat interval is 30 seconds', () => expect(HEARTBEAT_INTERVAL_MS).toBe(30_000))
  it('heartbeat timeout is 90 seconds (3 missed)', () => expect(HEARTBEAT_TIMEOUT_MS).toBe(90_000))
  it('max worker restarts is 3', () => expect(MAX_WORKER_RESTARTS).toBe(3))
  it('force kill delay is 10 seconds', () => expect(RESULT_FORCE_KILL_DELAY_MS).toBe(10_000))
  it('keep runs count is 50', () => expect(KEEP_RUNS_COUNT).toBe(50))
})

describe('MIN_SCHEDULE_INTERVAL_HOURS (Phase 8)', () => {
  it('MIN_SCHEDULE_INTERVAL_HOURS is 10 minutes in hours', () => {
    expect(MIN_SCHEDULE_INTERVAL_HOURS).toBeCloseTo(1 / 6, 5)
    expect(MIN_SCHEDULE_INTERVAL_HOURS * 60).toBeCloseTo(10, 1) // 10 minutes
  })
})
