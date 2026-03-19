import { html } from 'htm/preact'
import { useState, useEffect, useRef } from 'preact/hooks'
import { render } from 'preact'
import type { ScheduleConfig, TargetHealthData } from '../shared/types.ts'
import { Dashboard } from './pages/dashboard.ts'
import { Runs } from './pages/runs.ts'
import { Config } from './pages/config.ts'
import { Health } from './pages/health.ts'
import { BottomNav } from './components/bottom-nav.ts'
import { ScheduleBar } from './components/schedule-bar.ts'
import { ChatDrawer } from './components/chat-drawer.ts'
import { api } from './lib/api.ts'

type Page = 'dashboard' | 'runs' | 'health' | 'config'

function getPage(): Page {
  const hash = location.hash
  if (hash.startsWith('#/runs')) return 'runs'
  if (hash === '#/health') return 'health'
  if (hash === '#/config') return 'config'
  return 'dashboard'
}

function App() {
  const [page, setPage] = useState<Page>(getPage())
  const [schedule, setSchedule] = useState<ScheduleConfig | null>(null)
  const [chatOpen, setChatOpen] = useState(false)
  const [chatTarget, setChatTarget] = useState<string | null>(null)
  const [chatBriefBadge, setChatBriefBadge] = useState(false)
  const [healthData, setHealthData] = useState<Record<string, { health: 'improving' | 'stable' | 'degrading' }>>({})
  const globalEsRef = useRef<EventSource | null>(null)

  useEffect(() => {
    api.getSchedule().then(setSchedule).catch(console.error)

    const handler = () => setPage(getPage())
    window.addEventListener('hashchange', handler)

    // Global SSE for lifecycle events (auto-brief)
    const es = new EventSource('/api/events')
    globalEsRef.current = es

    es.addEventListener('brief-ready', (e: MessageEvent) => {
      const data = JSON.parse(e.data)
      // Auto-open chat drawer with briefing
      // Find first target from summary to use as chat target
      const targetNames = Object.keys(data.summary?.per_target ?? {})
      const briefTarget = targetNames[0] ?? chatTarget
      if (briefTarget) {
        setChatTarget(briefTarget)
        // Send brief context to chat session
        api.briefChat(briefTarget, data.summary).catch(console.error)
        if (!chatOpen) {
          setChatBriefBadge(true)
        }
        setChatOpen(true)
      }
    })

    return () => {
      window.removeEventListener('hashchange', handler)
      es.close()
    }
  }, [])

  // Fetch health data for sidebar arrows after targets are loaded
  useEffect(() => {
    api.getTargets()
      .then(targets => {
        if (targets.length === 0) return
        return Promise.all(
          targets.map(t =>
            api.getHealth(t.name)
              .then((h: TargetHealthData) => ({ name: t.name, health: h.health }))
              .catch(() => null)
          )
        ).then(results => {
          const data: Record<string, { health: 'improving' | 'stable' | 'degrading' }> = {}
          for (const r of results ?? []) {
            if (r) data[r.name] = { health: r.health }
          }
          setHealthData(data)
        })
      })
      .catch(console.error)
  }, [])

  function handleScheduleToggle() {
    if (!schedule) return
    const updated = { ...schedule, enabled: !schedule.enabled }
    setSchedule(updated)
    api.updateSchedule({ enabled: !schedule.enabled }).then(setSchedule).catch(console.error)
  }

  function handleChatToggle() {
    setChatOpen(prev => !prev)
    setChatBriefBadge(false)
  }

  // Allow pages to set chat target via custom event
  useEffect(() => {
    const handler = (e: CustomEvent) => {
      setChatTarget(e.detail.target)
      setChatOpen(true)
      setChatBriefBadge(false)
    }
    window.addEventListener('open-chat', handler as EventListener)
    return () => window.removeEventListener('open-chat', handler as EventListener)
  }, [])

  return html`
    <div style="display:flex;flex-direction:column;height:100%;overflow:hidden;">
      <${ScheduleBar} schedule=${schedule} onToggle=${handleScheduleToggle} />
      <div style="flex:1;overflow:hidden;padding-bottom:48px;">
        ${page === 'dashboard' && html`<${Dashboard} healthData=${healthData} />`}
        ${page === 'runs' && html`<${Runs} />`}
        ${page === 'health' && html`<${Health} />`}
        ${page === 'config' && html`<${Config} />`}
      </div>
      <${BottomNav} current=${page} />

      <!-- Chat toggle button -->
      <button
        onClick=${handleChatToggle}
        aria-label="Open NW-Claude chat"
        style="
          position:fixed;bottom:60px;right:16px;z-index:150;
          width:44px;height:44px;border-radius:50%;
          background:var(--btn-primary);color:#fff;border:none;
          font-size:18px;display:flex;align-items:center;justify-content:center;
          box-shadow:0 2px 8px rgba(0,0,0,0.3);
        "
      >
        ${chatOpen ? 'X' : 'C'}
        ${chatBriefBadge && !chatOpen && html`
          <span style="
            position:absolute;top:-2px;right:-2px;
            background:var(--warn);color:#000;font-size:9px;font-weight:700;
            padding:2px 5px;border-radius:8px;white-space:nowrap;
          ">New briefing</span>
        `}
      </button>

      <!-- Chat drawer -->
      <${ChatDrawer}
        isOpen=${chatOpen}
        onClose=${() => { setChatOpen(false); setChatBriefBadge(false) }}
        targetName=${chatTarget}
      />
    </div>
  `
}

render(html`<${App} />`, document.getElementById('app')!)
