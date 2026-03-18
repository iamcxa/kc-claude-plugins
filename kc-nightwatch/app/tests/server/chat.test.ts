import { describe, it, expect, beforeEach } from 'bun:test'
import {
  getOrCreateSession,
  killSession,
  killAllSessions,
  listSessions,
  subscribeToTarget,
  setBriefContext,
} from '../../server/services/chat-manager.ts'

describe('chat-manager', () => {
  beforeEach(() => {
    killAllSessions()
  })

  it('getOrCreateSession creates new session for target', () => {
    const session = getOrCreateSession('my-plugin')
    expect(session.targetName).toBe('my-plugin')
    expect(session.messages).toEqual([])
    expect(session.subscribers.size).toBe(0)
  })

  it('getOrCreateSession returns existing session', () => {
    const s1 = getOrCreateSession('my-plugin')
    s1.messages.push({ role: 'user', content: 'hello' })
    const s2 = getOrCreateSession('my-plugin')
    expect(s2.messages.length).toBe(1)
    expect(s2.messages[0].content).toBe('hello')
  })

  it('killSession removes session', () => {
    getOrCreateSession('my-plugin')
    expect(listSessions()).toContain('my-plugin')
    killSession('my-plugin')
    expect(listSessions()).not.toContain('my-plugin')
  })

  it('subscribeToTarget adds writer', () => {
    const events: unknown[] = []
    const writer = { writeSSE: async (d: unknown) => { events.push(d) } }
    const ac = new AbortController()
    subscribeToTarget('my-plugin', writer, ac.signal)
    const session = getOrCreateSession('my-plugin')
    expect(session.subscribers.size).toBe(1)
    ac.abort()
    expect(session.subscribers.size).toBe(0)
  })

  it('setBriefContext stores summary in session', () => {
    const summary = { targets_active: 1, targets_skipped: 0, total_signals: 3, total_actions: 1, errors: 0, per_target: {} }
    setBriefContext('my-plugin', summary as any)
    const session = getOrCreateSession('my-plugin')
    expect(session.briefContext).toBeDefined()
    expect(session.briefContext!.total_signals).toBe(3)
  })

  it('killAllSessions clears all sessions', () => {
    getOrCreateSession('plugin-a')
    getOrCreateSession('plugin-b')
    expect(listSessions().length).toBe(2)
    killAllSessions()
    expect(listSessions().length).toBe(0)
  })
})
