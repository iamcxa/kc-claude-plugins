import path from 'node:path'
import { log } from '../shared/logger.ts'
import type { IpcMessage, ServerToWorker } from '../shared/types.ts'
import { HEARTBEAT_INTERVAL_MS } from '../shared/constants.ts'
import { executeRun, killAllActive } from './executor.ts'
import type { PolicyTarget } from './policy.ts'

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
      log.info({ component: 'worker', msg: 'Received shutdown — killing active runs and exiting' })
      clearInterval(heartbeatTimer)
      killAllActive().then(() => process.exit(0))
      break
    case 'status':
      send({ type: 'state', queue: [], current: undefined })
      break
    case 'enqueue': {
      const target: PolicyTarget = {
        name: msg.run.target as string,
        resolved_path: process.env.TARGET_PATH ?? '/tmp',  // real path from Phase 2
      }
      executeRun(msg.run, target, {
        runsDir: path.join(import.meta.dir, '../../runs'),
        maxRuntimeMs: 30 * 60_000,  // from safety.yaml — Phase 2 will load dynamically
        onMessage: (m) => send(m),
      }).catch(err => {
        log.error({ component: 'worker', msg: `Run failed: ${String(err)}` })
        send({ type: 'run:failed', run_id: msg.run.id, error: String(err) } satisfies IpcMessage)
      })
      break
    }
    case 'cancel':
      log.info({ component: 'worker', msg: `Cancel run ${msg.run_id} (cancel not yet implemented)` })
      break
  }
})
