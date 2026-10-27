import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { stringify } from 'yaml'

const accept = fileURLToPath(new URL('./journey-accept.mjs', import.meta.url))
const hash = (path) => createHash('sha256').update(readFileSync(path)).digest('hex')
const node = (...args) => spawnSync(process.execPath, args, { encoding: 'utf8' })

const story = (id, extra = {}) => ({ id, card: `Story ${id}`, release: 'r1', status: 'exists', evidence: 'someSymbol', ...extra })
const map = (status = {}) => ({
	journey: 'demo',
	releases: [{ id: 'r1', name: 'One', goal: 'All six work.' }, { id: 'r2', name: 'Two', goal: 'Later.' }],
	steps: [{ id: 'a', card: 'A', stories: ['s1', 's2', 's3', 's4', 's5', 's6'].map((id) => story(id)) }, { id: 'b', card: 'B', stories: [story('later', { release: 'r2' })] }],
	status,
})
const report = (results, over = {}) => ({
	schema: 'release-acceptance/v1',
	walk: { journey: 'demo', release: 'r1', source_commit: 'abc1234' },
	stories: results.map(([id, result]) => ({ id, result, entry: 'nav', evidence: [], findings: [] })),
	not_tested: [],
	...over,
})
const SIX = [['s1', 'works'], ['s2', 'works'], ['s3', 'broken'], ['s4', 'missing-entry-point'], ['s5', 'not-reachable'], ['s6', 'not-reachable']]

function files(t, model, doc) {
	const dir = mkdtempSync(join(tmpdir(), 'journey-accept-'))
	t.after(() => rmSync(dir, { recursive: true, force: true }))
	const journey = join(dir, 'journey.yaml'); const reportPath = join(dir, 'report.json')
	writeFileSync(journey, stringify(model)); writeFileSync(reportPath, JSON.stringify(doc))
	return { journey, reportPath }
}

test('six exists stories: broken proposes unverified, missing-entry-point proposes gap, works and not-reachable propose no status change', (t) => {
	const f = files(t, map({ unproven: 'Nothing is proven yet.' }), report(SIX, { not_tested: ['the refund path', 'offline use'] }))
	const before = [hash(f.journey), hash(f.reportPath)]
	const run = node(accept, f.journey, f.reportPath)
	assert.equal(run.status, 0, run.stderr)
	const out = JSON.parse(run.stdout)
	assert.deepEqual(out.proposals.map((p) => [p.story, p.from, p.to]), [['s3', 'exists', 'unverified'], ['s4', 'exists', 'gap']])
	assert.equal(out.unproven.current, 'Nothing is proven yet.')
	assert.equal(out.unproven.proposed, 'Not reachable in the release walk: s5, s6. Not tested: the refund path; offline use.')
	assert.deepEqual([hash(f.journey), hash(f.reportPath)], before, 'neither file changed')
})

test('a missing-entry-point story already unverified proposes gap, a gap or broken-but-unverified story proposes nothing, and a clean walk proposes nothing', (t) => {
	const m = map(); const stories = m.steps[0].stories
	Object.assign(stories[0], { status: 'unverified', evidence: undefined }); Object.assign(stories[1], { status: 'gap', evidence: undefined }); Object.assign(stories[2], { status: 'unverified', evidence: undefined })
	const f = files(t, m, report([['s1', 'missing-entry-point'], ['s2', 'missing-entry-point'], ['s3', 'broken']]))
	assert.deepEqual(JSON.parse(node(accept, f.journey, f.reportPath).stdout).proposals.map((p) => [p.story, p.to]), [['s1', 'gap']])
	const clean = files(t, map(), report(SIX.map(([id]) => [id, 'works'])))
	const out = JSON.parse(node(accept, clean.journey, clean.reportPath).stdout)
	assert.deepEqual([out.proposals, out.unproven.proposed], [[], null])
})

test('a wrong schema string, a story off the release, a result outside the four, another journey and an unknown release exit 1 and name the cause', (t) => {
	const cases = [
		['schema', report(SIX, { schema: 'release-acceptance/v2' }), /not release-acceptance\/v1/],
		['story off the release', report([...SIX, ['later', 'works']]), /not on release r1: later/],
		['unknown story', report([['ghost', 'works']]), /not on release r1: ghost/],
		['result', report([['s1', 'fine']]), /result outside works, broken, missing-entry-point, not-reachable: s1="fine"/],
		['journey', report(SIX, { walk: { journey: 'other', release: 'r1' } }), /walks journey "other", the map is demo/],
		['release', report(SIX, { walk: { journey: 'demo', release: 'r9' } }), /release "r9", which the map lacks/],
	]
	for (const [label, doc, message] of cases) {
		const f = files(t, map(), doc)
		const before = [hash(f.journey), hash(f.reportPath)]
		const run = node(accept, f.journey, f.reportPath)
		assert.equal(run.status, 1, label)
		assert.equal(run.stdout, '', label)
		assert.match(run.stderr, message, label)
		assert.deepEqual([hash(f.journey), hash(f.reportPath)], before, label)
	}
	assert.equal(node(accept).status, 2)
})
