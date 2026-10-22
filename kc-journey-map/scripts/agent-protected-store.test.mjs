import assert from 'node:assert/strict'
import { test } from 'node:test'
import { mkdtemp,readFile,rm,lstat } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { openProtectedStore } from './agent-protected-store.mjs'

test('real macOS app-owned Keychain item roundtrip and interprocess lock; no secret disk fallback',async()=>{
 assert.equal(process.platform,'darwin','other OS adapters remain unverified')
 const root=await mkdtemp(join(tmpdir(),'journey-agent-keychain-test-'))
 const config={backendId:'synthetic-test',installationId:crypto.randomUUID()}
 let store
 try {
  store=await openProtectedStore(config,root)
  await assert.rejects(()=>openProtectedStore(config,root),/installation_busy/)
  assert.equal(await store.get(),null)
  const secret=crypto.randomUUID()
  await store.set({state:'rotation-pending',refreshSecret:secret}); await store.confirm()
  assert.deepEqual(await store.get(),{state:'rotation-pending',refreshSecret:secret})
  const manifest=await readFile(join(store.directory,'manifest.json'),'utf8')
  assert.ok(!manifest.includes(secret)); assert.equal((await lstat(store.directory)).mode & 0o077,0)
  await store.close(); store=await openProtectedStore(config,root)
  assert.equal((await store.get()).refreshSecret,secret)
  await store.set({state:'active',refreshSecret:'unconfirmed synthetic replacement'})
  await store.close();store=await openProtectedStore(config,root)
  assert.deepEqual(await store.get(),{state:'repair-pending',refreshSecret:secret})
  await store.set({state:'active',refreshSecret:'synthetic replacement'}); await store.confirm()
  await store.set({state:'revoked'}); await store.confirm(); await store.removeRevoked()
  assert.equal(await store.get(),null)
 } finally { if(store) { try { const current=await store.get(); if(current) { await store.set({state:'revoked'}); await store.confirm() } await store.removeRevoked() } finally { await store.close() } } await rm(root,{recursive:true,force:true}) }
})
