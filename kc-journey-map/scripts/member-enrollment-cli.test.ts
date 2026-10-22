import assert from 'node:assert/strict'
import { test } from 'node:test'
import { spawn } from 'node:child_process'
import { writeFile, readFile } from 'node:fs/promises'
import { openSync,closeSync } from 'node:fs'
import { join } from 'node:path'
import { fixture,provider,binding,target,subject } from './member-enrollment-fixture'
import { resolveMember } from './member-resolver'

test('actual command reads protected descriptors, emits summary only and inspect cannot enroll',async()=>{
 const h=await fixture('node');try{
  const t=target(),proof=await resolveMember(t.email,binding,provider().read)
  await h.member('enroll',{target:t,proof,operationId:crypto.randomUUID()})
  const before=await h.snapshot(),input=join(h.dir,'input'),receipt=join(h.dir,'receipt'),credential=join(h.dir,'credential'),profile=join(h.dir,'test.json'),preload=join(h.dir,'preload.mjs')
  await writeFile(input,JSON.stringify(t),{mode:0o600});await writeFile(receipt,'',{mode:0o600});await writeFile(credential,'synthetic-test-secret-not-output',{mode:0o600})
  await writeFile(profile,JSON.stringify({enabled:true,writersStopped:true,candidate:'synthetic-cli',binding,providerFd:5,transport:{mode:'cloudflare-private',url:'https://operator.synthetic.invalid/',credentialFd:5}}),{mode:0o600})
  const reads:any={};for(const path of ['/accounts/account/access/organizations','/accounts/account/access/apps/app','/accounts/account/identity_providers/otp','/accounts/account/access/users','/accounts/account/access/users/directory-id-never-subject/last_seen_identity'])reads[path]=await provider().read(path,path.endsWith('/users')?{page:'1'}:undefined)
  const response=await h.member('inspect',{target:t,proof,operationId:crypto.randomUUID()})
  await writeFile(preload,`const reads=${JSON.stringify(reads)};globalThis.fetch=async(url,init)=>{url=new URL(url);if(url.origin==='https://api.cloudflare.com'){const v=reads[url.pathname.slice('/client/v4'.length)];if(!v)throw new Error('unexpected path');return Response.json(v)}if(url.origin==='https://operator.synthetic.invalid'){const c=JSON.parse(init.body);if(c.op!=='member-inspect')throw new Error('inspect attempted mutation');return Response.json(${JSON.stringify(response)})}throw new Error('unexpected outbound')}`,{mode:0o600})
  const fds=[openSync(input,'r'),openSync(receipt,'w'),openSync(credential,'r')]
  const run=await new Promise<{code:number|null;output:string}>((done,reject)=>{const p=spawn(process.execPath,['--import','tsx','--import',preload,'scripts/journey-member.ts','inspect','--profile','test','--input-fd','3','--receipt-fd','4'],{cwd:new URL('..',import.meta.url),env:{...process.env,JOURNEY_MEMBER_PROFILE_DIR:h.dir},stdio:['ignore','pipe','pipe',...fds]});let output='';p.stdout.on('data',c=>output+=c);p.stderr.on('data',c=>output+=c);p.on('error',reject);p.on('exit',code=>done({code,output}))})
  for(const fd of fds)closeSync(fd)
  assert.equal(run.code,0,run.output);assert.equal(JSON.parse(run.output.trim()).result,'matching-current-state');for(const secret of ['synthetic-test-secret-not-output',t.email,subject])assert.ok(!run.output.includes(secret));assert.equal(JSON.parse(await readFile(receipt,'utf8')).target.memberId,'person');assert.equal(await h.snapshot(),before)
 }finally{await h.close()}
})

test('actual typed executable enrollment and inspect reach sole owning Node process over protected pipes',async()=>{
 const {spawnSync}=await import('node:child_process'),{constants}=await import('node:fs')
 const h=await fixture('node');let server:any;const fds:number[]=[]
 try{
  const t=target();h.host.close()
  const inPipe=join(h.dir,'control-in'),outPipe=join(h.dir,'control-out');assert.equal(spawnSync('mkfifo',['-m','600',inPipe,outPipe]).status,0)
  const inputPipe=openSync(inPipe,constants.O_RDWR),outputPipe=openSync(outPipe,constants.O_RDWR);fds.push(inputPipe,outputPipe)
  server=spawn(process.execPath,['--import','tsx','server/canvas-server.ts'],{cwd:new URL('..',import.meta.url),env:{...process.env,JOURNEY_PRIVATE_DIR:join(h.dir,'private'),JOURNEY_HUMAN_CONFIG:join(h.dir,'human.json'),JOURNEY_GRANTS_FILE:join(h.dir,'grants.json'),JOURNEY_ORIGIN:binding.origin,JOURNEY_API_PORT:'0',JOURNEY_AGENT_PAIRING:'true',JOURNEY_MEMBER_ENROLLMENT:'true',JOURNEY_MEMBER_BINDING:JSON.stringify(binding),JOURNEY_CONTROL_STDIO:'1'},stdio:[inputPipe,outputPipe,'pipe']})
  let serverError='';server.stderr.on('data',(c:any)=>serverError+=c)
  const reads:any={};for(const path of ['/accounts/account/access/organizations','/accounts/account/access/apps/app','/accounts/account/identity_providers/otp','/accounts/account/access/users','/accounts/account/access/users/directory-id-never-subject/last_seen_identity'])reads[path]=await provider().read(path,path.endsWith('/users')?{page:'1'}:undefined)
  const preload=join(h.dir,'provider-only.mjs');await writeFile(preload,`const reads=${JSON.stringify(reads)};globalThis.fetch=async url=>{url=new URL(url);if(url.origin!=='https://api.cloudflare.com')throw new Error('unexpected outbound');const v=reads[url.pathname.slice('/client/v4'.length)];if(!v)throw new Error('unexpected path');return Response.json(v)}`,{mode:0o600})
  const input=join(h.dir,'target'),receipt=join(h.dir,'receipt'),credential=join(h.dir,'credential');await writeFile(input,JSON.stringify(t),{mode:0o600});await writeFile(receipt,'',{mode:0o600});await writeFile(credential,'synthetic',{mode:0o600});await writeFile(join(h.dir,'pipes.json'),JSON.stringify({enabled:true,writersStopped:true,candidate:'synthetic-node-owning-pipes',binding,providerFd:5,transport:{mode:'node',inputFd:6,outputFd:7}}),{mode:0o600})
  const files=[openSync(input,'r'),openSync(receipt,'w'),openSync(credential,'r')];fds.push(...files)
  const driver=join(h.dir,'typed-review.py');await writeFile(driver,`import os,pty,subprocess,select,json,time,sys
master,slave=pty.openpty()
p=subprocess.Popen([sys.argv[1],'--import','tsx','--import',sys.argv[2],'scripts/journey-member.ts','enroll','--profile','pipes','--input-fd','3','--receipt-fd','4'],stdin=slave,stdout=slave,stderr=slave,pass_fds=(3,4,5,6,7))
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
if p.poll() is None: p.kill();raise Exception('typed command timed out')
results=[line.strip() for line in buf.splitlines() if line.startswith('{"result":')]
if p.returncode or not results: raise Exception('typed command failed')
print(results[-1])
`,{mode:0o600})
  const enrolled=await new Promise<{code:number|null;output:string}>((done,reject)=>{const p=spawn('python3',[driver,process.execPath,preload],{cwd:new URL('..',import.meta.url),env:{...process.env,JOURNEY_MEMBER_PROFILE_DIR:h.dir},stdio:['ignore','pipe','pipe',...files,inputPipe,outputPipe]});let output='';p.stdout.on('data',c=>output+=c);p.stderr.on('data',c=>output+=c);p.on('error',reject);p.on('exit',code=>done({code,output}))})
  assert.equal(enrolled.code,0,enrolled.output+serverError);assert.equal(JSON.parse(enrolled.output.trim()).result,'created');assert.equal(JSON.parse(await readFile(receipt,'utf8')).result.result,'created')
  for(const fd of files){closeSync(fd);fds.splice(fds.indexOf(fd),1)}
  await writeFile(receipt,'')
  files.splice(0,files.length,openSync(input,'r'),openSync(receipt,'w'),openSync(credential,'r'));fds.push(...files)
  const result=await new Promise<{code:number|null;output:string}>((done,reject)=>{const p=spawn(process.execPath,['--import','tsx','--import',preload,'scripts/journey-member.ts','inspect','--profile','pipes','--input-fd','3','--receipt-fd','4'],{cwd:new URL('..',import.meta.url),env:{...process.env,JOURNEY_MEMBER_PROFILE_DIR:h.dir},stdio:['ignore','pipe','pipe',...files,inputPipe,outputPipe]});let output='';p.stdout.on('data',c=>output+=c);p.stderr.on('data',c=>output+=c);const timeout=setTimeout(()=>{p.kill();reject(new Error('CLI pipe timeout '+serverError))},20_000);p.on('error',reject);p.on('exit',code=>{clearTimeout(timeout);done({code,output})})})
  assert.equal(result.code,0,result.output+serverError);assert.equal(JSON.parse(result.output.trim()).result,'matching-current-state');assert.equal(JSON.parse(await readFile(receipt,'utf8')).target.memberId,'person')
 }finally{server?.kill('SIGTERM');if(server)await new Promise(r=>server.once('exit',r));for(const fd of fds)closeSync(fd);await h.mf?.dispose()}
})
