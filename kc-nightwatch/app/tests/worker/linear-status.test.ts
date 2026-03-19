import { describe, it, expect, beforeEach, afterEach, mock } from 'bun:test'

// ============================================================
// Tests for checkLinearStatus in feedback-collector.ts
// ============================================================

describe('checkLinearStatus', () => {
  const originalEnv = process.env.LINEAR_API_KEY

  afterEach(() => {
    if (originalEnv === undefined) {
      delete process.env.LINEAR_API_KEY
    } else {
      process.env.LINEAR_API_KEY = originalEnv
    }
  })

  it('returns null when LINEAR_API_KEY is not set', async () => {
    delete process.env.LINEAR_API_KEY
    const { checkLinearStatus } = await import('../../worker/feedback-collector.ts')
    const result = await checkLinearStatus('https://linear.app/team/issue/SC-123')
    expect(result).toBeNull()
  })

  it('returns null for invalid URL format', async () => {
    process.env.LINEAR_API_KEY = 'test-key'
    const { checkLinearStatus } = await import('../../worker/feedback-collector.ts')
    const result = await checkLinearStatus('https://github.com/not-linear')
    expect(result).toBeNull()
  })

  it('returns null for Linear URL without valid issue ID', async () => {
    process.env.LINEAR_API_KEY = 'test-key'
    const { checkLinearStatus } = await import('../../worker/feedback-collector.ts')
    const result = await checkLinearStatus('https://linear.app/team/project/ABC')
    expect(result).toBeNull()
  })

  it('returns accepted when state.type is completed', async () => {
    process.env.LINEAR_API_KEY = 'test-key'

    const mockFetch = mock(async (_url: string, _opts: unknown) => ({
      json: async () => ({ data: { issue: { state: { type: 'completed' } } } }),
    }))
    const originalFetch = globalThis.fetch
    globalThis.fetch = mockFetch as unknown as typeof fetch

    try {
      // Re-import to pick up env var (module caches, but function reads env at call time)
      const { checkLinearStatus } = await import('../../worker/feedback-collector.ts')
      const result = await checkLinearStatus('https://linear.app/myteam/issue/SC-123')
      expect(result).toBe('accepted')
      expect(mockFetch).toHaveBeenCalledTimes(1)
      const [url, opts] = mockFetch.mock.calls[0]! as [string, { method: string; headers: Record<string, string>; body: string }]
      expect(url).toBe('https://api.linear.app/graphql')
      expect(opts.method).toBe('POST')
      expect(opts.headers['Authorization']).toBe('test-key')
      expect(opts.headers['Authorization']).not.toContain('Bearer')
      const body = JSON.parse(opts.body) as { query: string }
      expect(body.query).toContain('SC-123')
    } finally {
      globalThis.fetch = originalFetch
    }
  })

  it('returns rejected when state.type is cancelled', async () => {
    process.env.LINEAR_API_KEY = 'test-key'

    const mockFetch = mock(async (_url: string, _opts: unknown) => ({
      json: async () => ({ data: { issue: { state: { type: 'cancelled' } } } }),
    }))
    const originalFetch = globalThis.fetch
    globalThis.fetch = mockFetch as unknown as typeof fetch

    try {
      const { checkLinearStatus } = await import('../../worker/feedback-collector.ts')
      const result = await checkLinearStatus('https://linear.app/myteam/issue/SC-456')
      expect(result).toBe('rejected')
    } finally {
      globalThis.fetch = originalFetch
    }
  })

  it('returns null when state.type is started (in progress)', async () => {
    process.env.LINEAR_API_KEY = 'test-key'

    const mockFetch = mock(async (_url: string, _opts: unknown) => ({
      json: async () => ({ data: { issue: { state: { type: 'started' } } } }),
    }))
    const originalFetch = globalThis.fetch
    globalThis.fetch = mockFetch as unknown as typeof fetch

    try {
      const { checkLinearStatus } = await import('../../worker/feedback-collector.ts')
      const result = await checkLinearStatus('https://linear.app/myteam/issue/SC-789')
      expect(result).toBeNull()
    } finally {
      globalThis.fetch = originalFetch
    }
  })

  it('returns null when fetch throws (network error)', async () => {
    process.env.LINEAR_API_KEY = 'test-key'

    const mockFetch = mock(async (_url: string, _opts: unknown) => {
      throw new Error('Network error')
    })
    const originalFetch = globalThis.fetch
    globalThis.fetch = mockFetch as unknown as typeof fetch

    try {
      const { checkLinearStatus } = await import('../../worker/feedback-collector.ts')
      const result = await checkLinearStatus('https://linear.app/myteam/issue/SC-111')
      expect(result).toBeNull()
    } finally {
      globalThis.fetch = originalFetch
    }
  })
})
