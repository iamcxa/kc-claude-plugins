import assert from 'node:assert/strict'
import { test } from 'node:test'
import { bootstrapAgent,agentOperation } from '../server/host/agent-store'
import { bootstrapHuman,type SyncMetadata } from '../server/host/human-store'
test('approval requires the exact inspected original room and sign-in context',()=>{
 const map=new Map(),store:SyncMetadata={get:k=>structuredClone(map.get(k)||null),put:(k,v)=>{map.set(k,structuredClone(v))},delete:k=>{map.delete(k)},list:(p,n)=>[...map].filter(([k])=>k.startsWith(p)).slice(0,n).map(([key,value])=>({key,value}))}
 const now=Date.now(),c={version:1 as const,backendId:'synthetic',origin:'http://127.0.0.1:3737',mode:'local' as const,issuer:'local:test',localOwnerUid:501,localMemberId:'owner',members:[{id:'owner',issuer:'local:test',subject:'uid:501',label:'owner',role:'operator' as const,rooms:['one','two'].map(id=>({id,expiresAt:now+999999}))}]}
 bootstrapHuman(store,c);bootstrapAgent(store,true,{})
 for(const room of ['one','two'])store.put('room:'+room,{})
 store.put('browser-session:session',{actorType:'human',memberId:'owner',backendId:'synthetic',generation:1,expiresAt:now+900000,humanRevalidateBy:now+604800000,verifiedHumanSignInAt:now,csrfDigest:'csrf',revoked:false})
 const scope=(roomId:string)=>({roomId,records:'full-replacement' as const,assets:false,saveDirectory:null,repositories:[]})
 const run=(op:string,input:any)=>agentOperation(store,op,input,scope,now,'https://api.example.test')
 run('create',{requestId:'request',installationId:'installation',memberId:'owner',rooms:['one'],label:'test',verifierDigest:'a'.repeat(64),codeDigest:'b'.repeat(64)})
 const context={sessionDigest:'session',csrfDigest:'csrf',memberId:'owner',backendId:'synthetic',signInAt:now,originalRoom:'one',codeDigest:'b'.repeat(64)}
 const consent=run('inspect',context)
 assert.throws(()=>run('approve',{...context,originalRoom:'two',consentId:consent.consentId}),/consent_context_denied/)
 assert.throws(()=>run('approve',{...context,consentId:'guessed'}),/consent_context_denied/)
 assert.equal(run('approve',{...context,consentId:consent.consentId}).status,'approved')
})
