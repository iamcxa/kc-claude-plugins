import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { mkdtemp, writeFile } from 'node:fs/promises'
import { createServer } from 'node:net'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { parseArgs } from 'node:util'
import { chromium } from 'playwright'
import { createServer as createVite } from 'vite'

const { values } = parseArgs({ options: { root: { type: 'string' }, 'baseline-root': { type: 'string' }, output: { type: 'string' } } })
const root = resolve(values.root || new URL('..', import.meta.url).pathname)
const scratch = await mkdtemp(join(tmpdir(), 'native-account-http-'))
const report = { checks: [], failures: [] }
const port = () => new Promise(resolvePort => {
 const socket = createServer()
 socket.listen(0, '127.0.0.1', () => {
  const value = socket.address().port
  socket.close(() => [3757, 5878].includes(value) ? port().then(resolvePort) : resolvePort(value))
 })
})
const browser = await chromium.launch({ headless: true, args: ['--host-resolver-rules=MAP canvas.test 127.0.0.1', '--no-proxy-server'] })
async function check(packageRoot, label, mode) {
 const apiPort = await port(), uiPort = await port(), errors = [], logs = []
 const env = { ...process.env, JOURNEY_API_PORT: String(apiPort), JOURNEY_ALLOWED_HOSTS: 'canvas.test', JOURNEY_ROOMS_DIR: join(scratch, label, 'rooms'), JOURNEY_SAVE_DIR: join(scratch, label, 'save') }
 for (const key of ['JOURNEY_NATIVE_ACCOUNT', 'JOURNEY_HUMAN_CONFIG', 'JOURNEY_PRIVATE_DIR', 'JOURNEY_GRANTS_FILE', 'VITE_JOURNEY_HUMAN_ENTRY']) delete env[key]
 if (mode !== 'legacy') env.VITE_JOURNEY_HUMAN_ENTRY = 'true'
 if (mode === 'enabled') env.JOURNEY_NATIVE_ACCOUNT = 'true'
 const child = spawn(process.execPath, ['--import', 'tsx', 'server/canvas-server.ts'], { cwd: packageRoot, env, stdio: ['ignore', 'pipe', 'pipe'] })
 child.stdout.on('data', value => logs.push(String(value)))
 child.stderr.on('data', value => logs.push(String(value)))
 let vite, context
 try {
  for (let n = 0; ; n++) {
   try { if ((await fetch('http://127.0.0.1:' + apiPort + '/health')).ok) break } catch {}
   if (child.exitCode !== null || n === 199) throw new Error('server startup failed: ' + logs.join(''))
   await new Promise(resolveWait => setTimeout(resolveWait, 50))
  }
  for (const key of ['JOURNEY_NATIVE_ACCOUNT', 'JOURNEY_HUMAN_CONFIG', 'JOURNEY_PRIVATE_DIR', 'JOURNEY_GRANTS_FILE', 'VITE_JOURNEY_HUMAN_ENTRY']) delete process.env[key]
  Object.assign(process.env, { JOURNEY_API_PORT: String(apiPort), JOURNEY_ALLOWED_HOSTS: 'canvas.test', VITE_JOURNEY_HUMAN_ENTRY: mode === 'legacy' ? 'false' : 'true' })
  vite = await createVite({ cacheDir: join(scratch, label, 'vite'), configFile: join(packageRoot, 'vite.config.mts'), server: { hmr: false, host: '127.0.0.1', port: uiPort, strictPort: true } })
  await vite.listen()
  context = await browser.newContext({ viewport: { width: 1280, height: 800 } })
  await context.route('**/*', route => {
   const url = new URL(route.request().url())
   if (url.hostname === 'cdn.tldraw.com' && process.env.JOURNEY_TLDRAW_ASSETS) return route.fulfill({ path: join(process.env.JOURNEY_TLDRAW_ASSETS, url.pathname.replace(/^\/[^/]+\//, '')) })
   if (['canvas.test', '127.0.0.1', 'localhost'].includes(url.hostname)) return route.continue()
   return route.abort()
  })
  if (mode !== 'legacy') {
   await context.route('**/auth/config', route => route.fulfill({ json: { enabled: mode === 'enabled', nativeAccount: mode === 'enabled', mode: 'local', localReady: true } }))
   await context.route('**/auth/entry?**', route => route.fulfill({ status: 401, json: { category: 'human_sign_in_required' } }))
  }
  await context.addInitScript(() => {
   window.__nativeHoldReads = 0
   const getItem = Storage.prototype.getItem
   Storage.prototype.getItem = function (key) {
    if (key === 'journey-native-session-hold') window.__nativeHoldReads++
    return getItem.call(this, key)
   }
  })
  const page = await context.newPage()
  page.on('pageerror', error => errors.push(error.message))
  await page.goto('http://canvas.test:' + uiPort + '/?room=legacy')
  const ready = await page.waitForFunction(enabled => enabled ? document.querySelector('#human-entry-title')?.textContent === '驗證後進入畫布' : !!window.editor, mode === 'enabled', { timeout: 15000 }).then(() => true, () => false)
  if (ready && mode !== 'enabled') await page.getByRole('button', { name: 'save', exact: true }).waitFor()
  const state = await page.evaluate(() => ({ secureContext: isSecureContext, randomUUID: typeof crypto.randomUUID, getRandomValues: typeof crypto.getRandomValues, editor: !!window.editor, canvas: !!document.querySelector('.tl-container'), mainMenu: !!document.querySelector('[data-testid="main-menu.button"]'), roomTrigger: !!document.querySelector('[data-testid="room-trigger"]'), nativeHoldReads: window.__nativeHoldReads, entry: document.querySelector('#human-entry-title')?.textContent || null, text: document.body.innerText }))
  await page.screenshot({ path: join(scratch, label + '.png') })
  const result = { label, mode, ready, errors, ...state }
  report.checks.push(result)
  assert.equal(state.secureContext, false)
  assert.equal(state.randomUUID, 'undefined')
  assert.equal(state.getRandomValues, 'function')
  assert.deepEqual(errors, [])
  assert.equal(ready, true)
  if (mode === 'enabled') {
   assert.equal(state.entry, '驗證後進入畫布')
   assert.equal(state.nativeHoldReads, 1)
   assert.equal(await page.getByRole('button', { name: '開始本機帳號驗證', exact: true }).isEnabled(), true)
  } else {
   assert.equal(state.editor && state.canvas && state.mainMenu && state.roomTrigger, true)
   assert.equal(state.nativeHoldReads, 0)
  }
  return state
 } finally {
  await context?.close()
  await vite?.close()
  if (child.exitCode === null) {
   const exited = new Promise(resolveExit => child.once('exit', resolveExit))
   child.kill('SIGTERM'); await exited
  }
  await writeFile(join(scratch, label + '-server.log'), logs.join(''))
 }
}
try {
 let baseline
 if (values['baseline-root']) {
  baseline = await check(resolve(values['baseline-root']), 'main-flag-off', 'legacy')
  console.log('PASS main-flag-off')
 }
 for (const [label, mode] of [['candidate-flag-off', 'legacy'], ['candidate-disabled-config', 'disabled'], ['candidate-flag-on', 'enabled']]) {
  try {
   const state = await check(root, label, mode)
   if (baseline && mode !== 'enabled') assert.deepEqual(state, baseline)
   console.log('PASS ' + label)
  } catch (error) { report.failures.push({ label, error: String(error) }); console.error('FAIL ' + label + ': ' + error) }
 }
} finally {
 await browser.close()
 await writeFile(values.output || join(scratch, 'report.json'), JSON.stringify(report, null, 2))
 console.log('evidence=' + scratch)
}
assert.equal(report.failures.length, 0, JSON.stringify(report.failures))
