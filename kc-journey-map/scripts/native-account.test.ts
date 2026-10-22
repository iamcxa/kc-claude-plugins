import assert from 'node:assert/strict'
import { test } from 'node:test'
import { bootstrapHuman, humanOperation, type HumanConfig, type SyncMetadata } from '../server/host/human-store'
const now=Date.now(),origin='http://127.0.0.1:3737'
const config:HumanConfig={version:1,backendId:'synthetic',origin,mode:'local',issuer:'local:synthetic',localOwnerUid:501,localMemberId:'owner',members:[
 {id:'owner',issuer:'local:synthetic',subject:'uid:501',label:'Synthetic owner',role:'operator',rooms:['one','two'].map(id=>({id,expiresAt:now+3600_000}))},
 {id:'member',issuer:'local:synthetic',subject:'ordinary',label:'Synthetic member',role:'operator',rooms:[{id:'one',expiresAt:now+3600_000}]}]}
function fixture(){
 const data=new Map<string,any>(),store:SyncMetadata={get:key=>structuredClone(data.get(key)??null),put:(key,value)=>{data.set(key,structuredClone(value))},delete:key=>{data.delete(key)},list:(prefix,limit,after='')=>[...data].filter(([k])=>k.startsWith(prefix)&&k>after).sort(([a],[b])=>a.localeCompare(b)).slice(0,limit).map(([key,value])=>({key,value:structuredClone(value)}))}
 bootstrapHuman(store,config)
 for(const room of ['one','two'])store.put('room:'+room,{createdAt:now})
 for(const memberId of ['owner','member'])store.put('browser-session:'+memberId,{actorType:'human',backendId:'synthetic',memberId,generation:1,expiresAt:now+900_000,verifiedHumanSignInAt:now,humanRevalidateBy:now+1209600_000,csrfDigest:'csrf',revoked:false})
 return store
}
const binding={backendId:'synthetic',ownerMemberId:'owner',issuer:config.issuer,subject:'uid:501',sessionDigest:'owner',initializationOperationId:'init-owner'}
const context={sessionDigest:'owner',csrfDigest:'csrf',backendId:'synthetic',memberId:'owner',signInAt:now,roomId:'one'}
test('protected owner binding is exact verified create-once; operator role alone grants nothing',()=>{
 const store=fixture()
 assert.equal(humanOperation(store,'account-read',context,now).owner,false)
 for(const changed of [{backendId:'other'},{subject:'ordinary'},{ownerMemberId:'member'},{sessionDigest:'absent'}])assert.throws(()=>humanOperation(store,'owner-bind',{...binding,...changed},now))
 const before=store.list('member',100)
 humanOperation(store,'owner-bind',binding,now)
 assert.deepEqual(store.list('member',100),before)
 assert.equal(humanOperation(store,'account-read',context,now).owner,true)
 assert.equal(humanOperation(store,'account-read',{...context,sessionDigest:'member',memberId:'member'},now).owner,false)
 humanOperation(store,'owner-bind',binding,now)
 assert.throws(()=>humanOperation(store,'owner-bind',{...binding,initializationOperationId:'replace'},now),/owner_binding_exists/)
})
test('room member read requires bound owner and current room, with no grant/session/agent mutation',()=>{
 const store=fixture()
 assert.throws(()=>humanOperation(store,'owner-room-members',context,now),/owner_required/)
 humanOperation(store,'owner-bind',binding,now)
 const before=store.list('',100)
 assert.deepEqual(humanOperation(store,'owner-room-members',context,now).members.map((m:any)=>m.memberId).sort(),['member','owner'])
 assert.deepEqual(humanOperation(store,'owner-room-members',{...context,roomId:'two'},now).members.map((m:any)=>m.memberId),['owner'])
 for(const change of [{sessionDigest:'member',memberId:'member'},{memberId:'member'},{backendId:'other'},{signInAt:now-1},{roomId:'denied'},{csrfDigest:'wrong'}])assert.throws(()=>humanOperation(store,'owner-room-members',{...context,...change},now))
 assert.deepEqual(store.list('',100),before)
 store.put('owner:synthetic',{schemaVersion:9})
 assert.throws(()=>humanOperation(store,'owner-room-members',context,now),/owner_required/)
})
