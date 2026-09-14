#!/usr/bin/env node
// Run against an explicitly started isolated canvas frontend; each run owns a fresh room.
import { execFileSync } from 'node:child_process'
import { randomUUID } from 'node:crypto'
import { readFileSync } from 'node:fs'

if (!process.argv[2]) throw new Error('Pass the origin of a local frontend you started for this test.')
const url = new URL(process.argv[2])
if (url.protocol !== 'http:' || !['localhost', '127.0.0.1'].includes(url.hostname) ||
	url.username || url.password || url.search || url.hash || url.pathname !== '/') {
	throw new Error('Pass an isolated local frontend origin, without credentials, a room, or a query.')
}
const session = `sequence-smoke-${randomUUID()}`
url.searchParams.set('room', session)
const source = readFileSync(new URL('../skills/kc-journey-map/references/example/book-pickup-sequence.mmd', import.meta.url), 'utf8')
const browser = (args, input) => execFileSync('agent-browser', ['--session', session, ...args], { encoding: 'utf8', input, timeout: 60000 })

async function verify(source) {
	const editor = window.editor
	const assert = (condition, message) => { if (!condition) throw new Error(message) }
	const records = () => editor.store.allRecords().filter((r) => ['shape', 'binding', 'page', 'document'].includes(r.typeName))
	const before = () => new Map(records().map((r) => [r.id, JSON.stringify(r)]))
	const preserved = (snapshot) => {
		for (const [id, json] of snapshot) assert(JSON.stringify(editor.store.get(id)) === json, `changed existing record ${id}`)
	}
	const text = (shape) => JSON.stringify(shape.props.richText ?? '')
	editor.createShapes([{ id: 'shape:manual', type: 'geo', x: 30, y: 20, props: { w: 100, h: 100 } }])
	editor.createPage({ id: 'page:release', name: 'Release board' })
	const original = before()
	const input = { source, sourcePath: 'docs/journey/book-pickup-sequence.mmd', name: 'Book pickup — sequence' }
	const first = await window.addSequencePage(input)
	preserved(original)
	const shapes = editor.getCurrentPageShapes()
	const arrows = shapes.filter((s) => s.type === 'arrow')
	assert(arrows.length === 6, 'expected six native message arrows')
	for (let number = 1; number <= 6; number++) assert(arrows.some((s) => text(s).includes(`${number}  `)), `missing autonumber ${number}`)
	assert(shapes.some((s) => text(s).includes('alt [Available]')), 'missing native branch label')
	assert(shapes.every((s) => !s.meta.journey && s.type !== 'image'), 'auxiliary shapes must be native and untagged as journey')
	assert(editor.getPage(first.pageId).meta.sequence.source === input.sourcePath, 'missing source provenance')
	const edited = arrows[0]
	editor.updateShapes([{ id: edited.id, type: edited.type, props: { richText: { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Native reviewer edit' }] }] } } }])
	assert(text(editor.getShape(edited.id)).includes('Native reviewer edit'), 'native text edit did not stick')
	const editedSnapshot = before()
	const second = await window.addSequencePage(input)
	assert(second.name === `${first.name} (2)` && second.pageId !== first.pageId, 'rerender must add a distinguishable page')
	preserved(editedSnapshot)
	const failureSnapshot = before()
	const pageBeforeFailure = editor.getCurrentPageId()
	let refused = false
	try { await window.addSequencePage({ ...input, source: 'sequenceDiagram\nAlice->>\n' }) } catch { refused = true }
	assert(refused, 'malformed sequence must refuse')
	assert(records().length === failureSnapshot.size, 'malformed input added records')
	preserved(failureSnapshot)
	assert(editor.getCurrentPageId() === pageBeforeFailure, 'malformed input changed active page')
	await window.addSequencePage({ ...input, source: source.replace('    autonumber\n', ''), name: 'Unnumbered sequence' })
	assert(editor.getCurrentPageShapes().filter((s) => s.type === 'arrow').every((s) => !/\b[1-6]  /.test(text(s))), 'explicit unnumbered source changed')
	const backup = JSON.parse(await window.serializeTldrawJson())
	assert(backup.records.some((r) => r.id === edited.id && text(r).includes('Native reviewer edit')), 'native backup lost edit')
	return { first, second, numberedMessages: arrows.length, preservedRecords: failureSnapshot.size, malformed: 'refused', backup: 'native edit retained' }
}

try {
	browser(['open', url.href])
	browser(['wait', '--fn', 'typeof window.addSequencePage === "function"'])
	console.log(browser(['eval', '--stdin'], `(${verify.toString()})(${JSON.stringify(source)})`))
} finally {
	browser(['close'])
}
