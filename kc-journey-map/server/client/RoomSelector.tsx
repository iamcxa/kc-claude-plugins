import { useEffect, useState } from 'react'
import { journeyApi } from './api'
import './room-selector.css'

export type ConnectionState = 'loading' | 'connected' | 'offline' | 'error'

export function RoomSelector({ roomId, connection, switching, switchError, onNavigate }: { roomId: string; connection: ConnectionState; switching: boolean; switchError: boolean; onNavigate: (room: string) => void }) {
	const [rooms, setRooms] = useState<string[]>([])
	const [error, setError] = useState(false)
	const [loading, setLoading] = useState(true)
	const [refresh, setRefresh] = useState(0)
	useEffect(() => {
		const controller = new AbortController()
		setLoading(true)
		setError(false)
		fetch(journeyApi('/health'), { signal: controller.signal })
			.then(async response => {
				if (!response.ok) throw new Error('Room inventory unavailable')
				const result = await response.json()
				if (!Array.isArray(result.rooms) || result.rooms.some((room: unknown) => typeof room !== 'string')) throw new Error('Invalid inventory')
				if (!controller.signal.aborted) setRooms([...new Set<string>(result.rooms)].sort())
			})
			.catch(() => { if (!controller.signal.aborted) { setRooms([]); setError(true) } })
			.finally(() => { if (!controller.signal.aborted) setLoading(false) })
		return () => controller.abort()
	}, [roomId, refresh])
	const changeRoom = (next: string) => {
		if (next === roomId || !rooms.includes(next)) return
		onNavigate(next)
	}
	return <nav className="journey-rooms" aria-label="Room navigation">
		<div className="journey-rooms-controls">
			<label htmlFor="journey-room">Room</label>
			<select id="journey-room" value={roomId} disabled={loading || error || switching || connection === 'offline'} onChange={event => changeRoom(event.target.value)}>
				{!rooms.includes(roomId) && <option value={roomId} disabled>{roomId} (requested)</option>}
				{rooms.map(room => <option key={room} value={room}>{room}</option>)}
			</select>
			<button type="button" onClick={() => setRefresh(value => value + 1)} disabled={loading} aria-label="Refresh rooms">Refresh</button>
		</div>
		<div className="journey-rooms-status" role="status">
			{switching ? 'Confirming edits…' : switchError ? 'Edits not confirmed. Stay here; select a room to retry.' : error ? 'Rooms unavailable. Refresh to retry.' : loading ? 'Loading rooms…' : connection === 'offline' ? 'Offline. Reconnect before switching.' : connection === 'error' ? 'Room unavailable. Choose another room.' : connection === 'loading' ? 'Connecting…' : 'Connected'}
		</div>
	</nav>
}
