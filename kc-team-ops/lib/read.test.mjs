// node --test lib/*.test.mjs
//
// Drives the reader against shapes the renderer actually produced, not hand-built ones,
// so a change in what the renderer tags is caught here rather than in a browser.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { diffAgainstModel } from './read.mjs'
import { buildJourneyBoard } from './render.mjs'
import { buildStoryMap } from './storymap.mjs'
import { fixtureModel } from './fixture.mjs'

const rt = (text) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text }] }] })

const board = () => buildJourneyBoard(fixtureModel).map((r) => ({ ...r, parentId: 'page:page' }))
const story = () => buildStoryMap(fixtureModel).filter((r) => r.typeName === 'shape')
const rendered = () => [...board(), ...story()]

const find = (shapes, id) => shapes.find((s) => s.id === id)
const clean = { reordered: null, reorderConflict: null, reworded: [], rewordConflict: [], releaseMoved: [], storiesReordered: [], duplicated: [], unclaimed: [], missing: [] }

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
	// The planning gesture: this belongs in a later release, or has been pulled forward.
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
	find(shapes, 'shape:jm-card-a').props.richText = rt('1. Board wording')
	find(shapes, 'shape:sm-act-a').props.richText = rt('Story map wording')
	const d = diffAgainstModel(shapes, fixtureModel)
	assert.equal(d.reworded.length, 0, 'a conflicting reword must not be applied')
	assert.deepEqual(d.rewordConflict, [{ id: 'a', field: 'card', board: 'Board wording', storymap: 'Story map wording' }])
})

test('the two pages in different column orders is a conflict', () => {
	const shapes = rendered()
	const [ca, cb] = [find(shapes, 'shape:jm-card-a'), find(shapes, 'shape:jm-card-b')]
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
	shapes.push({ id: 'shape:hand', typeName: 'shape', type: 'note', parentId: 'page:jm-storymap', x: anchor.x, y: anchor.y + 900, props: { richText: rt('A question nobody answered') } })
	const [card] = diffAgainstModel(shapes, fixtureModel).unclaimed
	assert.deepEqual({ page: card.page, column: card.column }, { page: 'storymap', column: 'b' })
})

test('a card straddling two columns is reported, never guessed', () => {
	const shapes = rendered()
	const [b, c] = [find(shapes, 'shape:sm-act-b'), find(shapes, 'shape:sm-act-c')]
	shapes.push({ id: 'shape:hand', typeName: 'shape', type: 'note', parentId: 'page:jm-storymap', x: (b.x + c.x) / 2, y: b.y + 900, props: { richText: rt('Which column is this?') } })
	const [card] = diffAgainstModel(shapes, fixtureModel).unclaimed
	assert.equal(card.column, null, 'an ambiguous card must not be assigned')
	assert.deepEqual(card.candidates.map((c) => c.step).sort(), ['b', 'c'])
})

// ── applying it back to the file ────────────────────────────────────────────────

import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { stringify } from 'yaml'
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
	// Stories may be a bare string or {id, card}; they take different branches on the way
	// back into the file, and only the string one was covered.
	const path = onDisk()
	applyDiff(path, {
		...clean,
		reworded: [{ id: 'b-see', field: 'story', step: 'b', was: 'Sees it arrive', now: 'Watches it land' }],
	})
	const after = readFileSync(path, 'utf8')
	assert.match(after, /Watches it land/)
	// Rewriting the whole entry as a bare string would also satisfy the line above while
	// silently dropping the story's id, so the id is what the assertion is really for.
	assert.match(after, /id: b-see/, 'the story lost its id and became a bare string')
})
