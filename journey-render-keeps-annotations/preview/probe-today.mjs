// Disposable probe: today's renderToRoom against a stub room. Not repository code.
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const KJM = process.env.KJM
if (!KJM) throw new Error('set KJM to a kc-journey-map checkout with node_modules installed')
const need = createRequire(`${KJM}/package.json`)
const lib = (name) => import(pathToFileURL(`${KJM}/lib/${name}`).href)
import http from 'node:http'
import { readFileSync, writeFileSync } from 'node:fs'
const { stringify, parse } = need('yaml')
const { renderToRoom } = await lib('render.mjs')
const { note, label } = await lib('records.mjs')

const store = new Map()
const srv = http.createServer((req, res) => {
	if (req.method === 'GET') {
		res.setHeader('content-type', 'application/json')
		return res.end(JSON.stringify({ snapshot: { documents: [...store.values()].map((state) => ({ state })) } }))
	}
	let body = ''; req.on('data', (c) => (body += c)); req.on('end', () => {
		const { put = [], remove = [] } = JSON.parse(body)
		for (const r of put) store.set(r.id, r); for (const id of remove) store.delete(id)
		res.end('{}')
	})
}).listen(0)
const api = `http://127.0.0.1:${srv.address().port}`

const src = `${KJM}/skills/kc-journey-map/references/journey.example.yaml`
const v1 = join(tmpdir(), 'jr-today-v1.yaml'), v2 = join(tmpdir(), 'jr-today-v2.yaml')
writeFileSync(v1, readFileSync(src, 'utf8'))
const m = parse(readFileSync(src, 'utf8'))
m.steps[0].stories.push({ id: 'reserve-two', card: 'Reserve a second copy', release: 'r1', status: 'unverified' }, { id: 'reserve-three', card: 'Reserve a third copy', release: 'r1', status: 'unverified' })
writeFileSync(v2, stringify(m))

await renderToRoom({ path: v1, room: 'book-pickup', api })
const card = (id) => store.get(`shape:sm-story-${id}`)
const c = card('choose-pickup-day'), r = card('receive-reminder'), far = card('collect-book')
const idx = 'a9'
// a sticky grazing the corner of one card, a frame around another, a sticky touching nothing
const sticky = { ...note({ id: 'shape:hand-sticky', text: 'hand note', x: c.x + 150, y: c.y + 150, index: idx, parentId: 'page:page' }), meta: {} }
const frame = { ...label({ id: 'shape:hand-frame', parentId: 'page:page', text: 'discussed', x: r.x - 26, y: r.y - 26, w: 252, h: 304, index: 'a8', color: 'light-blue', size: 's' }), meta: {} }
const loose = { ...note({ id: 'shape:hand-loose', text: 'loose', x: 3000, y: 3000, index: 'a7', parentId: 'page:page' }), meta: {} }
for (const s of [sticky, frame, loose]) store.set(s.id, s)
const before = Object.fromEntries([sticky, frame, loose].map((s) => [s.id, [s.x, s.y]]))
const out = await renderToRoom({ path: v2, room: 'book-pickup', api })
console.log('result keys', Object.keys(out))
console.log('cards: choose-pickup-day', [c.x, c.y], '->', [card('choose-pickup-day').x, card('choose-pickup-day').y])
for (const id of Object.keys(before)) console.log(id, before[id], '->', [store.get(id).x, store.get(id).y])
srv.close()
