import { describe, it, expect } from 'bun:test'
import type {
  Target,
  RunSummary,
  RunSummaryAction,
  IndicatorBaseline,
  ImplementationOutcome,
  PerTargetSummary,
  ParsedLogEvent,
  ScheduleConfig,
  ServerToWorker,
  WorkerToServer,
} from '../../shared/types.ts'
import { AppConfigSchema } from '../../shared/types.ts'

// --- PHASE 1 TESTS (must stay passing) ---
describe('AppConfigSchema', () => {
  const base = {
    host: '127.0.0.1',
    port: 3200,
    schedule: { enabled: false, self_repair_before: true },
    plugins_dir: '/tmp',
  }

  it('accepts valid config', () => {
    expect(() => AppConfigSchema.parse(base)).not.toThrow()
  })

  it('silently ignores unknown fields like max_concurrent_runs (backward compat)', () => {
    const result = AppConfigSchema.parse({ ...base, max_concurrent_runs: 1 })
    expect(result.host).toBe('127.0.0.1')
    // max_concurrent_runs passes through (passthrough mode)
    expect((result as Record<string, unknown>).max_concurrent_runs).toBe(1)
  })

  it('accepts config without max_concurrent_runs field at all', () => {
    expect(() => AppConfigSchema.parse(base)).not.toThrow()
  })

  it('parsed result does not have max_concurrent_runs as typed property', () => {
    const result = AppConfigSchema.parse(base)
    // The AppConfig type does not include max_concurrent_runs
    expect('max_concurrent_runs' in result).toBe(false)
  })

  it('accepts optional auth_token', () => {
    const result = AppConfigSchema.parse({ ...base, auth_token: 'abc123' })
    expect(result.auth_token).toBe('abc123')
  })

  it('defaults host to 127.0.0.1 when omitted', () => {
    const result = AppConfigSchema.parse({ ...base, host: undefined })
    expect(result.host).toBe('127.0.0.1')
  })

  // PHASE 2: plugins_dir now has a default value
  it('plugins_dir has default when omitted', () => {
    const result = AppConfigSchema.parse({
      schedule: { enabled: false, self_repair_before: true },
    })
    expect(result.plugins_dir).toBeTruthy()
    expect(result.plugins_dir).toContain('.claude/plugins/local')
  })
})

// --- PHASE 2 NEW TESTS ---
describe('Target type', () => {
  it('accepts full Target object with all fields', () => {
    const target: Target = {
      name: 'test-plugin',
      type: 'plugin',
      monitors: ['github-issues', 'journal'],
      watch: ['performance', 'bug'],
      respond: { 'code-fix': true, 'proposal': true },
      indicators: [{ id: 'IND-01', description: 'Issue count', target: '< 10' }],
      north_star: 'Zero open issues',
      path: '/home/user/project',
      auth: 'token',
      extra_plugin_dirs: ['/home/user/.claude/plugins'],
      extra_mcp_config: [],
    }
    expect(target.name).toBe('test-plugin')
    expect(target.type).toBe('plugin')
    expect(target.monitors).toContain('github-issues')
    expect(target.respond['code-fix']).toBe(true)
  })

  it('accepts product type', () => {
    const target: Target = {
      name: 'my-product',
      type: 'product',
      monitors: [],
      watch: [],
      respond: {},
      indicators: [],
      north_star: 'User growth',
    }
    expect(target.type).toBe('product')
  })
})

describe('ScheduleConfig type', () => {
  it('is exported as standalone type', () => {
    const config: ScheduleConfig = {
      enabled: true,
      interval_hours: 4,
      self_repair_before: true,
    }
    expect(config.enabled).toBe(true)
    expect(config.interval_hours).toBe(4)
  })

  it('allows interval_hours to be optional', () => {
    const config: ScheduleConfig = {
      enabled: false,
      self_repair_before: false,
    }
    expect(config.interval_hours).toBeUndefined()
  })
})

describe('RunSummary (Appendix B full shape)', () => {
  it('accepts full Appendix B RunSummary', () => {
    const action: RunSummaryAction = {
      signal_id: 'SIG-001',
      type: 'code-fix',
      summary: 'Fixed null check',
      pr_url: 'https://github.com/org/repo/pull/1',
      branch: 'kc-nightwatch/2026-03-18-plugin-fixes',
      indicator: 'IND-01',
      assessment: {
        closer_to_north_star: 'yes',
        confidence: 'high',
        reasoning: 'Directly reduces bug count',
      },
    }

    const baseline: IndicatorBaseline = {
      value: 5,
      measurement: '5 journal mentions in 14d',
      previous_value: 8,
      trend: 'improving',
    }

    const outcome: ImplementationOutcome = {
      proposal_id: 'PROP-001',
      pr_url: 'https://github.com/org/repo/pull/2',
      target: 'test-plugin',
      indicator: 'IND-01',
      before: 8,
      after: 5,
      delta: -3,
      effective: true,
    }

    const perTarget: PerTargetSummary = {
      monitors: { 'github-issues': { status: 'ok', signals: 3 } },
      pipeline: {
        found: 5,
        after_dedup: 4,
        after_confidence_filter: 3,
        after_cooldown: 2,
        classified: { 'code-fix': 1, 'proposal': 1 },
        executed: { 'code-fix': 1 },
      },
      actions: [action],
      indicator_baseline: { 'IND-01': baseline },
      implementation_outcomes: [outcome],
      pre_assessment: 'Plugin has high churn',
      post_assessment: 'Fixed 1 critical bug',
    }

    const summary: RunSummary = {
      targets_active: 2,
      targets_skipped: 0,
      total_signals: 5,
      total_actions: 1,
      errors: 0,
      per_target: { 'test-plugin': perTarget },
    }

    expect(summary.targets_active).toBe(2)
    expect(summary.per_target['test-plugin'].actions[0].signal_id).toBe('SIG-001')
    expect(summary.per_target['test-plugin'].pipeline.found).toBe(5)
    expect(summary.per_target['test-plugin'].indicator_baseline['IND-01'].trend).toBe('improving')
  })

  it('allows legacy phases_completed field for backward compat', () => {
    const summary: RunSummary = {
      targets_active: 1,
      targets_skipped: 0,
      total_signals: 0,
      total_actions: 0,
      errors: 0,
      per_target: {},
      phases_completed: ['Phase 1', 'Phase 2'],
    }
    expect(summary.phases_completed).toContain('Phase 1')
  })
})

describe('ParsedLogEvent (extended with Phase 2 fields)', () => {
  it('has base fields from Phase 1', () => {
    const event: ParsedLogEvent = { type: 'assistant', content: 'hello', raw: '{}' }
    expect(event.type).toBe('assistant')
  })

  it('has new Phase 2 optional fields', () => {
    const event: ParsedLogEvent = {
      type: 'assistant',
      content: 'Phase 2: Signal Harvesting',
      raw: '{}',
      phase: 'Phase 2',
      tool_name: 'bash',
      agent_name: 'signal-harvester',
      is_phase_start: true,
      is_phase_complete: false,
    }
    expect(event.phase).toBe('Phase 2')
    expect(event.tool_name).toBe('bash')
    expect(event.agent_name).toBe('signal-harvester')
    expect(event.is_phase_start).toBe(true)
  })
})

describe('IPC message extensions', () => {
  it('ServerToWorker includes schedule type', () => {
    const msg: ServerToWorker = {
      type: 'schedule',
      config: { enabled: true, interval_hours: 6, self_repair_before: true },
    }
    expect(msg.type).toBe('schedule')
  })

  it('WorkerToServer state includes active array (not current)', () => {
    const msg: WorkerToServer = {
      type: 'state',
      queue: [],
      active: [],
      schedule: { enabled: false, self_repair_before: false },
    }
    expect(msg.type).toBe('state')
    expect(msg.active).toEqual([])
  })
})

describe('Target schedule override (Phase 8)', () => {
  it('accepts optional schedule override', () => {
    const target: Target = {
      name: 'scheduled-plugin',
      type: 'plugin',
      monitors: [],
      watch: [],
      respond: {},
      indicators: [],
      north_star: 'Fast builds',
      schedule: { interval_hours: 6 },
    }
    expect(target.schedule?.interval_hours).toBe(6)
  })

  it('accepts target without schedule field', () => {
    const target: Target = {
      name: 'unscheduled-plugin',
      type: 'plugin',
      monitors: [],
      watch: [],
      respond: {},
      indicators: [],
      north_star: 'Fast builds',
    }
    expect(target.schedule).toBeUndefined()
  })
})

describe('RunSummaryAction.linear_url (Phase 8)', () => {
  it('RunSummaryAction accepts optional linear_url', () => {
    const action: RunSummaryAction = {
      signal_id: 'SIG-001',
      type: 'code-fix',
      summary: 'Fix test',
      linear_url: 'https://linear.app/team/issue/TEAM-123',
      indicator: 'IND-01',
      assessment: { closer_to_north_star: 'yes', confidence: 'high', reasoning: 'test' },
    }
    expect(action.linear_url).toBe('https://linear.app/team/issue/TEAM-123')
  })

  it('RunSummaryAction works without linear_url', () => {
    const action: RunSummaryAction = {
      signal_id: 'SIG-002',
      type: 'proposal',
      summary: 'Proposal without linear',
      indicator: 'IND-02',
      assessment: { closer_to_north_star: 'uncertain', confidence: 'medium', reasoning: 'maybe' },
    }
    expect(action.linear_url).toBeUndefined()
  })
})
