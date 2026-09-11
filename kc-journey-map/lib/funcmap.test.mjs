
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { buildFunctionMap } from './funcmap.mjs'
import { buildStoryMap } from './storymap.mjs'
import { buildJourneyBoard, buildAllPages } from './render.mjs'
import { fixtureModel } from './fixture.mjs'

const kinds = (put) => new Set(put.map((r) => r.meta?.journey?.kind).filter(Boolean))
const text = (r) =>
	(r.props?.richText?.content ?? []).map((p) => (p.content ?? []).map((t) => t.text ?? '').join('')).join('\n')

test('the function map draws all four lanes', () => {
	const k = kinds(buildFunctionMap(fixtureModel))
	for (const kind of ['command', 'event', 'state', 'readmodel', 'lane-label']) {
		assert.ok(k.has(kind), `function map is missing ${kind}`)
	}
})

test('a step nobody modelled is drawn as a gap, not left blank', () => {
	const put = buildFunctionMap(fixtureModel)
	const cmdA = put.find((r) => r.id === 'shape:fm-cmd-a')
	assert.match(text(cmdA), /not modelled/, 'an unmodelled step must say so on the board')
	const cmdB = put.find((r) => r.id === 'shape:fm-cmd-b')
	assert.equal(text(cmdB), 'GetTheThing(id)')
})

test('every event gets its own shape, in the order the file lists them', () => {
	const events = buildFunctionMap(fixtureModel).filter((r) => r.meta?.journey?.kind === 'event' && r.id.includes('-b-'))
	assert.deepEqual(events.map(text), ['ThingDelivered', 'DeliveryRefused'])
	assert.ok(events[0].y < events[1].y, 'events are not stacked in order')
})

test('event stickies do not overlap each other', () => {
	const events = buildFunctionMap(fixtureModel).filter((r) => r.meta?.journey?.kind === 'event' && r.id.includes('-b-'))
	assert.ok(events[1].y - events[0].y >= 200, `pitch ${events[1].y - events[0].y} is smaller than a sticky`)
})

test('no page claims a shape id another page already uses, with every projection selected', () => {
	const ids = buildAllPages(fixtureModel, null, ['story-map', 'journey-board', 'function-map']).map((r) => r.id)
	assert.equal(new Set(ids).size, ids.length, 'two pages share a shape id')
})

test('the function map is opt-in: selection decides, never the file content', () => {
	const bare = { ...fixtureModel, steps: fixtureModel.steps.map(({ command, events, state, readmodel, ...rest }) => rest) }

	const byDefault = buildAllPages(fixtureModel).filter((r) => r.typeName === 'page').map((r) => r.name)
	assert.ok(!byDefault.includes('Function map'), 'the function map arrived uninvited, though the file models something')

	const selected = buildAllPages(bare, null, ['story-map', 'function-map'])
	assert.ok(selected.some((r) => r.name === 'Function map'), 'selecting the function map on an unmodelled file did not draw it')
	assert.match(text(selected.find((r) => r.id === 'shape:fm-cmd-a')), /not modelled/, 'a selected but unmodelled step must still say so')
})
