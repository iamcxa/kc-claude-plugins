import { Hono } from 'hono'
import { log } from '../shared/logger.ts'
import type { IpcMessage, WorkerToServer } from '../shared/types.ts'
import {
  handleWorkerMessage,
  setWorkerProc,
  setWorkerStatus,
  startHeartbeatWatchdog,
} from './ipc.ts'
import { healthRoutes } from './routes/health.ts'
import {
  WORKER_RESTART_BACKOFF_MS,
  MAX_WORKER_RESTARTS,
  SHUTDOWN_WORKER_TIMEOUT_MS,
  DEFAULT_PORT,
  DEFAULT_HOST,
} from '../shared/constants.ts'

const app = new Hono()
app.route('/', healthRoutes)

let restartCount = 0
let isShuttingDown = false

async function spawnWorker(): Promise<void> {
  const proc = Bun.spawn(['bun', 'run', `${import.meta.dir}/../worker/index.ts`], {
    ipc(message: WorkerToServer) {
      handleWorkerMessage(message)
    },
    stdout: 'inherit',
    stderr: 'inherit',
    env: { ...process.env, NIGHTWATCH_WORKER: '1' },
  })
  setWorkerProc(proc)

  proc.exited.then((code) => {
    if (isShuttingDown) return
    log.warn({ component: 'server', msg: `Worker exited with code ${code}` })
    setWorkerStatus('offline')
    setWorkerProc(null)
    handleWorkerCrash()
  })

  log.info({ component: 'server', msg: `Worker spawned (PID ${proc.pid})` })
}

async function handleWorkerCrash(): Promise<void> {
  if (isShuttingDown) return
  if (restartCount >= MAX_WORKER_RESTARTS) {
    log.error({ component: 'server', msg: 'Worker failed 3 times — entering read-only mode' })
    setWorkerStatus('offline_permanent')
    return
  }
  const backoff = WORKER_RESTART_BACKOFF_MS[restartCount]
  const delay = backoff !== undefined ? backoff : WORKER_RESTART_BACKOFF_MS[WORKER_RESTART_BACKOFF_MS.length - 1] ?? 15000
  restartCount++
  log.info({ component: 'server', msg: `Restarting worker in ${delay}ms (attempt ${restartCount}/${MAX_WORKER_RESTARTS})` })
  await Bun.sleep(delay)
  if (!isShuttingDown) await spawnWorker()
}

async function shutdown(signal: string): Promise<void> {
  if (isShuttingDown) return
  isShuttingDown = true
  log.info({ component: 'server', msg: `Received ${signal} — shutting down` })

  // Import workerProc lazily to get current reference
  const { workerProc } = await import('./ipc.ts')
  if (workerProc) {
    workerProc.send({ type: 'shutdown' } satisfies IpcMessage)
    const timeout = setTimeout(() => workerProc.kill('SIGKILL'), SHUTDOWN_WORKER_TIMEOUT_MS)
    await workerProc.exited.catch(() => {})
    clearTimeout(timeout)
  }

  server.stop()
  log.info({ component: 'server', msg: 'Shutdown complete' })
  process.exit(0)
}

process.on('SIGINT', () => { void shutdown('SIGINT') })
process.on('SIGTERM', () => { void shutdown('SIGTERM') })

const port = Number(process.env.PORT ?? DEFAULT_PORT)
const hostname = process.env.HOST ?? DEFAULT_HOST

const server = Bun.serve({
  port,
  hostname,
  fetch: app.fetch,
})

log.info({ component: 'server', msg: `Listening on http://${hostname}:${port}` })

startHeartbeatWatchdog()
await spawnWorker()
