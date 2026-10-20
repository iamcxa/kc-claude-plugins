import { spawn } from 'node:child_process'
import { createInterface } from 'node:readline'
import { mkdir,lstat,open,rename,unlink } from 'node:fs/promises'
import { constants } from 'node:fs'
import { createHash,randomUUID } from 'node:crypto'
import { join,resolve } from 'node:path'
const uuid=value=>typeof value==='string' && /^[a-f0-9-]{36}$/i.test(value)
const pointer=value=>value&&typeof value==='object'&&(value.slot===null||uuid(value.slot))
async function privateDirectory(path) {
 await mkdir(path,{recursive:true,mode:0o700})
 const stat=await lstat(path)
 if(!stat.isDirectory() || stat.isSymbolicLink() || stat.uid!==process.geteuid() || (stat.mode & 0o077)) throw new Error('protected_directory_denied')
}
async function atomicFile(directory,name,value) {
 const temporary=join(directory,'.'+randomUUID()),file=await open(temporary,constants.O_WRONLY|constants.O_CREAT|constants.O_EXCL|constants.O_NOFOLLOW,0o600)
 try { await file.writeFile(JSON.stringify(value)); await file.sync() } finally { await file.close() }
 await rename(temporary,join(directory,name))
 const dir=await open(directory,constants.O_RDONLY); try { await dir.sync() } finally { await dir.close() }
}
async function ownedJSON(path,fallback) {
 let file
 try {
  file=await open(path,constants.O_RDONLY|constants.O_NOFOLLOW); const stat=await file.stat()
  if(!stat.isFile() || stat.uid!==process.geteuid() || (stat.mode & 0o077)) throw new Error('protected_manifest_denied')
  return JSON.parse(await file.readFile('utf8'))
 } catch(error) { if(error.code==='ENOENT') return fallback; throw error } finally { await file?.close() }
}
export async function openProtectedStore(config,root) {
 if(process.platform!=='darwin' || typeof process.geteuid!=='function') throw new Error('protected_store_unverified_platform')
 for(const key of ['backendId','installationId']) if(!/^[a-zA-Z0-9_-]{1,128}$/.test(config[key])) throw new Error('protected_store_invalid')
 root=resolve(root); await privateDirectory(root)
 const directory=join(root,createHash('sha256').update(config.backendId+':'+config.installationId).digest('hex'))
 await privateDirectory(directory)
 const child=spawn('/usr/bin/swift',['-module-cache-path',join(root,'swift-cache'),new URL('./agent-keychain.swift',import.meta.url).pathname],{stdio:['pipe','pipe','pipe']})
 child.stderr.resume()
 const waiting=[]; let dead=false
 createInterface({input:child.stdout}).on('line',line=>{ const resolve=waiting.shift(); try { resolve?.(JSON.parse(line)) } catch { resolve?.({ok:false,category:'protected_store_unavailable'}) } })
 const failed=()=>{dead=true;for(const resolve of waiting.splice(0)) resolve({ok:false,category:'protected_store_unavailable'})}
 child.once('error',failed); child.once('exit',failed)
 child.stdin.on('error',failed)
 async function send(value) {
  if(dead) throw new Error('protected_store_unavailable')
  const result=new Promise(resolve=>waiting.push(resolve)); child.stdin.write(JSON.stringify(value)+'\n')
  let timer
  const reply=await Promise.race([result,new Promise(resolve=>{timer=setTimeout(()=>{child.kill();resolve({ok:false,category:'protected_store_timeout'})},60_000)})]); clearTimeout(timer)
  if(!reply.ok) { const error=new Error(reply.category); error.osStatus=reply.osStatus; throw error }
  return reply
 }
 try { await send({backendId:config.backendId,installationId:config.installationId,lockPath:join(directory,'process.lock')}) }
 catch(error) { child.kill(); throw error }
 let manifest,journal,checkpoint
 try { manifest=await ownedJSON(join(directory,'manifest.json'),{slot:null});journal=await ownedJSON(join(directory,'slots.json'),[]);checkpoint=await ownedJSON(join(directory,'checkpoint.json'),null) }
 catch(error) { child.kill();throw error }
 if(!pointer(manifest) || (checkpoint!==null&&!pointer(checkpoint)) || !Array.isArray(journal) || journal.some(s=>!uuid(s))) { child.kill(); throw new Error('protected_manifest_denied') }
 let staged
 async function clean() {
  const obsolete=journal.filter(s=>s!==manifest.slot && s!==staged?.slot && s!==checkpoint?.slot)
  for(const slot of obsolete) { await send({action:'delete',slot}); journal=journal.filter(s=>s!==slot) }
  await atomicFile(directory,'slots.json',journal)
 }
 try { await clean() } catch(error) { child.kill(); throw error }
 return {
  directory,
  async get() {
   const slot=staged?.slot||(checkpoint?checkpoint.slot:manifest.slot)
   if(!slot)return null
   const value=JSON.parse((await send({action:'get',slot})).value)
   return checkpoint&&!staged&&value.state!=='revoked'?{...value,state:'repair-pending'}:value
  },
  async set(value) {
   if(staged) throw new Error('secure_save_unconfirmed')
   if(!checkpoint){await atomicFile(directory,'checkpoint.json',manifest);checkpoint={...manifest}}
   const slot=randomUUID(); journal.push(slot); await atomicFile(directory,'slots.json',journal)
   await send({action:'put',slot,value:JSON.stringify(value)})
   const saved=JSON.parse((await send({action:'get',slot})).value)
   if(JSON.stringify(saved)!==JSON.stringify(value)) throw new Error('secure_save_unknown')
   staged={slot}
  },
  async confirm() {
   if(!staged) throw new Error('secure_save_unconfirmed')
   try {
    await atomicFile(directory,'manifest.json',staged);manifest=staged
    await unlink(join(directory,'checkpoint.json'));checkpoint=null;staged=undefined
   } catch { staged=undefined;throw new Error('secure_save_unknown') }
   // Confirmation is known; cleanup failure can only retain a conservative checkpoint or obsolete slot.
   try { const dir=await open(directory,constants.O_RDONLY);try{await dir.sync()}finally{await dir.close()} } catch { return }
   try { await clean() } catch { /* Committed pointer remains valid; the owned slot journal retains cleanup work. */ }
  },
  async removeRevoked() {
   if(checkpoint||staged)throw new Error('confirmed_revoke_required')
   const value=manifest.slot ? JSON.parse((await send({action:'get',slot:manifest.slot})).value) : null
   if(value && value.state!=='revoked') throw new Error('confirmed_revoke_required')
   await atomicFile(directory,'manifest.json',{slot:null}); manifest={slot:null}; staged=undefined; await clean()
  },
  async close() { child.stdin.end(); await new Promise(resolve=>{ if(dead) resolve();else child.once('exit',resolve) }) },
 }
}
