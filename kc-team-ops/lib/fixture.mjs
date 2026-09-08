// A test fixture, and nothing else — it is not a journey of any product.
//
// The shipped example is a real board and declares no stories, no Now row and no
// ownership band, so those paths need a model of their own.

export const fixtureModel = {
	journey: 'fixture',
	persona: 'A person who has to do the thing.',
	now: [
		{ id: 'now-manual', card: 'Does it by hand', pain: 'takes an afternoon', workaround: 'a spreadsheet' },
		{ id: 'now-tool', card: 'Uses an existing tool', pain: 'stops at the boundary' },
	],
	steps: [
		{ id: 'a', card: 'Asks for the thing', stories: ['Names it', 'Picks a target'] },
		{
			id: 'b',
			card: 'Gets the thing',
			badge: 'NOT_BUILT',
			stories: [{ id: 'b-see', card: 'Sees it arrive' }],
			command: 'GetTheThing(id)',
			events: ['ThingDelivered', 'DeliveryRefused'],
			state: 'the thing',
			readmodel: 'a delivery receipt',
		},
		{ id: 'c', card: 'Uses the thing', stories: ['Reads the result'] },
	],
	later: ['Does it for a team', 'Does it on a schedule'],
	ownership: [{ id: 'own-setup', owner: 'Setup', from: 'a', to: 'b', note: 'operator-assisted is acceptable' }],
	slices: [{ id: 'first', outcome: 'One person completes the loop once.' }],
	rules: [],
	status: { undeployed: 'nothing is deployed', as_of: '2026-09-08' },
}
