import assert from 'node:assert/strict'
import { spawn, execFileSync } from 'node:child_process'
import { once } from 'node:events'
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
const evidence = dirname(fileURLToPath(import.meta.url))
const root = resolve(process.argv[2])
const pkg = join(evidence, '.scratch/baseline')
const data = join(evidence, '.scratch/data')
mkdirSync(data, { recursive: true })
const checked = ['server/canvas-server.ts','server/rooms.ts','server/assets.ts','lib/records.mjs','lib/render.mjs','lib/read.mjs','package-lock.json']
for (const file of checked) assert.equal(readFileSync(join(pkg,file)).toString(),readFileSync(join(root,'kc-journey-map',file)).toString(),file)
const hash = file => createHash('sha256').update(readFileSync(file)).digest('hex')
const results = []
const pass = (claim, actual) => { results.push({claim, actual}); console.log('PASS: '+claim+' — '+JSON.stringify(actual)) }
let child
async function stop() { if (child && child.exitCode === null) { child.kill('SIGTERM'); await once(child,'exit') } child = undefined }
async function start() {
 child=spawn(process.execPath,['--import','tsx','server/canvas-server.ts'],{cwd:pkg,env:{PATH:process.env.PATH,JOURNEY_API_PORT:'0',JOURNEY_ROOMS_DIR:join(data,'rooms'),JOURNEY_ASSETS_DIR:join(data,'assets'),JOURNEY_SAVE_DIR:join(data,'save')},stdio:['ignore','pipe','pipe']})
 let output=''
 child.stderr.on('data', b=>{ output+=b.toString() })
 return await new Promise((ok,no)=>{
  const timer=setTimeout(()=>no(new Error('start timeout '+output)),10000)
  child.stdout.on('data',b=>{output+=b.toString(); const m=output.match(/doc API on (http:\/\/127\.0\.0\.1:\d+)/); if(m){clearTimeout(timer);ok(m[1])}})
  child.once('exit',code=>{clearTimeout(timer);no(new Error('server exited '+code+' '+output))})
 })
}
let api
const request=async(path,method='GET',body)=>{ const r=await fetch(api+path,{method,headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined,signal:AbortSignal.timeout(5000)});return {status:r.status,body:await r.json()} }
try {
 api=await start()
 const id='synthetic-'+Date.now()
 const url='/doc?room='+id
 const before=await request('/health'); assert(!before.body.rooms.includes(id))
 const first=await request(url); assert.equal(first.status,200)
 const health=await request('/health');assert(health.body.rooms.includes(id));pass('GET creates room before immediate health read',{status:first.status,roomListed:true,healthFields:Object.keys(health.body)})
 const {note,pageLink}=await import(pathToFileURL(join(pkg,'lib/records.mjs')))
 const pages=first.body.snapshot.documents.map(d=>d.state).filter(r=>r.typeName==='page')
 const rec=note({id:'shape:synthetic',text:'Synthetic only',x:0,y:0,parentId:pages[0].id})
 let r=await request(url,'PATCH',{put:[rec],remove:[]}); assert.equal(r.status,200)
 const stale=structuredClone(rec)
 const a=await request(url,'PATCH',{put:[{...stale,x:456}],remove:[],expectedVersion:-99})
 const b=await request(url,'PATCH',{put:[{...stale,y:789}],remove:[],expectedVersion:-99})
 const read=await request(url);const current=read.body.snapshot.documents.find(d=>d.state.id===rec.id).state
 assert.deepEqual([a.status,b.status,current.x,current.y],[200,200,0,789]);pass('Stale complete-record PATCHes both succeed and last record wins',{statuses:[a.status,b.status],x:current.x,y:current.y})
 const saved=read.body.snapshot
 r=await request(url,'PATCH',{put:[{id:'shape:invalid',typeName:'missing'}],remove:[rec.id]});assert.equal(r.status,400)
 assert((await request(url)).body.snapshot.documents.some(d=>d.state.id===rec.id));pass('Invalid PATCH rejects before remove',{status:r.status,originalPresent:true})
 await request(url,'PATCH',{remove:[rec.id]})
 r=await request(url,'PUT',{snapshot:saved});assert.equal(r.status,200)
 assert((await request(url)).body.snapshot.documents.some(d=>d.state.id===rec.id));pass('PUT replaces snapshot without expected version',{status:r.status})
 const asset='synthetic-asset-'+id
 for (const body of ['room A synthetic bytes','room B synthetic bytes']) assert.equal((await fetch(api+'/uploads/'+asset,{method:'PUT',headers:{'Content-Type':'application/octet-stream'},body})).status,200)
 const assetRead=await fetch(api+'/uploads/'+asset)
 assert.equal(await assetRead.text(),'room B synthetic bytes');pass('Global asset ID overwrites across intended rooms; ownership is absent',{sameIdOverwrite:true,contentType:assetRead.headers.get('content-type')})
 const defaultLink=pageLink(id,'page:synthetic')
 assert.equal(defaultLink,'http://localhost:3737/?room='+id+'&d=v0.0.1.1.synthetic');pass('Default page link remains localhost 3737',defaultLink)
 const yaml=join(data,'journey.yaml')
 writeFileSync(yaml,'journey: synthetic-library\ntitle: Synthetic library\nsteps:\n  - id: reserve\n    card: Reserve a book\n    activity: Reserve\n    stories:\n      - id: reserve-copy\n        card: Reserve one copy\n        status: unverified\n')
 const env={PATH:process.env.PATH,JOURNEY_API:api}
 const rendered=execFileSync(process.execPath,['lib/journey-render.mjs',yaml,id],{cwd:pkg,env,encoding:'utf8'})
 const cliRead=execFileSync(process.execPath,['lib/journey-read.mjs',yaml,id],{cwd:pkg,env,encoding:'utf8'})
 assert.match(rendered,/^200 /);assert.doesNotThrow(()=>JSON.parse(cliRead));pass('Existing render and read CLI operate on a fictional journey',{render:rendered.trim(),readKeys:Object.keys(JSON.parse(cliRead))})
 const snapshot=(await request(url)).body.snapshot
 await stop();api=await start()
 assert((await request('/health')).body.rooms.includes(id))
 assert.deepEqual((await request(url)).body.snapshot.documents,snapshot.documents);pass('Node restart preserves stored records and room inventory',{records:snapshot.documents.length})
 const wrapper=await import(pathToFileURL(join(pkg,'node_modules/@tldraw/sync-core/dist-esm/index.mjs')))
 assert.equal(typeof wrapper.DurableObjectSqliteSyncWrapper,'function')
 assert.equal(typeof wrapper.TLSocketRoom.prototype.handleSocketResume,'function')
 pass('Pinned 5.4.0 exports Durable Object SQLite and resume APIs',{storageWrapper:true,sessionResume:true,cloudflareExecuted:false})
 writeFileSync(join(evidence,'baseline-result.json'),JSON.stringify({sourceHead:execFileSync('git',['-C',root,'rev-parse','HEAD'],{encoding:'utf8'}).trim(),node:process.version,at:new Date().toISOString(),fileHashes:Object.fromEntries(checked.map(f=>[f,hash(join(pkg,f))])),results},null,2)+'\n')
} finally { await stop() }
