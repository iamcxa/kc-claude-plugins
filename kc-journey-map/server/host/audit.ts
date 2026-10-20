import { HostError } from './core'
import { digest } from './policy'
import { canonical } from '../draft-data'
import type { Admission } from './policy'
import type { Host } from './transport'
export async function audited<T>(host: Host, admission: Admission | null, room: string, action: string, effect: () => Promise<T>, operationId?: string, outcome:'committed'|'admitted'='committed', requestBody?: unknown): Promise<T> {
 if(!host.private || !host.meta.security)return effect()
 if(operationId && !/^[a-zA-Z0-9_-]{1,128}$/.test(operationId))throw new HostError(400,'invalid_operation_id')
 let correlation
 if(admission?.actorType==='human' && requestBody!==undefined){
  const session=await host.meta.get<any>('browser-session:'+admission.humanSessionDigest),member=await host.meta.get<any>('member:'+admission.principalId)
  if(!session || !member)throw new HostError(403,'authority_denied')
  correlation={version:1,requestHash:await digest(canonical(requestBody)),context:{backend:session.backendId,member:member.id,issuer:member.issuer,subject:member.subject,generation:session.generation,signInAt:session.verifiedHumanSignInAt,room}}
 }
 const reserved=await host.meta.security('reserve',{action,actor:admission,room,operationId,correlation})
 let value:T
 try {value=await effect()}
 catch(error){try {await host.meta.security('finalize',{operationId:reserved.operationId,outcome:'unknown'})}catch{}throw error}
 try {await host.meta.security('finalize',{operationId:reserved.operationId,outcome})}
 catch {throw new HostError(503,'mutation_receipt_pending',{category:'mutation_receipt_pending',operationId:reserved.operationId,outcome:outcome+'_receipt_pending',retry:false})}
 return value
}
