import { Hono } from 'hono'
import { streamSSE } from 'hono/streaming'
import * as chatManager from '../services/chat-manager.ts'
import type { RunSummary } from '../../shared/types.ts'

export const chatRoutes = new Hono()

/** Extract display-friendly text from Anthropic message content (string or ContentBlock[]) */
export function extractDisplayContent(content: unknown): string | null {
  if (typeof content === 'string') return content

  if (Array.isArray(content)) {
    const textParts: string[] = []
    let isToolResult = false
    for (const block of content) {
      if (block.type === 'text' && block.text) {
        textParts.push(block.text)
      } else if (block.type === 'tool_result') {
        isToolResult = true
      }
    }
    // Skip tool_result messages entirely — they're internal API plumbing
    if (isToolResult) return null
    return textParts.join('\n') || null
  }

  return String(content)
}

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

    // Send current message history on connect (normalize content blocks for display)
    const session = chatManager.getOrCreateSession(target)
    for (const msg of session.messages) {
      const displayContent = extractDisplayContent(msg.content)
      if (displayContent === null) continue // Skip tool_result and empty messages
      void stream.writeSSE({
        data: JSON.stringify({ type: 'history', role: msg.role, content: displayContent }),
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
