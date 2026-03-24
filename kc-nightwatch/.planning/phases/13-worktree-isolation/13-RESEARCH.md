# Phase 13: Worktree Isolation - Research

**Researched:** 2026-03-24
**Domain:** git worktree management, Bun.spawn git subprocess, executor.ts integration
**Confidence:** HIGH

## Summary

Phase 13 adds worktree isolation to the nightwatch executor: every run executes in a temporary `git worktree` checked out from the target's default branch, so the target's working directory is never modified by a nightwatch run. The implementation lives entirely in `executor.ts` plus a new `worktree-manager.ts` helper, with a small schema addition to `Target` for the optional `default_branch` field.

Git worktree is a built-in git feature (git 2.5+, verified 2.50.1 on this machine) that creates a linked working tree sharing the same `.git` object store. All commands (`add`, `remove`, `prune`, `list --porcelain`) were experimentally verified to work exactly as expected on this machine. No third-party library is needed — `Bun.spawn(['git', 'worktree', ...])` suffices.

The key correctness insight confirmed by live testing: adding `.worktrees` to `.git/info/exclude` before creating any worktree makes the directory completely invisible to `git status`. Without this step, `git status` shows `?? .worktrees/` — violating success criterion #4. This must happen before the first `git worktree add`, not after.

**Primary recommendation:** Implement `worktree-manager.ts` with four pure async functions (create/detectBranch/pushBranch/cleanup), wire into `executeRun` try/finally, and add `.worktrees` to `.git/info/exclude` as the very first worktree operation.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01:** Worktrees created at `{target}/.worktrees/nw-{run_id}/` — inside the target directory, generic `.worktrees/` path (composable, other tools can use same dir with different prefix)
**D-02:** `nw-` prefix namespaces nightwatch worktrees — prevents collision with other tools that may use `.worktrees/`
**D-03:** Add `.worktrees` to `{target}/.git/info/exclude` before first worktree creation — local-only gitignore, doesn't modify tracked files, ensures `git status` unchanged (success criteria #4)
**D-04:** Safehouse already covers target path — no new safehouse entries needed since `.worktrees/` is inside `target.resolved_path`
**D-05:** Optional `default_branch` field in target config (`nightwatch-targets.yaml`) — explicit override for repos using `develop`, `release`, etc.
**D-06:** Auto-detect fallback chain (all local, no network): `target.default_branch` → `git symbolic-ref refs/remotes/origin/HEAD` → try `origin/main` → try `origin/master` → error
**D-07:** If all detection fails, error out with clear message — don't guess, don't skip
**D-08:** Worktree creation failure: prune stale entries + retry once, then fail the run (no in-place fallback)
**D-09:** Flow: `git worktree add` → if fails → `git worktree prune` → retry `git worktree add` → if still fails → `run.status = 'failed'`, `run.error = 'worktree_creation_failed: {msg}'`
**D-10:** No fallback to in-place execution — Phase 13's purpose IS isolation, silent degradation would undermine the guarantee
**D-11:** Executor creates worktree before `Bun.spawn(claude)`, cleans up in `finally` block
**D-12:** Cleanup path: check if new branches exist in worktree → if yes, push to origin first → then `git worktree remove`
**D-13:** If process crashes (SIGKILL timeout), worktree survives — next run's `git worktree prune` in retry logic handles stale entries
**D-14:** `git worktree add` uses detached HEAD from `origin/{default_branch}` — avoids "branch already checked out" conflicts

### Claude's Discretion
- `worktree-manager.ts` internal structure (create/detect-branch/push/cleanup functions)
- How to pass worktree path through to `policy.ts` (extend `PolicyTarget` or add param to `executeRun`)
- `git worktree add --detach` vs `-b nw-{run_id}` (detached is simpler, skill creates its own branch anyway)
- Whether to `git fetch origin` before worktree creation to ensure latest (trade-off: network vs freshness)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| WKTREE-01 | Executor creates a temporary git worktree from target's latest main branch before each run — run executes in isolated worktree, not target's working directory | `git worktree add --detach <path> origin/<branch>` confirmed working; change `cwd: target.resolved_path` → `cwd: worktreePath` at executor.ts line 140 |
| WKTREE-02 | Worktree cleanup after run — remove worktree when run has no branch to preserve; keep worktree if proposal/fix branch was created | `git worktree list --porcelain` reliably distinguishes `detached` from `branch refs/heads/...`; `git worktree remove --force` handles untracked files |
| WKTREE-03 | Proposals and fixes create branches inside the worktree — branches are pushed to origin but worktree is cleaned up; main working directory is never modified by nightwatch | Verified experimentally: push from worktree leaves main worktree's `git status` clean (when `.git/info/exclude` is set) |
</phase_requirements>

## Standard Stack

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| git worktree | git 2.50.1 (built-in) | Isolated working tree per run | Native git feature, no deps, shared object store |
| Bun.spawn | Bun native | Run git subprocesses | Already used in executor.ts for cleanup; consistent pattern |
| node:fs/promises | Node built-in | Append to .git/info/exclude | Already imported in executor.ts |
| node:path | Node built-in | Construct worktree path | Already imported in executor.ts |

### No New Dependencies
This phase requires zero new npm packages. All git operations use `Bun.spawn(['git', ...])` exactly as `cleanupOldRuns` already uses `Bun.spawn(['rm', '-rf', ...])`.

**Version verification:** git 2.50.1 confirmed on this machine via `git --version`. `git worktree` was introduced in git 2.5 (2015) — no minimum version concern in practice.

## Architecture Patterns

### Recommended File Structure
```
app/worker/
├── executor.ts          # Existing — add worktree create/cleanup calls
├── policy.ts            # May need worktreeResolvedPath in PolicyTarget
├── worktree-manager.ts  # NEW — pure git worktree helpers
│
tests/worker/
├── executor.test.ts     # Existing — add worktree integration tests
├── worktree-manager.test.ts  # NEW — unit tests for all 4 helpers
```

### Pattern 1: worktree-manager.ts — Four Pure Functions

**What:** A module with four exported async functions wrapping git worktree subcommands via Bun.spawn.

**Functions:**
```typescript
// Source: verified by live git worktree add --detach testing (2026-03-24)

// 1. Detect default branch (local-only, no fetch)
async function detectDefaultBranch(repoPath: string, configBranch?: string): Promise<string>
// Chain: configBranch → git symbolic-ref refs/remotes/origin/HEAD → rev-parse origin/main → rev-parse origin/master → throw

// 2. Create worktree (with prune-and-retry on failure)
async function createWorktree(repoPath: string, worktreePath: string, branch: string): Promise<void>
// git worktree add --detach {worktreePath} origin/{branch}
// On fail: git worktree prune → retry → throw on second fail

// 3. Detect branch created in worktree (for cleanup decision)
async function detectWorktreeBranch(repoPath: string, worktreePath: string): Promise<string | null>
// git worktree list --porcelain → parse → return branch name or null if detached

// 4. Cleanup worktree (push branch first if exists, then remove)
async function cleanupWorktree(repoPath: string, worktreePath: string): Promise<void>
// detectWorktreeBranch → if branch: git push origin {branch} from worktreePath → git worktree remove --force {worktreePath}
```

**When to use:** All worktree operations go through this module. executor.ts only calls these functions, never git worktree commands directly.

### Pattern 2: .git/info/exclude Write (MUST be first operation)

```typescript
// Source: verified by live testing (2026-03-24) — without this, git status shows ?? .worktrees/
async function ensureWorktreesExcluded(repoPath: string): Promise<void> {
  const excludePath = path.join(repoPath, '.git', 'info', 'exclude')
  const current = await fs.readFile(excludePath, 'utf8').catch(() => '')
  if (!current.includes('.worktrees')) {
    await fs.appendFile(excludePath, '\n.worktrees\n')
  }
}
```

**Critical ordering:** Call `ensureWorktreesExcluded` BEFORE the first `git worktree add`. If called after, `git status` will already show the directory during the run.

### Pattern 3: executeRun Integration

```typescript
// Source: executor.ts analysis — fits naturally into existing try/finally
export async function executeRun(...): Promise<void> {
  // ... existing setup ...

  // WKTREE-01: Create isolated worktree
  const worktreePath = path.join(target.resolved_path, '.worktrees', `nw-${run.id}`)
  await ensureWorktreesExcluded(target.resolved_path)  // must be first
  const defaultBranch = await detectDefaultBranch(target.resolved_path, target.default_branch)
  await createWorktree(target.resolved_path, worktreePath, defaultBranch)

  const child = Bun.spawn(claudeArgs, {
    cwd: worktreePath,  // KEY CHANGE: was target.resolved_path
    ...
  })

  try {
    // ... existing stdout/stderr handling ...
  } finally {
    // ... existing cleanup (log write, summary, feedback, outcomes) ...

    // WKTREE-02/03: Cleanup worktree AFTER artifacts collected
    await cleanupWorktree(target.resolved_path, worktreePath)
  }
}
```

**Ordering in finally:** Worktree cleanup goes LAST in the finally block — after `collectImplicitFeedback`, `writeFeedbackTrends`, and `recordRunOutcomes` (which may need to inspect summary data written by Claude in the worktree). Run artifacts go to `runs/{id}/` (separate from worktree) so they survive worktree removal.

### Pattern 4: Branch Detection via Porcelain Parsing

```
# Porcelain format per worktree entry (blank line separates entries):
worktree /path/to/worktree
HEAD <sha>
detached               ← no branch created

worktree /path/to/worktree
HEAD <sha>
branch refs/heads/kc-nightwatch/proposal  ← branch exists
```

Parse: find the block where `worktree` line matches `worktreePath`, then check the third line for `detached` vs `branch refs/heads/`.

### Pattern 5: PolicyTarget Extension (Discretionary)

Two options — both work:

**Option A:** Add `worktree_path?: string` to `PolicyTarget` interface; `buildSafehouseFlags` adds `--add-dirs worktreePath` for non-dry-run. Advantage: safehouse explicitly knows about worktree. Disadvantage: worktree path is per-run, not per-target.

**Option B:** Pass `worktreePath` as an additional parameter to `buildSafehouseFlags`. Advantage: cleaner — PolicyTarget stays target-scoped. Disadvantage: signature change.

**Recommendation:** Option B — PolicyTarget is target-scoped metadata, worktree path is run-scoped. Per CONTEXT.md D-04, safehouse already covers the target path and `.worktrees/` is inside it, so this may be moot — the safehouse `--add-dirs target.resolved_path` flag already includes `.worktrees/` subdirectories.

### Anti-Patterns to Avoid

- **Passing `~` paths to git commands:** policy.ts already has tilde-expansion guard; apply same pattern in worktree-manager.ts — always use `path.join(os.homedir(), ...)` never template `~`
- **Running git commands from worktree path without `-C`:** git commands for worktree management (add/remove/prune/list) must run against the repo root, not the worktree path. `git -C repoPath worktree ...`. Exception: `git push` from within the worktree can use the worktree as cwd.
- **Silent degradation on worktree failure:** D-10 is explicit — no in-place fallback. Fail the run with `worktree_creation_failed` error.
- **Removing worktree before pushing branch:** If branch exists, push FIRST, then `worktree remove`. Removing first loses the commits.
- **Using `git worktree remove` without `--force`:** Claude's run will leave untracked files in the worktree (artifacts, etc.). Without `--force`, remove fails if modified/untracked files exist. Always use `--force` for programmatic cleanup.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Isolated working directory | Custom file copy/sync | `git worktree add --detach` | Copy misses .git history; worktree shares object store |
| Stale worktree cleanup | Track worktrees in a database | `git worktree prune` | Built-in git mechanism for orphaned entries |
| Branch detection | Parse `.git/HEAD` file directly | `git worktree list --porcelain` | HEAD file uses gitdir pointer in linked worktrees, not direct ref |
| Default branch | Hardcode "main" | Fallback detection chain (D-06) | Repos use develop/release/master variants |

**Key insight:** `.git` inside a linked worktree is a TEXT FILE containing `gitdir: /path/to/.git/worktrees/<name>`, not a directory. Parsing it directly gives the gitdir, not the branch. Always use `git worktree list --porcelain` for branch detection.

## Common Pitfalls

### Pitfall 1: git status Shows `?? .worktrees/` (Success Criteria #4 violation)
**What goes wrong:** After `git worktree add`, the `.worktrees/` directory appears as untracked in `git status` of the main worktree.
**Why it happens:** `.worktrees/` is created inside the tracked directory. Without exclusion, git reports it as untracked.
**How to avoid:** Write `.worktrees` to `.git/info/exclude` BEFORE the first `git worktree add`. Verified: this makes the directory completely invisible to `git status`.
**Warning signs:** After cleanup, `git -C target.resolved_path status --short` shows `?? .worktrees/`.

### Pitfall 2: `git worktree remove` Fails on Untracked Files
**What goes wrong:** `git worktree remove <path>` exits with 128 and "contains modified or untracked files".
**Why it happens:** Claude's run creates files in the worktree (artifacts, logs, temp files). Plain `remove` refuses to delete a dirty worktree.
**How to avoid:** Always use `git worktree remove --force <path>`. Confirmed in live testing.
**Warning signs:** Error message "use --force to delete it".

### Pitfall 3: git Worktree Commands Must Target Repo Root, Not Subdirectory
**What goes wrong:** `git -C worktreePath worktree list` reports the wrong repo root if worktreePath is a subdirectory of a larger repo.
**Why it happens:** `git -C path` resolves the git repo root for that path. In a monorepo, this is the parent repo root, not the target subdirectory.
**How to avoid:** Use `repoPath` (= `target.resolved_path` for targets that are their own git repos). For plugin-type targets living inside kc-claude-plugins, the "repo path" for git worktree commands is the parent git repo root (`git -C targetPath rev-parse --show-toplevel`).
**Warning signs:** `git worktree list` shows an unexpected root path.

### Pitfall 4: Worktree Directory Already Exists on Retry
**What goes wrong:** After a SIGKILL, the worktree directory survives. Next run tries to create the same worktree path (same `run_id` only if run_id is reused — but UUIDs prevent this). However, a previous run's stale entry in `.git/worktrees/` can still cause `git worktree add` to fail.
**Why it happens:** If the worktree dir is manually deleted without `git worktree remove`, the git metadata in `.git/worktrees/<name>` is orphaned (marked as "prunable").
**How to avoid:** D-08/D-09 retry flow: on first `git worktree add` failure, run `git worktree prune` then retry. `git worktree prune` removes orphaned entries. Confirmed in live testing.
**Warning signs:** `git worktree add` fails even though the directory doesn't exist.

### Pitfall 5: Cleanup Ordering — Branch Data Lost if Worktree Removed Before Push
**What goes wrong:** `cleanupWorktree` removes the worktree dir before pushing the branch to origin. Branch commits are lost.
**Why it happens:** `git worktree remove --force` deletes the directory AND the git worktree metadata, but commits on a local branch still exist in the object store until GC. However, if the branch was only in the worktree and not pushed, it's effectively inaccessible after the worktree is removed from the list.
**How to avoid:** detectBranch → push → then remove. Never remove before push. Also: `collectImplicitFeedback` and `recordRunOutcomes` run BEFORE worktree cleanup (they use run summary data, not the worktree directly).
**Warning signs:** Proposal branches disappear after runs complete.

### Pitfall 6: `git symbolic-ref refs/remotes/origin/HEAD` Fails on Fresh Clones
**What goes wrong:** On a repo where `git remote set-head origin -a` was never run, this command exits with 128 ("is not a symbolic ref").
**Why it happens:** `origin/HEAD` is not set by default in all clone configurations.
**How to avoid:** The detection chain D-06 handles this with fallbacks. Catch the non-zero exit and try `rev-parse --verify origin/main`, then `origin/master`, then error.
**Warning signs:** Run fails immediately with "worktree_creation_failed" on repos using default branch name.

## Code Examples

### Default Branch Detection
```typescript
// Source: verified against actual git behavior (2026-03-24)
async function detectDefaultBranch(repoPath: string, configBranch?: string): Promise<string> {
  // D-06 chain: config → symbolic-ref → try main → try master → error
  if (configBranch) return configBranch

  // Try symbolic-ref (set by git remote set-head -a or git clone)
  const symref = await runGit(repoPath, ['symbolic-ref', 'refs/remotes/origin/HEAD'])
  if (symref.exitCode === 0) {
    // Returns "refs/remotes/origin/main" — extract branch name
    return symref.stdout.trim().replace('refs/remotes/origin/', '')
  }

  // Try origin/main
  const mainCheck = await runGit(repoPath, ['rev-parse', '--verify', 'origin/main'])
  if (mainCheck.exitCode === 0) return 'main'

  // Try origin/master
  const masterCheck = await runGit(repoPath, ['rev-parse', '--verify', 'origin/master'])
  if (masterCheck.exitCode === 0) return 'master'

  // D-07: error out with clear message
  throw new Error(`Cannot detect default branch for ${repoPath} — set target.default_branch in nightwatch-targets.yaml`)
}
```

### Worktree Create with Prune-Retry
```typescript
// Source: D-08/D-09 from CONTEXT.md, validated by worktree prune live test
async function createWorktree(repoPath: string, worktreePath: string, branch: string): Promise<void> {
  // D-03: ensure .worktrees is excluded from git status FIRST
  await ensureWorktreesExcluded(repoPath)

  // D-14: --detach avoids "branch already checked out" conflict
  const result = await runGit(repoPath, ['worktree', 'add', '--detach', worktreePath, `origin/${branch}`])
  if (result.exitCode === 0) return

  // D-08/D-09: prune stale entries and retry once
  await runGit(repoPath, ['worktree', 'prune'])
  const retry = await runGit(repoPath, ['worktree', 'add', '--detach', worktreePath, `origin/${branch}`])
  if (retry.exitCode !== 0) {
    throw new Error(`worktree_creation_failed: ${retry.stderr.trim()}`)
  }
}
```

### Branch Detection via Porcelain
```typescript
// Source: validated by git worktree list --porcelain live test (2026-03-24)
// Porcelain entry for detached:  "worktree <path>\nHEAD <sha>\ndetached"
// Porcelain entry for branch:    "worktree <path>\nHEAD <sha>\nbranch refs/heads/<name>"
async function detectWorktreeBranch(repoPath: string, worktreePath: string): Promise<string | null> {
  const result = await runGit(repoPath, ['worktree', 'list', '--porcelain'])
  if (result.exitCode !== 0) return null

  const blocks = result.stdout.trim().split('\n\n')
  for (const block of blocks) {
    const lines = block.trim().split('\n')
    if (lines[0] === `worktree ${worktreePath}`) {
      const branchLine = lines.find(l => l.startsWith('branch '))
      if (branchLine) {
        return branchLine.replace('branch refs/heads/', '')
      }
    }
  }
  return null  // detached or not found
}
```

### Cleanup Worktree (Push Branch + Remove)
```typescript
// Source: D-12 from CONTEXT.md + live test confirming --force needed
async function cleanupWorktree(repoPath: string, worktreePath: string): Promise<void> {
  const branch = await detectWorktreeBranch(repoPath, worktreePath)
  if (branch) {
    // Push branch to origin before removing worktree
    await runGit(worktreePath, ['push', 'origin', branch])
  }
  // --force required: Claude's run leaves untracked files in worktree
  await runGit(repoPath, ['worktree', 'remove', '--force', worktreePath])
}
```

### Bun.spawn Helper for Git
```typescript
// Consistent with existing Bun.spawn usage in executor.ts
async function runGit(
  cwd: string,
  args: string[]
): Promise<{ exitCode: number; stdout: string; stderr: string }> {
  const proc = Bun.spawn(['git', ...args], {
    cwd,
    stdout: 'pipe',
    stderr: 'pipe',
  })
  const [stdout, stderr] = await Promise.all([
    new Response(proc.stdout).text(),
    new Response(proc.stderr).text(),
  ])
  return { exitCode: await proc.exited, stdout, stderr }
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Run in `target.resolved_path` directly | Run in temporary `git worktree` | Phase 13 (now) | Target working directory never modified by nightwatch |
| `cwd: target.resolved_path` in Bun.spawn | `cwd: worktreePath` in Bun.spawn | Phase 13 (now) | Single-line change at executor.ts:140 |

**No deprecated approaches** — this is net-new functionality.

## Open Questions

1. **Should worktree-manager.ts call `git fetch origin` before `git worktree add`?**
   - What we know: D-14 says "detached HEAD from `origin/{branch}`". If origin hasn't been fetched recently, the worktree may be stale (behind upstream).
   - What's unclear: The CONTEXT.md discretion section explicitly flags this as a trade-off (network vs freshness). No locked decision.
   - Recommendation: Skip `git fetch` for Phase 13 (avoid network dependency for a reliability phase). Log a warning if `origin/{branch}` is more than 24h behind HEAD via `git log --oneline origin/{branch}..HEAD` count — purely informational, no action.

2. **What if `target.resolved_path` is a subdirectory of a larger git repo (not itself a git root)?**
   - What we know: All git worktree commands run against the git repo root. `git -C targetPath rev-parse --show-toplevel` returns the actual root. If the target is a plugin living inside `kc-claude-plugins/`, worktrees are created at the `kc-claude-plugins/` level, not inside the plugin subdirectory.
   - What's unclear: Is this the intended behavior? The target plugin's files would be in the worktree but so would all other plugins.
   - Recommendation: For Phase 13, assert that `target.resolved_path` equals its git root (via `git rev-parse --show-toplevel`). If they differ, log a warning and fail the run with a clear message asking the user to configure a full git repo as the target path.

3. **How does `worktreePath` interact with safehouse `--add-dirs` when `policy.ts` uses `target.resolved_path`?**
   - What we know: D-04 says safehouse already covers target path (`.worktrees/` is inside it). Verified: `--add-dirs /path/to/target` includes all subdirectories recursively for safehouse.
   - What's unclear: Does safehouse also need the worktree path explicitly? Since `.worktrees/nw-{id}/` is a subdirectory of `target.resolved_path`, the existing `--add-dirs target.resolved_path` flag should cover it.
   - Recommendation: No `policy.ts` changes needed. If safehouse enforcement fails in testing, add explicit `--add-dirs worktreePath` as fallback.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| git | worktree commands | Yes | 2.50.1 (Apple Git-155) | — |
| git worktree subcommand | WKTREE-01/02/03 | Yes | Available since git 2.5 | — |
| Bun.spawn | git subprocess calls | Yes | Bun native | — |

All dependencies available. No missing dependencies.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Bun test (built-in) |
| Config file | None — `bun test` discovers `tests/**/*.test.ts` automatically |
| Quick run command | `bun test tests/worker/worktree-manager.test.ts` |
| Full suite command | `bun test` (from `app/` directory) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| WKTREE-01 | `createWorktree` creates worktree at correct path from origin/branch | unit | `bun test tests/worker/worktree-manager.test.ts` | Wave 0 |
| WKTREE-01 | `detectDefaultBranch` fallback chain | unit | `bun test tests/worker/worktree-manager.test.ts` | Wave 0 |
| WKTREE-01 | `ensureWorktreesExcluded` adds to .git/info/exclude | unit | `bun test tests/worker/worktree-manager.test.ts` | Wave 0 |
| WKTREE-01 | `executeRun` uses worktreePath as cwd | unit | `bun test tests/worker/executor.test.ts` | Exists (extend) |
| WKTREE-02 | `detectWorktreeBranch` returns null when detached | unit | `bun test tests/worker/worktree-manager.test.ts` | Wave 0 |
| WKTREE-02 | `cleanupWorktree` removes worktree when no branch | unit | `bun test tests/worker/worktree-manager.test.ts` | Wave 0 |
| WKTREE-03 | `cleanupWorktree` pushes branch before removing | unit | `bun test tests/worker/worktree-manager.test.ts` | Wave 0 |
| WKTREE-01+04 | `git status` clean after worktree add + .git/info/exclude | integration | `bun test tests/worker/worktree-manager.test.ts` | Wave 0 |

**Note on testing approach:** The git operations can be tested against real temporary git repos (as used in this research — `git init`, commit, test operations, cleanup). This is faster and more reliable than mocking git. Use `mkdtemp` + `git init` pattern from existing `executor.test.ts`.

### Sampling Rate
- **Per task commit:** `bun test tests/worker/worktree-manager.test.ts`
- **Per wave merge:** `bun test` (full suite from `app/`)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/worker/worktree-manager.test.ts` — covers WKTREE-01/02/03 (new file)
- [ ] Framework/config: None — `bun test` is already in use, no config needed

## Sources

### Primary (HIGH confidence)
- Live git worktree testing (2026-03-24): All command behaviors verified experimentally — `add --detach`, `remove --force`, `prune`, `list --porcelain`, `.git/info/exclude` effect on `git status`, branch detection via porcelain output, push from worktree, main worktree cleanliness.
- `app/worker/executor.ts` source read: Integration point at line 140 (`cwd: target.resolved_path`), try/finally structure, existing Bun.spawn pattern.
- `app/worker/policy.ts` source read: `buildSafehouseFlags` coverage of target path and subdirectories.
- `.planning/phases/13-worktree-isolation/13-CONTEXT.md`: All locked decisions (D-01 through D-14).

### Secondary (MEDIUM confidence)
- git 2.50.1 man page (`git worktree --help`): Confirmed `--detach` flag syntax and behavior.
- `app/shared/types.ts`: `Target` interface — `path?` field to be joined by `default_branch?` field.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — git worktree is built-in, Bun.spawn pattern established in codebase
- Architecture: HIGH — all patterns experimentally verified in live git testing
- Pitfalls: HIGH — discovered by actually running the commands and observing failure modes
- Test approach: HIGH — real tmp git repos pattern validated in executor.test.ts

**Research date:** 2026-03-24
**Valid until:** 2026-06-24 (git worktree API is stable, no expiry concern)
