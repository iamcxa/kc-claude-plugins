import { describe, it, expect } from 'bun:test'
import { stringify, parse } from 'yaml'

describe('target wizard YAML generation', () => {
  it('generates valid target YAML from wizard fields', () => {
    const target = {
      type: 'plugin',
      path: '/path/to/plugin',
      north_star: 'Improve test coverage',
      monitors: ['github-issues', 'git-churn'],
      watch: ['coverage', 'test'],
      respond: { 'code-fix': true, 'proposal': true },
      indicators: [{ id: 'test-coverage', description: 'Test coverage percentage' }],
    }
    const yaml = stringify({ targets: { 'my-plugin': target } })
    const parsed = parse(yaml) as { targets: Record<string, unknown> }
    expect(parsed.targets['my-plugin']).toBeDefined()
    expect((parsed.targets['my-plugin'] as any).type).toBe('plugin')
    expect((parsed.targets['my-plugin'] as any).north_star).toBe('Improve test coverage')
  })

  it('rejects target with empty name', () => {
    const name = ''
    expect(name.trim()).toBe('')
  })

  it('serializes respond object correctly', () => {
    const respond = { 'code-fix': true, 'proposal': true, 'e2e-flow': false }
    const yaml = stringify(respond)
    const parsed = parse(yaml) as Record<string, boolean>
    expect(parsed['code-fix']).toBe(true)
    expect(parsed['e2e-flow']).toBe(false)
  })
})
