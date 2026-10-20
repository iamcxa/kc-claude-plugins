import assert from 'node:assert/strict'
import { spawn, execFileSync } from 'node:child_process'
import { mkdtemp, writeFile, readFile, mkdir, symlink } from 'node:fs/promises'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { createHash } from 'node:crypto'
import { DatabaseSync } from 'node:sqlite'
import { createServer } from 'node:net'
import { createServer as viteServer } from 'vite'
import { chromium } from 'playwright'
import { startCloudflare } from './cloudflare-local.mjs'
import { note } from '../lib/records.mjs'
import { checkNativeUi } from './native-ui-check.mjs'

const root = new URL('..', import.meta.url).pathname.replace(/\/$/, '')
const adapter = process.argv.includes('cloudflare-local') ? 'cloudflare-local' : 'node'
const assets = process.env.JOURNEY_TLDRAW_ASSETS
if (!assets) throw new Error('JOURNEY_TLDRAW_ASSETS must point to unpacked @tldraw/assets@5.4.0')
await mkdir(join(root, '.host-check'), { recursive: true })
const scratch = await mkdtemp(join(root, '.host-check/room-catalog-' + adapter + '-'))
const freePort = () => new Promise(resolve => { const server = createServer(); server.listen(0, '127.0.0.1', () => { const port = server.address().port; server.close(() => resolve(port)) }) })
const apiPort = await freePort(), uiPort = await freePort(), origin = 'http://127.0.0.1:' + uiPort, api = 'http://127.0.0.1:' + apiPort
const now = Date.now(), hash = value => createHash('sha256').update(value).digest('hex')
const longRoom = 'project-very-long-room-identifier-for-native-menu-check'
const many = Array.from({ length: 200 }, (_, i) => 'registered-' + String(i).padStart(3, '0'))
const inventory = ['A', 'B', 'qnow-day2', 'future', longRoom, ...many]
const config = { version: 1, backendId: 'catalog-' + adapter, origin, mode: adapter === 'node' ? 'local' : 'cloudflare', issuer: adapter === 'node' ? 'local:catalog' : 'https://catalog.synthetic.cloudflareaccess.com', audience: 'synthetic', localOwnerUid: process.geteuid(), localMemberId: 'person', members: [{ id: 'person', issuer: adapter === 'node' ? 'local:catalog' : 'https://catalog.synthetic.cloudflareaccess.com', subject: adapter === 'node' ? 'uid:' + process.geteuid() : 'person', label: 'Synthetic catalog member', role: 'operator', rooms: [...inventory, 'missing'].map(id => ({ id, expiresAt: now + 3600_000 })) }] }
const secret = 's'.repeat(43), bearer = 'seed.' + secret, token = 'synthetic-catalog-human'
const grants = [{ credentialId: 'seed', principalId: 'seed', secretDigest: hash(secret), rooms: [...inventory, 'denied'], expiresAt: now + 3600_000, revoked: false }]
const grantsFile = join(scratch, 'grants.json'), configFile = join(scratch, 'human.json'), dataDir = adapter === 'node' ? await mkdtemp(join(tmpdir(), 'catalog-data-')) : join(scratch, 'data'), saveDir = join(scratch, 'saved'), fixture = join(scratch, 'fixture')
await writeFile(grantsFile, JSON.stringify(grants), { mode: 0o600 }); await writeFile(configFile, JSON.stringify(config), { mode: 0o600 })
await mkdir(join(fixture, 'docs'), { recursive: true })
await writeFile(join(fixture, 'docs/chapter.md'), '# Synthetic chapter\n\n## Sequence\n\n' + Array.from({ length: 80 }, (_, i) => 'Synthetic paragraph ' + i).join('\n\n'))
for (const args of [['init', '-q', '-b', 'main'], ['add', 'docs/chapter.md'], ['-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid', 'commit', '-qm', 'synthetic chapter']]) execFileSync('git', ['-C', fixture, ...args], { stdio: 'pipe' })
const report = { adapter, candidate: execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(), dirty: !!execFileSync('git', ['-C', root, 'status', '--porcelain'], { encoding: 'utf8' }).trim(), checks: [], physicalDevice: 'NOT RUN', hostedProvider: 'NOT RUN', streamRevocation: 'NOT PROVEN; default-off retained', authenticationFixture: 'fresh typed synthetic browser session; owner/provider handoff covered by prerequisite suite' }
const check = async (name, run) => { await run(); report.checks.push(name); console.log('PASS ' + name) }
const waitFor = async fn => { for (let i = 0; i < 160; i++) { if (await fn()) return; await new Promise(resolve => setTimeout(resolve, 100)) } throw new Error('bounded condition timeout') }
const request = (path, method = 'GET', body) => fetch(api + path, { method, headers: { Authorization: 'Bearer ' + bearer, ...(body ? { 'Content-Type': 'application/json' } : {}) }, ...(body ? { body: JSON.stringify(body) } : {}) })
const data = async (path, _id, method = 'GET', body) => { const response = await request(path, method, body); assert.equal(response.status, 200, await response.clone().text()); return response.json() }
const records = doc => doc.snapshot.documents.map(item => item.state)
let child, host, db, metadata, vite, browser, page
let logs = ''
try {
 if (adapter === 'cloudflare-local') {
  await symlink(join(root, 'node_modules'), join(scratch, 'node_modules'), 'dir')
  host = await startCloudflare({ dir: dataDir, port: apiPort, origin, grants, humanConfig: config })
  const ns = await host.mf.getDurableObjectNamespace('REGISTRY'), registry = ns.get(ns.idFromName('private-pilot'))
  metadata = async (operation, body) => { const response = await registry.fetch('https://registry/' + operation, { method: 'POST', body: JSON.stringify(body) }); assert.equal(response.status, 200, await response.clone().text()); return response.json() }
 } else {
  child = spawn(process.execPath, ['--import', 'tsx', 'server/canvas-server.ts'], { cwd: root, env: { ...process.env, JOURNEY_PRIVATE_DIR: dataDir, JOURNEY_GRANTS_FILE: grantsFile, JOURNEY_HUMAN_CONFIG: configFile, JOURNEY_ORIGIN: origin, JOURNEY_API_PORT: String(apiPort), JOURNEY_SAVE_DIR: saveDir, JOURNEY_DOC_REPOS: 'synthetic/chapter=' + fixture, JOURNEY_ROOM_REPOS: JSON.stringify({ A: ['synthetic/chapter'] }) }, stdio: ['ignore', 'pipe', 'pipe'] })
  child.stdout.on('data', data => { logs += data }); child.stderr.on('data', data => { logs += data })
  await waitFor(async () => { try { return (await request('/health')).ok } catch { if (child.exitCode !== null) throw new Error(logs); return false } })
  db = new DatabaseSync(join(dataDir, 'metadata.sqlite'))
  db.exec('PRAGMA busy_timeout=5000')
  metadata = async (operation, body) => {
   if (operation === 'put') { db.prepare('INSERT OR REPLACE INTO metadata VALUES (?, ?)').run(body.key, JSON.stringify(body.value)); return { ok: true } }
   if (operation === 'get') { const row = db.prepare('SELECT value FROM metadata WHERE key = ?').get(body.key); return row ? JSON.parse(row.value) : null }
   if (operation === 'list') return db.prepare('SELECT key, value FROM metadata WHERE substr(key,1,?) = ? ORDER BY key').all(body.prefix.length, body.prefix).map(row => ({ key: row.key, value: JSON.parse(row.value) }))
   throw new Error('unknown fixture metadata operation')
  }
 }
 for (const room of inventory) await metadata('put', { key: 'room:' + room, value: { createdAt: now, displayName: room === 'qnow-day2' ? 'Day2' : room === longRoom ? 'A very long display name '.repeat(12) : room } })
 for (const room of ['A', 'B', 'qnow-day2', 'future', longRoom, 'registered-199', 'denied']) {
  const initial = await data('/doc?room=' + room), parentId = records(initial).find(record => record.typeName === 'page').id
  await data('/doc?room=' + room, null, 'PATCH', { put: [note({ id: 'shape:' + room, text: room + ' sentinel', x: 360, y: 220, parentId })] })
 }
 const sessionKey = 'browser-session:' + hash(token)
 const session = { actorType: 'human', backendId: config.backendId, memberId: 'person', generation: 1, expiresAt: now + 900_000, verifiedHumanSignInAt: now, humanRevalidateBy: now + 604800_000, csrfDigest: hash('csrf'), revoked: false }
 await metadata('put', { key: sessionKey, value: session })
 process.env.JOURNEY_API_PORT = String(apiPort); process.env.VITE_JOURNEY_HUMAN_ENTRY = 'true'
 if (adapter === 'node') process.env.JOURNEY_HUMAN_CONFIG = configFile
 vite = await viteServer({ configFile: join(root, 'vite.config.mts'), cacheDir: join(scratch, 'vite-cache'), server: { host: '127.0.0.1', port: uiPort, strictPort: true } }); await vite.listen()
 browser = await chromium.launch({ headless: true })
 const context = await browser.newContext({ viewport: { width: 1440, height: 900 } })
 await context.addCookies([{ name: 'journey_human', value: token, url: origin, httpOnly: true, sameSite: 'Strict' }])
 const external = [], uiErrors = []
 await context.route('**/*', route => {
  const url = new URL(route.request().url())
  if (url.origin === origin) return route.continue()
  if (url.hostname === 'cdn.tldraw.com') return route.fulfill({ path: join(assets, url.pathname.replace(/^\/[^/]+\//, '')) })
  external.push(url.origin + url.pathname); return route.abort()
 })
 report.responses = []; report.browserEvents = []; report.confirmations = []
 page = await context.newPage(); page.on('framenavigated', frame => { if (frame === page.mainFrame()) report.browserEvents.push({ event: 'navigation', url: frame.url() }) }); page.on('console', message => { if (message.text().includes('[vite]') || message.type() === 'error') report.browserEvents.push({ event: message.type(), text: message.text() }) }); page.on('response', async response => { const responseUrl = new URL(response.url()); if (responseUrl.pathname === '/doc' && responseUrl.searchParams.has('_human')) { const bytes = await response.body().catch(() => null); const timing = response.request().timing(); report.confirmations.push({ room: responseUrl.searchParams.get('room'), status: response.status(), bytes: bytes?.length, milliseconds: Math.round(timing.responseEnd) }) }; if (new URL(response.url()).pathname.startsWith('/auth/') || response.status() >= 400) { const body = await response.json().catch(() => ({})); report.responses.push({ path: new URL(response.url()).pathname + new URL(response.url()).search, status: response.status(), category: body.category, error: body.error }) } }); page.on('pageerror', error => uiErrors.push(error.message))
 const humanPath = path => { const url = new URL(origin + path); for (const [key, value] of Object.entries({ _human: 'person', _backend: config.backendId, _humanAt: String(now), _humanRoom: 'A' })) url.searchParams.set(key, value); return url.href }
 const click = async locator => {
  await locator.waitFor({ state: 'visible' }); await locator.scrollIntoViewIfNeeded(); await locator.click({ trial: true })
  assert.ok(await locator.evaluate(el => { const b = el.getBoundingClientRect(), hit = document.elementFromPoint(b.x + b.width / 2, b.y + b.height / 2); return el === hit || el.contains(hit) }), 'pointer center obstructed')
  await locator.click()
 }
 const openRooms = async () => { if (!await page.locator('.journey-room-menu').isVisible()) await click(page.getByTestId('room-trigger')) }
 const chooseRoom = async room => { await openRooms(); await page.getByRole('textbox', { name: 'Search rooms' }).fill(''); await click(page.locator('[data-room-id="' + room + '"]')) }
 const ready = async room => {
  await page.waitForFunction(room => (window.editor?.getShape('shape:' + room) && document.querySelector('[data-testid="room-trigger"]')?.title.endsWith('Connected')) || document.querySelector('[data-testid="room-trigger"]')?.title.includes('Edits not confirmed'), room)
  if (!await page.evaluate(room => !!window.editor?.getShape('shape:' + room), room)) {
   const from = new URL(page.url()).searchParams.get('room')
   report.visibleRetries ??= []; report.visibleRetries.push({ from, to: room, reason: 'conservative complete-record confirmation held source' })
   await stableSource(from); await chooseRoom(room)
   await page.waitForFunction(room => window.editor?.getShape('shape:' + room) && document.querySelector('[data-testid="room-trigger"]')?.title.endsWith('Connected'), room)
  }
  assert.equal(new URL(page.url()).searchParams.get('room'), room)
 }
 const stableSource = async (room = 'A') => {
  await waitFor(async () => {
   const local = await page.evaluate(() => window.editor?.store.getStoreSnapshot('document').store)
   const remote = Object.fromEntries(records(await data('/doc?room=' + encodeURIComponent(room))).map(record => [record.id, record]))
   const ordered = value => Array.isArray(value) ? value.map(ordered) : value && typeof value === 'object' ? Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([key, item]) => [key, ordered(item)])) : value
   return JSON.stringify(ordered(local)) === JSON.stringify(ordered(remote))
  })
 }
 let socketAction
 report.socketRoutes = []
 await page.routeWebSocket(url => url.pathname === '/connect/B', socket => { report.socketRoutes.push({ url: socket.url(), intercepted: !!socketAction }); if (socketAction) socketAction(socket); else socket.connectToServer() })
 await page.goto(origin + '/?room=A&keep=yes'); await ready('A'); await stableSource()
 await check('human catalog is exact registered intersection with future rooms, display labels and no activity payload', async () => {
  const response = await context.request.get(humanPath('/auth/rooms')); assert.equal(response.status(), 200)
  const result = await response.json(); assert.deepEqual(result.rooms.map(room => room.roomId).sort(), inventory.slice().sort())
  assert.deepEqual(Object.keys(result).sort(), ['backendId', 'memberId', 'rooms'])
  assert.equal(result.rooms.find(room => room.roomId === 'qnow-day2').displayName, 'Day2')
  await openRooms(); assert.equal(await page.locator('[data-room-id]').count(), inventory.length)
  assert.equal(await page.locator('[data-room-id="denied"]').count(), 0); assert.equal(await page.locator('[data-room-id="missing"]').count(), 0)
  await page.keyboard.press('Escape')
 })
 await check('A B qnow-day2 future A switch keeps exact sentinels and URL only after sync', async () => {
  for (const room of ['B', 'qnow-day2', 'future', 'A']) { await chooseRoom(room); await ready(room); assert.equal(await page.evaluate(room => window.editor.store.allRecords().filter(r => r.typeName === 'shape').some(r => r.id !== 'shape:' + room), room), false) }
  assert.equal(new URL(page.url()).searchParams.get('keep'), 'yes')
  for (const room of ['A', 'B', 'qnow-day2', 'future']) assert.deepEqual(records(await data('/doc?room=' + room)).filter(r => r.typeName === 'shape').map(r => r.id), ['shape:' + room])
  await page.goBack(); await ready('future'); await page.goForward(); await ready('A')
 })
 await check('target admission failure preserves source editor identity, records and URL', async () => {
  await page.evaluate(() => { window.sourceEditor = window.editor })
  await page.route('**/auth/entry?room=B', route => route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ category: 'synthetic_unavailable' }) }))
  await chooseRoom('B'); await page.getByText(/Target B unavailable/).waitFor()
  assert.equal(new URL(page.url()).searchParams.get('room'), 'A'); assert.equal(await page.evaluate(() => window.editor === window.sourceEditor && !!window.editor.getShape('shape:A')), true)
  await page.unroute('**/auth/entry?room=B')
 })
 await check('dirty confirmation failure retains source and does not stage a target', async () => {
  let targetAdmissions = 0
  const listener = request => { if (request.url().includes('/auth/entry?room=B')) targetAdmissions++ }
  page.on('request', listener)
  await page.route('**/doc?room=A*', route => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ snapshot: { documents: [] } }) }))
  await chooseRoom('B'); await page.getByText('Edits not confirmed. Stay here; select a room to retry.').waitFor()
  assert.equal(targetAdmissions, 0); assert.equal(await page.evaluate(() => window.editor === window.sourceEditor), true)
  assert.equal(new URL(page.url()).searchParams.get('room'), 'A')
  await page.unroute('**/doc?room=A*'); page.off('request', listener)
 })
 await check('bounded complete-record coediting during confirmation retains source and uses one source GET', async () => {
  await stableSource()
  let reads = 0
  const started = performance.now()
  await page.route('**/doc?room=A*', async route => {
   reads++
   const doc = await data('/doc?room=A'), original = records(doc).find(record => record.id === 'shape:A')
   for (const color of ['blue', 'green', 'orange', 'blue']) {
    await data('/doc?room=A', null, 'PATCH', { put: [{ ...original, props: { ...original.props, color } }] })
    await new Promise(resolve => setTimeout(resolve, 35))
   }
   await route.continue()
  })
  await chooseRoom('B'); await page.getByText('Edits not confirmed. Stay here; select a room to retry.').first().waitFor()
  assert.equal(reads, 1); assert.equal(new URL(page.url()).searchParams.get('room'), 'A')
  assert.equal(await page.evaluate(() => window.editor === window.sourceEditor), true)
  report.coeditingConfirmation = { sourceGets: reads, completeRecordWrites: 4, milliseconds: Math.round(performance.now() - started), outcome: 'source retained; explicit retry available' }
  await page.unroute('**/doc?room=A*'); await stableSource()
 })
 await check('target socket timeout and changed source during staging retain source and URL', async () => {
  socketAction = () => {}
  await chooseRoom('B'); await page.getByText('Target B timed out. Original room retained.').waitFor({ timeout: 12000 })
  assert.equal(await page.evaluate(() => window.editor === window.sourceEditor), true); assert.equal(new URL(page.url()).searchParams.get('room'), 'A')
  socketAction = null
  let release
  const connected = new Promise(resolve => {
   socketAction = socket => { release = () => socket.connectToServer(); resolve() }
  })
  await chooseRoom('B'); await connected
  await page.evaluate(() => { window.editor.updateShape({ id: 'shape:A', type: 'note', props: { color: 'red' } }) })
  release(); await page.getByText('Source changed while connecting. Stay here; select a room to retry.').waitFor()
  assert.equal(await page.evaluate(() => window.editor === window.sourceEditor), true); assert.equal(new URL(page.url()).searchParams.get('room'), 'A')
  socketAction = null
 })
 await page.reload(); await ready('A'); await stableSource()
 await check('expired target after catalog read is denied without replacing source', async () => {
  const key = 'member-room:person:B', saved = await metadata('get', { key })
  await metadata('put', { key, value: { ...saved, expiresAt: 1 } })
  await chooseRoom('B'); await page.getByText(/Target B unavailable \(room_denied\)/).waitFor()
  assert.equal(new URL(page.url()).searchParams.get('room'), 'A'); assert.equal(await page.evaluate(() => !!window.editor.getShape('shape:A')), true)
  await metadata('put', { key, value: saved })
 })
 await check('replacement sign-in while target is staged cannot activate or reconnect the old source context', async () => {
  await stableSource(); await page.evaluate(() => { window.sourceEditor = window.editor })
  let release
  const entered = new Promise(resolve => { socketAction = socket => { release = () => socket.connectToServer(); resolve() } })
  await chooseRoom('B'); await entered
  const replacement = 'synthetic-replacement'
  await metadata('put', { key: 'browser-session:' + hash(replacement), value: { ...session, verifiedHumanSignInAt: now + 1 } })
  await context.addCookies([{ name: 'journey_human', value: replacement, url: origin, httpOnly: true, sameSite: 'Strict' }])
  release(); await page.getByText(/Source access paused/).first().waitFor()
  assert.equal(new URL(page.url()).searchParams.get('room'), 'A')
  assert.equal(await page.evaluate(() => window.editor === window.sourceEditor && window.editor.getInstanceState().isReadonly), true)
  socketAction = null
  await context.addCookies([{ name: 'journey_human', value: token, url: origin, httpOnly: true, sameSite: 'Strict' }])
  await page.reload(); await ready('A')
 })
 await check('empty, malformed and unavailable inventory stay distinct and refresh recovers', async () => {
  const refresh = async () => { await openRooms(); await click(page.getByRole('button', { name: 'Refresh rooms' })) }
  await page.route('**/auth/rooms*', route => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ memberId: 'person', backendId: config.backendId, rooms: [] }) }))
  await refresh(); await page.getByText('No permitted registered rooms').waitFor(); assert.equal(await page.locator('[data-room-id]').count(), 0)
  await page.unroute('**/auth/rooms*')
  await page.route('**/auth/rooms*', route => route.fulfill({ status: 200, contentType: 'application/json', body: '{"rooms": [null]}' }))
  await refresh(); await page.getByText('Rooms unavailable. Refresh to retry.').first().waitFor(); await page.unroute('**/auth/rooms*')
  let reads = 0
  await page.route('**/auth/rooms*', route => { reads++; return route.fulfill({ status: 503, body: 'unavailable' }) })
  await refresh(); await page.getByText('Rooms unavailable. Refresh to retry.').first().waitFor(); await page.waitForTimeout(500); assert.equal(reads, 1)
  await page.unroute('**/auth/rooms*'); await refresh(); await page.locator('[data-room-id="A"]:not(:disabled)').waitFor(); await page.keyboard.press('Escape')
 })
 await check('desktop and 390px native light/dark long and 200-room menus have 44px center hits, normal scrolling and Escape focus', async () => {
  for (const width of [1440, 390]) for (const theme of ['light', 'dark']) {
   await page.setViewportSize({ width, height: 844 }); await page.evaluate(theme => window.editor.user.updateUserPreferences({ colorScheme: theme }), theme)
   await page.waitForFunction(theme => window.editor.getColorMode() === theme, theme)
   await openRooms()
   const menu = page.locator('.journey-room-menu'), b = await menu.boundingBox(); assert.ok(b.x >= 0 && b.x + b.width <= width)
   assert.equal(await menu.evaluate(el => el.scrollWidth > el.clientWidth), false)
   for (const control of await page.locator('.journey-room-trigger, .journey-room-menu input, .journey-room-menu button').all()) assert.ok((await control.boundingBox()).height >= 44)
   await page.locator('.journey-room-options').hover(); await page.mouse.wheel(0, 20000)
   await page.waitForFunction(() => document.querySelector('.journey-room-options').scrollTop > 100)
   const last = page.locator('[data-room-id="registered-199"]'); await last.scrollIntoViewIfNeeded(); await click(last)
   
   await ready('registered-199')
   await openRooms(); await page.getByRole('textbox', { name: 'Search rooms' }).fill('qnow-day2')
   await page.getByRole('textbox', { name: 'Search rooms' }).press('Enter'); await ready('qnow-day2')
   await openRooms(); await page.getByRole('textbox', { name: 'Search rooms' }).fill('very long display')
   assert.equal(await page.locator('[data-room-id]').count(), 1); assert.ok(await page.locator('[data-room-id]').innerText().then(t => t.includes(longRoom)))
   await page.screenshot({ path: join(scratch, width + '-' + theme + '-long.png') })
   await page.keyboard.press('Escape'); await page.waitForFunction(() => document.activeElement === document.querySelector('[data-testid="room-trigger"]'))
   await chooseRoom('A'); await ready('A')
  }
 })
 await page.evaluate(() => window.editor.user.updateUserPreferences({ colorScheme: 'light' }))
 await checkNativeUi({ page, context, adapter, origin, scratch, saveDir, longRoom, data, request: (path, _id) => request(path), check, click, ready, chooseRoom, openRooms })
 if (adapter === 'node') await check('a delayed source save completion cannot update the target save UI or document', async () => {
  await stableSource()
  const before = await data('/doc?room=B')
  let release
  const entered = new Promise(resolve => {
   page.route('**/save?*', async route => {
    if (route.request().method() !== 'POST') return route.continue()
    resolve(); await new Promise(resolve => { release = resolve }); await route.continue()
   })
  })
  await click(page.getByRole('button', { name: 'save', exact: true }))
  await page.getByRole('textbox', { name: 'Filename' }).fill('delayed-source.tldr')
  await click(page.getByRole('button', { name: 'write', exact: true })); await entered
  await chooseRoom('B'); await ready('B'); release()
  await waitFor(async () => { try { return !!JSON.parse(await readFile(join(saveDir, 'delayed-source.tldr'), 'utf8')) } catch { return false } })
  assert.equal(await page.locator('.journey-save-note').count(), 0)
  assert.deepEqual((await data('/doc?room=B')).snapshot.documents, before.snapshot.documents)
  const saved = JSON.parse(await readFile(join(saveDir, 'delayed-source.tldr'), 'utf8')); assert.ok(saved.records.some(record => record.id === 'shape:A')); assert.equal(saved.records.some(record => record.id === 'shape:B'), false)
  await page.unroute('**/save?*'); await chooseRoom('A'); await ready('A')
 })
 await check('a closed source document popup cannot reopen from a delayed response after target activation', async () => {
  await page.evaluate(() => { const editor = window.editor; editor.setCurrentTool('select'); editor.select('shape:A'); editor.zoomToSelection({ inset: 150 }) })
  let release
  const entered = new Promise(resolve => {
   page.route('**/repo-doc?*', async route => { resolve(); await new Promise(resolve => { release = resolve }); await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ state: 'unavailable', reason: 'late source result' }) }).catch(() => {}) })
  })
  await click(page.locator('a.tl-hyperlink-button')); await entered; await page.locator('dialog.doc-popup[open]').waitFor()
  await page.keyboard.press('Escape'); await page.locator('dialog.doc-popup').waitFor({ state: 'detached' })
  await stableSource(); await chooseRoom('B'); await ready('B'); release(); await page.waitForTimeout(100)
  assert.equal(await page.locator('dialog.doc-popup').count(), 0); assert.equal(await page.getByText('late source result').count(), 0)
  await page.unroute('**/repo-doc?*'); await chooseRoom('A'); await ready('A')
 })
 await check('catalog policy denial freezes the same source editor and keeps the original URL', async () => {
  await page.evaluate(() => { window.sourceEditor = window.editor })
  await page.route('**/auth/rooms*', route => route.fulfill({ status: 403, contentType: 'application/json', body: JSON.stringify({ category: 'authority_denied' }) }))
  await openRooms(); await click(page.getByRole('button', { name: 'Refresh rooms' })); await page.getByText(/Source access paused/).first().waitFor()
  assert.equal(new URL(page.url()).searchParams.get('room'), 'A'); assert.equal(await page.evaluate(() => window.editor === window.sourceEditor && window.editor.getInstanceState().isReadonly), true)
  await page.keyboard.press('Escape'); await page.unroute('**/auth/rooms*'); await page.reload(); await ready('A')
 })
 await check('legacy exact links keep A B qnow-day2 identity and denied or missing links create no substitute', async () => {
  for (const room of ['A', 'B', 'qnow-day2']) { await page.goto(origin + '/?room=' + room); await ready(room) }
  for (const room of ['denied', 'missing']) { await page.goto(origin + '/?room=' + room); await page.locator('.human-entry').waitFor(); assert.equal(await page.evaluate(() => !!window.editor), false); assert.equal(new URL(page.url()).searchParams.get('room'), room) }
  assert.equal(await metadata('get', { key: 'room:missing' }), null)
 })
 await page.goto(origin + '/?room=A'); await ready('A'); await stableSource()
 await check('source revocation freezes retained editor, sends no source document confirmation and alternative opens separately', async () => {
  await page.evaluate(() => { window.sourceEditor = window.editor })
  const key = 'member-room:person:A', grant = await metadata('get', { key })
  await metadata('put', { key, value: { ...grant, expiresAt: 1 } })
  let reads = 0
  const listener = request => { if (new URL(request.url()).pathname === '/doc') reads++ }; page.on('request', listener)
  await chooseRoom('B'); await page.getByText(/Source access paused/).first().waitFor()
  assert.equal(await page.evaluate(() => window.editor === window.sourceEditor && window.editor.getInstanceState().isReadonly), true)
  assert.equal(new URL(page.url()).searchParams.get('room'), 'A'); assert.equal(reads, 0)
  await page.evaluate(() => { const url = new URL(location.href); url.searchParams.set('room', 'B'); history.pushState(null, '', url); window.dispatchEvent(new PopStateEvent('popstate')) })
  assert.equal(new URL(page.url()).searchParams.get('room'), 'A'); assert.equal(reads, 0)
  const popup = context.waitForEvent('page'); await chooseRoom('B'); const alternate = await popup
  await alternate.waitForFunction(() => window.editor?.getShape('shape:B')); assert.equal(new URL(alternate.url()).searchParams.get('room'), 'B')
  assert.equal(await page.evaluate(() => window.editor === window.sourceEditor), true); assert.equal(reads, 0)
  await alternate.close(); page.off('request', listener)
 })
 assert.deepEqual(uiErrors, []); assert.deepEqual(external, [])
 report.result = 'PASS'
} catch (error) {
 report.result = 'FAIL'; report.error = error.stack; process.exitCode = 1
 if (page && !page.isClosed()) await page.screenshot({ path: join(scratch, 'failure.png') }).catch(() => {})
} finally {
 await browser?.close(); await vite?.close(); db?.close(); await host?.close()
 if (child?.exitCode === null) { const exit = new Promise(resolve => child.once('exit', resolve)); child.kill('SIGTERM'); await exit }
 await writeFile(join(scratch, 'report.json'), JSON.stringify(report, null, 2)); await writeFile(join(scratch, 'server.log'), logs)
 console.log(JSON.stringify({ result: report.result, evidence: scratch, error: report.error }))
}
