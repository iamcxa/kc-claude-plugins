import assert from 'node:assert/strict'
import { build } from 'esbuild'
import { Miniflare, Log, LogLevel } from 'miniflare'
import { WebSocket } from 'ws'
import { createTLSchema } from '@tldraw/tlschema'
import { getTlsyncProtocolVersion } from '@tldraw/sync-core'
import { spawn, execFileSync } from 'node:child_process'
import { createInterface } from 'node:readline'
import { mkdtemp, mkdir, writeFile, readFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { join } from 'node:path'
import { createServer } from 'node:net'
const root=new URL('..',import.meta.url).pathname.replace(/\/$/,'')
const adapter=process.argv[2]
if(!['node','cloudflare-local'].includes(adapter))throw new Error('node or cloudflare-local required; synthetic only')
await mkdir(join(root,'.host-check'),{recursive:true})
const scratch=await mkdtemp(join(root,'.host-check/revocation-'))
const privateDir=await mkdtemp('/tmp/revoke-store-');await import('node:fs/promises').then(fs=>fs.chmod(privateDir,0o700))
const hash=s=>createHash('sha256').update(s).digest('hex'),sleep=ms=>new Promise(r=>setTimeout(r,ms))
const port=await new Promise(resolve=>{const server=createServer();server.listen(0,'127.0.0.1',()=>{const p=server.address().port;server.close(()=>resolve(p))})})
const origin=adapter==='node'?'http://127.0.0.1:'+port:'https://revoke.synthetic.invalid'
const api='http://127.0.0.1:'+port,secret='s'.repeat(64),seed={Authorization:'Bearer seed.'+secret},time=Date.now()
const grants=[{credentialId:'seed',secretDigest:hash(secret),principalId:'legacy',rooms:['one','two'],expiresAt:time+3600000,revoked:false}]
const config={version:1,backendId:'synthetic-revoke',origin,mode:adapter==='node'?'local':'cloudflare',issuer:adapter==='node'?'local:revoke':'https://issuer.synthetic.invalid',audience:'synthetic',localOwnerUid:process.geteuid(),localMemberId:'owner',members:[{id:'owner',issuer:adapter==='node'?'local:revoke':'https://issuer.synthetic.invalid',subject:adapter==='node'?'uid:'+process.geteuid():'synthetic-subject',label:'Synthetic owner',role:'operator',rooms:[{id:'one',expiresAt:time+3600000}]}]}
const report={adapter,candidate:execFileSync('git',['-C',root,'rev-parse','HEAD'],{encoding:'utf8'}).trim(),dirty:!!execFileSync('git',['-C',root,'status','--porcelain'],{encoding:'utf8'}).trim(),provider:'NOT RUN; human identity fixture only',physicalDevice:'NOT RUN',time:'actual Date.now; fault controls are injected separately',checks:[],enqueues:[],receives:[],closes:[]}
const logs=[],pending=new Map(),clients=[]
let child,mf,registry,serverBundle,script,mfOptions
const instrumentation={name:'synthetic-revocation-faults',setup(builder){builder.onLoad({filter:/host\/(node|cloudflare)\.ts$/},async args=>{
 let contents=await readFile(args.path,'utf8')
 if(args.path.endsWith('/node.ts'))contents=contents.replace('socket.send(data)',"console.log(JSON.stringify({enqueue:entry.lease?.admission.credentialId,at:Date.now()}));socket.send(data)")
 else {
  contents=contents.replace('ws.send(data)',"console.log(JSON.stringify({enqueue:ws.deserializeAttachment().admission.credentialId,at:Date.now()}));ws.send(data)")
  contents=contents.replace("  const body = await req.json() as any","  const body = await req.json() as any\n  if(new URL(req.url).pathname==='/synthetic-fault'){this.put('synthetic:fault',body);return Response.json({ok:true})}\n  const fault=this.get('synthetic:fault')\n  if(fault?.outage && ((new URL(req.url).pathname==='/agent' && body.operation==='current') || (new URL(req.url).pathname==='/get' && /^(browser-session:|human-config:|member:|member-room:)/.test(body.key))))return Response.json({error:'synthetic policy outage'},{status:503})")
  contents=contents.replace('   const url=new URL(req.url)',`   const url=new URL(req.url)
   if(url.pathname==='/internal/synthetic-case'){
    const body=await req.json() as any
    for(const ws of this.ctx.getWebSockets()){
     const a=ws.deserializeAttachment()
     if(body.credentialId && a.admission.credentialId===body.credentialId && body.action==='queued-expiry'){
      const queued=this.socket(ws);ws.serializeAttachment({...a,leaseUntil:Date.now()-1});queued.send('SYNTHETIC_QUEUED_AFTER_EXPIRY')
     }
    }
    if(body.action==='duplicate-alarm'){await this.alarm();await this.alarm()}
    return Response.json({alarm:await this.ctx.storage.getAlarm(),attachments:this.ctx.getWebSockets().map((ws:any)=>{const a=ws.deserializeAttachment();return {streamId:a.streamId,credentialId:a.admission.credentialId,leaseUntil:a.leaseUntil,invalidated:a.invalidated}})})
   }`)
  contents=contents.replace(' async notifyResult(result: any) {'," async notifyResult(result: any) {\n  if(this.get('synthetic:fault')?.missed)return result")
 }
 return {contents,loader:'ts'}
})
if(adapter==='node')builder.onLoad({filter:/canvas-server\.ts$/},async args=>({loader:'ts',contents:(await readFile(args.path,'utf8')).replace('const host = new NodeHost()',`const host = new NodeHost()
let fault={missed:false,outage:false};const notify=host.notifyResult.bind(host),get=host.meta.get.bind(host.meta),agent=host.meta.agent.bind(host.meta)
host.notifyResult=async result=>fault.missed?result:notify(result)
host.meta.get=async key=>{if(fault.outage&&/^(browser-session:|human-config:|member:|member-room:)/.test(key))throw new Error('synthetic policy outage');return get(key)}
host.meta.agent=async(op,input)=>{if(fault.outage&&op==='current')throw new Error('synthetic policy outage');return agent(op,input)}`)
.replace("const result = command.op === 'revoke' ?", "const result = command.op === 'synthetic-fault' ? (fault=command.fault,{ok:true}) : command.op==='synthetic-metadata' ? (command.operation==='get'?await host.meta.get(command.input.key):await host.meta.security(command.operation,command.input)) : command.op==='synthetic-alarm' ? {ok:true} : command.op === 'revoke' ?")}))}}
const logLine=line=>{logs.push(line);try{const value=JSON.parse(line);if(value.enqueue)report.enqueues.push(value);if(value.control){pending.get(value.control)?.(value.result);pending.delete(value.control)}}catch{}}
async function start(){
 if(adapter==='node'){
  const grantFile=join(scratch,'grants.json'),configFile=join(scratch,'human.json')
  await writeFile(grantFile,JSON.stringify(grants));await writeFile(configFile,JSON.stringify(config))
  serverBundle=join(scratch,'server.mjs')
  await build({entryPoints:[join(root,'server/canvas-server.ts')],outfile:serverBundle,bundle:true,format:'esm',platform:'node',packages:'external',plugins:[instrumentation],logLevel:'silent'})
  child=spawn(process.execPath,[serverBundle],{cwd:root,stdio:['pipe','pipe','pipe'],env:{...process.env,JOURNEY_PRIVATE_DIR:privateDir,JOURNEY_ORIGIN:origin,JOURNEY_API_PORT:String(port),JOURNEY_GRANTS_FILE:grantFile,JOURNEY_HUMAN_CONFIG:configFile,JOURNEY_AGENT_PAIRING:'true',JOURNEY_CONTROL_STDIO:'1'}})
  createInterface({input:child.stdout}).on('line',logLine);child.stderr.on('data',data=>logs.push(String(data)))
  for(let i=0;i<150;i++){try{if((await fetch(api+'/health',{headers:seed})).ok)return}catch{}if(child.exitCode!==null)throw new Error(logs.join('\n'));await sleep(50)}
  throw new Error('node startup timed out '+logs.join('\n'))
 }
 const bundle=await build({entryPoints:[join(root,'server/host/cloudflare.ts')],bundle:true,write:false,format:'esm',platform:'browser',conditions:['workerd','worker','browser'],external:['cloudflare:workers'],plugins:[instrumentation],logLevel:'silent'})
 script=bundle.outputFiles[0].text
 class Capture extends Log{log(message){logLine(message)}}
 mfOptions={script,modules:true,compatibilityDate:'2026-07-01',compatibilityFlags:['nodejs_compat'],host:'127.0.0.1',port,log:new Capture(LogLevel.INFO,{prefix:'',suffix:''}),bindings:{JOURNEY_ORIGIN:origin,JOURNEY_GRANTS:JSON.stringify(grants),JOURNEY_HUMAN_CONFIG:JSON.stringify(config),JOURNEY_AGENT_PAIRING:'true'},durableObjects:{ROOMS:{className:'JourneyRoom',useSQLite:true},REGISTRY:{className:'JourneyRegistry',useSQLite:true}},durableObjectsPersist:join(scratch,'objects')}
 mf=new Miniflare(mfOptions)
 await mf.ready;const namespace=await mf.getDurableObjectNamespace('REGISTRY');registry=namespace.get(namespace.idFromName('private-pilot'))
}
const control=command=>new Promise((resolve,reject)=>{const id=crypto.randomUUID();pending.set(id,resolve);child.stdin.write(JSON.stringify({id,...command})+'\n');setTimeout(()=>{if(pending.delete(id))reject(new Error('control timeout'))},5000).unref()})
const metadata=async(operation,input)=>{
 if(adapter==='node')return control({op:'synthetic-metadata',operation,input})
 const r=await registry.fetch('https://registry/'+(operation==='get'?'get':'security'),{method:'POST',body:JSON.stringify(operation==='get'?input:{operation,input})});assert.equal(r.status,200,await r.clone().text());return r.json()
}
const fault=async value=>adapter==='node'?control({op:'synthetic-fault',fault:value}):registry.fetch('https://registry/synthetic-fault',{method:'POST',body:JSON.stringify(value)})
const request=(path,options={})=>{
 const {headers={},body,method='GET'}=options
 const init={method,headers:{Host:new URL(origin).host,...headers},...(body===undefined?{}:{body:JSON.stringify(body)})}
 return adapter==='node'?fetch(api+path,init):mf.dispatchFetch(origin+path,init)
}
async function data(path,options){const r=await request(path,options);assert.equal(r.status,200,await r.clone().text());return r.json()}
let cookie,csrf,signInAt
const context=()=>new URLSearchParams({_human:'owner',_backend:config.backendId,_humanAt:String(signInAt),_humanRoom:'one'})
const post=(op,body,human=false)=>request('/agents/'+op+(human?'?'+context():''),{method:'POST',headers:{'Content-Type':'application/json',...(human?{Cookie:cookie,Origin:origin,'X-Journey-Entry':'1','X-Journey-Csrf':csrf}:{})},body:{backendId:config.backendId,...body}})
async function login(){
 if(adapter==='node'){
  const verifier='a'.repeat(64);csrf='b'.repeat(64)
  const headers={Origin:origin,'X-Journey-Entry':'1','Content-Type':'application/json'}
  const pending=await data('/auth/local/start',{method:'POST',headers,body:{verifier,csrf}})
  execFileSync('python3',[join(root,'scripts/owner-login.py'),join(privateDir,'owner-login.sock'),pending.requestId],{input:'approve\n',encoding:'utf8'})
  const r=await request('/auth/local/consume',{method:'POST',headers,body:{...pending,verifier,csrf}});assert.equal(r.status,200,await r.clone().text());cookie=r.headers.getSetCookie().map(c=>c.split(';')[0]).join('; ')
  const entry=await data('/auth/entry?room=one',{headers:{Cookie:cookie}});signInAt=entry.verifiedHumanSignInAt
 }else{
  const token='h'.repeat(64);csrf='c'.repeat(64);signInAt=Date.now();cookie='journey_human='+token+'; journey_human_csrf='+csrf
  const value={actorType:'human',backendId:config.backendId,memberId:'owner',generation:1,expiresAt:Date.now()+900000,verifiedHumanSignInAt:signInAt,humanRevalidateBy:signInAt+604800000,csrfDigest:hash(csrf),revoked:false}
  const r=await registry.fetch('https://registry/put',{method:'POST',body:JSON.stringify({key:'browser-session:'+hash(token),value})});assert.equal(r.status,200)
 }
}
async function pair(label){
 const verifier='a'.repeat(64),requestId=crypto.randomUUID()
 const started=await post('start',{requestId,installationId:crypto.randomUUID(),memberId:'owner',rooms:['one'],label,verifier});assert.equal(started.status,200,await started.clone().text());const p=await started.json()
 const inspected=await post('inspect',{code:p.code},true);assert.equal(inspected.status,200,await inspected.clone().text());const consent=await inspected.json()
 assert.equal((await post('approve',{code:p.code,consentId:consent.consentId},true)).status,200)
 const issued=await post('redeem',{requestId,verifier});assert.equal(issued.status,200,await issued.clone().text());return issued.json()
}
async function socket(issued){
 const id=crypto.randomUUID(),credentialId=issued?.credentialId||'human'
 const path='/connect/one?sessionId='+id+(issued?'':'&'+context())
 let ws
 ws=await new Promise((resolve,reject)=>{const s=new WebSocket(api.replace('http','ws')+path,{headers:{Host:new URL(origin).host,Origin:origin,...(issued?{Authorization:'Bearer '+issued.accessToken}:{Cookie:cookie})}});s.once('open',()=>resolve(s));s.once('error',reject)})
 clients.push(ws)
 const observed={credentialId,connectedAt:Date.now(),lastReceive:null,closedAt:null,messages:[],close:new Promise(resolve=>{
  const closed=()=>{observed.closedAt=Date.now();report.closes.push({credentialId,at:observed.closedAt});resolve()}
  ws.once('close',closed)
 })}
 const receive=data=>{const text=typeof data==='string'?data:data.toString();observed.lastReceive=Date.now();observed.messages.push(text);report.receives.push({credentialId,at:observed.lastReceive});}
 ws.on('message',receive)
 ws.send(JSON.stringify({type:'connect',connectRequestId:id,lastServerClock:-1,protocolVersion:getTlsyncProtocolVersion(),schema:createTLSchema().serialize()}))
 for(let i=0;i<100&&!observed.messages.some(m=>m.includes('connect'));i++)await sleep(20)
 assert.ok(observed.messages.some(m=>m.includes('connect')),'stream handshake not received')
 return observed
}
const pass=name=>{report.checks.push(name);console.log('PASS '+name)}
async function assertDenied(issued){
 const headers={Authorization:'Bearer '+issued.accessToken},before=await data('/doc?room=one',{headers:seed}),fingerprint=hash(JSON.stringify(before.snapshot.documents))
 for(const [path,method,body]of [['/doc?room=one','GET'],['/doc?room=one','PATCH',{put:[],remove:[]}],['/uploads/no?room=one','PUT',{}],['/mcp','POST',{jsonrpc:'2.0',id:1,method:'tools/call',params:{name:'patch_doc',arguments:{room:'one',body:{put:[],remove:[]}}}}],['/connect/one?sessionId=denied','GET']]){const r=await request(path,{method,headers:{...headers,'Content-Type':'application/json',Origin:origin},body});assert.ok([401,403].includes(r.status),path+' '+r.status)}
 assert.equal(hash(JSON.stringify((await data('/doc?room=one',{headers:seed})).snapshot.documents)),fingerprint)
}
try{
 await start();await data('/doc?room=one',{headers:seed});await login()
 const one=await pair('Synthetic first'),two=await pair('Synthetic second')
 const first=await socket(one),second=await socket(two),human=await socket()
 const revoke=await post('revoke',{familyId:one.family.id},true);assert.equal(revoke.status,200,await revoke.clone().text());const receipt=await revoke.json();report.firstDenial={deniedAt:receipt.deniedAt,commitObservedAt:receipt.denialCommitObservedAt,receivedAt:Date.now(),state:receipt.streamsStopped}
 await Promise.race([first.close,sleep(5000).then(()=>{throw new Error('fanout did not close client')})]);await assertDenied(one)
 assert.equal(second.closedAt,null);assert.equal(human.closedAt,null)
 const update={id:'page:synthetic',typeName:'page',name:'After first revoke',index:'a1',meta:{}}
 await data('/doc?room=one',{method:'PATCH',headers:{...seed,'Content-Type':'application/json'},body:{put:[update]}});await sleep(150)
 assert.ok(second.messages.some(m=>m.includes('After first revoke')));assert.ok(!first.messages.some(m=>m.includes('After first revoke')))
 pass('own family denial closes actual client while independent installation and browser continue; HTTP/MCP/assets/reconnect denied hashes unchanged')
 if(process.env.JOURNEY_REVOKE_SEAMS_ONLY!=='true'){
 await fault({missed:true})
 const revokeStarted=Date.now(),result=await post('revoke',{familyId:two.family.id},true);assert.equal(result.status,200);const denied=await result.json();report.missedFanout={deniedAt:denied.deniedAt,commitObservedAt:denied.denialCommitObservedAt,replyAt:Date.now()}
 await assertDenied(two)
 while(second.closedAt===null&&Date.now()-revokeStarted<45000){update.name='Lease update '+Date.now();await data('/doc?room=one',{method:'PATCH',headers:{...seed,'Content-Type':'application/json'},body:{put:[update]}});await sleep(500)}
 assert.ok(second.closedAt,'missed fanout never closed passive stream');assert.ok(second.closedAt-denied.deniedAt<=60000)
 report.missedFanout={...report.missedFanout,closedAt:second.closedAt,closeMs:second.closedAt-denied.deniedAt,lastClientReceipt:second.lastReceive,lastServerEnqueue:report.enqueues.filter(e=>e.enqueue===two.credentialId).at(-1)?.at}
 assert.ok(second.lastReceive-denied.deniedAt<30000)
 pass('missed fanout passive stream closes on actual 30-second lease; last enqueue, receipt, close and denial commit recorded separately')
 await fault({missed:false})
 let progress;for(let i=0;i<40;i++){progress=await metadata('progress',{operationId:denied.operationId});if(progress.streamsStopped==='stopped')break;await sleep(50)}assert.equal(progress.streamsStopped,'stopped')
 pass('close acknowledgment updates durable progress independently of committed denial')
 const third=await pair('Synthetic outage'),thirdStream=await socket(third)
 await fault({outage:true,missed:true});const outageAt=Date.now()
 await Promise.race([thirdStream.close,sleep(40000).then(()=>{throw new Error('policy outage left stream alive')})]);assert.ok(thirdStream.closedAt-outageAt<=60000)
 report.outage={startedAt:outageAt,closedAt:thirdStream.closedAt,lastClientReceipt:thirdStream.lastReceive}
 await fault({})
 pass('authoritative policy outage closes passive actual stream without an incoming message or successful renewal')
 }
 if(process.env.JOURNEY_REVOKE_SEAMS_ONLY==='true'){
  if(adapter==='cloudflare-local'){
   const namespace=await mf.getDurableObjectNamespace('ROOMS'),room=namespace.get(namespace.idFromName('one'))
   const roomCase=async body=>(await room.fetch('https://room/internal/synthetic-case',{method:'POST',body:JSON.stringify(body)})).json()
   const before=await roomCase({action:'inspect'});assert.ok(before.alarm && before.alarm<=Date.now()+30000)
   await roomCase({action:'duplicate-alarm'});assert.equal(second.closedAt,null)
   await sleep(1200);await mf.unsafeEvictDurableObject('','JourneyRoom',{name:'one',webSockets:'hibernate'})
   await data('/doc?room=one',{method:'PATCH',headers:{...seed,'Content-Type':'application/json'},body:{put:[{...update,name:'After actual hibernation wake'}]}});await sleep(100)
   assert.ok(second.messages.some(m=>m.includes('After actual hibernation wake')))
   pass('actual local-workerd hibernation preserves attachments and rechecks current policy before resuming delivery; duplicate alarms preserve authorized streams')
   await fault({missed:true});const r=await post('revoke',{familyId:two.family.id},true);assert.equal(r.status,200)
   await mf.unsafeEvictDurableObject('','JourneyRoom',{name:'one',webSockets:'hibernate'})
   await data('/doc?room=one',{method:'PATCH',headers:{...seed,'Content-Type':'application/json'},body:{put:[{...update,name:'Private after revoked cold wake'}]}})
   await Promise.race([second.close,sleep(3000).then(()=>{throw new Error('revoked cold wake did not close')})])
   assert.ok(!second.messages.some(m=>m.includes('Private after revoked cold wake')));await fault({})
   const queued=await pair('Synthetic queued'),queuedStream=await socket(queued)
   await roomCase({action:'queued-expiry',credentialId:queued.credentialId})
   await Promise.race([queuedStream.close,sleep(3000).then(()=>{throw new Error('expired queued stream not closed')})])
   assert.ok(!queuedStream.messages.some(m=>m.includes('SYNTHETIC_QUEUED_AFTER_EXPIRY')))
   pass('revoked cold wake emits no private snapshot; queued actual send rejects an injected expired lease without waiting for the alarm')
   const rollback=join(scratch,'rollback');await mkdir(rollback)
   execFileSync('tar',['-x','-C',rollback],{input:execFileSync('git',['-C',join(root,'..'),'archive','6d35f5c45e9231585fe632c7f33694e678473ee5','kc-journey-map/server','kc-journey-map/lib'])})
   await writeFile(join(rollback,'kc-journey-map/package.json'),JSON.stringify({type:'module'}))
   const old=await build({entryPoints:[join(rollback,'kc-journey-map/server/host/cloudflare.ts')],bundle:true,write:false,format:'esm',platform:'browser',conditions:['workerd','worker','browser'],external:['cloudflare:workers'],logLevel:'silent'})
   await mf.setOptions({...mfOptions,script:old.outputFiles[0].text});const denied=await request('/doc?room=one',{headers:seed});assert.notEqual(denied.status,200)
   await mf.setOptions({...mfOptions,script});await assertDenied(one)
   pass('actual accepted older workerd binary refuses versioned human security metadata; current binary restart preserves revoked authority')
  }else{
   for(const ws of clients)ws.close();child.kill('SIGTERM');await new Promise(resolve=>child.once('exit',resolve));await start();await assertDenied(one)
   const rollback=join(scratch,'rollback');await mkdir(rollback)
   execFileSync('tar',['-x','-C',rollback],{input:execFileSync('git',['-C',join(root,'..'),'archive','6d35f5c45e9231585fe632c7f33694e678473ee5','kc-journey-map/server','kc-journey-map/lib'])})
   await writeFile(join(rollback,'kc-journey-map/package.json'),JSON.stringify({type:'module'}))
   let error;try{execFileSync(process.execPath,['--import','tsx','--input-type=module','-e',`const {NodeHost}=await import(${JSON.stringify(join(rollback,'kc-journey-map/server/host/node.ts'))});new NodeHost()`],{cwd:root,env:{...process.env,JOURNEY_PRIVATE_DIR:privateDir,JOURNEY_ORIGIN:origin,JOURNEY_GRANTS_FILE:join(scratch,'grants.json')},stdio:'pipe'})}catch(e){error=e}
   assert.ok(error && /private storage must start empty/.test(String(error.stderr)),String(error?.stderr||'older binary unexpectedly started'))
   pass('actual Node restart preserves denial and accepted older Node binary refuses the security-versioned private directory')
  }
 }
 report.status='PASS'
}catch(error){report.status='FAIL';report.error=error.stack;report.logs=logs.slice(-30);console.error(error.stack);process.exitCode=1}
finally{
 for(const client of clients)try{client.close()}catch{}
 if(child&&child.exitCode===null){child.kill('SIGTERM');await new Promise(resolve=>child.once('exit',resolve))}
 await mf?.dispose()
 await writeFile(join(scratch,'report.json'),JSON.stringify(report,null,2));console.log('evidence='+join(scratch,'report.json'))
}
