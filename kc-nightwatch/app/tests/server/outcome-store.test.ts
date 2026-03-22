import { describe, it, expect, beforeEach, afterEach } from 'bun:test'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import type { OutcomeRecord } from '../../shared/types.ts'

// We need to test readOutcomes, appendOutcome, queryOutcomes
// but these functions use a hardcoded OUTCOMES_YAML_PATH.
// We'll import the underlying yaml-store functions and test the store
// using a temp file by overriding the path module-level.

// Strategy: mock at the module level by dynamic import with patched env,
// or call the yaml-store directly and test through it.
// Per project pattern (yaml-store.test.ts): use temp dir + call the underlying store functions.

// Since outcome-store.ts exports functions with a hardcoded path,
// we test by importing the module and overriding the OUTCOMES_YAML_PATH
// via the exported constant, or by testing through yaml-store with the same wrapper.
// Per plan instruction: "Mock readYamlFile/writeYamlFile or use temp dir".
// We'll mock the YAML path by directly testing the store functions
// after module-level patching via a test-only export.

// The outcome-store.ts module must export OUTCOMES_YAML_PATH so tests can override it.
// Tests use the direct readYamlFile/writeYamlFile to set up state.

import { readYamlFile, writeYamlFile } from '../../server/services/yaml-store.ts'
import {
  readOutcomes,
  appendOutcome,
  queryOutcomes,
  OUTCOMES_YAML_PATH,
} from '../../server/services/outcome-store.ts'

// Test with a temp file by monkey-patching the module path.
// Since Bun doesn't support module mocking easily, we use a workaround:
// outcome-store.ts should accept an optional path parameter (testable design).

// NOTE: The outcome-store must accept optional outcomesPath param for testability.
// If the module doesn't support this, we use the real path in /tmp tests.

let testOutcomesPath: string
let testDir: string

beforeEach(async () => {
  testDir = await mkdtemp(join(tmpdir(), 'nw-outcomes-'))
  testOutcomesPath = join(testDir, 'nightwatch-outcomes.yaml')
})

afterEach(async () => {
  await rm(testDir, { recursive: true, force: true })
})

const makeRecord = (overrides: Partial<OutcomeRecord> = {}): OutcomeRecord => ({
  id: 'test-id-1',
  type: 'pr',
  target: 'e2e-pipeline',
  signal_id: 'sig-001',
  run_id: 'run-001',
  url: 'https://github.com/org/repo/pull/42',
  branch: 'kc-nightwatch/2026-03-22-e2e-pipeline-fixes',
  status: 'open',
  created_at: '2026-03-22T10:00:00.000Z',
  ...overrides,
})

describe('readOutcomes', () => {
  it('returns empty array when file does not exist', async () => {
    const results = await readOutcomes(testOutcomesPath)
    expect(results).toEqual([])
  })

  it('returns empty array when file exists but has no outcomes key', async () => {
    await writeYamlFile(testOutcomesPath, {})
    const results = await readOutcomes(testOutcomesPath)
    expect(results).toEqual([])
  })
})

describe('appendOutcome', () => {
  it('creates the file if it does not exist, then readOutcomes returns it', async () => {
    const record = makeRecord()
    await appendOutcome(record, testOutcomesPath)
    const results = await readOutcomes(testOutcomesPath)
    expect(results).toHaveLength(1)
    expect(results[0]?.id).toBe('test-id-1')
    expect(results[0]?.url).toBe('https://github.com/org/repo/pull/42')
    expect(await Bun.file(testOutcomesPath).exists()).toBe(true)
  })

  it('appends multiple records and readOutcomes returns all', async () => {
    const r1 = makeRecord({ id: 'id-1', signal_id: 'sig-1' })
    const r2 = makeRecord({ id: 'id-2', signal_id: 'sig-2', type: 'linear_issue', url: 'https://linear.app/team/issue/SC-123' })
    await appendOutcome(r1, testOutcomesPath)
    await appendOutcome(r2, testOutcomesPath)
    const results = await readOutcomes(testOutcomesPath)
    expect(results).toHaveLength(2)
    const ids = results.map(r => r.id)
    expect(ids).toContain('id-1')
    expect(ids).toContain('id-2')
  })
})

describe('queryOutcomes', () => {
  beforeEach(async () => {
    // Seed with 4 records across 2 targets, 2 types, 2 statuses
    await appendOutcome(makeRecord({
      id: 'q-1', target: 'e2e-pipeline', type: 'pr', status: 'open',
      signal_id: 'sig-1', created_at: '2026-03-22T10:00:00.000Z',
    }), testOutcomesPath)
    await appendOutcome(makeRecord({
      id: 'q-2', target: 'e2e-pipeline', type: 'linear_issue', status: 'open',
      signal_id: 'sig-2', url: 'https://linear.app/team/issue/SC-100',
      created_at: '2026-03-21T10:00:00.000Z',
    }), testOutcomesPath)
    await appendOutcome(makeRecord({
      id: 'q-3', target: 'kc-plugin-forge', type: 'pr', status: 'merged',
      signal_id: 'sig-3', created_at: '2026-03-20T10:00:00.000Z',
    }), testOutcomesPath)
    await appendOutcome(makeRecord({
      id: 'q-4', target: 'kc-plugin-forge', type: 'linear_issue', status: 'closed',
      signal_id: 'sig-4', url: 'https://linear.app/team/issue/SC-101',
      created_at: '2026-03-19T10:00:00.000Z',
    }), testOutcomesPath)
  })

  it('queryOutcomes({}) returns all records', async () => {
    const results = await queryOutcomes({}, testOutcomesPath)
    expect(results).toHaveLength(4)
  })

  it('queryOutcomes({ target }) filters by target name', async () => {
    const results = await queryOutcomes({ target: 'e2e-pipeline' }, testOutcomesPath)
    expect(results).toHaveLength(2)
    expect(results.every(r => r.target === 'e2e-pipeline')).toBe(true)
  })

  it('queryOutcomes({ type: "pr" }) filters by outcome type', async () => {
    const results = await queryOutcomes({ type: 'pr' }, testOutcomesPath)
    expect(results).toHaveLength(2)
    expect(results.every(r => r.type === 'pr')).toBe(true)
  })

  it('queryOutcomes({ status: "open" }) filters by status', async () => {
    const results = await queryOutcomes({ status: 'open' }, testOutcomesPath)
    expect(results).toHaveLength(2)
    expect(results.every(r => r.status === 'open')).toBe(true)
  })

  it('queryOutcomes({ since }) filters by created_at date', async () => {
    // since '2026-03-21' should include 2026-03-21 and 2026-03-22, exclude 2026-03-20 and 2026-03-19
    const results = await queryOutcomes({ since: '2026-03-21' }, testOutcomesPath)
    expect(results).toHaveLength(2)
    const ids = results.map(r => r.id)
    expect(ids).toContain('q-1')
    expect(ids).toContain('q-2')
  })

  it('results are sorted by created_at descending', async () => {
    const results = await queryOutcomes({}, testOutcomesPath)
    // Most recent first
    expect(results[0]?.created_at).toBe('2026-03-22T10:00:00.000Z')
    expect(results[results.length - 1]?.created_at).toBe('2026-03-19T10:00:00.000Z')
  })
})
