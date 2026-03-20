---
phase: 02-core-cockpit
plan: "01"
subsystem: api
tags: [hono, bun, sse, yaml, ipc, rest-api, types]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: Hono server, ipc.ts worker IPC, yaml-store, auth middleware, Run/AppConfig/ParsedLogEvent types
provides:
  - Target type (full nightwatch-targets.yaml v2 schema with Appendix A compat)
  - ScheduleConfig exported standalone type
  - RunSummary full Appendix B shape (per_target, indicator_baseline, actions[], implementation_outcomes)
  - ParsedLogEvent extended (phase, tool_name, agent_name, is_phase_start)
  - SSE fan-out: subscribeToRun(), fanOutLogEvent(), closeRunSubscribers() in ipc.ts
  - REST API routes (api.ts): /api/targets, /api/runs, /api/webhook
  - SSE stream route (stream.ts): /api/runs/:id/stream
  - Schedule API (schedule.ts): GET+PUT /api/schedule
  - run-store service: listRuns(), getRun(), appendRun()
  - yaml-store extensions: readTargets() (Appendix A compat), writeAppConfig()
  - log-parser.ts: phase/tool_name/agent_name extraction from stream events
affects: [02-02-worker-nw-memory, 02-03-frontend-dashboard]

# Tech tracking
tech-stack:
  added: [hono/streaming for SSE]
  patterns:
    - Hono route modules (Hono app exported as named const, mounted via app.route)
    - SSE fan-out via Map<runId, Set<SSEWriter>> with AbortSignal cleanup
    - Appendix A field normalization (monitors/sources, watch/keywords, respond/actions)
    - TDD: write failing tests first, implement to GREEN

key-files:
  created:
    - app/server/routes/api.ts
    - app/server/routes/stream.ts
    - app/server/routes/schedule.ts
    - app/server/services/run-store.ts
    - app/tests/server/api.test.ts
    - app/tests/server/sse.test.ts
    - app/tests/server/schedule.test.ts
  modified:
    - app/shared/types.ts
    - app/server/ipc.ts
    - app/server/services/yaml-store.ts
    - app/server/index.ts
    - app/worker/log-parser.ts
    - app/worker/executor.ts
    - app/tests/shared/types.test.ts

key-decisions:
  - "RunSummary phases_completed kept as optional field for Phase 1 executor backward compat"
  - "SSE subscribers stored as Map<runId, Set<SSEWriter>> — O(1) lookup, auto-cleaned on run complete/fail"
  - "readTargets() normalizes both old (sources/keywords/actions/proxy_signals) and new field names at read time — no migration needed"
  - "writeAppConfig() always re-creates Bun.file handle (Pitfall: stale handle after write)"
  - "POST /api/runs returns 202 immediately (never awaits run completion) — worker gets enqueue IPC async"

patterns-established:
  - "Route module pattern: create new Hono(), export as named const, mount via app.route('/', xRoutes) in index.ts"
  - "SSE cleanup pattern: subscribeToRun returns cleanup fn, AbortSignal addEventListener handles disconnect"
  - "Worker offline check: workerStatus !== 'online' returns 503 before any run dispatch"

requirements-completed:
  - DASH-01
  - DASH-03
  - DASH-04
  - EXEC-01
  - EXEC-02
  - EXEC-03
  - EXEC-06
  - EXEC-07
  - EXEC-08
  - SCHED-02
  - SCHED-03
  - HIST-01
  - HIST-02
  - HIST-03

# Metrics
duration: 6min
completed: 2026-03-18
---

# Phase 2 Plan 01: Core Cockpit Backend Summary

**REST API + SSE fan-out infrastructure: 9 endpoints callable via curl, run:log IPC wired to browser SSE, RunSummary upgraded to full Appendix B shape with per_target/indicator_baseline/actions**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-18T02:19:53Z
- **Completed:** 2026-03-18T02:26:18Z
- **Tasks:** 2
- **Files modified:** 14

## Accomplishments
- Full shared type layer: Target, ScheduleConfig, RunSummary (Appendix B), ParsedLogEvent (extended), IPC schedule message
- SSE fan-out in ipc.ts: subscribeToRun/fanOutLogEvent/closeRunSubscribers wired to handleWorkerMessage for run:log/run:completed/run:failed
- 7 REST endpoints across 3 new route modules: /api/targets, /api/runs (CRUD), /api/webhook, GET+PUT /api/schedule, /api/runs/:id/stream
- run-store service: listRuns(filter?), getRun(id), appendRun() reading nightwatch-runs.yaml
- yaml-store extended: readTargets() with Appendix A compat normalization, writeAppConfig()
- log-parser.ts extracts phase headers, tool_name from tool_use blocks, agent_name from dispatch text
- 77 tests pass (19 new: api + sse + schedule); tsc --noEmit clean

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend shared types** - `1b51c1e` (feat)
2. **Task 2: SSE fan-out + route modules + run-store + yaml-store + server wiring** - `356d6a9` (feat)

## Files Created/Modified
- `app/shared/types.ts` — Extended with Target, ScheduleConfig, RunSummary (Appendix B), ParsedLogEvent (Phase 2 fields), IPC schedule message
- `app/server/ipc.ts` — SSE fan-out state + subscribeToRun/fanOutLogEvent/closeRunSubscribers + run:log/run:completed/run:failed IPC cases
- `app/server/routes/api.ts` — GET/POST /api/targets, GET/POST/DELETE /api/runs, POST /api/webhook
- `app/server/routes/stream.ts` — GET /api/runs/:id/stream with 60s keepalive + 35min max
- `app/server/routes/schedule.ts` — GET+PUT /api/schedule
- `app/server/services/run-store.ts` — listRuns(), getRun(), appendRun() over nightwatch-runs.yaml
- `app/server/services/yaml-store.ts` — readTargets() (Appendix A compat), writeAppConfig()
- `app/server/index.ts` — Mount apiRoutes, streamRoutes, scheduleRoutes
- `app/worker/log-parser.ts` — Extract phase/tool_name/agent_name/is_phase_start from stream events
- `app/worker/executor.ts` — Updated to use new RunSummary shape (legacy compat via legacyPhases var)
- `app/tests/server/api.test.ts` — 12 tests covering all API endpoints
- `app/tests/server/sse.test.ts` — 5 tests: fan-out delivery, closeRunSubscribers, AbortSignal cleanup
- `app/tests/server/schedule.test.ts` — GET/PUT /api/schedule tests

## Decisions Made
- phases_completed kept as optional backward-compat field in RunSummary so executor.ts Phase 1 code compiles without migration
- writeAppConfig() uses Bun.write directly (not re-using pre-write handle) per Pitfall rule from Phase 1 (01-03)
- POST /api/runs returns 202 immediately and dispatches enqueue IPC — never awaits run completion

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fix executor.ts RunSummary shape mismatch**
- **Found during:** Task 1 (extend shared types)
- **Issue:** executor.ts constructs `{ phases_completed: [], signals_found: 0, actions_taken: 0, errors: [] }` — doesn't match new RunSummary shape, causes 4 TypeScript errors
- **Fix:** Introduced `legacyPhases: string[]` local variable, constructed full RunSummary with zero defaults, kept phases_completed as optional legacy compat field
- **Files modified:** `app/worker/executor.ts`
- **Verification:** `tsc --noEmit` exits 0
- **Committed in:** `1b51c1e` (Task 1 commit)

**2. [Rule 1 - Bug] Fix TypeScript union type narrowing in webhook route**
- **Found during:** Task 2 (api.ts webhook handler)
- **Issue:** `.catch(() => ({}))` returns `{} | ParsedBody` union — TypeScript can't access `.target`/`.mode` properties on `{}`
- **Fix:** Added explicit cast: `.catch(() => ({} as { target?: string; mode?: Run['mode'] }))`
- **Files modified:** `app/server/routes/api.ts`
- **Verification:** `tsc --noEmit` exits 0
- **Committed in:** `356d6a9` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 - type correctness)
**Impact on plan:** Both auto-fixes necessary for TypeScript correctness. No scope creep.

## Issues Encountered
None beyond the two auto-fixed TypeScript issues above.

## User Setup Required
None - no external service configuration required. The `nightwatch-runs.yaml` and `nightwatch-targets.yaml` files are read from `~/.claude/kc-plugins-config/` at runtime (created by Phase 1 config bootstrap if absent).

## Next Phase Readiness
- All 9 REST endpoints callable via curl or test suite
- SSE stream wired: run:log IPC → fanOutLogEvent → browser connections
- SSE cleanup: closeRunSubscribers called on run:completed and run:failed (no memory leak)
- Plan 02-02 (worker NW memory isolation) and 02-03 (frontend) can now build on real API endpoints
- No blockers

---
*Phase: 02-core-cockpit*
*Completed: 2026-03-18*
