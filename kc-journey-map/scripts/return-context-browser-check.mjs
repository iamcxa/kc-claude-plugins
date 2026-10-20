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
const scratch=await mkdtemp(join(root,'.host-check/return-'+adapter+'-'))
const port=()=>new Promise(resolve=>{const s=createServer();s.listen(0,'127.0.0.1',()=>{const p=s.address().port;s.close(()=>resolve(p))})})
const apiPort=await port(),uiPort=await port(),origin='http://127.0.0.1:'+uiPort,api='http://127.0.0.1:'+apiPort,time=Date.now(),hash=s=>createHash('sha256').update(s).digest('hex')
const issuer=adapter==='node'?'local:draft':'https://draft.synthetic.invalid'
const config={version:1,backendId:'return-'+adapter,origin,mode:adapter==='node'?'local':'cloudflare',issuer,audience:'synthetic',localOwnerUid:process.geteuid(),localMemberId:'owner',members:[{id:'owner',issuer,subject:adapter==='node'?'uid:'+process.geteuid():'owner',label:'Synthetic owner',role:'operator',rooms:[{id:'one',expiresAt:time+3600000},{id:'two',expiresAt:time+3600000}]},{id:'other',issuer,subject:'other-subject',label:'Synthetic other',role:'member',rooms:[{id:'one',expiresAt:time+3600000}]}]}
const grants=[{credentialId:'seed',secretDigest:hash('s'.repeat(43)),principalId:'seed',rooms:['one','two'],expiresAt:time+3600000,revoked:false}]
const dataDir=await mkdtemp(join(tmpdir(),'return-data-')),configFile=join(scratch,'human.json'),grantsFile=join(scratch,'grants.json')
await writeFile(configFile,JSON.stringify(config));await writeFile(grantsFile,JSON.stringify(grants))
const report={adapter,candidate:execFileSync('git',['-C',root,'rev-parse','HEAD'],{encoding:'utf8'}).trim(),dirty:!!execFileSync('git',['-C',root,'status','--porcelain'],{encoding:'utf8'}).trim(),checks:[],provider:'NOT RUN; synthetic typed sessions',physicalDevice:'NOT RUN',browser:chromium.executablePath()}
const pass=name=>{report.checks.push(name);console.log('PASS '+name)}
const faults={name:'synthetic-draft-audit-faults',setup(builder){builder.onLoad({filter:/host\/audit\.ts$/},async args=>{
 let contents=await readFile(args.path,'utf8')
 assert.ok(contents.includes(" const reserved=await host.meta.security('reserve'"))
 contents=contents.replace(" const reserved=await host.meta.security('reserve'"," if(await host.meta.get('synthetic:draft-reserve-fault'))throw new HostError(503,'synthetic_reserve_failure')\n const reserved=await host.meta.security('reserve'")
 contents=contents.replaceAll("try {await host.meta.security('finalize'","try {if(await host.meta.get('synthetic:draft-finalize-fault'))throw new Error('synthetic finalize fault');await host.meta.security('finalize'")
 return {contents,loader:'ts'}
})}}
let child,host,db,metadata,vite,browser,page,logs=''
const seed=(path,method='GET',body)=>fetch(api+path,{method,headers:{Authorization:'Bearer seed.'+'s'.repeat(43),...(body?{'Content-Type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{})})
const doc=async()=>{const r=await seed('/doc?room=one');assert.equal(r.status,200);return r.json()}
const wait=async fn=>{for(let i=0;i<150;i++){if(await fn())return;await new Promise(r=>setTimeout(r,100))}throw Error('bounded condition timed out')}
const click=async loc=>{await loc.scrollIntoViewIfNeeded();assert.ok(await loc.evaluate(el=>{const r=el.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return r.width>=44&&r.height>=44&&(hit===el||el.contains(hit))}));await loc.click()}
try{
 if(adapter==='cloudflare-local'){
  await symlink(join(root,'node_modules'),join(dataDir,'node_modules'),'dir')
  host=await startCloudflare({dir:dataDir,port:apiPort,origin,grants,humanConfig:config,plugins:[faults]})
  const ns=await host.mf.getDurableObjectNamespace('REGISTRY'),registry=ns.get(ns.idFromName('private-pilot'))
  metadata=async(operation,body)=>{const r=await registry.fetch('https://registry/'+operation,{method:'POST',body:JSON.stringify(body)});assert.equal(r.status,200,await r.clone().text());return r.json()}
 }else{
  const bundle=join(scratch,'server.mjs');await build({entryPoints:[join(root,'server/canvas-server.ts')],outfile:bundle,bundle:true,format:'esm',platform:'node',packages:'external',plugins:[faults],logLevel:'silent'})
  child=spawn(process.execPath,[bundle],{cwd:root,env:{...process.env,JOURNEY_PRIVATE_DIR:dataDir,JOURNEY_GRANTS_FILE:grantsFile,JOURNEY_HUMAN_CONFIG:configFile,JOURNEY_ORIGIN:origin,JOURNEY_API_PORT:String(apiPort)},stdio:['ignore','pipe','pipe']});child.stdout.on('data',d=>{logs+=d});child.stderr.on('data',d=>{logs+=d})
  await wait(async()=>{try{return(await seed('/health')).ok}catch{if(child.exitCode!==null)throw Error(logs);return false}})
  db=new DatabaseSync(join(dataDir,'metadata.sqlite'))
  metadata=async(operation,body)=>{if(operation==='put'){db.prepare('INSERT OR REPLACE INTO metadata VALUES (?,?)').run(body.key,JSON.stringify(body.value));return{ok:true}}const r=db.prepare('SELECT value FROM metadata WHERE key=?').get(body.key);return r?JSON.parse(r.value):null}
 }
 for(const room of ['one','two']){await metadata('put',{key:'room:'+room,value:{createdAt:time}});await seed('/doc?room='+room)}
 const before=await doc(),pageId=before.snapshot.documents.find(d=>d.state.typeName==='page').state.id
 const sentinel=note({id:'shape:seed',text:'untouched synthetic base',x:300,y:200,parentId:pageId})
 assert.equal((await seed('/doc?room=one','PATCH',{put:[sentinel]})).status,200)
 const baseline=await doc()
 for(const member of ['owner','other'])await metadata('put',{key:'browser-session:'+hash('return-'+member),value:{actorType:'human',backendId:config.backendId,memberId:member,generation:1,expiresAt:time+900000,verifiedHumanSignInAt:time,humanRevalidateBy:time+604800000,csrfDigest:hash('csrf-'+member),revoked:false}})
 process.env.JOURNEY_API_PORT=String(apiPort);process.env.VITE_JOURNEY_HUMAN_ENTRY='true';if(adapter==='node')process.env.JOURNEY_HUMAN_CONFIG=configFile
 vite=await viteServer({configFile:join(root,'vite.config.mts'),cacheDir:join(scratch,'vite-cache'),server:{host:'127.0.0.1',port:uiPort,strictPort:true}});await vite.listen()
 browser=await chromium.launch({headless:true});report.browserVersion=browser.version()
 const context=await browser.newContext({viewport:{width:1280,height:900}})
 const cookies=member=>context.addCookies([{name:'journey_human',value:'return-'+member,url:origin,httpOnly:true,sameSite:'Strict'},{name:'journey_human_csrf',value:'csrf-'+member,url:origin,sameSite:'Strict'}])
 await cookies('owner')
 await context.route('**/*',route=>{const u=new URL(route.request().url());if(u.origin===origin)return route.continue();if(u.hostname==='cdn.tldraw.com')return route.fulfill({path:join(root,'.host-check/assets/package',u.pathname.replace(/^\/[^/]+\//,''))});return route.abort()})
 page=await context.newPage();page.on('console',m=>{if(m.type()==='warning')console.log('browser warning: '+m.text())});const errors=[];page.on('pageerror',e=>errors.push(e.message))
 let drop=false,blockSockets=false,blockedSockets=0,clientFrames=[],latestSocket
 await context.routeWebSocket(url=>url.pathname.startsWith('/connect/'),socket=>{latestSocket=socket;if(blockSockets){blockedSockets++;socket.close();return}const server=socket.connectToServer();socket.onMessage(message=>{clientFrames.push(String(message));if(!drop || !String(message).includes('"type":"push"'))server.send(message)})})
 const ready=async()=>page.waitForFunction(()=>window.editor&&document.querySelector('[data-testid="room-trigger"]')?.title.endsWith('Connected'))
 const editorRecord=text=>page.evaluate(record=>window.editor.store.put([record]),note({id:'shape:retained',text,x:440,y:400,parentId:pageId}))
 const inventory=()=>page.evaluate(async owner=>{const {humanDrafts}=await import('/human-drafts.ts');return(await humanDrafts()).inventory({...owner,origin:location.origin})},{backend:config.backendId,member:'owner',issuer,subject:config.members[0].subject,generation:1,room:'one',signInAt:time,revalidateBy:time+604800000})
 await page.goto(origin+'/');await page.getByText('請選擇你有權限的既有畫布。').waitFor();assert.equal(await page.evaluate(()=>!!window.editor),false)
 await page.goto(origin+'/?room=one');await ready()
 await wait(async()=>page.evaluate(async()=>{const {humanDrafts}=await import('/human-drafts.ts');const r=await fetch('/auth/entry?room=one').then(r=>r.json());return(await(await humanDrafts()).history({origin:location.origin,backend:r.backendId,member:r.memberId,issuer:r.issuer,subject:r.subject}))==='one'}))
 await page.goto(origin+'/');await ready();assert.equal(new URL(page.url()).searchParams.get('room'),'one')
 pass('initial successful sync commits scoped IndexedDB history; no-URL reload resumes exact permitted room')
 await page.goto(origin+'/?room=denied');await page.getByText(/你無法進入指定畫布/).waitFor();assert.equal(await page.evaluate(()=>!!window.editor),false)
 blockSockets=true;const blockedBefore=blockedSockets;await page.goto(origin+'/?room=two');await wait(async()=>blockedSockets>blockedBefore);await page.getByText(/雲端未連線或已暫停/).waitFor();assert.equal(await page.evaluate(()=>!!window.editor),false);blockSockets=false
 assert.equal(await page.evaluate(async()=>{const {humanDrafts}=await import('/human-drafts.ts');const r=await fetch('/auth/identity').then(r=>r.json());return(await humanDrafts()).history({origin:location.origin,backend:r.backendId,member:r.memberId,issuer:r.issuer,subject:r.subject})}),'one')
 await page.goto(origin+'/');await ready();assert.equal(new URL(page.url()).searchParams.get('room'),'one')
 pass('denied explicit URL mounts no substitute and admitted-but-failed initial sync never replaces last successful room history')
 await click(page.getByRole('button',{name:'本機草稿',exact:true}));await page.getByText('沒有可列出的本機版本；其他身分的草稿不會顯示。').waitFor();await click(page.getByRole('button',{name:'關閉本機草稿'}))
 pass('first-use empty draft inventory is reachable and does not create or restore any document')
 drop=true;await editorRecord('draft first');await page.getByText('已儲存本機 v1',{exact:false}).waitFor();await editorRecord('draft second');await page.getByText('已儲存本機 v2',{exact:false}).waitFor()
 assert.ok(!(await doc()).snapshot.documents.some(d=>d.state.id==='shape:retained'))
 const ownVersions=await inventory();assert.equal(ownVersions.length,2);const sourceSocket=latestSocket
 const another=await context.newPage();await another.goto(origin+'/?room=one');await another.waitForFunction(()=>window.editor&&document.querySelector('[data-testid="room-trigger"]')?.title.endsWith('Connected'));await another.evaluate(record=>window.editor.store.put([record]),note({id:'shape:other-tab',text:'independent tab draft',x:100,y:300,parentId:pageId}));await another.getByText('已儲存本機 v1',{exact:false}).waitFor();await another.close();assert.equal((await inventory()).length,3);const otherKey=(await inventory()).find(v=>v.key[4]!==ownVersions[0].key[4]).key
 sourceSocket.close();await page.getByText(/Source access paused/).first().waitFor();drop=false
 await page.reload();await ready();await click(page.getByRole('button',{name:'本機草稿',exact:true}))
 await wait(async()=>await page.locator('.human-draft-body section').count()===3)
 const versionRow=n=>rowForKey(ownVersions.find(v=>v.key[5]===n).key)
 const rowForKey=key=>page.locator('.human-draft-body section').filter({has:page.getByRole('heading',{name:'版本 '+key[5]+' · 分頁 '+key[4].slice(0,8),exact:true})})
 await click(versionRow(1).getByRole('button',{name:'檢視此版本'}));await page.getByTestId('detached-draft').waitFor()
 const frameCount=clientFrames.length;await new Promise(r=>setTimeout(r,300));assert.equal(clientFrames.length,frameCount)
 assert.ok(!(await doc()).snapshot.documents.some(d=>d.state.id==='shape:retained'))
 await click(page.getByRole('button',{name:'確認套用這些變更'}));await page.getByText(/恢復與雲端同步已核對/).waitFor()
 assert.equal((await inventory()).length,2);assert.ok((await doc()).snapshot.documents.some(d=>d.state.id==='shape:retained'&&JSON.stringify(d.state).includes('draft first')))
 pass('real newer and other-tab versions survive disconnect/reload; selected draft opens detached with zero outgoing frames; explicit original receipt/readback/sync clears only v1')
 await click(versionRow(2).getByRole('button',{name:'檢視此版本'}))
 await page.getByTestId('detached-draft').waitFor();await wait(async()=>!await page.getByRole('button',{name:'確認套用這些變更'}).isDisabled())
 const moved={...sentinel,x:sentinel.x+11};await seed('/doc?room=one','PATCH',{put:[moved]})
 await click(page.getByRole('button',{name:'確認套用這些變更'}));await page.getByText(/雲端已改變/).waitFor();assert.equal((await inventory()).length,2)
 pass('cloud movement between review and confirm forces review again and preserves selected version without apply')
 await click(page.getByRole('button',{name:'重新確認草稿'}));await click(versionRow(2).getByRole('button',{name:'檢視此版本'}))
 let patches=0
 await page.route('**/doc?**',async route=>{if(route.request().method()!=='PATCH')return route.continue();patches++;await route.fetch();await route.abort()})
 await click(page.getByRole('button',{name:'確認套用這些變更'}));await page.getByText(/結果未確認或儲存失敗/).waitFor();await page.unroute('**/doc?**')
 assert.equal(patches,1);assert.equal((await inventory()).length,2)
 await click(page.getByRole('button',{name:'重新確認草稿'}));await click(versionRow(2).getByRole('button',{name:'檢視此版本'}));await page.getByText(/不會自動重送/).waitFor()
 await click(page.getByRole('button',{name:'核對原操作，不重送'}));await page.getByText(/原操作、雲端紀錄及同步已核對/).waitFor();assert.equal((await inventory()).length,1);assert.equal(patches,1)
 pass('lost actual mutation reply retains unknown version and sends once; explicit original-attempt reconciliation plus fresh sync removes only its exact version')
 await click(page.getByRole('button',{name:'關閉本機草稿'}));await page.reload();await ready();drop=true;await editorRecord('account pending');await page.getByText('已儲存本機 v1',{exact:false}).waitFor();const accountTabId=(await inventory()).find(v=>v.key[4]!==otherKey[4]).key[4]
 const outgoing=clientFrames.length;const accountTab=await context.newPage();await accountTab.route('**/synthetic-account-switch',route=>route.fulfill({headers:{'Content-Type':'text/html','Set-Cookie':'journey_human=return-other; Path=/; HttpOnly; SameSite=Strict'},body:'<!doctype html><title>Synthetic account switched</title>'}));await accountTab.goto(origin+'/synthetic-account-switch');await editorRecord('account swapped');await page.getByText(/Source access paused/).first().waitFor();drop=false
 assert.ok(!clientFrames.slice(outgoing).some(s=>s.includes('account swapped')))
 await click(page.getByRole('button',{name:'本機草稿',exact:true}));await page.getByText(/身分已改變/).waitFor();assert.equal(await page.locator('.human-draft-body section').count(),0)
 await accountTab.close();await cookies('owner');await click(page.getByRole('button',{name:'重新確認草稿'}));await wait(async()=>await page.locator('.human-draft-body section').count()>0)
 assert.ok(!(await doc()).snapshot.documents.some(d=>JSON.stringify(d.state).includes('account swapped')))
 pass('actual other-tab HttpOnly cookie replacement with unchanged CSRF marker with queued edits pauses original transport; wrong member gets no inventory/content, reversion does not auto-flush')
 for(const theme of ['light','dark'])for(const width of [1280,390]){
  await page.setViewportSize({width,height:900});await page.emulateMedia({colorScheme:theme});await page.evaluate(theme=>window.editor.user.updateUserPreferences({colorScheme:theme}),theme)
  await page.waitForFunction(theme=>document.querySelector('.human-draft-dialog')?.dataset.theme===theme,theme)
  await click(page.getByRole('button',{name:'重新確認草稿'}));await wait(async()=>!await page.locator('.human-draft-body').getAttribute('aria-busy').then(v=>v==='true'));await page.screenshot({path:join(scratch,'drafts-'+theme+'-'+width+'.png')});await page.getByRole('button',{name:'關閉本機草稿'}).focus();await page.keyboard.press('Escape');await wait(async()=>await page.locator('dialog[open]').count()===0);assert.equal(await page.getByRole('button',{name:'本機草稿',exact:true}).evaluate(el=>el===document.activeElement),true);await click(page.getByRole('button',{name:'本機草稿',exact:true}))
 }
 pass('desktop/390px light/dark draft controls have actual 44px center hits, reachable scrolling, Escape dismissal and restored focus')
 const policy=await metadata('get',{key:'member-room:owner:one'});await metadata('put',{key:'member-room:owner:one',value:{...policy,revoked:true}})
 await click(page.getByRole('button',{name:'重新確認草稿'}));await page.getByText(/內容保持鎖定/).waitFor();assert.equal(await page.getByTestId('detached-draft').count(),0)
 const count=(await inventory()).length,first=rowForKey((await inventory()).find(v=>v.key[4]===accountTabId).key)
 await click(first.getByRole('button',{name:'刪除此版本'}));await click(page.getByRole('button',{name:'取消刪除'}));assert.equal((await inventory()).length,count)
 await click(first.getByRole('button',{name:'刪除此版本'}));await click(page.getByRole('button',{name:'確認刪除此版本'}));await page.getByText(/已刪除指定本機版本/).waitFor();assert.equal((await inventory()).length,count-1)
 pass('denied-room content stays locked; original-member content-free cancel preserves versions and explicit delete removes only selected version')
 await metadata('put',{key:'member-room:owner:one',value:policy})
 const seedLocal=async label=>{
  const base=Object.fromEntries((await doc()).snapshot.documents.map(d=>[d.state.id,d.state])),record=note({id:'shape:'+label,text:label,x:400,y:480,parentId:pageId})
  const value=await page.evaluate(async({base,record,owner})=>{const {humanDrafts}=await import('/human-drafts.ts');return(await humanDrafts()).save({...owner,origin:location.origin},crypto.randomUUID(),crypto.randomUUID(),base,{...base,[record.id]:record})},{base,record,owner:{backend:config.backendId,member:'owner',issuer,subject:config.members[0].subject,generation:1,room:'one',signInAt:time,revalidateBy:time+604800000}})
  await click(page.getByRole('button',{name:'重新確認草稿'}));await wait(async()=>await rowForKey(value.key).count()===1);await click(rowForKey(value.key).getByRole('button',{name:'檢視此版本'}));await page.getByTestId('detached-draft').waitFor();await wait(async()=>!await page.getByRole('button',{name:'確認套用這些變更'}).isDisabled());return{value,record}
 }
 const reserve=await seedLocal('reserve-fault')
 await metadata('put',{key:'synthetic:draft-reserve-fault',value:true});await click(page.getByRole('button',{name:'確認套用這些變更'}));await page.getByText(/結果未確認或儲存失敗/).waitFor();await metadata('put',{key:'synthetic:draft-reserve-fault',value:false})
 assert.ok(!(await doc()).snapshot.documents.some(d=>d.state.id===reserve.record.id))
 await seed('/doc?room=one','PATCH',{put:[reserve.record]})
 await click(page.getByRole('button',{name:'重新確認草稿'}));await click(rowForKey(reserve.value.key).getByRole('button',{name:'檢視此版本'}));await page.getByRole('button',{name:'核對原操作，不重送'}).waitFor();await click(page.getByRole('button',{name:'核對原操作，不重送'}));await page.getByText(/結果未確認或儲存失敗/).waitFor();assert.ok((await inventory()).some(v=>JSON.stringify(v.key)===JSON.stringify(reserve.value.key)))
 pass('actual adapter audit reservation failure prevents mutation; another writer producing equal state cannot justify original-attempt cleanup')
 const finalizing=await seedLocal('finalize-fault')
 await metadata('put',{key:'synthetic:draft-finalize-fault',value:true});await click(page.getByRole('button',{name:'確認套用這些變更'}));await page.getByText(/結果未確認或儲存失敗/).waitFor();await metadata('put',{key:'synthetic:draft-finalize-fault',value:false})
 assert.ok((await doc()).snapshot.documents.some(d=>d.state.id===finalizing.record.id))
 await click(page.getByRole('button',{name:'重新確認草稿'}));await click(rowForKey(finalizing.value.key).getByRole('button',{name:'檢視此版本'}));await page.getByRole('button',{name:'核對原操作，不重送'}).waitFor();await click(page.getByRole('button',{name:'核對原操作，不重送'}));await page.getByText(/原操作結果仍未確認/).waitFor();assert.ok((await inventory()).some(v=>JSON.stringify(v.key)===JSON.stringify(finalizing.value.key)))
 pass('actual adapter final receipt failure leaves committed document but unfinalized original outcome; equal readback never erases the retained unknown version')
 const syncing=await seedLocal('sync-fault');blockSockets=true
 await click(page.getByRole('button',{name:'確認套用這些變更'}));await page.getByText(/結果未確認或儲存失敗/).waitFor();assert.ok((await inventory()).some(v=>JSON.stringify(v.key)===JSON.stringify(syncing.value.key)));blockSockets=false
 await click(page.getByRole('button',{name:'重新確認草稿'}));await click(rowForKey(syncing.value.key).getByRole('button',{name:'檢視此版本'}));await page.getByRole('button',{name:'核對原操作，不重送'}).waitFor();await click(page.getByRole('button',{name:'核對原操作，不重送'}));await page.getByText(/原操作、雲端紀錄及同步已核對/).waitFor();assert.ok(!(await inventory()).some(v=>JSON.stringify(v.key)===JSON.stringify(syncing.value.key)))
 pass('actual fresh sync refusal retains selected version despite committed receipt/readback; later explicit reconciliation verifies sync before exact cleanup')
 const removable=note({id:'shape:explicit-remove',text:'explicit selected deletion',x:50,y:300,parentId:pageId});await seed('/doc?room=one','PATCH',{put:[removable]})
 const removeBase=Object.fromEntries((await doc()).snapshot.documents.map(d=>[d.state.id,d.state]))
 const removeVersion=await page.evaluate(async({base,owner})=>{const {humanDrafts}=await import('/human-drafts.ts');const records={...base};delete records['shape:explicit-remove'];return(await humanDrafts()).save({...owner,origin:location.origin},crypto.randomUUID(),crypto.randomUUID(),base,records)},{base:removeBase,owner:{backend:config.backendId,member:'owner',issuer,subject:config.members[0].subject,generation:1,room:'one',signInAt:time,revalidateBy:time+604800000}})
 await click(page.getByRole('button',{name:'重新確認草稿'}));await wait(async()=>await rowForKey(removeVersion.key).count()===1);await click(rowForKey(removeVersion.key).getByRole('button',{name:'檢視此版本'}));await page.getByTestId('detached-draft').waitFor();await page.getByText(/刪除 1 筆/).waitFor();await click(page.getByRole('button',{name:'確認套用這些變更'}));await page.getByText(/恢復與雲端同步已核對/).waitFor();assert.ok(!(await doc()).snapshot.documents.some(d=>d.state.id===removable.id));assert.ok(!(await inventory()).some(v=>JSON.stringify(v.key)===JSON.stringify(removeVersion.key)))
 pass('explicit selected-version remove operations delete the exact intended cloud record and clean that version only after receipt/readback/sync')
 const ownerMember=await metadata('get',{key:'member:owner'}),renewedAt=Date.now()
 await metadata('put',{key:'member:owner',value:{...ownerMember,generation:2}})
 await metadata('put',{key:'browser-session:'+hash('return-owner-new'),value:{actorType:'human',backendId:config.backendId,memberId:'owner',generation:2,expiresAt:renewedAt+900000,verifiedHumanSignInAt:renewedAt,humanRevalidateBy:renewedAt+604800000,csrfDigest:hash('csrf-new'),revoked:false}})
 await context.addCookies([{name:'journey_human',value:'return-owner-new',url:origin,httpOnly:true,sameSite:'Strict'},{name:'journey_human_csrf',value:'csrf-new',url:origin,sameSite:'Strict'}])
 const beforeReauthCount=(await inventory()).length;await click(page.getByRole('button',{name:'重新確認草稿'}));await wait(async()=>await rowForKey(otherKey).count()===1);assert.equal((await inventory()).length,beforeReauthCount)
 await click(rowForKey(otherKey).getByRole('button',{name:'檢視此版本'}));await page.getByTestId('detached-draft').waitFor();await click(page.getByRole('button',{name:'確認套用這些變更'}));await page.getByText(/恢復與雲端同步已核對/).waitFor();assert.ok(!(await inventory()).some(v=>JSON.stringify(v.key)===JSON.stringify(otherKey)))
 pass('a fresh verified sign-in/generation for the same original person can explicitly restore an older other-tab draft, without automatic adoption or deletion on regrant')
 const unknownBase=await page.evaluate(async owner=>{const {humanDrafts}=await import('/human-drafts.ts');const current=await fetch('/doc?room=one&'+new URLSearchParams({_human:'owner',_backend:owner.backend,_humanAt:String(owner.signInAt),_humanRoom:'one'})).then(r=>r.json());const records=Object.fromEntries(current.snapshot.documents.map(d=>[d.state.id,d.state]));return(await humanDrafts()).save({...owner,origin:location.origin},crypto.randomUUID(),crypto.randomUUID(),null,records)},{backend:config.backendId,member:'owner',issuer,subject:config.members[0].subject,generation:2,room:'one',signInAt:renewedAt,revalidateBy:renewedAt+604800000})
 await click(page.getByRole('button',{name:'重新確認草稿'}));await wait(async()=>await rowForKey(unknownBase.key).count()===1);await click(rowForKey(unknownBase.key).getByRole('button',{name:'檢視此版本'}));await page.getByText(/原始雲端版本不明/).waitFor();assert.equal(await page.getByTestId('detached-draft').count(),0);assert.ok((await inventory()).some(v=>JSON.stringify(v.key)===JSON.stringify(unknownBase.key)))
 pass('unknown-base draft remains retained with no preview/apply authority instead of adopting current cloud as an invented base')
 const unsupported=await context.newPage();await unsupported.addInitScript(()=>{const original=IDBDatabase.prototype.transaction;IDBDatabase.prototype.transaction=function(stores,mode,options){return original.call(this,stores,mode,options?.durability==='strict'?{durability:'relaxed'}:options)}})
 drop=true;await unsupported.goto(origin+'/?room=one');await unsupported.waitForFunction(()=>!!window.editor);await unsupported.evaluate(record=>window.editor.store.put([record]),note({id:'shape:unsupported-save',text:'unacknowledged current work',x:500,y:500,parentId:pageId}));await unsupported.getByText(/未儲存本機版本/).waitFor();assert.ok(await unsupported.evaluate(()=>!!window.editor.getShape('shape:unsupported-save')));await unsupported.close();drop=false
 pass('UI refuses local-saved acknowledgment for actual relaxed transactions while retaining visible unacknowledged editor work')
 const final=await doc();assert.deepEqual(final.snapshot.documents.find(d=>d.state.id==='shape:seed').state,moved)
 assert.deepEqual(errors,[]);report.result='PASS';report.preservedBaselineRecordIds=baseline.snapshot.documents.map(d=>d.state.id)
}catch(error){report.error=String(error);report.logs=logs;report.visibleProblem=await page?.locator('.human-draft-body [role=status]').innerText().catch(()=>null);if(page)await page.screenshot({path:join(scratch,'failure.png')}).catch(()=>{});throw error}
finally{await browser?.close();await vite?.close();db?.close();await host?.close();if(child&&child.exitCode===null)child.kill('SIGTERM');await writeFile(join(scratch,'report.json'),JSON.stringify(report,null,2));console.log('evidence='+join(scratch,'report.json'))}
