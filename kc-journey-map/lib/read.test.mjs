
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { diffAgainstModel } from './read.mjs'
import { buildJourneyBoard, QUESTION_PITCH } from './render.mjs'
import { buildStoryMap } from './storymap.mjs'
import { fixtureModel } from './fixture.mjs'

const rt = (text) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text }] }] })

const board = () => buildJourneyBoard(fixtureModel).filter((r) => r.typeName === 'shape')
const story = () => buildStoryMap(fixtureModel).filter((r) => r.typeName === 'shape')
const rendered = () => [...board(), ...story()]
const BOARD = 'shape:jm-all-'

const find = (shapes, id) => shapes.find((s) => s.id === id)
const clean = { reordered: null, reorderConflict: null, reworded: [], rewordConflict: [], releaseMoved: [], storiesReordered: [], duplicated: [], unclaimed: [], missing: [],
	questionsAdded: [], questionsReworded: [], questionsDeleted: [], answersAdded: [], answersReworded: [], answersDeleted: [] }

test('a freshly rendered board reports no drift', () => {
	assert.deepEqual(diffAgainstModel(rendered(), fixtureModel), clean)
})

test('rewording an activity on the story map is seen', () => {
	const shapes = rendered()
	find(shapes, 'shape:sm-act-b').props.richText = rt('Receives the thing')
	const d = diffAgainstModel(shapes, fixtureModel)
	assert.equal(d.reworded.length, 1)
	assert.deepEqual(
		{ id: d.reworded[0].id, page: d.reworded[0].page, now: d.reworded[0].now },
		{ id: 'b', page: 'storymap', now: 'Receives the thing' }
	)
})

test('dragging a story up inside its band is a priority change', () => {
	const shapes = rendered()
	const first = find(shapes, 'shape:sm-story-a-0')
	const second = find(shapes, 'shape:sm-story-a-2')
	;[first.y, second.y] = [second.y, first.y]
	const d = diffAgainstModel(shapes, fixtureModel)
	assert.deepEqual(d.storiesReordered, [{ step: 'a', release: 'r1', was: ['a-0', 'a-2'], now: ['a-2', 'a-0'] }])
	assert.deepEqual(d.releaseMoved, [], 'a move inside a band is not a release change')
})

test('dragging a story across a release line is read as a release change', () => {
	const shapes = rendered()
	const line = shapes.filter((s) => s.meta?.journey?.kind === 'release-line').sort((a, b) => a.y - b.y)[0]
	find(shapes, 'shape:sm-story-a-0').y = line.y + 50
	const d = diffAgainstModel(shapes, fixtureModel)
	assert.deepEqual(d.releaseMoved, [{ id: 'a-0', step: 'a', was: 'r1', now: 'r2' }])
})

test('a release change is written into the file', () => {
	const path = onDisk()
	applyDiff(path, { ...clean, releaseMoved: [{ id: 'a-0', step: 'a', was: 'r1', now: 'r2' }] })
	const after = readFileSync(path, 'utf8')
	const block = after.slice(after.indexOf('id: a-0'), after.indexOf('id: a-2'))
	assert.match(block, /release: r2/, 'the story kept its old release')
})

test('the two pages disagreeing about one card is a conflict, not a winner', () => {
	const shapes = rendered()
	find(shapes, `${BOARD}card-a`).props.richText = rt('Board wording')
	find(shapes, 'shape:sm-act-a').props.richText = rt('Story map wording')
	const d = diffAgainstModel(shapes, fixtureModel)
	assert.equal(d.reworded.length, 0, 'a conflicting reword must not be applied')
	assert.deepEqual(d.rewordConflict, [{ id: 'a', field: 'card', board: 'Board wording', storymap: 'Story map wording' }])
})

test('the two pages in different column orders is a conflict', () => {
	const shapes = rendered()
	const [ca, cb] = [find(shapes, `${BOARD}card-a`), find(shapes, `${BOARD}card-b`)]
	;[ca.x, cb.x] = [cb.x, ca.x]
	const [sa, sc] = [find(shapes, 'shape:sm-act-a'), find(shapes, 'shape:sm-act-c')]
	;[sa.x, sc.x] = [sc.x, sa.x]
	const d = diffAgainstModel(shapes, fixtureModel)
	assert.equal(d.reordered, null, 'neither order may win')
	assert.deepEqual(d.reorderConflict, { board: ['b', 'a', 'c'], storymap: ['c', 'b', 'a'] })
})

test('a hand-added card is placed under the column it sits beneath', () => {
	const shapes = rendered()
	const anchor = find(shapes, 'shape:sm-act-b')
	shapes.push({ id: 'shape:hand', typeName: 'shape', type: 'note', parentId: 'page:page', x: anchor.x, y: anchor.y + 900, props: { richText: rt('A question nobody answered') } })
	const [card] = diffAgainstModel(shapes, fixtureModel).unclaimed
	assert.deepEqual({ page: card.page, column: card.column }, { page: 'storymap', column: 'b' })
})

test('a card straddling two columns is reported, never guessed', () => {
	const shapes = rendered()
	const [b, c] = [find(shapes, 'shape:sm-act-b'), find(shapes, 'shape:sm-act-c')]
	shapes.push({ id: 'shape:hand', typeName: 'shape', type: 'note', parentId: 'page:page', x: (b.x + c.x) / 2, y: b.y + 900, props: { richText: rt('Which column is this?') } })
	const [card] = diffAgainstModel(shapes, fixtureModel).unclaimed
	assert.equal(card.column, null, 'an ambiguous card must not be assigned')
	assert.deepEqual(card.candidates.map((c) => c.step).sort(), ['b', 'c'])
})


import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { parse, stringify } from 'yaml'
import { applyDiff } from './read.mjs'

const onDisk = () => {
	const dir = mkdtempSync(join(tmpdir(), 'journey-'))
	const path = join(dir, 'j.yaml')
	writeFileSync(path, stringify(fixtureModel, { lineWidth: 0, flowCollectionPadding: false }))
	return path
}

test('a story dragged up is reordered in the file', () => {
	const path = onDisk()
	const { applied } = applyDiff(path, {
		...clean,
		storiesReordered: [{ step: 'a', was: ['a-0', 'a-1'], now: ['a-1', 'a-0'] }],
	})
	assert.ok(applied.some((a) => a.includes('reprioritised')), applied.join())
	const after = readFileSync(path, 'utf8')
	assert.ok(after.indexOf('Picks a target') < after.indexOf('Names it'), 'the file kept the old priority')
})

test('a reworded story is rewritten in the file', () => {
	const path = onDisk()
	applyDiff(path, { ...clean, reworded: [{ id: 'a-0', field: 'story', step: 'a', was: 'Names it', now: 'Gives it a name' }] })
	assert.match(readFileSync(path, 'utf8'), /Gives it a name/)
})

test('a conflict is refused and nothing is written', () => {
	const path = onDisk()
	const before = readFileSync(path, 'utf8')
	const { applied, skipped } = applyDiff(path, {
		...clean,
		reorderConflict: { board: ['b', 'a', 'c'], storymap: ['c', 'b', 'a'] },
		rewordConflict: [{ id: 'a', field: 'card', board: 'x', storymap: 'y' }],
	})
	assert.deepEqual(applied, [])
	assert.equal(skipped.length, 2, skipped.join(' | '))
	assert.equal(readFileSync(path, 'utf8'), before, 'the file was written despite a conflict')
})

test('a story written in object form is reworded too', () => {
	const path = onDisk()
	applyDiff(path, {
		...clean,
		reworded: [{ id: 'b-see', field: 'story', step: 'b', was: 'Sees it arrive', now: 'Watches it land' }],
	})
	const after = readFileSync(path, 'utf8')
	assert.match(after, /Watches it land/)
	assert.match(after, /id: b-see/, 'the story lost its id and became a bare string')
})

import { buildAllPages } from './render.mjs'

test('with no selection, buildAllPages draws the story map alone', () => {
	const pages = buildAllPages(fixtureModel).filter((r) => r.typeName === 'page').map((r) => r.id)
	assert.deepEqual(pages, ['page:page'])
})

test('an empty selection falls back to the default rather than rendering nothing', () => {
	// An empty selection must not reconcile away every journey shape.
	const pages = buildAllPages(fixtureModel, null, []).filter((r) => r.typeName === 'page').map((r) => r.id)
	assert.deepEqual(pages, ['page:page'])
})

test('selecting the journey board draws one page per release, alongside the story map', () => {
	const pages = buildAllPages(fixtureModel, null, ['story-map', 'journey-board']).filter((r) => r.typeName === 'page').map((r) => r.id)
	const expectedBoards = fixtureModel.releases.map((r) => `page:jm-board-${r.id}`)
	assert.deepEqual(pages, ['page:page', ...expectedBoards])
})


const releaseBoards = (model = fixtureModel) => buildAllPages(model, null, ['story-map', 'journey-board'])
	.filter((s) => s.typeName === 'shape')

test('fresh release boards and story map share story ids without duplicates or drift', () => {
	assert.deepEqual(diffAgainstModel(releaseBoards(), fixtureModel), clean)
})

test('editing a release story round-trips its identity and leaves the original file alone with save-as', () => {
	const shapes = releaseBoards()
	find(shapes, 'shape:jm-r1-story-a-0').props.richText = rt('Gives it a name')
	const diff = diffAgainstModel(shapes, fixtureModel)
	assert.deepEqual(diff.reworded, [{ id: 'a-0', field: 'story', page: 'board:r1', step: 'a', was: 'Names it', now: 'Gives it a name' }])
	const path = onDisk()
	const before = readFileSync(path, 'utf8')
	const out = `${path}.updated`
	applyDiff(path, diff, out)
	assert.match(readFileSync(out, 'utf8'), /Gives it a name/)
	assert.equal(readFileSync(path, 'utf8'), before)
})

test('different story edits across projections are refused; matching edits apply once', () => {
	const shapes = releaseBoards()
	find(shapes, 'shape:jm-r1-story-a-0').props.richText = rt('Board wording')
	find(shapes, 'shape:sm-story-a-0').props.richText = rt('Map wording')
	const diff = diffAgainstModel(shapes, fixtureModel)
	assert.deepEqual(diff.reworded, [])
	assert.deepEqual(diff.rewordConflict, [{ id: 'a-0', field: 'story', board: 'Board wording', storymap: 'Map wording' }])
	const path = onDisk()
	const before = readFileSync(path, 'utf8')
	assert.equal(applyDiff(path, diff).wrote, null)
	assert.equal(readFileSync(path, 'utf8'), before)
	find(shapes, 'shape:sm-story-a-0').props.richText = rt('Board wording')
	assert.equal(diffAgainstModel(shapes, fixtureModel).reworded.length, 1)
})

test('a story duplicated within a release page is ambiguous even if the map has an edit', () => {
	const shapes = releaseBoards()
	const copy = structuredClone(find(shapes, 'shape:jm-r1-story-a-0'))
	copy.id = 'shape:copy'
	shapes.push(copy)
	find(shapes, 'shape:sm-story-a-0').props.richText = rt('Should not apply')
	const diff = diffAgainstModel(shapes, fixtureModel)
	assert.deepEqual(diff.duplicated, ['a-0'])
	assert.deepEqual(diff.reworded, [])
})

test('activity headings target activity rather than card and detect competing release edits', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].activity = 'Ask'
	const shapes = releaseBoards(model)
	find(shapes, 'shape:jm-r1-card-a').props.richText = rt('Request')
	assert.deepEqual(diffAgainstModel(shapes, model).reworded, [{ id: 'a', field: 'activity', page: 'board:r1', was: 'Ask', now: 'Request' }])
	find(shapes, 'shape:jm-r2-card-a').props.richText = rt('Choose')
	const diff = diffAgainstModel(shapes, model)
	assert.deepEqual(diff.reworded, [])
	assert.equal(diff.rewordConflict[0].field, 'activity')
})

test('a release-only board cannot reorder the full journey or change membership and priority', () => {
	const shapes = buildJourneyBoard(fixtureModel, { release: fixtureModel.releases[0] }).filter((s) => s.typeName === 'shape')
	const a = find(shapes, 'shape:jm-r1-card-a')
	const c = find(shapes, 'shape:jm-r1-card-c')
	;[a.x, c.x] = [c.x, a.x]
	find(shapes, 'shape:jm-r1-story-a-0').y += 2000
	const diff = diffAgainstModel(shapes, fixtureModel)
	assert.equal(diff.reordered, null)
	assert.deepEqual(diff.releaseMoved, [])
	assert.deepEqual(diff.storiesReordered, [])
})

test('hand-added notes use the activity span on their own release page', () => {
	const shapes = releaseBoards()
	const a = find(shapes, 'shape:jm-r1-card-a')
	shapes.push({ id: 'shape:hand', typeName: 'shape', type: 'note', parentId: a.parentId,
		x: a.x + 50, y: a.y + 900, props: { richText: rt('Another question') } })
	assert.equal(diffAgainstModel(shapes, fixtureModel).unclaimed[0].column, 'a')
})

test('legacy numbered step cards remain readable', () => {
	const shapes = [{ id: 'shape:legacy', typeName: 'shape', type: 'note', parentId: 'page:jm-board-all',
		x: 0, y: 0, props: { richText: rt('1. New legacy wording') }, meta: { journey: { nodeId: 'a', kind: 'step-card' } } }]
	assert.deepEqual(diffAgainstModel(shapes, fixtureModel).reworded, [{ id: 'a', field: 'card', page: 'board:all', was: 'Asks for the thing', now: 'New legacy wording' }])
})

test('stories with the same wording are written by id, not by first text match', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].stories[1].card = 'Names it'
	const path = onDisk()
	writeFileSync(path, stringify(model))
	const shapes = releaseBoards(model)
	find(shapes, 'shape:jm-r1-story-a-2').props.richText = rt('Second story changed')
	applyDiff(path, diffAgainstModel(shapes, model))
	const after = parse(readFileSync(path, 'utf8'))
	assert.equal(after.steps[0].stories[0].card, 'Names it')
	assert.equal(after.steps[0].stories[1].card, 'Second story changed')
})


test('a bare-string story on the whole-journey board can be reworded', () => {
	const shapes = rendered()
	find(shapes, 'shape:jm-all-story-c-1').props.richText = rt('A clearer unplaced idea')
	const path = onDisk()
	applyDiff(path, diffAgainstModel(shapes, fixtureModel))
	const after = parse(readFileSync(path, 'utf8'))
	assert.equal(after.steps[2].stories[1], 'A clearer unplaced idea')
})

test('a stale story wording diff does not overwrite a newer file edit', () => {
	const shapes = releaseBoards()
	find(shapes, 'shape:jm-r1-story-a-0').props.richText = rt('Canvas wording')
	const diff = diffAgainstModel(shapes, fixtureModel)
	const path = onDisk()
	const newer = readFileSync(path, 'utf8').replace('Names it', 'Newer file wording')
	writeFileSync(path, newer)
	const result = applyDiff(path, diff)
	assert.equal(result.wrote, null)
	assert.match(result.skipped[0], /wording changed in the file/)
	assert.equal(readFileSync(path, 'utf8'), newer)
})

for (const field of ['activity', 'card']) {
	test(`stale ${field} wording is refused while current wording applies`, () => {
		const model = structuredClone(fixtureModel)
		model.steps[0][field] = 'Original wording'
		const path = onDisk()
		writeFileSync(path, stringify(model))
		const shapes = releaseBoards(model)
		find(shapes, 'shape:jm-r1-card-a').props.richText = rt('Canvas wording')
		const diff = diffAgainstModel(shapes, model)
		assert.equal(diff.reworded[0].field, field)
		assert.ok(applyDiff(path, diff).applied.length)
		assert.equal(parse(readFileSync(path, 'utf8')).steps[0][field], 'Canvas wording')
		model.steps[0][field] = 'Newer file wording'
		writeFileSync(path, stringify(model))
		const before = readFileSync(path, 'utf8')
		const result = applyDiff(path, diff)
		assert.equal(result.wrote, null)
		assert.match(result.skipped[0], /wording changed in the file/)
		assert.equal(readFileSync(path, 'utf8'), before)
	})
}

test('a hand-added note under a story becomes a new question', () => {
	const shapes = releaseBoards()
	const storyShape = find(shapes, 'shape:jm-r1-story-a-0')
	shapes.push({ id: 'shape:hand-q', typeName: 'shape', type: 'note', parentId: storyShape.parentId,
		x: storyShape.x, y: storyShape.y + 250, props: { richText: rt('Is this synchronous?') } })
	const diff = diffAgainstModel(shapes, fixtureModel)
	assert.deepEqual(diff.questionsAdded,
		[{ story: 'a-0', step: 'a', id: 'a-0-q0', ask: 'Is this synchronous?', page: 'board:r1', shapeId: 'shape:hand-q' }])
	assert.deepEqual(diff.answersAdded, [])
	assert.equal(diff.unclaimed.length, 0)
})

test('a hand-added note beside an open question becomes its answer', () => {
	const shapes = releaseBoards()
	const q = find(shapes, 'shape:jm-r1-question-b-see-b-see-q0')
	shapes.push({ id: 'shape:hand-a', typeName: 'shape', type: 'note', parentId: q.parentId,
		x: q.x + QUESTION_PITCH, y: q.y, props: { richText: rt('Push, with a retry queue.'), url: 'https://example.com/delivery' } })
	const diff = diffAgainstModel(shapes, fixtureModel)
	assert.deepEqual(diff.answersAdded, [{ story: 'b-see', step: 'b', question: 'b-see-q0',
		answer: 'Push, with a retry queue.', doc: 'https://example.com/delivery', page: 'board:r1', shapeId: 'shape:hand-a' }])
	assert.deepEqual(diff.questionsAdded, [])
})

test('editing a generated question note updates its ask', () => {
	const shapes = releaseBoards()
	find(shapes, 'shape:jm-r1-question-b-see-b-see-q0').props.richText = rt('Should delivery retry automatically?')
	const diff = diffAgainstModel(shapes, fixtureModel)
	assert.deepEqual(diff.questionsReworded, [{ story: 'b-see', step: 'b', id: 'b-see-q0',
		was: 'Should delivery be push or pull?', now: 'Should delivery retry automatically?', page: 'board:r1' }])
})

test('editing a generated answer note updates its answer and doc', () => {
	const model = structuredClone(fixtureModel)
	delete model.steps[1].stories[0].question
	model.steps[1].stories[0].questions = [{ id: 'b-see-q0', ask: 'Should delivery be push or pull?', answer: 'Push.', doc: 'https://example.com/old' }]
	const shapes = releaseBoards(model)
	const a = find(shapes, 'shape:jm-r1-answer-b-see-b-see-q0')
	a.props.richText = rt('Push, confirmed by the delivery team.')
	a.props.url = 'https://example.com/new'
	const diff = diffAgainstModel(shapes, model)
	assert.deepEqual(diff.answersReworded, [{ story: 'b-see', step: 'b', question: 'b-see-q0',
		was: { answer: 'Push.', doc: 'https://example.com/old' },
		now: { answer: 'Push, confirmed by the delivery team.', doc: 'https://example.com/new' }, page: 'board:r1' }])
})

test('deleting a generated question note is reported, not silently applied', () => {
	const shapes = releaseBoards().filter((s) => s.id !== 'shape:jm-r1-question-b-see-b-see-q0')
	const diff = diffAgainstModel(shapes, fixtureModel)
	assert.deepEqual(diff.questionsDeleted,
		[{ story: 'b-see', step: 'b', id: 'b-see-q0', was: 'Should delivery be push or pull?', page: 'board:r1' }])
	const path = onDisk()
	const before = readFileSync(path, 'utf8')
	applyDiff(path, diff)
	assert.equal(readFileSync(path, 'utf8'), before, 'a reported deletion must not be written')
})

test('deleting a generated answer note is reported, not silently applied', () => {
	const model = structuredClone(fixtureModel)
	delete model.steps[1].stories[0].question
	model.steps[1].stories[0].questions = [{ id: 'b-see-q0', ask: 'Should delivery be push or pull?', answer: 'Push.' }]
	const shapes = releaseBoards(model).filter((s) => s.id !== 'shape:jm-r1-answer-b-see-b-see-q0')
	const diff = diffAgainstModel(shapes, model)
	assert.deepEqual(diff.answersDeleted,
		[{ story: 'b-see', step: 'b', question: 'b-see-q0', was: { answer: 'Push.', doc: undefined }, page: 'board:r1' }])
})

test('a note exactly on a neighbouring story column is its question, not the open answer slot 20px away', () => {
	// a-0 with one open question reserves the same STORY_PITCH width as no question at all,
	// so a-2's own column sits only QUESTION_GAP (10px) past a-0's answer slot — the
	// collision the tolerance has to resolve, not just avoid by luck.
	const model = structuredClone(fixtureModel)
	model.steps[0].stories[0].questions = [{ id: 'a-0-q0', ask: 'Confirmed by whom?' }]
	const shapes = releaseBoards(model)
	const q = find(shapes, 'shape:jm-r1-question-a-0-a-0-q0')
	const storyA2 = find(shapes, 'shape:jm-r1-story-a-2')
	shapes.push({ id: 'shape:hand-col', typeName: 'shape', type: 'note', parentId: q.parentId,
		x: storyA2.x, y: q.y, props: { richText: rt('A question about confirming it') } })
	const diff = diffAgainstModel(shapes, model)
	assert.deepEqual(diff.answersAdded, [])
	assert.equal(diff.questionsAdded.length, 1)
	assert.equal(diff.questionsAdded[0].story, 'a-2')
})

test('the mirror: a note exactly on the open answer slot is that answer, not the neighbouring column', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].stories[0].questions = [{ id: 'a-0-q0', ask: 'Confirmed by whom?' }]
	const shapes = releaseBoards(model)
	const q = find(shapes, 'shape:jm-r1-question-a-0-a-0-q0')
	shapes.push({ id: 'shape:hand-row', typeName: 'shape', type: 'note', parentId: q.parentId,
		x: q.x + QUESTION_PITCH, y: q.y, props: { richText: rt('By the requester.') } })
	const diff = diffAgainstModel(shapes, model)
	assert.deepEqual(diff.questionsAdded, [])
	assert.equal(diff.answersAdded.length, 1)
	assert.equal(diff.answersAdded[0].question, 'a-0-q0')
})

test('a note exactly between the two slots is reported, never guessed', () => {
	const model = structuredClone(fixtureModel)
	model.steps[0].stories[0].questions = [{ id: 'a-0-q0', ask: 'Confirmed by whom?' }]
	const shapes = releaseBoards(model)
	const q = find(shapes, 'shape:jm-r1-question-a-0-a-0-q0')
	const storyA2 = find(shapes, 'shape:jm-r1-story-a-2')
	const x = (q.x + QUESTION_PITCH + storyA2.x) / 2
	shapes.push({ id: 'shape:hand-amb', typeName: 'shape', type: 'note', parentId: q.parentId,
		x, y: q.y, props: { richText: rt('Which one is this?') } })
	const diff = diffAgainstModel(shapes, model)
	assert.deepEqual(diff.questionsAdded, [])
	assert.deepEqual(diff.answersAdded, [])
	assert.ok(diff.unclaimed.some((u) => u.id === 'shape:hand-amb'))
})

test('an unrelated hand-added note is not read as a question or answer', () => {
	const shapes = releaseBoards()
	shapes.push({ id: 'shape:hand-note', typeName: 'shape', type: 'note', parentId: 'page:jm-board-r1',
		x: 5000, y: 5000, props: { richText: rt('Lunch on Thursday?') } })
	const diff = diffAgainstModel(shapes, fixtureModel)
	assert.equal(diff.questionsAdded.length, 0)
	assert.equal(diff.answersAdded.length, 0)
	assert.ok(diff.unclaimed.some((u) => u.id === 'shape:hand-note'))
})

test('a new question is appended to the story it belongs to', () => {
	const shapes = releaseBoards()
	const storyShape = find(shapes, 'shape:jm-r1-story-a-0')
	shapes.push({ id: 'shape:hand-new-q', typeName: 'shape', type: 'note', parentId: storyShape.parentId,
		x: storyShape.x, y: storyShape.y + 250, props: { richText: rt('Is this synchronous?') } })
	const diff = diffAgainstModel(shapes, fixtureModel)
	const path = onDisk()
	applyDiff(path, diff, path)
	const after = parse(readFileSync(path, 'utf8'))
	const written = after.steps[0].stories.find((s) => s.id === 'a-0')
	assert.deepEqual(written.questions, [{ id: 'a-0-q0', ask: 'Is this synchronous?' }])
})

test('a new answer is attached to its question, upgrading question sugar to a map', () => {
	const shapes = releaseBoards()
	const q = find(shapes, 'shape:jm-r1-question-b-see-b-see-q0')
	shapes.push({ id: 'shape:hand-new-a', typeName: 'shape', type: 'note', parentId: q.parentId,
		x: q.x + QUESTION_PITCH, y: q.y, props: { richText: rt('Push.'), url: 'https://example.com/answer' } })
	const diff = diffAgainstModel(shapes, fixtureModel)
	const path = onDisk()
	applyDiff(path, diff, path)
	const after = parse(readFileSync(path, 'utf8'))
	const written = after.steps[1].stories.find((s) => s.id === 'b-see')
	assert.deepEqual(written.questions, [{ id: 'b-see-q0', ask: 'Should delivery be push or pull?', answer: 'Push.', doc: 'https://example.com/answer' }])
	assert.equal(written.question, undefined)
})

test('applying a new question reports only its own shape as absorbed, leaving an unrelated note alone', () => {
	const shapes = releaseBoards()
	const storyShape = find(shapes, 'shape:jm-r1-story-a-0')
	shapes.push({ id: 'shape:hand-q2', typeName: 'shape', type: 'note', parentId: storyShape.parentId,
		x: storyShape.x, y: storyShape.y + 250, props: { richText: rt('Is this synchronous?') } })
	shapes.push({ id: 'shape:hand-unrelated', typeName: 'shape', type: 'note', parentId: storyShape.parentId,
		x: 9000, y: 9000, props: { richText: rt('Unrelated note') } })
	const diff = diffAgainstModel(shapes, fixtureModel)
	const path = onDisk()
	const { applied, absorbed } = applyDiff(path, diff, path)
	assert.ok(applied.some((a) => a.includes('a-0')))
	assert.deepEqual(absorbed.map((a) => a.shapeId), ['shape:hand-q2'])
})
