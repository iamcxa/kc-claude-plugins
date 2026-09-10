#!/usr/bin/env node
// node lib/journey-tldr.mjs export <roomId> <out.tldr>
// node lib/journey-tldr.mjs import <in.tldr>  <roomId>
//
// tldraw's own file format, used for what it is good at: moving a board between tools
// without losing a pixel. It is not a journey file — it stores coordinates and colours,
// not steps and citations. The two compose because `meta.journey` rides inside the
// records, so a board can leave here, be opened in any tldraw, come back, and still be
// read against its journey file.
//
// Import writes the whole document. Anything already in the target room is replaced.

import { execFileSync } from 'node:child_process'
import { readFileSync, writeFileSync } from 'node:fs'

const [mode, a, b] = process.argv.slice(2)
const API = process.env.JOURNEY_API ?? `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`

if (mode === 'export') {
	if (!a || !b) usage()
	const sh = (args) => execFileSync('agent-browser', args, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 })
	sh(['open', `http://localhost:3737/?room=${a}`, '--viewport', '1400x900'])

	// serializeTldrawJson is bound to a live editor, so the export goes through the
	// browser. Ask until the canvas has finished connecting rather than sleeping blind.
	let json
	for (let attempt = 0; attempt < 12; attempt++) {
		const raw = sh(['eval', 'window.serializeTldrawJson ? window.serializeTldrawJson() : Promise.resolve("")']).trim()
		json = JSON.parse(raw)
		if (json) break
		execFileSync('sleep', ['2'])
	}
	if (!json) {
		console.error('export failed: the canvas never finished loading')
		process.exit(1)
	}
	writeFileSync(b, json)
	const parsed = JSON.parse(json)
	const tagged = parsed.records.filter((r) => r.meta?.journey).length
	console.log(`${b} — ${parsed.records.length} records, ${tagged} carrying journey meta`)
	process.exit(0)
}

if (mode === 'import') {
	if (!a || !b) usage()
	const file = JSON.parse(readFileSync(a, 'utf8'))
	if (!Array.isArray(file.records) || !file.schema) {
		console.error('import failed: that is not a tldraw file — no records or schema')
		process.exit(1)
	}

	// A .tldr's records and schema are exactly a TLStoreSnapshot, which loadSnapshot
	// takes, so the file goes in without tldraw having to be imported here.
	const snapshot = { store: Object.fromEntries(file.records.map((r) => [r.id, r])), schema: file.schema }
	const res = await fetch(`${API}/doc?room=${b}`, {
		method: 'PUT',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ snapshot }),
	})
	if (!res.ok) {
		console.error(`import failed: ${res.status} ${await res.text()}`)
		process.exit(1)
	}
	const tagged = file.records.filter((r) => r.meta?.journey).length
	console.log(`${b} — ${file.records.length} records, ${tagged} carrying journey meta`)
	process.exit(0)
}

function usage() {
	console.error('usage: journey-tldr.mjs export <roomId> <out.tldr>')
	console.error('       journey-tldr.mjs import <in.tldr> <roomId>')
	process.exit(2)
}
usage()
