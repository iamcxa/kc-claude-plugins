import { html } from 'htm/preact'
import { useState, useEffect } from 'preact/hooks'
import type { Target, Run, RunSummary, ScheduleConfig } from '../../shared/types.ts'
import { RunTimeline } from './run-timeline.ts'

interface Props {
  target: Target | null
  lastRun: (Run & { summary?: RunSummary }) | null
  workerQueue?: Run[]
  globalSchedule?: ScheduleConfig | null  // NEW
  onRun: (mode: 'production' | 'dry-run') => void
  onEdit: () => void
  onRemove: () => void
}

function statusBadge(status: Run['status']) {
  const colors: Record<string, string> = {
    completed: 'var(--success)',
    failed: 'var(--error)',
    running: 'var(--accent)',
    queued: 'var(--warn)',
    cancelled: 'var(--muted)',
    timeout: 'var(--warn)',
  }
  const color = colors[status] ?? 'var(--muted)'
  return html`<span style="color:${color};font-size:12px;font-weight:600;text-transform:uppercase;">${status}</span>`
}

function formatDuration(seconds?: number): string {
  if (seconds === undefined) return '—'
  if (seconds < 60) return `${seconds}s`
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}m ${s}s`
}

function timeAgo(dateStr?: string): string {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const m = Math.floor(diff / 60_000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

export function TargetDetail({ target, lastRun, workerQueue, globalSchedule, onRun, onEdit, onRemove }: Props) {
  const [showMenu, setShowMenu] = useState(false)
  const [showRemoveConfirm, setShowRemoveConfirm] = useState(false)
  const [nextRunText, setNextRunText] = useState('')

  const phases = lastRun?.summary?.phases_completed ?? []
  const isRunning = lastRun?.status === 'running'

  useEffect(() => {
    if (!target) { setNextRunText(''); return }
    const effectiveInterval = target.schedule?.interval_hours ?? globalSchedule?.interval_hours
    if (!effectiveInterval || !globalSchedule?.enabled) {
      setNextRunText('Not yet scheduled')
      return
    }
    const updateCountdown = () => {
      const lastRunMs = lastRun?.started_at ? new Date(lastRun.started_at).getTime() : null
      if (!lastRunMs) {
        setNextRunText('Not yet scheduled')
        return
      }
      const intervalMs = effectiveInterval * 3_600_000
      const nextRunMs = lastRunMs + intervalMs
      const remaining = nextRunMs - Date.now()
      if (remaining <= 0) {
        setNextRunText('Due now')
        return
      }
      const h = Math.floor(remaining / 3_600_000)
      const m = Math.floor((remaining % 3_600_000) / 60_000)
      const nextDate = new Date(nextRunMs)
      const hh = String(nextDate.getHours()).padStart(2, '0')
      const mm = String(nextDate.getMinutes()).padStart(2, '0')
      setNextRunText(`Next: ${hh}:${mm} (in ${h}h ${m}m)`)
    }
    updateCountdown()
    const id = setInterval(updateCountdown, 60_000)
    return () => clearInterval(id)
  }, [target?.name, target?.schedule?.interval_hours, globalSchedule?.interval_hours, globalSchedule?.enabled, lastRun?.started_at])

  if (!target) {
    return html`
      <div style="flex:1;display:flex;align-items:center;justify-content:center;color:var(--muted);">
        Select a target from the sidebar to view details
      </div>
    `
  }

  return html`
    <div style="flex:1;overflow-y:auto;padding:16px;position:relative;">
      <!-- Header -->
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
        <h2 style="margin:0;font-size:18px;">${target.name}</h2>
        <span style="font-size:12px;color:var(--muted);background:var(--btn-secondary);padding:2px 6px;border-radius:4px;">${target.type}</span>
      </div>

      <!-- North star -->
      <div style="margin-bottom:20px;padding:12px;background:var(--panel);border:1px solid var(--border);border-radius:6px;">
        <div style="font-size:12px;color:var(--muted);font-weight:600;margin-bottom:6px;">North star</div>
        <p style="margin:0;color:var(--text);font-style:italic;line-height:1.5;">${target.north_star}</p>
      </div>

      <!-- Schedule -->
      <div style="margin-bottom:20px;padding:12px;background:var(--panel);border:1px solid var(--border);border-radius:6px;">
        <div style="font-size:12px;color:var(--muted);font-weight:600;margin-bottom:6px;">Schedule</div>
        <div style="font-size:14px;color:var(--text);margin-bottom:4px;">
          ${target.schedule?.interval_hours
            ? `Every ${target.schedule.interval_hours}h (custom)`
            : globalSchedule?.interval_hours
              ? `Every ${globalSchedule.interval_hours}h (global)`
              : 'No schedule configured'}
        </div>
        <div style="font-size:12px;color:var(--muted);">${nextRunText}</div>
      </div>

      <!-- Action buttons -->
      <div style="display:flex;gap:8px;margin-bottom:20px;position:relative;">
        <button
          style="background:var(--btn-primary);color:#fff;border-color:var(--btn-primary);"
          onClick=${() => onRun('production')}
        >Run</button>
        <button onClick=${() => onRun('dry-run')}>Dry run</button>
        <button
          onClick=${() => setShowMenu(v => !v)}
          style="padding:6px 10px;"
          title="More options"
        >⋮</button>

        ${showMenu && html`
          <div
            style="position:absolute;top:100%;left:0;background:var(--panel);border:1px solid var(--border);border-radius:6px;min-width:160px;z-index:10;box-shadow:0 4px 12px rgba(0,0,0,0.4);margin-top:4px;"
            onMouseLeave=${() => setShowMenu(false)}
          >
            <button style="width:100%;text-align:left;border:none;border-radius:6px 6px 0 0;background:transparent;" onClick=${() => { onRun('production'); setShowMenu(false) }}>Run</button>
            <button style="width:100%;text-align:left;border:none;border-radius:0;background:transparent;" onClick=${() => { onRun('dry-run'); setShowMenu(false) }}>Dry run</button>
            <div style="height:1px;background:var(--border);margin:4px 0;"></div>
            <button
              style="width:100%;text-align:left;border:none;border-radius:0;background:transparent;"
              onClick=${() => { onEdit(); setShowMenu(false) }}
            >Edit</button>
            <button
              aria-disabled="true"
              title="Coming in Phase 3"
              style="width:100%;text-align:left;border:none;border-radius:0;background:transparent;opacity:0.5;cursor:not-allowed;"
              onClick=${(e: Event) => e.preventDefault()}
            >Chat</button>
            <div style="height:1px;background:var(--border);margin:4px 0;"></div>
            ${showRemoveConfirm
              ? html`
                <div style="padding:8px 12px;">
                  <div style="font-size:12px;margin-bottom:8px;">Remove ${target.name}? This will not delete any files.</div>
                  <div style="display:flex;gap:8px;">
                    <button style="font-size:12px;padding:3px 8px;" onClick=${() => setShowRemoveConfirm(false)}>Never mind</button>
                    <button style="font-size:12px;padding:3px 8px;background:var(--btn-danger);color:#fff;border-color:var(--btn-danger);" onClick=${() => { onRemove(); setShowMenu(false); setShowRemoveConfirm(false) }}>Remove</button>
                  </div>
                </div>
              `
              : html`
                <button
                  style="width:100%;text-align:left;border:none;border-radius:0 0 6px 6px;background:transparent;color:var(--error);"
                  onClick=${() => setShowRemoveConfirm(true)}
                >Remove target</button>
              `
            }
          </div>
        `}
      </div>

      <!-- Queue status -->
      ${(() => {
        const queuedForTarget = (workerQueue ?? []).filter(r => r.target === target.name)
        if (queuedForTarget.length === 0) return null
        return html`
          <div style="margin-bottom:16px;">
            <div style="font-size:12px;color:var(--muted);font-weight:600;margin-bottom:8px;">Queue</div>
            <div style="background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:12px;">
              <div style="font-size:14px;color:var(--warn);font-weight:600;margin-bottom:8px;">${queuedForTarget.length} queued</div>
              ${queuedForTarget.map((run, index) => {
                const allQueued = workerQueue ?? []
                const globalIndex = allQueued.indexOf(run)
                const position = globalIndex >= 0 ? globalIndex + 1 : index + 1
                const queuedAgo = run.queued_at ? timeAgo(run.queued_at) : ''
                return html`
                  <div key=${run.id} style="display:flex;align-items:center;gap:8px;padding:4px 0;font-size:13px;">
                    <span style="background:var(--warn);color:#000;font-size:11px;font-weight:700;padding:1px 6px;border-radius:10px;">#${position}</span>
                    <span style="color:var(--muted);">${run.mode}</span>
                    ${queuedAgo && html`<span style="color:var(--muted);font-size:12px;margin-left:auto;">${queuedAgo}</span>`}
                  </div>
                `
              })}
            </div>
          </div>
        `
      })()}

      <!-- Last run summary -->
      <div style="margin-bottom:16px;">
        <div style="font-size:12px;color:var(--muted);font-weight:600;margin-bottom:8px;">Last run</div>
        ${lastRun
          ? html`
            <div style="background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:12px;">
              <div style="display:flex;gap:16px;align-items:center;margin-bottom:8px;">
                ${statusBadge(lastRun.status)}
                <span style="color:var(--muted);font-size:12px;">${lastRun.trigger}</span>
                <span style="color:var(--muted);font-size:12px;">${formatDuration(lastRun.duration_seconds)}</span>
              </div>
              ${phases.length > 0 && html`
                <div style="margin-top:8px;">
                  <${RunTimeline} phases=${phases} activePhase=${isRunning ? phases[phases.length - 1] ?? null : null} />
                </div>
              `}
            </div>
          `
          : html`<div style="color:var(--muted);font-size:13px;">No runs yet</div>`
        }
      </div>
    </div>
  `
}
