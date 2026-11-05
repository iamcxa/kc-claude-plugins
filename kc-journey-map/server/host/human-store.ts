import { canonicalRoom, HostError } from './core'
import { denial } from './security-store'

export const HUMAN_BOUND = 7 * 24 * 60 * 60_000
export const HUMAN_ACCESS = 15 * 60_000
export type HumanConfig = {
 version: 1; backendId: string; origin: string; mode: 'local' | 'cloudflare'; issuer: string
 audience?: string; localOwnerUid?: number; localMemberId?: string
 members: Array<{ id: string; issuer: string; subject: string; label: string; role: 'operator' | 'member'; rooms: Array<{ id: string; expiresAt: number }> }>
}
export type Member = { id: string; issuer: string; subject: string; label: string; role: 'operator' | 'member'; enabled: boolean; generation: number }
export type HumanSession = { actorType: 'human'; backendId: string; memberId: string; generation: number; expiresAt: number; verifiedHumanSignInAt: number; humanRevalidateBy: number; csrfDigest: string; revoked: boolean }
export type MemberRoom = { memberId: string; roomId: string; expiresAt: number; revoked: boolean; generation: number }
export type SyncMetadata = {
 get<T = any>(key: string): T | null; put(key: string, value: unknown): void; delete(key: string): void
 list(prefix: string, limit: number, after?: string): Array<{ key: string; value: any }>
}
const fail = (status: number, category: string): never => { throw new HostError(status, category, { category }) }
const id = (value: unknown) => typeof value === 'string' && /^[a-zA-Z0-9_-]{1,128}$/.test(value)
const identityKey = (issuer: string, subject: string) => 'human-identity:' + JSON.stringify([issuer, subject])
export function validateHumanConfig(value: HumanConfig, origin: string) {
 if (value?.version !== 1 || !id(value.backendId) || value.origin !== origin || !['local', 'cloudflare'].includes(value.mode) || !value.issuer || !Array.isArray(value.members)) throw new Error('invalid human-entry configuration')
 const url = new URL(origin)
 if (url.origin !== origin || (url.protocol !== 'https:' && !['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname))) throw new Error('human entry requires HTTPS or exact loopback')
 if (value.mode === 'local' && (!['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname) || !Number.isSafeInteger(value.localOwnerUid) || !id(value.localMemberId))) throw new Error('local entry requires an explicit loopback owner/member')
 if (value.mode === 'cloudflare' && (new URL(value.issuer).protocol !== 'https:' || new URL(value.issuer).origin !== value.issuer || !value.audience)) throw new Error('provider requires exact HTTPS issuer and audience')
 const ids = new Set(), identities = new Set()
 for (const m of value.members) {
  const key = identityKey(m.issuer, m.subject)
  if (!id(m.id) || ids.has(m.id) || identities.has(key) || m.issuer !== value.issuer || !m.subject || typeof m.label !== 'string' || !m.label.trim() || !['member', 'operator'].includes(m.role) || !Array.isArray(m.rooms)) throw new Error('invalid or duplicate member binding')
  ids.add(m.id); identities.add(key)
  const rooms = new Set()
  for (const r of m.rooms) {
   if (!r.id || canonicalRoom(r.id) !== r.id || rooms.has(r.id) || !Number.isFinite(r.expiresAt)) throw new Error('invalid member room')
   rooms.add(r.id)
  }
 }
 if (value.mode === 'local' && !value.members.some(m => m.id === value.localMemberId && m.role === 'operator' && m.subject === 'uid:' + value.localOwnerUid)) throw new Error('local owner must bind the exact configured OS account')
 return value
}
export function bootstrapHuman(store: SyncMetadata, config: HumanConfig) {
 const previous = store.get<HumanConfig & {minimumSecurityVersion?:number}>('human-config:v1')
 if (previous) {
  const {minimumSecurityVersion,...original}=previous
  if(minimumSecurityVersion && minimumSecurityVersion!==2)throw new Error('unsupported security version')
  if (JSON.stringify(original) !== JSON.stringify(config)) throw new Error('human configuration is immutable; use explicit operator policy changes')
  if(!minimumSecurityVersion)store.put('human-config:v1',{...config,minimumSecurityVersion:2})
  return
 }
 store.put('human-schema:v1', { version: 1 })
 store.put('human-config:v1', {...config,minimumSecurityVersion:2})
 for (const m of config.members) {
  if (store.get('member:' + m.id) || store.get(identityKey(m.issuer, m.subject))) throw new Error('member binding exists')
  store.put('member:' + m.id, { id: m.id, issuer: m.issuer, subject: m.subject, label: m.label, role: m.role, enabled: true, generation: 1 })
  store.put(identityKey(m.issuer, m.subject), m.id)
  for (const r of m.rooms) store.put('member-room:' + m.id + ':' + r.id, { memberId: m.id, roomId: r.id, expiresAt: r.expiresAt, revoked: false, generation: 1 })
 }
 receipt(store, 'bootstrap', null, null, 'allowed', Date.now())
}
function receipt(store: SyncMetadata, operation: string, memberId: string | null, requestId: string | null, outcome: string, now: number) {
 const cutoff = now - 30 * 24 * 60 * 60_000
 for (const row of store.list('human-receipt:', 64)) if (row.value.serverTime < cutoff) store.delete(row.key)
 const eventId = crypto.randomUUID()
 store.put('human-receipt:' + String(now).padStart(16, '0') + ':' + eventId, { eventId, operation, memberId, requestId, room: null, actorType: ['bootstrap', 'disable-member', 'set-room', 'local-approve'].includes(operation) ? 'operator' : memberId ? 'human' : 'unknown', outcome, serverTime: now })
}
function member(store: SyncMetadata, memberId: string): Member {
 const m = store.get<Member>('member:' + memberId)
 if (!m?.enabled) fail(403, 'member_denied')
 return m!
}
function activeSession(store: SyncMetadata, config: HumanConfig, sessionDigest: string, now: number) {
 const s = store.get<HumanSession>('browser-session:' + sessionDigest)
 if (!s || s.actorType !== 'human' || s.backendId !== config.backendId || s.revoked) fail(401, 'authority_denied')
 if (!Number.isFinite(s!.humanRevalidateBy) || !Number.isFinite(s!.verifiedHumanSignInAt) || s!.humanRevalidateBy <= now || s!.verifiedHumanSignInAt > now || s!.humanRevalidateBy > s!.verifiedHumanSignInAt + HUMAN_BOUND) fail(401, 'human_revalidation_due')
 if (!Number.isFinite(s!.expiresAt) || s!.expiresAt <= now) fail(401, 'session_expired')
 const m = member(store, s!.memberId)
 if (m.generation !== s!.generation) fail(403, 'authority_denied')
 return { session: s!, member: m }
}
function mint(store: SyncMetadata, config: HumanConfig, input: any, memberId: string, signInAt: number, now: number) {
 const m = member(store, memberId)
 if (!Number.isFinite(signInAt) || signInAt > now || signInAt + HUMAN_BOUND <= now) fail(401, 'human_revalidation_due')
 const session: HumanSession = { actorType: 'human', backendId: config.backendId, memberId: m.id, generation: m.generation,
  expiresAt: Math.min(now + HUMAN_ACCESS, signInAt + HUMAN_BOUND), verifiedHumanSignInAt: signInAt, humanRevalidateBy: signInAt + HUMAN_BOUND, csrfDigest: input.csrfDigest, revoked: false }
 if (store.get('browser-session:' + input.sessionDigest)) fail(409, 'session_collision')
 store.put('browser-session:' + input.sessionDigest, session)
 receipt(store, 'sign-in', m.id, input.requestId || null, 'allowed', now)
 return session
}
export function humanOperation(store: SyncMetadata, operation: string, input: any, now = Date.now()): any {
 const config = store.get<HumanConfig>('human-config:v1')
 if (!config) fail(503, 'human_entry_unconfigured')
 if (operation === 'record-denial') {
  if (!/^[a-z_]{1,64}$/.test(input.category)) fail(400, 'invalid_receipt')
  receipt(store, 'entry', null, null, input.category, now)
  return { recorded: true }
 }
 if (operation === 'challenge-create') {
  if (config!.mode !== 'local' || input.origin !== config!.origin) fail(403, 'local_entry_denied')
  if (store.list('human-challenge:', 128).filter(row => row.value.expiresAt > now && !row.value.consumed).length >= 32) fail(429, 'challenge_limit')
  for (const row of store.list('human-challenge:', 128)) if (row.value.expiresAt <= now) store.delete(row.key)
  store.put('human-challenge:' + input.requestId, { requestId: input.requestId, origin: input.origin, verifierDigest: input.verifierDigest, csrfDigest: input.csrfDigest, memberId: config!.localMemberId, createdAt: now, expiresAt: now + 60_000, approvedAt: null, consumed: false })
  return { requestId: input.requestId, expiresAt: now + 60_000 }
 }
 if (['challenge-inspect', 'challenge-approve', 'challenge-consume'].includes(operation)) {
  const key = 'human-challenge:' + input.requestId, challenge = store.get<any>(key)
  if (!challenge || challenge.consumed || challenge.expiresAt <= now) fail(410, 'challenge_expired_or_consumed')
  if (operation !== 'challenge-consume') {
   if (config!.mode !== 'local' || input.peerUid !== config!.localOwnerUid || challenge.origin !== config!.origin) fail(403, 'owner_peer_denied')
   member(store, challenge.memberId)
   if (operation === 'challenge-inspect') return { requestId: challenge.requestId, origin: challenge.origin, memberId: challenge.memberId, expiresAt: challenge.expiresAt }
   if (challenge.approvedAt !== null) fail(409, 'challenge_already_approved')
   challenge.approvedAt = now; store.put(key, challenge)
   receipt(store, 'local-approve', challenge.memberId, challenge.requestId, 'allowed', now)
   return { approved: true }
  }
  if (input.origin !== challenge.origin || input.verifierDigest !== challenge.verifierDigest || input.csrfDigest !== challenge.csrfDigest) fail(403, 'challenge_binding_denied')
  if (challenge.approvedAt === null) fail(409, 'approval_pending')
  const session = mint(store, config!, input, challenge.memberId, challenge.approvedAt, now)
  store.put(key, { ...challenge, consumed: true })
  return session
 }
 if (operation === 'provider-consume') {
  const c = store.get<any>('human-provider:' + input.requestId)
  if (!c || c.consumed || c.expiresAt <= now || c.verifierDigest !== input.verifierDigest || c.origin !== config!.origin) fail(403, 'login_state_denied')
  if (config!.mode !== 'cloudflare' || input.identity.issuer !== config!.issuer || input.identity.audience !== config!.audience) fail(403, 'provider_identity_denied')
  const memberId = store.get<string>(identityKey(input.identity.issuer, input.identity.subject))
  if (!memberId) fail(403, 'member_unbound')
  const session = mint(store, config!, input, memberId!, input.identity.signInAt, now)
  store.put('human-provider:' + input.requestId, { ...c, consumed: true })
  return session
 }
 if (operation === 'provider-start') {
  if (config!.mode !== 'cloudflare') fail(403, 'provider_unconfigured')
  for (const row of store.list('human-provider:', 128)) if (row.value.expiresAt <= now) store.delete(row.key)
  if (store.list('human-provider:', 128).filter(row => row.value.expiresAt > now).length >= 32) fail(429, 'challenge_limit')
  store.put('human-provider:' + input.requestId, { origin: config!.origin, verifierDigest: input.verifierDigest, expiresAt: now + 60_000, consumed: false })
  return { requestId: input.requestId }
 }
 if (operation === 'disable-member') {
  const m = member(store, input.memberId)
  const result = denial(store, { memberId: m.id }, operation, {}, now)
  store.put('member:' + m.id, { ...m, enabled: false, generation: m.generation + 1 })
  receipt(store, 'disable-member', m.id, null, 'denied', now)
  return result
 }
 if (operation === 'set-room') {
  const m = member(store, input.memberId)
  if (!input.roomId || canonicalRoom(input.roomId) !== input.roomId || typeof input.revoked !== 'boolean' || !Number.isFinite(input.expiresAt)) fail(400, 'invalid_room_policy')
  const result = denial(store, { memberId: m.id, roomId: input.roomId }, operation, {}, now)
  const previous = store.get<MemberRoom>('member-room:' + m.id + ':' + input.roomId)
  store.put('member-room:' + m.id + ':' + input.roomId, { memberId: m.id, roomId: input.roomId, expiresAt: input.expiresAt, revoked: input.revoked, generation: (previous?.generation || 0) + 1 })
  store.put('member:' + m.id, { ...m, generation: m.generation + 1 })
  receipt(store, 'set-room', m.id, null, input.revoked ? 'denied' : 'allowed', now)
  return { changed: true, ...result }
 }
 const { session, member: m } = activeSession(store, config!, input.sessionDigest, now)
 if (input.csrfDigest !== session.csrfDigest) fail(403, 'csrf_denied')
 if (operation === 'account-read') {
  if(input.backendId!==config!.backendId || input.memberId!==m.id || input.signInAt!==session.verifiedHumanSignInAt)fail(403,'identity_changed')
  const room=input.roomId,grant=store.get<MemberRoom>('member-room:'+m.id+':'+room)
  if(!room || canonicalRoom(room)!==room || !grant || grant.memberId!==m.id || grant.roomId!==room || grant.revoked || grant.expiresAt<=now)fail(403,'room_denied')
  if(!store.get('room:'+room))fail(404,'room_missing')
  return {backendId:config!.backendId,memberId:m.id,label:m.label,roomId:room}
 }
 if (operation === 'renew') {
  session.expiresAt = Math.min(now + HUMAN_ACCESS, session.humanRevalidateBy)
  store.put('browser-session:' + input.sessionDigest, session)
  return session
 }
 if (operation === 'logout') {
  const result = denial(store, { humanSessionDigest: input.sessionDigest }, operation, { actorType: 'human', principalId: m.id }, now)
  store.put('browser-session:' + input.sessionDigest, { ...session, revoked: true, revokeOperation: result.operationId })
  receipt(store, 'logout', m.id, null, 'denied', now)
  return { loggedOut: true, ...result }
 }
 return fail(400, 'unknown_human_operation')
}
