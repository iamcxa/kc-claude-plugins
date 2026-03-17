---
phase: 01-foundation
plan: 01
subsystem: infra
tags: [bun, hono, zod, ipc, typescript, process-lifecycle]

# Dependency graph
requires: []
provides:
  - "Bun project scaffold (package.json, tsconfig.json, bunfig.toml) with hono, zod, yaml dependencies"
  - "app/shared/types.ts: AppConfigSchema, AppConfig, Run, RunSummary, ParsedLogEvent, ServerToWorker, WorkerToServer, IpcMessage union"
  - "app/shared/constants.ts: all timing constants (HEARTBEAT_INTERVAL_MS=30s, HEARTBEAT_TIMEOUT_MS=90s, etc.)"
  - "app/shared/logger.ts: structured JSON logger with debug/info/warn/error, no external deps"
  - "app/server/ipc.ts: workerStatus, lastHeartbeatAt, handleWorkerMessage, sendToWorker, startHeartbeatWatchdog"
  - "app/server/routes/health.ts: GET /health returning { status, worker, last_heartbeat, uptime }"
  - "app/server/index.ts: Hono server + Bun.spawn native IPC + crash recovery backoff + SIGINT/SIGTERM handlers"
  - "app/worker/index.ts: process.on('message') dispatch + 30s heartbeat + shutdown handler"
  - "13 tests passing across 4 test files"
affects: [01-02, 01-03, all-phases]

# Tech tracking
tech-stack:
  added:
    - "bun@1.3.9 (runtime + test runner)"
    - "hono@^4.12.8 (HTTP server)"
    - "zod@^3.25.76 (schema validation)"
    - "yaml@^2.8.2 (YAML r/w — bun built-in is parse-only)"
    - "@types/bun@latest"
    - "biome@^0.3.3 (linter/formatter)"
  patterns:
    - "Bun native IPC (Bun.spawn ipc:true) for server-worker communication — no Unix socket"
    - "Module-level mutable state for IPC tracking (workerStatus, lastHeartbeatAt, workerProc)"
    - "TDD: RED (test file) → GREEN (implementation) per task"
    - "10-line structured JSON logger with process.env.LOG_LEVEL — no external logging library"
    - "Zod at boundaries: AppConfigSchema validates all config at parse time"

key-files:
  created:
    - "app/package.json"
    - "app/tsconfig.json"
    - "app/bunfig.toml"
    - "app/.gitignore"
    - "app/shared/types.ts"
    - "app/shared/constants.ts"
    - "app/shared/logger.ts"
    - "app/server/ipc.ts"
    - "app/server/routes/health.ts"
    - "app/server/index.ts"
    - "app/worker/index.ts"
    - "app/tests/shared/types.test.ts"
    - "app/tests/shared/constants.test.ts"
    - "app/tests/server/ipc.test.ts"
    - "app/tests/server/health.test.ts"
  modified: []

key-decisions:
  - "Bun native IPC (Bun.spawn ipc:true) used — not node:net Unix socket; eliminates socket file management entirely"
  - "Heartbeat timeout set to 90s (3 missed intervals) per RESEARCH.md open question recommendation"
  - "Initial smoke test shows worker 'offline' at t=5s — correct behavior; first heartbeat fires at t=30s"
  - "Zod v3 pinned (^3.0.0) — v4 auto-installed by bun but plan specifies v3 API"

patterns-established:
  - "Pattern: Bun native IPC parent-child — server spawns worker, receives messages via ipc() callback"
  - "Pattern: Module-level export mutable state — workerStatus/lastHeartbeatAt exported directly, not wrapped in getter"
  - "Pattern: Crash recovery with indexed backoff array — WORKER_RESTART_BACKOFF_MS[restartCount++]"
  - "Pattern: Lazy dynamic import for shutdown — import('./ipc.ts') inside shutdown() gets current reference"

requirements-completed:
  - FOUND-01

# Metrics
duration: 5min
completed: 2026-03-18
---

# Phase 1 Plan 01: Foundation Scaffold Summary

**Two-process Bun app skeleton with Hono HTTP server, Bun native IPC worker, 30s heartbeat liveness, GET /health endpoint, and 13 passing tests**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-17T18:23:34Z
- **Completed:** 2026-03-17T18:28:15Z
- **Tasks:** 2 of 2
- **Files modified:** 15 created, 0 modified

## Accomplishments

- Bun project scaffold with strict TypeScript, hono + zod + yaml dependencies, bunfig.toml test config
- All shared types and constants defined: AppConfigSchema (Zod), Run, RunSummary, ParsedLogEvent, IpcMessage union, 12 constants
- Server spawns worker using Bun native IPC (`ipc: true` callback); worker sends heartbeat every 30s via `process.send`
- GET /health returns `{"status":"ok","worker":"online"}` when worker is live, `"degraded"` when offline
- Heartbeat watchdog checks every 10s, marks worker offline after 90s without heartbeat
- Worker crash recovery with exponential backoff (2s, 5s, 15s, then permanent offline)
- Graceful SIGINT/SIGTERM shutdown: sends `{ type: 'shutdown' }` to worker, waits up to 35s, then exits

## Task Commits

1. **Task 1: Project scaffold, shared types, and test stubs** - `23f03d0` (feat)
2. **Task 2: Server entry point, Bun IPC spawn, worker heartbeat, health endpoint** - `150c98d` (feat)

## Files Created/Modified

- `app/package.json` — Bun project manifest (name: nightwatch-app, start/dev/test scripts)
- `app/tsconfig.json` — Strict TypeScript (ESNext, bundler moduleResolution, noEmit)
- `app/bunfig.toml` — `[test]` section with 10s timeout
- `app/.gitignore` — logs/, runs/, nightwatch-app.yaml, *.bak added
- `app/shared/types.ts` — IpcMessage union, AppConfigSchema (Zod), Run, RunSummary, ParsedLogEvent
- `app/shared/constants.ts` — HEARTBEAT_INTERVAL_MS=30000, HEARTBEAT_TIMEOUT_MS=90000, all timing constants
- `app/shared/logger.ts` — 10-line structured JSON logger, LOG_LEVEL env var, no external deps
- `app/server/ipc.ts` — workerStatus, lastHeartbeatAt, handleWorkerMessage, sendToWorker, startHeartbeatWatchdog
- `app/server/routes/health.ts` — GET /health Hono route
- `app/server/index.ts` — Hono server, Bun.spawn with ipc callback, crash recovery, signal handlers
- `app/worker/index.ts` — process.on('message') dispatch, heartbeat timer, shutdown/status/enqueue/cancel handlers
- `app/tests/shared/types.test.ts` — 4 tests for AppConfigSchema
- `app/tests/shared/constants.test.ts` — 5 tests for constants values
- `app/tests/server/ipc.test.ts` — 2 tests for heartbeat handling
- `app/tests/server/health.test.ts` — 2 tests for GET /health with worker status

## Interfaces Exported from shared/types.ts

```typescript
// IPC unions
export type ServerToWorker = { type: 'enqueue'; run: Run } | { type: 'cancel'; run_id: string } | { type: 'shutdown' } | { type: 'status' }
export type WorkerToServer = { type: 'heartbeat'; ts: number } | { type: 'run:started'; run_id: string; pid: number } | { type: 'run:log'; run_id: string; event: ParsedLogEvent } | { type: 'run:completed'; run_id: string; summary: RunSummary } | { type: 'run:failed'; run_id: string; error: string } | { type: 'state'; queue: Run[]; current?: Run }
export type IpcMessage = ServerToWorker | WorkerToServer

// Zod schema
export const AppConfigSchema = z.object({ host, port, auth_token, schedule: { enabled, interval_hours, self_repair_before }, max_concurrent_runs: z.literal(1), safehouse_path, plugins_dir })
export type AppConfig = z.infer<typeof AppConfigSchema>

// Domain interfaces
export interface Run { id, target, mode, trigger, status, custom_prompt?, started_at?, completed_at?, duration_seconds?, log_path }
export interface RunSummary { phases_completed, signals_found, actions_taken, errors }
export interface ParsedLogEvent { type, content?, raw }
```

## Constants Exported from shared/constants.ts

```typescript
HEARTBEAT_INTERVAL_MS = 30_000       // Worker sends heartbeat every 30s
HEARTBEAT_TIMEOUT_MS = 90_000        // Server marks offline after 3 missed heartbeats
WORKER_RESTART_BACKOFF_MS = [2000, 5000, 15000]
MAX_WORKER_RESTARTS = 3
RESULT_FORCE_KILL_DELAY_MS = 10_000  // Force-kill claude after result event (CLI bug workaround)
ORPHAN_SIGTERM_WAIT_MS = 3000
SHUTDOWN_WORKER_TIMEOUT_MS = 35_000  // Grace period before SIGKILL
KEEP_RUNS_COUNT = 50
DEFAULT_PORT = 3200
DEFAULT_HOST = '127.0.0.1'
LOG_ROTATION_MAX_SIZE = 10 * 1024 * 1024  // 10MB
LOG_ROTATION_MAX_FILES = 5
```

## IPC Messages Produced by Worker (for Plan 01-02 reference)

Worker sends to server via `process.send()`:
- `{ type: 'heartbeat', ts: Date.now() }` — every HEARTBEAT_INTERVAL_MS (30s)
- `{ type: 'state', queue: [], current: undefined }` — on startup and in response to 'status' command
- `{ type: 'run:started', run_id, pid }` — when executor starts a run (Phase 2)
- `{ type: 'run:log', run_id, event }` — stream-json log events (Phase 2)
- `{ type: 'run:completed', run_id, summary }` — on run success (Phase 2)
- `{ type: 'run:failed', run_id, error }` — on run failure (Phase 2)

## Decisions Made

- **Bun native IPC chosen**: Confirmed `Bun.spawn({ ipc: true })` over node:net Unix socket. Eliminates socket file management, EADDRINUSE risk, and reconnect loop code entirely.
- **Heartbeat timeout 90s**: Per RESEARCH.md open question recommendation — 3 missed intervals gives buffer for system sleep/throttle.
- **Zod v3 pinned**: `bun add zod` installed v4.3.6, but plan specifies v3 API. Explicitly pinned to `^3.0.0`.
- **Module-level mutable state**: `workerStatus` and `lastHeartbeatAt` exported as module-level `let` variables for simplicity — avoids getter/setter boilerplate while keeping tests clean.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Pinned zod to v3 instead of auto-installed v4**
- **Found during:** Task 1 (project scaffold)
- **Issue:** `bun add zod` installed v4.3.6; plan specifies `"zod": "^3.0.0"`. Zod v4 has breaking API changes and different module paths.
- **Fix:** Ran `bun add zod@^3.0.0` to pin to v3
- **Files modified:** app/package.json, app/bun.lock
- **Verification:** `bun pm ls | grep zod` shows `zod@3.25.76`
- **Committed in:** 23f03d0 (Task 1 commit)

**2. [Rule 3 - Blocking] Added `void` wrapper on SIGINT/SIGTERM handlers**
- **Found during:** Task 2 (server/index.ts)
- **Issue:** TypeScript strict mode: `process.on('SIGINT', () => shutdown('SIGINT'))` causes "Promise returned from event handler ignored" — shutdown() is async but process.on callback doesn't await.
- **Fix:** Added `void` wrapper: `process.on('SIGINT', () => { void shutdown('SIGINT') })`
- **Files modified:** app/server/index.ts
- **Verification:** TypeScript strict mode satisfied, tests pass
- **Committed in:** 150c98d (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** Both auto-fixes required for correctness. No scope creep.

## Issues Encountered

- Smoke test at t=5s showed `"worker":"offline"` — this is correct behavior (first heartbeat at t=30s). The worker is spawned but the server doesn't mark it online until receiving the first heartbeat message.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All shared types and IPC contracts are in place for Plan 01-02 (executor, orphan cleanup, yaml-store)
- Plan 01-02 can import from `shared/types.ts`, `shared/constants.ts`, and `server/ipc.ts` directly
- FOUND-01 satisfied: server spawns worker with native IPC, worker sends heartbeats, server tracks liveness via GET /health
- Remaining FOUND-xx requirements (02-08) and SEC-xx requirements handled in Plans 01-02 and 01-03

---
*Phase: 01-foundation*
*Completed: 2026-03-18*

## Self-Check: PASSED

- All 15 files created and verified on disk
- Both task commits verified: 23f03d0, 150c98d
- 13/13 tests passing
- No node:net or .sock references found
- shared/types.ts has no `any` type annotations
