// Adapted from tldraw's `templates/simple-server-example` (MIT).
import { useSync } from '@tldraw/sync'
import { TLAssetStore, Tldraw } from 'tldraw'
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
				}}
			/>
		</div>
	)
}
