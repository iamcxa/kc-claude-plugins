import { randomBytes, randomUUID } from 'node:crypto'
const secret=()=>randomBytes(32).toString('hex')
export function validateInstallation(config) {
 const url=new URL(config.endpoint)
 if (url.origin!==config.endpoint || url.username || url.password || (url.protocol!=='https:' && !(url.protocol==='http:' && ['127.0.0.1','localhost','[::1]'].includes(url.hostname)))) throw new Error('invalid_installation_endpoint')
 for(const key of ['backendId','installationId','memberId']) if(!/^[a-zA-Z0-9_-]{1,128}$/.test(config[key])) throw new Error('invalid_installation_identity')
 if(!Array.isArray(config.rooms) || !config.rooms.length || typeof config.label!=='string') throw new Error('invalid_installation_scope')
 return config
}
export class PairedInstallation {
 constructor(config, store, fetcher=fetch) { this.config=validateInstallation(config); this.store=store; this.fetcher=fetcher; this.queue=Promise.resolve() }
 exclusive(action) { const result=this.queue.then(action); this.queue=result.catch(()=>{}); return result }
 async saved() {
  const value=this.recovery||await this.store.get()
  if(value && (value.backendId!==this.config.backendId || value.endpoint!==this.config.endpoint)) throw new Error('installation_binding_denied')
  return value
 }
 async request(path,body,headers={}) {
  const response=await this.fetcher(this.config.endpoint+path,{method:body===undefined?'GET':'POST',redirect:'manual',signal:AbortSignal.timeout(15_000),headers:{'Content-Type':'application/json',...headers},...(body===undefined?{}:{body:JSON.stringify(body)})})
  if(response.status>=300 && response.status<400) throw new Error('redirect_denied')
  if(response.status===202) return null
  const result=await response.json()
  if(!response.ok) throw new Error(typeof result.category==='string'?result.category:'agent_request_denied')
  return result
 }
 async save(value) {
  const previous=this.recovery||await this.store.get()
  try {
   await this.store.set(value);const readback=await this.store.get()
   if(JSON.stringify(readback)!==JSON.stringify(value))throw new Error('secure_save_unknown')
   await this.store.confirm();this.recovery=null
  } catch {
   this.recovery={...(previous?.familyId||previous?.verifier?previous:value),state:'repair-pending'}
   throw new Error('repair_required')
  }
 }
 base() { return {backendId:this.config.backendId,endpoint:this.config.endpoint} }
 async begin() { return this.exclusive(async()=>{
  const old=await this.saved()
  if(old && old.state!=='revoked') throw new Error('existing_installation_requires_reconcile')
  const pending={...this.base(),state:'pairing-pending',requestId:randomUUID(),verifier:secret()}
  await this.save(pending)
  try {
   const result=await this.request('/agents/start',{...this.config,...pending})
   return {requestId:result.id,code:result.code,verificationUrl:result.verificationUrl,scopes:result.scopes,expiresAt:result.expiresAt}
  } catch { throw new Error('pairing_outcome_unknown_reconcile') }
 }) }
 async finish() { return this.exclusive(async()=>{
  const pending=await this.saved()
  if(pending?.state!=='pairing-pending') throw new Error('repair_required')
  const result=await this.request('/agents/poll',{backendId:this.config.backendId,requestId:pending.requestId,verifier:pending.verifier})
  if(result.status!=='approved') throw new Error('approval_pending')
  await this.save({...pending,state:'redemption-pending'})
  try {
   const issued=await this.request('/agents/redeem',{backendId:this.config.backendId,requestId:pending.requestId,verifier:pending.verifier})
   this.checkIssued(issued)
   await this.save({...this.base(),state:'active',familyId:issued.family.id,generation:issued.generation,refreshSecret:issued.refreshSecret,accessToken:issued.accessToken,expiresAt:issued.expiresAt})
   return {state:'active',familyId:issued.family.id}
  } catch { throw new Error('repair_required') }
 }) }
 checkIssued(value, familyId) {
  if(!value?.family?.id || value.family.backendId!==this.config.backendId || (familyId && value.family.id!==familyId) || !Number.isSafeInteger(value.generation) || !/^[a-f0-9]{64}$/.test(value.refreshSecret) || !/^agt_[a-zA-Z0-9_-]+\.[a-f0-9]{64}$/.test(value.accessToken) || !Number.isFinite(value.expiresAt) || value.expiresAt<=Date.now()) throw new Error('invalid_issued_material')
 }
 async call(rpc) { return this.exclusive(async()=>{
  let value=await this.saved()
  if(!value) throw new Error('pairing_required')
  if(value.state!=='active') throw new Error('repair_required')
  if(value.expiresAt<=Date.now()+60_000) {
   try { const ready=await this.request('/agents/config'); if(!ready.enabled) throw new Error() } catch { throw new Error('offline_or_unavailable') }
   await this.save({...value,state:'rotation-pending'})
   try {
    const issued=await this.request('/agents/rotate',{backendId:this.config.backendId,familyId:value.familyId,generation:value.generation,secret:value.refreshSecret})
    this.checkIssued(issued,value.familyId)
    if(issued.generation!==value.generation+1) throw new Error('invalid_generation')
    value={...this.base(),state:'active',familyId:issued.family.id,generation:issued.generation,refreshSecret:issued.refreshSecret,accessToken:issued.accessToken,expiresAt:issued.expiresAt}
    await this.save(value)
   } catch { throw new Error('repair_required') }
  }
  return this.request('/mcp',rpc,{Authorization:'Bearer '+value.accessToken})
 }) }
 async reconcile() { return this.exclusive(async()=>{
  const value=await this.saved()
  if(!value) return {state:'unpaired'}
  if(value.state==='revoked') return {state:'revoked'}
  try {
   const result=value.verifier ? await this.request('/agents/cancel',{backendId:this.config.backendId,requestId:value.requestId,verifier:value.verifier})
    : await this.request('/agents/repair',{backendId:this.config.backendId,familyId:value.familyId,generation:value.generation,secret:value.refreshSecret})
   if(result.revoked!==true) throw new Error()
   await this.save({...this.base(),state:'revoked'})
   return {state:'revoked',freshPairingRequired:true}
  } catch { throw new Error('revoke_pending') }
 }) }
 async status() { return this.exclusive(async()=>{ const value=await this.saved(); return {state:value?.state||'unpaired',familyId:value?.familyId||null,automaticRenewal:value?.state==='active'} }) }
}

