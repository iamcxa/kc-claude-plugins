import { describe, it, expect } from 'bun:test'
import { AppConfigSchema } from '../../shared/types.ts'

describe('AppConfigSchema', () => {
  const base = {
    host: '127.0.0.1',
    port: 3200,
    schedule: { enabled: false, self_repair_before: true },
    max_concurrent_runs: 1 as const,
    plugins_dir: '/tmp',
  }

  it('accepts valid config', () => {
    expect(() => AppConfigSchema.parse(base)).not.toThrow()
  })

  it('rejects max_concurrent_runs != 1', () => {
    expect(() => AppConfigSchema.parse({ ...base, max_concurrent_runs: 2 })).toThrow()
  })

  it('accepts optional auth_token', () => {
    const result = AppConfigSchema.parse({ ...base, auth_token: 'abc123' })
    expect(result.auth_token).toBe('abc123')
  })

  it('defaults host to 127.0.0.1 when omitted', () => {
    const result = AppConfigSchema.parse({ ...base, host: undefined })
    expect(result.host).toBe('127.0.0.1')
  })
})
