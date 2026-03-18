import { html } from 'htm/preact'
import { useState, useEffect } from 'preact/hooks'
import { render } from 'preact'
import type { ScheduleConfig } from '../shared/types.ts'
import { Dashboard } from './pages/dashboard.ts'
import { Runs } from './pages/runs.ts'
import { Config } from './pages/config.ts'
import { BottomNav } from './components/bottom-nav.ts'
import { ScheduleBar } from './components/schedule-bar.ts'
import { api } from './lib/api.ts'

type Page = 'dashboard' | 'runs' | 'config'

function getPage(): Page {
  const hash = location.hash
  if (hash.startsWith('#/runs')) return 'runs'
  if (hash === '#/config') return 'config'
  return 'dashboard'
}

function App() {
  const [page, setPage] = useState<Page>(getPage())
  const [schedule, setSchedule] = useState<ScheduleConfig | null>(null)

  useEffect(() => {
    api.getSchedule().then(setSchedule).catch(console.error)

    const handler = () => setPage(getPage())
    window.addEventListener('hashchange', handler)
    return () => window.removeEventListener('hashchange', handler)
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
        ${page === 'dashboard' && html`<${Dashboard} />`}
        ${page === 'runs' && html`<${Runs} />`}
        ${page === 'config' && html`<${Config} />`}
      </div>
      <${BottomNav} current=${page} />
    </div>
  `
}

render(html`<${App} />`, document.getElementById('app')!)
