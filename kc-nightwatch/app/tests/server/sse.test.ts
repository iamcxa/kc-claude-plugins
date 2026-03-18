import { describe, it, expect, beforeEach } from 'bun:test'
import { subscribeToRun, fanOutLogEvent, closeRunSubscribers } from '../../server/ipc.ts'
import type { ParsedLogEvent } from '../../shared/types.ts'

describe('SSE fan-out', () => {
  // Reset subscribers between tests by closing any existing subscriptions
  beforeEach(() => {
    closeRunSubscribers('test-run-1')
    closeRunSubscribers('test-run-2')
  })

  it('fanOutLogEvent delivers event to subscriber', async () => {
    const received: string[] = []
    const controller = new AbortController()

    const writer = {
      writeSSE: async (data: { data: string; event?: string }) => {
        received.push(data.data)
      },
    }

    subscribeToRun('test-run-1', writer, controller.signal)

    const event: ParsedLogEvent = { type: 'assistant', content: 'Phase 1', raw: '{}' }
    fanOutLogEvent('test-run-1', event)

    // Allow async write to propagate
    await Bun.sleep(1)
    expect(received).toHaveLength(1)
    expect(JSON.parse(received[0])).toMatchObject({ type: 'assistant' })

    controller.abort()
  })

  it('fanOutLogEvent is no-op when no subscribers', () => {
    // Should not throw
    const event: ParsedLogEvent = { type: 'assistant', raw: '{}' }
    expect(() => fanOutLogEvent('nonexistent-run', event)).not.toThrow()
  })

  it('closeRunSubscribers prevents further delivery', async () => {
    const received: string[] = []
    const controller = new AbortController()

    const writer = {
      writeSSE: async (data: { data: string; event?: string }) => {
        received.push(data.data)
      },
    }

    subscribeToRun('test-run-2', writer, controller.signal)

    // Deliver once before close
    const event: ParsedLogEvent = { type: 'assistant', raw: '{}' }
    fanOutLogEvent('test-run-2', event)
    await Bun.sleep(1)
    expect(received).toHaveLength(1)

    // Close subscribers
    closeRunSubscribers('test-run-2')

    // Deliver again — should not receive
    fanOutLogEvent('test-run-2', event)
    await Bun.sleep(1)
    expect(received).toHaveLength(1) // still 1, not 2

    controller.abort()
  })

  it('AbortSignal removes subscriber', async () => {
    const received: string[] = []
    const controller = new AbortController()

    const writer = {
      writeSSE: async (data: { data: string; event?: string }) => {
        received.push(data.data)
      },
    }

    subscribeToRun('test-run-1', writer, controller.signal)

    // Abort the connection
    controller.abort()
    await Bun.sleep(1)

    // Delivery after abort should not reach the writer
    const event: ParsedLogEvent = { type: 'assistant', raw: '{}' }
    fanOutLogEvent('test-run-1', event)
    await Bun.sleep(1)
    expect(received).toHaveLength(0)
  })

  it('subscribeToRun returns cleanup function', () => {
    const controller = new AbortController()
    const writer = { writeSSE: async () => {} }

    const cleanup = subscribeToRun('test-run-1', writer, controller.signal)
    expect(typeof cleanup).toBe('function')

    // Calling cleanup removes the subscriber
    cleanup()
    controller.abort()
  })
})
