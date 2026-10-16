import assert from 'node:assert/strict'
import { spawn, execFileSync } from 'node:child_process'
import { createServer } from 'node:net'
import { createHash, randomBytes } from 'node:crypto'
import { mkdtemp, writeFile, readFile, mkdir, symlink } from 'node:fs/promises'
import { join } from 'node:path'
import { createServer as viteServer } from 'vite'
import { chromium } from 'playwright'
import { WebSocket } from 'ws'
import { startCloudflare } from './cloudflare-local.mjs'
import { note } from '../lib/records.mjs'
import { checkNativeUi } from './native-ui-check.mjs'

const root = new URL('..', import.meta.url).pathname.replace(/\/$/, '')
const adapter = process.argv[process.argv.indexOf('--adapter') + 1]
if (!['node', 'cloudflare-local'].includes(adapter) || !process.argv.includes('--synthetic')) throw new Error('usage: --adapter node|cloudflare-local --synthetic; local targets only')
const assetDir = process.env.JOURNEY_TLDRAW_ASSETS
if (!assetDir) throw new Error('Set JOURNEY_TLDRAW_ASSETS to an unpacked @tldraw/assets@5.4.0 package; this check makes no asset downloads')
const evidenceRoot = process.env.JOURNEY_CHECK_OUTPUT_DIR || join(root, '.host-check')
await mkdir(evidenceRoot, { recursive: true })
const scratch = await mkdtemp(join(evidenceRoot, 'room-switch-'))
const freePort = () => new Promise((resolve, reject) => { const server = createServer(); server.once('error', reject); server.listen(0, '127.0.0.1', () => { const port = server.address().port; server.close(() => resolve(port)) }) })
const port = await freePort(), browserPort = await freePort()
const apiPrefix = adapter === 'cloudflare-local' ? '/journey/api' : ''
const api = `http://127.0.0.1:${port}`, origin = `https://localhost:${browserPort}`
const secret = randomBytes(32).toString('base64url'), token = id => `${id}.${secret}`
const longRoom = 'project-very-long-room-identifier-for-native-menu-check'
const inventory = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', longRoom]
const grants = ['browser', 'restricted', 'other'].map(id => ({ credentialId: id, principalId: id, secretDigest: createHash('sha256').update(secret).digest('hex'), rooms: id === 'browser' ? inventory : id === 'restricted' ? ['A'] : ['Hidden'], expiresAt: Date.now() + 3600_000, revoked: false }))
const grantFile = join(scratch, 'grants.json')
await writeFile(grantFile, JSON.stringify(grants), { mode: 0o600 })
const report = { adapter, nativeOnly: process.argv.includes('--native-only'), viewports: process.env.JOURNEY_CHECK_VIEWPORTS || 'all', candidate: execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(), dirty: !!execFileSync('git', ['-C', root, 'status', '--porcelain'], { encoding: 'utf8' }).trim(), checks: [], hosted: 'NOT RUN', nativeAgents: 'NOT RUN', build: 'Vite development; SDK enforcement unchanged' }
const check = async (name, fn) => { await fn(); report.checks.push({ name, result: 'PASS' }); console.log('PASS ' + name) }
const request = (path, id = 'browser', method = 'GET', body) => fetch(api + path, { method, headers: { Authorization: 'Bearer ' + token(id), ...(body ? { 'Content-Type': 'application/json' } : {}) }, body: body ? JSON.stringify(body) : undefined })
const data = async (path, id, method, body) => { const response = await request(path, id, method, body); assert.equal(response.status, 200, await response.clone().text()); return response.json() }
const rpc = (name, args, id) => data('/mcp', id, 'POST', { jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name, arguments: args } })
const records = doc => doc.snapshot.documents.map(item => item.state)
const shapes = doc => records(doc).filter(record => record.typeName === 'shape')
const waitFor = async (predicate, attempts = 100) => { for (let i = 0; i < attempts; i++) { if (await predicate()) return; await new Promise(resolve => setTimeout(resolve, 100)) } throw new Error('bounded condition timeout') }
let host, child, vite, browser, page
let childLogs = ''
const fixture = join(scratch, 'fixture'), saveDir = join(scratch, 'saved')
await mkdir(join(fixture, 'docs'), { recursive: true })
await writeFile(join(fixture, 'docs', 'chapter.md'), '# Synthetic chapter\n\n## Sequence\n\n' + Array.from({ length: 60 }, (_, i) => 'Paragraph ' + i + ' of the local synthetic document.').join('\n\n'))
for (const args of [['init', '-q', '-b', 'main'], ['add', 'docs/chapter.md'], ['-c', 'user.name=Synthetic check', '-c', 'user.email=check@example.invalid', 'commit', '-qm', 'test fixture']]) execFileSync('git', ['-C', fixture, ...args], { stdio: 'pipe' })

try {
 if (adapter === 'cloudflare-local') {
  await symlink(join(root, 'node_modules'), join(scratch, 'node_modules'), 'dir')
  host = await startCloudflare({ dir: join(scratch, 'private'), port, origin, grants })
 }
 else {
  child = spawn(process.execPath, ['--import', 'tsx', join(root, 'server/canvas-server.ts')], { cwd: root, env: { ...process.env, JOURNEY_PRIVATE_DIR: join(scratch, 'private'), JOURNEY_API_PORT: String(port), JOURNEY_ORIGIN: origin, JOURNEY_GRANTS_FILE: grantFile, JOURNEY_SAVE_DIR: saveDir, JOURNEY_DOC_REPOS: 'synthetic/chapter=' + fixture, JOURNEY_ROOM_REPOS: JSON.stringify({ A: ['synthetic/chapter'] }) }, stdio: ['ignore', 'pipe', 'pipe'] })
  child.stdout.on('data', value => { childLogs += value }); child.stderr.on('data', value => { childLogs += value })
  host = { close: () => new Promise(resolve => { if (child.exitCode !== null) return resolve(); child.once('exit', resolve); child.kill('SIGTERM') }) }
 }
 await waitFor(async () => { try { return (await request('/health')).ok } catch { return false } })
 for (const room of [...inventory, 'Hidden']) {
  const id = room === 'Hidden' ? 'other' : 'browser'
  const doc = await data('/doc?room=' + room, id)
  const parentId = records(doc).find(record => record.typeName === 'page').id
  await data('/doc?room=' + room, id, 'PATCH', { put: [note({ id: 'shape:' + room, text: room + ' original note', x: 360, y: 220, parentId })] })
 }
 await check('HTTP and MCP inventories filter grants; forged HTTP/MCP/socket room access denied', async () => {
  assert.deepEqual((await data('/health')).rooms.sort(), inventory.slice().sort())
  assert.deepEqual((await rpc('health', {}, 'restricted')).result.structuredContent.rooms, ['A'])
  for (const path of ['/doc?room=B', '/doc?room=Hidden', '/capabilities?room=B']) assert.equal((await request(path, 'restricted')).status, 403)
  assert.equal((await request('/mcp', 'restricted', 'POST', { jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: 'get_doc', arguments: { room: 'B' } } })).status, 403)
  await new Promise((resolve, reject) => {
   const ws = new WebSocket(api.replace('http', 'ws') + '/connect/B?sessionId=forged', { headers: { Origin: origin, Authorization: 'Bearer ' + token('restricted') } })
   ws.on('unexpected-response', (_request, response) => { response.resume(); try { assert.equal(response.statusCode, 403); resolve() } catch (error) { reject(error) } })
   ws.on('open', () => { ws.close(); reject(new Error('forged socket admitted')) }); ws.on('error', reject)
  })
 })
 const key = join(scratch, 'key.pem'), cert = join(scratch, 'cert.pem')
 execFileSync('openssl', ['req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-keyout', key, '-out', cert, '-days', '1', '-subj', '/CN=localhost'], { stdio: 'pipe' })
 vite = await viteServer({ configFile: join(root, 'vite.config.mts'), optimizeDeps: { include: ['@tldraw/mermaid'] }, define: { 'import.meta.env.VITE_JOURNEY_API_URL': JSON.stringify(apiPrefix) }, server: { host: '127.0.0.1', port: browserPort, strictPort: true, https: { key: await readFile(key), cert: await readFile(cert) }, proxy: Object.fromEntries(['/connect', '/uploads/', '/repo-doc', '/save', '/session', '^/doc($|[?])', '/health', '/capabilities', '/mcp'].map(route => [apiPrefix ? apiPrefix + (route.startsWith('^') ? '/doc' : route) : route, { target: api, ws: route === '/connect', rewrite: path => apiPrefix ? path.slice(apiPrefix.length) : path }])) } })
 await vite.listen()
 browser = await chromium.launch({ headless: true })
 const context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1280, height: 820 } })
 await context.request.post(origin + apiPrefix + '/session', { headers: { Authorization: 'Bearer ' + token('browser'), Origin: origin } }).then(response => assert.equal(response.status(), 200))
 page = await context.newPage()
 const external = []
 await context.route('**/*', async route => {
  const url = new URL(route.request().url())
  if (url.origin === origin) return route.continue()
  if (assetDir && url.hostname === 'cdn.tldraw.com') {
   const path = url.pathname.replace(/^\/[^/]+\//, '')
   if (!path.includes('..')) return route.fulfill({ path: join(assetDir, path) })
  }
  external.push(url.origin + url.pathname)
  return route.abort()
 })
 report.blockedExternalRequests = external

 report.browserEvents = []
 page.on('framenavigated', frame => { if (frame === page.mainFrame()) report.browserEvents.push({ event: 'navigation', url: frame.url() }) })
 page.on('console', message => { if (message.type() === 'error' || message.text().includes('[vite]')) report.browserEvents.push({ event: message.type(), text: message.text() }) })
 page.on('pageerror', error => report.browserEvents.push({ event: 'pageerror', message: error.message }))
 await page.addInitScript(() => {
  window.observedSockets = []
  window.WebSocket = class extends WebSocket {
   constructor(...args) { super(...args); window.observedSockets.push(this) }
   close(...args) { this.observedClose = args; return super.close(...args) }
  }
 })
 const sockets = []
 page.on('websocket', socket => { if (socket.url().includes('/connect/')) sockets.push(socket) })
 const click = async locator => {
  await locator.waitFor({ state: 'visible' }); await locator.scrollIntoViewIfNeeded(); await locator.click({ trial: true })
  assert.ok(await locator.evaluate(el => { const r = el.getBoundingClientRect(); const hit = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2); return hit === el || el.contains(hit) }), 'control centre obstructed: ' + await locator.evaluate(el => el.outerHTML.slice(0, 200)))
  await locator.click()
 }
 const openRooms = async () => { if (!await page.locator('.journey-room-menu').isVisible()) await click(page.getByTestId('room-trigger')) }
 const chooseRoom = async room => {
  if (await page.locator('#journey-room').isVisible()) return page.locator('#journey-room').selectOption(room)
  await openRooms(); await page.getByRole('textbox', { name: 'Search rooms' }).fill('')
  await click(page.locator('.journey-room-options button').filter({ hasText: new RegExp('^' + room + '$') }))
 }
 const ready = async room => {
  await page.waitForFunction(room => window.editor?.getShape('shape:' + room), room)
  await page.waitForFunction(() => document.querySelector('[data-testid="room-trigger"]')?.title.endsWith('Connected'))
  assert.equal(await page.locator('.journey-room-recovery').count(), 0)
 }

 await page.goto(origin + '/?room=A&keep=yes')
 await ready('A')
 if (!process.argv.includes('--native-only')) {
 await check('room selector shows the authorized inventory and an acknowledged browser edit survives switching', async () => {
  await openRooms(); assert.deepEqual(await page.locator('.journey-room-options button').allTextContents(), inventory.slice().sort()); await page.keyboard.press('Escape')
  await page.screenshot({ path: join(scratch, 'rooms-a.png') })
  const point = await page.evaluate(() => { const bounds = window.editor.getShapePageBounds('shape:A'); return window.editor.pageToScreen({ x: bounds.x + 90, y: bounds.y + 70 }) })
  await page.mouse.dblclick(point.x, point.y)
  const editable = page.locator('[contenteditable="true"]').last()
  await editable.waitFor({ state: 'visible' }); await editable.fill('A acknowledged browser edit')
  await page.keyboard.press('Escape')
  await waitFor(async () => JSON.stringify(shapes(await data('/doc?room=A'))).includes('A acknowledged browser edit'))
  const oldSockets = sockets.filter(socket => !socket.isClosed())
  await chooseRoom('B'); await ready('B')
  assert.equal(new URL(page.url()).searchParams.get('keep'), 'yes')
  assert.equal(await page.evaluate(() => !!window.editor.getShape('shape:A')), false)
  const closingAt = performance.now()
  try { await waitFor(() => oldSockets.every(socket => socket.isClosed()), 350); report.oldSocketClosedMs = Math.round(performance.now() - closingAt) }
  catch (error) {
   report.socketDiagnostic = { playwright: oldSockets.map(socket => ({ url: socket.url(), closed: socket.isClosed() })), browser: await page.evaluate(() => window.observedSockets.map(socket => ({ url: socket.url, state: socket.readyState, close: socket.observedClose }))), server: await data('/health') }
   throw error
  }
  await page.screenshot({ path: join(scratch, 'rooms-b.png') })
  await page.goBack(); await ready('A')
  assert.ok(JSON.stringify(await page.evaluate(() => window.editor.getShape('shape:A'))).includes('A acknowledged browser edit'))
  await page.goForward(); await ready('B'); await page.reload(); await ready('B')
  assert.deepEqual(shapes(await data('/doc?room=B')).map(shape => shape.id), ['shape:B'])
  await chooseRoom('A'); await ready('A')
  assert.ok(JSON.stringify((await rpc('get_doc', { room: 'A' }, 'restricted')).result.structuredContent).includes('A acknowledged browser edit'))
 })
 await check('immediate browser edit then blur and switch preserves the edit without pre-switch acknowledgement polling', async () => {
  const point = await page.evaluate(() => { const bounds = window.editor.getShapePageBounds('shape:A'); return window.editor.pageToScreen({ x: bounds.x + 90, y: bounds.y + 70 }) })
  await page.mouse.dblclick(point.x, point.y)
  const editable = page.locator('[contenteditable="true"]').last()
  await editable.waitFor({ state: 'visible' }); await editable.fill('A immediate switch edit')
  await page.getByTestId('room-trigger').focus()
  await chooseRoom('B')
  await page.waitForFunction(() => new URL(location.href).searchParams.get('room') === 'B' || document.querySelector('.journey-rooms-status')?.textContent?.includes('Edits not confirmed'))
  if (new URL(page.url()).searchParams.get('room') === 'A') {
   report.immediateSwitchSafelyHeld = true
   assert.ok(JSON.stringify(await page.evaluate(() => window.editor.getShape('shape:A'))).includes('A immediate switch edit'))
   await waitFor(async () => JSON.stringify(shapes(await data('/doc?room=A'))).includes('A immediate switch edit'))
   await chooseRoom('B')
  }
  await ready('B')
  await waitFor(async () => JSON.stringify(shapes(await data('/doc?room=A'))).includes('A immediate switch edit'))
  assert.deepEqual(shapes(await data('/doc?room=B')).map(shape => shape.id), ['shape:B'])
  await chooseRoom('A'); await ready('A')
  assert.ok(JSON.stringify(await page.evaluate(() => window.editor.getShape('shape:A'))).includes('A immediate switch edit'))
 })
 await check('delayed verification and offline failure keep the current editor and unconfirmed edits', async () => {
  const stale = await data('/doc?room=A')
  const point = await page.evaluate(() => { const bounds = window.editor.getShapePageBounds('shape:A'); return window.editor.pageToScreen({ x: bounds.x + 90, y: bounds.y + 70 }) })
  await page.mouse.dblclick(point.x, point.y)
  const editable = page.locator('[contenteditable="true"]').last(); await editable.waitFor({ state: 'visible' }); await editable.fill('A delayed confirmation edit')
  let release, requested
  const entered = new Promise(resolve => { requested = resolve })
  await page.route('**/doc?room=A', async route => { requested(); await new Promise(resolve => { release = resolve }); await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(stale) }) })
  await page.getByTestId('room-trigger').focus(); await chooseRoom('B')
  await entered
  assert.equal(new URL(page.url()).searchParams.get('room'), 'A')
  assert.equal(await page.getByTestId('room-trigger').isDisabled(), true)
  release(); await page.getByText('Edits not confirmed. Stay here; select a room to retry.').waitFor()
  assert.ok(JSON.stringify(await page.evaluate(() => window.editor.getShape('shape:A'))).includes('A delayed confirmation edit'))
  await page.screenshot({ path: join(scratch, 'rooms-unconfirmed.png') })
  await page.unroute('**/doc?room=A')
  await page.route('**/doc?room=A', route => route.abort('internetdisconnected'))
  await chooseRoom('B')
  await page.waitForFunction(() => !document.querySelector('[data-testid="room-trigger"]').disabled)
  assert.equal(new URL(page.url()).searchParams.get('room'), 'A')
  assert.ok(JSON.stringify(await page.evaluate(() => window.editor.getShape('shape:A'))).includes('A delayed confirmation edit'))
  await page.unroute('**/doc?room=A')
  await waitFor(async () => JSON.stringify(shapes(await data('/doc?room=A'))).includes('A delayed confirmation edit'))
  await chooseRoom('B'); await ready('B')
  await chooseRoom('A'); await ready('A')
 })
 await check('inventory failure is visible and manual refresh recovers without polling', async () => {
  let failedReads = 0
  await page.route('**/health', route => { failedReads++; return route.fulfill({ status: 503, body: 'synthetic unavailable' }) })
  await openRooms(); await click(page.getByRole('button', { name: 'Refresh rooms' }))
  await page.getByText('Rooms unavailable. Refresh to retry.').waitFor()
  assert.equal(await page.locator('.journey-room-options button:not(:disabled)').count(), 0)
  await new Promise(resolve => setTimeout(resolve, 1200)); assert.equal(failedReads, 1)
  await page.screenshot({ path: join(scratch, 'rooms-error.png') })
  await page.unroute('**/health'); await openRooms(); await click(page.getByRole('button', { name: 'Refresh rooms' })); await ready('A')
 })
 await page.keyboard.press('Escape')
 }
 await checkNativeUi({ page, context, adapter, origin, scratch, saveDir, longRoom, data, request, check, click, ready, chooseRoom, openRooms })
 assert.deepEqual(external, [])
 await context.close()
 const restricted = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1280, height: 820 } })
 await restricted.route('https://cdn.tldraw.com/**', route => assetDir ? route.fulfill({ path: join(assetDir, new URL(route.request().url()).pathname.replace(/^\/[^/]+\//, '')) }) : route.abort())
 await restricted.request.post(origin + apiPrefix + '/session', { headers: { Authorization: 'Bearer ' + token('restricted'), Origin: origin } }).then(response => assert.equal(response.status(), 200)); page = await restricted.newPage()
 await check('forged browser URL cannot show B and selector recovers to authorized A', async () => {
  await page.goto(origin + '/?room=B')
  await page.waitForFunction(() => document.querySelector('#journey-room')?.querySelector('option[value="A"]'))
  assert.equal(await page.locator('#journey-room option[value="Hidden"]').count(), 0)
  assert.equal(await page.locator('#journey-room option[value="B"]').isDisabled(), true)
  assert.equal(await page.evaluate(() => !!window.editor?.getShape('shape:B')), false)
  await page.screenshot({ path: join(scratch, 'rooms-denied.png') })
  await chooseRoom('A'); await ready('A')
  await openRooms(); assert.deepEqual(await page.locator('.journey-room-options button').allTextContents(), ['A'])
 })
 await restricted.close()
 report.result = 'PASS'
} catch (error) {
 report.result = 'FAIL'; report.error = error.stack
 if (page && !page.isClosed()) await page.screenshot({ path: join(scratch, 'failure.png') }).catch(() => {})
 process.exitCode = 1
} finally {
 await browser?.close(); await vite?.close(); await host?.close()
 await writeFile(join(scratch, 'result.json'), JSON.stringify(report, null, 2))
 await writeFile(join(scratch, 'server.log'), childLogs)
 console.log(JSON.stringify({ result: report.result, evidence: scratch, error: report.error }))
}
