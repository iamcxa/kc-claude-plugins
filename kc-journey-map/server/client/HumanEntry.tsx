import { useEffect, useRef, useState, type ReactNode } from 'react'
import { journeyApi, setHumanContext } from './api'
import './human-entry.css'
type Entry = { backendId: string; memberId: string; label: string; rooms: string[]; room: string | null; expiresAt: number; verifiedHumanSignInAt: number; status: string }
const secret = () => [...crypto.getRandomValues(new Uint8Array(32))].map(b => b.toString(16).padStart(2, '0')).join('')
async function post(path: string, body: object) {
 const response = await fetch(journeyApi(path), { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Journey-Entry': '1' }, body: JSON.stringify(body) })
 const result = await response.json()
 if (!response.ok) throw new Error(result.category || result.error || 'host_unavailable')
 return result
}
const messages: Record<string, string> = {
 human_sign_in_required: '請先驗證你的身分。', session_expired: '登入已到期，請重新驗證。', human_revalidation_due: '已到七天驗證期限，請重新登入。',
 identity_changed: '登入身分已改變，請重新確認原本的畫布入口。', authority_denied: '目前的登入或成員權限已停用。', member_denied: '目前的成員權限已停用。', room_denied: '你無法進入指定畫布。請明確選擇另一張畫布。', room_missing: '指定畫布不存在；未建立空白畫布。',
 provider_unavailable: '身分服務暫時無法使用。請稍後重試。', owner_peer_unavailable: '此主機無法確認本機帳號，登入已停止。', challenge_expired_or_consumed: '這次驗證已到期或已使用，請重新開始。',
}
const humanEntryEnabled = import.meta.env.VITE_JOURNEY_HUMAN_ENTRY === 'true'
export function HumanEntry({ children }: { children: () => ReactNode }) {
 const [config, setConfig] = useState<{ enabled: boolean; mode?: string; localReady?: boolean } | null>(humanEntryEnabled ? null : { enabled: false })
 const [entry, setEntry] = useState<Entry | null>(null)
 const [problem, setProblem] = useState('')
 const [busy, setBusy] = useState(humanEntryEnabled)
 const [requestId, setRequestId] = useState('')
 const verifier = useRef<{ verifier: string; csrf: string; requestId: string } | null>(null)
 const requestVersion = useRef(0)
 const search = new URLSearchParams(window.location.search)
 const requested = search.get('room')
 async function refresh() {
  const requested = new URLSearchParams(window.location.search).get('room')
  const version = ++requestVersion.current
  setBusy(true); setEntry(null); setProblem('')
  try {
   const query = new URLSearchParams()
   if (requested !== null) query.set('room', requested)
   const response = await fetch(journeyApi('/auth/entry?' + query))
   let result = await response.json()
   if (version !== requestVersion.current) return
   if (!response.ok) {
    setProblem(result.category || 'host_unavailable')
    if (['room_denied', 'room_missing'].includes(result.category)) {
     const inventory = await fetch(journeyApi('/auth/entry'))
     if (inventory.ok && version === requestVersion.current) setEntry(await inventory.json())
    }
    return
   }
   const historyKey = 'journey-human-history:' + window.location.origin + ':' + result.backendId + ':' + result.memberId
   if (requested === null) {
    let remembered: string | null = null
    try { remembered = localStorage.getItem(historyKey) } catch {}
    if (remembered && result.rooms.includes(remembered)) {
     const resumed = await fetch(journeyApi('/auth/entry?' + new URLSearchParams({ remembered, member: result.memberId })))
     if (!resumed.ok) throw new Error('entry changed')
     result = await resumed.json()
     if (version !== requestVersion.current) return
    }
   }
   setEntry(result)
   if (result.room) {
    try { localStorage.setItem(historyKey, result.room) } catch {}
    if (requested === null) {
     const url = new URL(window.location.href); url.searchParams.set('room', result.room)
     window.history.replaceState(null, '', url)
     window.dispatchEvent(new PopStateEvent('popstate'))
    }
   }
  } catch { if (version === requestVersion.current) setProblem('host_unavailable') }
  finally { if (version === requestVersion.current) setBusy(false) }
 }
 useEffect(() => {
  if (!humanEntryEnabled) return
  let active = true
  fetch(journeyApi('/auth/config')).then(async response => {
   if (!response.ok) throw new Error()
   const value = await response.json()
   if (!active) return
   setConfig(value)
   if (value.enabled) void refresh(); else setBusy(false)
  }).catch(() => { if (active) { setProblem('host_unavailable'); setBusy(false) } })
  return () => { active = false; requestVersion.current++ }
 }, [])
 useEffect(() => {
  if (!config?.enabled) return
  const onNavigation = () => { void refresh() }
  window.addEventListener('popstate', onNavigation)
  return () => window.removeEventListener('popstate', onNavigation)
 }, [config, requested])
 useEffect(() => {
  if (!entry?.room || problem) return
  const timer = setTimeout(async () => {
   const csrf = /(?:^|;\s*)journey_human_csrf=([^;]+)/.exec(document.cookie)?.[1] || ''
   try {
    const response = await fetch(journeyApi('/auth/renew?' + new URLSearchParams({ _human: entry.memberId, _backend: entry.backendId, _humanAt: String(entry.verifiedHumanSignInAt), _humanRoom: entry.room! })), { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Journey-Entry': '1', 'X-Journey-Csrf': csrf }, body: '{}' })
    const result = await response.json()
    if (!response.ok) { setProblem(result.category || 'host_unavailable'); return }
    setEntry(current => current ? { ...current, expiresAt: result.expiresAt } : null)
   } catch { setProblem('host_unavailable') }
  }, Math.max(0, entry.expiresAt - Date.now() - 60_000))
  return () => clearTimeout(timer)
 }, [entry, problem])
 async function login() {
  setBusy(true); setProblem('')
  try {
   if (config?.mode === 'local') {
    const material = { verifier: secret(), csrf: secret() }
    const result = await post('/auth/local/start', material)
    verifier.current = { ...material, requestId: result.requestId }; setRequestId(result.requestId)
   } else {
    const popup = window.open('about:blank', '_blank')
    if (popup) popup.opener = null
    try {
     const result = await post('/auth/provider/start', {})
     if (popup) popup.location.href = result.loginUrl
     else { setProblem('請允許登入視窗，然後重試。') }
    } catch (error) { popup?.close(); throw error }
   }
  } catch (error) { setProblem(error instanceof Error ? error.message : 'host_unavailable') }
  finally { setBusy(false) }
 }
 async function finishLocal() {
  if (!verifier.current) return
  setBusy(true); setProblem('')
  try { await post('/auth/local/consume', verifier.current); verifier.current = null; setRequestId(''); await refresh() }
  catch (error) { setProblem(error instanceof Error ? error.message : 'host_unavailable'); setBusy(false) }
 }
 function select(room: string) {
  const url = new URL(window.location.href); url.searchParams.set('room', room); url.searchParams.delete('d'); url.hash = ''
  window.history.pushState(null, '', url); window.dispatchEvent(new PopStateEvent('popstate'))
 }
 if (config && !config.enabled) { setHumanContext(null); return children() }
 if (entry?.room && !problem && !busy) { setHumanContext({ member: entry.memberId, backend: entry.backendId, signInAt: entry.verifiedHumanSignInAt, room: entry.room }); return <><div className="human-entry-identity">{entry.label} · 身分已驗證</div>{children()}</> }
 return <main className="human-entry"><section aria-labelledby="human-entry-title" aria-busy={busy}>
  <p className="human-entry-eyebrow">私人畫布</p><h1 id="human-entry-title">{busy ? '正在確認入口' : entry ? '選擇畫布' : '驗證後進入畫布'}</h1>
  {requested !== null && <p>指定畫布：<strong>{requested || '（空白）'}</strong></p>}
  {entry && <p>{entry.label} · 身分已驗證 · 尚未連線至畫布</p>}
  <p role="status">{busy ? '正在確認身分與目前權限。' : problem ? messages[problem] || (problem === 'approval_pending' ? '本機帳號尚未核准這次驗證。' : problem === 'host_unavailable' ? '主機暫時無法使用，請重試。' : problem) : entry?.rooms.length ? '請選擇你有權限的既有畫布。' : entry ? '目前沒有可進入的畫布。' : '登入只建立你的身分；每張畫布仍會確認權限。'}</p>
  {requestId && <div><p>在本機終端機，用畫面中的請求編號核准登入：</p><code>{requestId}</code><p>驗證只保留在這個分頁，60 秒後失效。</p><button disabled={busy} onClick={() => void finishLocal()}>我已在本機核准</button></div>}
  {!entry && <button disabled={busy || (config?.mode === 'local' && !config.localReady)} onClick={() => void login()}>{config?.mode === 'local' ? '開始本機帳號驗證' : '開啟身分登入'}</button>}
  {config?.mode === 'local' && !config.localReady && <p>本機帳號驗證通道不可用；請由主機擁有者檢查。</p>}
  {entry?.rooms.map(room => <button key={room} disabled={busy} onClick={() => select(room)}>{room}</button>)}
  <button className="human-entry-secondary" disabled={busy} onClick={() => void refresh()}>重新確認入口</button>
 </section></main>
}
