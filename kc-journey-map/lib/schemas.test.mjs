import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { cpSync, existsSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { test } from 'node:test'
import { ADR_TITLE, footer } from './schemas.mjs'

const here = dirname(fileURLToPath(import.meta.url))
const copy = (t) => {
	const dir = mkdtempSync(join(tmpdir(), 'schemas-'))
	t.after(() => rmSync(dir, { recursive: true, force: true }))
	for (const f of ['schemas.mjs', 'contract-versions.json']) cpSync(join(here, f), join(dir, f))
	return dir
}
const run = (dir) => spawnSync('node', [join(dir, 'schemas.mjs'), 'journey-map-question'], { encoding: 'utf8' })

test('the table and version print and the recorded hash binds them', () => {
	const r = run(here)
	assert.equal(r.status, 0, r.stderr)
	assert.match(r.stdout, /^journey-map-question 1\.0\.0\n\| field \| rule \|/)
	assert.match(r.stdout, /\| `source` \|/)
})

test('an edited table with an unchanged version exits 1 naming the schema', (t) => {
	const dir = copy(t)
	const file = join(dir, 'schemas.mjs')
	writeFileSync(file, readFileSync(file, 'utf8').replace("['source',", "['origin',"))
	const r = run(dir)
	assert.equal(r.status, 1)
	assert.match(r.stderr, /journey-map-question: the field table changed but version 1\.0\.0 did not/)
})

test('a bumped version with no recorded hash exits 1', (t) => {
	const dir = copy(t)
	const file = join(dir, 'contract-versions.json')
	writeFileSync(file, readFileSync(file, 'utf8').replace('"current": "1.0.0"', '"current": "1.1.0"'))
	const r = run(dir)
	assert.equal(r.status, 1)
	assert.match(r.stderr, /current version 1\.1\.0 has no recorded hash/)
})

test('the printed history pointers name files that exist and a runnable command', () => {
	const repo = join(here, '..', '..')
	assert.ok(existsSync(join(repo, 'kc-journey-map', 'CHANGELOG.md')))
	const adrs = existsSync(join(repo, 'docs', 'adr')) ? readdirSync(join(repo, 'docs', 'adr')) : []
	assert.ok(adrs.some((f) => f.endsWith(`-${ADR_TITLE}.md`)), `an ADR titled ${ADR_TITLE} exists`)
	const text = footer('journey-map-question')
	assert.match(text, /node kc-journey-map\/lib\/schemas\.mjs journey-map-question/)
	assert.match(text, /kc-journey-map\/CHANGELOG\.md/)
	const r = spawnSync('node', [join(repo, 'kc-journey-map', 'lib', 'schemas.mjs'), 'journey-map-question'], { encoding: 'utf8' })
	assert.ok(r.stdout.includes(text))
})

test('the README and SKILL.md send a reader to the schema command, the CHANGELOG and the ADR, and say when', () => {
	const plugin = join(here, '..')
	const readme = readFileSync(join(plugin, 'README.md'), 'utf8').replace(/\s+/g, ' ')
	const skill = readFileSync(join(plugin, 'skills', 'kc-journey-map', 'SKILL.md'), 'utf8').replace(/\s+/g, ' ')
	for (const pointer of ['`node lib/schemas.mjs journey-map-question`', 'release-please `CHANGELOG.md`', "`docs/adr/`", 'Read the CHANGELOG when', 'read the ADR before']) {
		assert.ok(readme.includes(pointer), `README names ${pointer}`)
	}
	for (const pointer of ['node lib/schemas.mjs journey-map-question', '`CHANGELOG.md`', 'Rulings from kc-dev-flow-2']) {
		assert.ok(skill.includes(pointer), `SKILL.md names ${pointer}`)
	}
})
