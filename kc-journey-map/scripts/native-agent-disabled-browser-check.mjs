import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { writeFile } from 'node:fs/promises'
import { join } from 'node:path'
import { chromium } from 'playwright'
import { startFixture } from './native-account-fixture.mjs'

const report={candidate:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),flags:{nativeAccount:true,agentPairing:false},checks:[],requests:[],dialogs:[]}
const f=await startFixture(report.flags)
let browser
try {
 browser=await chromium.launch({headless:true})
 const context=await browser.newContext({viewport:{width:1280,height:844}}),page=await context.newPage(),errors=[]
 page.on('pageerror',error=>errors.push(error.message))
 page.on('request',request=>{const url=new URL(request.url());if(/^\/(?:auth|agents)\//.test(url.pathname))report.requests.push({method:request.method(),path:url.pathname})})
 await page.goto(f.origin+'/?room=one')
 await page.getByRole('button',{name:'開始本機帳號驗證',exact:true}).click()
 assert.match(f.approve(await page.locator('.human-entry code').innerText()),/"approved": true/)
 await page.getByRole('button',{name:'我已在本機核准',exact:true}).click()
 await page.waitForFunction(()=>!!window.editor)
 for(const width of [1280,390])for(const theme of ['light','dark']){
  await page.setViewportSize({width,height:844})
  await page.evaluate(theme=>window.editor.user.updateUserPreferences({colorScheme:theme}),theme)
  await page.getByTestId('main-menu.button').click()
  await page.getByRole('menuitem',{name:'我的帳號',exact:true}).click()
  await page.getByText('目前權限已確認',{exact:true}).waitFor()
  const dialog=page.getByRole('dialog'),entry=page.getByRole('button',{name:'我的 agent',exact:true}),count=await entry.count()
  report.dialogs.push({width,theme,text:await dialog.innerText(),html:await dialog.innerHTML(),bounds:await dialog.boundingBox(),buttons:await dialog.getByRole('button').allTextContents(),agentEntryCount:count})
  await page.screenshot({path:join(f.scratch,`pairing-off-${width}-${theme}.png`)})
  if(count){
   await entry.click()
   await page.getByText('代理配對目前未啟用。',{exact:true}).waitFor()
  }
  assert.equal(count,0,'pairing disabled must preserve the account-base dialog: no 我的 agent entry')
  assert.deepEqual(report.requests.filter(request=>request.path.startsWith('/agents/')),[],'pairing disabled must send no /agents/* requests')
  assert.equal(await page.locator('.agent-account,.human-entry-identity').count(),0)
  assert.equal(await page.getByRole('button',{name:'帳號與代理',exact:true}).count(),0)
  await page.keyboard.press('Escape')
  await page.waitForFunction(()=>document.activeElement===document.querySelector('[data-testid="main-menu.button"]'))
  report.checks.push(`native account on / pairing off: ${width}px ${theme}; no agent entry or request; Escape returns focus`)
  console.log('PASS '+report.checks.at(-1))
 }
 assert.deepEqual(report.requests.filter(request=>request.path.startsWith('/agents/')),[])
 assert.deepEqual(errors,[])
} finally {
 await browser?.close();await f.close()
 const path=process.env.JOURNEY_DISABLED_EVIDENCE||join(f.scratch,'native-agent-disabled-report.json')
 await writeFile(path,JSON.stringify({...report,scratch:f.scratch},null,2)+'\n')
 console.log('evidence='+path)
}
