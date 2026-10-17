import { useEffect, useRef, useState } from 'react'
import { serializeTldrawJson, useEditor } from 'tldraw'
import { journeyApi } from './api'
import './canvas-save.css'

// A viewer front-end answers with the SPA fallback HTML here, so the content type decides.
async function call<T>(roomId: string, path: string, method: 'GET' | 'POST' | 'DELETE', body?: unknown): Promise<T | null> {
	try {
		const res = await fetch(journeyApi(path + (path.includes('?') ? '&' : '?') + 'room=' + encodeURIComponent(roomId)), {
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
	const trigger = useRef<HTMLButtonElement>(null)
	const closeForm = () => {
		setName(null)
		requestAnimationFrame(() => trigger.current?.focus())
	}

	useEffect(() => {
		call<{ dir: string }>(roomId, '/save', 'GET').then((r) => setCanSave(r !== null)).catch(() => setCanSave(false))
	}, [roomId])

	useEffect(() => {
		if (name === null) return
		call<{ exists: boolean }>(roomId, `/save?name=${encodeURIComponent(name)}`, 'GET')
			.then((r) => setExists(r?.exists ?? false))
			.catch(() => setExists(false))
	}, [name, roomId])

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
			const saved = await call<{ path: string; records: number }>(roomId, '/save', 'POST', { name: name ?? roomId, file })
			if (saved) setNote(`${saved.records} records → ${saved.path.split('/').slice(-2).join('/')}`)
			closeForm()
		})

	return (
		<div className="journey-save">
			<button ref={trigger} type="button" className="tlui-button" disabled={busy} aria-expanded={name !== null} onClick={() => setName(`${roomId}.tldr`)}>
				save
			</button>
			<button type="button" className="tlui-button" disabled={busy} onClick={download}>
				download
			</button>
			{(name !== null || note) && <div className="journey-save-panel">
				{note && <div className="journey-save-note" role="status">{note}</div>}
				{name !== null ? <div className="journey-save-form">
					<label htmlFor="journey-save-name">Filename</label>
					<input
						id="journey-save-name"
						value={name}
						autoFocus
						onChange={(e) => setName(e.target.value)}
						onKeyDown={(e) => {
							e.stopPropagation()
							if (e.key === 'Enter') save()
							if (e.key === 'Escape') closeForm()
						}}
					/>
					<div className="journey-save-actions">
						<button type="button" className="tlui-button" disabled={busy} onClick={closeForm}>Cancel</button>
						<button type="button" className="tlui-button" disabled={busy} onClick={save}>{exists ? 'overwrite' : 'write'}</button>
					</div>
				</div> : <button type="button" className="tlui-button" onClick={() => { setNote(null); trigger.current?.focus() }}>Dismiss</button>}
			</div>}
		</div>
	)
}
