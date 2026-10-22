import { fingerprint, samePerson, validateDocuments, validateDraftContext, type Documents, type DraftContext } from '../draft-data'
export const DRAFT_DATABASE = 'journey-human-drafts'
export const DRAFT_SCHEMA_VERSION = 2
export type VersionKey = [string,string,string,string,string,number]
export type Version = { key: VersionKey; schemaVersion: 1; context: DraftContext; base: Documents | null; records: Documents; hash: string; createdAt: number }
export type VersionItem = { key: VersionKey; hash?: string }
type Head = { context: DraftContext; version: number; hash: string; selectedVersion?:number|null; lastAcknowledgedVersion?:number|null }
export type ApplyAttempt = { id: string; key: VersionKey; hash: string; context: DraftContext; reviewedHash: string; patch: {put: any[]; remove: string[]}; requestHash: string; tabId: string; leaseToken: string; state: 'prepared'|'sent'|'unknown'|'verified'; proof?: { receipt: unknown; readback: string; sync: true }; createdAt: number }
const request = <T>(r: IDBRequest<T>) => new Promise<T>((resolve,reject) => { r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error) })
const range = (prefix: IDBValidKey[]) => IDBKeyRange.bound(prefix,[...prefix,[]])
const lineage = (key: VersionKey) => key.slice(0,5)
export class HumanDrafts {
 constructor(readonly db: IDBDatabase) {}
 close() { this.db.close() }
 async transaction<T>(stores: string[], write: boolean, operation: (tx: IDBTransaction) => Promise<T> | T) {
  const tx=this.db.transaction(stores,write?'readwrite':'readonly',write?{durability:'strict'}:undefined)
  const completion=new Promise<void>((resolve,reject)=>{tx.oncomplete=()=>resolve();tx.onabort=()=>reject(tx.error || new Error('draft_transaction_aborted'));tx.onerror=()=>{}})
  if (write && tx.durability !== 'strict') {tx.abort();await completion.catch(()=>{});throw new Error('strict_durability_unsupported')}
  try { const result=await operation(tx);await completion;return result }
  catch(error) {try{tx.abort()}catch{};await completion.catch(()=>{});throw error}
 }
 async save(context: DraftContext, draftId: string, tabId: string, base: Documents|null, records: Documents) {
  context=validateDraftContext(context)
  if([draftId,tabId].some(id=>!id||!/^[a-zA-Z0-9_-]{1,128}$/.test(id)))throw new Error('draft_lineage_invalid')
  records=validateDocuments(records);if(base)base=validateDocuments(base)
  const hash=await fingerprint(records),prefix=[context.backend,context.member,context.room,draftId,tabId]
  return this.transaction(['draftVersions','draftHeads'],true,async tx=>{
   const heads=tx.objectStore('draftHeads'),previous=await request<Head|undefined>(heads.get(prefix))
   if(previous && (!Number.isSafeInteger(previous.version)||previous.version<1))throw new Error('draft_head_invalid')
   if(previous && !samePerson(previous.context,context))throw new Error('draft_owner_changed')
   const version=(previous?.version||0)+1,key=[...prefix,version] as VersionKey
   const value:Version={key,schemaVersion:1,context:structuredClone(context),base,records,hash,createdAt:Date.now()}
   await request(tx.objectStore('draftVersions').add(value,key));await request(heads.put({context,version,hash,selectedVersion:version,lastAcknowledgedVersion:version},prefix))
   return value
  })
 }
 async inventory(context: DraftContext):Promise<VersionItem[]> {
  return this.transaction(['draftHeads','draftVersions'],false,async tx=>{
   const heads=tx.objectStore('draftHeads'),prefix=[context.backend,context.member,context.room]
   const keys=await request(heads.getAllKeys(range(prefix))),values=await request<Head[]>(heads.getAll(range(prefix))),items:VersionItem[]=[]
   for(let i=0;i<keys.length;i++)if(samePerson(values[i].context,context))for(const key of await request(tx.objectStore('draftVersions').getAllKeys(range(keys[i] as IDBValidKey[]))))items.push({key:key as VersionKey})
   return items.sort((a,b)=>Number(b.key[5])-Number(a.key[5]))
  })
 }
 async load(context: DraftContext,key: VersionKey) {
  const version=await this.transaction(['draftVersions'],false,tx=>request<Version|undefined>(tx.objectStore('draftVersions').get(key)))
  if(!version || !samePerson(version.context,context) || version.context.room!==context.room || version.schemaVersion!==1)throw new Error('draft_version_unavailable')
  validateDocuments(version.records);if(version.base)validateDocuments(version.base)
  if(await fingerprint(version.records)!==version.hash)throw new Error('draft_fingerprint_changed')
  return version
 }
 async history(context: Pick<DraftContext,'backend'|'member'|'issuer'|'subject'|'origin'>) {
  return this.transaction(['roomHistory'],false,async tx=>{const value=await request<any>(tx.objectStore('roomHistory').get([context.backend,context.member]));return value && samePerson(value.context,context as DraftContext)?value.room:null})
 }
 async activate(context: DraftContext,token: string,current: ()=>boolean) {
  return this.transaction(['roomHistory'],true,tx=>{if(!current())throw new Error('stale_activation');return request(tx.objectStore('roomHistory').put({context,room:context.room,token},[context.backend,context.member]))})
 }
 async attempts(key: VersionKey) {return this.transaction(['applyAttempts'],false,async tx=>(await request<ApplyAttempt[]>(tx.objectStore('applyAttempts').getAll())).filter(a=>JSON.stringify(a.key)===JSON.stringify(key)))}
 async prepare(attempt: ApplyAttempt) {
  return this.transaction(['applyAttempts','restoreLease','draftVersions'],true,async tx=>{
   const selected=await request<Version|undefined>(tx.objectStore('draftVersions').get(attempt.key))
   if(!selected || selected.hash!==attempt.hash)throw new Error('draft_version_changed')
   const leases=tx.objectStore('restoreLease'),prior=await request(leases.get(attempt.key))
   if(prior)throw new Error('draft_attempt_requires_reconciliation')
   const attempts=await request<ApplyAttempt[]>(tx.objectStore('applyAttempts').getAll())
   if(attempts.some(a=>JSON.stringify(a.key)===JSON.stringify(attempt.key)))throw new Error('draft_attempt_requires_reconciliation')
   await request(tx.objectStore('applyAttempts').add(attempt,attempt.id))
   await request(leases.add({attemptId:attempt.id,token:attempt.leaseToken,tabId:attempt.tabId,deadline:Date.now()+30_000},attempt.key))
  })
 }
 async outcome(attempt: ApplyAttempt,state: ApplyAttempt['state'],proof?: ApplyAttempt['proof']) {
  return this.transaction(['applyAttempts','restoreLease'],true,async tx=>{
   const saved=await request<ApplyAttempt|undefined>(tx.objectStore('applyAttempts').get(attempt.id)),lease=await request<any>(tx.objectStore('restoreLease').get(attempt.key))
   if(!saved || lease?.token!==attempt.leaseToken)throw new Error('draft_attempt_owner_changed')
   if(saved.state==='verified')return
   await request(tx.objectStore('applyAttempts').put({...saved,state,...(proof?{proof}:{})},attempt.id))
  })
 }
 async remove(context: DraftContext,key: VersionKey,verified?: ApplyAttempt,current:()=>boolean=()=>true) {
  return this.transaction(['draftVersions','draftHeads','applyAttempts','restoreLease'],true,async tx=>{
   const heads=tx.objectStore('draftHeads'),head=await request<Head|undefined>(heads.get(lineage(key)))
   if(!head || !samePerson(head.context,context) || head.context.room!==context.room)throw new Error('draft_owner_changed')
   const lease=await request<any>(tx.objectStore('restoreLease').get(key))
   if(verified){
    const a=await request<ApplyAttempt|undefined>(tx.objectStore('applyAttempts').get(verified.id)),v=await request<Version|undefined>(tx.objectStore('draftVersions').get(key))
    if(a?.state!=='verified' || !a.proof?.sync || !v || v.hash!==a.hash || lease?.token!==a.leaseToken)throw new Error('draft_restoration_unverified')
   }else if(lease && lease.deadline>Date.now())throw new Error('draft_apply_in_progress')
   if(!current())throw new Error('draft_identity_changed')
   await request(tx.objectStore('draftVersions').delete(key));await request(tx.objectStore('restoreLease').delete(key))
   if((head.selectedVersion??head.version)===key[5]){
    const remaining=await request(tx.objectStore('draftVersions').getAllKeys(range(lineage(key)))),last=remaining.length?Number((remaining.at(-1) as VersionKey)[5]):null
    await request(heads.put({...head,hash:'',selectedVersion:last,lastAcknowledgedVersion:last},lineage(key)))
   }
  })
 }
}
export function openHumanDrafts(name=DRAFT_DATABASE):Promise<HumanDrafts> {
 return new Promise((resolve,reject)=>{
  let refused=false
  const r=indexedDB.open(name,DRAFT_SCHEMA_VERSION)
  r.onupgradeneeded=event=>{
   const db=r.result,old=(event as IDBVersionChangeEvent).oldVersion
   if(old<1)for(const store of ['draftVersions','draftHeads','roomHistory'])db.createObjectStore(store)
   if(old<2)for(const store of ['applyAttempts','restoreLease'])db.createObjectStore(store)
  }
  r.onblocked=()=>{refused=true;reject(new Error('draft_upgrade_blocked'))}
  r.onerror=()=>reject(r.error)
  r.onsuccess=()=>{if(refused){r.result.close();return}r.result.onversionchange=()=>r.result.close();resolve(new HumanDrafts(r.result))}
 })
}
let connection:Promise<HumanDrafts>|undefined
export const humanDrafts=()=>connection ||= openHumanDrafts().catch(error=>{connection=undefined;throw error})
