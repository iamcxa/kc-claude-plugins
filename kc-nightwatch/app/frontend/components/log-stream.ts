import { html } from 'htm/preact'
import { useState, useEffect, useRef } from 'preact/hooks'
import type { ParsedLogEvent } from '../../shared/types.ts'

interface PhaseGroup {
  phase: string
  events: ParsedLogEvent[]
  status: 'running' | 'complete' | 'failed'
}

interface Props {
  runId: string
  initialEvents?: ParsedLogEvent[]
  isCompleted: boolean
}

function appendToPhases(prev: PhaseGroup[], event: ParsedLogEvent): PhaseGroup[] {
  const next = [...prev]
  if (event.is_phase_start && event.phase) {
    // Close previous phase
    if (next.length > 0) {
      next[next.length - 1] = { ...next[next.length - 1], status: 'complete' }
    }
    next.push({ phase: event.phase, events: [], status: 'running' })
  } else if (next.length === 0) {
    next.push({ phase: 'Output', events: [event], status: 'running' })
  } else {
    const last = next[next.length - 1]
    next[next.length - 1] = { ...last, events: [...last.events, event] }
  }
  return next
}

function renderEventLine(event: ParsedLogEvent) {
  if (event.agent_name) {
    return html`<div style="color:var(--muted);font-size:12px;">→ Agent: ${event.agent_name} dispatched</div>`
  }
  if (event.tool_name) {
    return html`<div style="color:var(--muted);font-size:12px;">→ Tool: ${event.tool_name}</div>`
  }
  if (event.content) {
    return html`<div style="color:var(--text);font-size:12px;white-space:pre-wrap;">${event.content}</div>`
  }
  return null
}

export function LogStream({ runId, initialEvents = [], isCompleted }: Props) {
  const [phases, setPhases] = useState<PhaseGroup[]>(() => {
    const initial: PhaseGroup[] = []
    for (const ev of initialEvents) {
      appendToPhases(initial, ev)
    }
    return initial
  })
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set())
  const [autoScroll, setAutoScroll] = useState(true)
  const [showRaw, setShowRaw] = useState(false)
  const [rawLines, setRawLines] = useState<string[]>([])
  const [connected, setConnected] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const esRef = useRef<EventSource | null>(null)

  function connectSSE() {
    if (isCompleted) return
    const es = new EventSource(`/api/runs/${runId}/stream`)
    esRef.current = es
    setConnected(true)

    es.addEventListener('log', (e: MessageEvent) => {
      const event = JSON.parse(e.data) as ParsedLogEvent
      setPhases(prev => appendToPhases(prev, event))
      setRawLines(prev => [...prev, event.raw])
    })

    es.addEventListener('ping', () => {})

    es.onerror = () => {
      setConnected(false)
      es.close()
      esRef.current = null
    }
  }

  useEffect(() => {
    connectSSE()
    return () => {
      esRef.current?.close()
      esRef.current = null
    }
  }, [runId])

  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [phases, autoScroll])

  function handleScroll(e: Event) {
    const el = e.target as HTMLElement
    const distFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight
    if (distFromBottom > 50) {
      setAutoScroll(false)
    }
  }

  function toggleCollapsed(phase: string) {
    setCollapsed(prev => {
      const next = new Set(prev)
      if (next.has(phase)) {
        next.delete(phase)
      } else {
        next.add(phase)
      }
      return next
    })
  }

  const statusSymbol = (status: PhaseGroup['status']) => {
    if (status === 'running') return html`<span style="color:var(--accent);animation:spin 1s linear infinite;">●</span>`
    if (status === 'complete') return html`<span style="color:var(--success);">✓</span>`
    return html`<span style="color:var(--error);">✗</span>`
  }

  return html`
    <div
      ref=${containerRef}
      onScroll=${handleScroll}
      style="background:var(--bg);border-radius:4px;overflow-y:auto;height:100%;font-family:var(--font-mono);font-size:13px;position:relative;"
      role="log"
      aria-live="polite"
    >
      <!-- Top bar -->
      <div style="position:sticky;top:0;right:0;display:flex;justify-content:flex-end;padding:4px 8px;background:var(--bg);border-bottom:1px solid var(--border);z-index:1;">
        <button
          onClick=${() => setShowRaw(v => !v)}
          style="font-size:12px;padding:3px 8px;color:${showRaw ? 'var(--accent)' : 'var(--muted)'};"
        >${showRaw ? 'Show parsed' : 'Show raw'}</button>
      </div>

      ${showRaw
        ? html`<pre style="margin:0;padding:16px;white-space:pre-wrap;word-break:break-all;color:var(--text);font-size:12px;">${rawLines.join('\n')}</pre>`
        : html`
          ${phases.length === 0 && html`
            <div style="padding:16px;color:var(--muted);">Waiting for output...</div>
          `}
          ${phases.map(group => html`
            <div key=${group.phase}>
              <div
                onClick=${() => toggleCollapsed(group.phase)}
                style="padding-left:16px;height:36px;display:flex;align-items:center;gap:8px;cursor:pointer;background:transparent;"
                onMouseEnter=${(e: MouseEvent) => { (e.currentTarget as HTMLElement).style.background = 'var(--panel)' }}
                onMouseLeave=${(e: MouseEvent) => { (e.currentTarget as HTMLElement).style.background = 'transparent' }}
              >
                ${statusSymbol(group.status)}
                <span style="color:var(--text);font-weight:600;">${group.phase}</span>
                <span style="color:var(--muted);font-size:12px;margin-left:auto;padding-right:16px;">${collapsed.has(group.phase) ? '▶' : '▼'}</span>
              </div>
              ${!collapsed.has(group.phase) && html`
                <div style="padding-left:32px;padding-right:16px;padding-bottom:8px;">
                  ${group.events.map((ev, i) => html`<div key=${i}>${renderEventLine(ev)}</div>`)}
                </div>
              `}
            </div>
          `)}
        `
      }

      <!-- SSE disconnected notice -->
      ${!connected && !isCompleted && html`
        <div style="padding:8px 16px;background:rgba(248,81,73,0.1);border-top:1px solid var(--error);color:var(--error);display:flex;align-items:center;gap:8px;">
          Log stream disconnected.
          <button onClick=${connectSSE} style="color:var(--accent);background:transparent;border:none;cursor:pointer;padding:0;font-family:var(--font-mono);">[Reconnect]</button>
        </div>
      `}

      <!-- Auto-scroll resume button -->
      ${!autoScroll && html`
        <div style="position:sticky;bottom:8px;right:8px;display:flex;justify-content:flex-end;padding-right:8px;">
          <button
            onClick=${() => setAutoScroll(true)}
            style="background:var(--panel);color:var(--accent);border-color:var(--accent);font-size:12px;padding:4px 8px;"
          >↓ Resume</button>
        </div>
      `}

      <div ref=${bottomRef} style="height:1px;"></div>
    </div>
  `
}
