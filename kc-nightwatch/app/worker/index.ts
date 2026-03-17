import { log } from '../shared/logger.ts'
import type { IpcMessage, ServerToWorker } from '../shared/types.ts'
import { HEARTBEAT_INTERVAL_MS } from '../shared/constants.ts'

log.info({ component: 'worker', msg: 'Worker started' })

// Send initial state
process.send({ type: 'state', queue: [], current: undefined } satisfies IpcMessage)

// Heartbeat every 30s
const heartbeatTimer = setInterval(() => {
  process.send({ type: 'heartbeat', ts: Date.now() } satisfies IpcMessage)
}, HEARTBEAT_INTERVAL_MS)

// Handle messages from server
process.on('message', (msg: ServerToWorker) => {
  switch (msg.type) {
    case 'shutdown':
      log.info({ component: 'worker', msg: 'Received shutdown — exiting' })
      clearInterval(heartbeatTimer)
      process.exit(0)
      break
    case 'status':
      process.send({ type: 'state', queue: [], current: undefined } satisfies IpcMessage)
      break
    case 'enqueue':
      log.info({ component: 'worker', msg: `Enqueue run ${msg.run.id} (executor not yet implemented)` })
      break
    case 'cancel':
      log.info({ component: 'worker', msg: `Cancel run ${msg.run_id} (executor not yet implemented)` })
      break
  }
})
