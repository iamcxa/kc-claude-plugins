// Adapted from tldraw's `templates/simple-server-example` (MIT).
import { useSync } from '@tldraw/sync'
import { useEffect, useMemo, useSyncExternalStore } from 'react'
import { Editor, TLAssetStore, TLShape, Tldraw, serializeTldrawJson } from 'tldraw'
import 'tldraw/tldraw.css'
import { storyBorder } from '../../lib/records.mjs'
import { ShareButton } from './ShareButton'
import { addSequencePage } from './sequence'

// Falls back to the page's own origin so the /connect proxy (see vite.config.mts)
// reaches the loopback-bound doc API from whichever host served this page.
const SERVER_URL =
	import.meta.env.VITE_JOURNEY_API_URL || `${window.location.protocol}//${window.location.host}`

const APP_NAME = 'kc-journey-map'

function subscribeToLocation(onChange: () => void) {
	window.addEventListener('popstate', onChange)
	return () => window.removeEventListener('popstate', onChange)
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

const canvasAssets: TLAssetStore = {
	async upload(_asset, file) {
		// crypto.randomUUID is unavailable over plain http on a private-network hostname.
		const name = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}-${file.name}`
		const res = await fetch(`/uploads/${encodeURIComponent(name)}`, { method: 'PUT', body: file })
		if (!res.ok) throw new Error(`upload failed: ${res.status} ${res.statusText}`)
		return { src: `${ASSET_SCHEME}${name}` }
	},
	resolve(asset) {
		const src = asset.props.src
		if (!src?.startsWith(ASSET_SCHEME)) return src
		return `${window.location.origin}/uploads/${encodeURIComponent(src.slice(ASSET_SCHEME.length))}`
	},
}

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
	const search = useSyncExternalStore(subscribeToLocation, () => window.location.search)
	const roomId = new URLSearchParams(search).get('room') || 'default'
	return <RoomCanvas key={roomId} roomId={roomId} />
}

function RoomCanvas({ roomId }: { roomId: string }) {
	const components = useMemo(() => ({ SharePanel: () => <ShareButton roomId={roomId} /> }), [roomId])
	const store = useSync({
		uri: `${SERVER_URL}/connect/${roomId}`,
		assets: canvasAssets,
	})
	useEffect(() => {
		if (store.status !== 'synced-remote') document.title = `${roomId} | ${APP_NAME}`
	}, [roomId, store.status])

	return (
		<div style={{ position: 'fixed', inset: 0 }}>
			<Tldraw
				store={store}
				components={components}
				deepLinks
				onMount={(editor) => {
					;(window as any).editor = editor
					;(window as any).addSequencePage = (input: Parameters<typeof addSequencePage>[1]) => addSequencePage(editor, input)
					;(window as any).serializeTldrawJson = () => serializeTldrawJson(editor)
					const stopBorders = syncStoryBorders(editor)
					const stopTitle = syncDocumentTitle(editor, roomId)
					return () => { stopBorders(); stopTitle() }
				}}
			/>
		</div>
	)
}
