import { createTLSchema, type TLRecord } from '@tldraw/tlschema'
export type DraftContext = { origin: string; backend: string; member: string; issuer: string; subject: string; generation: number; signInAt: number; revalidateBy: number; room: string }
export type Documents = Record<string, TLRecord>
export const canonical = (value: any): string => JSON.stringify(order(value))
function order(value: any): any {
 if (Array.isArray(value)) return value.map(order)
 if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(key => [key, order(value[key])]))
 return value
}
export async function fingerprint(value: unknown) {
 return [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonical(value))))].map(b => b.toString(16).padStart(2, '0')).join('')
}
export function validateDraftContext(c:DraftContext):DraftContext {
 const {origin,backend,member,issuer,subject,generation,signInAt,revalidateBy,room}=c
 if([backend,member,room].some(v=>typeof v!=='string'||!/^[a-zA-Z0-9_-]{1,128}$/.test(v)) || [issuer,subject].some(v=>typeof v!=='string'||!v||v.length>2048) || new URL(origin).origin!==origin || (typeof window!=='undefined'&&origin!==window.location.origin) || !Number.isSafeInteger(generation)||generation<1 || !Number.isSafeInteger(signInAt)||!Number.isSafeInteger(revalidateBy)||revalidateBy<=signInAt||revalidateBy>signInAt+1209600000)throw new Error('draft_context_invalid')
 return {origin,backend,member,issuer,subject,generation,signInAt,revalidateBy,room}
}
export const samePerson = (a: DraftContext, b: DraftContext) => ['origin', 'backend', 'member', 'issuer', 'subject'].every(key => a[key as keyof DraftContext] === b[key as keyof DraftContext])
export const sameMount = (a: DraftContext, b: DraftContext) => samePerson(a,b) && a.room === b.room && a.signInAt === b.signInAt && a.generation === b.generation
const schema = createTLSchema()
export function validateDocuments(value: unknown): Documents {
 if (!value || typeof value !== 'object' || Array.isArray(value) || new TextEncoder().encode(JSON.stringify(value)).length > 5_000_000) throw new Error('draft_payload_invalid_or_too_large')
 const entries = Object.entries(value)
 if (entries.length > 20_000) throw new Error('draft_payload_too_large')
 for (const [id, record] of entries as Array<[string, TLRecord]>) {
  if (!record || record.id !== id || (schema.types as any)[record.typeName]?.scope!=='document') throw new Error('draft_document_records_only')
  const type = schema.types[record.typeName] as any
  if (!type) throw new Error('draft_record_invalid')
  type.validate(record)
 }
 return structuredClone(value) as Documents
}
export const changes = (base: Documents, draft: Documents) => ({
 put: Object.values(draft).filter(record => canonical(base[record.id]) !== canonical(record)),
 remove: Object.keys(base).filter(id => !draft[id]).sort(),
})
export const matchesChanges = (current: Documents, patch: ReturnType<typeof changes>) => patch.put.every(record => canonical(current[record.id]) === canonical(record)) && patch.remove.every(id => !current[id])
