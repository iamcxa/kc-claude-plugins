import { describe, it, expect, beforeEach, afterEach } from 'bun:test'
import { mkdtemp, rm, stat, readFile, writeFile, mkdir } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  runGit,
  ensureWorktreesExcluded,
  detectDefaultBranch,
  createWorktree,
  detectWorktreeBranch,
  cleanupWorktree,
} from '../../worker/worktree-manager.ts'

// ============================================================
// Shared helper: create a minimal git repo in a tmp directory
// ============================================================
interface TmpRepo {
  repoPath: string
  cleanup: () => Promise<void>
}

async function createTmpRepo(): Promise<TmpRepo> {
  const repoPath = await mkdtemp(join(tmpdir(), 'nw-wt-'))
  // Init, configure identity, commit
  await runGit(repoPath, ['init'])
  await runGit(repoPath, ['config', 'user.email', 'test@test.com'])
  await runGit(repoPath, ['config', 'user.name', 'Test User'])
  await runGit(repoPath, ['commit', '--allow-empty', '-m', 'init'])
  // Rename default branch to 'main'
  await runGit(repoPath, ['branch', '-M', 'main'])
  return {
    repoPath,
    cleanup: () => rm(repoPath, { recursive: true, force: true }),
  }
}

// ============================================================
// runGit helper
// ============================================================
describe('runGit', () => {
  it('returns { exitCode, stdout, stderr } shape for successful command', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      const result = await runGit(repoPath, ['status'])
      expect(typeof result.exitCode).toBe('number')
      expect(typeof result.stdout).toBe('string')
      expect(typeof result.stderr).toBe('string')
      expect(result.exitCode).toBe(0)
    } finally {
      await cleanup()
    }
  })

  it('returns non-zero exitCode for failed git command', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      const result = await runGit(repoPath, ['rev-parse', '--verify', 'nonexistent-ref-xyz'])
      expect(result.exitCode).not.toBe(0)
    } finally {
      await cleanup()
    }
  })
})

// ============================================================
// ensureWorktreesExcluded
// ============================================================
describe('ensureWorktreesExcluded', () => {
  it('appends .worktrees to .git/info/exclude', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      await ensureWorktreesExcluded(repoPath)
      const excludePath = join(repoPath, '.git', 'info', 'exclude')
      const content = await readFile(excludePath, 'utf8')
      expect(content).toContain('.worktrees')
    } finally {
      await cleanup()
    }
  })

  it('is idempotent — calling twice does not duplicate the line', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      await ensureWorktreesExcluded(repoPath)
      await ensureWorktreesExcluded(repoPath)
      const excludePath = join(repoPath, '.git', 'info', 'exclude')
      const content = await readFile(excludePath, 'utf8')
      // Count occurrences of .worktrees
      const count = (content.match(/\.worktrees/g) ?? []).length
      expect(count).toBe(1)
    } finally {
      await cleanup()
    }
  })

  it('creates .git/info/exclude if it does not exist', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      // Remove the exclude file if it exists
      const excludePath = join(repoPath, '.git', 'info', 'exclude')
      try {
        await rm(excludePath)
      } catch { /* file may not exist */ }
      await ensureWorktreesExcluded(repoPath)
      const content = await readFile(excludePath, 'utf8')
      expect(content).toContain('.worktrees')
    } finally {
      await cleanup()
    }
  })
})

// ============================================================
// detectDefaultBranch
// ============================================================
describe('detectDefaultBranch', () => {
  it('returns configBranch when provided', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      const branch = await detectDefaultBranch(repoPath, 'develop')
      expect(branch).toBe('develop')
    } finally {
      await cleanup()
    }
  })

  it('detects branch from git symbolic-ref refs/remotes/origin/HEAD', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      // Set up a self-referencing remote with symbolic HEAD pointing to main
      await runGit(repoPath, ['remote', 'add', 'origin', repoPath])
      await runGit(repoPath, ['fetch', 'origin'])
      await runGit(repoPath, ['remote', 'set-head', 'origin', 'main'])
      const branch = await detectDefaultBranch(repoPath)
      expect(branch).toBe('main')
    } finally {
      await cleanup()
    }
  })

  it('falls back to "main" when origin/main exists but symbolic-ref is unset', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      // Add origin and fetch (creates origin/main) but don't set symbolic-ref
      await runGit(repoPath, ['remote', 'add', 'origin', repoPath])
      await runGit(repoPath, ['fetch', 'origin'])
      // Don't set remote HEAD — symbolic-ref will fail
      const branch = await detectDefaultBranch(repoPath)
      expect(branch).toBe('main')
    } finally {
      await cleanup()
    }
  })

  it('falls back to "master" when origin/master exists but not origin/main', async () => {
    // Create repo with master as the only branch
    const masterPath = await mkdtemp(join(tmpdir(), 'nw-wt-master-'))
    try {
      await runGit(masterPath, ['init'])
      await runGit(masterPath, ['config', 'user.email', 'test@test.com'])
      await runGit(masterPath, ['config', 'user.name', 'Test User'])
      await runGit(masterPath, ['commit', '--allow-empty', '-m', 'init'])
      // Branch is "master" by default on older git configs; ensure it's named master
      // Rename to master explicitly
      await runGit(masterPath, ['branch', '-M', 'master'])

      // Create the test repo that has origin/master
      const { repoPath, cleanup } = await createTmpRepo()
      try {
        // The test repo currently has 'main'. We need to create origin/master but NOT origin/main.
        // Use the masterPath repo as origin
        await runGit(repoPath, ['remote', 'add', 'origin', masterPath])
        await runGit(repoPath, ['fetch', 'origin'])
        // Now we have origin/master. Remove origin/main if it exists
        // (it won't since masterPath only has master)
        const branch = await detectDefaultBranch(repoPath)
        expect(branch).toBe('master')
      } finally {
        await cleanup()
      }
    } finally {
      await rm(masterPath, { recursive: true, force: true })
    }
  })

  it('throws Error with "Cannot detect default branch" when all fallbacks fail', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      // No remote configured → all fallbacks fail
      let threw = false
      try {
        await detectDefaultBranch(repoPath)
      } catch (err) {
        threw = true
        expect(err).toBeInstanceOf(Error)
        expect((err as Error).message).toContain('Cannot detect default branch')
      }
      expect(threw).toBe(true)
    } finally {
      await cleanup()
    }
  })
})

// ============================================================
// createWorktree + ensureWorktreesExcluded integration
// ============================================================
describe('createWorktree', () => {
  it('creates directory at worktreePath', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      // Set up self-referencing remote for origin/main
      await runGit(repoPath, ['remote', 'add', 'origin', repoPath])
      await runGit(repoPath, ['fetch', 'origin'])
      const worktreePath = join(repoPath, '.worktrees', 'nw-test-create')
      await createWorktree(repoPath, worktreePath, 'main')
      const s = await stat(worktreePath)
      expect(s.isDirectory()).toBe(true)
      // Cleanup
      await runGit(repoPath, ['worktree', 'remove', '--force', worktreePath])
    } finally {
      await cleanup()
    }
  })

  it('uses --detach (per D-14) — worktree list --porcelain shows "detached" line', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      await runGit(repoPath, ['remote', 'add', 'origin', repoPath])
      await runGit(repoPath, ['fetch', 'origin'])
      const worktreePath = join(repoPath, '.worktrees', 'nw-test-detach')
      await createWorktree(repoPath, worktreePath, 'main')
      const listResult = await runGit(repoPath, ['worktree', 'list', '--porcelain'])
      expect(listResult.stdout).toContain('detached')
      // Cleanup
      await runGit(repoPath, ['worktree', 'remove', '--force', worktreePath])
    } finally {
      await cleanup()
    }
  })

  it('calls prune + retry on first failure — succeeds when stale entry is present', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      await runGit(repoPath, ['remote', 'add', 'origin', repoPath])
      await runGit(repoPath, ['fetch', 'origin'])
      const worktreePath = join(repoPath, '.worktrees', 'nw-stale-test')
      // Create a worktree, then manually remove its directory to create a stale entry
      await createWorktree(repoPath, worktreePath, 'main')
      // Delete the directory without git worktree remove (creates stale entry)
      await rm(worktreePath, { recursive: true, force: true })
      // Now createWorktree should fail on first attempt (stale entry),
      // prune, then succeed on retry
      await expect(createWorktree(repoPath, worktreePath, 'main')).resolves.toBeUndefined()
      const s = await stat(worktreePath)
      expect(s.isDirectory()).toBe(true)
      await runGit(repoPath, ['worktree', 'remove', '--force', worktreePath])
    } finally {
      await cleanup()
    }
  })

  it('throws Error with "worktree_creation_failed" on double failure', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      // Use a non-existent branch to force both attempts to fail
      let threw = false
      try {
        await createWorktree(repoPath, join(repoPath, '.worktrees', 'nw-fail-test'), 'nonexistent-branch-xyz')
      } catch (err) {
        threw = true
        expect(err).toBeInstanceOf(Error)
        expect((err as Error).message).toContain('worktree_creation_failed')
      }
      expect(threw).toBe(true)
    } finally {
      await cleanup()
    }
  })

  it('after createWorktree + ensureWorktreesExcluded, git status does NOT contain ".worktrees"', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      await runGit(repoPath, ['remote', 'add', 'origin', repoPath])
      await runGit(repoPath, ['fetch', 'origin'])
      const worktreePath = join(repoPath, '.worktrees', 'nw-test-status')
      // createWorktree calls ensureWorktreesExcluded internally
      await createWorktree(repoPath, worktreePath, 'main')
      const statusResult = await runGit(repoPath, ['status', '--short'])
      expect(statusResult.stdout).not.toContain('.worktrees')
      // Cleanup
      await runGit(repoPath, ['worktree', 'remove', '--force', worktreePath])
    } finally {
      await cleanup()
    }
  })
})

// ============================================================
// detectWorktreeBranch
// ============================================================
describe('detectWorktreeBranch', () => {
  it('returns null for detached HEAD worktree', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      await runGit(repoPath, ['remote', 'add', 'origin', repoPath])
      await runGit(repoPath, ['fetch', 'origin'])
      const worktreePath = join(repoPath, '.worktrees', 'nw-test-detached')
      await createWorktree(repoPath, worktreePath, 'main')
      const branch = await detectWorktreeBranch(repoPath, worktreePath)
      expect(branch).toBeNull()
      await runGit(repoPath, ['worktree', 'remove', '--force', worktreePath])
    } finally {
      await cleanup()
    }
  })

  it('returns branch name when worktree has been checked out to a branch', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      await runGit(repoPath, ['remote', 'add', 'origin', repoPath])
      await runGit(repoPath, ['fetch', 'origin'])
      const worktreePath = join(repoPath, '.worktrees', 'nw-test-branch')
      await createWorktree(repoPath, worktreePath, 'main')
      // Checkout a new branch inside the worktree
      await runGit(worktreePath, ['checkout', '-b', 'test-branch'])
      const branch = await detectWorktreeBranch(repoPath, worktreePath)
      expect(branch).toBe('test-branch')
      await runGit(repoPath, ['worktree', 'remove', '--force', worktreePath])
    } finally {
      await cleanup()
    }
  })
})

// ============================================================
// cleanupWorktree
// ============================================================
describe('cleanupWorktree', () => {
  it('removes the worktree directory (stat throws ENOENT after cleanup)', async () => {
    const { repoPath, cleanup } = await createTmpRepo()
    try {
      await runGit(repoPath, ['remote', 'add', 'origin', repoPath])
      await runGit(repoPath, ['fetch', 'origin'])
      const worktreePath = join(repoPath, '.worktrees', 'nw-test-cleanup')
      await createWorktree(repoPath, worktreePath, 'main')
      // Verify it exists
      await stat(worktreePath)
      // Cleanup
      await cleanupWorktree(repoPath, worktreePath)
      // Should be gone
      let threw = false
      try {
        await stat(worktreePath)
      } catch (err) {
        threw = true
        expect((err as NodeJS.ErrnoException).code).toBe('ENOENT')
      }
      expect(threw).toBe(true)
    } finally {
      await cleanup()
    }
  })

  it('with branch pushes to origin before removing (verify branch exists in origin after cleanup)', async () => {
    // Create a bare remote repo
    const remotePath = await mkdtemp(join(tmpdir(), 'nw-wt-remote-'))
    try {
      await runGit(remotePath, ['init', '--bare'])
      // Create a local repo with initial commit
      const { repoPath, cleanup } = await createTmpRepo()
      try {
        // Configure the bare repo as origin
        await runGit(repoPath, ['remote', 'add', 'origin', remotePath])
        // Push main to remote so origin/main exists for worktree creation
        await runGit(repoPath, ['push', 'origin', 'main'])
        await runGit(repoPath, ['fetch', 'origin'])
        const worktreePath = join(repoPath, '.worktrees', 'nw-test-push')
        await createWorktree(repoPath, worktreePath, 'main')
        // Create a branch in the worktree
        await runGit(worktreePath, ['checkout', '-b', 'kc-nightwatch/test-proposal'])
        // Verify cleanupWorktree pushes and then removes
        await cleanupWorktree(repoPath, worktreePath)
        // Verify worktree is gone
        let threw = false
        try {
          await stat(worktreePath)
        } catch {
          threw = true
        }
        expect(threw).toBe(true)
        // Verify branch was pushed to remote
        const branchResult = await runGit(remotePath, ['branch'])
        expect(branchResult.stdout).toContain('kc-nightwatch/test-proposal')
      } finally {
        await cleanup()
      }
    } finally {
      await rm(remotePath, { recursive: true, force: true })
    }
  })
})
