import { canonicalRoom, HostError } from './core'
import { HUMAN_BOUND, type HumanConfig, type SyncMetadata } from './human-store'
import { reserveAudit, securityOperation } from './security-store'

export type EnrollmentTarget = { backendId: string; origin: string; issuer: string; audience: string; email: string; memberId: string; label: string; rooms: Array<{roomId:string;expiresAt:number}> }
export type EnrollmentBinding = { accountId:string; applicationId:string; providerId:string; backendId:string; origin:string; issuer:string; audience:string; rooms:string[] }
export type EnrollmentProof = { accountId:string; applicationId:string; providerId:string; backendId:string; origin:string; issuer:string; audience:string; email:string; subject:string; lookupId:string; signInAt:number; observedAt:number; classification:'authenticated-last-seen-onetimepin' }
export const identityKey = (issuer:string,subject:string) => 'human-identity:'+JSON.stringify([issuer,subject])
const fail = (category:string,status=400):never => { throw new HostError(status,category,{category}) }
const id = (v:unknown) => typeof v==='string' && /^[a-zA-Z0-9_-]{1,128}$/.test(v)
const clean = (v:unknown,max=256) => typeof v==='string' && v.length>0 && v.length<=max && !/[\x00-\x1f\x7f]/.test(v)
const closed = (v:any,keys:string[]) => v && typeof v==='object' && !Array.isArray(v) && Object.keys(v).length===keys.length && keys.every(k=>Object.hasOwn(v,k))
export function validateTarget(v:any,now=Date.now()):EnrollmentTarget {
 if(!closed(v,['backendId','origin','issuer','audience','email','memberId','label','rooms']) || !id(v.backendId) || !id(v.memberId) || !clean(v.label,128) || v.label.trim()!==v.label || !clean(v.email,254) || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.email) || !clean(v.audience) || !clean(v.issuer) || !clean(v.origin))fail('invalid_target')
 try {if(new URL(v.origin).origin!==v.origin || new URL(v.issuer).origin!==v.issuer || new URL(v.issuer).protocol!=='https:')fail('invalid_target')}catch{fail('invalid_target')}
 if(!Array.isArray(v.rooms) || !v.rooms.length || v.rooms.length>64)fail('invalid_rooms')
 const seen=new Set()
 for(const r of v.rooms){if(!closed(r,['roomId','expiresAt']) || !clean(r.roomId,128) || canonicalRoom(r.roomId)!==r.roomId || r.roomId.includes('*') || seen.has(r.roomId) || !Number.isSafeInteger(r.expiresAt) || r.expiresAt<=now)fail('invalid_rooms');seen.add(r.roomId)}
 return v
}
export const scopeText = (v:EnrollmentTarget) => JSON.stringify({...v,rooms:[...v.rooms].sort((a,b)=>a.roomId.localeCompare(b.roomId))})
function history(store:SyncMetadata,prefix:string) {
 const all:Array<{key:string;value:any}>=[];let after=''
 for(;;){const page=store.list(prefix,128,after);all.push(...page);if(all.length>4096)fail('incomplete_history_scan',409);if(page.length<128)return all;const next=page.at(-1)!.key;if(next<=after)fail('incomplete_history_scan',409);after=next}
}
function binding(config:HumanConfig,b:EnrollmentBinding,target:EnrollmentTarget) {
 if(config.mode!=='cloudflare')fail('remote_enrollment_unsupported',403)
 for(const key of ['backendId','origin','issuer','audience'] as const)if(target[key]!==config[key] || target[key]!==b[key])fail('backend_binding_denied',403)
 if(!clean(b.accountId) || !clean(b.applicationId) || !clean(b.providerId) || !Array.isArray(b.rooms) || b.rooms.some(r=>!clean(r)||canonicalRoom(r)!==r))fail('operator_configuration_denied',403)
 if(target.rooms.some(r=>!b.rooms.includes(r.roomId)))fail('operator_scope_denied',403)
}
function state(store:SyncMetadata,t:EnrollmentTarget,p?:EnrollmentProof) {
 const indexes=history(store,'human-identity:')
 const members=history(store,'member:'),rows=history(store,'member-room:'+t.memberId+':')
 for(const row of members){const m=row.value;if(!closed(m,['id','issuer','subject','label','role','enabled','generation']) || row.key!=='member:'+m.id || !id(m.id) || !clean(m.issuer) || !clean(m.subject) || !['member','operator'].includes(m.role) || typeof m.enabled!=='boolean' || !Number.isSafeInteger(m.generation))fail('unknown_member_schema',409)}
 const m=store.get<any>('member:'+t.memberId)
 const subject=p?.subject || m?.subject
 if(!subject)return {result:rows.length?'conflict':'absent',category:rows.length?'retained_room_history':'absent'}
 const matches=members.filter(r=>r.value.issuer===t.issuer && r.value.subject===subject)
 const index=store.get<string>(identityKey(t.issuer,subject))
 if(indexes.some(r=>r.value===t.memberId && r.key!==identityKey(t.issuer,subject)))return {result:'conflict',category:'identity_index_inconsistent'}
 if(!m && !matches.length && !index && !rows.length)return {result:'absent',category:'absent'}
 if(matches.length!==1 || matches[0].value.id!==t.memberId || index!==t.memberId || !m || m.issuer!==t.issuer || m.subject!==subject || m.label!==t.label || m.role!=='member' || !m.enabled || m.generation!==1 || rows.length!==t.rooms.length)return {result:'conflict',category:'retained_or_different_member'}
 for(const r of rows){const expected=t.rooms.find(g=>r.key==='member-room:'+t.memberId+':'+g.roomId),v=r.value;if(!expected || !closed(v,['memberId','roomId','expiresAt','revoked','generation']) || v.memberId!==t.memberId || v.roomId!==expected.roomId || v.expiresAt!==expected.expiresAt || v.revoked!==false || v.generation!==1)return {result:'conflict',category:'retained_or_different_grants'}}
 return {result:'matching-current-state',category:'exact_current_state',member:{id:m.id,issuer:m.issuer,subject:m.subject,label:m.label,role:m.role,enabled:m.enabled,generation:m.generation},rooms:rows.map(r=>r.value)}
}
export function enrollmentOperation(store:SyncMetadata,op:string,input:any,b:EnrollmentBinding|undefined,enabled:boolean,now=Date.now()):any {
 if(store.get<any>('human-schema:v1')?.version!==1)fail('unknown_member_schema',409)
 if(!enabled || !b)fail('member_enrollment_disabled',403)
 const config=store.get<HumanConfig>('human-config:v1');if(!config)fail('human_entry_unconfigured',503)
 if(!['enroll','inspect'].includes(op))fail('unsupported_member_operation')
 const t=validateTarget(input?.target,now);binding(config!,b!,t)
 const p:EnrollmentProof=input.proof
 if(!p || p.classification!=='authenticated-last-seen-onetimepin' || !clean(p.lookupId) || !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(p.subject) || p.email!==t.email || !Number.isFinite(p.signInAt) || p.signInAt>now || p.signInAt+HUMAN_BOUND<=now || !Number.isFinite(p.observedAt) || p.observedAt<p.signInAt || p.observedAt>now)fail('invalid_identity_proof',403)
 for(const key of ['accountId','applicationId','providerId','backendId','origin','issuer','audience'] as const)if(p[key]!==b![key])fail('identity_binding_denied',403)
 for(const r of t.rooms)if(!store.get('room:'+r.roomId))fail('unknown_room',404)
 const current=state(store,t,p)
 if(op==='inspect')return {...current,receiptAvailable:!!(id(input.operationId)&&store.get('security-receipt:'+input.operationId))}
 if(!id(input.operationId))fail('invalid_operation_id')
 if(store.get('security-receipt:'+input.operationId))return {result:'refused',category:'operation_already_reserved'}
 if(current.result==='conflict')return current
 if(current.result==='matching-current-state')return {...current,result:'no-op'}
 const operationId=reserveAudit(store,'enroll-member',{},null,now,input.operationId)
 store.put('member:'+t.memberId,{id:t.memberId,issuer:t.issuer,subject:p.subject,label:t.label,role:'member',enabled:true,generation:1})
 store.put(identityKey(t.issuer,p.subject),t.memberId)
 for(const r of t.rooms)store.put('member-room:'+t.memberId+':'+r.roomId,{memberId:t.memberId,roomId:r.roomId,expiresAt:r.expiresAt,revoked:false,generation:1})
 securityOperation(store,'finalize',{operationId,outcome:'committed'},now)
 return {...state(store,t,p),result:'created',auditReference:operationId,committedAt:now}
}
