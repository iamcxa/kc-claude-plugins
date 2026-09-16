import { useEffect, useState } from 'react'
import { serializeTldrawJson, useEditor } from 'tldraw'

type Status = { running: boolean; url: string | null; targetUp: boolean }

// A shared page gets the SPA fallback HTML here, so the content type decides, not the status.
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

export function ShareButton({ roomId }: { roomId: string }) {
	const editor = useEditor()
	const [status, setStatus] = useState<Status | null>(null)
	const [busy, setBusy] = useState(false)
	const [note, setNote] = useState<string | null>(null)
	const [name, setName] = useState<string | null>(null)
	const [exists, setExists] = useState(false)

	useEffect(() => {
		call<Status>('/tunnel', 'GET').then(setStatus).catch(() => setStatus(null))
	}, [])

	useEffect(() => {
		if (name === null) return
		call<{ exists: boolean }>(`/save?name=${encodeURIComponent(name)}`, 'GET')
			.then((r) => setExists(r?.exists ?? false))
			.catch(() => setExists(false))
	}, [name])

	if (!status) return null

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

	const toggleTunnel = () =>
		guard(async () => {
			const next = await call<Status>('/tunnel', status.running ? 'DELETE' : 'POST')
			if (next) setStatus(next)
		})

	const copy = () =>
		guard(async () => {
			if (!status.url) return
			await navigator.clipboard.writeText(status.url)
			setNote('link copied')
		})

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
			{status.running && status.url && (
				<>
					<span style={{ fontSize: 11, userSelect: 'all', opacity: 0.8 }}>{status.url}</span>
					<button type="button" className="tlui-button" disabled={busy} onClick={copy}>
						copy link
					</button>
				</>
			)}
			{status.running && !status.targetUp && (
				<span style={{ fontSize: 11, color: '#b00' }}>share front-end is down</span>
			)}
			<button type="button" className="tlui-button" disabled={busy} onClick={toggleTunnel}>
				{busy ? '…' : status.running ? 'stop sharing' : 'share'}
			</button>
		</div>
	)
}
