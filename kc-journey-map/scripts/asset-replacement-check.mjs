import assert from 'node:assert/strict'
import { mkdtemp, mkdir, writeFile, readdir, rm } from 'node:fs/promises'
import { join } from 'node:path'
import fs from 'node:fs/promises'
import { syncBuiltinESMExports } from 'node:module'
import { build } from 'esbuild'
import { Miniflare } from 'miniflare'
import { NodeHost } from '../server/host/node.ts'
import { CloudflareHost } from '../server/host/cloudflare.ts'
import { digest } from '../server/host/policy.ts'
import { handle } from '../server/host/transport.ts'

const root = new URL('..', import.meta.url).pathname
await mkdir(join(root, '.host-check'), { recursive: true })
const scratch = await mkdtemp(join(root, '.host-check/asset-replacement-'))
const origin = 'https://asset-check.example.invalid', secret = 's'.repeat(43)
const grants = [{ credentialId: 'probe', principalId: 'probe', secretDigest: await digest(secret), rooms: ['A', 'B'], expiresAt: Date.now() + 3600000, revoked: false }]
const grantFile = join(scratch, 'grants.json')
await writeFile(grantFile, JSON.stringify(grants), { mode: 0o600 })
const savedEnv = Object.fromEntries(['JOURNEY_PRIVATE_DIR', 'JOURNEY_GRANTS_FILE', 'JOURNEY_ORIGIN'].map(k => [k, process.env[k]]))
const bundle = await build({ stdin: { contents: `
import worker, {JourneyRegistry, JourneyRoom} from './server/host/cloudflare.ts'
export {JourneyRoom}
export class AssetRegistry extends JourneyRegistry {
 constructor(ctx, env) {super(ctx, env); this.testContext = ctx}
 async fetch(req) {
  if (new URL(req.url).pathname === '/test/sql') {
   const {sql, params = []} = await req.json()
   return Response.json(this.testContext.storage.sql.exec(sql, ...params).toArray())
  }
  return super.fetch(req)
 }
}
export default worker
`, resolveDir: root, sourcefile: 'asset-replacement-fixture.ts' }, bundle: true, write: false, format: 'esm', platform: 'browser',
 conditions: ['workerd', 'worker', 'browser'], external: ['cloudflare:workers'], logLevel: 'silent' })
const reports = []
const originalFs = {readFile:fs.readFile, writeFile:fs.writeFile, unlink:fs.unlink}
const deferred = () => {let resolve; const promise = new Promise((r,reject) => {
 const timer=setTimeout(()=>reject(new Error('synthetic barrier timed out')),10000); timer.unref()
 resolve=()=>{clearTimeout(timer);r()}
}); return {promise,resolve}}
const text = bytes => new TextDecoder().decode(bytes)
let mf, node
try {
 Object.assign(process.env, { JOURNEY_PRIVATE_DIR: join(scratch, 'node'), JOURNEY_GRANTS_FILE: grantFile, JOURNEY_ORIGIN: origin })
 node = new NodeHost()
 console.error('Node ready; starting local workerd/R2')
 mf = new Miniflare({ script: bundle.outputFiles[0].text, modules: true, compatibilityDate: '2026-07-01', compatibilityFlags: ['nodejs_compat'],
  host: '127.0.0.1', port: 0, bindings: { JOURNEY_ORIGIN: origin, JOURNEY_GRANTS: JSON.stringify(grants) },
  durableObjects: { REGISTRY: { className: 'AssetRegistry', useSQLite: true }, ROOMS: { className: 'JourneyRoom', useSQLite: true } },
  durableObjectsPersist: join(scratch, 'objects'), r2Buckets: ['ASSETS'], r2Persist: join(scratch, 'r2') })
 await mf.ready
 console.error('Local workerd ready')
 const registry = await mf.getDurableObjectNamespace('REGISTRY'), bucket = await mf.getR2Bucket('ASSETS')
 const nodeHooks = {}, cloudHooks = {}
 const registryBinding = {idFromName: name => registry.idFromName(name), get: id => ({fetch: async request => {
  const body = await request.text()
  const response = await registry.get(id).fetch(request.url, {method:request.method,headers:Object.fromEntries(request.headers),body})
  if(new URL(request.url).pathname === '/replace-asset' && response.ok) await cloudHooks.afterCommit?.()
  return response
 }})}
 const assets = {
  put: async (key, bytes, options) => {await cloudHooks.beforeUpload?.(key,bytes); const value=await bucket.put(key,bytes,options); await cloudHooks.afterUpload?.(key,bytes); return value},
  get: async key => {await cloudHooks.beforeRead?.(key); return bucket.get(key)},
  delete: async key => {await cloudHooks.beforeDelete?.(key); return bucket.delete(key)},
 }
 const cloud = new CloudflareHost({ REGISTRY: registryBinding, ASSETS: assets, JOURNEY_ORIGIN: origin, JOURNEY_GRANTS: JSON.stringify(grants) })
 const nodeAssets = join(scratch,'node','assets') + '/'
 fs.writeFile = async (path,bytes,...args) => {
  if(!String(path).startsWith(nodeAssets)) return originalFs.writeFile(path,bytes,...args)
  await nodeHooks.beforeUpload?.(String(path).slice(nodeAssets.length),bytes)
  const result=await originalFs.writeFile(path,bytes,...args)
  await nodeHooks.afterUpload?.(String(path).slice(nodeAssets.length),bytes); return result
 }
 fs.readFile = async (path,...args) => {if(String(path).startsWith(nodeAssets)) await nodeHooks.beforeRead?.(String(path).slice(nodeAssets.length)); return originalFs.readFile(path,...args)}
 fs.unlink = async path => {if(String(path).startsWith(nodeAssets)) await nodeHooks.beforeDelete?.(String(path).slice(nodeAssets.length)); return originalFs.unlink(path)}
 syncBuiltinESMExports()
 const nodeExec = node.db.exec.bind(node.db)
 node.db.exec = sql => {const value=nodeExec(sql); if(sql==='COMMIT') nodeHooks.afterCommit?.(); return value}
 const registryStub = registry.get(registry.idFromName('private-pilot'))
 const adapters = [
  {name: 'node', host: node, hooks:nodeHooks, request: r => handle(node, r), keys: () => readdir(join(scratch, 'node', 'assets')),
   sql: async sql => nodeExec(sql), remove: key => originalFs.unlink(join(nodeAssets,key))},
  {name: 'cloudflare-local', host: cloud, request: async r => mf.dispatchFetch(r.url, {method:r.method,headers:Object.fromEntries(r.headers),...(r.method==='PUT'?{body:await r.arrayBuffer()}:{})}),
   hooks:cloudHooks, keys: async () => (await bucket.list()).objects.map(o => o.key), remove:key => bucket.delete(key),
   sql: async sql => {const r=await registryStub.fetch('https://registry/test/sql',{method:'POST',body:JSON.stringify({sql})}); assert.equal(r.status,200); return r.json()}}
 ]
 for (const a of adapters) {
  console.error('Checking ' + a.name)
  try {
   await a.host.meta.put('room:A', {createdAt:1}); await a.host.meta.put('room:B', {createdAt:1})
   const request = (method, body) => a.request(new Request(origin + '/uploads/proof?room=A', {method,
    headers:{authorization:'Bearer probe.'+secret,'content-type':'text/plain'},...(body===undefined?{}:{body})}))
   assert.equal((await request('PUT', 'first')).status, 200)
   const old = await a.host.meta.get('asset:A:proof')
   assert.equal((await request('PUT', 'replacement')).status, 200)
   const current = await a.host.meta.get('asset:A:proof'), keys = await a.keys()
   const response = await request('GET')
   assert.equal(response.status, 200); assert.equal(await response.text(), 'replacement')
   assert.notEqual(old.blobKey, current.blobKey)
   assert.equal(keys.length, 1, a.name + ': successful replacement retains ' + keys.length + ' blobs')
   assert(!keys.includes(old.blobKey)); assert(keys.includes(current.blobKey))
   const checks = ['actual HTTP replacement leaves one blob and reads latest content']
   const put = (id, value, room='A') => a.host.putAsset(room,id,new TextEncoder().encode(value),'text/'+value)
   const mapping = (id,room='A') => a.host.meta.get('asset:'+room+':'+id)
   const read = async (id,room='A') => {const r=await a.host.getAsset(room,id); return {text:text(r.data),type:r.contentType}}
   const clear = () => {for(const k of Object.keys(a.hooks)) delete a.hooks[k]}
   await put('untouched','same'); await put('untouched','other','B')
   const preserved = [await mapping('untouched'),await mapping('untouched','B')]
   for(const existing of [false,true]) {
    const id='overlap-'+existing
    if(existing) await put(id,'old')
    const before=new Set(await a.keys()), release=deferred(), arrived=deferred(); let count=0
    a.hooks.afterUpload=async()=>{if(++count===2) arrived.resolve(); await release.promise}
    const first=put(id,'first'), second=put(id,'second')
    await arrived.promise; release.resolve(); await Promise.all([first,second]); clear()
    const live=await mapping(id), stored=await a.keys()
    assert.equal(stored.filter(k=>!before.has(k)).length,1); assert(stored.includes(live.blobKey))
    const value=await read(id); assert(['first','second'].includes(value.text)); assert.equal(value.type,'text/'+value.text)
    if(existing) assert.equal(stored.length,before.size)
   }
   checks.push('concurrent first uploads and overwrites reclaim losing versions')
   {
    const id='reverse', entered=deferred(), release=deferred(); await put(id,'old')
    const before=new Set(await a.keys())
    a.hooks.beforeUpload=async(_key,bytes)=>{if(text(bytes)==='slow'){entered.resolve();await release.promise}}
    const slow=put(id,'slow'); await entered.promise; await put(id,'fast'); release.resolve(); await slow; clear()
    assert.deepEqual(await read(id),{text:'slow',type:'text/slow'})
    assert.equal((await a.keys()).length,before.size)
   }
   {
    const id='late-cleanup'; await put(id,'old'); const old=await mapping(id), entered=deferred(), release=deferred()
    const before=(await a.keys()).length
    a.hooks.beforeDelete=async key=>{if(key===old.blobKey){entered.resolve();await release.promise}}
    const first=put(id,'first'); await entered.promise; await put(id,'second'); release.resolve(); await first; clear()
    assert.deepEqual(await read(id),{text:'second',type:'text/second'}); assert.equal((await a.keys()).length,before)
   }
   checks.push('reversed upload completion and delayed predecessor deletion preserve last commit')
   {
    const id='read-race'; await put(id,'old'); const old=await mapping(id)
    a.hooks.beforeRead=async key=>{if(key===old.blobKey){delete a.hooks.beforeRead; await put(id,'new')}}
    assert.deepEqual(await read(id),{text:'new',type:'text/new'}); clear()
    let reads=0
    a.hooks.beforeRead=async()=>{reads++; await put(id,'next'+reads)}
    await assert.rejects(read(id),e=>e.status===503); clear(); assert.equal(reads,2)
   }
   checks.push('old-mapping read recovers once; repeated replacement stops after two blob reads with 503')
   for(const phase of ['beforeUpload','afterUpload']) {
    const id='upload-fail-'+phase; await put(id,'old'); const old=await mapping(id), before=(await a.keys()).length
    a.hooks[phase]=()=>{throw new Error('synthetic upload failure')}
    await assert.rejects(put(id,'new')); clear()
    assert.deepEqual(await mapping(id),old); assert.equal((await a.keys()).length,before)
    assert.equal((await read(id)).text,'old')
   }
   checks.push('failed and partial uploads keep old mapping and remove only new key')
   {
    const id='metadata-fail'; await put(id,'old'); const old=await mapping(id), before=(await a.keys()).length
    await a.sql("CREATE TRIGGER fail_asset BEFORE INSERT ON metadata WHEN new.key = 'asset:A:metadata-fail' BEGIN SELECT RAISE(ABORT, 'synthetic metadata failure'); END")
    try {await assert.rejects(put(id,'new'))} finally {await a.sql('DROP TRIGGER fail_asset')}
    assert.deepEqual(await mapping(id),old); assert.equal((await read(id)).text,'old')
    assert.equal((await a.keys()).length,before+(a.name==='node'?0:1))
   }
   checks.push('actual SQLite failure rolls back; Node removes uncommitted new blob, remote error conservatively retains it')
   {
    const id='unknown-commit'; await put(id,'old'); const old=await mapping(id), before=(await a.keys()).length
    a.hooks.afterCommit=()=>{throw new Error('synthetic lost commit acknowledgement')}
    await assert.rejects(put(id,'new')); clear()
    const current=await mapping(id); assert.notEqual(current.blobKey,old.blobKey)
    const keys=await a.keys(); assert(keys.includes(old.blobKey)); assert(keys.includes(current.blobKey)); assert.equal(keys.length,before+1)
    assert.equal((await read(id)).text,'new')
   }
   checks.push('commit-then-lost-ack retains current and prior blobs without rollback/retry')
   {
    const id='delete-fail'; await put(id,'old'); const old=await mapping(id), before=(await a.keys()).length
    a.hooks.beforeDelete=key=>{if(key===old.blobKey) throw new Error('synthetic delete failure')}
    const response=await handle(a.host,new Request(origin+'/uploads/'+id+'?room=A',{method:'PUT',headers:{authorization:'Bearer probe.'+secret},body:'new'}))
    assert.equal(response.status,503); clear()
    assert.notEqual((await mapping(id)).blobKey,old.blobKey); assert.equal((await a.keys()).length,before+1); assert.equal((await read(id)).text,'new')
   }
   {
    const id='missing-predecessor'; await put(id,'old'); await a.remove((await mapping(id)).blobKey); await put(id,'new'); assert.equal((await read(id)).text,'new')
   }
   {
    const id='invalid-owner', invalid={blobKey:a.name==='node'?'../outside':'B/'+crypto.randomUUID(),contentType:'text/plain',size:1}
    await a.host.meta.put('asset:A:'+id,invalid)
    await assert.rejects(put(id,'new')); assert.deepEqual(await mapping(id),invalid)
   }
   checks.push('delete failure returns 503 with valid committed data; missing old blob is clean; invalid predecessor rejected')
   assert.deepEqual([await mapping('untouched'),await mapping('untouched','B')],preserved)
   assert.equal((await read('untouched')).text,'same'); assert.equal((await read('untouched','B')).text,'other')
   clear()
   if(a.name==='cloudflare-local') {
    const unsupported=new CloudflareHost({REGISTRY:registryBinding,JOURNEY_ORIGIN:origin,JOURNEY_GRANTS:JSON.stringify(grants)})
    await assert.rejects(unsupported.putAsset('A','none',new Uint8Array(),'text/plain'),e=>e.status===501)
   }
   reports.push({adapter:a.name,result:'PASS',checks,storage:a.name==='node'?'actual Node SQLite/files':'actual workerd registry SQLite/local R2; fault probes orchestrate exact CloudflareHost in Node',faults:'narrow I/O and post-commit injection; no replacement storage implementation'})
  } catch(error) { for(const k of Object.keys(a.hooks)) delete a.hooks[k]; reports.push({adapter:a.name,result:'FAIL',error:error.message}); process.exitCode=1 }
 }
} finally {
 Object.assign(fs,originalFs); syncBuiltinESMExports()
 node?.close(); await mf?.dispose()
 for (const [k,v] of Object.entries(savedEnv)) if(v===undefined) delete process.env[k]; else process.env[k]=v
 await rm(scratch,{recursive:true,force:true})
}
console.log(JSON.stringify({reports,hosted:'NOT RUN',billing:'NOT RUN',cleanup:'owned stores/runtime removed'},null,2))

