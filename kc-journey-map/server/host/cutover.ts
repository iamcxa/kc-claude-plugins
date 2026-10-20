import { HostError, prepareDoc } from './core'
import { currentGrant, type Admission } from './policy'
import { audited } from './audit'
import type { Host } from './transport'
export async function verifyCutoverConsumer(host:Host,admission:Admission,credentialId:string,consumerId:string) {
 const plan=await host.meta.get<any>('security-cutover:'+credentialId),consumer=plan?.consumers.find((c:any)=>c.id===consumerId)
 if(!plan?.synthetic || !consumer || admission.actorType!=='agent' || admission.familyId!==consumer.familyId)throw new HostError(403,'cutover_consumer_denied')
 const grant=await currentGrant(host.meta,admission)
 for(const room of consumer.rooms) {
  if(!grant.rooms.includes(room))throw new HostError(403,'cutover_room_denied')
  const before=await host.document(room,'GET',null) as any
  const id='page:cutover_'+crypto.randomUUID().replaceAll('-',''),sentinel={id,typeName:'page',name:'Synthetic cutover verification',index:'a1',meta:{}}
  await audited(host,admission,room,'cutover:sentinel',()=>host.document(room,'PATCH',prepareDoc('PATCH',{put:[sentinel]})))
  const written=await host.document(room,'GET',null) as any
  if(!written.snapshot.documents.some((d:any)=>d.state.id===id))throw new HostError(503,'cutover_write_unverified')
  await audited(host,admission,room,'cutover:cleanup',()=>host.document(room,'PATCH',prepareDoc('PATCH',{remove:[id]})))
  const after=await host.document(room,'GET',null) as any
  const records=(doc:any)=>JSON.stringify(doc.snapshot.documents.map((d:any)=>d.state).sort((a:any,b:any)=>a.id.localeCompare(b.id)))
  if(records(before)!==records(after))throw new HostError(409,'cutover_original_records_changed')
 }
 return host.meta.security!('cutover-verified',{credentialId,consumerId,familyId:admission.familyId,rooms:consumer.rooms})
}
