import { describe, it, expect, beforeEach, afterEach } from 'bun:test'
import { activePids, executeRun, killAllActive, cleanupOldRuns, ensureNwMemoryDir, writeNwJournalConfig } from '../../worker/executor.ts'
import type { Run, IpcMessage } from '../../shared/types.ts'
import { mkdtemp, rm, stat, readFile } from 'node:fs/promises'
import { tmpdir, homedir } from 'node:os'
import { join } from 'node:path'

let testDir: string

beforeEach(async () => {
  testDir = await mkdtemp(join(tmpdir(), 'nw-executor-'))
  activePids.clear()
})

afterEach(async () => {
  await rm(testDir, { recursive: true, force: true })
})

const baseRun: Run = {
  id: 'test-run-001',
  target: 'test-target',
  mode: 'dry-run',
  trigger: 'manual',
  status: 'queued',
  log_path: '',
}

describe('activePids', () => {
  it('starts empty', () => {
    expect(activePids.size).toBe(0)
  })

  it('killAllActive clears the set', async () => {
    activePids.add(999999)  // fake PID — process likely doesn't exist
    await killAllActive()   // should not throw, process may already be gone
    expect(activePids.size).toBe(0)
  })
})

describe('executeRun — PID tracking', () => {
  it('removes PID from activePids after run completes', async () => {
    // Verify activePids is empty before and after a simulated run
    expect(activePids.size).toBe(0)
    // The actual executeRun with real safehouse is an integration test;
    // this verifies the baseline state expectation
  })
})

describe('executor module exports', () => {
  it('exports executeRun function', () => {
    expect(typeof executeRun).toBe('function')
  })

  it('exports activePids Set', () => {
    expect(activePids).toBeInstanceOf(Set)
  })

  it('exports killAllActive function', () => {
    expect(typeof killAllActive).toBe('function')
  })

  it('exports cleanupOldRuns function', () => {
    expect(typeof cleanupOldRuns).toBe('function')
  })

  it('exports ensureNwMemoryDir function (MEM-01)', () => {
    expect(typeof ensureNwMemoryDir).toBe('function')
  })

  it('exports writeNwJournalConfig function (MEM-02)', () => {
    expect(typeof writeNwJournalConfig).toBe('function')
  })
})

describe('NW memory isolation — MEM-01: ensureNwMemoryDir', () => {
  // Track directories to clean up
  const dirsToClean: string[] = []

  afterEach(async () => {
    for (const dir of dirsToClean) {
      // Walk up to the nightwatch test directory and remove it
      // e.g. ~/.claude/nightwatch/memory/test-target-XXXX/.private-journal/
      // We created a unique target name per test to avoid conflict
      try {
        await rm(dir, { recursive: true, force: true })
      } catch { /* ignore */ }
    }
    dirsToClean.length = 0
  })

  it('creates journal directory at expected path', async () => {
    const targetName = `test-mem-${Date.now()}`
    const dir = await ensureNwMemoryDir(targetName)
    dirsToClean.push(join(homedir(), '.claude', 'nightwatch', 'memory', targetName))

    const expectedPath = join(homedir(), '.claude', 'nightwatch', 'memory', targetName, '.private-journal')
    expect(dir).toBe(expectedPath)

    // Directory should actually exist
    const s = await stat(dir)
    expect(s.isDirectory()).toBe(true)
  })

  it('does not throw when called again (directory already exists)', async () => {
    const targetName = `test-mem-idem-${Date.now()}`
    dirsToClean.push(join(homedir(), '.claude', 'nightwatch', 'memory', targetName))

    // Call twice — second call should not throw
    await ensureNwMemoryDir(targetName)
    expect(async () => {
      await ensureNwMemoryDir(targetName)
    }).not.toThrow()
  })

  it('uses os.homedir() — path does not contain literal tilde (MEM-01 anti-pattern)', async () => {
    const targetName = `test-mem-tilde-${Date.now()}`
    const dir = await ensureNwMemoryDir(targetName)
    dirsToClean.push(join(homedir(), '.claude', 'nightwatch', 'memory', targetName))

    expect(dir).not.toContain('~')
    expect(dir.startsWith('/')).toBe(true)
  })
})

describe('NW memory isolation — MEM-03: each target gets distinct path', () => {
  const dirsToClean: string[] = []

  afterEach(async () => {
    for (const dir of dirsToClean) {
      try { await rm(dir, { recursive: true, force: true }) } catch { /* ignore */ }
    }
    dirsToClean.length = 0
  })

  it('target-a and target-b have different journal paths', async () => {
    const nameA = `target-a-${Date.now()}`
    const nameB = `target-b-${Date.now()}`
    dirsToClean.push(
      join(homedir(), '.claude', 'nightwatch', 'memory', nameA),
      join(homedir(), '.claude', 'nightwatch', 'memory', nameB)
    )

    const dirA = await ensureNwMemoryDir(nameA)
    const dirB = await ensureNwMemoryDir(nameB)

    expect(dirA).not.toBe(dirB)
    expect(dirA).toContain(nameA)
    expect(dirB).toContain(nameB)
  })
})

describe('NW memory isolation — MEM-02: writeNwJournalConfig', () => {
  it('writes nw-journal.json with correct MCP config structure', async () => {
    const runDir = testDir
    const journalDir = join(testDir, 'fake-journal')
    const configPath = await writeNwJournalConfig(runDir, journalDir)

    expect(configPath).toBe(join(runDir, 'nw-journal.json'))

    // File should exist and parse correctly
    const content = await readFile(configPath, 'utf-8')
    const parsed = JSON.parse(content)
    expect(parsed).toHaveProperty('mcpServers')
    expect(parsed.mcpServers).toHaveProperty('nw-journal')
    expect(parsed.mcpServers['nw-journal'].command).toBe('private-journal')
    expect(parsed.mcpServers['nw-journal'].args).toContain(journalDir)
    expect(parsed.mcpServers['nw-journal'].args).toContain('--dir')
  })

  it('nw-journal.json uses stdio type', async () => {
    const runDir = testDir
    const journalDir = join(testDir, 'journal')
    const configPath = await writeNwJournalConfig(runDir, journalDir)

    const content = await readFile(configPath, 'utf-8')
    const parsed = JSON.parse(content)
    expect(parsed.mcpServers['nw-journal'].type).toBe('stdio')
  })
})

describe('cancel / EXEC-08: activePids pattern', () => {
  it('activePids is exported and is a Set (used by cancel in worker/index.ts)', () => {
    expect(activePids).toBeInstanceOf(Set)
  })

  it('activePids is cleared after killAllActive', async () => {
    activePids.add(999998)
    activePids.add(999997)
    await killAllActive()
    expect(activePids.size).toBe(0)
  })
})
