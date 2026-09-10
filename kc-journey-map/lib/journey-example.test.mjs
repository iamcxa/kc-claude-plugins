// node --test lib/*.test.mjs
//
// The value criterion the rest of this stage serves: the skill's own journey file,
// migrated to the new format, passes every lint against this repository's real code.
// A fixture passing proves the lints run; this file passing proves the format actually
// describes the tool that made it.

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
