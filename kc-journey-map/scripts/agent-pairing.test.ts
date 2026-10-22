import assert from 'node:assert/strict'
import { test } from 'node:test'
import { handle, type Host } from '../server/host/transport'
import { DatabaseSync } from 'node:sqlite'
import { bootstrapHuman, humanOperation, type SyncMetadata, type HumanConfig } from '../server/host/human-store'
import { bootstrapAgent, agentOperation, type AgentScope } from '../server/host/agent-store'
import { digest, authenticate } from '../server/host/policy'
import { HostError } from '../server/host/core'

const now = 1_000_000, origin = 'http://127.0.0.1:3737'
const config: HumanConfig = { version: 1, backendId: 'synthetic', origin, mode: 'local', issuer: 'local:test', localOwnerUid: 501, localMemberId: 'owner', members: [
 { id: 'owner', issuer: 'local:test', subject: 'uid:501', label: 'Owner', role: 'operator', rooms: [{ id: 'one', expiresAt: 9e15 }] },
 { id: 'other', issuer: 'local:test', subject: 'uid:502', label: 'Other', role: 'member', rooms: [{ id: 'one', expiresAt: 9e15 }] },
] }
const scope = (roomId: string): AgentScope => ({ roomId, records: 'full-replacement', assets: true, saveDirectory: '/synthetic/owned', repositories: ['synthetic/docs'] })
async function fixture() {
 const db = new DatabaseSync(':memory:'); db.exec('CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)')
 const store: SyncMetadata = {
  get: key => { const row = db.prepare('SELECT value FROM metadata WHERE key=?').get(key) as any; return row ? JSON.parse(row.value) : null },
  put: (key, value) => { db.prepare('INSERT OR REPLACE INTO metadata VALUES(?,?)').run(key, JSON.stringify(value)) },
  delete: key => { db.prepare('DELETE FROM metadata WHERE key=?').run(key) },
  list: (prefix, limit) => db.prepare('SELECT key,value FROM metadata WHERE key>=? AND key<? ORDER BY key LIMIT ?').all(prefix, prefix+'\uffff', limit).map((r: any) => ({ key: r.key, value: JSON.parse(r.value) })),
 }
 bootstrapHuman(store, config); bootstrapAgent(store, true, { synthetic: true }); store.put('room:one', {})
 humanOperation(store, 'challenge-create', { requestId: 'login', origin, verifierDigest: 'v', csrfDigest: 'csrf' }, now)
 humanOperation(store, 'challenge-approve', { requestId: 'login', peerUid: 501 }, now)
 humanOperation(store, 'challenge-consume', { requestId: 'login', origin, verifierDigest: 'v', csrfDigest: 'csrf', sessionDigest: 'human' }, now)
 const human = { sessionDigest: 'human', csrfDigest: 'csrf', memberId: 'owner', backendId: 'synthetic', signInAt: now, originalRoom: 'one' }
 const request = { requestId: crypto.randomUUID(), installationId: crypto.randomUUID(), memberId: 'owner', label: 'self-reported test', rooms: ['one'], verifierDigest: await digest('v'.repeat(64)), codeDigest: await digest('CODE1234') }
 const material = async () => ({ familyId: crypto.randomUUID(), accessId: 'agt_'+crypto.randomUUID(), accessDigest: await digest('a'.repeat(64)), refreshDigest: await digest('r'.repeat(64)) })
 const run = (op: string, input: any, time = now, scopes = scope, endpoint = 'https://api.example.test') => {
  db.exec('BEGIN IMMEDIATE')
  try { const result = agentOperation(store, op, input, scopes, time, endpoint); db.exec('COMMIT'); return result }
  catch (error) { db.exec(error instanceof HostError ? 'COMMIT' : 'ROLLBACK'); throw error }
 }
 const approve=(input:any={...human,codeDigest:request.codeDigest},op='approve')=>{ const consent=run('inspect',input);return run(op,{...input,consentId:consent.consentId}) }
 async function pair() { run('create', request); approve(); const m = await material(); const result = run('redeem', { ...request, ...m }); return { ...result, ...m } }
 return { db, store, run, human, request, material, pair,approve }
}

test('exact authorizer, original verifier and immutable scope gate a one-shot independent family', async () => {
 const f = await fixture(); const { run, request, human, store } = f
 const pending = run('create', request); assert.deepEqual(pending.scopes, [scope('one')]); assert.equal(pending.expiresAt, 1_300_000)
 const saved = store.get<any>('browser-session:human'); store.put('browser-session:other', { ...saved, memberId: 'other' })
 assert.throws(() => run('approve', { ...human, sessionDigest: 'other', memberId: 'other', codeDigest: request.codeDigest }), /authorizer_denied/)
 assert.throws(() => run('approve', { ...human, codeDigest: request.codeDigest, signInAt: now-1 }), /human_context_denied/)
 assert.throws(() => run('approve', { ...human, codeDigest: request.codeDigest }, now, r => ({ ...scope(r), saveDirectory: null })), /scope_changed/)
 f.approve()
 assert.throws(() => run('redeem', { ...request, verifierDigest: 'wrong', ...{} }), /verifier_denied/)
 const m = await f.material(), first = run('redeem', { ...request, ...m })
 assert.equal(first.family.memberId, 'owner'); assert.equal(first.family.installationId, request.installationId)
 assert.equal(first.expiresAt, 1_900_000)
 assert.throws(() => run('redeem', { ...request, ...m }), /request_consumed/)
 assert.throws(() => run('approve', { ...human, codeDigest: request.codeDigest }), /request_consumed/)
 const next = { ...request, requestId: crypto.randomUUID(), installationId: crypto.randomUUID(), codeDigest: await digest('NEXT1234') }
 run('create', next); f.approve({ ...human, codeDigest: next.codeDigest })
 const second = run('redeem', { ...next, ...await f.material() })
 assert.notEqual(first.family.id, second.family.id)
 assert.equal(store.list('agent-family:', 100).length, 2)
 assert.equal(store.list('agent-receipt:', 100).filter(x => x.value.operation === 'redeem').length, 2)
 f.db.close()
})

test('renewal ignores human sign-in age and inactivity but enforces current authority and exact rotation', async () => {
 const f = await fixture(), paired = await f.pair()
 const input = { familyId: paired.family.id, generation: 1, secretDigest: paired.refreshDigest, nextDigest: await digest('n'.repeat(64)), accessId: 'agt_next', accessDigest: await digest('b'.repeat(64)) }
 const renewed = f.run('rotate', input, now + 30*24*3600_000)
 assert.equal(renewed.generation, 2); assert.equal(renewed.expiresAt, now + 30*24*3600_000 + 900_000)
 const before = JSON.stringify(f.store.get('agent-family:'+paired.family.id))
 assert.throws(() => f.run('rotate', { ...input, secretDigest: 'guess' }), /refresh_denied/)
 assert.equal(JSON.stringify(f.store.get('agent-family:'+paired.family.id)), before)
 assert.throws(() => f.run('rotate', input), /refresh_replayed/)
 // Replay revocation must be committed by the production adapter even when the HTTP reply is an error.
 f.db.close()
})

test('cancel authenticates original verifier, tombstones lost redemption and cannot resurrect', async () => {
 const f = await fixture(), paired = await f.pair()
 assert.throws(() => f.run('cancel', { requestId: f.request.requestId, verifierDigest: 'guessed' }), /verifier_denied/)
 assert.equal(f.store.get<any>('agent-family:'+paired.family.id).revoked, false)
 assert.equal(f.run('cancel', f.request).revoked, true)
 assert.equal(f.run('cancel', f.request).revoked, true)
 assert.throws(() => f.run('rotate', { familyId: paired.family.id, generation: 1, secretDigest: paired.refreshDigest }), /family_revoked/)
 const m = await f.material()
 assert.throws(() => f.run('redeem', { ...f.request, ...m }), /request_cancelled/)
 f.db.close()
})

test('expired, denied, removed/regranted and policy-disabled authorities cannot mint or revive', async () => {
 const f = await fixture()
 f.run('create', f.request)
 assert.throws(() => f.run('approve', { ...f.human, codeDigest: f.request.codeDigest }, now+300_000), /request_expired/)
 f.db.close()
 for (const change of ['deny', 'room', 'member', 'policy']) {
  const g = await fixture()
  if (change === 'deny') {
   g.run('create', g.request); g.approve({ ...g.human, codeDigest: g.request.codeDigest },'deny')
   assert.throws(() => g.run('redeem', g.request), /request_denied/)
  } else {
   const p = await g.pair()
   if (change === 'room') for (const revoked of [true,false]) humanOperation(g.store, 'set-room', { memberId: 'owner', roomId: 'one', expiresAt: 9e15, revoked }, now)
   if (change === 'member') { humanOperation(g.store, 'disable-member', { memberId: 'owner' }, now); const m=g.store.get<any>('member:owner'); g.store.put('member:owner', {...m, enabled:true}) }
   if (change === 'policy') { bootstrapAgent(g.store, false, { synthetic: true }); bootstrapAgent(g.store, true, { synthetic: true }) }
   assert.throws(() => g.run('rotate', { familyId:p.family.id, generation:1, secretDigest:p.refreshDigest }), /authority_denied/)
  }
  g.db.close()
 }
})

test('pairing defaults closed before issuing requests or accepting legacy bearer identity', async () => {
 const response = await handle({ private: true, origin: 'http://127.0.0.1:3737', meta: { get: async () => null } } as unknown as Host,
  new Request('http://127.0.0.1:3737/agents/start', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }))
 assert.equal(response.status, 503)
 assert.equal((await response.json()).category, 'agent_pairing_disabled')
})

test('HTTP approval binds current human context and never accepts agent or legacy authorization', async () => {
 const f=await fixture(), token='browser-token', csrf='c'.repeat(64), time=Date.now()
 const session=f.store.get<any>('browser-session:human')
 f.store.put('browser-session:'+await digest(token), {...session, verifiedHumanSignInAt:time, humanRevalidateBy:time+604800_000, expiresAt:time+900_000, csrfDigest:await digest(csrf)})
 const meta={ get:async <T>(k:string)=>f.store.get<T>(k), put:async(k:string,v:unknown)=>f.store.put(k,v), list:async(p:string)=>f.store.list(p,100), agent:async(op:string,input:any)=>f.run(op,input,time) }
 const host={ private:true,origin,humanConfig:config,agentPairing:true,meta,document:async(room:string)=>({room}) } as unknown as Host
 const post=(op:string,body:any,headers:any={})=>handle(host,new Request(origin+'/agents/'+op+'?'+new URLSearchParams({_human:'owner',_backend:'synthetic',_humanAt:String(time),_humanRoom:'one'}),{method:'POST',headers:{'Content-Type':'application/json',...headers},body:JSON.stringify({backendId:'synthetic',...body})}))
 const verifier='e'.repeat(64)
 const started=await post('start',{requestId:f.request.requestId,installationId:f.request.installationId,memberId:'owner',rooms:['one'],label:'test',verifier})
 assert.equal(started.status,200)
 const start=await started.json(), humanHeaders={Cookie:'journey_human='+token,Origin:origin,'X-Journey-Entry':'1','X-Journey-Csrf':csrf}
 assert.equal((await post('approve',{code:start.code},{Authorization:'Bearer legacy.'+'x'.repeat(43),...humanHeaders})).status,403)
 const inspected=await post('inspect',{code:start.code},humanHeaders);const consent=await inspected.json()
 assert.equal((await post('approve',{code:start.code,consentId:consent.consentId},humanHeaders)).status,200)
 const replies=await Promise.all([1,2].map(()=>post('redeem',{requestId:f.request.requestId,verifier})))
 assert.deepEqual(replies.map(r=>r.status).sort(),[200,410])
 const issued=await replies.find(r=>r.status===200)!.json()
 const admission=await authenticate(meta,new Headers({Authorization:'Bearer '+issued.accessToken}))
 assert.equal(admission.actorType,'agent'); assert.deepEqual(admission.rooms,['one'])
 assert.equal((await handle(host,new Request(origin+'/doc?room=two',{headers:{Authorization:'Bearer '+issued.accessToken}}))).status,403)
 assert.equal((await post('approve',{code:start.code},{...humanHeaders,Authorization:'Bearer '+issued.accessToken})).status,403)
 const turn={familyId:issued.family.id,generation:1,secret:issued.refreshSecret}
 const rotations=await Promise.all([1,2].map(()=>post('rotate',turn)))
 assert.deepEqual(rotations.map(r=>r.status).sort(),[200,403])
 assert.equal(f.store.get<any>('agent-family:'+issued.family.id).revoked,true)
 const repaired=await post('repair',turn); assert.equal(repaired.status,200)
 const persisted=JSON.stringify(f.store.list('agent-',1000))
 for(const secret of [verifier,issued.refreshSecret,issued.accessToken.split('.')[1]]) assert.ok(!persisted.includes(secret))
 f.db.close()
})

test('required lifecycle evidence failure rolls back family, access and consume together',async()=>{
 const f=await fixture();f.run('create',f.request);f.approve()
 const original=f.store.put
 f.store.put=(key,value)=>{if(key.startsWith('agent-receipt:') && (value as any).operation==='redeem')throw new Error('receipt storage failed');original(key,value)}
 const m=await f.material()
 assert.throws(()=>f.run('redeem',{...f.request,...m}),/receipt storage failed/)
 assert.equal(f.store.get<any>('agent-request:'+f.request.requestId).status,'approved')
 assert.equal(f.store.get('agent-family:'+m.familyId),null);assert.equal(f.store.get('agent-access:'+m.accessId),null)
 f.store.put=original;assert.equal(f.run('redeem',{...f.request,...m}).generation,1);f.db.close()
})
test('issuance, guesses and polling limits survive denied replies and expired access is refused',async()=>{
 const f=await fixture();f.run('create',f.request)
 f.run('poll',f.request)
 assert.throws(()=>f.run('poll',f.request),/agent_rate_limited/)
 for(let n=0;n<30;n++)assert.throws(()=>f.run('inspect',{...f.human,codeDigest:'f'.repeat(64)}),/authorizer_denied/)
 assert.throws(()=>f.run('inspect',{...f.human,codeDigest:'f'.repeat(64)}),/agent_rate_limited/)
 for(let n=0;n<4;n++)f.run('create',{...f.request,requestId:crypto.randomUUID(),codeDigest:await digest('code'+n)})
 assert.throws(()=>f.run('create',{...f.request,requestId:crypto.randomUUID(),codeDigest:'e'.repeat(64)}),/agent_rate_limited/)
 f.db.close()
 const g=await fixture(),p=await g.pair()
 assert.throws(()=>g.run('admit',{credentialId:p.accessId,secretDigest:p.accessDigest},now+900000),/agent_access_denied/)
 g.db.close()
})
test('legacy ids sharing the agent prefix preserve their original authority and expiry',async()=>{
 const f=await fixture(),secret='d'.repeat(64)
 f.store.put('grant:agt_legacy',{credentialId:'agt_legacy',secretDigest:await digest(secret),principalId:'old-owner-label',rooms:['one'],expiresAt:Date.now()+123456,revoked:false})
 const meta={get:async<T>(key:string)=>f.store.get<T>(key),put:async(k:string,v:unknown)=>f.store.put(k,v),list:async(p:string)=>f.store.list(p,100)}
 const a=await authenticate(meta,new Headers({Authorization:'Bearer agt_legacy.'+secret}))
 assert.equal(a.actorType,'legacy');assert.equal(a.principalId,'old-owner-label')
 f.db.close()
})

test('outgoing send guard rejects absent, expired, malformed and invalidated leases at the actual send boundary',async()=>{
 const {canSend,renewLease}=await import('../server/host/stream-lease')
 const time=Date.now(),lease={streamId:'stream',room:'one',admission:{actorType:'legacy' as const,credentialId:'old',principalId:'old',rooms:['one'],cookie:false,expiresAt:time+100000},leaseUntil:time+30000}
 assert.equal(canSend(lease,time),true)
 for(const bad of [null,{...lease,leaseUntil:NaN},{...lease,leaseUntil:time},{...lease,invalidated:true}])assert.equal(canSend(bad,time),false)
 const meta={get:async()=>{throw new Error('synthetic policy outage')}} as any
 await assert.rejects(renewLease(meta,lease),/synthetic policy outage/)
 assert.equal(lease.leaseUntil,time+30000)
})

test('revocation reserves audit before mutation and waits for actual indexed close acknowledgment',async()=>{
 const {securityOperation}=await import('../server/host/security-store'),f=await fixture(),p=await f.pair()
 const lease={streamId:'passive',room:'one',admission:{actorType:'agent',familyId:p.family.id,credentialId:p.credentialId,principalId:'owner',rooms:['one'],cookie:false,expiresAt:now+900000},leaseUntil:now+30000}
 securityOperation(f.store,'stream-register',lease,now)
 const original=f.store.put
 f.store.put=(key,value)=>{if(key.startsWith('security-receipt:'))throw new Error('audit reservation failed');original(key,value)}
 assert.throws(()=>f.run('revoke',{...f.human,familyId:p.family.id}),/audit reservation failed/)
 assert.equal(f.store.get<any>('agent-family:'+p.family.id).revoked,false)
 f.store.put=original
 const result=f.run('revoke',{...f.human,familyId:p.family.id})
 assert.equal(securityOperation(f.store,'status',result,now).streamsStopped,'stopping')
 assert.equal(securityOperation(f.store,'status',result,now+30001).streamsStopped,'unknown')
 assert.throws(()=>securityOperation(f.store,'stream-register',{...lease,streamId:'late'},now),/stream_denied/)
 securityOperation(f.store,'stream-close',{streamId:'passive'},now+30002)
 assert.equal(securityOperation(f.store,'status',result,now+30002).closeConfirmed,true)
 f.db.close()
})

test('own revoke cannot target another authorizer and an agent cannot operate human or member controls',async()=>{
 const f=await fixture(),p=await f.pair()
 const other={...f.store.get<any>('browser-session:human'),memberId:'other'}
 f.store.put('browser-session:other',other)
 assert.throws(()=>f.run('revoke',{...f.human,sessionDigest:'other',memberId:'other',familyId:p.family.id}),/authorizer_denied/)
 assert.equal(f.store.get<any>('agent-family:'+p.family.id).revoked,false)
 const reply=await handle({private:true,origin,meta:{get:async()=>null},humanConfig:config,agentPairing:true} as any,new Request(origin+'/auth/logout',{method:'POST',headers:{Authorization:'Bearer '+p.credentialId+'.'+'a'.repeat(64),'Content-Type':'application/json',Origin:origin,'X-Journey-Entry':'1'},body:'{}'}))
 assert.notEqual(reply.status,200)
 f.db.close()
})

test('final mutation receipt failure exposes committed pending outcome and a reused operation never repeats mutation',async()=>{
 const {securityOperation}=await import('../server/host/security-store'),{audited}=await import('../server/host/audit'),f=await fixture()
 let effects=0,failFinalize=true
 const host={private:true,meta:{security:async(op:string,input:any)=>{if(op==='finalize'&&failFinalize)throw new Error('synthetic final failure');return securityOperation(f.store,op,input,now)}}} as any
 await assert.rejects(audited(host,null,'one','synthetic',async()=>++effects,'fixed-operation'),(error:any)=>error.details.outcome==='committed_receipt_pending'&&error.details.retry===false)
 assert.equal(effects,1);failFinalize=false
 await assert.rejects(audited(host,null,'one','synthetic',async()=>++effects,'fixed-operation'),/operation_already_reserved/)
 assert.equal(effects,1)
 assert.equal(f.store.get<any>('security-receipt:fixed-operation').final,false)
 f.db.close()
})

test('shared legacy cutover requires every declared consumer in its original room and preserves original expiry',async()=>{
 const {securityOperation}=await import('../server/host/security-store'),f=await fixture(),p=await f.pair()
 const grant={credentialId:'shared',secretDigest:'a'.repeat(64),principalId:'old',rooms:['one'],expiresAt:now+50000,revoked:false}
 f.store.put('grant:shared',grant)
 securityOperation(f.store,'cutover-plan',{credentialId:'shared',synthetic:true,inventoryComplete:true,consumers:[{id:'one',familyId:p.family.id,rooms:['one']},{id:'two',familyId:p.family.id,rooms:['one']}]},now)
 securityOperation(f.store,'cutover-verified',{credentialId:'shared',consumerId:'one',familyId:p.family.id,rooms:['one']},now)
 assert.throws(()=>securityOperation(f.store,'revoke-legacy',{credentialId:'shared'},now),/cutover_consumers_unverified/)
 assert.deepEqual(f.store.get('grant:shared'),grant)
 assert.throws(()=>securityOperation(f.store,'cutover-verified',{credentialId:'shared',consumerId:'two',familyId:p.family.id,rooms:['elsewhere']},now),/cutover_consumer_denied/)
 assert.throws(()=>securityOperation(f.store,'cutover-verified',{credentialId:'shared',consumerId:'two',familyId:p.family.id,rooms:['one']},now+50001),/cutover_legacy_expired_or_changed/)
 securityOperation(f.store,'cutover-verified',{credentialId:'shared',consumerId:'two',familyId:p.family.id,rooms:['one']},now)
 assert.equal(securityOperation(f.store,'revoke-legacy',{credentialId:'shared'},now).revoked,true)
 assert.equal(f.store.get<any>('grant:shared').expiresAt,grant.expiresAt)
 f.db.close()
})

test('security recovery quarantines stale authority and ordinary receipt pruning keeps tombstones and spent proof',async()=>{
 const {securityOperation}=await import('../server/host/security-store'),f=await fixture(),p=await f.pair()
 const archive={format:'journey-security-1',records:f.store.list('',10000).filter(row=>!row.key.startsWith('room:'))}
 f.run('rotate',{familyId:p.family.id,generation:1,secretDigest:p.refreshDigest,nextDigest:'e'.repeat(64),accessId:'agt_new',accessDigest:'d'.repeat(64)})
 const revoked=f.run('revoke',{...f.human,familyId:p.family.id})
 assert.throws(()=>securityOperation(f.store,'restore-security',archive,now),/recovery_requires_fresh_backend_and_member_ids/)
 f.store.put('human-config:v1',{...config,backendId:'recovered',members:[]})
 securityOperation(f.store,'restore-security',archive,now)
 assert.equal(f.store.get<any>('agent-family:'+p.family.id).revoked,true)
 assert.ok(f.store.get('agent-spent:'+p.family.id+':1'))
 assert.equal(f.store.get<any>('member:owner').enabled,false)
 securityOperation(f.store,'prune',{},now+31*24*3600_000)
 assert.ok(f.store.get('security-denial:'+revoked.operationId));assert.ok(f.store.get('agent-spent:'+p.family.id+':1'))
 assert.equal(f.store.list('security-receipt:',100).length,0)
 assert.throws(()=>bootstrapHuman(f.store,config),/immutable/)
 f.db.close()
})

test('two real Node consumers verify sentinel read/write in the original room before shared legacy cutover',async()=>{
 const {mkdtemp,writeFile,chmod}=await import('node:fs/promises'),{tmpdir}=await import('node:os'),{join}=await import('node:path')
 const {NodeHost}=await import('../server/host/node'),{verifyCutoverConsumer}=await import('../server/host/cutover'),{backupPrivateHost}=await import('./private-backup')
 const root=await mkdtemp(join(tmpdir(),'cutover-'));await chmod(root,0o700)
 const secret='d'.repeat(64),grantFile=join(root,'grants.json'),configFile=join(root,'human.json'),dataDir=join(root,'data'),time=Date.now()
 const liveConfig={...config,localOwnerUid:process.geteuid(),members:config.members.map(m=>m.id==='owner'?{...m,subject:'uid:'+process.geteuid()}:{...m,subject:'synthetic-other'})}
 await writeFile(grantFile,JSON.stringify([{credentialId:'shared',secretDigest:await digest(secret),principalId:'old',rooms:['one'],expiresAt:time+600000,revoked:false}]))
 await writeFile(configFile,JSON.stringify(liveConfig))
 const previous={...process.env}
 Object.assign(process.env,{JOURNEY_PRIVATE_DIR:dataDir,JOURNEY_GRANTS_FILE:grantFile,JOURNEY_HUMAN_CONFIG:configFile,JOURNEY_AGENT_PAIRING:'true',JOURNEY_ORIGIN:origin})
 const host=new NodeHost()
 try {
  await host.document('one','GET',null)
  await host.meta.put('browser-session:human',{actorType:'human',backendId:'synthetic',memberId:'owner',generation:1,expiresAt:time+900000,verifiedHumanSignInAt:time,humanRevalidateBy:time+604800000,csrfDigest:'csrf',revoked:false})
  const context={sessionDigest:'human',csrfDigest:'csrf',memberId:'owner',backendId:'synthetic',signInAt:time,originalRoom:'one'}
  async function installation(){
   const request={requestId:crypto.randomUUID(),installationId:crypto.randomUUID(),memberId:'owner',label:'Synthetic cutover consumer',rooms:['one'],verifierDigest:await digest('verifier'),codeDigest:await digest(crypto.randomUUID())}
   await host.meta.agent!('create',request)
   const consent=await host.meta.agent!('inspect',{...context,codeDigest:request.codeDigest})
   await host.meta.agent!('approve',{...context,codeDigest:request.codeDigest,consentId:consent.consentId})
   const accessSecret='e'.repeat(64)
   const issued=await host.meta.agent!('redeem',{...request,familyId:crypto.randomUUID(),refreshDigest:await digest('refresh'),accessId:'agt_'+crypto.randomUUID(),accessDigest:await digest(accessSecret)})
   return authenticate(host.meta,new Headers({Authorization:'Bearer '+issued.credentialId+'.'+accessSecret}))
  }
  const one=await installation(),two=await installation(),before=await host.document('one','GET',null) as any
  await host.meta.security!('cutover-plan',{credentialId:'shared',synthetic:true,inventoryComplete:true,consumers:[{id:'one',familyId:one.familyId,rooms:['one']},{id:'two',familyId:two.familyId,rooms:['one']}]})
  await verifyCutoverConsumer(host,one,'shared','one')
  await assert.rejects(host.revoke('shared'),/cutover_consumers_unverified/)
  assert.equal((await authenticate(host.meta,new Headers({Authorization:'Bearer shared.'+secret}))).expiresAt,time+600000)
  await verifyCutoverConsumer(host,two,'shared','two');assert.equal((await host.revoke('shared')).revoked,true)
  await assert.rejects(authenticate(host.meta,new Headers({Authorization:'Bearer shared.'+secret})),/revoked/)
  assert.deepEqual((await host.document('one','GET',null) as any).snapshot.documents,before.snapshot.documents)
  assert.deepEqual(host.db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all().map((r:any)=>r.name),['metadata'])
  const archive=await backupPrivateHost(host);assert.ok(archive.security?.records.some(r=>r.key.startsWith('security-denial:')))
  await (await import('node:fs/promises')).access(join(dataDir,'.journey-private-v2'))
 }finally{await new Promise(resolve=>setTimeout(resolve,1100));host.close();for(const key of Object.keys(process.env))if(!(key in previous))delete process.env[key];Object.assign(process.env,previous)}
})

test('human and paired-agent leases cannot exceed the current exact room authority expiry',async()=>{
 const {renewLease}=await import('../server/host/stream-lease'),time=Date.now(),expiry=time+1000
 const records:Record<string,any>={'human-config:v1':{backendId:'synthetic'},'member:owner':{id:'owner',enabled:true,generation:1},'browser-session:synthetic':{actorType:'human',backendId:'synthetic',memberId:'owner',generation:1,expiresAt:time+900000,verifiedHumanSignInAt:time,humanRevalidateBy:time+604800000,revoked:false},'member-room:owner:one':{memberId:'owner',roomId:'one',expiresAt:expiry,revoked:false,generation:1}}
 const meta={get:async <T>(key:string)=>records[key] as T||null,list:async(prefix:string)=>Object.entries(records).filter(([key])=>key.startsWith(prefix)).map(([key,value])=>({key,value})),agent:async()=>({credentialId:'synthetic',principalId:'owner',rooms:['one'],expiresAt:time+900000})} as any
 for(const actorType of ['human','agent'] as const){
  const admission={actorType,credentialId:actorType==='human'?'owner':'synthetic',principalId:'owner',humanSessionDigest:'synthetic',familyId:'synthetic-family',expiresAt:time+900000,rooms:['one'],cookie:actorType==='human'}
  const lease=await renewLease(meta,{streamId:'synthetic',room:'one',admission,leaseUntil:0})
  assert.equal(lease.leaseUntil,expiry)
  records['member-room:owner:one'].expiresAt=time-1
  await assert.rejects(renewLease(meta,{...lease,leaseUntil:0}),/stream_denied|stream_room_expired/)
  records['member-room:owner:one'].expiresAt=expiry
 }
})

 test('server-owned endpoint is disclosed/bound, stale pending requests fail closed and issued families stay compatible',async()=>{
 const f=await fixture()
 try {
  const pending=f.run('create',{...f.request,apiEndpoint:'https://attacker.invalid',endpoint:'https://attacker.invalid'})
  assert.equal(pending.apiEndpoint,'https://api.example.test')
  const context={...f.human,codeDigest:f.request.codeDigest},consent=f.run('inspect',context)
  assert.equal(consent.apiEndpoint,'https://api.example.test');assert.equal(consent.origin,origin)
  assert.throws(()=>f.run('approve',{...context,consentId:consent.consentId},now,scope,'https://changed.example.test'),/scope_changed/)
  f.run('approve',{...context,consentId:consent.consentId})
  const issued=await f.material()
  assert.throws(()=>f.run('redeem',{...f.request,...issued},now,scope,'https://changed.example.test'),/scope_changed/)
  const saved=f.store.get<any>('agent-request:'+f.request.requestId);delete saved.apiEndpoint;f.store.put('agent-request:'+f.request.requestId,saved)
  for(const op of ['inspect','approve'])assert.throws(()=>f.run(op,{...context,consentId:consent.consentId}),/scope_changed/)
  assert.throws(()=>f.run('redeem',{...f.request,...issued}),/scope_changed/)
  assert.equal(f.store.get('agent-family:'+issued.familyId),null)
  assert.equal(f.run('cancel',f.request).revoked,true)
 }finally{f.db.close()}
 const g=await fixture()
 try{
  const issued=await g.pair()
  assert.equal('apiEndpoint' in issued.family,false)
  const admitted=g.run('admit',{credentialId:issued.credentialId,secretDigest:issued.accessDigest},now,scope,'https://changed.example.test')
  assert.deepEqual(admitted.rooms,['one'])
  assert.equal(g.run('repair',{familyId:issued.family.id,generation:1,secretDigest:issued.refreshDigest}).revoked,true)
 }finally{g.db.close()}
})
