import { log } from '../shared/logger.ts'
import type { IpcMessage, ServerToWorker } from '../shared/types.ts'
import { HEARTBEAT_INTERVAL_MS } from '../shared/constants.ts'

log.info({ component: 'worker', msg: 'Worker started' })

const send = (msg: IpcMessage) => process.send?.(msg)

// Send initial state
send({ type: 'state', queue: [], current: undefined })

// Heartbeat every 30s
const heartbeatTimer = setInterval(() => {
  send({ type: 'heartbeat', ts: Date.now() })
}, HEARTBEAT_INTERVAL_MS)

// Handle messages from server
process.on('message', (msg: ServerToWorker) => {
  switch (msg.type) {
    case 'shutdown':
      log.info({ component: 'worker', msg: 'Received shutdown — exiting' })
      clearInterval(heartbeatTimer)
      process.exit(0)
    case 'status':
      send({ type: 'state', queue: [], current: undefined })
      break
    case 'enqueue':
      log.info({ component: 'worker', msg: `Enqueue run ${msg.run.id} (executor not yet implemented)` })
      break
    case 'cancel':
      log.info({ component: 'worker', msg: `Cancel run ${msg.run_id} (executor not yet implemented)` })
      break
  }
})
