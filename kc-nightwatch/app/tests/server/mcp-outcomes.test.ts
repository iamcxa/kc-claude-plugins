import { describe, it, expect, mock, beforeEach, afterEach, spyOn } from 'bun:test'
import type { OutcomeRecord } from '../../shared/types.ts'
import * as outcomeStore from '../../server/services/outcome-store.ts'
import * as feedbackCollector from '../../worker/feedback-collector.ts'
import * as yamlStore from '../../server/services/yaml-store.ts'
import * as runStore from '../../server/services/run-store.ts'
import * as feedbackStore from '../../server/services/feedback-store.ts'

// ============================================================
// Import after namespace imports (spyOn patches at runtime in beforeEach)
// ============================================================
const { createMcpServer } = await import('../../server/services/mcp-tools.ts')

// ============================================================
// Spy declarations
// ============================================================
let queryOutcomesSpy: ReturnType<typeof spyOn>
let readOutcomesSpy: ReturnType<typeof spyOn>
let appendOutcomeSpy: ReturnType<typeof spyOn>
let checkPrStatusSpy: ReturnType<typeof spyOn>
let checkLinearStatusSpy: ReturnType<typeof spyOn>
let collectImplicitFeedbackSpy: ReturnType<typeof spyOn>
let readTargetsSpy: ReturnType<typeof spyOn>
let writeTargetsSpy: ReturnType<typeof spyOn>
let loadOrCreateAppConfigSpy: ReturnType<typeof spyOn>
let writeAppConfigSpy: ReturnType<typeof spyOn>
let readYamlFileSpy: ReturnType<typeof spyOn>
let writeYamlFileSpy: ReturnType<typeof spyOn>
let listRunsSpy: ReturnType<typeof spyOn>
let getRunSpy: ReturnType<typeof spyOn>
let appendRunSpy: ReturnType<typeof spyOn>
let appendFeedbackSpy: ReturnType<typeof spyOn>
let getCalibrationDataSpy: ReturnType<typeof spyOn>
let getFeedbackForRunSpy: ReturnType<typeof spyOn>
let getFeedbackForSignalSpy: ReturnType<typeof spyOn>
let writeFeedbackTrendsSpy: ReturnType<typeof spyOn>

beforeEach(() => {
  queryOutcomesSpy = spyOn(outcomeStore, 'queryOutcomes').mockResolvedValue([])
  readOutcomesSpy = spyOn(outcomeStore, 'readOutcomes').mockResolvedValue([])
  appendOutcomeSpy = spyOn(outcomeStore, 'appendOutcome').mockResolvedValue(undefined)
  checkPrStatusSpy = spyOn(feedbackCollector, 'checkPrStatus').mockResolvedValue(null)
  checkLinearStatusSpy = spyOn(feedbackCollector, 'checkLinearStatus').mockResolvedValue(null)
  collectImplicitFeedbackSpy = spyOn(feedbackCollector, 'collectImplicitFeedback').mockResolvedValue({ entries: [], errors: [] })
  readTargetsSpy = spyOn(yamlStore, 'readTargets').mockResolvedValue({})
  writeTargetsSpy = spyOn(yamlStore, 'writeTargets').mockResolvedValue(undefined)
  loadOrCreateAppConfigSpy = spyOn(yamlStore, 'loadOrCreateAppConfig').mockResolvedValue({
    host: '127.0.0.1',
    port: 3200,
    schedule: { enabled: false, self_repair_before: true },
    max_concurrent_runs: 1 as const,
    plugins_dir: '/tmp/plugins',
  })
  writeAppConfigSpy = spyOn(yamlStore, 'writeAppConfig').mockResolvedValue(undefined)
  readYamlFileSpy = spyOn(yamlStore, 'readYamlFile').mockResolvedValue(null)
  writeYamlFileSpy = spyOn(yamlStore, 'writeYamlFile').mockResolvedValue(undefined)
  listRunsSpy = spyOn(runStore, 'listRuns').mockResolvedValue([])
  getRunSpy = spyOn(runStore, 'getRun').mockResolvedValue(null)
  appendRunSpy = spyOn(runStore, 'appendRun').mockResolvedValue(undefined)
  appendFeedbackSpy = spyOn(feedbackStore, 'appendFeedback').mockResolvedValue(undefined)
  getCalibrationDataSpy = spyOn(feedbackStore, 'getCalibrationData').mockResolvedValue([])
  getFeedbackForRunSpy = spyOn(feedbackStore, 'getFeedbackForRun').mockResolvedValue([])
  getFeedbackForSignalSpy = spyOn(feedbackStore, 'getFeedbackForSignal').mockResolvedValue([])
  writeFeedbackTrendsSpy = spyOn(feedbackStore, 'writeFeedbackTrends').mockResolvedValue(undefined)
})

afterEach(() => {
  queryOutcomesSpy.mockRestore()
  readOutcomesSpy.mockRestore()
  appendOutcomeSpy.mockRestore()
  checkPrStatusSpy.mockRestore()
  checkLinearStatusSpy.mockRestore()
  collectImplicitFeedbackSpy.mockRestore()
  readTargetsSpy.mockRestore()
  writeTargetsSpy.mockRestore()
  loadOrCreateAppConfigSpy.mockRestore()
  writeAppConfigSpy.mockRestore()
  readYamlFileSpy.mockRestore()
  writeYamlFileSpy.mockRestore()
  listRunsSpy.mockRestore()
  getRunSpy.mockRestore()
  appendRunSpy.mockRestore()
  appendFeedbackSpy.mockRestore()
  getCalibrationDataSpy.mockRestore()
  getFeedbackForRunSpy.mockRestore()
  getFeedbackForSignalSpy.mockRestore()
  writeFeedbackTrendsSpy.mockRestore()
})

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
    queryOutcomesSpy.mockClear()
    readOutcomesSpy.mockClear()
    checkPrStatusSpy.mockClear()
    checkLinearStatusSpy.mockClear()
  })

  it('Test 1: returns all outcomes when no filters provided', async () => {
    queryOutcomesSpy.mockImplementation(async () => [PR_OUTCOME, LINEAR_OUTCOME, OLD_OUTCOME])

    const result = await callTool('nw_get_outcomes', {})
    const outcomes = JSON.parse(result.content[0]!.text) as OutcomeRecord[]
    expect(Array.isArray(outcomes)).toBe(true)
    expect(outcomes.length).toBe(3)
    // Verify queryOutcomes was called (filter values may be undefined/omitted)
    expect(queryOutcomesSpy).toHaveBeenCalledTimes(1)
  })

  it('Test 2: filters by target when target is provided', async () => {
    queryOutcomesSpy.mockImplementation(async (filter: unknown) => {
      const f = filter as { target?: string }
      return [PR_OUTCOME, OLD_OUTCOME].filter(o => !f.target || o.target === f.target)
    })

    const result = await callTool('nw_get_outcomes', { target: 'e2e-pipeline' })
    const outcomes = JSON.parse(result.content[0]!.text) as OutcomeRecord[]
    expect(outcomes.every(o => o.target === 'e2e-pipeline')).toBe(true)
    // Verify the filter was passed through (either as {target: 'e2e-pipeline'} or positional)
    expect(queryOutcomesSpy).toHaveBeenCalledTimes(1)
    const callArgs = queryOutcomesSpy.mock.calls[0]![0] as { target?: string }
    expect(callArgs.target).toBe('e2e-pipeline')
  })

  it('Test 3: filters by type=pr when type is provided', async () => {
    queryOutcomesSpy.mockImplementation(async (filter: unknown) => {
      const f = filter as { type?: string }
      return [PR_OUTCOME, LINEAR_OUTCOME, OLD_OUTCOME].filter(o => !f.type || o.type === f.type)
    })

    const result = await callTool('nw_get_outcomes', { type: 'pr' })
    const outcomes = JSON.parse(result.content[0]!.text) as OutcomeRecord[]
    expect(outcomes.every(o => o.type === 'pr')).toBe(true)
    expect(queryOutcomesSpy).toHaveBeenCalledTimes(1)
    const callArgs = queryOutcomesSpy.mock.calls[0]![0] as { type?: string }
    expect(callArgs.type).toBe('pr')
  })

  it('Test 4: filters by since date when since is provided', async () => {
    queryOutcomesSpy.mockImplementation(async (filter: unknown) => {
      const f = filter as { since?: string }
      return [PR_OUTCOME, LINEAR_OUTCOME, OLD_OUTCOME].filter(o => !f.since || o.created_at >= f.since)
    })

    const result = await callTool('nw_get_outcomes', { since: '2026-03-20' })
    const outcomes = JSON.parse(result.content[0]!.text) as OutcomeRecord[]
    expect(outcomes.every(o => o.created_at >= '2026-03-20')).toBe(true)
    expect(queryOutcomesSpy).toHaveBeenCalledTimes(1)
    const callArgs = queryOutcomesSpy.mock.calls[0]![0] as { since?: string }
    expect(callArgs.since).toBe('2026-03-20')
  })
})

// ============================================================
// nw_get_outcome_status tests
// ============================================================
describe('nw_get_outcome_status', () => {
  beforeEach(() => {
    readOutcomesSpy.mockClear()
    checkPrStatusSpy.mockClear()
    checkLinearStatusSpy.mockClear()
  })

  it('Test 5: polls checkPrStatus for PR outcomes and returns live status', async () => {
    readOutcomesSpy.mockImplementation(async () => [PR_OUTCOME])
    checkPrStatusSpy.mockImplementation(async () => 'accepted')

    const result = await callTool('nw_get_outcome_status', { outcome_id: 'oc-pr-001' })
    const data = JSON.parse(result.content[0]!.text) as OutcomeRecord & { live_status: string; checked_at: string }
    expect(data.id).toBe('oc-pr-001')
    expect(data.live_status).toBe('accepted')
    expect(data.checked_at).toBeDefined()
    expect(checkPrStatusSpy).toHaveBeenCalledWith(PR_OUTCOME.url)
    expect(checkLinearStatusSpy).not.toHaveBeenCalled()
  })

  it('Test 6: polls checkLinearStatus for Linear outcomes and returns live status', async () => {
    readOutcomesSpy.mockImplementation(async () => [LINEAR_OUTCOME])
    checkLinearStatusSpy.mockImplementation(async () => 'accepted')

    const result = await callTool('nw_get_outcome_status', { outcome_id: 'oc-li-001' })
    const data = JSON.parse(result.content[0]!.text) as OutcomeRecord & { live_status: string }
    expect(data.id).toBe('oc-li-001')
    expect(data.live_status).toBe('accepted')
    expect(checkLinearStatusSpy).toHaveBeenCalledWith(LINEAR_OUTCOME.url)
    expect(checkPrStatusSpy).not.toHaveBeenCalled()
  })

  it('Test 7: returns isError when outcome_id is not found', async () => {
    readOutcomesSpy.mockImplementation(async () => [PR_OUTCOME])

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
    readOutcomesSpy.mockImplementation(async () => [PR_OUTCOME, LINEAR_OUTCOME, OLD_OUTCOME])

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
