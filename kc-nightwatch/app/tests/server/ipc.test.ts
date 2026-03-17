import { describe, it, expect } from 'bun:test'
import { workerStatus, lastHeartbeatAt, handleWorkerMessage, setWorkerStatus } from '../../server/ipc.ts'

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
