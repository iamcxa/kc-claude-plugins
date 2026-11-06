import assert from 'node:assert/strict'
import { spawn, execFileSync } from 'node:child_process'
import { mkdtemp, mkdir, writeFile, readFile } from 'node:fs/promises'
import { createServer } from 'node:net'
import { request as rawRequest } from 'node:http'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createServer as viteServer } from 'vite'
import { chromium } from 'playwright'

const root = new URL('..', import.meta.url).pathname
const assets = process.env.JOURNEY_TLDRAW_ASSETS
assert.ok(assets, 'JOURNEY_TLDRAW_ASSETS must contain @tldraw/assets@5.4.0')
const scratch = await mkdtemp(join(process.env.JOURNEY_CHECK_OUTPUT_DIR || tmpdir(), 'share-entrance-'))
const freePort = () => new Promise((resolve, reject) => {
 const server = createServer(); server.once('error', reject)
 server.listen(0, '127.0.0.1', () => { const port = server.address().port; server.close(() => resolve(port)) })
})
const apiPort = await freePort(), uiPort = await freePort(), oldPort = await freePort()
const api = `http://127.0.0.1:${apiPort}`, origin = `http://127.0.0.1:${uiPort}`, oldOrigin = `http://127.0.0.1:${oldPort}`
const env = Object.fromEntries(Object.entries(process.env).filter(([key]) => !/^(JOURNEY_|VITE_JOURNEY_)/.test(key)))
const report = { candidate: execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(), checks: [], api, origin, scratch }
let child, vite, old, browser, page, logs = ''
const forwarded = []
const journeyEnv = Object.fromEntries(Object.entries(process.env).filter(([key]) => /^(JOURNEY_|VITE_JOURNEY_)/.test(key)))
const check = async (name, run) => { await run(); report.checks.push({ name, status: 'passed' }); console.log('PASS ' + name) }
const json = async url => { const response = await fetch(url); assert.equal(response.status, 200); assert.match(response.headers.get('content-type'), /application\/json/); return response.json() }
try {
 const fixture = join(scratch, 'checkout')
 await mkdir(fixture)
 await writeFile(join(fixture, 'note.md'), 'synthetic checkout content')
 for (const args of [['init', '-q', '-b', 'main'], ['add', 'note.md'], ['-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid', 'commit', '-qm', 'synthetic']]) execFileSync('git', ['-C', fixture, ...args], { stdio: 'pipe' })
 child = spawn(process.execPath, ['--import', import.meta.resolve('tsx'), join(root, 'server/canvas-server.ts')], { cwd: scratch, env: { ...env, JOURNEY_API_PORT: String(apiPort), JOURNEY_ROOMS_DIR: join(scratch, 'rooms'), JOURNEY_ASSETS_DIR: join(scratch, 'assets'), JOURNEY_DOC_REPOS: 'synthetic/fixture=' + fixture }, stdio: ['ignore', 'pipe', 'pipe'] })
 child.stdout.on('data', value => { logs += value }); child.stderr.on('data', value => { logs += value })
 let ready = false
 for (let i = 0; i < 150; i++) {
  if (child.exitCode !== null) throw new Error(logs)
  try { if ((await fetch(api + '/health')).ok) { ready = true; break } } catch {}
  await new Promise(resolve => setTimeout(resolve, 100))
 }
 assert.ok(ready, 'API startup timed out')
 for (const room of ['A', 'B']) await json(api + '/doc?room=' + room)
 for (const key of Object.keys(journeyEnv)) delete process.env[key]
 process.env.JOURNEY_API_PORT = String(apiPort)
 vite = await viteServer({ configFile: join(root, 'vite.share.config.mts'), cacheDir: join(scratch, 'vite-cache'), plugins: [{ name: 'share-forwarding-receipt', configResolved(config) {
  for (const options of Object.values(config.server.proxy)) {
   const configure = options.configure
   options.configure = (proxy, opts) => { configure?.(proxy, opts); proxy.on('proxyReq', (_request, req) => forwarded.push({ method: req.method, url: req.url })); proxy.on('proxyReqWs', (_request, req) => { if (req.method === 'GET') forwarded.push({ method: 'WS', url: req.url }) }) }
  }
 } }], server: { port: uiPort, host: '127.0.0.1', strictPort: true } })
 await vite.listen()
 old = await viteServer({ configFile: false, root: join(root, 'server/client'), cacheDir: join(scratch, 'old-cache'), server: { port: oldPort, host: '127.0.0.1', strictPort: true, proxy: Object.fromEntries(['/connect/', '/uploads/'].map(path => [path, { target: api, ws: path === '/connect/', changeOrigin: true }])) } })
 await old.listen()
 await check('share /health returns JSON containing both legacy rooms', async () => {
  assert.deepEqual((await json(origin + '/health')).rooms.sort(), ['A', 'B'])
  assert.ok(forwarded.some(request => request.method === 'GET' && request.url === '/health'), 'receipt observes successful forwarding')
 })
 await check('legacy share withholds save, checkout, auth and browser agent routes like the old entrance', async () => {
  const marker = join(scratch, 'docs/journey/protected.tldr')
  await mkdir(join(scratch, 'docs/journey'), { recursive: true })
  await writeFile(marker, 'host file must survive')
  const paths = ['/save?room=A', '/repo-doc?room=A&owner=synthetic&repo=fixture&refPath=main/note.md', '/auth/config', '/auth/entry', '/auth/rooms', '/auth/account', '/auth/local/start', '/auth/local/consume', '/auth/provider/start', '/auth/login', '/auth/renew', '/auth/logout', ...['inspect', 'approve', 'deny', 'list', 'revoke', 'start', 'repair'].map(operation => '/agents/' + operation)]
  report.denied = []
  for (const path of paths) for (const method of ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']) {
   const init = { method, ...(method === 'GET' || method === 'HEAD' ? {} : { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: 'protected.tldr', file: JSON.stringify({ schema: {}, records: [{ id: 'attack' }] }) }) }) }
   const count = forwarded.length
   const current = await fetch(origin + path, init), previous = await fetch(oldOrigin + path, init)
   assert.equal(current.status, previous.status, method + ' ' + path)
   assert.equal(current.headers.get('content-type')?.split(';')[0], previous.headers.get('content-type')?.split(';')[0], path)
   assert.equal(forwarded.length, count, 'not forwarded: ' + method + ' ' + path)
   if (method === 'GET') assert.match(await current.text(), /<html/)
   report.denied.push({ path, method, status: current.status, forwarded: false })
  }
  assert.equal(await readFile(marker, 'utf8'), 'host file must survive')
 })
 await check('legacy share keeps image upload and retrieval, including filename extensions', async () => {
  const path = '/uploads/share-image.png?room=A'
  const upload = await fetch(origin + path, { method: 'PUT', headers: { 'Content-Type': 'image/png' }, body: 'synthetic image bytes' })
  assert.equal(upload.status, 200)
  const download = await fetch(origin + path)
  assert.equal(download.status, 200)
  assert.equal(await download.text(), 'synthetic image bytes')
  for (const method of ['POST', 'DELETE', 'PATCH']) assert.equal((await fetch(origin + path, { method })).status, 404)
 })
 await check('share document reads work and document writes stay closed', async () => {
  const before = await json(api + '/doc?room=A')
  assert.deepEqual(await json(origin + '/doc?room=A'), before)
  for (const method of ['POST', 'PATCH', 'PUT', 'DELETE']) {
   const response = await fetch(origin + '/doc?room=A', { method, headers: { 'Content-Type': 'application/json' }, body: '{}' })
   assert.equal(response.status, 404, method)
  }
  assert.deepEqual(await json(api + '/doc?room=A'), before)
 })
 await check('socket upgrades reject non-GET methods before reaching the API', async () => {
  const status = await new Promise((resolve, reject) => {
   const request = rawRequest(origin, { path: '/connect/A', method: 'POST', headers: { Connection: 'Upgrade', Upgrade: 'websocket', 'Sec-WebSocket-Key': 'dGhlIHNhbXBsZSBub25jZQ==', 'Sec-WebSocket-Version': '13' } }, response => { response.resume(); resolve(response.statusCode) })
   request.on('error', reject); request.end()
  })
  assert.equal(status, 404)
 })
 await check('raw dot paths cannot reach operator routes or document writes', async () => {
  for (const path of ['/uploads/../save?room=A', '/uploads/%2e%2e/save?room=A', '/uploads/%2f..%2fsave?room=A', '/uploads/../capabilities', '/auth/%2e%2e/doc?room=A', '/connect/../mcp']) {
   const status = await new Promise((resolve, reject) => {
    const request = rawRequest(origin, { path, method: 'PATCH', headers: { 'Content-Type': 'application/json' } }, response => { response.resume(); resolve(response.statusCode) })
    request.on('error', reject); request.end('{}')
   })
   assert.equal(status, 404, path)
  }
 })
 browser = await chromium.launch({ headless: true })
 const context = await browser.newContext({ viewport: { width: 1280, height: 820 } })
 await context.route('**/*', route => {
  const url = new URL(route.request().url())
  if (url.origin === origin) return route.continue()
  if (url.hostname === 'cdn.tldraw.com') return route.fulfill({ path: join(assets, url.pathname.replace(/^\/[^/]+\//, '')) })
  return route.abort()
 })
 page = await context.newPage()
 const errors = []; page.on('pageerror', error => errors.push(error.message))
 report.browserRequests = []; report.browserEvents = []
 page.on('framenavigated', frame => { if (frame === page.mainFrame()) report.browserEvents.push({ navigation: frame.url() }) })
 page.on('console', message => { if (message.text().includes('[vite]')) report.browserEvents.push({ console: message.text() }) })
 page.on('request', request => { const url = new URL(request.url()); if (['/doc', '/health', '/save'].includes(url.pathname)) report.browserRequests.push({ method: request.method(), url: request.url() }) })
 page.on('requestfailed', request => report.browserRequests.push({ failed: request.url(), error: request.failure() }))
 await check('legacy room menu lists A and B through the unmodified share proxy', async () => {
  await page.goto(origin + '/?room=A')
  await page.waitForLoadState('networkidle')
  await vite.waitForRequestsIdle()
  await page.waitForFunction(() => window.editor && document.querySelector('[data-testid="room-trigger"]')?.title.endsWith('Connected'))
  await page.getByTestId('room-trigger').click()
  assert.deepEqual(await page.locator('.journey-room-options button').allTextContents(), ['A', 'B'])
  assert.equal(await page.getByRole('button', { name: 'save', exact: true }).count(), 0)
  await page.screenshot({ path: join(scratch, 'share-rooms.png') })
 })
 await check('shared legacy client can confirm and switch from A to B', async () => {
  const stableSource = async () => {
  await page.evaluate(() => { window.editor.complete() })
  await page.waitForFunction(async () => {
   const ordered = value => Array.isArray(value) ? value.map(ordered) : value && typeof value === 'object' ? Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([key, item]) => [key, ordered(item)])) : value
   const response = await fetch('/doc?room=A')
   if (!response.ok) return false
   const remote = Object.fromEntries((await response.json()).snapshot.documents.map(({ state }) => [state.id, state]))
   return JSON.stringify(ordered(window.editor.store.getStoreSnapshot('document').store)) === JSON.stringify(ordered(remote))
  }, undefined, { polling: 100, timeout: 10000 })
  }
  await stableSource()
  await page.locator('.journey-room-options button').filter({ hasText: /^B$/ }).click()
  await page.waitForFunction(() => (new URL(location.href).searchParams.get('room') === 'B' && document.querySelector('[data-testid="room-trigger"]')?.title.endsWith('Connected')) || document.querySelector('[data-testid="room-trigger"]')?.title.includes('Edits not confirmed'))
  if (new URL(page.url()).searchParams.get('room') !== 'B') {
   report.visibleRetries = [{ from: 'A', to: 'B', reason: 'conservative source confirmation held the source editor' }]
   await stableSource()
   await page.getByTestId('room-trigger').click()
   await page.locator('.journey-room-options button').filter({ hasText: /^B$/ }).click()
   await page.waitForFunction(() => new URL(location.href).searchParams.get('room') === 'B' && document.querySelector('[data-testid="room-trigger"]')?.title.endsWith('Connected'))
  }
  assert.deepEqual(errors, [])
  assert.deepEqual((await json(origin + '/health')).rooms.sort(), ['A', 'B'])
 })
 report.result = 'PASS'
} catch (error) {
 report.result = 'FAIL'; report.error = error.stack; process.exitCode = 1
 report.failure = await page?.evaluate(async () => ({ url: location.href, status: document.querySelector('[data-testid=room-trigger]')?.title, local: window.editor?.store.getStoreSnapshot('document').store, remote: await (await fetch('/doc?room=A')).json() })).catch(() => null)
 await page?.screenshot({ path: join(scratch, 'failure.png') }).catch(() => {})
} finally {
 report.forwarded = forwarded
 for (const key of Object.keys(process.env)) if (/^(JOURNEY_|VITE_JOURNEY_)/.test(key)) delete process.env[key]
 Object.assign(process.env, journeyEnv)
 await browser?.close(); await vite?.close(); await old?.close()
 if (child && child.exitCode === null) await new Promise(resolve => { child.once('exit', resolve); child.kill('SIGTERM') })
 await mkdir(scratch, { recursive: true })
 await writeFile(join(scratch, 'result.json'), JSON.stringify(report, null, 2))
 await writeFile(join(scratch, 'server.log'), logs)
 console.log(JSON.stringify({ result: report.result, checks: report.checks.length, error: report.error, report: join(scratch, 'result.json') }))
}
