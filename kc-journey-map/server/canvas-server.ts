import { hostname } from 'node:os'
import { createInterface } from 'node:readline'
import websocketPlugin from '@fastify/websocket'
import fastify from 'fastify'
import { NodeHost } from './host/node'
import { admit, handle } from './host/transport'
import { HostError } from './host/core'
import { exportRoom, restoreRoom } from './host/recovery'

const host = new NodeHost()
const app = fastify({ bodyLimit: Number(process.env.JOURNEY_BODY_LIMIT ?? 64 * 1024 * 1024) })
await app.register(websocketPlugin)
app.removeAllContentTypeParsers()
app.addContentTypeParser('*', { parseAs: 'buffer' }, (_req, body, done) => done(null, body))
const headersOf = (req: any) => new Headers(Object.fromEntries(Object.entries(req.headers).filter(([, v]) => v !== undefined).map(([k, v]) => [k, String(v)])))
app.get('/connect/:roomId', {
 websocket: true,
 preValidation: async (req, res) => {
  try {
   const admission = await admit(host, headersOf(req), (req.params as any).roomId, false, true)
   ;(req as any).journeyAdmission = admission
   await host.openRoom(admission.room)
  } catch (e) { return res.status(e instanceof HostError ? e.status : 503).send({ error: e instanceof HostError ? e.message : 'room unavailable' }) }
 },
}, (socket, req) => {
 const { room: id, admission } = (req as any).journeyAdmission
 const room = host.rooms.get(id)!.room
 const sessionId = String((req.query as any).sessionId || '')
 host.track(socket, admission, id)
 room.handleSocketConnect({ sessionId, socket: { send: (data: string) => socket.send(data), close: (code?: number, reason?: string) => socket.close(code, reason), get readyState() { return socket.readyState } } as any })
 socket.on('message', async data => {
  if (!await host.socketAllowed(admission, id)) { socket.close(1008, 'credential invalid'); return }
  room.handleSocketMessage(sessionId, data.toString())
 })
 socket.on('close', () => room.handleSocketClose(sessionId))
 socket.on('error', () => room.handleSocketError(sessionId))
})
app.all('/*', async (req, res) => {
 const response = await handle(host, new Request('http://localhost' + req.raw.url, {
  method: req.method, headers: headersOf(req), ...(['GET', 'HEAD'].includes(req.method) ? {} : { body: req.body as BodyInit }),
 }))
 res.status(response.status)
 for (const [key, value] of response.headers) res.header(key, value)
 return res.send(Buffer.from(await response.arrayBuffer()))
})
if (process.env.JOURNEY_CONTROL_STDIO === '1') {
 const control = createInterface({ input: process.stdin })
 control.on('line', async line => {
  try {
   const command = JSON.parse(line)
   const result = command.op === 'revoke' ? await host.revoke(command.credentialId)
    : command.op === 'export' ? await exportRoom(host, command.room)
    : command.op === 'restore' ? await restoreRoom(host, command.archive)
    : (() => { throw new Error('unknown operator command') })()
   console.log(JSON.stringify({ control: command.id, result }))
  } catch { console.log(JSON.stringify({ controlError: 'operator command failed' })) }
 })
}
const address = await app.listen({ port: host.port, host: '127.0.0.1' })
const printHost = (process.env.JOURNEY_ALLOWED_HOSTS || '').split(',').find(Boolean) || hostname()
console.log(`doc API on ${address}  (canvas: http://${printHost}:3737/?room=default)`)
for (const signal of ['SIGINT', 'SIGTERM'] as const) process.once(signal, () => { host.close(); app.close().finally(() => process.exit()) })
