import { html } from 'htm/preact'
import { useState, useEffect } from 'preact/hooks'
import type { Target, TargetHealthData } from '../../shared/types.ts'
import { api } from '../lib/api.ts'
import { Sparkline } from '../components/sparkline.ts'
import { LineChart } from '../components/line-chart.ts'
import { HealthSummaryBar } from '../components/health-summary.ts'

function trendArrow(trend: 'improving' | 'stable' | 'degrading'): { symbol: string; color: string; label: string } {
  switch (trend) {
    case 'improving': return { symbol: '\u2191', color: 'var(--success)', label: 'trend: up' }
    case 'degrading': return { symbol: '\u2193', color: 'var(--error)', label: 'trend: down' }
    case 'stable':
    default: return { symbol: '\u2192', color: 'var(--muted)', label: 'trend: flat' }
  }
}

function deriveOverallHealth(
  healthData: Record<string, TargetHealthData>
): 'improving' | 'stable' | 'degrading' | null {
  const values = Object.values(healthData)
  if (values.length === 0) return null
  const improvingCount = values.filter(v => v.health === 'improving').length
  const degradingCount = values.filter(v => v.health === 'degrading').length
  if (improvingCount > degradingCount) return 'improving'
  if (degradingCount > improvingCount) return 'degrading'
  return 'stable'
}

export function Health() {
  const [targets, setTargets] = useState<Target[]>([])
  const [healthData, setHealthData] = useState<Record<string, TargetHealthData>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.getTargets()
      .then(list => {
        setTargets(list)
        return Promise.all(
          list.map(t =>
            api.getHealth(t.name).then(h => ({ name: t.name, data: h })).catch(() => null)
          )
        )
      })
      .then(results => {
        const data: Record<string, TargetHealthData> = {}
        for (const r of results) {
          if (r) data[r.name] = r.data
        }
        setHealthData(data)
        setLoading(false)
      })
      .catch(err => {
        setError(String(err))
        setLoading(false)
      })
  }, [])

  const overallHealth = deriveOverallHealth(healthData)

  // Check if any target has fewer than 3 runs analyzed
  const sparseTargets = Object.values(healthData).filter(d => d.runs_analyzed < 3)
  const hasSparseData = sparseTargets.length > 0

  return html`
    <div style="flex:1;overflow-y:auto;background:var(--bg);">
      <div style="padding:16px 16px 0;">
        <div style="font-size:16px;font-weight:600;color:var(--text);">Flywheel Health</div>
      </div>

      <${HealthSummaryBar} health=${overallHealth} />

      ${loading && html`
        <div style="padding:16px;color:var(--muted);font-size:14px;">Loading...</div>
      `}

      ${!loading && error && html`
        <div style="background:var(--panel);border:1px solid var(--accent);border-radius:6px;padding:8px 16px;color:var(--muted);margin:16px;">
          Could not load health data. Check that the server is running.
        </div>
      `}

      ${!loading && !error && hasSparseData && html`
        <div style="background:var(--panel);border:1px solid var(--accent);border-radius:6px;padding:8px 16px;font-size:14px;color:var(--muted);margin:16px;">
          Gathering data (${Object.values(healthData).reduce((sum, d) => sum + d.runs_analyzed, 0) / Object.keys(healthData).length || 0}/10 runs) -- health metrics are available after 3 completed runs.
        </div>
      `}

      ${!loading && !error && targets.map(target => {
        const data = healthData[target.name]
        if (!data) return null

        const targetArrow = trendArrow(data.health)

        return html`
          <div
            key=${target.name}
            style="background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:12px;margin:0 16px 16px;"
          >
            <!-- Target header -->
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
              <div style="font-size:16px;font-weight:600;color:var(--text);">${target.name}</div>
              <span
                aria-label=${targetArrow.label}
                style="font-size:14px;color:${targetArrow.color};"
              >${targetArrow.symbol}</span>
              <div style="font-size:12px;color:var(--muted);margin-left:auto;">${data.runs_analyzed} runs analyzed</div>
            </div>

            <!-- Indicators with sparklines -->
            ${Object.entries(data.indicators).map(([name, indicator]) => {
              const arrow = trendArrow(indicator.trend)
              return html`
                <div
                  key=${name}
                  style="display:flex;align-items:center;gap:12px;padding:4px 0;border-bottom:1px solid var(--border);"
                >
                  <div style="font-size:14px;color:var(--text);flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${name}</div>
                  <${Sparkline} values=${indicator.history} />
                  <div style="font-size:13px;font-weight:600;color:var(--text);min-width:40px;text-align:right;">${indicator.current}</div>
                  <span
                    aria-label=${arrow.label}
                    style="font-size:13px;color:${arrow.color};"
                  >${arrow.symbol}</span>
                </div>
              `
            })}

            <!-- Acceptance rate -->
            <div style="font-size:14px;color:var(--text);padding:8px 0 4px;">
              Proposals accepted:
              ${Math.round(data.acceptance_rate * (Object.values(healthData).reduce((s, d) => s + d.runs_analyzed, 0)))} /
              ${Object.values(healthData).reduce((s, d) => s + d.runs_analyzed, 0)}
              (${Math.round(data.acceptance_rate * 100)}%)
              <span
                aria-label=${data.acceptance_rate > 0.5 ? 'trend: up' : 'trend: flat'}
                style="margin-left:4px;color:${data.acceptance_rate > 0.5 ? 'var(--success)' : 'var(--muted)'};"
              >${data.acceptance_rate > 0.5 ? '\u2191' : '\u2192'}</span>
            </div>
          </div>
        `
      })}

      <!-- Reject rate charts section -->
      ${!loading && !error && Object.keys(healthData).length > 0 && html`
        <div style="margin:0 16px 16px;">
          <div style="font-size:12px;font-weight:600;color:var(--muted);margin-bottom:8px;">Reject Rate by Indicator</div>
          <div style="display:flex;flex-wrap:wrap;gap:16px;">
            ${Object.values(healthData).flatMap(data =>
              Object.entries(data.per_indicator_rates ?? {}).map(([name, rateData]) =>
                html`<${LineChart} key=${name} values=${rateData.history} label="${name} (${Math.round(rateData.rate * 100)}%)" />`
              )
            )}
          </div>
        </div>
      `}
    </div>
  `
}
