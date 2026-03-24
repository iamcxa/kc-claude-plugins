---
phase: 13-worktree-isolation
plan: 02
subsystem: infra
tags: [git-worktree, executor, typescript, integration, isolation]

# Dependency graph
requires:
  - phase: 13-worktree-isolation
    plan: 01
    provides: worktree-manager.ts with 6 exported functions (createWorktree, cleanupWorktree, detectDefaultBranch, etc.)
provides:
  - executor.ts with worktree lifecycle integrated — cwd switched to worktreePath
  - PolicyTarget.default_branch optional field (WKTREE-01)
  - resolveTarget passes default_branch from Target config (WKTREE-01)
  - Worktree create-before-spawn + cleanup-in-finally lifecycle (D-11, D-12)
  - run:failed on worktree creation failure with no in-place fallback (D-10)
  - 4 new executor integration tests verifying wiring
affects: [executor.ts, policy.ts, index.ts, executor.test.ts]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Worktree lifecycle in executeRun: create → spawn(cwd=worktreePath) → finally { cleanup LAST }"
    - "worktreeCreated boolean guard prevents spurious cleanup attempts on creation failure"
    - "Structural source tests via Bun.file().text() for verifying cwd and cleanup patterns"

key-files:
  created: []
  modified:
    - app/worker/executor.ts
    - app/worker/policy.ts
    - app/worker/index.ts
    - app/tests/worker/executor.test.ts

key-decisions:
  - "Worktree cleanup placed AFTER cleanupOldRuns (last in finally block) — per D-12: feedback + outcome recording runs first, worktree removal is final step"
  - "worktreeCreated boolean guard: only attempt cleanup if creation succeeded — prevents confusing error logs when run fails at creation stage"
  - "Structural source tests (Bun.file read executor.ts) for cwd/cleanup verification — lightweight, no process spawning required"

requirements-completed: [WKTREE-01, WKTREE-02, WKTREE-03]

# Metrics
duration: 3min
completed: 2026-03-24
---

# Phase 13 Plan 02: Executor Worktree Integration Summary

**Worktree lifecycle wired into executeRun — cwd switched from target.resolved_path to worktreePath, with create-before-spawn and cleanup-in-finally ordering**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-03-24T09:43:05Z
- **Completed:** 2026-03-24T09:45:43Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Modified `executor.ts` to import and use worktree-manager functions (detectDefaultBranch, createWorktree, cleanupWorktree)
- Changed `Bun.spawn` cwd from `target.resolved_path` to `worktreePath` (`.worktrees/nw-{run_id}`)
- Worktree creation fails fast with `run:failed` — no silent fallback to in-place execution (D-10)
- Cleanup placed as last operation in finally block, after feedback collection + outcome recording (D-12)
- Added `default_branch?` to PolicyTarget interface and plumbed through resolveTarget
- 4 new executor integration tests; full suite 322 pass, 0 fail

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire worktree lifecycle into executeRun** - `28efc29` (feat)
2. **Task 2: Add executor integration tests for worktree wiring** - `56ab972` (test)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `app/worker/executor.ts` - Worktree lifecycle integrated: import, create before spawn, cleanup in finally
- `app/worker/policy.ts` - PolicyTarget.default_branch? optional field added
- `app/worker/index.ts` - resolveTarget passes target.default_branch through
- `app/tests/worker/executor.test.ts` - 4 new worktree integration tests (25 total, was 21)

## Decisions Made

- **Cleanup ordering**: Worktree cleanup is the very last operation in the finally block — after `cleanupOldRuns`. This ensures feedback collection (`collectImplicitFeedback`, `writeFeedbackTrends`) and outcome recording (`recordRunOutcomes`) have already run before the worktree is removed. Per D-12 and CONTEXT.md.

- **worktreeCreated boolean guard**: Boolean set to `true` only on successful creation. Cleanup is `if (worktreeCreated)` — prevents confusing cleanup error logs when the run failed at creation stage (worktreePath never existed).

- **Structural source tests**: Used `Bun.file(executor.ts).text()` to verify cwd pattern and cleanup presence without spawning processes. Lightweight, deterministic, and catches future accidental regressions.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None.

## Next Phase Readiness

- Phase 13 worktree isolation is complete (both plans done)
- All 3 requirements (WKTREE-01, WKTREE-02, WKTREE-03) satisfied
- Full test suite: 322 pass, 0 fail — no regression
- Ready for Phase 14 (next phase per ROADMAP)

---
*Phase: 13-worktree-isolation*
*Completed: 2026-03-24*
