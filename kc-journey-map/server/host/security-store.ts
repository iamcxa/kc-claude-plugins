import { HostError } from './core'
import type { SyncMetadata } from './human-store'
import type { Admission, Grant } from './policy'
import type { StreamLease } from './stream-lease'
export type RevokeTarget = { familyId?: string; memberId?: string; humanSessionDigest?: string; credentialId?: string; roomId?: string }
const fail = (category: string): never => { throw new HostError(409, category, { category }) }
const targetKey = (t: RevokeTarget) => t.familyId ? 'family:'+t.familyId : t.humanSessionDigest ? 'browser:'+t.humanSessionDigest : t.credentialId ? 'credential:'+t.credentialId : 'member:'+t.memberId
const indexPrefix = (t: RevokeTarget) => 'security-stream-index:'+targetKey(t)+(t.roomId?':room:'+t.roomId:'')+':'
export function matchesTarget(admission: Admission, room: string, t: RevokeTarget) {
 return (!t.roomId || t.roomId===room) && (t.familyId ? admission.familyId===t.familyId : t.humanSessionDigest ? admission.humanSessionDigest===t.humanSessionDigest : t.credentialId ? admission.credentialId===t.credentialId : admission.actorType!=='legacy' && admission.principalId===t.memberId)
}
function indexes(lease: StreamLease) {
 const a=lease.admission, targets: RevokeTarget[]=[{credentialId:a.credentialId}]
 if(a.actorType!=='legacy')targets.push({memberId:a.principalId})
 if(a.familyId)targets.push({familyId:a.familyId})
 if(a.humanSessionDigest)targets.push({humanSessionDigest:a.humanSessionDigest})
 return targets.flatMap(t=>[indexPrefix(t)+lease.streamId,indexPrefix({...t,roomId:lease.room})+lease.streamId])
}
export function reserveAudit(store: SyncMetadata, action: string, actor: Partial<Admission>, room: string | null, now=Date.now(), operationId=crypto.randomUUID()) {
 if(store.get('security-receipt:'+operationId))fail('operation_already_reserved')
 store.put('security-receipt:'+operationId,{operationId,action,actorType:actor.actorType||'operator',memberId:actor.principalId||null,familyId:actor.familyId||null,credentialId:actor.credentialId||null,room,serverTime:now,outcome:'admitted',final:false})
 return operationId
}
export function denial(store: SyncMetadata, target: RevokeTarget, action: string, actor: Partial<Admission>={}, now=Date.now()) {
 const operationId=reserveAudit(store,action,actor,target.roomId||null,now)
 store.put('security-denial:'+operationId,{operationId,target,deniedAt:now})
 store.put('security-operation:'+operationId,{operationId,target,deniedAt:now,notification:'pending',cursor:''})
 store.put('security-notify-pending:'+operationId,{operationId})
 store.put('security-receipt:'+operationId,{...store.get<any>('security-receipt:'+operationId),outcome:'committed',final:true})
 return {operationId,denied:true,deniedAt:now,streamsStopped:'stopping'}
}
function operationStatus(store: SyncMetadata, operationId: string, now: number) {
 const op=store.get<any>('security-operation:'+operationId)
 if(!op)fail('unknown_security_operation')
 const rows=store.list(indexPrefix(op.target),65).filter(row=>matchesTarget(row.value.admission,row.value.room,op.target))
 const streamsStopped=rows.length ? rows.some(row=>row.value.leaseUntil<=now) ? 'unknown' : 'stopping' : 'stopped'
 return {...op,denied:true,streamsStopped,closeConfirmed:streamsStopped==='stopped'}
}
export function securityOperation(store: SyncMetadata, operation: string, input: any, now=Date.now()): any {
 if(operation==='stream-register') {
  const lease=input as StreamLease
  if(!lease.streamId || !lease.room || !lease.admission || !Number.isFinite(lease.leaseUntil) || lease.leaseUntil>now+30_000 || lease.leaseUntil>lease.admission.expiresAt || lease.leaseUntil<=now)fail('invalid_stream_lease')
  const a=lease.admission
  if(a.actorType==='human') {
   const session=store.get<any>('browser-session:'+a.humanSessionDigest), member=store.get<any>('member:'+a.principalId), room=store.get<any>('member-room:'+a.principalId+':'+lease.room)
   if(!session || session.revoked || session.expiresAt<=now || session.humanRevalidateBy<=now || !member?.enabled || member.generation!==session.generation || !room || room.revoked || room.expiresAt<=now)fail('stream_denied')
  } else if(a.actorType==='agent') {
   const f=store.get<any>('agent-family:'+a.familyId), m=store.get<any>('member:'+a.principalId), policy=store.get<any>('agent-policy:v1'), config=store.get<any>('human-config:v1')
   if(!f || f.revoked || !m?.enabled || m.generation!==f.memberGeneration || !policy?.enabled || policy.generation!==f.policyGeneration || config?.backendId!==f.backendId)fail('stream_denied')
   for(const [room,generation] of Object.entries(f.roomGenerations)){const r=store.get<any>('member-room:'+a.principalId+':'+room);if(!r || r.revoked || r.expiresAt<=now || r.generation!==generation)fail('stream_denied')}
  } else {const g=store.get<Grant>('grant:'+a.credentialId);if(!g || g.revoked || g.expiresAt<=now || !g.rooms.includes(lease.room))fail('stream_denied')}
  const saved={streamId:lease.streamId,room:lease.room,admission:lease.admission,leaseUntil:lease.leaseUntil}
  store.put('security-stream:'+lease.streamId,saved)
  for(const key of indexes(lease))store.put(key,saved)
  return {registered:true}
 }
 if(operation==='stream-close') {
  const lease=store.get<StreamLease>('security-stream:'+input.streamId)
  if(lease){for(const key of indexes(lease))store.delete(key);store.delete('security-stream:'+input.streamId)}
  return {closed:true}
 }
 if(operation==='status')return operationStatus(store,input.operationId,now)
 if(operation==='notify') {
  const op=store.get<any>('security-operation:'+input.operationId)
  if(!op)fail('unknown_security_operation')
  const rows=store.list(indexPrefix(op.target),64,op.cursor||undefined)
  const rooms=[...new Set(rows.filter(row=>matchesTarget(row.value.admission,row.value.room,op.target)).map(row=>row.value.room))]
  return {target:op.target,rooms,cursor:rows.at(-1)?.key||op.cursor,more:rows.length===64}
 }
 if(operation==='notified') {
  const op=store.get<any>('security-operation:'+input.operationId)
  if(!op)fail('unknown_security_operation')
  const attempts=(op.attempts||0)+1
  store.put('security-operation:'+input.operationId,{...op,cursor:input.ok?input.cursor:op.cursor,attempts,notification:input.ok?'sent':'unknown'})
  if((input.ok&&!input.more)||attempts>=3)store.delete('security-notify-pending:'+input.operationId)
  return operationStatus(store,input.operationId,now)
 }
 if(operation==='reserve')return {operationId:reserveAudit(store,input.action,input.actor||{},input.room||null,now,input.operationId)}
 if(operation==='finalize') {
  const r=store.get<any>('security-receipt:'+input.operationId)
  if(!r || r.final)fail('operation_already_finalized')
  store.put('security-receipt:'+input.operationId,{...r,outcome:input.outcome,final:true})
  return {recorded:true}
 }
 if(operation==='prune') {
  let removed=0;const cursors:Record<string,string>={}
  for(const prefix of ['security-receipt:','human-receipt:','agent-receipt:']) {
   const rows=store.list(prefix,128,input.cursors?.[prefix])
   for(const row of rows)if((prefix!=='security-receipt:' || row.value.final) && row.value.serverTime<now-30*24*3600_000){store.delete(row.key);removed++}
   if(rows.length===128)cursors[prefix]=rows.at(-1)!.key
  }
  return {removed,cursors}
 }
 if(operation==='cutover-plan') {
  const grant=store.get<Grant>('grant:'+input.credentialId)
  if(!grant || grant.revoked || grant.expiresAt<=now || input.synthetic!==true || input.inventoryComplete!==true || !Array.isArray(input.consumers) || !input.consumers.length || input.consumers.length>64 || new Set(input.consumers.map((c:any)=>c.id)).size!==input.consumers.length)fail('invalid_cutover_inventory')
  if(store.get('security-cutover:'+input.credentialId))fail('cutover_inventory_immutable')
  for(const c of input.consumers)if(!c.id || !c.familyId || !Array.isArray(c.rooms) || !c.rooms.length || c.rooms.some((room:string)=>!grant!.rooms.includes(room)))fail('invalid_cutover_consumer')
  const plan={credentialId:grant!.credentialId,originalExpiry:grant!.expiresAt,synthetic:true,consumers:input.consumers.map((c:any)=>({id:c.id,familyId:c.familyId,rooms:c.rooms,verified:false}))}
  const operationId=reserveAudit(store,'cutover-plan',{},null,now)
  store.put('security-cutover:'+grant!.credentialId,plan)
  store.put('security-receipt:'+operationId,{...store.get<any>('security-receipt:'+operationId),outcome:'committed',final:true})
  return plan
 }
 if(operation==='cutover-verified') {
  const plan=store.get<any>('security-cutover:'+input.credentialId),grant=store.get<Grant>('grant:'+input.credentialId)
  if(!plan || !grant || grant.revoked || grant.expiresAt<=now || grant.expiresAt!==plan.originalExpiry)fail('cutover_legacy_expired_or_changed')
  const c=plan.consumers.find((c:any)=>c.id===input.consumerId)
  if(!c || c.familyId!==input.familyId || JSON.stringify(c.rooms)!==JSON.stringify(input.rooms))fail('cutover_consumer_denied')
  const operationId=reserveAudit(store,'cutover-verified',{},null,now)
  c.verified=true;c.verifiedAt=now
  store.put('security-cutover:'+input.credentialId,plan)
  store.put('security-receipt:'+operationId,{...store.get<any>('security-receipt:'+operationId),outcome:'committed',final:true})
  return {verified:true,consumerId:c.id}
 }
 if(operation==='restore-security') {
  if(!Array.isArray(input.records) || input.format!=='journey-security-1')fail('invalid_security_archive')
  const currentConfig=store.get<any>('human-config:v1'),oldConfig=input.records.find((r:any)=>r.key==='human-config:v1')?.value
  if(oldConfig && (!currentConfig || currentConfig.backendId===oldConfig.backendId))fail('recovery_requires_fresh_backend_and_member_ids')
  const operationId=reserveAudit(store,'restore-security',{},null,now)
  for(const row of input.records) {
   const k=row.key,v=row.value
   if(typeof k!=='string' || !/^(grant:|member:|member-room:|human-|browser-session:|agent-|security-)/.test(k))fail('invalid_security_archive')
   if(k==='human-config:v1' || k==='agent-policy:v1' || k.startsWith('human-identity:') || k.startsWith('security-stream') || k.startsWith('security-notify-pending:'))continue
   const old=store.get<any>(k)
   if(k.startsWith('member:')) {
    if(currentConfig?.members.some((m:any)=>m.id===v.id))fail('recovery_requires_fresh_backend_and_member_ids')
    store.put(k,{...v,enabled:false,generation:Math.max(v.generation||0,old?.generation||0)+1})
   } else if(k.startsWith('member-room:'))store.put(k,{...v,revoked:true,generation:Math.max(v.generation||0,old?.generation||0)+1})
   else if(k.startsWith('grant:') || k.startsWith('agent-family:') || k.startsWith('browser-session:'))store.put(k,{...v,...old,revoked:true})
   else if(k.startsWith('agent-request:'))store.put(k,{...v,...old,status:'cancelled'})
   else if(!old)store.put(k,v)
  }
  store.put('security-required:v1',{version:1,recoveredAt:now})
  store.put('security-receipt:'+operationId,{...store.get<any>('security-receipt:'+operationId),outcome:'committed',final:true})
  return {restored:true,archivedAuthority:'disabled',freshIdsRequired:true}
 }
 if(operation==='revoke-legacy') {
  const grant=store.get<Grant>('grant:'+input.credentialId)
  if(!grant)fail('unknown_credential')
  const plan=store.get<any>('security-cutover:'+input.credentialId)
  if(plan)for(const c of plan.consumers) {
   const f=store.get<any>('agent-family:'+c.familyId),m=f?store.get<any>('member:'+f.memberId):null,policy=store.get<any>('agent-policy:v1'),config=store.get<any>('human-config:v1')
   if(grant!.expiresAt!==plan.originalExpiry || !c.verified || !f || f.revoked || !m?.enabled || m.generation!==f.memberGeneration || !policy?.enabled || policy.generation!==f.policyGeneration || config?.backendId!==f.backendId)fail('cutover_consumers_unverified')
   for(const [room,generation]of Object.entries(f.roomGenerations)){const r=store.get<any>('member-room:'+f.memberId+':'+room);if(!r || r.revoked || r.expiresAt<=now || r.generation!==generation)fail('cutover_consumers_unverified')}
  }
  if(grant!.revoked)return grant!.revokeOperation ? operationStatus(store,grant!.revokeOperation,now):{revoked:true,streamsStopped:'unknown'}
  const result=denial(store,{credentialId:grant!.credentialId},'revoke-legacy',{},now)
  store.put('grant:'+grant!.credentialId,{...grant,revoked:true,revokeOperation:result.operationId})
  return {...result,revoked:true}
 }
 return fail('unknown_security_operation')
}
