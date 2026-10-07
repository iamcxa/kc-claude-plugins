// Disposable preview builder: draws the fictional example into two throwaway rooms, adds hand-drawn
// annotations, grows one release row by two stories, and leaves one room as today's render leaves it
// and one as the proposed render leaves it. Not repository code.
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const KJM = process.env.KJM
if (!KJM) throw new Error('set KJM to a kc-journey-map checkout with node_modules installed')
const need = createRequire(`${KJM}/package.json`)
const lib = (name) => import(pathToFileURL(`${KJM}/lib/${name}`).href)
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
const { parse, stringify } = need('yaml')
const { renderToRoom, buildAllPages, loadJourney } = await lib('render.mjs')
const { note, label } = await lib('records.mjs')
const { carryAnnotations } = await import('./anchor.mjs')

const api = process.env.JOURNEY_API ?? `http://127.0.0.1:${process.env.JOURNEY_API_PORT}`
const example = `${KJM}/skills/kc-journey-map/references/journey.example.yaml`
const dir = mkdtempSync(join(tmpdir(), 'jr-preview-'))
const grown = parse(readFileSync(example, 'utf8'))
grown.steps[0].stories.push(
	{ id: 'reserve-two', card: 'Reserve a second copy', release: 'r1', status: 'unverified' },
	{ id: 'reserve-three', card: 'Reserve a third copy', release: 'r1', status: 'unverified' })
const v2 = join(dir, 'grown.yaml'); writeFileSync(v2, stringify(grown))

const hand = (rec) => ({ ...rec, meta: {} })
const annotations = () => [
	hand(label({ id: 'shape:hand-frame-choose', parentId: 'page:page', text: 'A: discussed Tue', x: 274, y: 926, w: 252, h: 252, index: 'a1', color: 'light-blue', size: 's' })),
	hand(note({ id: 'shape:hand-sticky-reminder', text: 'B: copy for the reminder?', x: 700, y: 1100, index: 'a2', parentId: 'page:page', color: 'yellow' })),
	hand(note({ id: 'shape:hand-sticky-span', text: 'C: both need a date', x: 400, y: 1020, index: 'a3', parentId: 'page:page', color: 'light-green' })),
	hand(label({ id: 'shape:hand-frame-tall', parentId: 'page:page', text: 'D: spans two rows', x: 280, y: 760, w: 240, h: 260, index: 'a4', color: 'orange', size: 's' })),
	hand(note({ id: 'shape:hand-sticky-loose', text: 'E: unrelated', x: 1200, y: 400, index: 'a5', parentId: 'page:page', color: 'light-violet' })),
]
const patch = (room, body) => fetch(`${api}/doc?room=${room}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
const records = async (room) => (await fetch(`${api}/doc?room=${room}`).then((r) => r.json())).snapshot.documents.map((d) => d.state)

for (const [room, carry] of [['today', false], ['carried', true]]) {
	await renderToRoom({ path: example, room, selection: ['story-map'], api })
	const res = await patch(room, { put: annotations(), remove: [] })
	if (res.status !== 200) throw new Error(`annotations rejected: ${res.status} ${await res.text()}`)
	if (carry) {
		const put = buildAllPages(loadJourney(v2), room, ['story-map'])
		const { moved, stranded } = carryAnnotations(await records(room), put, [])
		console.log('carried', moved.map((m) => `${m.id.slice(11)} ${m.dx},${m.dy}`), 'reported', stranded.map((s) => `${s.id.slice(11)} ${s.reason}`))
		const r2 = await patch(room, { put: moved.map((m) => m.record), remove: [] })
		if (r2.status !== 200) throw new Error(`carry rejected: ${r2.status} ${await r2.text()}`)
	}
	const out = await renderToRoom({ path: v2, room, selection: ['story-map'], api })
	console.log(room, 'render', out.status)
}
