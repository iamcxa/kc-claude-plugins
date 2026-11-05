import assert from 'node:assert/strict'
import { writeFile } from 'node:fs/promises'
import { execFileSync } from 'node:child_process'
import { join } from 'node:path'
import { chromium } from 'playwright'
import { startFixture } from './native-account-fixture.mjs'
const report={candidate:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),checks:[],screenshots:[],limits:['Local Node fixture and browser emulation; no provider or physical device proof']}
const pass=name=>{report.checks.push(name);console.log('PASS '+name)}
const click=async locator=>{await locator.scrollIntoViewIfNeeded();assert.ok(await locator.evaluate(el=>{const r=el.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return hit===el||el.contains(hit)}));await locator.click()}
let browser
try {
 browser=await chromium.launch({headless:true})
 for(const nativeAccount of [true,false]){
  const f=await startFixture({nativeAccount,agentPairing:true}),context=await browser.newContext({viewport:{width:1280,height:800}}),page=await context.newPage(),errors=[]
  page.on('pageerror',error=>errors.push(error.message))
  try {
   await page.goto(f.origin+'/?room=one')
   await click(page.getByRole('button',{name:'開始本機帳號驗證',exact:true}))
   assert.match(f.approve(await page.locator('.human-entry code').innerText()),/"approved": true/)
   await click(page.getByRole('button',{name:'我已在本機核准',exact:true}));await page.waitForFunction(()=>!!window.editor)
   const open=async()=>{
    if(nativeAccount){
     assert.equal(await page.locator('.agent-account,.human-entry-identity').count(),0)
     assert.equal(await page.getByRole('button',{name:'帳號與代理',exact:true}).count(),0)
     assert.ok(await page.evaluate(()=>window.editor.getViewportScreenBounds().y<56))
     await click(page.getByTestId('main-menu.button'))
     await click(page.getByRole('menuitem',{name:'我的帳號',exact:true}))
     await page.getByText('目前權限已確認',{exact:true}).waitFor()
     await click(page.getByRole('button',{name:'我的 agent',exact:true}))
     await page.getByRole('heading',{name:'我的 agent',exact:true}).waitFor()
     assert.equal(await page.getByRole('heading',{name:'我的帳號',exact:true}).count(),0)
    } else {
     await page.locator('.agent-account').waitFor()
     assert.ok(await page.evaluate(()=>window.editor.getViewportScreenBounds().y>=56))
     await click(page.getByRole('button',{name:'帳號與代理',exact:true}))
     await page.getByRole('heading',{name:'帳號與代理',exact:true}).waitFor()
    }
    await page.getByText('目前沒有代理安裝。',{exact:true}).waitFor()
   }
   const returnedFocus=()=>page.waitForFunction(native=>document.activeElement===document.querySelector(native?'[data-testid="main-menu.button"]':'.agent-account button'),nativeAccount,{timeout:3000})
   for(const width of [1280,390])for(const theme of ['light','dark']){
    await page.setViewportSize({width,height:844});await page.evaluate(theme=>window.editor.user.updateUserPreferences({colorScheme:theme}),theme)
    await open()
    assert.equal(await page.getByRole('dialog').count(),1)
    assert.equal(await page.getByRole('dialog').evaluate(el=>el.scrollWidth<=el.clientWidth),true)
    const code=page.getByLabel('配對碼');await code.fill('RETAINED')
    await click(page.getByRole('button',{name:'更新代理清單',exact:true}));await page.getByText('目前沒有代理安裝。',{exact:true}).waitFor()
    assert.equal(await code.inputValue(),'RETAINED')
    const path=join(f.scratch,`agents-${nativeAccount?'native':'outer'}-${width}-${theme}.png`);await page.screenshot({path});report.screenshots.push(path)
    await page.keyboard.press('Escape');await returnedFocus()
   }
   pass((nativeAccount?'both flags: no outer identity/account bar; 我的帳號 → 我的 agent opens native pairing':'native account off: outer 帳號與代理 still opens pairing')+'; desktop/390 light/dark retained input, refresh, no overflow, Escape focus return')
   // Start a genuine synthetic installation request, inspect and approve it through the rendered sheet.
   const requestId=crypto.randomUUID(),verifier='b'.repeat(64)
   const response=await fetch('http://127.0.0.1:'+f.apiPort+'/agents/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({backendId:'synthetic-native',requestId,installationId:crypto.randomUUID(),memberId:'owner',label:'Synthetic native integration',rooms:['one'],verifier})})
   assert.equal(response.status,200);const request=await response.json()
   await open();await page.getByLabel('配對碼').fill(request.code)
   await click(page.getByRole('button',{name:'檢視配對請求',exact:true}));await page.getByText('Synthetic native integration',{exact:true}).waitFor()
   await page.getByText('完整紀錄新增、修改、刪除與整份文件取代',{exact:true}).waitFor()
   const approve=page.getByRole('button',{name:'核准這些畫布與能力',exact:true});assert.ok((await approve.boundingBox()).height>=44);await click(approve)
   await page.getByText('已核准，等待原安裝兌換；尚未簽發安裝憑證。',{exact:true}).waitFor()
   const poll=await fetch('http://127.0.0.1:'+f.apiPort+'/agents/poll',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({backendId:'synthetic-native',requestId,verifier})})
   assert.equal(poll.status,200);assert.equal((await poll.json()).status,'approved')
   await page.keyboard.press('Escape');await returnedFocus()
   assert.deepEqual(errors,[])
   pass((nativeAccount?'native':'outer')+' sheet inspects and approves exact real synthetic consent through hit-tested controls; no browser runtime errors')
  } catch(error){await page.screenshot({path:join(f.scratch,'failure.png')});await writeFile(join(f.scratch,'failure.txt'),await page.locator('body').innerText());console.error('failure evidence='+f.scratch);throw error}
  finally {await context.close();await f.close();await writeFile(join(f.scratch,'native-agent-report.json'),JSON.stringify(report,null,2));console.log('evidence='+join(f.scratch,'native-agent-report.json'))}
 }
} finally {await browser?.close()}
