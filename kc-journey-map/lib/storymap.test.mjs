import assert from 'node:assert/strict'
import { test } from 'node:test'
import { buildStoryMap } from './storymap.mjs'
import { buildJourneyBoard } from './render.mjs'
import { fixtureModel as model } from './fixture.mjs'
import { fitHeight, NOTE_SIZE } from './records.mjs'
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
// A question is a note, with no props.w/h of its own — its footprint is the same
const spans = (r) => ({ x1: r.x, y1: r.y, x2: r.x + NOTE_SIZE.s, y2: r.y + NOTE_SIZE.s })
const overlap = (a, b) => Math.min(a.x2, b.x2) - Math.max(a.x1, b.x1) > 1 && Math.min(a.y2, b.y2) - Math.max(a.y1, b.y1) > 1

// The story map is the whole journey's definition — persona, activities, stories and
// release slices. Questions and answers are detail for a zoomed-in release board, so the
// story map draws none of them, whatever the stories carry.
test('the story map draws no question, answer or connector, even when stories carry questions', () => {
	const withQuestions = structuredClone(model)
	withQuestions.steps[1].stories[0].questions = [
		{ id: 'q1', ask: 'Open one' },
		{ id: 'q2', ask: 'Settled one', answer: 'Push, per the ADR.', doc: 'https://example.com/adr#q1' },
	]
	const put = buildStoryMap(withQuestions)
	for (const kind of ['question', 'answer', 'question-link', 'answer-link']) {
		assert.equal(kindOf(put, kind).length, 0, `story map drew a ${kind}`)
	}
	assert.equal(put.filter((r) => r.type === 'arrow' || r.typeName === 'binding').length, 0, 'story map drew a connector')
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

test('a CJK label is measured by the width its glyphs take, not how many there are', () => {
	const han = '這是一段中文說明。'.repeat(6)
	assert.equal(fitHeight(han, 300), fitHeight('a'.repeat(han.length * 2), 300),
		`${han.length} CJK glyphs were not measured as ${han.length * 2} character widths`)
	assert.ok(fitHeight(han, 300) > fitHeight('a'.repeat(han.length), 300))
})
