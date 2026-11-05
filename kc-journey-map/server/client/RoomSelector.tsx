import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { DefaultPageMenu, TldrawUiButton, TldrawUiButtonIcon, TldrawUiButtonLabel, TldrawUiDropdownMenuContent, TldrawUiDropdownMenuGroup, TldrawUiDropdownMenuItem, TldrawUiDropdownMenuRoot, TldrawUiDropdownMenuTrigger, TldrawUiInput, useMenuIsOpen } from 'tldraw'
import { journeyFetch, journeyApi, type HumanContext } from './api'
import './room-selector.css'

export type ConnectionState = 'loading' | 'connected' | 'offline' | 'error'
type CatalogRoom = { roomId: string; displayName: string }
type RoomNavigation = { roomId: string; human: HumanContext | null; connection: ConnectionState; switching: boolean; switchError: string; frozen: boolean; onDenied: () => void; onNavigate: (room: string) => void }
type RoomInventory = RoomNavigation & { rooms: CatalogRoom[]; loading: boolean; unavailable: boolean; disabled: boolean; status: string; refresh: () => void }
const RoomContext = createContext<RoomInventory | null>(null)

export function RoomSelector({ children, ...navigation }: RoomNavigation & { children: ReactNode }) {
	const { roomId, human, connection, switching, switchError, frozen, onDenied, onNavigate } = navigation
	const [rooms, setRooms] = useState<CatalogRoom[]>([])
	const [error, setError] = useState(false)
	const [loading, setLoading] = useState(true)
	const [refresh, setRefresh] = useState(0)
	useEffect(() => {
		if (frozen) return
		const controller = new AbortController()
		setLoading(true)
		setError(false)
		journeyFetch(journeyApi(human ? '/auth/rooms' : '/health'), { signal: controller.signal })
			.then(async response => {
				if (!response.ok) { if (human && [401, 403].includes(response.status)) onDenied(); throw new Error('Room inventory unavailable') }
				const result = await response.json()
				const rows = human ? result.rooms : result.rooms?.map((roomId: string) => ({ roomId, displayName: roomId }))
    if (human && (typeof result.memberId !== 'string' || typeof result.backendId !== 'string')) throw new Error('Invalid inventory context')
    if (human && (result.memberId !== human.member || result.backendId !== human.backend)) { onDenied(); throw new Error('Identity changed') }
    if (!Array.isArray(rows) || rows.some((room: CatalogRoom) => !room || typeof room.roomId !== 'string' || !room.roomId || typeof room.displayName !== 'string')) throw new Error('Invalid inventory')
    if (!controller.signal.aborted) setRooms([...new Map<string, CatalogRoom>(rows.map((room: CatalogRoom) => [room.roomId, room])).values()].sort((a, b) => a.roomId.localeCompare(b.roomId)))
			})
			.catch(() => { if (!controller.signal.aborted) { setError(true) } })
			.finally(() => { if (!controller.signal.aborted) setLoading(false) })
		return () => controller.abort()
	}, [roomId, refresh, human?.member, human?.backend, human?.signInAt, frozen, onDenied])
	const changeRoom = (next: string) => {
		if (next === roomId || !rooms.some(room => room.roomId === next)) return
		onNavigate(next)
	}
	const disabled = !frozen && (loading || error || switching || connection === 'offline')
	const status = frozen ? switchError : switching ? 'Confirming edits and connecting target…' : error ? 'Rooms unavailable. Refresh to retry.' : loading ? 'Loading rooms…' : switchError || (connection === 'offline' ? 'Offline. Reconnect before switching.' : connection === 'error' ? 'Room unavailable. Choose another room.' : connection === 'loading' ? 'Connecting…' : 'Connected')
	const value = { ...navigation, onNavigate: changeRoom, rooms, loading, unavailable: error, disabled, status, refresh: () => setRefresh(value => value + 1) }
	return <RoomContext.Provider value={value}>
		{children}
		{!frozen && (connection === 'loading' || connection === 'error') && <nav className="journey-room-recovery" aria-label="Room recovery">
			<label htmlFor="journey-room">Room</label>
			<select id="journey-room" value={roomId} disabled={disabled} onChange={event => changeRoom(event.target.value)}>
				{!rooms.some(room => room.roomId === roomId) && <option value={roomId} disabled>{roomId} (requested)</option>}
				{rooms.map(room => <option key={room.roomId} value={room.roomId}>{room.displayName} · {room.roomId}</option>)}
			</select>
			<button type="button" onClick={value.refresh} disabled={loading || frozen} aria-label="Refresh rooms">Refresh</button>
			<div className="journey-rooms-status" role="status">{status}</div>
		</nav>}
	</RoomContext.Provider>
}

export function RoomPageMenu() {
	const room = useContext(RoomContext)!
	const [query, setQuery] = useState('')
	const [open, setOpen] = useMenuIsOpen('journey-rooms')
	useEffect(() => { if (!open) setQuery('') }, [open])
	const matching = room.rooms.filter(item => (item.roomId + ' ' + item.displayName).toLowerCase().includes(query.trim().toLowerCase()))
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
					<TldrawUiInput aria-label="Search rooms" placeholder="Search names or room IDs" value={query} onValueChange={setQuery} onCancel={cancel} onComplete={() => { if (!room.disabled && matching.length === 1) select(matching[0].roomId) }} />
				</div>
				<TldrawUiDropdownMenuGroup>
					<div className="journey-room-options">
						{matching.map(({ roomId: id, displayName }) => <TldrawUiDropdownMenuItem key={id}>
							<TldrawUiButton type="menu" data-room-id={id} title={displayName + ' · ' + id} disabled={room.disabled} onClick={() => select(id)}>
								<TldrawUiButtonLabel><span>{room.frozen ? 'Open separately: ' : ''}{displayName}</span>{displayName !== id && <small>{id}</small>}</TldrawUiButtonLabel>
								{id === room.roomId && <TldrawUiButtonIcon icon="check" small />}
							</TldrawUiButton>
						</TldrawUiDropdownMenuItem>)}
						{!matching.length && !room.loading && !room.unavailable && <p className="journey-room-empty">{room.rooms.length ? 'No matching rooms' : 'No permitted registered rooms'}</p>}
					</div>
				</TldrawUiDropdownMenuGroup>
				<div className="journey-room-footer">
					<div className="journey-rooms-status" role="status">{room.status}</div>
					<TldrawUiButton type="normal" disabled={room.loading || room.frozen} onClick={room.refresh} aria-label="Refresh rooms"><TldrawUiButtonLabel>Refresh</TldrawUiButtonLabel></TldrawUiButton>
				</div>
			</TldrawUiDropdownMenuContent>
		</TldrawUiDropdownMenuRoot>
		<span className="journey-room-divider" />
		<DefaultPageMenu />
		{(room.frozen || room.switching || room.switchError || room.connection === 'offline') && <div className="journey-room-feedback journey-rooms-status" role="status">{room.status}</div>}
	</>
}
