import { canonicalRoom, HostError } from './core'
import { denial } from './security-store'
import { HUMAN_BOUND, type HumanConfig, type HumanSession, type Member, type MemberRoom, type SyncMetadata } from './human-store'
export type AgentScope = { roomId: string; records: 'full-replacement'; assets: boolean; saveDirectory: string | null; repositories: string[] }
type Binding = { memberId: string; memberGeneration: number; roomGenerations: Record<string, number>; policyGeneration: number; backendId: string; scopes: AgentScope[] }
export type AgentFamily = Binding & { id: string; installationId: string; label: string; createdAt: number; revoked: boolean; revokeOperation?: string; reason?: string; refresh: { generation: number; digest: string } }
type PairRequest = Binding & { id: string; installationId: string; label: string; verifierDigest: string; codeDigest: string; expiresAt: number; status: string; familyId?: string }
const deny = (status: number, category: string): never => { throw new HostError(status, category, { category }) }
const id = (v: unknown) => typeof v === 'string' && /^[a-zA-Z0-9_-]{1,128}$/.test(v)
const hash = (v: unknown) => typeof v === 'string' && /^[a-f0-9]{64}$/.test(v)
const same = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b)
export function bootstrapAgent(store: SyncMetadata, enabled: boolean, policy: unknown) {
 const old = store.get<any>('agent-policy:v1')
 if (!old || old.enabled !== enabled || !same(old.policy, policy)) store.put('agent-policy:v1', { enabled, policy, generation: (old?.generation || 0) + 1 })
}
function receipt(store: SyncMetadata, operation: string, memberId: string | null, familyId: string | null, requestId: string | null, now: number) {
 for (const row of store.list('agent-receipt:', 64)) if (row.value.serverTime < now - 30*24*3600_000) store.delete(row.key)
 const eventId = crypto.randomUUID()
 const label=familyId?store.get<AgentFamily>('agent-family:'+familyId)?.label:requestId?store.get<PairRequest>('agent-request:'+requestId)?.label:null
 store.put('agent-receipt:'+String(now).padStart(16,'0')+':'+eventId, { eventId, operation, memberId, familyId, requestId, installationLabel:label||null, room:null, actorType: ['approve','deny','revoke'].includes(operation) ? 'human' : 'agent', outcome: 'committed', serverTime: now })
}
function rate(store: SyncMetadata, key: string, maximum: number, window: number, now: number) {
 const saved = store.get<any>('agent-rate:'+key), count = saved && saved.until > now ? saved.count+1 : 1
 store.put('agent-rate:'+key, { count, until: saved && saved.until > now ? saved.until : now+window })
 if (count > maximum) deny(429,'agent_rate_limited')
}
function binding(store: SyncMetadata, memberId: string, rooms: string[], scopes: (r: string) => AgentScope, now: number): Binding {
 const config = store.get<HumanConfig>('human-config:v1'), m = store.get<Member>('member:'+memberId), policy = store.get<any>('agent-policy:v1')
 if (!config || !m?.enabled || !policy?.enabled) deny(403,'authority_denied')
 const roomGenerations: Record<string,number> = {}
 for (const room of rooms) {
  const r=store.get<MemberRoom>('member-room:'+memberId+':'+room)
  if (!r || r.revoked || r.expiresAt <= now || !store.get('room:'+room)) deny(403,'room_denied')
  roomGenerations[room]=r!.generation
 }
 return { memberId, memberGeneration:m!.generation, roomGenerations, policyGeneration:policy.generation, backendId:config!.backendId, scopes:rooms.map(scopes) }
}
function current(store: SyncMetadata, saved: Binding, scopes: (r: string) => AgentScope, now: number) {
 const fresh=binding(store,saved.memberId,saved.scopes.map(s=>s.roomId),scopes,now)
 if (fresh.backendId !== saved.backendId || fresh.memberGeneration !== saved.memberGeneration || fresh.policyGeneration !== saved.policyGeneration || !same(fresh.roomGenerations,saved.roomGenerations)) deny(403,'authority_denied')
 if (!same(fresh.scopes,saved.scopes)) deny(403,'scope_changed')
}
function human(store: SyncMetadata, input: any, now: number) {
 const s=store.get<HumanSession>('browser-session:'+input.sessionDigest), c=store.get<HumanConfig>('human-config:v1')
 if (!s || s.actorType !== 'human' || s.revoked || s.expiresAt <= now || !Number.isFinite(s.humanRevalidateBy) || s.humanRevalidateBy <= now || s.verifiedHumanSignInAt > now || s.humanRevalidateBy > s.verifiedHumanSignInAt+HUMAN_BOUND || !c || s.backendId !== c.backendId) deny(403,'verified_human_required')
 if (s!.csrfDigest !== input.csrfDigest) deny(403,'csrf_denied')
 if (input.memberId !== s!.memberId || input.backendId !== s!.backendId || input.signInAt !== s!.verifiedHumanSignInAt) deny(403,'human_context_denied')
 const m=store.get<Member>('member:'+s!.memberId), r=store.get<MemberRoom>('member-room:'+s!.memberId+':'+input.originalRoom)
 if (!m?.enabled || m.generation !== s!.generation) deny(403,'authority_denied')
 if (!r || r.revoked || r.expiresAt <= now || !store.get('room:'+input.originalRoom)) deny(403,'human_context_denied')
 return m!
}
function revoke(store: SyncMetadata, f: AgentFamily, reason: string, now: number, requestId: string | null = null) {
 if (!f.revoked) {
  const result=denial(store,{familyId:f.id},reason,{actorType:reason==='revoke'?'human':'agent',principalId:f.memberId,familyId:f.id},now)
  store.put('agent-family:'+f.id,{...f,revoked:true,reason,revokeOperation:result.operationId});receipt(store,reason,f.memberId,f.id,requestId,now)
  return {revoked:true,familyId:f.id,...result}
 }
 return {revoked:true,familyId:f.id,operationId:f.revokeOperation,streamsStopped:'unknown'}
}
function publicFamily(f: AgentFamily) { const { refresh, ...rest }=f; return rest }
function publicRequest(r: PairRequest) { const { verifierDigest,codeDigest,...rest }=r; return rest }
function access(store: SyncMetadata, f: AgentFamily, input: any, now: number) {
 const expiresAt=now+900_000
 store.put('agent-access:'+input.accessId,{ credentialId:input.accessId,familyId:f.id,secretDigest:input.accessDigest,expiresAt })
 return { family:publicFamily(f), generation:f.refresh.generation, credentialId:input.accessId, expiresAt }
}
function material(store: SyncMetadata, input: any) {
 if (!id(input.accessId) || !input.accessId.startsWith('agt_') || !hash(input.accessDigest) || store.get('agent-access:'+input.accessId) || store.get('grant:'+input.accessId)) deny(400,'invalid_access_material')
}
export function agentOperation(store: SyncMetadata, operation: string, input: any, scope: (room: string) => AgentScope, now = Date.now()): any {
 const policy=store.get<any>('agent-policy:v1')
 // Reconciliation accepts only existing proof and remains available while disabled.
 if (!policy?.enabled && !['cancel','repair'].includes(operation)) deny(503,'agent_pairing_disabled')
 if (operation === 'create') {
  rate(store,'issue',20,60_000,now)
  if (!id(input.memberId) || !id(input.requestId) || !id(input.installationId) || !hash(input.verifierDigest) || !hash(input.codeDigest) || typeof input.label !== 'string' || !input.label.trim() || input.label.length>120 || !Array.isArray(input.rooms) || !input.rooms.length || input.rooms.length>32 || new Set(input.rooms).size !== input.rooms.length || input.rooms.some((r: any)=>typeof r !== 'string' || !r || canonicalRoom(r)!==r)) deny(400,'invalid_pairing_request')
  rate(store,'issue:'+input.memberId,5,60_000,now)
  if (store.get('agent-request:'+input.requestId) || store.get('agent-code:'+input.codeDigest)) deny(409,'request_collision')
  const bound=binding(store,input.memberId,[...input.rooms].sort(),scope,now)
  const r: PairRequest={ ...bound,id:input.requestId,installationId:input.installationId,label:input.label,verifierDigest:input.verifierDigest,codeDigest:input.codeDigest,expiresAt:now+300_000,status:'pending' }
  store.put('agent-request:'+r.id,r); store.put('agent-code:'+r.codeDigest,r.id); receipt(store,'create',r.memberId,null,r.id,now)
  return publicRequest(r)
 }
 if (['inspect','approve','deny','list','revoke'].includes(operation)) {
  const m=human(store,input,now)
  if (operation === 'list') return { families:store.list('agent-family:',1000).map(r=>r.value as AgentFamily).filter(f=>f.memberId===m.id).map(publicFamily) }
  if (operation === 'revoke') {
   const f=store.get<AgentFamily>('agent-family:'+input.familyId)
   if (!f || f.memberId!==m.id) deny(403,'authorizer_denied')
   return revoke(store,f!,'revoke',now)
  }
  rate(store,'code-guess',30,60_000,now)
  const requestId=hash(input.codeDigest) ? store.get<string>('agent-code:'+input.codeDigest) : null
  const r=requestId ? store.get<PairRequest>('agent-request:'+requestId) : null
  if (!r || r.memberId!==m.id) deny(403,'authorizer_denied')
  if (['consumed','cancelled','denied'].includes(r!.status)) deny(410,'request_'+r!.status)
  if (r!.expiresAt<=now) deny(410,'request_expired')
  current(store,r!,scope,now)
  const context={ requestId:r!.id,sessionDigest:input.sessionDigest,csrfDigest:input.csrfDigest,memberId:input.memberId,backendId:input.backendId,signInAt:input.signInAt,originalRoom:input.originalRoom }
  if (operation==='inspect') {
   const consentId=crypto.randomUUID();store.put('agent-consent:'+consentId,context)
   return { ...publicRequest(r!),consentId,authorizer:{ id:m.id,label:m.label },origin:store.get<HumanConfig>('human-config:v1')!.origin }
  }
  if(!id(input.consentId) || !same(store.get('agent-consent:'+input.consentId),context))deny(403,'consent_context_denied')
  if (r!.status!=='pending') deny(409,'request_already_approved')
  store.delete('agent-consent:'+input.consentId)
  store.put('agent-request:'+r!.id,{ ...r,status:operation==='approve'?'approved':'denied' }); receipt(store,operation,m.id,null,r!.id,now)
  return { status:operation==='approve'?'approved':'denied',credentialsIssued:false }
 }
 if (['poll','redeem','cancel'].includes(operation)) {
  const r=store.get<PairRequest>('agent-request:'+input.requestId)
  if (!r && operation==='cancel' && id(input.requestId) && hash(input.verifierDigest)) {
   rate(store,'cancel-reservation',20,60_000,now)
   store.put('agent-request:'+input.requestId,{ id:input.requestId,status:'cancelled',verifierDigest:input.verifierDigest })
   receipt(store,'cancel',null,null,input.requestId,now)
   return { cancelled:true,revoked:true }
  }
  if (!r || r.verifierDigest!==input.verifierDigest) deny(403,'verifier_denied')
  if (operation==='cancel') {
   const f=r!.familyId ? store.get<AgentFamily>('agent-family:'+r!.familyId) : null
   if (f) revoke(store,f,'cancel',now,r!.id)
   if (r!.status!=='cancelled') { store.put('agent-request:'+r!.id,{ ...r,status:'cancelled' }); receipt(store,'cancel',r!.memberId,r!.familyId||null,r!.id,now) }
   return { cancelled:true,revoked:true }
  }
  if (['consumed','cancelled','denied'].includes(r!.status)) deny(410,'request_'+r!.status)
  if (r!.expiresAt<=now) deny(410,'request_expired')
  current(store,r!,scope,now)
  if (operation==='poll') { rate(store,'poll:'+r!.id,1,2_000,now); return { status:r!.status,expiresAt:r!.expiresAt } }
  if (r!.status!=='approved') deny(409,'approval_pending')
  if (!id(input.familyId) || !hash(input.refreshDigest) || store.get('agent-family:'+input.familyId)) deny(400,'invalid_access_material')
  material(store,input)
  const f: AgentFamily={ memberId:r!.memberId,memberGeneration:r!.memberGeneration,roomGenerations:r!.roomGenerations,policyGeneration:r!.policyGeneration,backendId:r!.backendId,scopes:r!.scopes,id:input.familyId,installationId:r!.installationId,label:r!.label,createdAt:now,revoked:false,refresh:{ generation:1,digest:input.refreshDigest } }
  store.put('agent-family:'+f.id,f); store.put('agent-request:'+r!.id,{ ...r,status:'consumed',familyId:f.id }); receipt(store,'redeem',f.memberId,f.id,r!.id,now)
  return access(store,f,input,now)
 }
 if (['rotate','repair'].includes(operation)) {
  const f=store.get<AgentFamily>('agent-family:'+input.familyId)
  if (!f || !Number.isSafeInteger(input.generation) || !hash(input.secretDigest)) deny(403,'refresh_denied')
  const matching=f!.refresh.generation===input.generation && f!.refresh.digest===input.secretDigest, spent=store.get<any>('agent-spent:'+f!.id+':'+input.generation)
  if (!matching && (!spent || spent.digest!==input.secretDigest)) deny(403,'refresh_denied')
  if (operation==='repair') return revoke(store,f!,'repair',now)
  if (!matching) { revoke(store,f!,'replay',now); deny(403,'refresh_replayed') }
  if (f!.revoked) deny(403,'family_revoked')
  current(store,f!,scope,now); material(store,input)
  if (!hash(input.nextDigest) || input.nextDigest===input.secretDigest) deny(400,'invalid_access_material')
  store.put('agent-spent:'+f!.id+':'+input.generation,{ digest:input.secretDigest })
  const next={ ...f!,refresh:{ generation:input.generation+1,digest:input.nextDigest } }
  store.put('agent-family:'+next.id,next); receipt(store,'rotate',next.memberId,next.id,null,now)
  return access(store,next,input,now)
 }
 if (operation==='admit' || operation==='current') {
  const a=store.get<any>('agent-access:'+input.credentialId)
  if (!a || a.expiresAt<=now || (operation==='admit' ? a.secretDigest!==input.secretDigest : a.familyId!==input.familyId)) deny(401,'agent_access_denied')
  const f=store.get<AgentFamily>('agent-family:'+a.familyId)
  if (!f || f.revoked) deny(403,'family_revoked')
  current(store,f!,scope,now)
  if(operation==='admit')receipt(store,'admit',f!.memberId,f!.id,null,now)
  return { credentialId:a.credentialId,familyId:f!.id,actorType:'agent',principalId:f!.memberId,rooms:f!.scopes.map(s=>s.roomId),expiresAt:Math.min(a.expiresAt,...f!.scopes.map(s=>store.get<MemberRoom>('member-room:'+f!.memberId+':'+s.roomId)!.expiresAt)),cookie:false }
 }
 return deny(400,'unknown_agent_operation')
}
export function captureAgent(action: () => any) {
 try { return { ok:true,value:action() } }
 catch (error) { if (error instanceof HostError) return { ok:false,status:error.status,category:error.message }; throw error }
}
export function agentResult(result: any) {
 if (!result.ok) deny(result.status,result.category)
 return result.value
}

