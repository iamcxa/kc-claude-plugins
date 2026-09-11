#!/usr/bin/env node
import { renderToRoom, PROJECTION_KEYS, DEFAULT_PROJECTIONS } from './render.mjs'

const argv = process.argv.slice(2)
const pagesIndex = argv.indexOf('--pages')
const selection = pagesIndex >= 0 ? argv[pagesIndex + 1].split(',').filter(Boolean) : undefined
const positional = pagesIndex >= 0 ? [...argv.slice(0, pagesIndex), ...argv.slice(pagesIndex + 2)] : argv
const [path, room] = positional

const unknown = (selection ?? []).filter((key) => !PROJECTION_KEYS.includes(key))
if (!path || unknown.length) {
	if (unknown.length) console.error(`unknown --pages value(s): ${unknown.join(', ')}`)
	console.error(`usage: journey-render.mjs <journey.yaml> [roomId] [--pages ${PROJECTION_KEYS.join(',')}]`)
	console.error(`  no --pages renders the default: ${DEFAULT_PROJECTIONS.join(', ')}`)
	process.exit(2)
}

const r = await renderToRoom({ path, room, selection })
console.log(r.status, r.shapes, 'shapes ->', r.body)
for (const c of r.coverage ?? []) {
	const gap = c.missing.length ? `  not touched: ${c.missing.join(', ')}` : ''
	console.log(`  ${c.release}: covers ${c.covered}/${c.of} activities${gap}`)
}
