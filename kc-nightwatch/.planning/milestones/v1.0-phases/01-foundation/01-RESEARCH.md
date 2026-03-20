# Phase 1: Foundation - Research

**Researched:** 2026-03-18
**Domain:** Bun native IPC, process lifecycle management, graceful shutdown, orphan cleanup, structured logging, security defaults
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**CLI Interface**
- Single entry point: `bun run app/server/index.ts` spawns both server and worker
- Server process is the parent; worker is spawned as child process
- Flags: `--port` (override yaml), `--host` (for remote), `--token` (remote auth)
- package.json scripts: `start` (production), `dev` (bun --watch for hot reload)
- mprocs-friendly: one process to manage, stdout captured by terminal
- No separate `stop` command — kill server → graceful shutdown handles worker

**Crash Behavior**
- Worker auto-restart with exponential backoff: 2s, 5s, 15s (3 attempts)
- After 3rd crash: stop retrying, server enters read-only mode
- Dashboard shows "Worker offline" banner when worker is down
- Manual restart via page refresh or POST /api/worker/restart
- Server stays up regardless — last run results always viewable
- Orphaned safehouse+claude processes cleaned up on each crash recovery

**Logging**
- Structured JSON to stdout: `{"ts":"...","level":"info","component":"server|worker","msg":"..."}`
- Worker stdout piped to server, forwarded to mprocs terminal
- Default level: INFO, --verbose flag for DEBUG
- File rotation: app/logs/nightwatch.log (5 files × 10MB) for post-mortem
- Custom 10-line structured logger — no external logging library

**IPC Transport**
- **Bun native IPC** (`Bun.spawn` with `ipc: true`), NOT `node:net` Unix socket
- Server is parent, worker is child — matches Bun IPC direction naturally
- `proc.send()` / `process.on('message')` with JSON serialization
- Eliminates socket file management, EADDRINUSE risk, and FOUND-04 complexity
- Overrides design spec Appendix C (which specified Unix socket) — simpler, zero dependencies
- Heartbeat: worker sends heartbeat every 30s via IPC; server marks offline if >60s stale

**Claude Process Lifecycle**
- Force-kill claude child process within 10s after receiving `{"type":"result"}` event
- PID tracking: store claude PIDs in memory (not file) — worker has direct handle
- Orphan scan on startup: `pgrep -f "safehouse.*claude"` to find zombies from prior crash
- Timeout from safety.yaml `max_runtime_minutes` (default 30min)

**Security Defaults**
- Bind to 127.0.0.1 by default
- Remote mode: explicit --host 0.0.0.0 + --token required
- Token checked on all routes (API, SSE, WebSocket, MCP) when remote mode active
- Bearer token in Authorization header

### Claude's Discretion
- Heartbeat interval (30s suggested, can adjust)
- Exact structured logger implementation
- Run artifact directory structure details
- nightwatch-app.yaml default values beyond what spec defines

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FOUND-01 | Server + worker two-process architecture with Bun native IPC | Bun.spawn `ipc: true` pattern; `proc.send()` / `process.on('message')` — see Code Examples §1 |
| FOUND-02 | Graceful shutdown (SIGINT/SIGTERM) with child process cleanup | `process.on('SIGTERM')` + `proc.kill('SIGTERM')` + await `proc.exited` — see Code Examples §2 |
| FOUND-03 | Worker crash recovery — server detects disconnect, cleans orphan processes | `proc.exited` promise + exponential backoff restart — see Code Examples §3 |
| FOUND-04 | Socket/PID file cleanup on startup (prevent EADDRINUSE) | Bun native IPC: no socket file. FOUND-04 is structurally eliminated by the IPC decision. Startup still cleans stale orphan PIDs. |
| FOUND-05 | Timeout enforcement per run (from safety.yaml max_runtime_minutes) | `setTimeout(() => child.kill('SIGKILL'), maxMs)` in executor.ts — see Pitfall 1 |
| FOUND-06 | Orphaned safehouse+claude process detection and kill on startup | `pgrep -f "safehouse.*claude"` scan + SIGTERM/SIGKILL at server boot — see Code Examples §4 |
| FOUND-07 | App bootstrap — create default nightwatch-app.yaml on first start | `Bun.file(path).exists()` check + write defaults — see Code Examples §5 |
| FOUND-08 | Run artifact directory with rolling cleanup (keep last 50) | `app/runs/` mkdir on bootstrap; keep-last-50 cleanup in executor on completion — see Architecture Patterns §3 |
| SEC-01 | Localhost binding by default (127.0.0.1) | `Bun.serve({ hostname: '127.0.0.1' })` default — see Code Examples §6 |
| SEC-02 | Optional remote mode (0.0.0.0) with required token auth | Startup gate: if `host == '0.0.0.0'` and no `auth_token` → refuse to start — see Security section |
| SEC-03 | Token auth on all API/MCP/WebSocket endpoints in remote mode | Hono middleware applied at app level before all routes — see Code Examples §6 |
</phase_requirements>

---

## Summary

Phase 1 builds the two-process skeleton: a Hono HTTP server that spawns a Bun worker using native IPC, handles every crash/restart/orphan-cleanup scenario, enforces timeouts, bootstraps config, and applies security defaults. No features, no UI — only the infrastructure every subsequent phase builds on.

The IPC decision to use **Bun native IPC** (not Unix socket) is the most important architectural simplification in this phase. It eliminates socket file management entirely, removing EADDRINUSE risk (FOUND-04) as a structural non-problem. The tradeoff is that `Bun.spawn` with `ipc: true` requires both parent and child to be Bun processes — which is satisfied in this project.

The most critical failure mode to get right in Phase 1 is the **Claude CLI hang after result event** (Pitfall 1 from PITFALLS.md). This is a confirmed CLI bug (GitHub #25629) where active MCP connections keep the process alive indefinitely after the result event. The force-kill pattern (10s after `{"type":"result"}`) is not optional — it must be built into executor.ts from the first commit, not added later when zombies accumulate.

**Primary recommendation:** Build in this order: shared/types.ts → yaml-store + bootstrap → server/index.ts (IPC parent) → worker/index.ts (IPC child + heartbeat) → executor.ts (spawn + force-kill + timeout) → orphan cleanup → graceful shutdown → security middleware. Each module is independently testable before wiring.

---

## Standard Stack

### Core (Phase 1 subset)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Bun | 1.2.x | Runtime, IPC, file I/O, process spawning | Constraint; native IPC via `Bun.spawn({ ipc })` is the locked IPC transport |
| Hono | 4.12.2 | HTTP server, middleware, security layer | Constraint; `Bun.serve` backend; used for auth middleware in SEC-02/SEC-03 |
| `zod` | 3.x | Schema validation for YAML config, IPC messages | Required by project conventions ("Zod at boundaries"); prevents silent schema drift |
| `yaml` (npm) | 2.x | Read/write nightwatch-app.yaml on bootstrap | Bun's built-in `Bun.YAML.parse()` is parse-only; `yaml` npm package handles stringify |

### Phase 1 Does NOT Need

The following stack members (from STACK.md) are NOT needed in Phase 1:
- `@modelcontextprotocol/sdk` / `@hono/mcp` — MCP is Phase 4
- `@preact/signals` — Frontend is Phase 2+
- `Bun.build()` — No frontend bundle in Phase 1

### Installation

```bash
# From kc-nightwatch/app/
bun init
bun add hono zod yaml
bun add -D @types/bun biome
```

---

## Architecture Patterns

### Recommended Project Structure (Phase 1 scope)

```
kc-nightwatch/app/
├── package.json
├── tsconfig.json
├── nightwatch-app.yaml           # created on first start (FOUND-07)
├── logs/                         # gitignored (FOUND-07)
├── runs/                         # gitignored; rolling cleanup to 50 (FOUND-08)
│
├── server/
│   ├── index.ts                  # entry point: Hono + spawn worker + signal handlers
│   ├── ipc.ts                    # server-side IPC message handlers; worker process ref
│   ├── routes/
│   │   └── health.ts             # GET /health (worker status, uptime) — minimal Phase 1 route
│   └── services/
│       ├── auth.ts               # Bearer token middleware (SEC-02, SEC-03)
│       └── yaml-store.ts         # read/write YAML with zod validation
│
├── worker/
│   ├── index.ts                  # entry point: process.on('message') dispatch + heartbeat
│   └── executor.ts               # spawn claude, force-kill, timeout, PID tracking
│
└── shared/
    ├── types.ts                  # Run, Target, AppConfig, IPC message union types
    └── constants.ts              # HEARTBEAT_INTERVAL_MS, HEARTBEAT_TIMEOUT_MS, etc.
```

Note: `routes/api.ts`, `routes/stream.ts`, `worker/scheduler.ts`, `worker/policy.ts`, `worker/log-parser.ts`, and all frontend files are Phase 2+ work. Phase 1 only needs the skeleton routes to prove the server starts and the health endpoint to verify worker status.

### Pattern 1: Bun Native IPC Parent-Child

**What:** Server spawns worker with `Bun.spawn(['bun', 'run', 'worker/index.ts'], { ipc(message) {...} })`. Messages are structured-clone serialized automatically.

**When to use:** Both processes are Bun. Server needs to send commands to worker and receive async events back. No socket file, no reconnect loop needed — parent detects child exit via `proc.exited` promise.

**Source:** [Bun IPC docs](https://bun.com/docs/guides/process/ipc) — HIGH confidence

```typescript
// server/index.ts — spawn worker with IPC
import type { IpcMessage } from '../shared/types.ts'

let workerProc: ReturnType<typeof Bun.spawn> | null = null
let restartCount = 0
const BACKOFF_MS = [2000, 5000, 15000]

async function spawnWorker() {
  workerProc = Bun.spawn(['bun', 'run', 'worker/index.ts'], {
    ipc(message: IpcMessage) {
      handleWorkerMessage(message)
    },
    stdout: 'inherit',    // worker stdout piped to server's stdout (mprocs captures both)
    stderr: 'inherit',
    env: { ...process.env, NIGHTWATCH_WORKER: '1' },
  })

  // Detect crash via exited promise
  workerProc.exited.then((code) => {
    log.warn({ component: 'server', msg: `Worker exited with code ${code}` })
    handleWorkerCrash()
  })
}

async function handleWorkerCrash() {
  await cleanupOrphans()   // kill any leftover safehouse+claude processes
  if (restartCount >= BACKOFF_MS.length) {
    log.error({ component: 'server', msg: 'Worker failed 3 times — entering read-only mode' })
    setWorkerStatus('offline_permanent')
    return
  }
  const delay = BACKOFF_MS[restartCount++]
  log.info({ component: 'server', msg: `Restarting worker in ${delay}ms (attempt ${restartCount}/3)` })
  await Bun.sleep(delay)
  await spawnWorker()
}

// Server sends to worker
function sendToWorker(msg: IpcMessage) {
  workerProc?.send(msg)
}
```

```typescript
// worker/index.ts — receive from parent
import type { IpcMessage } from '../shared/types.ts'

process.on('message', (msg: IpcMessage) => {
  handleServerMessage(msg)
})

// Send heartbeat every 30s
setInterval(() => {
  process.send({ type: 'heartbeat', ts: Date.now() })
}, 30_000)

// Send initial state on startup
process.send({ type: 'state', queue: [], current: undefined })
```

### Pattern 2: Graceful Shutdown Chain

**What:** SIGINT/SIGTERM handler on server sends shutdown to worker, waits for worker to exit, then exits server.

**Source:** Bun process signal handling — HIGH confidence

```typescript
// server/index.ts — graceful shutdown
async function shutdown(signal: string) {
  log.info({ component: 'server', msg: `Received ${signal} — shutting down` })

  // 1. Tell worker to stop accepting new runs and flush current
  workerProc?.send({ type: 'shutdown' })

  // 2. Wait up to 35s for worker to finish current run or force-kill
  const timeout = setTimeout(() => workerProc?.kill('SIGKILL'), 35_000)
  await workerProc?.exited.catch(() => {})
  clearTimeout(timeout)

  // 3. Close HTTP server (stop accepting new connections)
  server.stop()

  log.info({ component: 'server', msg: 'Shutdown complete' })
  process.exit(0)
}

process.on('SIGINT', () => shutdown('SIGINT'))
process.on('SIGTERM', () => shutdown('SIGTERM'))
```

```typescript
// worker/index.ts — handle shutdown command
process.on('message', (msg: IpcMessage) => {
  if (msg.type === 'shutdown') {
    // Cancel queued runs, wait for current run to finish (or timeout)
    gracefulWorkerShutdown().then(() => process.exit(0))
  }
})
```

### Pattern 3: Claude Force-Kill After Result Event

**What:** After receiving `{"type":"result"}` from claude's stdout stream, schedule a SIGKILL after 10 seconds. This is a required workaround for a confirmed Claude CLI bug (GitHub #25629).

**Source:** PITFALLS.md Pitfall 1 — HIGH confidence (issue confirmed closed as duplicate)

```typescript
// worker/executor.ts
async function executeRun(run: Run, target: Target): Promise<void> {
  const child = Bun.spawn(['safehouse', ...buildSafehouseFlags(target, run), 'claude', '-p',
    '--output-format', 'stream-json',
    '--model', 'claude-opus-4-5',
    '--cwd', target.resolved_path,
  ], { stdout: 'pipe', stderr: 'pipe' })

  // Track PID for orphan cleanup if worker itself crashes
  activePids.add(child.pid)

  // Enforce max_runtime_minutes from safety.yaml
  const maxMs = appConfig.max_runtime_minutes * 60_000
  const runtimeTimeout = setTimeout(() => {
    log.warn({ component: 'worker', msg: `Run ${run.id} timed out after ${maxMs}ms — SIGKILL` })
    child.kill('SIGKILL')
  }, maxMs)

  let resultReceived = false

  for await (const line of lineIterator(child.stdout)) {
    const event = parseStreamJsonLine(line)
    process.send({ type: 'run:log', run_id: run.id, event })

    // CRITICAL: Force-kill after result event — Claude CLI bug workaround
    if (event.type === 'result' && !resultReceived) {
      resultReceived = true
      log.info({ component: 'worker', msg: `Result received for ${run.id} — scheduling force-kill in 10s` })
      setTimeout(() => {
        if (child.exitCode === null) {
          child.kill('SIGKILL')
        }
      }, 10_000)
    }
  }

  clearTimeout(runtimeTimeout)
  activePids.delete(child.pid)

  process.send({ type: 'run:completed', run_id: run.id, summary: buildSummary(run) })
}
```

### Pattern 4: Orphan Scan on Server Startup

**What:** On server boot, find any `safehouse.*claude` processes left from a prior crash and kill them.

**Source:** CONTEXT.md decision + PITFALLS.md Pitfall 5 — HIGH confidence

```typescript
// server/index.ts — orphan cleanup at startup
async function cleanupOrphans(): Promise<void> {
  const result = await Bun.spawn(['pgrep', '-f', 'safehouse.*claude'], {
    stdout: 'pipe',
  }).text()

  const pids = result.trim().split('\n').filter(Boolean).map(Number)
  for (const pid of pids) {
    log.warn({ component: 'server', msg: `Killing orphan process PID ${pid}` })
    try {
      process.kill(pid, 'SIGTERM')
      await Bun.sleep(3000)
      process.kill(pid, 'SIGKILL')
    } catch (_) {
      // Process already gone — that's fine
    }
  }
  if (pids.length > 0) {
    log.info({ component: 'server', msg: `Cleaned up ${pids.length} orphan process(es)` })
  }
}
```

### Pattern 5: App Bootstrap (FOUND-07)

**What:** On first start, create `nightwatch-app.yaml` with defaults. On subsequent starts, read and validate it.

```typescript
// server/services/yaml-store.ts
import { parse, stringify } from 'yaml'
import { AppConfigSchema } from '../../shared/types.ts'

const APP_CONFIG_PATH = new URL('../../nightwatch-app.yaml', import.meta.url).pathname

const DEFAULT_APP_CONFIG = {
  host: '127.0.0.1',
  port: 3200,
  schedule: { enabled: false, interval_hours: 2, self_repair_before: true },
  max_concurrent_runs: 1,
  plugins_dir: `${process.env.HOME}/.claude/plugins/local`,
}

export async function loadOrCreateAppConfig() {
  const file = Bun.file(APP_CONFIG_PATH)
  if (!(await file.exists())) {
    await Bun.write(APP_CONFIG_PATH, stringify(DEFAULT_APP_CONFIG))
    log.info({ component: 'server', msg: 'Created default nightwatch-app.yaml' })
  }
  const raw = parse(await file.text())
  return AppConfigSchema.parse(raw)   // zod validation — throws on invalid schema
}
```

### Pattern 6: Security Middleware (SEC-01, SEC-02, SEC-03)

**What:** Default localhost binding. If host is not 127.0.0.1 and no token is configured, refuse to start. When in remote mode, apply Bearer token middleware to all routes.

```typescript
// server/index.ts — startup security gate
if (config.host !== '127.0.0.1' && !config.auth_token) {
  log.error({ component: 'server', msg: 'Remote mode (non-localhost) requires --token. Refusing to start.' })
  process.exit(1)
}

// server/services/auth.ts — Hono middleware
import type { MiddlewareHandler } from 'hono'

export function tokenAuth(token: string): MiddlewareHandler {
  return async (c, next) => {
    const authHeader = c.req.header('Authorization')
    if (authHeader !== `Bearer ${token}`) {
      return c.json({ error: 'Unauthorized' }, 401)
    }
    await next()
  }
}

// server/index.ts — apply middleware when remote mode
if (config.host !== '127.0.0.1') {
  app.use('*', tokenAuth(config.auth_token!))
}
app.route('/api', apiRoutes)
// ... other routes
```

### Anti-Patterns to Avoid

- **Using Unix socket for IPC**: The CONTEXT.md decision locks Bun native IPC. Do not introduce `node:net` or `nightwatch.sock`. The design spec's Appendix C is explicitly overridden.
- **Waiting for `proc.exited` to detect worker offline**: The `exited` promise fires on exit — combine it with the heartbeat timeout (>60s stale) to detect live-but-unresponsive workers. A hung worker may not exit but stop sending heartbeats.
- **Storing claude PIDs in files**: CONTEXT.md decision locks in-memory PID tracking. The worker has direct process handles from `Bun.spawn()`. File-based PID tracking adds I/O and staleness risk.
- **Using external logging library**: CONTEXT.md locks a custom 10-line logger. Do not add `pino`, `winston`, etc.
- **Binding to 0.0.0.0 without enforcement**: Must fail-fast at startup, not silently expose the server.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML config serialization | Custom YAML writer | `yaml` npm package | Comment preservation, proper quoting, mature TypeScript types. Bun's built-in is parse-only. |
| Schema validation at config load | Manual field checks | `zod` | Config schema drift silently breaks executor — zod gives readable parse errors at startup, not cryptic runtime failures. |
| Bearer token parsing | Regex on Authorization header | Hono middleware (`tokenAuth` helper) | Hono's middleware chain ensures auth applies uniformly — per-route checks get missed. |
| Process signal registration | Ad-hoc signal handlers scattered | Centralized in `server/index.ts` `shutdown()` | Multiple handlers for SIGTERM on the same process create race conditions. |

**Key insight:** The "don't hand-roll" discipline here is primarily about not adding dependencies beyond what is already decided — the logging library constraint is intentional, and complexity should come from the spec, not from library choice.

---

## Common Pitfalls

### Pitfall 1: Claude CLI hangs after result event (CRITICAL — must address in Phase 1)

**What goes wrong:** `claude -p --output-format stream-json` emits `{"type":"result"}` but never exits because active MCP connections keep the process alive. Worker's `for await` loop blocks forever. Run stays `status: running` permanently.

**Why it happens:** Confirmed CLI bug (GitHub #25629, #21099 — February 2026). MCP connections prevent clean `process.exit()`.

**How to avoid:** After receiving the result event, set a `setTimeout(() => child.kill('SIGKILL'), 10_000)`. Do NOT wait for the stream to close naturally. See Pattern 3 above.

**Warning signs:** Run shows `running` after `max_runtime_minutes`. `ps aux | grep claude` shows N processes older than expected.

### Pitfall 2: FOUND-04 misinterpretation

**What goes wrong:** FOUND-04 reads "Socket/PID file cleanup on startup (prevent EADDRINUSE)". With Bun native IPC (no socket file), a developer might mark this done without implementing the startup orphan scan.

**Why it happens:** The requirement name references Unix socket cleanup, but the IPC decision eliminated the socket. The underlying intent — clean crash recovery — still requires the orphan PID scan.

**How to avoid:** FOUND-04 is satisfied by: (a) confirming no socket file is created (structural), plus (b) implementing the orphan scan from FOUND-06 that covers the "stale state from prior crash" concern. Both are needed.

### Pitfall 3: Worker heartbeat vs. worker exit

**What goes wrong:** Server only listens to `proc.exited` to detect worker health. A worker that is alive but hung (waiting for a lock, stuck in a long I/O call) never exits, so the server believes it is healthy. New run enqueues succeed but are never processed.

**Why it happens:** `proc.exited` fires only on process termination. A live-but-hung process does not trigger it.

**How to avoid:** Track `lastHeartbeatAt` separately. If `Date.now() - lastHeartbeatAt > 60_000`, mark worker as offline even if `proc.exitCode === null`. Use BOTH signals together.

### Pitfall 4: Orphan scan at crash recovery vs. startup only

**What goes wrong:** Orphan cleanup runs on startup but not on each worker crash-recovery cycle. If the worker crashes during a run, the orphan `claude -p` process accumulates. On next crash, it accumulates again. The startup scan only runs once.

**How to avoid:** Call `cleanupOrphans()` in both `spawnWorker()` startup AND `handleWorkerCrash()` before each restart attempt.

### Pitfall 5: Safehouse path tilde expansion

**What goes wrong:** Paths like `~/.claude/kc-plugins-config` passed to `safehouse --add-dirs` fail silently. Safehouse does not expand shell tildes.

**Why it happens:** `~` expansion is a shell feature, not a libc/OS feature. `execvp` does not expand it.

**How to avoid:** Always resolve to absolute paths: `path.resolve(process.env.HOME!, '.claude/kc-plugins-config')`. Add a startup assertion in `policy.ts` that no generated flag contains `~`.

### Pitfall 6: Remote mode partially applied

**What goes wrong:** Auth middleware is added to `/api/*` but forgotten on `/api/worker/restart` (added later), or forgotten when new routes are added in Phase 2.

**How to avoid:** Apply the auth middleware at the top-level app instance, not per-route. All routes registered after `app.use('*', tokenAuth(...))` are automatically covered. Never register auth at the route level.

---

## Code Examples

All examples are synthesized from official sources (Bun docs, CONTEXT.md decisions, PITFALLS.md) — see Sources section.

### IPC Types (shared/types.ts foundation)

```typescript
// shared/types.ts
import { z } from 'zod'

// --- IPC Messages ---
export type ServerToWorker =
  | { type: 'enqueue'; run: Run }
  | { type: 'cancel'; run_id: string }
  | { type: 'shutdown' }
  | { type: 'status' }

export type WorkerToServer =
  | { type: 'heartbeat'; ts: number }
  | { type: 'run:started'; run_id: string; pid: number }
  | { type: 'run:log'; run_id: string; event: ParsedLogEvent }
  | { type: 'run:completed'; run_id: string; summary: RunSummary }
  | { type: 'run:failed'; run_id: string; error: string }
  | { type: 'state'; queue: Run[]; current?: Run }

export type IpcMessage = ServerToWorker | WorkerToServer

// --- Domain types ---
export const AppConfigSchema = z.object({
  host: z.string().default('127.0.0.1'),
  port: z.number().default(3200),
  auth_token: z.string().optional(),
  schedule: z.object({
    enabled: z.boolean().default(false),
    interval_hours: z.number().optional(),
    self_repair_before: z.boolean().default(true),
  }),
  max_concurrent_runs: z.literal(1),
  safehouse_path: z.string().optional(),
  plugins_dir: z.string(),
})
export type AppConfig = z.infer<typeof AppConfigSchema>

export interface Run {
  id: string
  target: string | '__all__'
  mode: 'production' | 'dry-run' | 'self-repair'
  trigger: 'manual' | 'interval' | 'webhook' | 'implementation'
  status: 'queued' | 'running' | 'completed' | 'failed' | 'timeout' | 'cancelled'
  custom_prompt?: string
  started_at?: string
  completed_at?: string
  duration_seconds?: number
  log_path: string
}
```

### Structured Logger (10-line custom, no dependencies)

```typescript
// server/logger.ts (shared between server + worker via process env context)
type Level = 'debug' | 'info' | 'warn' | 'error'
type LogEntry = { ts?: string; level?: Level; component: string; msg: string; [key: string]: unknown }

const LOG_LEVEL: Level = (process.env.LOG_LEVEL as Level) ?? 'info'
const LEVELS: Record<Level, number> = { debug: 0, info: 1, warn: 2, error: 3 }

export const log = {
  debug: (e: LogEntry) => LEVELS[LOG_LEVEL] <= 0 && console.log(JSON.stringify({ ts: new Date().toISOString(), level: 'debug', ...e })),
  info:  (e: LogEntry) => LEVELS[LOG_LEVEL] <= 1 && console.log(JSON.stringify({ ts: new Date().toISOString(), level: 'info', ...e })),
  warn:  (e: LogEntry) => LEVELS[LOG_LEVEL] <= 2 && console.warn(JSON.stringify({ ts: new Date().toISOString(), level: 'warn', ...e })),
  error: (e: LogEntry) => LEVELS[LOG_LEVEL] <= 3 && console.error(JSON.stringify({ ts: new Date().toISOString(), level: 'error', ...e })),
}
```

### Rolling Artifact Cleanup (FOUND-08)

```typescript
// worker/executor.ts — after run completes
async function cleanupOldRuns(runsDir: string, keepCount = 50): Promise<void> {
  const entries = await Array.fromAsync(new Bun.Glob('*').scan({ cwd: runsDir, onlyFiles: false }))
  // Sort by mtime ascending (oldest first)
  const withStats = await Promise.all(
    entries.map(async (name) => ({ name, mtime: (await Bun.file(`${runsDir}/${name}`).stat()).mtime }))
  )
  withStats.sort((a, b) => a.mtime - b.mtime)
  const toDelete = withStats.slice(0, Math.max(0, withStats.length - keepCount))
  for (const { name } of toDelete) {
    await Bun.spawn(['rm', '-rf', `${runsDir}/${name}`]).exited
  }
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Unix socket for same-machine IPC | Bun native IPC (`Bun.spawn` + `ipc: true`) | Decision locked 2026-03-18 | No socket file, no EADDRINUSE, no reconnect loop code |
| `node:child_process.spawn` | `Bun.spawn()` | Bun 1.0+ | stdout as ReadableStream (async line iteration), native AbortSignal, direct `.kill()` |
| External log library (pino/winston) | Custom 10-line JSON logger | Decision locked 2026-03-18 | Zero dependencies, stdout-only (mprocs captures it) |

**Deprecated/outdated for this project:**
- Design spec Appendix C (Unix socket / `node:net`): Overridden by IPC decision. Do not implement.
- `Bun.YAML.parse()` for write: Parse-only. Use `yaml` npm package for config writes.

---

## Open Questions

1. **Heartbeat interval tuning**
   - What we know: 30s interval, 60s offline threshold — within Claude's discretion
   - What's unclear: Under mprocs CPU throttling (e.g., system sleep), can a heartbeat miss two intervals before the worker is incorrectly marked offline?
   - Recommendation: Use 30s/90s (interval/timeout) to give 3 missed heartbeats before marking offline. Adjust downward after real usage data.

2. **`pgrep -f "safehouse.*claude"` scope**
   - What we know: Used for orphan scan on startup
   - What's unclear: On a system where other users or processes run `claude`, this regex might match unrelated processes
   - Recommendation: Add the server's PID as a prefix guard, or use a unique marker string in the safehouse spawn args (e.g., `--nightwatch-run-id ${id}`) and grep for that marker instead. Low priority for MVP on single-user machine.

3. **Log file rotation without external library**
   - What we know: 5 files × 10MB rotation locked in CONTEXT.md
   - What's unclear: Bun has no built-in rotating file writer
   - Recommendation: Implement simple size-check-and-rotate in the custom logger's `writeToFile()` helper: check file size before each write, rotate (rename → `.1`, `.2`, etc.) when >10MB. ~20 lines, no dependency.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `bun test` (built-in, Jest-compatible API) |
| Config file | `app/bunfig.toml` with `[test]` section — Wave 0 creates it |
| Quick run command | `bun test --filter "worker\|server\|shared"` (from `kc-nightwatch/app/`) |
| Full suite command | `bun test` (from `kc-nightwatch/app/`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FOUND-01 | Server spawns worker; worker sends heartbeat; server receives it | integration | `bun test --filter ipc` | ❌ Wave 0 |
| FOUND-02 | SIGTERM on server kills worker cleanly within 35s | integration | `bun test --filter shutdown` | ❌ Wave 0 |
| FOUND-03 | Worker crash → server detects via `exited` → cleans orphans → restarts with backoff | integration | `bun test --filter crash-recovery` | ❌ Wave 0 |
| FOUND-04 | After worker crash, server restart succeeds (no EADDRINUSE loop with Bun IPC) | integration | `bun test --filter startup` | ❌ Wave 0 |
| FOUND-05 | Run that exceeds `max_runtime_minutes` gets SIGKILL; status set to `timeout` | unit | `bun test --filter executor` | ❌ Wave 0 |
| FOUND-06 | Orphan `safehouse.*claude` PIDs killed on server startup | unit (mock pgrep) | `bun test --filter orphan-cleanup` | ❌ Wave 0 |
| FOUND-07 | First start creates `nightwatch-app.yaml` with valid defaults; second start reads it | unit | `bun test --filter yaml-store` | ❌ Wave 0 |
| FOUND-08 | After 51 runs, oldest run directory is deleted; 50 remain | unit | `bun test --filter artifact-cleanup` | ❌ Wave 0 |
| SEC-01 | Server binds to 127.0.0.1 by default | unit | `bun test --filter security` | ❌ Wave 0 |
| SEC-02 | Server refuses to start if host=0.0.0.0 and no token | unit | `bun test --filter security` | ❌ Wave 0 |
| SEC-03 | All endpoints return 401 without Bearer token in remote mode | integration | `bun test --filter auth-middleware` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `bun test --filter` on the module being implemented (< 5s)
- **Per wave merge:** `bun test` full suite
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `app/bunfig.toml` — `[test]` configuration, timeout settings
- [ ] `app/tests/shared/types.test.ts` — Zod schema validation for AppConfig, Run, IPC messages
- [ ] `app/tests/server/yaml-store.test.ts` — covers FOUND-07 (bootstrap + read)
- [ ] `app/tests/server/security.test.ts` — covers SEC-01, SEC-02, SEC-03
- [ ] `app/tests/server/ipc.test.ts` — covers FOUND-01 (spawn + heartbeat)
- [ ] `app/tests/server/shutdown.test.ts` — covers FOUND-02
- [ ] `app/tests/server/crash-recovery.test.ts` — covers FOUND-03
- [ ] `app/tests/server/startup.test.ts` — covers FOUND-04
- [ ] `app/tests/worker/executor.test.ts` — covers FOUND-05, FOUND-06 (with mock pgrep)
- [ ] `app/tests/worker/artifact-cleanup.test.ts` — covers FOUND-08

---

## Sources

### Primary (HIGH confidence)
- [Bun IPC docs](https://bun.com/docs/guides/process/ipc) — `Bun.spawn({ ipc })`, `proc.send()`, `process.on('message')` patterns
- [Bun child process docs](https://bun.com/docs/runtime/child-process) — `Bun.spawn()`, `.exited` promise, `.kill()` method
- `.planning/research/STACK.md` — Library versions, IPC transport rationale, installation
- `.planning/research/PITFALLS.md` — All 6 pitfalls; Phase 1 owns Pitfalls 1, 2, 3, 4, 5
- `.planning/research/ARCHITECTURE.md` — Component responsibilities, build order, IPC message protocol
- `.planning/phases/01-foundation/01-CONTEXT.md` — All locked decisions for this phase
- `config/safety.yaml` — `max_runtime_minutes: 30`, used in FOUND-05 timeout enforcement
- [Claude Code CLI hang after result event — GitHub #25629](https://github.com/anthropics/claude-code/issues/25629) — Pitfall 1 workaround (force-kill after result)

### Secondary (MEDIUM confidence)
- [Hono Bun getting started](https://hono.dev/docs/getting-started/bun) — `Bun.serve()` hostname binding for SEC-01
- [Bun YAML docs](https://bun.com/docs/runtime/yaml) — parse-only confirmation; reason to use `yaml` npm for writes

### Tertiary (LOW confidence)
- None in Phase 1 scope — all critical patterns verified against official sources

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions from STACK.md (verified 2026-03-18 against official docs/npm)
- Architecture: HIGH — patterns from ARCHITECTURE.md + Bun official docs + CONTEXT.md locked decisions
- Pitfalls: HIGH — Pitfalls 1-5 verified against official GitHub issues and Bun docs; Pitfall 6 (tilde) from official safehouse docs

**Research date:** 2026-03-18
**Valid until:** 2026-04-17 (30 days — Bun and Hono have stable APIs; Claude CLI bug status may change)
