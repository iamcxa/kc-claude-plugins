// Requires Node >=22.13, the declared canvas dependencies, and the real Spacedock CLI on PATH.
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { execFileSync, spawn } from 'node:child_process'
import { once } from 'node:events'
import { stringify } from 'yaml'
import { readProgress, taskListing } from './progress.mjs'
import { buildAllPages, loadJourney } from './render.mjs'
import { storyBorder, richText } from './records.mjs'
import { diffAgainstModel, applyDiff, readRoom } from './read.mjs'

const plugin = fileURLToPath(new URL('..', import.meta.url))
const ids = ['a', 'b', 'c', 'd', 'e'].map((n) => n + '0'.repeat(23))
const model = { journey: 'demo', releases: [{ id: 'R1', name: 'First release', goal: 'Use both stories' }],
	steps: [{ id: 'act', card: 'Plan the work', stories: [
		{ id: 'alpha', release: 'R1', card: 'Review required work', status: 'exists', evidence: 'Authored evidence' },
		{ id: 'beta', release: 'R1', card: 'Inspect completed work', status: 'gap' },
	] }] }
const cli = (...args) => execFileSync('spacedock', ['status', ...args, '--json'], { encoding: 'utf8' })
function fixture(t) {
	const root = mkdtempSync(join(tmpdir(), 'journey-progress-'))
	t.after(() => rmSync(root, { recursive: true, force: true }))
	const workflow = join(root, 'workflow'); mkdirSync(join(workflow, '_archive'), { recursive: true })
	writeFileSync(join(workflow, 'README.md'), `---
commissioned-by: spacedock@0.27.2
entity-type: task
id-style: sd-b32
stages:
  states:
    - name: implementation
      initial: true
    - name: done
      terminal: true
---
`)
	const tasks = ids.map((id, i) => ({ id, title: `Task ${i}`, status: i === 1 ? 'implementation' : 'done',
		journey: i === 3 ? 'other' : 'demo', 'journey-release': i === 4 ? 'R2' : 'R1', 'journey-story': i === 2 ? 'beta' : 'alpha',
		...(i === 0 || i === 2 ? { 'journey-required-tasks': JSON.stringify(i === 0 ? ids.slice(0, 2) : [id]), 'journey-mapping-complete': true } : {}) }))
	const paths = tasks.map((_, i) => join(workflow, i === 2 ? '_archive/c.md' : `${String.fromCharCode(97 + i)}.md`))
	const save = () => tasks.forEach((task, i) => writeFileSync(paths[i], `---\n${stringify(task)}---\n`))
	save(); const path = join(root, 'journey.yaml'); writeFileSync(path, stringify(model))
	const bytes = () => [path, ...paths].map((p) => readFileSync(p, 'utf8'))
	return { root, workflow, tasks, paths, save, path, bytes, read: (m = model) => readProgress(m, workflow) }
}
const texts = (records) => JSON.stringify(records.map((r) => r.props?.richText))

test('real archived reader distinguishes task/story ratios, full identities, and reopening', (t) => {
	const f = fixture(t), before = f.bytes(), result = f.read()
	assert.equal(result.diagnostic, null)
	assert.deepEqual(result.stories.map((s) => [s.doneTasks, s.requiredTasks, s.status]), [[1, 2, 'gap'], [1, 1, 'exists']])
	assert.deepEqual([result.releases[0].doneTasks, result.releases[0].requiredTasks, result.releases[0].doneStories, result.releases[0].totalStories], [2, 3, 1, 2])
	assert.deepEqual(result.stories.flatMap((s) => s.taskIds).sort(), ids.slice(0, 3))
	assert.deepEqual(f.bytes(), before)
	f.tasks[2].status = 'implementation'; f.save()
	assert.equal(f.read().releases[0].doneStories, 0)
	f.tasks[2].status = 'done'; f.tasks[1].status = 'done'; f.save()
	const complete = f.read()
	assert.equal(complete.releases[0].acceptance, 'pending delivery acceptance')
	const pages = buildAllPages(model, null, ['story-map', 'journey-board'], complete)
	assert.match(texts(pages), /2\/2 stories development-complete/)
	assert.match(texts(pages), /pending delivery acceptance/)
	assert.ok(pages.filter((r) => r.meta?.journey?.kind === 'story-border').every((r) => r.props.color === 'green'))
})

test('real records refuse missing, partial, conflicting, duplicate, malformed, and short-ID scope', (t) => {
	const f = fixture(t), original = structuredClone(f.tasks)
	const bad = [
		(a, b) => { delete a['journey-required-tasks']; delete a['journey-mapping-complete']; b.status = 'done' },
		(a) => { delete a['journey-mapping-complete'] },
		(a) => { a['journey-mapping-complete'] = false },
		(a) => { a['journey-required-tasks'] = '[]' },
		(a) => { a['journey-required-tasks'] = '{}' },
		(a) => { a['journey-required-tasks'] = '[' },
		(a) => { a['journey-required-tasks'] = [ids[0], ids[1]] },
		(a) => { a['journey-required-tasks'] = JSON.stringify([ids[0]]) },
		(a) => { a['journey-required-tasks'] = JSON.stringify([ids[1]]) },
		(a) => { a['journey-required-tasks'] = JSON.stringify([ids[0], ids[0]]) },
		(a) => { a['journey-required-tasks'] = JSON.stringify([ids[0], 'missing']) },
		(a) => { a['journey-required-tasks'] = JSON.stringify(['a0']) },
		(a, b) => { b['journey-required-tasks'] = a['journey-required-tasks']; b['journey-mapping-complete'] = true },
		(a, b) => { b.id = a.id },
		(a, b) => { delete b['journey-story'] },
		(a, b) => { b.journey = 'other' },
		(a, b) => { b['journey-release'] = 'R2' },
		(a, b, c, d) => { d.journey = 'demo' },
	]
	for (const mutate of bad) {
		f.tasks.splice(0, 5, ...structuredClone(original)); mutate(...f.tasks); f.save()
		assert.equal(f.read().stories[0].status, 'unverified', String(mutate))
	}
	f.tasks.splice(0, 5, ...structuredClone(original)); f.save(); rmSync(f.paths[1])
	assert.equal(f.read().stories[0].status, 'unverified', 'missing required file')
	f.save(); writeFileSync(f.paths[1], '---\nstatus: [malformed\n---\n')
	assert.equal(f.read().stories[0].status, 'unverified', 'unreadable required frontmatter')
})

test('actual partial page, missing CLI, and implicit or empty journey scope cannot complete', (t) => {
	const f = fixture(t)
	const partial = JSON.parse(cli('--workflow-dir', f.workflow, '--archived', '--all-fields', '--limit', '2', '--page', '1'))
	assert.throws(() => taskListing(partial), /Incomplete/)
	assert.throws(() => taskListing({ entities: [], pagination: { has_next: 'false', total: '1', page: '1', limit: '0' } }), /Incomplete/)
	for (const mutate of [(m) => { delete m.journey }, (m) => { delete m.steps[0].stories[0].id },
		(m) => { m.steps[0].stories.push({ ...m.steps[0].stories[0], release: 'R2' }) }]) {
		const copy = structuredClone(model); mutate(copy)
		assert.equal(f.read(copy).stories[0].status, 'unverified')
	}
	const empty = { ...model, steps: [] }
	assert.notEqual(f.read(empty).releases[0].status, 'exists')
	const oldPath = process.env.PATH
	try { process.env.PATH = ''; assert.equal(f.read().stories[0].status, 'unverified') } finally { process.env.PATH = oldPath }
	const code = `import {buildAllPages} from './lib/render.mjs'; console.log(buildAllPages(${JSON.stringify(model)}, null, ['story-map','journey-board']).length)`
	assert.ok(Number(execFileSync(process.execPath, ['--input-type=module', '-e', code], { cwd: plugin, env: { ...process.env, PATH: '' } })) > 0)
	assert.throws(() => execFileSync(process.execPath, ['--input-type=module', '-e', code.replace("['story-map','journey-board']", "['invalid']")], { cwd: plugin, env: { ...process.env, PATH: '' }, stdio: 'pipe' }))
})

test('derived projections use three borders without entering story wording or source readback', (t) => {
	const f = fixture(t), copy = structuredClone(model)
	copy.steps[0].stories.push({ id: 'gamma', card: 'Inspect unknown work', release: 'R1', status: 'exists' })
	const before = JSON.stringify(copy), progress = f.read(copy), pages = ['story-map', 'journey-board']
	const records = buildAllPages(copy, null, pages, progress)
	for (const prefix of ['shape:sm-story-', 'shape:jm-R1-story-']) {
		assert.deepEqual(['alpha', 'beta', 'gamma'].map((id) => records.find((r) => r.id === `${prefix}${id}-status-border`).props.color), ['red', 'green', 'violet'])
		const native = records.find((r) => r.id === `${prefix}alpha`)
		assert.equal(storyBorder({ ...native, props: { ...native.props, growY: 80 } }).props.color, 'red')
	}
	assert.equal(JSON.stringify(copy), before)
	assert.match(texts(records), /local Spacedock tasks/)
	assert.match(texts(records), /1\/3 stories development-complete/)
	assert.doesNotMatch(texts(buildAllPages(copy, null, pages)), /stories development-complete/)
	const source = join(f.root, 'copy.yaml'); writeFileSync(source, stringify(copy)); const original = readFileSync(source, 'utf8')
	assert.equal(applyDiff(source, diffAgainstModel(records, copy), source).wrote, null)
	assert.equal(readFileSync(source, 'utf8'), original)
	records.find((r) => r.id === 'shape:sm-story-alpha').props.richText = richText('Progress injected into wording')
	assert.equal(diffAgainstModel(records, copy).reworded.length, 1, 'wording injection falsifier')
})

test('actual refresh CLI draws to isolated canvas and native-compatible readback preserves bytes', async (t) => {
	const f = fixture(t), before = f.bytes(), room = 'progress-test'
	const server = spawn(process.execPath, ['--import', 'tsx', 'server/canvas-server.ts'], { cwd: plugin,
		env: { ...process.env, JOURNEY_API_PORT: '0', JOURNEY_ROOMS_DIR: join(f.root, 'rooms') }, stdio: ['ignore', 'pipe', 'pipe'] })
	t.after(async () => { if (server.exitCode === null) { server.kill(); await once(server, 'exit') } })
	const api = await new Promise((resolve, reject) => {
		const timeout = setTimeout(() => reject(new Error('Canvas startup timeout')), 10_000)
		server.once('exit', (code) => { clearTimeout(timeout); reject(new Error(`Canvas exited ${code}`)) })
		server.stdout.on('data', (chunk) => { const match = String(chunk).match(/doc API on (http:\/\/[^ ]+)/); if (match) { clearTimeout(timeout); resolve(match[1]) } })
	})
	const run = (...args) => execFileSync(process.execPath, ['lib/journey-progress.mjs', f.path, ...args], { cwd: plugin, env: { ...process.env, JOURNEY_API: api }, encoding: 'utf8', stdio: 'pipe' })
	assert.throws(() => run('--workflow-dir'), /usage/)
	assert.throws(() => run('--workflow-dir', f.workflow, '--draw', room, '--pages', 'invalid'), /usage/)
	const result = JSON.parse(run('--workflow-dir', f.workflow, '--draw', room, '--pages', 'story-map,journey-board'))
	assert.equal(result.drawn.status, 200)
	assert.throws(() => execFileSync(process.execPath, ['lib/journey-progress.mjs', f.path, '--workflow-dir', f.workflow, '--draw', room],
		{ cwd: plugin, env: { ...process.env, JOURNEY_API: 'http://127.0.0.1:0' }, stdio: 'pipe' }), (error) => {
		const refusal = JSON.parse(error.stderr)
		assert.equal(refusal.drawn, false)
		assert.equal(refusal.progress.releases[0].doneStories, 1)
		return error.status === 1
	})
	const records = await readRoom({ room, api })
	assert.match(texts(records), /1\/2 stories development-complete/)
	assert.equal(applyDiff(f.path, diffAgainstModel(records, model), f.path).wrote, null)
	assert.deepEqual(f.bytes(), before)
	const card = records.find((r) => r.id === 'shape:sm-story-alpha'); card.props.richText = richText('Review the required tasks')
	const res = await fetch(`${api}/doc?room=${room}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ put: [card] }) })
	assert.equal(res.status, 200)
	applyDiff(f.path, diffAgainstModel(await readRoom({ room, api }), model), f.path)
	const expected = structuredClone(model); expected.steps[0].stories[0].card = 'Review the required tasks'
	assert.deepEqual(loadJourney(f.path), expected)
	assert.deepEqual(f.bytes().slice(1), before.slice(1))
})
