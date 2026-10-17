import { CloudflareHost } from '../server/host/cloudflare'
import { backupPrivateHost, restorePrivateHost, validateBackup } from './private-backup'
import { canonicalRoom } from '../server/host/core'
import type { Grant } from '../server/host/policy'

export default {
 async fetch(req: Request, env: any) {
  if (req.method !== 'POST' || new URL(req.url).pathname !== '/') return new Response(null, { status: 404 })
  try {
   const command = await req.json() as any
   if (!['backup', 'restore', 'revoke'].includes(command.op)) throw new Error('unsupported operation')
   if (command.writersStopped !== true) throw new Error('stop writers before operator work')
   const rooms = JSON.parse(env.JOURNEY_OPERATOR_ROOMS)
   if (!Array.isArray(rooms) || !rooms.length || rooms.some(r => !r || canonicalRoom(r) !== r)) throw new Error('explicit operator rooms required')
   const host = new CloudflareHost(env)
   const existing = (await host.meta.list('room:')).map(e => e.key.slice(5))
   if (existing.some(r => !rooms.includes(r))) throw new Error('namespace contains rooms outside operator scope')
   let result
   if (command.op === 'backup') result = await backupPrivateHost(host)
   if (command.op === 'restore') {
    const archive = validateBackup(command.archive)
    if (archive.rooms.some(r => !rooms.includes(r.room))) throw new Error('archive outside operator scope')
    if (archive.rooms.some(r => r.assets.length)) throw new Error('hosted assets are not enabled')
    result = await restorePrivateHost(host, archive)
   }
   if (command.op === 'revoke') {
    const grant = await host.meta.get<Grant>('grant:' + command.credentialId)
    if (!grant || grant.rooms.some(r => !rooms.includes(r))) throw new Error('credential outside operator scope')
    const registry = env.REGISTRY.get(env.REGISTRY.idFromName('private-pilot'))
    const response = await registry.fetch(new Request('https://registry/revoke', { method: 'POST', body: JSON.stringify({ credentialId: grant.credentialId }) }))
    if (!response.ok) throw new Error('partial revocation; retry before resuming')
    result = await response.json()
   }
   return Response.json(result)
  } catch (error) {
   return Response.json({ error: (error as Error).message }, { status: 400 })
  }
 },
}
