import { Hono } from 'hono'
import { listRuns, getRun } from '../services/run-store.ts'
import { getCalibrationData } from '../services/feedback-store.ts'
import type { TargetHealthData, HealthIndicatorData } from '../../shared/types.ts'

export const healthApiRoutes = new Hono()

healthApiRoutes.get('/api/health/:target', async (c) => {
  const target = c.req.param('target')

  // Get last 10 runs for this target (listRuns returns sorted desc by started_at)
  const allRuns = await listRuns({ target })
  const last10 = allRuns.slice(0, 10)

  // Process runs in chronological order (oldest first) for history arrays
  const runsWithSummary = await Promise.all(
    [...last10].reverse().map(r => getRun(r.id))
  )

  // Build indicator history from run summaries
  const indicatorHistory: Record<string, number[]> = {}
  const indicatorTrends: Record<string, string> = {}

  for (const runData of runsWithSummary) {
    if (!runData?.summary) continue
    const targetSummary = runData.summary.per_target[target]
    if (!targetSummary) continue

    // Aggregate indicator baselines
    for (const [name, baseline] of Object.entries(targetSummary.indicator_baseline)) {
      if (!indicatorHistory[name]) indicatorHistory[name] = []
      indicatorHistory[name].push(baseline.value)
      indicatorTrends[name] = baseline.trend  // latest trend wins
    }
  }

  // Build indicators map
  const indicators: Record<string, HealthIndicatorData> = {}
  for (const [name, history] of Object.entries(indicatorHistory)) {
    const trend = (indicatorTrends[name] as 'improving' | 'stable' | 'degrading') ?? 'stable'
    indicators[name] = {
      current: history[history.length - 1] ?? 0,
      trend,
      history,
    }
  }

  // Determine overall health from indicator trends
  const trends = Object.values(indicators).map(i => i.trend)
  const improvingCount = trends.filter(t => t === 'improving').length
  const degradingCount = trends.filter(t => t === 'degrading').length
  let health: 'improving' | 'stable' | 'degrading' = 'stable'
  if (trends.length > 0) {
    if (improvingCount > degradingCount) health = 'improving'
    else if (degradingCount > improvingCount) health = 'degrading'
  }

  // Get reject rate from calibration data (aggregate across all indicators)
  const calibration = await getCalibrationData()
  const relevantCalibration = calibration.filter(c => c.total_feedback > 0)
  const avgRejectRate = relevantCalibration.length > 0
    ? relevantCalibration.reduce((sum, c) => sum + c.reject_rate, 0) / relevantCalibration.length
    : 0

  // Acceptance rate: (total_feedback - total_rejects) / total_feedback
  const totalFeedback = relevantCalibration.reduce((sum, c) => sum + c.total_feedback, 0)
  const totalRejects = relevantCalibration.reduce((sum, c) => sum + c.reject_count, 0)
  const acceptanceRate = totalFeedback > 0
    ? Math.round(((totalFeedback - totalRejects) / totalFeedback) * 100) / 100
    : 0

  const result: TargetHealthData = {
    target,
    health,
    indicators,
    reject_rate: Math.round(avgRejectRate * 100) / 100,
    acceptance_rate: acceptanceRate,
    runs_analyzed: last10.length,
  }

  return c.json(result)
})
