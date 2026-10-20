import * as SyncCore from '@tldraw/sync-core'
import type { useSync } from '@tldraw/sync'
type Socket=ReturnType<NonNullable<Parameters<typeof useSync>[0]['connect']>>
const {ClientWebSocketAdapter}=SyncCore as unknown as {ClientWebSocketAdapter:new(uri:()=>Promise<string>)=>Socket}
import { sameMount, type DraftContext } from '../draft-data'
import { verifiedDraftContext } from './draft-recovery'
import { humanSocketUrl, type HumanSocketParams } from './human-socket-url'
export type { HumanSocketParams } from './human-socket-url'
const marker=()=>document.cookie.split(';').map(s=>s.trim()).find(s=>s.startsWith('journey_human_csrf='))||''
export function humanSocket(uri:string,context:DraftContext,onPause:()=>void,params:HumanSocketParams) {
 const socketUri=humanSocketUrl(uri,params)
 let closed=false,everOnline=false,queue=Promise.resolve()
 const initial=marker(),controller=new AbortController()
 const stop=()=>{if(closed)return;closed=true;controller.abort();socket.close();onPause()}
 const verify=async()=>{
  if(closed || marker()!==initial)throw new Error('draft_identity_changed')
  const current=await verifiedDraftContext(context,true,controller.signal)
  if(closed || marker()!==initial || !sameMount(current,context))throw new Error('draft_identity_changed')
 }
 const socket=new ClientWebSocketAdapter(async()=>{try{await verify();if(everOnline)throw new Error('explicit_resume_required');return socketUri}catch{stop();return socketUri}})
 const status=socket.onStatusChange(event=>{if(event.status==='online')everOnline=true;else stop()})
 const channel=typeof BroadcastChannel!=='undefined'?new BroadcastChannel('journey-human-authority'):null
 if(channel)channel.onmessage=stop
 window.addEventListener('offline',stop)
 return {
  get connectionStatus(){return closed?'error' as const:socket.connectionStatus},
  onReceiveMessage(listener:Parameters<Socket['onReceiveMessage']>[0]) {
   return socket.onReceiveMessage(message=>{queue=queue.then(async()=>{await verify();if(!closed)listener(message)}).catch(stop)})
  },
  onStatusChange:socket.onStatusChange.bind(socket),
  sendMessage(message:Parameters<Socket['sendMessage']>[0]) {
   queue=queue.then(async()=>{await verify();if(!closed)socket.sendMessage(message)}).catch(stop)
  },
  restart(){stop()},
  close(){closed=true;controller.abort();status();channel?.close();window.removeEventListener('offline',stop);socket.close()},
 }
}
