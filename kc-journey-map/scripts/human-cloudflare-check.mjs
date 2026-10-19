import assert from 'node:assert/strict'
import { build } from 'esbuild'
import { Miniflare, Response as WorkerResponse } from 'miniflare'
import { mkdtemp, mkdir, writeFile } from 'node:fs/promises'
import { join } from 'node:path'
const root = new URL('..', import.meta.url).pathname
await mkdir(join(root, '.host-check'), { recursive: true })
const scratch = await mkdtemp(join(root, '.host-check/human-cloudflare-'))
const origin = 'https://entry.synthetic.invalid', issuer = 'https://team.synthetic.cloudflareaccess.com'
const now = Math.floor(Date.now() / 1000)
const config = { version: 1, backendId: 'cf-synthetic', origin, mode: 'cloudflare', issuer, audience: 'synthetic', members: [{ id: 'person', issuer, subject: 'subject', label: 'Synthetic person', role: 'member', rooms: [{ id: 'one', expiresAt: Date.now() + 3600_000 }, { id: 'missing', expiresAt: Date.now() + 3600_000 }] }] }
const hash = async token => Buffer.from(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(token))).toString('hex')
const secret = 's'.repeat(43), grants = [{ credentialId: 'seed', secretDigest: await hash(secret), principalId: 'seed', rooms: ['one', 'two', 'missing'], expiresAt: Date.now() + 3600_000, revoked: false }]
const keys = await crypto.subtle.generateKey({ name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' }, true, ['sign', 'verify'])
const jwk = { ...await crypto.subtle.exportKey('jwk', keys.publicKey), kid: 'synthetic', alg: 'RS256' }
const data = Buffer.from(JSON.stringify({ alg: 'RS256', kid: 'synthetic', typ: 'JWT' })).toString('base64url') + '.' + Buffer.from(JSON.stringify({ type: 'app', iss: issuer, aud: ['synthetic'], sub: 'subject', identity_nonce: 'nonce', iat: now, nbf: now, exp: now + 300 })).toString('base64url')
const assertion = data + '.' + Buffer.from(await crypto.subtle.sign('RSASSA-PKCS1-v1_5', keys.privateKey, new TextEncoder().encode(data))).toString('base64url')
const bundle = await build({ entryPoints: [join(root, 'server/host/cloudflare.ts')], bundle: true, write: false, format: 'esm', platform: 'browser', conditions: ['workerd', 'worker', 'browser'], external: ['cloudflare:workers'], logLevel: 'silent' })
let providerDown = false
const mf = new Miniflare({ script: bundle.outputFiles[0].text, modules: true, compatibilityDate: '2026-07-01', compatibilityFlags: ['nodejs_compat'], host: '127.0.0.1', port: 0,
 bindings: { JOURNEY_ORIGIN: origin, JOURNEY_GRANTS: JSON.stringify(grants), JOURNEY_HUMAN_CONFIG: JSON.stringify(config) },
 durableObjects: { ROOMS: { className: 'JourneyRoom', useSQLite: true }, REGISTRY: { className: 'JourneyRegistry', useSQLite: true } }, durableObjectsPersist: join(scratch, 'objects'),
 outboundService: async req => {
  if (providerDown) return new WorkerResponse('synthetic outage', { status: 503 })
  if (req.url === issuer + '/cdn-cgi/access/certs') return WorkerResponse.json({ keys: [jwk] })
  assert.equal(req.url, issuer + '/cdn-cgi/access/get-identity')
  assert.equal(req.headers.get('cookie'), 'CF_Authorization=' + assertion)
  return WorkerResponse.json({ user_uuid: 'subject', iat: now - 600, service_token_status: false })
 } })
const report = { provider: 'SIMULATED signed assertion and trusted endpoint in local workerd; real account NOT RUN', checks: [] }
const pass = name => { console.log('PASS ' + name); report.checks.push(name) }
const request = (path, { method = 'GET', headers = {}, body, unbound = false } = {}) => {
 const url = new URL(origin + path)
 if (!unbound && headers.Cookie?.includes('journey_human=') && !path.startsWith('/auth/')) {
  url.searchParams.set('_human', 'person'); url.searchParams.set('_backend', 'cf-synthetic'); url.searchParams.set('_humanAt', String((now - 600) * 1000))
 }
 return mf.dispatchFetch(url.href, { method, headers: { Host: new URL(origin).host, ...headers }, ...(body === undefined ? {} : { body: JSON.stringify(body) }) })
}
const postHeaders = { Origin: origin, 'Content-Type': 'application/json', 'X-Journey-Entry': '1' }
try {
 await mf.ready
 const namespace = await mf.getDurableObjectNamespace('REGISTRY'), registry = namespace.get(namespace.idFromName('private-pilot'))
 const metadata = async (op, body) => { const response = await registry.fetch('https://registry/' + op, { method: 'POST', body: JSON.stringify(body) }); assert.equal(response.status, 200); return response.json() }
 assert.equal((await request('/doc?room=one', { headers: { Authorization: 'Bearer seed.' + secret } })).status, 200)
 const start = await request('/auth/provider/start', { method: 'POST', headers: postHeaders, body: {} })
 assert.equal(start.status, 200, await start.clone().text())
 const state = await start.json(), loginCookie = start.headers.get('set-cookie').split(';')[0]
 const login = await request(state.loginUrl, { headers: { Cookie: loginCookie, 'Cf-Access-Jwt-Assertion': assertion } })
 assert.equal(login.status, 200, await login.clone().text())
 const cookies = login.headers.getSetCookie(), cookie = cookies.filter(c => !c.startsWith('journey_login=')).map(c => c.split(';')[0]).join('; ')
 assert.ok(cookies.filter(c => !c.startsWith('journey_login=')).every(c => /Secure/.test(c) && /SameSite=Strict/.test(c)))
 assert.equal((await request('/auth/entry?room=one', { headers: { Cookie: cookie } })).status, 200)
 pass('Cloudflare adapter verifies signed assertion, correlated original event and bound member before exact registered-room entry')
 assert.equal((await request(state.loginUrl, { headers: { Cookie: loginCookie, 'Cf-Access-Jwt-Assertion': assertion } })).status, 403)
 const concurrentStart = await request('/auth/provider/start', { method: 'POST', headers: postHeaders, body: {} })
 const concurrentState = await concurrentStart.json(), concurrentCookie = concurrentStart.headers.get('set-cookie').split(';')[0]
 const attempts = await Promise.all([1, 2].map(() => request(concurrentState.loginUrl, { headers: { Cookie: concurrentCookie, 'Cf-Access-Jwt-Assertion': assertion } })))
 assert.deepEqual(attempts.map(response => response.status).sort(), [200, 403])
 pass('registry transaction consumes provider handoff once under concurrent requests; replay fails')
 for (const path of ['/doc?room=two', '/uploads/a?room=two', '/connect/two?sessionId=synthetic']) assert.equal((await request(path, { headers: { Cookie: cookie, Origin: origin } })).status, 403)
 assert.equal((await request('/auth/entry?room=missing', { headers: { Cookie: cookie } })).status, 404)
 assert.equal(await metadata('get', { key: 'room:missing' }), null)
 assert.equal((await request('/doc?room=one', { headers: { Cookie: cookie }, unbound: true })).status, 403)
 assert.equal((await request('/doc?room=one', { headers: { Cookie: cookie } })).status, 200)
 pass('HTTP/assets/socket admission denies forbidden room and missing entry never creates a document')
 const csrf = /journey_human_csrf=([^;]+)/.exec(cookie)[1]
 const renewed = await request('/auth/renew', { method: 'POST', body: {}, headers: { ...postHeaders, Cookie: cookie, 'X-Journey-Csrf': csrf } })
 assert.equal(renewed.status, 200)
 const session = await renewed.json()
 assert.equal(session.verifiedHumanSignInAt, (now - 600) * 1000)
 assert.equal(session.humanRevalidateBy, (now - 600) * 1000 + 7 * 24 * 3600_000)
 const token = /journey_human=([^;]+)/.exec(cookie)[1], sessionKey = 'browser-session:' + await hash(token)
 await metadata('put', { key: 'session:expired-synthetic', value: { credentialId: 'seed', expiresAt: 1 } })
 assert.equal((await request('/session', { method: 'POST', headers: { Origin: origin, Authorization: 'Bearer seed.' + secret } })).status, 200)
 const storedSession = await metadata('get', { key: sessionKey })
 assert.equal(storedSession.expiresAt, session.expiresAt); assert.equal(storedSession.verifiedHumanSignInAt, session.verifiedHumanSignInAt)
 assert.equal('csrfDigest' in session, false)
 pass('renewal preserves original seven-day deadline; legacy cleanup preserves live typed human sessions')
 assert.equal((await request('/auth/renew', { method: 'POST', body: {}, headers: { ...postHeaders, Cookie: cookie } })).status, 403)
 const providerStart = await request('/auth/provider/start', { method: 'POST', headers: postHeaders, body: {} })
 const freshState = await providerStart.json()
 providerDown = true
 const failed = await request(freshState.loginUrl, { headers: { Cookie: providerStart.headers.get('set-cookie').split(';')[0], 'Cf-Access-Jwt-Assertion': assertion } })
 assert.equal(failed.status, 503); assert.match(await failed.text(), /身分服務暫時無法使用/)
 pass('provider outage is distinct from denied authority and CSRF failure')
 await metadata('human', { operation: 'disable-member', input: { memberId: 'person' } })
 assert.equal((await request('/doc?room=one', { headers: { Cookie: cookie } })).status, 403)
 pass('current disabled-member policy denies existing human session')
 await writeFile(join(scratch, 'report.json'), JSON.stringify(report, null, 2))
 console.log('evidence=' + join(scratch, 'report.json'))
} finally { await mf.dispose() }
