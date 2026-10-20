import assert from 'node:assert/strict'
import { test } from 'node:test'
import { openSync, closeSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { fixture, provider, binding, target, subject, issuer } from './member-enrollment-fixture'
import { resolveMember } from './member-resolver'
import { runMemberCommand, strictJson, protectedFd } from './journey-member'
import { identityKey } from '../server/host/member-enrollment'
import { HUMAN_BOUND } from '../server/host/human-store'
const adapters=process.env.JOURNEY_MEMBER_TEST_ADAPTER?[process.env.JOURNEY_MEMBER_TEST_ADAPTER]:['node','cloudflare-local']
const input=async(t=target(),operationId=crypto.randomUUID())=>({target:t,proof:await resolveMember(t.email,binding,provider().read),operationId})

test('provider resolution exhausts exact email pagination and never substitutes directory IDs',async()=>{
 const p=provider({pages:[[{id:'unrelated',email:'Person@synthetic.invalid'}],[{id:'directory-id-never-subject',email:'person@synthetic.invalid'}]]})
 const proof=await resolveMember('person@synthetic.invalid',binding,p.read);assert.equal(proof.subject,subject);assert.equal(proof.lookupId,'directory-id-never-subject');assert.equal(p.calls.filter(c=>c.includes('/users?')).length,2)
 for(const changes of [{pages:[[],[]]},{users:[{id:'one',email:'person@synthetic.invalid'},{id:'two',email:'person@synthetic.invalid'}]},{pageInfo:{total_pages:33}},{identity:{user_uuid:'directory-id-never-subject'}},{identity:{account_id:'other'}},{identity:{email:'other@synthetic.invalid'}},{identity:{service_token_status:undefined}},{identity:{service_token_status:true}},{identity:{service_token_id:'service'}},{identity:{common_name:'certificate'}},{identity:{idp:{id:'other'}}},{identity:{iat:Math.floor((Date.now()-HUMAN_BOUND)/1000)}},{identity:{iat:Date.now()}},{organization:{auth_domain:'other.invalid'}},{app:{aud:'other'}},{app:{domain:'entry.synthetic.invalid/path'}},{provider:{type:'oidc'}},{absent:true}])await assert.rejects(resolveMember('person@synthetic.invalid',binding,provider(changes).read))
})
test('strict JSON, empty inputs and owner-only descriptors reject ambiguous command input',async()=>{
 for(const text of ['', '{} {}','{"email":"a","email":"b"}','{"x":{"a":1,"\\u0061":2}}'])assert.throws(()=>strictJson(text))
 assert.deepEqual(strictJson('{"x":[1,true,"ok"]}'),{x:[1,true,'ok']})
 const h=await fixture('node');try{const p=join(h.dir,'protected');writeFileSync(p,'{}',{mode:0o600});const fd=openSync(p,'r');try{assert.equal(protectedFd(fd),fd)}finally{closeSync(fd)}writeFileSync(join(h.dir,'public'),'{}',{mode:0o644});const bad=openSync(join(h.dir,'public'),'r');try{assert.throws(()=>protectedFd(bad))}finally{closeSync(bad)}}finally{await h.close()}
})
for(const adapter of adapters)test(adapter+' actual metadata: atomic exact grant, unchanged replay, retained history and private authority',async()=>{
 const h=await fixture(adapter);try{
  const t=target(),i=await input(t),before=await h.snapshot(),sentinel=await h.get('asset:one:sentinel'),config=await h.get('human-config:v1')
  assert.equal((await h.member('inspect',i)).result,'absent');assert.equal(await h.snapshot(),before)
  for(let at=1;at<=5;at++)for(const after of [false,true]){await h.fault({at,after});const r=await h.member('enroll',i);assert.equal(r.result,'refused',JSON.stringify({at,after,r}));assert.equal(await h.snapshot(),before)}
  await h.fault({commit:true});assert.equal((await h.member('enroll',i)).result,'refused');assert.equal(await h.snapshot(),before);await h.fault(null)
  const results=await Promise.all([h.member('enroll',i),h.member('enroll',{...i,operationId:crypto.randomUUID()})]);assert.deepEqual(results.map(r=>r.result).sort(),['created','no-op'])
  const saved=await h.snapshot();assert.equal((await h.member('enroll',await input(t))).result,'no-op');assert.equal(await h.snapshot(),saved)
  assert.equal((await h.member('enroll',i)).category,'operation_already_reserved')
  assert.equal((await h.get('member:person')).subject,subject);assert.equal((await h.get('member:person')).role,'member');assert.equal(await h.get('member-room:person:two'),null);assert.deepEqual(await h.get('asset:one:sentinel'),sentinel);assert.deepEqual(await h.get('human-config:v1'),config)
  const audit=await h.get('security-receipt:'+i.operationId);assert.equal(audit.final,true);assert.equal(audit.outcome,'committed');assert.equal(audit.memberId,null)
  for(const change of [{label:'Changed'},{memberId:'alternate'},{rooms:[...t.rooms,{roomId:'two',expiresAt:t.rooms[0].expiresAt}]},{rooms:[{roomId:'one',expiresAt:t.rooms[0].expiresAt+1}]}]){const r=await h.member('enroll',await input({...t,...change}));assert.equal(r.result,'conflict');assert.equal(await h.snapshot(),saved)}
  for(const change of [{rooms:[]},{rooms:[{roomId:'*',expiresAt:Date.now()+1e5}]},{rooms:[t.rooms[0],t.rooms[0]]},{rooms:[{roomId:'missing',expiresAt:Date.now()+1e5}]},{role:'operator'},{audience:'other'}])assert.equal((await h.member('enroll',await input({...t,...change} as any))).result,'refused')
  for(const proof of [{...i.proof,subject:'wrong'},{...i.proof,signInAt:Date.now()-HUMAN_BOUND},{...i.proof,accountId:'wrong'},{...i.proof,classification:'self-asserted'}])assert.equal((await h.member('enroll',{...i,proof})).result,'refused')
  assert.equal(await h.snapshot(),saved)
  await h.put('member:person',{...await h.get('member:person'),generation:2});assert.equal((await h.member('enroll',await input(t))).result,'conflict')
  await h.human('disable-member',{memberId:'person'});assert.equal((await h.member('enroll',await input(t))).result,'conflict')
  await h.put(identityKey(issuer,subject),null)
  for(let n=0;n<140;n++)await h.put('member:a'+String(n).padStart(3,'0'),{id:'a'+String(n).padStart(3,'0'),issuer,subject:'unrelated-'+n,label:'Archived',role:'member',enabled:false,generation:2})
  const retained=await h.snapshot();assert.equal((await h.member('enroll',await input({...t,memberId:'new-id'}))).result,'conflict');assert.equal(await h.snapshot(),retained)
  for(const headers of [{Cookie:'journey_human=ordinary'},{Authorization:'Bearer agent.ordinary'}])for(const path of ['/member','/member-enroll','/human','/admin/members'])assert.notEqual((await h.request(path,{method:'POST',headers:{...headers,Origin:h.config.origin,'Content-Type':'application/json'},body:JSON.stringify(i)})).status,200)
 }finally{await h.close()}
})
for(const adapter of adapters)test(adapter+' command cancellation, lost reply/readback, delegation and default off',async()=>{
 const h=await fixture(adapter);try{
  const t=target();let sends=0,receipt:any
  const base={op:'enroll' as const,target:t,binding,read:provider().read,candidate:'synthetic-test-candidate',confirm:async(r:string)=>'CONFIRM '+r,save:(r:any)=>{receipt=r},send:async(op:string,i:any)=>{sends++;return h.member(op,i)}}
  assert.equal((await runMemberCommand({...base,allowedTarget:{...t,memberId:'unapproved'}})).category,'delegated_scope_denied');assert.equal(sends,0)
  const before=await h.snapshot();assert.equal((await runMemberCommand({...base,confirm:async()=> 'cancel'})).category,'cancelled');assert.equal(sends,0);assert.equal(await h.snapshot(),before)
  const result=await runMemberCommand({...base,send:async(op,i)=>{sends++;const r=await h.member(op,i);if(op==='enroll')throw new Error('synthetic dropped postcommit reply');return r}})
  assert.equal(result.result,'unknown');assert.equal(result.readback,'matching-current-state');assert.equal(sends,2);assert.equal(receipt.result.retry,false);assert.equal(receipt.proof.subject,subject)
  const saved=await h.snapshot();let confirmations=0;assert.equal((await runMemberCommand({...base,op:'inspect',confirm:async()=>{confirmations++;return ''}})).result,'matching-current-state');assert.equal(confirmations,0);assert.equal(await h.snapshot(),saved)
  assert.equal((await runMemberCommand({...base,save:()=>{throw new Error('disk full')}})).result,'unknown');assert.equal(await h.snapshot(),saved)
 }finally{await h.close()}
 const off=await fixture(adapter,{enabled:false});try{const before=await off.snapshot();assert.equal((await off.member('enroll',await input())).category,'member_enrollment_disabled');assert.equal(await off.snapshot(),before)}finally{await off.close()}
 if(adapter==='node'){const local=await fixture(adapter,{mode:'local'});try{assert.equal((await local.member('enroll',await input())).category,'remote_enrollment_unsupported')}finally{await local.close()}}
})
for(const adapter of adapters)test(adapter+' multiroom rollback, competing scope, restore quarantine and exact readback',async()=>{
 const h=await fixture(adapter);try{
  const t=target();t.rooms.push({roomId:'two',expiresAt:t.rooms[0].expiresAt});const i=await input(t),before=await h.snapshot()
  for(const at of [4,5,6])for(const after of [false,true]){await h.fault({at,after});assert.equal((await h.member('enroll',i)).result,'refused');assert.equal(await h.snapshot(),before)}await h.fault(null)
  const r=await Promise.all([h.member('enroll',i),h.member('enroll',{...i,target:{...t,rooms:[t.rooms[0]]},operationId:crypto.randomUUID()})]);assert.deepEqual(r.map(x=>x.result).sort(),['conflict','created'])
  assert.equal((await h.member('inspect',i)).rooms.length,2)
  assert.equal((await h.member('inspect',{...i,target:{...t,memberId:'other'}})).result,'conflict')
  assert.equal((await h.member('inspect',i)).receiptAvailable,true)
  const archivedSubject='22222222-2222-4222-8222-222222222222'
  await h.security('restore-security',{format:'journey-security-1',records:[{key:'member:quarantined',value:{id:'quarantined',issuer,subject:archivedSubject,label:'Old',role:'member',enabled:true,generation:1}}]})
  const q={...i,operationId:crypto.randomUUID(),target:{...t,memberId:'quarantined',label:'Old'},proof:{...i.proof,subject:archivedSubject}}
  assert.equal((await h.member('enroll',q)).result,'conflict');assert.equal((await h.get('member:quarantined')).enabled,false)
 }finally{await h.close()}
})
test('Node postcommit exception remains unknown with exact readback and unchanged bootstrap after restart',async()=>{
 const h=await fixture('node');try{const i=await input(),config=await h.get('human-config:v1');await h.fault({commit:true,after:true});assert.equal((await h.member('enroll',i)).result,'unknown');await h.fault(null);assert.equal((await h.member('inspect',i)).result,'matching-current-state');assert.deepEqual(await h.get('human-config:v1'),config)}finally{await h.close()}
})
for(const adapter of adapters)test(adapter+' history scan limit, unknown schema and orphan history fail closed',async()=>{
 const h=await fixture(adapter);try{
  const i=await input();await h.put('member-room:person:one',{memberId:'person',roomId:'one',revoked:true,generation:2,expiresAt:i.target.rooms[0].expiresAt});const before=await h.snapshot();assert.equal((await h.member('enroll',i)).result,'conflict');assert.equal(await h.snapshot(),before)
  await h.put('member:alien',{id:'alien',issuer,subject:'alien',label:'Alien',role:'member',enabled:true,generation:1,unknownFutureField:true});assert.equal((await h.member('enroll',i)).category,'unknown_member_schema')
  for(let n=0;n<4097;n++)await h.put('human-identity:budget-'+String(n).padStart(5,'0'),'unrelated')
  const full=await h.snapshot();assert.equal((await h.member('enroll',i)).category,'incomplete_history_scan');assert.equal(await h.snapshot(),full)
 }finally{await h.close()}
})
