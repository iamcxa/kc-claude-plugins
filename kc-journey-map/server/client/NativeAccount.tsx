import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from 'react'
import { DefaultMainMenu, DefaultMainMenuContent, TldrawUiMenuGroup, TldrawUiMenuItem, TldrawUiButton, TldrawUiButtonLabel, TldrawUiDialogHeader, TldrawUiDialogTitle, TldrawUiDialogCloseButton, TldrawUiDialogBody, TldrawUiDialogFooter, useDialogs, useEditor, type TLUiDialogProps } from 'tldraw'
import { journeyFetch, journeyApi, type HumanContext } from './api'
import type { HumanCanvasEntry } from './HumanEntry'
import './native-account.css'
import { confirmRoomSwitch } from './confirm-room-switch'
type Account = {backendId:string;memberId:string;roomId:string;label:string}
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
function useReturnFocus() {
 const editor=useEditor(),dialogs=useDialogs()
 return ()=>requestAnimationFrame(()=>requestAnimationFrame(()=>{
  if(!dialogs.dialogs.get().length)editor.getContainer().querySelector<HTMLElement>('[data-testid="main-menu.button"]')?.focus()
 }))
}
function Header({title,closable=true}:{title:string;closable?:boolean}) {return <TldrawUiDialogHeader><TldrawUiDialogTitle>{title}</TldrawUiDialogTitle>{closable&&<TldrawUiDialogCloseButton/>}</TldrawUiDialogHeader>}
function Logout({session,onClose}:TLUiDialogProps&{session:NativeSession}) {
 const editor=useEditor(),pending=useRef(false),[busy,setBusy]=useState(false),[problem,setProblem]=useState('')
 useEffect(()=>{if(!busy)return;const prevent=(event:KeyboardEvent)=>{if(event.key==='Escape'){event.preventDefault();event.stopPropagation()}};document.addEventListener('keydown',prevent,true);return()=>document.removeEventListener('keydown',prevent,true)},[busy])
 const confirm=async()=>{
  if(pending.current || !session.context)return
  pending.current=true;setBusy(true);setProblem('')
  editor.updateInstanceState({isReadonly:true})
  try {
   if(!await confirmRoomSwitch(editor,session.context.room))throw new Error('unconfirmed edits')
   await session.entry.signOut(session.context)
  }catch{editor.updateInstanceState({isReadonly:session.paused});setProblem('目前修改未確認同步；登出已停止，請保留目前工作並重試。');pending.current=false;setBusy(false)}
 }
 return <><Header title="登出目前帳號？" closable={!busy}/><TldrawUiDialogBody className="journey-private-dialog">
  <p>登出會關閉這個應用程式的私密畫布。其他同一登入的分頁會停止連線，保留目前畫面供你另存。</p><p>先確認目前修改已同步；未確認就留在畫布。本版本尚無本機草稿恢復。</p><p>這不會登出 Cloudflare 的全域身分服務；重新進入可能沿用仍有效的驗證，原始登入期限不會重設。</p>
  <p role="status">{busy?'正在確認同步並結束登入…':problem}</p>
 </TldrawUiDialogBody><TldrawUiDialogFooter><TldrawUiButton type="normal" disabled={busy} onClick={onClose}><TldrawUiButtonLabel>取消</TldrawUiButtonLabel></TldrawUiButton><TldrawUiButton type="danger" disabled={busy} onClick={()=>void confirm()}><TldrawUiButtonLabel>確認登出</TldrawUiButtonLabel></TldrawUiButton></TldrawUiDialogFooter></>
}
function AccountDialog({onClose}:TLUiDialogProps) {
 const {session,account,problem}=useAccount(),dialogs=useDialogs(),returnFocus=useReturnFocus()
 if(!session?.context)return null
 const context=session.context
 return <><Header title="我的帳號"/><TldrawUiDialogBody className="journey-private-dialog">
  <p>{account?.label||session.entry.label} · {session.paused?'先前驗證身分，存取已暫停':'已驗證的人類'}</p><p>{context.member}</p><p>目前房間：{context.room}</p><p role="status">{problem||(!account?'正在確認目前權限…':'目前權限已確認')}</p>
 </TldrawUiDialogBody><TldrawUiDialogFooter><TldrawUiButton type="normal" onClick={()=>{onClose();dialogs.addDialog({id:'journey-logout',onClose:returnFocus,preventBackgroundClose:true,component:props=><Logout {...props} session={session}/>})}}><TldrawUiButtonLabel>登出</TldrawUiButtonLabel></TldrawUiButton></TldrawUiDialogFooter></>
}
export function NativeMainMenu() {
 const session=useContext(NativeContext),dialogs=useDialogs(),returnFocus=useReturnFocus()
 if(!session?.entry.nativeAccount || !session.context)return <DefaultMainMenu/>
 return <DefaultMainMenu><TldrawUiMenuGroup id="journey-private">
  <TldrawUiMenuItem id="journey-account" label="我的帳號" readonlyOk onSelect={()=>{dialogs.addDialog({id:'journey-account',onClose:returnFocus,component:AccountDialog})}}/>
 </TldrawUiMenuGroup><DefaultMainMenuContent/></DefaultMainMenu>
}
