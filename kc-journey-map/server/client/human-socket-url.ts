import type { useSync } from '@tldraw/sync'
export type HumanSocketParams=Parameters<NonNullable<Parameters<typeof useSync>[0]['connect']>>[0]
export function humanSocketUrl(uri:string,params:HumanSocketParams) {
 const url=new URL(uri)
 for(const key of ['sessionId','storeId'] as const){
  if(url.searchParams.has(key))throw new Error(`useSync. "${key}" is a reserved query param name. Please use a different name`)
  url.searchParams.set(key,params[key])
 }
 return url.toString()
}
