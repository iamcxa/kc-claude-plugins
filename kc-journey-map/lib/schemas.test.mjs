import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { chmodSync, cpSync, existsSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { test } from 'node:test'
import { ADR_TITLES, footer } from './schemas.mjs'
import { readProgress } from './progress.mjs'

const here = dirname(fileURLToPath(import.meta.url))
const copy = (t) => {
	const dir = mkdtempSync(join(tmpdir(), 'schemas-'))
	t.after(() => rmSync(dir, { recursive: true, force: true }))
	for (const f of ['schemas.mjs', 'contract-versions.json']) cpSync(join(here, f), join(dir, f))
	return dir
}
const run = (dir, name = 'journey-map-question') => spawnSync('node', [join(dir, 'schemas.mjs'), name], { encoding: 'utf8' })

test('the table and version print and the recorded hash binds them', () => {
	const r = run(here)
	assert.equal(r.status, 0, r.stderr)
	assert.match(r.stdout, /^journey-map-question 1\.1\.0\n\| field \| rule \|/)
	assert.match(r.stdout, /\| `source` \|/)
})

test('an edited table with an unchanged version exits 1 naming the schema', (t) => {
	const dir = copy(t)
	const file = join(dir, 'schemas.mjs')
	writeFileSync(file, readFileSync(file, 'utf8').replace("['source',", "['origin',"))
	const r = run(dir)
	assert.equal(r.status, 1)
	assert.match(r.stderr, /journey-map-question: the field table changed but version 1\.1\.0 did not/)
})

test('a bumped version with no recorded hash exits 1', (t) => {
	const dir = copy(t)
	const file = join(dir, 'contract-versions.json')
	writeFileSync(file, readFileSync(file, 'utf8').replace('"current": "1.1.0"', '"current": "1.2.0"'))
	const r = run(dir)
	assert.equal(r.status, 1)
	assert.match(r.stderr, /current version 1\.2\.0 has no recorded hash/)
})

test('the printed history pointers name files that exist and a runnable command', () => {
	const repo = join(here, '..', '..')
	assert.ok(existsSync(join(repo, 'kc-journey-map', 'CHANGELOG.md')))
	const adrs = existsSync(join(repo, 'docs', 'adr')) ? readdirSync(join(repo, 'docs', 'adr')) : []
	for (const [name, title] of Object.entries(ADR_TITLES)) {
		assert.ok(adrs.some((f) => f.endsWith(`-${title}.md`)), `an ADR titled ${title} exists`)
		const text = footer(name)
		assert.ok(text.includes(`node kc-journey-map/lib/schemas.mjs ${name}`))
		assert.ok(text.includes(title), `the ${name} footer names its own ADR`)
		assert.match(text, /kc-journey-map\/CHANGELOG\.md/)
		const r = spawnSync('node', [join(repo, 'kc-journey-map', 'lib', 'schemas.mjs'), name], { encoding: 'utf8' })
		assert.ok(r.stdout.includes(text))
	}
})

test('release-walk prints its table and version, and an edited table with an unchanged version exits 1', (t) => {
	const ok = run(here, 'release-walk')
	assert.equal(ok.status, 0, ok.stderr)
	assert.match(ok.stdout, /^release-walk 1\.0\.0\n\| field \| rule \|/)
	assert.match(ok.stdout, /\| `proof_line` \|/)
	const dir = copy(t)
	const file = join(dir, 'schemas.mjs')
	writeFileSync(file, readFileSync(file, 'utf8').replace("['proof_line',", "['proof',"))
	const r = run(dir, 'release-walk')
	assert.equal(r.status, 1)
	assert.match(r.stderr, /release-walk: the field table changed but version 1\.0\.0 did not/)
})

test('journey-progress registers its printed table and refuses an unversioned shape edit', (t) => {
	const ok = run(here, 'journey-progress')
	assert.equal(ok.status, 0, ok.stderr)
	assert.match(ok.stdout, /^journey-progress 1\.1\.0\n/)
	assert.match(ok.stdout, /pending delivery acceptance/)
	const dir = copy(t), file = join(dir, 'schemas.mjs')
	writeFileSync(file, readFileSync(file, 'utf8').replace("['releases',", "['deliveries',"))
	const bad = run(dir, 'journey-progress')
	assert.equal(bad.status, 1)
	assert.match(bad.stderr, /journey-progress: the field table changed but version 1\.1\.0 did not/)
})

test('the progress producer preserves the registered keys and acceptance meanings', (t) => {
	const dir = mkdtempSync(join(tmpdir(), 'progress-contract-'))
	t.after(() => rmSync(dir, { recursive: true, force: true }))
	const taskPath = join(dir, 'build.md'); writeFileSync(taskPath, '')
	const task = { journey: 'demo', 'journey-release': 'r1', 'journey-story': 'first', status: 'done',
		'journey-required-tasks': '["build"]', 'journey-mapping-complete': 'true' }
	const model = { journey: 'demo', releases: [{ id: 'r1' }], steps: [{ stories: [{ id: 'first', release: 'r1' }] }] }
	const binary = join(dir, 'spacedock')
	const save = () => {
		const listing = { entities: [{ ...task, slug: 'build', id: 'build' }, { journey: 'demo', slug: 'old', id: 'old' }],
			pagination: { has_next: 'false', total: '2', page: '1', limit: '0' } }
		writeFileSync(binary, `#!/usr/bin/env node
const args = process.argv;
const value = args.includes('--read') ? ${JSON.stringify({ path: taskPath, frontmatter: task })}
 : args.includes('--resolve') ? ${JSON.stringify({ path: taskPath, slug: 'build', id: 'build', stored_id: '' })}
 : ${JSON.stringify(listing)};
console.log(JSON.stringify(value));
`)
		chmodSync(binary, 0o755)
	}
	const keys = (row, expected) => assert.deepEqual(Object.keys(row).sort(), expected.split(' ').sort())
	const oldPath = process.env.PATH
	process.env.PATH = `${dir}:${oldPath}`
	t.after(() => { process.env.PATH = oldPath })
	save()
	const complete = readProgress(model, dir)
	keys(complete, 'schema journey source observedAt diagnostic orphans stories releases')
	assert.equal(complete.schema, 'journey-progress/v1')
	assert.equal(complete.source, dir)
	assert.ok(Number.isFinite(Date.parse(complete.observedAt)))
	assert.equal(complete.diagnostic, null)
	assert.deepEqual(complete.orphans, [{ slug: 'old', id: 'old', release: null, story: null }])
	keys(complete.stories[0], 'journey release story status requiredTasks doneTasks taskIds members')
	assert.deepEqual(complete.stories[0], { journey: 'demo', release: 'r1', story: 'first', status: 'exists', requiredTasks: 1, doneTasks: 1, taskIds: ['build'], members: { tasks: 1, done: 1, prs: [] } })
	keys(complete.releases[0], 'release totalStories doneStories requiredTasks doneTasks status acceptance members')
	assert.deepEqual(complete.releases[0], { release: 'r1', totalStories: 1, doneStories: 1, requiredTasks: 1, doneTasks: 1, status: 'exists', acceptance: 'pending delivery acceptance', members: { storiesDone: 1, storiesOpen: 0, storiesEmpty: 0 } })
	task.status = 'implementation'; save()
	const gap = readProgress(model, dir)
	assert.equal(gap.stories[0].status, 'gap')
	assert.equal(gap.releases[0].status, 'gap')
	assert.equal(gap.releases[0].acceptance, 'delivery acceptance not established')
	writeFileSync(binary, '#!/bin/sh\nexit 2\n')
	const failed = readProgress(model, dir)
	assert.ok(failed.diagnostic)
	assert.equal(failed.stories[0].status, 'unverified')
	assert.ok(failed.stories[0].diagnostic)
	assert.equal(failed.releases[0].status, 'unverified')
	assert.equal(failed.releases[0].acceptance, 'delivery acceptance not established')
})

test('the README and SKILL.md send a reader to the schema command, the CHANGELOG and the ADR, and say when', () => {
	const plugin = join(here, '..')
	const readme = readFileSync(join(plugin, 'README.md'), 'utf8').replace(/\s+/g, ' ')
	const skill = readFileSync(join(plugin, 'skills', 'kc-journey-map', 'SKILL.md'), 'utf8').replace(/\s+/g, ' ')
	for (const pointer of ['`node lib/schemas.mjs journey-map-question`', '`node lib/schemas.mjs release-walk`', 'release-please `CHANGELOG.md`', "`docs/adr/`", 'Read the CHANGELOG when', 'read the ADR before']) {
		assert.ok(readme.includes(pointer), `README names ${pointer}`)
	}
	for (const pointer of ['node lib/schemas.mjs journey-map-question', '`CHANGELOG.md`', 'Rulings from kc-dev-flow-2']) {
		assert.ok(skill.includes(pointer), `SKILL.md names ${pointer}`)
	}
})
