import { HUMAN_BOUND } from '../server/host/human-store'
import type { EnrollmentBinding, EnrollmentProof } from '../server/host/member-enrollment'
export type ProviderRead = (path:string,query?:Record<string,string>)=>Promise<any>
const refuse=(category:string):never=>{throw new Error(category)}
export async function resolveMember(email:string,b:EnrollmentBinding,read:ProviderRead,now=Date.now(),signal?:AbortSignal):Promise<EnrollmentProof> {
 const get=async(path:string,query?:Record<string,string>)=>{signal?.throwIfAborted();const r=await read(path,query);signal?.throwIfAborted();if(r?.success!==true)refuse('provider_unavailable');return r}
 const base='/accounts/'+encodeURIComponent(b.accountId)+'/access'
 const organization=(await get(base+'/organizations')).result
 if(organization?.auth_domain!==new URL(b.issuer).host)refuse('account_issuer_mismatch')
 const app=(await get(base+'/apps/'+encodeURIComponent(b.applicationId))).result
 if(app?.id!==b.applicationId || app?.aud!==b.audience || app?.domain!==new URL(b.origin).host)refuse('application_binding_mismatch')
 const provider=(await get('/accounts/'+encodeURIComponent(b.accountId)+'/identity_providers/'+encodeURIComponent(b.providerId))).result
 if(provider?.id!==b.providerId || provider?.type!=='onetimepin')refuse('unsupported_identity_proof')
 const matches:any[]=[];let totalPages=0
 for(let page=1;page<=32;page++){
  const response=await get(base+'/users',{email,page:String(page),per_page:'100'}),info=response.result_info
  if(!Array.isArray(response.result) || !Number.isSafeInteger(info?.total_pages) || info.total_pages<1 || info.total_pages>32 || info.page!==page || (totalPages && totalPages!==info.total_pages))refuse('incomplete_identity_scan')
  totalPages=info.total_pages;matches.push(...response.result.filter((u:any)=>u.email===email))
  if(page===totalPages)break
 }
 if(matches.length===0)refuse('identity_not_ready');if(matches.length!==1)refuse('ambiguous_identity')
 const user=matches[0];if(typeof user.id!=='string' || !user.id)refuse('unsupported_identity_proof')
 const identity=(await get(base+'/users/'+encodeURIComponent(user.id)+'/last_seen_identity')).result
 if(!identity)refuse('identity_not_ready')
 if(identity.email!==email || identity.account_id!==b.accountId || !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(identity.user_uuid) || identity.service_token_status!==false || identity.service_token_id || identity.common_name || identity.idp?.id!==b.providerId || !Number.isFinite(identity.iat))refuse('unsupported_identity_proof')
 const signInAt=identity.iat*1000
 if(signInAt>now || signInAt+HUMAN_BOUND<=now)refuse('identity_not_ready')
 return {accountId:b.accountId,applicationId:b.applicationId,providerId:b.providerId,backendId:b.backendId,origin:b.origin,issuer:b.issuer,audience:b.audience,email,subject:identity.user_uuid,lookupId:user.id,signInAt,observedAt:now,classification:'authenticated-last-seen-onetimepin'}
}
