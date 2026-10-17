import { build } from 'esbuild'
import { Miniflare } from 'miniflare'
import { resolve, join } from 'node:path'
import { mkdir, readFile } from 'node:fs/promises'
import { createInterface } from 'node:readline'
import { pathToFileURL } from 'node:url'
let operatorModule
export async function startCloudflare({ dir, port, origin, grants, failRegistration = false }) {
 await mkdir(dir, { recursive: true })
 const bundle = join(dir, 'worker.mjs')
 const entry = new URL('../server/host/cloudflare.ts', import.meta.url).pathname
 await build({ entryPoints: [entry], outfile: bundle, bundle: true, format: 'esm', platform: 'browser', conditions: ['workerd', 'worker', 'browser'], external: ['cloudflare:workers'], logLevel: 'silent' })
 let script = await readFile(bundle, 'utf8')
 if (failRegistration) script = script.replace('export {', `const OriginalRegistry = JourneyRegistry;
class FaultRegistry extends OriginalRegistry {
 async fetch(req) {
  const body = await req.clone().json();
  if (new URL(req.url).pathname === '/put' && body.key.startsWith('room:')) return new Response('synthetic registry fault', { status: 503 });
  return super.fetch(req);
 }
}
export {`).replace('JourneyRegistry,', 'FaultRegistry as JourneyRegistry,')
 const mf = new Miniflare({
  script, modules: true, compatibilityDate: '2026-07-01', compatibilityFlags: ['nodejs_compat'], host: '127.0.0.1', port,
  bindings: { JOURNEY_ORIGIN: origin, JOURNEY_GRANTS: JSON.stringify(grants) },
  durableObjects: { ROOMS: { className: 'JourneyRoom', useSQLite: true }, REGISTRY: { className: 'JourneyRegistry', useSQLite: true } },
  durableObjectsPersist: join(dir, 'objects'), r2Buckets: ['ASSETS'], r2Persist: join(dir, 'assets'),
 })
 await mf.ready
 if (!operatorModule) {
  const operatorBundle = join(dir, 'operator.mjs')
  await build({ entryPoints: [entry], outfile: operatorBundle, bundle: true, format: 'esm', platform: 'node', packages: 'external', logLevel: 'silent' })
  operatorModule = await import(pathToFileURL(operatorBundle).href)
 }
 const { CloudflareHost, exportRoom, restoreRoom } = operatorModule
 const namespace = async name => {
  const ns = await mf.getDurableObjectNamespace(name)
  return { idFromName: id => ns.idFromName(id), get: id => {
   const target = ns.get(id)
   return { fetch: async (req, init) => req instanceof Request
    ? target.fetch(req.url, { method: req.method, headers: Object.fromEntries(req.headers), ...(['GET', 'HEAD'].includes(req.method) ? {} : { body: await req.arrayBuffer() }) })
    : target.fetch(req, init) }
  } }
 }
 const operator = new CloudflareHost({ ROOMS: await namespace('ROOMS'), REGISTRY: await namespace('REGISTRY'),
  ASSETS: await mf.getR2Bucket('ASSETS'), JOURNEY_ORIGIN: origin, JOURNEY_GRANTS: JSON.stringify(grants) })
 return {
  export: room => exportRoom(operator, room),
  restore: archive => restoreRoom(operator, archive),
  mf,
  async revoke(credentialId) {
   const ns = await mf.getDurableObjectNamespace('REGISTRY')
   const response = await ns.get(ns.idFromName('private-pilot')).fetch('https://registry/revoke', { method: 'POST', body: JSON.stringify({ credentialId }) })
   const result = await response.json()
   if (!response.ok) throw new Error('partial revocation')
   return result
  },
  close: () => mf.dispose(),
 }
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
 const dir = process.env.JOURNEY_PRIVATE_DIR
 if (!dir || !process.env.JOURNEY_GRANTS_FILE || !process.env.JOURNEY_ORIGIN) throw new Error('private directory, grants file and origin required')
 const host = await startCloudflare({ dir, port: Number(process.env.JOURNEY_API_PORT || 5858), origin: process.env.JOURNEY_ORIGIN, grants: JSON.parse(await readFile(process.env.JOURNEY_GRANTS_FILE, 'utf8')) })
 console.log('Cloudflare local emulator ready')
 if (process.env.JOURNEY_CONTROL_STDIO === '1') createInterface({ input: process.stdin }).on('line', async line => {
  try { const c = JSON.parse(line); const result = c.op === 'revoke' ? await host.revoke(c.credentialId) : c.op === 'export' ? await host.export(c.room) : c.op === 'restore' ? await host.restore(c.archive) : (() => { throw new Error('unknown command') })(); console.log(JSON.stringify({ control: c.id, result })) }
  catch { console.log(JSON.stringify({ controlError: 'operator command failed' })) }
 })
 for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, () => host.close().finally(() => process.exit()))
}
