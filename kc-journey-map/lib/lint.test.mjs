
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { execFileSync, spawnSync } from 'node:child_process'
import { mkdirSync, mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { stringify } from 'yaml'
import { lintEvidenceNotFound, lintExistsWithOpenQuestion, lintExistsWithoutEvidence, lintJourney, lintNoStatus, lintQuestionStatus, oversizedSlices } from './lint.mjs'

const model = (steps) => ({ steps })

test('lintNoStatus fires on a story with no status field, not on one with an explicit gap', () => {
	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x' }, { id: 's-1', card: 'y', status: 'gap' }] }])
	const v = lintNoStatus(m)
	assert.deepEqual(v.map((x) => x.story), ['s-0'])
	assert.equal(v[0].lint, 'no-status')
})

test('a bare-string story cannot carry a status, so it fires the same lint', () => {
	const m = model([{ id: 's', stories: ['just a string'] }])
	assert.deepEqual(lintNoStatus(m).map((x) => x.story), ['s-0'])
})

test('lintExistsWithoutEvidence fires only on exists with no evidence', () => {
	const m = model([
		{
			id: 's',
			stories: [
				{ id: 's-0', card: 'x', status: 'exists' },
				{ id: 's-1', card: 'y', status: 'exists', evidence: 'Thing' },
				{ id: 's-2', card: 'z', status: 'gap' },
			],
		},
	])
	const v = lintExistsWithoutEvidence(m)
	assert.deepEqual(v.map((x) => x.story), ['s-0'])
})

function tempRepo() {
	const dir = mkdtempSync(join(tmpdir(), 'journey-lint-'))
	execFileSync('git', ['init', '-q'], { cwd: dir })
	execFileSync('git', ['config', 'user.email', 'a@b.c'], { cwd: dir })
	execFileSync('git', ['config', 'user.name', 'test'], { cwd: dir })
	writeFileSync(join(dir, 'code.mjs'), 'export function RealSymbol() {}\n')
	execFileSync('git', ['add', '-A'], { cwd: dir })
	execFileSync('git', ['commit', '-q', '-m', 'init'], { cwd: dir })
	return dir
}

test('lintEvidenceNotFound fires when the cited symbol no longer greps, and passes when it does', () => {
	const repoRoot = tempRepo()
	const m = model([
		{
			id: 's',
			stories: [
				{ id: 's-0', card: 'x', status: 'exists', evidence: 'RealSymbol' },
				{ id: 's-1', card: 'y', status: 'exists', evidence: 'RenamedAway' },
			],
		},
	])
	const v = lintEvidenceNotFound(m, { repoRoot })
	assert.deepEqual(v.map((x) => x.story), ['s-1'])
	assert.match(v[0].detail, /RenamedAway/, 'the violation must name the missing symbol, not just report a count')
})

test('a symbol that greps only inside the journey file itself is still reported missing', () => {
	const repoRoot = tempRepo()
	const journeyPath = join(repoRoot, 'journey.yaml')
	writeFileSync(journeyPath, 'evidence: OnlyInTheJourneyFile\n')
	execFileSync('git', ['add', '-A'], { cwd: repoRoot })
	execFileSync('git', ['commit', '-q', '-m', 'journey'], { cwd: repoRoot })

	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x', status: 'exists', evidence: 'OnlyInTheJourneyFile' }] }])
	const v = lintEvidenceNotFound(m, { repoRoot, journeyPath })
	assert.equal(v.length, 1, 'a symbol cited only by the journey file passed as if real code proved it')
})

test('evidence that greps only in prose is reported missing, even though the string exists', () => {
	const repoRoot = tempRepo()
	writeFileSync(join(repoRoot, 'docs.md'), 'See ProseOnlySymbol in the reference.\n')
	execFileSync('git', ['add', '-A'], { cwd: repoRoot })
	execFileSync('git', ['commit', '-q', '-m', 'docs'], { cwd: repoRoot })

	const m = model([
		{
			id: 's',
			stories: [
				{ id: 's-0', card: 'x', status: 'exists', evidence: 'RealSymbol' },
				{ id: 's-1', card: 'y', status: 'exists', evidence: 'ProseOnlySymbol' },
			],
		},
	])
	const v = lintEvidenceNotFound(m, { repoRoot })
	assert.deepEqual(v.map((x) => x.story), ['s-1'], 's-1 must fail because the only match is a doc, not because the string is missing')
})

test('evidence found only in a shell script or a CI workflow still counts, since both are executable', () => {
	const repoRoot = tempRepo()
	writeFileSync(join(repoRoot, 'deploy.sh'), '# ScriptSymbol runs the release\n')
	mkdirSync(join(repoRoot, '.github', 'workflows'), { recursive: true })
	writeFileSync(join(repoRoot, '.github', 'workflows', 'ci.yml'), 'name: CI\n# WorkflowSymbol\n')
	execFileSync('git', ['add', '-A'], { cwd: repoRoot })
	execFileSync('git', ['commit', '-q', '-m', 'scripts'], { cwd: repoRoot })

	const m = model([
		{
			id: 's',
			stories: [
				{ id: 's-0', card: 'x', status: 'exists', evidence: 'ScriptSymbol' },
				{ id: 's-1', card: 'y', status: 'exists', evidence: 'WorkflowSymbol' },
			],
		},
	])
	assert.deepEqual(lintEvidenceNotFound(m, { repoRoot }), [], 'a shell script and a CI workflow both run; over-restricting to a narrower extension list would wrongly turn these into gaps')
})

test('lintJourney combines all three and reports nothing against a clean model', () => {
	const repoRoot = tempRepo()
	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x', status: 'exists', evidence: 'RealSymbol' }] }])
	assert.deepEqual(lintJourney(m, { repoRoot }), [])
})

test('lint rejects unsupported status and accepts gap, unverified and exists', () => {
	const m = model([{ id: 's', stories: ['gap', 'unverified', 'exists', 'made-up'].map((status) => ({ id: status, card: status, status, ...(status === 'exists' ? { evidence: 'RealSymbol' } : {}) })) }])
	const dir = tempRepo()
	const violations = lintJourney(m, { repoRoot: dir })
	assert.deepEqual(violations.map((v) => [v.lint, v.story]), [['invalid-status', 'made-up']])
})

test('lintExistsWithOpenQuestion fires on exists with an unanswered question, not on an answered one', () => {
	const m = model([{ id: 's', stories: [
		{ id: 's-0', card: 'x', status: 'exists', evidence: 'X', questions: [{ id: 'q1', ask: 'Who?' }] },
		{ id: 's-1', card: 'y', status: 'exists', evidence: 'Y', questions: [{ id: 'q2', ask: 'Who?', answer: 'The owner does.' }] },
		{ id: 's-2', card: 'z', status: 'gap', questions: [{ id: 'q3', ask: 'Who?' }] },
	] }])
	const v = lintExistsWithOpenQuestion(m)
	assert.deepEqual(v.map((x) => x.story), ['s-0'])
	assert.match(v[0].detail, /q1/)
})

test('the singular question field is sugar, so it reaches the same gate', () => {
	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x', status: 'exists', evidence: 'X', question: 'Who owns this?' }] }])
	assert.deepEqual(lintExistsWithOpenQuestion(m).map((x) => x.story), ['s-0'])
})

test('a question answered only by a doc link does not hold a story back', () => {
	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x', status: 'exists', evidence: 'X',
		questions: [{ id: 'q', ask: 'Who?', doc: 'https://example.com/adr#q1' }] }] }])
	assert.deepEqual(lintExistsWithOpenQuestion(m), [])
})

test('a deferred question with a because does not hold a story back — the reason becomes its answer', () => {
	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x', status: 'exists', evidence: 'X',
		questions: [{ id: 'q', ask: 'Later?', status: 'deferred', because: 'belongs to the reminder release' }] }] }])
	assert.deepEqual(lintExistsWithOpenQuestion(m), [])
})

test('a legacy "answered" status with no answer text or doc still holds a story back', () => {
	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x', status: 'exists', evidence: 'X',
		questions: [{ id: 'q', ask: 'Who?', status: 'answered' }] }] }])
	assert.deepEqual(lintExistsWithOpenQuestion(m).map((x) => x.story), ['s-0'])
})

test('a mistyped question status is caught, not silently read as settled', () => {
	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x', status: 'gap',
		questions: [{ id: 'q', ask: 'Who?', status: 'opne' }] }] }])
	const v = lintQuestionStatus(m)
	assert.deepEqual(v.map((x) => x.story), ['s-0'])
	assert.match(v[0].detail, /unsupported status "opne"/)
})

test('a deferred question without a because is caught', () => {
	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x', status: 'gap',
		questions: [{ id: 'q', ask: 'Who?', status: 'deferred' }] }] }])
	const v = lintQuestionStatus(m)
	assert.deepEqual(v.map((x) => x.story), ['s-0'])
	assert.match(v[0].detail, /deferred without a "because"/)
})

test('open, answered, and a reasoned deferral all pass lintQuestionStatus', () => {
	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x', status: 'gap', questions: [
		{ id: 'q1', ask: 'A?', status: 'open' },
		{ id: 'q2', ask: 'B?', status: 'answered' },
		{ id: 'q3', ask: 'C?', status: 'deferred', because: 'later release' },
	] }] }])
	assert.deepEqual(lintQuestionStatus(m), [])
})

test('a card past the text limit is reported as advisory, and a short one is not', async () => {
	const { longCards, CARD_TEXT_LIMIT } = await import('./lint.mjs')
	const model = { steps: [{ id: 's', stories: [
		{ id: 'short', card: '看這家店的服務', questions: [{ id: 'q1', ask: '短問題', answer: '短答案' }] },
		{ id: 'long', card: '字'.repeat(CARD_TEXT_LIMIT), questions: [{ id: 'q1', ask: 'ok', answer: '答'.repeat(CARD_TEXT_LIMIT) }] },
	] }] }
	const notes = longCards(model)
	assert.ok(notes.some((n) => n.startsWith('story long')), 'a long story card was not reported')
	assert.ok(notes.some((n) => n.startsWith('answer long/q1')), 'a long answer was not reported')
	assert.ok(!notes.some((n) => n.includes('short')), 'a short card was reported')
})

test('a long flow line, step note, rule or status field is reported as advisory', async () => {
	const { longCards, CARD_TEXT_LIMIT } = await import('./lint.mjs')
	const long = 'x'.repeat(CARD_TEXT_LIMIT + 1)
	const model = {
		steps: [{ id: 's', system: ['short', long], note: long, stories: [] }],
		rules: [{ id: 'short-rule', text: 'short' }, { id: 'long-rule', text: long }],
		status: { as_of: '2026-09-23', unproven: long },
	}
	assert.deepEqual(longCards(model).map((n) => n.split(' is ')[0]), ['flow s line 2', 'note s', 'rule long-rule', 'status unproven'])
})

function otherRepo() {
	const dir = mkdtempSync(join(tmpdir(), 'journey-lint-other-'))
	execFileSync('git', ['init', '-q', '-b', 'main'], { cwd: dir })
	execFileSync('git', ['config', 'user.email', 'a@b.c'], { cwd: dir })
	execFileSync('git', ['config', 'user.name', 'test'], { cwd: dir })
	writeFileSync(join(dir, 'tui.go'), 'package main\n\nfunc GoSymbol() {}\n')
	execFileSync('git', ['add', '-A'], { cwd: dir })
	execFileSync('git', ['commit', '-q', '-m', 'init'], { cwd: dir })
	return dir
}

test('evidence qualified with another repository greps that repository, Go included', () => {
	const repoRoot = tempRepo()
	const other = otherRepo()
	const m = model([{ id: 's', stories: [
		{ id: 's-0', card: 'x', status: 'exists', evidence: 'other:GoSymbol' },
		{ id: 's-1', card: 'y', status: 'exists', evidence: 'other:RealSymbol' },
	] }])
	const v = lintEvidenceNotFound(m, { repoRoot, repos: { other: { root: other } } })
	assert.deepEqual(v.map((x) => [x.lint, x.story]), [['evidence-not-found', 's-1']], 'RealSymbol lives in the primary repo only, so qualifying it with the other repo must fail')
})

test('evidence naming a repository that was not passed is refused, not grepped in the primary repo', () => {
	const repoRoot = tempRepo()
	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x', status: 'exists', evidence: 'other:RealSymbol' }] }])
	const v = lintEvidenceNotFound(m, { repoRoot })
	assert.deepEqual(v.map((x) => [x.lint, x.story]), [['evidence-repo-unknown', 's-0']])
})

test('a repository passed with a ref greps that ref, not the working tree', () => {
	const repoRoot = tempRepo()
	const other = otherRepo()
	execFileSync('git', ['checkout', '-q', '-b', 'feature'], { cwd: other })
	writeFileSync(join(other, 'branch.go'), 'package main\n\nfunc BranchOnly() {}\n')
	execFileSync('git', ['add', '-A'], { cwd: other })
	execFileSync('git', ['commit', '-q', '-m', 'branch'], { cwd: other })
	const m = model([{ id: 's', stories: [
		{ id: 's-0', card: 'x', status: 'exists', evidence: 'other:BranchOnly' },
		{ id: 's-1', card: 'y', status: 'exists', evidence: 'other:GoSymbol' },
	] }])
	const v = lintEvidenceNotFound(m, { repoRoot, repos: { other: { root: other, ref: 'main' } } })
	assert.deepEqual(v.map((x) => x.story), ['s-0'], 'BranchOnly is in the checked-out working tree but not on main')
})

const sliced = (open, { exists = 0, ...extra } = {}) => ({
	releases: [{ id: 'r1', goal: 'g' }],
	steps: [{ id: 's', stories: [
		...Array.from({ length: open }, (_, i) => ({ id: `o${i}`, card: 'x', release: 'r1', status: i % 2 ? 'unverified' : 'gap' })),
		...Array.from({ length: exists }, (_, i) => ({ id: `e${i}`, card: 'x', release: 'r1', status: 'exists', evidence: 'Sym' })),
	] }],
	...extra,
})

test('a release with more than five stories that do not exist yet is reported, five is not', () => {
	assert.deepEqual(oversizedSlices(sliced(6)), [{ kind: 'advisory',
		text: 'release r1 holds 6 stories that do not exist yet (limit 5); split into sub-slices or record slice_because' }])
	assert.deepEqual(oversizedSlices(sliced(5)), [])
})

test('stories that already exist are not counted', () => {
	assert.deepEqual(oversizedSlices(sliced(5, { exists: 1 })), [])
	assert.equal(oversizedSlices(sliced(6, { exists: 3 }))[0].text.includes('holds 6 stories'), true)
})

test('a story with no status counts as not existing, and a story with no release counts for no release', () => {
	const m = sliced(5)
	m.steps[0].stories.push({ id: 'bare', card: 'x', release: 'r1' }, { id: 'free', card: 'x' }, 'plain string')
	assert.match(oversizedSlices(m)[0].text, /holds 6 stories/)
})

test('slice_limit replaces the default and anything but a positive integer is a violation', () => {
	assert.deepEqual(oversizedSlices(sliced(6, { slice_limit: 6 })), [])
	assert.equal(oversizedSlices(sliced(6, { slice_limit: 3 }))[0].text.includes('(limit 3)'), true)
	for (const bad of [0, '5', 2.5, -1, null, true]) {
		const violations = lintJourney(sliced(6, { slice_limit: bad }), { repoRoot: tmpdir() }).filter((v) => v.lint === 'invalid-slice-limit')
		assert.equal(violations.length, 1, `slice_limit ${JSON.stringify(bad)} was not refused`)
		assert.match(oversizedSlices(sliced(6, { slice_limit: bad }))[0].text, /\(limit 5\)/)
	}
	assert.deepEqual(lintJourney(sliced(6, { slice_limit: 6 }), { repoRoot: tmpdir() }).filter((v) => v.lint === 'invalid-slice-limit'), [])
})

test('slice_because turns the advisory into an accepted line, an empty one does not', () => {
	const m = sliced(6)
	m.releases[0].slice_because = 'one demo, the reader sees it whole'
	assert.deepEqual(oversizedSlices(m), [{ kind: 'accepted', text: 'release r1 holds 6 stories that do not exist yet (limit 5) because one demo, the reader sees it whole' }])
	for (const empty of ['', '   ', null]) {
		m.releases[0].slice_because = empty
		assert.equal(oversizedSlices(m)[0].kind, 'advisory')
	}
})

test('journey-lint prints the slice-size line and its exit code is unchanged by it', () => {
	const dir = mkdtempSync(join(tmpdir(), 'journey-lint-slice-'))
	const cli = fileURLToPath(new URL('./journey-lint.mjs', import.meta.url))
	const run = (model) => {
		const path = join(dir, 'j.yaml')
		writeFileSync(path, stringify(model))
		return spawnSync(process.execPath, [cli, path, dir], { encoding: 'utf8' })
	}
	const over = run(sliced(6))
	assert.equal(over.status, 0, over.stdout)
	assert.match(over.stdout, /^slice-size \(advisory\): release r1 holds 6 stories that do not exist yet \(limit 5\); split into sub-slices or record slice_because$/m)
	assert.match(over.stdout, /all lints pass/)
	assert.doesNotMatch(run(sliced(5)).stdout, /slice-size/)
	const bad = run(sliced(6, { slice_limit: 0 }))
	assert.equal(bad.status, 1)
	assert.match(bad.stdout, /^invalid-slice-limit: /m)
})

const boarded = (board) => ({ ...sliced(1), releases: [{ id: 'r1', name: 'R1', ...(board === undefined ? {} : { board }) }] })

test('a board value that is present and not a boolean is a violation naming the release', () => {
	for (const bad of ['false', 0, null]) {
		const violations = lintJourney(boarded(bad), { repoRoot: tmpdir() }).filter((v) => v.lint === 'invalid-board')
		assert.equal(violations.length, 1, `board ${JSON.stringify(bad)} was not refused`)
		assert.equal(violations[0].release, 'r1')
		assert.match(violations[0].detail, /release r1 has board/)
	}
	for (const ok of [true, false, undefined]) {
		assert.deepEqual(lintJourney(boarded(ok), { repoRoot: tmpdir() }).filter((v) => v.lint === 'invalid-board'), [])
	}
})

test('journey-lint exits 1 on a non-boolean board and names the release', () => {
	const dir = mkdtempSync(join(tmpdir(), 'journey-lint-board-'))
	const cli = fileURLToPath(new URL('./journey-lint.mjs', import.meta.url))
	const path = join(dir, 'j.yaml')
	writeFileSync(path, stringify(boarded('false')))
	const bad = spawnSync(process.execPath, [cli, path, dir], { encoding: 'utf8' })
	assert.equal(bad.status, 1)
	assert.match(bad.stdout, /^invalid-board: release r1 has board "false"; use true or false$/m)
})
