import assert from 'node:assert/strict'
import { test } from 'node:test'
import { createHash } from 'node:crypto'
import { mkdtempSync, readFileSync, writeFileSync, existsSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawnSync } from 'node:child_process'
import { parse, stringify } from 'yaml'

const cli = fileURLToPath(new URL('./journey-handoff.mjs', import.meta.url))
const hash = (value) => createHash('sha256').update(value).digest('hex')
function fixture(t) {
	const dir = mkdtempSync(join(tmpdir(), 'journey-handoff-'))
	t.after(() => rmSync(dir, { recursive: true, force: true }))
	const baseline = { journey: 'parcel', persona: 'Sender', one_journey: 'Send and track a parcel', releases: [{ id: 'r1', goal: 'Send a parcel and see arrival.' }, { id: 'later', goal: 'Schedule pickup.' }], rules: [{ id: 'private', text: 'Only the sender sees tracking.' }], steps: [
		{ id: 'send', stories: [{ id: 'send', card: 'Send a parcel', release: 'r1' }, { id: 'schedule', card: 'Schedule pickup', release: 'r1' }] },
		{ id: 'track', rules: ['private'], stories: [{ id: 'track', card: 'See arrival', release: 'r1' }] },
	] }
	const source = structuredClone(baseline)
	source.steps[0].stories[1].release = 'later'
	const paths = ['baseline.yaml', 'source.yaml', 'assessment.json', 'brief.md'].map((name) => join(dir, name))
	writeFileSync(paths[0], stringify(baseline))
	writeFileSync(paths[1], stringify(source))
	// The guard transports the host's existing brief; dev-flow owns its section schema.
	writeFileSync(paths[3], '# Existing Development Brief\nSender can send and track a parcel.\n')
	const assessment = {
		version: 1, release: 'r1', goal: source.releases[0].goal,
		baseline_sha256: hash(readFileSync(paths[0])), source_sha256: hash(readFileSync(paths[1])), brief_sha256: hash(readFileSync(paths[3])),
		outcome: { start: 'Sender has a parcel', finish: 'Sender sees arrival', verification: 'Send a parcel and observe its arrival record', complete: true },
		constraints: [{ id: 'private', preserved: true, verification: 'A second sender cannot read tracking' }],
		retained: [{ id: 'send', necessary: true, breaks: 'outcome', reason: 'No parcel enters transit without sending' }, { id: 'track', necessary: true, breaks: 'outcome', reason: 'Sender cannot observe arrival without tracking' }],
		deferred: [{ id: 'schedule', reason: 'Drop-off already lets the sender complete this journey' }],
		dependencies: [{ story: 'track', prerequisite: 'send', evidence: 'Carrier contract requires an accepted parcel ID for tracking' }],
		unresolved: [], budget: { appetite: 2, unit: 'days', user_basis: 'Fictional exercise: user chose two days', estimate: 1, estimate_basis: 'Fictional exercise: comparable send-and-track adapter took one day including validation' },
	}
	const save = () => writeFileSync(paths[2], JSON.stringify(assessment))
	const run = (...args) => { save(); return spawnSync(process.execPath, [cli, ...paths, ...args], { encoding: 'utf8' }) }
	const accept = () => {
		const digest = run('--digest')
		assert.equal(digest.status, 0, digest.stderr)
		assessment.acceptance = { decision: 'accepted', evidence: 'Fictional test answer; not live approval', digest: digest.stdout.trim() }
	}
	return { dir, paths, assessment, source, run, accept }
}

test('actual handoff emits the existing brief after recorded acceptance; map source remains unchanged', (t) => {
	const f = fixture(t); f.accept()
	const before = readFileSync(f.paths[1])
	const out = join(f.dir, 'handoff.md')
	const result = f.run('--out', out)
	assert.equal(result.status, 0, result.stderr)
	assert.deepEqual(readFileSync(out), readFileSync(f.paths[3]))
	assert.deepEqual(readFileSync(f.paths[1]), before)
	assert.equal(JSON.parse(result.stdout).source_sha256, f.assessment.source_sha256)
})

for (const [name, mutate, message] of [
	['missing appetite', (f) => delete f.assessment.budget.appetite, /appetite/],
	['oversized', (f) => { f.assessment.budget.estimate = 3 }, /oversized/],
	['unsupported estimate', (f) => delete f.assessment.budget.estimate_basis, /estimate/],
	['optional retained story', (f) => { f.assessment.retained[0].necessary = false }, /shrink-required/],
	['incomplete journey', (f) => { f.assessment.outcome.complete = false }, /incomplete/],
	['lost constraint', (f) => { f.assessment.constraints = [] }, /constraint/],
	['unavailable external dependency', (f) => { f.assessment.dependencies[0].prerequisite = 'Future carrier API' }, /dependency/],
	['unsupported dependency', (f) => { f.assessment.dependencies[0].evidence = '' }, /dependency/],
	['unresolved decision', (f) => { f.assessment.unresolved = ['Who may track?'] }, /unresolved/],
	['missing acceptance', (f) => delete f.assessment.acceptance, /acceptance/],
	['changed accepted premises', (f) => { f.assessment.budget.estimate_basis = 'A different assumption' }, /stale acceptance/],
	['changed brief', (f) => writeFileSync(f.paths[3], 'A different outcome'), /brief_sha256/],
	['changed source', (f) => writeFileSync(f.paths[1], readFileSync(f.paths[1], 'utf8') + '\n# edit\n'), /source_sha256/],
	['silent deletion', (f) => { f.source.steps[0].stories.pop(); writeFileSync(f.paths[1], stringify(f.source)); f.assessment.source_sha256 = hash(readFileSync(f.paths[1])) }, /requirements changed or deleted/],
	['missing deferral', (f) => { f.assessment.deferred = [] }, /deferral/],
]) test(`actual handoff refuses ${name} without emitting a brief`, (t) => {
	const f = fixture(t); f.accept(); mutate(f)
	const out = join(f.dir, 'refused.md')
	const result = f.run('--out', out)
	assert.notEqual(result.status, 0)
	assert.match(result.stderr, message)
	assert.equal(existsSync(out), false)
})

test('an open question on a selected story refuses handoff; an answered or deferred one does not', (t) => {
	for (const [question, refused] of [
		[{ id: 'q1', ask: 'Who may see arrival?' }, true],
		[{ id: 'q1', ask: 'Who may see arrival?', answer: 'Only the sender.' }, false],
		[{ id: 'q1', ask: 'Who may see arrival?', status: 'deferred', because: 'Decided in the next release.' }, false],
	]) {
		const f = fixture(t)
		for (const path of [f.paths[0], f.paths[1]]) {
			const model = parse(readFileSync(path, 'utf8'))
			model.steps[1].stories[0].questions = [question]
			writeFileSync(path, stringify(model))
		}
		f.assessment.baseline_sha256 = hash(readFileSync(f.paths[0]))
		f.assessment.source_sha256 = hash(readFileSync(f.paths[1]))
		const out = join(f.dir, 'handoff.md')
		if (refused) {
			const result = f.run('--digest')
			assert.notEqual(result.status, 0)
			assert.match(result.stderr, /open questions on track: q1/)
		} else {
			f.accept()
			assert.equal(f.run('--out', out).status, 0)
		}
		assert.equal(existsSync(out), !refused)
	}
})

test('an earlier output is not silently overwritten or presented as a current pass', (t) => {
	const f = fixture(t); f.accept()
	const out = join(f.dir, 'handoff.md')
	assert.equal(f.run('--out', out).status, 0)
	const original = readFileSync(out)
	f.assessment.budget.estimate = 9
	const result = f.run('--out', out)
	assert.notEqual(result.status, 0)
	assert.match(result.stderr, /output already exists/)
	assert.equal(result.stdout, '')
	assert.deepEqual(readFileSync(out), original)
})

test('a proven available external capability does not force extra stories into the slice', (t) => {
	const f = fixture(t)
	f.assessment.dependencies = [{ story: 'send', prerequisite: 'Carrier accepts parcels', available: true, evidence: 'Fictional integration exercise: published carrier endpoint accepts parcel requests' }]
	f.accept()
	const result = f.run('--out', join(f.dir, 'handoff.md'))
	assert.equal(result.status, 0, result.stderr)
})

test('the first cut may assign unplaced whole-map stories and retain deferred requirements', (t) => {
	const f = fixture(t)
	const baseline = parse(readFileSync(f.paths[0], 'utf8'))
	baseline.releases = []
	for (const step of baseline.steps) for (const story of step.stories) delete story.release
	writeFileSync(f.paths[0], stringify(baseline))
	f.assessment.baseline_sha256 = hash(readFileSync(f.paths[0]))
	f.accept()
	assert.equal(f.run('--out', join(f.dir, 'first-cut.md')).status, 0)
})
