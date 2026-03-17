import { describe, it, expect } from 'bun:test'
import {
  WORKER_RESTART_BACKOFF_MS,
  MAX_WORKER_RESTARTS,
} from '../../shared/constants.ts'

describe('crash recovery constants', () => {
  it('has 3-element backoff array', () => {
    expect(WORKER_RESTART_BACKOFF_MS).toHaveLength(3)
  })

  it('first backoff is 2000ms', () => {
    expect(WORKER_RESTART_BACKOFF_MS[0]).toBe(2000)
  })

  it('second backoff is 5000ms', () => {
    expect(WORKER_RESTART_BACKOFF_MS[1]).toBe(5000)
  })

  it('third backoff is 15000ms', () => {
    expect(WORKER_RESTART_BACKOFF_MS[2]).toBe(15_000)
  })

  it('MAX_WORKER_RESTARTS is 3', () => {
    expect(MAX_WORKER_RESTARTS).toBe(3)
  })
})

// Integration test: the actual crash recovery behavior requires spawning real processes.
// See VALIDATION.md manual verification section: "Worker auto-restart 3x with backoff"
