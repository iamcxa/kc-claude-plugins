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
      const targetNames = Object.keys(data.summary?.per_target ?? {})
      const briefTarget = targetNames[0]
      if (briefTarget) {
        // Send brief context to the target's chat session
        api.briefChat(briefTarget, data.summary).catch(console.error)
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
    </div>
  `
}

render(html`<${App} />`, document.getElementById('app')!)
