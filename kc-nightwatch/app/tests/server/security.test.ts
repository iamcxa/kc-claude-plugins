import { describe, it, expect } from 'bun:test'
import { Hono } from 'hono'
import { tokenAuth } from '../../server/services/auth.ts'

function makeApp(token: string) {
  const app = new Hono()
  app.use('*', tokenAuth(token))
  app.get('/api/test', (c) => c.json({ ok: true }))
  return app
}

describe('tokenAuth middleware', () => {
  it('returns 401 when no Authorization header', async () => {
    const app = makeApp('secret')
    const res = await app.request('/api/test')
    expect(res.status).toBe(401)
  })

  it('returns 401 for wrong token', async () => {
    const app = makeApp('secret')
    const res = await app.request('/api/test', {
      headers: { Authorization: 'Bearer wrong-token' }
    })
    expect(res.status).toBe(401)
  })

  it('returns 200 for correct Bearer token', async () => {
    const app = makeApp('secret')
    const res = await app.request('/api/test', {
      headers: { Authorization: 'Bearer secret' }
    })
    expect(res.status).toBe(200)
  })

  it('returns 401 for malformed header (no Bearer prefix)', async () => {
    const app = makeApp('secret')
    const res = await app.request('/api/test', {
      headers: { Authorization: 'secret' }
    })
    expect(res.status).toBe(401)
  })
})
