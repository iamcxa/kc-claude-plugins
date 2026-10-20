import { DurableObjectSqliteSyncWrapper, SQLiteSyncStorage, TLSocketRoom } from '@tldraw/sync-core'
import { HostError, operate, prepareDoc } from './core'
import { admit, handle, type Host } from './transport'
import { currentGrant, validateGrants, type Admission, type Grant, type Metadata } from './policy'
import { pruneExpiredSessions } from './session-retention'
import { bootstrapHuman, humanOperation, validateHumanConfig, type HumanConfig, type SyncMetadata } from './human-store'
import { audited } from './audit'
import { securityOperation, matchesTarget } from './security-store'
import { canSend, renewLease, type StreamLease } from './stream-lease'
import { bootstrapAgent, agentOperation, captureAgent, agentResult, type AgentScope } from './agent-store'

type Env = { ROOMS: any; REGISTRY: any; ASSETS?: any; STATIC?: any; JOURNEY_ORIGIN: string; JOURNEY_GRANTS: string; JOURNEY_HUMAN_CONFIG?: string; JOURNEY_AGENT_PAIRING?: string }
const agentScope = (env: Env, roomId: string): AgentScope => ({ roomId, records: 'full-replacement', assets: !!env.ASSETS, saveDirectory: null, repositories: [] })
const stub = (namespace: any, id: string) => namespace.get(namespace.idFromName(id))
const assetBlobKey = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/
const ownsAsset = (room: string, key: unknown) => typeof key === 'string' && key.startsWith(room + '/') && assetBlobKey.test(key.slice(room.length + 1))
class RegistryMetadata implements Metadata {
 constructor(private env: Env) {}
 async call(path: string, body: any) {
  const response = await stub(this.env.REGISTRY, 'private-pilot').fetch(new Request('https://registry/' + path, { method: 'POST', body: JSON.stringify(body) }))
  if (!response.ok) { const body = await response.json().catch(() => ({})) as any; throw new HostError(response.status, body.error || 'registry unavailable', body.category ? { category: body.category } : {}) }
  return response.json()
 }
 async get<T>(key: string): Promise<T | null> { return await this.call('get', { key }) as T | null }
 async put(key: string, value: unknown) { await this.call('put', { key, value }) }
 async human(operation: string, input: any) { return this.call('human', { operation, input }) }
 async agent(operation: string, input: any) { return this.call('agent', { operation, input }) }
 async security(operation: string, input: any) { return this.call('security', { operation, input }) }
 async replaceAsset(room: string, id: string, value: unknown) { return await this.call('replace-asset', { room, id, value }) as { previous: { blobKey: string } | null } }
 async list<T>(prefix: string): Promise<Array<{ key: string; value: T }>> { return await this.call('list', { prefix }) as any }
}
export class JourneyRegistry {
 constructor(private ctx: any, private env: Env) {
  ctx.blockConcurrencyWhile(async () => {
   ctx.storage.sql.exec('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
   if (env.JOURNEY_HUMAN_CONFIG) {
    const config = validateHumanConfig(JSON.parse(env.JOURNEY_HUMAN_CONFIG), env.JOURNEY_ORIGIN)
    if (config.mode !== 'cloudflare') throw new Error('Cloudflare does not accept local owner handoff')
    ctx.storage.transactionSync(() => bootstrapHuman(this.sync(), config))
   }
   const grants = validateGrants(JSON.parse(env.JOURNEY_GRANTS || 'null'))
   if (env.JOURNEY_AGENT_PAIRING === 'true' && !env.JOURNEY_HUMAN_CONFIG) throw new Error('agent pairing requires verified human entry')
   ctx.storage.transactionSync(() => bootstrapAgent(this.sync(), env.JOURNEY_AGENT_PAIRING === 'true', { assets: !!env.ASSETS, saveDirectory: null, repositories: {} }))
   for (const grant of grants) if (!this.get('grant:' + grant.credentialId)) this.put('grant:' + grant.credentialId, grant)
  })
 }
 get(key: string) { const row = this.ctx.storage.sql.exec('SELECT value FROM metadata WHERE key = ?', key).toArray()[0]; return row ? JSON.parse(row.value) : null }
 put(key: string, value: unknown) {
  if (key.startsWith('session:')) pruneExpiredSessions((sql, ...bindings) => this.ctx.storage.sql.exec(sql, ...bindings).toArray())
  this.ctx.storage.sql.exec('INSERT OR REPLACE INTO metadata VALUES (?, ?)', key, JSON.stringify(value))
 }
 sync(): SyncMetadata {
  return { get: key => this.get(key), put: (key, value) => this.put(key, value), delete: key => { this.ctx.storage.sql.exec('DELETE FROM metadata WHERE key = ?', key) },
   list: (prefix, limit, after = '') => this.ctx.storage.sql.exec('SELECT key,value FROM metadata WHERE key >= ? AND key < ? AND key > ? ORDER BY key LIMIT ?', prefix, prefix + '\uffff', after, limit).toArray().map((row: any) => ({ key: row.key, value: JSON.parse(row.value) })) }
 }
 async fetch(req: Request) {
  const body = await req.json() as any
  const op = new URL(req.url).pathname
  if (op === '/agent') {
   try {
    const result=this.ctx.storage.transactionSync(() => captureAgent(() => agentOperation(this.sync(), body.operation, body.input, room => agentScope(this.env, room))))
    if(result.ok && result.value?.operationId)result.value.denialCommitObservedAt=Date.now()
    const f=body.input.familyId ? this.get('agent-family:'+body.input.familyId) : null
    if(f?.revokeOperation)await this.notifyResult({operationId:f.revokeOperation})
    return Response.json(await this.notifyResult(agentResult(result)))
   }
   catch (error) { return Response.json({ error: error instanceof HostError ? error.message : 'metadata unavailable', ...(error instanceof HostError ? error.details : {}) }, { status: error instanceof HostError ? error.status : 503 }) }
  }
  if (op === '/human') {
   try { const result=this.ctx.storage.transactionSync(() => humanOperation(this.sync(), body.operation, body.input));if(result?.operationId)result.denialCommitObservedAt=Date.now();return Response.json(await this.notifyResult(result)) }
   catch (error) { return Response.json({ error: error instanceof HostError ? error.message : 'metadata unavailable', ...(error instanceof HostError ? error.details : {}) }, { status: error instanceof HostError ? error.status : 503 }) }
  }
  if (op === '/security') {
   try { return Response.json(body.operation==='progress'?await this.notifyResult({operationId:body.input.operationId}):this.ctx.storage.transactionSync(() => securityOperation(this.sync(), body.operation, body.input))) }
   catch(error){return Response.json({error:error instanceof HostError?error.message:'security unavailable'},{status:error instanceof HostError?error.status:503})}
  }
  if (op === '/get') return Response.json(this.get(body.key))
  if (op === '/replace-asset') {
   const previous = this.ctx.storage.transactionSync(() => {
    const key = 'asset:' + body.room + ':' + body.id, old = this.get(key)
    if (!ownsAsset(body.room, body.value?.blobKey) || (old && !ownsAsset(body.room, old.blobKey))) throw new HostError(503, 'invalid asset ownership')
    this.put(key, body.value)
    return old
   })
   return Response.json({ previous })
  }
  if (op === '/put') { if (!body.key.startsWith('room:') || !this.get(body.key)) this.put(body.key, body.value); return Response.json({ ok: true }) }
  if (op === '/list') return Response.json(this.ctx.storage.sql.exec('SELECT key, value FROM metadata WHERE substr(key,1,?) = ? ORDER BY key', body.prefix.length, body.prefix).toArray().map((r: any) => ({ key: r.key, value: JSON.parse(r.value) })))
  if (op === '/revoke') {
   try {return Response.json({revoked:true,...await this.notifyResult(this.ctx.storage.transactionSync(()=>securityOperation(this.sync(),'revoke-legacy',body)))})}
   catch(error){return Response.json({error:error instanceof HostError?error.message:'security unavailable'},{status:error instanceof HostError?error.status:503})}
  }
  return new Response(null, { status: 404 })
 }
 async notifyResult(result: any) {
  if(!result?.operationId)return result
  try {
   const batch=securityOperation(this.sync(),'notify',{operationId:result.operationId})
   const results=await Promise.all(batch.rooms.map(async (room: string)=>{
    try {const response=await stub(this.env.ROOMS,room).fetch(new Request('https://room/internal/revoke',{method:'POST',body:JSON.stringify({target:batch.target})}));return response.ok}catch{return false}
   }))
   const status=this.ctx.storage.transactionSync(()=>securityOperation(this.sync(),'notified',{operationId:result.operationId,cursor:batch.cursor,more:batch.more,ok:results.every(Boolean)}))
   if(this.sync().list('security-notify-pending:',1).length)await this.ctx.storage.setAlarm(Date.now()+1000)
   return {...result,...status}
  } catch {return {...result,denied:true,streamsStopped:'unknown',notification:'unknown'}}
 }
 async alarm() {
  for(const row of this.sync().list('security-notify-pending:',16))await this.notifyResult({operationId:row.value.operationId})
  if(this.sync().list('security-notify-pending:',1).length)await this.ctx.storage.setAlarm(Date.now()+1000)
 }

}
export class CloudflareHost implements Host {
 private = true
 publicRequestUrl = true
 humanConfig?: HumanConfig
 agentPairing: boolean
 meta: RegistryMetadata
 port: number
 origin: string
 constructor(private env: Env) {
  this.agentPairing = env.JOURNEY_AGENT_PAIRING === 'true'
  this.origin = env.JOURNEY_ORIGIN
  const origin = new URL(this.origin)
  if (origin.origin !== this.origin || (origin.protocol !== 'https:' && !['localhost', '127.0.0.1'].includes(origin.hostname))) throw new Error('private origin requires HTTPS')
  validateGrants(JSON.parse(env.JOURNEY_GRANTS || 'null'))
  this.port = Number(origin.port || (origin.protocol === 'https:' ? 443 : 80))
  if (env.JOURNEY_HUMAN_CONFIG) {
   this.humanConfig = validateHumanConfig(JSON.parse(env.JOURNEY_HUMAN_CONFIG), this.origin)
   if (this.humanConfig.mode !== 'cloudflare') throw new Error('Cloudflare requires provider entry')
  }
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
  try {
   if (!await this.env.ASSETS.put(blobKey, bytes, { httpMetadata: { contentType: type } })) throw new HostError(503, 'asset upload failed')
  } catch (error) { await this.env.ASSETS.delete(blobKey).catch(() => {}); throw error }
  const { previous } = await this.meta.replaceAsset(room, id, { blobKey, contentType: type, size: bytes.length })
  if (previous && previous.blobKey !== blobKey) await this.env.ASSETS.delete(previous.blobKey)
 }
 async getAsset(room: string, id: string) {
  const key = 'asset:' + room + ':' + id
  let asset = await this.meta.get<{ blobKey: string; contentType: string }>(key)
  if (!asset || !this.env.ASSETS) throw new HostError(404, 'asset not found')
  for (let attempt = 0; ; attempt++) {
   const blob = await this.env.ASSETS.get(asset.blobKey)
   if (blob) return { data: new Uint8Array(await blob.arrayBuffer()), contentType: asset.contentType }
   const latest = await this.meta.get<{ blobKey: string; contentType: string }>(key)
   if (!latest || latest.blobKey === asset.blobKey) throw new HostError(404, 'asset not found')
   if (attempt) throw new HostError(503, 'asset changed during read')
   asset = latest
  }
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
   this.roomId=await ctx.storage.get('roomId')
   if(!this.roomId)return
   const sockets=ctx.getWebSockets()
   await Promise.all(sockets.slice(0,64).map(async(ws:any)=>{
    const a=ws.deserializeAttachment()
    if(!await this.refresh(ws,a)){this.closeSocket(ws,'authority unavailable');return}
    if(a.snapshot)this.open().handleSocketResume({sessionId:a.sessionId,socket:this.socket(ws),snapshot:a.snapshot})
    else this.closeSocket(ws,'reconnect required',1012)
   }))
   for(const ws of sockets.slice(64))this.closeSocket(ws,'reconnect required',1012)
   await this.scheduleAlarm()
  })
 }
 open() {
  if(!this.room)this.room=new TLSocketRoom({
   storage:new SQLiteSyncStorage({sql:new DurableObjectSqliteSyncWrapper(this.ctx.storage)}),clientTimeout:Infinity,
   onSessionSnapshot:(sessionId,snapshot)=>{
    for(const ws of this.ctx.getWebSockets()){const a=ws.deserializeAttachment();if(a.sessionId===sessionId)ws.serializeAttachment({...a,snapshot})}
   },
  })
  return this.room
 }
 closeSocket(ws: any, reason: string, code=1008) {
  const a=ws.deserializeAttachment()
  if(a){a.invalidated=true;ws.serializeAttachment(a)}
  ws.close(code,reason)
  if(a)this.room?.handleSocketClose(a.sessionId)
 }
 socket(ws: any) {
  return {get readyState(){return ws.readyState},close:(code?:number,reason?:string)=>ws.close(code,reason),send:(data:string)=>{
   if(!canSend(ws.deserializeAttachment())){this.closeSocket(ws,'stream lease expired');return}
   ws.send(data)
  }}
 }
 async refresh(ws:any,a:any) {
  if(!a || a.room!==this.roomId || a.invalidated)return false
  try {
   await renewLease(this.meta,a);await this.meta.security('stream-register',a)
   const latest=ws.deserializeAttachment()
   if(!latest || latest.streamId!==a.streamId || latest.invalidated || ws.readyState!==1){if(ws.readyState===3)await this.meta.security('stream-close',{streamId:a.streamId});return false}
   ws.serializeAttachment({...latest,leaseUntil:a.leaseUntil});return true
  }catch{return false}
 }
 async scheduleAlarm() {
  const deadlines=this.ctx.getWebSockets().map((ws:any)=>ws.deserializeAttachment()).filter((a:any)=>a&&!a.invalidated).map((a:any)=>Math.min(a.leaseUntil,a.admission.expiresAt))
  if(!deadlines.length){await this.ctx.storage.deleteAlarm();return}
  const deadline=Math.max(Date.now()+1,Math.min(...deadlines)),saved=await this.ctx.storage.getAlarm()
  if(!saved || deadline<saved)await this.ctx.storage.setAlarm(deadline)
 }
 async register(id:string) {
  this.roomId=id;await this.ctx.storage.put('roomId',id);this.open();await this.meta.put('room:'+id,{createdAt:Date.now()})
 }
 async fetch(req:Request) {
  try {
   const url=new URL(req.url)
   if(url.pathname==='/internal/revoke') {
    const body=await req.json() as any,target=body.target||{credentialId:body.credentialId}
    for(const ws of this.ctx.getWebSockets()){const a=ws.deserializeAttachment();if(a?.admission&&matchesTarget(a.admission,a.room,target))this.closeSocket(ws,'authority revoked')}
    await this.scheduleAlarm()
    return Response.json({notified:true,streamsStopped:'stopping'})
   }
   if(url.pathname==='/internal/active')return Response.json({sessions:this.ctx.getWebSockets().length,clock:this.open().getCurrentDocumentClock()})
   if(url.pathname==='/internal/doc') {
    const {room,method,prepared}=await req.json() as any,valid=prepareDoc(method,prepared)
    await this.register(room);return Response.json(await operate(this.open(),room,method,valid))
   }
   if(url.pathname.startsWith('/connect/')) {
    const host=new CloudflareHost(this.env),{room,admission}=await admit(host,req.headers,decodeURIComponent(url.pathname.slice(9)),false,true,url)
    if(req.headers.get('upgrade')?.toLowerCase()!=='websocket')return new Response(null,{status:426})
    await this.register(room)
    const lease=await renewLease(this.meta,{streamId:crypto.randomUUID(),room,admission:admission!,leaseUntil:0})
    const pair=new (globalThis as any).WebSocketPair(),client=pair[0],server=pair[1],sessionId=url.searchParams.get('sessionId')||''
    this.ctx.acceptWebSocket(server);server.serializeAttachment({...lease,leaseUntil:0,sessionId})
    if(!await this.refresh(server,server.deserializeAttachment())){this.closeSocket(server,'authority denied');await this.meta.security('stream-close',{streamId:lease.streamId,abortedBeforeUpgrade:true});await this.scheduleAlarm();return Response.json({error:'authority_denied'},{status:403})}
    this.open().handleSocketConnect({sessionId,socket:this.socket(server)})
    await this.scheduleAlarm()
    return new Response(null,{status:101,webSocket:client} as any)
   }
   return new Response(null,{status:404})
  } catch(e){return Response.json({error:e instanceof HostError?e.message:'room unavailable'},{status:e instanceof HostError?e.status:503})}
 }
 async webSocketMessage(ws:any,message:string|ArrayBuffer) {
  const a=ws.deserializeAttachment()
  if(!await this.refresh(ws,a)){this.closeSocket(ws,'authority unavailable');return}
  try {
   const batch=typeof message==='string'?JSON.parse(message):null
   if(batch?.type==='push')await audited(new CloudflareHost(this.env),a.admission,a.room,'socket:push',async()=>{this.open().handleSocketMessage(a.sessionId,message)},undefined,'admitted')
   else this.open().handleSocketMessage(a.sessionId,message)
  } catch {this.closeSocket(ws,'mutation outcome unknown',1011);return}
  const snapshot=this.open().getSessionSnapshot(a.sessionId)
  if(snapshot)ws.serializeAttachment({...ws.deserializeAttachment(),snapshot})
  await this.scheduleAlarm()
 }
 async webSocketClose(ws:any,code:number,reason:string) {
  const a=ws.deserializeAttachment()
  try {if(ws.readyState<3){if(code===1005||code===1006)ws.close();else ws.close(code,reason)};this.room?.handleSocketClose(a.sessionId)}
  finally {await this.meta.security('stream-close',{streamId:a.streamId});await this.scheduleAlarm()}
 }
 async webSocketError(ws:any) {this.closeSocket(ws,'socket error');await this.scheduleAlarm()}
 async alarm() {
  const due=this.ctx.getWebSockets().filter((ws:any)=>{const a=ws.deserializeAttachment();return !a || a.invalidated || a.leaseUntil<=Date.now()})
  await Promise.all(due.slice(0,64).map(async(ws:any)=>{if(!await this.refresh(ws,ws.deserializeAttachment()))this.closeSocket(ws,'authority unavailable')}))
  for(const ws of due.slice(64))this.closeSocket(ws,'reconnect required',1012)
  await this.scheduleAlarm()
 }
}

export default {
 async fetch(req: Request, env: Env) {
  let host: CloudflareHost
  try { host = new CloudflareHost(env) } catch { return Response.json({ error: 'private host not configured' }, { status: 503 }) }
  const url = new URL(req.url)
  if (url.pathname.startsWith('/connect/')) {
   try {
    const { room } = await admit(host, req.headers, decodeURIComponent(url.pathname.slice(9)), false, true, url)
    return await stub(env.ROOMS, room).fetch(req)
   } catch (e) { return Response.json({ error: e instanceof HostError ? e.message : 'room unavailable' }, { status: e instanceof HostError ? e.status : 503 }) }
  }
  if (['/', '/index.html'].includes(url.pathname) || url.pathname.startsWith('/assets/')) return env.STATIC ? env.STATIC.fetch(req) : new Response('canvas build unavailable', { status: 404 })
  return handle(host, req)
 },
}

export { exportRoom, restoreRoom } from './recovery'
