import { html } from 'htm/preact'
import { useState, useEffect, useRef } from 'preact/hooks'
import { api } from '../lib/api.ts'
import type { ChatMessage } from '../../shared/types.ts'

interface Props {
  targetName: string | null
}

export function ChatPanel({ targetName }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const [sessionVersion, setSessionVersion] = useState(0)
  const esRef = useRef<EventSource | null>(null)
  const messagesEndRef = useRef<HTMLDivElement | null>(null)
  const streamingTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Connect SSE when target or session changes
  useEffect(() => {
    if (!targetName) return

    // Cleanup old connection
    if (esRef.current) {
      esRef.current.close()
      esRef.current = null
    }
    if (streamingTimeoutRef.current) clearTimeout(streamingTimeoutRef.current)

    setMessages([])
    setStreaming(false)
    setSending(false)

    const es = new EventSource(`/api/chat/${encodeURIComponent(targetName)}/stream`)
    esRef.current = es

    // Clear messages only on REconnect — useEffect already cleared on initial connect.
    // First open is harmless (messages already empty), but a race exists if user
    // sends a message before the connection establishes.
    let connected = false
    es.addEventListener('open', () => {
      if (connected) {
        // Reconnect: clear stale client messages, server resends full history
        setMessages([])
      }
      connected = true
    })

    es.addEventListener('chat', (e: MessageEvent) => {
      const data = JSON.parse(e.data)
      if (data.type === 'history') {
        setMessages(prev => [...prev, {
          id: crypto.randomUUID(),
          role: data.role,
          content: data.content,
          timestamp: new Date().toISOString(),
        }])
      } else if (data.type === 'start') {
        setStreaming(true)
        if (streamingTimeoutRef.current) clearTimeout(streamingTimeoutRef.current)
        streamingTimeoutRef.current = setTimeout(() => {
          setStreaming(false)
          setSending(false)
        }, 120_000)
        setMessages(prev => [...prev, {
          id: data.id,
          role: 'assistant',
          content: '',
          timestamp: new Date().toISOString(),
          streaming: true,
        }])
      } else if (data.type === 'delta') {
        setMessages(prev => {
          const updated = [...prev]
          const last = updated[updated.length - 1]
          if (last?.streaming) {
            updated[updated.length - 1] = { ...last, content: last.content + data.content }
          }
          return updated
        })
      } else if (data.type === 'end') {
        if (streamingTimeoutRef.current) clearTimeout(streamingTimeoutRef.current)
        setStreaming(false)
        setSending(false)
        setMessages(prev => {
          const updated = [...prev]
          const last = updated[updated.length - 1]
          if (last?.streaming) {
            updated[updated.length - 1] = { ...last, content: data.content, streaming: false }
          }
          return updated
        })
      } else if (data.type === 'error') {
        if (streamingTimeoutRef.current) clearTimeout(streamingTimeoutRef.current)
        setStreaming(false)
        setSending(false)
        setMessages(prev => {
          const updated = [...prev]
          const last = updated[updated.length - 1]
          if (last?.streaming) updated.pop()
          return [...updated, {
            id: crypto.randomUUID(),
            role: 'assistant' as const,
            content: `Error: ${data.error ?? 'Connection lost'}`,
            timestamp: new Date().toISOString(),
          }]
        })
      }
    })

    return () => {
      es.close()
      esRef.current = null
      if (streamingTimeoutRef.current) clearTimeout(streamingTimeoutRef.current)
    }
  }, [targetName, sessionVersion])

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend() {
    if (!input.trim() || !targetName || sending || streaming) return
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setSending(true)
    try {
      await api.sendChatMessage(targetName, userMsg.content)
    } finally {
      setSending(false)
    }
  }

  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
      e.preventDefault()
      void handleSend()
    }
  }

  async function handleReset() {
    if (!targetName) return
    try {
      await api.resetChatSession(targetName)
    } catch {
      // Reset frontend state even if server call fails
    }
    setSessionVersion(v => v + 1)
  }

  if (!targetName) {
    return html`
      <div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--muted);font-size:13px;padding:16px;text-align:center;">
        Select a target to start chatting with NW-Claude
      </div>
    `
  }

  const emptyState = messages.length === 0

  return html`
    <div style="display:flex;flex-direction:column;height:100%;">
      <!-- Header -->
      <div style="padding:8px 12px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:8px;flex-shrink:0;">
        <span style="font-weight:600;font-size:13px;flex:1;">NW-Claude</span>
        <span style="font-size:11px;color:var(--muted);">${targetName}</span>
        <button
          onClick=${handleReset}
          aria-label="Reset conversation"
          style="padding:2px 6px;font-size:11px;"
        >Reset</button>
      </div>

      <!-- Messages -->
      <div style="flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:6px;">
        ${emptyState && html`
          <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:6px;">
            <div style="font-size:14px;font-weight:600;color:var(--text);">NW-Claude</div>
            <p style="margin:0;color:var(--muted);text-align:center;font-size:12px;max-width:280px;line-height:1.4;">
              Ask about run results, config changes, or improvement signals.
            </p>
          </div>
        `}
        ${messages.map(msg => html`
          <div key=${msg.id} style="
            padding:6px 10px;border-radius:6px;font-size:13px;line-height:1.4;
            ${msg.role === 'user'
              ? `background:var(--chat-user-bg);margin-left:32px;`
              : `background:var(--chat-nw-bg);border:1px solid var(--border);margin-right:32px;`
            }
          ">
            <div style="font-size:10px;color:var(--muted);margin-bottom:2px;">${msg.role === 'user' ? 'You' : 'NW-Claude'}</div>
            <div style="white-space:pre-wrap;">${msg.content}${msg.streaming ? '\u2588' : ''}</div>
          </div>
        `)}
        <div ref=${messagesEndRef} />
      </div>

      <!-- Input -->
      <div style="padding:8px 12px;border-top:1px solid var(--border);display:flex;gap:6px;flex-shrink:0;">
        <textarea
          value=${input}
          onInput=${(e: Event) => setInput((e.target as HTMLTextAreaElement).value)}
          onKeyDown=${handleKeyDown}
          placeholder="Ask NW-Claude..."
          rows="1"
          style="flex:1;resize:none;min-height:32px;max-height:80px;font-family:inherit;font-size:13px;"
          disabled=${sending || streaming}
        />
        <button
          onClick=${handleSend}
          disabled=${!input.trim() || sending || streaming}
          style="background:var(--btn-primary);color:#fff;border-color:var(--btn-primary);align-self:flex-end;font-size:12px;padding:4px 10px;"
        >Send</button>
      </div>
    </div>
  `
}
