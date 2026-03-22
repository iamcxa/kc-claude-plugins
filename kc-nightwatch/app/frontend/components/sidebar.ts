import { html } from 'htm/preact'
import type { Target, Run } from '../../shared/types.ts'

interface Props {
  targets: Target[]
  selectedTarget: string | null
  lastRuns: Record<string, Run>
  activeRuns?: Run[]  // NEW — from worker IPC state
  healthData?: Record<string, { health: 'improving' | 'stable' | 'degrading' }>
  onSelect: (targetName: string) => void
  onRun: (targetName: string) => void
  onAddTarget: () => void
}

function statusDotInfo(
  targetName: string,
  lastRun: Run | undefined,
  activeRuns: Run[]
): { color: string; animate: boolean } {
  const targetActive = activeRuns.filter(r => r.target === targetName)
  if (targetActive.some(r => r.status === 'running')) {
    return { color: 'var(--accent)', animate: true }
  }
  if (targetActive.some(r => r.status === 'queued')) {
    return { color: 'var(--warn)', animate: false }
  }
  if (!lastRun) return { color: 'var(--muted)', animate: false }
  const colors: Record<string, string> = {
    completed: 'var(--success)',
    failed: 'var(--error)',
    running: 'var(--accent)',
    queued: 'var(--warn)',
    cancelled: 'var(--muted)',
  }
  return { color: colors[lastRun.status] ?? 'var(--muted)', animate: false }
}

export function Sidebar({ targets, selectedTarget, lastRuns, activeRuns, healthData, onSelect, onRun, onAddTarget }: Props) {
  if (targets.length === 0) {
    return html`
      <aside style="width:240px;min-width:240px;background:var(--panel);border-right:1px solid var(--border);display:flex;flex-direction:column;overflow:hidden;">
        <div style="flex:1;display:flex;align-items:center;justify-content:center;padding:16px;color:var(--muted);text-align:center;font-size:13px;">
          No targets configured. Add a target to get started.
        </div>
        <div style="padding:8px;">
          <button style="width:100%;background:transparent;border:1px dashed var(--border);color:var(--muted);" onClick=${onAddTarget}>+ Add Target</button>
        </div>
      </aside>
    `
  }

  return html`
    <aside style="width:240px;min-width:240px;background:var(--panel);border-right:1px solid var(--border);display:flex;flex-direction:column;overflow:hidden;">
      <ul style="flex:1;overflow-y:auto;list-style:none;padding:8px 0;margin:0;">
        ${targets.map(target => {
          const isSelected = selectedTarget === target.name
          const lastRun = lastRuns[target.name]
          const targetHealth = healthData?.[target.name]
          return html`
            <li
              key=${target.name}
              onClick=${() => onSelect(target.name)}
              style="
                padding:10px 12px;
                cursor:pointer;
                border-left:2px solid ${isSelected ? 'var(--accent)' : 'transparent'};
                background:${isSelected ? 'rgba(88,166,255,0.1)' : 'transparent'};
                display:flex;
                align-items:center;
                gap:8px;
              "
            >
              <div style="flex:1;min-width:0;">
                <div style="font-weight:600;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${target.name}</div>
                <div style="font-size:12px;color:var(--muted);">${target.type}</div>
              </div>
              ${(() => {
                const dot = statusDotInfo(target.name, lastRun, activeRuns ?? [])
                return html`<div style="width:8px;height:8px;border-radius:50%;background:${dot.color};flex-shrink:0;${dot.animate ? 'animation:pulse 1.5s ease-in-out infinite;' : ''}" title=${lastRun?.status ?? 'no runs'}></div>`
              })()}
              ${targetHealth && html`
                <span
                  aria-label="trend: ${targetHealth.health === 'improving' ? 'up' : targetHealth.health === 'degrading' ? 'down' : 'flat'}"
                  style="font-size:12px;color:${targetHealth.health === 'improving' ? 'var(--success)' : targetHealth.health === 'degrading' ? 'var(--error)' : 'var(--muted)'};"
                >${targetHealth.health === 'improving' ? '\u2191' : targetHealth.health === 'degrading' ? '\u2193' : '\u2192'}</span>
              `}
            </li>
          `
        })}
      </ul>
      <div style="padding:8px;border-top:1px solid var(--border);">
        <button style="width:100%;background:transparent;border:1px dashed var(--border);color:var(--muted);" onClick=${onAddTarget}>+ Add Target</button>
      </div>
    </aside>
  `
}
