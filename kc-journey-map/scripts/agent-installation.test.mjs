import assert from 'node:assert/strict'
import { test } from 'node:test'
import { PairedInstallation } from './agent-installation.mjs'

const config={ endpoint:'http://127.0.0.1:3737',backendId:'synthetic',installationId:'synthetic-installation',memberId:'owner',rooms:['one'],label:'test' }
function fixture({lose=false,saveFail=false,confirmFail=false,offline=false,revokeUnknown=false}={}) {
 let data={ state:'active',backendId:'synthetic',endpoint:config.endpoint,familyId:'family',generation:1,refreshSecret:'a'.repeat(64),accessToken:'agt_old.'+'b'.repeat(64),expiresAt:1 },rotations=0,calls=0
 const saves=[]
 let staged
 const store={ get:async()=>structuredClone(staged||data),set:async value=>{ saves.push(value.state); if(saveFail && value.state==='active') throw new Error('save_unknown'); staged=structuredClone(value) },confirm:async()=>{if(confirmFail&&staged.state==='active')throw new Error('confirm_unknown');data=staged;staged=undefined} }
 const fetcher=async(url,init={})=>{
  if(offline) throw new Error('offline')
  if(url.endsWith('/agents/config')) return Response.json({enabled:true})
  if(url.endsWith('/agents/rotate')) { rotations++; assert.equal(data.state,'rotation-pending'); if(lose) throw new Error('lost'); return Response.json({family:{id:'family',backendId:'synthetic'},generation:2,refreshSecret:'c'.repeat(64),accessToken:'agt_new.'+'d'.repeat(64),expiresAt:Date.now()+900000}) }
  if(url.endsWith('/agents/repair')) { if(revokeUnknown) throw new Error('unknown'); assert.equal(JSON.parse(init.body).generation,1); return Response.json({revoked:true,familyId:'family'}) }
  calls++; assert.equal(data.state,'active'); assert.equal(data.generation,2); return Response.json({jsonrpc:'2.0',id:1,result:{ok:true}})
 }
 return {client:new PairedInstallation(config,store,fetcher),store,saves,counts:()=>({rotations,calls}),data:()=>data}
}
test('single-flight rotates once, durably saves before releasing every queued operation',async()=>{
 const f=fixture(); const replies=await Promise.all([1,2,3].map(()=>f.client.call({jsonrpc:'2.0',id:1,method:'ping'})))
 assert.equal(replies.length,3); assert.deepEqual(f.counts(),{rotations:1,calls:3}); assert.deepEqual(f.saves,['rotation-pending','active'])
})
test('lost rotation reply pauses across restarts; only authenticated confirmed revoke permits fresh pairing',async()=>{
 const f=fixture({lose:true}); await assert.rejects(()=>f.client.call({}),/repair_required/)
 const restarted=new PairedInstallation(config,f.store,async()=>{throw new Error('must not send operation')})
 await assert.rejects(()=>restarted.call({}),/repair_required/)
 assert.deepEqual(f.counts(),{rotations:1,calls:0})
 await f.client.reconcile(); assert.equal(f.data().state,'revoked')
})
test('unknown secure-save and unknown revoke keep calls stopped without retrying old refresh',async()=>{
 const f=fixture({saveFail:true,revokeUnknown:true}); await assert.rejects(()=>f.client.call({}),/repair_required/)
 await assert.rejects(()=>f.client.call({}),/repair_required/)
 await assert.rejects(()=>f.client.reconcile(),/revoke_pending/)
 assert.equal(f.data().state,'rotation-pending'); assert.deepEqual(f.counts(),{rotations:1,calls:0})
})
test('ordinary offline preflight retains the family without starting rotation or repair',async()=>{
 const f=fixture({offline:true}); await assert.rejects(()=>f.client.call({}),/offline/)
 assert.equal(f.data().state,'active'); assert.deepEqual(f.counts(),{rotations:0,calls:0})
})
test('failed confirmation cannot release queued calls even when an adapter still exposes active staging',async()=>{
 const f=fixture({confirmFail:true})
 const calls=await Promise.allSettled([1,2,3].map(()=>f.client.call({})))
 assert.ok(calls.every(c=>c.status==='rejected'&&/repair_required/.test(c.reason.message)))
 assert.equal((await f.store.get()).state,'active')
 assert.deepEqual(f.counts(),{rotations:1,calls:0})
 await assert.rejects(()=>f.client.call({}),/repair_required/)
 assert.equal((await f.client.status()).state,'repair-pending')
 assert.equal((await f.client.reconcile()).state,'revoked');assert.equal(f.data().state,'revoked')
})
test('endpoint/backend mismatch and redirects never release an operation or leak its bearer',async()=>{
 const f=fixture(); const wrong=new PairedInstallation({...config,endpoint:'http://127.0.0.1:8888'},f.store,async()=>{throw new Error('must not call')})
 await assert.rejects(()=>wrong.call({}),/installation_binding_denied/)
 f.data().expiresAt=Date.now()+900000
 let sent=0
 const redirected=new PairedInstallation(config,f.store,async(url,init)=>{sent++;assert.equal(url,config.endpoint+'/mcp');assert.equal(init.redirect,'manual');return new Response('',{status:307,headers:{Location:'https://untrusted.invalid/mcp'}})})
 await assert.rejects(()=>redirected.call({}),/redirect_denied/);assert.equal(sent,1)
})
test('lost redemption reply persists original verifier for cancel only before a fresh request',async()=>{
 let data={state:'pairing-pending',backendId:config.backendId,endpoint:config.endpoint,requestId:'original',verifier:'a'.repeat(64)},staged
 const store={get:async()=>structuredClone(staged||data),set:async v=>{staged=structuredClone(v)},confirm:async()=>{data=staged;staged=undefined}}
 let redemptions=0,cancellations=0
 const client=new PairedInstallation(config,store,async(url,init)=>{
  if(url.endsWith('/agents/poll'))return Response.json({status:'approved'})
  if(url.endsWith('/agents/redeem')){redemptions++;throw new Error('lost reply')}
  if(url.endsWith('/agents/cancel')){cancellations++;assert.equal(JSON.parse(init.body).requestId,'original');return Response.json({revoked:true,cancelled:true})}
  throw new Error('unexpected call')
 })
 await assert.rejects(()=>client.finish(),/repair_required/);assert.equal(data.state,'redemption-pending')
 await assert.rejects(()=>client.finish(),/repair_required/);await assert.rejects(()=>client.call({}),/repair_required/)
 await client.reconcile();assert.equal(data.state,'revoked');assert.equal(redemptions,1);assert.equal(cancellations,1)
})
