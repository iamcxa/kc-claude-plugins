import { journeyApi } from './api'
import { canonical, changes, fingerprint, matchesChanges, sameMount, samePerson, type Documents, type DraftContext } from '../draft-data'
import { type ApplyAttempt, type HumanDrafts, type Version } from './human-drafts'
export const humanCookieMarker=()=>document.cookie.split(';').map(v=>v.trim()).find(v=>v.startsWith('journey_human_csrf='))||''
const checked = async (response: Response) => {const value=await response.json();if(!response.ok)throw new Error(value.category||value.error||'draft_request_failed');return value}
export async function verifiedDraftContext(original: DraftContext, room=true, signal?: AbortSignal):Promise<DraftContext> {
 const marker=humanCookieMarker()
 const identity=await checked(await fetch(journeyApi('/auth/identity',null),{cache:'no-store',signal:AbortSignal.any([AbortSignal.timeout(8000),...(signal?[signal]:[])])}))
 const current:DraftContext={origin:window.location.origin,backend:identity.backendId,member:identity.memberId,issuer:identity.issuer,subject:identity.subject,generation:identity.generation,signInAt:identity.verifiedHumanSignInAt,revalidateBy:identity.humanRevalidateBy,room:original.room}
 if(!samePerson(current,original))throw new Error('draft_identity_changed')
 if(room){
  const entry=await checked(await fetch(journeyApi('/auth/entry?'+new URLSearchParams({room:original.room}),null),{cache:'no-store',signal}))
  if(entry.memberId!==current.member || entry.backendId!==current.backend || entry.room!==current.room || entry.verifiedHumanSignInAt!==current.signInAt || entry.generation!==current.generation)throw new Error('draft_identity_changed')
 }
 signal?.throwIfAborted();if(marker!==humanCookieMarker())throw new Error('draft_identity_changed');return current
}
export async function currentDocuments(context: DraftContext,signal?: AbortSignal):Promise<Documents> {
 const value=await checked(await fetch(journeyApi('/doc?room='+encodeURIComponent(context.room),context),{cache:'no-store',signal}))
 return Object.fromEntries(value.snapshot.documents.map(({state}:{state:any})=>[state.id,state]))
}
export type DraftReview = { version: Version; context: DraftContext; current: Documents; currentHash: string; patch: ReturnType<typeof changes> }
export async function reviewDraft(db: HumanDrafts,original: DraftContext,key: Version['key'],signal?: AbortSignal):Promise<DraftReview> {
 const context=await verifiedDraftContext(original,true,signal),version=await db.load(context,key)
 if(!version.base)throw new Error('draft_base_unknown')
 const current=await currentDocuments(context,signal)
 const currentHash=await fingerprint(current)
 const latest=await verifiedDraftContext(original,true,signal);if(!sameMount(context,latest))throw new Error('draft_identity_changed')
 return {version,context,current,currentHash,patch:changes(version.base,version.records)}
}
export type SyncConfirmation = (context:DraftContext,patch:DraftReview['patch'],signal:AbortSignal)=>Promise<void>
export async function reconcileDraft(db:HumanDrafts,original:DraftContext,attempt:ApplyAttempt,sync:SyncConfirmation,signal:AbortSignal) {
 try {
  const context=await verifiedDraftContext(original,true,signal)
  const receipt=await checked(await fetch(journeyApi('/auth/draft-receipt?'+new URLSearchParams({room:context.room,operationId:attempt.id}),context),{cache:'no-store',signal}))
  const expected={backend:attempt.context.backend,member:attempt.context.member,issuer:attempt.context.issuer,subject:attempt.context.subject,generation:attempt.context.generation,signInAt:attempt.context.signInAt,room:attempt.context.room}
  if(receipt.operationId!==attempt.id || receipt.action!=='document:PATCH' || receipt.outcome!=='committed' || receipt.final!==true || receipt.correlation?.version!==1 || receipt.correlation.requestHash!==attempt.requestHash || canonical(receipt.correlation.context)!==canonical(expected))throw new Error('draft_original_outcome_unknown')
  const current=await currentDocuments(context,signal)
  if(!matchesChanges(current,attempt.patch))throw new Error('draft_readback_unconfirmed')
  await sync(context,attempt.patch,signal)
  const latest=await verifiedDraftContext(original,true,signal)
  if(!sameMount(context,latest))throw new Error('draft_identity_changed')
  signal.throwIfAborted()
  await db.outcome(attempt,'verified',{receipt,readback:await fingerprint(current),sync:true})
  const marker=humanCookieMarker(),finalContext=await verifiedDraftContext(original,true,signal)
  if(!sameMount(context,finalContext))throw new Error('draft_identity_changed')
  await db.remove(context,attempt.key,attempt,()=>!signal.aborted&&humanCookieMarker()===marker)
 }catch(error){await db.outcome(attempt,'unknown').catch(()=>{});throw error}
}
export async function applyDraft(db:HumanDrafts,review:DraftReview,tabId:string,sync:SyncConfirmation,signal:AbortSignal) {
 const context=await verifiedDraftContext(review.context,true,signal)
 if(!sameMount(context,review.context))throw new Error('draft_identity_changed')
 const current=await currentDocuments(context,signal)
 if(await fingerprint(current)!==review.currentHash)throw new Error('draft_cloud_changed_review_again')
 signal.throwIfAborted()
 const attempt:ApplyAttempt={id:crypto.randomUUID(),key:review.version.key,hash:review.version.hash,context,reviewedHash:review.currentHash,patch:review.patch,requestHash:await fingerprint(review.patch),tabId,leaseToken:crypto.randomUUID(),state:'prepared',createdAt:Date.now()}
 await db.prepare(attempt)
 try {
  signal.throwIfAborted();await db.outcome(attempt,'sent')
  const fresh=await verifiedDraftContext(context,true,signal);if(!sameMount(fresh,context))throw new Error('draft_identity_changed')
  const response=await fetch(journeyApi('/doc?room='+encodeURIComponent(context.room),context),{method:'PATCH',headers:{'Content-Type':'application/json','x-journey-operation':attempt.id},body:JSON.stringify(attempt.patch),signal})
  await checked(response)
  await reconcileDraft(db,context,attempt,sync,signal)
 }catch(error){await db.outcome(attempt,'unknown').catch(()=>{});throw error}
}
