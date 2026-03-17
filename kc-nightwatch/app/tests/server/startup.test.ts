// FOUND-04: With Bun native IPC, no socket file is ever created.
// The FOUND-04 requirement ("Socket/PID file cleanup on startup — prevent EADDRINUSE")
// is satisfied structurally by the IPC choice. No .sock file exists anywhere in app/.
// The orphan scan covers the "clean crash recovery" intent — killing stale claude processes
// from a prior crash that did not clean up after itself.
import { describe, it, expect } from 'bun:test'
import { cleanupOrphans } from '../../server/index.ts'

describe('cleanupOrphans', () => {
  it('runs without throwing when no orphans exist', async () => {
    // pgrep returns exit code 1 with no output when no processes match
    await expect(cleanupOrphans()).resolves.toBeUndefined()
  })

  it('is a function that returns a Promise', () => {
    expect(typeof cleanupOrphans).toBe('function')
    const result = cleanupOrphans()
    expect(result instanceof Promise).toBe(true)
    return result  // let it run
  })
})
