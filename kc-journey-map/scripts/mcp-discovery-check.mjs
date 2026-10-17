import assert from 'node:assert/strict'
import { randomBytes } from 'node:crypto'
import { mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { NodeHost } from '../server/host/node.ts'
import { digest } from '../server/host/policy.ts'
import { handle } from '../server/host/transport.ts'
import { note } from '../lib/records.mjs'

// Exercise advertised MCP metadata and real SQLite operations without a listener or native client.
const scratch = await mkdtemp(join(tmpdir(), 'journey-discovery-'))
const savedEnv = Object.fromEntries(['JOURNEY_PRIVATE_DIR', 'JOURNEY_GRANTS_FILE', 'JOURNEY_ORIGIN'].map(key => [key, process.env[key]]))
const secret = randomBytes(32).toString('base64url')
let host
let report
try {
 const grantsFile = join(scratch, 'grants.json')
 await writeFile(grantsFile, JSON.stringify([{ credentialId: 'discovery', secretDigest: await digest(secret),
  principalId: 'discovery', rooms: ['A'], expiresAt: Date.now() + 60_000, revoked: false }]), { mode: 0o600 })
 Object.assign(process.env, { JOURNEY_PRIVATE_DIR: join(scratch, 'storage'), JOURNEY_GRANTS_FILE: grantsFile, JOURNEY_ORIGIN: 'https://localhost' })
 host = new NodeHost()
 const request = async (path, body) => {
  const response = await handle(host, new Request('https://localhost' + path, {
   method: body === undefined ? 'GET' : 'POST', headers: { Authorization: 'Bearer discovery.' + secret, 'Content-Type': 'application/json' },
   ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  }))
  assert.equal(response.status, 200)
  return response.json()
 }
 const rpc = async (method, params) => {
  const result = await request('/mcp', { jsonrpc: '2.0', id: 1, method, params })
  assert.equal(result.error, undefined)
  return result.result
 }
 const call = async (name, args) => (await rpc('tools/call', { name, arguments: { room: 'A', ...args } })).structuredContent
 const inventory = await rpc('tools/list')
 assert.deepEqual(inventory.tools.map(tool => tool.name), ['get_doc', 'patch_doc', 'put_doc', 'health'])
 const patch = inventory.tools.find(tool => tool.name === 'patch_doc')
 const fields = patch.inputSchema.properties.body.properties
 assert.ok(fields?.put, 'tools/list must advertise body.put, not an opaque body')
 assert.equal(fields.put.type, 'array'); assert.equal(fields.put.items.type, 'object')
 assert.equal(fields.remove.type, 'array'); assert.equal(fields.remove.items.type, 'string')
 assert.match(fields.put.description, /complete/i)
 for (const term of ['body.put', 'body.remove', 'removed', 'get_doc']) assert.ok(patch.description.includes(term), term)
 const putKey = Object.keys(fields).find(key => fields[key].items?.type === 'object')
 const removeKey = Object.keys(fields).find(key => fields[key].items?.type === 'string')
 const page = { id: 'page:discovery', typeName: 'page', name: 'Discovery', index: 'a1', meta: {} }
 const shape = note({ id: 'shape:discovery', text: 'Discovered envelope', x: 0, y: 0, parentId: page.id })
 const ack = await call('patch_doc', { body: { [putKey]: [page, shape], [removeKey]: [] } })
 assert.equal(ack.put, 2); assert.equal(ack.removed, 0)
 const read = await call('get_doc')
 assert.deepEqual(read.snapshot.documents.find(doc => doc.state.id === shape.id).state, shape)
 assert.deepEqual(await request('/doc?room=A'), read)
 // Legacy omissions/unknown keys remain accepted no-ops; this repair adds no alias or rejection.
 for (const args of [undefined, { body: {} }, { body: { puts: [shape] } }]) {
  const noop = await call('patch_doc', args)
  assert.equal(noop.put, 0); assert.equal(noop.removed, 0)
  assert.deepEqual(await call('get_doc'), read)
 }
 const removed = await call('patch_doc', { body: { [removeKey]: [shape.id, page.id] } })
 assert.equal(removed.put, 0); assert.equal(removed.removed, 2)
 const final = await request('/doc?room=A')
 assert.ok(final.snapshot.documents.every(doc => ![shape.id, page.id].includes(doc.state.id)))
 report = { result: 'PASS', layer: 'in-process MCP handler with real Node SQLite storage; synthetic client',
  checks: ['advertised envelope', 'complete-record write/readback', 'HTTP readback', 'legacy no-op compatibility', 'remove/readback'], patchTool: patch }
} finally {
 // Drain the SDK's deferred SQLite housekeeping before this short-lived check closes its database.
 for (const { room } of host?.rooms.values() ?? []) room.storage.pruneTombstones.flush()
 host?.close()
 for (const [key, value] of Object.entries(savedEnv)) if (value === undefined) delete process.env[key]; else process.env[key] = value
 await rm(scratch, { recursive: true, force: true })
}
console.log(JSON.stringify(report, null, 2))
