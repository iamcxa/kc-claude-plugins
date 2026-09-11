// node --test lib/*.test.mjs
//
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { buildStoryMap } from './storymap.mjs'
import { fixtureModel as model } from './fixture.mjs'
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
	// a-0 is in release 1 and a-1 in release 2, so a-1 sits below the line even though it
	// is second in the same activity's list.
	const put = buildStoryMap(model)
	const line = kindOf(put, 'release-line')[0]
	assert.ok(byId(put, 'shape:sm-story-a-0').y < line.y, 'a release-1 story is below the first line')
	assert.ok(byId(put, 'shape:sm-story-a-1').y > line.y, 'a release-2 story is above the first line')
})

test('a release line spans every activity, not a range of them', () => {
	// A band scoped to some columns cannot express a walking skeleton; that was the defect.
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



test('no shape carries a note fontSizeAdjustment of 0', () => {
	// A zero passes schema validation and renders the label at font-size 0px.
	for (const r of buildStoryMap(model)) {
		if (r.type === 'note') assert.equal(r.props.fontSizeAdjustment, 1, `${r.id} would render blank`)
	}
})

test('a map past the 61st shape still gets valid ordered unique indexes', () => {
	// Sized to emit more than 61 shapes on one page, which is where a hand-rolled run
	// started producing keys the schema rejects. A nine-activity map emits 47 and would
	// have passed either way.
	const steps = Array.from({ length: 16 }, (_, i) => ({ id: `s${i}`, card: `Step ${i}`, stories: ['a', 'b', 'c', 'd'] }))
	const shapes = buildStoryMap({ journey: 'big', steps, slices: [{ id: 'f', outcome: 'x' }] }).filter(
		(r) => r.typeName === 'shape'
	)
	assert.ok(shapes.length > 61, `fixture emits ${shapes.length} shapes, too few to reach the failure`)
	const ix = shapes.map((r) => r.index)
	assert.equal(new Set(ix).size, ix.length, 'two shapes share an index')
	assert.deepEqual(ix, [...ix].sort(), 'indexes are not in ascending order')

	// Unique and ordered is not the same as valid: the leading letter encodes how long the
	// rest must be, and a run that looked fine produced keys the schema rejected at 62.
	const schema = createTLSchema()
	for (const shape of shapes) {
		assert.doesNotThrow(() => schema.types.shape.validate(shape), `${shape.id} carries an index the schema rejects`)
	}
})
