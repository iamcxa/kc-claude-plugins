import { Hono } from 'hono'
import { queryOutcomes, readOutcomes } from '../services/outcome-store.ts'

export const outcomesRoutes = new Hono()

// GET /api/outcomes — list outcomes with optional filters (per D-02)
outcomesRoutes.get('/api/outcomes', async (c) => {
  const target = c.req.query('target') || undefined
  const type = c.req.query('type') || undefined
  const status = c.req.query('status') || undefined
  const records = await queryOutcomes({ target, type, status })
  return c.json(records)
})

// GET /api/outcomes/:id/status — cached status for a single outcome (per D-13, D-14, OUT-04)
outcomesRoutes.get('/api/outcomes/:id/status', async (c) => {
  const id = c.req.param('id')
  const records = await readOutcomes()
  const record = records.find(r => r.id === id)
  if (!record) return c.json({ error: 'not found' }, 404)
  return c.json({ status: record.status })
})
