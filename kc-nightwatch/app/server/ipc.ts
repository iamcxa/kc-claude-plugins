import type { WorkerToServer, IpcMessage } from '../shared/types.ts'
import { log } from '../shared/logger.ts'
import { HEARTBEAT_TIMEOUT_MS } from '../shared/constants.ts'

export type WorkerStatus = 'online' | 'offline' | 'offline_permanent'

export let workerStatus: WorkerStatus = 'offline'
export let lastHeartbeatAt: number | null = null
export let workerProc: ReturnType<typeof Bun.spawn> | null = null

export function setWorkerProc(proc: ReturnType<typeof Bun.spawn> | null) {
  workerProc = proc
}

export function setWorkerStatus(status: WorkerStatus) {
  workerStatus = status
  log.info({ component: 'server', msg: `Worker status: ${status}` })
}

export function handleWorkerMessage(msg: WorkerToServer) {
  switch (msg.type) {
    case 'heartbeat':
      lastHeartbeatAt = msg.ts
      if (workerStatus === 'offline') setWorkerStatus('online')
      break
    case 'state':
      log.debug({ component: 'server', msg: 'Worker state received', queue: msg.queue.length })
      break
    default:
      log.debug({ component: 'server', msg: `IPC message: ${msg.type}` })
  }
}

export function sendToWorker(msg: IpcMessage): boolean {
  if (!workerProc || workerStatus === 'offline_permanent') return false
  workerProc.send(msg)
  return true
}

// Heartbeat watchdog — checks every 10s, marks offline if stale
export function startHeartbeatWatchdog() {
  return setInterval(() => {
    if (lastHeartbeatAt !== null && Date.now() - lastHeartbeatAt > HEARTBEAT_TIMEOUT_MS) {
      if (workerStatus === 'online') {
        log.warn({ component: 'server', msg: `Heartbeat stale (>${HEARTBEAT_TIMEOUT_MS}ms) — marking worker offline` })
        setWorkerStatus('offline')
      }
    }
  }, 10_000)
}
