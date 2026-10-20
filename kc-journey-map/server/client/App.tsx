// Adapted from tldraw's `templates/simple-server-example` (MIT).
import { useSync } from '@tldraw/sync'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { Editor, TLAssetStore, TLShape, Tldraw, serializeTldrawJson, type TLStoreWithStatus } from 'tldraw'
import 'tldraw/tldraw.css'
import { parseGithubBlobUrl } from '../../lib/repo-doc.mjs'
import { storyBorder } from '../../lib/records.mjs'
import { DocPopup, type DocTarget } from './DocPopup'
import './doc-popup.css'
import { SaveButton } from './SaveButton'
import { StickyBackbone } from './StickyBackbone'
import { addSequencePage } from './sequence'
import { journeyApi, type HumanContext } from './api'
import { RoomPageMenu, RoomSelector, type ConnectionState } from './RoomSelector'
import { confirmRoomSwitch, documentFingerprint } from './confirm-room-switch'
import { verifyRoomAdmission, RoomAdmissionError, sourceAdmissionLost } from './room-admission'
import { assetUploadId } from './asset-upload-id'
import { HumanEntry, type HumanCanvasEntry } from './HumanEntry'
import { HumanDraftPanel } from './HumanDraftPanel'
import { humanSocket } from './human-socket'
import type { DraftContext } from '../draft-data'

const APP_NAME = 'kc-journey-map'

function parseChapterUrl(url: string): DocTarget | null {
	const parsed = parseGithubBlobUrl(url)
	return parsed && { ...parsed, sourceUrl: url }
}

// tldraw's HyperlinkButton (shared by note/geo/bookmark/image/video shapes)
// always renders `<a target="_blank">` with no override slot in TLComponents.
// A capture-phase click listener on the editor container is the only seam
// available to intercept before the browser's default new-tab navigation fires.
function useChapterPopupIntercept(editor: Editor | null, onOpen: (target: DocTarget, trigger: HTMLElement) => void) {
	useEffect(() => {
		if (!editor) return
		const container = editor.getContainer()
		const handler = (e: MouseEvent) => {
			const anchor = (e.target as HTMLElement)?.closest?.('a.tl-hyperlink-button') as HTMLAnchorElement | null
			if (!anchor) return
			const target = parseChapterUrl(anchor.href)
			if (!target) return // not a chapter link (e.g. a blame/evidence link) — let it open normally
			e.preventDefault()
			e.stopPropagation()
			onOpen(target, anchor)
		}
		container.addEventListener('click', handler, { capture: true })
		return () => container.removeEventListener('click', handler, { capture: true })
	}, [editor, onOpen])
}

function syncDocumentTitle(editor: Editor, roomId: string) {
	const update = () => {
		document.title = `${editor.getDocumentSettings().name.trim() || roomId} | ${APP_NAME}`
	}
	update()
	return editor.store.listen(update, { scope: 'document' })
}

// `asset:` is schema-valid and carries no origin, so each viewer resolves against their own.
const ASSET_SCHEME = 'asset:'

const canvasAssets = (roomId: string): TLAssetStore => ({
	async upload(_asset, file) {
		// crypto.randomUUID is unavailable over plain http on a private-network hostname.
		const name = assetUploadId(file.name)
		const res = await fetch(journeyApi(`/uploads/${encodeURIComponent(name)}?room=${encodeURIComponent(roomId)}`), { method: 'PUT', body: file })
		if (!res.ok) throw new Error(`upload failed: ${res.status} ${res.statusText}`)
		return { src: `${ASSET_SCHEME}${name}` }
	},
	resolve(asset) {
		const src = asset.props.src
		if (!src?.startsWith(ASSET_SCHEME)) return src
		return journeyApi(`/uploads/${encodeURIComponent(src.slice(ASSET_SCHEME.length))}?room=${encodeURIComponent(roomId)}`)
	},
})

// After-change hooks see the note's measured growY, including native text edits.
// Decorations stay standard geo records so the file exporter needs no custom schema.
function syncStoryBorders(editor: Editor) {
	const isBorder = (shape: TLShape) => (shape.meta.journey as { kind?: string })?.kind === 'story-border'
	const sync = (shape: TLShape) => {
		const story = isBorder(shape) ? editor.getShape(shape.parentId) : shape
		if (!story || story.type !== 'note') return
		const wanted = storyBorder(story)
		const borders = editor.getSortedChildIdsForParent(story.id).map((id) => editor.getShape(id)!)
			.filter((child) => isBorder(child))
		const obsolete = borders.filter((child) => child.id !== wanted?.id).map((child) => child.id)
		if (obsolete.length) editor.store.remove(obsolete)
		if (wanted && JSON.stringify(editor.getShape(wanted.id)) !== JSON.stringify(wanted)) editor.store.put([wanted])
	}
	const stopCreate = editor.sideEffects.registerAfterCreateHandler('shape', sync)
	const stopChange = editor.sideEffects.registerAfterChangeHandler('shape', (_prev, next) => sync(next))
	editor.run(() => editor.store.allRecords().filter((r): r is TLShape => r.typeName === 'shape').forEach(sync), { history: 'ignore' })
	return () => { stopCreate(); stopChange() }
}

export default function App() {
 return <HumanEntry>{entry => <CanvasApp entry={entry} />}</HumanEntry>
}

type RoomSession = { id: number; roomId: string; uri: string; context?:DraftContext; store?: TLStoreWithStatus }
function CanvasApp({ entry }: { entry: HumanCanvasEntry }) {
 const [active, setActive] = useState<RoomSession>(() => {
  const roomId = entry.context?.room || new URLSearchParams(window.location.search).get('room') || 'default'
  return { id: 0, roomId, context:entry.context?{...entry.context,room:roomId}:undefined, uri: journeyApi('/connect/' + encodeURIComponent(roomId)) }
 })
 const [target, setTarget] = useState<RoomSession | null>(null)
 const [connection, setConnection] = useState<ConnectionState>('loading')
 const [switching, setSwitching] = useState(false)
 const [switchError, setSwitchError] = useState('')
 const [frozen, setFrozen] = useState(false)
 const editor = useRef<Editor | null>(null)
 const [currentEditor,setCurrentEditor]=useState<Editor|null>(null)
 const lifetime=useRef(0),frozenRef=useRef(false),historyRecorded=useRef(new Set<number>())
 const activeId = useRef(active.id); activeId.current = active.id
 const acceptedUrl = useRef(window.location.href)
 const navigation = useRef(0)
 const latestEntry = useRef(entry); latestEntry.current = entry
 const pending = useRef<{ id: number; url: URL; push: boolean; fingerprint: string; controller: AbortController } | null>(null)
 const freeze = useCallback(() => {
  frozenRef.current=true
  navigation.current++; pending.current?.controller.abort(); pending.current = null
  setTarget(null); setSwitching(false); setFrozen(true)
  editor.current?.updateInstanceState({ isReadonly: true })
  setSwitchError('Source access paused. Work retained here. Open another room in a separate tab and verify access.')
 }, [])
 useEffect(() => { if (entry.problem) freeze() }, [entry.problem, freeze])
 useEffect(() => {lifetime.current++;return()=>{lifetime.current++;navigation.current++; pending.current?.controller.abort()}}, [])
 const restoreUrl = () => {
  if (window.location.href !== acceptedUrl.current) {
   window.history.replaceState(null, '', acceptedUrl.current)
   window.dispatchEvent(new PopStateEvent('popstate'))
  }
 }
 const navigate = useCallback(async (url: URL, push: boolean) => {
  const next = url.searchParams.get('room') || (latestEntry.current.context ? '' : 'default')
  if (next === active.roomId) return
  if (frozen) { if (!push) restoreUrl(); return }
  const id = ++navigation.current
  pending.current?.controller.abort()
  const controller = new AbortController()
  pending.current = { id, url, push, fingerprint: '', controller }
  setTarget(null); setSwitching(true); setSwitchError('')
  if (!push) restoreUrl()
  const context = latestEntry.current.context
  try {
   if (context) await verifyRoomAdmission(active.roomId, context, controller.signal)
   if (id !== navigation.current) return
   const confirmed = await confirmRoomSwitch(editor.current, active.roomId, () => freeze())
   if (id !== navigation.current) return
   if (!confirmed) throw new Error('Edits not confirmed. Stay here; select a room to retry.')
   const fingerprint = editor.current ? documentFingerprint(editor.current) : ''
   if (context) await verifyRoomAdmission(next, context, controller.signal)
   if (id !== navigation.current) return
   pending.current!.fingerprint = fingerprint
   setTarget({ id, roomId: next, context:context?{...context,room:next}:undefined, uri: journeyApi('/connect/' + encodeURIComponent(next), context ? { ...context, room: next } : null) })
  } catch (error) {
   if (id !== navigation.current) return
   if (sourceAdmissionLost(error, active.roomId)) { freeze(); return }
   setTarget(null); setSwitching(false); pending.current = null
   setSwitchError(error instanceof RoomAdmissionError ? `Target ${next} unavailable (${error.category}). Original room retained.` : error instanceof Error ? error.message : 'Room switch failed. Original room retained.')
  }
 }, [active.roomId, frozen, freeze])
 const failTarget = useCallback(async (id: number, message: string) => {
  const attempt = pending.current
  if (attempt?.id !== id) return
  try {
   const context = latestEntry.current.context
   if (context) await verifyRoomAdmission(active.roomId, context, attempt.controller.signal)
  } catch (error) {
   if (pending.current?.id !== id) return
   if (sourceAdmissionLost(error, active.roomId)) { freeze(); return }
  }
  if (pending.current?.id !== id) return
  attempt.controller.abort(); pending.current = null; navigation.current++
  setTarget(null); setSwitching(false); setSwitchError(message)
 }, [active.roomId, freeze])
 const onStore = useCallback((id: number, store: TLStoreWithStatus) => {
  if (id === activeId.current && store.status === 'error') setConnection('error')
  setActive(current => current.id === id && !(store.status === 'error' && current.store?.status === 'synced-remote') ? { ...current, store } : current)
  setTarget(current => current?.id === id ? { ...current, store } : current)
 }, [])
 useEffect(() => {
  if (!target || !pending.current || target.id !== pending.current.id) return
  const attempt = pending.current
  if (target.store?.status === 'error') {
   void failTarget(target.id, `Target ${target.roomId} could not connect. Original room retained.`); return
  }
  if (target.store?.status !== 'synced-remote' || target.store.connectionStatus !== 'online') return
  let canceled = false
  void (async () => {
   try {
    const context = latestEntry.current.context
    if (context) {
     await verifyRoomAdmission(active.roomId, context, attempt.controller.signal)
     await verifyRoomAdmission(target.roomId, context, attempt.controller.signal)
    }
    if (canceled || attempt.id !== navigation.current) return
    if (editor.current && documentFingerprint(editor.current) !== attempt.fingerprint) throw new Error('Source changed while connecting. Stay here; select a room to retry.')
    if (attempt.push) window.history.pushState(null, '', attempt.url)
    else window.history.replaceState(null, '', attempt.url)
    acceptedUrl.current = attempt.url.href
    activeId.current = target.id; editor.current = null;setCurrentEditor(null)
    pending.current = null; setActive(target); setTarget(null); setSwitching(false); setSwitchError('')
    window.dispatchEvent(new PopStateEvent('popstate'))
   } catch (error) {
    if (canceled || attempt.id !== navigation.current) return
    if (sourceAdmissionLost(error, active.roomId)) { freeze(); return }
    pending.current = null; setTarget(null); setSwitching(false)
    setSwitchError(error instanceof Error ? error.message : 'Target unavailable. Original room retained.')
   }
  })()
  return () => { canceled = true }
 }, [target, active.roomId, freeze, failTarget])
 useEffect(() => {
  if (!target) return
  const id = target.id
  const timer = setTimeout(() => {
   if (pending.current?.id !== id) return
   void failTarget(id, `Target ${target.roomId} timed out. Original room retained.`)
  }, 8000)
  return () => clearTimeout(timer)
 }, [target?.id, failTarget])
 useEffect(() => {
  const onHistory = () => {
   const url = new URL(window.location.href)
   if (url.href !== acceptedUrl.current && (url.searchParams.get('room') || 'default') !== active.roomId) void navigate(url, false)
  }
  window.addEventListener('popstate', onHistory, { capture: true })
  return () => window.removeEventListener('popstate', onHistory, { capture: true })
 }, [active.roomId, navigate])
 const onEditor = useCallback((id: number, value: Editor | null) => { if (id === activeId.current) {editor.current = value;setCurrentEditor(value)} }, [])
 useEffect(()=>{
  const id=active.id,life=lifetime.current
  if(!active.context || frozen || historyRecorded.current.has(id) || active.store?.status!=='synced-remote' || active.store.connectionStatus!=='online')return
  historyRecorded.current.add(id)
  void latestEntry.current.activate(active.roomId,()=>activeId.current===id&&!frozenRef.current&&life===lifetime.current)
 },[active,frozen])
 const pausedCheck = useRef(false)
 useEffect(() => {
  if (frozen || !entry.context || (connection !== 'offline' && connection !== 'error') || pausedCheck.current) return
  pausedCheck.current = true
  const controller = new AbortController()
  verifyRoomAdmission(active.roomId, entry.context, controller.signal).catch(error => { if (error instanceof RoomAdmissionError && error.denied) freeze() }).finally(() => { pausedCheck.current = false })
  return () => controller.abort()
 }, [connection, active.roomId, entry.context?.member, frozen, freeze])
 return <RoomSelector roomId={active.roomId} human={entry.context} connection={connection} switching={switching} switchError={switchError} frozen={frozen} onDenied={freeze} onNavigate={next => {
  const url = new URL(acceptedUrl.current)
  url.searchParams.set('room', next); url.searchParams.delete('d'); url.hash = ''
  if (frozen) { window.open(url.href, '_blank', 'noopener,noreferrer'); return }
  void navigate(url, true)
 }}>
  {[...(!frozen ? [active] : []), ...(target ? [target] : [])].map(session => <RoomSync key={session.id} session={session} onStore={onStore} onPause={session.id===active.id?freeze:()=>void failTarget(session.id,'Target access paused. Original room retained.')} />)}
  <RoomCanvas key={active.id} session={active} frozen={frozen} onConnection={setConnection} onEditor={onEditor} />
  {active.context && <HumanDraftPanel key={'draft:'+active.id} context={active.context} label={entry.label} editor={currentEditor} connection={connection} onPause={freeze}/> }
 </RoomSelector>
}

function RoomSync({ session, onStore, onPause }: { session: RoomSession; onStore: (id: number, store: TLStoreWithStatus) => void; onPause:()=>void }) {
 const assets = useMemo(() => canvasAssets(session.roomId), [session.roomId])
 const pause=useRef(onPause);pause.current=onPause
 const connect=useMemo(()=>session.context?()=>humanSocket(session.uri,session.context!,()=>pause.current()):undefined,[session.uri])
 const store = useSync({ ...(connect?{connect}:{uri:session.uri}), assets })
 useEffect(() => { onStore(session.id, store) }, [session.id, store, onStore])
 return null
}

function RoomCanvas({ session, frozen, onConnection, onEditor }: { session: RoomSession; frozen: boolean; onConnection: (state: ConnectionState) => void; onEditor: (id: number, editor: Editor | null) => void }) {
 const roomId = session.roomId
 const store = session.store || { status: 'loading' as const }
	const components = useMemo(
		() => ({ PageMenu: RoomPageMenu, SharePanel: () => frozen ? null : <SaveButton roomId={roomId} />, InFrontOfTheCanvas: StickyBackbone }),
		[roomId, frozen]
	)
	useEffect(() => {
		if (store.status !== 'synced-remote') document.title = `${roomId} | ${APP_NAME}`
		onConnection(frozen ? 'error' : store.status === 'synced-remote' ? store.connectionStatus === 'online' ? 'connected' : 'offline' : store.status === 'error' ? 'error' : 'loading')
	}, [roomId, store, onConnection, frozen])

	const [editor, setEditor] = useState<Editor | null>(null)
	const [popup, setPopup] = useState<{ target: DocTarget; trigger: HTMLElement } | null>(null)
	useChapterPopupIntercept(frozen ? null : editor, (target, trigger) => setPopup({ target, trigger }))

 useEffect(() => { if (frozen) setPopup(null) }, [frozen])
	return (
		<div className="journey-canvas-root" style={{ position: 'fixed', inset: 0 }}>
			<Tldraw
				licenseKey={import.meta.env.VITE_TLDRAW_LICENSE_KEY}
				store={store}
				components={components}
				deepLinks
				onMount={(editor) => {
					onEditor(session.id, editor)
     if (frozen) editor.updateInstanceState({ isReadonly: true })
					;(window as any).editor = editor
					;(window as any).addSequencePage = (input: Parameters<typeof addSequencePage>[1]) => addSequencePage(editor, input)
					;(window as any).serializeTldrawJson = () => serializeTldrawJson(editor)
					const stopBorders = syncStoryBorders(editor)
					const stopTitle = syncDocumentTitle(editor, roomId)
					setEditor(editor)
					return () => { onEditor(session.id, null); stopBorders(); stopTitle() }
				}}
			/>
			{popup &&
				createPortal(
					// tldraw's InFrontOfTheCanvas slot sits under an ancestor
					// (.tl-canvas__in-front) that sets pointer-events: none, so nothing
					// rendered there is hit-testable; mount as a sibling of the canvas
					// container instead.
					<DocPopup roomId={roomId} target={popup.target} returnFocusTo={popup.trigger} onClose={() => setPopup(null)} />,
					document.body,
				)}
		</div>
	)
}
