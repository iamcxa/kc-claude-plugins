---
phase: 13-worktree-isolation
plan: 01
subsystem: infra
tags: [git-worktree, bun, typescript, tdd, isolation]

# Dependency graph
requires:
  - phase: 12-test-infra-run-ux-fixes
    provides: executor.ts Bun.spawn pattern + test infrastructure (mkdtemp pattern)
provides:
  - worktree-manager.ts with 6 exported async functions for git worktree lifecycle
  - runGit helper wrapping Bun.spawn for all git subprocesses
  - ensureWorktreesExcluded — .git/info/exclude management (D-03)
  - detectDefaultBranch — 4-step fallback chain (D-06/D-07)
  - createWorktree — prune-retry on failure (D-08/D-09/D-14)
  - detectWorktreeBranch — porcelain parsing with realpath resolution
  - cleanupWorktree — push-before-remove ordering (D-12)
  - Target.default_branch optional field (D-05/WKTREE-01)
affects: [13-02-executor-integration, future-plans-using-worktree-manager]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bun.spawn(['git', ...args]) with piped stdout/stderr via new Response(proc.stdout).text()"
    - "realpath() symlink resolution before git porcelain path comparison (macOS /var/folders → /private/var/folders)"
    - "mkdtemp + git init + git commit --allow-empty pattern for real tmp git repo tests"
    - "Self-referencing remote (git remote add origin .) for unit-testing git operations without network"

key-files:
  created:
    - app/worker/worktree-manager.ts
    - app/tests/worker/worktree-manager.test.ts
  modified:
    - app/shared/types.ts

key-decisions:
  - "Use realpath() in detectWorktreeBranch to resolve macOS /var/folders symlink — git porcelain output uses resolved path"
  - "Self-referencing remote (origin = '.') enables unit-testing fetch/push without network"
  - "TDD RED→GREEN→REFACTOR completed in single task — 19 tests, all pass against real tmp repos"

patterns-established:
  - "Worktree path comparison: always realpath() before comparing against git porcelain output"
  - "Git subprocess in Bun: Bun.spawn + new Response(proc.stdout).text() + await proc.exited"

requirements-completed: [WKTREE-01, WKTREE-02, WKTREE-03]

# Metrics
duration: 4min
completed: 2026-03-24
---

# Phase 13 Plan 01: Worktree Manager Summary

**Bun.spawn-based git worktree lifecycle module with 6 exported async functions, tested against real tmp git repos with macOS symlink resolution**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-03-24T09:35:06Z
- **Completed:** 2026-03-24T09:39:00Z
- **Tasks:** 1
- **Files modified:** 3

## Accomplishments

- Created `worktree-manager.ts` with all 6 exported async functions implementing D-01 through D-14
- 19 unit tests against real temporary git repositories — no mocks, all behavior verified experimentally
- Added `default_branch?: string` to Target interface (D-05)
- Full test suite 318 pass, 0 fail — no regression from types.ts change

## Task Commits

Each task was committed atomically:

1. **Task 1: Add default_branch to Target type + create worktree-manager.ts** - `5c58e09` (feat)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `app/worker/worktree-manager.ts` - 6 exported async functions: runGit, ensureWorktreesExcluded, detectDefaultBranch, createWorktree, detectWorktreeBranch, cleanupWorktree
- `app/tests/worker/worktree-manager.test.ts` - 19 unit tests using real tmp git repos (mkdtemp + git init pattern)
- `app/shared/types.ts` - Added `default_branch?: string` field to Target interface

## Decisions Made

- **realpath() for symlink resolution**: macOS paths from `mkdtemp` start with `/var/folders/...` but git's `worktree list --porcelain` output uses the real path `/private/var/folders/...`. Fixed by calling `realpath()` on the worktreePath before comparing with porcelain output. Catch clause handles cases where the path doesn't exist yet.

- **Self-referencing remote for tests**: `git remote add origin .` (pointing to the repo itself) enables testing `fetch`, `push`, and `rev-parse origin/main` without network. Lightweight, no external dependencies.

- **Bare repo for push test**: For the `cleanupWorktree` push test, used `git init --bare` remote repo — standard approach for testing git push without SSH/network.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] realpath() symlink resolution in detectWorktreeBranch**
- **Found during:** Task 1 (GREEN phase — tests failing after implementation)
- **Issue:** `detectWorktreeBranch` returned null instead of branch name. `mkdtemp()` returns `/var/folders/...` but `git worktree list --porcelain` outputs the real path `/private/var/folders/...`. Comparison failed.
- **Fix:** Added `import { realpath } from 'node:fs/promises'` and `const resolvedWorktreePath = await realpath(worktreePath).catch(() => worktreePath)` before comparing with porcelain lines. The `catch` handles the edge case where the path doesn't exist yet.
- **Files modified:** `app/worker/worktree-manager.ts`
- **Verification:** Both `detectWorktreeBranch` tests pass; push test also now passes
- **Committed in:** `5c58e09` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug)
**Impact on plan:** Essential correctness fix for macOS. The realpath issue is a well-known macOS symlink behavior — Linux systems won't hit this but the fix is portable and harmless.

## Issues Encountered

- macOS `/tmp` → `/private/tmp` and `/var/folders` → `/private/var/folders` symlink chains in `mkdtemp` output caused porcelain path comparison failures. Resolved by calling `realpath()` in `detectWorktreeBranch`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `worktree-manager.ts` ready for import by `executor.ts` in plan 13-02
- All 6 functions tested and verified against real git repos
- `Target.default_branch` field ready for use in executor integration
- Full test suite green — ready for plan 13-02 executor integration

---
*Phase: 13-worktree-isolation*
*Completed: 2026-03-24*
