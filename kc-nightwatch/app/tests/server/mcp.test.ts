import { describe, it, expect, beforeEach, afterEach, spyOn } from 'bun:test'
import type { Run, RunSummary } from '../../shared/types.ts'
import * as yamlStore from '../../server/services/yaml-store.ts'
import * as outcomeStore from '../../server/services/outcome-store.ts'
import * as feedbackCollector from '../../worker/feedback-collector.ts'
import * as runStore from '../../server/services/run-store.ts'
import * as feedbackStore from '../../server/services/feedback-store.ts'

// ============================================================
// Mock data fixtures
// ============================================================
const MOCK_TARGETS = {
  'e2e-pipeline': { name: 'e2e-pipeline', type: 'plugin' as const, monitors: [], watch: [], respond: {}, indicators: [], north_star: 'quality' },
  'kc-nightwatch': { name: 'kc-nightwatch', type: 'plugin' as const, monitors: [], watch: [], respond: {}, indicators: [], north_star: 'self-improve' },
}

const MOCK_RUNS: Run[] = [
  { id: 'run-001', target: 'e2e-pipeline', mode: 'production', trigger: 'manual', status: 'completed', log_path: '/tmp/run-001.jsonl', started_at: '2026-03-19T00:00:00Z' },
  { id: 'run-002', target: 'kc-nightwatch', mode: 'dry-run', trigger: 'interval', status: 'running', log_path: '/tmp/run-002.jsonl', started_at: '2026-03-19T01:00:00Z' },
]

const mockRunSummary: RunSummary = {
  targets_active: 1,
  targets_skipped: 0,
  total_signals: 2,
  total_actions: 1,
  errors: 0,
  per_target: {
    'e2e-pipeline': {
      monitors: {},
      pipeline: { found: 2, after_dedup: 2, after_confidence_filter: 2, after_cooldown: 2, classified: {}, executed: {} },
      actions: [
        { signal_id: 'sig-abc', type: 'proposal', summary: 'Add feature X', indicator: 'quality', assessment: { closer_to_north_star: 'yes', confidence: 'high', reasoning: 'test' } },
      ],
      indicator_baseline: {},
      implementation_outcomes: [],
      pre_assessment: '',
      post_assessment: '',
    },
  },
}

// ============================================================
// Import system under test (static import — spyOn patches at runtime in beforeEach)
// ============================================================
const { createMcpServer } = await import('../../server/services/mcp-tools.ts')
const { setWorkerStatus } = await import('../../server/ipc.ts')

// ============================================================
// Spy declarations
// ============================================================
let readTargetsSpy: ReturnType<typeof spyOn>
let listRunsSpy: ReturnType<typeof spyOn>
let getRunSpy: ReturnType<typeof spyOn>
let appendRunSpy: ReturnType<typeof spyOn>
let appendFeedbackSpy: ReturnType<typeof spyOn>
let getCalibrationDataSpy: ReturnType<typeof spyOn>
let loadOrCreateAppConfigSpy: ReturnType<typeof spyOn>
let writeAppConfigSpy: ReturnType<typeof spyOn>
let readYamlFileSpy: ReturnType<typeof spyOn>
let writeYamlFileSpy: ReturnType<typeof spyOn>
let queryOutcomesSpy: ReturnType<typeof spyOn>
let readOutcomesSpy: ReturnType<typeof spyOn>
let appendOutcomeSpy: ReturnType<typeof spyOn>
let checkPrStatusSpy: ReturnType<typeof spyOn>
let checkLinearStatusSpy: ReturnType<typeof spyOn>
let collectImplicitFeedbackSpy: ReturnType<typeof spyOn>
let getFeedbackForRunSpy: ReturnType<typeof spyOn>
let getFeedbackForSignalSpy: ReturnType<typeof spyOn>
let writeFeedbackTrendsSpy: ReturnType<typeof spyOn>

beforeEach(() => {
  readTargetsSpy = spyOn(yamlStore, 'readTargets').mockResolvedValue(MOCK_TARGETS)
  listRunsSpy = spyOn(runStore, 'listRuns').mockImplementation(async (_filter?: { status?: string; target?: string }) => {
    if (_filter?.target) return MOCK_RUNS.filter(r => r.target === _filter.target)
    return MOCK_RUNS
  })
  getRunSpy = spyOn(runStore, 'getRun').mockImplementation(async (id: string) => {
    if (id === 'run-001') {
      return { id: 'run-001', target: 'e2e-pipeline', mode: 'production' as const, trigger: 'manual' as const, status: 'completed' as const, log_path: '/tmp/run-001.jsonl', started_at: '2026-03-19T00:00:00Z', summary: mockRunSummary }
    }
    return null
  })
  appendRunSpy = spyOn(runStore, 'appendRun').mockResolvedValue(undefined)
  appendFeedbackSpy = spyOn(feedbackStore, 'appendFeedback').mockResolvedValue(undefined)
  getCalibrationDataSpy = spyOn(feedbackStore, 'getCalibrationData').mockResolvedValue([])
  loadOrCreateAppConfigSpy = spyOn(yamlStore, 'loadOrCreateAppConfig').mockResolvedValue({
    host: '127.0.0.1',
    port: 3200,
    schedule: { enabled: false, self_repair_before: true },
    max_concurrent_runs: 1 as const,
    plugins_dir: '/tmp/.claude/plugins/local',
  })
  writeAppConfigSpy = spyOn(yamlStore, 'writeAppConfig').mockResolvedValue(undefined)
  readYamlFileSpy = spyOn(yamlStore, 'readYamlFile').mockResolvedValue(null)
  writeYamlFileSpy = spyOn(yamlStore, 'writeYamlFile').mockResolvedValue(undefined)
  queryOutcomesSpy = spyOn(outcomeStore, 'queryOutcomes').mockResolvedValue([])
  readOutcomesSpy = spyOn(outcomeStore, 'readOutcomes').mockResolvedValue([])
  appendOutcomeSpy = spyOn(outcomeStore, 'appendOutcome').mockResolvedValue(undefined)
  checkPrStatusSpy = spyOn(feedbackCollector, 'checkPrStatus').mockResolvedValue(null)
  checkLinearStatusSpy = spyOn(feedbackCollector, 'checkLinearStatus').mockResolvedValue(null)
  collectImplicitFeedbackSpy = spyOn(feedbackCollector, 'collectImplicitFeedback').mockResolvedValue({ entries: [], errors: [] })
  getFeedbackForRunSpy = spyOn(feedbackStore, 'getFeedbackForRun').mockResolvedValue([])
  getFeedbackForSignalSpy = spyOn(feedbackStore, 'getFeedbackForSignal').mockResolvedValue([])
  writeFeedbackTrendsSpy = spyOn(feedbackStore, 'writeFeedbackTrends').mockResolvedValue(undefined)
})

afterEach(() => {
  readTargetsSpy.mockRestore()
  listRunsSpy.mockRestore()
  getRunSpy.mockRestore()
  appendRunSpy.mockRestore()
  appendFeedbackSpy.mockRestore()
  getCalibrationDataSpy.mockRestore()
  loadOrCreateAppConfigSpy.mockRestore()
  writeAppConfigSpy.mockRestore()
  readYamlFileSpy.mockRestore()
  writeYamlFileSpy.mockRestore()
  queryOutcomesSpy.mockRestore()
  readOutcomesSpy.mockRestore()
  appendOutcomeSpy.mockRestore()
  checkPrStatusSpy.mockRestore()
  checkLinearStatusSpy.mockRestore()
  collectImplicitFeedbackSpy.mockRestore()
  getFeedbackForRunSpy.mockRestore()
  getFeedbackForSignalSpy.mockRestore()
  writeFeedbackTrendsSpy.mockRestore()
})

// ============================================================
// Helper: call a registered tool by name
// ============================================================
async function callTool(name: string, args: Record<string, unknown> = {}) {
  const server = createMcpServer()
  // MCP SDK v1.27.1: _registeredTools is a plain object (not Map)
  // biome-ignore lint: accessing private for testing
  const tools = (server as unknown as { _registeredTools: Record<string, { handler: (args: Record<string, unknown>) => Promise<unknown> }> })._registeredTools
  const tool = tools[name]
  if (!tool) throw new Error(`Tool not found: ${name}`)
  return tool.handler(args)
}

// ============================================================
// Tests
// ============================================================
describe('createMcpServer', () => {
  it('returns an McpServer instance with name nightwatch', () => {
    const server = createMcpServer()
    expect(server).toBeDefined()
    // MCP SDK v1.27.1: server._serverInfo contains the name
    // biome-ignore lint: accessing private for testing
    expect((server as unknown as { server: { _serverInfo: { name: string } } }).server._serverInfo.name).toBe('nightwatch')
  })

  it('registers all 15 tools (7 query + 1 search + 4 action + 3 outcome)', () => {
    const server = createMcpServer()
    // biome-ignore lint: accessing private for testing
    const tools = (server as unknown as { _registeredTools: Record<string, unknown> })._registeredTools
    const toolNames = Object.keys(tools)
    // 7 query tools
    expect(toolNames).toContain('nw_get_targets')
    expect(toolNames).toContain('nw_get_latest_run')
    expect(toolNames).toContain('nw_get_run')
    expect(toolNames).toContain('nw_get_proposals')
    expect(toolNames).toContain('nw_get_config_warnings')
    expect(toolNames).toContain('nw_get_schedule')
    expect(toolNames).toContain('nw_read_journal')
    // 1 search tool
    expect(toolNames).toContain('nw_search_journal')
    // 4 action tools
    expect(toolNames).toContain('nw_trigger_run')
    expect(toolNames).toContain('nw_submit_feedback')
    expect(toolNames).toContain('nw_update_schedule')
    expect(toolNames).toContain('nw_implement_proposal')
    // 3 outcome tools (Phase 10)
    expect(toolNames).toContain('nw_get_outcomes')
    expect(toolNames).toContain('nw_get_outcome_status')
    expect(toolNames).toContain('nw_outcome_summary')
    expect(toolNames.length).toBe(15)
  })
})

describe('nw_get_targets', () => {
  it('returns JSON array of targets', async () => {
    const result = await callTool('nw_get_targets') as { content: Array<{ type: string; text: string }> }
    expect(result.content[0]!.type).toBe('text')
    const targets = JSON.parse(result.content[0]!.text)
    expect(Array.isArray(targets)).toBe(true)
    expect(targets.length).toBe(2)
    expect(targets[0].name).toBeDefined()
  })
})

describe('nw_get_run', () => {
  it('returns run data for valid run_id', async () => {
    const result = await callTool('nw_get_run', { run_id: 'run-001' }) as { content: Array<{ type: string; text: string }> }
    const data = JSON.parse(result.content[0]!.text)
    expect(data.id).toBe('run-001')
  })

  it('returns isError:true for unknown run_id', async () => {
    const result = await callTool('nw_get_run', { run_id: 'unknown-run' }) as { content: Array<{ type: string; text: string }>; isError?: boolean }
    expect(result.isError).toBe(true)
    expect(result.content[0]!.text).toContain('not found')
  })
})

describe('nw_submit_feedback', () => {
  it('returns isError:true when run_id does not exist', async () => {
    const result = await callTool('nw_submit_feedback', {
      signal_id: 'sig-abc',
      target: 'e2e-pipeline',
      run_id: 'run-999',
      verdict: 'accepted',
    }) as { content: Array<{ type: string; text: string }>; isError?: boolean }
    expect(result.isError).toBe(true)
    expect(result.content[0]!.text).toContain('run-999')
  })

  it('returns isError:true when signal_id does not exist in run actions', async () => {
    const result = await callTool('nw_submit_feedback', {
      signal_id: 'sig-nonexistent',
      target: 'e2e-pipeline',
      run_id: 'run-001',
      verdict: 'accepted',
    }) as { content: Array<{ type: string; text: string }>; isError?: boolean }
    expect(result.isError).toBe(true)
    expect(result.content[0]!.text).toContain('sig-nonexistent')
  })

  it('calls appendFeedback and returns success for valid signal_id', async () => {
    const result = await callTool('nw_submit_feedback', {
      signal_id: 'sig-abc',
      target: 'e2e-pipeline',
      run_id: 'run-001',
      verdict: 'accepted',
      reason: 'Good change',
    }) as { content: Array<{ type: string; text: string }> }
    const data = JSON.parse(result.content[0]!.text)
    expect(data.ok).toBe(true)
    expect(appendFeedbackSpy).toHaveBeenCalledTimes(1)
    const calledWith = appendFeedbackSpy.mock.calls[0]![0] as { signal_id: string; source: string }
    expect(calledWith.signal_id).toBe('sig-abc')
    expect(calledWith.source).toBe('user')
  })
})

describe('nw_trigger_run', () => {
  afterEach(() => {
    // Reset worker status after each test
    setWorkerStatus('offline')
  })

  it('returns error when worker is offline', async () => {
    setWorkerStatus('offline')
    const result = await callTool('nw_trigger_run', { target: 'e2e-pipeline' }) as { content: Array<{ type: string; text: string }>; isError?: boolean }
    expect(result.isError).toBe(true)
    expect(result.content[0]!.text).toContain('offline')
  })

  it('enqueues run and returns run_id when worker is online', async () => {
    setWorkerStatus('online')
    appendRunSpy.mockClear()
    const result = await callTool('nw_trigger_run', { target: 'e2e-pipeline' }) as { content: Array<{ type: string; text: string }> }
    const data = JSON.parse(result.content[0]!.text)
    expect(data.run_id).toBeDefined()
    expect(data.status).toBe('queued')
  })
})

describe('nw_implement_proposal', () => {
  it('returns stub text containing nw_trigger_run', async () => {
    const result = await callTool('nw_implement_proposal', { proposal_id: 'prop-001' }) as { content: Array<{ type: string; text: string }>; isError?: boolean }
    expect(result.isError).toBeUndefined()
    expect(result.content[0]!.text).toContain('nw_trigger_run')
  })
})

describe('nw_read_journal', () => {
  it('returns graceful message when journal directory does not exist', async () => {
    const result = await callTool('nw_read_journal', { target: 'nonexistent-target-xyzxyz' }) as { content: Array<{ type: string; text: string }> }
    expect(result.content[0]!.type).toBe('text')
    expect(result.content[0]!.text).toContain('nonexistent-target-xyzxyz')
  })
})

describe('nw_search_journal', () => {
  it('returns graceful message for nonexistent target journal', async () => {
    const result = await callTool('nw_search_journal', { target: 'nonexistent-target-xyzxyz', query: 'test' }) as { content: Array<{ type: string; text: string }> }
    expect(result.content[0]!.type).toBe('text')
    expect(result.content[0]!.text).toContain('nonexistent-target-xyzxyz')
  })
})
