import assert from 'node:assert/strict'
import { mkdtemp, rm } from 'node:fs/promises'
import { createServer } from 'node:http'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { test } from 'node:test'
import { tsImport } from 'tsx/esm/api'
import { createServer as createViteServer } from 'vite'

const root = new URL('..', import.meta.url).pathname
const { agentGuide } = await tsImport(join(root, 'server/agent-guide.ts'), import.meta.url)

test('guide includes actionable tools and safety without disclosing unrelated configuration', () => {
 const text = agentGuide({ JOURNEY_API_TOKEN: 'secret-token', JOURNEY_ROOM_REPOS: 'secret-room', JOURNEY_AGENT_SSH_HOST: 'vm.example.invalid', JOURNEY_API_PORT: '6590' })
 assert.ok(text.split('\n').length < 120)
 for (const value of ['ssh -N -L 5858:127.0.0.1:6590 vm.example.invalid', 'http://127.0.0.1:5858/mcp', 'get_doc, patch_doc, put_doc, health', 'source of truth', 'journey-render.mjs', 'journey-read.mjs', 'journey-tldr.mjs export', 'never delete a room database', 'cannot recover unexported manual edits']) assert.ok(text.includes(value), value)
 assert.doesNotMatch(text, /secret-token|secret-room/)
 const examples = text.split('\n').filter(line => line.startsWith('curl') && line.includes('/mcp'))
 const requests = examples.map(line => JSON.parse(line.split(" -d '")[1].slice(0, -1)))
 assert.deepEqual(requests.map(request => request.params.name), ['get_doc', 'patch_doc'])
 assert.deepEqual(requests[1].params.arguments.body, { put: [], remove: [] })
 for (const host of ['user@example.invalid', '-oProxyCommand=anything', 'vm\nsecret', "vm'; touch /tmp/anything"]) {
  assert.doesNotMatch(agentGuide({ JOURNEY_AGENT_SSH_HOST: host }), /## SSH tunnel|ssh -N/)
 }
 for (const flag of [undefined, 'false', '1', 'TRUE']) assert.equal(agentGuide({ JOURNEY_PRIVATE_DIR: '/synthetic/private', JOURNEY_AGENT_GUIDE: flag }), null)
 assert.match(agentGuide({ JOURNEY_PRIVATE_DIR: '/synthetic/private', JOURNEY_AGENT_GUIDE: 'true' }), /existing agent authorization is still required/)
})

test('real share and operator entrances generate guides per request with private opt-in and no guide forwarding', async () => {
 const saved = Object.fromEntries(Object.entries(process.env).filter(([key]) => /^(JOURNEY_|VITE_JOURNEY_)/.test(key)))
 const scratch = await mkdtemp(join(tmpdir(), 'journey-guide-check-'))
 const forwarded = []
 const backend = createServer((req, res) => { forwarded.push(req.url); res.setHeader('Content-Type', 'application/json'); res.end('{"backend":true}') })
 let vite
 try {
  for (const key of Object.keys(saved)) delete process.env[key]
  await new Promise(resolve => backend.listen(0, '127.0.0.1', resolve))
  process.env.JOURNEY_API_PORT = String(backend.address().port)
  for (const config of ['vite.share.config.mts', 'vite.config.mts']) {
   delete process.env.JOURNEY_PRIVATE_DIR
   delete process.env.JOURNEY_AGENT_GUIDE
   delete process.env.JOURNEY_AGENT_SSH_HOST
   vite = await createViteServer({ configFile: join(root, config), cacheDir: join(scratch, config), optimizeDeps: { noDiscovery: true, include: [] }, server: { port: 0, host: '127.0.0.1', strictPort: true, watch: null } })
   await vite.listen()
   const origin = `http://127.0.0.1:${vite.httpServer.address().port}`
   const getGuide = async () => {
    const response = await fetch(origin + '/llms.txt')
    assert.equal(response.status, 200)
    assert.equal(response.headers.get('content-type'), 'text/plain; charset=utf-8')
    assert.equal(response.headers.get('cache-control'), 'no-store')
    return response.text()
   }
   assert.match(await getGuide(), new RegExp(`API: http://127.0.0.1:${backend.address().port}`))
   assert.doesNotMatch(await getGuide(), /## SSH tunnel|ssh -N/)
   process.env.JOURNEY_AGENT_SSH_HOST = 'teammate-vm.example.invalid'
   assert.match(await getGuide(), new RegExp(`ssh -N -L 5858:127.0.0.1:${backend.address().port} teammate-vm.example.invalid`))
   process.env.JOURNEY_AGENT_SSH_HOST = 'updated-vm.example.invalid'
   assert.match(await getGuide(), /updated-vm\.example\.invalid/)
   const post = await fetch(origin + '/llms.txt', { method: 'POST' })
   assert.equal(post.status, 405)
   assert.equal(post.headers.get('allow'), 'GET')
   process.env.JOURNEY_PRIVATE_DIR = '/synthetic/private'
   const disabled = await fetch(origin + '/llms.txt')
   assert.equal(disabled.status, 404)
   assert.equal(await disabled.text(), 'Not found\n')
   process.env.JOURNEY_AGENT_GUIDE = 'false'
   assert.equal((await fetch(origin + '/llms.txt?probe=1')).status, 404)
   process.env.JOURNEY_AGENT_GUIDE = 'true'
   assert.match(await getGuide(), /Private mode/)
   if (config === 'vite.share.config.mts') {
    for (const method of ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']) {
     const response = await fetch(origin + '/mcp', { method })
     assert.doesNotMatch(await response.text(), /"backend":true/)
    }
   }
   assert.deepEqual(forwarded, [], 'guide and share MCP requests never reach the backend')
   assert.deepEqual(await (await fetch(origin + '/health')).json(), { backend: true })
   assert.deepEqual(forwarded.splice(0), ['/health'], 'positive control proves backend forwarding is observable')
   await vite.close()
   vite = undefined
  }
 } finally {
  await vite?.close()
  await new Promise(resolve => backend.close(resolve))
  for (const key of Object.keys(process.env)) if (/^(JOURNEY_|VITE_JOURNEY_)/.test(key)) delete process.env[key]
  Object.assign(process.env, saved)
  await rm(scratch, { recursive: true, force: true })
 }
})
