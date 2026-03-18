import { html } from 'htm/preact'

const PHASES = ['Phase 0', 'Phase 1', 'Phase 2', 'Phase 3', 'Phase 4', 'Phase 5']

interface Props {
  phases: string[]
  activePhase: string | null
}

export function RunTimeline({ phases, activePhase }: Props) {
  return html`
    <div>
      <div style="display:flex;gap:4px;height:8px;margin-bottom:4px;">
        ${PHASES.map(p => {
          const completed = phases.includes(p)
          const active = p === activePhase
          const color = completed ? 'var(--success)' : active ? 'var(--accent)' : 'var(--border)'
          return html`
            <div
              key=${p}
              title=${p}
              style="flex:1;border-radius:4px;background:${color};${active ? 'animation:pulse 1.5s ease-in-out infinite;' : ''}"
            ></div>
          `
        })}
      </div>
      ${activePhase && html`<div style="font-size:12px;color:var(--muted);">${activePhase}</div>`}
    </div>
  `
}
