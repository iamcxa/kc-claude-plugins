import assert from 'node:assert/strict'
import {spawn,execFileSync} from 'node:child_process'
import {mkdtemp,mkdir,writeFile,readFile,symlink} from 'node:fs/promises'
import {join} from 'node:path'
import {tmpdir} from 'node:os'
import {createHash} from 'node:crypto'
import {DatabaseSync} from 'node:sqlite'
import {createServer} from 'node:net'
import {build} from 'esbuild'
import {createServer as viteServer} from 'vite'
import {chromium} from 'playwright'
import {startCloudflare} from './cloudflare-local.mjs'
import {note} from '../lib/records.mjs'
const root=new URL('..',import.meta.url).pathname.replace(/\/$/,''),adapter=process.argv[2]||'node'
if(!['node','cloudflare-local'].includes(adapter))throw Error('synthetic adapter required')
await mkdir(join(root,'.host-check'),{recursive:true})
const scratch=await mkdtemp(join(root,'.host-check/access-'+adapter+'-'))
const port=()=>new Promise((resolve,reject)=>{const s=createServer();s.once('error',reject);s.listen(0,'127.0.0.1',()=>{const p=s.address().port;s.close(()=>resolve(p))})})
const apiPort=await port(),uiPort=await port(),origin='http://127.0.0.1:'+uiPort,api='http://127.0.0.1:'+apiPort,time=Date.now(),hash=s=>createHash('sha256').update(s).digest('hex')
const issuer=adapter==='node'?'local:draft':'https://draft.synthetic.invalid'
const config={version:1,backendId:'return-'+adapter,origin,mode:adapter==='node'?'local':'cloudflare',issuer,audience:'synthetic',localOwnerUid:process.geteuid(),localMemberId:'owner',members:[{id:'owner',issuer,subject:adapter==='node'?'uid:'+process.geteuid():'owner',label:'Synthetic owner',role:'operator',rooms:[{id:'one',expiresAt:time+3600000},{id:'two',expiresAt:time+3600000},{id:'live',expiresAt:time+3600000}]},{id:'other',issuer,subject:'other-subject',label:'Synthetic other',role:'member',rooms:[{id:'one',expiresAt:time+3600000},{id:'live',expiresAt:time+3600000}]}]}
const grants=[{credentialId:'seed',secretDigest:hash('s'.repeat(43)),principalId:'seed',rooms:['one','two','live'],expiresAt:time+3600000,revoked:false}]
const dataDir=await mkdtemp(join(tmpdir(),'return-data-')),configFile=join(scratch,'human.json'),grantsFile=join(scratch,'grants.json')
await writeFile(configFile,JSON.stringify(config));await writeFile(grantsFile,JSON.stringify(grants))
const report={adapter,candidate:execFileSync('git',['-C',root,'rev-parse','HEAD'],{encoding:'utf8'}).trim(),dirty:!!execFileSync('git',['-C',root,'status','--porcelain'],{encoding:'utf8'}).trim(),counterfactual:process.env.JOURNEY_RECOVERY_DROP_CAUSE==='1',checks:[],provider:'NOT RUN; synthetic typed sessions',physicalDevice:'NOT RUN',browser:chromium.executablePath()}
const pass=name=>{report.checks.push(name);console.log('PASS '+name)}
let child,host,db,metadata,vite,browser,page,logs=''
const seed=(path,method='GET',body)=>fetch(api+path,{method,headers:{Authorization:'Bearer seed.'+'s'.repeat(43),...(body?{'Content-Type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{})})
const doc=async()=>{const r=await seed('/doc?room=one');assert.equal(r.status,200);return r.json()}
report.startedAt=new Date().toISOString()
const wait=async fn=>{for(let i=0;i<150;i++){if(await fn())return;await new Promise(r=>setTimeout(r,100))}throw Error('bounded condition timed out')}
const click=async loc=>{await loc.scrollIntoViewIfNeeded();assert.ok(await loc.evaluate(el=>{const r=el.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return r.width>=44&&r.height>=44&&(hit===el||el.contains(hit))}));await loc.click()}
try{
 if(adapter==='cloudflare-local'){
  await symlink(join(root,'node_modules'),join(dataDir,'node_modules'),'dir')
  host=await startCloudflare({dir:dataDir,port:apiPort,origin,grants,humanConfig:config})
  const ns=await host.mf.getDurableObjectNamespace('REGISTRY'),registry=ns.get(ns.idFromName('private-pilot'))
  metadata=async(operation,body)=>{const r=await registry.fetch('https://registry/'+operation,{method:'POST',body:JSON.stringify(body)});assert.equal(r.status,200,await r.clone().text());return r.json()}
 }else{
  const bundle=join(scratch,'server.mjs');await build({entryPoints:[join(root,'server/canvas-server.ts')],outfile:bundle,bundle:true,format:'esm',platform:'node',packages:'external',logLevel:'silent'})
  child=spawn(process.execPath,[bundle],{cwd:root,env:{...process.env,JOURNEY_PRIVATE_DIR:dataDir,JOURNEY_GRANTS_FILE:grantsFile,JOURNEY_HUMAN_CONFIG:configFile,JOURNEY_ORIGIN:origin,JOURNEY_API_PORT:String(apiPort)},stdio:['ignore','pipe','pipe']});child.stdout.on('data',d=>{logs+=d});child.stderr.on('data',d=>{logs+=d})
  await wait(async()=>{try{return(await seed('/health')).ok}catch{if(child.exitCode!==null)throw Error(logs);return false}})
  db=new DatabaseSync(join(dataDir,'metadata.sqlite'));db.exec('PRAGMA busy_timeout=5000')
  metadata=async(operation,body)=>{if(operation==='put'){db.prepare('INSERT OR REPLACE INTO metadata VALUES (?,?)').run(body.key,JSON.stringify(body.value));return{ok:true}}const r=db.prepare('SELECT value FROM metadata WHERE key=?').get(body.key);return r?JSON.parse(r.value):null}
 }
 for(const room of ['one','two','live']){await metadata('put',{key:'room:'+room,value:{createdAt:time}});await seed('/doc?room='+room)}
 const before=await doc(),pageId=before.snapshot.documents.find(d=>d.state.typeName==='page').state.id
 const sentinel=note({id:'shape:seed',text:'untouched synthetic base',x:300,y:200,parentId:pageId})
 assert.equal((await seed('/doc?room=one','PATCH',{put:[sentinel]})).status,200)
 const baseline=await doc()
 for(const member of ['owner','other'])await metadata('put',{key:'browser-session:'+hash('return-'+member),value:{actorType:'human',backendId:config.backendId,memberId:member,generation:1,expiresAt:time+900000,verifiedHumanSignInAt:time,humanRevalidateBy:time+604800000,csrfDigest:hash('csrf-'+member),revoked:false}})
 process.env.JOURNEY_API_PORT=String(apiPort);process.env.VITE_JOURNEY_HUMAN_ENTRY='true';if(adapter==='node')process.env.JOURNEY_HUMAN_CONFIG=configFile
 vite=await viteServer({plugins:[{name:'observe-native-human-params',enforce:'pre',transform(source,id){if(!id.endsWith('/human-socket.ts'))return;if(process.env.JOURNEY_RECOVERY_DROP_CAUSE==='1'){assert.ok(source.includes('onPause(recoveryCause(error))'));source=source.replace('onPause(recoveryCause(error))','onPause()')}const needle=' const socketUri=humanSocketUrl(uri,params)';assert.ok(source.includes(needle));return source.replace(needle,' ;((window as any).__nativeHumanSocketParams??=[]).push({uri,...params})\n'+needle)}}],configFile:join(root,'vite.config.mts'),cacheDir:join(scratch,'vite-cache'),server:{host:'127.0.0.1',port:uiPort,strictPort:true}});await vite.listen()
 browser=await chromium.launch({headless:true});report.browserVersion=browser.version()
 const context=await browser.newContext({viewport:{width:1280,height:900}})
 const cookies=member=>context.addCookies([{name:'journey_human',value:'return-'+member,url:origin,httpOnly:true,sameSite:'Strict'},{name:'journey_human_csrf',value:'csrf-'+member,url:origin,sameSite:'Strict'}])
 await cookies('owner')
 const routeAssets=route=>{const u=new URL(route.request().url());if(u.origin===origin)return route.continue();if(u.hostname==='cdn.tldraw.com')return route.fulfill({path:join(root,'.host-check/assets/package',u.pathname.replace(/^\/[^/]+\//,''))});return route.abort()}
 await context.route('**/*',routeAssets)
 page=await context.newPage();page.on('console',m=>{if(m.type()==='warning')console.log('browser warning: '+m.text())});const errors=[];page.on('pageerror',e=>errors.push(e.message))
 let drop=false,blockSockets=false,blockedSockets=0,clientFrames=[],latestSocket;report.socketUrls=[]
 await context.routeWebSocket(url=>url.pathname.startsWith('/connect/'),socket=>{report.socketUrls.push(socket.url());latestSocket=socket;if(blockSockets){blockedSockets++;socket.close();return}const server=socket.connectToServer();socket.onMessage(message=>{clientFrames.push(String(message));if(!drop || !String(message).includes('"type":"push"'))server.send(message)})})
 const ready=async target=>target.waitForFunction(()=>window.editor&&document.querySelector('[data-testid="room-trigger"]')?.title.endsWith('Connected'))
 const originalContext={origin,backend:config.backendId,member:'owner',issuer,subject:config.members[0].subject,generation:1,room:'one',signInAt:time,revalidateBy:time+604800000}
 const inventory=()=>page.evaluate(async owner=>{const {humanDrafts}=await import('/human-drafts.ts');return(await humanDrafts()).inventory(owner)},originalContext)
 const session=await metadata('get',{key:'browser-session:'+hash('return-owner')})
 const grant=await metadata('get',{key:'member-room:owner:one'})
 const edit=label=>page.evaluate(record=>window.editor.store.put([record]),note({id:'shape:retained',text:label,x:440,y:400,parentId:pageId}))
 async function open(){await cookies('owner');await metadata('put',{key:'browser-session:'+hash('return-owner'),value:session});await metadata('put',{key:'member-room:owner:one',value:grant});await page.goto(origin+'/?room=one');await ready(page)}
 const cause=kind=>page.locator('.human-recovery[data-kind="'+kind+'"]')
 const cases=[
  ['expired',async()=>metadata('put',{key:'browser-session:'+hash('return-owner'),value:{...session,expiresAt:time-1}})],
  ['denied',async()=>metadata('put',{key:'member-room:owner:one',value:{...grant,revoked:true}})],
  ['denied',async()=>cookies('other')],
  ['unavailable',async()=>page.route('**/auth/identity',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({error:'synthetic host down'})}))],
  ['unknown',async()=>page.route('**/auth/identity',route=>route.fulfill({contentType:'text/html',body:'<html>not an identity response</html>'}))],
  ['unknown',async()=>page.route('**/auth/identity',route=>route.fulfill({contentType:'application/json',body:JSON.stringify({unexpected:true})}))],
 ]
 for(const [i,[kind,fail]] of cases.entries()){
  await open();drop=true;await edit('retained before '+i);await page.getByText(/已儲存本機 v1/).waitFor();const beforeVersions=(await inventory()).length
  await fail();await edit('failure '+i);await cause(kind).waitFor();assert.equal(new URL(page.url()).searchParams.get('room'),'one');assert.equal(await page.evaluate(()=>window.editor.getInstanceState().isReadonly),true)
  if(i===0){const opened=page.waitForEvent('popup');await click(cause('expired').getByRole('link',{name:'另開原畫布並驗證登入',exact:true}));const loginPage=await opened;await loginPage.getByRole('button',{name:adapter==='node'?'開始本機帳號驗證':'開啟身分登入',exact:true}).waitFor();assert.equal(new URL(loginPage.url()).searchParams.get('room'),'one');assert.equal(await loginPage.evaluate(()=>!!window.editor),false);await loginPage.close()}
  await page.unroute('**/auth/identity');await cookies('owner');await metadata('put',{key:'browser-session:'+hash('return-owner'),value:session});await metadata('put',{key:'member-room:owner:one',value:grant})
  const paused=clientFrames.length;drop=false;await edit('old buffer after repair '+i);await new Promise(r=>setTimeout(r,250));assert.equal(clientFrames.length,paused);assert.ok((await inventory()).length>=beforeVersions)
  const actions=cause(kind);const expected={expired:'另開原畫布並驗證登入',denied:'另開原畫布確認權限',unavailable:'另開原畫布重新確認',unknown:'另開原畫布核對身分'}
  assert.equal(await actions.getByRole('link',{name:expected[kind],exact:true}).getAttribute('href'),origin+'/?room=one')
  await click(actions.getByRole('button',{name:'重新確認原身分與權限',exact:true}));await actions.getByText(/原身分與畫布權限已確認/).waitFor();assert.equal(clientFrames.length,paused);assert.equal(await page.evaluate(()=>window.editor.getInstanceState().isReadonly),true)
  if(i===0){
   await page.route('**/auth/identity',async route=>{await new Promise(r=>setTimeout(r,600));await route.continue().catch(()=>{})})
   await click(actions.getByRole('button',{name:'重新確認原身分與權限',exact:true}));await actions.getByText(/正在重新確認/).waitFor();await click(actions.getByRole('button',{name:'暫不恢復，保留暫停',exact:true}));await new Promise(r=>setTimeout(r,750));assert.equal(await actions.locator('.recovery-body').count(),0);assert.equal(await actions.locator('.recovery-toggle').evaluate(el=>el===document.activeElement),true);await page.unroute('**/auth/identity');await page.keyboard.press('Space');await actions.locator('.recovery-body').waitFor()
   for(const theme of ['light','dark'])for(const width of [1280,390]){
    await page.setViewportSize({width,height:900});await page.emulateMedia({colorScheme:theme});await page.evaluate(theme=>window.editor.user.updateUserPreferences({colorScheme:theme}),theme);await page.waitForFunction(theme=>!!document.querySelector('.tl-theme__'+theme),theme)
    await click(actions.getByRole('button',{name:'暫不恢復，保留暫停',exact:true}));await page.keyboard.press('Space');await actions.locator('.recovery-body').waitFor();await click(actions.getByRole('button',{name:'重新確認原身分與權限',exact:true}));await actions.getByText(/原身分與畫布權限已確認/).waitFor()
    await wait(()=>page.evaluate(()=>{const a=document.querySelector('.human-recovery').getBoundingClientRect(),c=document.querySelector('.journey-canvas-root').getBoundingClientRect();return c.bottom<=a.top+1}))
    await actions.locator('.recovery-toggle').focus();await page.keyboard.press('Escape');assert.equal(await actions.locator('.recovery-body').count(),0);assert.equal(await actions.locator('.recovery-toggle').evaluate(el=>el===document.activeElement),true);await page.keyboard.press('Space');await actions.locator('.recovery-body').waitFor();await page.screenshot({path:join(scratch,'recovery-'+theme+'-'+width+'.png')})
    report.presentation??=[];report.presentation.push({theme,width,background:await actions.evaluate(el=>getComputedStyle(el).backgroundColor),hitTargets:true,keyboard:true,focus:true,separateCanvas:true})
   }
   pass('actual desktop/390px light/dark recovery controls: 44px real center hits, scrolling, pending-cancel abort, Escape/Space focus and no canvas overlap')
  }
  const popupPromise=page.waitForEvent('popup');await click(actions.getByRole('link',{name:expected[kind],exact:true}));const fresh=await popupPromise;await ready(fresh);assert.equal(new URL(fresh.url()).searchParams.get('room'),'one');assert.equal(await fresh.evaluate(()=>window.editor.getShape('shape:retained')),undefined);await fresh.close();await new Promise(r=>setTimeout(r,200));assert.equal(clientFrames.slice(paused).some(frame=>frame.includes('old buffer after repair')),false)
  assert.ok(!(await doc()).snapshot.documents.some(d=>d.state.id==='shape:retained'))
  pass('mounted '+i+' '+kind+' keeps exact original room/read-only editor, maps the matching explicit action, retains versions and sends no old buffer after reauthorization')
 }
 await open();await page.route('**/auth/entry?**',async route=>{const response=await route.fetch(),value=await response.json();if(response.ok&&value.room==='one')value.expiresAt=Date.now()+60100;await route.fulfill({response,json:value})});await page.route('**/auth/renew?**',route=>route.fulfill({status:401,contentType:'application/json',body:JSON.stringify({category:'human_revalidation_due'})}));await page.reload();await cause('expired').waitFor();await page.unroute('**/auth/entry?**');await page.unroute('**/auth/renew?**');pass('actual HumanEntry renewal timer propagates typed seven-day refusal to the retained native canvas without unmount/resume')
 await open();drop=true;await edit('ordinary offline retained');await page.getByText(/已儲存本機 v1/).waitFor();await context.setOffline(true);await cause('unavailable').waitFor();await context.setOffline(false);const offlineFrames=clientFrames.length;drop=false;await edit('offline old buffer');await new Promise(r=>setTimeout(r,250));assert.equal(clientFrames.length,offlineFrames);pass('ordinary browser offline is unavailable, never revoked or repair-required, and reconnect does not flush the paused native store')
 await open();drop=true;await edit('unknown selected apply');await page.getByText(/已儲存本機 v1/).waitFor();latestSocket.close();await cause('unavailable').waitFor();drop=false
 await click(page.getByRole('button',{name:'本機草稿',exact:true}));await page.locator('.human-draft-body section').first().waitFor();await click(page.getByRole('button',{name:'檢視此版本',exact:true}).first());await page.getByTestId('detached-draft').waitFor();const retained=(await inventory()).length;let patches=0
 await page.route('**/doc?**',async route=>{if(route.request().method()!=='PATCH')return route.continue();patches++;await route.fetch();await route.abort()})
 await click(page.getByRole('button',{name:'確認套用這些變更',exact:true}));await page.getByText(/結果未確認或儲存失敗/).waitFor();assert.equal(patches,1);assert.equal((await inventory()).length,retained);await page.unroute('**/doc?**')
 await click(page.getByRole('button',{name:'關閉本機草稿',exact:true}));await cause('unknown').waitFor();await page.route('**/auth/identity',route=>route.fulfill({status:503,contentType:'application/json',body:'{}'}));await click(cause('unknown').getByRole('button',{name:'重新確認原身分與權限',exact:true}));await cause('unknown').getByText(/重新確認未完成/).waitFor();await page.unroute('**/auth/identity');await click(cause('unknown').getByRole('button',{name:'暫不恢復，保留暫停',exact:true}));assert.equal(patches,1);assert.equal((await inventory()).length,retained)
 await click(page.getByRole('button',{name:'本機草稿',exact:true}));await click(page.getByRole('button',{name:'檢視此版本',exact:true}).first());await page.getByRole('button',{name:'核對原操作，不重送',exact:true}).waitFor();assert.equal(patches,1);await click(page.getByRole('button',{name:'核對原操作，不重送',exact:true}));await page.getByText(/原操作、雲端紀錄及同步已核對/).waitFor();assert.equal((await inventory()).length,retained-1);assert.equal(await page.locator('.human-recovery[data-kind=unknown]').count(),0);assert.equal(await page.evaluate(()=>window.editor.getInstanceState().isReadonly),true);pass('actual dropped apply reply renders unknown recovery, retains every version without resend or cancel-cleanup, then explicit original receipt/readback/fresh sync removes only selected version')
 const final=await doc();assert.deepEqual(final.snapshot.documents.find(d=>d.state.id==='shape:seed').state,sentinel);assert.deepEqual(errors,[]);report.result='PASS';report.preservedBaselineRecordIds=baseline.snapshot.documents.map(d=>d.state.id)
}catch(error){report.error=String(error);report.logs=logs;report.visibleProblem=await page?.locator('.human-draft-body [role=status]').innerText().catch(()=>null);if(page)await page.screenshot({path:join(scratch,'failure.png')}).catch(()=>{});throw error}
finally{await browser?.close();await vite?.close();db?.close();await host?.close();if(child&&child.exitCode===null)child.kill('SIGTERM');report.finishedAt=new Date().toISOString();await writeFile(join(scratch,'report.json'),JSON.stringify(report,null,2));console.log('evidence='+join(scratch,'report.json'))}
