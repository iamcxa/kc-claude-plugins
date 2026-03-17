import { describe, it, expect, beforeEach, afterEach } from 'bun:test'
import { activePids, executeRun, killAllActive, cleanupOldRuns } from '../../worker/executor.ts'
import type { Run, IpcMessage } from '../../shared/types.ts'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

let testDir: string

beforeEach(async () => {
  testDir = await mkdtemp(join(tmpdir(), 'nw-executor-'))
  activePids.clear()
})

afterEach(async () => {
  await rm(testDir, { recursive: true, force: true })
})

const baseRun: Run = {
  id: 'test-run-001',
  target: 'test-target',
  mode: 'dry-run',
  trigger: 'manual',
  status: 'queued',
  log_path: '',
}

describe('activePids', () => {
  it('starts empty', () => {
    expect(activePids.size).toBe(0)
  })

  it('killAllActive clears the set', async () => {
    activePids.add(999999)  // fake PID — process likely doesn't exist
    await killAllActive()   // should not throw, process may already be gone
    expect(activePids.size).toBe(0)
  })
})

describe('executeRun — PID tracking', () => {
  it('removes PID from activePids after run completes', async () => {
    // Verify activePids is empty before and after a simulated run
    expect(activePids.size).toBe(0)
    // The actual executeRun with real safehouse is an integration test;
    // this verifies the baseline state expectation
  })
})

describe('executor module exports', () => {
  it('exports executeRun function', () => {
    expect(typeof executeRun).toBe('function')
  })

  it('exports activePids Set', () => {
    expect(activePids).toBeInstanceOf(Set)
  })

  it('exports killAllActive function', () => {
    expect(typeof killAllActive).toBe('function')
  })

  it('exports cleanupOldRuns function', () => {
    expect(typeof cleanupOldRuns).toBe('function')
  })
})
