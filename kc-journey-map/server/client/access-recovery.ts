export type RecoveryCause = { kind: 'expired' | 'denied' | 'unavailable' | 'unknown'; category: string }
const expired = new Set(['session_expired', 'human_revalidation_due', 'human_sign_in_required'])
const denied = new Set(['identity_changed', 'draft_identity_changed', 'authority_denied', 'member_denied', 'room_denied', 'room_missing', 'room_context_changed', 'human_context_denied'])
const unavailable = new Set(['host_unavailable', 'provider_unavailable', 'owner_peer_unavailable'])
export class RecoveryError extends Error {
 constructor(readonly cause: RecoveryCause, message=cause.category) { super(message) }
}
export function recoveryCause(error: unknown): RecoveryCause {
 if (error instanceof RecoveryError) return error.cause
 const category = error && typeof error === 'object' && 'category' in error && typeof error.category === 'string' ? error.category : error instanceof Error ? error.message : ''
 if (expired.has(category)) return { kind: 'expired', category }
 if (denied.has(category)) return { kind: 'denied', category }
 if (unavailable.has(category) || error instanceof TypeError || (error instanceof Error && error.name === 'TimeoutError')) return { kind: 'unavailable', category: 'host_unavailable' }
 return { kind: 'unknown', category: 'outcome_unknown' }
}
export async function recoveryResponse(response: Response) {
 let value: any
 try { value = await response.json() } catch { throw new RecoveryError({ kind: 'unknown', category: 'protocol_unknown' }) }
 if (!value || typeof value !== 'object' || Array.isArray(value)) throw new RecoveryError({ kind: 'unknown', category: 'protocol_unknown' })
 if (!response.ok) {
  const typed = recoveryCause(new Error(value.category))
  if (typed.kind !== 'unknown') throw new RecoveryError(typed)
  throw new RecoveryError(response.status >= 500 ? { kind: 'unavailable', category: 'host_unavailable' } : { kind: 'unknown', category: 'protocol_unknown' })
 }
 return value
}
