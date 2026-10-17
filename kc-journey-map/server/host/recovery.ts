import { canonicalAsset, canonicalRoom, HostError, prepareDoc } from './core'
import type { Host } from './transport'
export async function exportRoom(host: Host, room: string) {
 if (canonicalRoom(room) !== room || !await host.meta.get('room:' + room)) throw new HostError(404, 'room not found')
 const document = await host.document(room, 'GET', null)
 const assets = []
 for (const entry of await host.meta.list('asset:' + room + ':')) {
  const id = entry.key.slice(('asset:' + room + ':').length)
  const asset = await host.getAsset(room, id)
  assets.push({ id, contentType: asset.contentType, bytes: Array.from(asset.data) })
 }
 return { format: 'journey-private-room-1', room, document, assets }
}
export async function restoreRoom(host: Host, archive: any) {
 const { room, document, assets } = archive
 if (archive.format !== 'journey-private-room-1' || !room || canonicalRoom(room) !== room || document?.roomId !== room || !Array.isArray(assets))
  throw new HostError(400, 'invalid room archive')
 const snapshot = prepareDoc('PUT', document.snapshot)
 const ids = new Set()
 for (const asset of assets) {
  if (!asset.id || canonicalAsset(asset.id) !== asset.id || ['.', '..'].includes(asset.id) || ids.has(asset.id) ||
   typeof asset.contentType !== 'string' || !Array.isArray(asset.bytes) || asset.bytes.some((b: any) => !Number.isInteger(b) || b < 0 || b > 255))
   throw new HostError(400, 'invalid asset archive')
  ids.add(asset.id)
 }
 if (await host.meta.get('room:' + room)) throw new HostError(400, 'restore requires an empty target room')
 await host.document(room, 'PUT', snapshot)
 for (const asset of assets) await host.putAsset(room, asset.id, new Uint8Array(asset.bytes), asset.contentType)
 return { room, assets: assets.length }
}
