// FOUND-04: Using Bun native IPC (not Unix socket) eliminates EADDRINUSE risk.
// No socket file is created. Stale state from prior crash is handled by cleanupOrphans().
import { Hono } from 'hono'
import { serveStatic } from 'hono/bun'
import path from 'node:path'
import { log } from '../shared/logger.ts'
import type { IpcMessage, WorkerToServer } from '../shared/types.ts'
import {
  handleWorkerMessage,
  setWorkerProc,
  setWorkerStatus,
  startHeartbeatWatchdog,
} from './ipc.ts'
import { healthRoutes } from './routes/health.ts'
import { apiRoutes } from './routes/api.ts'
import { streamRoutes } from './routes/stream.ts'
import { scheduleRoutes } from './routes/schedule.ts'
import { chatRoutes } from './routes/chat.ts'
import { feedbackRoutes } from './routes/feedback.ts'
import { configRoutes } from './routes/config.ts'
import { mcpRoutes } from './routes/mcp.ts'
import { healthApiRoutes } from './routes/health-api.ts'
import { outcomesRoutes } from './routes/outcomes.ts'
import { signalPriorityRoutes } from './routes/signal-priority.ts'
import {
  WORKER_RESTART_BACKOFF_MS,
  MAX_WORKER_RESTARTS,
  SHUTDOWN_WORKER_TIMEOUT_MS,
  DEFAULT_PORT,
  DEFAULT_HOST,
} from '../shared/constants.ts'
import { loadOrCreateAppConfig } from './services/yaml-store.ts'
import { tokenAuth } from './services/auth.ts'
import { cleanupOrphans } from './services/orphan-cleanup.ts'

const FRONTEND_ROOT = path.join(import.meta.dir, '../frontend')

const app = new Hono()

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
    void handleWorkerCrash()
  })

  log.info({ component: 'server', msg: `Worker spawned (PID ${proc.pid})` })
}

async function handleWorkerCrash(): Promise<void> {
  if (isShuttingDown) return
  // CRITICAL: Call cleanupOrphans here too, not just at startup (Pitfall 4)
  await cleanupOrphans()
  if (restartCount >= MAX_WORKER_RESTARTS) {
    log.error({ component: 'server', msg: 'Worker failed 3 times — entering read-only mode' })
    setWorkerStatus('offline_permanent')
    return
  }
  const delay = WORKER_RESTART_BACKOFF_MS[restartCount++] ?? 15000
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

// SEC-01: load config (creates nightwatch-app.yaml if first run)
const config = await loadOrCreateAppConfig()

// SEC-02: Remote mode requires explicit token — refuse to start otherwise
if (config.host !== '127.0.0.1' && !config.auth_token) {
  log.error({
    component: 'server',
    msg: 'Remote mode (non-localhost host) requires auth_token in nightwatch-app.yaml. Refusing to start.'
  })
  process.exit(1)
}

// SEC-03: Apply auth middleware BEFORE registering routes, at app level
if (config.host !== '127.0.0.1' && config.auth_token) {
  app.use('*', tokenAuth(config.auth_token))
  log.info({ component: 'server', msg: 'Remote mode: Bearer token auth enabled on all routes' })
}

// Serve frontend static files — BEFORE API routes (order matters in Hono)
// Vendor files (preact, htm) are plain JS — serve as-is
app.use('/vendor/*', serveStatic({ root: FRONTEND_ROOT }))

// TypeScript files — transpile on-the-fly with Bun then serve as JS
const serveTsFile = async (filePath: string) => {
  const file = Bun.file(filePath)
  if (!(await file.exists())) return null
  const transpiler = new Bun.Transpiler({ loader: 'ts' })
  const source = await file.text()
  const js = transpiler.transformSync(source)
  return new Response(js, { headers: { 'Content-Type': 'application/javascript; charset=utf-8' } })
}

app.get('/pages/*', async (c) => {
  const resp = await serveTsFile(path.join(FRONTEND_ROOT, c.req.path))
  return resp ?? c.notFound()
})
app.get('/components/*', async (c) => {
  const resp = await serveTsFile(path.join(FRONTEND_ROOT, c.req.path))
  return resp ?? c.notFound()
})
app.get('/lib/*', async (c) => {
  const resp = await serveTsFile(path.join(FRONTEND_ROOT, c.req.path))
  return resp ?? c.notFound()
})
app.get('/app.ts', async (c) => {
  const resp = await serveTsFile(path.join(FRONTEND_ROOT, 'app.ts'))
  return resp ?? c.notFound()
})
app.get('/shared/*', async (c) => {
  const resp = await serveTsFile(path.join(import.meta.dir, '..', c.req.path))
  return resp ?? c.notFound()
})

// Register API routes after auth middleware and static serving (order matters in Hono)
app.route('/', healthRoutes)
app.route('/', apiRoutes)
app.route('/', streamRoutes)
app.route('/', scheduleRoutes)
app.route('/', chatRoutes)
app.route('/', feedbackRoutes)
app.route('/', configRoutes)
app.route('/', mcpRoutes)
app.route('/', healthApiRoutes)
app.route('/', outcomesRoutes)
app.route('/', signalPriorityRoutes)

// SPA root route — serve index.html for / (after all API routes)
app.get('/', async (c) => {
  const html = await Bun.file(path.join(FRONTEND_ROOT, 'index.html')).text()
  return c.html(html)
})

const port = Number(process.env.PORT ?? config.port ?? DEFAULT_PORT)
const hostname = process.env.HOST ?? config.host ?? DEFAULT_HOST

const server = Bun.serve({
  port,
  hostname,
  fetch: app.fetch,
})

log.info({ component: 'server', msg: `Listening on http://${hostname}:${port}` })

// Run orphan cleanup before spawning worker — covers prior crash scenario (FOUND-06)
await cleanupOrphans()
startHeartbeatWatchdog()
await spawnWorker()
