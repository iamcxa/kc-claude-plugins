import { describe, it, expect, beforeEach, afterEach } from 'bun:test'
import { cleanupOldRuns } from '../../worker/executor.ts'
import { mkdtemp, rm, mkdir } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

let testDir: string

beforeEach(async () => {
  testDir = await mkdtemp(join(tmpdir(), 'nw-test-'))
})

afterEach(async () => {
  await rm(testDir, { recursive: true, force: true })
})

async function createRunDirs(dir: string, count: number): Promise<void> {
  for (let i = 0; i < count; i++) {
    await mkdir(join(dir, `run-${String(i).padStart(4, '0')}`))
    // Small delay to ensure distinct mtimes
    await Bun.sleep(2)
  }
}

describe('cleanupOldRuns', () => {
  it('keeps exactly 50 runs when 51 exist', async () => {
    await createRunDirs(testDir, 51)
    await cleanupOldRuns(testDir, 50)
    const remaining = await Array.fromAsync(new Bun.Glob('*').scan({ cwd: testDir, onlyFiles: false }))
    expect(remaining.length).toBe(50)
  })

  it('deletes oldest runs first', async () => {
    await createRunDirs(testDir, 51)
    await cleanupOldRuns(testDir, 50)
    const remaining = await Array.fromAsync(new Bun.Glob('*').scan({ cwd: testDir, onlyFiles: false }))
    // run-0000 should be deleted (oldest), run-0050 should remain (newest)
    expect(remaining).not.toContain('run-0000')
    expect(remaining).toContain('run-0050')
  })

  it('does not delete when count <= 50', async () => {
    await createRunDirs(testDir, 30)
    await cleanupOldRuns(testDir, 50)
    const remaining = await Array.fromAsync(new Bun.Glob('*').scan({ cwd: testDir, onlyFiles: false }))
    expect(remaining.length).toBe(30)
  })
})
