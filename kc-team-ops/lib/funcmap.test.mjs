// node --test lib/*.test.mjs

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
	// A size-m note is 200 tall; a pitch under that drew them as one block and spilled
	// the last one into the State lane.
	const events = buildFunctionMap(fixtureModel).filter((r) => r.meta?.journey?.kind === 'event' && r.id.includes('-b-'))
	assert.ok(events[1].y - events[0].y >= 200, `pitch ${events[1].y - events[0].y} is smaller than a sticky`)
})

test('no page claims a shape id another page already uses', () => {
	const all = [buildJourneyBoard(fixtureModel), buildStoryMap(fixtureModel), buildFunctionMap(fixtureModel)]
	const ids = all.flat().map((r) => r.id)
	assert.equal(new Set(ids).size, ids.length, 'two pages share a shape id')
})

test('a file that models nothing gets no function map page', () => {
	const bare = { ...fixtureModel, steps: fixtureModel.steps.map(({ command, events, state, readmodel, ...rest }) => rest) }
	const pages = buildAllPages(bare).filter((r) => r.typeName === 'page').map((r) => r.name)
	assert.deepEqual(pages.sort(), ['Journey board', 'Story map'], 'an empty function map claims the modelling was done')
	assert.ok(buildAllPages(fixtureModel).some((r) => r.name === 'Function map'), 'a modelled file must get the page')
})
