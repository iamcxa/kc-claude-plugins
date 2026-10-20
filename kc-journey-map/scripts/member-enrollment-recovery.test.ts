import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createServer } from 'node:http'
import { spawn } from 'node:child_process'
import { writeFile, readFile } from 'node:fs/promises'
import { openSync,closeSync } from 'node:fs'
import { join } from 'node:path'
import { fixture,binding,target,provider } from './member-enrollment-fixture'
import client from './private-cloudflare-client'
import operator from './private-cloudflare-ops'
const cwd=new URL('..',import.meta.url).pathname
for(const drop of ['registry','client','inspection','inspect-denied','none','default-off','scope-denied'])test('actual private CLI recovery: '+drop,async()=>{
const h=await fixture('cloudflare-local',{enabled:drop!=='default-off'}),token='synthetic-private-operator-token-'.repeat(2),t=target(),p=provider(),requests:string[]=[];let dropped=false,firstInput:any
const env={JOURNEY_ORIGIN:binding.origin,JOURNEY_GRANTS:JSON.stringify(h.grants),JOURNEY_HUMAN_CONFIG:JSON.stringify(h.config),JOURNEY_OPERATOR_ROOMS:drop==='scope-denied'?'["two"]':'["one","two"]',JOURNEY_MEMBER_ENROLLMENT:'true',JOURNEY_MEMBER_BINDING:JSON.stringify(binding),REGISTRY:{idFromName:(s:string)=>s,get:()=>({fetch:async(r:Request)=>{const body=await r.arrayBuffer();if(drop==='inspection'&&r.url.endsWith('/member')&&JSON.parse(new TextDecoder().decode(body)).operation==='inspect')throw Error('synthetic inspection unavailable');const result=await h.registry.fetch(r.url,{method:r.method,headers:Object.fromEntries(r.headers),body});if(drop==='registry'&&r.url.endsWith('/member')&&!dropped){dropped=true;throw Error('synthetic dropped committed registry response')}return result}})},ROOMS:{}}
const server=createServer(async(req,res)=>{try{const url=new URL(req.url!,'http://127.0.0.1');if(url.pathname.startsWith('/provider/')){const result=await p.read(url.pathname.slice('/provider'.length),Object.fromEntries(url.searchParams));res.setHeader('Content-Type','application/json');res.end(JSON.stringify(result));return}const chunks=[];for await(const chunk of req)chunks.push(chunk);const body=Buffer.concat(chunks);const command=JSON.parse(body.toString());assert.deepEqual(command.input.target,t);assert.ok(req.headers.authorization==='Bearer '+token,'same protected credential authenticates each request');if(firstInput)assert.deepEqual(command.input,firstInput);else firstInput=command.input;requests.push(command.op);const r=await client.fetch(new Request('https://operator.synthetic.invalid/',{method:'POST',headers:req.headers as any,body}),{JOURNEY_OPERATOR_TOKEN:drop==='inspect-denied'&&command.op==='member-inspect'?'different-synthetic-operator-token-'.repeat(2):token,OPERATOR:{fetch:(r:Request)=>operator.fetch(r,env)}});res.writeHead(r.status,Object.fromEntries(r.headers));res.end(Buffer.from(await r.arrayBuffer()))}catch(error){res.statusCode=500;res.end(String(error))}})
const fds:number[]=[]
try {
 await new Promise<void>(done=>server.listen(0,'127.0.0.1',done));const port=(server.address() as any).port
 const input=join(h.dir,'target'),receipt=join(h.dir,'receipt'),credential=join(h.dir,'credential'),preload=join(h.dir,'synthetic-network.mjs')
 await writeFile(input,JSON.stringify(t),{mode:0o600});await writeFile(receipt,'',{mode:0o600});await writeFile(credential,token,{mode:0o600})
 await writeFile(join(h.dir,'counterexample.json'),JSON.stringify({enabled:true,writersStopped:true,candidate:'synthetic-private-recovery',binding,providerFd:5,transport:{mode:'cloudflare-private',url:'https://operator.synthetic.invalid/',credentialFd:6}}),{mode:0o600})
 await writeFile(preload,`const original=globalThis.fetch;let dropped=false;globalThis.fetch=(url,init)=>{url=new URL(url);if(url.origin==='https://api.cloudflare.com')return original('http://127.0.0.1:${port}/provider'+url.pathname.slice('/client/v4'.length)+url.search,init);if(url.origin==='https://operator.synthetic.invalid')return original('http://127.0.0.1:${port}/operator',init).then(r=>{if(['client','inspection','inspect-denied'].includes('${drop}')&&!dropped&&JSON.parse(init.body).op==='member-enroll'){dropped=true;throw Error('synthetic lost client reply')}return r});throw Error('unexpected outbound '+url.origin)}`,{mode:0o600})
 fds.push(openSync(input,'r'),openSync(receipt,'w'),openSync(credential,'r'),openSync(credential,'r'))
 const driver=`import os,pty,subprocess,select,time,sys
master,slave=pty.openpty()
p=subprocess.Popen([sys.argv[1],'--import','tsx','--import',sys.argv[2],'scripts/journey-member.ts','enroll','--profile','counterexample','--input-fd','3','--receipt-fd','4'],stdin=slave,stdout=slave,stderr=slave,pass_fds=(3,4,5,6))
os.close(slave)
buf='';confirmed=False;deadline=time.time()+20
while time.time()<deadline:
 if select.select([master],[],[],0.1)[0]:
  try: chunk=os.read(master,65536).decode()
  except OSError: break
  buf+=chunk
  if not confirmed and 'Type CONFIRM' in buf:
   review=next(line.strip() for line in buf.splitlines() if line.startswith('{"target":'))
   os.write(master,('CONFIRM '+review+'\\n').encode());confirmed=True
 if p.poll() is not None: break
if p.poll() is None: p.kill();raise Exception('actual CLI timed out')
print(buf)
sys.exit(p.returncode)
`
 const run=await new Promise<{code:number|null;output:string}>((done,reject)=>{const child=spawn('python3',['-c',driver,process.execPath,preload],{cwd,env:{...process.env,JOURNEY_MEMBER_PROFILE_DIR:h.dir},stdio:['ignore','pipe','pipe',...fds]});let output='';child.stdout.on('data',c=>output+=c);child.stderr.on('data',c=>output+=c);child.on('error',reject);child.on('exit',code=>done({code,output}))})
 assert.equal(run.code,0,run.output);assert.ok(!run.output.includes(token))
 const saved=JSON.parse(await readFile(receipt,'utf8')),state=await h.member('inspect',{target:t,proof:saved.proof,operationId:saved.operationId})
 assert.ok(!JSON.stringify(saved).includes(token));assert.deepEqual(saved.target,t);if(saved.readback?.member)assert.equal(saved.readback.member.id,t.memberId)
 if(['default-off','scope-denied'].includes(drop)){assert.equal(saved.result.result,'refused');assert.deepEqual(requests,['member-enroll']);assert.equal(await h.get('member:'+t.memberId),null);assert.equal(saved.readback,null)}
 else {assert.equal(state.result,'matching-current-state');assert.equal(state.receiptAvailable,true);assert.equal(saved.result.result,drop==='none'?'created':'unknown');assert.deepEqual(requests,drop==='none'?['member-enroll']:['member-enroll','member-inspect']);assert.equal(saved.readback?.result,drop==='none'?undefined:['inspection','inspect-denied'].includes(drop)?'unknown':'matching-current-state')}
} finally {for(const fd of fds)closeSync(fd);await new Promise<void>(done=>server.close(()=>done()));await h.close()}

})

test('standalone unknown inspection is attempted only once',async()=>{
 const {runMemberCommand}=await import('./journey-member');let sends=0,saved:any
 const result=await runMemberCommand({op:'inspect',target:target(),binding,read:provider().read,send:async()=>{sends++;throw Error('synthetic unavailable inspection')},confirm:async()=>{throw Error('inspect must not confirm enrollment')},save:r=>{saved=r},candidate:'synthetic-readonly-recovery'})
 assert.equal(sends,1);assert.equal(result.result,'unknown');assert.equal(saved.readback,null)
})
