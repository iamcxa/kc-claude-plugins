import { describe, it, expect, beforeEach } from 'bun:test'
import { subscribeGlobal, broadcastGlobal, handleWorkerMessage } from '../../server/ipc.ts'

describe('Global SSE broadcast', () => {
  it('subscribeGlobal adds writer to global set', () => {
    const events: Array<{ data: string; event?: string }> = []
    const writer = { writeSSE: async (d: { data: string; event?: string }) => { events.push(d) } }
    const ac = new AbortController()
    const unsub = subscribeGlobal(writer, ac.signal)
    broadcastGlobal('test-event', { foo: 'bar' })
    expect(events.length).toBe(1)
    expect(events[0].event).toBe('test-event')
    expect(JSON.parse(events[0].data)).toEqual({ foo: 'bar' })
    unsub()
  })

  it('abort signal cleans up subscriber', () => {
    const events: Array<{ data: string; event?: string }> = []
    const writer = { writeSSE: async (d: { data: string; event?: string }) => { events.push(d) } }
    const ac = new AbortController()
    subscribeGlobal(writer, ac.signal)
    ac.abort()
    broadcastGlobal('test-event', { ignored: true })
    expect(events.length).toBe(0)
  })

  it('run:completed broadcasts brief-ready via global SSE', () => {
    const events: Array<{ data: string; event?: string }> = []
    const writer = { writeSSE: async (d: { data: string; event?: string }) => { events.push(d) } }
    const ac = new AbortController()
    subscribeGlobal(writer, ac.signal)
    handleWorkerMessage({
      type: 'run:completed',
      run_id: 'test-123',
      summary: { targets_active: 1, targets_skipped: 0, total_signals: 2, total_actions: 1, errors: 0, per_target: {} }
    })
    const briefEvent = events.find(e => e.event === 'brief-ready')
    expect(briefEvent).toBeDefined()
    const data = JSON.parse(briefEvent!.data)
    expect(data.run_id).toBe('test-123')
    expect(data.summary).toBeDefined()
    ac.abort()
  })
})
