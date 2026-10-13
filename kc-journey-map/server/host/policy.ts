import { canonicalRoom, HostError } from './core'
export type Grant = { credentialId: string; secretDigest: string; principalId: string; rooms: string[]; expiresAt: number; revoked: boolean }
export type Session = { credentialId: string; expiresAt: number }
export type Admission = Session & { rooms: string[]; principalId: string; cookie: boolean }
export interface Metadata {
 get<T>(key: string): Promise<T | null>
 put(key: string, value: unknown): Promise<void>
 list<T>(prefix: string): Promise<Array<{ key: string; value: T }>>
}
export async function digest(secret: string) {
 return [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(secret)))].map(b => b.toString(16).padStart(2, '0')).join('')
}
export function validateGrants(grants: Grant[]) {
 if (!Array.isArray(grants) || !grants.length) throw new Error('private mode requires grants')
 const ids = new Set()
 for (const g of grants) {
  if (!/^[a-zA-Z0-9_-]+$/.test(g.credentialId) || ids.has(g.credentialId) || !/^[a-f0-9]{64}$/.test(g.secretDigest) ||
   typeof g.principalId !== 'string' || !g.principalId || !Array.isArray(g.rooms) ||
   g.rooms.some(r => !r || canonicalRoom(r) !== r) || !Number.isFinite(g.expiresAt) || typeof g.revoked !== 'boolean')
   throw new Error('invalid grant document')
  ids.add(g.credentialId)
 }
 return grants
}
export async function currentGrant(meta: Metadata, session: Session): Promise<Grant> {
 const grant = await meta.get<Grant>('grant:' + session.credentialId)
 if (!grant || grant.revoked || grant.expiresAt <= Date.now() || session.expiresAt <= Date.now())
  throw new HostError(401, 'credential expired, revoked or invalid')
 return grant
}
export async function authenticate(meta: Metadata, headers: Headers): Promise<Admission> {
 const bearer = headers.get('authorization')
 let session: Session, cookie = false
 if (bearer) {
  const match = /^Bearer ([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]{43,})$/.exec(bearer)
  if (!match) throw new HostError(401, 'invalid credential')
  const grant = await meta.get<Grant>('grant:' + match[1])
  if (!grant || await digest(match[2]) !== grant.secretDigest) throw new HostError(401, 'invalid credential')
  session = { credentialId: grant.credentialId, expiresAt: grant.expiresAt }
 } else {
  const token = /(?:^|;\s*)journey_session=([^;]+)/.exec(headers.get('cookie') ?? '')?.[1]
  const found = token ? await meta.get<Session>('session:' + await digest(token)) : null
  if (!found) throw new HostError(401, 'credential required')
  session = found; cookie = true
 }
 const grant = await currentGrant(meta, session)
 return { ...session, expiresAt: Math.min(session.expiresAt, grant.expiresAt), rooms: grant.rooms, principalId: grant.principalId, cookie }
}
export function authorize(admission: Admission | null, raw: string) {
 const room = canonicalRoom(raw)
 if (admission && (raw !== room || !room || !admission.rooms.includes(room))) throw new HostError(403, 'room forbidden')
 return room
}
export function requireOrigin(headers: Headers, origin: string) {
 if (headers.get('origin') !== origin) throw new HostError(403, 'origin forbidden')
}
export async function exchange(meta: Metadata, headers: Headers, origin: string) {
 requireOrigin(headers, origin)
 if (!headers.has('authorization')) throw new HostError(401, 'bearer credential required')
 const a = await authenticate(meta, headers)
 const token = [...crypto.getRandomValues(new Uint8Array(32))].map(b => b.toString(16).padStart(2, '0')).join('')
 const expiresAt = Math.min(Date.now() + 15 * 60_000, a.expiresAt)
 await meta.put('session:' + await digest(token), { credentialId: a.credentialId, expiresAt })
 return { expiresAt, cookie: `journey_session=${token}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=${Math.max(0, Math.floor((expiresAt-Date.now())/1000))}` }
}
