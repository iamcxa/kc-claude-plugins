import assert from 'node:assert/strict'
import { test } from 'node:test'
import { mkdtemp, writeFile, mkdir, readFile, rm } from 'node:fs/promises'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { launchNative, nativeArguments, nativeEnvironment, observeNative } from './private-native-client.mjs'

test('paired launch configs contain only helper paths and preserve native login locations while dropping ambient secrets', () => {
 const env = nativeEnvironment({ HOME: '/existing-home', CODEX_HOME: '/existing-codex', PATH: '/bin', API_TOKEN: 'forbidden', JOURNEY_NATIVE_TOKEN: 'forbidden', CODEX_THREAD_ID: 'ambient' })
 assert.equal(env.HOME, '/existing-home'); assert.equal(env.CODEX_HOME, '/existing-codex')
 assert.equal(env.API_TOKEN, undefined); assert.equal(env.JOURNEY_NATIVE_TOKEN, undefined); assert.equal(env.CODEX_THREAD_ID, undefined)
 const args = nativeArguments('codex', '/fixture/config', '/fixture/store', '/fixture/mcp', '/neutral')
 assert.ok(args.includes('--ignore-user-config')); assert.ok(args.includes('gpt-6.1-sol')); assert.ok(args.includes('read-only'))
 assert.ok(args.includes('model_reasoning_effort="high"')); assert.ok(args.some(a => a.includes('agent-helper.mjs') && a.includes('"mcp"')))
 assert.ok(!args.some(a => /bearer_token|JOURNEY_NATIVE_TOKEN/.test(a)))
 assert.ok(!args.some(a => a.startsWith('model_providers.')))
})
test('native event observation retains real failure calls and refuses extra/wrapper or unobservable items', () => {
 const seen = new Map()
 const event = { type: 'item.completed', item: { id: '1', type: 'mcp_tool_call', server: 'journey', tool: 'get_doc', arguments: { room: 'denied' }, status: 'failed', error: { message: 'room_denied' } } }
 assert.equal(observeNative('codex', event, seen), 'tool_error'); assert.equal(seen.get('1').arguments.room, 'denied')
 assert.equal(observeNative('codex', { type: 'item.started', item: { id: '2', type: 'code_mode_call', name: 'exec' } }, seen), 'unexpected_native_item')
 assert.equal(observeNative('claude', { type: 'assistant', message: { content: [{ type: 'tool_use', id: '3', name: 'Bash', input: {} }] } }, seen), 'unexpected_tool_call')
 for (let i = 2; i <= 9; i++) observeNative('claude', { message: { content: [{ type: 'tool_use', id: String(i), name: 'mcp__journey__health', input: {} }] } }, seen)
 assert.equal(observeNative('claude', { message: { content: [{ type: 'tool_use', id: '10', name: 'mcp__journey__health', input: {} }] } }, seen), 'call_limit')
})
test('actual child receipt stops after an observed disallowed tool and cannot report a passing process exit', async () => {
 const root = await mkdtemp(join(tmpdir(), 'native-runner-test-'))
 try {
  const config = join(root, 'installation.json'), store = join(root, 'store'), prompt = join(root, 'prompt.txt'), out = join(root, 'receipts'), executable = join(root, 'fake-native')
  await mkdir(store, { mode: 0o700 })
  await writeFile(config, JSON.stringify({ endpoint: 'http://127.0.0.1:1234', backendId: 'synthetic', installationId: 'independent', memberId: 'owner', rooms: ['fresh'], label: 'synthetic' }))
  await writeFile(prompt, 'No model is run in this test.')
  await writeFile(executable, '#!' + process.execPath + '\nif(process.argv.includes("--version")){console.log("2.1.303 (Claude Code)")}else{console.log(JSON.stringify({type:"assistant",message:{content:[{type:"tool_use",id:"bad",name:"Bash",input:{}}]}}));setInterval(()=>{},1000)}\n', { mode: 0o700 })
  assert.equal(await launchNative(['claude', config, store, prompt, out, executable]), 1)
  const result = JSON.parse(await readFile(join(out, 'result.json'), 'utf8'))
  assert.equal(result.stopped, 'unexpected_tool_call'); assert.equal(result.signal, 'SIGTERM')
  const mcp = JSON.parse(await readFile(join(out, 'claude-mcp.json'), 'utf8')).mcpServers.journey
  assert.equal(mcp.type, 'stdio'); assert.equal(mcp.args[1], 'mcp'); assert.equal(mcp.args[2], config); assert.equal(mcp.args[3], store)
  assert.ok(!JSON.stringify(mcp).includes('Authorization'))
 } finally { await rm(root, { recursive: true, force: true }) }
})
