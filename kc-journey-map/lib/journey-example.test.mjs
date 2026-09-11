// Checks the worked example against the plugin schema and citation lints.
// Self-citation consistency does not establish delivery or target-user usability.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadModel } from './read.mjs'
import { lintJourney } from './lint.mjs'
import { buildReleaseContract } from './release-contract.mjs'

const PKG_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const JOURNEY = join(PKG_ROOT, 'skills/kc-journey-map/references/journey.example.yaml')

test("this skill's own journey file passes every lint", () => {
	const model = loadModel(JOURNEY)
	const violations = lintJourney(model, { repoRoot: PKG_ROOT, journeyPath: JOURNEY })
	assert.deepEqual(violations, [], JSON.stringify(violations, null, 2))
})

test('every story in the migrated file carries a status', () => {
	// Guards the format itself, not just the lint: a story that slipped past migration
	// with no status field would still be caught above, but this names what "every lint
	// passes" actually proved for this file — nobody left a story unmigrated.
	const model = loadModel(JOURNEY)
	const stories = (model.steps ?? []).flatMap((s) => s.stories ?? [])
	assert.ok(stories.length > 0, 'the file has no stories to check')
	assert.ok(
		stories.every((s) => typeof s === 'object' && s.status),
		'a story in the migrated file has no status'
	)
})

test('a release contract generates for every release the migrated file declares', () => {
	const model = loadModel(JOURNEY)
	assert.ok(model.releases.length > 0)
	for (const release of model.releases) {
		const doc = buildReleaseContract(model, release.id, { journeyPath: 'journey.example.yaml' })
		assert.match(doc, new RegExp(release.name))
		assert.match(doc, /\| Story \| Status \| Evidence \| Question \| Rules \|/)
	}
})

import { buildJourneyBoard } from './render.mjs'
import { buildStoryMap } from './storymap.mjs'

test('worked host selection stays unverified across projections and contract', () => {
	const model = loadModel(JOURNEY)
	const host = model.steps.flatMap((s) => s.stories ?? []).find((s) => s.id === 'ask-which-boards-to-draw')
	assert.equal(host.status, 'unverified')
	const release = model.releases.find((r) => r.id === host.release)
	const text = (s) => s.props.richText.content.flatMap((p) => (p.content ?? []).map((t) => t.text ?? '')).join('\n')
	for (const [records, kind] of [[buildStoryMap(model), 'story-border'], [buildJourneyBoard(model, { release }), 'story-border']]) {
		assert.equal(records.find((s) => s.meta?.journey?.nodeId === host.id && s.meta.journey.kind === kind).props.color, 'violet')
		const stories = model.steps.flatMap((s) => s.stories ?? []).filter((s) => s.release === release.id)
		const count = stories.filter((s) => s.status === 'exists').length
		assert.match(text(records.find((s) => s.meta?.journey?.nodeId === release.id && s.meta.journey.kind === 'release-label')), new RegExp(`${count}/${stories.length} (stories )?exist`))
	}
	assert.match(buildReleaseContract(model, release.id), /Ask which boards[^\n]*\| unverified \|/)
})
