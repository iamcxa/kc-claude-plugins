import { HostError } from './core'
import { humanFromHeaders, requireHumanContext, randomSecret } from './human'
import { digest } from './policy'
import type { Host } from './transport'
const deny = (status: number, category: string): never => { throw new HostError(status, category, { category }) }
const secret = (value: unknown) => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value)
export async function agentRoute(host: Host, req: Request): Promise<Response | null> {
 const url=new URL(req.url)
 if (!url.pathname.startsWith('/agents/')) return null
 const op=url.pathname.slice(8)
 if (req.method==='GET' && op==='config') return Response.json({ enabled:!!host.agentPairing })
 if (!host.meta.agent || !host.humanConfig || (!host.agentPairing && !['cancel','repair'].includes(op))) deny(503,'agent_pairing_disabled')
 if (req.method!=='POST' || req.headers.get('content-type')?.split(';')[0]!=='application/json') deny(415,'agent_json_required')
 const raw=await req.text()
 if (raw.length>16384) deny(413,'agent_request_too_large')
 const body=JSON.parse(raw)
 if (body?.backendId!==host.humanConfig!.backendId) deny(403,'backend_denied')
 if (['inspect','approve','deny','list','revoke'].includes(op)) {
  const requestHost=host.publicRequestUrl ? url.host : req.headers.get('host') || url.host
  if (requestHost!==new URL(host.origin).host || req.headers.get('origin')!==host.origin || req.headers.get('x-journey-entry')!=='1' || (host.publicRequestUrl && url.origin!==host.origin)) deny(403,'origin_or_csrf_denied')
  const h=await humanFromHeaders(host,req.headers)
  const admission={ credentialId:h.member.id,principalId:h.member.id,actorType:'human' as const,humanSessionDigest:h.sessionDigest,rooms:h.rooms,expiresAt:h.session.expiresAt,cookie:true }
  await requireHumanContext(host.meta,admission,url)
  const result=await host.meta.agent!(op,{ sessionDigest:h.sessionDigest,csrfDigest:await digest(req.headers.get('x-journey-csrf') || ''),memberId:url.searchParams.get('_human'),backendId:url.searchParams.get('_backend'),signInAt:Number(url.searchParams.get('_humanAt')),originalRoom:url.searchParams.get('_humanRoom'),codeDigest:await digest(typeof body.code==='string' ? body.code.toUpperCase().replace(/[- ]/g,'') : ''),familyId:body.familyId,consentId:body.consentId })
  if(op==='list' && host.meta.security)for(const family of result.families)if(family.revokeOperation){try{Object.assign(family,await host.meta.security('progress',{operationId:family.revokeOperation}))}catch{family.streamsStopped='unknown'}}
  return Response.json(result)
 }
 if (req.headers.has('origin') || req.headers.has('cookie') || req.headers.has('authorization')) deny(403,'installation_channel_required')
 if (op==='start') {
  if (!secret(body.verifier)) deny(400,'invalid_verifier')
  const alphabet='ABCDEFGHJKLMNPQRSTUVWXYZ23456789', bytes=crypto.getRandomValues(new Uint8Array(10)), code=[...bytes].map(b=>alphabet[b%32]).join('')
  const result=await host.meta.agent!('create',{ requestId:body.requestId,installationId:body.installationId,memberId:body.memberId,label:body.label,rooms:body.rooms,verifierDigest:await digest(body.verifier),codeDigest:await digest(code) })
  return Response.json({ ...result,code,verificationUrl:host.origin+'/?pair=1' })
 }
 if (['poll','redeem','cancel'].includes(op)) {
  if (!secret(body.verifier)) deny(400,'invalid_verifier')
  const input={ requestId:body.requestId,verifierDigest:await digest(body.verifier) }
  if (op!=='redeem') return Response.json(await host.meta.agent!(op,input))
  const refreshSecret=randomSecret(),accessSecret=randomSecret()
  const result=await host.meta.agent!('redeem',{ ...input,familyId:crypto.randomUUID(),refreshDigest:await digest(refreshSecret),accessId:'agt_'+crypto.randomUUID(),accessDigest:await digest(accessSecret) })
  return Response.json({ ...result,refreshSecret,accessToken:result.credentialId+'.'+accessSecret })
 }
 if (['rotate','repair'].includes(op)) {
  if (!secret(body.secret)) deny(400,'invalid_refresh')
  const input={ familyId:body.familyId,generation:body.generation,secretDigest:await digest(body.secret) }
  if (op==='repair') return Response.json(await host.meta.agent!('repair',input))
  const refreshSecret=randomSecret(),accessSecret=randomSecret()
  const result=await host.meta.agent!('rotate',{ ...input,nextDigest:await digest(refreshSecret),accessId:'agt_'+crypto.randomUUID(),accessDigest:await digest(accessSecret) })
  return Response.json({ ...result,refreshSecret,accessToken:result.credentialId+'.'+accessSecret })
 }
 return deny(404,'agent_route_missing')
}

