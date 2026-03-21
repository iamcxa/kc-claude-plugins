import { describe, it, expect } from 'bun:test'
import type { Run } from '../../shared/types.ts'
import { workerStatus, lastHeartbeatAt, handleWorkerMessage, setWorkerStatus, getLastWorkerState } from '../../server/ipc.ts'

describe('IPC heartbeat handling', () => {
  it('updates lastHeartbeatAt on heartbeat message', () => {
    const before = Date.now()
    handleWorkerMessage({ type: 'heartbeat', ts: before })
    expect(lastHeartbeatAt).toBe(before)
  })

  it('sets status to online on heartbeat when offline', () => {
    setWorkerStatus('offline')
    handleWorkerMessage({ type: 'heartbeat', ts: Date.now() })
    expect(workerStatus).toBe('online')
  })
})

describe('IPC state handling', () => {
  it('stores active array from state message', () => {
    const run: Run = {
      id: 'test-run-1',
      target: 'test-target',
      mode: 'dry-run',
      trigger: 'manual',
      status: 'running',
      log_path: 'runs/test-run-1/log.jsonl',
    }
    handleWorkerMessage({ type: 'state', queue: [], active: [run] })
    const state = getLastWorkerState()
    expect(state.active).toHaveLength(1)
    expect(state.active[0].id).toBe('test-run-1')
    expect(state.queue).toHaveLength(0)
  })

  it('stores empty active array when no runs executing', () => {
    handleWorkerMessage({ type: 'state', queue: [], active: [] })
    const state = getLastWorkerState()
    expect(state.active).toHaveLength(0)
  })

  it('lastWorkerState has active property not current', () => {
    handleWorkerMessage({ type: 'state', queue: [], active: [] })
    const state = getLastWorkerState()
    expect('active' in state).toBe(true)
    expect('current' in state).toBe(false)
  })
})
