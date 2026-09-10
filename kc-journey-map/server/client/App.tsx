// Adapted from tldraw's `templates/simple-server-example` (MIT).
import { useSync } from '@tldraw/sync'
import { TLAssetStore, Tldraw, serializeTldrawJson } from 'tldraw'
import 'tldraw/tldraw.css'

const SERVER_URL = `http://localhost:5858`

// Story maps are notes, frames and lines. Image upload is deliberately absent — there is
// no blob endpoint on the server, so a paste would fail late instead of here.
const noAssets: TLAssetStore = {
	async upload() {
		throw new Error('This canvas has no asset storage. Use notes and shapes, not images.')
	},
	resolve(asset) {
		return asset.props.src
	},
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
				// Puts the camera and page in the URL as ?d=..., so a screenshot run can be
				// pointed at one page of one map.
				deepLinks
				onMount={(editor) => {
					;(window as any).editor = editor
					// tldraw's own file format, so a board can leave here and be opened in any
					// tldraw — and come back with its meta intact.
					;(window as any).serializeTldrawJson = () => serializeTldrawJson(editor)
				}}
			/>
		</div>
	)
}
