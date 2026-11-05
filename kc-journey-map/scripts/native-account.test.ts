import assert from 'node:assert/strict'
import { test } from 'node:test'
import { bootstrapHuman, humanOperation, type HumanConfig, type SyncMetadata } from '../server/host/human-store'
import { handle, type Host } from '../server/host/transport'
import { digest } from '../server/host/policy'
const now=Date.now(),origin='http://127.0.0.1:3737',token='synthetic-browser',csrf='synthetic-csrf'
const config:HumanConfig={version:1,backendId:'synthetic',origin,mode:'local',issuer:'local:synthetic',localOwnerUid:501,localMemberId:'owner',members:[
 {id:'owner',issuer:'local:synthetic',subject:'uid:501',label:'Synthetic person',role:'operator',rooms:['one','two','missing'].map(id=>({id,expiresAt:now+3600_000}))}]}
async function fixture(){
 const data=new Map<string,any>(),store:SyncMetadata={get:key=>structuredClone(data.get(key)??null),put:(key,value)=>{data.set(key,structuredClone(value))},delete:key=>{data.delete(key)},list:(prefix,limit)=>[...data].filter(([k])=>k.startsWith(prefix)).sort(([a],[b])=>a.localeCompare(b)).slice(0,limit).map(([key,value])=>({key,value:structuredClone(value)}))}
 bootstrapHuman(store,config)
 for(const room of ['one','two'])store.put('room:'+room,{createdAt:now})
 const sessionDigest=await digest(token),csrfDigest=await digest(csrf)
 store.put('browser-session:'+sessionDigest,{actorType:'human',backendId:'synthetic',memberId:'owner',generation:1,expiresAt:now+900_000,verifiedHumanSignInAt:now,humanRevalidateBy:now+604800_000,csrfDigest,revoked:false})
 return {store,sessionDigest,csrfDigest,context:{sessionDigest,csrfDigest,backendId:'synthetic',memberId:'owner',signInAt:now,roomId:'one'}}
}
test('account read returns exact verified identity and registered current room without mutation',async()=>{
 const {store,context}=await fixture(),before=store.list('',100)
 assert.deepEqual(humanOperation(store,'account-read',context,now),{backendId:'synthetic',memberId:'owner',label:'Synthetic person',roomId:'one'})
 assert.equal(humanOperation(store,'account-read',{...context,roomId:'two'},now).roomId,'two')
 for(const changed of [{backendId:'other'},{memberId:'other'},{signInAt:now-1},{roomId:'denied'},{roomId:'missing'},{csrfDigest:'wrong'},{sessionDigest:'absent'}])assert.throws(()=>humanOperation(store,'account-read',{...context,...changed},now))
 assert.deepEqual(store.list('',100),before)
 for(const changed of [{revoked:true},{expiresAt:now-1}]){
  const key='browser-session:'+context.sessionDigest,session=store.get<any>(key);store.put(key,{...session,...changed})
  assert.throws(()=>humanOperation(store,'account-read',context,now));store.put(key,session)
 }
 store.put('member:owner',{...store.get<any>('member:owner'),enabled:false})
 assert.throws(()=>humanOperation(store,'account-read',context,now))
})
test('account route is default-off, context-bound and denies bearer identity',async()=>{
 const {store,context}=await fixture()
 const host={origin,private:true,humanConfig:config,meta:{get:async(key:string)=>store.get(key),put:async(key:string,value:unknown)=>store.put(key,value),list:async(prefix:string)=>store.list(prefix,100),human:async(op:string,input:any)=>humanOperation(store,op,input)}} as Host
 const query=new URLSearchParams({_human:context.memberId,_backend:context.backendId,_humanAt:String(now),_humanRoom:'one'})
 const request=(path:string,headers:Record<string,string>={})=>handle(host,new Request(origin+path,{headers:{Cookie:'journey_human='+token,...headers}}))
 assert.equal((await request('/auth/account?'+query)).status,404)
 host.nativeAccount=true
 const response=await request('/auth/account?'+query)
 assert.equal(response.status,200);assert.equal(response.headers.get('cache-control'),'private, no-store')
 assert.deepEqual(await response.json(),{backendId:'synthetic',memberId:'owner',label:'Synthetic person',roomId:'one'})
 assert.equal((await request('/auth/account')).status,403)
 assert.equal((await request('/auth/account?'+query,{Authorization:'Bearer synthetic'})).status,403)
 assert.equal((await request('/auth/account?'+new URLSearchParams({...Object.fromEntries(query),_humanRoom:'missing'}))).status,404)
})
test('existing app logout checks context/CSRF, revokes only the session and rejects subsequent account reads',async()=>{
 const {store,context}=await fixture()
 const host={origin,private:true,nativeAccount:true,humanConfig:config,meta:{get:async(key:string)=>store.get(key),put:async(key:string,value:unknown)=>store.put(key,value),list:async(prefix:string)=>store.list(prefix,100),human:async(op:string,input:any)=>humanOperation(store,op,input)}} as Host
 const query=new URLSearchParams({_human:'owner',_backend:'synthetic',_humanAt:String(now),_humanRoom:'one'})
 const post=(q=query,c=csrf)=>handle(host,new Request(origin+'/auth/logout?'+q,{method:'POST',headers:{Origin:origin,'Content-Type':'application/json','X-Journey-Entry':'1','X-Journey-Csrf':c,Cookie:'journey_human='+token+'; journey_human_csrf='+csrf},body:'{}'}))
 assert.equal((await post(query,'wrong')).status,403)
 assert.equal((await post(new URLSearchParams({...Object.fromEntries(query),_human:'other'}))).status,403)
 const before=store.list('member',100),response=await post()
 assert.equal(response.status,200);assert.deepEqual(await response.json(),{loggedOut:true})
 assert.match(response.headers.get('set-cookie')||'',/Max-Age=0/)
 assert.equal(store.get<any>('browser-session:'+context.sessionDigest).revoked,true)
 assert.deepEqual(store.list('member',100),before)
 assert.throws(()=>humanOperation(store,'account-read',context,now),/authority_denied/)
})
