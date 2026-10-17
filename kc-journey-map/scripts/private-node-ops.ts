import { readFile, writeFile, readdir, access } from 'node:fs/promises'
import { resolve, relative, isAbsolute } from 'node:path'
import { pathToFileURL } from 'node:url'
import { NodeHost } from '../server/host/node'
import { backupPrivateHost, restorePrivateHost, validateBackup, type PrivateBackup } from './private-backup'
import { validateGrants } from '../server/host/policy'

const exists = async (path: string) => access(path).then(() => true, () => false)

export async function privateNodeOperation(op: string, fileOrId: string, stopped: boolean) {
 if (!stopped || !process.env.JOURNEY_PRIVATE_DIR || !process.env.JOURNEY_GRANTS_FILE || !process.env.JOURNEY_ORIGIN)
  throw new Error('stop the owning server and writers; private environment and --stopped are required')
 if (!['backup', 'restore', 'revoke'].includes(op) || !fileOrId) throw new Error('expected backup <new-file>, restore <archive>, or revoke <credential-id>')
 const root = resolve(process.env.JOURNEY_PRIVATE_DIR)
 let archive: PrivateBackup | undefined
 if (op === 'restore') {
  if (await exists(root) && (await readdir(root)).length) throw new Error('restore requires a fresh empty private directory')
  archive = validateBackup(JSON.parse(await readFile(fileOrId, 'utf8')))
  const oldIds = new Set(archive.grants.map(g => g.credentialId))
  const fresh = validateGrants(JSON.parse(await readFile(process.env.JOURNEY_GRANTS_FILE, 'utf8')))
  if (fresh.some(g => oldIds.has(g.credentialId))) throw new Error('restore requires new credential IDs; archived IDs stay revoked')
 } else if (!await exists(resolve(root, '.journey-private-v1'))) {
  throw new Error('backup/revoke requires existing private storage')
 }
 if (op === 'backup') {
  const path = relative(root, resolve(fileOrId))
  if (!path || !(path === '..' || path.startsWith('../') || isAbsolute(path))) throw new Error('backup must be outside private storage')
  if (await exists(fileOrId)) throw new Error('backup refuses to overwrite an existing file')
 }
 const host = new NodeHost()
 try {
  if (op === 'revoke') return await host.revoke(fileOrId)
  if (op === 'backup') {
   const backup = await backupPrivateHost(host)
   await writeFile(fileOrId, JSON.stringify(backup) + '\n', { flag: 'wx', mode: 0o600 })
   return { rooms: backup.rooms.length, policy: 'included; secrets and sessions excluded' }
  }
  return await restorePrivateHost(host, archive!)
 } finally { host.close() }
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
 try {
  const [op, fileOrId, confirmation] = process.argv.slice(2)
  console.log(JSON.stringify(await privateNodeOperation(op, fileOrId, confirmation === '--stopped')))
 } catch (error) {
  console.error((error as Error).message)
  process.exitCode = 1
 }
}
