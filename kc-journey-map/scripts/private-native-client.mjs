import { readFile, mkdir, writeFile, readdir, lstat, mkdtemp, rm } from 'node:fs/promises'
import { spawn, execFileSync } from 'node:child_process'
import { join, resolve, isAbsolute } from 'node:path'
import { tmpdir } from 'node:os'
import { fileURLToPath } from 'node:url'
import { validateInstallation } from './agent-installation.mjs'

const tools = ['get_doc', 'patch_doc', 'health']
const allowedConfig = ['endpoint', 'backendId', 'installationId', 'memberId', 'rooms', 'label']
const helper = fileURLToPath(new URL('./agent-helper.mjs', import.meta.url))
export function nativeEnvironment(source = process.env) {
 const keys = ['HOME', 'USER', 'LOGNAME', 'PATH', 'TMPDIR', 'LANG', 'TERM', 'CODEX_HOME', 'CLAUDE_CONFIG_DIR']
 return { ...Object.fromEntries(keys.filter(key => source[key] !== undefined).map(key => [key, source[key]])), ENABLE_CLAUDEAI_MCP_SERVERS: 'false' }
}
export function nativeArguments(client, config, store, mcpConfig, cwd) {
 if (client === 'claude') return ['-p', '--output-format', 'stream-json', '--verbose', '--restricted', '--disable-slash-commands', '--no-chrome', '--strict-mcp-config', '--mcp-config', mcpConfig, '--setting-sources', '', '--settings', JSON.stringify({ disableAllHooks: true, disableClaudeAiConnectors: true, enabledPlugins: {} }), '--tools', '', '--allowedTools', tools.map(tool => 'mcp__journey__' + tool).join(','), '--disallowedTools', 'Bash,Edit,Write', '--permission-mode', 'dontAsk', '--permission-prompts', 'none', '--no-session-persistence']
 const settings = {
  'model_reasoning_effort': 'high', 'project_doc_max_bytes': 0, 'skills.include_instructions': false,
  'agents.enabled': false, 'web_search': 'disabled', 'suppress_unstable_features_warning': true,
  'features.code_mode.direct_only_tool_namespaces': ['mcp__journey'],
  'mcp_servers.journey.command': process.execPath,
  'mcp_servers.journey.args': [helper, 'mcp', config, store],
  'mcp_servers.journey.enabled_tools': tools, 'mcp_servers.journey.tool_timeout_sec': 20,
 }
 for (const tool of tools) settings['mcp_servers.journey.tools.' + tool + '.approval_mode'] = 'approve'
 for (const feature of ['shell_tool', 'apps', 'plugins', 'hooks', 'multi_agent', 'multi_agent_v2', 'memories', 'skill_search']) settings['features.' + feature] = false
 settings['features.skip_host_skill_discovery'] = true
 return ['--no-daemon', 'exec', '--ignore-user-config', '--ephemeral', '--skip-git-repo-check', '--sandbox', 'read-only', '--strict-config', '--json', '-C', cwd, '-m', 'gpt-6.1-sol', ...Object.entries(settings).flatMap(([key, value]) => ['-c', key + '=' + JSON.stringify(value)]), '-']
}
export function observeNative(client, event, seen) {
 let calls = [], toolError = false
 if (client === 'claude') {
  calls = (event.message?.content || []).filter(item => item.type === 'tool_use' || item.type === 'server_tool_use').map(item => ({ id: item.id, name: item.name, arguments: item.input }))
  if (event.type === 'user' && event.message?.content?.some(item => item.type === 'tool_result' && item.is_error)) return 'tool_error'
  if (event.type === 'result' && event.is_error) return 'native_error'
 } else if (event.type === 'item.started' || event.type === 'item.completed') {
  const item = event.item
  if (!item || !['reasoning', 'agent_message', 'mcp_tool_call'].includes(item.type)) return 'unexpected_native_item'
  if (item.type === 'mcp_tool_call') {
   calls = [{ id: item.id, name: 'mcp__' + item.server + '__' + item.tool, arguments: item.arguments }]
   toolError = item.status === 'failed' || !!item.error || !!item.result?.isError
  }
 }
 if (event.type === 'error' || event.type === 'turn.failed') return 'native_error'
 for (const call of calls) {
  if (!call.id || !tools.map(tool => 'mcp__journey__' + tool).includes(call.name)) return 'unexpected_tool_call'
  if (!seen.has(call.id)) seen.set(call.id, call)
  if (seen.size > 8) return 'call_limit'
 }
 return toolError ? 'tool_error' : null
}
async function ownedDirectory(path) {
 const stat = await lstat(path)
 if (!stat.isDirectory() || stat.isSymbolicLink() || stat.uid !== process.geteuid() || (stat.mode & 0o077)) throw new Error('owned_0700_directory_required')
}
export async function launchNative(argv) {
 const [client, configPath, storeRoot, promptPath, outputPath, executable] = argv
 if (argv.length !== 6 || !['claude', 'codex'].includes(client) || ![configPath, storeRoot, promptPath, outputPath, executable].every(isAbsolute)) throw new Error('usage_client_absolute_config_store_prompt_empty_receipts_native_executable')
 const config = JSON.parse(await readFile(configPath, 'utf8'))
 if (Object.keys(config).some(key => !allowedConfig.includes(key))) throw new Error('config_contains_unsupported_fields')
 validateInstallation(config)
 await ownedDirectory(storeRoot)
 await mkdir(outputPath, { mode: 0o700 })
 await ownedDirectory(outputPath)
 if ((await readdir(outputPath)).length) throw new Error('receipt_directory_must_be_empty')
 const env = nativeEnvironment(), version = execFileSync(executable, ['--version'], { env, encoding: 'utf8', timeout: 10000 }).trim()
 if (!(client === 'codex' ? /^codex-cli 0\.162\.1$/ : /^2\.1\.303 \(Claude Code\)$/).test(version)) throw new Error('native_version_requires_reverification')
 const cwd = await mkdtemp(join(tmpdir(), 'journey-native-cwd-'))
 const mcpConfig = join(outputPath, 'claude-mcp.json')
 await writeFile(mcpConfig, JSON.stringify({ mcpServers: { journey: { type: 'stdio', command: process.execPath, args: [helper, 'mcp', configPath, storeRoot] } } }), { mode: 0o600 })
 const args = nativeArguments(client, configPath, storeRoot, mcpConfig, cwd)
 const prompt = await readFile(promptPath, 'utf8')
 const child = spawn(executable, args, { cwd, env, detached: true, stdio: ['pipe', 'pipe', 'pipe'] })
 let stdout = '', stderr = '', buffered = '', stopped = null
 const seen = new Map()
 let hardKill
 const stop = reason => {
  if (stopped) return
  stopped = reason
  try { process.kill(-child.pid, 'SIGTERM') } catch {}
  hardKill = setTimeout(() => { try { process.kill(-child.pid, 'SIGKILL') } catch {} }, 5000)
 }
 const timer = setTimeout(() => stop('timeout'), 180000)
 child.stdout.on('data', value => {
  stdout += value; buffered += value
  let at
  while ((at = buffered.indexOf('\n')) !== -1) {
   const line = buffered.slice(0, at); buffered = buffered.slice(at + 1)
   if (!line.trim()) continue
   try { const event = JSON.parse(line); const reason = observeNative(client, event, seen); if (reason) stop(reason) }
   catch { stop('unparseable_native_event') }
  }
 })
 child.stderr.on('data', value => { stderr += value })
 child.stdin.on('error', () => {})
 child.stdin.end('Use only journey get_doc, patch_doc and health, at most 8 calls. Do not use any wrapper, shell, browser, file, search, resource, management or subagent tool. If the native protocol requires one, stop and state that limitation. No retries. Preserve every existing record. Use the exact supplied complete records and singular put/remove.\n' + prompt)
 const exit = await new Promise(resolve => { child.once('error', error => resolve({ error: error.code })); child.once('close', (code, signal) => resolve({ code, signal })) })
 clearTimeout(timer); clearTimeout(hardKill)
 if (buffered.trim()) stopped ||= 'incomplete_native_event'
 const clean = value => value.replace(/agt_[A-Za-z0-9_-]+\.[a-f0-9]{64}/g, '[credential redacted]')
 await writeFile(join(outputPath, 'stdout.jsonl'), clean(stdout), { mode: 0o600 })
 await writeFile(join(outputPath, 'stderr.txt'), clean(stderr), { mode: 0o600 })
 const result = { client, version, executable, args, cwd, ...exit, stopped, calls: [...seen.values()], acceptance: 'Observation only; require actual MCP arguments/results plus independent family/backend/browser readback. Extra advertised built-ins were not removed.' }
 await writeFile(join(outputPath, 'result.json'), JSON.stringify(result, null, 2), { mode: 0o600 })
 await rm(cwd, { recursive: true })
 console.log(JSON.stringify({ client, code: exit.code, stopped, observedCalls: seen.size }))
 return exit.code === 0 && !stopped && seen.size > 0 ? 0 : 1
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
 try { process.exitCode = await launchNative(process.argv.slice(2)) }
 catch (error) { console.error(error.message); process.exitCode = 1 }
}
