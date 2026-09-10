// node --test lib/*.test.mjs
//
// Each lint is exercised against a real defect first, so a lint nobody can make fail is
// caught here rather than shipped as decoration.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { execFileSync } from 'node:child_process'
import { mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { lintEvidenceNotFound, lintExistsWithoutEvidence, lintJourney, lintNoStatus } from './lint.mjs'

const model = (steps) => ({ steps })

test('lintNoStatus fires on a story with no status field, not on one with an explicit gap', () => {
	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x' }, { id: 's-1', card: 'y', status: 'gap' }] }])
	const v = lintNoStatus(m)
	assert.deepEqual(v.map((x) => x.story), ['s-0'])
	assert.equal(v[0].lint, 'no-status')
	// Mutation this catches: a lint that defaults a missing status to 'gap' before
	// checking would never fire here, though nothing that fires makes it pass either.
})

test('a bare-string story cannot carry a status, so it fires the same lint', () => {
	// Absorbed constraint: a bare string structurally cannot carry status/evidence/question.
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
	// Mutation this catches: a lint that checks only `status === 'exists'` (dropping the
	// `!evidence` half) would also fire on s-1, which carries real evidence.
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
	// Mutation this catches: a lint that only checks `evidence` is truthy (never greps)
	// would report neither s-0 nor s-1 — this fixture is built so that check alone passes.
})

test('a symbol that greps only inside the journey file itself is still reported missing', () => {
	// This is the check a table could never do: the file citing its own claim is not
	// evidence that the claim is still true of the code.
	const repoRoot = tempRepo()
	const journeyPath = join(repoRoot, 'journey.yaml')
	writeFileSync(journeyPath, 'evidence: OnlyInTheJourneyFile\n')
	execFileSync('git', ['add', '-A'], { cwd: repoRoot })
	execFileSync('git', ['commit', '-q', '-m', 'journey'], { cwd: repoRoot })

	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x', status: 'exists', evidence: 'OnlyInTheJourneyFile' }] }])
	const v = lintEvidenceNotFound(m, { repoRoot, journeyPath })
	assert.equal(v.length, 1, 'a symbol cited only by the journey file passed as if real code proved it')
})

test('lintJourney combines all three and reports nothing against a clean model', () => {
	const repoRoot = tempRepo()
	const m = model([{ id: 's', stories: [{ id: 's-0', card: 'x', status: 'exists', evidence: 'RealSymbol' }] }])
	assert.deepEqual(lintJourney(m, { repoRoot }), [])
})
