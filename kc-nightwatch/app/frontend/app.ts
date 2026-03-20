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
import { Toast } from './components/toast.ts'
import { api } from './lib/api.ts'
import { showToast } from './lib/use-toast.ts'
import { refreshTrigger } from './lib/use-poll.ts'

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

    // NOTE: Notification.requestPermission() is called on first manual run trigger
    // in dashboard.ts (user gesture required). Here we only CHECK permission before firing.

    es.addEventListener('brief-ready', (e: MessageEvent) => {
      const data = JSON.parse(e.data)
      const targetNames = Object.keys(data.summary?.per_target ?? {})
      const briefTarget = targetNames[0]
      if (briefTarget) {
        // Send brief context to the target's chat session
        api.briefChat(briefTarget, data.summary).catch(console.error)

        // Toast for completion
        const actionCount = data.summary?.per_target?.[briefTarget]?.actions?.length ?? 0
        showToast(`${briefTarget} run complete (${actionCount} actions)`, 'success')

        // Increment refreshTrigger so usePoll consumers re-fetch immediately
        refreshTrigger.value++

        // Browser notification when tab is backgrounded
        if (document.visibilityState === 'hidden' && Notification.permission === 'granted') {
          const proposals = data.summary?.per_target?.[briefTarget]?.actions?.filter((a: any) => a.type === 'proposal')?.length ?? 0
          const n = new Notification(`NW: ${briefTarget} complete`, { body: `${actionCount} actions, ${proposals} proposals` })
          n.onclick = () => { window.focus() }
        }
      }
    })

    es.addEventListener('run:failed', (e: MessageEvent) => {
      const data = JSON.parse(e.data)
      const target = data.target ?? 'unknown'
      const errorMsg = data.error ? String(data.error).slice(0, 80) : 'Unknown error'
      showToast(`${target} run failed: ${errorMsg}`, 'error')

      // Increment refreshTrigger so usePoll consumers re-fetch immediately
      refreshTrigger.value++

      // Browser notification when tab is backgrounded
      if (document.visibilityState === 'hidden' && Notification.permission === 'granted') {
        const n = new Notification(`NW: ${target} failed`, { body: errorMsg })
        n.onclick = () => { window.focus() }
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
    <>
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
      <${Toast} />
    </>
  `
}

render(html`<${App} />`, document.getElementById('app')!)
