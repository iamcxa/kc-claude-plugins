// Adapted from tldraw's `templates/simple-server-example` (MIT).
import { useSync } from '@tldraw/sync'
import { Editor, TLAssetStore, TLShape, Tldraw, serializeTldrawJson } from 'tldraw'
import 'tldraw/tldraw.css'
import { storyBorder } from '../../lib/records.mjs'

const SERVER_URL = `http://localhost:5858`

const noAssets: TLAssetStore = {
	async upload() {
		throw new Error('This canvas has no asset storage. Use notes and shapes, not images.')
	},
	resolve(asset) {
		return asset.props.src
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
	const roomId = new URLSearchParams(window.location.search).get('room') || 'default'

	const store = useSync({
		uri: `${SERVER_URL}/connect/${roomId}`,
		assets: noAssets,
	})

	return (
		<div style={{ position: 'fixed', inset: 0 }}>
			<Tldraw
				store={store}
				deepLinks
				onMount={(editor) => {
					;(window as any).editor = editor
					;(window as any).serializeTldrawJson = () => serializeTldrawJson(editor)
					return syncStoryBorders(editor)
				}}
			/>
		</div>
	)
}
