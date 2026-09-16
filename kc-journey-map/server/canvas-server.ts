// Adapted from tldraw's `templates/simple-server-example` (MIT).
import { hostname } from 'node:os'
import websocketPlugin from '@fastify/websocket'
import fastify from 'fastify'
import type { RawData } from 'ws'
import { createTLSchema } from '@tldraw/tlschema'
import { loadAsset, storeAsset } from './assets'
import { activeRooms, listRooms, makeOrLoadRoom, sanitizeRoomId } from './rooms'
import { saveBoard, saveDir, saveTarget } from './save'
import { startTunnel, stopTunnel, tunnelStatus } from './tunnel'

// Separate ports keep checks from mutating another running canvas.
const PORT = Number(process.env.JOURNEY_API_PORT ?? 5858)
const DEFAULT_ROOM = 'default'

// Same allowlist source as vite.config.mts: the first operator-configured name, so the
// printed URL resolves from the viewer's machine even when os.hostname() does not.
const PRINT_HOST = (process.env.JOURNEY_ALLOWED_HOSTS ?? '').split(',').map((h) => h.trim()).find(Boolean) ?? hostname()

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

// A .tldr carrying inlined image bytes exceeds fastify's 1 MiB default on PUT /doc.
const BODY_LIMIT = Number(process.env.JOURNEY_BODY_LIMIT ?? 64 * 1024 * 1024)

const app = fastify({ bodyLimit: BODY_LIMIT })
app.register(websocketPlugin)

function roomIdOf(req: any): string {
	return sanitizeRoomId((req.query as any)?.room || DEFAULT_ROOM)
}

app.register(async (app) => {
	app.get('/connect/:roomId', { websocket: true }, async (socket, req) => {
		const roomId = (req.params as any).roomId as string
		const sessionId = (req.query as any)?.['sessionId'] as string

		const caughtMessages: RawData[] = []
		const collect = (message: RawData) => caughtMessages.push(message)
		socket.on('message', collect)

		const room = makeOrLoadRoom(roomId)
		room.handleSocketConnect({ sessionId, socket })

		socket.off('message', collect)
		for (const message of caughtMessages) socket.emit('message', message)
	})

	app.addContentTypeParser('*', (_req, _payload, done) => done(null))

	app.put('/uploads/:id', async (req, res) => {
		await storeAsset((req.params as any).id as string, req.raw, req.headers['content-type'])
		return res.send({ ok: true })
	})

	app.get('/uploads/:id', async (req, res) => {
		const { data, contentType } = await loadAsset((req.params as any).id as string)
		res.header('Content-Security-Policy', "default-src 'none'")
		res.header('X-Content-Type-Options', 'nosniff')
		res.header('Content-Type', contentType)
		return res.send(data)
	})

	app.get('/save', async (req) => {
		const name = (req.query as any)?.name as string | undefined
		return { dir: saveDir(), ...(name ? saveTarget(name) : {}) }
	})

	app.post('/save', async (req, res) => {
		const body = (req.body ?? {}) as { name?: string; file?: string }
		if (typeof body.name !== 'string' || typeof body.file !== 'string') {
			return res.status(400).send({ error: 'name and file are required' })
		}
		try {
			return await saveBoard(body.name, body.file)
		} catch (e) {
			return res.status(400).send({ error: (e as Error).message })
		}
	})

	app.get('/tunnel', async () => await tunnelStatus())

	app.post('/tunnel', async (_req, res) => {
		const result = await startTunnel()
		if ('error' in result) return res.status(result.status).send({ error: result.error })
		return { ...(await tunnelStatus()), url: result.url }
	})

	app.delete('/tunnel', async () => {
		const stopped = stopTunnel()
		return { stopped, ...(await tunnelStatus()) }
	})

	app.get('/health', async () => ({
		ok: true,
		tldraw: '5.4.0',
		port: PORT,
		rooms: listRooms(),
		active: activeRooms(),
	}))

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
	// The doc API itself stays loopback-only; this is the frontend port the operator opens.
	console.log(`doc API on ${address}  (canvas: http://${PRINT_HOST}:3737/?room=${DEFAULT_ROOM})`)
})
