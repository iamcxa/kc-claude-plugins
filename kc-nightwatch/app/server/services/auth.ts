import type { MiddlewareHandler } from 'hono'

// IMPORTANT: Apply at app level (app.use('*', tokenAuth(token))), NOT per-route.
// Per-route auth gets missed when new routes are added — see PITFALLS.md Pitfall 6.
export function tokenAuth(token: string): MiddlewareHandler {
  return async (c, next) => {
    const authHeader = c.req.header('Authorization')
    if (authHeader !== `Bearer ${token}`) {
      return c.json({ error: 'Unauthorized' }, 401)
    }
    await next()
  }
}
