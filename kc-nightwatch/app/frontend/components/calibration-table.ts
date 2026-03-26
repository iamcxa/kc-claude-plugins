import { html } from 'htm/preact'
import type { CalibrationData } from '../../shared/types.ts'

export function sortByRejectRate(data: CalibrationData[]): CalibrationData[] {
  return [...data].sort((a, b) => b.reject_rate - a.reject_rate)
}

export function formatThreshold(threshold: number | null, nullReason?: string): string {
  if (threshold === null) return nullReason ?? 'Accumulating data'
  return `${Math.round(threshold * 100)}%`
}

interface CalibrationTableProps {
  calibration: CalibrationData[] | null  // null = loading; [] = empty after fetch
  loading: boolean
}

export function CalibrationTable({ calibration, loading }: CalibrationTableProps) {
  return html`
    <div style="background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:12px;margin:0 16px 16px;">
      <div style="font-size:11px;font-weight:600;color:var(--muted);margin-bottom:8px;">Calibration</div>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        <thead>
          <tr>
            <th style="font-size:11px;font-weight:600;color:var(--muted);text-align:left;padding:8px 12px;border-bottom:1px solid var(--border);">Indicator</th>
            <th style="font-size:11px;font-weight:600;color:var(--muted);text-align:left;padding:8px 12px;border-bottom:1px solid var(--border);">Threshold</th>
            <th style="font-size:11px;font-weight:600;color:var(--muted);text-align:left;padding:8px 12px;border-bottom:1px solid var(--border);">Reject %</th>
            <th style="font-size:11px;font-weight:600;color:var(--muted);text-align:left;padding:8px 12px;border-bottom:1px solid var(--border);">Feedback</th>
          </tr>
        </thead>
        <tbody>
          ${loading && html`
            <tr>
              <td colspan="4" style="font-size:14px;color:var(--muted);padding:8px 12px;">Loading...</td>
            </tr>
          `}
          ${!loading && calibration !== null && calibration.length === 0 && html`
            <tr>
              <td colspan="4" style="font-size:14px;color:var(--muted);padding:8px 12px;">No feedback collected yet \u2014 run the pipeline to generate data.</td>
            </tr>
          `}
          ${!loading && calibration !== null && calibration.length > 0 && sortByRejectRate(calibration).map((row, i) => {
            const isLast = i === calibration.length - 1
            const rowStyle = `font-size:14px;color:var(--text);padding:8px 12px;${isLast ? '' : 'border-bottom:1px solid var(--border);'}`
            const thresholdIsNull = row.current_threshold === null
            return html`
              <tr key=${row.indicator}>
                <td style="${rowStyle}">${row.indicator}</td>
                <td style="${rowStyle}">
                  ${thresholdIsNull
                    ? html`<span style="font-style:italic;color:var(--muted);">${formatThreshold(row.current_threshold, row.threshold_null_reason)}</span>`
                    : formatThreshold(row.current_threshold)
                  }
                </td>
                <td style="${rowStyle}">${Math.round(row.reject_rate * 100)}%</td>
                <td style="${rowStyle}">${row.total_feedback}</td>
              </tr>
            `
          })}
        </tbody>
      </table>
    </div>
  `
}
