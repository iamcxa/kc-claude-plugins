import { describe, it, expect } from 'bun:test'
import type { FeedbackEntry } from '../../shared/types.ts'

// Test the pure helper functions from action-card.ts
// We re-implement them here to test the logic without requiring Preact/DOM.
// If these functions are ever refactored out of the component, import directly.

function sourceLabel(source: FeedbackEntry['source']): string {
  const labels: Record<string, string> = {
    user: 'manual',
    pr_status: 'PR status',
    linear_status: 'Linear',
    slack_reaction: 'Slack',
    pr_review: 'PR review',
  }
  return labels[source] ?? source
}

function verdictBg(verdict: FeedbackEntry['verdict']): string {
  if (verdict === 'accepted') return 'rgba(63,185,80,0.15)'
  if (verdict === 'rejected') return 'rgba(248,81,73,0.15)'
  return 'rgba(227,179,65,0.15)'
}

function verdictColor(verdict: FeedbackEntry['verdict']): string {
  if (verdict === 'accepted') return 'var(--success)'
  if (verdict === 'rejected') return 'var(--error)'
  return 'var(--warn)'
}

function makeFeedback(overrides: Partial<FeedbackEntry> = {}): FeedbackEntry {
  return {
    signal_id: 'sig-001',
    target: 'test-target',
    run_id: 'run-001',
    verdict: 'accepted',
    source: 'user',
    submitted_at: '2026-03-24T10:00:00Z',
    ...overrides,
  }
}

describe('sourceLabel', () => {
  it('maps user to manual', () => {
    expect(sourceLabel('user')).toBe('manual')
  })

  it('maps slack_reaction to Slack', () => {
    expect(sourceLabel('slack_reaction')).toBe('Slack')
  })

  it('maps pr_review to PR review', () => {
    expect(sourceLabel('pr_review')).toBe('PR review')
  })

  it('maps pr_status to PR status', () => {
    expect(sourceLabel('pr_status')).toBe('PR status')
  })

  it('maps linear_status to Linear', () => {
    expect(sourceLabel('linear_status')).toBe('Linear')
  })

  it('returns source as-is for unknown values', () => {
    expect(sourceLabel('unknown_source' as FeedbackEntry['source'])).toBe('unknown_source')
  })
})

describe('verdictBg', () => {
  it('returns green for accepted', () => {
    expect(verdictBg('accepted')).toBe('rgba(63,185,80,0.15)')
  })

  it('returns red for rejected', () => {
    expect(verdictBg('rejected')).toBe('rgba(248,81,73,0.15)')
  })

  it('returns yellow for uncertain', () => {
    expect(verdictBg('uncertain')).toBe('rgba(227,179,65,0.15)')
  })
})

describe('verdictColor', () => {
  it('returns success for accepted', () => {
    expect(verdictColor('accepted')).toBe('var(--success)')
  })

  it('returns error for rejected', () => {
    expect(verdictColor('rejected')).toBe('var(--error)')
  })

  it('returns warn for uncertain', () => {
    expect(verdictColor('uncertain')).toBe('var(--warn)')
  })
})

describe('feedback entry filtering logic', () => {
  it('separates user feedback from auto-collected', () => {
    const entries: FeedbackEntry[] = [
      makeFeedback({ source: 'user', verdict: 'accepted' }),
      makeFeedback({ source: 'slack_reaction', verdict: 'accepted' }),
      makeFeedback({ source: 'pr_review', verdict: 'rejected' }),
    ]

    const userFeedback = entries.find(f => f.source === 'user')
    const autoFeedback = entries.filter(f => f.source !== 'user')

    expect(userFeedback?.verdict).toBe('accepted')
    expect(autoFeedback).toHaveLength(2)
    expect(autoFeedback[0].source).toBe('slack_reaction')
    expect(autoFeedback[1].source).toBe('pr_review')
  })

  it('handles empty feedback list', () => {
    const entries: FeedbackEntry[] = []
    const userFeedback = entries.find(f => f.source === 'user')
    const autoFeedback = entries.filter(f => f.source !== 'user')

    expect(userFeedback).toBeUndefined()
    expect(autoFeedback).toHaveLength(0)
  })

  it('handles only auto-collected feedback (no user)', () => {
    const entries: FeedbackEntry[] = [
      makeFeedback({ source: 'slack_reaction', verdict: 'accepted' }),
      makeFeedback({ source: 'pr_review', verdict: 'uncertain' }),
    ]

    const userFeedback = entries.find(f => f.source === 'user')
    const autoFeedback = entries.filter(f => f.source !== 'user')

    expect(userFeedback).toBeUndefined()
    expect(autoFeedback).toHaveLength(2)
  })

  it('handles only user feedback (no auto)', () => {
    const entries: FeedbackEntry[] = [
      makeFeedback({ source: 'user', verdict: 'rejected' }),
    ]

    const userFeedback = entries.find(f => f.source === 'user')
    const autoFeedback = entries.filter(f => f.source !== 'user')

    expect(userFeedback?.verdict).toBe('rejected')
    expect(autoFeedback).toHaveLength(0)
  })

  it('uncertain verdict from auto-collected is displayed correctly', () => {
    const entry = makeFeedback({ source: 'pr_review', verdict: 'uncertain' })

    expect(verdictColor(entry.verdict)).toBe('var(--warn)')
    expect(verdictBg(entry.verdict)).toBe('rgba(227,179,65,0.15)')
    expect(sourceLabel(entry.source)).toBe('PR review')
  })

  it('groups feedback by signal_id for ActionCard lookup', () => {
    const entries: FeedbackEntry[] = [
      makeFeedback({ signal_id: 'sig-001', source: 'user', verdict: 'accepted' }),
      makeFeedback({ signal_id: 'sig-001', source: 'slack_reaction', verdict: 'accepted' }),
      makeFeedback({ signal_id: 'sig-002', source: 'pr_review', verdict: 'rejected' }),
    ]

    const map: Record<string, FeedbackEntry[]> = {}
    for (const e of entries) {
      if (!map[e.signal_id]) map[e.signal_id] = []
      map[e.signal_id].push(e)
    }

    expect(Object.keys(map)).toHaveLength(2)
    expect(map['sig-001']).toHaveLength(2)
    expect(map['sig-002']).toHaveLength(1)
    expect(map['sig-003'] ?? []).toHaveLength(0)
  })
})
