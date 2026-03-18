import { Hono } from 'hono'
import { streamSSE } from 'hono/streaming'
import * as chatManager from '../services/chat-manager.ts'
import type { RunSummary } from '../../shared/types.ts'

export const chatRoutes = new Hono()

// POST /api/chat/:target/message — send a message, response streams via SSE
chatRoutes.post('/api/chat/:target/message', async (c) => {
  const target = decodeURIComponent(c.req.param('target'))
  const { message } = await c.req.json<{ message: string }>()
  if (!message?.trim()) return c.json({ error: 'message required' }, 400)

  // Fire and forget — response streams via SSE
  void chatManager.sendMessage(target, message)
  return c.json({ ok: true }, 202)
})

// GET /api/chat/:target/stream — SSE for chat response streaming
chatRoutes.get('/api/chat/:target/stream', (c) => {
  const target = decodeURIComponent(c.req.param('target'))
  return streamSSE(c, async (stream) => {
    const unsub = chatManager.subscribeToTarget(target, stream, c.req.raw.signal)

    // Send current message history on connect
    const session = chatManager.getOrCreateSession(target)
    for (const msg of session.messages) {
      void stream.writeSSE({
        data: JSON.stringify({ type: 'history', role: msg.role, content: msg.content }),
        event: 'chat',
      })
    }

    const pingTimer = setInterval(() => {
      void stream.writeSSE({ data: '', event: 'ping' })
    }, 60_000)

    // 10 min timeout for chat stream
    await stream.sleep(10 * 60_000)
    clearInterval(pingTimer)
    unsub()
  })
})

// POST /api/chat/:target/reset — kill session and start fresh
chatRoutes.post('/api/chat/:target/reset', (c) => {
  const target = decodeURIComponent(c.req.param('target'))
  chatManager.killSession(target)
  return c.json({ ok: true })
})

// POST /api/chat/:target/brief — inject run summary as brief context
chatRoutes.post('/api/chat/:target/brief', async (c) => {
  const target = decodeURIComponent(c.req.param('target'))
  const { summary } = await c.req.json<{ summary: unknown }>()
  chatManager.setBriefContext(target, summary as RunSummary)
  // Auto-send a briefing message
  void chatManager.sendMessage(
    target,
    'A run just completed. Please summarize the key findings, actions taken, and any notable changes in indicators.'
  )
  return c.json({ ok: true }, 202)
})
