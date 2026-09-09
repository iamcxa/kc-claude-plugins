// Projects a journey file onto a tldraw room.
//
// The file in the repository is the source of truth; the room is a rendering of it.
// Nothing here reads the room back — that is `read.mjs`. Positions are computed from
// the model's order, never stored in the model, so a journey file stays diffable.

const API = process.env.JOURNEY_API ?? `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`

import { readFileSync } from 'node:fs'
import { parse } from 'yaml'
import { fitHeight, indexes, label, note, page, pageLink, releaseLine } from './records.mjs'
import { STORY_PAGE_ID, buildStoryMap } from './storymap.mjs'
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

// One board per release, scoped to the steps that release touches.
//
// The board exists to answer the question the story map raises and cannot answer: given
// that we want this release, what does the system do today, what has to stay true, and
// what is therefore missing. Scoped that way, the NOT BUILT columns on a release's board
// are that release's build list. Drawn across the whole journey — which is what this did
// — the same badges are a pile of unrelated gaps belonging to no particular decision.
export const boardPageId = (releaseId) => (releaseId ? `page:jm-board-${releaseId}` : 'page:jm-board-all')

export function buildJourneyBoard(model, { release = null, room = null } = {}) {
	const inRelease = (step) =>
		!release || (step.stories ?? []).some((x) => x?.release === release.id)
	const steps = (model.steps ?? []).filter(inRelease)
	const parentId = boardPageId(release?.id)
	const idp = `shape:jm-${release?.id ?? 'all'}-`
	const rulesById = new Map((model.rules ?? []).map((r) => [r.id, r.text]))
	const put = []
	const ix = indexes(Math.max(12, steps.length * 5 + 16))
	let n = 0

	// Shape ids are derived from the model, never from a coordinate: a position-derived
	// id leaves an orphan behind the moment a row changes height.
	const lane = (slug, text, y, h) =>
		put.push({
			...label({ id: `${idp}lane-${slug}`, text, x: LANE_X, y, w: LANE_W, h, index: ix[n++], parentId, color: 'grey' }),
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
					id: `${idp}badge-${step.id}`,
					parentId,
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
				id: `${idp}card-${step.id}`,
				parentId,
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
				id: `${idp}sys-${step.id}`,
				parentId,
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
					id: `${idp}note-${step.id}`,
					parentId,
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
				id: `${idp}rules-${step.id}`,
				parentId,
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
			id: `${idp}status`,
			parentId,
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

	const title = release ? `${release.name} — what is missing` : 'Journey board'
	const relText = release ? `${release.name}\n${release.goal ?? ''}\n\n← back to the story map`.trim() : ''
	const relH = relText ? fitHeight(relText, LANE_W) : 0
	put.unshift(page({ id: parentId, name: title, index: release ? `a${5 + (model.releases ?? []).findIndex((r) => r.id === release.id)}` : 'a2' }))

	if (release) {
		put.push({
			...label({
				id: `${idp}release`,
				text: relText,
				x: LANE_X,
				// Sits clear of the first lane label rather than on top of it: the label's
				// height follows the release goal, which is as long as somebody wrote it.
				y: Y_CARD - relH - 40,
				w: LANE_W,
				h: relH,
				index: ix[n++],
				parentId,
				color: 'blue',
				size: 's',
				url: room ? pageLink(room, STORY_PAGE_ID) : '',
			}),
			meta: tag(release.id, 'release-label'),
		})
	}

	const slice = (model.slices ?? [])[0]
	if (slice) {
		const y = Y_RULES + H_RULES + 50
		put.push({
			...releaseLine({ id: `${idp}slice-line`, x: LANE_X, y, w: X0 + steps.length * PITCH, index: ix[n++], parentId }),
			meta: tag(slice.id, 'slice-line'),
		})
		put.push({
			...label({
				id: `${idp}slice-label`,
				parentId,
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
// Which activities a release actually touches. A release that leaves an activity empty is
// not automatically wrong — a later release's activities are not part of an earlier one's
// journey — but it is the question the map exists to make askable, so it is said out loud
// rather than left to whoever is looking at the picture.
export function releaseCoverage(model) {
	const steps = model.steps ?? []
	return (model.releases ?? []).map((r) => {
		const covered = steps.filter((s) => (s.stories ?? []).some((x) => x?.release === r.id)).map((s) => s.id)
		return { release: r.id, covered: covered.length, of: steps.length, missing: steps.filter((s) => !covered.includes(s.id)).map((s) => s.id) }
	})
}

export function buildAllPages(model, room = null) {
	const modelled = (model.steps ?? []).some((s) => s.command || s.events?.length || s.state || s.readmodel)
	const releases = model.releases ?? []
	// A board per release when the file has releases; one whole-journey board when it does
	// not, so a map drawn before anyone has sliced it still renders.
	const boards = releases.length
		? releases.flatMap((release) => buildJourneyBoard(model, { release, room }))
		: buildJourneyBoard(model, { room })
	return [...buildStoryMap(model, room), ...boards, ...(modelled ? buildFunctionMap(model) : [])]
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
	const put = buildAllPages(model, roomId)
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
	return { status: res.status, body: await res.text(), shapes: put.length, removed: remove.length, coverage: releaseCoverage(model) }
}
