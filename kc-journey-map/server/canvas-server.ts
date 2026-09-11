// Adapted from tldraw's `templates/simple-server-example` (MIT).
import websocketPlugin from '@fastify/websocket'
import fastify from 'fastify'
import type { RawData } from 'ws'
import { createTLSchema } from '@tldraw/tlschema'
import { activeRooms, listRooms, makeOrLoadRoom, sanitizeRoomId } from './rooms'

// Overridable so a check can run its own server on its own port instead of silently
// talking to whichever canvas the developer already had open.
const PORT = Number(process.env.JOURNEY_API_PORT ?? 5858)
const DEFAULT_ROOM = 'default'

// Validate PATCH records before writing so malformed client input receives detailed HTTP 400 diagnostics.
const schema = createTLSchema()

function validateRecord(record: any): string | null {
	if (!record || typeof record !== 'object') return 'record is not an object'
	const { id, typeName } = record
	if (typeof id !== 'string') return 'record.id must be a string'
	if (typeof typeName !== 'string') return `record ${id} has no typeName`
	const type = (schema.types as Record<string, any>)[typeName]
	if (!type) return `record ${id} has unknown typeName "${typeName}"`
	try {
		type.validate(record)
		return null
	} catch (e) {
		return `record ${id} failed validation: ${(e as Error).message}`
	}
}

const app = fastify()
app.register(websocketPlugin)

function roomIdOf(req: any): string {
	return sanitizeRoomId((req.query as any)?.room || DEFAULT_ROOM)
}

app.register(async (app) => {
	app.get('/connect/:roomId', { websocket: true }, async (socket, req) => {
		const roomId = (req.params as any).roomId as string
		const sessionId = (req.query as any)?.['sessionId'] as string

		// Messages that arrive before the room finishes loading are collected and replayed.
		const caughtMessages: RawData[] = []
		const collect = (message: RawData) => caughtMessages.push(message)
		socket.on('message', collect)

		const room = makeOrLoadRoom(roomId)
		room.handleSocketConnect({ sessionId, socket })

		socket.off('message', collect)
		for (const message of caughtMessages) socket.emit('message', message)
	})

	app.get('/health', async () => ({
		ok: true,
		tldraw: '5.4.0',
		port: PORT,
		rooms: listRooms(),
		active: activeRooms(),
	}))

	// Whole-document snapshot: {clock, documents:[{state, lastChangedClock}], schema, tombstones}
	app.get('/doc', async (req) => {
		const roomId = roomIdOf(req)
		return { roomId, snapshot: makeOrLoadRoom(roomId).getCurrentSnapshot() }
	})

	// Incremental write. `put` entries are COMPLETE records, not property fragments.
	app.patch('/doc', async (req, res) => {
		const roomId = roomIdOf(req)
		const body = (req.body ?? {}) as { put?: any[]; remove?: string[] }
		const put = body.put ?? []
		const remove = body.remove ?? []
		if (!Array.isArray(put) || !Array.isArray(remove)) {
			return res.status(400).send({ error: 'put and remove must be arrays' })
		}

		const errors = put.map(validateRecord).filter((e): e is string => e !== null)
		if (errors.length) return res.status(400).send({ error: 'validation failed', errors })

		const room = makeOrLoadRoom(roomId)
		await room.updateStore((store) => {
			for (const record of put) store.put(record)
			for (const id of remove) store.delete(id)
		})
		return { roomId, put: put.length, removed: remove.length, clock: room.getCurrentDocumentClock() }
	})

	// Whole-document replace. Every page not in the snapshot is dropped.
	app.put('/doc', async (req, res) => {
		const roomId = roomIdOf(req)
		const body = req.body as any
		const snapshot = body?.snapshot ?? body
		if (!snapshot?.documents && !snapshot?.store) {
			return res.status(400).send({ error: 'body must be a RoomSnapshot or TLStoreSnapshot' })
		}
		const room = makeOrLoadRoom(roomId)
		room.loadSnapshot(snapshot)
		return { roomId, clock: room.getCurrentDocumentClock() }
	})
})

app.listen({ port: PORT, host: '127.0.0.1' }, (err, address) => {
	if (err) {
		console.error(err)
		process.exit(1)
	}
	console.log(`doc API on ${address}  (canvas: http://localhost:3737/?room=${DEFAULT_ROOM})`)
})
