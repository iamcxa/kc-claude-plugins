import { HostError, canonicalRoom } from './core'
import { digest, type Metadata, type Admission } from './policy'
import { HUMAN_BOUND, type HumanConfig, type HumanSession, type Member, type MemberRoom } from './human-store'
import { verifyCloudflareIdentity } from './human-provider'
export const randomSecret = () => [...crypto.getRandomValues(new Uint8Array(32))].map(b => b.toString(16).padStart(2, '0')).join('')
export const cookieValue = (headers: Headers, name: string) => new RegExp('(?:^|;\\s*)' + name + '=([^;]+)').exec(headers.get('cookie') || '')?.[1]
export type HumanHost = { origin: string; meta: Metadata; humanConfig?: HumanConfig; localHumanReady?: boolean; publicRequestUrl?: boolean }
function deny(status: number, category: string): never { throw new HostError(status, category, { category }) }
export async function currentHuman(meta: Metadata, session: HumanSession, now = Date.now()) {
 const config = await meta.get<HumanConfig>('human-config:v1')
 if (!config || session.actorType !== 'human' || session.backendId !== config.backendId || session.revoked) deny(401, 'authority_denied')
 if (!Number.isFinite(session.humanRevalidateBy) || !Number.isFinite(session.verifiedHumanSignInAt) || session.humanRevalidateBy <= now || session.humanRevalidateBy > session.verifiedHumanSignInAt + HUMAN_BOUND || session.verifiedHumanSignInAt > now) deny(401, 'human_revalidation_due')
 if (!Number.isFinite(session.expiresAt) || session.expiresAt <= now) deny(401, 'session_expired')
 const member = await meta.get<Member>('member:' + session.memberId)
 if (!member?.enabled || member.generation !== session.generation) deny(403, 'authority_denied')
 const rooms = (await meta.list<MemberRoom>('member-room:' + session.memberId + ':')).map(row => row.value)
  .filter(r => r.memberId === session.memberId && !r.revoked && r.expiresAt > now)
 return { member: member!, rooms: rooms.map(r => r.roomId), expiresAt: session.expiresAt }
}
export async function humanFromHeaders(host: HumanHost, headers: Headers) {
 if (headers.has('authorization')) deny(403, 'verified_human_required')
 const token = cookieValue(headers, 'journey_human')
 const session = token ? await host.meta.get<HumanSession>('browser-session:' + await digest(token)) : null
 if (!session) deny(401, 'human_sign_in_required')
 return { session: session!, sessionDigest: await digest(token!), ...await currentHuman(host.meta, session!) }
}
export async function requireHumanContext(meta: Metadata, admission: Admission | null, url: URL) {
 if (!['_human', '_backend', '_humanAt', '_humanRoom'].some(key => url.searchParams.has(key))) {
  if (admission?.actorType === 'human' && !url.pathname.startsWith('/auth/')) deny(403, 'human_context_required')
  return
 }
 if (admission?.actorType !== 'human' || url.searchParams.get('_human') !== admission.principalId) deny(403, 'identity_changed')
 const session = await meta.get<HumanSession>('browser-session:' + admission.humanSessionDigest)
 if (!session || session.backendId !== url.searchParams.get('_backend') || String(session.verifiedHumanSignInAt) !== url.searchParams.get('_humanAt')) deny(403, 'identity_changed')
 const originalRoom = url.searchParams.get('_humanRoom')
 if (!originalRoom) deny(403, 'human_context_required')
 await registeredHumanRoom(meta, originalRoom!, admission.rooms)
 const targetRoom = url.pathname.startsWith('/connect/') ? decodeURIComponent(url.pathname.slice(9)) : url.searchParams.get('room')
 if (targetRoom !== null && targetRoom !== originalRoom) deny(403, 'room_context_changed')
}
export async function registeredHumanRoom(meta: Metadata, raw: string, rooms: string[]) {
 if (!raw || canonicalRoom(raw) !== raw || !rooms.includes(raw)) deny(403, 'room_denied')
 if (!await meta.get('room:' + raw)) deny(404, 'room_missing')
 return raw
}
export async function permittedRoomCatalog(meta: Metadata, allowed: string[]) {
 return (await meta.list<{ displayName?: string }>('room:'))
  .filter(row => allowed.includes(row.key.slice(5)) && canonicalRoom(row.key.slice(5)) === row.key.slice(5))
  .map(row => ({ roomId: row.key.slice(5), displayName: typeof row.value?.displayName === 'string' && row.value.displayName.trim() ? row.value.displayName.trim() : row.key.slice(5) }))
}
function sameOrigin(host: HumanHost, req: Request) {
 const hostHeader = host.publicRequestUrl ? new URL(req.url).host : req.headers.get('host') || new URL(req.url).host
 if (host.publicRequestUrl && new URL(req.url).origin !== host.origin) deny(403, 'origin_or_csrf_denied')
 if (hostHeader !== new URL(host.origin).host || req.headers.get('origin') !== host.origin || req.headers.get('x-journey-entry') !== '1') deny(403, 'origin_or_csrf_denied')
 if (req.headers.get('content-type')?.split(';')[0] !== 'application/json') deny(403, 'origin_or_csrf_denied')
}
function cookies(origin: string, token: string, csrf: string, expiresAt: number) {
 const flags = '; SameSite=Strict; Path=/' + (new URL(origin).protocol === 'https:' ? '; Secure' : '') + '; Max-Age=' + Math.max(0, Math.floor((expiresAt - Date.now()) / 1000))
 const headers = new Headers({ 'Cache-Control': 'private, no-store' })
 headers.append('Set-Cookie', 'journey_human=' + token + '; HttpOnly' + flags)
 headers.append('Set-Cookie', 'journey_human_csrf=' + csrf + flags)
 return headers
}
async function sessionMaterial() {
 const token = randomSecret(), csrf = randomSecret()
 return { token, csrf, sessionDigest: await digest(token), csrfDigest: await digest(csrf) }
}
export async function humanRoute(host: HumanHost, req: Request): Promise<Response | null> {
 const url = new URL(req.url), path = url.pathname
 if (!path.startsWith('/auth/')) return null
 if (path === '/auth/config' && req.method === 'GET') return Response.json(host.humanConfig ? { enabled: true, mode: host.humanConfig.mode, localReady: !!host.localHumanReady } : { enabled: false })
 if (!host.humanConfig || !host.meta.human) deny(503, 'human_entry_unconfigured')
 if (req.method === 'POST') sameOrigin(host, req)
 if (path === '/auth/rooms' && req.method === 'GET') {
  const human = await humanFromHeaders(host, req.headers)
  await requireHumanContext(host.meta, { actorType: 'human', credentialId: human.member.id, principalId: human.member.id, humanSessionDigest: human.sessionDigest, rooms: human.rooms, cookie: true, expiresAt: human.session.expiresAt }, url)
  return Response.json({ backendId: host.humanConfig.backendId, memberId: human.member.id, rooms: await permittedRoomCatalog(host.meta, human.rooms) })
 }
 if (path === '/auth/entry' && req.method === 'GET') {
  const human = await humanFromHeaders(host, req.headers)
  const rooms: string[] = []
  for (const r of human.rooms) if (await host.meta.get('room:' + r)) rooms.push(r)
  const explicit = url.searchParams.get('room'), remembered = url.searchParams.get('remembered')
  let room: string | null = null
  if (explicit !== null) room = await registeredHumanRoom(host.meta, explicit, human.rooms)
  else if (url.searchParams.get('member') === human.member.id && remembered && rooms.includes(remembered)) room = remembered
  return Response.json({ backendId: host.humanConfig.backendId, memberId: human.member.id, label: human.member.label, rooms, room, expiresAt: human.session.expiresAt, humanRevalidateBy: human.session.humanRevalidateBy, verifiedHumanSignInAt: human.session.verifiedHumanSignInAt, status: room ? 'admitted' : rooms.length ? 'choose_room' : 'no_rooms' })
 }
 if (path === '/auth/local/start' && req.method === 'POST') {
  if (host.humanConfig.mode !== 'local' || !host.localHumanReady) deny(503, 'owner_peer_unavailable')
  const body = await req.json() as any
  if (!/^[a-f0-9]{64}$/.test(body.verifier) || !/^[a-f0-9]{64}$/.test(body.csrf)) deny(400, 'invalid_challenge')
  const result = await host.meta.human('challenge-create', { requestId: crypto.randomUUID(), verifierDigest: await digest(body.verifier), csrfDigest: await digest(body.csrf), origin: host.origin })
  return Response.json(result)
 }
 if (path === '/auth/local/consume' && req.method === 'POST') {
  if (host.humanConfig.mode !== 'local' || !host.localHumanReady) deny(503, 'owner_peer_unavailable')
  const body = await req.json() as any, material = await sessionMaterial()
  if (typeof body.verifier !== 'string' || typeof body.csrf !== 'string' || typeof body.requestId !== 'string') deny(400, 'invalid_challenge')
  const session = await host.meta.human('challenge-consume', { requestId: body.requestId, origin: host.origin, verifierDigest: await digest(body.verifier), csrfDigest: await digest(body.csrf), sessionDigest: material.sessionDigest }) as HumanSession
  return Response.json({ ok: true, expiresAt: session.expiresAt }, { headers: cookies(host.origin, material.token, body.csrf, session.expiresAt) })
 }
 if (path === '/auth/provider/start' && req.method === 'POST') {
  const material = await sessionMaterial(), requestId = crypto.randomUUID()
  await host.meta.human('provider-start', { requestId, verifierDigest: material.sessionDigest })
  const headers = cookies(host.origin, '', '', 0)
  headers.delete('Set-Cookie')
  headers.append('Set-Cookie', 'journey_login=' + material.token + '; HttpOnly; SameSite=Lax; Path=/auth/; Max-Age=60' + (new URL(host.origin).protocol === 'https:' ? '; Secure' : ''))
  return Response.json({ requestId, loginUrl: '/auth/login?state=' + encodeURIComponent(requestId) }, { headers })
 }
 if (path === '/auth/login' && req.method === 'GET') {
  if (host.humanConfig.mode !== 'cloudflare') deny(403, 'provider_unconfigured')
  const token = req.headers.get('cf-access-jwt-assertion') || ''
  const identity = await verifyCloudflareIdentity(token, host.humanConfig)
  const verifier = cookieValue(req.headers, 'journey_login'), requestId = url.searchParams.get('state')
  if (!verifier || !requestId) deny(403, 'login_state_denied')
  const material = await sessionMaterial()
  const session = await host.meta.human('provider-consume', { requestId, verifierDigest: await digest(verifier), identity, sessionDigest: material.sessionDigest, csrfDigest: material.csrfDigest }) as HumanSession
  const headers = cookies(host.origin, material.token, material.csrf, session.expiresAt)
  headers.append('Set-Cookie', 'journey_login=; HttpOnly; SameSite=Lax; Path=/auth/; Max-Age=0' + (new URL(host.origin).protocol === 'https:' ? '; Secure' : ''))
  headers.set('Content-Type', 'text/html; charset=utf-8')
  headers.set('Content-Security-Policy', "default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
  return new Response('<!doctype html><meta charset="utf-8"><title>登入完成</title><p>登入完成，請回到原本的畫布分頁，重新確認入口。</p>', { headers })
 }
 if (['/auth/renew', '/auth/logout'].includes(path) && req.method === 'POST') {
  const human = await humanFromHeaders(host, req.headers)
  await requireHumanContext(host.meta, { actorType: 'human', credentialId: human.member.id, principalId: human.member.id, humanSessionDigest: human.sessionDigest, rooms: human.rooms, cookie: true, expiresAt: human.session.expiresAt }, url)
  const csrf = req.headers.get('x-journey-csrf') || ''
  if (!csrf || csrf !== cookieValue(req.headers, 'journey_human_csrf')) deny(403, 'csrf_denied')
  const result = await host.meta.human(path === '/auth/renew' ? 'renew' : 'logout', { sessionDigest: human.sessionDigest, csrfDigest: await digest(csrf) })
  const token = cookieValue(req.headers, 'journey_human')!
  return Response.json(path === '/auth/logout' ? result : { ok: true, expiresAt: result.expiresAt, verifiedHumanSignInAt: result.verifiedHumanSignInAt, humanRevalidateBy: result.humanRevalidateBy }, { headers: cookies(host.origin, path === '/auth/logout' ? '' : token, path === '/auth/logout' ? '' : csrf, path === '/auth/logout' ? 0 : result.expiresAt) })
 }
 return deny(404, 'unknown_human_operation')
}
