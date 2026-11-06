import type { ProxyOptions } from 'vite'
import { nodeHumanConfig } from './host/node-human-config'

type ShareRequest = { method?: string; url?: string; headers?: { upgrade?: string } }
type Operation = { path: string; methods: string[]; socket?: boolean }
const operatorPrefixes = ['/connect/', '/uploads/', '/health', '/auth/', '/save', '/repo-doc', '/doc', '/agents/', '/session', '/capabilities', '/mcp']

export function shareClientMode(env: NodeJS.ProcessEnv = process.env) {
 const human = nodeHumanConfig(env)?.mode
 const privateHost = !!env.JOURNEY_PRIVATE_DIR
 return {
  human,
  nativeAccount: !!human && env.JOURNEY_NATIVE_ACCOUNT === 'true',
  pairing: !!human && env.JOURNEY_AGENT_PAIRING === 'true',
  save: privateHost && env.JOURNEY_SHARE_SAVE === 'true' && !!env.JOURNEY_SAVE_DIR,
  repoDoc: privateHost && env.JOURNEY_SHARE_REPO_DOC === 'true' && !!env.JOURNEY_DOC_REPOS && Object.values(JSON.parse(env.JOURNEY_ROOM_REPOS || '{}')).some(value => Array.isArray(value) && value.length > 0),
 }
}

export function shareClientOperations(mode: ReturnType<typeof shareClientMode>): Operation[] {
 const operations: Operation[] = [
  { path: '/connect/', methods: ['GET'], socket: true },
  { path: '/uploads/', methods: ['GET', 'PUT'] },
  { path: '/doc', methods: ['GET'] },
 ]
 const add = (path: string, ...methods: string[]) => operations.push({ path, methods })
 if (!mode.human) add('/health', 'GET')
 if (mode.human) {
  for (const path of ['/auth/config', '/auth/entry', '/auth/rooms']) add(path, 'GET')
  for (const path of ['/auth/renew', '/auth/logout']) add(path, 'POST')
  if (mode.human === 'local') for (const path of ['/auth/local/start', '/auth/local/consume']) add(path, 'POST')
  else { add('/auth/provider/start', 'POST'); add('/auth/login', 'GET') }
  if (mode.nativeAccount) add('/auth/account', 'GET')
  if (mode.pairing) for (const operation of ['inspect', 'approve', 'deny', 'list', 'revoke']) add('/agents/' + operation, 'POST')
 }
 if (mode.save) add('/save', 'GET', 'POST')
 if (mode.repoDoc) add('/repo-doc', 'GET')
 return operations
}

export function clientApiProxy(target: string, entrance: 'operator' | 'share', env: NodeJS.ProcessEnv = process.env): Record<string, ProxyOptions> {
 if (entrance === 'operator') return Object.fromEntries(operatorPrefixes.map(prefix => [prefix === '/doc' ? '^/doc($|[?])' : prefix === '/connect/' ? '/connect' : prefix, { target, ws: prefix === '/connect/' }]))
 return Object.fromEntries(shareClientOperations(shareClientMode(env)).map(({ path, methods, socket }) => {
  const route = path.endsWith('/') ? `^${path}${socket ? '[a-zA-Z0-9_-]+' : '[a-zA-Z0-9_.%-]+'}($|[?])` : `^${path}($|[?])`
  const bypass = (req: ShareRequest) => {
   const raw = (req.url || '/').split('?')[0]
   const normalized = new URL(req.url || '/', 'http://localhost').pathname
   let decoded: string
   try { decoded = decodeURIComponent(normalized) } catch { return false }
   if (path.endsWith('/') && (/[\\/]/.test(decoded.slice(path.length)) || ['.', '..'].includes(decoded.slice(path.length)))) return false
   if (normalized !== raw || !new RegExp(route).test(normalized) || !methods.includes(req.method || '') || (socket && req.headers?.upgrade?.toLowerCase() !== 'websocket')) return false
  }
  return [route, {
   target, ws: !!socket, changeOrigin: path === '/connect/' || path === '/uploads/', bypass,
   ...(socket ? { configure: (proxy: Parameters<NonNullable<ProxyOptions['configure']>>[0]) => {
    proxy.on('proxyReqWs', (request, req, client) => {
     if (bypass(req) === false) { request.destroy(); client.end('HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n') }
    })
   } } : {}),
  }]
 }))
}
