import { currentGrant, type Admission, type Metadata } from './policy'
import { HostError } from './core'
export const STREAM_LEASE = 30_000
export type StreamLease = { streamId: string; room: string; admission: Admission; leaseUntil: number; invalidated?: boolean }
export function canSend(lease: StreamLease | null | undefined, now = Date.now()) {
 return !!lease && !lease.invalidated && Number.isFinite(lease.leaseUntil) && Number.isFinite(lease.admission?.expiresAt) && now < lease.leaseUntil && now < lease.admission.expiresAt
}
export async function renewLease(meta: Metadata, lease: StreamLease, now = Date.now()) {
 let timer: ReturnType<typeof setTimeout> | undefined
 const check=async()=>{
  if(lease.invalidated)throw new HostError(403,'stream_invalidated')
  const grant=await currentGrant(meta,lease.admission)
  if(!grant.rooms.includes(lease.room))throw new HostError(403,'stream_denied')
  let roomExpiry=Infinity
  if(lease.admission.actorType==='human' || lease.admission.actorType==='agent'){
   const room=await meta.get<{memberId:string;roomId:string;expiresAt:number;revoked:boolean}>('member-room:'+lease.admission.principalId+':'+lease.room)
   if(!room || room.memberId!==lease.admission.principalId || room.roomId!==lease.room || room.revoked || !Number.isFinite(room.expiresAt) || room.expiresAt<=Date.now())throw new HostError(403,'stream_room_expired')
   roomExpiry=room.expiresAt
  }
  if(lease.invalidated)throw new HostError(403,'stream_invalidated')
  lease.leaseUntil=Math.min(now+STREAM_LEASE,grant.expiresAt,lease.admission.expiresAt,roomExpiry)
  if(!canSend(lease))throw new HostError(403,'stream_expired')
  return lease
 }
 try {return await Promise.race([check(),new Promise<never>((_,reject)=>{timer=setTimeout(()=>reject(new HostError(503,'policy_unavailable')),2000)})])}
 finally {clearTimeout(timer)}
}
