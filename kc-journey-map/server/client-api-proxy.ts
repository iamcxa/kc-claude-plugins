import type { ProxyOptions } from 'vite'

export const clientApiPrefixes = [
 '/connect/', '/uploads/', '/health', '/auth/', '/save', '/repo-doc', '/doc',
 '/agents/inspect', '/agents/approve', '/agents/deny', '/agents/list', '/agents/revoke',
] as const

export function clientApiProxy(target: string, mode: 'operator' | 'share'): Record<string, ProxyOptions> {
 const prefixes = mode === 'operator' ? [...clientApiPrefixes.filter(prefix => !prefix.startsWith('/agents/')), '/agents/', '/session', '/capabilities', '/mcp'] : clientApiPrefixes
 return Object.fromEntries(prefixes.map(prefix => {
  let route = prefix.endsWith('/') ? prefix : `^${prefix}($|[?])`
  if (mode === 'operator' && prefix !== '/doc') route = prefix === '/connect/' ? '/connect' : prefix
  return [route, {
   target,
   ws: prefix === '/connect/',
   changeOrigin: mode === 'share' && (prefix === '/connect/' || prefix === '/uploads/'),
   ...(mode === 'share' ? { bypass: (req: { method?: string; url?: string }) => {
    const path = new URL(req.url || '/', 'http://localhost').pathname
    if (prefix.endsWith('/') ? !path.startsWith(prefix) : path !== prefix) return false
    if (prefix === '/doc' && req.method !== 'GET') return false
   } } : {}),
  }]
 }))
}
