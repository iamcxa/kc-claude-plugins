import { HostError } from './core'
import { HUMAN_BOUND, type HumanConfig } from './human-store'
const reject = (category = 'provider_identity_denied'): never => { throw new HostError(401, category, { category }) }
const decode = (part: string) => Uint8Array.from(atob(part.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0))
async function trustedJson(url: string, init: RequestInit, fetcher: typeof fetch) {
 try {
  const response = await fetcher(url, { ...init, redirect: 'manual', signal: AbortSignal.timeout(10_000) })
  if (!response.ok) throw new Error('provider status')
  const text = await response.text()
  if (text.length > 128_000) throw new Error('provider size')
  return JSON.parse(text)
 } catch { throw new HostError(503, 'provider_unavailable', { category: 'provider_unavailable' }) }
}
export async function verifyCloudflareIdentity(token: string, config: HumanConfig, fetcher: typeof fetch = fetch, now = Date.now()) {
 if (config.mode !== 'cloudflare' || !config.audience || !/^https:\/\/[^/]+$/.test(config.issuer)) reject()
 if (!token || token.length > 32_000 || !/^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/.test(token)) reject()
 let header: any, claims: any, signature: Uint8Array
 const parts = token.split('.')
 try { header = JSON.parse(new TextDecoder().decode(decode(parts[0]))); claims = JSON.parse(new TextDecoder().decode(decode(parts[1]))); signature = decode(parts[2]) } catch { return reject() }
 if (header.alg !== 'RS256' || typeof header.kid !== 'string' || header.crit || (header.typ && header.typ !== 'JWT')) reject()
 if (claims.iss !== config.issuer || !(Array.isArray(claims.aud) ? claims.aud : [claims.aud]).includes(config.audience) || claims.type !== 'app' || typeof claims.sub !== 'string' || !claims.sub.trim() || claims.sub.length > 256 || typeof claims.identity_nonce !== 'string' || !claims.identity_nonce || claims.common_name || claims.service_token_id) reject()
 if (![claims.exp, claims.iat, claims.nbf].every(Number.isFinite) || claims.exp * 1000 <= now || claims.nbf * 1000 > now || claims.iat * 1000 > now || claims.iat >= claims.exp) reject()
 const jwks = await trustedJson(config.issuer + '/cdn-cgi/access/certs', {}, fetcher)
 const matches = Array.isArray(jwks.keys) ? jwks.keys.filter((k: any) => k.kid === header.kid && k.kty === 'RSA' && (!k.alg || k.alg === 'RS256') && (!k.use || k.use === 'sig')) : []
 if (matches.length !== 1 || typeof matches[0].n !== 'string' || decode(matches[0].n).length < 256) reject()
 try {
  const key = await crypto.subtle.importKey('jwk', matches[0], { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify'])
  if (!await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, signature! as BufferSource, new TextEncoder().encode(parts[0] + '.' + parts[1]))) reject()
 } catch { return reject() }
 const identity = await trustedJson(config.issuer + '/cdn-cgi/access/get-identity', { headers: { Cookie: 'CF_Authorization=' + token } }, fetcher)
 if (identity.user_uuid !== claims.sub || identity.service_token_status === true || identity.service_token_id || identity.common_name || !Number.isFinite(identity.iat)) reject()
 const signInAt = identity.iat * 1000
 if (signInAt > now || signInAt > claims.iat * 1000 || signInAt + HUMAN_BOUND <= now) reject('human_revalidation_due')
 return { issuer: config.issuer, audience: config.audience, subject: claims.sub, signInAt }
}
