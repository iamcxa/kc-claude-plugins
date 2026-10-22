import assert from 'node:assert/strict'
import { test } from 'node:test'
import { mkdtemp, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { NodeHost } from '../server/host/node'
import { CloudflareHost } from '../server/host/cloudflare'
import { handle, type Host } from '../server/host/transport'
import { digest, type Metadata } from '../server/host/policy'
import type { HumanConfig, HumanSession } from '../server/host/human-store'

const origin = 'http://127.0.0.1:3737', now = Date.now()
const config: HumanConfig = { version: 1, backendId: 'catalog-synthetic', origin, mode: 'cloudflare', issuer: 'https://synthetic.cloudflareaccess.com', audience: 'synthetic', members: [{ id: 'person', issuer: 'https://synthetic.cloudflareaccess.com', subject: 'person', label: 'Synthetic', role: 'member', rooms: ['A', 'B', 'qnow-day2', 'future', 'missing'].map(id => ({ id, expiresAt: now + 3600_000 })) }] }
const session: HumanSession = { actorType: 'human', backendId: config.backendId, memberId: 'person', generation: 1, expiresAt: now + 900_000, verifiedHumanSignInAt: now, humanRevalidateBy: now + 604800_000, csrfDigest: 'synthetic', revoked: false }
const cookie = 'synthetic-human'
const url = (path = '/auth/rooms') => origin + path + (path.includes('?') ? '&' : '?') + new URLSearchParams({ _human: 'person', _backend: config.backendId, _humanAt: String(now), _humanRoom: 'A' })
const request = (host: Host, path = url()) => handle(host, new Request(path, { headers: { Cookie: 'journey_human=' + cookie } }))
async function seed(meta: Metadata) {
 await meta.put('human-config:v1', config)
 await meta.put('member:person', { ...config.members[0], enabled: true, generation: 1 })
 await meta.put('browser-session:' + await digest(cookie), session)
 for (const id of ['A', 'B', 'qnow-day2', 'future', 'missing']) await meta.put('member-room:person:' + id, { memberId: 'person', roomId: id, expiresAt: now + 3600_000, revoked: false, generation: 1 })
 for (const id of ['A', 'B', 'qnow-day2', 'future', 'denied']) await meta.put('room:' + id, { createdAt: now, displayName: id === 'qnow-day2' ? 'Day2' : id })
}
async function assertCatalog(host: Host) {
 let healthCalls = 0, documentCalls = 0
 host.health = async () => { healthCalls++; throw new Error('catalog must not sample health') }
 host.document = async () => { documentCalls++; throw new Error('catalog must not read documents') }
 const response = await request(host)
 assert.equal(response.status, 200, await response.clone().text())
 assert.equal(response.headers.get('cache-control'), 'private, no-store')
 assert.deepEqual(await response.json(), { backendId: config.backendId, memberId: 'person', rooms: [{ roomId: 'A', displayName: 'A' }, { roomId: 'B', displayName: 'B' }, { roomId: 'future', displayName: 'future' }, { roomId: 'qnow-day2', displayName: 'Day2' }] })
 assert.equal(healthCalls, 0); assert.equal(documentCalls, 0)
 const stale = url('/doc?room=missing')
 assert.equal((await request(host, stale.replace('_humanRoom=A', '_humanRoom=missing'))).status, 404)
 assert.equal(await host.meta.get('room:missing'), null)
 const originalList = host.meta.list.bind(host.meta)
 host.meta.list = async prefix => { if (prefix === 'room:') throw new Error('registry down'); return originalList(prefix) }
 assert.equal((await request(host)).status, 503)
 host.meta.list = originalList
 const member = await host.meta.get<any>('member:person')
 await host.meta.put('member:person', { ...member, enabled: false })
 assert.equal((await request(host)).status, 403)
 await host.meta.put('member:person', member)
 for (const [key, value] of [['_human', 'other'], ['_backend', 'other'], ['_humanAt', String(now - 1)]]) {
  const changed = new URL(url()); changed.searchParams.set(key, value)
  assert.equal((await request(host, changed.href)).status, 403)
 }
 await host.meta.put('browser-session:' + await digest(cookie), { ...session, expiresAt: 1 })
 assert.equal((await request(host)).status, 401)
}

test('Node SQLite catalog intersects registered metadata and current grants without opening a document', async () => {
 const dir = await mkdtemp(join(tmpdir(), 'catalog-node-'))
 const grants = join(dir, 'grants.json'), human = join(dir, 'human.json'), data = join(dir, 'data')
 await writeFile(grants, JSON.stringify([{ credentialId: 'legacy', secretDigest: 'f'.repeat(64), principalId: 'seed', rooms: ['A'], expiresAt: now + 3600_000, revoked: false }]))
 await writeFile(human, JSON.stringify(config))
 const before = { ...process.env }
 Object.assign(process.env, { JOURNEY_PRIVATE_DIR: data, JOURNEY_GRANTS_FILE: grants, JOURNEY_HUMAN_CONFIG: human, JOURNEY_ORIGIN: origin })
 const host = new NodeHost()
 try { await seed(host.meta); await assertCatalog(host); assert.equal(host.rooms.size, 0) }
 finally { host.close(); process.env = before }
})

test('Cloudflare catalog never constructs a document Durable Object stub or samples activity', async () => {
 const metadata = new Map<string, unknown>()
 let roomStubs = 0, mutations = 0
 const registry = { fetch: async (request: Request) => {
  const path = new URL(request.url).pathname, body = await request.json() as any
  if (path === '/human' && body.operation === 'record-denial') return Response.json({ recorded: true })
  if (path === '/get') return Response.json(metadata.get(body.key) ?? null)
  if (path === '/put') { mutations++; metadata.set(body.key, body.value); return Response.json({ ok: true }) }
  if (path === '/list') return Response.json([...metadata].filter(([key]) => key.startsWith(body.prefix)).sort(([a], [b]) => a.localeCompare(b)).map(([key, value]) => ({ key, value })))
  throw new Error('unexpected registry operation')
 } }
 const host = new CloudflareHost({ JOURNEY_ORIGIN: origin, JOURNEY_GRANTS: JSON.stringify([{ credentialId: 'seed', secretDigest: 'f'.repeat(64), principalId: 'seed', rooms: ['A'], expiresAt: now + 3600_000, revoked: false }]), JOURNEY_HUMAN_CONFIG: JSON.stringify(config), REGISTRY: { idFromName: (id: string) => id, get: () => registry }, ROOMS: { idFromName: () => { roomStubs++; throw new Error('document wake') }, get: () => { throw new Error('document stub') } } })
 await seed(host.meta)
 const before = mutations
 const response = await request(host)
 assert.equal(response.status, 200)
 assert.equal(mutations, before); assert.equal(roomStubs, 0)
 await assertCatalog(host)
 assert.equal(roomStubs, 0)
})
