import assert from 'node:assert/strict'
import { writeFile } from 'node:fs/promises'
import { join } from 'node:path'
import { chromium } from 'playwright'
import { DatabaseSync } from 'node:sqlite'
import { startFixture, hash } from './native-account-fixture.mjs'
const f=await startFixture()
let browser,db,page
const report={checks:[],screenshots:[],limits:['Local synthetic Node accounts only; no hosted provider, physical device or durable drafts'],origin:f.origin}
const pass=name=>{report.checks.push(name);console.log('PASS '+name)}
const click=async locator=>{await locator.scrollIntoViewIfNeeded();assert.ok(await locator.evaluate(el=>{const r=el.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return hit===el||el.contains(hit)}));await locator.click()}
async function login(p=page){
 await click(p.getByRole('button',{name:'開始本機帳號驗證',exact:true}))
 const id=await p.locator('.human-entry code').innerText();assert.match(f.approve(id),/"approved": true/)
 await click(p.getByRole('button',{name:'我已在本機核准'}));await p.waitForFunction(()=>!!window.editor)
}
async function account(p=page){await click(p.getByTestId('main-menu.button'));await click(p.getByRole('menuitem',{name:'我的帳號',exact:true}));await p.getByRole('heading',{name:'我的帳號',exact:true}).waitFor()}
async function returnedFocus(){await page.waitForFunction(()=>document.activeElement===document.querySelector('[data-testid="main-menu.button"]'),null,{timeout:3000})}
async function logout(){await account();await click(page.getByRole('button',{name:'登出',exact:true}));await page.getByRole('heading',{name:'登出目前帳號？'}).waitFor()}
try{
 browser=await chromium.launch({headless:true})
 const context=await browser.newContext({viewport:{width:1280,height:800}}),errors=[]
 page=await context.newPage();page.on('pageerror',error=>errors.push(error.message))
 db=new DatabaseSync(join(f.dataDir,'metadata.sqlite'))
 const read=key=>{const row=db.prepare('SELECT value FROM metadata WHERE key=?').get(key);return row?JSON.parse(row.value):null}
 await page.goto(f.origin+'/?room=one');await login()
 const sessionDigest=hash((await context.cookies()).find(c=>c.name==='journey_human').value)
 let posts=0;page.on('request',r=>{if(new URL(r.url()).pathname==='/auth/logout')posts++})
 for(const width of [1280,390])for(const theme of ['light','dark']){
  await page.setViewportSize({width,height:800});await page.evaluate(theme=>window.editor.user.updateUserPreferences({colorScheme:theme}),theme)
  await account();await page.getByText('目前權限已確認',{exact:true}).waitFor()
  assert.match(await page.getByRole('dialog').innerText(),/Synthetic owner/)
  assert.equal(await page.getByText('owner',{exact:true}).count(),1)
  assert.equal(await page.getByText('目前房間：one',{exact:true}).count(),1)
  assert.equal(await page.getByRole('button',{name:/本人代理|管理目前房間成員/}).count(),0)
  const image=join(f.scratch,width+'-'+theme+'-account.png');await page.screenshot({path:image});report.screenshots.push(image)
  await page.keyboard.press('Escape');await page.waitForFunction(()=>document.activeElement===document.querySelector('[data-testid="main-menu.button"]'),null,{timeout:3000})
  await logout();await click(page.getByRole('button',{name:'取消',exact:true}));await returnedFocus();assert.ok(await page.evaluate(()=>!!window.editor))
 }
 assert.equal(posts,0)
 await click(page.getByTestId('main-menu.button'));assert.equal(await page.getByRole('menuitem',{name:'本機草稿',exact:true}).count(),0);await page.keyboard.press('Escape')
 pass('1280/390 light/dark account identity, exact member/current room, menu focus return and logout cancel; no later-slice entries')
 await click(page.getByTestId('room-trigger'));await click(page.locator('[data-room-id="two"]'));await page.waitForURL('**room=two')
 await account();await page.getByText('目前房間：two',{exact:true}).waitFor();await page.keyboard.press('Escape')
 pass('account follows the activated slice-2 room')
 await page.route('**/doc?**',route=>route.fulfill({status:503,contentType:'application/json',body:'{}'}))
 await logout();await click(page.getByRole('button',{name:'確認登出'}));await page.getByText('目前修改未確認同步；登出已停止，請保留目前工作並重試。',{exact:true}).waitFor()
 assert.equal(posts,0);assert.equal(await page.evaluate(()=>window.editor.getInstanceState().isReadonly),false)
 await click(page.getByRole('button',{name:'取消',exact:true}));await returnedFocus();await page.unroute('**/doc?**')
 pass('failed sync confirmation blocks logout, preserves the editor and restores editing')
 let holdOtherWrites=false
 const other=await context.newPage()
 await other.routeWebSocket('**/connect/**',ws=>{const server=ws.connectToServer();ws.onMessage(message=>{if(!holdOtherWrites)server.send(message)});server.onMessage(message=>ws.send(message));ws.onClose(()=>server.close());server.onClose(()=>ws.close())})
 await other.goto(f.origin+'/?room=two');await other.waitForFunction(()=>!!window.editor);await other.waitForTimeout(700);await other.waitForFunction(()=>!!window.editor)
 await other.evaluate(()=>{window.editor.createShape({id:'shape:other-work',type:'geo',x:20,y:20,props:{w:80,h:80}})});await page.waitForFunction(()=>!!window.editor.getShape('shape:other-work'))
 holdOtherWrites=true;await other.evaluate(()=>{window.editor.createShape({id:'shape:unsynced-other',type:'geo',x:120,y:20,props:{w:80,h:80}})})
 assert.equal(await page.evaluate(()=>!!window.editor.getShape('shape:unsynced-other')),false)
 await logout();await click(page.getByRole('button',{name:'確認登出'}));await page.getByText('應用程式登入已結束。',{exact:true}).waitFor()
 assert.equal(posts,1);assert.equal(read('browser-session:'+sessionDigest).revoked,true)
 assert.equal(await page.evaluate(()=>!!window.editor),false);assert.equal(await page.locator('.tl-container').count(),0);assert.equal(await page.evaluate(()=>typeof window.serializeTldrawJson),'undefined')
 await other.waitForFunction(()=>window.editor?.getInstanceState().isReadonly===true)
 assert.ok(await other.evaluate(()=>window.editor.getShape('shape:other-work')))
 assert.ok(await other.evaluate(()=>window.editor.getShape('shape:unsynced-other')))
 assert.equal((await f.api('/doc?room=two').then(r=>r.json())).snapshot.documents.some(r=>r.state.id==='shape:unsynced-other'),false)
 await other.close()
 await page.reload();await page.getByRole('heading',{name:'目前已停止存取'}).waitFor();assert.equal(await page.evaluate(()=>!!window.editor),false)
 pass('real logout writes once, revokes only the session, unmounts initiating canvas and pauses other-tab retained work; reload stays closed')
 await login();assert.equal(new URL(page.url()).searchParams.get('room'),'two')
 await page.route('**/auth/logout?**',route=>route.fulfill({status:503,contentType:'application/json',body:'{}'}))
 await logout();await click(page.getByRole('button',{name:'確認登出'}));await page.getByRole('heading',{name:'登出結果未確認'}).waitFor()
 assert.equal(await page.evaluate(()=>!!window.editor),false)
 await page.reload();await page.getByRole('heading',{name:'登出結果未確認'}).waitFor();assert.equal(posts,2)
 await page.unroute('**/auth/logout?**');await click(page.getByRole('button',{name:'重新驗證入口'}));await page.waitForFunction(()=>!!window.editor)
 pass('unknown logout stays unknown across reload without replay; explicit re-entry alone reopens')
 await logout();await click(page.getByRole('button',{name:'確認登出'}));await page.getByText('應用程式登入已結束。',{exact:true}).waitFor()
 let release,seen
 const started=new Promise(resolve=>{seen=resolve})
 await page.route('**/auth/local/start',async route=>{const response=await route.fetch();seen();await new Promise(resolve=>{release=resolve});await route.fulfill({response}).catch(()=>{})})
 await click(page.getByRole('button',{name:'開始本機帳號驗證',exact:true}));await started
 await click(page.getByRole('button',{name:'取消登入'}));release();await page.waitForTimeout(100)
 assert.equal(await page.locator('.human-entry code').count(),0);assert.equal(await page.evaluate(()=>!!window.editor),false)
 await page.unroute('**/auth/local/start');await page.reload();await page.getByRole('heading',{name:'登入已取消'}).waitFor();await login()
 pass('cancelled local-login reply cannot reopen or publish a challenge after cancellation/reload; fresh login works')
 await page.route('**/auth/config',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({enabled:true,mode:'local',localReady:true,nativeAccount:false})}))
 await page.evaluate(()=>sessionStorage.setItem('journey-native-session-hold','confirmed'));await page.reload();await page.waitForFunction(()=>!!window.editor)
 await click(page.getByTestId('main-menu.button'));assert.equal(await page.getByRole('menuitem',{name:'我的帳號',exact:true}).count(),0);await page.keyboard.press('Escape')
 pass('turning off the account flag restores slice-2 entry even with a retained logout hold')
 assert.deepEqual(errors,[])
 await writeFile(join(f.scratch,'report.json'),JSON.stringify(report,null,2));console.log('evidence='+join(f.scratch,'report.json'))
}catch(error){console.error(error);if(page){await page.screenshot({path:join(f.scratch,'failure.png')});await writeFile(join(f.scratch,'failure.txt'),await page.locator('body').innerText())}console.log('failure evidence='+f.scratch);throw error}finally{db?.close();await browser?.close();await f.close()}
