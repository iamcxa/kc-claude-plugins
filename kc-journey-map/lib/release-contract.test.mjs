import assert from 'node:assert/strict'
import { test } from 'node:test'
import { buildReleaseContract, releaseContractRows } from './release-contract.mjs'

const fixture = {
	journey: 'demo',
	releases: [{ id: 'r1', name: 'RELEASE 1', goal: 'Ship the thin line.' }],
	rules: [{ id: 'r-a', text: 'Rule A text' }],
	steps: [
		{
			id: 's',
			rules: ['r-a'],
			stories: [
				{ id: 's-0', card: 'Do the thing', release: 'r1', status: 'exists', evidence: 'DoTheThing' },
				{ id: 's-1', card: 'Do another', release: 'r1', status: 'gap', question: 'Who owns this?' },
				{ id: 's-2', card: 'Not in this release', release: 'r2', status: 'exists', evidence: 'Elsewhere' },
			],
		},
	],
}

test('releaseContractRows scopes to one release only, in step/story order', () => {
	const { rows } = releaseContractRows(fixture, 'r1')
	assert.deepEqual(rows.map((r) => r.id), ['s-0', 's-1'])
})

test('buildReleaseContract carries status, evidence and rule ids per story', () => {
	const doc = buildReleaseContract(fixture, 'r1', { journeyPath: 'demo.yaml' })
	assert.match(doc, /Do the thing[\s\S]*exists[\s\S]*DoTheThing[\s\S]*r-a/, 'an exists story lost its evidence or its rule id')
	assert.match(doc, /Do another[\s\S]*gap[\s\S]*Who owns this\?/, 'a gap story lost its question')
	assert.match(doc, /Generated from demo\.yaml/)
	assert.ok(!doc.includes('Not in this release'), 'a story from another release leaked into this contract')
})

test('an unknown release throws rather than generating an empty contract', () => {
	assert.throws(() => buildReleaseContract(fixture, 'nope'), /no release/)
})

test('release contract preserves all three story states', () => {
	const model = structuredClone(fixture)
	model.steps[0].stories = ['gap', 'unverified', 'exists'].map((status) => ({ id: status, card: status, release: 'r1', status }))
	assert.deepEqual(releaseContractRows(model, 'r1').rows.map((r) => r.status), ['gap', 'unverified', 'exists'])
	assert.match(buildReleaseContract(model, 'r1'), /\| unverified \| unverified \|/)
})

const asked = {
	journey: 'demo',
	releases: [{ id: 'r1', name: 'RELEASE 1', goal: 'Ship the thin line.' }],
	rules: [],
	steps: [{ id: 's', stories: [
		{ id: 'a', card: 'Settled', release: 'r1', status: 'gap', questions: [
			{ id: 'a1', ask: 'Already decided?', status: 'answered' },
			{ id: 'a2', ask: 'Still deciding?', status: 'open' },
		] },
		{ id: 'b', card: 'All settled', release: 'r1', status: 'gap', questions: [{ id: 'b1', ask: 'Was decided?', status: 'answered' }] },
	] }],
}

test('the contract column carries only open questions, so it reads as what is still missing', () => {
	const doc = buildReleaseContract(asked, 'r1', { journeyPath: 'demo.yaml' })
	assert.match(doc, /Still deciding\?/, 'an open question is missing from the contract')
	assert.doesNotMatch(doc, /Already decided\?/, 'an answered question still fills the column')
})

test('a story whose questions are all answered shows an empty column, not a stale one', () => {
	const row = buildReleaseContract(asked, 'r1', { journeyPath: 'demo.yaml' }).split('\n').find((l) => l.startsWith('| All settled'))
	assert.match(row, /\| — \|/, 'a fully answered story did not fall back to the dash')
})
