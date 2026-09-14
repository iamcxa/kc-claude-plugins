import assert from 'node:assert/strict'
import { test } from 'node:test'
import { buildStoryMap } from './storymap.mjs'
import { buildJourneyBoard } from './render.mjs'
import { fixtureModel as model } from './fixture.mjs'
import { fitHeight } from './records.mjs'
import { createTLSchema } from '@tldraw/tlschema'

const kinds = (put) => new Set(put.map((r) => r.meta?.journey?.kind).filter(Boolean))

test('the story map draws every element the method calls for', () => {
	const k = kinds(buildStoryMap(model))
	for (const kind of [
		'persona',
		'now',
		'one-journey',
		'activity',
		'story',
		'story-border', 'status-legend',
		'story-question',
		'ownership',
		'release-line',
		'release-label',
	]) {
		assert.ok(k.has(kind), `story map is missing ${kind}`)
	}
})

const kindOf = (put, kind) => put.filter((r) => r.meta?.journey?.kind === kind)
const byId = (put, id) => put.find((r) => r.id === id)

test('a story is drawn in its own release band, not its declaring order', () => {
	const put = buildStoryMap(model)
	const line = kindOf(put, 'release-line')[0]
	assert.ok(byId(put, 'shape:sm-story-a-0').y < line.y, 'a release-1 story is below the first line')
	assert.ok(byId(put, 'shape:sm-story-a-1').y > line.y, 'a release-2 story is above the first line')
})

test('a release line spans every activity, not a range of them', () => {
	const put = buildStoryMap(model)
	const line = kindOf(put, 'release-line')[0]
	const activities = kindOf(put, 'activity')
	const right = Math.max(...activities.map((a) => a.x)) + 200
	assert.ok(line.x <= Math.min(...activities.map((a) => a.x)), 'the line starts after the first activity')
	assert.ok(line.x + line.props.w >= right, 'the line stops before the last activity')
})

test('a story with no release is drawn in an UNASSIGNED band, never dropped', () => {
	const put = buildStoryMap(model)
	const labels = kindOf(put, 'release-label').map((r) =>
		(r.props.richText.content ?? []).map((p) => (p.content ?? []).map((t) => t.text).join('')).join(' ')
	)
	assert.ok(labels.some((t) => t.includes('UNASSIGNED')), 'an unplaced story vanished instead of being flagged')
	assert.ok(kindOf(put, 'story').some((r) => r.id === 'shape:sm-story-c-1'), 'the unplaced story itself is missing')
})

test('bands do not overlap', () => {
	const put = buildStoryMap(model)
	const lines = kindOf(put, 'release-line').sort((a, b) => a.y - b.y)
	for (const line of lines) {
		const above = kindOf(put, 'story').filter((r) => r.y < line.y)
		assert.ok(above.every((r) => r.y + 200 <= line.y + 20), 'a story overlaps the line below its band')
	}
})

test('both pages render from one model and never share a shape id', () => {
	const board = buildJourneyBoard(model)
	const map = buildStoryMap(model)
	const shared = board.map((r) => r.id).filter((id) => map.some((r) => r.id === id))
	assert.deepEqual(shared, [], 'a shape id is claimed by both pages')
})

test('no shape carries a note fontSizeAdjustment of 0', () => {
	for (const r of [...buildStoryMap(model), ...buildJourneyBoard(model)]) {
		if (r.type === 'note') assert.equal(r.props.fontSizeAdjustment, 1, `${r.id} would render blank`)
	}
})

test('a map past the 61st shape still gets valid ordered unique indexes', () => {
	const steps = Array.from({ length: 16 }, (_, i) => ({ id: `s${i}`, card: `Step ${i}`, stories: ['a', 'b', 'c', 'd'] }))
	const shapes = buildStoryMap({ journey: 'big', steps, slices: [{ id: 'f', outcome: 'x' }] }).filter(
		(r) => r.typeName === 'shape'
	)
	assert.ok(shapes.length > 61, `fixture emits ${shapes.length} shapes, too few to reach the failure`)
	for (const parentId of new Set(shapes.map((s) => s.parentId))) {
		const ix = shapes.filter((s) => s.parentId === parentId).map((r) => r.index)
		assert.equal(new Set(ix).size, ix.length, 'siblings share an index')
		assert.deepEqual(ix, [...ix].sort(), 'sibling indexes are not in ascending order')
	}

	const schema = createTLSchema()
	for (const shape of shapes) {
		assert.doesNotThrow(() => schema.types.shape.validate(shape), `${shape.id} carries an index the schema rejects`)
	}
})

test('story map borders all three states and counts exists alone', () => {
	const three = { releases: [{ id: 'r', name: 'Release' }], steps: [{ id: 'a', card: 'Act', stories: ['gap', 'unverified', 'exists'].map((status) => ({ id: status, card: status, release: 'r', status })) }] }
	const text = (s) => s.props.richText.content.flatMap((p) => (p.content ?? []).map((t) => t.text ?? '')).join('\n')
	const records = buildStoryMap(three)
	assert.deepEqual(kindOf(records, 'story-border').map((s) => s.props.color), ['red', 'violet', 'green'])
	assert.equal(kindOf(records, 'story-status').length, 0)
	assert.match(text(kindOf(records, 'release-label')[0]), /1\/3 exist/)
	delete three.steps[0].stories[0].status
	assert.equal(kindOf(buildStoryMap(three), 'story-border').length, 2)
})

// Measured on a real board before the fix: 170px of 200 hidden, the card on top.
const spans = (r) => ({ x1: r.x, y1: r.y, x2: r.x + r.props.w, y2: r.y + r.props.h })
const overlap = (a, b) => Math.min(a.x2, b.x2) - Math.max(a.x1, b.x1) > 1 && Math.min(a.y2, b.y2) - Math.max(a.y1, b.y1) > 1

test('a question never renders underneath another story card', () => {
	const questions = kindOf(buildStoryMap(model), 'story-question')
	assert.ok(questions.length, 'fixture draws no question, so this proves nothing')
	const cards = kindOf(buildStoryMap(model), 'story').map((s) => ({ id: s.meta.journey.nodeId, box: { x1: s.x, y1: s.y, x2: s.x + 200, y2: s.y + 200 + s.props.growY } }))
	for (const q of questions) {
		const hit = cards.find((c) => c.id !== q.meta.journey.nodeId && overlap(spans(q), c.box))
		assert.equal(hit, undefined, `question on ${q.meta.journey.nodeId} is covered by story ${hit?.id}`)
	}
})

test('a question is drawn under its own story, in its own column', () => {
	const put = buildStoryMap(model)
	for (const q of kindOf(put, 'story-question')) {
		const own = byId(put, `shape:sm-story-${q.meta.journey.nodeId}`)
		assert.equal(q.x, own.x, `question on ${q.meta.journey.nodeId} is not in its story's column`)
		assert.ok(q.y >= own.y + 200, `question on ${q.meta.journey.nodeId} does not sit below its story`)
	}
})

test('a question grows its row, so the row beneath it stays clear', () => {
	const tall = {
		releases: [{ id: 'r', name: 'Release' }],
		steps: [{ id: 'a', card: 'Act', stories: [
			{ id: 'q', card: 'Asks', release: 'r', status: 'gap', question: 'x'.repeat(400) },
			{ id: 'below', card: 'Next', release: 'r', status: 'gap' },
		] }],
	}
	const put = buildStoryMap(tall)
	const q = kindOf(put, 'story-question')[0]
	assert.ok(byId(put, 'shape:sm-story-below').y > q.y + q.props.h, 'the next row starts inside the question box')
})

// Every other box on the page takes its height from fitHeight; the banner took a
// literal 70. Measured on a real board: 60px drawn against 88px of text.
const labelText = (s) => s.props.richText.content.flatMap((p) => (p.content ?? []).map((t) => t.text ?? '')).join('\n')

test('the one-journey banner is tall enough for its sentence', () => {
	const long = { ...model, one_journey: 'A person asks for the thing once, and it arrives without them checking twice, and nobody has to be told which queue it went into or who is holding it now.' }
	const banner = kindOf(buildStoryMap(long), 'one-journey')[0]
	assert.ok(banner, 'no banner drawn')
	assert.ok(
		banner.props.h >= fitHeight(labelText(banner), banner.props.w),
		`banner is ${banner.props.h}px for ${fitHeight(labelText(banner), banner.props.w)}px of text`
	)
})

test('no drawn label is shorter than the text inside it', () => {
	const long = { ...model, one_journey: 'A sentence long enough to wrap more than twice at the width this banner is given, which is how the clipping was first seen.' }
	for (const s of buildStoryMap(long)) {
		if (s.type !== 'geo' || !s.props?.richText) continue
		const text = labelText(s)
		if (!text.trim()) continue
		assert.ok(
			s.props.h >= fitHeight(text, s.props.w),
			`${s.meta?.journey?.kind ?? s.id} is ${s.props.h}px for ${fitHeight(text, s.props.w)}px of text`
		)
	}
})
