import { describe, it, expect } from 'bun:test'
import { parse } from 'yaml'
import type { RunSummary, PerTargetSummary } from '../../shared/types.ts'

describe('executor summary.yaml parsing', () => {
  const sampleYaml = `
targets_active: 2
targets_skipped: 0
total_signals: 5
total_actions: 3
errors: 0
per_target:
  my-plugin:
    monitors:
      github-issues:
        status: ok
        signals: 3
    pipeline:
      found: 5
      after_dedup: 4
      after_confidence_filter: 3
      after_cooldown: 3
      classified:
        code-fix: 2
        proposal: 1
      executed:
        code-fix: 2
        proposal: 1
    actions:
      - signal_id: "lint-warnings:001"
        type: code-fix
        summary: "Fixed 12 lint warnings in auth module"
        pr_url: "https://github.com/owner/repo/pull/47"
        branch: "kc-nightwatch/2026-03-18-my-plugin-fixes"
        indicator: code-quality
        assessment:
          closer_to_north_star: "yes"
          confidence: high
          reasoning: "Lint warnings directly degrade code quality metric"
    indicator_baseline:
      code-quality:
        value: 85
        measurement: "percent"
        previous_value: 82
        trend: improving
      open-issues:
        value: 12
        measurement: "count"
        trend: stable
    pre_assessment: "3 high-priority signals targeting code quality. Focusing on lint fixes and error handling."
    post_assessment: "2 of 3 actions succeeded. PR #47 created for lint fixes. Code quality improved."
`

  it('parses per_target from summary.yaml', () => {
    const data = parse(sampleYaml) as RunSummary
    expect(data.targets_active).toBe(2)
    expect(data.total_signals).toBe(5)
    expect(data.per_target['my-plugin']).toBeDefined()
  })

  it('parses indicator_baseline correctly', () => {
    const data = parse(sampleYaml) as RunSummary
    const target = data.per_target['my-plugin'] as PerTargetSummary
    expect(target.indicator_baseline['code-quality']).toBeDefined()
    expect(target.indicator_baseline['code-quality'].value).toBe(85)
    expect(target.indicator_baseline['code-quality'].trend).toBe('improving')
    expect(target.indicator_baseline['code-quality'].previous_value).toBe(82)
  })

  it('parses pre/post assessment as strings', () => {
    const data = parse(sampleYaml) as RunSummary
    const target = data.per_target['my-plugin'] as PerTargetSummary
    expect(typeof target.pre_assessment).toBe('string')
    expect(typeof target.post_assessment).toBe('string')
    expect(target.pre_assessment).toContain('high-priority')
    expect(target.post_assessment).toContain('PR #47')
  })

  it('parses actions with assessment', () => {
    const data = parse(sampleYaml) as RunSummary
    const target = data.per_target['my-plugin'] as PerTargetSummary
    expect(target.actions.length).toBe(1)
    expect(target.actions[0].assessment.closer_to_north_star).toBe('yes')
    expect(target.actions[0].assessment.confidence).toBe('high')
    expect(target.actions[0].assessment.reasoning).toContain('code quality')
  })

  it('handles missing per_target gracefully', () => {
    const minimal = parse('targets_active: 0\ntargets_skipped: 0') as Record<string, unknown>
    const summary: RunSummary = {
      targets_active: (minimal.targets_active as number) ?? 0,
      targets_skipped: (minimal.targets_skipped as number) ?? 0,
      total_signals: 0,
      total_actions: 0,
      errors: 0,
      per_target: (minimal.per_target as Record<string, PerTargetSummary>) ?? {},
    }
    expect(Object.keys(summary.per_target).length).toBe(0)
  })
})
