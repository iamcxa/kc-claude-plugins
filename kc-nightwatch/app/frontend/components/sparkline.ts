import { html } from 'htm/preact'
import { useState } from 'preact/hooks'

interface Props {
  values: number[]
  width?: number
  height?: number
  runIds?: string[]  // parallel to values — tooltip shows run ID when present
}

export function tooltipStyle(idx: number, total: number, width: number): Record<string, string> {
  if (idx === 0) return { left: '0px', transform: 'none' }
  if (idx === total - 1) return { right: '0px', left: 'auto', transform: 'none' }
  const x = (idx / (total - 1)) * width
  return { left: `${x}px`, transform: 'translateX(-50%)' }
}

export function formatTooltipValue(v: number): string {
  return `${Math.round(v * 100)}%`
}

function tooltipStyleStr(idx: number, total: number, width: number): string {
  const s = tooltipStyle(idx, total, width)
  return Object.entries(s).map(([k, v]) => `${k}:${v}`).join(';')
}

export function Sparkline({ values, width = 80, height = 20, runIds }: Props) {
  if (values.length < 2) {
    return html`<span style="color:var(--muted);font-size:11px;">--</span>`
  }

  const [activeIdx, setActiveIdx] = useState<number | null>(null)

  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1

  const points = values.map((v, i) => {
    const x = (i / (values.length - 1)) * width
    const y = height - ((v - min) / range) * height
    return `${x},${y}`
  }).join(' ')

  const first = values[0]!
  const last = values[values.length - 1]!
  const flat = last === first
  const color = flat ? 'var(--muted)' : last > first ? 'var(--success)' : 'var(--error)'

  const pointSpacing = values.length > 1 ? width / (values.length - 1) : width

  return html`
    <div style="position:relative;display:inline-block;">
      ${activeIdx !== null && html`
        <div style="position:absolute;top:-36px;${tooltipStyleStr(activeIdx, values.length, width)};background:var(--panel);border:1px solid var(--border);border-radius:4px;padding:4px 8px;font-size:11px;color:var(--text);white-space:nowrap;pointer-events:none;z-index:10;">
          <div>${formatTooltipValue(values[activeIdx])}</div>
          ${runIds?.[activeIdx] && html`<div style="color:var(--muted);">${runIds[activeIdx]}</div>`}
        </div>
      `}
      <svg width=${width} height=${height} style="overflow:visible">
        <polyline points=${points} fill="none" stroke=${color} stroke-width="1.5" style="pointer-events:none;" />
        ${values.map((_v, i) => {
          const x = (i / (values.length - 1)) * width
          const rectX = i === 0 ? 0 : (i === values.length - 1 ? x - pointSpacing / 2 : x - pointSpacing / 2)
          const rectW = (i === 0 || i === values.length - 1) ? pointSpacing / 2 : pointSpacing
          return html`
            <rect
              key=${i}
              x=${rectX} y=${0} width=${rectW} height=${height}
              fill="transparent"
              onMouseEnter=${() => setActiveIdx(i)}
              onMouseLeave=${() => setActiveIdx(null)}
            />
          `
        })}
      </svg>
    </div>
  `
}
