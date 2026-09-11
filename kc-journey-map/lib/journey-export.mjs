#!/usr/bin/env node

import { execFileSync } from 'node:child_process'
import { writeFileSync } from 'node:fs'

const [room, out, pageId = 'page:page'] = process.argv.slice(2)
if (!room || !out) {
	console.error('usage: journey-export.mjs <roomId> <out.png> [pageId]')
	process.exit(2)
}

const sh = (args) => execFileSync('agent-browser', args, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 })

sh(['open', `http://localhost:3737/?room=${room}`, '--viewport', '1600x1000'])

const script = `
(async () => {
  const e = window.editor
  if (!e) return JSON.stringify({ error: 'the canvas has not finished loading' })
  e.setCurrentPage(${JSON.stringify(pageId)})
  const ids = [...e.getCurrentPageShapeIds()]
  if (!ids.length) return JSON.stringify({ error: 'that page has no shapes' })
  const { blob, width, height } = await e.toImage(ids, { format: 'png', scale: 2, background: true })
  const buf = new Uint8Array(await blob.arrayBuffer())
  let s = ''
  for (let i = 0; i < buf.length; i += 8192) s += String.fromCharCode(...buf.subarray(i, i + 8192))
  return JSON.stringify({ width, height, b64: btoa(s) })
})()
`

let payload
for (let attempt = 0; attempt < 12; attempt++) {
	const raw = sh(['eval', script]).trim()
	try {
		payload = JSON.parse(JSON.parse(raw))
	} catch {
		payload = { error: raw.slice(0, 200) }
	}
	if (!payload.error) break
	execFileSync('sleep', ['2'])
}

if (payload?.error) {
	console.error(`export failed: ${payload.error}`)
	process.exit(1)
}

writeFileSync(out, Buffer.from(payload.b64, 'base64'))
console.log(`${out} — ${payload.width}x${Math.round(payload.height)}`)
