import assert from 'node:assert/strict'
import { test } from 'node:test'
import { handle, type Host } from '../server/host/transport'

test('disabled human entry is discoverable without treating a bearer as a human', async () => {
 const host = { private: true, origin: 'http://127.0.0.1:3737', meta: { get: async () => null } } as unknown as Host
 const response = await handle(host, new Request('http://127.0.0.1:3737/auth/config'))
 assert.equal(response.status, 200)
 assert.deepEqual(await response.json(), { enabled: false })
})

import { humanOperation, bootstrapHuman, validateHumanConfig, HUMAN_BOUND, type HumanConfig, type SyncMetadata } from '../server/host/human-store'
import { digest } from '../server/host/policy'
const origin = 'http://127.0.0.1:3737'
const config: HumanConfig = { version: 1, backendId: 'synthetic', origin, mode: 'local', issuer: 'local:synthetic', localOwnerUid: 501, localMemberId: 'owner', members: [{ id: 'owner', issuer: 'local:synthetic', subject: 'uid:501', label: 'Synthetic owner', role: 'operator', rooms: [{ id: 'one', expiresAt: 9e15 }] }] }
function fixture() {
 const data = new Map<string, any>()
 const store: SyncMetadata = { get: key => structuredClone(data.get(key) ?? null), put: (key, value) => { data.set(key, structuredClone(value)) }, delete: key => { data.delete(key) }, list: (prefix, limit) => [...data].filter(([k]) => k.startsWith(prefix)).sort().slice(0, limit).map(([key, value]) => ({ key, value: structuredClone(value) })) }
 bootstrapHuman(store, validateHumanConfig(config, origin))
 return { data, store }
}
const challenge = { requestId: 'request', verifierDigest: 'verifier', csrfDigest: 'csrf', origin, sessionDigest: 'session' }
test('local handoff binds owner, original verifier and origin; consumes exactly once', () => {
 const { store } = fixture(), now = 10_000
 humanOperation(store, 'challenge-create', challenge, now)
 assert.throws(() => humanOperation(store, 'challenge-approve', { ...challenge, peerUid: 502 }, now), /owner_peer_denied/)
 humanOperation(store, 'challenge-approve', { ...challenge, peerUid: 501 }, now)
 for (const changed of [{ origin: 'http://localhost:3737' }, { verifierDigest: 'copied' }, { csrfDigest: 'missing' }]) assert.throws(() => humanOperation(store, 'challenge-consume', { ...challenge, ...changed }, now), /challenge_binding_denied/)
 const session = humanOperation(store, 'challenge-consume', challenge, now)
 assert.equal(session.actorType, 'human')
 assert.equal(session.humanRevalidateBy, now + HUMAN_BOUND)
 assert.throws(() => humanOperation(store, 'challenge-consume', challenge, now), /challenge_expired_or_consumed/)
})
test('renewal preserves original event and denies exact seven-day boundary and disabled membership', () => {
 const { store } = fixture(), now = 10_000
 humanOperation(store, 'challenge-create', challenge, now)
 humanOperation(store, 'challenge-approve', { ...challenge, peerUid: 501 }, now)
 let session = humanOperation(store, 'challenge-consume', challenge, now)
 for (let time = now + 600_000; time < now + HUMAN_BOUND; time += 600_000) session = humanOperation(store, 'renew', challenge, time)
 assert.equal(session.verifiedHumanSignInAt, now)
 assert.equal(session.humanRevalidateBy, now + HUMAN_BOUND)
 assert.throws(() => humanOperation(store, 'renew', challenge, now + HUMAN_BOUND), /human_revalidation_due/)
 humanOperation(store, 'disable-member', { memberId: 'owner' }, now)
 assert.throws(() => humanOperation(store, 'renew', challenge, now + 1), /member_denied/)
})
test('expired and unapproved challenges never mint and policy generation blocks removal/regrant resurrection', () => {
 const { store } = fixture(), now = 10_000
 humanOperation(store, 'challenge-create', challenge, now)
 assert.throws(() => humanOperation(store, 'challenge-consume', challenge, now), /approval_pending/)
 assert.throws(() => humanOperation(store, 'challenge-approve', { ...challenge, peerUid: 501 }, now + 60_000), /challenge_expired_or_consumed/)
 humanOperation(store, 'challenge-approve', { ...challenge, peerUid: 501 }, now)
 humanOperation(store, 'challenge-consume', challenge, now)
 for (const revoked of [true, false]) humanOperation(store, 'set-room', { memberId: 'owner', roomId: 'one', revoked, expiresAt: 9e15 }, now)
 assert.throws(() => humanOperation(store, 'renew', challenge, now + 1), /authority_denied/)
})

import { verifyCloudflareIdentity } from '../server/host/human-provider'
import { authenticate } from '../server/host/policy'
const providerConfig: HumanConfig = { ...config, mode: 'cloudflare', issuer: 'https://synthetic.cloudflareaccess.com', audience: 'synthetic-audience', members: [{ ...config.members[0], issuer: 'https://synthetic.cloudflareaccess.com', subject: 'person' }] }
const b64 = (value: string | Uint8Array) => Buffer.from(value).toString('base64url')
test('signed Cloudflare assertion correlates provider login event; token issuance cannot reset age', async () => {
 const now = Date.now(), seconds = Math.floor(now / 1000)
 const keys = await crypto.subtle.generateKey({ name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' }, true, ['sign', 'verify'])
 const jwk = { ...await crypto.subtle.exportKey('jwk', keys.publicKey), kid: 'test', alg: 'RS256' }
 const base = { iss: providerConfig.issuer, aud: [providerConfig.audience], sub: 'person', identity_nonce: 'nonce', type: 'app', iat: seconds, nbf: seconds, exp: seconds + 300 }
 const sign = async (claims: any, alg = 'RS256') => { const body = b64(JSON.stringify({ alg, kid: 'test', typ: 'JWT' })) + '.' + b64(JSON.stringify(claims)); return body + '.' + b64(new Uint8Array(await crypto.subtle.sign('RSASSA-PKCS1-v1_5', keys.privateKey, new TextEncoder().encode(body)))) }
 let identity: any = { user_uuid: 'person', iat: seconds - 600, service_token_status: false }
 const fetcher = async (url: any, init: any) => {
  assert.equal(init.redirect, 'manual')
  if (String(url).endsWith('/certs')) return Response.json({ keys: [jwk] })
  assert.equal(String(url), providerConfig.issuer + '/cdn-cgi/access/get-identity')
  assert.ok(init.headers.Cookie.startsWith('CF_Authorization='))
  return Response.json(identity)
 }
 const valid = await sign(base)
 assert.equal((await verifyCloudflareIdentity(valid, providerConfig, fetcher as any, now)).signInAt, identity.iat * 1000)
 for (const changed of [{ iss: 'https://wrong.invalid' }, { aud: ['wrong'] }, { sub: '' }, { common_name: 'service' }, { exp: seconds }, { identity_nonce: undefined }]) await assert.rejects(() => sign({ ...base, ...changed }).then(token => verifyCloudflareIdentity(token, providerConfig, fetcher as any, now)), /provider_identity_denied/)
 await assert.rejects(() => sign(base, 'none').then(token => verifyCloudflareIdentity(token, providerConfig, fetcher as any, now)), /provider_identity_denied/)
 await assert.rejects(() => verifyCloudflareIdentity(valid.slice(0, -4) + 'xxxx', providerConfig, fetcher as any, now), /provider_identity_denied/)
 identity = { user_uuid: 'different', iat: seconds - 600 }
 await assert.rejects(() => verifyCloudflareIdentity(valid, providerConfig, fetcher as any, now), /provider_identity_denied/)
 identity = { user_uuid: 'person', iat: seconds - 604800 }
 await assert.rejects(() => verifyCloudflareIdentity(valid, providerConfig, fetcher as any, now), /human_revalidation_due/)
 identity = { user_uuid: 'person', iat: seconds - 1, service_token_status: true }
 await assert.rejects(() => verifyCloudflareIdentity(valid, providerConfig, fetcher as any, now), /provider_identity_denied/)
 await assert.rejects(() => verifyCloudflareIdentity(valid, providerConfig, (async () => { throw new Error('outage') }) as any, now), /provider_unavailable/)
})
test('legacy bearer and spoofed identity header do not acquire human provenance', async () => {
 const { store } = fixture(), token = 'x'.repeat(43)
 store.put('grant:legacy', { credentialId: 'legacy', secretDigest: await digest(token), principalId: 'owner', rooms: ['one'], expiresAt: Date.now() + 60_000, revoked: false })
 const meta = { get: async <T>(key: string) => store.get<T>(key), put: async (key: string, value: unknown) => store.put(key, value), list: async (prefix: string) => store.list(prefix, 100), human: async (operation: string, input: any) => humanOperation(store, operation, input) }
 const admission = await authenticate(meta, new Headers({ Authorization: 'Bearer legacy.' + token, 'Cf-Access-Authenticated-User-Email': 'owner' }))
 assert.equal(admission.actorType, 'legacy')
 const response = await handle({ private: true, origin, humanConfig: config, meta } as unknown as Host, new Request(origin + '/auth/entry', { headers: { Authorization: 'Bearer legacy.' + token } }))
 assert.equal(response.status, 403)
 assert.equal(store.list('browser-session:', 100).length, 0)
})

test('a context from another human or original sign-in cannot be used with a replacement cookie', async () => {
 const { store } = fixture(), now = Date.now()
 humanOperation(store, 'challenge-create', challenge, now)
 humanOperation(store, 'challenge-approve', { ...challenge, peerUid: 501 }, now)
 const token = 'human-cookie', sessionDigest = await digest(token)
 humanOperation(store, 'challenge-consume', { ...challenge, sessionDigest }, now)
 store.put('room:one', { createdAt: now })
 const meta = { get: async <T>(key: string) => store.get<T>(key), put: async (key: string, value: unknown) => store.put(key, value), list: async (prefix: string) => store.list(prefix, 100), human: async (operation: string, input: any) => humanOperation(store, operation, input) }
 const host = { private: true, origin, humanConfig: config, meta, document: async () => ({ room: 'one' }) } as unknown as Host
 for (const context of [['_human', 'different'], ['_backend', 'other'], ['_humanAt', String(now - 1)]]) {
  const url = new URL(origin + '/doc?room=one&_human=owner&_backend=synthetic&_humanAt=' + now)
  url.searchParams.set(context[0], context[1])
  assert.equal((await handle(host, new Request(url, { headers: { Cookie: 'journey_human=' + token } }))).status, 403)
 }
 const valid = await handle(host, new Request(origin + '/doc?room=one&_human=owner&_backend=synthetic&_humanAt=' + now, { headers: { Cookie: 'journey_human=' + token } }))
 assert.equal(valid.status, 200)
})

test('entry preserves explicit empty/denied target and empty inventory without creating a document', async () => {
 const { store } = fixture(), now = Date.now(), token = 'synthetic-human'
 humanOperation(store, 'challenge-create', challenge, now)
 humanOperation(store, 'challenge-approve', { ...challenge, peerUid: 501 }, now)
 humanOperation(store, 'challenge-consume', { ...challenge, sessionDigest: await digest(token) }, now)
 const meta = { get: async <T>(key: string) => store.get<T>(key), put: async (key: string, value: unknown) => store.put(key, value), list: async (prefix: string) => store.list(prefix, 100), human: async (operation: string, input: any) => humanOperation(store, operation, input) }
 const host = { private: true, origin, humanConfig: config, meta, document: async () => { throw new Error('must not open a document') } } as unknown as Host
 for (const path of ['/auth/entry?room=', '/auth/entry?room=denied']) assert.equal((await handle(host, new Request(origin + path, { headers: { Cookie: 'journey_human=' + token } }))).status, 403)
 const entry = await handle(host, new Request(origin + '/auth/entry?remembered=one&member=other', { headers: { Cookie: 'journey_human=' + token } }))
 const value = await entry.json()
 assert.deepEqual(value.rooms, []); assert.equal(value.room, null); assert.equal(value.status, 'no_rooms')
 assert.equal(store.list('room:', 100).length, 0)
})
