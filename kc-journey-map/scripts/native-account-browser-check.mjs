import assert from 'node:assert/strict'
import { writeFile,mkdir } from 'node:fs/promises'
import { join } from 'node:path'
import { chromium } from 'playwright'
import { DatabaseSync } from 'node:sqlite'
import { startFixture,hash,root } from './native-account-fixture.mjs'
const f=await startFixture(),browser=await chromium.launch({headless:true})
const report={checks:[],screenshots:[],limits:['Local synthetic accounts only; no production provider, email or physical mobile keyboard'],origin:f.origin}
const pass=name=>{report.checks.push(name);console.log('PASS '+name)}
const context=await browser.newContext({viewport:{width:1280,height:800}}),page=await context.newPage(),errors=[]
page.on('pageerror',error=>errors.push(error.message))
const click=async locator=>{await locator.scrollIntoViewIfNeeded();const hit=await locator.evaluate(el=>{const r=el.getBoundingClientRect(),target=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return target===el||el.contains(target)});assert.ok(hit,'hit-test '+await locator.innerText());await locator.click()}
async function login(p=page){
 await click(p.getByRole('button',{name:'開始本機帳號驗證',exact:true}))
 const id=await p.locator('.human-entry code').innerText();assert.match(f.approve(id),/"approved": true/)
 await click(p.getByRole('button',{name:'我已在本機核准'}))
 await p.waitForFunction(()=>!!window.editor)
}
async function account(p=page){await click(p.getByTestId('main-menu.button'));await click(p.getByRole('menuitem',{name:'我的帳號',exact:true}));await p.getByRole('heading',{name:'我的帳號',exact:true}).waitFor()}
async function logout(p=page){await account(p);await click(p.getByRole('button',{name:'登出',exact:true}));await p.getByRole('heading',{name:'登出目前帳號？'}).waitFor()}
const db=new DatabaseSync(join(f.dataDir,'metadata.sqlite'))
const read=key=>{const row=db.prepare('SELECT value FROM metadata WHERE key=?').get(key);return row?JSON.parse(row.value):null}
const put=(key,value)=>db.prepare('INSERT OR REPLACE INTO metadata VALUES (?,?)').run(key,JSON.stringify(value))
try{
 await page.goto(f.origin+'/?room=one');await login()
 await account();assert.equal(await page.getByRole('button',{name:'管理目前房間成員'}).count(),0)
 await page.keyboard.press('Escape')
 const token=(await context.cookies()).find(c=>c.name==='journey_human').value,sessionDigest=hash(token)
 const binding={backendId:'synthetic-native',ownerMemberId:'owner',issuer:'local:synthetic-native',subject:'uid:'+process.geteuid(),sessionDigest,initializationOperationId:'synthetic-owner-init'}
 assert.equal((await f.control({op:'owner-bind',writersStopped:true,input:binding})).bound,true)
 const human=await context.request.get(f.origin+'/auth/entry?room=one').then(r=>r.json())
 const path=(suffix,room='one',who=human)=>suffix+'?'+new URLSearchParams({_human:who.memberId,_backend:who.backendId,_humanAt:String(who.verifiedHumanSignInAt),_humanRoom:room})
 assert.equal((await context.request.get(f.origin+'/auth/room-members')).status(),403)
 assert.equal((await context.request.get(f.origin+path('/auth/room-members','denied'))).status(),403)
 assert.equal((await context.request.get(f.origin+path('/auth/room-members'),{headers:{Authorization:'Bearer synthetic.'+'s'.repeat(43)}})).status(),403)
 pass('actual Node operator path creates verified immutable owner; unauthenticated/context/room/bearer bypasses denied')
 for(const width of [1280,390])for(const theme of ['light','dark']){
  await page.setViewportSize({width,height:800});await page.evaluate(theme=>window.editor.user.updateUserPreferences({colorScheme:theme}),theme)
  await account();await page.getByRole('button',{name:'管理目前房間成員'}).waitFor()
  const a=join(f.scratch,width+'-'+theme+'-account.png');await page.screenshot({path:a});report.screenshots.push(a)
  await click(page.getByRole('button',{name:'管理目前房間成員'}))
  await page.getByRole('heading',{name:'目前房間成員與存取'}).waitFor();await page.getByText('Synthetic member',{exact:true}).waitFor()
  assert.equal(await page.getByRole('button',{name:/邀請|移除/}).count(),0)
  const b=join(f.scratch,width+'-'+theme+'-members.png');await page.screenshot({path:b});report.screenshots.push(b)
  await page.keyboard.press('Escape')
  await click(page.getByRole('button',{name:'save',exact:true}));await page.getByRole('textbox',{name:'Filename'}).waitFor()
  const save=join(f.scratch,width+'-'+theme+'-save.png');await page.screenshot({path:save});report.screenshots.push(save)
  await click(page.getByRole('button',{name:'Cancel',exact:true}))
  await page.evaluate(()=>{window.editor.createShape({id:'shape:synthetic-document',type:'note',x:100,y:100,props:{url:'https://github.com/synthetic/notes/blob/main/README.md#synthetic-fixture'}});window.editor.select('shape:synthetic-document')})
  await click(page.locator('a.tl-hyperlink-button'))
  await page.getByRole('dialog').getByText('Only local synthetic document content.',{exact:false}).waitFor()
  const doc=join(f.scratch,width+'-'+theme+'-document.png');await page.screenshot({path:doc});report.screenshots.push(doc)
  await click(page.getByRole('button',{name:'Close',exact:true}));await page.evaluate(()=>window.editor.deleteShapes(['shape:synthetic-document']))
  await logout()
  const c=join(f.scratch,width+'-'+theme+'-logout.png');await page.screenshot({path:c});report.screenshots.push(c)
  await click(page.getByRole('button',{name:'取消',exact:true}));assert.ok(await page.evaluate(()=>!!window.editor))
 }
 pass('1280/390 light/dark native account, room, save, synthetic local document and logout cancel; controls hit-tested')
 assert.equal(await page.locator('.agent-account,.human-draft-bar').count(),0)
 await click(page.getByTestId('room-trigger'));await click(page.locator('[data-room-id="two"]'));await page.waitForURL('**room=two');await page.waitForFunction(()=>!!window.editor)
 await account();await click(page.getByRole('button',{name:'管理目前房間成員'}));await page.getByText('目前房間：two',{exact:true}).waitFor()
 assert.equal(await page.getByText('Synthetic member',{exact:true}).count(),0);await page.keyboard.press('Escape')
 await click(page.getByTestId('room-trigger'));await click(page.getByRole('menuitem',{name:'管理目前房間成員'}));await page.getByText('目前房間：two',{exact:true}).waitFor();await page.keyboard.press('Escape')
 pass('A to B shortcut and room menu share guarded current-room destination; no persistent outer control bars')
 const verifier='a'.repeat(64),installationRequest=crypto.randomUUID()
 const installation=async(op,body)=>fetch('http://127.0.0.1:'+f.apiPort+'/agents/'+op,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({backendId:'synthetic-native',...body})})
 const started=await installation('start',{requestId:installationRequest,installationId:crypto.randomUUID(),memberId:'owner',rooms:['two'],label:'Synthetic native agent',verifier}).then(r=>r.json())
 await account();await click(page.getByRole('button',{name:'本人代理',exact:true}));await page.getByRole('heading',{name:'本人代理',exact:true}).waitFor()
 await page.getByLabel('配對碼').fill(started.code);await click(page.getByRole('button',{name:'檢視配對請求'}));await click(page.getByRole('button',{name:'核准這些畫布與能力'}));await page.getByText('已核准，等待原安裝兌換；尚未簽發安裝憑證。',{exact:true}).waitFor()
 const issued=await installation('redeem',{requestId:installationRequest,verifier}).then(r=>r.json())
 assert.ok(issued.accessToken)
 assert.equal((await fetch('http://127.0.0.1:'+f.apiPort+'/auth/room-members',{headers:{Authorization:'Bearer '+issued.accessToken}})).status,403)
 await click(page.getByRole('button',{name:'更新代理清單'}));await page.getByText('Synthetic native agent',{exact:true}).waitFor()
 await click(page.getByRole('button',{name:'撤銷此安裝',exact:true}));await click(page.getByRole('button',{name:'取消撤銷'}));await page.keyboard.press('Escape')
 pass('native own-agent dialog inspects/approves real helper request and original redemption, lists installation, cancels revoke; actual agent cannot read owner list')

 const before=await f.api('/doc?room=two').then(r=>r.json())
 await page.evaluate(()=>window.editor.createShape({id:'shape:synthetic-retained',type:'geo',x:10,y:10,props:{w:100,h:100}}))
 const retained=await page.evaluate(()=>window.editor.getShape('shape:synthetic-retained'))
 await page.waitForTimeout(300)
 const other=await context.newPage();await other.goto(f.origin+'/?room=two');await other.waitForFunction(()=>!!window.editor)
 let writes=0;page.on('request',r=>{if(new URL(r.url()).pathname==='/auth/logout')writes++})
 await logout();await click(page.getByRole('button',{name:'確認登出'}))
 await page.getByText('應用程式登入已結束。',{exact:false}).waitFor()
 assert.equal(await page.locator('.tl-container,.agent-account,.human-draft-bar').count(),0)
 assert.equal(await page.evaluate(()=>!!window.editor),false)
 await other.getByRole('heading',{name:'目前已停止存取'}).waitFor();assert.equal(await other.evaluate(()=>!!window.editor),false);await other.close()
 assert.equal(writes,1);assert.equal(read('browser-session:'+sessionDigest).revoked,true);assert.equal(read('agent-family:'+issued.family.id).revoked,false);assert.equal(read('member:owner').generation,1);assert.equal(read('member-room:owner:two').generation,1)
 assert.doesNotMatch(await page.locator('main').innerText(),/Synthetic owner|synthetic-retained|two/)
 await page.reload();await page.getByRole('heading',{name:'目前已停止存取'}).waitFor();assert.equal(await page.evaluate(()=>!!window.editor),false)
 await login()
 assert.equal(new URL(page.url()).searchParams.get('room'),'two')
 await click(page.getByTestId('main-menu.button'));await click(page.getByRole('menuitem',{name:'本機草稿',exact:true}));await page.getByRole('heading',{name:'本機草稿',exact:true}).waitFor();await page.getByRole('button',{name:'檢視此版本'}).first().waitFor();await page.keyboard.press('Escape')
 assert.equal(read('owner:synthetic-native').initializationOperationId,binding.initializationOperationId)
 pass('confirmed real logout writes once, revokes session, unmounts both tabs, persists privacy on reload; real owner reentry retains explicit B and drafts')
 await page.route('**/auth/logout?**',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({category:'host_unavailable'})}))
 await logout();await click(page.getByRole('button',{name:'確認登出'}));await page.getByRole('heading',{name:'登出結果未確認'}).waitFor();assert.equal(await page.evaluate(()=>!!window.editor),false)
 await page.reload();await page.getByRole('heading',{name:'登出結果未確認'}).waitFor();assert.equal(writes,2)
 await page.unroute('**/auth/logout?**');await click(page.getByRole('button',{name:'重新驗證入口'}));await page.waitForFunction(()=>!!window.editor)
 pass('network/unknown logout hides private canvas, truthfully persists unknown on reload and does not replay POST')
 await context.setOffline(true)
 await page.evaluate(()=>window.editor.createShape({id:'shape:unsynced-retained',type:'geo',x:140,y:10,props:{w:80,h:80}}))
 await logout();await click(page.getByRole('button',{name:'確認登出'}));await page.getByRole('heading',{name:'登出結果未確認'}).waitFor()
 await context.setOffline(false)
 await click(page.getByRole('button',{name:'重新驗證入口'}));await page.waitForFunction(()=>!!window.editor)
 assert.equal(await page.evaluate(()=>!!window.editor.getShape('shape:unsynced-retained')),false);assert.deepEqual(await page.evaluate(()=>window.editor.getShape('shape:synthetic-retained')),retained)
 await click(page.getByTestId('main-menu.button'));await click(page.getByRole('menuitem',{name:'本機草稿',exact:true}));await page.getByRole('button',{name:'檢視此版本'}).first().waitFor();await page.keyboard.press('Escape')
 pass('unsynced offline content survives logout as local versions and is never automatically applied to fresh cloud canvas')
 await logout();await click(page.getByRole('button',{name:'確認登出'}));await page.getByText('應用程式登入已結束。',{exact:false}).waitFor()
 let releaseStart,seenStart
 const startSeen=new Promise(resolve=>{seenStart=resolve})
 await page.route('**/auth/local/start',async route=>{const response=await route.fetch();seenStart();await new Promise(resolve=>{releaseStart=resolve});await route.fulfill({response}).catch(()=>{})})
 await click(page.getByRole('button',{name:'開始本機帳號驗證',exact:true}));await startSeen
 await click(page.getByRole('button',{name:'取消登入'}));releaseStart();await page.waitForTimeout(100)
 assert.equal(await page.locator('.human-entry code').count(),0);assert.equal(await page.evaluate(()=>!!window.editor),false)
 await page.unroute('**/auth/local/start');await page.reload();await page.getByRole('heading',{name:'登入已取消'}).waitFor();await login()
 let releaseEntry,seenEntry
 const entrySeen=new Promise(resolve=>{seenEntry=resolve})
 await page.route('**/auth/entry?**',async route=>{const response=await route.fetch();seenEntry();await new Promise(resolve=>{releaseEntry=resolve});await route.fulfill({response}).catch(()=>{})})
 await page.evaluate(()=>{sessionStorage.setItem('journey-native-session-hold','cancelled')});await page.reload();await page.getByRole('heading',{name:'登入已取消'}).waitFor()
 await click(page.getByRole('button',{name:'重新驗證入口'}));await entrySeen
 await click(page.getByRole('button',{name:'取消登入'}));releaseEntry();await page.waitForTimeout(100);assert.equal(await page.evaluate(()=>!!window.editor),false)
 await page.unroute('**/auth/entry?**');await click(page.getByRole('button',{name:'重新驗證入口'}));await page.waitForFunction(()=>!!window.editor)
 pass('cancelled actual local login-start and room-entry replies cannot reopen private canvas, including reload')
 const memberToken='synthetic-member-browser',memberSession={...read('browser-session:'+hash((await context.cookies()).find(c=>c.name==='journey_human').value)),memberId:'member'}
 put('browser-session:'+hash(memberToken),memberSession)
 const memberContext=await browser.newContext();await memberContext.addCookies([{name:'journey_human',value:memberToken,url:f.origin,httpOnly:true,sameSite:'Strict'},{name:'journey_human_csrf',value:(await context.cookies()).find(c=>c.name==='journey_human_csrf').value,url:f.origin,sameSite:'Strict'}])
 const memberPage=await memberContext.newPage();await memberPage.goto(f.origin+'/?room=one');await memberPage.waitForFunction(()=>!!window.editor)
 await account(memberPage);assert.equal(await memberPage.getByRole('button',{name:'管理目前房間成員'}).count(),0);await memberPage.keyboard.press('Escape')
 const m=await memberContext.request.get(f.origin+'/auth/entry?room=one').then(r=>r.json())
 assert.equal((await memberContext.request.get(f.origin+path('/auth/room-members','one',m))).status(),403)
 await memberContext.close()
 pass('actual synthetic ordinary-member session (even operator role) has no owner shortcut and guarded read is denied')
 let releaseLogout,seenLogout
 const logoutSeen=new Promise(resolve=>{seenLogout=resolve})
 await page.route('**/auth/logout?**',async route=>{const response=await route.fetch();seenLogout();await new Promise(resolve=>{releaseLogout=resolve});await route.fulfill({response}).catch(()=>{})})
 const beforeLate=writes
 await logout();await click(page.getByRole('button',{name:'確認登出'}));await logoutSeen
 await page.getByRole('heading',{name:'正在結束登入'}).waitFor();assert.equal(await page.evaluate(()=>!!window.editor),false)
 await page.reload();await page.getByRole('heading',{name:/正在結束登入|登出結果未確認/}).waitFor();releaseLogout();await page.waitForTimeout(100)
 assert.equal(writes,beforeLate+1);assert.equal(await page.evaluate(()=>!!window.editor),false)
 await page.unroute('**/auth/logout?**');await login()
 pass('delayed actual committed logout reply and reload keep private canvas closed, never replay the write, and require explicit real reentry')
 assert.deepEqual(errors,[])
 report.candidateTree='working candidate; exact committed tree recorded by implementation report'
 await writeFile(join(f.scratch,'report.json'),JSON.stringify(report,null,2));console.log('evidence='+join(f.scratch,'report.json'))
}catch(error){await page.screenshot({path:join(f.scratch,'failure.png')});await writeFile(join(f.scratch,'failure.txt'),await page.locator('body').innerText());console.log('failure evidence='+f.scratch);throw error}finally{db.close();await browser.close();await f.close()}
