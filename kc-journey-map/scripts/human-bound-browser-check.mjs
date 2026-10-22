import assert from 'node:assert/strict'
import { spawn, execFileSync } from 'node:child_process'
import { mkdtemp, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createHash } from 'node:crypto'
import { createServer } from 'node:net'
import { createServer as viteServer } from 'vite'
import { chromium } from 'playwright'
const root = new URL('..', import.meta.url).pathname.replace(/\/$/, '')
const scratch = await mkdtemp(join(tmpdir(), 'human-entry-'))
const hash = value => createHash('sha256').update(value).digest('hex')
const port = () => new Promise(resolve => { const socket = createServer(); socket.listen(0, '127.0.0.1', () => { const n = socket.address().port; socket.close(() => resolve(n)) }) })
const apiPort = await port(), uiPort = await port(), origin = 'http://127.0.0.1:' + uiPort
const secret = 's'.repeat(43), bearer = 'synthetic.' + secret
const grantsFile=join(scratch,'grants.json'), configFile=join(scratch,'human.json'), dataDir=join(scratch,'data')
await writeFile(grantsFile,JSON.stringify([{credentialId:'synthetic',secretDigest:hash(secret),principalId:'synthetic-seeder',rooms:['one'],expiresAt:Date.now()+3600000,revoked:false}]),{mode:0o600})
await writeFile(configFile,JSON.stringify({version:1,backendId:'bound-check',origin,mode:'local',issuer:'local:bound-check',localOwnerUid:process.geteuid(),localMemberId:'owner',members:[{id:'owner',issuer:'local:bound-check',subject:'uid:'+process.geteuid(),label:'Synthetic owner',role:'operator',rooms:[{id:'one',expiresAt:Date.now()+3600000}]}]}),{mode:0o600})
const child=spawn(process.execPath,['--import','tsx','server/canvas-server.ts'],{cwd:root,stdio:['pipe','pipe','pipe'],env:{...process.env,JOURNEY_PRIVATE_DIR:dataDir,JOURNEY_GRANTS_FILE:grantsFile,JOURNEY_HUMAN_CONFIG:configFile,JOURNEY_ORIGIN:origin,JOURNEY_API_PORT:String(apiPort)}})
const logs=[];child.stdout.on('data',b=>logs.push(String(b)));child.stderr.on('data',b=>logs.push(String(b)))
let vite,browser
const report={checks:[],provider:'NOT RUN',syntheticOnly:true}
const pass=name=>{report.checks.push(name);console.log('PASS '+name)}
try{
 let ready=false
 for(let n=0;n<200;n++){try{if((await fetch('http://127.0.0.1:'+apiPort+'/health',{headers:{Authorization:'Bearer '+bearer}})).ok){ready=true;break}}catch{}if(child.exitCode!==null)throw Error('API exited');await new Promise(resolve=>setTimeout(resolve,50))}
 assert.equal(ready,true,'API ready')
 assert.equal((await fetch('http://127.0.0.1:'+apiPort+'/doc?room=one',{headers:{Authorization:'Bearer '+bearer}})).status,200)
 process.env.JOURNEY_API_PORT=String(apiPort);process.env.JOURNEY_HUMAN_CONFIG=configFile
 vite=await viteServer({configFile:join(root,'vite.config.mts'),server:{host:'127.0.0.1',port:uiPort,strictPort:true}});await vite.listen()
 browser=await chromium.launch({headless:true})
 const context=await browser.newContext(),page=await context.newPage()
 await page.goto(origin+'/')
 const bounds=await page.evaluate(async sourceRoot=>{
  const {validateDraftContext}=await import('/@fs'+sourceRoot+'/server/draft-data.ts'),at=Date.now()
  const c={origin:location.origin,backend:'test',member:'owner',issuer:'synthetic',subject:'subject',generation:1,signInAt:at,revalidateBy:at+14*86400000,room:'one'}
  let accepted=false,rejected=false
  try{validateDraftContext(c);accepted=true}catch{}
  try{validateDraftContext({...c,revalidateBy:c.revalidateBy+1})}catch{rejected=true}
  return {accepted,rejected}
 },root)
 assert.deepEqual(bounds,{accepted:true,rejected:true})
 pass('frontend accepts exactly fourteen days and rejects one millisecond beyond')
 await page.getByRole('button',{name:'開始本機帳號驗證'}).click()
 const requestId=await page.locator('.human-entry code').innerText()
 assert.match(execFileSync('python3',[join(root,'scripts/owner-login.py'),join(dataDir,'owner-login.sock'),requestId],{input:'approve\n',encoding:'utf8'}),/"approved": true/)
 await page.getByRole('button',{name:'我已在本機核准'}).click()
 await page.getByRole('button',{name:'one',exact:true}).waitFor()
 const identity=await context.request.get(origin+'/auth/identity').then(r=>r.json())
 assert.equal(identity.humanRevalidateBy-identity.verifiedHumanSignInAt,14*86400000)
 pass('real local owner-consumed session carries server fourteen-day bound')
 let frames=0;page.on('websocket',socket=>socket.on('framereceived',()=>frames++))
 await page.getByRole('button',{name:'one',exact:true}).click()
 await page.waitForFunction(()=>!!window.editor,{},{timeout:15000})
 assert.ok(frames>0,'first WebSocket received actual server frames')
 assert.equal(await page.getByText('結果未確認',{exact:true}).count(),0)
 pass('first human socket verifies fourteen-day session, receives real frames and mounts native canvas')
 await page.screenshot({path:join(scratch,'first-canvas.png')})
}finally{
 await browser?.close();await vite?.close()
 if(child.exitCode===null){const exit=new Promise(resolve=>child.once('exit',resolve));child.kill('SIGTERM');await exit}
 await writeFile(join(scratch,'report.json'),JSON.stringify(report,null,2));console.log('evidence='+join(scratch,'report.json'))
}
