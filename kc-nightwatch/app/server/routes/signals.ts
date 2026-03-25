import { Hono } from 'hono'
import { listRuns, getRun } from '../services/run-store.ts'
import { getCalibrationData } from '../services/feedback-store.ts'
import type { SignalPriorityItem } from '../../shared/types.ts'

export const signalsRoutes = new Hono()

const CONFIDENCE_WEIGHT: Record<string, number> = {
  high: 1.0,
  medium: 0.6,
  low: 0.3,
}

signalsRoutes.get('/api/signals/priority', async (c) => {
  // D-09: cap at 30 runs
  const allRuns = await listRuns({})
  const last30 = allRuns.slice(0, 30)

  // Collect all actions from the last 30 runs
  const indicatorCounts = new Map<string, { weightSum: number; count: number }>()

  for (const run of last30) {
    const detail = await getRun(run.id)
    if (!detail?.summary?.per_target) continue
    for (const targetSummary of Object.values(detail.summary.per_target)) {
      for (const action of targetSummary.actions ?? []) {
        const indicator = action.indicator
        const weight = CONFIDENCE_WEIGHT[action.assessment.confidence] ?? 0.3
        const current = indicatorCounts.get(indicator) ?? { weightSum: 0, count: 0 }
        current.weightSum += weight
        current.count++
        indicatorCounts.set(indicator, current)
      }
    }
  }

  // Get calibration data for reject rates
  const calibration = await getCalibrationData()
  const rejectRateByIndicator = new Map(calibration.map(cal => [cal.indicator, cal]))

  // Compute priority scores
  const items: SignalPriorityItem[] = []
  for (const [indicator, { weightSum, count }] of indicatorCounts) {
    const avgWeight = count > 0 ? weightSum / count : 0
    const calData = rejectRateByIndicator.get(indicator)
    const rejectRate = calData?.reject_rate ?? 0
    const score = Math.round(avgWeight * (1 - rejectRate) * 100) / 100
    items.push({
      indicator,
      score,
      confidence_weight: Math.round(avgWeight * 100) / 100,
      reject_rate: rejectRate,
      total_feedback: calData?.total_feedback ?? 0,
    })
  }

  // Sort descending by score
  items.sort((a, b) => b.score - a.score)

  return c.json(items)
})
