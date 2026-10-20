import { HostError } from './core'
import type { Admission } from './policy'
import type { Host } from './transport'
export async function audited<T>(host: Host, admission: Admission | null, room: string, action: string, effect: () => Promise<T>, operationId?: string, outcome:'committed'|'admitted'='committed'): Promise<T> {
 if(!host.private || !host.meta.security)return effect()
 if(operationId && !/^[a-zA-Z0-9_-]{1,128}$/.test(operationId))throw new HostError(400,'invalid_operation_id')
 const reserved=await host.meta.security('reserve',{action,actor:admission,room,operationId})
 let value:T
 try {value=await effect()}
 catch(error){try {await host.meta.security('finalize',{operationId:reserved.operationId,outcome:'unknown'})}catch{}throw error}
 try {await host.meta.security('finalize',{operationId:reserved.operationId,outcome})}
 catch {throw new HostError(503,'mutation_receipt_pending',{category:'mutation_receipt_pending',operationId:reserved.operationId,outcome:outcome+'_receipt_pending',retry:false})}
 return value
}
