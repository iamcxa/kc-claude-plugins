import { createTLSchema } from '@tldraw/tlschema'
import type { TLSocketRoom } from '@tldraw/sync-core'

export class HostError extends Error {
 constructor(public status: number, message: string, public details: object = {}) { super(message) }
}
export const canonicalRoom = (id: string) => id.replace(/[^a-zA-Z0-9_-]/g, '_')
export const canonicalAsset = (id: string) => id.replace(/[^a-zA-Z0-9._-]/g, '_')
const schema = createTLSchema()
export function validateRecord(record: any): string | null {
 if (!record || typeof record !== 'object') return 'record is not an object'
 const { id, typeName } = record
 if (typeof id !== 'string') return 'record.id must be a string'
 if (typeof typeName !== 'string') return `record ${id} has no typeName`
 const type = (schema.types as Record<string, any>)[typeName]
 if (!type) return `record ${id} has unknown typeName "${typeName}"`
 try { type.validate(record); return null }
 catch (e) { return `record ${id} failed validation: ${(e as Error).message}` }
}
export function prepareDoc(method: string, body: any) {
 if (method === 'GET') return null
 if (method === 'PATCH') {
  const put = body?.put ?? [], remove = body?.remove ?? []
  if (!Array.isArray(put) || !Array.isArray(remove)) throw new HostError(400, 'put and remove must be arrays')
  const errors = put.map(validateRecord).filter(Boolean)
  if (errors.length) throw new HostError(400, 'validation failed', { errors })
  return { put, remove }
 }
 const snapshot = body?.snapshot ?? body
 if (!snapshot?.documents && !snapshot?.store) throw new HostError(400, 'body must be a RoomSnapshot or TLStoreSnapshot')
 return snapshot
}
export async function operate(room: TLSocketRoom<any, any>, roomId: string, method: string, prepared: any) {
 if (method === 'GET') return { roomId, snapshot: room.getCurrentSnapshot() }
 if (method === 'PATCH') {
  await room.updateStore(store => {
   for (const record of prepared.put) store.put(record)
   for (const id of prepared.remove) store.delete(id)
  })
  return { roomId, put: prepared.put.length, removed: prepared.remove.length, clock: room.getCurrentDocumentClock() }
 }
 room.loadSnapshot(prepared)
 return { roomId, clock: room.getCurrentDocumentClock() }
}
