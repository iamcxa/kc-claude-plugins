
import { fitHeight, indexes, label, note, page, releaseLine, withStoryStatus, storyProgress, releaseProgressText, connector, connectorBindings, QUESTION_STATUS_COLORS } from './records.mjs'
import { normalizeStory, questionCardText } from './model.mjs'

const PITCH = 240
const X0 = 300
const LEFT = 20
const LEFT_W = 250

const Y_PERSONA = 40
const BAND_H = 60
const STORY_PITCH = 250
const STORY_W = 200
const STORY_H = 200
const QUESTION_GAP = 10
const GAP = 40

export const STORY_PAGE_ID = 'page:page'

const tag = (nodeId, kind) => ({ journey: { nodeId, kind } })

export function buildStoryMap(model, room = null, progress = null) {
	const steps = model.steps ?? []
	const put = [page({ id: STORY_PAGE_ID, name: 'Story map', index: 'a1' })]

	const parentId = STORY_PAGE_ID
	const maxStories = Math.max(0, ...steps.map((s) => (s.stories ?? []).length))
	// Each question needs 2 index slots (card + connector arrow); its bindings need none.
	const totalQuestions = steps.flatMap((step) => (step.stories ?? []).map((story, j) => normalizeStory(step, story, j)))
		.reduce((sum, s) => sum + (s.questions?.length ?? 0), 0)
	const ix = indexes(Math.max(24, steps.length * (maxStories + 4) + (model.releases?.length ?? 0) * 2 + 24) + totalQuestions * 2)
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
	// Every other box measures its text; this one took a literal 70 and clipped the
	// last line of any sentence that wrapped past two.
	const oneJourneyW = Math.max(600, steps.length * PITCH - 20)
	const oneJourneyH = model.one_journey ? fitHeight(`ONE JOURNEY\n${model.one_journey}`, oneJourneyW) + 10 : 0
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
				w: oneJourneyW,
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

		const questionsHeight = (story) => (story?.questions ?? []).reduce((h, q, k) => h + (k ? QUESTION_GAP : 0) + fitHeight(questionCardText(q), STORY_W), 0)
		const perColumn = new Map()
		for (const story of band.stories) {
			const list = perColumn.get(story.step.id) ?? []
			list.push(story)
			perColumn.set(story.step.id, list)
		}
		// Beside the card puts the question in the next column's lane, where that column's
		// card covers it and the surviving sliver reads as the neighbour's question.
		const rows = Math.max(1, ...[...perColumn.values()].map((l) => l.length))
		const columns = [...perColumn.values()]
		const rowTop = [bandTop]
		for (let j = 0; j < rows; j++) {
			const q = Math.max(0, ...columns.map((l) => questionsHeight(l[j])))
			rowTop.push(rowTop[j] + STORY_PITCH + (q ? q + QUESTION_GAP : 0))
		}

		for (const [stepId, list] of perColumn) {
			const i = steps.findIndex((s) => s.id === stepId)
			list.forEach((story, j) => {
				const x = X0 + i * PITCH
				const y = rowTop[j]
				const storyShapeId = `shape:sm-story-${story.id}`
				put.push({
					...note({ id: storyShapeId, text: story.card, x, y, index: ix[n++], parentId, color: 'yellow' }),
					meta: { journey: { nodeId: story.id, kind: 'story', ...(progress ? { progress: storyProgress(progress, model, story) } : {}), ...(story.status ? { status: story.status } : {}) } },
				})

				let qy = y + STORY_H + QUESTION_GAP
				for (const question of story.questions ?? []) {
					const h = fitHeight(questionCardText(question), STORY_W)
					const questionId = `shape:sm-question-${story.id}-${question.id}`
					put.push({
						...label({
							id: questionId,
							text: questionCardText(question),
							x,
							y: qy,
							w: STORY_W,
							h,
							index: ix[n++],
							parentId,
							color: QUESTION_STATUS_COLORS[question.status] ?? 'grey',
							size: 's',
							align: 'start',
						}),
						// The question id binds to its review-board card; the story id keeps the
						// layout checks able to find the card a question hangs under.
						meta: { journey: { nodeId: question.id, kind: 'question', story: story.id } },
					})
					const linkId = `shape:sm-qlink-${story.id}-${question.id}`
					put.push({
						...connector({ id: linkId, parentId, index: ix[n++], color: 'grey' }),
						meta: { journey: { nodeId: question.id, kind: 'question-link', story: story.id } },
					})
					put.push(...connectorBindings(linkId, storyShapeId, questionId).map((b) => ({
						...b, meta: { journey: { nodeId: question.id, kind: 'question-link', story: story.id } },
					})))
					qy += h + QUESTION_GAP
				}
			})
		}

		const bandH2 = rowTop[rows] - bandTop
		bandTop += progress ? Math.max(bandH2, fitHeight(text, LEFT_W)) : bandH2
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

