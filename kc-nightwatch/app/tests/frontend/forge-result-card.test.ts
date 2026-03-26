import { describe, it, expect } from 'bun:test'

// Test the pure helper functions from forge-result-card.ts
// We re-implement them here to test the logic without requiring Preact/DOM.
// If these functions are ever refactored out of the component, import directly.

interface ForgeResultData {
  forge_result: {
    status: 'pass' | 'fail'
    branch: string | null
    details: string
  } | null
  run_date: string | null
  stale: boolean
}

function relativeTime(isoDate: string | null): string {
  if (isoDate === null) return 'never'
  const diffMs = Date.now() - new Date(isoDate).getTime()
  const diffH = Math.floor(diffMs / 3600000)
  if (diffH < 1) return 'just now'
  if (diffH < 24) return `${diffH}h ago`
  const diffD = Math.floor(diffH / 24)
  return `${diffD}d ago`
}

function statusColor(data: ForgeResultData): string {
  if (data.stale === true) return 'var(--muted)'
  if (data.forge_result === null) return 'var(--muted)'
  if (data.forge_result.status === 'pass') return 'var(--success)'
  return 'var(--error)'
}

describe('relativeTime', () => {
  it('returns "never" for null', () => {
    expect(relativeTime(null)).toBe('never')
  })

  it('returns "just now" for < 1h ago', () => {
    const thirtyMinAgo = new Date(Date.now() - 30 * 60 * 1000).toISOString()
    expect(relativeTime(thirtyMinAgo)).toBe('just now')
  })

  it('returns "Xh ago" for hours ago (< 24h)', () => {
    const fiveHoursAgo = new Date(Date.now() - 5 * 3600 * 1000).toISOString()
    expect(relativeTime(fiveHoursAgo)).toBe('5h ago')
  })

  it('returns "Xd ago" for days ago', () => {
    const threeDaysAgo = new Date(Date.now() - 3 * 24 * 3600 * 1000).toISOString()
    expect(relativeTime(threeDaysAgo)).toBe('3d ago')
  })

  it('returns "1h ago" for exactly 1h ago', () => {
    const oneHourAgo = new Date(Date.now() - 3600 * 1000).toISOString()
    expect(relativeTime(oneHourAgo)).toBe('1h ago')
  })

  it('returns "1d ago" for 25h ago', () => {
    const twentyFiveHoursAgo = new Date(Date.now() - 25 * 3600 * 1000).toISOString()
    expect(relativeTime(twentyFiveHoursAgo)).toBe('1d ago')
  })
})

describe('statusColor', () => {
  it('returns muted when stale is true', () => {
    const data: ForgeResultData = {
      forge_result: { status: 'pass', branch: 'main', details: 'ok' },
      run_date: '2026-03-24T00:00:00Z',
      stale: true,
    }
    expect(statusColor(data)).toBe('var(--muted)')
  })

  it('returns muted when forge_result is null', () => {
    const data: ForgeResultData = {
      forge_result: null,
      run_date: null,
      stale: false,
    }
    expect(statusColor(data)).toBe('var(--muted)')
  })

  it('returns success for pass status when not stale', () => {
    const data: ForgeResultData = {
      forge_result: { status: 'pass', branch: 'main', details: 'ok' },
      run_date: '2026-03-26T08:00:00Z',
      stale: false,
    }
    expect(statusColor(data)).toBe('var(--success)')
  })

  it('returns error for fail status when not stale', () => {
    const data: ForgeResultData = {
      forge_result: { status: 'fail', branch: 'main', details: 'failed' },
      run_date: '2026-03-26T08:00:00Z',
      stale: false,
    }
    expect(statusColor(data)).toBe('var(--error)')
  })

  it('stale takes precedence over pass status', () => {
    const data: ForgeResultData = {
      forge_result: { status: 'pass', branch: 'main', details: 'ok' },
      run_date: '2026-03-24T00:00:00Z',
      stale: true,
    }
    expect(statusColor(data)).toBe('var(--muted)')
  })

  it('stale takes precedence over fail status', () => {
    const data: ForgeResultData = {
      forge_result: { status: 'fail', branch: 'main', details: 'failed' },
      run_date: '2026-03-24T00:00:00Z',
      stale: true,
    }
    expect(statusColor(data)).toBe('var(--muted)')
  })
})
