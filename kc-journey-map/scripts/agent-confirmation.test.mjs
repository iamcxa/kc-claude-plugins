import assert from 'node:assert/strict'
import { test } from 'node:test'
import { mkdtemp,writeFile,readFile,chmod,rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { NodeHost } from '../server/host/node.ts'
import { handle } from '../server/host/transport.ts'
import { digest } from '../server/host/policy.ts'
import { PairedInstallation } from './agent-installation.mjs'
import { openProtectedStore } from './agent-protected-store.mjs'

for(const [operation,ambiguousManifest] of [['rotation',false],['redemption',false],['rotation',true]]) {
 test(operation+' confirmation failure blocks queued/repeated calls and survives restart'+(ambiguousManifest?' with an unconfirmed manifest pointer':''),async()=>{
  const root=await mkdtemp(join(tmpdir(),'journey-agent-confirm-')),origin='http://127.0.0.1:3737'
  const config={endpoint:origin,backendId:'synthetic-confirm',installationId:crypto.randomUUID(),memberId:'owner',rooms:['one'],label:'synthetic confirmation'}
  const settings={JOURNEY_PRIVATE_DIR:join(root,'data'),JOURNEY_GRANTS_FILE:join(root,'grants.json'),JOURNEY_HUMAN_CONFIG:join(root,'human.json'),JOURNEY_AGENT_PAIRING:'true',JOURNEY_ORIGIN:origin,JOURNEY_ROOM_REPOS:'{}',JOURNEY_API_PORT:'3737'}
  const previous=Object.fromEntries(Object.keys(settings).map(k=>[k,process.env[k]]))
  let host,store,damaged=false,armed=false,rotations=0,redemptions=0,operations=0,dropRevoke=false
  let failedFamily
  try {
   await writeFile(settings.JOURNEY_GRANTS_FILE,JSON.stringify([{credentialId:'synthetic-seed',secretDigest:await digest('e'.repeat(64)),principalId:'legacy',rooms:['one'],expiresAt:Date.now()+3600000,revoked:false}]),{mode:0o600})
   await writeFile(settings.JOURNEY_HUMAN_CONFIG,JSON.stringify({version:1,backendId:config.backendId,origin,mode:'local',issuer:'local:synthetic-confirm',localOwnerUid:process.geteuid(),localMemberId:'owner',members:[{id:'owner',issuer:'local:synthetic-confirm',subject:'uid:'+process.geteuid(),label:'synthetic owner',role:'operator',rooms:[{id:'one',expiresAt:Date.now()+3600000}]}]}),{mode:0o600})
   Object.assign(process.env,settings);host=new NodeHost();await host.document('one','GET',null)
   const cookie='b'.repeat(64),csrf='c'.repeat(64),login={requestId:crypto.randomUUID(),origin,verifierDigest:await digest('d'.repeat(64)),csrfDigest:await digest(csrf),sessionDigest:await digest(cookie)}
   await host.meta.human('challenge-create',login);await host.meta.human('challenge-approve',{...login,peerUid:process.geteuid()})
   const session=await host.meta.human('challenge-consume',login)
   const human=async(op,body)=>{
    const url=new URL(origin+'/agents/'+op);for(const [k,v]of Object.entries({_human:'owner',_backend:config.backendId,_humanAt:String(session.verifiedHumanSignInAt),_humanRoom:'one'}))url.searchParams.set(k,v)
    const response=await handle(host,new Request(url,{method:'POST',headers:{'Content-Type':'application/json',Host:new URL(origin).host,Origin:origin,Cookie:'journey_human='+cookie,'X-Journey-Entry':'1','X-Journey-Csrf':csrf},body:JSON.stringify({backendId:config.backendId,...body})}))
    assert.equal(response.status,200);return response.json()
   }
   const approve=async code=>{const consent=await human('inspect',{code});await human('approve',{code,consentId:consent.consentId})}
   const fetcher=async(url,init)=>{
    if(url.endsWith('/mcp'))operations++
    if(url.endsWith('/agents/rotate'))rotations++
    if(url.endsWith('/agents/redeem'))redemptions++
    const response=await handle(host,new Request(url,init))
    if(url.endsWith('/agents/repair')||url.endsWith('/agents/cancel')){if(dropRevoke){dropRevoke=false;throw new Error('lost revoke reply')}}
    if(response.ok&&(url.endsWith('/agents/redeem')||url.endsWith('/agents/rotate'))){
     const issued=await response.json();failedFamily??=issued.family.id
     if(operation==='rotation'&&redemptions===1&&url.endsWith('/agents/redeem'))issued.expiresAt=Date.now()+500
     return Response.json(issued)
    }
    return response
   }
   store=await openProtectedStore(config,join(root,'protected'))
   let client=new PairedInstallation(config,store,fetcher)
   const request=await client.begin();await approve(request.code)
   if(operation==='rotation')await client.finish()
   const original=store.set.bind(store)
   store.set=async value=>{
    await original(value)
    if(!armed&&value.state==='active'&&value.generation===(operation==='rotation'?2:1)){
     armed=true
     if(ambiguousManifest){const slots=JSON.parse(await readFile(join(store.directory,'slots.json'),'utf8'));await writeFile(join(store.directory,'manifest.json'),JSON.stringify({slot:slots.at(-1)}),{mode:0o600})}
     await chmod(store.directory,0o500);damaged=true
    }
   }
   const rpc={jsonrpc:'2.0',id:1,method:'tools/call',params:{name:'health'}}
   const attempts=await Promise.allSettled([operation==='rotation'?client.call(rpc):client.finish(),client.call(rpc),client.call(rpc)])
   assert.equal(armed,true)
   assert.deepEqual(attempts.map(r=>r.status),['rejected','rejected','rejected'])
   assert.ok(attempts.every(r=>/repair_required/.test(r.reason.message)))
   assert.equal(operations,0)
   await assert.rejects(()=>client.call(rpc),/repair_required/)
   assert.notEqual((await store.get()).state,'active')
   await chmod(store.directory,0o700);damaged=false
   await store.close();store=await openProtectedStore(config,join(root,'protected'));client=new PairedInstallation(config,store,fetcher)
   assert.notEqual((await client.status()).state,'active')
   await assert.rejects(()=>client.call(rpc),/repair_required/);assert.equal(operations,0)
   assert.equal(rotations,operation==='rotation'?1:0);assert.equal(redemptions,1)
   dropRevoke=true;await assert.rejects(()=>client.reconcile(),/revoke_pending/)
   await assert.rejects(()=>client.call(rpc),/repair_required/)
   assert.equal((await client.reconcile()).state,'revoked')
   assert.equal((await host.meta.get('agent-family:'+failedFamily)).revoked,true)
   const fresh=await client.begin();await approve(fresh.code);const paired=await client.finish()
   assert.notEqual(paired.familyId,failedFamily);assert.equal((await client.call(rpc)).result.structuredContent.rooms[0],'one')
   assert.equal(operations,1);assert.equal((await host.meta.get('agent-family:'+failedFamily)).revoked,true)
  } finally {
   if(store){
    if(damaged)await chmod(store.directory,0o700)
    await store.close();store=await openProtectedStore(config,join(root,'protected'))
    const cleanup=new PairedInstallation(config,store,async(url,init)=>handle(host,new Request(url,init)))
    await cleanup.reconcile();await store.removeRevoked();await store.close()
   }
   host?.close();for(const [k,v]of Object.entries(previous)){if(v===undefined)delete process.env[k];else process.env[k]=v}
   await rm(root,{recursive:true,force:true})
  }
 })
}


for(const failure of ['endpoint','confirmation'])test('start '+failure+' refusal survives real protected-store restart with cancel-only proof',async()=>{
 const root=await mkdtemp(join(tmpdir(),'journey-start-confirm-'))
 const config={endpoint:'http://127.0.0.1:3737',backendId:'start-confirm',installationId:crypto.randomUUID(),memberId:'owner',rooms:['one'],label:'synthetic start confirmation'}
 let store,damaged=false,original
 const paths=[]
 const fetcher=async(url,init)=>{
  const body=JSON.parse(init.body);paths.push(new URL(url).pathname)
  if(url.endsWith('/agents/start')){original=body;return Response.json({id:body.requestId,code:'synthetic',apiEndpoint:failure==='endpoint'?'https://other.invalid':config.endpoint})}
  if(url.endsWith('/agents/cancel')){assert.equal(body.verifier,original.verifier);assert.equal(body.requestId,original.requestId);return Response.json({revoked:true})}
  throw new Error('refused start must not poll, redeem or call MCP')
 }
 try{
  store=await openProtectedStore(config,join(root,'protected'))
  const set=store.set.bind(store)
  store.set=async value=>{await set(value);if(failure==='confirmation'&&value.state==='pairing-pending'){await chmod(store.directory,0o500);damaged=true}}
  let client=new PairedInstallation(config,store,fetcher)
  await assert.rejects(()=>client.begin(),/pairing_outcome_unknown_reconcile/)
  await assert.rejects(()=>client.finish(),/repair_required/)
  if(damaged){await chmod(store.directory,0o700);damaged=false}
  await store.close();store=await openProtectedStore(config,join(root,'protected'));client=new PairedInstallation(config,store,fetcher)
  await assert.rejects(()=>client.finish(),/repair_required/);await assert.rejects(()=>client.call({}),/repair_required/)
  assert.equal((await client.reconcile()).state,'revoked');await store.removeRevoked()
  assert.deepEqual(paths,['/agents/start','/agents/cancel'])
 }finally{
  if(store){if(damaged)await chmod(store.directory,0o700);await store.close();store=await openProtectedStore(config,join(root,'protected'));const client=new PairedInstallation(config,store,fetcher);await client.reconcile();await store.removeRevoked();await store.close()}
  await rm(root,{recursive:true,force:true})
 }
})
