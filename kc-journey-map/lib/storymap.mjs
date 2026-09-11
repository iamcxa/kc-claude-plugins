
import { fitHeight, indexes, label, note, page, releaseLine, withStoryStatus, storyProgress, releaseProgressText } from './records.mjs'
import { normalizeStory } from './model.mjs'

const PITCH = 240
const X0 = 300
const LEFT = 20
const LEFT_W = 250

const Y_PERSONA = 40
const BAND_H = 60
const STORY_PITCH = 250
const GAP = 40

export const STORY_PAGE_ID = 'page:page'

const tag = (nodeId, kind) => ({ journey: { nodeId, kind } })

export function buildStoryMap(model, room = null, progress = null) {
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

	const releases = model.releases ?? []
	const all = steps.flatMap((step) => (step.stories ?? []).map((story, j) => ({ step, ...normalizeStory(step, story, j) })))

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

		const existsCount = band.id ? band.stories.filter((s) => s.status === 'exists').length : null
		const text = `${band.name}\n${band.goal ?? ''}${band.id ? `\n\n${progress ? releaseProgressText(progress, model, band.id) : `${existsCount}/${band.stories.length} exist`}` : ''}`.trim()
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
					meta: { journey: { nodeId: story.id, kind: 'story', ...(progress ? { progress: storyProgress(progress, model, story) } : {}), ...(story.status ? { status: story.status } : {}) } },
				})

				if (story.question) {
					const w = 200
					put.push({
						...label({
							id: `shape:sm-story-question-${story.id}`,
							text: `? ${story.question}`,
							x: x + 210,
							y,
							w,
							h: fitHeight(story.question, w),
							index: ix[n++],
							parentId,
							color: 'violet',
							size: 's',
							align: 'start',
						}),
						meta: tag(story.id, 'story-question'),
					})
				}
			})
		}

		const rows = Math.max(1, ...[...perColumn.values()].map((l) => l.length))
		bandTop += progress ? Math.max(rows * STORY_PITCH, fitHeight(text, LEFT_W)) : rows * STORY_PITCH
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

	return withStoryStatus(put, progress)
}

