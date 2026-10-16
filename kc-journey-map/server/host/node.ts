import { DatabaseSync } from 'node:sqlite'
import { mkdirSync, readFileSync, readdirSync, writeFileSync, existsSync } from 'node:fs'
import { readFile, writeFile, mkdir } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import { Readable } from 'node:stream'
import { NodeSqliteWrapper, SQLiteSyncStorage, TLSocketRoom } from '@tldraw/sync-core'
import { HostError, operate } from './core'
import { currentGrant, validateGrants, type Grant, type Admission, type Metadata } from './policy'
import type { Host } from './transport'
import { pruneExpiredSessions } from './session-retention'
import { loadAsset, storeAsset } from '../assets'
import { saveBoard, saveDir, saveTarget } from '../save'
import { readRepoDoc } from '../repo-doc'

export class NodeHost implements Host {
 private = !!process.env.JOURNEY_PRIVATE_DIR
 origin = process.env.JOURNEY_ORIGIN || 'http://localhost:3737'
 port = Number(process.env.JOURNEY_API_PORT || 5858)
 root = resolve(process.env.JOURNEY_PRIVATE_DIR || '.')
 roomsDir = this.private ? join(this.root, 'rooms') : (process.env.JOURNEY_ROOMS_DIR || './.rooms')
 rooms = new Map<string, { room: TLSocketRoom<any, any>; db: DatabaseSync }>()
 sockets = new Map<any, { admission: Admission | null; room: string; timer?: ReturnType<typeof setTimeout> }>()
 db: DatabaseSync
 meta: Metadata
 roomRepos: Record<string, string[]> = JSON.parse(process.env.JOURNEY_ROOM_REPOS || '{}')
 constructor() {
  if (this.private && (!process.env.JOURNEY_GRANTS_FILE || !process.env.JOURNEY_ORIGIN)) throw new Error('private mode requires JOURNEY_GRANTS_FILE and JOURNEY_ORIGIN')
  if (this.private) {
   const u = new URL(this.origin)
   if (u.origin !== this.origin || (u.protocol !== 'https:' && !['localhost', '127.0.0.1'].includes(u.hostname)))
    throw new Error('private browser origin requires HTTPS (loopback development excepted)')
  }
  if (this.private) {
   const marker = join(this.root, '.journey-private-v1')
   if (!existsSync(marker)) {
    if (existsSync(this.root) && readdirSync(this.root).length) throw new Error('private storage must start empty; retained-data import is not supported')
    mkdirSync(this.root, { recursive: true })
    writeFileSync(marker, 'journey-private-v1\n', { flag: 'wx', mode: 0o600 })
   }
  }
  mkdirSync(this.roomsDir, { recursive: true })
  const metadataDir = this.private ? this.root : join(this.roomsDir, '.metadata')
  mkdirSync(metadataDir, { recursive: true })
  this.db = new DatabaseSync(join(metadataDir, 'metadata.sqlite'))
  this.db.exec('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
  this.meta = {
   get: async <T>(key: string) => {
    const row = this.db.prepare('SELECT value FROM metadata WHERE key = ?').get(key) as { value: string } | undefined
    return row ? JSON.parse(row.value) as T : null
   },
   put: async (key, value) => {
    if (key.startsWith('session:')) pruneExpiredSessions((sql, ...bindings) => this.db.prepare(sql).all(...bindings))
    this.db.prepare('INSERT OR REPLACE INTO metadata VALUES (?, ?)').run(key, JSON.stringify(value))
   },
   list: async <T>(prefix: string) => (this.db.prepare('SELECT key, value FROM metadata WHERE substr(key,1,?) = ? ORDER BY key').all(prefix.length, prefix) as any[])
    .map(row => ({ key: row.key, value: JSON.parse(row.value) as T })),
  }
  if (this.private) {
   const grants = validateGrants(JSON.parse(readFileSync(process.env.JOURNEY_GRANTS_FILE!, 'utf8')))
   for (const grant of grants) {
    const old = this.db.prepare('SELECT value FROM metadata WHERE key = ?').get('grant:' + grant.credentialId)
    if (!old) this.db.prepare('INSERT INTO metadata VALUES (?, ?)').run('grant:' + grant.credentialId, JSON.stringify(grant))
   }
  }
 }
 async openRoom(id: string) {
  let entry = this.rooms.get(id)
  if (!entry) {
   const db = new DatabaseSync(join(this.roomsDir, id + '.db'))
   const room = new TLSocketRoom({ storage: new SQLiteSyncStorage({ sql: new NodeSqliteWrapper(db) }) })
   entry = { room, db }; this.rooms.set(id, entry)
  }
  this.db.prepare('INSERT OR IGNORE INTO metadata VALUES (?, ?)').run('room:' + id, JSON.stringify({ createdAt: Date.now() }))
  return entry.room
 }
 async document(id: string, method: string, prepared: any) { return operate(await this.openRoom(id), id, method, prepared) }
 async health() {
  return { rooms: this.private ? (await this.meta.list('room:')).map(e => e.key.slice(5)) : readdirSync(this.roomsDir).filter(f => f.endsWith('.db')).map(f => f.slice(0, -3)),
   active: [...this.rooms].map(([roomId, { room }]) => ({ roomId, sessions: room.getNumActiveSessions(), clock: room.getCurrentDocumentClock() })) }
 }
 capabilities(room: string) {
  return { assets: true, save: !this.private || !!process.env.JOURNEY_SAVE_DIR,
   repoDoc: !this.private || !!this.roomRepos[room]?.length }
 }
 async putAsset(room: string, id: string, bytes: Uint8Array, type: string) {
  if (!this.private) return storeAsset(id, Readable.from([bytes]), type)
  if (!await this.meta.get('room:' + room)) throw new HostError(404, 'room not found')
  const blobKey = crypto.randomUUID()
  await mkdir(join(this.root, 'assets'), { recursive: true })
  await writeFile(join(this.root, 'assets', blobKey), bytes)
  await this.meta.put('asset:' + room + ':' + id, { blobKey, contentType: type, size: bytes.length })
 }
 async getAsset(room: string, id: string) {
  if (!this.private) return loadAsset(id)
  const asset = await this.meta.get<{ blobKey: string; contentType: string }>('asset:' + room + ':' + id)
  if (!asset) throw new HostError(404, 'asset not found')
  return { data: await readFile(join(this.root, 'assets', asset.blobKey)), contentType: asset.contentType }
 }
 async save(_room: string, url: URL, method: string, body: any) {
  if (method === 'GET') { const name = url.searchParams.get('name'); return { dir: saveDir(), ...(name ? saveTarget(name) : {}) } }
  if (typeof body?.name !== 'string' || typeof body?.file !== 'string') throw new HostError(400, 'name and file are required')
  try { return await saveBoard(body.name, body.file) } catch (e) { throw new HostError(400, (e as Error).message) }
 }
 async repoDoc(room: string, url: URL) {
  const owner = url.searchParams.get('owner'), repo = url.searchParams.get('repo'), refPath = url.searchParams.get('refPath')
  if (!owner || !repo || !refPath) throw new HostError(400, 'owner, repo and refPath are required')
  if (this.private && !this.roomRepos[room]?.includes(owner + '/' + repo)) throw new HostError(403, 'checkout forbidden')
  return readRepoDoc(owner, repo, refPath)
 }
 track(socket: any, admission: Admission | null, room: string) {
  const timer = admission ? setTimeout(() => socket.close(1008, 'session expired'), Math.min(2 ** 31 - 1, admission.expiresAt - Date.now())) : undefined
  this.sockets.set(socket, { admission, room, timer })
  socket.on('close', () => { clearTimeout(timer); this.sockets.delete(socket) })
 }
 async revoke(credentialId: string) {
  const grant = await this.meta.get<Grant>('grant:' + credentialId)
  if (!grant) throw new Error('unknown credential')
  await this.meta.put('grant:' + credentialId, { ...grant, revoked: true })
  let closed = 0
  for (const [socket, entry] of this.sockets) if (entry.admission?.credentialId === credentialId) { socket.close(1008, 'credential revoked'); socket.terminate(); closed++ }
  const check = await this.meta.get<Grant>('grant:' + credentialId)
  if (!check?.revoked) throw new Error('partial revocation')
  return { revoked: true, closed }
 }
 async socketAllowed(admission: Admission | null, room: string) {
  if (!admission) return true
  try { return (await currentGrant(this.meta, admission)).rooms.includes(room) } catch { return false }
 }
 close() {
  for (const [socket, entry] of this.sockets) { clearTimeout(entry.timer); socket.terminate() }
  for (const { room, db } of this.rooms.values()) { room.close(); db.close() }
  this.db.close()
 }
}
