import assert from 'node:assert/strict'
import { build } from 'esbuild'
import { Miniflare } from 'miniflare'

const config = { siteOrigin: 'https://entry.example.invalid', backendOrigin: 'https://backend.example.invalid', pathPrefix: '/journey', rooms: ['A', 'B'] }
const bundled = await build({ entryPoints: [new URL('../server/sites-entry.ts', import.meta.url).pathname], bundle: true, format: 'esm', platform: 'browser', write: false })
const source = bundled.outputFiles[0].text
const { createSitesJourneyEntry, validateSitesJourneyConfig } = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'))
const calls = []
const token = 'synthetic.' + 'x'.repeat(43)
const entry = createSitesJourneyEntry(config, async (url, init) => { calls.push({ url, init }); return Response.json({ rooms: ['A', 'B', 'Hidden'], active: [{ roomId: 'A' }, { roomId: 'Hidden' }] }, { headers: { 'Set-Cookie': 'must-not-escape=value' } }) })
const headers = { 'oai-authenticated-user-id': 'synthetic-owner', Origin: config.siteOrigin }
const request = (path, options = {}) => new Request(config.siteOrigin + path, { headers, ...options })
const env = { JOURNEY_SITES_BEARER: token }
assert.equal(await entry(request('/original-route'), env), null)
assert.equal((await entry(request('/journey/api/health', { headers: {} }), env)).status, 403)
assert.equal((await entry(request('/journey/api/health'), {})).status, 503)
assert.equal((await entry(request('/journey/api/save?room=Hidden'), env)).status, 403)
assert.equal((await entry(request('/journey/api/save?room=A&room=B'), env)).status, 400)
assert.equal((await entry(request('/journey/api/connect/A', { headers: { ...headers, Origin: 'https://wrong.example.invalid', Upgrade: 'websocket' } }), env)).status, 403)
assert.equal((await entry(request('/journey/api/mcp', { method: 'POST' }), env)).status, 404)
assert.equal(calls.length, 0)
const health = await entry(request('/journey/api/health', { headers: { ...headers, Authorization: 'attacker-supplied', Cookie: 'must-not-forward' } }), env)
assert.deepEqual(await health.json(), { rooms: ['A', 'B'], active: [{ roomId: 'A' }] })
assert.equal(health.headers.get('set-cookie'), null)
assert.equal(calls[0].url, config.backendOrigin + '/health')
assert.equal(calls[0].init.headers.get('authorization'), 'Bearer ' + token)
assert.equal(calls[0].init.headers.get('cookie'), null)
assert.equal(calls[0].init.redirect, 'manual')
const redirected = createSitesJourneyEntry(config, async () => Response.redirect('https://wrong.example.invalid'))
assert.equal((await redirected(request('/journey/api/health'), env)).status, 502)
const bad = [{ ...config, backendOrigin: 'http://backend.example.invalid' }, { ...config, pathPrefix: '/a/b' }, { ...config, rooms: ['../A'] }]
for (const value of bad) assert.throws(() => validateSitesJourneyConfig(value))
console.log('PASS fixed target, identity/origin/room checks, inventory filtering, secret confinement and redirect refusal')
const mf = new Miniflare({ workers: [
 { name: 'entry', modules: true, compatibilityDate: '2026-07-01', script: source + '\nexport default { fetch(request, env) { return createSitesJourneyEntry(' + JSON.stringify(config) + ', (url, init) => env.BACKEND.fetch(url, init))(request, env) } }', bindings: env, serviceBindings: { BACKEND: 'backend' } },
 { name: 'backend', modules: true, compatibilityDate: '2026-07-01', script: `export default { fetch(request) {
  if (request.headers.get('authorization') !== ${JSON.stringify('Bearer ' + token)}) return new Response('denied', {status:403});
  const pair = new WebSocketPair(); pair[1].accept(); pair[1].addEventListener('message', event => pair[1].send(event.data));
  pair[1].addEventListener('close', () => pair[1].close()); return new Response(null, {status:101, webSocket:pair[0]});
 } }` },
] })
try {
 const response = await mf.dispatchFetch(config.siteOrigin + '/journey/api/connect/A?sessionId=synthetic', { headers: { ...headers, Upgrade: 'websocket' } })
 assert.equal(response.status, 101)
 const socket = response.webSocket; socket.accept()
 const received = new Promise((resolve, reject) => { const timeout = setTimeout(() => reject(new Error('socket timeout')), 3000); socket.addEventListener('message', event => { clearTimeout(timeout); resolve(event.data) }, { once: true }) })
 socket.send('synthetic handshake readback'); assert.equal(await received, 'synthetic handshake readback'); socket.close(1000)
 console.log('PASS real local Worker WebSocket upgrade and message forwarding; hosted Sites NOT RUN')
} finally { await mf.dispose() }
