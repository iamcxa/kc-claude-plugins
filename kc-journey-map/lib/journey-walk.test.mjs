import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { parse, stringify } from 'yaml'
import { buildReleaseContract } from './release-contract.mjs'

const walk = fileURLToPath(new URL('./journey-walk.mjs', import.meta.url))
const EXAMPLE = fileURLToPath(new URL('../skills/kc-journey-map/references/journey.example.yaml', import.meta.url))
const DOC = fileURLToPath(new URL('../skills/kc-journey-map/references/accept-release.md', import.meta.url))
const node = (...args) => spawnSync(process.execPath, args, { encoding: 'utf8' })
const scratch = (t) => {
	const dir = mkdtempSync(join(tmpdir(), 'journey-walk-'))
	t.after(() => rmSync(dir, { recursive: true, force: true }))
	return dir
}
const ids = (result) => JSON.parse(result.stdout).stories.map((s) => s.id)

test('r1 of the book-pickup example lists only its stories in step order, with the release goal as the proof line', () => {
	const first = node(walk, EXAMPLE, 'r1')
	assert.equal(first.status, 0, first.stderr)
	const doc = JSON.parse(first.stdout)
	assert.equal(doc.schema, 'release-walk/v1')
	assert.deepEqual(doc.stories.map((s) => [s.order, s.id]), [[1, 'reserve-copy'], [2, 'check-ready'], [3, 'collect-book']])
	const model = parse(readFileSync(EXAMPLE, 'utf8'))
	assert.equal(doc.proof_line, model.releases[0].goal)
	assert.ok(buildReleaseContract(model, 'r1').includes(doc.proof_line), 'the release contract prints the same goal text')
	assert.equal(node(walk, EXAMPLE, 'r1').stdout, first.stdout, 'a second run prints the same bytes')
	assert.deepEqual(ids(node(walk, EXAMPLE, 'r2')), ['choose-pickup-day', 'receive-reminder'])
})

test('swapping two steps in a copy of the map swaps the walk order', (t) => {
	const model = parse(readFileSync(EXAMPLE, 'utf8'))
	const [reserve, ready, collect] = model.steps
	model.steps = [reserve, collect, ready]
	const path = join(scratch(t), 'swapped.yaml')
	writeFileSync(path, stringify(model))
	assert.deepEqual(ids(node(walk, path, 'r1')), ['reserve-copy', 'collect-book', 'check-ready'])
})

test('story order inside one step follows the map, and a rule the map lacks reads as its id', (t) => {
	const path = join(scratch(t), 'map.yaml')
	writeFileSync(path, stringify({
		journey: 'demo', releases: [{ id: 'r1', name: 'One', goal: 'Do both.' }],
		steps: [{ id: 'a', card: 'A', activity: 'Act', rules: ['no-such-rule'], stories: [{ id: 'second', card: 'Two', release: 'r1' }, { id: 'first', card: 'One', release: 'r1' }] }],
	}))
	const doc = JSON.parse(node(walk, path, 'r1').stdout)
	assert.deepEqual(doc.stories.map((s) => s.id), ['second', 'first'])
	assert.deepEqual(doc.stories[0].rules, [{ id: 'no-such-rule', text: 'no-such-rule' }])
	assert.deepEqual([doc.persona, doc.one_journey, doc.source.commit], [null, null, null])
})

test('an unknown release, a release with no goal and a release with no stories are refused with exit 1; no arguments exit 2', (t) => {
	const path = join(scratch(t), 'map.yaml')
	writeFileSync(path, stringify({
		journey: 'demo',
		releases: [{ id: 'goalless', name: 'No goal' }, { id: 'empty', name: 'Empty', goal: 'Nothing is built.' }],
		steps: [{ id: 'a', card: 'A', stories: [{ id: 'one', card: 'One', release: 'goalless' }] }],
	}))
	for (const [release, message] of [['nope', /no release "nope"/], ['goalless', /no goal, so the walk has no proof line/], ['empty', /holds no stories/]]) {
		const refused = node(walk, path, release)
		assert.equal(refused.status, 1, release)
		assert.equal(refused.stdout, '')
		assert.match(refused.stderr, message)
	}
	assert.equal(node(walk, path).status, 2)
})

test('source.commit is the last commit touching the file, and null once the file has uncommitted edits', (t) => {
	const dir = scratch(t)
	const git = (...args) => spawnSync('git', ['-C', dir, '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', ...args], { encoding: 'utf8' })
	git('init', '-q', '-b', 'main')
	const path = join(dir, 'journey.yaml')
	writeFileSync(path, readFileSync(EXAMPLE, 'utf8'))
	git('add', 'journey.yaml'); git('commit', '-q', '-m', 'map')
	const head = git('rev-parse', 'HEAD').stdout.trim()
	writeFileSync(join(dir, 'other.txt'), 'x'); git('add', 'other.txt'); git('commit', '-q', '-m', 'unrelated')
	assert.deepEqual(JSON.parse(node(walk, path, 'r1').stdout).source, { file: 'journey.yaml', commit: head })
	writeFileSync(path, `${readFileSync(path, 'utf8')}\n# edited\n`)
	assert.equal(JSON.parse(node(walk, path, 'r1').stdout).source.commit, null)
})

test('the example printed in accept-release.md is what the walk prints for r1', () => {
	const printed = /```json\n(\{\n  "schema": "release-walk\/v1"[\s\S]*?\n\})\n```/.exec(readFileSync(DOC, 'utf8'))
	assert.ok(printed, 'accept-release.md prints a release-walk/v1 example')
	const documented = JSON.parse(printed[1])
	const actual = JSON.parse(node(walk, EXAMPLE, 'r1').stdout)
	assert.deepEqual(Object.keys(documented.source), Object.keys(actual.source))
	assert.deepEqual({ ...documented, source: null }, { ...actual, source: null })
})
