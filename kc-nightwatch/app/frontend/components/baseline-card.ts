import { html } from 'htm/preact'
import type { IndicatorBaseline } from '../../shared/types.ts'

interface Props {
  baselines: Record<string, IndicatorBaseline>
}

function trendArrow(trend: IndicatorBaseline['trend']): { symbol: string; color: string; label: string } {
  switch (trend) {
    case 'improving': return { symbol: '\u2191', color: 'var(--success)', label: 'trend: up' }
    case 'degrading': return { symbol: '\u2193', color: 'var(--error)', label: 'trend: down' }
    case 'stable':
    default: return { symbol: '\u2192', color: 'var(--muted)', label: 'trend: flat' }
  }
}

export function BaselineCard({ baselines }: Props) {
  const entries = Object.entries(baselines)
  if (entries.length === 0) return null

  return html`
    <div style="background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:12px;margin:12px 16px;">
      <div style="font-size:12px;color:var(--muted);font-weight:600;margin-bottom:8px;">Indicator Baselines</div>
      ${entries.map(([name, baseline]) => {
        const arrow = trendArrow(baseline.trend)
        return html`
          <div key=${name} style="display:flex;align-items:center;gap:8px;padding:4px 0;">
            <span style="font-size:14px;color:var(--text);flex:1;">${name}</span>
            <span style="font-size:14px;font-weight:600;color:var(--text);">
              ${baseline.value} ${baseline.measurement}
            </span>
            ${baseline.previous_value !== undefined && html`
              <span style="font-size:11px;color:var(--muted);">
                (was ${baseline.previous_value})
              </span>
            `}
            <span aria-label=${arrow.label} style="font-size:14px;color:${arrow.color};">${arrow.symbol}</span>
          </div>
        `
      })}
    </div>
  `
}
