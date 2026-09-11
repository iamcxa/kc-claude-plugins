
export const fixtureModel = {
	journey: 'fixture',
	persona: 'A person who has to do the thing.',
	one_journey: 'A person asks for the thing once, and it arrives without them checking twice.',
	now: [
		{ id: 'now-manual', card: 'Does it by hand', pain: 'takes an afternoon', workaround: 'a spreadsheet' },
		{ id: 'now-tool', card: 'Uses an existing tool', pain: 'stops at the boundary' },
	],
	releases: [
		{ id: 'r1', name: 'RELEASE 1', goal: 'One person gets one thing, once.' },
		{ id: 'r2', name: 'RELEASE 2', goal: 'Extend only after the first line works.' },
	],
	steps: [
		{
			id: 'a',
			card: 'Asks for the thing',
			stories: [
				{ id: 'a-0', card: 'Names it', release: 'r1', status: 'exists', evidence: 'NamesIt' },
				{ id: 'a-2', card: 'Confirms it', release: 'r1', status: 'exists', evidence: 'ConfirmsIt' },
				{ id: 'a-1', card: 'Picks a target', release: 'r2', status: 'exists', evidence: 'PicksTarget' },
			],
		},
		{
			id: 'b',
			card: 'Gets the thing',
			stories: [{ id: 'b-see', card: 'Sees it arrive', release: 'r1', status: 'gap', question: 'Should delivery be push or pull?' }],
			command: 'GetTheThing(id)',
			events: ['ThingDelivered', 'DeliveryRefused'],
			state: 'the thing',
			readmodel: 'a delivery receipt',
		},
		{
			id: 'c',
			card: 'Uses the thing',
			stories: [{ id: 'c-read', card: 'Reads the result', release: 'r1', status: 'exists', evidence: 'ReadsResult' }, 'An unplaced idea'],
		},
	],
	ownership: [{ id: 'own-setup', owner: 'Setup', from: 'a', to: 'b', note: 'operator-assisted is acceptable' }],
	rules: [],
	status: { undeployed: 'nothing is deployed', as_of: '2026-09-08' },
}
