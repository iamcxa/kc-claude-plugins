import { html } from 'htm/preact'

interface Props {
  health: 'improving' | 'stable' | 'degrading' | null
}

function trendDisplay(health: 'improving' | 'stable' | 'degrading' | null) {
  switch (health) {
    case 'improving': return { text: 'Overall: Improving \u2191', color: 'var(--success)' }
    case 'degrading': return { text: 'Overall: Degrading \u2193', color: 'var(--error)' }
    case 'stable':
    default: return { text: 'Overall: Stable \u2192', color: 'var(--muted)' }
  }
}

export function HealthSummaryBar({ health }: Props) {
  const display = trendDisplay(health)
  return html`
    <div style="
      background:var(--panel);
      border:1px solid var(--border);
      border-radius:6px;
      padding:8px 16px;
      text-align:center;
      font-size:14px;
      color:${display.color};
      margin:16px;
      height:40px;
      display:flex;
      align-items:center;
      justify-content:center;
    ">
      ${display.text}
    </div>
  `
}
