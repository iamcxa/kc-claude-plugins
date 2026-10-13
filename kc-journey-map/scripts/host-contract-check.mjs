import assert from 'node:assert/strict'
import { spawn, execFileSync } from 'node:child_process'
import { createServer as netServer } from 'node:net'
import { createHash } from 'node:crypto'
import { mkdtemp, mkdir, writeFile, readFile, symlink } from 'node:fs/promises'
import { join } from 'node:path'
import { createInterface } from 'node:readline'
import { createServer as viteServer } from 'vite'
import { chromium } from 'playwright'
import { WebSocket } from 'ws'
import { startCloudflare } from './cloudflare-local.mjs'
import { pathToFileURL } from 'node:url'
import { browserSession } from './journey-browser.mjs'

const root = new URL('..', import.meta.url).pathname.replace(/\/$/, '')
const adapter = process.argv[process.argv.indexOf('--adapter') + 1]
if (!['node', 'cloudflare-local'].includes(adapter) || !process.argv.includes('--synthetic')) throw new Error('supported: --adapter node|cloudflare-local --synthetic; hosted targets require separate authorization')
const baseline = '6d0f8da951b5ea9ea50fca6bd3685fc360bf502f'
const sha = execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim()
const sourceDirty = !!execFileSync('git', ['-C', root, 'status', '--porcelain'], { encoding: 'utf8' }).trim()
const scratch = await mkdtemp(join(root, '.host-check/run-'))
const report = { adapter, baseline, candidate: sha, sourceDirty, runtime: process.version, target: '', checks: [], hosted: 'NOT RUN', billing: 'NOT RUN', licensing: 'NOT RUN', providerHibernation: 'NOT RUN' }
report.versions = Object.fromEntries(await Promise.all(['@tldraw/sync-core', 'miniflare', 'playwright', 'esbuild'].map(async name => [name, JSON.parse(await readFile(join(root, 'node_modules', name, 'package.json'), 'utf8')).version])))
const hash = value => createHash('sha256').update(value).digest('hex')
const check = async (name, fn) => {
 const started = performance.now()
 await fn()
 report.checks.push({ name, result: 'PASS', durationMs: Math.round(performance.now() - started) })
 console.log('PASS ' + name)
}
const freePort = () => new Promise((resolve, reject) => { const s = netServer(); s.once('error', reject); s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => resolve(p)) }) })
const port = await freePort(), browserPort = await freePort()
const origin = 'https://pilot.test:' + browserPort
const api = 'http://127.0.0.1:' + port
report.target = api
const secret = 's'.repeat(43), token = id => id + '.' + secret
const grants = ['a', 'b', 'expired', 'revoked', 'short'].map(id => ({
 credentialId: id, principalId: 'principal-' + id, secretDigest: hash(secret),
 rooms: id === 'a' ? ['shared', 'a', 'invalid', 'alias_x', 'retry'] : id === 'b' ? ['shared', 'b'] : ['shared'],
 expiresAt: id === 'expired' ? Date.now() - 1000 : Date.now() + 3600_000, revoked: id === 'revoked',
}))
const grantFile = join(scratch, 'grants.json')
await writeFile(grantFile, JSON.stringify(grants), { mode: 0o600 })
const fixtureRepo = join(scratch, 'checkout'); await mkdir(fixtureRepo)
const git = args => execFileSync('git', ['-C', fixtureRepo, ...args], { stdio: 'pipe' })
git(['init', '-q', '-b', 'main']); git(['config', 'user.name', 'Synthetic acceptance']); git(['config', 'user.email', 'synthetic@example.invalid'])
await writeFile(join(fixtureRepo, 'guide.md'), '# Synthetic checkout\n')
git(['add', 'guide.md']); git(['commit', '-qm', 'Synthetic fixture'])
let host, vite, browser, child
const logs = []
const pending = new Map()
async function start(dir = join(scratch, 'private'), changedOrigin = origin, options = {}) {
 if (adapter === 'cloudflare-local') {
  host = await startCloudflare({ dir, port, origin: changedOrigin, grants, ...options })
 } else {
  child = spawn(process.execPath, ['--import', 'tsx', join(root, 'server/canvas-server.ts')], {
   cwd: root, stdio: ['pipe', 'pipe', 'pipe'], env: { ...process.env, JOURNEY_PRIVATE_DIR: dir, JOURNEY_API_PORT: String(port),
    JOURNEY_ORIGIN: changedOrigin, JOURNEY_GRANTS_FILE: grantFile, JOURNEY_CONTROL_STDIO: '1',
    JOURNEY_SAVE_DIR: join(scratch, 'saves'), JOURNEY_DOC_REPOS: 'synthetic/guide=' + fixtureRepo,
    JOURNEY_ROOM_REPOS: JSON.stringify({ shared: ['synthetic/guide'] }) },
  })
  createInterface({ input: child.stdout }).on('line', line => {
   logs.push(line)
   try { const r = JSON.parse(line); if (r.control) { pending.get(r.control)?.(r.result); pending.delete(r.control) } } catch {}
  })
  child.stderr.on('data', d => logs.push(String(d)))
  const control = command => new Promise((resolve, reject) => {
    const id = crypto.randomUUID(); pending.set(id, resolve); child.stdin.write(JSON.stringify({ id, ...command }) + '\n')
    setTimeout(() => { if (pending.delete(id)) reject(new Error('operator command timeout')) }, 5000).unref()
   })
  host = {
   revoke: credentialId => control({ op: 'revoke', credentialId }),
   export: room => control({ op: 'export', room }),
   restore: archive => control({ op: 'restore', archive }),
   close: () => new Promise(resolve => { if (child.exitCode !== null) return resolve(); child.once('exit', resolve); child.kill('SIGTERM') }),
  }
 }
 for (let n = 0; n < 200; n++) {
  try { if ((await request('/health')).status === 200) return } catch {}
  if (child?.exitCode !== null && adapter === 'node') throw new Error(logs.join('\n'))
  await new Promise(resolve => setTimeout(resolve, 50))
 }
 throw new Error('host startup timed out: ' + logs.join('\n'))
}
async function request(path, { id = 'a', method = 'GET', body, headers = {} } = {}) {
 return fetch(api + path, { method, headers: { ...(id ? { Authorization: 'Bearer ' + token(id) } : {}), ...(body === undefined ? {} : { 'Content-Type': 'application/json' }), ...headers }, body: body === undefined ? undefined : JSON.stringify(body) })
}
async function data(path, options) { const r = await request(path, options); assert.equal(r.status, 200, await r.clone().text()); return r.json() }
async function rpc(name, args = {}, id = 'a') { return data('/mcp', { id, method: 'POST', body: { jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name, arguments: args } } }) }
const records = snapshot => snapshot.documents.map(d => d.state).sort((a, b) => a.id.localeCompare(b.id))
const stableRecords = snapshot => hash(JSON.stringify(records(snapshot)))
const openSocket = (room, id = 'a', extra = {}) => new Promise((resolve, reject) => {
 const socket = new WebSocket(api.replace('http', 'ws') + '/connect/' + room + '?sessionId=' + crypto.randomUUID(), { headers: { Authorization: 'Bearer ' + token(id), Origin: origin, ...extra } })
 socket.once('open', () => resolve(socket))
 socket.once('unexpected-response', (_req, response) => { response.resume(); resolve({ status: response.statusCode }) })
 socket.once('error', reject)
})
const baselineDir = join(scratch, 'baseline')
const legacyDir = join(scratch, 'legacy')
let baselineChild, legacySnapshot
async function legacyRun(first) {
 const legacyPort = await freePort()
 baselineChild = spawn(process.execPath, ['--import', join(root, 'node_modules/tsx/dist/loader.mjs'), join(baselineDir, 'kc-journey-map/server/canvas-server.ts')], {
  cwd: baselineDir, stdio: ['ignore', 'pipe', 'pipe'],
  env: { ...process.env, JOURNEY_API_PORT: String(legacyPort), JOURNEY_ROOMS_DIR: legacyDir, JOURNEY_ASSETS_DIR: join(scratch, 'legacy-assets'), JOURNEY_PRIVATE_DIR: '', JOURNEY_API_TOKEN: '' },
 })
 let stderr = ''; baselineChild.stderr.on('data', b => { stderr += b })
 const url = 'http://127.0.0.1:' + legacyPort
 try {
  let ready = false
  for (let i = 0; i < 150; i++) {
   try { if ((await fetch(url + '/health')).ok) { ready = true; break } } catch {}
   if (baselineChild.exitCode !== null) throw new Error(stderr)
   await new Promise(r => setTimeout(r, 50))
  }
  assert.ok(ready, stderr)
  if (first) {
   legacySnapshot = await (await fetch(url + '/doc?room=legacy')).json()
   assert.ok((await (await fetch(url + '/health')).json()).rooms.includes('legacy'))
   assert.equal((await fetch(url + '/uploads/legacy', { method: 'PUT', body: 'legacy untouched bytes', headers: { 'Content-Type': 'application/octet-stream' } })).status, 200)
  } else {
   assert.deepEqual(await (await fetch(url + '/doc?room=legacy')).json(), legacySnapshot)
   assert.equal(await (await fetch(url + '/uploads/legacy')).text(), 'legacy untouched bytes')
  }
 } finally {
  if (baselineChild.exitCode === null) await new Promise(resolve => { baselineChild.once('exit', resolve); baselineChild.kill('SIGTERM') })
 }
}

try {
 await mkdir(baselineDir)
 execFileSync('tar', ['-xf', '-', '-C', baselineDir], { input: execFileSync('git', ['-C', join(root, '..'), 'archive', baseline, 'kc-journey-map']) })
 await symlink(join(root, 'node_modules'), join(baselineDir, 'kc-journey-map/node_modules'))
 await check('baseline legacy Node initializes disposable data before the private pilot', () => legacyRun(true))
 await check('baseline default records and page links are unchanged; configured base changes URL alone', async () => {
  const old = await import(pathToFileURL(join(baselineDir, 'kc-journey-map/lib/render.mjs')).href)
  const candidate = await import(pathToFileURL(join(root, 'lib/render.mjs')).href)
  const { fixtureModel } = await import(pathToFileURL(join(root, 'lib/fixture.mjs')).href)
  const comparable = records => ({
   records: records.map(({ index, ...r }) => r).sort((a, b) => a.id.localeCompare(b.id)),
   order: records.toSorted((a, b) => String(a.parentId || '').localeCompare(String(b.parentId || '')) || a.index.localeCompare(b.index)).map(r => r.id),
  })
  delete process.env.JOURNEY_CANVAS_BASE
  assert.deepEqual(comparable(candidate.buildAllPages(fixtureModel, 'shared')), comparable(old.buildAllPages(fixtureModel, 'shared')))
  const normal = candidate.buildAllPages(fixtureModel, 'shared', ['story-map', 'journey-board'])
  assert.deepEqual(comparable(normal), comparable(old.buildAllPages(fixtureModel, 'shared', ['story-map', 'journey-board'])))
  process.env.JOURNEY_CANVAS_BASE = 'https://canvas.example.invalid'
  const configured = candidate.buildAllPages(fixtureModel, 'shared', ['story-map', 'journey-board'])
  delete process.env.JOURNEY_CANVAS_BASE
  assert.deepEqual(comparable(JSON.parse(JSON.stringify(configured).replaceAll('https://canvas.example.invalid', 'http://localhost:3737'))), comparable(normal))
 })
 await check('grant helper issues a digest-only policy and refuses credential-ID reuse', async () => {
  const file = join(scratch, 'helper-grants.json'), tokenFile = join(scratch, 'helper.token')
  const args = ['--import', 'tsx', join(root, 'scripts/journey-grant.ts'), file, 'test-issued', 'test-principal', 'shared,a', new Date(Date.now() + 60000).toISOString(), tokenFile]
  execFileSync(process.execPath, args, { cwd: root, stdio: 'pipe' })
  const credential = await readFile(tokenFile, 'utf8')
  const grant = JSON.parse(await readFile(file, 'utf8'))[0]
  assert.equal(Buffer.from(credential.split('.')[1], 'base64url').length, 32)
  assert.equal(grant.secretDigest, hash(credential.split('.')[1]))
  assert.ok(!JSON.stringify(grant).includes(credential))
  assert.throws(() => execFileSync(process.execPath, args, { cwd: root, stdio: 'pipe' }))
 })
 await start()
 await check('HTTP and MCP deny missing invalid expired revoked and cross-room access before creation', async () => {
  for (const id of [null, 'unknown', 'expired', 'revoked', 'b']) assert.equal((await request('/doc?room=a', { id })).status, id === 'b' ? 403 : 401)
  assert.equal((await request('/doc?room=alias.x')).status, 403)
  assert.deepEqual((await data('/health')).rooms, [])
  for (const id of ['b', 'expired', 'revoked']) {
   const r = await request('/mcp', { id, method: 'POST', body: { jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: 'get_doc', arguments: { room: 'a' } } } })
   assert.equal(r.status, id === 'b' ? 403 : 401)
  }
 })
 if (adapter === 'cloudflare-local') await check('registry failure returns 503 and retry registers the initialized room before acknowledgement', async () => {
  const faultDir = join(scratch, 'registry-fault')
  await host.close(); await start(faultDir, origin, { failRegistration: true })
  assert.equal((await request('/doc?room=retry')).status, 503)
  assert.deepEqual((await data('/health')).rooms, [])
  await host.close(); await start(faultDir)
  await data('/doc?room=retry')
  assert.deepEqual((await data('/health')).rooms, ['retry'])
  await host.close(); await start()
 })
 await check('MCP initializes discovers tools and accepts initialized notification', async () => {
  const init = await data('/mcp', { method: 'POST', body: { jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-03-26', capabilities: {}, clientInfo: { name: 'synthetic', version: '1' } } } })
  assert.equal(init.result.protocolVersion, '2025-03-26')
  const list = await data('/mcp', { method: 'POST', body: { jsonrpc: '2.0', id: 2, method: 'tools/list' } })
  assert.deepEqual(list.result.tools.map(t => t.name), ['get_doc', 'patch_doc', 'put_doc', 'health'])
  assert.equal((await request('/mcp', { method: 'POST', body: { jsonrpc: '2.0', method: 'notifications/initialized' } })).status, 202)
  assert.equal((await request('/mcp')).status, 405)
 })
 await check('GET auto-creation is immediately visible and health filters room grants', async () => {
  await data('/doc?room=a'); await data('/doc?room=b', { id: 'b' }); await data('/doc?room=shared')
  assert.deepEqual((await data('/health')).rooms.sort(), ['a', 'shared'])
  assert.deepEqual((await data('/health', { id: 'b' })).rooms.sort(), ['b', 'shared'])
 })
 await check('invalid PATCH and PUT do not create a room or mutate an existing document', async () => {
  assert.equal((await request('/doc?room=invalid', { method: 'PATCH', body: { put: [{ id: 'bad' }] } })).status, 400)
  assert.equal((await request('/doc?room=invalid', { method: 'PUT', body: {} })).status, 400)
  assert.ok(!(await data('/health')).rooms.includes('invalid'))
  const before = await data('/doc?room=shared')
  assert.equal((await request('/doc?room=shared', { method: 'PATCH', body: { put: [{}], remove: ['page:page'] } })).status, 400)
  assert.deepEqual(await data('/doc?room=shared'), before)
 })
 const fixture = join(scratch, 'journey.yaml')
 await writeFile(fixture, `journey: synthetic-delivery
persona: A fictional parcel recipient.
one_journey: Reserve and collect a fictional parcel.
steps:
  - id: choose
    card: Choose a parcel
    stories:
      - {id: reserve, card: Reserve a parcel, release: trial, status: unverified}
releases:
  - {id: trial, name: Private trial, goal: Collect one parcel.}
`)
 await check('delivered CLI render/read and independent MCP read preserve journey records', async () => {
  const env = { ...process.env, JOURNEY_API: api, JOURNEY_API_TOKEN: token('a') }
  report.cliRender = execFileSync(process.execPath, [join(root, 'lib/journey-render.mjs'), fixture, 'shared', '--pages', 'story-map,journey-board'], { cwd: root, env, encoding: 'utf8' })
  report.cliRead = JSON.parse(execFileSync(process.execPath, [join(root, 'lib/journey-read.mjs'), fixture, 'shared'], { cwd: root, env, encoding: 'utf8' }))
  const http = await data('/doc?room=shared')
  assert.deepEqual((await rpc('get_doc', { room: 'shared' })).result.structuredContent, http)
  assert.ok(records(http.snapshot).some(r => r.typeName === 'shape'))
  assert.ok(records(http.snapshot).some(r => r.props?.url?.startsWith('http://localhost:3737/')))
  let failed = false
  try { execFileSync(process.execPath, [join(root, 'lib/journey-read.mjs'), fixture, 'shared'], { env: { ...env, JOURNEY_API_TOKEN: token('expired') }, stdio: 'pipe' }) } catch (e) { failed = /credential.*denied/.test(e.stderr.toString()) }
  assert.ok(failed)
 })
 await check('both principals share full-record last-writer PATCH and snapshot PUT', async () => {
  const snapshot = (await data('/doc?room=shared')).snapshot
  const shape = records(snapshot).find(r => r.typeName === 'shape')
  assert.equal((await data('/doc?room=shared', { method: 'PATCH', body: { put: [{ ...shape, x: 456 }] } })).put, 1)
  assert.equal((await rpc('patch_doc', { room: 'shared', body: { put: [{ ...shape, y: 789 }] } }, 'b')).result.structuredContent.put, 1)
  const current = records((await data('/doc?room=shared')).snapshot).find(r => r.id === shape.id)
  assert.equal(current.x, shape.x); assert.equal(current.y, 789)
  await data('/doc?room=shared', { method: 'PATCH', body: { remove: [shape.id] } })
  await rpc('put_doc', { room: 'shared', body: { snapshot } })
  assert.equal(stableRecords((await data('/doc?room=shared')).snapshot), stableRecords(snapshot))
 })
 await check('room-scoped assets reject unauthorized overwrite aliases and unassociated legacy IDs', async () => {
  for (const [room, id, bytes] of [['a', 'a', 'AAA'], ['b', 'b', 'BBB'], ['shared', 'a', 'SHARED']]) {
   const r = await fetch(api + '/uploads/same?room=' + room, { method: 'PUT', headers: { Authorization: 'Bearer ' + token(id), 'Content-Type': 'application/octet-stream' }, body: bytes })
   assert.equal(r.status, 200)
  }
  assert.equal(await (await request('/uploads/same?room=a')).text(), 'AAA')
  assert.equal(await (await request('/uploads/same?room=b', { id: 'b' })).text(), 'BBB')
  for (const path of ['/uploads/same?room=b', '/uploads/foo%2Fbar?room=a']) assert.equal((await request(path)).status, 403)
  assert.equal((await request('/uploads/legacy?room=a')).status, 404)
  assert.equal((await request('/uploads/same?room=b', { method: 'PUT', body: {} })).status, 403)
  assert.equal(await (await request('/uploads/same?room=b', { id: 'b' })).text(), 'BBB')
 })
 await check('socket admission checks exact origin and room rights', async () => {
  assert.equal((await openSocket('a', 'b')).status, 403)
  assert.equal((await openSocket('shared', 'expired')).status, 401)
  assert.equal((await openSocket('shared', 'a', { Origin: 'https://wrong.invalid' })).status, 403)
  const socket = await openSocket('shared'); socket.close()
 })
 await check('capabilities and configured checkout/save behavior are explicit', async () => {
  const cap = await data('/capabilities?room=shared')
  assert.equal(cap.assets, true)
  assert.equal(cap.save, adapter === 'node')
  assert.equal(cap.repoDoc, adapter === 'node')
  const doc = await data('/repo-doc?room=shared&owner=synthetic&repo=guide&refPath=main/guide.md')
  assert.equal(doc.state, adapter === 'node' ? 'ok' : 'unavailable')
  if (adapter === 'node') {
   assert.equal(doc.content, '# Synthetic checkout\n')
   const snapshot = (await data('/doc?room=shared')).snapshot
   const saved = await data('/save?room=shared', { method: 'POST', body: { name: 'synthetic', file: JSON.stringify({ schema: snapshot.schema, records: records(snapshot) }) } })
   assert.ok(saved.records > 0); assert.deepEqual(JSON.parse(await readFile(saved.path, 'utf8')).records, records(snapshot))
  } else {
   const response = await request('/save?room=shared')
   assert.equal(response.status, 501); assert.ok(!response.headers.get('content-type').includes('application/json'))
  }
 })
 await check('Node restart or Cloudflare-local eviction/reconnect preserves documents inventory and bytes', async () => {
  const before = stableRecords((await data('/doc?room=shared')).snapshot)
  await host.close(); await start()
  assert.equal(stableRecords((await data('/doc?room=shared')).snapshot), before)
  assert.equal(await (await request('/uploads/same?room=a')).text(), 'AAA')
  assert.deepEqual((await data('/health')).rooms.sort(), ['a', 'shared'])
 })
 const key = join(scratch, 'key.pem'), cert = join(scratch, 'cert.pem')
 execFileSync('openssl', ['req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-keyout', key, '-out', cert, '-days', '1', '-subj', '/CN=pilot.test'], { stdio: 'pipe' })
 vite = await viteServer({ configFile: join(root, 'vite.config.mts'), server: { host: '127.0.0.1', port: browserPort, strictPort: true,
  https: { key: await readFile(key), cert: await readFile(cert) }, allowedHosts: ['pilot.test'],
  proxy: Object.fromEntries(['/connect', '/uploads/', '/repo-doc', '/save', '/session', '^/doc($|[?])', '/health', '/capabilities', '/mcp'].map(route => [route, { target: api, ws: route === '/connect' }])) } })
 await vite.listen()
 browser = await chromium.launch({ headless: true, args: ['--host-resolver-rules=MAP pilot.test 127.0.0.1', '--no-proxy-server'] })
 await check('HTTPS hostname browser session and actual tldraw WebSocket read back CLI records', async () => {
  const context = await browser.newContext({ ignoreHTTPSErrors: true })
  const page = await context.newPage()
  page.on('pageerror', e => logs.push('browser pageerror: ' + e.message))
  page.on('console', m => { if (m.type() === 'error') logs.push('browser error: ' + m.text()) })
  page.on('requestfailed', r => logs.push('browser request failed: ' + r.url() + ' ' + r.failure()?.errorText))
  page.on('websocket', ws => { logs.push('browser websocket: ' + ws.url()); ws.on('socketerror', e => logs.push('browser websocket error: ' + e)); ws.on('framereceived', frame => { if (String(frame.payload).includes('error')) logs.push('browser socket frame: ' + String(frame.payload)) }) })
  await page.goto(origin)
  const exchanged = await page.evaluate(async ({ credential, origin }) => {
   const response = await fetch('/session', { method: 'POST', headers: { Authorization: 'Bearer ' + credential, Origin: origin } })
   return { status: response.status, body: await response.json() }
  }, { credential: token('a'), origin })
  assert.equal(exchanged.status, 200); assert.ok(!JSON.stringify(exchanged.body).includes(secret))
  const cookie = (await context.cookies()).find(c => c.name === 'journey_session')
  assert.ok(cookie.httpOnly && cookie.secure && cookie.sameSite === 'Strict')
  assert.equal((await request('/doc?room=shared', { id: null, method: 'PATCH', body: {}, headers: { Cookie: cookie.name + '=' + cookie.value, Origin: 'https://wrong.invalid' } })).status, 403)
  await page.goto(origin + '/?room=shared')
  await page.waitForFunction(() => window.editor?.store.allRecords().some(r => r.typeName === 'shape'), null, { timeout: 45000 }).catch(async e => { await page.screenshot({ path: join(scratch, 'browser-failure.png') }); throw e })
  const browserRecords = await page.evaluate(() => window.editor.store.allRecords().filter(r => r.typeName === 'shape').map(r => ({ id: r.id, type: r.type, props: r.props })))
  const expected = records((await data('/doc?room=shared')).snapshot).filter(r => r.typeName === 'shape')
  const exported = JSON.parse(await page.evaluate(() => window.serializeTldrawJson()))
  assert.ok(exported.records.some(r => r.id === expected[0].id))
  assert.ok(!JSON.stringify(exported).includes(secret))
  for (const r of browserRecords) assert.ok(expected.some(e => e.id === r.id && e.type === r.type))
  assert.equal(await page.evaluate(async () => (await fetch('/uploads/same?room=shared')).text()), 'SHARED')
  assert.equal(await page.evaluate(async () => (await fetch('/doc?room=b')).status), 403)
  let connections = 0
  page.on('websocket', ws => { if (ws.url().includes('/connect/')) connections++ })
  await host.close(); await start()
  await page.waitForFunction(() => window.editor?.store.allRecords().some(r => r.typeName === 'shape'), null, { timeout: 15000 })
  for (let n = 0; n < 100 && !connections; n++) await new Promise(resolve => setTimeout(resolve, 100))
  assert.ok(connections > 0, 'browser did not reconnect after host eviction')
  assert.equal(await page.evaluate(async () => (await fetch('/uploads/same?room=shared')).text()), 'SHARED')
  await page.screenshot({ path: join(scratch, 'canvas-hostname.png') })
  report.browserOrigin = await page.evaluate(() => location.origin)
  await context.close()
 })
 await check('HTTPS IP browser uses its genuine origin and configured session boundary', async () => {
  const ipOrigin = 'https://127.0.0.1:' + browserPort
  await host.close(); await start(join(scratch, 'private'), ipOrigin)
  const context = await browser.newContext({ ignoreHTTPSErrors: true })
  await browserSession(context, ipOrigin, token('b'))
  const page = await context.newPage(); await page.goto(ipOrigin + '/?room=shared')
  await page.waitForFunction(() => window.editor?.store.allRecords().some(r => r.typeName === 'shape'), null, { timeout: 45000 }).catch(async e => { await page.screenshot({ path: join(scratch, 'browser-failure.png') }); throw e })
  assert.equal(await page.evaluate(() => location.origin), ipOrigin)
  assert.equal(await page.evaluate(async () => (await fetch('/doc?room=a')).status), 403)
  await page.screenshot({ path: join(scratch, 'canvas-ip.png') })
  await context.close()
  await host.close(); await start()
 })
 await check('room snapshot plus complete asset manifest restores to empty storage and reconnects', async () => {
  const archive = await host.export('shared')
  assert.ok(archive.assets.some(a => a.id === 'same'))
  await writeFile(join(scratch, 'synthetic-backup.json'), JSON.stringify(archive))
  await host.close(); await start(join(scratch, 'restored'))
  await host.restore(archive)
  assert.equal(stableRecords((await data('/doc?room=shared')).snapshot), stableRecords(archive.document.snapshot))
  assert.equal(await (await request('/uploads/same?room=shared')).text(), 'SHARED')
  const socket = await openSocket('shared'); socket.close()
  await host.close(); await start()
 })
 await check('session exchange rejects wrong origin and expiry closes the live socket', async () => {
  assert.equal((await request('/session', { method: 'POST', headers: { Origin: 'https://wrong.invalid' } })).status, 403)
  const short = grants.find(g => g.credentialId === 'short')
  short.expiresAt = Date.now() + 8000
  await writeFile(grantFile, JSON.stringify(grants), { mode: 0o600 })
  await host.close(); await start(join(scratch, 'expiry'))
  const exchange = await request('/session', { id: 'short', method: 'POST', headers: { Origin: origin } })
  assert.equal(exchange.status, 200)
  const cookie = exchange.headers.get('set-cookie').split(';')[0]
  const body = await exchange.json()
  assert.ok(body.expiresAt <= short.expiresAt)
  const socket = await openSocket('shared', 'short')
  const closed = new Promise(resolve => socket.once('close', resolve))
  assert.equal(await Promise.race([closed, new Promise((_, reject) => setTimeout(() => reject(new Error('expiry did not close socket')), 40_000))]), 1008)
  assert.equal((await request('/doc?room=shared', { id: null, headers: { Cookie: cookie } })).status, 401)
  await host.close(); await start()
 })
 await check('revocation closes an admitted socket and survives restart', async () => {
  const socket = await openSocket('shared', 'b')
  const closed = new Promise(resolve => socket.once('close', code => resolve(code)))
  const result = await host.revoke('b'); assert.equal(result.revoked, true)
  assert.equal(await Promise.race([closed, new Promise((_, reject) => setTimeout(() => reject(new Error('socket remained open')), 35_000))]), 1008)
  assert.equal((await request('/doc?room=shared', { id: 'b' })).status, 401)
  await host.close(); await start()
  assert.equal((await openSocket('shared', 'b')).status, 401)
 })
 await host.close()
 host = null
 await check('rollback reruns unchanged baseline Node over untouched legacy documents and assets', () => legacyRun(false))
 report.status = 'PASS'
} catch (e) {
 report.status = 'FAIL'; report.failure = e.stack; report.logs = logs.slice(-15)
 console.error(e.stack); process.exitCode = 1
} finally {
 await browser?.close(); await vite?.close(); await host?.close()
 report.evidenceDirectory = scratch
 await writeFile(join(scratch, 'result.json'), JSON.stringify(report, null, 2))
 console.log('Evidence: ' + join(scratch, 'result.json'))
}
