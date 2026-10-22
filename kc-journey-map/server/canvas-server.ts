import { fstatSync } from 'node:fs'
import { hostname } from 'node:os'
import { createInterface } from 'node:readline'
import websocketPlugin from '@fastify/websocket'
import fastify from 'fastify'
import { audited } from './host/audit'
import { NodeHost } from './host/node'
import { startLocalOwner } from './host/local-owner'
import { admit, handle } from './host/transport'
import { HostError } from './host/core'
import { exportRoom, restoreRoom } from './host/recovery'

const host = new NodeHost()
const stopOwner = await startLocalOwner(host)
const app = fastify({ bodyLimit: Number(process.env.JOURNEY_BODY_LIMIT ?? 64 * 1024 * 1024) })
await app.register(websocketPlugin)
app.removeAllContentTypeParsers()
app.addContentTypeParser('*', { parseAs: 'buffer' }, (_req, body, done) => done(null, body))
const headersOf = (req: any) => new Headers(Object.fromEntries(Object.entries(req.headers).filter(([, v]) => v !== undefined).map(([k, v]) => [k, String(v)])))
app.get('/connect/:roomId', {
 websocket: true,
 preValidation: async (req, res) => {
  try {
   const admission = await admit(host, headersOf(req), (req.params as any).roomId, false, true, new URL(req.raw.url!, host.origin))
   ;(req as any).journeyAdmission = admission
   await host.openRoom(admission.room)
  } catch (e) { return res.status(e instanceof HostError ? e.status : 503).send({ error: e instanceof HostError ? e.message : 'room unavailable' }) }
 },
}, (socket, req) => {
 const { room: id, admission } = (req as any).journeyAdmission
 const room = host.rooms.get(id)!.room
 const sessionId = String((req.query as any).sessionId || '')
 const ready=(async()=>{await host.track(socket,admission,id);if(socket.readyState!==1)throw new Error('socket closed');room.handleSocketConnect({ sessionId, socket: { send: (data: string) => host.send(socket, data), close: (code?: number, reason?: string) => socket.close(code, reason), get readyState() { return socket.readyState } } as any })})().catch(()=>{socket.close(1008,'authority denied');return false})
 socket.on('message', async data => {
  if(await ready===false)return
  if (!await host.socketAllowed(admission, id)) { socket.close(1008, 'credential invalid'); return }
  try {
   const message=data.toString(),batch=JSON.parse(message)
   if(batch.type==='push')await audited(host,admission,id,'socket:push',async()=>{room.handleSocketMessage(sessionId,message)},undefined,'admitted')
   else room.handleSocketMessage(sessionId,message)
  } catch {socket.close(1011,'mutation outcome unknown')}
 })
 socket.on('close', () => room.handleSocketClose(sessionId))
 socket.on('error', () => room.handleSocketError(sessionId))
})
app.all('/*', async (req, res) => {
 const response = await handle(host, new Request('http://localhost' + req.raw.url, {
  method: req.method, headers: headersOf(req), ...(['GET', 'HEAD'].includes(req.method) ? {} : { body: req.body as BodyInit }),
 }))
 res.status(response.status)
 for (const [key, value] of response.headers) if (key !== 'set-cookie') res.header(key, value)
 if (response.headers.getSetCookie().length) res.header('set-cookie', response.headers.getSetCookie())
 return res.send(Buffer.from(await response.arrayBuffer()))
})
const ownerControl = () => [0,1].every(fd=>{const s=fstatSync(fd);return (s.isFIFO()||s.isSocket())&&s.uid===process.geteuid?.()&&!(s.mode&0o077)})
if (process.env.JOURNEY_CONTROL_STDIO === '1') {
 const control = createInterface({ input: process.stdin })
 control.on('line', async line => {
  try {
   const command = JSON.parse(line)
   const result = command.op === 'revoke' ? await host.revoke(command.credentialId)
    : command.op === 'owner-bind' && command.writersStopped===true && ownerControl() && host.nativeAccount && host.humanConfig ? await host.meta.human!('owner-bind',command.input)
    : ['member-enroll','member-inspect'].includes(command.op) && command.writersStopped===true && ownerControl() ? await host.memberOperation(command.op.slice(7),command.input)
    : ['disable-member', 'set-room'].includes(command.op) && host.humanConfig ? await host.meta.human!(command.op, command)
    : command.op === 'export' ? await exportRoom(host, command.room)
    : command.op === 'restore' ? await restoreRoom(host, command.archive)
    : (() => { throw new Error('unknown operator command') })()
   console.log(JSON.stringify({ control: command.id, result }))
  } catch { console.log(JSON.stringify({ controlError: 'operator command failed' })) }
 })
}
const address = await app.listen({ port: host.port, host: '127.0.0.1' })
host.port = (app.server.address() as { port: number }).port
const printHost = (process.env.JOURNEY_ALLOWED_HOSTS || '').split(',').find(Boolean) || hostname()
console.log(`doc API on ${address}  (canvas: http://${printHost}:3737/?room=default)`)
for (const signal of ['SIGINT', 'SIGTERM'] as const) process.once(signal, () => { stopOwner(); host.close(); app.close().finally(() => process.exit()) })
