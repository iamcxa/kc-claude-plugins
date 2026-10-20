import { currentGrant, type Admission, type Metadata } from './policy'
import { HostError } from './core'
export const STREAM_LEASE = 30_000
export type StreamLease = { streamId: string; room: string; admission: Admission; leaseUntil: number; invalidated?: boolean }
export function canSend(lease: StreamLease | null | undefined, now = Date.now()) {
 return !!lease && !lease.invalidated && Number.isFinite(lease.leaseUntil) && Number.isFinite(lease.admission?.expiresAt) && now < lease.leaseUntil && now < lease.admission.expiresAt
}
export async function renewLease(meta: Metadata, lease: StreamLease, now = Date.now()) {
 let timer: ReturnType<typeof setTimeout> | undefined
 try {
  if (lease.invalidated) throw new HostError(403, 'stream_invalidated')
  const grant = await Promise.race([currentGrant(meta, lease.admission), new Promise<never>((_, reject) => { timer = setTimeout(() => reject(new HostError(503, 'policy_unavailable')), 2000) })])
  if (!grant.rooms.includes(lease.room) || lease.invalidated) throw new HostError(403, 'stream_denied')
  lease.leaseUntil = Math.min(now + STREAM_LEASE, grant.expiresAt, lease.admission.expiresAt)
  if (!canSend(lease)) throw new HostError(403, 'stream_expired')
  return lease
 } finally { clearTimeout(timer) }
}
