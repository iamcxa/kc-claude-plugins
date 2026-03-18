import { html } from 'htm/preact'
import { useState, useEffect } from 'preact/hooks'
import type { Run, RunSummary, ParsedLogEvent } from '../../shared/types.ts'
import { LogStream } from '../components/log-stream.ts'
import { RunTimeline } from '../components/run-timeline.ts'
import { ActionCard } from '../components/action-card.ts'
import { api } from '../lib/api.ts'

function getRunIdFromHash(): string | null {
  const hash = location.hash
  const match = hash.match(/^#\/runs\/(.+)$/)
  return match ? match[1] : null
}

function formatDuration(seconds?: number): string {
  if (seconds === undefined) return '—'
  if (seconds < 60) return `${seconds}s`
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}m ${s}s`
}

function timeAgo(dateStr?: string): string {
  if (!dateStr) return '—'
  const diff = Date.now() - new Date(dateStr).getTime()
  const m = Math.floor(diff / 60_000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

function statusColor(status: Run['status']): string {
  const colors: Record<string, string> = {
    completed: 'var(--success)',
    failed: 'var(--error)',
    running: 'var(--accent)',
    queued: 'var(--warn)',
    cancelled: 'var(--muted)',
    timeout: 'var(--warn)',
  }
  return colors[status] ?? 'var(--muted)'
}

interface RunDetailData extends Run {
  summary?: RunSummary
}

export function Runs() {
  const [runs, setRuns] = useState<Run[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(getRunIdFromHash())
  const [selectedRun, setSelectedRun] = useState<RunDetailData | null>(null)
  const [statusFilter, setStatusFilter] = useState('')
  const [targetFilter, setTargetFilter] = useState('')

  useEffect(() => {
    api.getRuns().then(setRuns).catch(console.error)

    const handler = () => {
      const id = getRunIdFromHash()
      setSelectedId(id)
    }
    window.addEventListener('hashchange', handler)
    return () => window.removeEventListener('hashchange', handler)
  }, [])

  useEffect(() => {
    if (!selectedId) {
      setSelectedRun(null)
      return
    }
    api.getRun(selectedId).then(r => setSelectedRun(r)).catch(console.error)
  }, [selectedId])

  const filteredRuns = runs.filter(r => {
    if (statusFilter && r.status !== statusFilter) return false
    if (targetFilter && r.target !== targetFilter) return false
    return true
  })

  const uniqueTargets = [...new Set(runs.map(r => r.target))]

  if (selectedId && selectedRun) {
    const phases = selectedRun.summary?.phases_completed ?? []
    const isRunning = selectedRun.status === 'running'

    return html`
      <div style="height:100%;display:flex;flex-direction:column;overflow:hidden;">
        <!-- Header -->
        <div style="padding:12px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px;flex-shrink:0;">
          <a href="#/runs" style="color:var(--muted);font-size:13px;">← Back to runs</a>
          <span style="color:var(--border);">|</span>
          <span style="color:${statusColor(selectedRun.status)};font-size:12px;font-weight:600;text-transform:uppercase;">${selectedRun.status}</span>
          <span>${selectedRun.target}</span>
          <span style="color:var(--muted);font-size:12px;">${selectedRun.mode}</span>
          <span style="color:var(--muted);font-size:12px;">${selectedRun.trigger}</span>
          <span style="color:var(--muted);font-size:12px;margin-left:auto;">${formatDuration(selectedRun.duration_seconds)}</span>
          ${isRunning && html`
            <button
              style="background:var(--btn-danger);color:#fff;border-color:var(--btn-danger);font-size:12px;padding:4px 8px;"
              onClick=${() => api.cancelRun(selectedId).catch(console.error)}
            >Cancel Run</button>
          `}
        </div>
        <!-- Phase timeline -->
        ${phases.length > 0 && html`
          <div style="padding:12px 16px;border-bottom:1px solid var(--border);flex-shrink:0;">
            <${RunTimeline} phases=${phases} activePhase=${isRunning ? phases[phases.length - 1] ?? null : null} />
          </div>
        `}
        <!-- Action cards from per_target summary -->
        ${selectedRun.summary?.per_target && Object.entries(selectedRun.summary.per_target).map(([targetName, targetData]) =>
          targetData.actions && targetData.actions.length > 0 && html`
            <div key=${targetName} style="padding:12px 16px;border-bottom:1px solid var(--border);flex-shrink:0;overflow-y:auto;max-height:300px;">
              <div style="font-size:12px;color:var(--muted);font-weight:600;margin-bottom:8px;">${targetName} Actions</div>
              ${targetData.actions.map((action: import('../../shared/types.ts').RunSummaryAction) => html`
                <${ActionCard}
                  key=${action.signal_id}
                  action=${action}
                  target=${targetName}
                  runId=${selectedId}
                />
              `)}
            </div>
          `
        )}
        <!-- Log stream -->
        <div style="flex:1;overflow:hidden;padding:0;">
          <${LogStream}
            runId=${selectedId}
            initialEvents=${[] as ParsedLogEvent[]}
            isCompleted=${!isRunning}
          />
        </div>
      </div>
    `
  }

  return html`
    <div style="height:100%;display:flex;flex-direction:column;overflow:hidden;">
      <!-- Filter bar -->
      <div style="padding:12px 16px;border-bottom:1px solid var(--border);display:flex;gap:12px;flex-shrink:0;">
        <select
          value=${statusFilter}
          onChange=${(e: Event) => setStatusFilter((e.target as HTMLSelectElement).value)}
          style="padding:4px 8px;"
        >
          <option value="">All statuses</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="running">Running</option>
          <option value="queued">Queued</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <select
          value=${targetFilter}
          onChange=${(e: Event) => setTargetFilter((e.target as HTMLSelectElement).value)}
          style="padding:4px 8px;"
        >
          <option value="">All targets</option>
          ${uniqueTargets.map(t => html`<option key=${t} value=${t}>${t}</option>`)}
        </select>
      </div>
      <!-- Run list -->
      <div style="flex:1;overflow-y:auto;">
        ${filteredRuns.length === 0
          ? html`
            <div style="display:flex;align-items:center;justify-content:center;height:200px;color:var(--muted);">
              No runs yet. Trigger a run to see history here.
            </div>
          `
          : filteredRuns.map(run => html`
            <div
              key=${run.id}
              onClick=${() => { location.hash = `#/runs/${run.id}` }}
              style="
                padding:12px 16px;
                border-bottom:1px solid var(--border);
                cursor:pointer;
                display:flex;
                align-items:center;
                gap:12px;
                border-left:3px solid ${run.status === 'running' ? 'var(--accent)' : 'transparent'};
              "
              onMouseEnter=${(e: MouseEvent) => { (e.currentTarget as HTMLElement).style.background = 'var(--panel)' }}
              onMouseLeave=${(e: MouseEvent) => { (e.currentTarget as HTMLElement).style.background = '' }}
            >
              <span style="color:${statusColor(run.status)};font-size:12px;font-weight:600;min-width:80px;">${run.status}</span>
              <span style="font-weight:600;">${run.target}</span>
              <span style="color:var(--muted);font-size:12px;">${run.mode}</span>
              <span style="color:var(--muted);font-size:12px;">${run.trigger}</span>
              <span style="color:var(--muted);font-size:12px;margin-left:auto;">${formatDuration(run.duration_seconds)}</span>
              <span style="color:var(--muted);font-size:12px;">${timeAgo(run.started_at)}</span>
            </div>
          `)
        }
      </div>
    </div>
  `
}
