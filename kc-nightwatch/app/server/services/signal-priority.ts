import type { RunSummaryAction } from '../../shared/types.ts'

// ============================================================
// Signal Priority Scoring
// ============================================================
// Priority score = confidence_weight × alignment_weight
// Range: 0.0 (low confidence + no alignment) to 1.0 (high confidence + full alignment)
// Used to sort ActionCards so most valuable signals surface first.

const CONFIDENCE_WEIGHTS: Record<string, number> = {
  high: 1.0,
  medium: 0.67,
  low: 0.33,
}

const ALIGNMENT_WEIGHTS: Record<string, number> = {
  yes: 1.0,
  uncertain: 0.5,
  no: 0.0,
}

/**
 * Compute a priority score for a single action based on its assessment.
 * Returns a value in [0.0, 1.0] rounded to 2 decimal places.
 */
export function computePriorityScore(action: Pick<RunSummaryAction, 'assessment'>): number {
  const conf = CONFIDENCE_WEIGHTS[action.assessment.confidence] ?? 0.33
  const align = ALIGNMENT_WEIGHTS[action.assessment.closer_to_north_star] ?? 0.5
  return Math.round(conf * align * 100) / 100
}

export interface SignalPriorityEntry {
  signal_id: string
  score: number
  confidence: 'high' | 'medium' | 'low'
  closer_to_north_star: 'yes' | 'no' | 'uncertain'
}

/**
 * Compute priority entries for a list of actions, sorted descending by score.
 */
export function computePriorities(actions: RunSummaryAction[]): SignalPriorityEntry[] {
  const entries: SignalPriorityEntry[] = actions.map(a => ({
    signal_id: a.signal_id,
    score: computePriorityScore(a),
    confidence: a.assessment.confidence,
    closer_to_north_star: a.assessment.closer_to_north_star,
  }))
  // Sort descending by score, then by signal_id for deterministic tie-breaking
  entries.sort((a, b) => b.score - a.score || a.signal_id.localeCompare(b.signal_id))
  return entries
}
