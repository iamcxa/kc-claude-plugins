import { html } from 'htm/preact'
import { useState } from 'preact/hooks'
import type { ForgeResultData } from '../../shared/types.ts'

export function relativeTime(isoDate: string | null): string {
  if (isoDate === null) return 'never'
  const diffMs = Date.now() - new Date(isoDate).getTime()
  const diffH = Math.floor(diffMs / 3600000)
  if (diffH < 1) return 'just now'
  if (diffH < 24) return `${diffH}h ago`
  const diffD = Math.floor(diffH / 24)
  return `${diffD}d ago`
}

export function statusColor(data: ForgeResultData): string {
  if (data.stale === true) return 'var(--muted)'
  if (data.forge_result === null) return 'var(--muted)'
  if (data.forge_result.status === 'pass') return 'var(--success)'
  return 'var(--error)'
}

export function statusIcon(data: ForgeResultData): string {
  if (data.forge_result === null) return '\u2014'
  if (data.forge_result.status === 'pass') return '\u2713'
  return '\u2717'
}

export function ForgeResultCard({ data }: { data: ForgeResultData | null }) {
  const [expanded, setExpanded] = useState(false)

  // Fetch error state
  if (data === null) {
    return html`
      <div style="background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:12px;margin:0 16px 16px;color:var(--muted);font-size:14px;">
        Unavailable
      </div>
    `
  }

  // No forge run recorded
  if (data.forge_result === null) {
    return html`
      <div style="background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:12px;margin:0 16px 16px;">
        <div style="font-size:14px;color:var(--muted);">\u2014 No forge run recorded</div>
      </div>
    `
  }

  const color = statusColor(data)
  const icon = statusIcon(data)
  const badge = data.forge_result.status === 'pass' ? 'Pass' : 'Fail'
  const timeStr = relativeTime(data.run_date)
  const detailLines = data.forge_result.details
    ? data.forge_result.details.split('\n').filter(l => l.trim())
    : []

  function toggle() {
    setExpanded(e => !e)
  }

  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      toggle()
    } else if (e.key === ' ') {
      e.preventDefault()
      toggle()
    }
  }

  const textColor = data.stale ? 'var(--muted)' : 'var(--text)'

  return html`
    <div
      role="button"
      tabIndex=${0}
      aria-expanded=${expanded}
      onClick=${toggle}
      onKeyDown=${handleKeyDown}
      style="background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:12px;margin:0 16px 16px;cursor:pointer;outline-offset:2px;"
    >
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-size:14px;font-weight:600;color:${color};">${icon}</span>
        <span style="font-size:14px;font-weight:600;color:${color};">${badge}</span>
        <span style="font-size:14px;color:var(--muted);margin-left:auto;">${timeStr}</span>
      </div>

      ${expanded && html`
        <div style="padding-top:8px;border-top:1px solid var(--border);margin-top:8px;">
          ${data.forge_result.branch && html`
            <div style="font-size:14px;color:${textColor};font-family:var(--font-mono);margin-bottom:4px;">
              Branch: ${data.forge_result.branch}
            </div>
          `}
          ${detailLines.length > 0 && html`
            <div style="font-size:14px;color:var(--muted);margin-top:4px;">Details:</div>
            <ul style="font-size:14px;color:var(--muted);margin:4px 0;padding-left:16px;">
              ${detailLines.map((line, i) => html`<li key=${i}>${line}</li>`)}
            </ul>
          `}
        </div>
      `}
    </div>
  `
}
