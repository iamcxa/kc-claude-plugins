import assert from 'node:assert/strict'
import fs from 'node:fs'
import { createHash } from 'node:crypto'
import { syncBuiltinESMExports } from 'node:module'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

const scratch = fs.mkdtempSync(join(tmpdir(), 'journey-private-permissions-'))
const originalMask = process.umask()
const originalLstat = fs.lstatSync, originalGeteuid = process.geteuid
const grantFile = join(scratch, 'grants.json')
fs.writeFileSync(grantFile, JSON.stringify([{ credentialId: 'synthetic', principalId: 'synthetic', secretDigest: 'a'.repeat(64),
 rooms: ['A'], expiresAt: Date.now() + 3600000, revoked: false }]), { mode: 0o600 })
Object.assign(process.env, { JOURNEY_GRANTS_FILE: grantFile, JOURNEY_ORIGIN: 'https://synthetic.example.invalid',
 JOURNEY_ASSETS_DIR: join(scratch, 'legacy-assets'), JOURNEY_ROOM_REPOS: '{}' })
const { NodeHost } = await import('../server/host/node.ts')
const { prepareDoc } = await import('../server/host/core.ts')
const results = [], observations = {}
const mode = path => fs.statSync(path).mode & 0o777
const rootFor = name => join(scratch, name)
const snapshot = path => {
 if (!fs.existsSync(path) && !fs.lstatSync(path, { throwIfNoEntry: false })) return null
 const st = fs.lstatSync(path, { bigint: true })
 const result = { mode: String(st.mode), uid: String(st.uid), mtime: String(st.mtimeNs), ctime: String(st.ctimeNs) }
 if (st.isSymbolicLink()) result.link = fs.readlinkSync(path)
 else if (st.isDirectory()) result.entries = Object.fromEntries(fs.readdirSync(path).sort().map(name => [name, snapshot(join(path, name))]))
 else result.sha256 = createHash('sha256').update(fs.readFileSync(path)).digest('hex')
 return result
}
async function withHost(root, action) {
 process.env.JOURNEY_PRIVATE_DIR = root
 const host = new NodeHost()
 try { return await action(host) } finally { host.close() }
}
async function test(name, action) {
 try { await action(); results.push({ name, status: 'PASS' }) }
 catch (error) { results.push({ name, status: 'FAIL', error: error.message }) }
}
async function refuses(root, pattern, targets = [root]) {
 const before = targets.map(snapshot)
 let error
 try { await withHost(root, () => {}) } catch (caught) { error = caught }
 assert.deepEqual(targets.map(snapshot), before, 'refusal must not change fixture bytes, modes, entries or write times')
 assert.ok(error, 'private host must refuse this root')
 assert.match(error.message, pattern)
}
async function writeRead(host) {
 const page = { id: 'page:synthetic', typeName: 'page', name: 'Private storage proof', index: 'a1', meta: {} }
 await host.document('A', 'PATCH', prepareDoc('PATCH', { put: [page] }))
 const doc = await host.document('A', 'GET', null)
 assert.deepEqual(doc.snapshot.documents.find(item => item.state.id === page.id)?.state, page)
 await host.putAsset('A', 'synthetic.txt', new TextEncoder().encode('synthetic private bytes'), 'text/plain')
 const asset = await host.getAsset('A', 'synthetic.txt')
 assert.equal(new TextDecoder().decode(asset.data), 'synthetic private bytes')
 assert.equal(asset.contentType, 'text/plain')
 return doc
}
try {
 for (const mask of [0o022, 0o000]) await test(`new-root-umask-${mask.toString(8).padStart(3, '0')}`, async () => {
  process.umask(mask)
  const root = rootFor(`new-${mask}`)
  await withHost(root, async host => {
   await writeRead(host)
   observations[`umask-${mask.toString(8)}`] = { root: mode(root).toString(8), metadata: mode(join(root, 'metadata.sqlite')).toString(8), room: mode(join(root, 'rooms/A.db')).toString(8) }
   assert.equal(mode(root), 0o700, 'new private root must be owner-only')
   assert.equal(process.umask(), mask, 'NodeHost must not alter the process umask')
  })
 })
 process.umask(0o022)
 await test('existing-empty-0755-refused', async () => {
  const root = rootFor('empty-wide'); fs.mkdirSync(root, { mode: 0o755 })
  await refuses(root, /0700/)
 })
 await test('marked-0755-refused-before-write', async () => {
  const root = rootFor('marked-wide'); fs.mkdirSync(root, { mode: 0o700 })
  await withHost(root, writeRead)
  fs.chmodSync(root, 0o755)
  await refuses(root, /0700/)
 })
 await test('owned-0700-reopen-preserves-data', async () => {
  const root = rootFor('reopen'); fs.mkdirSync(root, { mode: 0o700 })
  const doc = await withHost(root, writeRead)
  const bytesBefore = snapshot(root)
  await withHost(root, async host => {
   assert.deepEqual(await host.document('A', 'GET', null), doc)
   assert.equal(new TextDecoder().decode((await host.getAsset('A', 'synthetic.txt')).data), 'synthetic private bytes')
  })
  assert.deepEqual(snapshot(root), bytesBefore)
 })
 await test('leaf-symlink-refused-without-target-change', async () => {
  const target = rootFor('link-target'), root = rootFor('linked-root')
  fs.mkdirSync(target, { mode: 0o700 }); fs.symlinkSync(target, root)
  await refuses(root, /directory.*symlink|symlink.*directory/, [root, target])
 })
 await test('non-directory-refused-without-change', async () => {
  const root = rootFor('file-root'); fs.writeFileSync(root, 'synthetic sentinel', { mode: 0o600 })
  await refuses(root, /directory/)
 })
 await test('nonempty-unmarked-0700-still-refused', async () => {
  const root = rootFor('unmarked'); fs.mkdirSync(root, { mode: 0o700 }); fs.writeFileSync(join(root, 'sentinel'), 'keep')
  await refuses(root, /start empty/)
 })
 await test('foreign-owner-metadata-fault-refused', async () => {
  const root = rootFor('foreign-metadata'); fs.mkdirSync(root, { mode: 0o700 })
  const before = snapshot(root)
  fs.lstatSync = (...args) => {
   const stat = originalLstat(...args)
   if (args[0] === root && !args[1]?.bigint) stat.uid = originalGeteuid() + 1
   return stat
  }
  syncBuiltinESMExports()
  try { await refuses(root, /own.*user|user.*own/) }
  finally { fs.lstatSync = originalLstat; syncBuiltinESMExports() }
  assert.deepEqual(snapshot(root), before)
 })
 await test('missing-effective-uid-refused-before-create', async () => {
  const root = rootFor('no-posix')
  process.geteuid = undefined
  try { await refuses(root, /POSIX/) } finally { process.geteuid = originalGeteuid }
 })
 await test('legacy-layout-and-roundtrip-unchanged', async () => {
  delete process.env.JOURNEY_PRIVATE_DIR
  process.env.JOURNEY_ROOMS_DIR = rootFor('legacy-rooms')
  const host = new NodeHost()
  try {
   assert.equal(host.private, false)
   await writeRead(host)
   assert.equal(mode(host.roomsDir), 0o755)
   assert.ok(fs.existsSync(join(host.roomsDir, '.metadata/metadata.sqlite')))
   assert.ok(fs.existsSync(join(scratch, 'legacy-assets/synthetic.txt')))
   assert.equal(fs.existsSync(join(host.roomsDir, '.journey-private-v1')), false)
  } finally { host.close() }
 })
} finally {
 fs.lstatSync = originalLstat; syncBuiltinESMExports(); process.geteuid = originalGeteuid; process.umask(originalMask)
 fs.rmSync(scratch, { recursive: true, force: true })
}
console.log(JSON.stringify({ ok: results.every(r => r.status === 'PASS'), node: process.version, platform: process.platform,
 observations, results, cleanup: !fs.existsSync(scratch), limits: 'Foreign ownership and missing POSIX primitive use labelled metadata/process faults; no other-user or ACL/ancestor-race proof.' }, null, 2))
process.exitCode = results.some(r => r.status === 'FAIL') ? 1 : 0
