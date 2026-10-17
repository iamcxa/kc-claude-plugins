import type { Editor } from 'tldraw'
import { journeyApi } from './api'

function ordered(value: unknown): unknown {
	if (Array.isArray(value)) return value.map(ordered)
	if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([key, item]) => [key, ordered(item)]))
	return value
}

export async function confirmRoomSwitch(editor: Editor | null, roomId: string): Promise<boolean> {
	if (!editor) return true
	editor.complete()
	const snapshot = () => JSON.stringify(ordered(editor.store.getStoreSnapshot('document').store))
	const before = snapshot()
	try {
		const response = await fetch(journeyApi('/doc?room=' + encodeURIComponent(roomId)), { signal: AbortSignal.timeout(8000) })
		if (!response.ok) return false
		const result = await response.json()
		const remote = Object.fromEntries(result.snapshot.documents.map(({ state }: { state: { id: string } }) => [state.id, state]))
		return before === snapshot() && before === JSON.stringify(ordered(remote))
	} catch { return false }
}
