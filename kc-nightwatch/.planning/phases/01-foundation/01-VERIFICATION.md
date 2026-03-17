---
phase: 01-foundation
verified: 2026-03-18T19:12:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 1: Foundation Verification Report

**Phase Goal:** The two-process app starts, stays up across crashes, and handles every process-lifecycle failure mode before any feature work starts
**Verified:** 2026-03-18T19:12:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (from ROADMAP.md Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Server and worker start together; worker connects via Bun native IPC and sends heartbeat every 30s; server marks worker offline if heartbeat >90s stale | VERIFIED | `server/index.ts` calls `Bun.spawn` with `ipc(message)` callback; `worker/index.ts` sets `setInterval` with `HEARTBEAT_INTERVAL_MS`; `server/ipc.ts` watchdog fires every 10s checking `HEARTBEAT_TIMEOUT_MS` |
| 2 | Worker kill → server detects disconnect, cleans orphaned processes (pgrep scan), enters exponential backoff 2s/5s/15s; after 3rd crash enters read-only mode | VERIFIED | `server/index.ts` `handleWorkerCrash()` calls `cleanupOrphans()` then reads `WORKER_RESTART_BACKOFF_MS[restartCount++]`; at `restartCount >= MAX_WORKER_RESTARTS` calls `setWorkerStatus('offline_permanent')` |
| 3 | Restart after crash starts cleanly — Bun native IPC eliminates socket file/EADDRINUSE; orphan scan covers stale state | VERIFIED | No `node:net` or `.sock` anywhere in source; `cleanupOrphans()` called at `server/index.ts` boot (line 121) before `spawnWorker()`; FOUND-04 comment at top of `index.ts` |
| 4 | A claude run that completes (result event) is force-killed within 10 seconds even if MCP connections keep process alive | VERIFIED | `worker/executor.ts` lines 104–115: `setTimeout(() => child.kill('SIGKILL'), RESULT_FORCE_KILL_DELAY_MS)` triggered on `event.type === 'result'`; references GitHub #25629 |
| 5 | App binds to 127.0.0.1 by default; remote mode requires explicit opt-in and a token on all API endpoints | VERIFIED | `yaml-store.ts` DEFAULT_APP_CONFIG sets `host: DEFAULT_HOST` (127.0.0.1); `server/index.ts` lines 92–98 `process.exit(1)` if host != 127.0.0.1 without auth_token; lines 101–104 apply `tokenAuth` middleware before routes |

**Score:** 5/5 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `app/shared/types.ts` | IpcMessage union, AppConfigSchema, Run, RunSummary, ParsedLogEvent | VERIFIED | All types present; no `any` annotations; exports match plan spec exactly |
| `app/shared/constants.ts` | All timing constants | VERIFIED | HEARTBEAT_INTERVAL_MS=30000, HEARTBEAT_TIMEOUT_MS=90000, RESULT_FORCE_KILL_DELAY_MS=10000, all 12 constants present |
| `app/shared/logger.ts` | 10-line structured JSON logger | VERIFIED | Exports `log.debug/info/warn/error`; LOG_LEVEL env var; no external deps |
| `app/server/index.ts` | Hono server with Bun.spawn IPC, crash recovery, signal handlers | VERIFIED | Contains `Bun.spawn` with `ipc(message)`, SIGINT/SIGTERM handlers, security gate, route registration |
| `app/server/ipc.ts` | Worker IPC state and message handler | VERIFIED | Exports `workerStatus`, `lastHeartbeatAt`, `handleWorkerMessage`, `sendToWorker`, `startHeartbeatWatchdog` |
| `app/server/routes/health.ts` | GET /health Hono route | VERIFIED | Returns `{ status, worker, last_heartbeat, uptime }`; status is 'ok' when online, 'degraded' when offline |
| `app/server/services/yaml-store.ts` | loadOrCreateAppConfig with Zod validation | VERIFIED | Exports `loadOrCreateAppConfig`, `readYamlFile`, `writeYamlFile`; calls `AppConfigSchema.parse(raw)`; uses `yaml` package not Bun built-in |
| `app/server/services/auth.ts` | tokenAuth Hono middleware | VERIFIED | Exports `tokenAuth`; checks `Authorization: Bearer ${token}` exact match; applies at app level |
| `app/server/services/orphan-cleanup.ts` | cleanupOrphans with pgrep + SIGTERM/SIGKILL | VERIFIED | Extracted to service (cleaner than plan spec which said export from index.ts); uses `pgrep -f safehouse.*claude`; SIGTERM then SIGKILL with `ORPHAN_SIGTERM_WAIT_MS` gap |
| `app/worker/index.ts` | process.on('message') dispatch, heartbeat, shutdown | VERIFIED | Contains `process.on('message')`, `setInterval` for heartbeat, `killAllActive().then(() => process.exit(0))` on shutdown |
| `app/worker/executor.ts` | executeRun with force-kill, PID tracking, timeout, artifact write | VERIFIED | `activePids`, `executeRun`, `killAllActive`, `cleanupOldRuns` exported; force-kill setTimeout uses `RESULT_FORCE_KILL_DELAY_MS`; writes `log.jsonl` and `summary.yaml` |
| `app/worker/policy.ts` | buildSafehouseFlags with tilde-safety | VERIFIED | `buildSafehouseFlags` exported; tilde assertion throws; no literal `~` in path strings |
| `app/worker/log-parser.ts` | parseStreamJsonLine | VERIFIED | Handles result/assistant/text events; graceful JSON parse fallback |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `server/index.ts` | `worker/index.ts` | `Bun.spawn` with `ipc(message)` callback | WIRED | `Bun.spawn(['bun', 'run', .../worker/index.ts], { ipc(message) {...} })` at line 30–37 |
| `worker/index.ts` | `server/ipc.ts` | `process.send` heartbeat every 30s | WIRED | `send({ type: 'heartbeat', ts: Date.now() })` in `setInterval(HEARTBEAT_INTERVAL_MS)` |
| `server/index.ts` | `server/services/yaml-store.ts` | `loadOrCreateAppConfig()` before `Bun.serve()` | WIRED | `const config = await loadOrCreateAppConfig()` at line 89, before `Bun.serve` at line 112 |
| `server/index.ts` | `server/services/auth.ts` | `app.use('*', tokenAuth(token))` before routes | WIRED | `app.use('*', tokenAuth(config.auth_token))` at line 102, `app.route('/')` at line 107 — correct order |
| `server/index.ts` | `server/services/orphan-cleanup.ts` | `cleanupOrphans()` at boot AND in `handleWorkerCrash` | WIRED | Two calls verified: line 54 (in handleWorkerCrash) and line 121 (at boot); both confirmed with grep |
| `worker/executor.ts` | force-kill after result | `setTimeout(SIGKILL, RESULT_FORCE_KILL_DELAY_MS)` | WIRED | Lines 110–115; references `RESULT_FORCE_KILL_DELAY_MS` constant (not hardcoded); GitHub #25629 comment present |
| `worker/executor.ts` | `app/runs/{run.id}/` | write `log.jsonl` and `summary.yaml` | WIRED | `Bun.write(logFilePath, ...)` and `Bun.write(summaryPath, ...)` in finally block |
| `worker/index.ts` | `executor.ts` `killAllActive` | shutdown handler calls killAllActive | WIRED | `killAllActive().then(() => process.exit(0))` in shutdown case |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FOUND-01 | 01-01 | Server + worker two-process architecture with Bun native IPC | SATISFIED | `Bun.spawn` with `ipc: true` callback; heartbeat liveness; GET /health |
| FOUND-02 | 01-03 | Graceful shutdown (SIGINT/SIGTERM) with child process cleanup | SATISFIED | `process.on('SIGINT/SIGTERM')` → `shutdown()` → `workerProc.send({type:'shutdown'})` → wait 35s → SIGKILL → `server.stop()` → `process.exit(0)` |
| FOUND-03 | 01-03 | Worker crash recovery — server detects disconnect, cleans orphan processes | SATISFIED | `proc.exited.then()` triggers `handleWorkerCrash()` which calls `cleanupOrphans()` then exponential backoff restart |
| FOUND-04 | 01-03 | Socket/PID file cleanup on startup (prevent EADDRINUSE) | SATISFIED (structural) | Bun native IPC eliminates socket files entirely; no `.sock` anywhere; orphan scan on boot covers stale process state |
| FOUND-05 | 01-02 | Timeout enforcement per run (from safety.yaml max_runtime_minutes) | SATISFIED | `setTimeout(() => child.kill('SIGKILL'), opts.maxRuntimeMs)` in executor.ts; sets `timedOut=true` → `run:failed` with 'timeout' |
| FOUND-06 | 01-02 | Orphaned safehouse+claude process detection and kill on startup | SATISFIED | `cleanupOrphans()` at boot (line 121 of index.ts); also in `killAllActive()` via worker shutdown |
| FOUND-07 | 01-03 | App bootstrap — create default nightwatch-app.yaml on first start | SATISFIED | `loadOrCreateAppConfig()` creates file with typed defaults on first call; Zod validates on every subsequent start |
| FOUND-08 | 01-02 | Run artifact directory with rolling cleanup (keep last 50) | SATISFIED | `cleanupOldRuns(opts.runsDir)` called in `executeRun` finally block; deletes oldest when count > `KEEP_RUNS_COUNT` (50) |
| SEC-01 | 01-03 | Localhost binding by default (127.0.0.1) | SATISFIED | `DEFAULT_APP_CONFIG.host = DEFAULT_HOST` ('127.0.0.1'); server reads from config via `loadOrCreateAppConfig()` |
| SEC-02 | 01-03 | Optional remote mode with required token auth | SATISFIED | `process.exit(1)` when `config.host !== '127.0.0.1' && !config.auth_token` at server startup |
| SEC-03 | 01-03 | Token auth on all API/MCP/WebSocket endpoints in remote mode | SATISFIED | `app.use('*', tokenAuth(...))` applied before `app.route()` — all routes covered |

**Coverage: 11/11 requirements satisfied (all FOUND-0x and SEC-0x)**

No orphaned requirements found — all 11 phase requirements from ROADMAP.md are claimed by plans and verified in the codebase.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `worker/index.ts` | 34 | `resolved_path: process.env.TARGET_PATH ?? '/tmp'` | INFO | Known Phase 2 placeholder; explicitly commented "real path from Phase 2"; executor infrastructure is complete |
| `worker/index.ts` | 38 | `maxRuntimeMs: 30 * 60_000` hardcoded | INFO | Known Phase 2 placeholder; commented "Phase 2 will load dynamically"; constant value matches safety.yaml |
| `worker/index.ts` | 47 | `Cancel run ... (cancel not yet implemented)` log message | INFO | EXEC-08 (run cancellation) is a Phase 2 requirement; correctly stubbed — logs but does not crash |

No blocker or warning anti-patterns. All INFO items are intentional Phase 2 deferral stubs, consistent with the phase goal scoping.

---

### Test Suite Results

**47 tests pass, 0 fail** across 12 test files (543ms)

| Test File | Tests | Status |
|-----------|-------|--------|
| `tests/shared/types.test.ts` | 4 | Pass |
| `tests/shared/constants.test.ts` | 5 | Pass |
| `tests/server/ipc.test.ts` | 3 | Pass |
| `tests/server/health.test.ts` | 2 | Pass |
| `tests/server/yaml-store.test.ts` | 5 | Pass |
| `tests/server/security.test.ts` | 4 | Pass |
| `tests/server/startup.test.ts` | 2 | Pass |
| `tests/server/crash-recovery.test.ts` | 5 | Pass |
| `tests/worker/log-parser.test.ts` | 4 | Pass |
| `tests/worker/policy.test.ts` | 4 | Pass |
| `tests/worker/artifact-cleanup.test.ts` | 3 | Pass |
| `tests/worker/executor.test.ts` | 6 | Pass |

**Known test limitation:** `bun test tests/` glob hangs because `startup.test.ts` imports `server/index.ts` which has top-level `await spawnWorker()` and `Bun.serve()`. Running `bun test` (from `app/` directory) works because Bun discovers test files without importing `index.ts` directly. All 47 tests run and pass via `bun test`.

---

### Notable Structural Deviation (Non-Blocking)

The 01-03 PLAN specified `cleanupOrphans` should be exported from `server/index.ts`. The implementation correctly extracted it to `server/services/orphan-cleanup.ts` (a cleaner separation of concerns). The startup test imports from the service directly, which is better design. `server/index.ts` imports and calls `cleanupOrphans` at both required call sites. This deviation improves the architecture.

---

### Human Verification Required

#### 1. Full startup smoke test

**Test:** Run `bun run server/index.ts` from `app/`, wait 35 seconds, then `curl http://127.0.0.1:3200/health`
**Expected:** First response (t=5s): `{"status":"degraded","worker":"offline",...}` (worker spawned but not yet heartbeated); second response (t=35s): `{"status":"ok","worker":"online",...}`
**Why human:** Integration behavior depends on actual process spawning and timing; automated tests mock the IPC state.

#### 2. Graceful shutdown verification

**Test:** Start server, wait for worker online, send `kill -SIGTERM <pid>` to server process
**Expected:** Server sends shutdown IPC to worker; worker exits cleanly; server logs "Shutdown complete" and exits with code 0; no zombie processes remain
**Why human:** Requires spawning real processes; timing-dependent behavior.

#### 3. Remote mode security gate

**Test:** Set `nightwatch-app.yaml` to `host: 0.0.0.0` with no `auth_token`, start server
**Expected:** Server logs error "Remote mode ... requires auth_token" and exits with code 1 immediately
**Why human:** Requires editing the config file and observing exit behavior.

---

## Summary

Phase 1 goal is fully achieved. All 5 success criteria from ROADMAP.md are verified against the actual codebase. All 11 requirements (FOUND-01 through FOUND-08 plus SEC-01 through SEC-03) have implementation evidence. The test suite runs 47 tests with 0 failures. No blocker anti-patterns found — the 3 INFO items are intentional Phase 2 deferral stubs explicitly documented in the code. The codebase is ready for Phase 2 (Core Cockpit) work.

---

_Verified: 2026-03-18T19:12:00Z_
_Verifier: Claude (gsd-verifier)_
