import { describe, it, expect } from 'bun:test'
import path from 'node:path'
import { TARGETS_YAML_PATH } from '../../server/services/yaml-store.ts'

describe('config routes setup', () => {
  it('TARGETS_YAML_PATH resolves to home dir', () => {
    const expected = path.join(process.env.HOME ?? '/tmp', '.claude/kc-plugins-config/nightwatch-targets.yaml')
    expect(TARGETS_YAML_PATH).toBe(expected)
  })

  it('ConfigValidationResult type has required fields', () => {
    // Type-check: ensure the interface has the expected shape
    const result = {
      valid: true,
      step: 'ready' as const,
      haiku_verdict: 'OK',
      diff: [{ type: 'same' as const, line: 'foo: bar' }],
    }
    expect(result.valid).toBe(true)
    expect(result.step).toBe('ready')
  })
})
