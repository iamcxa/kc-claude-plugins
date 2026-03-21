/**
 * Tests for execution queue (EXEC-09), cancel (EXEC-08), and per-target queue isolation (PARA-01)
 * These tests exercise queue logic in isolation using module-level helpers.
 */

import { describe, it, expect } from 'bun:test'
import { SCHEDULER_RUNS_ALL_TARGET } from '../../shared/constants.ts'

// Inline queue logic tested in isolation (avoids importing worker/index.ts which has top-level await)
// The queue module logic is extracted here for unit testing

interface Run {
  id: string
  target: string
  mode: string
  trigger: string
  status: string
  log_path: string
}

// ============================================================
// Per-target queue model (PARA-01) helper — mirrors worker/index.ts implementation
// ============================================================
function makeQueue() {
  const targetQueues: Map<string, Run[]> = new Map()
  const activeRuns: Map<string, Run> = new Map()
  const completedRuns: Run[] = []
  const sentStates: Array<{ active: Run[]; queue: Run[] }> = []
  const rejections: Array<{ run_id: string; reason: string }> = []

  function sendState(): void {
    const active = Array.from(activeRuns.values())
    const queue = Array.from(targetQueues.values()).flat()
    sentStates.push({ active: [...active], queue: [...queue] })
  }

  async function processTarget(targetName: string): Promise<void> {
    if (activeRuns.has(targetName)) return // idempotent guard
    const queue = targetQueues.get(targetName)
    if (!queue || queue.length === 0) return
    const run = queue.shift()!
    activeRuns.set(targetName, run)
    sendState()
    // Simulate async execution
    await Promise.resolve()
    completedRuns.push(run)
    activeRuns.delete(targetName)
    sendState()
    void processTarget(targetName) // drain next in this target's queue
  }

  function enqueue(run: Run): 'accepted' | 'rejected' | 'skipped' {
    const target = run.target
    if (target === '__all__') {
      // Expand to per-target sub-runs — not tested here (tested in separate describe)
      return 'accepted'
    }
    // Queue depth 1: max 1 active + 1 queued per target
    const isActive = activeRuns.has(target)
    const queuedCount = (targetQueues.get(target) ?? []).length
    if (isActive && queuedCount >= 1) {
      if (run.trigger === 'interval') return 'skipped' // D-06: silent skip
      rejections.push({ run_id: run.id, reason: `target '${target}' already has a queued run` })
      return 'rejected' // D-05: reject with message
    }
    if (!targetQueues.has(target)) targetQueues.set(target, [])
    targetQueues.get(target)!.push(run)
    sendState()
    void processTarget(target)
    return 'accepted'
  }

  function cancel(runId: string, activePids: Map<string, number>): boolean {
    // Check active PIDs first
    const pid = activePids.get(runId)
    if (pid !== undefined) {
      try { process.kill(pid, 'SIGTERM') } catch { /* already gone */ }
      return true
    }
    // Search all target queues
    for (const [, queue] of targetQueues) {
      const idx = queue.findIndex(r => r.id === runId)
      if (idx >= 0) {
        queue.splice(idx, 1)
        sendState()
        return true
      }
    }
    return false
  }

  return {
    targetQueues, activeRuns, completedRuns, sentStates, rejections,
    enqueue, cancel, processTarget, sendState,
  }
}

const makeRun = (id: string, target = 'test-target', trigger = 'manual'): Run => ({
  id,
  target,
  mode: 'dry-run',
  trigger,
  status: 'queued',
  log_path: '',
})

// ============================================================
// PARA-01: Per-target queue isolation tests
// ============================================================
describe('PARA-01: Per-target queue isolation', () => {
  it('two different targets triggered simultaneously both start immediately (no waiting)', async () => {
    const q = makeQueue()
    const runA = makeRun('run-a', 'target-a')
    const runB = makeRun('run-b', 'target-b')

    q.enqueue(runA)
    q.enqueue(runB)

    // Both should be active (not one waiting behind the other)
    expect(q.activeRuns.has('target-a')).toBe(true)
    expect(q.activeRuns.has('target-b')).toBe(true)
    expect(q.activeRuns.size).toBe(2)
  })

  it('second run for same target queues (does not start immediately)', async () => {
    const q = makeQueue()
    const run1 = makeRun('run-1', 'target-a')
    const run2 = makeRun('run-2', 'target-a')

    q.enqueue(run1) // starts immediately
    const result = q.enqueue(run2) // should queue, not start

    // run-1 is active
    expect(q.activeRuns.has('target-a')).toBe(true)
    expect(q.activeRuns.get('target-a')?.id).toBe('run-1')
    // run-2 is queued (not active yet)
    expect(q.targetQueues.get('target-a')?.length).toBe(1)
    expect(q.targetQueues.get('target-a')![0].id).toBe('run-2')
    expect(result).toBe('accepted')
  })

  it('queue depth 1 enforcement — third run for same target (1 active + 1 queued) rejects manual trigger', () => {
    const q = makeQueue()
    const run1 = makeRun('run-1', 'target-a')
    const run2 = makeRun('run-2', 'target-a')
    const run3 = makeRun('run-3', 'target-a')

    q.enqueue(run1) // active
    q.enqueue(run2) // queued
    const result = q.enqueue(run3) // should be rejected (queue full)

    expect(result).toBe('rejected')
    expect(q.rejections.length).toBe(1)
    expect(q.rejections[0].reason).toContain('already has a queued run')
    expect(q.rejections[0].run_id).toBe('run-3')
  })

  it('scheduled trigger for target with active/queued run is silently skipped', () => {
    const q = makeQueue()
    const run1 = makeRun('run-1', 'target-a', 'manual')
    const run2 = makeRun('run-2', 'target-a', 'manual')
    const run3 = makeRun('run-3', 'target-a', 'interval') // scheduled — should skip silently

    q.enqueue(run1) // active
    q.enqueue(run2) // queued
    const result = q.enqueue(run3) // scheduled: skip silently

    expect(result).toBe('skipped')
    expect(q.rejections.length).toBe(0) // no rejection record for scheduled
  })

  it('after target run completes, its queued run starts automatically (drain)', async () => {
    const q = makeQueue()
    const run1 = makeRun('run-1', 'target-a')
    const run2 = makeRun('run-2', 'target-a')

    q.enqueue(run1) // active
    q.enqueue(run2) // queued

    // Wait for run1 to complete (Promise.resolve drain)
    await new Promise(r => setTimeout(r, 10))

    // Both should have completed
    expect(q.completedRuns.length).toBe(2)
    expect(q.completedRuns[0].id).toBe('run-1')
    expect(q.completedRuns[1].id).toBe('run-2')
    expect(q.activeRuns.size).toBe(0)
  })

  it('processTarget is idempotent — calling while target is already active is a no-op', async () => {
    const q = makeQueue()
    const run1 = makeRun('run-1', 'target-a')
    const run2 = makeRun('run-2', 'target-a')

    q.enqueue(run1) // start run1 for target-a
    // target-a is now active with run1

    // Manually add run2 to queue and call processTarget again
    if (!q.targetQueues.has('target-a')) q.targetQueues.set('target-a', [])
    q.targetQueues.get('target-a')!.push(run2)
    // Call processTarget while target-a is already active — should be no-op (idempotent)
    void q.processTarget('target-a')

    // run-1 should still be active, run-2 still in queue
    expect(q.activeRuns.get('target-a')?.id).toBe('run-1')
    expect(q.targetQueues.get('target-a')?.length).toBe(1)
  })

  it('cancel by run_id removes from correct target queue (not other targets)', () => {
    const q = makeQueue()
    const runA1 = makeRun('run-a1', 'target-a')
    const runA2 = makeRun('run-a2', 'target-a')
    const runB1 = makeRun('run-b1', 'target-b')
    const runB2 = makeRun('run-b2', 'target-b')

    q.enqueue(runA1) // target-a active
    q.enqueue(runA2) // target-a queued
    q.enqueue(runB1) // target-b active
    q.enqueue(runB2) // target-b queued

    // Cancel a queued run from target-a only
    const pids = new Map<string, number>()
    const result = q.cancel('run-a2', pids)

    expect(result).toBe(true)
    // target-a queue is now empty
    expect(q.targetQueues.get('target-a')?.length).toBe(0)
    // target-b queue is unaffected
    expect(q.targetQueues.get('target-b')?.length).toBe(1)
    expect(q.targetQueues.get('target-b')![0].id).toBe('run-b2')
  })

  it('sendState collects from all activeRuns into flat active: Run[] array', () => {
    const q = makeQueue()
    const runA = makeRun('run-a', 'target-a')
    const runB = makeRun('run-b', 'target-b')

    q.enqueue(runA)
    q.enqueue(runB)

    // sendState is called on each enqueue — check that it collected both active runs
    const lastState = q.sentStates[q.sentStates.length - 1]
    expect(lastState.active.length).toBe(2)
    const ids = lastState.active.map(r => r.id).sort()
    expect(ids).toEqual(['run-a', 'run-b'].sort())
  })

  it('sendState collects all queued runs from all targetQueues into flat queue: Run[] array', () => {
    const q = makeQueue()
    // Create 2 targets each with 1 active + 1 queued
    q.enqueue(makeRun('a1', 'target-a'))  // active
    q.enqueue(makeRun('a2', 'target-a'))  // queued
    q.enqueue(makeRun('b1', 'target-b'))  // active
    q.enqueue(makeRun('b2', 'target-b'))  // queued

    const lastState = q.sentStates[q.sentStates.length - 1]
    expect(lastState.queue.length).toBe(2)
    const queuedIds = lastState.queue.map(r => r.id).sort()
    expect(queuedIds).toEqual(['a2', 'b2'].sort())
  })
})

// ============================================================
// EXEC-09: Existing queue tests (updated for per-target model)
// ============================================================
describe('EXEC-09: Execution queue max concurrency per target', () => {
  it('enqueuing a run while idle starts it immediately (activeRuns set)', () => {
    const q = makeQueue()
    const run = makeRun('run-1')

    expect(q.activeRuns.size).toBe(0)
    expect(q.targetQueues.size).toBe(0)

    q.enqueue(run)

    expect(q.activeRuns.has('test-target')).toBe(true)
    expect(q.activeRuns.get('test-target')?.id).toBe('run-1')
  })

  it('second enqueue for same target while a run is active goes into queue', () => {
    const q = makeQueue()
    const run1 = makeRun('run-1')
    const run2 = makeRun('run-2')

    q.enqueue(run1) // starts immediately — active
    q.enqueue(run2) // queued (same target)

    expect(q.activeRuns.has('test-target')).toBe(true)
    expect(q.targetQueues.get('test-target')?.length).toBe(1)
    expect(q.targetQueues.get('test-target')![0].id).toBe('run-2')
  })

  it('same-target queue drains when run completes (processTarget chains)', async () => {
    const q = makeQueue()
    const run1 = makeRun('run-1')
    const run2 = makeRun('run-2')
    const run3 = makeRun('run-3')

    q.enqueue(run1)
    q.enqueue(run2)
    q.enqueue(run3)  // third — rejected by queue depth 1

    // Wait for all to complete via the auto-drain
    await new Promise(r => setTimeout(r, 10))
    // run-3 was rejected, run-1 and run-2 completed
    expect(q.completedRuns.length).toBe(2)  // run-1 and run-2 only
    expect(q.activeRuns.size).toBe(0)
    expect(q.targetQueues.get('test-target')?.length).toBe(0)
  })

  it('sendState helper emits active array shape (not current)', async () => {
    const q = makeQueue()
    const run1 = makeRun('run-1')

    q.enqueue(run1)
    // Wait for completion
    await new Promise(r => setTimeout(r, 10))

    // Should have emitted states with active array
    expect(q.sentStates.length).toBeGreaterThan(0)
    // All emitted states should have active array property
    for (const state of q.sentStates) {
      expect(Array.isArray(state.active)).toBe(true)
      expect('current' in state).toBe(false)
    }
  })
})

// ============================================================
// EXEC-08: Cancel active and queued runs
// ============================================================
describe('EXEC-08: Cancel active and queued runs', () => {
  it('cancel removes a queued run by id (splice from correct target queue)', () => {
    const q = makeQueue()
    const run1 = makeRun('run-1', 'tgt-x')
    const run2 = makeRun('run-2', 'tgt-x')
    const run3 = makeRun('run-3', 'tgt-y')

    q.enqueue(run1) // tgt-x active
    q.enqueue(run2) // tgt-x queued
    q.enqueue(run3) // tgt-y active (different target — starts immediately)

    // Cancel the queued run in tgt-x queue
    const pids = new Map<string, number>()
    const result = q.cancel('run-2', pids)
    expect(result).toBe(true)
    expect(q.targetQueues.get('tgt-x')?.length).toBe(0)
    // tgt-y unaffected
    expect(q.activeRuns.has('tgt-y')).toBe(true)
  })

  it('cancel returns false for unknown run id', () => {
    const q = makeQueue()
    const pids = new Map<string, number>()
    const result = q.cancel('nonexistent-run', pids)
    expect(result).toBe(false)
  })

  it('cancel active run sends SIGTERM via Map lookup (not bulk kill)', () => {
    const q = makeQueue()
    // Simulate an active run PID in the Map
    const pids = new Map<string, number>()
    pids.set('run-1', 999999)  // fake PID — process.kill will throw but cancel catches it

    // cancel should return true for the active run (PID found in Map)
    const result = q.cancel('run-1', pids)
    expect(result).toBe(true)
  })

  it('cancel targets specific run PID via Map lookup (not all PIDs)', () => {
    const q = makeQueue()
    const pids = new Map<string, number>()
    pids.set('run-1', 11111)
    pids.set('run-2', 22222)

    // Cancel only run-1 — should NOT affect run-2's PID
    const result = q.cancel('run-1', pids)
    expect(result).toBe(true)
    // run-2 still in the Map (cancel does not clear all)
    expect(pids.has('run-2')).toBe(true)
  })
})

// ============================================================
// SCHEDULER_RUNS_ALL_TARGET constant
// ============================================================
describe('SCHEDULER_RUNS_ALL_TARGET constant', () => {
  it('SCHEDULER_RUNS_ALL_TARGET is "__all__"', () => {
    expect(SCHEDULER_RUNS_ALL_TARGET).toBe('__all__')
  })
})
