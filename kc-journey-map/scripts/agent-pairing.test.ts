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
 const run = (op: string, input: any, time = now, scopes = scope) => {
  db.exec('BEGIN IMMEDIATE')
  try { const result = agentOperation(store, op, input, scopes, time); db.exec('COMMIT'); return result }
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

test('renewal ignores human seven-day age and inactivity but enforces current authority and exact rotation', async () => {
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
