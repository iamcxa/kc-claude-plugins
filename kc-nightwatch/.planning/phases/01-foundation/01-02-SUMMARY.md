---
phase: 01-foundation
plan: 02
subsystem: infra
tags: [bun, spawn, safehouse, process-lifecycle, pid-tracking, stream-json, tdd]

# Dependency graph
requires:
  - phase: 01-01
    provides: "shared/types.ts (Run, RunSummary, ParsedLogEvent, IpcMessage), shared/constants.ts (RESULT_FORCE_KILL_DELAY_MS, KEEP_RUNS_COUNT), worker/index.ts skeleton, shared/logger.ts"

provides:
  - "worker/executor.ts: executeRun (force-kill, timeout, PID tracking, artifact write), cleanupOldRuns, activePids, killAllActive"
  - "worker/policy.ts: buildSafehouseFlags with tilde-expansion safety assertion, PolicyTarget interface"
  - "worker/log-parser.ts: parseStreamJsonLine handles stream-json and non-JSON lines"
  - "18 tests passing: log-parser, policy, artifact-cleanup, executor"

affects:
  - 01-03
  - 02-core-cockpit
  - phase-2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Force-kill pattern: setTimeout SIGKILL after RESULT_FORCE_KILL_DELAY_MS on result event (GitHub #25629 workaround)"
    - "In-memory PID set (activePids): never files; worker holds direct process handles from Bun.spawn"
    - "Tilde safety assertion: buildSafehouseFlags throws on any ~ path — safehouse does not shell-expand tildes"
    - "TDD: RED (tests fail with missing module) -> GREEN (implementation passes) per each module"

key-files:
  created:
    - app/worker/executor.ts
    - app/worker/policy.ts
    - app/worker/log-parser.ts
    - app/tests/worker/executor.test.ts
    - app/tests/worker/log-parser.test.ts
    - app/tests/worker/policy.test.ts
    - app/tests/worker/artifact-cleanup.test.ts
  modified:
    - app/worker/index.ts

key-decisions:
  - "PolicyTarget is a minimal interface (name + resolved_path + optional extra_plugin_dirs) — full Target type deferred to Phase 2"
  - "maxRuntimeMs hardcoded to 30*60_000 in worker/index.ts enqueue handler — Phase 2 loads from safety.yaml dynamically"
  - "executor.ts is the single file containing all executor exports (executeRun, cleanupOldRuns, activePids, killAllActive)"

patterns-established:
  - "Force-kill after result event: always use RESULT_FORCE_KILL_DELAY_MS constant, never hardcode 10_000"
  - "Tilde paths: always use path.join(homeDir, '...') — never string concatenation with ~"
  - "PID lifecycle: activePids.add on spawn, activePids.delete in finally block, killAllActive on shutdown"

requirements-completed: [FOUND-05, FOUND-06, FOUND-08]

# Metrics
duration: 2min
completed: 2026-03-18
---

# Phase 1 Plan 02: Worker Executor Summary

**Bun subprocess executor with force-kill (GitHub #25629 workaround), SIGKILL timeout, in-memory PID tracking, safehouse flag builder with tilde-safety assertion, and rolling 50-run cleanup**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-17T18:34:50Z
- **Completed:** 2026-03-17T18:37:28Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- `worker/log-parser.ts`: parseStreamJsonLine handles result/assistant/text events with graceful JSON fallback
- `worker/policy.ts`: buildSafehouseFlags generates tilde-free safehouse CLI flags with runtime assertion
- `worker/executor.ts`: executeRun with force-kill setTimeout (GitHub #25629), SIGKILL timeout from maxRuntimeMs, in-memory activePids tracking, log.jsonl + summary.yaml write, rolling cleanup to 50 runs
- `worker/index.ts`: wired with killAllActive on shutdown + executeRun on enqueue

## executeRun Signature

```typescript
export async function executeRun(
  run: Run,
  target: PolicyTarget,
  opts: {
    runsDir: string
    safehousePath?: string
    maxRuntimeMs: number  // safety.yaml max_runtime_minutes * 60_000
    onMessage: (msg: IpcMessage) => void
  }
): Promise<void>
```

## PolicyTarget Interface

```typescript
export interface PolicyTarget {
  name: string
  resolved_path: string
  extra_plugin_dirs?: string[]
}
```

## Task Commits

Each task was committed atomically:

1. **Task 1: Log parser, safehouse policy, and artifact cleanup** - `e29b9f7` (feat)
2. **Task 2: Wire executeRun into worker + executor tests** - `da1d3c8` (feat)

## Files Created/Modified

- `app/worker/log-parser.ts` - parseStreamJsonLine (stream-json + non-JSON fallback)
- `app/worker/policy.ts` - buildSafehouseFlags, PolicyTarget interface, tilde-safety assertion
- `app/worker/executor.ts` - executeRun, cleanupOldRuns, activePids, killAllActive
- `app/worker/index.ts` - updated: killAllActive on shutdown, executeRun on enqueue
- `app/tests/worker/log-parser.test.ts` - 4 tests
- `app/tests/worker/policy.test.ts` - 4 tests
- `app/tests/worker/artifact-cleanup.test.ts` - 3 tests (51 runs keeps 50, oldest deleted first, 30 unchanged)
- `app/tests/worker/executor.test.ts` - 7 tests (exports, activePids, killAllActive)

## Decisions Made

- PolicyTarget is minimal (name + resolved_path + optional extra_plugin_dirs) — full Target type deferred to Phase 2 when YAML config is loaded
- maxRuntimeMs hardcoded as `30 * 60_000` in worker/index.ts enqueue handler; Phase 2 will load `max_runtime_minutes` dynamically from safety.yaml
- executor.ts is a single export file (not split) — all four exports (executeRun, cleanupOldRuns, activePids, killAllActive) live together for clarity

## Deviations from Plan

None — plan executed exactly as written.

The plan specified writing `cleanupOldRuns` in Task 1 as part of executor.ts, then adding `executeRun` in Task 2. Since executor.ts was new in Task 1, both the cleanup portion and full executeRun were written together in a single file and committed atomically per task. The TDD RED/GREEN cycle was honored: tests were written before implementation in each task.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 01-03 (orphan cleanup + graceful shutdown) can build on killAllActive and the process lifecycle patterns established here
- executeRun signature is stable — plan 01-03 should reference PolicyTarget from worker/policy.ts
- The hardcoded `30 * 60_000` in worker/index.ts is a known placeholder — Phase 2 yaml-store integration will replace it

---
*Phase: 01-foundation*
*Completed: 2026-03-18*
