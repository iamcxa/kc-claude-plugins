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
import { fitHeight, indexes, label, note, page, releaseLine } from './records.mjs'
import { normalizeStory } from './model.mjs'

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

// tldraw's default page, so the map people should land on is the one they land on and
// no empty 'Page 1' is left beside it.
export const STORY_PAGE_ID = 'page:page'

const tag = (nodeId, kind) => ({ journey: { nodeId, kind } })

export function buildStoryMap(model) {
	const steps = model.steps ?? []
	const put = [page({ id: STORY_PAGE_ID, name: 'Story map', index: 'a1' })]

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
	const oneJourneyH = model.one_journey ? 70 : 0
	const Y_BACKBONE = Y_BAND + (hasOwnership ? bandH + GAP : 0) + oneJourneyH
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

	// One sentence naming what is true when the whole loop works, read above the
	// backbone it sits over rather than folded into the persona note it is not part of.
	if (model.one_journey) {
		put.push({
			...label({
				id: 'shape:sm-one-journey',
				text: `ONE JOURNEY\n${model.one_journey}`,
				x: X0,
				y: Y_BACKBONE - oneJourneyH,
				w: Math.max(600, steps.length * PITCH - 20),
				h: oneJourneyH - 10,
				index: ix[n++],
				parentId,
				color: 'blue',
				size: 's',
				align: 'start',
			}),
			meta: tag('one-journey', 'one-journey'),
		})
	}

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
	})

	// ── release bands ────────────────────────────────────────────────────────────
	const releases = model.releases ?? []
	const all = steps.flatMap((step) => (step.stories ?? []).map((story, j) => ({ step, ...normalizeStory(step, story, j) })))

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
				const x = X0 + i * PITCH
				const y = bandTop + j * STORY_PITCH
				put.push({
					...note({ id: `shape:sm-story-${story.id}`, text: story.card, x, y, index: ix[n++], parentId, color: 'yellow' }),
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
