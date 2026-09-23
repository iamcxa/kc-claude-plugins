
const API = process.env.JOURNEY_API ?? `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`

import { readFileSync } from 'node:fs'
import { parse } from 'yaml'
import { DocumentRecordType, TLDOCUMENT_ID } from '@tldraw/tlschema'
import { fitHeight, indexes, label, note, page, pageLink, releaseLine, withStoryStatus, storyProgress, releaseProgressText, connector, connectorBindings } from './records.mjs'
import { STORY_PAGE_ID, buildStoryMap } from './storymap.mjs'
import { buildFunctionMap } from './funcmap.mjs'
import { normalizeStory, storyStatusLabel, questionCardText } from './model.mjs'

const STORY_PITCH = 240
const STORY_W = 220
const STORY_H = 200
const GROUP_GAP = 60
const X0 = 320
const LANE_X = 20
const LANE_W = 270
const GAP = 40
const QUESTION_GAP = 10
const tag = (nodeId, kind) => ({ journey: { nodeId, kind } })

// Every card colour the release board draws, plus the story-status border it does not
// explain on its own — one legend, top-left, so a reader never has to guess what a
// colour or an outline means. QUESTION shows both outline states since colour alone no
// longer carries a question's status.
const BOARD_LEGEND = [
	{ nodeId: 'activity', text: 'ACTIVITY', color: 'green', extra: {} },
	{ nodeId: 'flow', text: 'FLOW — one card per system: line', color: 'light-blue', extra: { fill: 'solid' } },
	{ nodeId: 'constraint', text: 'CONSTRAINT — one card per rule', color: 'orange', extra: { fill: 'solid' } },
	{ nodeId: 'story', text: 'STORY', color: 'yellow', extra: { fill: 'solid' } },
	{ nodeId: 'question-open', text: 'QUESTION — OPEN', color: 'light-green', extra: { fill: 'solid', dash: 'dashed' } },
	{ nodeId: 'question-settled', text: 'QUESTION — ANSWERED or DEFERRED', color: 'light-green', extra: { fill: 'solid', dash: 'solid' } },
	{ nodeId: 'status-exists', text: 'STORY BORDER: EXISTS', color: 'green', extra: { dash: 'solid' } },
	{ nodeId: 'status-gap', text: 'STORY BORDER: GAP', color: 'red', extra: { dash: 'solid' } },
	{ nodeId: 'status-unverified', text: 'STORY BORDER: UNVERIFIED', color: 'violet', extra: { dash: 'solid' } },
]

// Shared activity rules are context, not proof that each story exists.
export const boardPageId = (releaseId) => (releaseId ? `page:jm-board-${releaseId}` : 'page:jm-board-all')

export function buildJourneyBoard(model, { release = null, room = null, progress = null } = {}) {
	let right = X0
	const groups = (model.steps ?? []).map((step) => {
		const stories = (step.stories ?? []).map((story, j) => normalizeStory(step, story, j))
			.filter((story) => !release || story.release === release.id)
		if (release && !stories.length) return null
		const w = Math.max(300, stories.length * STORY_PITCH - 20)
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
	const stackHeight = (lines, w) => lines.reduce((h, l, k) => h + (k ? QUESTION_GAP : 0) + fitHeight(l, w), 0)

	// Each question needs 2 index slots (card + connector arrow); its bindings need none.
	const questionSlots = groups.reduce((sum, g) => sum + g.stories.reduce((s, story) => s + (story.questions?.length ?? 0) * 2, 0), 0)
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
	const activityText = (step) => step.activity ?? step.card
	const storyCardText = (story) => [
		story.card,
		progress && (() => {
			const p = storyProgress(progress, model, story)
			return `Local tasks: ${p.doneTasks ?? 0}/${p.requiredTasks ?? 0} done\n${p.taskIds?.join(', ') || p.diagnostic}`
		})(),
		story.status && ['exists', 'gap', 'unverified'].includes(story.status) ? null : storyStatusLabel(story.status),
		// The evidence symbol is this card's last line, not a separate cell.
		story.evidence ? `Evidence: ${story.evidence}` : 'No story evidence recorded.',
	].filter(Boolean).join('\n')
	const questionsHeight = (story) => (story.questions ?? []).reduce((h, q, k) => h + (k ? QUESTION_GAP : 0) + fitHeight(questionCardText(q), STORY_W), 0)

	const activityH = Math.max(120, ...groups.map((g) => fitHeight(activityText(g.step), g.w)))
	// Flow, then constraints, then stories. Every group shares one flow band and one
	// constraint band sized to the tallest column, exactly like the shared rows this
	// replaces — a short activity's cards just leave blank space, not a row that creeps
	// up under a neighbour's taller stack.
	const flowY = activityH + GAP
	const flowH = Math.max(60, ...groups.map((g) => stackHeight(flowLines(g.step), g.w)))
	const constraintY = flowY + flowH + GAP
	const constraintH = Math.max(60, ...groups.map((g) => stackHeight(constraintLines(g.step), g.w)))
	const storyY = constraintY + constraintH + GAP

	let ly = 0
	for (const entry of BOARD_LEGEND) {
		const h = fitHeight(entry.text, LANE_W)
		box(`legend-${entry.nodeId}`, entry.nodeId, 'board-legend', entry.text, LANE_X, ly, LANE_W, h, entry.color, entry.extra)
		ly += h + 6
	}

	for (const group of groups) {
		const { step, stories, x, w } = group
		box(`card-${step.id}`, step.id, 'activity', activityText(step), x, 0, w, activityH, 'green')

		let fy = flowY
		flowLines(step).forEach((line, k) => {
			const h = fitHeight(line, w)
			box(`flow-${step.id}-${k}`, step.id, 'flow', line, x, fy, w, h, 'light-blue', { fill: 'solid' })
			fy += h + QUESTION_GAP
		})

		let cy = constraintY
		constraintLines(step).forEach((line, k) => {
			const h = fitHeight(line, w)
			box(`constraint-${step.id}-${k}`, step.id, 'constraint', line, x, cy, w, h, 'orange', { fill: 'solid' })
			cy += h + QUESTION_GAP
		})

		if (!stories.length) {
			box(`empty-${step.id}`, step.id, 'empty-stories', 'No stories recorded.', x, storyY, w, STORY_H, 'grey')
		}
		stories.forEach((story, j) => {
			const sx = x + j * STORY_PITCH + (stories.length === 1 ? (w - STORY_W) / 2 : 0)
			const storyShapeId = `${idp}story-${story.id}`
			put.push({
				...note({ id: storyShapeId, parentId, text: storyCardText(story),
					x: sx + 10, y: storyY, index: ix[n++], color: 'yellow' }),
				meta: { journey: { nodeId: story.id, kind: 'story', ...(progress ? { progress: storyProgress(progress, model, story) } : {}), ...(story.status ? { status: story.status } : {}) } },
			})

			let qy = storyY + STORY_H + QUESTION_GAP
			for (const question of story.questions ?? []) {
				const h = fitHeight(questionCardText(question), STORY_W)
				const questionId = `${idp}question-${story.id}-${question.id}`
				put.push({
					...label({ id: questionId, parentId, text: questionCardText(question), x: sx, y: qy, w: STORY_W, h,
						index: ix[n++], color: 'light-green', fill: 'solid', dash: question.status === 'open' ? 'dashed' : 'solid',
						size: 's', align: 'start', verticalAlign: 'start' }),
					// The question id binds to its story-map twin; the story id lets a layout
					// check find the card a question hangs under.
					meta: { journey: { nodeId: question.id, kind: 'question', story: story.id } },
				})
				const linkId = `${idp}qlink-${story.id}-${question.id}`
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

	const boardBottom = storyY + Math.max(STORY_H, ...groups.flatMap((g) => g.stories.map((s) =>
		STORY_H + (questionsHeight(s) ? QUESTION_GAP + questionsHeight(s) : 0))))

	const s = model.status ?? {}
	const statusText = [
		`STATUS — as of ${s.as_of ?? 'unknown date'}`,
		s.unproven && `Unproven: ${s.unproven}`,
		s.unmerged && `Unmerged: ${s.unmerged}`,
		s.undeployed && `Undeployed: ${s.undeployed}`,
		s.irreversible && `Irreversible: ${s.irreversible}`,
	].filter(Boolean).join('\n')
	const statusW = Math.max(600, right - GROUP_GAP - X0)
	box('status', 'status', 'status', statusText, X0, boardBottom + 100, statusW, fitHeight(statusText, statusW), 'red')

	const title = release ? `${release.name} — stories, flow & constraints` : 'Journey board'
	put.unshift(page({ id: parentId, name: title, index: release ? `a${5 + (model.releases ?? []).findIndex((r) => r.id === release.id)}` : 'a2' }))
	if (release) {
		const stories = groups.flatMap((g) => g.stories)
		const text = `${release.name}\n${release.goal ?? ''}\n\n${progress ? releaseProgressText(progress, model, release.id) : `${stories.filter((s) => s.status === 'exists').length}/${stories.length} stories exist`}\n← back to the story map`
		const h = fitHeight(text, statusW)
		box('release', release.id, 'release-label', text, X0, -h - GAP, statusW, h, 'blue',
			{ url: room ? pageLink(room, STORY_PAGE_ID) : '' })
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
