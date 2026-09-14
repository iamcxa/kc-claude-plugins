
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { readFileSync } from 'node:fs'
import { loadModel, diffAgainstModel } from './read.mjs'
import { buildAllPages } from './render.mjs'
import { lintJourney } from './lint.mjs'
import { buildReleaseContract } from './release-contract.mjs'

const PKG_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const JOURNEY = join(PKG_ROOT, 'skills/kc-journey-map/references/journey.example.yaml')

test("the packaged fictional journey passes every lint", () => {
	const model = loadModel(JOURNEY)
	const violations = lintJourney(model, { repoRoot: PKG_ROOT, journeyPath: JOURNEY })
	assert.deepEqual(violations, [], JSON.stringify(violations, null, 2))
})

test('every fictional story is explicitly unverified', () => {
	const model = loadModel(JOURNEY)
	const stories = (model.steps ?? []).flatMap((s) => s.stories ?? [])
	assert.ok(stories.length > 0, 'the file has no stories to check')
	assert.ok(
		stories.every((s) => typeof s === 'object' && s.status === 'unverified' && !s.evidence),
		'a fictional story claims implementation evidence or lacks unverified status'
	)
})

test('a release contract generates for every packaged release', () => {
	const model = loadModel(JOURNEY)
	assert.ok(model.releases.length > 0)
	for (const release of model.releases) {
		const doc = buildReleaseContract(model, release.id, { journeyPath: 'journey.example.yaml' })
		assert.match(doc, new RegExp(release.name))
		assert.match(doc, /\| Story \| Status \| Evidence \| Question \| Rules \|/)
	}
})

test('the packaged native snapshot matches the source across all projections', () => {
	const model = loadModel(JOURNEY)
	const snapshot = JSON.parse(readFileSync(join(PKG_ROOT, 'skills/kc-journey-map/references/example/book-pickup.tldr'), 'utf8'))
	assert.ok(snapshot.schema, 'the snapshot must retain the native tldraw schema')
	const expected = buildAllPages(model, null, ['story-map', 'journey-board', 'function-map'])
	const pages = (records) => records.filter((r) => r.typeName === 'page').map(({ id, name }) => ({ id, name })).sort((a, b) => a.id.localeCompare(b.id))
	assert.deepEqual(pages(snapshot.records), pages(expected))
	// Native layout normalization may change geometry; authored text, identities and status must agree.
	const content = (records) => records.filter((r) => r.typeName === 'shape' && r.meta?.journey).map((r) => ({
		id: r.id, parentId: r.parentId, journey: r.meta.journey,
		richText: r.props.richText, color: r.props.color,
	})).sort((a, b) => a.id.localeCompare(b.id))
	assert.deepEqual(content(snapshot.records), content(expected))
	const diff = diffAgainstModel(snapshot.records.filter((r) => r.typeName === 'shape'), model)
	for (const [kind, changes] of Object.entries(diff)) {
		assert.ok(Array.isArray(changes) ? changes.length === 0 : !changes, `unexpected snapshot drift: ${kind}`)
	}
})
