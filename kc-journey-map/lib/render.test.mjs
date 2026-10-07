import assert from 'node:assert/strict'
import { test } from 'node:test'
import { execFile } from 'node:child_process'
import { createServer } from 'node:http'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { promisify } from 'node:util'
import { fileURLToPath } from 'node:url'
import { parse, stringify } from 'yaml'
import { createTLSchema } from '@tldraw/tlschema'
import { buildJourneyBoard, buildAllPages, staleRecordIds, staleBoardPages, handEditedIds, withRenderedText, carryAnnotations, renderToRoom } from './render.mjs'
import { buildStoryMap } from './storymap.mjs'
import { fixtureModel } from './fixture.mjs'
import { sortByIndex, validateIndexKey } from '@tldraw/utils'
import { fitHeight, label, note, richText, storyBorder, NOTE_SIZE } from './records.mjs'

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

test('a grown story or question pushes the notes below it down instead of covering them', () => {
	const model = structuredClone(fixtureModel)
	const story = model.steps[0].stories[0]
	story.card = 'Open the review page automatically when the gate is ready'
	story.questions = [
		{ id: 'long', ask: 'A question long enough to grow its note. '.repeat(4), answer: 'An answer. '.repeat(12) },
		{ id: 'next', ask: 'The next question' },
	]
	const records = buildJourneyBoard(model)
	const bottom = (s) => s.y + 200 + s.props.growY
	const card = kind(records, 'story').find((s) => s.meta.journey.nodeId === story.id)
	const [first, second] = ['long', 'next'].map((id) => kind(records, 'question').find((q) => q.meta.journey.nodeId === id))
	const answer = kind(records, 'answer').find((a) => a.meta.journey.nodeId === 'long')
	assert.ok(card.props.growY > 0 && first.props.growY > 0 && answer.props.growY > 0, 'the fixture did not grow its notes')
	assert.ok(first.y > bottom(card), 'the first question covers its grown story')
	assert.ok(second.y > Math.max(bottom(first), bottom(answer)), 'the next question covers a grown question or answer')
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

test('a generated shape edited on the canvas blocks the render that would overwrite it', () => {
	const rich = (text) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text }] }] })
	const drawn = withRenderedText([{ typeName: 'shape', id: 'shape:a', props: { richText: rich('原本') }, meta: { journey: { nodeId: 'a' } } }])[0]
	const edited = { ...drawn, props: { richText: rich('手改') } }
	const next = withRenderedText([{ ...drawn, props: { richText: rich('新版') } }])
	assert.deepEqual(handEditedIds([drawn], next, []), [])
	assert.deepEqual(handEditedIds([edited], next, []), ['shape:a'])
	assert.deepEqual(handEditedIds([edited], [], ['shape:a']), ['shape:a'])
	const legacy = { ...edited, meta: { journey: { nodeId: 'a' } } }
	assert.deepEqual(handEditedIds([legacy], next, []), [])
})

const optedOut = () => {
	const model = structuredClone(fixtureModel)
	model.releases[1].board = false
	return model
}
const pageIds = (records) => records.filter((r) => r.typeName === 'page').map((r) => r.id)

test('a release with board false gets no board page and keeps its story-map band', () => {
	assert.deepEqual(pageIds(buildAllPages(optedOut(), null, ['journey-board'])), ['page:jm-board-r1'])
	const withoutIndex = (records) => records.map(({ index, ...rest }) => rest)
	assert.deepEqual(withoutIndex(buildAllPages(optedOut(), null, ['story-map'])), withoutIndex(buildAllPages(fixtureModel, null, ['story-map'])))
	assert.ok(buildAllPages(optedOut(), null, ['story-map']).some((r) => r.id.includes('r2') || r.meta?.journey?.nodeId === 'r2'), 'the r2 band is missing from the story map')
})

test('every release opting out draws no board; no releases key draws the whole-journey board', () => {
	const none = structuredClone(fixtureModel)
	for (const release of none.releases) release.board = false
	assert.deepEqual(buildAllPages(none, null, ['journey-board']), [])
	const whole = structuredClone(fixtureModel)
	delete whole.releases
	assert.deepEqual(pageIds(buildAllPages(whole, null, ['journey-board'])), ['page:jm-board-all'])
})

const room = (model, selection = ['story-map', 'journey-board']) => buildAllPages(model, null, selection)
const boardShape = (page, id, meta = { journey: { nodeId: id, kind: 'story' } }) =>
	({ id: `shape:${id}`, typeName: 'shape', type: 'note', parentId: page, meta })

test('a re-render retires board pages it no longer draws: opted out, removed from the file, and the whole-journey page', () => {
	const current = room(fixtureModel)
	const shapes = current.filter((r) => r.typeName === 'shape')
	const onR2 = (r) => r.parentId === 'page:jm-board-r2' || (shapes.some((p) => p.id === r.parentId) && onR2(shapes.find((p) => p.id === r.parentId)))
	const generated = shapes.filter(onR2).map((r) => r.id)
	assert.ok(generated.some((id) => id.endsWith('-status-border')), 'the fixture draws no nested border, so this proves nothing')

	const out = staleBoardPages(current, buildAllPages(optedOut(), null, ['journey-board']), ['journey-board'])
	assert.deepEqual(out.pages, ['page:jm-board-r2'])
	assert.deepEqual(out.kept, [])
	assert.deepEqual(out.records.sort(), generated.sort())

	const dropped = structuredClone(fixtureModel)
	dropped.releases.pop()
	assert.deepEqual(staleBoardPages(current, room(dropped, ['journey-board']), ['journey-board']).pages, ['page:jm-board-r2'])

	const whole = structuredClone(fixtureModel)
	delete whole.releases
	const withAll = [...current, ...buildAllPages(whole, null, ['journey-board'])]
	assert.deepEqual(staleBoardPages(withAll, buildAllPages(fixtureModel, null, ['journey-board']), ['journey-board']).pages, ['page:jm-board-all'])
})

test('a stale board page holding a hand-drawn shape is kept with it; other pages are never touched', () => {
	const human = boardShape('page:jm-board-r2', 'human-note', {})
	const person = { id: 'page:xyz', typeName: 'page', name: 'Notes' }
	const current = [...room(fixtureModel), human, person, { id: 'page:jm-funcmap', typeName: 'page', name: 'Function map' }]
	const out = staleBoardPages(current, buildAllPages(optedOut(), null, ['journey-board']), ['journey-board'])
	assert.deepEqual(out.pages, [])
	assert.deepEqual(out.kept, [{ id: 'page:jm-board-r2', humanShapes: 1 }])
	assert.ok(!out.records.includes(human.id), 'the hand-drawn note was listed for removal')
	assert.ok(out.records.some((id) => current.find((r) => r.id === id)?.parentId === 'page:jm-board-r2'), 'generated shapes stayed')
	for (const id of ['page:xyz', 'page:jm-funcmap', 'page:page']) assert.ok(!out.pages.includes(id))
})

test('a render that does not select journey-board removes no board page', () => {
	const out = staleBoardPages(room(fixtureModel), buildAllPages(optedOut(), null, ['story-map']), ['story-map'])
	assert.deepEqual(out, { pages: [], kept: [], records: [] })
	assert.deepEqual(staleBoardPages(room(fixtureModel), buildAllPages(optedOut(), null, ['story-map']), undefined), { pages: [], kept: [], records: [] })
})

test('a generated card edited on a stale board page stops the render', () => {
	const rich = (text) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text }] }] })
	const current = withRenderedText(room(fixtureModel))
	const card = current.find((r) => r.typeName === 'shape' && r.parentId === 'page:jm-board-r2' && r.meta?.journey?.kind === 'story')
	card.props = { ...card.props, richText: rich('edited by hand') }
	const put = buildAllPages(optedOut(), null, ['journey-board'])
	const board = staleBoardPages(current, put, ['journey-board'])
	assert.ok(handEditedIds(current, put, [...board.records, ...board.pages]).includes(card.id))
	assert.deepEqual(handEditedIds(current, put, []), [], 'the edit is only visible once the stale removal list is built')
})

test('the render never removes the last page in the room', () => {
	const only = room(fixtureModel, ['journey-board']).filter((r) => r.id !== 'page:jm-board-r1' && r.parentId !== 'page:jm-board-r1')
	assert.deepEqual(pageIds(only), ['page:jm-board-r2'])
	const none = structuredClone(fixtureModel)
	for (const release of none.releases) release.board = false
	const out = staleBoardPages(only, buildAllPages(none, null, ['journey-board']), ['journey-board'])
	assert.deepEqual(out.pages, [])
	assert.deepEqual(out.kept, [{ id: 'page:jm-board-r2', humanShapes: 0 }])
})

const PKG_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const EXAMPLE = join(PKG_ROOT, 'skills/kc-journey-map/references/journey.example.yaml')

const stubRoom = async (run) => {
	const store = new Map()
	const patches = []
	const server = createServer((req, res) => {
		if (req.method === 'GET') {
			res.setHeader('content-type', 'application/json')
			return res.end(JSON.stringify({ snapshot: { documents: [...store.values()].map((state) => ({ state })) } }))
		}
		let body = ''
		req.on('data', (chunk) => { body += chunk })
		req.on('end', () => {
			const patch = JSON.parse(body)
			patches.push(patch)
			for (const r of patch.put ?? []) store.set(r.id, r)
			for (const id of patch.remove ?? []) store.delete(id)
			res.end('{}')
		})
	})
	await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve))
	try {
		return await run({ api: `http://127.0.0.1:${server.address().port}`, store, patches })
	} finally {
		server.closeAllConnections()
		server.close()
	}
}

// Two stories added to the first activity push the r2 stories of the example down by 500.
const exampleBeforeAndAfter = (t) => {
	const dir = mkdtempSync(join(tmpdir(), 'render-carry-'))
	t.after(() => rmSync(dir, { recursive: true, force: true }))
	const model = parse(readFileSync(EXAMPLE, 'utf8'))
	const before = join(dir, 'before.yaml')
	writeFileSync(before, stringify(model))
	model.steps[0].stories.push(
		{ id: 'reserve-two', card: 'Reserve a second copy', release: 'r1', status: 'unverified' },
		{ id: 'reserve-three', card: 'Reserve a third copy', release: 'r1', status: 'unverified' })
	const after = join(dir, 'after.yaml')
	writeFileSync(after, stringify(model))
	return { before, after }
}

const CARD = {
	moved: 'shape:sm-story-choose-pickup-day',
	alsoMoved: 'shape:sm-story-receive-reminder',
	stays: 'shape:sm-story-reserve-copy',
}

// Draws the example, then adds hand-drawn shapes: a frame round one moving card, a sticky across two
// moving cards, a tall frame across a moving and a staying card, and a sticky touching no card.
const drawWithAnnotations = async ({ before }, room) => {
	await renderToRoom({ path: before, room: 'carry', api: room.api })
	const at = (id) => room.store.get(id)
	const hand = (record) => ({ ...record, meta: {} })
	const moved = at(CARD.moved)
	const alsoMoved = at(CARD.alsoMoved)
	const stays = at(CARD.stays)
	const shapes = [
		hand(label({ id: 'shape:hand-frame', text: 'discussed', x: alsoMoved.x - 26, y: alsoMoved.y - 26, w: 252, h: 304, index: 'a8', color: 'light-blue', size: 's' })),
		hand(note({ id: 'shape:hand-both', text: 'across two cards', x: 450, y: moved.y + 50, index: 'a9', parentId: 'page:page' })),
		hand(label({ id: 'shape:hand-tall', text: 'across a card that stays', x: stays.x - 10, y: stays.y - 22, w: 240, h: moved.y + 250 - stays.y, index: 'a7', color: 'red', size: 's' })),
		hand(note({ id: 'shape:hand-loose', text: 'nowhere near', x: 3000, y: 3000, index: 'a6', parentId: 'page:page' })),
	]
	for (const s of shapes) room.store.set(s.id, s)
	return { moved, alsoMoved, positions: Object.fromEntries(shapes.map((s) => [s.id, [s.x, s.y]])) }
}

test('a re-render moves a hand-drawn shape with the cards it overlaps and lists the one it cannot place', async (t) => {
	const files = exampleBeforeAndAfter(t)
	await stubRoom(async (room) => {
		const { moved, alsoMoved, positions } = await drawWithAnnotations(files, room)
		const out = await renderToRoom({ path: files.after, room: 'carry', api: room.api })

		assert.equal(out.status, 200)
		assert.deepEqual([room.store.get(CARD.moved).y - moved.y, room.store.get(CARD.alsoMoved).y - alsoMoved.y], [500, 500], 'the example stopped moving its cards')
		const now = (id) => [room.store.get(id).x, room.store.get(id).y]
		const [frameX, frameY] = positions['shape:hand-frame']
		const [bothX, bothY] = positions['shape:hand-both']
		assert.deepEqual(now('shape:hand-frame'), [frameX, frameY + 500])
		assert.deepEqual(now('shape:hand-both'), [bothX, bothY + 500])
		assert.deepEqual(now('shape:hand-tall'), positions['shape:hand-tall'])
		assert.deepEqual(now('shape:hand-loose'), positions['shape:hand-loose'])
		assert.deepEqual(out.carried, [
			{ id: 'shape:hand-frame', cards: [CARD.alsoMoved], dx: 0, dy: 500 },
			{ id: 'shape:hand-both', cards: [CARD.moved, CARD.alsoMoved], dx: 0, dy: 500 },
		])
		assert.deepEqual(out.stranded, [{ id: 'shape:hand-tall', reason: 'cards-disagree', cards: [CARD.moved, CARD.stays] }])
	})
})

test('a render leaves a shape on a page it did not draw, and a second render of the same file carries nothing', async (t) => {
	const files = exampleBeforeAndAfter(t)
	await stubRoom(async (room) => {
		const { positions } = await drawWithAnnotations(files, room)
		const boardsOnly = await renderToRoom({ path: files.after, room: 'carry', api: room.api, selection: ['journey-board'] })
		assert.deepEqual([boardsOnly.carried, boardsOnly.stranded], [[], []])
		assert.equal(room.store.get(CARD.moved).y, 952, 'the story map was redrawn although it was not selected')
		for (const [id, xy] of Object.entries(positions)) assert.deepEqual([room.store.get(id).x, room.store.get(id).y], xy)

		await renderToRoom({ path: files.after, room: 'carry', api: room.api })
		const settled = Object.fromEntries(Object.keys(positions).map((id) => [id, [room.store.get(id).x, room.store.get(id).y]]))
		const again = await renderToRoom({ path: files.after, room: 'carry', api: room.api })
		assert.deepEqual([again.carried, again.stranded], [[], []])
		for (const id of Object.keys(positions)) {
			assert.deepEqual([room.store.get(id).x, room.store.get(id).y], settled[id])
			assert.ok(!room.patches.at(-1).put.some((r) => r.id === id), `${id} was written by a render that moved nothing`)
		}
	})
})

test('a render refused for a hand-edited card writes nothing and carries nothing', async (t) => {
	const files = exampleBeforeAndAfter(t)
	await stubRoom(async (room) => {
		const { positions } = await drawWithAnnotations(files, room)
		const card = room.store.get(CARD.stays)
		room.store.set(card.id, { ...card, props: { ...card.props, richText: richText('edited on the canvas') } })
		const sent = room.patches.length
		const out = await renderToRoom({ path: files.after, room: 'carry', api: room.api })
		assert.deepEqual(out.refused, [CARD.stays])
		assert.equal(out.carried, undefined)
		assert.equal(room.patches.length, sent, 'a refused render still sent a PATCH')
		for (const [id, xy] of Object.entries(positions)) assert.deepEqual([room.store.get(id).x, room.store.get(id).y], xy)
	})
})

const run = promisify(execFile)

test('the render CLI prints one line per carried and per stranded shape', async (t) => {
	const files = exampleBeforeAndAfter(t)
	await stubRoom(async (room) => {
		await drawWithAnnotations(files, room)
		const { stdout } = await run(process.execPath, ['lib/journey-render.mjs', files.after, 'carry'], { cwd: PKG_ROOT, env: { ...process.env, JOURNEY_API: room.api } })
		const lines = stdout.split('\n')
		assert.ok(lines.includes(`carried shape:hand-frame (0, 500) with ${CARD.alsoMoved}`), stdout)
		assert.ok(lines.includes(`carried shape:hand-both (0, 500) with ${CARD.moved}, ${CARD.alsoMoved}`), stdout)
		assert.ok(lines.includes(`stranded shape:hand-tall: cards-disagree ${CARD.moved}, ${CARD.stays}`), stdout)
		assert.equal(lines.filter((l) => /^(carried|stranded) /.test(l)).length, 3, 'a shape touching no card was listed')
	})
})

const card = (id, x, y, kind = 'story') => ({ id, typeName: 'shape', type: 'note', x, y, parentId: 'page:p', props: { scale: 1, growY: 0 }, meta: { journey: { kind } } })
const hand = (id, x, y, extra = {}) => ({ id, typeName: 'shape', type: 'note', x, y, parentId: 'page:p', props: { scale: 1, growY: 0 }, meta: {}, ...extra })
const movedBy = (record, dy) => ({ ...record, y: record.y + dy })

test('a shape over cards that move differently is returned as cards-disagree, never moved', () => {
	const a = card('shape:a', 0, 0), b = card('shape:b', 300, 0)
	const across = hand('shape:across', 150, 0)
	const out = carryAnnotations([a, b, across], [movedBy(a, 100), b], [])
	assert.deepEqual(out, { carried: [], stranded: [{ id: 'shape:across', reason: 'cards-disagree', cards: ['shape:a', 'shape:b'] }] })
})

test('a shape over a card this render removes is returned as card-removed, never moved', () => {
	const a = card('shape:a', 0, 0)
	const out = carryAnnotations([a, hand('shape:over', 100, 100)], [], ['shape:a'])
	assert.deepEqual(out, { carried: [], stranded: [{ id: 'shape:over', reason: 'card-removed', cards: ['shape:a'] }] })
})

test('a shape that overlaps no card with positive area is in neither list', () => {
	const a = card('shape:a', 0, 0)
	const edge = hand('shape:edge', 200, 0)
	const flow = { ...card('shape:flow', 1000, 0, 'flow'), type: 'geo', props: { w: 200, h: 200 } }
	const overFlow = hand('shape:over-flow', 1100, 100)
	const elsewhere = { ...hand('shape:other-page', 100, 100), parentId: 'page:q' }
	const nested = hand('shape:nested', 100, 100, { parentId: 'shape:frame' })
	const text = { ...hand('shape:text', 100, 100), type: 'text', props: { w: 80 } }
	const out = carryAnnotations([a, edge, flow, overFlow, elsewhere, nested, text], [movedBy(a, 100), movedBy(flow, 100)], [])
	assert.deepEqual(out, { carried: [], stranded: [] })
})

test('a shape over a card that stays put is not carried and not listed', () => {
	const a = card('shape:a', 0, 0)
	assert.deepEqual(carryAnnotations([a, hand('shape:over', 100, 100)], [a], []), { carried: [], stranded: [] })
})

test('the recorded incident: 8 shapes are carried, 7 to where the hand repair put them', () => {
	const raw = readFileSync(join(PKG_ROOT, 'lib/fixtures/render-annotation-geometry.json'), 'utf8')
	assert.ok(!/richText|assetId|"url"|"nodeId"/.test(raw), 'the geometry fixture holds text, a url, a node id or an asset reference')
	const { current, put, remove, repaired } = JSON.parse(raw)
	assert.ok(current.every((r) => Object.keys(r).sort().join() === 'id,meta,parentId,props,type,typeName,x,y'))

	const { carried, stranded } = carryAnnotations(current, put, remove)
	const annotations = current.filter((r) => !r.meta.journey)
	assert.equal(annotations.length, 74)
	assert.deepEqual(stranded, [])
	assert.equal(carried.length, 8)
	const at = new Map(current.map((r) => [r.id, r]))
	const toRepair = carried.filter((c) => repaired[c.id])
	assert.equal(toRepair.length, 7)
	for (const c of toRepair) assert.deepEqual([at.get(c.id).x + c.dx, at.get(c.id).y + c.dy], [repaired[c.id].x, repaired[c.id].y], c.id)

	// Where the rule and the hand repair differ: a 252 x 304 frame whose corner overlaps a card by 28px.
	// The hand repair left it in place; the rule keeps its offset to the card, so it moves by that card's delta.
	const [extra] = carried.filter((c) => !repaired[c.id])
	assert.deepEqual([at.get(extra.id).props.w, at.get(extra.id).props.h, extra.dx, extra.dy], [252, 304, 0, 750])
	assert.equal(annotations.length - carried.length, 66)
})
