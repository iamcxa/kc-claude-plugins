import assert from 'node:assert/strict'
import { mkdtemp, mkdir, readFile, writeFile, stat, readdir } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import { execFileSync } from 'node:child_process'
import { createHash, randomBytes } from 'node:crypto'
import { NodeHost } from '../server/host/node'
import { prepareDoc } from '../server/host/core'
import { authenticate } from '../server/host/policy'
import privateClient from './private-cloudflare-client'
import { Miniflare } from 'miniflare'
import { build } from 'esbuild'
import { build as viteBuild } from 'vite'
import { buildAllPages } from '../lib/render.mjs'
import { fixtureModel } from '../lib/fixture.mjs'

const root = resolve(import.meta.dirname, '..')
const reportFile = process.argv[2]
if (!reportFile || !process.argv.includes('--synthetic')) throw new Error('usage: private-readiness-check.ts <local-report.json> --synthetic')
await mkdir(join(root, '.host-check'), { recursive: true })
const scratch = await mkdtemp(join(root, '.host-check/readiness-'))
const report: any = { runtime: process.version, checks: [], payloads: [], hosted: 'NOT RUN', retainedDeployment: 'NOT RUN' }
const check = async (name: string, fn: () => Promise<void>) => { await fn(); report.checks.push(name); console.log('PASS: ' + name) }
const secret = randomBytes(32).toString('base64url')
const operatorToken = randomBytes(32).toString('base64url')
const grant = (credentialId: string, revoked = false) => ({ credentialId, principalId: 'synthetic-operator', rooms: ['shared'], expiresAt: Date.now() + 3600_000, revoked, secretDigest: createHash('sha256').update(secret).digest('hex') })
const originalGrants = [grant('old'), grant('revoked', true)]
const freshGrants = [grant('fresh')]
const originalFile = join(scratch, 'original-policy.json'), freshFile = join(scratch, 'fresh-policy.json')
await writeFile(originalFile, JSON.stringify(originalGrants), { mode: 0o600 })
await writeFile(freshFile, JSON.stringify(freshGrants), { mode: 0o600 })
const origin = 'https://canvas.example.invalid'
const source = join(scratch, 'source'), restored = join(scratch, 'restored'), backup = join(scratch, 'backup.json')
const env = (dir: string, policy = originalFile) => ({ ...process.env, JOURNEY_PRIVATE_DIR: dir, JOURNEY_GRANTS_FILE: policy, JOURNEY_ORIGIN: origin })
const openNode = (dir: string, policy = originalFile) => { Object.assign(process.env, env(dir, policy)); return new NodeHost() }
const ops = (dir: string, policy: string, ...args: string[]) => execFileSync(process.execPath, ['--import', 'tsx', 'scripts/private-node-ops.ts', ...args], { cwd: root, env: env(dir, policy), stdio: 'pipe' })
const records = (doc: any) => doc.snapshot.documents.map((d: any) => d.state).sort((a: any, b: any) => a.id.localeCompare(b.id))
const put = buildAllPages(fixtureModel, 'shared')
const fixture = JSON.parse(await readFile(join(root, 'skills/kc-journey-map/references/example/book-pickup.tldr'), 'utf8'))
const fixtureRecords = Array.isArray(fixture.records) ? fixture.records : Object.values(fixture.records ?? {})
report.payloads = [
 { fixture: 'lib/fixture.mjs complete rendered pages', records: put.length, patchBytes: Buffer.byteLength(JSON.stringify({ put })) },
 { fixture: 'book-pickup.tldr', records: fixtureRecords.length, fileBytes: Buffer.byteLength(JSON.stringify(fixture)) },
]
let sourceDoc: any
let mf: Miniflare | undefined
try {
 await check('local operator client rejects browser headers and non-JSON requests before delegation', async () => {
  let delegated = 0
  const stub = { JOURNEY_OPERATOR_TOKEN: operatorToken, OPERATOR: { fetch: (request: Request) => { assert.equal(request.headers.has('authorization'), false); delegated++; return new Response('allowed') } } }
  for (const value of ['https://untrusted.example.invalid', 'null', '']) {
   assert.equal((await privateClient.fetch(new Request(origin, { method: 'POST', headers: { Origin: value, 'Content-Type': 'application/json' }, body: '{}' }), stub)).status, 403)
  }
  assert.equal((await privateClient.fetch(new Request(origin, { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: '{}' }), stub)).status, 415)
  assert.equal((await privateClient.fetch(new Request(origin, { method: 'OPTIONS' }), stub)).status, 404)
  for (const token of ['', 'wrong']) {
   assert.equal((await privateClient.fetch(new Request(origin, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token }, body: '{}' }), stub)).status, 401)
  }
  assert.equal((await privateClient.fetch(new Request(origin, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }), { ...stub, JOURNEY_OPERATOR_TOKEN: undefined })).status, 401)
  assert.equal(delegated, 0)
  assert.equal((await privateClient.fetch(new Request(origin, { method: 'POST', headers: { 'Content-Type': 'application/json; charset=utf-8', Authorization: 'Bearer ' + operatorToken }, body: '{}' }), stub)).status, 200)
  assert.equal(delegated, 1)
 })
 await check('stopped Node backup captures document/assets and persisted policy without sessions or credentials', async () => {
  const host = openNode(source)
  try {
   await host.document('shared', 'PATCH', prepareDoc('PATCH', { put }))
   await host.putAsset('shared', 'synthetic.txt', new TextEncoder().encode('synthetic asset'), 'text/plain')
   await host.meta.put('session:synthetic', { credentialId: 'old', expiresAt: Date.now() + 1000 })
   sourceDoc = await host.document('shared', 'GET', null)
  } finally { host.close() }
  assert.throws(() => ops(source, originalFile, 'backup', backup))
  ops(source, originalFile, 'backup', backup, '--stopped')
  const raw = await readFile(backup, 'utf8'), saved = JSON.parse(raw)
  assert.equal((await stat(backup)).mode & 0o777, 0o600)
  assert.deepEqual(saved.grants, originalGrants)
  assert.deepEqual(records(saved.rooms[0].document), records(sourceDoc))
  assert.equal(saved.rooms[0].assets[0].bytes.length, 15)
  assert.ok(!raw.includes(secret) && !raw.includes('session:synthetic'))
  assert.throws(() => ops(source, originalFile, 'backup', backup, '--stopped'))
 })
 await check('fresh restore quarantines every archived ID, including credentials revoked after the backup', async () => {
  ops(source, originalFile, 'revoke', 'old', '--stopped')
  assert.throws(() => ops(join(scratch, 'stale-policy-target'), originalFile, 'restore', backup, '--stopped'))
  ops(restored, freshFile, 'restore', backup, '--stopped')
  const host = openNode(restored, freshFile)
  try {
   assert.deepEqual(records(await host.document('shared', 'GET', null)), records(sourceDoc))
   assert.equal(new TextDecoder().decode((await host.getAsset('shared', 'synthetic.txt')).data), 'synthetic asset')
   for (const id of ['old', 'revoked']) await assert.rejects(authenticate(host.meta, new Headers({ Authorization: 'Bearer ' + id + '.' + secret })))
   assert.equal((await authenticate(host.meta, new Headers({ Authorization: 'Bearer fresh.' + secret }))).credentialId, 'fresh')
   assert.deepEqual(await host.meta.list('session:'), [])
  } finally { host.close() }
  assert.throws(() => ops(restored, freshFile, 'restore', backup, '--stopped'))
 })
 await check('before-switch failure preserves source; after-switch rollback saves divergent work before returning', async () => {
  const invalid = JSON.parse(await readFile(backup, 'utf8')); invalid.rooms[0].document.roomId = 'wrong'
  const invalidFile = join(scratch, 'invalid.json'); await writeFile(invalidFile, JSON.stringify(invalid))
  assert.throws(() => ops(join(scratch, 'failed-target'), freshFile, 'restore', invalidFile, '--stopped'))
  let host = openNode(source)
  try { assert.deepEqual(records(await host.document('shared', 'GET', null)), records(sourceDoc)) } finally { host.close() }
  host = openNode(restored, freshFile)
  try { const doc = await host.document('shared', 'GET', null); const page = records(doc).find((r: any) => r.typeName === 'page'); await host.document('shared', 'PATCH', prepareDoc('PATCH', { put: [{ ...page, name: 'Post-switch synthetic edit' }] })) } finally { host.close() }
  const divergent = join(scratch, 'failed-candidate-backup.json')
  ops(restored, freshFile, 'backup', divergent, '--stopped')
  const captured = JSON.parse(await readFile(divergent, 'utf8'))
  assert.ok(records(captured.rooms[0].document).some((r: any) => r.name === 'Post-switch synthetic edit'))
  host = openNode(source)
  try { assert.deepEqual(records(await host.document('shared', 'GET', null)), records(sourceDoc)); await assert.rejects(authenticate(host.meta, new Headers({ Authorization: 'Bearer old.' + secret }))) } finally { host.close() }
 })
 const bundles: Record<string, string> = {}
 for (const [name, file] of Object.entries({ product: 'server/host/cloudflare.ts', operator: 'scripts/private-cloudflare-ops.ts', client: 'scripts/private-cloudflare-client.ts' })) {
  const built = await build({ entryPoints: [join(root, file)], bundle: true, format: 'esm', platform: 'browser', conditions: ['workerd', 'worker', 'browser'], external: ['cloudflare:workers'], write: false, logLevel: 'silent' })
  bundles[name] = built.outputFiles[0].text
 }
 const startCloud = async (policy: any[], name: string) => {
  mf = new Miniflare({ port: 0, host: '127.0.0.1', durableObjectsPersist: join(scratch, name), workers: [
   { name: 'client', script: bundles.client, modules: true, compatibilityDate: '2026-07-01', bindings: { JOURNEY_OPERATOR_TOKEN: operatorToken }, serviceBindings: { OPERATOR: 'operator' } },
   { name: 'product', script: bundles.product, modules: true, compatibilityDate: '2026-07-01', compatibilityFlags: ['nodejs_compat'], bindings: { JOURNEY_ORIGIN: origin, JOURNEY_GRANTS: JSON.stringify(policy) }, durableObjects: { ROOMS: { className: 'JourneyRoom', useSQLite: true }, REGISTRY: { className: 'JourneyRegistry', useSQLite: true } } },
   { name: 'operator', script: bundles.operator, modules: true, compatibilityDate: '2026-07-01', compatibilityFlags: ['nodejs_compat'], bindings: { JOURNEY_ORIGIN: origin, JOURNEY_GRANTS: JSON.stringify(policy), JOURNEY_OPERATOR_ROOMS: '["shared"]' }, durableObjects: { ROOMS: { className: 'JourneyRoom', scriptName: 'product', useSQLite: true }, REGISTRY: { className: 'JourneyRegistry', scriptName: 'product', useSQLite: true } } },
  ] })
  await mf.ready
 }
 const app = async (path: string, id = 'old', method = 'GET', body?: any) => {
  const worker = await mf!.getWorker('product')
  return worker.fetch(origin + path, { method, headers: { Authorization: 'Bearer ' + id + '.' + secret, 'Content-Type': 'application/json' }, body: body === undefined ? undefined : JSON.stringify(body) })
 }
 const operator = (body: any) => mf!.dispatchFetch(origin + '/', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + operatorToken }, body: JSON.stringify(body) })
 let cloudBackup: any, cloudDoc: any
 await check('private service-binding chain delegates bounded backup/revoke and exposes absent-asset capabilities', async () => {
  await startCloud(originalGrants, 'cloud-source')
  for (const originHeader of ['https://untrusted.example.invalid', 'null']) {
   const response = await mf!.dispatchFetch(origin + '/', { method: 'POST', headers: { Origin: originHeader, 'Content-Type': 'application/json' }, body: JSON.stringify({ op: 'revoke', credentialId: 'old', writersStopped: true }) })
   assert.equal(response.status, 403)
  }
  assert.equal((await mf!.dispatchFetch(origin + '/', { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: '{}' })).status, 415)
  assert.equal((await mf!.dispatchFetch(origin + '/', { method: 'OPTIONS' })).status, 404)
  assert.equal((await app('/doc?room=shared', 'old', 'PATCH', { put })).status, 200)
  cloudDoc = await (await app('/doc?room=shared')).json()
  assert.deepEqual(await (await app('/capabilities?room=shared')).json(), { save: false, repoDoc: false, assets: false })
  assert.equal((await app('/uploads/synthetic?room=shared', 'old', 'PUT', {})).status, 501)
  assert.equal((await app('/uploads/synthetic?room=shared')).status, 404)
  assert.equal((await operator({ op: 'backup' })).status, 400)
  assert.equal((await operator({ op: 'sql', writersStopped: true })).status, 400)
  const response = await operator({ op: 'backup', writersStopped: true }); assert.equal(response.status, 200)
  cloudBackup = await response.json()
  assert.deepEqual(records(cloudBackup.rooms[0].document), records(cloudDoc))
  const revoked = await operator({ op: 'revoke', credentialId: 'old', writersStopped: true }); assert.equal(revoked.status, 200)
  assert.equal((await app('/doc?room=shared')).status, 401)
  assert.equal((await operator({ op: 'restore', archive: cloudBackup, writersStopped: true })).status, 400)
  await mf!.dispose(); mf = undefined
 })
 await check('fresh cloud namespace restore preserves records and denies all archived credentials through the actual adapter', async () => {
  await startCloud(freshGrants, 'cloud-restored')
  const wrong = structuredClone(cloudBackup); wrong.rooms[0].room = 'outside'
  assert.equal((await operator({ op: 'restore', archive: wrong, writersStopped: true })).status, 400)
  const response = await operator({ op: 'restore', archive: cloudBackup, writersStopped: true }); assert.equal(response.status, 200, await response.clone().text())
  assert.deepEqual(records(await (await app('/doc?room=shared', 'fresh')).json()), records(cloudDoc))
  for (const id of ['old', 'revoked']) assert.equal((await app('/doc?room=shared', id)).status, 401)
  assert.equal((await operator({ op: 'restore', archive: cloudBackup, writersStopped: true })).status, 400)
  await mf!.dispose(); mf = undefined
 })
 await check('normal production build accepts the existing license environment input without changing enforcement', async () => {
  const marker = 'INVALID-SYNTHETIC-LICENSE-INPUT'
  process.env.VITE_TLDRAW_LICENSE_KEY = marker
  const outDir = join(scratch, 'production-build')
  await viteBuild({ configFile: join(root, 'vite.config.mts'), mode: 'production', build: { outDir, emptyOutDir: false }, logLevel: 'silent' })
  delete process.env.VITE_TLDRAW_LICENSE_KEY
  const js = (await readdir(join(outDir, 'assets'))).filter(name => name.endsWith('.js'))
  assert.ok((await Promise.all(js.map(name => readFile(join(outDir, 'assets', name), 'utf8')))).some(code => code.includes(marker)))
  report.license = 'build input proven with invalid marker; valid license and licensed rendering NOT SHOWN'
 })
 report.result = 'PASS'
} catch (error) {
 report.result = 'FAIL'; report.error = (error as Error).message; throw error
} finally {
 if (mf) await mf.dispose()
 await writeFile(reportFile, JSON.stringify(report, null, 2) + '\n', { mode: 0o600 })
}
