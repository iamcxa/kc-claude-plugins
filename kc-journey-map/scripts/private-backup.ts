import { exportRoom, restoreRoom } from '../server/host/recovery'
import { validateGrants, type Grant } from '../server/host/policy'
import { canonicalRoom } from '../server/host/core'
import type { Host } from '../server/host/transport'

export type PrivateBackup = { format: 'journey-private-backup-1'; grants: Grant[]; rooms: Awaited<ReturnType<typeof exportRoom>>[]; security?: {format:'journey-security-1';records:Array<{key:string;value:any}>} }

export function validateBackup(archive: PrivateBackup) {
 if (archive?.format !== 'journey-private-backup-1' || !Array.isArray(archive.rooms) || !archive.rooms.length ||
  archive.rooms.some(r => !r.room || canonicalRoom(r.room) !== r.room) ||
  new Set(archive.rooms.map(r => r.room)).size !== archive.rooms.length) throw new Error('invalid private backup')
 validateGrants(archive.grants)
 return archive
}

export async function backupPrivateHost(host: Host) {
 const grants = (await host.meta.list<Grant>('grant:')).map(e => e.value)
 const rooms = []
 for (const entry of await host.meta.list('room:')) rooms.push(await exportRoom(host, entry.key.slice(5)))
 const records=(await host.meta.list('')).filter(row=>/^(grant:|member:|member-room:|human-|browser-session:|agent-|security-)/.test(row.key))
 return validateBackup({ format: 'journey-private-backup-1', grants, rooms, security:{format:'journey-security-1',records} })
}

export async function restorePrivateHost(host: Host, archive: PrivateBackup) {
 validateBackup(archive)
 if ((await host.meta.list('room:')).length) throw new Error('restore requires a fresh namespace')
 const oldIds = new Set(archive.grants.map(g => g.credentialId))
 const current = (await host.meta.list<Grant>('grant:')).map(e => e.value)
 if (current.some(g => oldIds.has(g.credentialId))) throw new Error('restore requires new credential IDs')
 if(host.humanConfig && !archive.security)throw new Error('human recovery requires a security-aware archive')
 if(archive.security){if(!host.meta.security)throw new Error('security-aware recovery required');await host.meta.security('restore-security',archive.security)}
 // A stale backup cannot prove current revocation state. Quarantine every old ID.
 for (const grant of archive.grants) await host.meta.put('grant:' + grant.credentialId, { ...grant, revoked: true })
 for (const room of archive.rooms) await restoreRoom(host, room)
 return { rooms: archive.rooms.length, policy: 'archived credentials revoked; fresh grants explicitly supplied' }
}
