---
phase: 13-worktree-isolation
verified: 2026-03-24T09:49:46Z
status: passed
score: 9/9 must-haves verified
re_verification: false
---

# Phase 13: Worktree Isolation Verification Report

**Phase Goal:** Every nightwatch run executes in a temporary git worktree, leaving the target's working directory untouched
**Verified:** 2026-03-24T09:49:46Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|---------|
| 1 | A run creates a new git worktree from target's latest main branch before execution | VERIFIED | `executor.ts` line 107-120: `createWorktree` called before `Bun.spawn`; path is `.worktrees/nw-{run.id}` |
| 2 | When run produces no branch, worktree is removed after run completes | VERIFIED | `executor.ts` line 314-324: `cleanupWorktree` in finally block; `cleanupWorktree` calls `detectWorktreeBranch` and removes regardless |
| 3 | When run creates a branch, that branch is pushed to origin before worktree removal | VERIFIED | `worktree-manager.ts` line 189-195: `detectWorktreeBranch` then `push origin {branch}` then `worktree remove --force` |
| 4 | After any run, target's main working directory git status is identical to before run | VERIFIED | `.worktrees` added to `.git/info/exclude` (D-03) + `--detach` prevents branch checkout conflicts + test "git status does NOT contain .worktrees" passes |

**Score:** 4/4 success criteria verified (from ROADMAP.md)

### Must-Haves from Plan 01 (worktree-manager)

| Truth | Status | Evidence |
|-------|--------|---------|
| detectDefaultBranch returns config branch when provided, falls back through symbolic-ref/main/master, throws on all-fail | VERIFIED | Implementation lines 77-98; 5 corresponding tests all pass |
| createWorktree creates worktree with --detach, prunes and retries once on failure | VERIFIED | Lines 122-131; prune+retry test and --detach test both pass |
| ensureWorktreesExcluded writes .worktrees to .git/info/exclude exactly once | VERIFIED | Lines 52-59; idempotent test confirms no duplicate |
| detectWorktreeBranch returns branch name from porcelain output or null when detached | VERIFIED | Lines 150-171 with realpath resolution; both branch/detached tests pass |
| cleanupWorktree pushes branch to origin before removing; removes without push when detached | VERIFIED | Lines 188-195; push test with bare remote confirms branch appears in origin |

### Must-Haves from Plan 02 (executor integration)

| Truth | Status | Evidence |
|-------|--------|---------|
| executeRun creates a worktree before spawning Claude and passes worktreePath as cwd | VERIFIED | `executor.ts` line 107-120 (create), line 156 `cwd: worktreePath` |
| executeRun cleans up the worktree in the finally block AFTER feedback collection and outcome recording | VERIFIED | Lines 314-324: cleanup is after `cleanupOldRuns`, which is after `collectImplicitFeedback` and `recordRunOutcomes` |
| When worktree creation fails, run status is 'failed' with error 'worktree_creation_failed: {msg}' | VERIFIED | Lines 115-119: `opts.onMessage({ type: 'run:failed', run_id: run.id, error: String(err) })` |
| The target's main working directory git status is unchanged after any run | VERIFIED | D-03 exclude + D-14 detach + test confirms git status clean |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `app/worker/worktree-manager.ts` | 6 exported async functions for git worktree lifecycle | VERIFIED | 6 `export async function` declarations: runGit, ensureWorktreesExcluded, detectDefaultBranch, createWorktree, detectWorktreeBranch, cleanupWorktree; 197 lines |
| `app/tests/worker/worktree-manager.test.ts` | Unit tests against real tmp git repos, min_lines 100 | VERIFIED | 402 lines, 19 tests (74 describe/it blocks counted), uses mkdtemp + real git repos |
| `app/shared/types.ts` | Target interface with `default_branch?: string` | VERIFIED | Line 21: `default_branch?: string    // WKTREE-01` |
| `app/worker/executor.ts` | Worktree-integrated executor with `cwd: worktreePath` | VERIFIED | Line 156: `cwd: worktreePath`; line 15: worktree-manager import |
| `app/tests/worker/executor.test.ts` | Extended executor tests covering worktree integration | VERIFIED | `worktree integration — WKTREE-01/02/03` describe block with 4 tests (lines 225-251) |
| `app/worker/policy.ts` | PolicyTarget with `default_branch?` field | VERIFIED | Line 9: `default_branch?: string` |
| `app/worker/index.ts` | resolveTarget passes default_branch through | VERIFIED | Line 59: `default_branch: target.default_branch` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `app/worker/executor.ts` | `app/worker/worktree-manager.ts` | `import { detectDefaultBranch, createWorktree, cleanupWorktree }` | WIRED | Line 15 confirmed |
| `app/worker/executor.ts` | `Bun.spawn(claudeArgs, { cwd: worktreePath })` | worktreePath replaces target.resolved_path | WIRED | Line 156 confirmed; `cwd: target.resolved_path` pattern is gone |
| `app/worker/worktree-manager.ts` | `Bun.spawn(['git', ...]` | `runGit` helper | WIRED | Line 28 confirmed |
| `app/tests/worker/worktree-manager.test.ts` | `app/worker/worktree-manager.ts` | direct import of all 6 functions | WIRED | Lines 6-12 confirmed |
| `app/worker/policy.ts` | `app/worker/index.ts` | `default_branch` field plumbed through `resolveTarget` | WIRED | index.ts line 59, policy.ts line 9 |

### Data-Flow Trace (Level 4)

Not applicable — worktree-manager.ts and executor.ts changes are infrastructure (git subprocess wrappers and lifecycle management), not data-rendering components. No dynamic UI data flow to trace.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| worktree-manager module exports 6 functions | `bun test tests/worker/worktree-manager.test.ts` | 19 pass, 0 fail | PASS |
| executor worktree integration tests pass | `bun test tests/worker/executor.test.ts` | 25 pass, 0 fail | PASS |
| Full test suite green (no regression) | `bun test` | 322 pass, 0 fail | PASS |
| Bun.spawn git pattern present in worktree-manager | grep for `Bun.spawn(['git'` | Line 28 found | PASS |
| cwd switched to worktreePath (not target.resolved_path) | grep for both patterns | `cwd: worktreePath` on line 156; `cwd: target.resolved_path` absent | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| WKTREE-01 | 13-01 + 13-02 | Executor creates temporary git worktree from target's latest main branch before each run | SATISFIED | `executor.ts` lines 107-120 — detectDefaultBranch + createWorktree before Bun.spawn; Target.default_branch + PolicyTarget.default_branch fields added |
| WKTREE-02 | 13-01 + 13-02 | Worktree cleanup after run — remove when no branch; keep if proposal/fix branch created | SATISFIED | `cleanupWorktree` detects branch via detectWorktreeBranch — if none, removes immediately; worktreeCreated guard in executor finally block |
| WKTREE-03 | 13-01 + 13-02 | Proposals/fixes create branches in worktree — branches pushed to origin, main working directory never modified | SATISFIED | `cleanupWorktree` pushes branch before `worktree remove --force`; push test confirms branch appears in bare remote after cleanup |

All 3 requirements SATISFIED. No orphaned requirements — WKTREE-01/02/03 are the only Phase 13 requirements in REQUIREMENTS.md and all three appear in both plan frontmatter fields.

### Anti-Patterns Found

No blockers or warnings. Scan of `app/worker/worktree-manager.ts` and modified files:

- No `return null` / `return {}` / `return []` stubs with empty data flows
- No TODO/FIXME/placeholder comments in any of the 5 modified files
- No hardcoded empty state that flows to rendering — all functions are git subprocess wrappers that either succeed or throw
- `cleanupWorktree` catch in executor.ts logs but does not swallow the result; this is intentional per D-13 ("if cleanup fails, log but don't fail the run") and documented in the code

### Human Verification Required

The following behaviors require a real target git repository to verify end-to-end:

#### 1. Full Run Isolation — Real Target

**Test:** Trigger a real nightwatch run against a target that has a git remote configured. Before the run, record `git status` and `git log -1` in the target repo. After the run completes, verify `git status` is unchanged and no new commits appear on the main branch.
**Expected:** Target working directory is byte-for-byte identical to pre-run state. Any changes made by Claude appear only in origin (pushed branch).
**Why human:** Requires a real Claude run with a real target repo + remote. Cannot execute without spawning a live nightwatch pipeline.

#### 2. Push-Before-Remove on Proposal Run

**Test:** Trigger a nightwatch run that produces a proposal branch. Verify the branch appears on the remote (e.g., `git ls-remote origin`) and the local target repo has no uncommitted changes or new branches.
**Expected:** Branch `kc-nightwatch/{date}-{target}-proposal` exists on remote origin. `git branch` in target repo is unchanged from before run.
**Why human:** Requires Claude to actually create a branch during a run — the unit tests verify the push mechanism but cannot simulate a live Claude session creating a proposal.

### Gaps Summary

No gaps. All must-haves verified, all key links wired, all 3 requirements satisfied, full test suite passes at 322/322.

---

_Verified: 2026-03-24T09:49:46Z_
_Verifier: Claude (gsd-verifier)_
