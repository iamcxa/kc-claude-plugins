// Adapted from tldraw's `templates/simple-server-example` (MIT).
import { useSync } from '@tldraw/sync'
import { TLAssetStore, Tldraw, serializeTldrawJson } from 'tldraw'
import 'tldraw/tldraw.css'

const SERVER_URL = `http://localhost:5858`

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
				deepLinks
				onMount={(editor) => {
					;(window as any).editor = editor
					;(window as any).serializeTldrawJson = () => serializeTldrawJson(editor)
				}}
			/>
		</div>
	)
}
