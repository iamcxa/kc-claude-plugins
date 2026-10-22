import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from 'react'
import { DefaultMainMenu, DefaultMainMenuContent, TldrawUiMenuGroup, TldrawUiMenuItem, TldrawUiDropdownMenuGroup, TldrawUiDropdownMenuItem, TldrawUiButton, TldrawUiButtonLabel, TldrawUiDialogHeader, TldrawUiDialogTitle, TldrawUiDialogCloseButton, TldrawUiDialogBody, TldrawUiDialogFooter, useDialogs, useEditor, type TLUiDialogProps } from 'tldraw'
import { journeyFetch, journeyApi, type HumanContext } from './api'
import { AgentSheet } from './AgentSheet'
import type { HumanCanvasEntry } from './HumanEntry'
import './native-account.css'
type Account = {backendId:string;memberId:string;roomId:string;owner:boolean;grant:{expiresAt:number}}
type NativeSession = {entry:HumanCanvasEntry;context:HumanContext|null;paused:boolean}
const NativeContext=createContext<NativeSession|null>(null)
export const NativeAccountProvider=({children,...session}:NativeSession&{children:ReactNode})=><NativeContext.Provider value={session}>{children}</NativeContext.Provider>
function useAccount() {
 const session=useContext(NativeContext),[account,setAccount]=useState<Account|null>(null),[problem,setProblem]=useState('')
 const context=session?.context
 useEffect(()=>{
  setAccount(null);setProblem('')
  if(!session?.entry.nativeAccount || !context || session.paused)return
  const controller=new AbortController()
  journeyFetch(journeyApi('/auth/account',context),{signal:controller.signal}).then(async response=>{
   if(!response.ok)throw new Error()
   const value=await response.json()
   if(value.backendId!==context.backend || value.memberId!==context.member || value.roomId!==context.room)throw new Error()
   if(!controller.signal.aborted)setAccount(value)
  }).catch(()=>{if(!controller.signal.aborted)setProblem('目前帳號權限未確認，請重新確認入口。')})
  return()=>controller.abort()
 },[context?.backend,context?.member,context?.room,context?.signInAt,session?.paused,session?.entry.nativeAccount])
 return {session,account,problem}
}
function Header({title,closable=true}:{title:string;closable?:boolean}) {return <TldrawUiDialogHeader><TldrawUiDialogTitle>{title}</TldrawUiDialogTitle>{closable&&<TldrawUiDialogCloseButton/>}</TldrawUiDialogHeader>}
function RoomAccess({context,onClose}:TLUiDialogProps&{context:HumanContext}) {
 const [result,setResult]=useState<any>(null),[failed,setFailed]=useState(false)
 useEffect(()=>{
  const controller=new AbortController()
  journeyFetch(journeyApi('/auth/room-members',context),{signal:controller.signal}).then(async response=>{
   if(!response.ok)throw new Error()
   const value=await response.json()
   if(value.backendId!==context.backend || value.memberId!==context.member || value.roomId!==context.room || !Array.isArray(value.members))throw new Error()
   if(!controller.signal.aborted)setResult(value)
  }).catch(()=>{if(!controller.signal.aborted)setFailed(true)})
  return()=>controller.abort()
 },[context])
 return <><Header title="目前房間成員與存取"/><TldrawUiDialogBody className="journey-private-dialog">
  <p>目前房間：{context.room}</p><p>目前可查看成員；邀請與移除尚未提供</p>
  {failed?<p role="status">成員權限未確認，已停止讀取。請關閉後重新確認。</p>:!result?<p role="status">正在讀取目前房間…</p>:<ul>{result.members.map((member:any)=><li key={member.memberId}><strong>{member.label}</strong><p>{member.memberId} · {member.owner?'擁有者':'普通成員'} · {member.status==='allowed'?'可存取':member.status==='revoked'?'已撤銷':member.status==='expired'?'已到期':'已停用'}</p><p>授權期限：{new Date(member.expiresAt).toLocaleString()}</p></li>)}</ul>}
 </TldrawUiDialogBody><TldrawUiDialogFooter><TldrawUiButton type="normal" onClick={onClose}><TldrawUiButtonLabel>關閉</TldrawUiButtonLabel></TldrawUiButton></TldrawUiDialogFooter></>
}
function Logout({session,onClose}:TLUiDialogProps&{session:NativeSession}) {
 const editor=useEditor(),pending=useRef(false),[busy,setBusy]=useState(false),[problem,setProblem]=useState('')
 useEffect(()=>{if(!busy)return;const prevent=(event:KeyboardEvent)=>{if(event.key==='Escape'){event.preventDefault();event.stopPropagation()}};document.addEventListener('keydown',prevent,true);return()=>document.removeEventListener('keydown',prevent,true)},[busy])
 const confirm=async()=>{
  if(pending.current || !session.context)return
  pending.current=true;setBusy(true);setProblem('')
  editor.updateInstanceState({isReadonly:true})
  try {
   const saves:Promise<void>[]=[]
   window.dispatchEvent(new CustomEvent('journey-before-logout',{detail:saves}))
   await Promise.all(saves)
   await session.entry.signOut(session.context)
  }catch{editor.updateInstanceState({isReadonly:session.paused});setProblem('本機草稿未確認保存；登出已停止。請保留目前工作。');pending.current=false;setBusy(false)}
 }
 return <><Header title="登出目前帳號？" closable={!busy}/><TldrawUiDialogBody className="journey-private-dialog">
  <p>登出會關閉這個應用程式的私密畫布。其他同一登入的畫布分頁也會停止。</p><p>先保存本機草稿；草稿保留，重新登入後仍須明確恢復。代理授權保留。</p><p>這不會登出 Cloudflare 的全域身分服務；重新進入可能沿用仍有效的驗證，原始登入期限不會重設。</p>
  <p role="status">{busy?'正在保存草稿並結束登入…':problem}</p>
 </TldrawUiDialogBody><TldrawUiDialogFooter><TldrawUiButton type="normal" disabled={busy} onClick={onClose}><TldrawUiButtonLabel>取消</TldrawUiButtonLabel></TldrawUiButton><TldrawUiButton type="danger" disabled={busy} onClick={()=>void confirm()}><TldrawUiButtonLabel>確認登出</TldrawUiButtonLabel></TldrawUiButton></TldrawUiDialogFooter></>
}
function AccountDialog({onClose}:TLUiDialogProps) {
 const {session,account,problem}=useAccount(),dialogs=useDialogs()
 if(!session?.context)return null
 const context=session.context
 return <><Header title="我的帳號"/><TldrawUiDialogBody className="journey-private-dialog">
  <p>{session.entry.label} · 已驗證的人類</p><p>{context.member}</p><p>目前房間：{context.room}</p><p role="status">{problem||(!account?'正在確認目前權限…':account.owner?'擁有者':'普通成員')}</p>
  {account?.owner&&<TldrawUiButton type="normal" onClick={()=>{onClose();dialogs.addDialog({id:'journey-room-access',component:props=><RoomAccess {...props} context={context}/>})}}><TldrawUiButtonLabel>管理目前房間成員</TldrawUiButtonLabel></TldrawUiButton>}
  <TldrawUiButton type="normal" disabled={session.paused} onClick={()=>{onClose();dialogs.addDialog({id:'journey-own-agents',component:props=><AgentSheet native entry={{backendId:context.backend,memberId:context.member,label:session.entry.label}} onClose={props.onClose}/>})}}><TldrawUiButtonLabel>本人代理</TldrawUiButtonLabel></TldrawUiButton>
 </TldrawUiDialogBody><TldrawUiDialogFooter><TldrawUiButton type="normal" onClick={()=>{onClose();dialogs.addDialog({id:'journey-logout',preventBackgroundClose:true,component:props=><Logout {...props} session={session}/>})}}><TldrawUiButtonLabel>登出</TldrawUiButtonLabel></TldrawUiButton></TldrawUiDialogFooter></>
}
export function NativeMainMenu() {
 const session=useContext(NativeContext),dialogs=useDialogs()
 if(!session?.entry.nativeAccount || !session.context)return <DefaultMainMenu/>
 return <DefaultMainMenu><TldrawUiMenuGroup id="journey-private">
  <TldrawUiMenuItem id="journey-account" label="我的帳號" readonlyOk onSelect={()=>{dialogs.addDialog({id:'journey-account',component:AccountDialog})}}/>
  <TldrawUiMenuItem id="journey-drafts" label="本機草稿" readonlyOk onSelect={()=>{window.dispatchEvent(new Event('journey-open-drafts'))}}/>
 </TldrawUiMenuGroup><DefaultMainMenuContent/></DefaultMainMenu>
}
export function NativeRoomAccessItem({close}:{close:()=>void}) {
 const {session,account}=useAccount(),dialogs=useDialogs()
 if(!account?.owner || !session?.context || session.paused)return null
 const context=session.context
 return <TldrawUiDropdownMenuGroup><TldrawUiDropdownMenuItem><TldrawUiButton type="menu" onClick={()=>{close();dialogs.addDialog({id:'journey-room-access',component:props=><RoomAccess {...props} context={context}/>})}}><TldrawUiButtonLabel>管理目前房間成員</TldrawUiButtonLabel></TldrawUiButton></TldrawUiDropdownMenuItem></TldrawUiDropdownMenuGroup>
}
