import { useEffect, useMemo, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { createTLStore, Tldraw, type Editor } from 'tldraw'
import { useSync } from '@tldraw/sync'
import { journeyApi } from './api'
import { canonical, matchesChanges, sameMount, type DraftContext, type Documents } from '../draft-data'
import { humanDrafts, type ApplyAttempt, type VersionItem } from './human-drafts'
import { applyDraft, currentDocuments, humanCookieMarker, reconcileDraft, reviewDraft, verifiedDraftContext, type DraftReview, type SyncConfirmation } from './draft-recovery'
import { humanSocket, type HumanSocketParams } from './human-socket'
import './human-drafts.css'
type Probe = { id:string; context:DraftContext; patch:DraftReview['patch']; signal:AbortSignal; resolve:()=>void; reject:(error:Error)=>void }
const text:Record<string,string>={draft_identity_changed:'身分已改變。草稿保持鎖定；請以原本身分重新登入。',draft_cloud_changed_review_again:'雲端已改變。請重新檢視後再確認。',draft_base_unknown:'原始雲端版本不明；保留草稿，無法安全計算變更。',draft_attempt_requires_reconciliation:'已有未確認的操作；請核對原操作，不能再次送出。',draft_original_outcome_unknown:'原操作結果仍未確認；草稿保留，不會自動重送。',draft_readback_unconfirmed:'雲端紀錄尚未核對成功；草稿保留。',draft_upgrade_blocked:'本機資料庫升級被其他分頁阻擋；關閉舊分頁後重試。',strict_durability_unsupported:'此瀏覽器不支援嚴格本機儲存；目前未儲存。',draft_apply_in_progress:'此版本有進行中的操作；請等候或核對原操作。'}
const errorText=(error:unknown)=>{const name=error instanceof Error?error.message:'';return text[name]||'結果未確認或儲存失敗。保留目前工作與草稿，請重新確認；不要推測已完成。'}
function SyncProbe({probe}:{probe:Probe}) {
 const connect=useMemo(()=>(params:HumanSocketParams)=>humanSocket(journeyApi('/connect/'+encodeURIComponent(probe.context.room),probe.context),probe.context,()=>probe.reject(new Error('draft_sync_paused')),params),[probe])
 const assets=useMemo(()=>({upload:async()=>{throw new Error('probe_has_no_upload')},resolve:()=>null}),[])
 const value=useSync({connect,assets})
 useEffect(()=>{
  const timer=setTimeout(()=>probe.reject(new Error('draft_sync_unconfirmed')),8000),abort=()=>probe.reject(new Error('draft_sync_aborted'))
  probe.signal.addEventListener('abort',abort)
  return()=>{clearTimeout(timer);probe.signal.removeEventListener('abort',abort)}
 },[probe])
 useEffect(()=>{
  if(value.status==='error'){probe.reject(value.error);return}
  if(value.status!=='synced-remote'||value.connectionStatus!=='online')return
  const check=()=>{if(matchesChanges(value.store.getStoreSnapshot('document').store as Documents,probe.patch))probe.resolve()}
  check();return value.store.listen(check,{scope:'document'})
 },[value,probe])
 return null
}
function DraftPreview({review}:{review:DraftReview}) {
 const store=useMemo(()=>{const value=createTLStore();value.put(Object.values(review.version.records));return value},[review.version])
 return <div className="human-draft-preview" data-testid="detached-draft"><Tldraw store={{status:'not-synced',store}} hideUi onMount={editor=>{editor.updateInstanceState({isReadonly:true})}}/></div>
}
export function HumanDraftPanel({context,label,editor,connection,onPause}:{context:DraftContext;label:string;editor:Editor|null;connection:string;onPause:()=>void}) {
 const [open,setOpen]=useState(false),[status,setStatus]=useState('尚無本機儲存'),[persistent,setPersistent]=useState(''),[problem,setProblem]=useState(''),[busy,setBusy]=useState(false),[items,setItems]=useState<VersionItem[]>([]),[allowed,setAllowed]=useState(false),[review,setReview]=useState<DraftReview|null>(null),[attempt,setAttempt]=useState<ApplyAttempt|null>(null),[deleting,setDeleting]=useState<VersionItem|null>(null),[probe,setProbe]=useState<Probe|null>(null),[theme,setTheme]=useState('light')
 const lineage=useRef({tabId:crypto.randomUUID(),draftId:crypto.randomUUID()}),dialog=useRef<HTMLDialogElement>(null),trigger=useRef<HTMLButtonElement>(null),operation=useRef(new AbortController()),epoch=useRef(0),alive=useRef(true)
 useEffect(()=>{
  alive.current=true
  document.body.classList.add('human-drafts-active')
  let active=true
  if(navigator.storage?.persist)void navigator.storage.persist().then(value=>{if(active)setPersistent(value?'已取得持續儲存許可；瀏覽器清除仍會遺失資料。':'未取得持續儲存許可；瀏覽器可能清除本機草稿。')}).catch(()=>{if(active)setPersistent('持續儲存許可未確認；瀏覽器可能清除本機草稿。')})
  else setPersistent('此瀏覽器無持續儲存許可；清除或私密模式可能遺失草稿。')
  const change=()=>{epoch.current++;operation.current.abort();setReview(null);setItems([]);setAllowed(false);setAttempt(null);setDeleting(null);setBusy(false);setProblem(text.draft_identity_changed);onPause()}
  const channel=new BroadcastChannel('journey-human-authority');channel.onmessage=change
  const update=()=>setTheme(document.querySelector('.tl-theme__dark')?'dark':'light')
  const observer=new MutationObserver(update);observer.observe(document.body,{subtree:true,attributes:true,attributeFilter:['class']});update()
  return()=>{active=false;alive.current=false;epoch.current++;operation.current.abort();channel.close();observer.disconnect();document.body.classList.remove('human-drafts-active')}
 },[])
 useEffect(()=>{
  if(!editor)return
  let timer:ReturnType<typeof setTimeout>|undefined,pending:Documents|null=null,queue=Promise.resolve()
  const base=verifiedDraftContext(context).then(current=>{if(!sameMount(current,context))throw new Error('draft_identity_changed');return currentDocuments(context)}).catch(()=>null)
  const flush=()=>{
   if(!pending)return
   const records=pending;pending=null
   if(alive.current)setStatus('正在儲存本機版本…')
   queue=queue.then(async()=>{const db=await humanDrafts();const version=await db.save(context,lineage.current.draftId,lineage.current.tabId,await base,records);if(alive.current)setStatus('已儲存本機 v'+version.key[5])}).catch(error=>{if(alive.current){setStatus('未儲存本機版本');setProblem(errorText(error))}})
  }
  const stop=editor.store.listen(()=>{pending=structuredClone(editor.store.getStoreSnapshot('document').store) as Documents;clearTimeout(timer);timer=setTimeout(flush,200)},{scope:'document',source:'user'})
  return()=>{stop();clearTimeout(timer);flush()}
 },[editor])
 async function inventory(signal:AbortSignal) {
  const current=await verifiedDraftContext(context,false,signal)
  let permitted=false
  try{await verifiedDraftContext(context,true,signal);permitted=true}catch(error){if(signal.aborted)throw error}
  const versions=await (await humanDrafts()).inventory(current)
  signal.throwIfAborted();setAllowed(permitted);setItems(versions)
  if(!permitted)setProblem('目前畫布權限未確認。內容保持鎖定；原身分可明確刪除指定本機版本。')
 }
 async function run(action:(signal:AbortSignal)=>Promise<void>) {
  operation.current.abort();operation.current=new AbortController();const id=++epoch.current,signal=AbortSignal.any([operation.current.signal,AbortSignal.timeout(30_000)])
  setBusy(true);setProblem('')
  try{await action(signal)}catch(error){if(id===epoch.current){setReview(null);setAttempt(null);setItems([]);setAllowed(false);setProblem(errorText(error))}}
  finally{if(id===epoch.current)setBusy(false)}
 }
 useEffect(()=>{
  if(!open)return
  dialog.current?.showModal();dialog.current?.querySelector<HTMLElement>('h2')?.focus()
  void run(inventory)
  return()=>{operation.current.abort();epoch.current++;dialog.current?.close();trigger.current?.focus()}
 },[open])
 const confirmSync:SyncConfirmation=(current,patch,signal)=>new Promise((resolve,reject)=>{const id=crypto.randomUUID();let settled=false;const clear=(error?:Error)=>{if(settled)return;settled=true;setProbe(value=>value?.id===id?null:value);if(error)reject(error);else resolve()};setProbe({id,context:current,patch,signal,resolve:()=>clear(),reject:error=>clear(error)})})
 const close=()=>{operation.current.abort();epoch.current++;setBusy(false);setOpen(false);setReview(null);setAttempt(null);setDeleting(null)}
 return <>
  <div className="human-draft-bar" data-theme={theme}><span role="status">{label} · {status} · 雲端{connection==='connected'?'已連線':'未連線或已暫停'}</span><button ref={trigger} onClick={()=>setOpen(true)}>本機草稿</button></div>
  {probe&&<SyncProbe key={probe.id} probe={probe}/>}
  {open&&createPortal(<dialog ref={dialog} className="human-draft-dialog" data-theme={theme} aria-labelledby="human-draft-title" onCancel={event=>{event.preventDefault();close()}}>
   <header><h2 id="human-draft-title" tabIndex={-1}>本機草稿</h2><button aria-label="關閉本機草稿" onClick={close}>×</button></header>
   <div className="human-draft-body" aria-busy={busy}>
    <p>畫布：{context.room} · 僅此瀏覽器來源與使用者設定檔</p><p>{persistent}</p><p>本機版本沒有自動到期。登出或失去權限不會刪除；恢復需要明確確認。</p>
    <p role="status">{busy?'正在確認身分、權限與結果…':problem}</p>
    <button className="secondary" disabled={busy} onClick={()=>void run(async signal=>{setReview(null);setAttempt(null);setDeleting(null);await inventory(signal)})}>重新確認草稿</button>
    {!busy&&!items.length&&<p>沒有可列出的本機版本；其他身分的草稿不會顯示。</p>}
    {items.map(item=><section key={JSON.stringify(item.key)}><h3>版本 {item.key[5]} · 分頁 {item.key[4].slice(0,8)}</h3><p>保留在本機，尚未經本流程確認恢復。</p><div className="human-draft-actions">
     <button disabled={busy||!allowed} onClick={()=>void run(async signal=>{setReview(null);setAttempt(null);const db=await humanDrafts(),selected=await reviewDraft(db,context,item.key,signal);const prior=await db.attempts(item.key);signal.throwIfAborted();onPause();setReview(selected);setAttempt(prior.at(-1)||null)})}>檢視此版本</button>
     <button className="secondary" disabled={busy} onClick={()=>{setReview(null);setAttempt(null);setDeleting(item)}}>刪除此版本</button>
    </div></section>)}
    {deleting&&<section aria-label="確認刪除本機版本"><h3>刪除版本 {deleting.key[5]}？</h3><p>只刪除選定的本機版本，不會回復雲端、取消已送出的操作或清除其他版本。</p><div className="human-draft-actions"><button className="destructive" disabled={busy} onClick={()=>void run(async signal=>{const marker=humanCookieMarker(),identity=await verifiedDraftContext(context,false,signal);signal.throwIfAborted();await(await humanDrafts()).remove(identity,deleting.key,undefined,()=>!signal.aborted&&humanCookieMarker()===marker);setDeleting(null);setStatus('已刪除指定本機版本');await inventory(signal)})}>確認刪除此版本</button><button className="secondary" disabled={busy} onClick={()=>setDeleting(null)}>取消刪除</button></div></section>}
    {review&&<section aria-label="檢視選定草稿"><h3>選定版本 {review.version.key[5]} · 畫布 {context.room}</h3><p>未連線的草稿預覽。下列完整紀錄會新增或取代；其他紀錄保留。確認後的並發修改仍遵循原本完整紀錄覆寫規則。</p><DraftPreview review={review}/>
     <details><summary>檢視原始、草稿、目前雲端與精確變更</summary><pre>{canonical({base:review.version.base,draft:review.version.records,current:review.current,put:review.patch.put,remove:review.patch.remove})}</pre></details>
     <p>將送出 {review.patch.put.length} 筆完整紀錄，刪除 {review.patch.remove.length} 筆。</p>
     {attempt?<><p>原操作 {attempt.id} 的結果需要核對。草稿保留，不會自動重送。</p><button disabled={busy} onClick={()=>void run(async signal=>{await reconcileDraft(await humanDrafts(),context,attempt,confirmSync,signal);setReview(null);setAttempt(null);setStatus('原操作、雲端紀錄及同步已核對；僅清除選定版本');await inventory(signal)})}>核對原操作，不重送</button></>:<button disabled={busy} onClick={()=>void run(async signal=>{await applyDraft(await humanDrafts(),review,lineage.current.tabId,confirmSync,signal);setReview(null);setStatus('恢復與雲端同步已核對；僅清除選定版本');await inventory(signal)})}>確認套用這些變更</button>}
     <button className="secondary" disabled={busy} onClick={()=>{setReview(null);setAttempt(null)}}>暫不恢復，保留草稿</button>
    </section>}
    <a href={window.location.href} target="_blank" rel="noopener noreferrer">另開畫布並重新驗證</a>
   </div>
  </dialog>,document.body)}
 </>
}
