import type { Plugin } from 'vite'

export function agentGuide(env: NodeJS.ProcessEnv = process.env): string | null {
 if (env.JOURNEY_PRIVATE_DIR && env.JOURNEY_AGENT_GUIDE !== 'true') return null
 const configuredPort = Number(env.JOURNEY_API_PORT || 5858)
 const port = Number.isInteger(configuredPort) && configuredPort > 0 && configuredPort <= 65535 ? configuredPort : 5858
 const host = env.JOURNEY_AGENT_SSH_HOST?.trim()
 const sshHost = host && /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/i.test(host) ? host : undefined
 const api = `http://127.0.0.1:${sshHost ? 5858 : port}`
 return [
  '# kc-journey-map agent guide',
  'An editable tldraw canvas for collaborating on user journeys in named rooms.',
  'The repository journey YAML is the source of truth; the room is its rendering.',
  'Human-only drawings have no YAML authority: preserve them before any replacement.',
  '',
  ...(sshHost ? [
   '## SSH tunnel',
   'Use your own SSH access to the VM (granted by its operator). Keep this command running:',
   `ssh -N -L 5858:127.0.0.1:${port} ${sshHost}`,
   'Run the commands below on your machine while that tunnel is open.',
   '',
  ] : []),
  '## Rooms and access',
  `API: ${api}`,
  `curl -fsS ${api}/health`,
  'The rooms array lists known room IDs. Confirm the target with the owner before writing.',
  'get_doc on a new room ID creates that room; choose a new ID only when asked to create one.',
  'The share entrance does not forward MCP or document writes; use the API directly.',
  ...(env.JOURNEY_PRIVATE_DIR ? ['Private mode: existing agent authorization is still required, including through SSH.',
   'Use JOURNEY_API_TOKEN with the plugin commands; for curl supply your authorized bearer locally.'] : []),
  '',
  '## MCP (Model Context Protocol, JSON-RPC over HTTP POST)',
  `Endpoint: ${api}/mcp`,
  'Tools: get_doc, patch_doc, put_doc, health. Use tools/list for their input schemas.',
  'get_doc example (replace example-room with the agreed room ID):',
  `curl -fsS ${api}/mcp -H 'Content-Type: application/json' -d '${JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: 'get_doc', arguments: { room: 'example-room' } } })}'`,
  'patch_doc example (empty patch safely demonstrates the request format):',
  `curl -fsS ${api}/mcp -H 'Content-Type: application/json' -d '${JSON.stringify({ jsonrpc: '2.0', id: 2, method: 'tools/call', params: { name: 'patch_doc', arguments: { room: 'example-room', body: { put: [], remove: [] } } } })}'`,
  'For an actual edit, put contains complete tldraw records read with get_doc, not partial fields.',
  'remove contains record IDs. Check put/removed counts, then get_doc to verify the exact edit.',
  'put_doc replaces the whole document; export a .tldr before using it.',
  '',
  '## Plugin commands',
  'Run from the installed kc-journey-map plugin directory, with dependencies installed:',
  `export JOURNEY_API=${api}`,
  'Set JOURNEY_CANVAS to the reachable board URL for export; it requires agent-browser and the live canvas.',
  'Export before overwriting:',
  'node lib/journey-tldr.mjs export <roomId> <backup.tldr>',
  'Read canvas edits against the source YAML:',
  'node lib/journey-read.mjs <journey.yaml> <roomId>',
  'Review changes before applying readback with --write (or --out <other.yaml>).',
  'Render the source into the agreed room:',
  'node lib/journey-render.mjs <journey.yaml> <roomId>',
  '',
  '## Safety',
  'Export a .tldr before overwriting a room; never delete a room database.',
  'Re-rendering cannot recover unexported manual edits. Read back or preserve them first.',
  'Do not use --force to discard edits without the owner approving that loss.',
  'Keep credentials out of records, URLs and YAML. See skills/kc-journey-map/references/canvas.md.',
  '',
 ].join('\n')
}

export function agentGuidePlugin(env: NodeJS.ProcessEnv = process.env): Plugin {
 return {
  name: 'journey-agent-guide',
  configureServer(server) {
   server.middlewares.use((req, res, next) => {
    if (req.url?.split('?')[0] !== '/llms.txt') return next()
    const guide = agentGuide(env)
    res.setHeader('Content-Type', 'text/plain; charset=utf-8')
    res.setHeader('Cache-Control', 'no-store')
    res.setHeader('X-Content-Type-Options', 'nosniff')
    if (guide === null) { res.statusCode = 404; res.end('Not found\n'); return }
    if (req.method !== 'GET') { res.statusCode = 405; res.setHeader('Allow', 'GET'); res.end('Method not allowed\n'); return }
    res.end(guide)
   })
  },
 }
}
