import assert from 'node:assert/strict'
import { test } from 'node:test'
import { fixture, target, provider, binding, subject, issuer, origin } from './member-enrollment-fixture'
import { runMemberCommand } from './journey-member'
import privateClient from './private-cloudflare-client'
import privateOperator from './private-cloudflare-ops'
const adapters=process.env.JOURNEY_MEMBER_TEST_ADAPTER?[process.env.JOURNEY_MEMBER_TEST_ADAPTER]:['node','cloudflare-local']
for(const adapter of adapters)test(adapter+' recipient normal login-first, private command, exact catalog, own agents and denial',async()=>{
 const now=Math.floor(Date.now()/1000),keys=await crypto.subtle.generateKey({name:'RSASSA-PKCS1-v1_5',modulusLength:2048,publicExponent:new Uint8Array([1,0,1]),hash:'SHA-256'},true,['sign','verify'])
 const jwk={...await crypto.subtle.exportKey('jwk',keys.publicKey),kid:'synthetic',alg:'RS256'}
 const data=Buffer.from(JSON.stringify({alg:'RS256',kid:'synthetic',typ:'JWT'})).toString('base64url')+'.'+Buffer.from(JSON.stringify({type:'app',iss:issuer,aud:['audience'],sub:subject,identity_nonce:'nonce',iat:now,nbf:now,exp:now+300})).toString('base64url')
 const assertion=data+'.'+Buffer.from(await crypto.subtle.sign('RSASSA-PKCS1-v1_5',keys.privateKey,new TextEncoder().encode(data))).toString('base64url')
 const providerFetch=async(req:any)=>{const url=typeof req==='string'?req:req.url;if(url===issuer+'/cdn-cgi/access/certs')return Response.json({keys:[jwk]});assert.equal(url,issuer+'/cdn-cgi/access/get-identity');return Response.json({user_uuid:subject,iat:now-60,service_token_status:false})}
 const h=await fixture(adapter,{providerFetch}),originalFetch=globalThis.fetch
 if(adapter==='node')globalThis.fetch=providerFetch as typeof fetch
 const post={Origin:origin,'Content-Type':'application/json','X-Journey-Entry':'1'}
 const login=async()=>{const start=await h.request('/auth/provider/start',{method:'POST',headers:post,body:'{}'});assert.equal(start.status,200,await start.clone().text());const s:any=await start.json();return h.request(s.loginUrl,{headers:{Cookie:start.headers.get('set-cookie')!.split(';')[0],'Cf-Access-Jwt-Assertion':assertion}})}
 try{
  for(const room of ['one','two'])assert.equal((await h.request('/doc?room='+room,{headers:{Authorization:'Bearer seed.'+'s'.repeat(43)}})).status,200)
  const canvasBefore=await h.request('/doc?room=one',{headers:{Authorization:'Bearer seed.'+'s'.repeat(43)}});const docBefore=await canvasBefore.json()
  const config=await h.get('human-config:v1')
  assert.equal((await login()).status,403);assert.equal(await h.get('member:person'),null)
  const t=target(),token='synthetic-private-operator-token-'.repeat(2)
  const env={JOURNEY_ORIGIN:origin,JOURNEY_GRANTS:JSON.stringify(h.grants),JOURNEY_HUMAN_CONFIG:JSON.stringify(h.config),JOURNEY_OPERATOR_ROOMS:'["one","two"]',JOURNEY_MEMBER_ENROLLMENT:'true',JOURNEY_MEMBER_BINDING:JSON.stringify(binding),REGISTRY:{idFromName:(s:string)=>s,get:()=>({fetch:async(r:Request)=>h.registry.fetch(r.url,{method:r.method,headers:Object.fromEntries(r.headers),body:await r.arrayBuffer()})})},ROOMS:{}}
  const send=async(op:string,input:any)=>{
   if(adapter==='node')return h.member(op,input)
   const r=await privateClient.fetch(new Request('https://operator.synthetic.invalid/',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+token},body:JSON.stringify({op:'member-'+op,writersStopped:true,input})}),{JOURNEY_OPERATOR_TOKEN:token,OPERATOR:{fetch:(r:Request)=>privateOperator.fetch(r,env)}})
   assert.equal(r.status,200,await r.clone().text());return r.json()
  }
  let receipt:any
  const result=await runMemberCommand({op:'enroll',target:t,binding,read:provider().read,send,confirm:async review=>'CONFIRM '+review,save:r=>{receipt=r},candidate:'synthetic-local-integration'})
  assert.equal(result.result,'created');assert.equal(receipt.result.result,'created');assert.equal(receipt.proof.subject,subject)
  if(adapter==='cloudflare-local')for(const headers of [{Origin:origin,Authorization:'Bearer '+token},{Authorization:'Bearer agent.ordinary'},{Cookie:'journey_human=ordinary'}])assert.notEqual((await privateClient.fetch(new Request('https://operator.synthetic.invalid/',{method:'POST',headers:{'Content-Type':'application/json',...headers},body:'{}'}),{JOURNEY_OPERATOR_TOKEN:token,OPERATOR:{fetch:()=>{throw new Error('unauthorized forwarded')}}})).status,200)
  const logged=await login();assert.equal(logged.status,200,await logged.clone().text())
  const cookie=logged.headers.getSetCookie().filter(c=>!c.startsWith('journey_login=')).map(c=>c.split(';')[0]).join('; '),csrf=/journey_human_csrf=([^;]+)/.exec(cookie)![1]
  const context='&_human=person&_backend=synthetic&_humanAt='+((now-60)*1000)+'&_humanRoom=one'
  const catalog=await h.request('/auth/rooms?room=one'+context,{headers:{Cookie:cookie}});assert.equal(catalog.status,200,await catalog.clone().text());const rooms:any=await catalog.json();assert.deepEqual(rooms.rooms.map((r:any)=>r.roomId),['one'])
  assert.equal((await h.request('/doc?room=one'+context,{headers:{Cookie:cookie}})).status,200)
  assert.equal((await h.request('/doc?room=two'+context,{headers:{Cookie:cookie}})).status,403)
  const agent=async(op:string,body:any,approve=false)=>h.request('/agents/'+op+(approve?'?'+context.slice(1):''),{method:'POST',headers:approve?{...post,Cookie:cookie,'X-Journey-Csrf':csrf}:{'Content-Type':'application/json'},body:JSON.stringify({backendId:'synthetic',...body})})
  const requestId=crypto.randomUUID(),verifier='a'.repeat(64)
  const start=await agent('start',{requestId,installationId:crypto.randomUUID(),memberId:'person',rooms:['one'],label:'Synthetic installation',verifier});assert.equal(start.status,200,await start.clone().text());const pending:any=await start.json()
  const inspected=await agent('inspect',{code:pending.code},true);assert.equal(inspected.status,200,await inspected.clone().text());const consent:any=await inspected.json()
  assert.equal((await agent('approve',{code:pending.code,consentId:consent.consentId},true)).status,200)
  const redeem=await agent('redeem',{requestId,verifier});assert.equal(redeem.status,200,await redeem.clone().text());const issued:any=await redeem.json(),auth={Authorization:'Bearer '+issued.accessToken}
  assert.equal((await h.request('/doc?room=one',{headers:auth})).status,200);assert.equal((await h.request('/doc?room=two',{headers:auth})).status,403)
  assert.notEqual((await h.request('/member-enroll',{method:'POST',headers:{...auth,'Content-Type':'application/json'},body:'{}'})).status,200)
  assert.equal((await agent('cancel',{requestId,verifier})).status,200);assert.equal((await h.request('/doc?room=one',{headers:auth})).status,403)
  await h.human('disable-member',{memberId:'person'});assert.equal((await h.request('/doc?room=one'+context,{headers:{Cookie:cookie}})).status,403)
  const final=await h.request('/doc?room=one',{headers:{Authorization:'Bearer seed.'+'s'.repeat(43)}});assert.deepEqual(await final.json(),docBefore);assert.deepEqual(await h.get('human-config:v1'),config)
 }finally{globalThis.fetch=originalFetch;await h.close()}
})
