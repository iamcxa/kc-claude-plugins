import { useEffect, useRef, useState } from 'react'
import { TldrawUiDialogHeader, TldrawUiDialogTitle, TldrawUiDialogCloseButton, TldrawUiDialogBody } from 'tldraw'
import { journeyApi } from './api'
import './agent-sheet.css'
type Entry = { backendId: string; memberId: string; label: string }
type Scope = { roomId: string; assets: boolean; saveDirectory: string | null; repositories: string[] }
type Family = { id: string; label: string; installationId: string; memberId: string; scopes: Scope[]; revoked: boolean; streamsStopped?: string; operationId?: string; reason?: string }
type Consent = { id: string; consentId: string; label: string; installationId: string; backendId: string; authorizer: { id: string; label: string }; origin: string; scopes: Scope[]; expiresAt: number; status: string }
const errors: Record<string,string> = {
 authorizer_denied:'這不是你的配對請求，或配對碼不正確。',request_expired:'配對請求已到期，請在原安裝重新開始。',request_consumed:'配對請求已兌換，請更新代理清單。',request_denied:'此請求已拒絕，請在原安裝重新開始。',request_cancelled:'此請求已取消，請在原安裝重新開始。',
 verified_human_required:'請重新驗證原本的人類身分。',identity_changed:'身分已改變，請關閉並重新確認入口。',human_context_denied:'原本的身分或畫布權限已改變。',authority_denied:'目前成員或畫布權限已失效。',scope_changed:'請求的能力已改變，請取消後重新配對。',agent_rate_limited:'請求太頻繁，請稍後再試。',agent_pairing_disabled:'代理配對目前未啟用。',
}
function Scopes({ scopes }: { scopes: Scope[] }) {
 return <ul className="agent-scopes">{scopes.map(scope=><li key={scope.roomId}><strong>畫布：{scope.roomId}</strong><p>完整紀錄新增、修改、刪除與整份文件取代</p><p>素材讀寫：{scope.assets?'允許':'未配置'}</p><p>本機儲存目錄：{scope.saveDirectory||'未配置'}</p><p>可讀儲存庫文件：{scope.repositories.length?scope.repositories.join('、'):'未配置'}</p></li>)}</ul>
}
export function AgentSheet({ entry }: { entry: Entry }) {
 const [busy,setBusy]=useState(false),[problem,setProblem]=useState(''),[notice,setNotice]=useState('')
 const [code,setCode]=useState(''),[consent,setConsent]=useState<Consent|null>(null),[families,setFamilies]=useState<Family[]>([]),[confirmation,setConfirmation]=useState<string|null>(null),[pending,setPending]=useState<string[]>([])
 const consentCode=useRef('')
 async function post(operation: string,body: object) {
  const csrf=/(?:^|;\s*)journey_human_csrf=([^;]+)/.exec(document.cookie)?.[1]||''
  const response=await fetch(journeyApi('/agents/'+operation),{method:'POST',headers:{'Content-Type':'application/json','X-Journey-Entry':'1','X-Journey-Csrf':csrf},body:JSON.stringify({backendId:entry.backendId,...body})})
  const result=await response.json()
  if(!response.ok)throw new Error(result.category||'host_unavailable')
  return result
 }
 async function perform(action:()=>Promise<void>) {
  setBusy(true);setProblem('');setNotice('')
  try { await action() } catch(error) { const category=error instanceof Error?error.message:'';setProblem(errors[category]||'主機回覆未確認。請保留此頁，重新確認；不要推測操作已完成。') }
  finally { setBusy(false) }
 }
 async function inventory() {
  const result=await post('list',{});setFamilies(result.families)
  setPending(current=>current.filter(id=>!result.families.some((f:Family)=>f.id===id && f.revoked)))
 }
 useEffect(()=>{void perform(inventory)},[])
 const content=<div className="agent-sheet-body" aria-busy={busy}>
    <p>{entry.label} · 已驗證的人類 · {entry.memberId}</p><p>後端：{entry.backendId}</p>
    <p role="status">{busy?'正在確認目前權限…':problem||notice}</p>
    <h3>配對新的代理安裝</h3>
    <p>請在原安裝啟動配對。每個安裝分別核准與撤銷；安裝名稱由對方自行填寫。</p>
    <label htmlFor="agent-code">配對碼</label><input id="agent-code" value={code} autoComplete="off" spellCheck={false} onChange={event=>{setCode(event.target.value);setConsent(null)}}/>
    <button disabled={busy||!code.trim()} onClick={()=>void perform(async()=>{const result=await post('inspect',{code});consentCode.current=code;setConsent(result)})}>檢視配對請求</button>
    {consent&&<section aria-label="配對請求"><h3>{consent.label}</h3><p>自行填寫的名稱，未驗證模型身分。</p><p>安裝識別：{consent.installationId}</p><p>核准者：{consent.authorizer.label} · {consent.authorizer.id}</p><p>目的地：{consent.origin} · {consent.backendId}</p><p>請求於 {new Date(consent.expiresAt).toLocaleTimeString()} 到期（五分鐘）。</p><Scopes scopes={consent.scopes}/>
     {consent.status==='approved'?<p>已核准，等待原安裝兌換；尚未簽發安裝憑證。</p>:<><p>這些權限包含刪除及整份文件取代；核准不會簽發管理員權限。</p><div className="agent-actions"><button disabled={busy} onClick={()=>void perform(async()=>{await post('approve',{code:consentCode.current,consentId:consent.consentId});setConsent({...consent,status:'approved'})})}>核准這些畫布與能力</button><button className="secondary" disabled={busy} onClick={()=>void perform(async()=>{await post('deny',{code:consentCode.current,consentId:consent.consentId});setConsent(null);setNotice('已拒絕這次請求；既有安裝不受影響。')})}>拒絕這次請求</button></div></>}
    </section>}
    <h3>已核准的代理安裝</h3><p>短期存取十五分鐘，自動更新，沒有閒置到期。瀏覽器登出不會撤銷代理。</p>
    <button className="secondary" disabled={busy} onClick={()=>void perform(async()=>{await inventory();setConsent(null)})}>更新代理清單</button>
    {!busy&&!families.length&&<p>目前沒有代理安裝。</p>}
    {families.map(f=><section className="agent-family" key={f.id}><h3>{f.label}</h3><p>自行填寫的名稱 · 安裝 {f.installationId}</p><p>授權成員：{f.memberId}</p><p>授權家族：{f.id}</p><Scopes scopes={f.scopes}/>{f.revoked?<><p>新請求已拒絕；舊安裝不會復活。</p><p>{f.streamsStopped==='stopped'?'所有已登記連線已確認關閉。':f.streamsStopped==='stopping'?'正在停止既有連線；尚未確認全部關閉。':'既有連線停止結果未確認；請更新清單。'}</p><p>請回原安裝確認撤銷，再啟動全新配對。</p></>:pending.includes(f.id)?<p>撤銷待確認。此處未確認完成；請保留暫停狀態並更新清單。</p>:<><p>目前授權有效。安裝端若顯示更新或安全儲存結果不明，必須停止呼叫，只能確認舊授權撤銷後重新配對。</p>{confirmation===f.id?<><p>確認撤銷這個安裝的所有畫布權限？</p><div className="agent-actions"><button className="destructive" disabled={busy} onClick={()=>void perform(async()=>{setPending(current=>[...current,f.id]);await post('revoke',{familyId:f.id});await inventory();setConfirmation(null)})}>確認撤銷此安裝</button><button className="secondary" disabled={busy} onClick={()=>setConfirmation(null)}>取消撤銷</button></div></>:<button className="secondary" disabled={busy} onClick={()=>setConfirmation(f.id)}>撤銷此安裝</button>}</>}</section>)}
   </div>
 return <><TldrawUiDialogHeader className="journey-agent-header"><TldrawUiDialogTitle>我的 agent</TldrawUiDialogTitle><TldrawUiDialogCloseButton/></TldrawUiDialogHeader><TldrawUiDialogBody className="journey-private-dialog journey-native-agents">{content}</TldrawUiDialogBody></>
}
