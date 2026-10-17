import { readFile, mkdir, writeFile, readdir } from 'node:fs/promises'
import { spawn } from 'node:child_process'
import { join, resolve } from 'node:path'

const [client, endpoint, tokenPath, promptPath, outputPath] = process.argv.slice(2)
if (!['claude', 'codex'].includes(client) || !outputPath) throw new Error('usage: claude|codex <loopback API> <token file> <prompt file> <empty receipt directory>')
const url = new URL(endpoint)
if (url.protocol !== 'http:' || !['127.0.0.1', '[::1]', 'localhost'].includes(url.hostname) || url.pathname !== '/' || url.search || url.hash || url.username || url.password) throw new Error('Only a fresh local Node target is allowed')
const credential = (await readFile(resolve(tokenPath), 'utf8')).trim()
if (!/^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]{43,}$/.test(credential)) throw new Error('Credential file invalid')
const prompt = await readFile(resolve(promptPath), 'utf8')
const out = resolve(outputPath)
await mkdir(out, { recursive: true, mode: 0o700 })
if ((await readdir(out)).length) throw new Error('Receipt directory must be empty; no repeated phase')
const tools = ['get_doc', 'patch_doc', 'health']
const config = join(out, 'claude-mcp.json')
await writeFile(config, JSON.stringify({ mcpServers: { journey: { type: 'http', url: url.origin + '/mcp', headers: { Authorization: 'Bearer ${JOURNEY_NATIVE_TOKEN}' } } } }), { mode: 0o600 })
const args = client === 'claude' ? ['-p', '--output-format', 'stream-json', '--verbose', '--disable-slash-commands', '--restricted', '--strict-mcp-config', '--mcp-config', config, '--setting-sources', '', '--settings', JSON.stringify({ disableAllHooks: true, disableClaudeAiConnectors: true, enabledPlugins: {} }), '--tools', '', '--allowedTools', tools.map(tool => 'mcp__journey__' + tool).join(','), '--disallowedTools', 'Bash,Edit,Write', '--permission-mode', 'dontAsk', '--permission-prompts', 'none', '--no-session-persistence'] :
 ['exec', '--ignore-user-config', '--ephemeral', '--skip-git-repo-check', '--sandbox', 'read-only', '--json', '-C', out,
  '-c', 'mcp_servers.journey.url=' + JSON.stringify(url.origin + '/mcp'), '-c', 'mcp_servers.journey.bearer_token_env_var="JOURNEY_NATIVE_TOKEN"', '-c', 'mcp_servers.journey.tool_timeout_sec=20', '-c', 'mcp_servers.journey.enabled_tools=' + JSON.stringify(tools),
  ...tools.flatMap(tool => ['-c', 'mcp_servers.journey.tools.' + tool + '.approval_mode="approve"']),
  ...['shell_tool', 'apps', 'plugins', 'hooks', 'multi_agent', 'multi_agent_v2', 'memories'].flatMap(feature => ['-c', 'features.' + feature + '=false']), '-']
const child = spawn(client, args, { cwd: out, env: { ...process.env, JOURNEY_NATIVE_TOKEN: credential, ENABLE_CLAUDEAI_MCP_SERVERS: 'false' }, stdio: ['pipe', 'pipe', 'pipe'] })
let stdout = '', stderr = '', timedOut = false
child.stdout.on('data', value => { stdout += value }); child.stderr.on('data', value => { stderr += value })
const timer = setTimeout(() => { timedOut = true; child.kill('SIGTERM') }, 180_000)
child.stdin.end('Use only journey MCP tools, at most 8 calls. No shell, files, browser, other servers, delegation or retries. Preserve all existing records. Report actual calls and failures; do not infer success.\n' + prompt)
const exit = await new Promise(resolve => { child.once('error', error => resolve({ error: error.message })); child.once('close', (code, signal) => resolve({ code, signal })) })
clearTimeout(timer)
const sanitize = value => value.split(credential).join('[credential redacted]')
await writeFile(join(out, 'stdout.jsonl'), sanitize(stdout), { mode: 0o600 })
await writeFile(join(out, 'stderr.txt'), sanitize(stderr), { mode: 0o600 })
await writeFile(join(out, 'result.json'), JSON.stringify({ client, ...exit, timedOut, acceptance: 'Inspect actual MCP calls and independent readback; exit alone is not PASS' }), { mode: 0o600 })
console.log(JSON.stringify({ client, ...exit, timedOut }))
if (exit.code !== 0 || timedOut) process.exitCode = 1
