// node --test lib/*.test.mjs
//
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { buildStoryMap } from './storymap.mjs'
import { buildJourneyBoard } from './render.mjs'
import { fixtureModel as model } from './fixture.mjs'

const kinds = (put) => new Set(put.map((r) => r.meta?.journey?.kind).filter(Boolean))

test('the story map draws every element the method calls for', () => {
	const k = kinds(buildStoryMap(model))
	for (const kind of ['persona', 'now', 'activity', 'story', 'badge', 'ownership', 'slice-line', 'slice-label', 'later']) {
		assert.ok(k.has(kind), `story map is missing ${kind}`)
	}
})

test('story order under an activity is the order the file declares', () => {
	const stories = buildStoryMap(model).filter((r) => r.meta?.journey?.kind === 'story')
	const first = stories.find((r) => r.id === 'shape:sm-story-a-0')
	const second = stories.find((r) => r.id === 'shape:sm-story-a-1')
	assert.ok(first.y < second.y, 'priority runs top to bottom')
})

test('both pages render from one model and never share a shape id', () => {
	const board = buildJourneyBoard(model)
	const map = buildStoryMap(model)
	const shared = board.map((r) => r.id).filter((id) => map.some((r) => r.id === id))
	assert.deepEqual(shared, [], 'a shape id is claimed by both pages')
})

test('no shape carries a note fontSizeAdjustment of 0', () => {
	// A zero passes schema validation and renders the label at font-size 0px.
	for (const r of [...buildStoryMap(model), ...buildJourneyBoard(model)]) {
		if (r.type === 'note') assert.equal(r.props.fontSizeAdjustment, 1, `${r.id} would render blank`)
	}
})

test('a nine-activity map with four stories each still gets ordered unique indexes', () => {
	// The screenshot this method was learned from has nine activities; a single-character
	// index run holds 61 and threw at 79.
	const steps = Array.from({ length: 9 }, (_, i) => ({ id: `s${i}`, card: `Step ${i}`, stories: ['a', 'b', 'c', 'd'] }))
	const shapes = buildStoryMap({ journey: 'big', steps, slices: [{ id: 'f', outcome: 'x' }] }).filter(
		(r) => r.typeName === 'shape'
	)
	const ix = shapes.map((r) => r.index)
	assert.equal(new Set(ix).size, ix.length, 'two shapes share an index')
	assert.deepEqual(ix, [...ix].sort(), 'indexes are not in ascending order')
})
