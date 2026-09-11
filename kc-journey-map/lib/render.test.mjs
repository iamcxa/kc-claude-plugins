import assert from 'node:assert/strict'
import { test } from 'node:test'
import { buildJourneyBoard, buildAllPages } from './render.mjs'
import { fixtureModel } from './fixture.mjs'
import { fitHeight, note, storyBorder } from './records.mjs'

const kind = (records, kind) => records.filter((s) => s.meta?.journey?.kind === kind)
const text = (s) => s.props.richText.content.map((p) => (p.content ?? []).map((t) => t.text ?? '').join('')).join('\n')

test('release boards show exactly the selected stories in yellow, grouped by green activities', () => {
	const records = buildJourneyBoard(fixtureModel, { release: fixtureModel.releases[0] })
	const stories = kind(records, 'story')
	assert.deepEqual(stories.map((s) => s.meta.journey.nodeId), ['a-0', 'a-2', 'b-see', 'c-read'])
	assert.ok(stories.every((s) => s.props.color === 'yellow'))
	assert.ok(kind(records, 'activity').every((s) => s.props.color === 'green'))
	const a = kind(records, 'activity')[0]
	assert.ok(stories.slice(0, 2).every((s) => s.x >= a.x && s.x + 200 <= a.x + a.props.w))
})

test('shared flow and constraints appear once per activity and story proof stays with its story', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].system = ['Calls the shared service']
	model.steps[0].rules = ['unique']
	model.rules = [{ id: 'unique', text: 'One unique name' }]
	const records = buildJourneyBoard(model, { release: model.releases[0] })
	assert.equal(kind(records, 'system').length, 3)
	assert.equal(kind(records, 'constraints').length, 3)
	assert.match(text(kind(records, 'system')[0]), /SHARED ACTIVITY CONTEXT\n• Calls the shared service/)
	assert.match(text(kind(records, 'constraints')[0]), /SHARED ACTIVITY CONSTRAINTS\n• One unique name/)
	assert.match(text(kind(records, 'story-proof').find((s) => s.meta.journey.nodeId === 'a-0')), /^Evidence: NamesIt/)
	assert.match(text(kind(records, 'story-proof').find((s) => s.meta.journey.nodeId === 'b-see')), /^No story evidence recorded.\n\? Should delivery be push or pull/)
})

test('long questions and shared content have fitted boxes and do not overlap later rows', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].stories[0].question = 'A long question that needs an answer. '.repeat(15)
	model.steps[0].system = ['A long system explanation. '.repeat(30)]
	model.rules = [{ id: 'long', text: 'A constraint. '.repeat(70) }]
	model.steps[0].rules = ['long']
	const records = buildJourneyBoard(model)
	const boxes = records.filter((s) => s.type === 'geo' && text(s))
	for (const s of boxes) assert.ok(s.props.h >= fitHeight(text(s), s.props.w), `${s.id} is too short`)
	const stories = kind(records, 'story')
	const proofs = kind(records, 'story-proof')
	const systems = kind(records, 'system')
	const rules = kind(records, 'constraints')
	assert.ok(Math.max(...stories.map((s) => s.y + 200)) < proofs[0].y)
	assert.ok(Math.max(...proofs.map((s) => s.y + s.props.h)) < systems[0].y)
	assert.ok(Math.max(...systems.map((s) => s.y + s.props.h)) < rules[0].y)
})

test('unsliced journeys retain unassigned stories and activities without stories', () => {
	const model = structuredClone(fixtureModel)
	delete model.releases
	model.steps.push({ id: 'empty', card: 'Decide later' })
	const records = buildAllPages(model, null, ['journey-board'])
	assert.ok(kind(records, 'story').some((s) => text(s) === 'An unplaced idea'))
	assert.equal(kind(records, 'empty-stories').length, 1)
	assert.match(text(kind(records, 'empty-stories')[0]), /No stories recorded/)
})

test('both projections border all three states, share legends, and count exists alone', () => {
	const model = { releases: [{ id: 'r', name: 'Release' }], steps: [{ id: 'a', card: 'Act', stories: ['gap', 'unverified', 'exists'].map((status) => ({ id: status, card: status, release: 'r', status })) }] }
	const records = buildJourneyBoard(model, { release: model.releases[0] })
	assert.deepEqual(kind(records, 'story-border').map((s) => s.props.color), ['red', 'violet', 'green'])
	assert.ok(kind(records, 'story-proof').every((s) => text(s) === 'No story evidence recorded.' && s.props.color === 'grey'))
	for (const page of buildAllPages(model, null, ['story-map', 'journey-board']).filter((r) => r.typeName === 'page')) {
		const all = buildAllPages(model, null, ['story-map', 'journey-board'])
		const stories = kind(all, 'story').filter((s) => s.parentId === page.id)
		assert.deepEqual(stories.map((s) => all.find((r) => r.parentId === s.id).props.color), ['red', 'violet', 'green'])
		assert.deepEqual(kind(all, 'status-legend').filter((s) => s.parentId === page.id).map((s) => text(s).split('\n')[0]), ['EXISTS', 'GAP', 'UNVERIFIED'])
		assert.equal(kind(all, 'story-status').length, 0)
	}
	assert.match(text(kind(records, 'release-label')[0]), /1\/3 stories exist/)
	delete model.steps[0].stories[0].status
	assert.match(text(kind(buildJourneyBoard(model), 'story-proof')[0]), /^UNASSESSED/)
})

test('story border geometry follows measured height and scale without moving the story', () => {
	const story = { ...note({ id: 'shape:story', text: 'A story', x: 40, y: 90 }), meta: { journey: { kind: 'story', nodeId: 'stable', status: 'gap' } } }
	for (const [growY, scale] of [[0, 1], [320, 1], [320, 1.5]]) {
		story.props.growY = growY
		story.props.scale = scale
		const before = structuredClone(story)
		const border = storyBorder(story)
		assert.deepEqual([border.parentId, border.x, border.y, border.props.w, border.props.h, border.props.scale], [story.id, 0, 0, 200 * scale, (200 + growY) * scale, scale])
		assert.deepEqual([border.props.fill, border.props.dash, border.props.size, border.isLocked], ['none', 'solid', 'xl', true])
		assert.deepEqual(story, before)
	}
	assert.equal(storyBorder(note({ id: 'shape:plain', text: 'Plain note', x: 0, y: 0 })), null)
	story.meta.journey.status = 'not-a-status'
	assert.equal(storyBorder(story), null)
})
