#!/usr/bin/env node
// node lib/journey-render.mjs <journey.yaml> [roomId]
import { renderToRoom } from './render.mjs'

const [path, room] = process.argv.slice(2)
if (!path) {
	console.error('usage: journey-render.mjs <journey.yaml> [roomId]')
	process.exit(2)
}
const r = await renderToRoom({ path, room })
console.log(r.status, r.shapes, 'shapes ->', r.body)
