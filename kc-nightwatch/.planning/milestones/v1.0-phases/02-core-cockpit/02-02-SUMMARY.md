---
phase: 02-core-cockpit
plan: "02"
subsystem: worker
tags: [bun, ipc, queue, scheduler, mcp, memory-isolation, executor, tdd]

# Dependency graph
requires:
  - phase: 02-01
    provides: "readTargets(), readYamlFile(), types (ScheduleConfig, Target, Run), IPC message types"
  - phase: 01-foundation
    provides: "executor.ts with activePids + executeRun, policy.ts with buildSafehouseFlags, worker/index.ts skeleton"
provides:
  - "FIFO execution queue with max concurrency 1 (EXEC-09)"
  - "Real target path resolution from nightwatch-targets.yaml (fixes TARGET_PATH /tmp stub)"
  - "Cancel IPC: SIGTERM for active run via activePids, splice for queued runs (EXEC-08)"
  - "Interval scheduler: startScheduler/stopScheduler/getNextRunAt with 'schedule' IPC wiring (SCHED-01)"
  - "SCHEDULER_RUNS_ALL_TARGET='__all__' constant with __all__ expansion in queue"
  - "ensureNwMemoryDir: per-target ~/.claude/nightwatch/memory/{name}/.private-journal/ (MEM-01)"
  - "writeNwJournalConfig: per-run nw-journal.json MCP config with private-journal stdio (MEM-02)"
  - "--mcp-config flag injected into claude -p args (MEM-03 isolation enforced)"
  - "safety.yaml max_runtime_minutes loaded dynamically at worker startup"
affects:
  - "02-03 (frontend): worker state message includes queue + currentRun for UI display"
  - "02-04 (server routes): schedule IPC from server triggers startScheduler in worker"
  - "Phase 3 (chat): each run has isolated NW journal memory via --mcp-config"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "FIFO queue with processNextRun drain: processNextRun checks currentRun guard, shifts queue, awaits run, recurses"
    - "TDD: RED (import fails) → GREEN (implement) → type-check clean (bun tsc --noEmit)"
    - "Fractional hours for sub-second scheduler test intervals (1/3_600_000 hours = 1ms)"

key-files:
  created:
    - "app/worker/scheduler.ts"
    - "app/tests/worker/queue.test.ts"
    - "app/tests/worker/scheduler.test.ts"
  modified:
    - "app/worker/index.ts"
    - "app/worker/executor.ts"
    - "app/shared/constants.ts"
    - "app/tests/worker/executor.test.ts"

key-decisions:
  - "self_repair_before is required in ScheduleConfig (not optional) — test configs must include it"
  - "0.001 hours = 3600ms not 3.6ms — scheduler test uses 1/3_600_000 hours for 1ms interval"
  - "__all__ target expanded inline in processNextRun (sub-runs pushed to queue, drain handles them)"
  - "ensureNwMemoryDir exported from executor.ts so it can be tested independently"
  - "writeNwJournalConfig uses JSON pretty-print (2 spaces) for readability"

patterns-established:
  - "Pattern: Worker queue drain — processNextRun() calls itself in finally block to chain runs"
  - "Pattern: Anti-tilde rule enforced — os.homedir() + path.join, never template literal '~'"
  - "Pattern: Per-run MCP config file isolation — nw-journal.json written to runs/{id}/ directory"

requirements-completed:
  - EXEC-04
  - EXEC-05
  - EXEC-08
  - EXEC-09
  - SCHED-01
  - MEM-01
  - MEM-02
  - MEM-03

# Metrics
duration: 5min
completed: 2026-03-18
---

# Phase 2 Plan 02: Worker Queue + NW Memory Isolation Summary

**FIFO execution queue (max concurrency 1), real target path resolution from nightwatch-targets.yaml, interval scheduler with IPC wiring, and per-target NW journal MCP injection via --mcp-config**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-18T02:29:35Z
- **Completed:** 2026-03-18T02:34:35Z
- **Tasks:** 2 (both TDD)
- **Files modified:** 7

## Accomplishments

- Rewrote worker/index.ts: FIFO queue, real target resolution (no more TARGET_PATH /tmp stub), cancel IPC (SIGTERM/splice), schedule IPC, __all__ expansion
- Created worker/scheduler.ts: setInterval-based startScheduler with nextRunAt tracking, replaces timer on restart
- Extended executor.ts: ensureNwMemoryDir + writeNwJournalConfig + --mcp-config injection (MEM-01/02/03)
- Full test coverage: 34 new/extended tests across queue.test.ts, scheduler.test.ts, executor.test.ts; 104 total suite green

## Task Commits

1. **Task 1: Worker queue, target resolution, cancel, scheduler** - `73afc16` (feat)
2. **Task 2: NW memory isolation in executor** - `62f7262` (feat)

## Files Created/Modified

- `app/worker/index.ts` — Rewritten: FIFO queue, resolveTarget(), cancel/schedule IPC, dynamic safety.yaml loading
- `app/worker/scheduler.ts` — New: startScheduler, stopScheduler, getNextRunAt
- `app/worker/executor.ts` — Extended: ensureNwMemoryDir, writeNwJournalConfig, --mcp-config in claudeArgs
- `app/shared/constants.ts` — Added: SCHEDULER_RUNS_ALL_TARGET = '__all__'
- `app/tests/worker/queue.test.ts` — New: EXEC-09 concurrency, EXEC-08 cancel tests
- `app/tests/worker/scheduler.test.ts` — New: SCHED-01 interval, disable, replace, getNextRunAt tests
- `app/tests/worker/executor.test.ts` — Extended: MEM-01/02/03 + cancel EXEC-08 pattern tests

## Decisions Made

- `self_repair_before` is required in `ScheduleConfig` (not optional) — all test configs must include it explicitly
- `0.001 hours = 3600ms not 3.6ms` — the plan's comment was wrong; used `1/3_600_000 hours = 1ms` for sub-millisecond timer tests
- `__all__` target expansion is inline in processNextRun (sub-runs pushed back to queue, drain chain handles them) rather than a separate expandRun helper
- `ensureNwMemoryDir` and `writeNwJournalConfig` exported from executor.ts (not private) to enable direct unit testing without spawning a run

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] ScheduleConfig.self_repair_before required, not optional**
- **Found during:** Task 1 (scheduler.test.ts TypeScript check)
- **Issue:** Test configs omitted `self_repair_before` field; TypeScript flagged 8 errors in scheduler.test.ts
- **Fix:** Added `self_repair_before: false` to all ScheduleConfig literals in the test file
- **Files modified:** app/tests/worker/scheduler.test.ts
- **Verification:** `bun run --bun tsc --noEmit` exits 0
- **Committed in:** 73afc16 (Task 1 commit)

**2. [Rule 1 - Bug] Plan's interval comment was wrong (0.001h = 3600ms, not 3.6ms)**
- **Found during:** Task 1 (scheduler timer test failure)
- **Issue:** Test used `interval_hours: 0.001` and waited 20ms — the interval is actually 3600ms so it never fired
- **Fix:** Changed to `1/3_600_000 hours` (= 1ms effective interval) and waited 50ms
- **Files modified:** app/tests/worker/scheduler.test.ts
- **Verification:** Test fires callback ≥1 time within 50ms
- **Committed in:** 73afc16 (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 - Bug)
**Impact on plan:** Both fixes were necessary for tests to type-check and run. No scope creep.

## Issues Encountered

None — both deviations were caught and fixed during TDD RED→GREEN cycle before proceeding.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Worker queue and scheduler ready for server-side schedule persistence (Plan 02-03/02-04)
- Per-target NW journal isolation in place — runs are fully memory-isolated from day one
- `__all__` target expansion works but requires targets loaded from nightwatch-targets.yaml at startup
- Note: if nightwatch-targets.yaml is missing, targetsMap is empty (logged as warning, not error)

---
*Phase: 02-core-cockpit*
*Completed: 2026-03-18*

## Self-Check: PASSED

- All 7 source files exist on disk
- Commit 73afc16 (Task 1) verified in git log
- Commit 62f7262 (Task 2) verified in git log
- SUMMARY.md at .planning/phases/02-core-cockpit/02-02-SUMMARY.md confirmed
