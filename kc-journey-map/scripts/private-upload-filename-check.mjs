import assert from 'node:assert/strict'
import { spawn, execFileSync } from 'node:child_process'
import { createServer } from 'node:net'
import { randomBytes, createHash } from 'node:crypto'
import { mkdtemp, mkdir, writeFile, readFile, rm } from 'node:fs/promises'
import { join } from 'node:path'
import { createServer as viteServer } from 'vite'
import { chromium } from 'playwright'
import { assetUploadId } from '../server/client/asset-upload-id.ts'

const root = new URL('..', import.meta.url).pathname.replace(/\/$/, '')
const output = process.env.JOURNEY_CHECK_OUTPUT_DIR || join(root,'.host-check')
await mkdir(output,{recursive:true})
const scratch = await mkdtemp(join(output,'upload-filename-'))
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6D1AAAAAASUVORK5CYII=','base64')
const names=['plain.png','space name.png','畫布圖片.png','photo (1).png','repeat.png','repeat.png']
const secret=randomBytes(32).toString('base64url'), token='probe.'+secret
const grants=[{credentialId:'probe',principalId:'probe',secretDigest:createHash('sha256').update(secret).digest('hex'),rooms:['A'],expiresAt:Date.now()+3600000,revoked:false}]
const grantFile=join(scratch,'grants.json')
await writeFile(grantFile,JSON.stringify(grants),{mode:0o600})
const envKeys=['JOURNEY_PRIVATE_DIR','JOURNEY_GRANTS_FILE','JOURNEY_ORIGIN','JOURNEY_ROOMS_DIR','JOURNEY_ASSETS_DIR']
const saved=Object.fromEntries(envKeys.map(k=>[k,process.env[k]]))
Object.assign(process.env,{JOURNEY_PRIVATE_DIR:join(scratch,'private'),JOURNEY_GRANTS_FILE:grantFile,JOURNEY_ORIGIN:'https://upload.example.invalid',JOURNEY_ASSETS_DIR:join(scratch,'legacy-assets')})
const {NodeHost}=await import('../server/host/node.ts'), {handle}=await import('../server/host/transport.ts')
const report={producer:[],negative:[],browser:'NOT RUN',hosted:'NOT RUN',external:[]}
let privateHost,legacyHost,child,vite,browser,childLog=''
const freePort=()=>new Promise(resolve=>{const s=createServer();s.listen(0,'127.0.0.1',()=>{const p=s.address().port;s.close(()=>resolve(p))})})
const until=async fn=>{for(let i=0;i<100;i++){if(await fn())return;await new Promise(r=>setTimeout(r,50))}throw new Error('bounded condition timeout')}
try {
 privateHost=new NodeHost();await privateHost.meta.put('room:A',{createdAt:1})
 delete process.env.JOURNEY_PRIVATE_DIR
 process.env.JOURNEY_ROOMS_DIR=join(scratch,'legacy-rooms')
 legacyHost=new NodeHost()
 const ids=[]
 const cryptoDescriptor=Object.getOwnPropertyDescriptor(globalThis,'crypto')
 try {
  Object.defineProperty(globalThis,'crypto',{value:undefined,configurable:true})
  for(const name of names) ids.push(assetUploadId(name))
 } finally {Object.defineProperty(globalThis,'crypto',cryptoDescriptor)}
 assert.equal(new Set(ids).size,ids.length,'time/random prefix must distinguish repeated names without crypto.randomUUID')
 for(const [i,name] of names.entries()) {
  const id=ids[i], file=new File([png],name,{type:'image/png'})
  const row={name,id,canonical:/^[a-zA-Z0-9._-]+$/.test(id)}
  for(const [label,host] of [['private',privateHost],['legacy',legacyHost]]) {
   const url='https://upload.example.invalid/uploads/'+encodeURIComponent(id)+'?room=A'
   const headers={authorization:'Bearer '+token}
   const put=await handle(host,new Request(url,{method:'PUT',headers,body:file}))
   row[label]=put.status
   if(put.ok){
    const get=await handle(host,new Request(url,{headers}))
    assert.equal(get.status,200);assert.equal(get.headers.get('content-type'),'image/png')
    assert.deepEqual(Buffer.from(await get.arrayBuffer()),png)
   }
  }
  assert.equal(file.name,name);assert.equal(file.type,'image/png');assert.deepEqual(Buffer.from(await file.arrayBuffer()),png)
  report.producer.push(row)
 }
 for(const [path,method,body,status] of [
  ['/uploads/noncanonical%20name.png?room=A','PUT',png,403],
  ['/uploads/..%2Foutside.png?room=A','PUT',png,403],
  ['/uploads/valid.png?room=B','PUT',png,403],
  ['/doc?room=A','PATCH','{bad json',400],
 ]) {
  const response=await handle(privateHost,new Request('https://upload.example.invalid'+path,{method,headers:{authorization:'Bearer '+token},body}))
  assert.equal(response.status,status);report.negative.push({path,status:response.status})
 }
 const oldUrl='https://upload.example.invalid/uploads/existing%20legacy%20(1).png?room=A'
 assert.equal((await handle(legacyHost,new Request(oldUrl,{method:'PUT',body:new File([png],'old.png',{type:'image/png'})}))).status,200)
 const old=await handle(legacyHost,new Request(oldUrl));assert.equal(old.status,200);assert.deepEqual(Buffer.from(await old.arrayBuffer()),png)
 report.legacyExistingReference='PASS'
 assert(report.producer.every(r=>r.canonical&&r.private===200&&r.legacy===200),'actual client ID producer rejects ordinary private filenames: '+JSON.stringify(report.producer))
 if(!process.argv.includes('--producer-only')){
  const assetDir=process.env.JOURNEY_TLDRAW_ASSETS
  assert(assetDir,'JOURNEY_TLDRAW_ASSETS must name an existing local @tldraw/assets package; no downloads')
  const port=await freePort(), browserPort=await freePort(), api='http://127.0.0.1:'+port, origin='https://localhost:'+browserPort
  child=spawn(process.execPath,['--import','tsx',join(root,'server/canvas-server.ts')],{cwd:root,env:{...process.env,JOURNEY_PRIVATE_DIR:join(scratch,'browser-store'),JOURNEY_GRANTS_FILE:grantFile,JOURNEY_ORIGIN:origin,JOURNEY_API_PORT:String(port)},stdio:['ignore','pipe','pipe']})
  child.stdout.on('data',b=>{childLog+=b});child.stderr.on('data',b=>{childLog+=b})
  const request=path=>fetch(api+path,{headers:{authorization:'Bearer '+token}})
  await until(async()=>{try{return(await request('/health')).ok}catch{return false}})
  assert.equal((await request('/doc?room=A')).status,200)
  const key=join(scratch,'key.pem'),cert=join(scratch,'cert.pem')
  execFileSync('openssl',['req','-x509','-newkey','rsa:2048','-nodes','-keyout',key,'-out',cert,'-days','1','-subj','/CN=localhost'],{stdio:'pipe'})
  vite=await viteServer({configFile:join(root,'vite.config.mts'),optimizeDeps:{include:['@tldraw/mermaid']},define:{'import.meta.env.VITE_JOURNEY_API_URL':JSON.stringify('')},
   server:{host:'127.0.0.1',port:browserPort,strictPort:true,https:{key:await readFile(key),cert:await readFile(cert)},proxy:Object.fromEntries(['/connect','/uploads/','/session','^/doc($|[?])','/health','/capabilities','/save','/repo-doc','/mcp'].map(route=>[route,{target:api,ws:route==='/connect'}]))}})
  await vite.listen()
  browser=await chromium.launch({headless:true})
  const context=await browser.newContext({ignoreHTTPSErrors:true,viewport:{width:1100,height:800}})
  await context.route('**/*',async route=>{
   const url=new URL(route.request().url())
   if(url.origin===origin)return route.continue()
   if(url.hostname==='cdn.tldraw.com'){
    const path=url.pathname.replace(/^\/[^/]+\//,'')
    if(!path.includes('..'))return route.fulfill({path:join(assetDir,path)})
   }
   report.external.push(url.origin+url.pathname);return route.abort()
  })
  const session=await context.request.post(origin+'/session',{headers:{Authorization:'Bearer '+token,Origin:origin}})
  assert.equal(session.status(),200)
  const page=await context.newPage()
  page.setDefaultTimeout(15000)
  await page.goto(origin+'/?room=A')
  await page.waitForFunction(()=>window.editor&&document.querySelector('[data-testid="room-trigger"]')?.title.endsWith('Connected'))
  const name='畫布 image (1).png'
  const chooser=page.waitForEvent('filechooser'), uploaded=page.waitForResponse(r=>r.request().method()==='PUT'&&new URL(r.url()).pathname.startsWith('/uploads/'))
  await page.mouse.click(550,400);await page.keyboard.press('ControlOrMeta+u')
  await(await chooser).setFiles({name,mimeType:'image/png',buffer:png})
  const response=await uploaded;assert.equal(response.status(),200)
  const id=decodeURIComponent(new URL(response.url()).pathname.slice('/uploads/'.length))
  assert.match(id,/^[a-zA-Z0-9._-]+$/)
  await page.waitForFunction(name=>window.editor.getAssets().some(a=>a.props.name===name&&a.props.src?.startsWith('asset:')),name)
  const asset=await page.evaluate(name=>window.editor.getAssets().find(a=>a.props.name===name),name)
  assert.equal(asset.props.src,'asset:'+id);assert.equal(asset.props.name,name);assert.equal(asset.props.mimeType,'image/png')
  const readback=await request('/uploads/'+encodeURIComponent(id)+'?room=A')
  assert.equal(readback.status,200);assert.equal(readback.headers.get('content-type'),'image/png');assert.deepEqual(Buffer.from(await readback.arrayBuffer()),png)
  await until(async()=>JSON.stringify(await(await request('/doc?room=A')).json()).includes(asset.props.src))
  await page.screenshot({path:join(output,'browser-upload.png')})
  report.browser={result:'PASS',gesture:'native Upload media file chooser via keyboard',name,id,src:asset.props.src,type:asset.props.mimeType,putStatus:response.status(),readStatus:readback.status,bytesExact:true,documentReadback:true,context:'disposable Chromium; local SDK assets; unchanged development mode'}
  await context.close()
 }
 report.result='PASS'
} catch(error){report.result='FAIL';report.error=error.message;process.exitCode=1}
finally {
 await browser?.close();await vite?.close()
 if(child&&child.exitCode===null){
  await new Promise(resolve=>{const timer=setTimeout(()=>child.kill('SIGKILL'),5000);child.once('exit',()=>{clearTimeout(timer);resolve()});child.kill('SIGTERM')})
 }
 privateHost?.close();legacyHost?.close()
 for(const [k,v] of Object.entries(saved))if(v===undefined)delete process.env[k];else process.env[k]=v
 await writeFile(join(output,'server.log'),childLog)
 await rm(scratch,{recursive:true,force:true})
 report.cleanup='owned servers, context, stores and synthetic credentials removed'
}
console.log(JSON.stringify(report,null,2))
