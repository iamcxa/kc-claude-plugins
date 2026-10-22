import { useEffect, useRef, useState } from 'react'
import type { DraftContext } from '../draft-data'
import { recoveryCause, type RecoveryCause } from './access-recovery'
import { verifiedDraftContext } from './draft-recovery'
import './recovery-notice.css'

const messages = {
 expired: ['登入已到期', '另開原畫布，完成這個主機設定的身分驗證，再明確檢視本機草稿。', '另開原畫布並驗證登入'],
 denied: ['原畫布存取遭拒', '請確認原本帳號，或請主機擁有者恢復這張畫布的權限。權限恢復不會自動繼續。', '另開原畫布確認權限'],
 unavailable: ['主機或網路暫時無法使用', '這不代表權限已撤銷。可以重新確認；連線恢復後仍需另開原畫布，明確檢視草稿。', '另開原畫布重新確認'],
 unknown: ['結果未確認', '請保留工作。若已套用草稿，開啟本機草稿並核對原操作；不會自動重送或清除。', '另開原畫布核對身分'],
}
export function RecoveryNotice({ context, cause, onCause }: { context: DraftContext; cause: RecoveryCause; onCause: (cause: RecoveryCause) => void }) {
 const [expanded, setExpanded] = useState(true), [busy, setBusy] = useState(false), [status, setStatus] = useState('')
 const root = useRef<HTMLElement>(null), toggle = useRef<HTMLButtonElement>(null), pending = useRef<AbortController | null>(null)
 const [title, guidance, action] = messages[cause.kind]
 const url = new URL(window.location.pathname, context.origin); url.searchParams.set('room', context.room)
 useEffect(() => {
  const resize = new ResizeObserver(() => document.documentElement.style.setProperty('--human-recovery-height', root.current!.getBoundingClientRect().height + 'px'))
  resize.observe(root.current!)
  document.body.classList.add('human-recovery-active')
  return () => { pending.current?.abort(); resize.disconnect(); document.body.classList.remove('human-recovery-active'); document.documentElement.style.removeProperty('--human-recovery-height') }
 }, [])
 const cancel = () => { pending.current?.abort(); pending.current = null; setBusy(false); setExpanded(false); setStatus(''); toggle.current?.focus() }
 async function recheck() {
  pending.current?.abort(); const controller = new AbortController(); pending.current = controller
  setBusy(true); setStatus('正在重新確認原身分與畫布權限…')
  try {
   await verifiedDraftContext(context, true, AbortSignal.any([controller.signal, AbortSignal.timeout(8000)]))
   if (!controller.signal.aborted) setStatus('原身分與畫布權限已確認；舊畫布仍暫停。請另開原畫布，明確檢視草稿。')
  } catch (error) { if (!controller.signal.aborted) { onCause(recoveryCause(error)); setStatus('重新確認未完成；原工作保持暫停。') } }
  finally { if (pending.current === controller) { pending.current = null; setBusy(false) } }
 }
 return <section ref={root} className="human-recovery" aria-label="存取復原" data-kind={cause.kind} onKeyDown={event => { if (event.key === 'Escape') { event.stopPropagation(); cancel() } }}>
  <button ref={toggle} className="recovery-toggle" aria-expanded={expanded} onClick={() => setExpanded(value => !value)}>{title} · 原畫布 {context.room}</button>
  {expanded && <div className="recovery-body"><p>{guidance}</p><p>原工作保留，傳送已停止。本機儲存與雲端同步分開確認。</p>
   <div role="status" aria-live="polite">{status || title}</div>
   <div className="recovery-actions"><a href={url.href} target="_blank" rel="noopener noreferrer">{action}</a><button disabled={busy} onClick={() => void recheck()}>重新確認原身分與權限</button><button className="secondary" onClick={cancel}>暫不恢復，保留暫停</button></div>
  </div>}
 </section>
}
