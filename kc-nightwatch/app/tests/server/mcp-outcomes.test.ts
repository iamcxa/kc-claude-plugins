import { describe, it, expect, mock, beforeEach } from 'bun:test'
import type { OutcomeRecord } from '../../shared/types.ts'

// ============================================================
// Mocks — must precede mcp-tools import
// ============================================================

const mockQueryOutcomes = mock(async (_filter?: unknown): Promise<OutcomeRecord[]> => [])
const mockReadOutcomes = mock(async (): Promise<OutcomeRecord[]> => [])
const mockCheckPrStatus = mock(async (_url: string): Promise<'accepted' | 'rejected' | null> => null)
const mockCheckLinearStatus = mock(async (_url: string): Promise<'accepted' | 'rejected' | null> => null)

// Existing dependency mocks (required by mcp-tools.ts)
mock.module('../../server/services/outcome-store.ts', () => ({
  queryOutcomes: mockQueryOutcomes,
  readOutcomes: mockReadOutcomes,
  appendOutcome: mock(async () => {}),
  OUTCOMES_YAML_PATH: '/tmp/test-outcomes.yaml',
}))

mock.module('../../worker/feedback-collector.ts', () => ({
  checkPrStatus: mockCheckPrStatus,
  checkLinearStatus: mockCheckLinearStatus,
  collectImplicitFeedback: mock(async () => ({ entries: [], errors: [] })),
}))

mock.module('../../server/services/yaml-store.ts', () => ({
  readTargets: mock(async () => ({})),
  writeTargets: mock(async () => {}),
  loadOrCreateAppConfig: mock(async () => ({
    host: '127.0.0.1',
    port: 3200,
    schedule: { enabled: false, self_repair_before: true },
    max_concurrent_runs: 1,
    plugins_dir: '/tmp/plugins',
  })),
  writeAppConfig: mock(async () => {}),
  readYamlFile: mock(async () => null),
  writeYamlFile: mock(async () => {}),
  TARGETS_YAML_PATH: '/tmp/test-targets.yaml',
}))

mock.module('../../server/services/run-store.ts', () => ({
  listRuns: mock(async () => []),
  getRun: mock(async () => null),
  appendRun: mock(async () => {}),
  RUNS_YAML_PATH: '/tmp/test-runs.yaml',
}))

mock.module('../../server/services/feedback-store.ts', () => ({
  appendFeedback: mock(async () => {}),
  getCalibrationData: mock(async () => []),
  getFeedbackForRun: mock(async () => []),
  getFeedbackForSignal: mock(async () => []),
  writeFeedbackTrends: mock(async () => {}),
  FEEDBACK_YAML_PATH: '/tmp/test-feedback.yaml',
}))

// ============================================================
// Import after mocks
// ============================================================
const { createMcpServer } = await import('../../server/services/mcp-tools.ts')

// ============================================================
// Helper: call a registered tool by name
// ============================================================
type ToolHandler = (args: Record<string, unknown>) => Promise<{
  content: Array<{ type: string; text: string }>
  isError?: boolean
}>

function callTool(name: string, args: Record<string, unknown> = {}): Promise<{
  content: Array<{ type: string; text: string }>
  isError?: boolean
}> {
  const server = createMcpServer()
  // biome-ignore lint: accessing private for testing
  const tools = (server as unknown as { _registeredTools: Record<string, { handler: ToolHandler }> })._registeredTools
  const tool = tools[name]
  if (!tool) throw new Error(`Tool not found: ${name}`)
  return tool.handler(args)
}

// ============================================================
// Test data
// ============================================================
const PR_OUTCOME: OutcomeRecord = {
  id: 'oc-pr-001',
  type: 'pr',
  target: 'e2e-pipeline',
  signal_id: 'sig-abc',
  run_id: 'run-001',
  url: 'https://github.com/iamcxa/kc-claude-plugins/pull/42',
  branch: 'kc-nightwatch/2026-03-22-e2e-pipeline-fixes',
  status: 'open',
  created_at: '2026-03-22T08:00:00Z',
}

const LINEAR_OUTCOME: OutcomeRecord = {
  id: 'oc-li-001',
  type: 'linear_issue',
  target: 'kc-nightwatch',
  signal_id: 'sig-def',
  run_id: 'run-002',
  url: 'https://linear.app/team/issue/SC-123',
  status: 'completed',
  created_at: '2026-03-21T10:00:00Z',
}

const OLD_OUTCOME: OutcomeRecord = {
  id: 'oc-pr-002',
  type: 'pr',
  target: 'e2e-pipeline',
  signal_id: 'sig-ghi',
  run_id: 'run-003',
  url: 'https://github.com/iamcxa/kc-claude-plugins/pull/41',
  branch: 'kc-nightwatch/2026-03-18-e2e-pipeline-fixes',
  status: 'merged',
  created_at: '2026-03-18T06:00:00Z',
}

// ============================================================
// nw_get_outcomes tests
// ============================================================
describe('nw_get_outcomes', () => {
  beforeEach(() => {
    mockQueryOutcomes.mockClear()
    mockReadOutcomes.mockClear()
    mockCheckPrStatus.mockClear()
    mockCheckLinearStatus.mockClear()
  })

  it('Test 1: returns all outcomes when no filters provided', async () => {
    mockQueryOutcomes.mockImplementation(async () => [PR_OUTCOME, LINEAR_OUTCOME, OLD_OUTCOME])

    const result = await callTool('nw_get_outcomes', {})
    const outcomes = JSON.parse(result.content[0]!.text) as OutcomeRecord[]
    expect(Array.isArray(outcomes)).toBe(true)
    expect(outcomes.length).toBe(3)
    // Verify queryOutcomes was called (filter values may be undefined/omitted)
    expect(mockQueryOutcomes).toHaveBeenCalledTimes(1)
  })

  it('Test 2: filters by target when target is provided', async () => {
    mockQueryOutcomes.mockImplementation(async (filter: unknown) => {
      const f = filter as { target?: string }
      return [PR_OUTCOME, OLD_OUTCOME].filter(o => !f.target || o.target === f.target)
    })

    const result = await callTool('nw_get_outcomes', { target: 'e2e-pipeline' })
    const outcomes = JSON.parse(result.content[0]!.text) as OutcomeRecord[]
    expect(outcomes.every(o => o.target === 'e2e-pipeline')).toBe(true)
    // Verify the filter was passed through (either as {target: 'e2e-pipeline'} or positional)
    expect(mockQueryOutcomes).toHaveBeenCalledTimes(1)
    const callArgs = mockQueryOutcomes.mock.calls[0]![0] as { target?: string }
    expect(callArgs.target).toBe('e2e-pipeline')
  })

  it('Test 3: filters by type=pr when type is provided', async () => {
    mockQueryOutcomes.mockImplementation(async (filter: unknown) => {
      const f = filter as { type?: string }
      return [PR_OUTCOME, LINEAR_OUTCOME, OLD_OUTCOME].filter(o => !f.type || o.type === f.type)
    })

    const result = await callTool('nw_get_outcomes', { type: 'pr' })
    const outcomes = JSON.parse(result.content[0]!.text) as OutcomeRecord[]
    expect(outcomes.every(o => o.type === 'pr')).toBe(true)
    expect(mockQueryOutcomes).toHaveBeenCalledTimes(1)
    const callArgs = mockQueryOutcomes.mock.calls[0]![0] as { type?: string }
    expect(callArgs.type).toBe('pr')
  })

  it('Test 4: filters by since date when since is provided', async () => {
    mockQueryOutcomes.mockImplementation(async (filter: unknown) => {
      const f = filter as { since?: string }
      return [PR_OUTCOME, LINEAR_OUTCOME, OLD_OUTCOME].filter(o => !f.since || o.created_at >= f.since)
    })

    const result = await callTool('nw_get_outcomes', { since: '2026-03-20' })
    const outcomes = JSON.parse(result.content[0]!.text) as OutcomeRecord[]
    expect(outcomes.every(o => o.created_at >= '2026-03-20')).toBe(true)
    expect(mockQueryOutcomes).toHaveBeenCalledTimes(1)
    const callArgs = mockQueryOutcomes.mock.calls[0]![0] as { since?: string }
    expect(callArgs.since).toBe('2026-03-20')
  })
})

// ============================================================
// nw_get_outcome_status tests
// ============================================================
describe('nw_get_outcome_status', () => {
  beforeEach(() => {
    mockReadOutcomes.mockClear()
    mockCheckPrStatus.mockClear()
    mockCheckLinearStatus.mockClear()
  })

  it('Test 5: polls checkPrStatus for PR outcomes and returns live status', async () => {
    mockReadOutcomes.mockImplementation(async () => [PR_OUTCOME])
    mockCheckPrStatus.mockImplementation(async () => 'accepted')

    const result = await callTool('nw_get_outcome_status', { outcome_id: 'oc-pr-001' })
    const data = JSON.parse(result.content[0]!.text) as OutcomeRecord & { live_status: string; checked_at: string }
    expect(data.id).toBe('oc-pr-001')
    expect(data.live_status).toBe('accepted')
    expect(data.checked_at).toBeDefined()
    expect(mockCheckPrStatus).toHaveBeenCalledWith(PR_OUTCOME.url)
    expect(mockCheckLinearStatus).not.toHaveBeenCalled()
  })

  it('Test 6: polls checkLinearStatus for Linear outcomes and returns live status', async () => {
    mockReadOutcomes.mockImplementation(async () => [LINEAR_OUTCOME])
    mockCheckLinearStatus.mockImplementation(async () => 'accepted')

    const result = await callTool('nw_get_outcome_status', { outcome_id: 'oc-li-001' })
    const data = JSON.parse(result.content[0]!.text) as OutcomeRecord & { live_status: string }
    expect(data.id).toBe('oc-li-001')
    expect(data.live_status).toBe('accepted')
    expect(mockCheckLinearStatus).toHaveBeenCalledWith(LINEAR_OUTCOME.url)
    expect(mockCheckPrStatus).not.toHaveBeenCalled()
  })

  it('Test 7: returns isError when outcome_id is not found', async () => {
    mockReadOutcomes.mockImplementation(async () => [PR_OUTCOME])

    const result = await callTool('nw_get_outcome_status', { outcome_id: 'unknown-id' })
    expect(result.isError).toBe(true)
    expect(result.content[0]!.text).toContain('unknown-id')
  })
})

// ============================================================
// nw_outcome_summary tests
// ============================================================
describe('nw_outcome_summary', () => {
  it('Test 8: returns aggregated counts by type+status and by target', async () => {
    mockReadOutcomes.mockImplementation(async () => [PR_OUTCOME, LINEAR_OUTCOME, OLD_OUTCOME])

    const result = await callTool('nw_outcome_summary', {})
    const summary = JSON.parse(result.content[0]!.text) as {
      total: number
      recent_7d: number
      by_type_status: Record<string, number>
      by_target: Record<string, number>
    }

    expect(summary.total).toBe(3)
    expect(typeof summary.recent_7d).toBe('number')
    // PR outcomes: oc-pr-001 (open), oc-pr-002 (merged) → pr:open=1, pr:merged=1
    expect(summary.by_type_status['pr:open']).toBe(1)
    expect(summary.by_type_status['pr:merged']).toBe(1)
    // Linear outcome: oc-li-001 (completed) → linear_issue:completed=1
    expect(summary.by_type_status['linear_issue:completed']).toBe(1)
    // Targets: e2e-pipeline=2, kc-nightwatch=1
    expect(summary.by_target['e2e-pipeline']).toBe(2)
    expect(summary.by_target['kc-nightwatch']).toBe(1)
  })
})
