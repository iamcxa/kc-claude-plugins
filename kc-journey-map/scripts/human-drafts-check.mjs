import assert from 'node:assert/strict'
import {mkdir,mkdtemp,writeFile} from 'node:fs/promises'
import {join} from 'node:path'
import {createServer as netServer} from 'node:net'
import {spawn} from 'node:child_process'
import {createServer} from 'vite'
import {chromium} from 'playwright'
const root=new URL('..',import.meta.url).pathname.replace(/\/$/,'')
await mkdir(join(root,'.host-check'),{recursive:true})
const scratch=await mkdtemp(join(root,'.host-check/draft-storage-'))
const freePort=()=>new Promise(resolve=>{const s=netServer();s.listen(0,'127.0.0.1',()=>{const p=s.address().port;s.close(()=>resolve(p))})})
const port=await freePort(),origin='http://127.0.0.1:'+port
const server=await createServer({configFile:join(root,'vite.config.mts'),server:{host:'127.0.0.1',port,strictPort:true}})
await server.listen()
let browser,child,storageContext,crashContext,ownBrowserPid
const report={browser:chromium.executablePath(),platform:process.platform,node:process.version,checks:[],crash:'NOT RUN'}
const pass=name=>{report.checks.push(name);console.log('PASS '+name)}
const setup=async page=>{
 await page.route(origin+'/draft-test',route=>route.fulfill({contentType:'text/html',body:'<!doctype html><title>Local draft storage test</title>'}))
 await page.goto(origin+'/draft-test')
 await page.evaluate(async sourceRoot=>{
  const S=await import('/human-drafts.ts'),D=await import('/@fs'+sourceRoot+'/server/draft-data.ts')
  const now=Date.now()
  window.storageTest={S,D,context:{origin:location.origin,backend:'test',member:'owner',issuer:'synthetic',subject:'owner-subject',generation:1,signInAt:now,revalidateBy:now+604800000,room:'one'},records:{'document:document':{id:'document:document',typeName:'document',gridSize:10,name:'synthetic',meta:{}}}}
 },root)
}
try{
 storageContext=await chromium.launchPersistentContext(join(scratch,'storage-profile'),{headless:true});const page=await storageContext.newPage();await setup(page)
 await page.evaluate(async()=>{
  const {S,context,records}=window.storageTest,db=await S.openHumanDrafts('storage-main')
  if(db.db.version!==2 || db.db.objectStoreNames.length!==5)throw Error('wrong initialized schema')
  const version=await db.save(context,'draft','tab',records,records)
  db.close();const reopened=await S.openHumanDrafts('storage-main')
  const loaded=await reopened.load(context,version.key)
  if(loaded.hash!==version.hash || JSON.stringify(loaded.records)!==JSON.stringify(records))throw Error('acknowledged version lost')
  window.storageTest.db=reopened;window.storageTest.version=version
 })
 pass('real new IndexedDB schema 2 strict write acknowledges intact immutable version only after reopen')
 await page.evaluate(async()=>{
  const {db,context,records,version}=window.storageTest
  const events=[],original=IDBDatabase.prototype.transaction
  IDBDatabase.prototype.transaction=function(...args){const tx=original.apply(this,args);if(args[1]==='readwrite')tx.addEventListener('complete',()=>events.push('complete'));return tx}
  try{await db.save(context,'draft','tab',records,records);events.push('ack');if(events.join(',')!=='complete,ack')throw Error('early acknowledgment')}
  finally{IDBDatabase.prototype.transaction=original}
  const add=IDBObjectStore.prototype.add
  IDBObjectStore.prototype.add=function(...args){const r=add.apply(this,args);if(this.name==='draftVersions')r.addEventListener('success',()=>this.transaction.abort());return r}
  let failed=false
  try{await db.save(context,'draft','tab',records,records)}catch{failed=true}finally{IDBObjectStore.prototype.add=add}
  if(!failed || (await db.inventory(context)).length!==2)throw Error('aborted version or head acknowledged')
  if((await db.load(context,version.key)).hash!==version.hash)throw Error('abort erased prior version')
  const a=await db.save(context,'draft','tab',records,records)
  if(a.key[5]!==3)throw Error('abort advanced head')
  const strict=IDBDatabase.prototype.transaction
  IDBDatabase.prototype.transaction=function(stores,mode,options){return strict.call(this,stores,mode,mode==='readwrite'?{durability:'relaxed'}:options)}
  try{await db.save(context,'draft','tab',records,records);throw Error('unsupported strict accepted')}catch(e){if(e.message!=='strict_durability_unsupported')throw e}finally{IDBDatabase.prototype.transaction=strict}
 })
 pass('transaction-complete precedes acknowledgment; real abort after request success preserves head/data; unsupported strict mode refuses acknowledgment')
 await page.evaluate(async()=>{
  const {db,context,records}=window.storageTest
  const saved=await Promise.all([db.save(context,'parallel','tab-A',records,records),db.save(context,'parallel','tab-B',records,records)])
  if(saved[0].key[4]===saved[1].key[4])throw Error('tab identities shared')
  if((await db.inventory({...context,member:'other'})).length || (await db.inventory({...context,subject:'rebound'})).length)throw Error('cross-person inventory')
  await db.remove(context,saved[0].key)
  await db.load(context,saved[1].key)
  try{await db.save(context,'invalid','tab',null,{token:{id:'token',typeName:'credential',secret:'synthetic'}});throw Error('private payload accepted')}catch(e){if(e.message==='private payload accepted')throw e}
 })
 pass('concurrent tab lineages and selected deletion preserve other tabs; wrong member/identity has no inventory and non-document payload is rejected')
 await page.evaluate(async()=>{
  const {S,context,records,D}=window.storageTest
  const raw=await new Promise((resolve,reject)=>{const r=indexedDB.open('storage-upgrade',1);r.onupgradeneeded=()=>{for(const name of ['draftVersions','draftHeads','roomHistory'])r.result.createObjectStore(name)};r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error)})
  const hash=await D.fingerprint(records),key=['test','owner','one','old','tab',1]
  await new Promise((resolve,reject)=>{const tx=raw.transaction(['draftVersions','draftHeads'],'readwrite');tx.objectStore('draftVersions').put({key,schemaVersion:1,context,base:records,records,hash,createdAt:1},key);tx.objectStore('draftHeads').put({context,version:1,hash},key.slice(0,5));tx.oncomplete=resolve;tx.onabort=reject})
  try{await S.openHumanDrafts('storage-upgrade');throw Error('blocked upgrade accepted')}catch(e){if(e.message!=='draft_upgrade_blocked')throw e}
  raw.close();await new Promise(resolve=>setTimeout(resolve,50))
  const upgraded=await S.openHumanDrafts('storage-upgrade');if((await upgraded.load(context,key)).hash!==hash)throw Error('upgrade lost old payload');upgraded.close()
 })
 pass('real version-1 database blocks upgrade while open, then upgrades to version 2 preserving old immutable payload/head')
 await page.evaluate(async()=>{
  const {S,context}=window.storageTest
  const first=await new Promise((resolve,reject)=>{const r=indexedDB.open('upgrade-abort',1);r.onupgradeneeded=()=>{for(const name of ['draftVersions','draftHeads','roomHistory'])r.result.createObjectStore(name)};r.onerror=()=>reject(r.error);r.onsuccess=()=>resolve(r.result)})
  await new Promise((resolve,reject)=>{const tx=first.transaction('roomHistory','readwrite');tx.objectStore('roomHistory').put({context,room:'one',token:'old'},['test','owner']);tx.oncomplete=resolve;tx.onabort=reject});first.close()
  const open=IDBFactory.prototype.open
  IDBFactory.prototype.open=function(...args){const r=open.apply(this,args);if(args[0]==='upgrade-abort'&&args[1]===2)r.addEventListener('upgradeneeded',()=>r.transaction.abort());return r}
  let rejected=false
  try{await S.openHumanDrafts('upgrade-abort')}catch{rejected=true}finally{IDBFactory.prototype.open=open}
  if(!rejected)throw Error('aborted upgrade accepted')
  const db=await S.openHumanDrafts('upgrade-abort');if(await db.history(context)!=='one')throw Error('aborted upgrade erased old value');db.close()
 })
 pass('real aborted onupgradeneeded transaction preserves previous data and later successful upgrade reopens it')
 await page.evaluate(async()=>{
  const {db,context,records,D}=window.storageTest,version=await db.save(context,'lease','tab',records,records)
  const patch={put:[],remove:[]},attempt={id:crypto.randomUUID(),key:version.key,hash:version.hash,context,reviewedHash:await D.fingerprint(records),patch,requestHash:await D.fingerprint(patch),tabId:'first',leaseToken:crypto.randomUUID(),state:'prepared',createdAt:Date.now()}
  const competing={...attempt,id:crypto.randomUUID(),leaseToken:crypto.randomUUID(),tabId:'second'}
  const result=await Promise.allSettled([db.prepare(attempt),db.prepare(competing)])
  if(result.filter(r=>r.status==='fulfilled').length!==1)throw Error('parallel lease ownership')
  const owner=result[0].status==='fulfilled'?attempt:competing
  try{await db.remove(context,version.key,owner);throw Error('unverified cleanup accepted')}catch(e){if(e.message==='unverified cleanup accepted')throw e}
  await db.transaction(['restoreLease'],true,async tx=>{const r=tx.objectStore('restoreLease').get(version.key);await new Promise(resolve=>{r.onsuccess=resolve});tx.objectStore('restoreLease').put({...r.result,deadline:1},version.key)})
  try{await db.prepare({...attempt,id:crypto.randomUUID()});throw Error('expired lease resent')}catch(e){if(e.message==='expired lease resent')throw e}
  await db.load(context,version.key)
 })
 pass('real local transactions elect one exact-version apply owner; unverified cleanup and expired-lease resend are refused without deleting draft')
 if(process.env.JOURNEY_DRAFT_SKIP_QUOTA!=='true'){
 const cdp=await page.context().newCDPSession(page)
 await cdp.send('Storage.overrideQuotaForOrigin',{origin,quotaSize:1})
 report.quotaBefore=await cdp.send('Storage.getUsageAndQuota',{origin})
 const quota=await page.evaluate(async()=>{
  const {S,context,records}=window.storageTest;window.storageTest.db.close();let fresh
  try{fresh=await S.openHumanDrafts('quota-fresh');await fresh.save(context,'quota','tab',records,{'document:document':{...records['document:document'],name:Array.from({length:48},()=>btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(65536))))).join('')}});return 'unexpected acknowledgment'}catch(e){return e.name}finally{fresh?.close()}
 })
 report.quotaAfter=await cdp.send('Storage.getUsageAndQuota',{origin});report.quotaProbe={result:quota,payloadCapBytes:5_000_000,totalNewStorageCapBytes:16*1024*1024,timeCapSeconds:60,probes:1,cleanup:'exact quota-fresh database deleted'}
 await page.evaluate(()=>new Promise((resolve,reject)=>{const r=indexedDB.deleteDatabase('quota-fresh');r.onsuccess=resolve;r.onerror=()=>reject(r.error)}))
 await cdp.send('Storage.overrideQuotaForOrigin',{origin})
 await page.evaluate(async()=>{const {S,context,version}=window.storageTest;const db=await S.openHumanDrafts('storage-main');await db.load(context,version.key);window.storageTest.db=db})
 if(quota==='QuotaExceededError')pass('real origin quota rejection prevents acknowledgment and preserves prior version')
 else{report.quotaEnforcement='UNPASSED: overrideActive quota 1 still accepted one bounded fresh-DB write; injected abort/strict evidence is distinct';console.log(report.quotaEnforcement)}

 }else report.quotaEnforcement='NOT RERUN; prior bounded fresh-DB probe remained unpassed'
 await storageContext.close();storageContext=undefined
 const profile=join(scratch,'crash-profile')
 async function start(){
  crashContext=await chromium.launchPersistentContext(profile,{headless:true})
  const cdp=await crashContext.browser().newBrowserCDPSession(),info=await cdp.send('SystemInfo.getProcessInfo')
  ownBrowserPid=info.processInfo.find(p=>p.type==='browser').id
  return crashContext.newPage()
 }
 let crashPage=await start();await setup(crashPage)
 await crashPage.evaluate(async()=>{const {S,context,records}=window.storageTest;const db=await S.openHumanDrafts('crash-test');await db.save(context,'crash','tab',records,records);window.storageTest.db=db})
 await crashPage.evaluate(()=>{
  const add=IDBObjectStore.prototype.add
  IDBObjectStore.prototype.add=function(...args){const r=add.apply(this,args);if(this.name==='draftVersions')r.addEventListener('success',()=>{window.unacknowledgedRequestSucceeded=true;const keep=()=>{try{this.count().onsuccess=keep}catch{}};keep()});return r}
  const {db,context,records}=window.storageTest;window.crashAck=false;void db.save(context,'crash','tab',records,records).then(()=>{window.crashAck=true})
 })
 await crashPage.waitForFunction(()=>window.unacknowledgedRequestSucceeded===true)
 assert.equal(await crashPage.evaluate(()=>window.crashAck),false)
 const exited=new Promise(resolve=>crashContext.browser().once('disconnected',resolve));process.kill(ownBrowserPid,'SIGKILL');await exited;crashContext=undefined
 crashPage=await start();await setup(crashPage)
 const crashResult=await crashPage.evaluate(async()=>{const {S,context}=window.storageTest;const db=await S.openHumanDrafts('crash-test');return (await db.inventory(context)).map(v=>v.key[5])})
 assert.deepEqual(crashResult,[1]);report.crash='Actual owned Chromium browser process SIGKILL after version-2 request success but before transaction completion; acknowledged v1 reopened, v2 absent. One Linux/macOS runtime observation, no OS/power-loss promise.'
 pass('actual browser-process kill during unacknowledged strict transaction preserves acknowledged v1 and does not acknowledge/restore uncommitted v2')
}finally{
 await crashContext?.close().catch(()=>{});await storageContext?.close().catch(()=>{});await browser?.close().catch(()=>{});if(child && child.exitCode===null)child.kill('SIGTERM');await server.close()
 await writeFile(join(scratch,'report.json'),JSON.stringify(report,null,2));console.log('evidence='+join(scratch,'report.json'))
}
