import { html } from 'htm/preact'
import { useState, useEffect, useRef } from 'preact/hooks'
import { api } from '../lib/api.ts'
import type { ChatMessage } from '../../shared/types.ts'

interface Props {
  isOpen: boolean
  onClose: () => void
  targetName: string | null
}

export function ChatDrawer({ isOpen, onClose, targetName }: Props) {
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

    let connected = false
    es.addEventListener('open', () => {
      if (connected) setMessages([])
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
        // Safety: reset streaming if 'end' never arrives (2 min for multi-round tool_use)
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
        // Show error to user so they know what went wrong
        setMessages(prev => {
          const updated = [...prev]
          // Remove the empty streaming placeholder if present
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

  // Keyboard handler
  useEffect(() => {
    if (!isOpen) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

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
      // Always reset sending after POST completes — streaming flag takes over as guard
      setSending(false)
    }
  }

  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
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
    setSessionVersion(v => v + 1) // Triggers useEffect to reconnect SSE to fresh session
  }

  const emptyState = messages.length === 0

  return html`
    <div
      style="position:fixed;inset:0;z-index:200;pointer-events:${isOpen ? 'all' : 'none'};"
    >
      <!-- Backdrop -->
      <div
        style="position:absolute;inset:0;background:rgba(0,0,0,${isOpen ? '0.3' : '0'});transition:background 200ms;"
        onClick=${onClose}
      />
      <!-- Drawer panel -->
      <div
        role="dialog"
        aria-label="NW-Claude chat"
        aria-modal="false"
        onClick=${(e: Event) => e.stopPropagation()}
        style="
          position:absolute;right:0;top:0;bottom:0;width:400px;
          background:var(--panel);border-left:1px solid var(--border);
          transform:translateX(${isOpen ? '0' : '100%'});
          transition:transform 200ms ease-out;
          display:flex;flex-direction:column;
        "
      >
        <!-- Header -->
        <div style="padding:12px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:8px;flex-shrink:0;">
          <span style="font-weight:600;flex:1;">NW-Claude</span>
          ${targetName && html`<span style="font-size:12px;color:var(--muted);">${targetName}</span>`}
          <button
            onClick=${handleReset}
            aria-label="Reset conversation"
            style="padding:3px 8px;font-size:12px;"
          >Reset</button>
          <button
            onClick=${onClose}
            aria-label="Close chat"
            style="padding:3px 8px;font-size:12px;"
          >X</button>
        </div>

        <!-- Messages -->
        <div style="flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:8px;">
          ${emptyState && html`
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:8px;">
              <div style="font-size:16px;font-weight:600;color:var(--text);">NW-Claude</div>
              <p style="margin:0;color:var(--muted);text-align:center;font-size:14px;max-width:320px;line-height:1.5;">
                Ask about run results, config changes, or improvement signals. Runs auto-brief here when they complete.
              </p>
            </div>
          `}
          ${messages.map(msg => html`
            <div key=${msg.id} style="
              padding:8px 12px;border-radius:8px;font-size:14px;line-height:1.5;
              ${msg.role === 'user'
                ? `background:var(--chat-user-bg);margin-left:48px;`
                : `background:var(--chat-nw-bg);border:1px solid var(--border);margin-right:48px;`
              }
            ">
              <div style="font-size:11px;color:var(--muted);margin-bottom:4px;">${msg.role === 'user' ? 'You' : 'NW-Claude'}</div>
              <div style="white-space:pre-wrap;">${msg.content}${msg.streaming ? '\u2588' : ''}</div>
            </div>
          `)}
          <div ref=${messagesEndRef} />
        </div>

        <!-- Input -->
        <div style="padding:12px 16px;border-top:1px solid var(--border);display:flex;gap:8px;flex-shrink:0;">
          <textarea
            value=${input}
            onInput=${(e: Event) => setInput((e.target as HTMLTextAreaElement).value)}
            onKeyDown=${handleKeyDown}
            placeholder="Ask NW-Claude..."
            rows="1"
            style="flex:1;resize:none;min-height:36px;max-height:96px;font-family:inherit;font-size:14px;"
            disabled=${sending || streaming}
          />
          <button
            onClick=${handleSend}
            disabled=${!input.trim() || sending || streaming}
            style="background:var(--btn-primary);color:#fff;border-color:var(--btn-primary);align-self:flex-end;"
          >Send</button>
        </div>
      </div>
    </div>
  `
}
