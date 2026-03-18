import { html } from 'htm/preact'
import { useState, useEffect } from 'preact/hooks'
import type { ScheduleConfig } from '../../shared/types.ts'

interface Props {
  schedule: ScheduleConfig | null
  onToggle: () => void
}

export function ScheduleBar({ schedule, onToggle }: Props) {
  const [countdown, setCountdown] = useState('')

  useEffect(() => {
    if (!schedule?.enabled || !schedule.interval_hours) {
      setCountdown('')
      return
    }
    const intervalMs = schedule.interval_hours * 3_600_000
    // Approximate: countdown from now since we don't know last run time
    let remaining = intervalMs

    const updateCountdown = () => {
      remaining -= 10_000
      if (remaining <= 0) remaining = intervalMs
      const h = Math.floor(remaining / 3_600_000)
      const m = Math.floor((remaining % 3_600_000) / 60_000)
      setCountdown(`${h}h ${m}m`)
    }
    updateCountdown()

    const id = setInterval(updateCountdown, 10_000)
    return () => clearInterval(id)
  }, [schedule?.enabled, schedule?.interval_hours])

  if (!schedule) {
    return html`
      <div style="background:var(--panel);border-bottom:1px solid var(--border);height:48px;display:flex;align-items:center;padding:0 16px;font-size:14px;color:var(--muted);">
        Loading...
      </div>
    `
  }

  return html`
    <div style="background:var(--panel);border-bottom:1px solid var(--border);height:48px;display:flex;align-items:center;padding:0 16px;gap:16px;font-size:14px;flex-shrink:0;">
      <button
        onClick=${onToggle}
        style="padding:3px 8px;font-size:12px;background:${schedule.enabled ? 'rgba(88,166,255,0.15)' : 'var(--btn-secondary)'};color:${schedule.enabled ? 'var(--accent)' : 'var(--muted)'};border-color:${schedule.enabled ? 'var(--accent)' : 'var(--border)'};"
      >
        ${schedule.enabled ? 'ON' : 'OFF'}
      </button>
      ${schedule.enabled
        ? html`
          <span style="color:var(--text);">Scheduler: every ${schedule.interval_hours}h</span>
          ${countdown && html`<span style="color:var(--muted);">· Next in ${countdown}</span>`}
        `
        : html`<span style="color:var(--muted);">Scheduler: off</span>`
      }
      <span style="color:var(--muted);margin-left:auto;">Last run: —</span>
    </div>
  `
}
