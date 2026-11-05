import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { writeFile } from 'node:fs/promises'
import { join } from 'node:path'
import { chromium } from 'playwright'
import { startFixture } from './native-account-fixture.mjs'
const report={candidate:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),checks:[],layouts:[]}
let browser
try {
 browser=await chromium.launch({headless:true})
 for(const agentPairing of [false,true]){
  const f=await startFixture({nativeAccount:false,agentPairing})
  try {
   for(const width of [1280,390])for(const theme of ['light','dark']){
    const context=await browser.newContext({viewport:{width,height:844}}),page=await context.newPage(),requests=[],errors=[]
    page.on('pageerror',error=>errors.push(error.message))
    page.on('request',request=>{const url=new URL(request.url());if(url.pathname.startsWith('/agents/'))requests.push(url.pathname)})
    try {
     await page.goto(f.origin+'/?room=one')
     await page.getByRole('button',{name:'開始本機帳號驗證',exact:true}).click()
     f.approve(await page.locator('.human-entry code').innerText())
     await page.getByRole('button',{name:'我已在本機核准',exact:true}).click()
     await page.waitForFunction(()=>!!window.editor)
     await page.evaluate(theme=>window.editor.user.updateUserPreferences({colorScheme:theme}),theme)
     await page.getByTestId('main-menu.button').click()
     assert.equal(await page.getByRole('menuitem',{name:'我的帳號',exact:true}).count(),0)
     const menu=await page.getByRole('menu').innerText()
     await page.keyboard.press('Escape')
     await page.getByText('Synthetic owner · 身分已驗證',{exact:true}).waitFor()
     assert.equal(await page.locator('.agent-account').count(),0)
     assert.equal(await page.getByRole('button',{name:'帳號與代理',exact:true}).count(),0)
     assert.equal(await page.getByRole('button',{name:'我的 agent',exact:true}).count(),0)
     const layout=await page.evaluate(()=>{const rect=el=>{const {x,y,width,height}=el.getBoundingClientRect();return {x,y,width,height}};return {identity:document.querySelector('.human-entry-identity').outerHTML,canvas:rect(document.querySelector('.tl-canvas')),cached:window.editor.getViewportScreenBounds().y}})
     layout.menu=menu
     assert.equal(layout.canvas.y,0);assert.equal(layout.cached,0)
     assert.deepEqual(requests,[]);assert.deepEqual(errors,[])
     const off=report.layouts.find(row=>row.width===width&&row.theme===theme)
     if(off)assert.deepEqual(layout,off.layout,'pairing flag must not change account-off rendering')
     report.layouts.push({agentPairing,width,theme,layout,requests})
     await page.screenshot({path:join(f.scratch,`account-off-${agentPairing}-${width}-${theme}.png`)})
     const name=`account off / pairing ${agentPairing}: ${width}px ${theme}; no entry or request; unchanged zero-offset canvas`
     report.checks.push(name);console.log('PASS '+name)
    } finally {await context.close()}
   }
  } finally {await f.close()}
 }
} finally {
 await browser?.close()
 const path=process.env.JOURNEY_ACCOUNT_OFF_EVIDENCE||'/tmp/agent-account-off-report.json'
 await writeFile(path,JSON.stringify(report,null,2)+'\n');console.log('evidence='+path)
}
