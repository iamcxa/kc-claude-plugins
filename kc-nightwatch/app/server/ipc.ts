import type { WorkerToServer, IpcMessage, ParsedLogEvent } from '../shared/types.ts'
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

// ============================================================
// SSE fan-out state
// ============================================================
type SSEWriter = { writeSSE: (data: { data: string; event?: string }) => Promise<void> }
const sseSubscribers = new Map<string, Set<SSEWriter>>()

export function subscribeToRun(runId: string, writer: SSEWriter, signal: AbortSignal): () => void {
  if (!sseSubscribers.has(runId)) sseSubscribers.set(runId, new Set())
  sseSubscribers.get(runId)!.add(writer)
  const cleanup = () => sseSubscribers.get(runId)?.delete(writer)
  signal.addEventListener('abort', cleanup)
  return cleanup
}

export function fanOutLogEvent(runId: string, event: ParsedLogEvent): void {
  const writers = sseSubscribers.get(runId)
  if (!writers?.size) return
  const data = JSON.stringify(event)
  for (const writer of writers) {
    void writer.writeSSE({ data, event: 'log' })
  }
}

export function closeRunSubscribers(runId: string): void {
  sseSubscribers.delete(runId)
}

// ============================================================
// IPC message handler
// ============================================================
export function handleWorkerMessage(msg: WorkerToServer) {
  switch (msg.type) {
    case 'heartbeat':
      lastHeartbeatAt = msg.ts
      if (workerStatus === 'offline') setWorkerStatus('online')
      break
    case 'state':
      log.debug({ component: 'server', msg: 'Worker state received', queue: msg.queue.length })
      break
    case 'run:log':
      fanOutLogEvent(msg.run_id, msg.event)
      break
    case 'run:started':
      log.info({ component: 'server', msg: `Run ${msg.run_id} started PID ${msg.pid}` })
      break
    case 'run:completed':
      closeRunSubscribers(msg.run_id)
      log.info({ component: 'server', msg: `Run ${msg.run_id} completed` })
      break
    case 'run:failed':
      closeRunSubscribers(msg.run_id)
      log.warn({ component: 'server', msg: `Run ${msg.run_id} failed: ${msg.error}` })
      break
    default:
      log.debug({ component: 'server', msg: `IPC message: ${(msg as WorkerToServer).type}` })
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
