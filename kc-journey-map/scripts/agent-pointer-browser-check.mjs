import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { writeFile } from 'node:fs/promises'
import { join } from 'node:path'
import { DatabaseSync } from 'node:sqlite'
import { chromium } from 'playwright'
import { startFixture } from './native-account-fixture.mjs'
const report={candidate:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),cases:[]}
let browser
try {
 browser=await chromium.launch({headless:true})
 for(const nativeAccount of [false,true])for(const width of [1280,390])for(const theme of ['light','dark']){
  const f=await startFixture({nativeAccount,agentPairing:true}),context=await browser.newContext({viewport:{width,height:844}}),page=await context.newPage()
  page.setDefaultTimeout(20000)
  const click={x:width===390?195:600,y:400}
  let before,shape
  try {
   await page.goto(f.origin+'/?room=one')
   await page.getByRole('button',{name:'開始本機帳號驗證',exact:true}).click()
   f.approve(await page.locator('.human-entry code').innerText())
   await page.getByRole('button',{name:'我已在本機核准',exact:true}).click()
   await page.waitForFunction(()=>!!window.editor)
   before=await page.evaluate(theme=>{const e=window.editor;e.user.updateUserPreferences({colorScheme:theme});e.setCurrentTool('geo');e.setCamera({x:0,y:0,z:1});return {cached:e.getViewportScreenBounds().y,dom:document.querySelector('.tl-canvas').getBoundingClientRect().y,camera:e.getCamera()}},theme)
   await page.mouse.click(click.x,click.y)
   await page.waitForFunction(()=>window.editor.getCurrentPageShapes().some(s=>s.type==='geo'))
   await page.waitForTimeout(500)
   shape=await page.evaluate(()=>{const e=window.editor,s=e.getCurrentPageShapes().find(s=>s.type==='geo'),bounds=e.getShapePageBounds(s);return {id:s.id,center:e.pageToScreen(bounds.center),pageCenter:{x:bounds.center.x,y:bounds.center.y},expectedDomY:document.querySelector('.tl-canvas').getBoundingClientRect().y}})
   assert.deepEqual({x:shape.center.x,y:shape.center.y},click,'settled screen center must equal the real click')
   assert.equal(before.dom,0);assert.equal(before.cached,0)
   let acknowledged=false
   for(let n=0;n<100;n++){
    const response=await f.api('/doc?room=one');assert.equal(response.status,200)
    if((await response.json()).snapshot.documents.some(document=>document.state.id===shape.id)){acknowledged=true;break}
    await new Promise(resolve=>setTimeout(resolve,50))
   }
   assert.ok(acknowledged,'server document must contain the real pointer shape')
  } finally {await context.close();await f.close();await writeFile(join(f.scratch,'pointer-server.log'),f.logs.join(''))}
  const db=new DatabaseSync(join(f.dataDir,'rooms','one.db'),{readOnly:true})
  try {
   const saved=db.prepare('SELECT state FROM documents').all().map(row=>JSON.parse(typeof row.state==='string'?row.state:new TextDecoder().decode(row.state)))
   const persisted=saved.find(s=>s.id===shape.id)
   assert.ok(persisted,'real pointer shape must survive server shutdown in SQLite')
   const expected={x:click.x/before.camera.z-before.camera.x,y:(click.y-shape.expectedDomY)/before.camera.z-before.camera.y}
   const persistedCenter={x:persisted.x+persisted.props.w/2,y:persisted.y+persisted.props.h/2}
   assert.deepEqual(persistedCenter,expected,'SQLite page coordinates must match the DOM-based click')
   report.cases.push({nativeAccount,width,theme,click,before,expected,persistedCenter,shape,scratch:f.scratch})
   console.log(`PASS real pointer persisted: account ${nativeAccount}, ${width}px ${theme}`)
  } finally {db.close()}
 }
} finally {
 await browser?.close()
 const path=process.env.JOURNEY_POINTER_EVIDENCE||'/tmp/agent-pointer-report.json'
 await writeFile(path,JSON.stringify(report,null,2)+'\n');console.log('evidence='+path)
}
