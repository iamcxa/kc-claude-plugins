// Adapted from tldraw's `templates/simple-server-example` (MIT).
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { join } from 'node:path'
import type { Readable } from 'node:stream'

const DIR = process.env.JOURNEY_ASSETS_DIR ?? './.assets'

// find-my-way decodes route params, so an encoded `../` would escape DIR without this.
export function sanitizeAssetId(id: string): string {
	return id.replace(/[^a-zA-Z0-9._-]/g, '_')
}

// `nosniff` makes a browser refuse to paint an image served as octet-stream.
export async function storeAsset(id: string, stream: Readable, contentType?: string): Promise<void> {
	await mkdir(DIR, { recursive: true })
	const path = join(DIR, sanitizeAssetId(id))
	await writeFile(path, stream)
	await writeFile(`${path}.type`, contentType || 'application/octet-stream')
}

export async function loadAsset(id: string): Promise<{ data: Buffer; contentType: string }> {
	const path = join(DIR, sanitizeAssetId(id))
	const data = await readFile(path)
	const contentType = await readFile(`${path}.type`, 'utf8').catch(() => 'application/octet-stream')
	return { data, contentType }
}
