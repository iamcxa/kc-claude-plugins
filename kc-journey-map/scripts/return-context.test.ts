import assert from 'node:assert/strict'
import {test} from 'node:test'
import {audited} from '../server/host/audit'
import {securityOperation} from '../server/host/security-store'
import {humanRoute} from '../server/host/human'
import {digest} from '../server/host/policy'

test('shared audit correlates exact human request; final receipt fault leaves mutation unknown and duplicate operation cannot execute again',async()=>{
 const rows=new Map<string,any>(),store={get:(key:string)=>rows.get(key)||null,put:(key:string,v:any)=>{rows.set(key,v)},delete:(key:string)=>{rows.delete(key)},list:()=>[]}
 const session={backendId:'backend',generation:1,verifiedHumanSignInAt:123},member={id:'owner',issuer:'issuer',subject:'subject'}
 rows.set('browser-session:session',session);rows.set('member:owner',member)
 let count=0,failFinal=true
 const host:any={private:true,meta:{get:async(key:string)=>rows.get(key),security:async(op:string,input:any)=>{if(op==='finalize'&&failFinal)throw Error('fixture finalize failure');return securityOperation(store,op,input)}}}
 const actor:any={actorType:'human',humanSessionDigest:'session',principalId:'owner',credentialId:'owner'},patch={put:[],remove:['shape:chosen']}
 await assert.rejects(audited(host,actor,'one','document:PATCH',async()=>{count++;return{ok:true}},'attempt','committed',patch),/mutation_receipt_pending/)
 const receipt=rows.get('security-receipt:attempt')
 assert.equal(count,1);assert.equal(receipt.outcome,'admitted');assert.equal(receipt.final,false)
 assert.equal(receipt.correlation.version,1);assert.equal(receipt.correlation.context.member,'owner');assert.equal(receipt.correlation.context.signInAt,123)
 assert.equal(typeof receipt.correlation.requestHash,'string');assert.equal('humanSessionDigest' in receipt.correlation.context,false)
 failFinal=false
 await assert.rejects(audited(host,actor,'one','document:PATCH',async()=>{count++},'attempt','committed',patch),/operation_already_reserved/)
 assert.equal(count,1)
 host.meta.security=async()=>{throw Error('fixture reserve failure')}
 await assert.rejects(audited(host,actor,'one','document:PATCH',async()=>{count++},'other-attempt','committed',patch),/fixture reserve failure/)
 assert.equal(count,1)
})

test('receipt readback requires current exact human room and original owner; older uncorrelated receipts stay unknown',async()=>{
 const now=Date.now(),rows=new Map<string,any>(),token='synthetic-token'
 rows.set('human-config:v1',{backendId:'backend'});rows.set('member:owner',{id:'owner',issuer:'issuer',subject:'subject',enabled:true,generation:1})
 rows.set('browser-session:'+await digest(token),{actorType:'human',backendId:'backend',memberId:'owner',generation:1,expiresAt:now+60000,verifiedHumanSignInAt:now,humanRevalidateBy:now+604800000,revoked:false})
 rows.set('room:one',{});rows.set('member-room:owner:one',{memberId:'owner',roomId:'one',revoked:false,expiresAt:now+60000})
 const host:any={origin:'https://synthetic.invalid',humanConfig:{backendId:'backend'},meta:{human:()=>{},get:async(key:string)=>rows.get(key),list:async(prefix:string)=>[...rows].filter(([key])=>key.startsWith(prefix)).map(([key,value])=>({key,value}))}}
 const headers={Cookie:'journey_human='+token},query=new URLSearchParams({room:'one',operationId:'attempt',_human:'owner',_backend:'backend',_humanAt:String(now),_humanRoom:'one'})
 const get=()=>humanRoute(host,new Request(host.origin+'/auth/draft-receipt?'+query,{headers}))
 rows.set('security-receipt:attempt',{actorType:'human',memberId:'owner',room:'one',outcome:'committed',final:true})
 await assert.rejects(get(),/draft_receipt_unknown/)
 const value={actorType:'human',memberId:'owner',room:'one',outcome:'committed',final:true,correlation:{version:1,requestHash:'hash',context:{backend:'backend',issuer:'issuer',subject:'subject'}}}
 rows.set('security-receipt:attempt',value);assert.equal((await get())?.status,200)
 rows.set('security-receipt:attempt',{...value,memberId:'other'});await assert.rejects(get(),/draft_receipt_unknown/)
 rows.set('security-receipt:attempt',value);rows.set('member-room:owner:one',{memberId:'owner',roomId:'one',revoked:true,expiresAt:now+60000});await assert.rejects(get(),/room_denied/)
 const identity=await humanRoute(host,new Request(host.origin+'/auth/identity',{headers}));assert.equal(identity?.status,200)
 assert.equal((await identity?.json()).memberId,'owner')
})
