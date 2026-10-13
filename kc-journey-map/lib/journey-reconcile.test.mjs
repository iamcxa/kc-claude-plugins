import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { chmodSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { delimiter, join } from 'node:path'
import { test } from 'node:test'
import { BLOCK, FLOW, footprint } from './fixtures/journey-fold-shapes.mjs'
import { planFold } from './journey-fold.mjs'
import { reconcile } from './journey-reconcile.mjs'

const task = (over = {}) => ({ slug: 't', journey: 'shop', story: 'enter-by-qr', archived: true, footprints: [], skipped: [], ...over })
const value = (result, key) => result.lines.find((l) => l.startsWith(`${key} `)).slice(key.length + 1)

test('counts a fixture the way the baselines count a real map', () => {
	const r = reconcile(FLOW, [])
	assert.deepEqual(['stories', 'duplicate-story-ids', 'questions', 'answered', 'open', 'deferred', 'plain-open', 'repeated-question-ids', 'unsourced', 'unfolded', 'stale-open']
		.map((k) => value(r, k)), ['2', '0', '4', '1', '3', '1', '2', '1', '1', '0', '0'])
	assert.equal(r.failing, false)
	assert.equal(reconcile(BLOCK, []).lines.filter((l) => /^(questions|answered|deferred|plain-open) /.test(l)).join(','), 'questions 3,answered 1,deferred 1,plain-open 1')
})

test('an archived footprint the map does not hold is unfolded, and folding it makes the count 0', () => {
	const fps = [footprint()]
	const before = reconcile(FLOW, [task({ footprints: fps })])
	assert.equal(value(before, 'unfolded'), '1')
	assert.equal(before.failing, true)
	assert.match(before.lines.join('\n'), /unfolded: applied fp:t:1 enter-by-qr\/q1/)
	const after = reconcile(planFold(FLOW, fps).draft, [task({ footprints: fps })])
	assert.equal(value(after, 'unfolded'), '0')
	assert.equal(value(after, 'unsourced'), '1', 'the hand-written answer is still unsourced; the folded one is not')
})

test('a conflict, a missing question and a missing story stay unfolded with their reason', () => {
	const fps = [footprint({ question: 'q2' }), footprint({ id: 'fp:t:2', question: 'zz' }), footprint({ id: 'fp:t:3', story: 'zz' })]
	const r = reconcile(FLOW, [task({ footprints: fps })])
	assert.equal(value(r, 'unfolded'), '3')
	assert.match(r.lines.join('\n'), /unfolded: conflict fp:t:1[^\n]*\nunfolded: no-question fp:t:2[^\n]*\nunfolded: no-story fp:t:3/)
})

test('open questions on a story whose tasks are all archived are stale-open; a live task or a deferral clears them', () => {
	const stale = reconcile(FLOW, [task()])
	assert.equal(value(stale, 'stale-open'), '1')
	assert.match(stale.lines.join('\n'), /stale-open: enter-by-qr\/q1/)
	assert.equal(stale.failing, true)
	assert.equal(value(reconcile(FLOW, [task(), task({ slug: 'live', archived: false })]), 'stale-open'), '0')
	assert.equal(value(reconcile(FLOW, [task({ story: 'pick-nearby' })]), 'stale-open'), '1')
	assert.equal(value(reconcile(FLOW, [task({ journey: 'other' })]), 'stale-open'), '0')
})

test('footprints on a live task are pending and do not change the exit status', () => {
	const r = reconcile(FLOW, [task({ slug: 'live', archived: false, footprints: [footprint()] }), task({ slug: 'old', story: 'pick-nearby', archived: true })])
	assert.equal(value(r, 'pending'), '1')
	assert.equal(value(r, 'unfolded'), '0')
})

test('a duplicate story id is reported and fails the run; the output carries no timestamp and is stable', () => {
	const dup = FLOW.replace('id: pick-nearby', 'id: enter-by-qr')
	const r = reconcile(dup, [])
	assert.equal(value(r, 'duplicate-story-ids'), '1')
	assert.equal(r.duplicateStories, true)
	assert.deepEqual(reconcile(FLOW, [task()]).lines, reconcile(FLOW, [task()]).lines)
	assert.doesNotMatch(reconcile(FLOW, []).lines.join('\n'), /\d{4}-\d{2}-\d{2}T/)
})

test('changing one answer text on a copy moves unsourced by one', () => {
	const base = Number(value(reconcile(FLOW, []), 'unsourced'))
	const more = FLOW.replace('{id: q1, status: open, ask: "Who issues codes?"}', '{id: q1, status: open, ask: "Who issues codes?", answer: "Platform."}')
	assert.equal(Number(value(reconcile(more, []), 'unsourced')), base + 1)
})

test('the command exits 1 on a duplicate story id and 0 on distinct ids', (t) => {
	const dir = mkdtempSync(join(tmpdir(), 'reconcile-'))
	t.after(() => rmSync(dir, { recursive: true, force: true }))
	const stub = join(dir, 'spacedock')
	const empty = { entities: [], pagination: { has_next: 'false', total: '0', page: '1', limit: '0' } }
	writeFileSync(stub, `#!/bin/sh\necho '${JSON.stringify(empty)}'\n`)
	chmodSync(stub, 0o755)
	const run = (ids) => {
		const map = join(dir, 'journey.yaml')
		writeFileSync(map, `journey: shop\nsteps:\n- id: s\n  card: S\n  stories:\n${ids.map((id) => `  - id: ${id}\n    card: ${id}\n`).join('')}`)
		return spawnSync('node', [new URL('./journey-reconcile.mjs', import.meta.url).pathname, map, '--workflow-dir', dir],
			{ encoding: 'utf8', env: { ...process.env, PATH: `${dir}${delimiter}${process.env.PATH}` } })
	}
	const dup = run(['a', 'a'])
	assert.equal(dup.status, 1, dup.stderr)
	assert.match(dup.stdout, /^duplicate-story-ids 1$/m)
	const distinct = run(['a', 'b'])
	assert.equal(distinct.status, 0, distinct.stderr)
})
