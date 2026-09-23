import { useEffect, useState } from 'react'
import { serializeTldrawJson, useEditor } from 'tldraw'

// A viewer front-end answers with the SPA fallback HTML here, so the content type decides.
async function call<T>(path: string, method: 'GET' | 'POST' | 'DELETE', body?: unknown): Promise<T | null> {
	try {
		const res = await fetch(path, {
			method,
			headers: body ? { 'Content-Type': 'application/json' } : undefined,
			body: body ? JSON.stringify(body) : undefined,
		})
		if (!res.headers.get('content-type')?.includes('application/json')) return null
		const parsed = (await res.json()) as T & { error?: string }
		if (!res.ok) throw new Error(parsed.error ?? `${res.status}`)
		return parsed
	} catch (e) {
		if (e instanceof Error && e.message && !e.message.includes('Failed to fetch')) throw e
		return null
	}
}

export function SaveButton({ roomId }: { roomId: string }) {
	const editor = useEditor()
	const [busy, setBusy] = useState(false)
	const [note, setNote] = useState<string | null>(null)
	const [name, setName] = useState<string | null>(null)
	const [exists, setExists] = useState(false)
	const [canSave, setCanSave] = useState(false)

	useEffect(() => {
		call<{ dir: string }>('/save', 'GET').then((r) => setCanSave(r !== null)).catch(() => setCanSave(false))
	}, [])

	useEffect(() => {
		if (name === null) return
		call<{ exists: boolean }>(`/save?name=${encodeURIComponent(name)}`, 'GET')
			.then((r) => setExists(r?.exists ?? false))
			.catch(() => setExists(false))
	}, [name])

	if (!canSave) return null

	const guard = async (work: () => Promise<void>) => {
		setBusy(true)
		setNote(null)
		try {
			await work()
		} catch (e) {
			setNote((e as Error).message)
		} finally {
			setBusy(false)
		}
	}

	const download = () =>
		guard(async () => {
			const file = await serializeTldrawJson(editor)
			const href = URL.createObjectURL(new Blob([file], { type: 'application/vnd.tldraw+json' }))
			const link = document.createElement('a')
			link.href = href
			link.download = `${roomId}.tldr`
			link.click()
			URL.revokeObjectURL(href)
			setNote('downloaded')
		})

	const save = () =>
		guard(async () => {
			const file = await serializeTldrawJson(editor)
			const saved = await call<{ path: string; records: number }>('/save', 'POST', { name: name ?? roomId, file })
			if (saved) setNote(`${saved.records} records → ${saved.path.split('/').slice(-2).join('/')}`)
			setName(null)
		})

	return (
		<div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: 6, pointerEvents: 'all' }}>
			{note && <span style={{ fontSize: 11, opacity: 0.8 }}>{note}</span>}
			{name !== null ? (
				<>
					<input
						value={name}
						autoFocus
						onChange={(e) => setName(e.target.value)}
						onKeyDown={(e) => {
							if (e.key === 'Enter') save()
							if (e.key === 'Escape') setName(null)
						}}
						style={{ width: 240, fontSize: 12 }}
					/>
					<button type="button" className="tlui-button" disabled={busy} onClick={save}>
						{exists ? 'overwrite' : 'write'}
					</button>
				</>
			) : (
				<>
					<button type="button" className="tlui-button" disabled={busy} onClick={() => setName(`${roomId}.tldr`)}>
						save
					</button>
					<button type="button" className="tlui-button" disabled={busy} onClick={download}>
						download
					</button>
				</>
			)}
		</div>
	)
}
