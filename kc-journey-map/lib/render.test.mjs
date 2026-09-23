import assert from 'node:assert/strict'
import { test } from 'node:test'
import { createTLSchema } from '@tldraw/tlschema'
import { buildJourneyBoard, buildAllPages, staleRecordIds } from './render.mjs'
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

test('the release board draws no lane boxes', () => {
	const records = buildJourneyBoard(fixtureModel, { release: fixtureModel.releases[0] })
	assert.equal(kind(records, 'lane-label').length, 0)
	const labelled = records.filter((s) => s.type === 'geo' || s.type === 'note').filter((s) => text(s))
	for (const s of labelled) {
		assert.doesNotMatch(text(s), /^(ACTIVITIES|RELEASE STORIES|STORY EVIDENCE|SYSTEM FLOW|CONSTRAINTS)\b/,
			`${s.id} still carries a dropped lane header`)
	}
})

test('a flow card is drawn once per system: line and a constraint card once per rule id; evidence lives in the story card', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].system = ['Calls the shared service']
	model.steps[0].rules = ['unique']
	model.rules = [{ id: 'unique', text: 'One unique name' }]
	const records = buildJourneyBoard(model, { release: model.releases[0] })

	// Steps b and c carry neither system nor rules; each still gets one placeholder card
	// per kind, so the board never reads as having silently dropped a step's flow.
	assert.equal(kind(records, 'flow').length, 3)
	assert.equal(kind(records, 'constraint').length, 3)

	const flowA = kind(records, 'flow').find((s) => s.meta.journey.nodeId === 'a')
	assert.equal(text(flowA), 'Calls the shared service')
	assert.deepEqual([flowA.props.color, flowA.props.fill], ['light-blue', 'solid'])

	const constraintA = kind(records, 'constraint').find((s) => s.meta.journey.nodeId === 'a')
	assert.equal(text(constraintA), 'One unique name')
	assert.deepEqual([constraintA.props.color, constraintA.props.fill], ['orange', 'solid'])

	const flowB = kind(records, 'flow').find((s) => s.meta.journey.nodeId === 'b')
	assert.equal(text(flowB), 'No system flow recorded.')

	const storyA0 = kind(records, 'story').find((s) => s.meta.journey.nodeId === 'a-0')
	assert.match(text(storyA0), /Evidence: NamesIt$/)

	// A question is a card of its own, not text folded into the story card.
	const bSee = kind(records, 'story').find((s) => s.meta.journey.nodeId === 'b-see')
	assert.match(text(bSee), /No story evidence recorded\.$/)
	assert.doesNotMatch(text(bSee), /push or pull/)
})

test('an open question is drawn as its own card, connected to its story by a native arrow', () => {
	const records = buildJourneyBoard(fixtureModel, { release: fixtureModel.releases[0] })
	const question = kind(records, 'question').find((q) => q.meta.journey.story === 'b-see')
	assert.ok(question, 'no question card drawn for b-see')
	assert.match(text(question), /^OPEN\nShould delivery be push or pull\?/)
	assert.deepEqual([question.props.color, question.props.fill, question.props.dash], ['light-green', 'solid', 'dashed'])

	const story = kind(records, 'story').find((s) => s.meta.journey.nodeId === 'b-see')
	const link = records.find((r) => r.type === 'arrow' && r.meta?.journey?.kind === 'question-link' && r.meta.journey.story === 'b-see')
	assert.ok(link, 'no connector drawn between the question and its story')
	const bindings = records.filter((r) => r.typeName === 'binding' && r.fromId === link.id)
	assert.equal(bindings.length, 2)
	assert.deepEqual(new Set(bindings.map((b) => b.toId)), new Set([story.id, question.id]))
})

test('open, answered and deferred questions share one fill; only the outline tells them apart', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].stories[0].status = 'gap'
	delete model.steps[0].stories[0].evidence
	model.steps[0].stories[0].questions = [
		{ id: 'q-open', ask: 'Still open', status: 'open' },
		{ id: 'q-answered', ask: 'Now settled', status: 'answered' },
		{ id: 'q-deferred', ask: 'Parked for now', status: 'deferred', because: 'waiting on design' },
	]
	const records = buildJourneyBoard(model, { release: model.releases[0] })
	const byId = (id) => kind(records, 'question').find((q) => q.meta.journey.nodeId === id)
	// Colour means kind (question), not status — fill is light-green for all three.
	for (const id of ['q-open', 'q-answered', 'q-deferred']) assert.equal(byId(id).props.color, 'light-green')
	assert.equal(byId('q-open').props.dash, 'dashed')
	assert.equal(byId('q-answered').props.dash, 'solid')
	assert.equal(byId('q-deferred').props.dash, 'solid')
	assert.match(text(byId('q-deferred')), /because: waiting on design/)
})

test('long lines have fitted cards and stack top to bottom: activity, flow, constraints, stories, questions', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].stories[0].question = 'A long question that needs an answer. '.repeat(15)
	model.steps[0].system = ['A long system explanation. '.repeat(30)]
	model.rules = [{ id: 'long', text: 'A constraint. '.repeat(70) }]
	model.steps[0].rules = ['long']
	const records = buildJourneyBoard(model)
	const boxes = records.filter((s) => s.type === 'geo' && text(s))
	for (const s of boxes) assert.ok(s.props.h >= fitHeight(text(s), s.props.w), `${s.id} is too short`)

	const activities = kind(records, 'activity')
	const flows = kind(records, 'flow')
	const constraints = kind(records, 'constraint')
	const stories = kind(records, 'story')
	const questions = kind(records, 'question')
	assert.ok(Math.max(...activities.map((s) => s.y + s.props.h)) <= Math.min(...flows.map((s) => s.y)))
	assert.ok(Math.max(...flows.map((s) => s.y + s.props.h)) <= Math.min(...constraints.map((s) => s.y)))
	assert.ok(Math.max(...constraints.map((s) => s.y + s.props.h)) < Math.min(...stories.map((s) => s.y)))
	assert.ok(Math.max(...stories.map((s) => s.y + 200)) < Math.min(...questions.map((s) => s.y)))
})

test('unsliced journeys retain unassigned stories and activities without stories', () => {
	const model = structuredClone(fixtureModel)
	delete model.releases
	model.steps.push({ id: 'empty', card: 'Decide later' })
	const records = buildAllPages(model, null, ['journey-board'])
	assert.ok(kind(records, 'story').some((s) => text(s).startsWith('An unplaced idea')))
	assert.equal(kind(records, 'empty-stories').length, 1)
	assert.match(text(kind(records, 'empty-stories')[0]), /No stories recorded/)
})

test('both projections border all three states and count exists alone; the release board folds its legend into one top-left panel', () => {
	const model = { releases: [{ id: 'r', name: 'Release' }], steps: [{ id: 'a', card: 'Act', stories: ['gap', 'unverified', 'exists'].map((status) => ({ id: status, card: status, release: 'r', status })) }] }
	const records = buildJourneyBoard(model, { release: model.releases[0] })
	assert.deepEqual(kind(records, 'story-border').map((s) => s.props.color), ['red', 'violet', 'green'])
	assert.ok(kind(records, 'story').every((s) => text(s).endsWith('No story evidence recorded.')))
	// The board draws its own legend (card colours + story-status borders); it does not
	// also carry withStoryStatus's separate horizontal legend.
	assert.equal(kind(records, 'status-legend').length, 0)
	const legend = kind(records, 'board-legend')
	assert.ok(legend.some((s) => s.meta.journey.nodeId === 'status-exists' && s.props.color === 'green'))
	assert.ok(legend.some((s) => s.meta.journey.nodeId === 'status-gap' && s.props.color === 'red'))
	assert.ok(legend.some((s) => s.meta.journey.nodeId === 'status-unverified' && s.props.color === 'violet'))
	assert.ok(legend.some((s) => s.meta.journey.nodeId === 'flow' && s.props.color === 'light-blue'))
	assert.ok(legend.some((s) => s.meta.journey.nodeId === 'constraint' && s.props.color === 'orange'))
	assert.ok(legend.some((s) => s.meta.journey.nodeId === 'question-open' && s.props.dash === 'dashed'))
	assert.ok(legend.some((s) => s.meta.journey.nodeId === 'question-settled' && s.props.dash === 'solid'))

	for (const page of buildAllPages(model, null, ['story-map', 'journey-board']).filter((r) => r.typeName === 'page')) {
		const all = buildAllPages(model, null, ['story-map', 'journey-board'])
		const stories = kind(all, 'story').filter((s) => s.parentId === page.id)
		assert.deepEqual(stories.map((s) => all.find((r) => r.parentId === s.id).props.color), ['red', 'violet', 'green'])
		assert.equal(kind(all, 'story-status').length, 0)
	}
	// The story map keeps its own separate horizontal legend, unchanged.
	assert.deepEqual(kind(buildAllPages(model, null, ['story-map']), 'status-legend').map((s) => text(s).split('\n')[0]), ['EXISTS', 'GAP', 'UNVERIFIED'])
	assert.match(text(kind(records, 'release-label')[0]), /1\/3 stories exist/)
	delete model.steps[0].stories[0].status
	// UNASSESSED is a status line inside the story card, after the card text and before
	// the evidence line, not a whole card of its own.
	assert.deepEqual(text(kind(buildJourneyBoard(model), 'story')[0]).split('\n'), ['gap', 'UNASSESSED', 'No story evidence recorded.'])
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

// Bit twice on 2026-09-21 (142 shapes, then 141): `--pages journey-board` computed
// `remove` from every tagged shape in the room, not just the pages this render drew,
// and wiped the story-map page it never touched.
test('a partial redraw does not delete another page it did not draw', () => {
	const full = buildAllPages(fixtureModel, null, ['story-map', 'journey-board'])
	const storyMapPage = full.find((r) => r.typeName === 'page' && r.id === 'page:page')
	const boardPage = full.find((r) => r.typeName === 'page' && r.id !== 'page:page')
	const staleOnBoard = { id: 'shape:jm-stale', typeName: 'shape', type: 'geo', parentId: boardPage.id, meta: { journey: { nodeId: 'gone', kind: 'story-proof' } } }
	const humanOnBoard = { id: 'shape:human-note', typeName: 'shape', type: 'note', parentId: boardPage.id, meta: {} }
	const current = [...full, staleOnBoard, humanOnBoard]

	const put = buildAllPages(fixtureModel, null, ['journey-board'])
	const removed = staleRecordIds(current, put)

	assert.ok(removed.includes('shape:jm-stale'), 'a stale shape on the redrawn page must go')
	assert.ok(!removed.includes('shape:human-note'), 'an untagged human shape must survive')
	for (const shape of full.filter((r) => r.typeName === 'shape' && r.parentId === storyMapPage.id)) {
		assert.ok(!removed.includes(shape.id), `story-map shape ${shape.id} was wiped by a journey-board-only redraw`)
	}
})

test('a partial redraw removes a stale question connector along with its bindings', () => {
	const full = buildAllPages(fixtureModel, null, ['journey-board'])
	const boardPage = full.find((r) => r.typeName === 'page')
	const staleLink = { id: 'shape:jm-stale-link', typeName: 'shape', type: 'arrow', parentId: boardPage.id, meta: { journey: { nodeId: 'gone-q', kind: 'question-link', story: 'gone' } } }
	const staleBindings = [
		{ id: 'binding:jm-stale-link-from', typeName: 'binding', type: 'arrow', fromId: staleLink.id, toId: 'shape:jm-r1-story-b-see', meta: { journey: { nodeId: 'gone-q', kind: 'question-link', story: 'gone' } } },
		{ id: 'binding:jm-stale-link-to', typeName: 'binding', type: 'arrow', fromId: staleLink.id, toId: 'shape:jm-stale-question', meta: { journey: { nodeId: 'gone-q', kind: 'question-link', story: 'gone' } } },
	]
	const current = [...full, staleLink, ...staleBindings]

	const removed = staleRecordIds(current, buildAllPages(fixtureModel, null, ['journey-board']))
	assert.ok(removed.includes(staleLink.id))
	for (const binding of staleBindings) assert.ok(removed.includes(binding.id), `${binding.id} outlived the arrow it hung off`)
})

// A story-status border is parented to its story shape, not the page — one hop of
// parentId is not enough to find the page a nested shape belongs to.
test('a removed story takes its nested status border with it', () => {
	const current = buildAllPages(fixtureModel, null, ['story-map'])
	assert.ok(current.some((r) => r.id === 'shape:sm-story-a-0-status-border'), 'fixture draws no border, so this proves nothing')
	const model = structuredClone(fixtureModel)
	model.steps[0].stories.splice(0, 1)
	const removed = staleRecordIds(current, buildAllPages(model, null, ['story-map']))
	assert.ok(removed.includes('shape:sm-story-a-0'))
	assert.ok(removed.includes('shape:sm-story-a-0-status-border'), 'the border outlived the story it was drawn on')
})

test('every record, including a connector arrow and its bindings, validates against the tldraw schema', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].stories[0].questions = ['a', 'b', 'c', 'd', 'e', 'f'].map((id, k) => ({ id, ask: `Question ${k}`, status: ['open', 'answered', 'deferred'][k % 3], because: 'because' }))
	const schema = createTLSchema()
	for (const selection of [['story-map'], ['journey-board'], ['story-map', 'journey-board', 'function-map']]) {
		const records = buildAllPages(model, 'schema-check', selection)
		const ids = records.map((r) => r.id)
		assert.equal(new Set(ids).size, ids.length, `${selection.join(',')} produced a duplicate id`)
		for (const r of records) {
			assert.ok(schema.types[r.typeName], `${selection.join(',')}: unknown typeName "${r.typeName}" on ${r.id}`)
			assert.doesNotThrow(() => schema.types[r.typeName].validate(r), `${selection.join(',')}: ${r.typeName} ${r.id} failed schema validation`)
		}
		assert.ok(records.some((r) => r.type === 'arrow'), `${selection.join(',')} drew no connector arrow for a 6-question story`)
		assert.ok(records.some((r) => r.typeName === 'binding'), `${selection.join(',')} drew no binding for a 6-question story`)
	}
})
