import assert from 'node:assert/strict'
import { spawn,execFileSync } from 'node:child_process'
import { mkdtemp,writeFile,readFile,mkdir } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createServer } from 'node:net'
import { createHash } from 'node:crypto'
import { createServer as viteServer } from 'vite'
import { chromium,devices } from 'playwright'
const root=new URL('..',import.meta.url).pathname.replace(/\/$/,'')
const scratch=await mkdtemp(join(tmpdir(),'agent-pair-browser-'))
const port=()=>new Promise(resolve=>{const s=createServer();s.listen(0,'127.0.0.1',()=>{const p=s.address().port;s.close(()=>resolve(p))})})
const apiPort=await port(),uiPort=await port(),origin='http://127.0.0.1:'+uiPort,endpoint='http://127.0.0.1:'+apiPort
const hash=s=>createHash('sha256').update(s).digest('hex')
const seed='e'.repeat(64),headers={Authorization:'Bearer seed.'+seed}
const grantsFile=join(scratch,'grants.json'),configFile=join(scratch,'human.json'),dataDir=join(scratch,'data'),helperConfig=join(scratch,'installation.json'),storeRoot=join(scratch,'protected')
await writeFile(grantsFile,JSON.stringify([{credentialId:'seed',secretDigest:hash(seed),principalId:'legacy',rooms:['one','two'],expiresAt:Date.now()+3600000,revoked:false}]),{mode:0o600})
await writeFile(configFile,JSON.stringify({version:1,backendId:'pair-browser',origin,mode:'local',issuer:'local:pair-browser',localOwnerUid:process.geteuid(),localMemberId:'owner',members:[{id:'owner',issuer:'local:pair-browser',subject:'uid:'+process.geteuid(),label:'Synthetic owner',role:'operator',rooms:[{id:'one',expiresAt:Date.now()+3600000}]}]}),{mode:0o600})
await writeFile(helperConfig,JSON.stringify({endpoint,backendId:'pair-browser',installationId:crypto.randomUUID(),memberId:'owner',rooms:['one'],label:'Synthetic installation; self-reported'}),{mode:0o600})
const logs=[]
const child=spawn(process.execPath,['--import','tsx','server/canvas-server.ts'],{cwd:root,stdio:['pipe','pipe','pipe'],env:{...process.env,JOURNEY_PRIVATE_DIR:dataDir,JOURNEY_GRANTS_FILE:grantsFile,JOURNEY_HUMAN_CONFIG:configFile,JOURNEY_AGENT_PAIRING:'true',JOURNEY_ORIGIN:origin,JOURNEY_API_PORT:String(apiPort)}})
child.stdout.on('data',d=>logs.push(String(d)));child.stderr.on('data',d=>logs.push(String(d)))
const helper=(command,input)=>execFileSync(process.execPath,[join(root,'scripts/agent-helper.mjs'),command,helperConfig,storeRoot],{cwd:root,input,encoding:'utf8',timeout:60000})
const report={candidate:execFileSync('git',['-C',root,'rev-parse','HEAD'],{encoding:'utf8'}).trim(),clean:!execFileSync('git',['-C',root,'status','--porcelain'],{encoding:'utf8'}).trim(),provider:'NOT RUN',physicalMobile:'NOT RUN; browser device emulation only',checks:[]}
const pass=name=>{report.checks.push(name);console.log('PASS '+name)}
let vite,browser,paired=false
try {
 for(let i=0;i<200;i++){try{if((await fetch(endpoint+'/health',{headers})).ok)break}catch{} if(child.exitCode!==null)throw new Error(logs.join(''));await new Promise(r=>setTimeout(r,50));if(i===199)throw new Error('startup timeout')}
 const before={}
 for(const room of ['one','two'])before[room]=await (await fetch(endpoint+'/doc?room='+room,{headers})).json()
 process.env.JOURNEY_API_PORT=String(apiPort);process.env.JOURNEY_HUMAN_CONFIG=configFile
 vite=await viteServer({configFile:join(root,'vite.config.mts'),server:{host:'127.0.0.1',port:uiPort,strictPort:true}});await vite.listen()
 browser=await chromium.launch({headless:true})
 const context=await browser.newContext({viewport:{width:1280,height:800}})
 const page=await context.newPage(); const errors=[];page.on('pageerror',e=>errors.push(e.message))
 await page.goto(origin+'/?room=one')
 await page.getByRole('button',{name:'開始本機帳號驗證'}).click()
 const login=await page.locator('.human-entry code').innerText()
 execFileSync('python3',[join(root,'scripts/owner-login.py'),join(dataDir,'owner-login.sock'),login],{input:'approve\n',encoding:'utf8'})
 await page.getByRole('button',{name:'我已在本機核准'}).click()
 await page.waitForFunction(()=>!!window.editor)
 await page.waitForFunction(()=>document.querySelector('.agent-account'))
 assert.ok(await page.evaluate(()=>window.editor.getViewportScreenBounds().y>=56))
 await page.getByRole('button',{name:'帳號與代理'}).click()
 await page.getByRole('heading',{name:'帳號與代理'}).waitFor()
 await page.getByText('目前沒有代理安裝。',{exact:true}).waitFor()
 pass('real tldraw canvas preserves account sheet entry and empty state')
 const request=JSON.parse(helper('begin'));paired=true
 await page.getByLabel('配對碼').fill(request.code)
 await page.getByRole('button',{name:'檢視配對請求'}).click()
 await page.getByText('完整紀錄新增、修改、刪除與整份文件取代',{exact:true}).waitFor()
 assert.ok((await page.locator('dialog').innerText()).includes('one'))
 const approve=page.getByRole('button',{name:'核准這些畫布與能力'})
 await approve.scrollIntoViewIfNeeded()
 assert.equal(await approve.evaluate(el=>{const r=el.getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)===el}),true)
 await approve.click()
 await page.getByText('已核准，等待原安裝兌換；尚未簽發安裝憑證。',{exact:true}).waitFor()
 const finished=JSON.parse(helper('finish'));assert.equal(finished.state,'active')
 await page.getByRole('button',{name:'更新代理清單'}).click()
 await page.getByText('Synthetic installation; self-reported',{exact:true}).first().waitFor()
 const rpc=JSON.parse(helper('mcp',JSON.stringify({jsonrpc:'2.0',id:1,method:'tools/call',params:{name:'health'}})+'\n').trim())
 assert.deepEqual(rpc.result.structuredContent.rooms,['one'])
 const denied=JSON.parse(helper('mcp',JSON.stringify({jsonrpc:'2.0',id:2,method:'tools/call',params:{name:'get_doc',arguments:{room:'two'}}})+'\n').trim())
 assert.equal(denied.error.code,-32001)
 pass('real Keychain-backed installation finishes original redemption and stdio MCP permits one room while denying another')
 for(const theme of ['light','dark']){
  await page.emulateMedia({colorScheme:theme})
  await page.evaluate(theme=>window.editor.user.updateUserPreferences({colorScheme:theme}),theme)
  await page.waitForFunction(theme=>document.querySelector('.agent-sheet')?.getAttribute('data-theme')===theme,theme)
  assert.equal(await page.evaluate(()=>!!document.querySelector('.tl-theme__dark')),theme==='dark')
  assert.equal(await page.locator('.agent-sheet').evaluate(el=>getComputedStyle(el).backgroundColor),theme==='dark'?'rgb(34, 39, 53)':'rgb(255, 255, 255)')
  for(const viewport of [{width:1280,height:800},{width:390,height:844}]){
   await page.setViewportSize(viewport)
   for(const button of await page.locator('dialog button:visible').all()){const box=await button.boundingBox();assert.ok(box.height>=44)}
   assert.equal(await page.locator('dialog').evaluate(el=>el.scrollWidth<=el.clientWidth),true)
   await page.screenshot({path:join(scratch,'agents-'+theme+'-'+viewport.width+'.png')})
  }
 }
 await page.keyboard.press('Escape')
 await page.getByRole('button',{name:'帳號與代理'}).waitFor()
 assert.equal(await page.getByRole('button',{name:'帳號與代理'}).evaluate(el=>document.activeElement===el),true)
 await page.keyboard.press('Enter');await page.getByRole('heading',{name:'帳號與代理'}).waitFor()
 await page.getByRole('button',{name:'撤銷此安裝'}).click()
 await page.getByRole('button',{name:'確認撤銷此安裝'}).click()
 await page.getByText('已撤銷；舊安裝不會復活。',{exact:true}).waitFor()
 const reconcile=JSON.parse(helper('reconcile'));assert.equal(reconcile.state,'revoked')
 helper('forget');paired=false
 pass('light/dark desktop and actual 390px viewport controls hit targets; Escape restores focus; human revoke plus authenticated helper reconcile confirms old family')
 const mobile=await browser.newContext({...devices['iPhone 13'],storageState:await context.storageState()})
 const touch=await mobile.newPage();await touch.goto(origin+'/?room=one');await touch.waitForFunction(()=>!!window.editor)
 await touch.getByRole('button',{name:'帳號與代理'}).tap();await touch.getByRole('heading',{name:'帳號與代理'}).waitFor()
 const close=touch.getByRole('button',{name:'關閉帳號與代理'});const box=await close.boundingBox();assert.ok(box.width>=44 && box.height>=44)
 await close.tap();assert.equal(await touch.locator('dialog[open]').count(),0)
 await mobile.close();pass('mobile browser touch emulation opens and closes real sheet; physical phone remains unverified')
 for(const room of ['one','two'])assert.deepEqual((await(await fetch(endpoint+'/doc?room='+room,{headers})).json()).snapshot.documents.filter(d=>d.state.typeName!=='user'),before[room].snapshot.documents)
 assert.deepEqual(errors,[])
 pass('permitted/denied proof and management leave synthetic room records unchanged; no browser runtime error')
} finally {
 if(paired){try{helper('reconcile');helper('forget')}catch{report.cleanup='FAILED; exact synthetic account retained in scratch for authenticated cleanup'}}
 await browser?.close();await vite?.close();child.kill('SIGTERM')
 const out=process.env.JOURNEY_EVIDENCE_DIR||scratch;await mkdir(out,{recursive:true});await writeFile(join(out,'agent-browser-report.json'),JSON.stringify({...report,scratch},null,2))
 console.log('Report '+join(out,'agent-browser-report.json'))
}

