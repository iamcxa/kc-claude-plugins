#!/usr/bin/env node
// node lib/journey-render.mjs <journey.yaml> [roomId]
import { renderToRoom } from './render.mjs'
const [path, room, ...extra] = process.argv.slice(2)
if (!path || path.startsWith('--') || room?.startsWith('--') || extra.length) {
 console.error('usage: journey-render.mjs <journey.yaml> [roomId]')
 process.exit(2)
}
const r = await renderToRoom({ path, room })
console.log(r.status, r.shapes, 'shapes ->', r.body)
for (const c of r.coverage ?? []) {
 const gap = c.missing.length ? `  not touched: ${c.missing.join(', ')}` : ''
 console.log(`  ${c.release}: covers ${c.covered}/${c.of} activities${gap}`)
}
