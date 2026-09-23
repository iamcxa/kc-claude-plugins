#!/usr/bin/env node
import { renderToRoom, PROJECTION_KEYS, DEFAULT_PROJECTIONS } from './render.mjs'

const argv = process.argv.slice(2).filter((a) => a !== '--force')
const force = process.argv.includes('--force')
const pagesIndex = argv.indexOf('--pages')
const selection = pagesIndex >= 0 ? argv[pagesIndex + 1].split(',').filter(Boolean) : undefined
const positional = pagesIndex >= 0 ? [...argv.slice(0, pagesIndex), ...argv.slice(pagesIndex + 2)] : argv
const [path, room] = positional

const unknown = (selection ?? []).filter((key) => !PROJECTION_KEYS.includes(key))
if (!path || unknown.length) {
	if (unknown.length) console.error(`unknown --pages value(s): ${unknown.join(', ')}`)
	console.error(`usage: journey-render.mjs <journey.yaml> [roomId] [--pages ${PROJECTION_KEYS.join(',')}] [--force]`)
	console.error(`  no --pages renders the default: ${DEFAULT_PROJECTIONS.join(', ')}`)
	process.exit(2)
}

const r = await renderToRoom({ path, room, selection, force })
if (r.refused) {
	console.error(`refused: ${r.refused.length} shape(s) were edited on the canvas since the last render:`)
	for (const id of r.refused) console.error(`  ${id}`)
	console.error('run journey-read.mjs <journey.yaml> <room> --write to keep those edits, or rerun with --force to overwrite them')
	process.exit(1)
}
console.log(r.status, r.shapes, 'shapes ->', r.body)
for (const c of r.coverage ?? []) {
	const gap = c.missing.length ? `  not touched: ${c.missing.join(', ')}` : ''
	console.log(`  ${c.release}: covers ${c.covered}/${c.of} activities${gap}`)
}
