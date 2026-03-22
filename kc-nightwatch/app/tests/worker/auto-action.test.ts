import { describe, it, expect, beforeEach, afterEach, mock, spyOn } from 'bun:test'
import path from 'node:path'

/**
 * Tests for auto-action.ts — outcome recording with dedup logic.
 *
 * Strategy: mock outcome-store module functions to isolate recordRunOutcomes logic.
 * We use spyOn to replace appendOutcome/queryOutcomes at runtime without touching the store.
 *
 * AUTO-01: PR outcomes recorded after production runs
 * AUTO-02: Linear issue outcomes recorded after production runs
 * D-02: dry-run and self-repair modes produce NO outcome records
 * D-08: PR dedup via gh pr list AND outcomes.yaml
 * D-09: Linear dedup via outcomes.yaml only
 */

import * as outcomeStore from '../../server/services/outcome-store.ts'
import type { Run, OutcomeRecord } from '../../shared/types.ts'

// We need to import recordRunOutcomes — but it imports outcome-store at module level.
// Use Bun's module mock: after spying on the outcome-store module, import auto-action.
import { recordRunOutcomes } from '../../worker/auto-action.ts'

const makeRun = (overrides: Partial<Run> = {}): Run => ({
  id: 'run-001',
  target: '__all__',
  mode: 'production',
  trigger: 'manual',
  status: 'completed',
  log_path: '/tmp/run-001/log.jsonl',
  queued_at: '2026-03-22T10:00:00.000Z',
  started_at: '2026-03-22T10:00:01.000Z',
  completed_at: '2026-03-22T10:05:00.000Z',
  ...overrides,
})

const makePerTarget = (overrides: {
  pr_url?: string
  linear_url?: string
  branch?: string
  signal_id?: string
} = {}) => ({
  'e2e-pipeline': {
    actions: [
      {
        signal_id: overrides.signal_id ?? 'sig-001',
        type: 'code-fix',
        summary: 'Fix a bug',
        pr_url: overrides.pr_url,
        linear_url: overrides.linear_url,
        branch: overrides.branch ?? 'kc-nightwatch/2026-03-22-e2e-pipeline-fixes',
        indicator: 'bug_count',
        assessment: {
          closer_to_north_star: 'yes' as const,
          confidence: 'high' as const,
          reasoning: 'reduces bugs',
        },
      },
    ],
  },
})

describe('recordRunOutcomes — mode gating (D-02)', () => {
  let appendSpy: ReturnType<typeof spyOn>
  let querySpy: ReturnType<typeof spyOn>

  beforeEach(() => {
    appendSpy = spyOn(outcomeStore, 'appendOutcome').mockResolvedValue(undefined)
    querySpy = spyOn(outcomeStore, 'queryOutcomes').mockResolvedValue([])
  })

  afterEach(() => {
    appendSpy.mockRestore()
    querySpy.mockRestore()
  })

  it('dry-run mode creates NO outcome records', async () => {
    const run = makeRun({ mode: 'dry-run' })
    const result = await recordRunOutcomes(run, makePerTarget({ pr_url: 'https://github.com/org/repo/pull/42' }))
    expect(result.skipped_mode).toBe(true)
    expect(appendSpy).not.toHaveBeenCalled()
    expect(result.recorded).toBe(0)
  })

  it('self-repair mode creates NO outcome records', async () => {
    const run = makeRun({ mode: 'self-repair' })
    const result = await recordRunOutcomes(run, makePerTarget({ pr_url: 'https://github.com/org/repo/pull/99' }))
    expect(result.skipped_mode).toBe(true)
    expect(appendSpy).not.toHaveBeenCalled()
    expect(result.recorded).toBe(0)
  })
})

describe('recordRunOutcomes — production mode recording (AUTO-01, AUTO-02)', () => {
  let appendSpy: ReturnType<typeof spyOn>
  let querySpy: ReturnType<typeof spyOn>

  beforeEach(() => {
    appendSpy = spyOn(outcomeStore, 'appendOutcome').mockResolvedValue(undefined)
    querySpy = spyOn(outcomeStore, 'queryOutcomes').mockResolvedValue([])
  })

  afterEach(() => {
    appendSpy.mockRestore()
    querySpy.mockRestore()
  })

  it('production mode with pr_url creates an OutcomeRecord of type "pr"', async () => {
    const run = makeRun()
    const result = await recordRunOutcomes(run, makePerTarget({ pr_url: 'https://github.com/org/repo/pull/42' }))
    expect(result.skipped_mode).toBe(false)
    expect(result.recorded).toBe(1)
    expect(appendSpy).toHaveBeenCalledTimes(1)
    const [record] = appendSpy.mock.calls[0] as [OutcomeRecord]
    expect(record.type).toBe('pr')
    expect(record.url).toBe('https://github.com/org/repo/pull/42')
    expect(record.target).toBe('e2e-pipeline')
    expect(record.signal_id).toBe('sig-001')
    expect(record.run_id).toBe('run-001')
    expect(record.status).toBe('open')
    expect(record.id).toBeTruthy()
  })

  it('production mode with linear_url creates an OutcomeRecord of type "linear_issue"', async () => {
    const run = makeRun()
    const result = await recordRunOutcomes(run, makePerTarget({ linear_url: 'https://linear.app/team/issue/SC-123' }))
    expect(result.skipped_mode).toBe(false)
    expect(result.recorded).toBe(1)
    expect(appendSpy).toHaveBeenCalledTimes(1)
    const [record] = appendSpy.mock.calls[0] as [OutcomeRecord]
    expect(record.type).toBe('linear_issue')
    expect(record.url).toBe('https://linear.app/team/issue/SC-123')
    expect(record.status).toBe('open')
  })

  it('action with both pr_url and linear_url creates two OutcomeRecords', async () => {
    const run = makeRun()
    const result = await recordRunOutcomes(run, makePerTarget({
      pr_url: 'https://github.com/org/repo/pull/42',
      linear_url: 'https://linear.app/team/issue/SC-123',
    }))
    expect(result.recorded).toBe(2)
    expect(appendSpy).toHaveBeenCalledTimes(2)
    const types = appendSpy.mock.calls.map(c => (c[0] as OutcomeRecord).type)
    expect(types).toContain('pr')
    expect(types).toContain('linear_issue')
  })

  it('recordRunOutcomes returns summary with recorded and skipped counts', async () => {
    const run = makeRun()
    const result = await recordRunOutcomes(run, makePerTarget({ pr_url: 'https://github.com/org/repo/pull/42' }))
    expect(typeof result.recorded).toBe('number')
    expect(typeof result.skipped_dedup).toBe('number')
    expect(typeof result.skipped_mode).toBe('boolean')
    expect(Array.isArray(result.errors)).toBe(true)
  })
})

describe('recordRunOutcomes — dedup logic (D-08, D-09)', () => {
  let appendSpy: ReturnType<typeof spyOn>
  let querySpy: ReturnType<typeof spyOn>

  afterEach(() => {
    appendSpy.mockRestore()
    querySpy.mockRestore()
  })

  it('PR dedup: skips recording when existing open outcome has same signal_id+target+type', async () => {
    appendSpy = spyOn(outcomeStore, 'appendOutcome').mockResolvedValue(undefined)
    querySpy = spyOn(outcomeStore, 'queryOutcomes').mockResolvedValue([
      {
        id: 'existing-1',
        type: 'pr',
        target: 'e2e-pipeline',
        signal_id: 'sig-001',
        run_id: 'run-000',
        url: 'https://github.com/org/repo/pull/41',
        status: 'open',
        created_at: '2026-03-21T10:00:00.000Z',
      },
    ] as OutcomeRecord[])

    const run = makeRun()
    const result = await recordRunOutcomes(run, makePerTarget({ pr_url: 'https://github.com/org/repo/pull/42' }))
    expect(result.skipped_dedup).toBe(1)
    expect(result.recorded).toBe(0)
    expect(appendSpy).not.toHaveBeenCalled()
  })

  it('Linear dedup: skips recording when existing open outcome has same signal_id+target+type', async () => {
    appendSpy = spyOn(outcomeStore, 'appendOutcome').mockResolvedValue(undefined)
    querySpy = spyOn(outcomeStore, 'queryOutcomes').mockResolvedValue([
      {
        id: 'existing-2',
        type: 'linear_issue',
        target: 'e2e-pipeline',
        signal_id: 'sig-001',
        run_id: 'run-000',
        url: 'https://linear.app/team/issue/SC-122',
        status: 'open',
        created_at: '2026-03-21T10:00:00.000Z',
      },
    ] as OutcomeRecord[])

    const run = makeRun()
    const result = await recordRunOutcomes(run, makePerTarget({ linear_url: 'https://linear.app/team/issue/SC-123' }))
    expect(result.skipped_dedup).toBe(1)
    expect(result.recorded).toBe(0)
    expect(appendSpy).not.toHaveBeenCalled()
  })
})

describe('executor.ts wiring (static verification)', () => {
  const EXECUTOR_PATH = path.join(import.meta.dir, '../../worker/executor.ts')

  it('imports recordRunOutcomes from auto-action.ts', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    expect(source).toMatch(/import\s*\{[^}]*recordRunOutcomes[^}]*\}\s*from\s*['"].*auto-action/)
  })

  it('calls recordRunOutcomes in post-run flow (not just imported)', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    const matches = source.match(/recordRunOutcomes/g)
    expect(matches).not.toBeNull()
    expect(matches!.length).toBeGreaterThanOrEqual(2)
  })
})
