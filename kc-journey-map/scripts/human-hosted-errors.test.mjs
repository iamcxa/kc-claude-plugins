import assert from 'node:assert/strict'
import { test } from 'node:test'
import { build } from 'esbuild'
import { Miniflare } from 'miniflare'

test('local Cloudflare preserves denial and logs sanitized registry/provider failures', async () => {
 const origin = 'https://entry.synthetic.invalid'
 const config = { version: 1, backendId: 'synthetic', origin, mode: 'cloudflare', issuer: 'https://synthetic.cloudflareaccess.com', audience: 'synthetic', members: [] }
 const bundle = await build({ entryPoints: [new URL('../server/host/cloudflare.ts', import.meta.url).pathname], bundle: true, write: false, format: 'esm', platform: 'browser', conditions: ['workerd', 'worker', 'browser'], external: ['cloudflare:workers'], logLevel: 'silent' })
 const script = bundle.outputFiles[0].text.replace('export {', `
class FaultRegistry extends JourneyRegistry {
 async fetch(req) { this.failWrites = true; return super.fetch(req); }
 sync() {
  const store = super.sync();
  return { ...store, put: (key, value) => {
   if (this.failWrites && (key.startsWith('human-receipt:') || key.startsWith('human-provider:')))
    throw new Error('SQLITE_FULL: database or disk is full; token=secret-token cookie=secret-cookie email=private@example.invalid subject=secret-subject body=secret-body');
   store.put(key, value);
  } };
 }
}
export {`).replace('JourneyRegistry,', 'FaultRegistry as JourneyRegistry,')
 assert.ok(script.includes('FaultRegistry as JourneyRegistry'))
 const lines = []
 const mf = new Miniflare({ script, modules: true, compatibilityDate: '2026-07-01', compatibilityFlags: ['nodejs_compat'], host: '127.0.0.1', port: 0,
  bindings: { JOURNEY_ORIGIN: origin, JOURNEY_GRANTS: JSON.stringify([{ credentialId: 'seed', secretDigest: 'a'.repeat(64), principalId: 'seed', rooms: ['one'], expiresAt: Date.now() + 3600_000, revoked: false }]), JOURNEY_HUMAN_CONFIG: JSON.stringify(config) },
  durableObjects: { ROOMS: { className: 'JourneyRoom', useSQLite: true }, REGISTRY: { className: 'JourneyRegistry', useSQLite: true } },
  handleRuntimeStdio: (stdout, stderr) => { stdout.on('data', data => lines.push(String(data))); stderr.on('data', data => lines.push(String(data))) },
  outboundService: () => { throw new Error('no external requests allowed') },
 })
 try {
  await mf.ready
  for (let i = 0; i < 2; i++) {
   const response = await mf.dispatchFetch(origin + '/auth/entry')
   assert.equal(response.status, 401)
   assert.deepEqual(await response.json(), { error: 'human_sign_in_required', category: 'human_sign_in_required' })
   assert.equal(response.headers.get('set-cookie'), null)
  }
  const response = await mf.dispatchFetch(origin + '/auth/provider/start', { method: 'POST', headers: { Origin: origin, 'X-Journey-Entry': '1', 'Content-Type': 'application/json' }, body: '{}' })
  assert.equal(response.status, 503)
  assert.deepEqual(await response.json(), { error: 'metadata unavailable' })
  assert.equal(response.headers.get('set-cookie'), null)
  for (let i = 0; i < 50 && !lines.join('').includes('provider-start'); i++) await new Promise(resolve => setTimeout(resolve, 10))
  const logged = lines.join('')
  assert.match(logged, /record-denial/)
  assert.match(logged, /provider-start/)
  assert.match(logged, /SQLITE_FULL/)
  assert.match(logged, /\"boundary\":\"registry\"/)
  assert.match(logged, /\"name\":\"Error\"/)
  assert.match(logged, /database or disk is full/)
  for (const secret of ['secret-token', 'secret-cookie', 'private@example.invalid', 'secret-subject', 'secret-body']) assert.ok(!logged.includes(secret), secret)
 } finally { await mf.dispose() }
})
