import { canonicalAsset, HostError, prepareDoc } from './core'
import { authenticate, authorize, exchange, requireOrigin, type Admission, type Metadata } from './policy'
export interface Host {
 private: boolean
 origin: string
 port: number
 meta: Metadata
 document(room: string, method: string, prepared: any): Promise<unknown>
 health(allowed?: string[]): Promise<{ rooms: string[]; active: Array<{ roomId: string; sessions: number; clock: number }> }>
 capabilities(room: string): { save: boolean; repoDoc: boolean; assets: boolean }
 putAsset(room: string, id: string, bytes: Uint8Array, type: string): Promise<void>
 getAsset(room: string, id: string): Promise<{ data: Uint8Array; contentType: string }>
 save?(room: string, url: URL, method: string, body: any): Promise<unknown>
 repoDoc?(room: string, url: URL): Promise<unknown>
}
const json = (value: unknown, status = 200) => Response.json(value, { status })
export async function admit(host: Host, headers: Headers, raw: string, write = false, socket = false) {
 const admission = host.private ? await authenticate(host.meta, headers) : null
 if (host.private && (socket || (write && admission?.cookie))) requireOrigin(headers, host.origin)
 return { room: authorize(admission, raw), admission }
}
async function health(host: Host, admission: Admission | null) {
 const h = await host.health(admission?.rooms)
 return { ok: true, tldraw: '5.4.0', port: host.port, rooms: h.rooms.filter(r => !admission || admission.rooms.includes(r)),
  active: h.active.filter(r => !admission || admission.rooms.includes(r.roomId)) }
}
const tools = ['get_doc', 'patch_doc', 'put_doc', 'health'].map(name => ({
 name, description: name === 'health' ? 'Authorized room inventory' : name === 'patch_doc'
  ? 'Update a room with body.put (singular): an array of complete tldraw records, and body.remove: an array of record IDs. Omitted arrays default to empty. Returns roomId, put and removed (submitted operation counts), and clock. Check counts against the intended operations, then use get_doc to verify exact records/text or absence; success or clock alone does not prove the intended edit. Unknown body keys such as puts do not write records.'
  : 'Existing complete-record journey document operation',
 inputSchema: { type: 'object', properties: name === 'health' ? {} : { room: { type: 'string' }, ...(name === 'get_doc' ? {} : { body: {
  type: 'object', ...(name === 'patch_doc' ? { properties: {
   put: { type: 'array', description: 'Complete tldraw records to insert or replace, including id, typeName and all fields required by that record type; not partial field edits. Defaults to [].', items: { type: 'object' } },
   remove: { type: 'array', description: 'Record IDs to remove. Defaults to [].', items: { type: 'string' } },
  } } : {}),
 } }) },
  ...(name === 'health' ? {} : { required: ['room'] }), additionalProperties: false },
}))
async function mcp(host: Host, req: Request, admission: Admission | null) {
 if (req.method !== 'POST') return new Response(null, { status: 405, headers: { Allow: 'POST' } })
 if (req.headers.has('origin')) requireOrigin(req.headers, host.origin)
 const rpc = await req.json() as any
 if (!rpc || rpc.jsonrpc !== '2.0' || typeof rpc.method !== 'string') return json({ error: 'invalid JSON-RPC request' }, 400)
 if (rpc.method.startsWith('notifications/')) return new Response(null, { status: 202 })
 let result: any
 if (rpc.method === 'initialize') result = { protocolVersion: '2025-03-26', capabilities: { tools: {} }, serverInfo: { name: 'kc-journey-map', version: '0.0.0' } }
 else if (rpc.method === 'ping') result = {}
 else if (rpc.method === 'tools/list') result = { tools }
 else if (rpc.method === 'tools/call') {
  const { name, arguments: args = {} } = rpc.params ?? {}
  let value
  if (name === 'health') value = await health(host, admission)
  else if (['get_doc', 'patch_doc', 'put_doc'].includes(name)) {
   const room = authorize(admission, args.room ?? 'default')
   const method = { get_doc: 'GET', patch_doc: 'PATCH', put_doc: 'PUT' }[name as string]!
   value = await host.document(room, method, prepareDoc(method, args.body))
  } else return json({ jsonrpc: '2.0', id: rpc.id, error: { code: -32601, message: 'unknown tool' } })
  result = { content: [{ type: 'text', text: JSON.stringify(value) }], structuredContent: value }
 } else return json({ jsonrpc: '2.0', id: rpc.id, error: { code: -32601, message: 'method not found' } })
 return json({ jsonrpc: '2.0', id: rpc.id, result })
}
export async function handle(host: Host, req: Request): Promise<Response> {
 const response = await route(host, req)
 if (host.private) response.headers.set('Cache-Control', 'private, no-store')
 return response
}
async function route(host: Host, req: Request): Promise<Response> {
 try {
  const url = new URL(req.url), method = req.method
  if (url.pathname === '/session' && method === 'POST') {
   if (!host.private) throw new HostError(400, 'sessions require private mode')
   const session = await exchange(host.meta, req.headers, host.origin)
   return Response.json({ ok: true, expiresAt: session.expiresAt }, { headers: { 'Set-Cookie': session.cookie, 'Cache-Control': 'no-store' } })
  }
  const admission = host.private ? await authenticate(host.meta, req.headers) : null
  if (host.private && method !== 'GET' && admission?.cookie) requireOrigin(req.headers, host.origin)
  const rawRoom = url.searchParams.get('room') || 'default'
  const room = ['/mcp', '/health'].includes(url.pathname) ? rawRoom : authorize(admission, rawRoom)
  if (url.pathname === '/mcp') return await mcp(host, req, admission)
  if (url.pathname === '/health' && method === 'GET') return json(await health(host, admission))
  if (url.pathname === '/capabilities' && method === 'GET') return json(host.capabilities(room))
  if (url.pathname === '/doc' && ['GET', 'PATCH', 'PUT'].includes(method))
   return json(await host.document(room, method, prepareDoc(method, method === 'GET' ? null : await req.json())))
  if (url.pathname.startsWith('/uploads/')) {
   const raw = decodeURIComponent(url.pathname.slice('/uploads/'.length)), id = canonicalAsset(raw)
   if (host.private && (raw !== id || !id || id === '.' || id === '..')) throw new HostError(403, 'asset forbidden')
   if (method === 'PUT') {
    await host.putAsset(room, id, new Uint8Array(await req.arrayBuffer()), req.headers.get('content-type') || 'application/octet-stream')
    return json({ ok: true })
   }
   if (method === 'GET') {
    const asset = await host.getAsset(room, id)
    return new Response(asset.data as BodyInit, { headers: { 'Content-Type': asset.contentType, 'Content-Security-Policy': "default-src 'none'", 'X-Content-Type-Options': 'nosniff' } })
   }
  }
  if (url.pathname === '/save' && ['GET', 'POST'].includes(method)) {
   if (!host.capabilities(room).save || !host.save) return new Response('save unsupported', { status: 501 })
   return json(await host.save(room, url, method, method === 'POST' ? await req.json() : null))
  }
  if (url.pathname === '/repo-doc' && method === 'GET') return json(host.capabilities(room).repoDoc && host.repoDoc
   ? await host.repoDoc(room, url) : { state: 'unavailable', reason: 'checkout capability is unavailable' })
  throw new HostError(404, 'not found')
 } catch (e) {
  if (e instanceof HostError) return json({ error: e.message, ...e.details }, e.status)
  if (e instanceof SyntaxError) return json({ error: 'invalid JSON' }, 400)
  return json({ error: 'host operation failed' }, 503)
 }
}
