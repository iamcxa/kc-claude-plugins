import { existsSync } from 'node:fs'
import { mkdir, writeFile } from 'node:fs/promises'
import { join, resolve } from 'node:path'

// The browser names the file, so one directory is the difference between a save button
// and a write primitive over the repository.
const DIR = resolve(process.env.JOURNEY_SAVE_DIR ?? './docs/journey')

export function saveFileName(name: string): string {
	const base = (name.split('/').pop() ?? '').replace(/[^a-zA-Z0-9._-]/g, '-').replace(/^[.-]+/, '')
	const stem = base.replace(/\.tldr$/, '')
	return stem ? `${stem}.tldr` : ''
}

export async function saveBoard(name: string, body: string): Promise<{ path: string; records: number }> {
	const file = saveFileName(name)
	if (!file) throw new Error('that name has nothing usable in it')
	const parsed = JSON.parse(body)
	if (!Array.isArray(parsed.records) || !parsed.schema) throw new Error('that is not a tldraw file')
	// Saving before the board syncs would otherwise overwrite last round's file with nothing.
	if (parsed.records.length === 0) throw new Error('the board is empty — nothing saved')
	await mkdir(DIR, { recursive: true })
	const path = join(DIR, file)
	await writeFile(path, body)
	return { path, records: parsed.records.length }
}

export function saveDir(): string {
	return DIR
}

// These files are untracked, so an overwrite has no undo; the button says which it is.
export function saveTarget(name: string): { file: string; exists: boolean } {
	const file = saveFileName(name)
	return { file, exists: file ? existsSync(join(DIR, file)) : false }
}
