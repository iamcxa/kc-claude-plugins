import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { parse, stringify } from 'yaml'

const review = fileURLToPath(new URL('./journey-review.mjs', import.meta.url))
const handoff = fileURLToPath(new URL('./journey-handoff.mjs', import.meta.url))
const EXAMPLE = fileURLToPath(new URL('../skills/kc-journey-map/references/journey.example.yaml', import.meta.url))
const hash = (value) => createHash('sha256').update(value).digest('hex')
const node = (...args) => spawnSync(process.execPath, args, { encoding: 'utf8' })

const RULING = (words) => ({ kind: 'release', ref: 'book-pickup/r1', words, date: '2026-10-22' })
const answer = (q, over = {}) => ({ ...q, status: 'answered', answer: `${q.id} settled.`, source: RULING(`I settle ${q.id}.`), ...over })

// The book-pickup example with two questions on r1 stories, open or answered.
function journey(answered) {
	const map = parse(readFileSync(EXAMPLE, 'utf8'))
	const story = (id) => map.steps.flatMap((s) => s.stories).find((s) => s.id === id)
	const hold = { id: 'hold-rule', ask: 'May a reader hold two copies of one book?' }
	const ready = { id: 'ready-where', ask: 'Where is the pickup desk shown?' }
	story('reserve-copy').questions = [answered ? answer(hold) : hold]
	story('check-ready').questions = [answered ? answer(ready) : ready]
	return map
}

const RECORD = `# Release review: book-pickup/r1
Reviewed: 2026-10-22; map at abc1234; code at example@abc1234
Interrogation: 2026-10-22; questions 12; dropped 3; decision rows 2; asked 2; open after 0; codex gpt-6.1-sol high lens
## Map edit
Answers applied to two questions.
## Walk
| Step | Actor |
|---|---|
## Holes
none
## Slice
3 of 4 limit
## Tasks
| Task | journey-story | Required tasks | Carries |
|---|---|---|---|
| Reserve a copy | reserve-copy | reserve-copy | ADR owed: hold-rule |
| Show readiness | check-ready | check-ready | - |
| Collect at the desk | collect-book | collect-book | - |
`

function workdir(t, name = 'docs/journey') {
	const dir = mkdtempSync(join(tmpdir(), 'journey-review-'))
	t.after(() => rmSync(dir, { recursive: true, force: true }))
	mkdirSync(join(dir, name), { recursive: true })
	return join(dir, name)
}

function fixture(t, { map = journey(true), record = RECORD } = {}) {
	const dir = workdir(t)
	const yaml = join(dir, 'book-pickup.yaml')
	const md = join(dir, 'record.md')
	writeFileSync(yaml, stringify(map))
	writeFileSync(md, record)
	return { dir, yaml, md, check: () => node(review, 'check', md, yaml) }
}

test('the record path sits beside the journey file and names the journey, so two journeys in one directory get two paths', (t) => {
	const dir = workdir(t)
	const first = join(dir, 'book-pickup.yaml')
	const second = join(dir, 'other.yaml')
	writeFileSync(first, stringify(journey(false)))
	writeFileSync(second, stringify({ ...journey(false), journey: 'other' }))
	const a = node(review, 'path', first, 'r1')
	const b = node(review, 'path', second, 'r1')
	assert.equal(a.status, 0, a.stderr)
	assert.equal(a.stdout.trim(), join(dir, 'reviews', 'book-pickup', 'r1.md'))
	assert.equal(b.stdout.trim(), join(dir, 'reviews', 'other', 'r1.md'))
	assert.notEqual(a.stdout, b.stdout)
	const unsafe = node(review, 'path', first, '../r1')
	assert.equal(unsafe.status, 1)
	assert.match(unsafe.stderr, /cannot build a record path/)
})

test('a complete record on a fully answered map passes', (t) => {
	const r = fixture(t).check()
	assert.equal(r.status, 0, r.stderr)
})

for (const [name, mutate, message] of [
	['a heading naming another journey', (f) => ({ record: RECORD.replace('book-pickup/r1', 'other/r1') }), /heading names journey other/],
	['a heading naming a release the map lacks', () => ({ record: RECORD.replace('book-pickup/r1', 'book-pickup/r9') }), /release r9, which the map lacks/],
	['a missing Interrogation line', () => ({ record: RECORD.replace(/Interrogation:.*\n/, '') }), /Interrogation: line is missing/],
	['an Interrogation line lacking a count', () => ({ record: RECORD.replace('dropped 3; ', '') }), /lacks the count "dropped <n>"/],
	['an Interrogation line naming no codex arm', () => ({ record: RECORD.replace('codex gpt-6.1-sol high lens', 'claude sonnet') }), /names no codex arm/],
	['a plain arm without its reason', () => ({ record: RECORD.replace('lens', 'lens; codex gpt-6.1-sol high plain') }), /plain arm must say why/],
	['an interrogation that did not run', () => ({ record: RECORD.replace(/Interrogation:.*\n/, 'Interrogation: interrogation not run: codex missing\n') }), /interrogation did not run: interrogation not run: codex missing/],
	['an open question on a release story', () => { const map = journey(true); map.steps[1].stories[0].questions[0] = { id: 'ready-where', ask: 'Where?' }; return { map } }, /open questions on check-ready: ready-where/],
	['a release answer sourced to another release', () => { const map = journey(true); map.steps[0].stories[0].questions[0].source.ref = 'book-pickup/r2'; return { map } }, /hold-rule: source\.ref is "book-pickup\/r2"/],
	['a release answer with empty words', () => { const map = journey(true); map.steps[0].stories[0].questions[0].source.words = ''; return { map } }, /hold-rule: source\.words is empty/],
	['a release answer with no date', () => { const map = journey(true); delete map.steps[0].stories[0].questions[0].source.date; return { map } }, /hold-rule: source\.date is empty/],
	['a question holding both answer and doc', () => { const map = journey(true); map.steps[0].stories[0].questions[0].doc = 'https://example.test/adr'; return { map } }, /hold-rule: holds both answer and doc/],
	['a task naming a story not on the release', () => ({ record: RECORD.replace('| collect-book |', '| elsewhere |') }), /journey-story elsewhere is not a story on release r1/],
	['a Carries id that is no release question on its story', () => ({ record: RECORD.replace('ADR owed: hold-rule', 'ADR owed: ready-where') }), /ADR owed ready-where is not a kind: release question on reserve-copy/],
	['a Carries entry that is not an ADR owed line', () => ({ record: RECORD.replace('ADR owed: hold-rule', 'a decision') }), /is not "ADR owed: <question id>"/],
]) test(`check refuses ${name}`, (t) => {
	const f = fixture(t, mutate())
	const r = f.check()
	assert.equal(r.status, 1, r.stdout)
	assert.match(r.stderr, message)
})

test('a question with neither answer nor doc is refused as the order check and as a release question', (t) => {
	const map = journey(true)
	delete map.steps[0].stories[0].questions[0].answer
	const r = fixture(t, { map }).check()
	assert.equal(r.status, 1)
	assert.match(r.stderr, /open questions on reserve-copy: hold-rule/)
	assert.match(r.stderr, /hold-rule: holds neither answer nor doc/)
})

test('the pre-task path: open questions refuse the handoff, answers and a record pass the check, and a pre-cut copy taken after the answers hands off', (t) => {
	const dir = workdir(t)
	const brief = join(dir, 'brief.md')
	writeFileSync(brief, '# Development Brief\nA reader reserves, checks and collects.\n')
	const assessmentFor = (baselinePath, sourcePath) => {
		const source = parse(readFileSync(sourcePath, 'utf8'))
		const release = source.releases.find((r) => r.id === 'r1')
		const file = join(dir, `assessment-${hash(readFileSync(baselinePath)).slice(0, 8)}.json`)
		writeFileSync(file, JSON.stringify({
			version: 1, release: 'r1', goal: release.goal,
			baseline_sha256: hash(readFileSync(baselinePath)), source_sha256: hash(readFileSync(sourcePath)), brief_sha256: hash(readFileSync(brief)),
			outcome: { start: 'A reader wants a book', finish: 'The reader holds the book', verification: 'Reserve, wait for ready, collect' , complete: true },
			constraints: ['one-active-hold', 'hold-deadline'].map((id) => ({ id, preserved: true, verification: `${id} holds in the walk` })),
			retained: ['reserve-copy', 'check-ready', 'collect-book'].map((id) => ({ id, necessary: true, breaks: 'outcome', reason: `${id} is on the path` })),
			deferred: [], dependencies: [], unresolved: [],
			budget: { appetite: 2, unit: 'days', user_basis: 'Fictional exercise', estimate: 1, estimate_basis: 'Fictional exercise' },
		}))
		return file
	}
	const digest = (baseline, source) => node(handoff, baseline, source, assessmentFor(baseline, source), brief, '--digest')
	const write = (name, map) => { const file = join(dir, name); writeFileSync(file, stringify(map)); return file }
	const unmember = (map) => { const copy = structuredClone(map); delete copy.steps[2].stories[0].release; return copy }

	const open = write('open.yaml', journey(false))
	const refused = digest(open, open)
	assert.equal(refused.status, 1)
	assert.match(refused.stderr, /open questions on reserve-copy: hold-rule/)

	const answered = journey(true)
	const source = write('answered.yaml', answered)
	const record = join(dir, 'record.md')
	writeFileSync(record, RECORD)
	const checked = node(review, 'check', record, source)
	assert.equal(checked.status, 0, checked.stderr)

	const preCut = write('pre-cut.yaml', unmember(answered))
	const ok = digest(preCut, source)
	assert.equal(ok.status, 0, ok.stderr)

	const before = write('before-answers.yaml', unmember(journey(false)))
	const stale = digest(before, source)
	assert.equal(stale.status, 1)
	assert.match(stale.stderr, /requirements changed or deleted/)

	const noWords = journey(true)
	noWords.steps[0].stories[0].questions[0].source.words = ''
	const broken = write('no-words.yaml', noWords)
	const refusedRecord = node(review, 'check', record, broken)
	assert.equal(refusedRecord.status, 1)
	assert.match(refusedRecord.stderr, /source\.words is empty/)
})
