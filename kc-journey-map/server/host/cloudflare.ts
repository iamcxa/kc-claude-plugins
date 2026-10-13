import { DurableObjectSqliteSyncWrapper, SQLiteSyncStorage, TLSocketRoom } from '@tldraw/sync-core'
import { HostError, operate, prepareDoc } from './core'
import { admit, handle, type Host } from './transport'
import { currentGrant, validateGrants, type Admission, type Grant, type Metadata } from './policy'

type Env = { ROOMS: any; REGISTRY: any; ASSETS?: any; STATIC?: any; JOURNEY_ORIGIN: string; JOURNEY_GRANTS: string }
const stub = (namespace: any, id: string) => namespace.get(namespace.idFromName(id))
class RegistryMetadata implements Metadata {
 constructor(private env: Env) {}
 async call(path: string, body: any) {
  const response = await stub(this.env.REGISTRY, 'private-pilot').fetch(new Request('https://registry/' + path, { method: 'POST', body: JSON.stringify(body) }))
  if (!response.ok) throw new HostError(503, 'registry unavailable')
  return response.json()
 }
 async get<T>(key: string): Promise<T | null> { return await this.call('get', { key }) as T | null }
 async put(key: string, value: unknown) { await this.call('put', { key, value }) }
 async list<T>(prefix: string): Promise<Array<{ key: string; value: T }>> { return await this.call('list', { prefix }) as any }
}
export class JourneyRegistry {
 constructor(private ctx: any, private env: Env) {
  ctx.blockConcurrencyWhile(async () => {
   ctx.storage.sql.exec('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
   const grants = validateGrants(JSON.parse(env.JOURNEY_GRANTS || 'null'))
   for (const grant of grants) if (!this.get('grant:' + grant.credentialId)) this.put('grant:' + grant.credentialId, grant)
  })
 }
 get(key: string) { const row = this.ctx.storage.sql.exec('SELECT value FROM metadata WHERE key = ?', key).toArray()[0]; return row ? JSON.parse(row.value) : null }
 put(key: string, value: unknown) { this.ctx.storage.sql.exec('INSERT OR REPLACE INTO metadata VALUES (?, ?)', key, JSON.stringify(value)) }
 async fetch(req: Request) {
  const body = await req.json() as any
  const op = new URL(req.url).pathname
  if (op === '/get') return Response.json(this.get(body.key))
  if (op === '/put') { if (!body.key.startsWith('room:') || !this.get(body.key)) this.put(body.key, body.value); return Response.json({ ok: true }) }
  if (op === '/list') return Response.json(this.ctx.storage.sql.exec('SELECT key, value FROM metadata WHERE substr(key,1,?) = ? ORDER BY key', body.prefix.length, body.prefix).toArray().map((r: any) => ({ key: r.key, value: JSON.parse(r.value) })))
  if (op === '/revoke') {
   const grant = this.get('grant:' + body.credentialId) as Grant | null
   if (!grant) return Response.json({ error: 'unknown credential' }, { status: 404 })
   this.put('grant:' + grant.credentialId, { ...grant, revoked: true })
   const results = await Promise.all(grant.rooms.map(async room => {
    const result = await stub(this.env.ROOMS, room).fetch(new Request('https://room/internal/revoke', { method: 'POST', body: JSON.stringify({ credentialId: grant.credentialId }) }))
    return result.ok
   }))
   const complete = results.every(Boolean) && this.get('grant:' + grant.credentialId).revoked
   return Response.json({ revoked: true, complete }, { status: complete ? 200 : 503 })
  }
  return new Response(null, { status: 404 })
 }
}
export class CloudflareHost implements Host {
 private = true
 meta: RegistryMetadata
 port: number
 origin: string
 constructor(private env: Env) {
  this.origin = env.JOURNEY_ORIGIN
  const origin = new URL(this.origin)
  if (origin.origin !== this.origin || (origin.protocol !== 'https:' && !['localhost', '127.0.0.1'].includes(origin.hostname))) throw new Error('private origin requires HTTPS')
  validateGrants(JSON.parse(env.JOURNEY_GRANTS || 'null'))
  this.port = Number(origin.port || (origin.protocol === 'https:' ? 443 : 80))
  this.meta = new RegistryMetadata(env)
 }
 async document(room: string, method: string, prepared: any) {
  const response = await stub(this.env.ROOMS, room).fetch(new Request('https://room/internal/doc', { method: 'POST', body: JSON.stringify({ room, method, prepared }) }))
  if (!response.ok) throw new HostError(response.status, 'room operation failed')
  return response.json()
 }
 async health(allowed?: string[]) {
  const rooms = (await this.meta.list('room:')).map(e => e.key.slice(5)).filter(r => !allowed || allowed.includes(r))
  const active = await Promise.all(rooms.map(async room => {
   const response = await stub(this.env.ROOMS, room).fetch('https://room/internal/active')
   if (!response.ok) throw new HostError(503, 'room telemetry unavailable')
   return { roomId: room, ...await response.json() as object } as { roomId: string; sessions: number; clock: number }
  }))
  return { rooms, active }
 }
 capabilities(_room: string) { return { save: false, repoDoc: false, assets: !!this.env.ASSETS } }
 async putAsset(room: string, id: string, bytes: Uint8Array, type: string) {
  if (!this.env.ASSETS) throw new HostError(501, 'assets unsupported')
  if (!await this.meta.get('room:' + room)) throw new HostError(404, 'room not found')
  const blobKey = room + '/' + crypto.randomUUID()
  await this.env.ASSETS.put(blobKey, bytes, { httpMetadata: { contentType: type } })
  await this.meta.put('asset:' + room + ':' + id, { blobKey, contentType: type, size: bytes.length })
 }
 async getAsset(room: string, id: string) {
  const asset = await this.meta.get<{ blobKey: string; contentType: string }>('asset:' + room + ':' + id)
  if (!asset || !this.env.ASSETS) throw new HostError(404, 'asset not found')
  const blob = await this.env.ASSETS.get(asset.blobKey)
  if (!blob) throw new HostError(404, 'asset not found')
  return { data: new Uint8Array(await blob.arrayBuffer()), contentType: asset.contentType }
 }
}
export class JourneyRoom {
 room?: TLSocketRoom<any, any>
 meta: RegistryMetadata
 roomId?: string
 constructor(private ctx: any, private env: Env) {
  this.meta = new RegistryMetadata(env)
  ctx.setWebSocketAutoResponse(new (globalThis as any).WebSocketRequestResponsePair('{"type":"ping"}', '{"type":"pong"}'))
  ctx.blockConcurrencyWhile(async () => {
   this.roomId = await ctx.storage.get('roomId')
   if (!this.roomId) return
   for (const ws of ctx.getWebSockets()) {
    const a = ws.deserializeAttachment()
    if (!await this.allowed(a)) { ws.close(1008, 'credential invalid'); continue }
    if (a.snapshot) this.open().handleSocketResume({ sessionId: a.sessionId, socket: this.socket(ws), snapshot: a.snapshot })
    else ws.close(1012, 'reconnect required')
   }
  })
 }
 open() {
  if (!this.room) this.room = new TLSocketRoom({
   storage: new SQLiteSyncStorage({ sql: new DurableObjectSqliteSyncWrapper(this.ctx.storage) }),
   clientTimeout: Infinity,
   onSessionSnapshot: (sessionId, snapshot) => {
    for (const ws of this.ctx.getWebSockets()) {
     const a = ws.deserializeAttachment()
     if (a.sessionId === sessionId) ws.serializeAttachment({ ...a, snapshot })
    }
   },
  })
  return this.room
 }
 socket(ws: any) {
  return { get readyState() { return ws.readyState }, close: (code?: number, reason?: string) => ws.close(code, reason),
   send: (data: string) => {
    const a = ws.deserializeAttachment()
    if (a.admission.expiresAt <= Date.now()) { ws.close(1008, 'session expired'); return }
    ws.send(data)
   } }
 }
 async allowed(a: any) {
  try { return (await currentGrant(this.meta, a.admission)).rooms.includes(this.roomId!) } catch { return false }
 }
 async register(id: string) {
  this.roomId = id
  await this.ctx.storage.put('roomId', id)
  this.open()
  await this.meta.put('room:' + id, { createdAt: Date.now() })
 }
 async fetch(req: Request) {
  try {
   const url = new URL(req.url)
   if (url.pathname === '/internal/revoke') {
    const { credentialId } = await req.json() as any
    const sockets = this.ctx.getWebSockets().filter((ws: any) => ws.deserializeAttachment().admission.credentialId === credentialId)
    for (const ws of sockets) {
     ws.close(1008, 'credential revoked'); this.room?.handleSocketClose(ws.deserializeAttachment().sessionId)
    }
    for (let n = 0; n < 100 && sockets.some((ws: any) => ws.readyState !== 3); n++) await new Promise(resolve => setTimeout(resolve, 10))
    const complete = sockets.every((ws: any) => ws.readyState === 3)
    return Response.json({ ok: complete, closed: sockets.filter((ws: any) => ws.readyState === 3).length }, { status: complete ? 200 : 503 })
   }
   if (url.pathname === '/internal/active') return Response.json({ sessions: this.ctx.getWebSockets().length, clock: this.open().getCurrentDocumentClock() })
   if (url.pathname === '/internal/doc') {
    const { room, method, prepared } = await req.json() as any
    const valid = prepareDoc(method, prepared)
    await this.register(room)
    return Response.json(await operate(this.open(), room, method, valid))
   }
   if (url.pathname.startsWith('/connect/')) {
    const host = new CloudflareHost(this.env)
    const { room, admission } = await admit(host, req.headers, decodeURIComponent(url.pathname.slice(9)), false, true)
    if (req.headers.get('upgrade')?.toLowerCase() !== 'websocket') return new Response(null, { status: 426 })
    await this.register(room)
    const pair = new (globalThis as any).WebSocketPair(), client = pair[0], server = pair[1]
    const sessionId = url.searchParams.get('sessionId') || ''
    this.ctx.acceptWebSocket(server)
    server.serializeAttachment({ sessionId, admission })
    this.open().handleSocketConnect({ sessionId, socket: this.socket(server) })
    const deadline = admission!.expiresAt, alarm = await this.ctx.storage.getAlarm()
    if (!alarm || deadline < alarm) await this.ctx.storage.setAlarm(deadline)
    return new Response(null, { status: 101, webSocket: client } as any)
   }
   return new Response(null, { status: 404 })
  } catch (e) { return Response.json({ error: e instanceof HostError ? e.message : 'room unavailable' }, { status: e instanceof HostError ? e.status : 503 }) }
 }
 async webSocketMessage(ws: any, message: string | ArrayBuffer) {
  const a = ws.deserializeAttachment()
  if (!await this.allowed(a)) { ws.close(1008, 'credential invalid'); return }
  this.open().handleSocketMessage(a.sessionId, message)
  const snapshot = this.open().getSessionSnapshot(a.sessionId)
  if (snapshot) ws.serializeAttachment({ ...a, snapshot })
 }
 webSocketClose(ws: any, code: number, reason: string) { ws.close(code, reason); this.room?.handleSocketClose(ws.deserializeAttachment().sessionId) }
 webSocketError(ws: any) { this.room?.handleSocketError(ws.deserializeAttachment().sessionId) }
 async alarm() {
  let next = Infinity
  for (const ws of this.ctx.getWebSockets()) {
   const a = ws.deserializeAttachment()
   if (!await this.allowed(a)) { ws.close(1008, 'session expired'); this.room?.handleSocketClose(a.sessionId) }
   else next = Math.min(next, a.admission.expiresAt)
  }
  if (Number.isFinite(next)) await this.ctx.storage.setAlarm(next)
 }
}
export default {
 async fetch(req: Request, env: Env) {
  let host: CloudflareHost
  try { host = new CloudflareHost(env) } catch { return Response.json({ error: 'private host not configured' }, { status: 503 }) }
  const url = new URL(req.url)
  if (url.pathname.startsWith('/connect/')) {
   try {
    const { room } = await admit(host, req.headers, decodeURIComponent(url.pathname.slice(9)), false, true)
    return await stub(env.ROOMS, room).fetch(req)
   } catch (e) { return Response.json({ error: e instanceof HostError ? e.message : 'room unavailable' }, { status: e instanceof HostError ? e.status : 503 }) }
  }
  if (['/', '/index.html'].includes(url.pathname) || url.pathname.startsWith('/assets/')) return env.STATIC ? env.STATIC.fetch(req) : new Response('canvas build unavailable', { status: 404 })
  return handle(host, req)
 },
}

export { exportRoom, restoreRoom } from './recovery'
