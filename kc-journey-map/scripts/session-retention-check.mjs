import assert from 'node:assert/strict'
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises'
import { join } from 'node:path'
import { build } from 'esbuild'
import { Miniflare } from 'miniflare'
import { NodeHost } from '../server/host/node.ts'
import { digest } from '../server/host/policy.ts'
import { handle } from '../server/host/transport.ts'

const root = new URL('..', import.meta.url).pathname
await mkdir(join(root, '.host-check'), { recursive: true })
const scratch = await mkdtemp(join(root, '.host-check/session-retention-'))
const savedEnv = Object.fromEntries(['JOURNEY_PRIVATE_DIR', 'JOURNEY_GRANTS_FILE', 'JOURNEY_ORIGIN'].map(k => [k, process.env[k]]))
const origin = 'https://retention.example.invalid', secret = 'x'.repeat(43)
const grants = [{ credentialId: 'probe', principalId: 'probe', secretDigest: await digest(secret), rooms: ['A'], expiresAt: Date.now() + 3600000, revoked: false }]
const grantFile = join(scratch, 'grants.json')
await writeFile(grantFile, JSON.stringify(grants), { mode: 0o600 })
const cursorKey = 'maintenance:session-gc'
const future = Date.now() + 3600000
const session = expiry => JSON.stringify({ credentialId: 'probe', expiresAt: expiry })
const key = i => 'session:!' + String(i).padStart(6, '0')
const wrapper = `
import worker, {JourneyRegistry, JourneyRoom} from './server/host/cloudflare.ts'
export {JourneyRoom}
export class RetentionRegistry extends JourneyRegistry {
 constructor(ctx, env) {
  const trace = []
  super({blockConcurrencyWhile: fn => ctx.blockConcurrencyWhile(fn), storage: {sql: {exec: (...args) => {
   const cursor = ctx.storage.sql.exec(...args), rows = cursor.toArray()
   trace.push({query:args[0], returned:rows.length, rowsRead:cursor.rowsRead, rowsWritten:cursor.rowsWritten})
   return {toArray: () => rows}
  }}}}, env)
  this.testContext = ctx; this.trace = trace
 }
 async fetch(req) {
  const path = new URL(req.url).pathname
  if (path === '/test/sql') {
   const {query, params} = await req.json()
   const cursor = this.testContext.storage.sql.exec(query, ...params), rows = cursor.toArray()
   return Response.json({rows, rowsRead:cursor.rowsRead})
  }
  if (path === '/test/trace') {const trace = this.trace.splice(0); return Response.json(trace)}
  if (path === '/test/alarm') return Response.json(await this.testContext.storage.getAlarm())
  return super.fetch(req)
 }
}
export default worker
`
const bundle = await build({ stdin: { contents: wrapper, resolveDir: root, sourcefile: 'session-retention-fixture.ts' },
 bundle: true, write: false, format: 'esm', platform: 'browser', conditions: ['workerd', 'worker', 'browser'], external: ['cloudflare:workers'], logLevel: 'silent' })
const reports = []
async function open(adapter, dir) {
 if (adapter === 'node') {
  Object.assign(process.env, { JOURNEY_PRIVATE_DIR: dir, JOURNEY_GRANTS_FILE: grantFile, JOURNEY_ORIGIN: origin })
  const host = new NodeHost()
  return { request: req => handle(host, req), sql: async (query, params = []) => ({ rows: host.db.prepare(query).all(...params) }),
   trace: async () => [], alarm: async () => null, close: async () => host.close() }
 }
 const mf = new Miniflare({ script: bundle.outputFiles[0].text, modules: true, compatibilityDate: '2026-07-01',
  compatibilityFlags: ['nodejs_compat'], host: '127.0.0.1', port: 0,
  bindings: { JOURNEY_ORIGIN: origin, JOURNEY_GRANTS: JSON.stringify(grants) },
  durableObjects: { REGISTRY: { className: 'RetentionRegistry', useSQLite: true }, ROOMS: { className: 'JourneyRoom', useSQLite: true } },
  durableObjectsPersist: join(dir, 'objects') })
 await mf.ready
 const ns = await mf.getDurableObjectNamespace('REGISTRY'), stub = ns.get(ns.idFromName('private-pilot'))
 const call = async (path, body) => {
  const r = await stub.fetch('https://registry' + path, { method: 'POST', body: JSON.stringify(body ?? {}) })
  assert.equal(r.status, 200, await r.clone().text()); return r.json()
 }
 return { request: req => mf.dispatchFetch(req.url, { method: req.method, headers: Object.fromEntries(req.headers) }),
  sql: (query, params = []) => call('/test/sql', { query, params }), trace: () => call('/test/trace'),
  alarm: () => call('/test/alarm'), close: () => mf.dispose() }
}
for (const adapter of ['node', 'cloudflare-local']) {
 let host
 try {
  const dir = join(scratch, adapter); host = await open(adapter, dir)
  const sql = (q, params = []) => host.sql(q, params)
  const put = (k, v) => sql('INSERT OR REPLACE INTO metadata VALUES (?, ?)', [k, v])
  const get = async k => (await sql('SELECT value FROM metadata WHERE key = ?', [k])).rows[0]?.value
  const all = async () => (await sql('SELECT key, value FROM metadata ORDER BY key')).rows
  const login = (headers = {}) => host.request(new Request(origin + '/session', { method: 'POST',
   headers: { origin, authorization: 'Bearer probe.' + secret, ...headers } }))
  const request = (path, headers = {}) => host.request(new Request(origin + path, { headers }))
  const reset = async () => { await sql("DELETE FROM metadata WHERE key >= 'session:' AND key < 'session;'"); await sql('DELETE FROM metadata WHERE key = ?', [cursorKey]) }
  await put(key(1), session(1))
  assert.equal((await login()).status, 200)
  assert.equal(await get(key(1)), undefined, 'expired session row survives a successful login')
  if (process.argv.includes('--falsifier')) { reports.push({ adapter, falsifier: 'PASS: expired legacy session removed' }); continue }
  const checkpoints = ['expired legacy session removed on successful login']
  const created = await login(), cookie = created.headers.get('set-cookie').split(';')[0]
  const cookieKey = 'session:' + await digest(cookie.slice(cookie.indexOf('=') + 1))
  assert.equal((await request('/capabilities?room=A', { cookie })).status, 200)
  await put(cookieKey, session(1))
  assert.equal((await request('/capabilities?room=A', { cookie })).status, 401)
  assert.equal((await login()).status, 200); assert.equal(await get(cookieKey), undefined)
  await reset()
  const preserved = [
   ['grant:untouched', JSON.stringify({ retained: true })], ['room:untouched', '{"createdAt":1}'],
   ['asset:A:untouched', '{"blobKey":"synthetic"}'], [key(190), session(future)],
   [key(191), '{bad JSON'], [key(192), '{"expiresAt":1}'],
   [key(193), '{"credentialId":"probe","expiresAt":"1"}'], [key(194), '{"credentialId":"probe","expiresAt":null}'],
  ]
  const fixtures = [...Array.from({length:150}, (_, i) => [key(i + 1), session(1)]), ...preserved,
   ...Array.from({length:2048}, (_, i) => ['unrelated:' + i, '{"unchanged":true}'])]
  for (let i = 0; i < fixtures.length; i += 40) {
   const batch = fixtures.slice(i, i + 40)
   await sql('INSERT OR REPLACE INTO metadata VALUES ' + batch.map(() => '(?, ?)').join(','), batch.flat())
  }
  const nonSession = (await all()).filter(r => !r.key.startsWith('session:') && r.key !== cursorKey)
  await host.trace()
  assert.equal((await login()).status, 200)
  assert.equal(JSON.parse(await get(cursorKey)), key(64))
  assert.equal((await sql("SELECT COUNT(*) AS n FROM metadata WHERE key >= ? AND key <= ?", [key(1), key(150)])).rows[0].n, 86)
  const trace = await host.trace()
  const pages = trace.filter(r => r.query.startsWith('SELECT key, value FROM metadata WHERE'))
  if (adapter === 'cloudflare-local') {
   assert.equal(pages.length, 1); assert.equal(pages[0].returned, 64); assert.equal(pages[0].rowsRead, 64)
  }
  const pageSql = pages[0]?.query ?? "SELECT key, value FROM metadata WHERE key > ? AND key < ? ORDER BY key LIMIT 64"
  const plan = (await sql('EXPLAIN QUERY PLAN ' + pageSql, ['session:', 'session;'])).rows
  assert(plan.some(row => /SEARCH metadata USING INDEX.*key>.*key</.test(row.detail)), JSON.stringify(plan))
  const savedCursor = await get(cursorKey)
  await host.close(); host = await open(adapter, dir)
  assert.equal(await get(cursorKey), savedCursor)
  assert.equal((await login()).status, 200); assert.equal(JSON.parse(await get(cursorKey)), key(128))
  assert.equal((await login()).status, 200); assert.equal(JSON.parse(await get(cursorKey)), 'session:')
  assert.equal((await sql("SELECT COUNT(*) AS n FROM metadata WHERE key >= ? AND key <= ?", [key(1), key(150)])).rows[0].n, 0)
  for (const [k, v] of preserved) assert.equal(await get(k), v)
  assert.deepEqual((await all()).filter(r => !r.key.startsWith('session:') && r.key !== cursorKey), nonSession)
  checkpoints.push('64-row indexed page; restart progress; legacy debt drained; malformed/live/non-session preservation')
  await reset()
  const laterFixtures = [...Array.from({length:4096}, (_, i) => [key(i + 1), session(future)]),
   ...Array.from({length:65}, (_, i) => [key(i + 4097), session(1)])]
  for (let i = 0; i < laterFixtures.length; i += 40) {
   const batch = laterFixtures.slice(i, i + 40)
   await sql('INSERT OR REPLACE INTO metadata VALUES ' + batch.map(() => '(?, ?)').join(','), batch.flat())
  }
  await put(cursorKey, JSON.stringify(key(4096)))
  await host.trace()
  assert.equal((await login()).status, 200)
  const laterPages = (await host.trace()).filter(r => r.query.startsWith('SELECT key, value FROM metadata WHERE'))
  const laterPage = laterPages[0] ?? { returned: 64, rowsRead: 'not instrumented on Node' }
  assert.equal(JSON.parse(await get(cursorKey)), key(4160))
  const laterRemaining = new Map((await all()).map(r => [r.key, r.value]))
  for (let i = 1; i <= 4096; i++) assert.equal(laterRemaining.get(key(i)), session(future))
  for (let i = 4097; i <= 4160; i++) assert.equal(laterRemaining.get(key(i)), undefined)
  assert.equal(laterRemaining.get(key(4161)), session(1))
  assert.deepEqual((await all()).filter(r => !r.key.startsWith('session:') && r.key !== cursorKey), nonSession)
  if (adapter === 'cloudflare-local') {
   assert.equal(laterPages.length, 1); assert.equal(laterPage.returned, 64)
   assert(laterPage.rowsRead <= 64, `later page returned ${laterPage.returned} but read ${laterPage.rowsRead} records`)
  }
  checkpoints.push('later page behind 4096 live rows; only 64 intended expired rows deleted; live/unrelated rows preserved')
  await reset()
  for (let i = 1; i <= 64; i++) await put(key(i), session(future))
  assert.equal((await login()).status, 200); assert.equal(JSON.parse(await get(cursorKey)), key(64))
  await put(key(1), session(1)); await put('session:!000000-lower', session(1))
  assert.equal((await login()).status, 200); assert.equal(JSON.parse(await get(cursorKey)), 'session:')
  assert.notEqual(await get(key(1)), undefined)
  assert.equal((await login()).status, 200); assert.equal(await get(key(1)), undefined); assert.equal(await get('session:!000000-lower'), undefined)
  await put(cursorKey, JSON.stringify('session:zzzzzzzz'))
  assert.equal((await login()).status, 200); assert.equal(JSON.parse(await get(cursorKey)), 'session:')
  checkpoints.push('expiry after passage; lower random insert revisited; EOF wraps without second scan')
  for (const invalid of [JSON.stringify('asset:'), JSON.stringify('session;'), '{invalid', 'null']) {
   await reset(); await put(cursorKey, invalid); await put(key(1), session(1))
   assert.equal((await login()).status, 200); assert.equal(await get(key(1)), undefined)
   for (const [k, v] of preserved.filter(([k]) => !k.startsWith('session:'))) assert.equal(await get(k), v)
  }
  await reset(); await put(key(1), session(1)); await put(cursorKey, JSON.stringify('session:'))
  const beforeFailure = await all()
  await sql("CREATE TRIGGER fail_delete BEFORE DELETE ON metadata WHEN old.key >= 'session:' AND old.key < 'session;' BEGIN SELECT RAISE(ABORT, 'synthetic cleanup failure'); END")
  assert.equal((await login()).status, 503)
  assert.deepEqual(await all(), beforeFailure)
  await sql('DROP TRIGGER fail_delete')
  assert.equal((await login()).status, 200); assert.equal(await get(key(1)), undefined)
  const beforeDenial = await all()
  assert.equal((await login({ origin: 'https://wrong.example.invalid' })).status, 403)
  assert.equal((await login({ authorization: 'Bearer invalid' })).status, 401)
  assert.equal((await request('/capabilities?room=B', { authorization: 'Bearer probe.' + secret })).status, 403)
  assert.deepEqual(await all(), beforeDenial)
  await put('grant:probe', JSON.stringify({ ...grants[0], revoked: true }))
  assert.equal((await login()).status, 401)
  await put('grant:probe', JSON.stringify({ ...grants[0], expiresAt: 1 }))
  assert.equal((await login()).status, 401)
  assert.equal(await host.alarm(), null)
  assert.deepEqual((await sql("SELECT key FROM metadata WHERE key >= 'room:' AND key < 'room;'")).rows.map(r => r.key), ['room:untouched'])
  checkpoints.push('invalid cursor bounded; failure leaves cursor/debt; auth/origin/revoke/room denial preserved; no room/alarm creation')
  reports.push({ adapter, result: 'PASS', checkpoints, page: pages[0] ?? { returned: 64, rowsRead: 'not instrumented on Node' }, laterPage, queryPlan: plan })
 } catch (error) {
  reports.push({ adapter, result: 'FAIL', error: error.message }); process.exitCode = 1
 } finally { await host?.close() }
}
for (const [k, v] of Object.entries(savedEnv)) if (v === undefined) delete process.env[k]; else process.env[k] = v
await rm(scratch, {recursive:true, force:true})
console.log(JSON.stringify({ reports, hosted: 'NOT RUN', billing: 'NOT RUN', cleanup: 'owned local stores/runtime removed' }, null, 2))

