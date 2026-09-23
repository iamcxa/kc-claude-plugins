
const API = process.env.JOURNEY_API ?? `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`

import { readFileSync } from 'node:fs'
import { parse } from 'yaml'
import { DocumentRecordType, TLDOCUMENT_ID } from '@tldraw/tlschema'
import { fitHeight, indexes, label, page, pageLink, releaseLine, withStoryStatus, releaseProgressText, activityCard, storyCard, questionCard, answerCard, note, storyBorder, NOTE_SIZE } from './records.mjs'
import { STORY_PAGE_ID, buildStoryMap } from './storymap.mjs'
import { buildFunctionMap } from './funcmap.mjs'
import { normalizeStory, isQuestionAnswered } from './model.mjs'

const STORY_PITCH = 240
const STORY_W = 220
const GROUP_GAP = 60
const X0 = 320
const LANE_X = 20
const LANE_W = 270
const GAP = 40
export const QUESTION_GAP = 10
// Questions spread out horizontally beneath their story, not stacked in one column —
// this is the release board's own zoom-in layout, not shared with the story map, which
// keeps its single vertical column.
// tldraw draws every note 200 wide whatever its size prop, which only scales the font —
// pitching questions by NOTE_SIZE.s packed six notes into the width of four.
const NOTE_W = 200
// Exported so read.mjs can recognise a hand-placed note by the same grid this file draws
// it on, instead of guessing a second tolerance.
export const QUESTION_PITCH = NOTE_W + 20
const tag = (nodeId, kind) => ({ journey: { nodeId, kind } })

// Every card colour the release board draws, plus the story-status border it does not
// explain on its own — one legend, top-left, so a reader never has to guess what a
// colour or an outline means. Whether a question is answered is shown by whether an
// answer card hangs under it, not by this legend or the question card itself.
const BOARD_LEGEND = [
	{ nodeId: 'activity', text: 'ACTIVITY', color: 'green' },
	{ nodeId: 'flow', text: 'FLOW', color: 'light-blue', box: true },
	{ nodeId: 'constraint', text: 'CONSTRAINT', color: 'orange', box: true },
	{ nodeId: 'story', text: 'STORY', color: 'yellow' },
	{ nodeId: 'question', text: 'QUESTION', color: 'light-green' },
	{ nodeId: 'answer', text: 'ANSWER', color: 'light-violet' },
	{ nodeId: 'status-exists', text: 'EXISTS', color: 'yellow', status: 'exists' },
	{ nodeId: 'status-gap', text: 'GAP', color: 'yellow', status: 'gap' },
	{ nodeId: 'status-unverified', text: 'UNVERIFIED', color: 'yellow', status: 'unverified' },
]
const LEGEND_SCALE = 0.45

// Shared activity rules are context, not proof that each story exists.
export const boardPageId = (releaseId) => (releaseId ? `page:jm-board-${releaseId}` : 'page:jm-board-all')

export function buildJourneyBoard(model, { release = null, room = null, progress = null } = {}) {
	let right = X0
	const groups = (model.steps ?? []).map((step) => {
		const stories = (step.stories ?? []).map((story, j) => normalizeStory(step, story, j))
			.filter((story) => !release || story.release === release.id)
		if (release && !stories.length) return null
		const questionRow = (story) => ((story.questions ?? []).some(isQuestionAnswered) ? 2 : 1) * QUESTION_PITCH
		const w = Math.max(300, stories.length * STORY_PITCH - 20,
			stories.reduce((sum, story) => sum + Math.max(STORY_PITCH, questionRow(story)), 0) - 20)
		const group = { step, stories, x: right, w }
		right += w + GROUP_GAP
		return group
	}).filter(Boolean)
	const parentId = boardPageId(release?.id)
	const idp = `shape:jm-${release?.id ?? 'all'}-`
	const rulesById = new Map((model.rules ?? []).map((r) => [r.id, r.text]))
	const put = []

	// system: and rules: belong to the step, not to each story — drawing them per story
	// would repeat them once per story in the step. One card per line/rule instead of one
	// aggregated box; a step with neither still gets one placeholder card so the render
	// never reads as having silently dropped a step's flow or constraints.
	const flowLines = (step) => {
		const lines = step.system?.length ? [...step.system] : ['No system flow recorded.']
		const extra = [step.cites?.length && `[${step.cites.join(', ')}]`, step.note?.trim()].filter(Boolean).join('\n')
		if (extra) lines[lines.length - 1] = `${lines[lines.length - 1]}\n${extra}`
		return lines
	}
	const constraintLines = (step) => step.rules?.length ? step.rules.map((id) => rulesById.get(id) ?? id) : ['No constraints recorded.']

	// Each question needs 2 index slots (card + connector arrow), and an answered one
	// needs 2 more (its own answer card + connector); bindings need none.
	const questionSlots = groups.reduce((sum, g) => sum + g.stories.reduce((s, story) =>
		s + (story.questions ?? []).reduce((qs, q) => qs + 2 + (isQuestionAnswered(q) ? 2 : 0), 0), 0), 0)
	const flowConstraintSlots = groups.reduce((sum, g) => sum + flowLines(g.step).length + constraintLines(g.step).length, 0)
	const ix = indexes(24 + BOARD_LEGEND.length + groups.length * 2 + flowConstraintSlots
		+ groups.reduce((sum, g) => sum + g.stories.length, 0) + questionSlots)
	let n = 0
	const box = (slug, nodeId, kind, text, x, y, w, h, color = 'black', extra = {}) => {
		put.push({
			...label({ id: `${idp}${slug}`, parentId, text, x, y, w, h, index: ix[n++],
				color, size: 's', align: 'start', verticalAlign: 'start', ...extra }),
			meta: tag(nodeId, kind),
		})
	}
	// A story's own open questions may stack wider than one story's worth; reserve one
	// question row plus, when any question here is answered, one answer row beneath it.
	const questionsHeight = (story) => (story.questions ?? []).length * QUESTION_PITCH

	// A note's rendered height is a runtime concern (growY), not something this generator
	// computes ahead of time — the story map has never tried to for its own activity or
	// story notes, and the release board's now the same shared note, so it stops trying too.
	const activityH = NOTE_SIZE.m
	// Flow, then constraints, then stories. Every group shares one flow band and one
	// constraint band sized to the tallest column, exactly like the shared rows this
	// replaces — a short activity's cards just leave blank space, not a row that creeps
	// up under a neighbour's taller stack.
	const flowY = activityH + GAP
	const bullets = (lines) => lines.length > 1 ? lines.map((l) => `• ${l}`).join('\n') : lines[0]
	const flowH = Math.max(60, ...groups.map((g) => fitHeight(bullets(flowLines(g.step)), g.w - 10)))
	const constraintY = flowY + flowH + GAP
	const constraintH = Math.max(60, ...groups.map((g) => fitHeight(bullets(constraintLines(g.step)), g.w - 10)))
	const storyY = constraintY + constraintH + GAP

	// The legend is made of the board's own cards, shrunk, so reading it is the same as
	// reading the board: a sample note per kind, and a sample story for each status border.
	BOARD_LEGEND.forEach((entry, k) => {
		const side = 200 * LEGEND_SCALE
		const lx = LANE_X + (k % 2) * (side + 10)
		const ly = Math.floor(k / 2) * (side + 10)
		const sample = { ...note({ id: `${idp}legend-${entry.nodeId}`, text: entry.text, x: lx, y: ly, index: ix[n++], parentId, color: entry.color, size: 's' }),
			meta: { journey: { nodeId: entry.nodeId, kind: 'board-legend', ...(entry.status ? { status: entry.status } : {}) } } }
		sample.props.scale = LEGEND_SCALE
		sample.props.growY = 0
		if (entry.box) {
			box(`legend-${entry.nodeId}`, entry.nodeId, 'board-legend', entry.text, lx, ly, side, side, entry.color, { fill: 'semi', align: 'middle', verticalAlign: 'middle' })
			put[put.length - 1].props.scale = LEGEND_SCALE
			return
		}
		put.push(sample)
		if (entry.status) {
			const border = storyBorder({ ...sample, meta: { journey: { kind: 'story', nodeId: entry.nodeId, status: entry.status } } })
			put.push({ ...border, id: `${sample.id}-border`, meta: { journey: { kind: 'board-legend-border', nodeId: entry.nodeId } } })
		}
	})

	for (const group of groups) {
		const { step, stories, x, w } = group
		// Same builder the story map uses for the same step, so the two cannot draw it
		// differently. Left-aligned on the group, unlike the flow/constraint cards below it
		// which still span the group's full width — this is the release board's own
		// addition, not shared with the story map.
		put.push(activityCard({ id: `${idp}card-${step.id}`, step, x: x + 10, y: 0, index: ix[n++], parentId }))

		// Flow and constraints are context for the step, read as one block each: several
		// lines become a bullet list inside one box rather than a stack of cards.
		const block = (lines, kind, color, top) => {
			const text = bullets(lines)
			box(`${kind}-${step.id}`, step.id, kind, text, x + 10, top, w - 10, fitHeight(text, w - 10), color, { fill: 'semi' })
		}
		block(flowLines(step), 'flow', 'light-blue', flowY)
		block(constraintLines(step), 'constraint', 'orange', constraintY)

		if (!stories.length) {
			box(`empty-${step.id}`, step.id, 'empty-stories', 'No stories recorded.', x, storyY, w, NOTE_SIZE.m, 'grey')
		}
		stories.forEach((story, j) => {
			const before = stories.slice(0, j).reduce((sum, st) => sum + Math.max(STORY_PITCH, (st.questions?.length ? ((st.questions ?? []).some(isQuestionAnswered) ? 2 : 1) : 0) * QUESTION_PITCH), 0)
			const sx = x + before + (stories.length === 1 && !story.questions?.length ? (w - STORY_W) / 2 : 0)
			const storyShapeId = `${idp}story-${story.id}`
			// Same builder the story map uses for the same story — its text is `story.card`
			// alone; evidence and task progress live in the release contract and story-status
			// meta, not on the card, so the two projections cannot draw the same story two
			// different ways.
			put.push(storyCard({ id: storyShapeId, story, x: sx + 10, y: storyY, index: ix[n++], parentId, progress, model }))

			// Questions spread left to right beneath the story, as laid out by hand on the
			// live canvas — not stacked in one column. Each answered question's answer sits
			// straight below that question, before the next question's column.
			// Questions stack straight down under their story and each answer sits to the right of
			// its own question, on the same row. Position says what belongs to what, so no
			// connectors are drawn and every gap on the grid is the same.
			story.questions?.forEach((question, k) => {
				const qx = sx + 10
				const qy = storyY + NOTE_SIZE.m + QUESTION_GAP + k * QUESTION_PITCH
				const questionId = `${idp}question-${story.id}-${question.id}`
				put.push(questionCard({ id: questionId, question, story: story.id, x: qx, y: qy, index: ix[n++], parentId }))
				if (isQuestionAnswered(question)) {
					const answerId = `${idp}answer-${story.id}-${question.id}`
					put.push(answerCard({ id: answerId, question, story: story.id, x: qx + QUESTION_PITCH, y: qy, index: ix[n++], parentId }))
				}
			})
		})
	}

	const boardBottom = storyY + Math.max(NOTE_SIZE.m, ...groups.flatMap((g) => g.stories.map((s) =>
		NOTE_SIZE.m + (questionsHeight(s) ? QUESTION_GAP + questionsHeight(s) : 0))))

	const s = model.status ?? {}
	const statusText = [
		`STATUS — as of ${s.as_of ?? 'unknown date'}`,
		s.unproven && `Unproven: ${s.unproven}`,
		s.unmerged && `Unmerged: ${s.unmerged}`,
		s.undeployed && `Undeployed: ${s.undeployed}`,
		s.irreversible && `Irreversible: ${s.irreversible}`,
	].filter(Boolean).join('\n')
	const boardW = Math.max(600, right - GROUP_GAP - X0)
	// The header row holds the release on the left and its status on the right. Below the
	// board, the status moved with whichever story carried the most questions.
	const headerW = release ? Math.floor((boardW - GAP) / 2) : boardW
	const statusW = headerW
	const statusH = fitHeight(statusText, statusW)

	const title = release ? `${release.name} — stories, flow & constraints` : 'Journey board'
	put.unshift(page({ id: parentId, name: title, index: release ? `a${5 + (model.releases ?? []).findIndex((r) => r.id === release.id)}` : 'a2' }))
	if (release) {
		const stories = groups.flatMap((g) => g.stories)
		const text = `${release.name}\n${release.goal ?? ''}\n\n${progress ? releaseProgressText(progress, model, release.id) : `${stories.filter((s) => s.status === 'exists').length}/${stories.length} stories exist`}\n← back to the story map`
		const h = Math.max(fitHeight(text, headerW), statusH)
		box('release', release.id, 'release-label', text, X0, -h - GAP, headerW, h, 'blue',
			{ url: room ? pageLink(room, STORY_PAGE_ID) : '' })
		box('status', 'status', 'status', statusText, X0 + headerW + GAP, -h - GAP, statusW, h, 'red')
	} else {
		box('status', 'status', 'status', statusText, X0, -statusH - GAP, statusW, statusH, 'red')
	}
	const slice = (model.slices ?? [])[0]
	if (slice) {
		const y = boardBottom + 50
		put.push({
			...releaseLine({ id: `${idp}slice-line`, x: LANE_X, y, w: right - LANE_X, index: ix[n++], parentId }),
			meta: tag(slice.id, 'slice-line'),
		})
		const text = `SLICE\n${slice.outcome}`
		box('slice-label', slice.id, 'slice-label', text, LANE_X, y + 50, LANE_W, fitHeight(text, LANE_W))
	}
	return withStoryStatus(put, progress, { legend: false })
}

export function loadJourney(path) {
	return parse(readFileSync(path, 'utf8'))
}

export function releaseCoverage(model) {
	const steps = model.steps ?? []
	return (model.releases ?? []).map((r) => {
		const covered = steps.filter((s) => (s.stories ?? []).some((x) => x?.release === r.id)).map((s) => s.id)
		return { release: r.id, covered: covered.length, of: steps.length, missing: steps.filter((s) => !covered.includes(s.id)).map((s) => s.id) }
	})
}

const journeyBoardPages = (model, room, progress) => {
	const releases = model.releases ?? []
	return releases.length
		? releases.flatMap((release) => buildJourneyBoard(model, { release, room, progress }))
		: buildJourneyBoard(model, { room, progress })
}

export const PROJECTIONS = {
	'story-map': (model, room, progress) => buildStoryMap(model, room, progress),
	'journey-board': journeyBoardPages,
	'function-map': (model) => buildFunctionMap(model),
}
export const PROJECTION_KEYS = Object.keys(PROJECTIONS)
export const DEFAULT_PROJECTIONS = ['story-map']

export function buildAllPages(model, room = null, selection = DEFAULT_PROJECTIONS, progress = null) {
	const chosen = selection?.length ? selection : DEFAULT_PROJECTIONS
	const unknown = chosen.filter((key) => !PROJECTIONS[key])
	if (unknown.length) throw new Error(`unknown projection(s): ${unknown.join(', ')}`)
	return PROJECTION_KEYS.filter((key) => chosen.includes(key)).flatMap((key) => PROJECTIONS[key](model, room, progress))
}

// Untagged shapes belong to the user and must survive redraw. A partial redraw
// (`--pages journey-board`) rebuilds only some pages; a tagged shape or binding whose
// page this render did not touch belongs to a different --pages run and must survive
// too — scope removal to the pages this render actually produced, not to every tagged
// record in the room. A binding carries no parentId of its own; look up the page of
// the connector shape it hangs off (`fromId`) instead.
export function staleRecordIds(currentRecords, put) {
	const wanted = new Set(put.map((r) => r.id))
	const scopedPageIds = new Set(put.filter((r) => r.typeName === 'page').map((r) => r.id))
	const shapesById = new Map(currentRecords.filter((r) => r.typeName === 'shape').map((r) => [r.id, r]))
	// A shape's own parentId is its page for every top-level shape, but storyBorder
	// nests a border under its story shape — walk the chain, not just one hop.
	const pageIdOfShape = (shape) => {
		const seen = new Set()
		for (let cur = shape; cur && !seen.has(cur.id); cur = shapesById.get(cur.parentId)) {
			if (String(cur.parentId).startsWith('page:')) return cur.parentId
			seen.add(cur.id)
		}
		return undefined
	}
	const pageIdOf = (r) => (r.typeName === 'binding' ? pageIdOfShape(shapesById.get(r.fromId)) : pageIdOfShape(r))
	return currentRecords
		.filter((r) => (r.typeName === 'shape' || r.typeName === 'binding') && r.meta?.journey && !wanted.has(r.id))
		.filter((r) => scopedPageIds.has(pageIdOf(r)))
		.map((r) => r.id)
}

export async function renderToRoom({ path, room, selection, progress = null, api = API }) {
	const model = loadJourney(path)
	const roomId = room ?? model.journey

	const put = buildAllPages(model, roomId, selection, progress)

	const current = await fetch(`${api}/doc?room=${roomId}`).then((r) => r.json())
	const currentRecords = (current.snapshot?.documents ?? []).map((d) => d.state)
	const currentDocument = currentRecords.find((r) => r.id === TLDOCUMENT_ID)
	// Re-rendering projects the canonical YAML title into tldraw's native name.
	const document = DocumentRecordType.create({ ...currentDocument, id: TLDOCUMENT_ID,
		name: typeof model.title === 'string' ? model.title.trim() : '' })
	const remove = staleRecordIds(currentRecords, put)

	const res = await fetch(`${api}/doc?room=${roomId}`, {
		method: 'PATCH',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ put: [document, ...put], remove }),
	})
	return { status: res.status, body: await res.text(), shapes: put.length, removed: remove.length, coverage: releaseCoverage(model) }
}
