import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { DefaultPageMenu, TldrawUiButton, TldrawUiButtonIcon, TldrawUiButtonLabel, TldrawUiDropdownMenuContent, TldrawUiDropdownMenuGroup, TldrawUiDropdownMenuItem, TldrawUiDropdownMenuRoot, TldrawUiDropdownMenuTrigger, TldrawUiInput, useMenuIsOpen } from 'tldraw'
import { journeyApi } from './api'
import './room-selector.css'

export type ConnectionState = 'loading' | 'connected' | 'offline' | 'error'
type RoomNavigation = { roomId: string; connection: ConnectionState; switching: boolean; switchError: boolean; onNavigate: (room: string) => void }
type RoomInventory = RoomNavigation & { rooms: string[]; loading: boolean; unavailable: boolean; disabled: boolean; status: string; refresh: () => void }
const RoomContext = createContext<RoomInventory | null>(null)

export function RoomSelector({ children, ...navigation }: RoomNavigation & { children: ReactNode }) {
	const { roomId, connection, switching, switchError, onNavigate } = navigation
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
	const disabled = loading || error || switching || connection === 'offline'
	const status = switching ? 'Confirming edits…' : switchError ? 'Edits not confirmed. Stay here; select a room to retry.' : error ? 'Rooms unavailable. Refresh to retry.' : loading ? 'Loading rooms…' : connection === 'offline' ? 'Offline. Reconnect before switching.' : connection === 'error' ? 'Room unavailable. Choose another room.' : connection === 'loading' ? 'Connecting…' : 'Connected'
	const value = { ...navigation, onNavigate: changeRoom, rooms, loading, unavailable: error, disabled, status, refresh: () => setRefresh(value => value + 1) }
	return <RoomContext.Provider value={value}>
		{children}
		{(connection === 'loading' || connection === 'error') && <nav className="journey-room-recovery" aria-label="Room recovery">
			<label htmlFor="journey-room">Room</label>
			<select id="journey-room" value={roomId} disabled={disabled} onChange={event => changeRoom(event.target.value)}>
				{!rooms.includes(roomId) && <option value={roomId} disabled>{roomId} (requested)</option>}
				{rooms.map(room => <option key={room} value={room}>{room}</option>)}
			</select>
			<button type="button" onClick={value.refresh} disabled={loading} aria-label="Refresh rooms">Refresh</button>
			<div className="journey-rooms-status" role="status">{status}</div>
		</nav>}
	</RoomContext.Provider>
}

export function RoomPageMenu() {
	const room = useContext(RoomContext)!
	const [query, setQuery] = useState('')
	const [open, setOpen] = useMenuIsOpen('journey-rooms')
	useEffect(() => { if (!open) setQuery('') }, [open])
	const matching = room.rooms.filter(id => id.toLowerCase().includes(query.trim().toLowerCase()))
	const select = (id: string) => { setOpen(false); room.onNavigate(id) }
	const cancel = () => {
		setOpen(false)
		requestAnimationFrame(() => document.querySelector<HTMLButtonElement>('[data-testid="room-trigger"]')?.focus())
	}
	return <>
		<TldrawUiDropdownMenuRoot id="journey-rooms">
			<TldrawUiDropdownMenuTrigger>
				<TldrawUiButton type="normal" className="journey-room-trigger" data-testid="room-trigger" title={`Room: ${room.roomId}. ${room.status}`} disabled={room.switching}>
					<span className={`journey-room-dot ${room.switching || room.loading ? 'pending' : room.switchError || room.unavailable || room.connection !== 'connected' ? 'unavailable' : ''}`} aria-hidden="true" />
					<span className="journey-room-trigger-label"><span className="journey-room-prefix">Room </span>{room.roomId}</span>
					<TldrawUiButtonIcon icon="chevron-down" small />
				</TldrawUiButton>
			</TldrawUiDropdownMenuTrigger>
			<TldrawUiDropdownMenuContent className="journey-room-menu" align="start" sideOffset={5} collisionPadding={8}>
				<div className="journey-room-heading">Switch room<span>Current: {room.roomId}</span></div>
				<div className="journey-room-search">
					<TldrawUiInput aria-label="Search rooms" placeholder="Search room IDs" value={query} onValueChange={setQuery} onCancel={cancel} onComplete={() => { if (!room.disabled && matching.length === 1) select(matching[0]) }} />
				</div>
				<TldrawUiDropdownMenuGroup>
					<div className="journey-room-options">
						{matching.map(id => <TldrawUiDropdownMenuItem key={id}>
							<TldrawUiButton type="menu" title={id} disabled={room.disabled} onClick={() => select(id)}>
								<TldrawUiButtonLabel>{id}</TldrawUiButtonLabel>
								{id === room.roomId && <TldrawUiButtonIcon icon="check" small />}
							</TldrawUiButton>
						</TldrawUiDropdownMenuItem>)}
						{!matching.length && !room.loading && !room.unavailable && <p className="journey-room-empty">No matching rooms</p>}
					</div>
				</TldrawUiDropdownMenuGroup>
				<div className="journey-room-footer">
					<div className="journey-rooms-status" role="status">{room.status}</div>
					<TldrawUiButton type="normal" disabled={room.loading} onClick={room.refresh} aria-label="Refresh rooms"><TldrawUiButtonLabel>Refresh</TldrawUiButtonLabel></TldrawUiButton>
				</div>
			</TldrawUiDropdownMenuContent>
		</TldrawUiDropdownMenuRoot>
		<span className="journey-room-divider" />
		<DefaultPageMenu />
		{(room.switching || room.switchError || room.connection === 'offline') && <div className="journey-room-feedback journey-rooms-status" role="status">{room.status}</div>}
	</>
}
