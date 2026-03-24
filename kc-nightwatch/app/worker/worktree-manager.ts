/**
 * worktree-manager.ts — Git worktree lifecycle management for nightwatch
 *
 * Encapsulates ALL git worktree operations so executor.ts only calls these
 * functions, never git worktree commands directly. Implements decisions
 * D-01 through D-14 from Phase 13 CONTEXT.md.
 *
 * All functions use Bun.spawn(['git', ...]) — consistent with executor.ts pattern.
 * No external dependencies.
 */

import path from 'node:path'
import fs from 'node:fs/promises'
import { realpath } from 'node:fs/promises'

// ============================================================
// runGit — Bun.spawn wrapper for git subprocesses
// ============================================================

/**
 * Run a git command in the given directory and return exitCode + captured output.
 * Consistent with existing Bun.spawn usage in executor.ts.
 */
export async function runGit(
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
  const exitCode = await proc.exited
  return { exitCode, stdout, stderr }
}

// ============================================================
// ensureWorktreesExcluded — D-03
// ============================================================

/**
 * Write `.worktrees` to `.git/info/exclude` so the directory is invisible
 * to `git status`. Must be called BEFORE the first `git worktree add`.
 *
 * Idempotent: if `.worktrees` is already present, does nothing.
 * Creates the exclude file if it does not exist (some git configurations).
 */
export async function ensureWorktreesExcluded(repoPath: string): Promise<void> {
  const excludePath = path.join(repoPath, '.git', 'info', 'exclude')
  const current = await fs.readFile(excludePath, 'utf8').catch(() => '')
  if (!current.includes('.worktrees')) {
    // Ensure the .git/info directory exists (it may not on some minimal git inits)
    await fs.mkdir(path.join(repoPath, '.git', 'info'), { recursive: true })
    await fs.appendFile(excludePath, '\n.worktrees\n')
  }
}

// ============================================================
// detectDefaultBranch — D-06/D-07
// ============================================================

/**
 * Detect the default branch for a git repository.
 *
 * Fallback chain (D-06, all local — no network):
 * 1. Return configBranch if truthy (D-05 explicit override)
 * 2. git symbolic-ref refs/remotes/origin/HEAD — extract branch name
 * 3. git rev-parse --verify origin/main — return 'main' if exits 0
 * 4. git rev-parse --verify origin/master — return 'master' if exits 0
 * 5. throw Error with clear message (D-07 — don't guess, don't skip)
 */
export async function detectDefaultBranch(repoPath: string, configBranch?: string): Promise<string> {
  // Chain step 1: config override (D-05)
  if (configBranch) return configBranch

  // Chain step 2: symbolic-ref (set by `git remote set-head origin -a` or `git clone`)
  const symref = await runGit(repoPath, ['symbolic-ref', 'refs/remotes/origin/HEAD'])
  if (symref.exitCode === 0) {
    // Output is "refs/remotes/origin/main\n" — extract branch name
    return symref.stdout.trim().replace('refs/remotes/origin/', '')
  }

  // Chain step 3: try origin/main
  const mainCheck = await runGit(repoPath, ['rev-parse', '--verify', 'origin/main'])
  if (mainCheck.exitCode === 0) return 'main'

  // Chain step 4: try origin/master
  const masterCheck = await runGit(repoPath, ['rev-parse', '--verify', 'origin/master'])
  if (masterCheck.exitCode === 0) return 'master'

  // Chain step 5: D-07 — error with clear message, no guessing
  throw new Error(
    `Cannot detect default branch for ${repoPath} — set target.default_branch in nightwatch-targets.yaml`
  )
}

// ============================================================
// createWorktree — D-08/D-09/D-14
// ============================================================

/**
 * Create a git worktree at worktreePath checked out from origin/{branch}.
 *
 * Ordering (D-03): calls ensureWorktreesExcluded BEFORE git worktree add.
 * Isolation (D-14): uses --detach to avoid "branch already checked out" conflicts.
 * Retry (D-08/D-09): on first failure, prune stale entries and retry once.
 * Failure (D-09): throws with 'worktree_creation_failed' on double failure.
 * No fallback (D-10): never falls back to in-place execution.
 */
export async function createWorktree(
  repoPath: string,
  worktreePath: string,
  branch: string
): Promise<void> {
  // D-03: ensure .worktrees excluded from git status FIRST
  await ensureWorktreesExcluded(repoPath)

  // D-14: --detach avoids "branch already checked out" conflicts
  const result = await runGit(repoPath, ['worktree', 'add', '--detach', worktreePath, `origin/${branch}`])
  if (result.exitCode === 0) return

  // D-08/D-09: prune stale entries and retry once
  await runGit(repoPath, ['worktree', 'prune'])
  const retry = await runGit(repoPath, ['worktree', 'add', '--detach', worktreePath, `origin/${branch}`])
  if (retry.exitCode !== 0) {
    throw new Error(`worktree_creation_failed: ${retry.stderr.trim()}`)
  }
}

// ============================================================
// detectWorktreeBranch — D-12
// ============================================================

/**
 * Check if a worktree has a named branch (vs detached HEAD).
 *
 * Returns the branch name if one exists, null if detached.
 * Uses `git worktree list --porcelain` — reliable even in linked worktrees
 * where `.git` is a file, not a directory.
 *
 * Porcelain format per entry (entries separated by blank lines):
 *   worktree /absolute/path
 *   HEAD <sha>
 *   branch refs/heads/my-branch   (or "detached")
 */
export async function detectWorktreeBranch(
  repoPath: string,
  worktreePath: string
): Promise<string | null> {
  const result = await runGit(repoPath, ['worktree', 'list', '--porcelain'])
  if (result.exitCode !== 0) return null

  // Resolve symlinks — on macOS, /var/folders resolves to /private/var/folders
  // git porcelain output uses the resolved real path, so we must match it
  const resolvedWorktreePath = await realpath(worktreePath).catch(() => worktreePath)

  const blocks = result.stdout.trim().split('\n\n')
  for (const block of blocks) {
    const lines = block.trim().split('\n')
    if (lines[0] === `worktree ${resolvedWorktreePath}`) {
      const branchLine = lines.find(l => l.startsWith('branch '))
      if (branchLine) {
        return branchLine.replace('branch refs/heads/', '')
      }
    }
  }
  return null  // detached or worktree not found
}

// ============================================================
// cleanupWorktree — D-12
// ============================================================

/**
 * Clean up a worktree: push branch to origin if one exists, then remove.
 *
 * Ordering (D-12): push FIRST, then remove — never remove before push.
 * Force (Research pitfall #2): always use --force because Claude's run
 * leaves untracked files in the worktree.
 *
 * @param repoPath - absolute path to the git repo root
 * @param worktreePath - absolute path to the worktree to clean up
 */
export async function cleanupWorktree(repoPath: string, worktreePath: string): Promise<void> {
  const branch = await detectWorktreeBranch(repoPath, worktreePath)
  if (branch) {
    // Push branch to origin before removing (cwd is worktreePath for push)
    await runGit(worktreePath, ['push', 'origin', branch])
  }
  // --force required: Claude's run leaves untracked files (Research pitfall #2)
  await runGit(repoPath, ['worktree', 'remove', '--force', worktreePath])
}
