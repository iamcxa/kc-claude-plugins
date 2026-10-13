import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { test } from 'node:test'
import { parse, parseDocument } from 'yaml'
import { WRITE_OPTS } from './read.mjs'
import { BLOCK, FLOW, footprint } from './fixtures/journey-fold-shapes.mjs'
import { planFold, readFootprints } from './journey-fold.mjs'
import { iterStories } from './model.mjs'

const lines = (s) => s.split('\n')
const changed = (a, b) => {
	const before = lines(a), after = lines(b)
	return { removed: before.filter((l) => !after.includes(l)), added: after.filter((l) => !before.includes(l)) }
}
const fold = (src, ...fps) => planFold(src, fps)

test('flow shape: only the folded question line changes, with answer, status and source', () => {
	const { draft, results } = fold(FLOW, footprint())
	assert.deepEqual(results.map((r) => r.outcome), ['applied'])
	const { removed, added } = changed(FLOW, draft)
	assert.equal(removed.length, 1)
	assert.match(removed[0], /id: q1, status: open, ask: "Who issues codes\?"/)
	assert.equal(added.length, 1)
	const q = parse(draft).steps[0].stories[0].questions[0]
	assert.deepEqual(q, { id: 'q1', status: 'answered', ask: 'Who issues codes?', answer: 'Platform issues codes.',
		source: { kind: 'gate', ref: 't/gate-attempt:t-1', words: '好，由平台發', date: '2026-10-13' } })
	assert.equal(parse(draft).steps[0].stories[1].questions[0].answer, undefined, 'the same question id on another story is untouched')
})

test('block shape: whole-file re-serialization rewrites the file, the fold adds lines inside the question only', () => {
	assert.notEqual(parseDocument(BLOCK).toString(WRITE_OPTS), BLOCK, 'the fixture must defeat a whole-file rewrite')
	const { draft } = fold(BLOCK, footprint({ journey: 'review', story: 'front-door', question: 'public-contract' }))
	const { removed, added } = changed(BLOCK, draft)
	assert.deepEqual(removed, [])
	assert.equal(added.length, 3)
	const at = lines(draft).indexOf(added[0])
	assert.equal(lines(draft)[at - 1], '        it?', 'inserted after the question’s last wrapped line')
	assert.match(lines(draft)[at + 3], /^    - id: audience$/)
	assert.equal(parse(draft).steps[0].stories[0].questions[1].status, 'answered')
})

test('block shape: a last question in a file with no trailing newline is folded onto its own lines', () => {
	const bare = BLOCK.replace(/\n$/, '').replace(/\n  - id: no-questions[\s\S]*$/, '') + '\n    - id: tail\n      ask: Last one'
	const { draft, results } = fold(bare, footprint({ journey: 'review', story: 'front-door', question: 'tail' }))
	assert.deepEqual(results.map((r) => r.outcome), ['applied'])
	assert.match(draft, /ask: Last one\n      answer: /)
	assert.equal(parse(draft).steps[0].stories[0].questions.at(-1).status, 'answered')
})

test('folding twice gives the same bytes and reports already', () => {
	const first = fold(FLOW, footprint())
	const second = planFold(first.draft, [footprint()])
	assert.equal(second.draft, first.draft)
	assert.deepEqual(second.results.map((r) => r.outcome), ['already'])
})

test('a different existing answer or source is a conflict and writes nothing for that question', () => {
	const { draft, results } = fold(FLOW, footprint({ question: 'q2' }))
	assert.deepEqual(results.map((r) => r.outcome), ['conflict'])
	assert.equal(draft, FLOW)
	const folded = fold(FLOW, footprint())
	const other = planFold(folded.draft, [footprint({ id: 'fp:u:1', task: 'u', source: 'gate-attempt:u-1' })])
	assert.deepEqual(other.results.map((r) => r.outcome), ['conflict'])
	assert.equal(other.draft, folded.draft)
})

test('an answer reworded or a status changed after folding is a conflict, not already, and writes nothing', () => {
	const folded = fold(FLOW, footprint()).draft
	for (const [label, edited] of [['answer', folded.replace('Platform issues codes.', 'Reworded by hand.')], ['status', folded.replace('status: answered, ask: "Who', 'status: open, ask: "Who')]]) {
		assert.notEqual(edited, folded, label)
		const again = planFold(edited, [footprint()])
		assert.deepEqual(again.results.map((r) => r.outcome), ['conflict'], label)
		assert.match(again.results[0].detail, new RegExp(`its ${label} no longer matches`))
		assert.equal(again.draft, edited, label)
	}
})

test('a story id or question id that matches twice is refused naming both, and the command writes no draft', (t) => {
	const dupQuestion = FLOW.replace('          - {id: q1, status: open, ask: "Who issues codes?"}', '          - {id: q1, status: open, ask: "Who issues codes?"}\n          - {id: q1, status: open, ask: "Again"}')
	const dupStory = FLOW.replace('      - id: pick-nearby', '      - id: enter-by-qr\n        release: r1\n        status: gap\n        card: "Twin"\n      - id: pick-nearby')
	const asked = fold(dupQuestion, footprint())
	assert.deepEqual(asked.results.map((r) => r.outcome), ['ambiguous'])
	assert.match(asked.results[0].detail, /question "q1" in story "enter-by-qr" matches 2 questions/)
	assert.equal(asked.draft, dupQuestion)
	const storied = fold(dupStory, footprint())
	assert.deepEqual(storied.results.map((r) => r.outcome), ['ambiguous'])
	assert.match(storied.results[0].detail, /story "enter-by-qr" matches 2 stories/)
	const dir = mkdtempSync(join(tmpdir(), 'fold-'))
	t.after(() => rmSync(dir, { recursive: true, force: true }))
	const map = join(dir, 'journey.yaml'), fps = join(dir, 'footprints.jsonl'), out = join(dir, 'draft.yaml')
	writeFileSync(map, dupQuestion)
	writeFileSync(fps, `${JSON.stringify(footprint())}\n`)
	const done = spawnSync('node', [new URL('./journey-fold.mjs', import.meta.url).pathname, map, '--footprints', fps, '--out', out], { encoding: 'utf8' })
	assert.equal(done.status, 1)
	assert.match(done.stderr, /no draft written: fp:t:1 question "q1" in story "enter-by-qr"/)
	assert.throws(() => readFileSync(out), /ENOENT/)
})

test('a deferred question keeps its because and becomes answered', () => {
	const { draft } = fold(FLOW, footprint({ question: 'q3' }))
	const q = parse(draft).steps[0].stories[0].questions[2]
	assert.equal(q.because, 'Wait for payments')
	assert.equal(q.status, 'answered')
	const block = fold(BLOCK, footprint({ journey: 'review', story: 'front-door', question: 'audience' })).draft
	assert.equal(parse(block).steps[0].stories[0].questions[2].because, 'Not before the first outside agent.')
})

test('a missing story, question or journey is listed and the draft is unchanged', () => {
	const { draft, results } = fold(FLOW, footprint({ story: 'nope' }), footprint({ id: 'fp:t:2', question: 'nope' }), footprint({ id: 'fp:t:3', journey: 'other' }))
	assert.deepEqual(results.map((r) => r.outcome), ['no-story', 'no-question', 'wrong-journey'])
	assert.equal(draft, FLOW)
})

test('footprint files: another major is refused naming it, growth is accepted, an unknown kind is skipped', (t) => {
	const dir = mkdtempSync(join(tmpdir(), 'fold-'))
	t.after(() => rmSync(dir, { recursive: true, force: true }))
	const path = join(dir, 'footprints.jsonl')
	writeFileSync(path, `${JSON.stringify(footprint({ future: 'field' }))}\n${JSON.stringify(footprint({ id: 'fp:t:2', kind: 'evidence' }))}\n`)
	const { lines: ok, skipped } = readFootprints(path)
	assert.deepEqual([ok.length, skipped.length], [1, 1])
	writeFileSync(path, `${JSON.stringify(footprint({ schema: 'journey-footprint/v2' }))}\n`)
	assert.throws(() => readFootprints(path), /"journey-footprint\/v2" is not journey-footprint\/v1/)
})

test('the command writes only the draft, refuses an existing draft, and exits 1 on a conflict', (t) => {
	const dir = mkdtempSync(join(tmpdir(), 'fold-'))
	t.after(() => rmSync(dir, { recursive: true, force: true }))
	const map = join(dir, 'journey.yaml'), fps = join(dir, 'footprints.jsonl'), out = join(dir, 'draft.yaml')
	writeFileSync(map, FLOW)
	writeFileSync(fps, `${JSON.stringify(footprint())}\n`)
	const sum = () => createHash('sha256').update(readFileSync(map)).digest('hex')
	const before = sum()
	const run = (...args) => spawnSync('node', [new URL('./journey-fold.mjs', import.meta.url).pathname, map, '--footprints', fps, '--out', ...args], { encoding: 'utf8' })
	const first = run(out)
	assert.equal(first.status, 0, first.stderr)
	assert.equal(sum(), before, 'the source file is not written')
	assert.equal(readFileSync(out, 'utf8'), fold(FLOW, footprint()).draft)
	const again = run(out)
	assert.equal(again.status, 1)
	assert.match(again.stderr, /EEXIST/)
	writeFileSync(fps, `${JSON.stringify(footprint({ question: 'q2' }))}\n`)
	const conflict = run(join(dir, 'draft2.yaml'))
	assert.equal(conflict.status, 1)
	assert.match(conflict.stdout, /^conflict fp:t:1/m)
})

test('the model reads a folded question\'s source back', () => {
	const { draft } = fold(FLOW, footprint())
	const question = iterStories(parse(draft)).find((s) => s.id === 'enter-by-qr').questions[0]
	assert.equal(question.source.ref, 't/gate-attempt:t-1')
	assert.equal(question.source.words, '好，由平台發')
})
