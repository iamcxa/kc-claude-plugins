import { Hono } from 'hono'
import { getRun } from '../services/run-store.ts'
import { computePriorities } from '../services/signal-priority.ts'
import type { RunSummaryAction } from '../../shared/types.ts'

export const signalPriorityRoutes = new Hono()

// GET /api/signals/priority/run?run_id=<id>
// Returns priority scores for all signals in a run, sorted descending.
// Distinct from Phase 15 /api/signals/priority (aggregate by indicator).
signalPriorityRoutes.get('/api/signals/priority/run', async (c) => {
  const runId = c.req.query('run_id')
  if (!runId) {
    return c.json({ error: 'run_id query parameter is required' }, 400)
  }

  const run = await getRun(runId)
  if (!run) {
    return c.json({ error: 'run not found' }, 404)
  }

  // Collect all actions across all targets
  const actions: RunSummaryAction[] = []
  if (run.summary?.per_target) {
    for (const targetData of Object.values(run.summary.per_target)) {
      if (targetData.actions) {
        actions.push(...targetData.actions)
      }
    }
  }

  const priorities = computePriorities(actions)
  return c.json(priorities)
})
