# Phase 13: Worktree Isolation - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Every nightwatch run executes in a temporary git worktree created from the target's latest default branch, leaving the target's working directory untouched. The worktree is cleaned up after the run completes (or kept until branch is pushed for proposal/fix runs).

</domain>

<decisions>
## Implementation Decisions

### Worktree Storage Location
- **D-01:** Worktrees created at `{target}/.worktrees/nw-{run_id}/` — inside the target directory, generic `.worktrees/` path (composable, other tools can use same dir with different prefix)
- **D-02:** `nw-` prefix namespaces nightwatch worktrees — prevents collision with other tools that may use `.worktrees/`
- **D-03:** Add `.worktrees` to `{target}/.git/info/exclude` before first worktree creation — local-only gitignore, doesn't modify tracked files, ensures `git status` unchanged (success criteria #4)
- **D-04:** Safehouse already covers target path — no new safehouse entries needed since `.worktrees/` is inside `target.resolved_path`

### Default Branch Detection
- **D-05:** Optional `default_branch` field in target config (`nightwatch-targets.yaml`) — explicit override for repos using `develop`, `release`, etc.
- **D-06:** Auto-detect fallback chain (all local, no network): `target.default_branch` → `git symbolic-ref refs/remotes/origin/HEAD` → try `origin/main` → try `origin/master` → error
- **D-07:** If all detection fails, error out with clear message — don't guess, don't skip

### Error Handling
- **D-08:** Worktree creation failure: prune stale entries + retry once, then fail the run (no in-place fallback)
- **D-09:** Flow: `git worktree add` → if fails → `git worktree prune` → retry `git worktree add` → if still fails → `run.status = 'failed'`, `run.error = 'worktree_creation_failed: {msg}'`
- **D-10:** No fallback to in-place execution — Phase 13's purpose IS isolation, silent degradation would undermine the guarantee

### Worktree Lifecycle
- **D-11:** Executor creates worktree before `Bun.spawn(claude)`, cleans up in `finally` block
- **D-12:** Cleanup path: check if new branches exist in worktree → if yes, push to origin first → then `git worktree remove`
- **D-13:** If process crashes (SIGKILL timeout), worktree survives — next run's `git worktree prune` in retry logic handles stale entries
- **D-14:** `git worktree add` uses detached HEAD from `origin/{default_branch}` — avoids "branch already checked out" conflicts

### Claude's Discretion
- `worktree-manager.ts` internal structure (create/detect-branch/push/cleanup functions)
- How to pass worktree path through to `policy.ts` (extend `PolicyTarget` or add param to `executeRun`)
- `git worktree add --detach` vs `-b nw-{run_id}` (detached is simpler, skill creates its own branch anyway)
- Whether to `git fetch origin` before worktree creation to ensure latest (trade-off: network vs freshness)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core execution path (modify these)
- `app/worker/executor.ts` — `executeRun()` at line 84: `cwd: target.resolved_path` (line 140) is the key change point; worktree creation goes before `Bun.spawn`, cleanup goes in `finally` block
- `app/worker/policy.ts` — `buildSafehouseFlags()`: worktree path may need separate `--add-dirs` entry (though it's inside target.resolved_path already)
- `app/worker/index.ts` — `resolveTarget()` at line 38: provides `PolicyTarget` with `resolved_path`

### Target config
- `~/.claude/kc-plugins-config/nightwatch-targets.yaml` — Target config schema; `default_branch` field will be added here (optional)

### Patterns to follow
- Phase 9 CONTEXT.md D-12~D-14: defense-in-depth validation (both UI and API)
- Phase 10 CONTEXT.md D-01~D-04: run mode behavior (dry-run vs production vs self-repair)
- Phase 12 CONTEXT.md D-07~D-09: Bun-native approaches preferred

### Success criteria (from ROADMAP.md)
- `.planning/ROADMAP.md` §Phase 13 — 4 success criteria defining worktree behavior
- `.planning/REQUIREMENTS.md` — WKTREE-01, WKTREE-02, WKTREE-03

### Out of scope (from REQUIREMENTS.md)
- "Worktree per-target persistence: Worktrees are ephemeral per-run, not persistent per-target"

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Bun.spawn(['git', ...])` pattern: already used in `cleanupOldRuns` for `rm -rf`; extend for `git worktree add/remove/prune`
- `buildSafehouseFlags()` in `policy.ts`: already handles target path + runs dir permissions
- `activePids` tracking: ensures cleanup runs even on timeout (SIGKILL path)

### Established Patterns
- `executeRun()` follows try/finally for cleanup — worktree removal fits naturally in the `finally` block
- Run artifacts stored in `runs/{uuid}/` — worktree is separate from artifacts (in target's `.worktrees/`)
- `collectImplicitFeedback` and `recordRunOutcomes` run after execution in finally — worktree cleanup should run AFTER these (they may need to inspect the worktree for branch info)

### Integration Points
- `executor.ts` line 140: `cwd: target.resolved_path` → `cwd: worktreePath`
- `policy.ts`: worktree path for safehouse `--add-dirs` (may already be covered by target path)
- `worker/index.ts` `resolveTarget()`: does NOT need to change — worktree is created per-run in executor, not per-target in resolver
- Run mode affects worktree: dry-run = read-only intent but worktree itself must be writable for Claude to operate

</code_context>

<specifics>
## Specific Ideas

- `.worktrees/` is a composable generic path — user prefers this over `.nw-worktrees/` so other tools can share the pattern with different prefixes
- `.git/info/exclude` is the correct mechanism to hide `.worktrees/` from git status (local-only, no tracked file changes)
- Cleanup ordering matters: push branches → remove worktree → then continue to feedback collection

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 13-worktree-isolation*
*Context gathered: 2026-03-24*
