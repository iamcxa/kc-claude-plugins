import { html } from 'htm/preact'
import { useState, useEffect, useCallback } from 'preact/hooks'
import type { Run, RunSummary, ParsedLogEvent, OutcomeRecord, FeedbackEntry } from '../../shared/types.ts'
import { LogStream } from '../components/log-stream.ts'
import { RunTimeline } from '../components/run-timeline.ts'
import { ActionCard } from '../components/action-card.ts'
import { BaselineCard } from '../components/baseline-card.ts'
import { api } from '../lib/api.ts'
import { usePoll } from '../lib/use-poll.ts'

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
  const [hasActiveRuns, setHasActiveRuns] = useState(false)
  const [selectedId, setSelectedId] = useState<string | null>(getRunIdFromHash())
  const [selectedRun, setSelectedRun] = useState<RunDetailData | null>(null)
  const [statusFilter, setStatusFilter] = useState('')
  const [targetFilter, setTargetFilter] = useState('')
  const [outcomesMap, setOutcomesMap] = useState<Record<string, OutcomeRecord>>({})
  const [feedbackMap, setFeedbackMap] = useState<Record<string, FeedbackEntry[]>>({})
  const [priorityMap, setPriorityMap] = useState<Record<string, number>>({})

  const loadRuns = useCallback(() => {
    api.getRuns().then(allRuns => {
      setRuns(allRuns)
      const active = allRuns.some(r => r.status === 'running' || r.status === 'queued')
      setHasActiveRuns(active)
    }).catch(console.error)
  }, [])

  useEffect(() => {
    loadRuns()
    api.getOutcomes().then(list => {
      const map: Record<string, OutcomeRecord> = {}
      for (const o of list) map[o.signal_id] = o
      setOutcomesMap(map)
    }).catch(console.error)

    const handler = () => {
      const id = getRunIdFromHash()
      setSelectedId(id)
    }
    window.addEventListener('hashchange', handler)
    return () => window.removeEventListener('hashchange', handler)
  }, [])

  // Auto-refresh every 5s when active runs exist.
  // usePoll also watches refreshTrigger internally — SSE events from app.ts
  // (run:failed, brief-ready) trigger immediate re-fetch without waiting for interval.
  usePoll(loadRuns, 5_000, hasActiveRuns)

  useEffect(() => {
    if (!selectedId) {
      setSelectedRun(null)
      setFeedbackMap({})
      return
    }
    api.getRun(selectedId).then(r => setSelectedRun(r)).catch(console.error)
    api.getFeedback(selectedId).then(entries => {
      const map: Record<string, FeedbackEntry[]> = {}
      for (const e of entries) {
        if (!map[e.signal_id]) map[e.signal_id] = []
        map[e.signal_id].push(e)
      }
      setFeedbackMap(map)
    }).catch(console.error)
    api.getSignalPriority(selectedId).then(items => {
      const map: Record<string, number> = {}
      for (const item of items) map[item.signal_id] = item.score
      setPriorityMap(map)
    }).catch(console.error)
  }, [selectedId])

  // Re-fetch run detail when the run list refreshes during active polling.
  // Keeps detail view current without requiring a manual refresh.
  useEffect(() => {
    if (!selectedId) return
    if (!hasActiveRuns) return
    api.getRun(selectedId).then(r => setSelectedRun(r)).catch(console.error)
    api.getFeedback(selectedId).then(entries => {
      const map: Record<string, FeedbackEntry[]> = {}
      for (const e of entries) {
        if (!map[e.signal_id]) map[e.signal_id] = []
        map[e.signal_id].push(e)
      }
      setFeedbackMap(map)
    }).catch(console.error)
    api.getSignalPriority(selectedId!).then(items => {
      const map: Record<string, number> = {}
      for (const item of items) map[item.signal_id] = item.score
      setPriorityMap(map)
    }).catch(console.error)
  }, [runs])

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
          ${selectedRun.queued_at && html`
            <span style="color:var(--muted);font-size:12px;" title=${`Queued: ${selectedRun.queued_at}`}>
              Queued ${timeAgo(selectedRun.queued_at)}
            </span>
          `}
          ${selectedRun.started_at && html`
            <span style="color:var(--muted);font-size:12px;" title=${`Started: ${selectedRun.started_at}`}>
              Started ${timeAgo(selectedRun.started_at)}
            </span>
          `}
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
        <!-- Indicator baselines (above action cards, always visible) -->
        ${selectedRun.summary?.per_target && Object.entries(selectedRun.summary.per_target).map(([targetName, targetData]) =>
          targetData.indicator_baseline && Object.keys(targetData.indicator_baseline).length > 0 && html`
            <${BaselineCard} key=${'baseline-' + targetName} baselines=${targetData.indicator_baseline} />
          `
        )}
        <!-- Pre/Post assessment text (target level) -->
        ${selectedRun.summary?.per_target && Object.entries(selectedRun.summary.per_target).map(([targetName, targetData]) =>
          (targetData.pre_assessment || targetData.post_assessment) && html`
            <div key=${'assess-' + targetName} style="padding:8px 16px;border-bottom:1px solid var(--border);flex-shrink:0;">
              ${targetData.pre_assessment && html`
                <div style="margin-bottom:8px;">
                  <div style="font-size:12px;color:var(--muted);font-weight:600;margin-bottom:4px;">Pre-Run Strategy (${targetName})</div>
                  <div style="font-size:14px;line-height:1.5;color:var(--text);">${targetData.pre_assessment}</div>
                </div>
              `}
              ${targetData.post_assessment && html`
                <div>
                  <div style="font-size:12px;color:var(--muted);font-weight:600;margin-bottom:4px;">Post-Run Reflection (${targetName})</div>
                  <div style="font-size:14px;line-height:1.5;color:var(--text);">${targetData.post_assessment}</div>
                </div>
              `}
            </div>
          `
        )}
        <!-- Action cards from per_target summary, sorted by priority score (descending) -->
        ${selectedRun.summary?.per_target && Object.entries(selectedRun.summary.per_target).map(([targetName, targetData]) =>
          targetData.actions && targetData.actions.length > 0 && html`
            <div key=${targetName} style="padding:12px 16px;border-bottom:1px solid var(--border);flex-shrink:0;overflow-y:auto;max-height:300px;">
              <div style="font-size:12px;color:var(--muted);font-weight:600;margin-bottom:8px;">${targetName} Actions</div>
              ${[...targetData.actions]
                .sort((a: import('../../shared/types.ts').RunSummaryAction, b: import('../../shared/types.ts').RunSummaryAction) => {
                  const scoreA = priorityMap[a.signal_id] ?? 0
                  const scoreB = priorityMap[b.signal_id] ?? 0
                  return scoreB - scoreA
                })
                .map((action: import('../../shared/types.ts').RunSummaryAction) => html`
                  <${ActionCard}
                    key=${action.signal_id}
                    action=${action}
                    target=${targetName}
                    runId=${selectedId}
                    existingFeedback=${feedbackMap[action.signal_id] ?? []}
                    outcomeStatus=${outcomesMap[action.signal_id] ? { status: outcomesMap[action.signal_id].status, url: outcomesMap[action.signal_id].url, type: outcomesMap[action.signal_id].type } : null}
                    priorityScore=${priorityMap[action.signal_id]}
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
              <span style="color:var(--muted);font-size:12px;">
                ${run.status === 'queued'
                  ? `Queued ${timeAgo(run.queued_at)}`
                  : timeAgo(run.started_at)
                }
              </span>
            </div>
          `)
        }
      </div>
    </div>
  `
}
