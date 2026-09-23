import assert from 'node:assert/strict'
import { test } from 'node:test'
import { createTLSchema } from '@tldraw/tlschema'
import { buildJourneyBoard, buildAllPages, staleRecordIds } from './render.mjs'
import { buildStoryMap } from './storymap.mjs'
import { fixtureModel } from './fixture.mjs'
import { sortByIndex, validateIndexKey } from '@tldraw/utils'
import { fitHeight, note, storyBorder, NOTE_SIZE } from './records.mjs'

const kind = (records, kind) => records.filter((s) => s.meta?.journey?.kind === kind)
const text = (s) => s.props.richText.content.map((p) => (p.content ?? []).map((t) => t.text ?? '').join('')).join('\n')

test('release boards show exactly the selected stories in yellow, grouped by green activities', () => {
	const records = buildJourneyBoard(fixtureModel, { release: fixtureModel.releases[0] })
	const stories = kind(records, 'story')
	assert.deepEqual(stories.map((s) => s.meta.journey.nodeId), ['a-0', 'a-2', 'b-see', 'c-read'])
	assert.ok(stories.every((s) => s.props.color === 'yellow'))
	assert.ok(kind(records, 'activity').every((s) => s.props.color === 'green'))
	const flowA = kind(records, 'flow').find((f) => f.meta.journey.nodeId === 'a')
	const activityA = kind(records, 'activity').find((f) => f.meta.journey.nodeId === 'a')
	assert.equal(flowA.type, 'geo')
	assert.equal(flowA.x, activityA.x)
	assert.ok(stories.slice(0, 2).every((s) => s.x >= activityA.x))
})

test('an activity or story card is structurally identical between the story map and the release board for the same node', () => {
	const board = buildJourneyBoard(fixtureModel, { release: fixtureModel.releases[0] })
	const map = buildStoryMap(fixtureModel)
	const cardShape = (s) => ({ type: s.type, color: s.props.color, size: s.props.size, richText: s.props.richText })

	const boardActivity = kind(board, 'activity').find((s) => s.meta.journey.nodeId === 'a')
	const mapActivity = kind(map, 'activity').find((s) => s.meta.journey.nodeId === 'a')
	assert.deepEqual(cardShape(boardActivity), cardShape(mapActivity))

	const boardStory = kind(board, 'story').find((s) => s.meta.journey.nodeId === 'a-0')
	const mapStory = kind(map, 'story').find((s) => s.meta.journey.nodeId === 'a-0')
	assert.deepEqual(cardShape(boardStory), cardShape(mapStory))
	const borderStyle = (border) => ({ color: border.props.color, dash: border.props.dash, size: border.props.size, isLocked: border.isLocked })
	assert.deepEqual(borderStyle(storyBorder(boardStory)), borderStyle(storyBorder(mapStory)))
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

test('each step gets one flow box and one constraint box, several lines becoming a bullet list', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].system = ['Calls the shared service', 'Keeps one copy']
	model.steps[0].rules = ['unique']
	model.rules = [{ id: 'unique', text: 'One unique name' }]
	const records = buildJourneyBoard(model, { release: model.releases[0] })

	assert.equal(kind(records, 'flow').length, 3)
	assert.equal(kind(records, 'constraint').length, 3)

	const flowA = kind(records, 'flow').find((s) => s.meta.journey.nodeId === 'a')
	assert.equal(text(flowA), '• Calls the shared service\n• Keeps one copy')
	assert.deepEqual([flowA.type, flowA.props.color], ['geo', 'light-blue'])

	const constraintA = kind(records, 'constraint').find((s) => s.meta.journey.nodeId === 'a')
	assert.equal(text(constraintA), 'One unique name')
	assert.deepEqual([constraintA.type, constraintA.props.color], ['geo', 'orange'])

	const flowB = kind(records, 'flow').find((s) => s.meta.journey.nodeId === 'b')
	assert.equal(text(flowB), 'No system flow recorded.')

	const storyA0 = kind(records, 'story').find((s) => s.meta.journey.nodeId === 'a-0')
	assert.equal(text(storyA0), 'Names it')
	const bSee = kind(records, 'story').find((s) => s.meta.journey.nodeId === 'b-see')
	assert.equal(text(bSee), 'Sees it arrive')
})

test('a question is drawn as its own note, straight below its story, with no connector', () => {
	const records = buildJourneyBoard(fixtureModel, { release: fixtureModel.releases[0] })
	const question = kind(records, 'question').find((q) => q.meta.journey.story === 'b-see')
	assert.ok(question, 'no question card drawn for b-see')
	assert.equal(question.type, 'note')
	assert.equal(text(question), 'Should delivery be push or pull?')
	assert.equal(question.props.color, 'light-green')

	const story = kind(records, 'story').find((s) => s.meta.journey.nodeId === 'b-see')
	assert.equal(question.x, story.x)
	assert.ok(question.y > story.y)
	assert.equal(records.filter((r) => r.type === 'arrow' || r.typeName === 'binding').length, 0, 'the release board draws no connectors')

	assert.equal(kind(records, 'answer').find((a) => a.meta.journey.story === 'b-see'), undefined)
})

test('an answered question draws an answer note to its right on the same row; an unanswered one draws none', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].stories[0].status = 'gap'
	delete model.steps[0].stories[0].evidence
	model.steps[0].stories[0].questions = [
		{ id: 'q-open', ask: 'Still open' },
		{ id: 'q-answered', ask: 'Now settled', answer: 'It is the owner.' },
		{ id: 'q-linked', ask: 'Where is this written up?', doc: 'https://example.com/adr#q1' },
		{ id: 'q-deferred', ask: 'Parked for now', status: 'deferred', because: 'waiting on design' },
	]
	const records = buildJourneyBoard(model, { release: model.releases[0] })
	const questionById = (id) => kind(records, 'question').find((q) => q.meta.journey.nodeId === id)
	const answerById = (id) => kind(records, 'answer').find((a) => a.meta.journey.nodeId === id)

	for (const id of ['q-open', 'q-answered', 'q-linked', 'q-deferred']) {
		assert.equal(questionById(id).type, 'note')
		assert.equal(questionById(id).props.color, 'light-green')
	}

	assert.equal(answerById('q-open'), undefined, 'an unanswered question draws no answer note')

	const answered = answerById('q-answered')
	assert.equal(answered.type, 'note')
	assert.equal(answered.props.color, 'light-violet')
	assert.equal(text(answered), 'It is the owner.')
	assert.equal(answered.y, questionById('q-answered').y, 'the answer sits on its own question\'s row')
	assert.ok(answered.x > questionById('q-answered').x, 'the answer sits to the right of its question')
	const ys = ['q-open', 'q-answered', 'q-linked', 'q-deferred'].map((id) => questionById(id).y)
	const gaps = ys.slice(1).map((y, k) => y - ys[k])
	assert.equal(new Set(gaps).size, 1, `questions are not evenly spaced: ${gaps}`)
	assert.equal(new Set(['q-open', 'q-answered', 'q-linked', 'q-deferred'].map((id) => questionById(id).x)).size, 1, 'questions are not in one column')

	assert.equal(answerById('q-linked').props.url, 'https://example.com/adr#q1')

	assert.equal(text(answerById('q-deferred')), 'waiting on design')
})

test('long lines have fitted flow/constraint cards, and cards stack top to bottom: activity, flow, constraints, stories, questions', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].stories[0].question = 'A long question that needs an answer. '.repeat(15)
	model.steps[0].system = ['A long system explanation. '.repeat(30)]
	model.rules = [{ id: 'long', text: 'A constraint. '.repeat(70) }]
	model.steps[0].rules = ['long']
	const records = buildJourneyBoard(model)
	const boxes = records.filter((s) => s.type === 'geo' && text(s))
	for (const s of boxes) assert.ok(s.props.h >= fitHeight(text(s), s.props.w), `${s.id} is too short`)
	const height = (s) => s.type === 'note' ? 200 + s.props.growY : s.props.h

	const activities = kind(records, 'activity')
	const flows = kind(records, 'flow')
	const constraints = kind(records, 'constraint')
	const stories = kind(records, 'story')
	const questions = kind(records, 'question')
	assert.ok(Math.max(...activities.map((s) => s.y)) + NOTE_SIZE.m <= Math.min(...flows.map((s) => s.y)))
	assert.ok(Math.max(...flows.map((s) => s.y + height(s))) <= Math.min(...constraints.map((s) => s.y)))
	assert.ok(Math.max(...constraints.map((s) => s.y + height(s))) < Math.min(...stories.map((s) => s.y)))
	assert.ok(Math.max(...stories.map((s) => s.y)) + NOTE_SIZE.m < Math.min(...questions.map((s) => s.y)))
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
	assert.deepEqual(kind(records, 'story').map((s) => text(s)), ['gap', 'unverified', 'exists'])
	assert.equal(kind(records, 'status-legend').length, 0)
	const legend = kind(records, 'board-legend')
	assert.ok(legend.every((s) => s.type === (['flow', 'constraint'].includes(s.meta.journey.nodeId) ? 'geo' : 'note')), 'a legend entry does not match the board')
	const legendBorder = (id) => kind(records, 'board-legend-border').find((b) => b.meta.journey.nodeId === id)
	assert.equal(legendBorder('status-exists').props.color, 'green')
	assert.equal(legendBorder('status-gap').props.color, 'red')
	assert.equal(legendBorder('status-unverified').props.color, 'violet')
	assert.ok(legend.some((s) => s.meta.journey.nodeId === 'flow' && s.props.color === 'light-blue'))
	assert.ok(legend.some((s) => s.meta.journey.nodeId === 'constraint' && s.props.color === 'orange'))
	assert.ok(legend.some((s) => s.meta.journey.nodeId === 'question' && s.props.color === 'light-green'))
	assert.ok(legend.some((s) => s.meta.journey.nodeId === 'answer' && s.props.color === 'light-violet'))

	for (const page of buildAllPages(model, null, ['story-map', 'journey-board']).filter((r) => r.typeName === 'page')) {
		const all = buildAllPages(model, null, ['story-map', 'journey-board'])
		const stories = kind(all, 'story').filter((s) => s.parentId === page.id)
		assert.deepEqual(stories.map((s) => all.find((r) => r.parentId === s.id).props.color), ['red', 'violet', 'green'])
		assert.equal(kind(all, 'story-status').length, 0)
	}
	assert.deepEqual(kind(buildAllPages(model, null, ['story-map']), 'status-legend').map((s) => text(s).split('\n')[0]), ['EXISTS', 'GAP', 'UNVERIFIED'])
	assert.match(text(kind(records, 'release-label')[0]), /1\/3 stories exist/)
	delete model.steps[0].stories[0].status
	assert.equal(text(kind(buildJourneyBoard(model), 'story')[0]), 'gap')
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

test('a removed story takes its nested status border with it', () => {
	const current = buildAllPages(fixtureModel, null, ['story-map'])
	assert.ok(current.some((r) => r.id === 'shape:sm-story-a-0-status-border'), 'fixture draws no border, so this proves nothing')
	const model = structuredClone(fixtureModel)
	model.steps[0].stories.splice(0, 1)
	const removed = staleRecordIds(current, buildAllPages(model, null, ['story-map']))
	assert.ok(removed.includes('shape:sm-story-a-0'))
	assert.ok(removed.includes('shape:sm-story-a-0-status-border'), 'the border outlived the story it was drawn on')
})

test('every record validates against the tldraw schema', () => {
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
	}
})

test('a note grows to fit its text, and a full-width character counts as two columns', async () => {
	const { note, textWidth } = await import('./records.mjs')
	assert.equal(textWidth('ab'), 2)
	assert.equal(textWidth('代碼'), 4)
	assert.equal(note({ id: 'shape:x', text: '短', x: 0, y: 0 }).props.growY, 0, 'a short note grew')
	assert.ok(note({ id: 'shape:y', text: '很長的中文'.repeat(20), x: 0, y: 0, size: 's' }).props.growY > 0, 'a long Chinese note did not grow')
})

test('the status sits in the header row beside the release, whatever the questions below', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].stories[0].questions = Array.from({ length: 8 }, (_, k) => ({ id: `q${k}`, ask: `Question ${k}` }))
	const records = buildJourneyBoard(model, { release: model.releases[0] })
	const status = records.find((r) => r.meta?.journey?.kind === 'status')
	const release = records.find((r) => r.meta?.journey?.kind === 'release-label')
	assert.equal(status.y, release.y, 'the status is not on the release header row')
	assert.ok(status.x > release.x, 'the status is not to the right of the release')
	for (const q of records.filter((r) => r.meta?.journey?.kind === 'question')) assert.ok(status.y < q.y)
})

test('every board page carries an index key tldraw accepts, however many releases there are', () => {
	const model = structuredClone(fixtureModel)
	model.releases = Array.from({ length: 9 }, (_, i) => ({ id: `r${i + 1}`, name: `RELEASE ${i + 1}`, goal: 'One outcome.' }))
	const pages = buildAllPages(model, null, ['story-map', 'journey-board']).filter((r) => r.typeName === 'page')
	assert.equal(pages.length, 10)
	for (const p of pages) assert.doesNotThrow(() => validateIndexKey(p.index), `${p.name} got index ${p.index}`)
	assert.equal(new Set(pages.map((p) => p.index)).size, pages.length)
	assert.deepEqual([...pages].sort(sortByIndex).map((p) => p.name), pages.map((p) => p.name))
})
