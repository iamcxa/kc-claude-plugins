import assert from 'node:assert/strict'
import { spawn, execFileSync } from 'node:child_process'
import { mkdtemp, mkdir, writeFile } from 'node:fs/promises'
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
const apiPort = await freePort(), uiPort = await freePort()
const api = `http://127.0.0.1:${apiPort}`, origin = `http://127.0.0.1:${uiPort}`
const env = Object.fromEntries(Object.entries(process.env).filter(([key]) => !/^(JOURNEY_|VITE_JOURNEY_)/.test(key)))
const report = { candidate: execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(), checks: [], api, origin, scratch }
let child, vite, browser, page, logs = ''
const check = async (name, run) => { await run(); report.checks.push({ name, status: 'passed' }); console.log('PASS ' + name) }
const json = async url => { const response = await fetch(url); assert.equal(response.status, 200); assert.match(response.headers.get('content-type'), /application\/json/); return response.json() }
try {
 child = spawn(process.execPath, ['--import', 'tsx', 'server/canvas-server.ts'], { cwd: root, env: { ...env, JOURNEY_API_PORT: String(apiPort), JOURNEY_ROOMS_DIR: join(scratch, 'rooms'), JOURNEY_SAVE_DIR: join(scratch, 'saved') }, stdio: ['ignore', 'pipe', 'pipe'] })
 child.stdout.on('data', value => { logs += value }); child.stderr.on('data', value => { logs += value })
 let ready = false
 for (let i = 0; i < 150; i++) {
  if (child.exitCode !== null) throw new Error(logs)
  try { if ((await fetch(api + '/health')).ok) { ready = true; break } } catch {}
  await new Promise(resolve => setTimeout(resolve, 100))
 }
 assert.ok(ready, 'API startup timed out')
 for (const room of ['A', 'B']) await json(api + '/doc?room=' + room)
 process.env.JOURNEY_API_PORT = String(apiPort)
 vite = await viteServer({ configFile: join(root, 'vite.share.config.mts'), cacheDir: join(scratch, 'vite-cache'), define: { 'import.meta.env.VITE_JOURNEY_HUMAN_ENTRY': JSON.stringify('false') }, server: { port: uiPort, host: '127.0.0.1', strictPort: true } })
 await vite.listen()
 await check('share /health returns JSON containing both legacy rooms', async () => {
  assert.deepEqual((await json(origin + '/health')).rooms.sort(), ['A', 'B'])
 })
 await check('disabled human entry still returns the API config through share', async () => {
  assert.deepEqual(await json(origin + '/auth/config'), { enabled: false })
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
 await check('raw dot paths cannot reach operator routes or document writes', async () => {
  for (const path of ['/uploads/../capabilities', '/auth/%2e%2e/doc?room=A', '/connect/../mcp']) {
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
 await check('legacy room menu lists A and B through the unmodified share proxy', async () => {
  await page.goto(origin + '/?room=A')
  await page.waitForFunction(() => window.editor && document.querySelector('[data-testid="room-trigger"]')?.title.endsWith('Connected'))
  await page.getByTestId('room-trigger').click()
  assert.deepEqual(await page.locator('.journey-room-options button').allTextContents(), ['A', 'B'])
  await page.screenshot({ path: join(scratch, 'share-rooms.png') })
 })
 await check('shared legacy client can confirm and switch from A to B', async () => {
  await page.waitForFunction(async () => {
   const ordered = value => Array.isArray(value) ? value.map(ordered) : value && typeof value === 'object' ? Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([key, item]) => [key, ordered(item)])) : value
   const response = await fetch('/doc?room=A')
   if (!response.ok) return false
   const remote = Object.fromEntries((await response.json()).snapshot.documents.map(({ state }) => [state.id, state]))
   return JSON.stringify(ordered(window.editor.store.getStoreSnapshot('document').store)) === JSON.stringify(ordered(remote))
  }, undefined, { polling: 100, timeout: 10000 })
  await page.locator('.journey-room-options button').filter({ hasText: /^B$/ }).click()
  await page.waitForFunction(() => new URL(location.href).searchParams.get('room') === 'B' && document.querySelector('[data-testid="room-trigger"]')?.title.endsWith('Connected'))
  assert.deepEqual(errors, [])
  assert.deepEqual((await json(origin + '/health')).rooms.sort(), ['A', 'B'])
 })
 report.result = 'PASS'
} catch (error) {
 report.result = 'FAIL'; report.error = error.stack; process.exitCode = 1
 await page?.screenshot({ path: join(scratch, 'failure.png') }).catch(() => {})
} finally {
 await browser?.close(); await vite?.close()
 if (child && child.exitCode === null) await new Promise(resolve => { child.once('exit', resolve); child.kill('SIGTERM') })
 await mkdir(scratch, { recursive: true })
 await writeFile(join(scratch, 'result.json'), JSON.stringify(report, null, 2))
 await writeFile(join(scratch, 'server.log'), logs)
 console.log(JSON.stringify(report))
}
