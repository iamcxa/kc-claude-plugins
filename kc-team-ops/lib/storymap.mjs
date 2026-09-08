// The story-map projection: the page people talk over.
//
// Jeff Patton's shape: blue for the persona and for release boundaries, green for the
// backbone of activities, yellow for the stories beneath them, small labels for ownership
// and for evidence status. The backbone reads left to right as a narrative.
//
// A release is a horizontal band across every activity, named at the left margin, with a
// full-width line above it. That is what makes the map plannable: the first band has to be
// a thin line through the whole backbone that still works, and you can only see whether it
// is one when the bands cut across all the columns. Bands scoped to a set of columns —
// which is what this drew before — cannot express a walking skeleton at all.
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
	const put = [page({ id: STORY_PAGE_ID, name: 'Story map', index: 'a3' })]

	const parentId = STORY_PAGE_ID
	const maxStories = Math.max(0, ...steps.map((s) => (s.stories ?? []).length))
	const ix = indexes(Math.max(24, steps.length * (maxStories + 4) + (model.releases?.length ?? 0) * 2 + 24))
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

	})

	// ── release bands ────────────────────────────────────────────────────────────
	// A release is a horizontal band across every activity, not a set of columns. That is
	// the whole point of the method: the first band has to be a thin line through the
	// entire backbone that still works, and you cannot see whether it is one unless the
	// bands cut across all of them.
	const releases = model.releases ?? []
	const storyOf = (step, story, j) => ({
		id: typeof story === 'string' ? `${step.id}-${j}` : (story.id ?? `${step.id}-${j}`),
		text: typeof story === 'string' ? story : story.card,
		release: typeof story === 'string' ? null : (story.release ?? null),
	})

	const all = steps.flatMap((step) => (step.stories ?? []).map((story, j) => ({ step, ...storyOf(step, story, j) })))

	// A story nobody has placed is drawn in a band of its own rather than dropped: where it
	// belongs is a decision someone still owes, and a silent omission hides that.
	const bands = [
		...releases.map((r) => ({ ...r, stories: all.filter((s) => s.release === r.id) })),
		{ id: null, name: 'UNASSIGNED', goal: 'No release decided yet.', stories: all.filter((s) => !s.release || !releases.some((r) => r.id === s.release)) },
	].filter((b) => b.stories.length)

	let bandTop = Y_STORIES
	bands.forEach((band, bi) => {
		if (bi > 0) {
			bandTop += 40
			put.push({
				...releaseLine({ id: `shape:sm-relline-${band.id ?? 'unassigned'}`, x: LEFT, y: bandTop, w: X0 + steps.length * PITCH, index: ix[n++], parentId }),
				meta: tag(band.id ?? 'unassigned', 'release-line'),
			})
			bandTop += 40
		}

		const text = `${band.name}\n${band.goal ?? ''}`.trim()
		put.push({
			...label({
				id: `shape:sm-rellabel-${band.id ?? 'unassigned'}`,
				text,
				x: LEFT,
				y: bandTop,
				w: LEFT_W,
				h: fitHeight(text, LEFT_W),
				index: ix[n++],
				parentId,
				color: band.id ? 'blue' : 'red',
				size: 's',
			}),
			meta: tag(band.id ?? 'unassigned', 'release-label'),
		})

		// Priority runs top to bottom inside a band, per column.
		const perColumn = new Map()
		for (const story of band.stories) {
			const list = perColumn.get(story.step.id) ?? []
			list.push(story)
			perColumn.set(story.step.id, list)
		}
		for (const [stepId, list] of perColumn) {
			const i = steps.findIndex((s) => s.id === stepId)
			list.forEach((story, j) => {
				put.push({
					...note({ id: `shape:sm-story-${story.id}`, text: story.text, x: X0 + i * PITCH, y: bandTop + j * STORY_PITCH, index: ix[n++], parentId, color: 'yellow' }),
					meta: tag(story.id, 'story'),
				})
			})
		}

		const rows = Math.max(1, ...[...perColumn.values()].map((l) => l.length))
		bandTop += rows * STORY_PITCH
	})

	;(model.ownership ?? []).forEach((band, i) => {
		const from = steps.findIndex((s) => s.id === band.from)
		const to = steps.findIndex((s) => s.id === band.to)
		if (from < 0 || to < 0) return
		put.push({
			...label({
				id: `shape:sm-own-${band.id ?? i}`,
				text: `${band.owner} — ${band.note ?? ''}`.trim(),
				x: X0 + from * PITCH - 20,
				y: Y_BAND,
				w: (to - from + 1) * PITCH,
				h: bandH,
				index: ix[n++],
				parentId,
				color: 'violet',
				size: 's',
			}),
			meta: tag(band.id ?? `own-${i}`, 'ownership'),
		})
	})

	return put
}

