// Adapted from tldraw's `templates/simple-server-example` (MIT).
import { mkdirSync, readdirSync } from 'fs'
import { join } from 'path'
import { NodeSqliteWrapper, SQLiteSyncStorage, TLSocketRoom } from '@tldraw/sync-core'
import { DatabaseSync } from 'node:sqlite'

// Rooms are a rendering cache, never the source of truth. The journey file in the
// repository is; a room can be deleted and rebuilt from it.
const DIR = process.env.JOURNEY_ROOMS_DIR ?? './.rooms'
mkdirSync(DIR, { recursive: true })

export function sanitizeRoomId(roomId: string): string {
	return roomId.replace(/[^a-zA-Z0-9_-]/g, '_')
}

const rooms = new Map<string, { room: TLSocketRoom<any, void>; db: DatabaseSync }>()

export function makeOrLoadRoom(roomId: string): TLSocketRoom<any, void> {
	roomId = sanitizeRoomId(roomId)

	const existing = rooms.get(roomId)
	if (existing && !existing.room.isClosed()) return existing.room

	const db = new DatabaseSync(join(DIR, `${roomId}.db`))
	const sql = new NodeSqliteWrapper(db)
	const storage = new SQLiteSyncStorage({ sql })

	// The room is kept open after the last socket leaves. A PATCH must be able to reach
	// a room nobody has open, and reopening on every request would drop the sync clock.
	const room = new TLSocketRoom({ storage })

	rooms.set(roomId, { room, db })
	return room
}

export function listRooms(): string[] {
	return readdirSync(DIR)
		.filter((f) => f.endsWith('.db'))
		.map((f) => f.slice(0, -3))
}

export function activeRooms(): Array<{ roomId: string; sessions: number; clock: number }> {
	return [...rooms.entries()].map(([roomId, { room }]) => ({
		roomId,
		sessions: room.getNumActiveSessions(),
		clock: room.getCurrentDocumentClock(),
	}))
}
