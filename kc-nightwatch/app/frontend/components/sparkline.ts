import { html } from 'htm/preact'

interface Props {
  values: number[]
  width?: number
  height?: number
}

export function Sparkline({ values, width = 80, height = 20 }: Props) {
  if (values.length < 2) {
    return html`<span style="color:var(--muted);font-size:11px;">--</span>`
  }

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

  return html`
    <svg width=${width} height=${height} style="overflow:visible">
      <polyline points=${points} fill="none" stroke=${color} stroke-width="1.5" />
    </svg>
  `
}
