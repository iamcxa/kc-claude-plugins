// The function-map projection: Event Modeling's swimlanes over the journey's own columns.
//
// The columns are the journey's steps, unchanged. Only the lanes differ — Command, Event,
// State, Read model — which is why this is a third page of the same file rather than a
// second tool. The vocabulary is fmodel's tactical grammar (a decider takes a command and
// current state and emits events; a view folds events into something readable), borrowed
// as nouns. Nothing here runs Kotlin or event-sources anything.
//
// Events are the lane that earns its place: they carry causal order, and story order does
// not, so a build order derived from this page is derived from something real.

import { fitHeight, indexes, label, note, page } from './records.mjs'

const PITCH = 320
const COL_W = 300
const X0 = 320
const LANE_X = 20
const LANE_W = 270
const GAP = 50
const Y_TOP = 60

export const FUNC_PAGE_ID = 'page:jm-funcmap'

const tag = (nodeId, kind) => ({ journey: { nodeId, kind } })

// A step nobody has modelled is drawn as a gap, not left blank: an empty column reads as
// "nothing happens here", and the whole point is to see which steps have no model yet.
const UNMODELLED = '— not modelled —'

export function buildFunctionMap(model) {
	const steps = model.steps ?? []
	const put = [page({ id: FUNC_PAGE_ID, name: 'Function map', index: 'a4' })]
	const parentId = FUNC_PAGE_ID
	const ix = indexes(steps.length * 6 + 12)
	let n = 0

	const commandOf = (s) => s.command ?? UNMODELLED
	const eventsOf = (s) => (s.events?.length ? s.events : [UNMODELLED])
	const stateOf = (s) => s.state ?? UNMODELLED
	const viewOf = (s) => s.readmodel ?? UNMODELLED

	const H_CMD = Math.max(120, ...steps.map((s) => fitHeight(commandOf(s), COL_W)))
	const maxEvents = Math.max(1, ...steps.map((s) => eventsOf(s).length))
	// A size-m note is 200 tall, so the row pitch has to clear it. At 130 the stickies
	// overlapped each other into one orange block and ran into the State lane below.
	const NOTE_H = 200
	const H_EVENT = NOTE_H + 40
	const H_EVENTS = (maxEvents - 1) * H_EVENT + NOTE_H
	const H_STATE = Math.max(120, ...steps.map((s) => fitHeight(stateOf(s), COL_W)))
	const H_VIEW = Math.max(120, ...steps.map((s) => fitHeight(viewOf(s), COL_W)))

	const Y_CMD = Y_TOP
	const Y_EVENTS = Y_CMD + H_CMD + GAP
	const Y_STATE = Y_EVENTS + H_EVENTS + GAP
	const Y_VIEW = Y_STATE + H_STATE + GAP

	const lane = (slug, text, y, h) =>
		put.push({
			...label({ id: `shape:fm-lane-${slug}`, text, x: LANE_X, y, w: LANE_W, h, index: ix[n++], parentId, color: 'grey', size: 's' }),
			meta: tag(`lane-${slug}`, 'lane-label'),
		})

	lane('command', 'COMMAND\nthe intent a person or a job submits', Y_CMD, H_CMD)
	lane('event', 'EVENT\nwhat became true, including the refusals', Y_EVENTS, H_EVENTS)
	lane('state', 'STATE\nwhat the decision is made against', Y_STATE, H_STATE)
	lane('readmodel', 'READ MODEL\nwhat someone can look at afterwards', Y_VIEW, H_VIEW)

	steps.forEach((step, i) => {
		const x = X0 + i * PITCH

		put.push({
			...label({ id: `shape:fm-cmd-${step.id}`, text: commandOf(step), x, y: Y_CMD, w: COL_W, h: H_CMD, index: ix[n++], parentId, color: 'blue', size: 's' }),
			meta: tag(step.id, 'command'),
		})

		// One sticky per event: an event is the unit a ticket and an acceptance criterion
		// are written against, so it has to be a thing you can point at and move.
		eventsOf(step).forEach((event, j) => {
			put.push({
				...note({ id: `shape:fm-event-${step.id}-${j}`, text: event, x: x + 50, y: Y_EVENTS + j * H_EVENT, index: ix[n++], parentId, color: 'orange', size: 's' }),
				meta: tag(`${step.id}-e${j}`, 'event'),
			})
		})

		put.push({
			...label({ id: `shape:fm-state-${step.id}`, text: stateOf(step), x, y: Y_STATE, w: COL_W, h: H_STATE, index: ix[n++], parentId, color: 'green', size: 's' }),
			meta: tag(step.id, 'state'),
		})

		put.push({
			...label({ id: `shape:fm-view-${step.id}`, text: viewOf(step), x, y: Y_VIEW, w: COL_W, h: H_VIEW, index: ix[n++], parentId, color: 'violet', size: 's' }),
			meta: tag(step.id, 'readmodel'),
		})
	})

	return put
}
