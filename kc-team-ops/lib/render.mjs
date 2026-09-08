// Projects a journey file onto a tldraw room.
//
// The file in the repository is the source of truth; the room is a rendering of it.
// Nothing here reads the room back — that is `read.mjs`. Positions are computed from
// the model's order, never stored in the model, so a journey file stays diffable.

const API = process.env.JOURNEY_API ?? `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`

import { readFileSync } from 'node:fs'
import { parse } from 'yaml'
import { fitHeight, indexes, label, note, page, releaseLine } from './records.mjs'
import { buildStoryMap } from './storymap.mjs'
import { buildFunctionMap } from './funcmap.mjs'

const PITCH = 320
const COL_W = 300
const X0 = 320
const LANE_X = 20
const LANE_W = 270

const Y_BADGE = 40
const Y_CARD = 110
const H_CARD = 200
const GAP = 60

// A badge changes what the column claims, so it is drawn as its own shape rather than
// folded into the sticky text where it would compete with the user's own words.
const BADGE_COLOR = {
	NEW: 'blue',
	NOT_BUILT: 'red',
	NOT_RULED: 'orange',
	CHANGED: 'violet',
}

const tag = (nodeId, kind) => ({ journey: { nodeId, kind } })

export function buildJourneyBoard(model) {
	const steps = model.steps ?? []
	const rulesById = new Map((model.rules ?? []).map((r) => [r.id, r.text]))
	const ix = indexes(Math.max(8, steps.length * 4 + 12))
	const put = []
	let n = 0

	// Shape ids are derived from the model, never from a coordinate: a position-derived
	// id leaves an orphan behind the moment a row changes height.
	const lane = (slug, text, y, h) =>
		put.push({
			...label({ id: `shape:jm-lane-${slug}`, text, x: LANE_X, y, w: LANE_W, h, index: ix[n++], color: 'grey' }),
			meta: tag(`lane-${slug}`, 'lane-label'),
		})

	// Every column in a row shares the tallest cell's height, so the lanes stay lanes.
	const systemText = (step) =>
		(step.system ?? []).map((l) => `• ${l}`).join('\n') + (step.cites?.length ? `\n[${step.cites.join(', ')}]` : '')
	const ruleText = (step) => (step.rules ?? []).map((id) => `• ${rulesById.get(id) ?? id}`).join('\n') || '—'

	// Every row below the cards is placed relative to what is actually above it: a step
	// note is optional and its height depends on its own text.
	const noteOf = (step) => (step.note ? step.note.trim() : '')
	const H_NOTE = Math.max(0, ...steps.map((s) => (noteOf(s) ? fitHeight(noteOf(s), COL_W) : 0)))
	const Y_NOTE = Y_CARD + H_CARD + 20
	const Y_SYSTEM = Y_NOTE + (H_NOTE ? H_NOTE + 20 : 0) + 20

	const H_SYSTEM = Math.max(200, ...steps.map((s) => fitHeight(systemText(s), COL_W)))
	const Y_RULES = Y_SYSTEM + H_SYSTEM + GAP
	const H_RULES = Math.max(160, ...steps.map((s) => fitHeight(ruleText(s), COL_W)))

	lane('journey', 'USER JOURNEY\nwhat a person does', Y_CARD, H_CARD)
	lane('system', 'SYSTEM FLOW\nthe call, route or write', Y_SYSTEM, H_SYSTEM)
	lane('constraints', 'CONSTRAINTS\nwhat must stay true', Y_RULES, H_RULES)

	steps.forEach((step, i) => {
		const x = X0 + i * PITCH

		if (step.badge) {
			put.push({
				...label({
					id: `shape:jm-badge-${step.id}`,
					text: step.badge.replace('_', ' '),
					x: x + 60,
					y: Y_BADGE,
					w: 180,
					h: 50,
					index: ix[n++],
					color: BADGE_COLOR[step.badge] ?? 'red',
				}),
				meta: tag(step.id, 'badge'),
			})
		}

		put.push({
			...note({
				id: `shape:jm-card-${step.id}`,
				text: `${i + 1}. ${step.card}`,
				x: x + 50,
				y: Y_CARD,
				index: ix[n++],
				color: 'green',
			}),
			meta: tag(step.id, 'step-card'),
		})

		// Citations name the repository, never a line number: a line number goes stale
		// silently and a sticky is the wrong place to carry one. The file keeps the detail.
		put.push({
			...label({
				id: `shape:jm-sys-${step.id}`,
				text: systemText(step),
				x,
				y: Y_SYSTEM,
				w: COL_W,
				h: H_SYSTEM,
				index: ix[n++],
				color: 'black',
				size: 's',
				align: 'start',
				verticalAlign: 'start',
			}),
			meta: tag(step.id, 'system'),
		})

		// A note on a step is why the column matters, not what it does — it sits under the
		// card rather than inside it, so the card stays the user's own words.
		if (step.note) {
			put.push({
				...label({
					id: `shape:jm-note-${step.id}`,
					text: noteOf(step),
					x,
					y: Y_NOTE,
					w: COL_W,
					h: H_NOTE,
					index: ix[n++],
					color: 'grey',
					size: 's',
					align: 'start',
					verticalAlign: 'start',
				}),
				meta: tag(step.id, 'note'),
			})
		}

		put.push({
			...label({
				id: `shape:jm-rules-${step.id}`,
				text: ruleText(step),
				x,
				y: Y_RULES,
				w: COL_W,
				h: H_RULES,
				index: ix[n++],
				color: 'blue',
				size: 's',
				align: 'start',
				verticalAlign: 'start',
			}),
			meta: tag(step.id, 'constraints'),
		})
	})

	const s = model.status ?? {}
	const statusText = [
		`STATUS — as of ${s.as_of ?? 'unknown date'}`,
		s.unproven && `Unproven: ${s.unproven}`,
		s.unmerged && `Unmerged: ${s.unmerged}`,
		s.undeployed && `Undeployed: ${s.undeployed}`,
		s.irreversible && `Irreversible: ${s.irreversible}`,
	]
		.filter(Boolean)
		.join('\n')

	const statusW = Math.max(600, steps.length * PITCH - 20)
	put.push({
		...label({
			id: 'shape:jm-status',
			text: statusText,
			x: X0,
			y: Y_RULES + H_RULES + 100,
			w: statusW,
			h: fitHeight(statusText, statusW),
			index: ix[n++],
			color: 'red',
			size: 's',
			align: 'start',
			verticalAlign: 'start',
		}),
		meta: tag('status', 'status'),
	})

	const slice = (model.slices ?? [])[0]
	if (slice) {
		const y = Y_RULES + H_RULES + 50
		put.push({
			...releaseLine({ id: 'shape:jm-slice-line', x: LANE_X, y, w: X0 + steps.length * PITCH, index: ix[n++] }),
			meta: tag(slice.id, 'slice-line'),
		})
		put.push({
			...label({
				id: 'shape:jm-slice-label',
				text: `SLICE\n${slice.outcome}`,
				x: LANE_X,
				y: y + 50,
				w: LANE_W,
				h: fitHeight(`SLICE\n${slice.outcome}`, LANE_W),
				index: ix[n++],
				size: 's',
			}),
			meta: tag(slice.id, 'slice-label'),
		})
	}

	return put
}

export function loadJourney(path) {
	return parse(readFileSync(path, 'utf8'))
}

// One room, several pages. The function map is drawn only when the file models something:
// an empty third page would claim the modelling was done and came out blank.
export function buildAllPages(model) {
	const modelled = (model.steps ?? []).some((s) => s.command || s.events?.length || s.state || s.readmodel)
	return [
		page({ id: 'page:page', name: 'Journey board', index: 'a1' }),
		...buildJourneyBoard(model),
		...buildStoryMap(model),
		...(modelled ? buildFunctionMap(model) : []),
	]
}

// Render is a reconcile, not an append: shapes this renderer owns that the model no
// longer produces are removed. Shapes a person drew by hand carry no `meta.journey`
// and are never touched — the room is where a workshop happens, not only where a file
// is displayed.
export async function renderToRoom({ path, room, api = API }) {
	const model = loadJourney(path)
	const roomId = room ?? model.journey

	// One room, two pages. The board a person talks over and the board the code is cited
	// on answer different questions and disagree about what the vertical axis means.
	const put = buildAllPages(model)
	const wanted = new Set(put.map((r) => r.id))

	const current = await fetch(`${api}/doc?room=${roomId}`).then((r) => r.json())
	// Only shapes are reconciled. Deleting a page would take a person's own pages with it.
	const remove = (current.snapshot?.documents ?? [])
		.map((d) => d.state)
		.filter((r) => r.typeName === 'shape' && r.meta?.journey && !wanted.has(r.id))
		.map((r) => r.id)

	const res = await fetch(`${api}/doc?room=${roomId}`, {
		method: 'PATCH',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ put, remove }),
	})
	return { status: res.status, body: await res.text(), shapes: put.length, removed: remove.length }
}
