// The story-map projection: the page people talk over.
//
// Jeff Patton's shape, and the visual convention from the workshop this borrows from:
// blue for the persona and for release boundaries, green for the backbone of activities,
// yellow for the stories beneath them, frames for Now and Later, small labels for
// ownership and for evidence status. The backbone reads left to right as a narrative;
// under each activity, order runs top to bottom by priority, with variants below the
// main path.
//
// It is a projection of the same file the journey board renders from. The two pages
// disagree about the vertical axis on purpose — here it is priority, there it is lane —
// which is exactly why they are two pages and not one grid.

import { fitHeight, indexes, label, note, page, releaseLine } from './records.mjs'

const PITCH = 240
const X0 = 300
const LEFT = 20
const LEFT_W = 250

const Y_PERSONA = 40
const BAND_H = 60
const STORY_PITCH = 250
// The Now row's height depends on how much pain a step carries, so every row below it
// is placed relative to the tallest thing above rather than at a fixed offset.
const GAP = 40

export const STORY_PAGE_ID = 'page:jm-storymap'

const tag = (nodeId, kind) => ({ journey: { nodeId, kind } })

export function buildStoryMap(model) {
	const steps = model.steps ?? []
	const later = model.later ?? []
	const put = [page({ id: STORY_PAGE_ID, name: 'Story map', index: 'a3' })]

	const parentId = STORY_PAGE_ID
	const maxStories = Math.max(0, ...steps.map((s) => (s.stories ?? []).length))
	const ix = indexes(Math.max(12, steps.length * (maxStories + 3) + later.length + 16))
	let n = 0

	const nowTexts = (model.now ?? []).map((item) =>
		[item.card, item.pain && `pain: ${item.pain}`, item.workaround && `workaround: ${item.workaround}`]
			.filter(Boolean)
			.join('\n')
	)
	const personaText = model.persona ? `PERSONA\n${model.persona}` : ''
	const headH = Math.max(
		personaText ? fitHeight(personaText, LEFT_W) : 0,
		0,
		...nowTexts.map((t) => fitHeight(t, 220))
	)
	// A band is as tall as the wordiest band in the row, so a long owner note cannot
	// spill over its neighbour.
	const bandH = Math.max(
		BAND_H,
		...(model.ownership ?? []).map((b) => fitHeight(`${b.owner} — ${b.note ?? ''}`.trim(), (steps.length ? PITCH : 240)))
	)
	const hasOwnership = (model.ownership ?? []).length > 0
	const Y_BAND = Y_PERSONA + headH + GAP
	const Y_BACKBONE = Y_BAND + (hasOwnership ? bandH + GAP : 0) + (steps.some((s) => s.badge) ? 60 : 0)
	const Y_STORIES = Y_BACKBONE + 260

	if (model.persona) {
		put.push({
			...label({
				id: 'shape:sm-persona',
				text: `PERSONA\n${model.persona}`,
				x: LEFT,
				y: Y_PERSONA,
				w: LEFT_W,
				h: headH,
				index: ix[n++],
				parentId,
				color: 'blue',
				size: 's',
			}),
			meta: tag('persona', 'persona'),
		})
	}

	// The status quo, when the file records one. CL's rule, kept: an unfinished
	// implementation of the thing being proposed is not the user's current world.
	;(model.now ?? []).forEach((item, i) => {
		const text = nowTexts[i]
		put.push({
			...label({
				id: `shape:sm-now-${item.id ?? i}`,
				text,
				x: X0 + i * PITCH,
				y: Y_PERSONA,
				w: 220,
				h: headH,
				index: ix[n++],
				parentId,
				color: 'grey',
				size: 's',
			}),
			meta: tag(item.id ?? `now-${i}`, 'now'),
		})
	})

	steps.forEach((step, i) => {
		const x = X0 + i * PITCH

		put.push({
			...note({
				id: `shape:sm-act-${step.id}`,
				text: step.activity ?? step.card,
				x,
				y: Y_BACKBONE,
				index: ix[n++],
				parentId,
				color: 'green',
			}),
			meta: tag(step.id, 'activity'),
		})

		// Evidence status rides as a small label, never inside the sticky: a card is the
		// user's words and a badge is ours, and mixing them is how a board starts lying.
		if (step.badge) {
			put.push({
				...label({
					id: `shape:sm-badge-${step.id}`,
					text: step.badge.replace('_', ' '),
					x,
					y: Y_BACKBONE - 56,
					w: 200,
					h: 48,
					index: ix[n++],
					parentId,
					color: step.badge === 'NOT_BUILT' ? 'red' : 'orange',
					size: 's',
				}),
				meta: tag(step.id, 'badge'),
			})
		}

		;(step.stories ?? []).forEach((story, j) => {
			const text = typeof story === 'string' ? story : story.card
			const id = typeof story === 'string' ? `${step.id}-${j}` : (story.id ?? `${step.id}-${j}`)
			put.push({
				...note({
					id: `shape:sm-story-${id}`,
					text,
					x,
					y: Y_STORIES + j * STORY_PITCH,
					index: ix[n++],
					parentId,
					color: 'yellow',
				}),
				meta: tag(id, 'story'),
			})
		})
	})

	const storyRows = Math.max(1, maxStories)
	let y = Y_STORIES + storyRows * STORY_PITCH + 40

	// Ownership is drawn as a band with a named edge rather than by recolouring cards,
	// so a journey that crosses two products still reads as one journey.
	;(model.ownership ?? []).forEach((band, i) => {
		const from = steps.findIndex((s) => s.id === band.from)
		const to = steps.findIndex((s) => s.id === band.to)
		if (from < 0 || to < 0) return
		const w = (to - from + 1) * PITCH
		put.push({
			...label({
				id: `shape:sm-own-${band.id ?? i}`,
				text: `${band.owner} — ${band.note ?? ''}`.trim(),
				x: X0 + from * PITCH - 20,
				y: Y_BAND,
				w,
				h: bandH,
				index: ix[n++],
				parentId,
				color: 'violet',
				size: 's',
			}),
			meta: tag(band.id ?? `own-${i}`, 'ownership'),
		})
	})

	// A slice that names its steps scopes columns, so it is drawn as a boundary around
	// those columns. A release line across the whole width would put every column above
	// it and claim the first slice contains all of them — which is what it did.
	;(model.slices ?? []).forEach((slice, i) => {
		const from = slice.steps?.length ? steps.findIndex((s) => s.id === slice.steps[0]) : -1
		const to = slice.steps?.length ? steps.findIndex((s) => s.id === slice.steps[slice.steps.length - 1]) : -1
		const scoped = from >= 0 && to >= from
		const text = `${slice.label ?? `SLICE ${i + 1}`}\n${slice.outcome}`

		if (scoped) {
			put.push({
				...releaseLine({
					id: `shape:sm-sliceline-${slice.id}`,
					x: X0 + from * PITCH - 20,
					y: y,
					w: (to - from + 1) * PITCH,
					index: ix[n++],
					parentId,
				}),
				meta: tag(slice.id, 'slice-line'),
			})
			put.push({
				...label({
					id: `shape:sm-slicelabel-${slice.id}`,
					text,
					x: X0 + from * PITCH - 20,
					y: y + 40,
					w: (to - from + 1) * PITCH - 20,
					h: fitHeight(text, (to - from + 1) * PITCH - 20),
					index: ix[n++],
					parentId,
					color: 'blue',
					size: 's',
				}),
				meta: tag(slice.id, 'slice-label'),
			})
			return
		}

		const lineY = y + i * 320
		put.push({
			...releaseLine({
				id: `shape:sm-sliceline-${slice.id}`,
				x: LEFT,
				y: lineY,
				w: X0 + Math.max(steps.length, later.length) * PITCH,
				index: ix[n++],
				parentId,
			}),
			meta: tag(slice.id, 'slice-line'),
		})
		put.push({
			...label({
				id: `shape:sm-slicelabel-${slice.id}`,
				text,
				x: LEFT,
				y: lineY + 40,
				w: LEFT_W,
				h: fitHeight(text, LEFT_W),
				index: ix[n++],
				parentId,
				color: 'blue',
				size: 's',
			}),
			meta: tag(slice.id, 'slice-label'),
		})
	})

	const scopedSlices = (model.slices ?? []).every((s) => s.steps?.length)
	const laterY = scopedSlices ? y + 260 : y + (model.slices?.length ?? 1) * 320 - 280
	later.forEach((item, i) => {
		const text = typeof item === 'string' ? item : item.card
		const id = typeof item === 'string' ? `later-${i}` : (item.id ?? `later-${i}`)
		put.push({
			...note({
				id: `shape:sm-later-${id}`,
				text,
				x: X0 + i * PITCH,
				y: laterY,
				index: ix[n++],
				parentId,
				color: 'orange',
			}),
			meta: tag(id, 'later'),
		})
	})

	return put
}
