import { html } from 'htm/preact'

interface Props {
  values: number[]
  label: string
  width?: number
  height?: number
}

export function LineChart({ values, label, width = 240, height = 80 }: Props) {
  if (values.length < 2) {
    return html`
      <div style="margin-bottom:8px;">
        <div style="font-size:11px;color:var(--muted);margin-bottom:4px;">${label}</div>
        <div style="width:${width}px;height:${height}px;display:flex;align-items:center;justify-content:center;font-size:11px;color:var(--muted);">Not enough data</div>
      </div>
    `
  }

  const padding = { top: 4, right: 4, bottom: 16, left: 30 }
  const chartW = width - padding.left - padding.right
  const chartH = height - padding.top - padding.bottom

  // Y-axis: 0.0 to 1.0 (reject rate fraction)
  const yMin = 0
  const yMax = 1

  const points = values.map((v, i) => {
    const x = padding.left + (i / (values.length - 1)) * chartW
    const y = padding.top + chartH - ((v - yMin) / (yMax - yMin)) * chartH
    return `${x},${y}`
  }).join(' ')

  return html`
    <div style="margin-bottom:8px;">
      <div style="font-size:11px;color:var(--muted);margin-bottom:4px;">${label}</div>
      <svg width=${width} height=${height} style="overflow:visible">
        <!-- Y axis -->
        <line x1=${padding.left} y1=${padding.top} x2=${padding.left} y2=${padding.top + chartH} stroke="var(--border)" stroke-width="1" />
        <!-- X axis -->
        <line x1=${padding.left} y1=${padding.top + chartH} x2=${padding.left + chartW} y2=${padding.top + chartH} stroke="var(--border)" stroke-width="1" />
        <!-- Y ticks -->
        <text x=${padding.left - 4} y=${padding.top + 4} fill="var(--muted)" font-size="9" text-anchor="end">100%</text>
        <text x=${padding.left - 4} y=${padding.top + chartH / 2 + 3} fill="var(--muted)" font-size="9" text-anchor="end">50%</text>
        <text x=${padding.left - 4} y=${padding.top + chartH + 3} fill="var(--muted)" font-size="9" text-anchor="end">0%</text>
        <!-- X ticks -->
        <text x=${padding.left} y=${padding.top + chartH + 12} fill="var(--muted)" font-size="9" text-anchor="middle">1</text>
        <text x=${padding.left + chartW} y=${padding.top + chartH + 12} fill="var(--muted)" font-size="9" text-anchor="middle">${values.length}</text>
        <!-- Data line -->
        <polyline points=${points} fill="none" stroke="var(--accent)" stroke-width="1.5" />
      </svg>
    </div>
  `
}
