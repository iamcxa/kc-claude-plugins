
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { execFileSync } from 'node:child_process'
import { mkdirSync, mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { lintEvidenceNotFound, lintExistsWithoutEvidence, lintJourney, lintNoStatus } from './lint.mjs'

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
