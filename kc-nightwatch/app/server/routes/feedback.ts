import { Hono } from 'hono'
import { appendFeedback, getFeedbackForRun, getCalibrationData } from '../services/feedback-store.ts'
import type { FeedbackEntry } from '../../shared/types.ts'

export const feedbackRoutes = new Hono()

// POST /api/feedback — submit feedback for a signal
feedbackRoutes.post('/api/feedback', async (c) => {
  const body = await c.req.json<{
    signal_id: string
    target: string
    run_id: string
    verdict: 'accepted' | 'rejected'
    reason?: string
  }>()

  if (!body.signal_id || !body.target || !body.run_id || !body.verdict) {
    return c.json({ error: 'signal_id, target, run_id, and verdict are required' }, 400)
  }

  if (body.verdict !== 'accepted' && body.verdict !== 'rejected') {
    return c.json({ error: 'verdict must be accepted or rejected' }, 400)
  }

  const entry: FeedbackEntry = {
    signal_id: body.signal_id,
    target: body.target,
    run_id: body.run_id,
    verdict: body.verdict,
    reason: body.reason,
    source: 'user',
    submitted_at: new Date().toISOString(),
  }

  await appendFeedback(entry)
  return c.json({ ok: true }, 201)
})

// GET /api/feedback/calibration — get reject rate calibration data
// NOTE: This route MUST be defined before /api/feedback/:runId to avoid
// "calibration" being parsed as a runId parameter
feedbackRoutes.get('/api/feedback/calibration', async (c) => {
  const data = await getCalibrationData()
  return c.json(data)
})

// GET /api/feedback/:runId — get feedback for a specific run
feedbackRoutes.get('/api/feedback/:runId', async (c) => {
  const runId = c.req.param('runId')
  const feedback = await getFeedbackForRun(runId)
  return c.json(feedback)
})
