
const API = process.env.JOURNEY_API ?? `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`

import { readFileSync } from 'node:fs'
import { parse } from 'yaml'
import { DocumentRecordType, TLDOCUMENT_ID } from '@tldraw/tlschema'
import { fitHeight, indexes, label, note, page, pageLink, releaseLine, withStoryStatus, storyProgress, releaseProgressText, connector, connectorBindings, QUESTION_STATUS_COLORS } from './records.mjs'
import { STORY_PAGE_ID, buildStoryMap } from './storymap.mjs'
import { buildFunctionMap } from './funcmap.mjs'
import { normalizeStory, storyStatusLabel, questionCardText } from './model.mjs'

const STORY_PITCH = 240
const STORY_W = 220
const GROUP_GAP = 60
const X0 = 320
const LANE_X = 20
const LANE_W = 270
const GAP = 40
const QUESTION_GAP = 10
const tag = (nodeId, kind) => ({ journey: { nodeId, kind } })

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
	// Each question needs 2 index slots (card + connector arrow); its bindings need none.
	const questionSlots = groups.reduce((sum, g) => sum + g.stories.reduce((s, story) => s + (story.questions?.length ?? 0) * 2, 0), 0)
	const ix = indexes(20 + groups.length * 4 + groups.reduce((sum, g) => sum + g.stories.length * 2, 0) + questionSlots)
	let n = 0
	const box = (slug, nodeId, kind, text, x, y, w, h, color = 'black', extra = {}) => {
		put.push({
			...label({ id: `${idp}${slug}`, parentId, text, x, y, w, h, index: ix[n++],
				color, size: 's', align: 'start', verticalAlign: 'start', ...extra }),
			meta: tag(nodeId, kind),
		})
	}
	const lane = (slug, text, y, h) => box(`lane-${slug}`, `lane-${slug}`, 'lane-label', text, LANE_X, y, LANE_W, h, 'grey')
	const activityText = (step) => step.activity ?? step.card
	const proofText = (story) => [
		progress && (() => {
			const p = storyProgress(progress, model, story)
			return `Local tasks: ${p.doneTasks ?? 0}/${p.requiredTasks ?? 0} done\n${p.taskIds?.join(', ') || p.diagnostic}`
		})(),
		story.status && ['exists', 'gap', 'unverified'].includes(story.status) ? null : storyStatusLabel(story.status),
		story.evidence ? `Evidence: ${story.evidence}` : 'No story evidence recorded.',
	].filter(Boolean).join('\n')
	// A question is its own card, connected to the story card by a native arrow — not
	// text folded into the evidence cell, which stops reading once a story asks six.
	const questionsHeight = (story) => (story.questions ?? []).reduce((h, q, k) => h + (k ? QUESTION_GAP : 0) + fitHeight(questionCardText(q), STORY_W), 0)
	const systemText = (step) => [
		'SHARED ACTIVITY CONTEXT',
		...(step.system?.length ? step.system.map((l) => `• ${l}`) : ['No system flow recorded.']),
		step.cites?.length && `[${step.cites.join(', ')}]`,
		step.note?.trim(),
	].filter(Boolean).join('\n')
	const ruleText = (step) => ['SHARED ACTIVITY CONSTRAINTS',
		...(step.rules?.length ? step.rules.map((id) => `• ${rulesById.get(id) ?? id}`) : ['No constraints recorded.']),
	].join('\n')
	const activityH = Math.max(fitHeight('ACTIVITIES\nshared groups', LANE_W), ...groups.map((g) => fitHeight(activityText(g.step), g.w)))
	const storyY = activityH + GAP
	const proofY = storyY + 200 + 20
	const proofH = Math.max(184, ...groups.flatMap((g) => g.stories.map((s) => fitHeight(proofText(s), STORY_W))))
	const proofBottom = proofY + proofH
	// A story's own open questions may stack taller than every other story's proof box;
	// the system lane must clear the tallest column, not just the shared proof height.
	const systemY = Math.max(proofBottom + GAP, ...groups.flatMap((g) => g.stories.map((s) =>
		questionsHeight(s) ? proofBottom + QUESTION_GAP + questionsHeight(s) + GAP : 0)))
	const systemH = Math.max(180, ...groups.map((g) => fitHeight(systemText(g.step), g.w)))
	const rulesY = systemY + systemH + GAP
	const rulesH = Math.max(160, ...groups.map((g) => fitHeight(ruleText(g.step), g.w)))

	lane('activity', 'ACTIVITIES\nshared groups', 0, activityH)
	lane('journey', 'RELEASE STORIES\nwhat a person can do', storyY, 200)
	lane('evidence', 'STORY EVIDENCE\nevidence and open questions', proofY, proofH)
	lane('system', 'SYSTEM FLOW\nshared by the activity; story mapping not recorded', systemY, systemH)
	lane('constraints', 'CONSTRAINTS\nshared by the activity; story mapping not recorded', rulesY, rulesH)

	for (const { step, stories, x, w } of groups) {
		box(`card-${step.id}`, step.id, 'activity', activityText(step), x, 0, w, activityH, 'green')
		if (!stories.length) {
			box(`empty-${step.id}`, step.id, 'empty-stories', 'No stories recorded.', x, storyY, w, 200, 'grey')
		}
		stories.forEach((story, j) => {
			const sx = x + j * STORY_PITCH + (stories.length === 1 ? (w - STORY_W) / 2 : 0)
			const storyShapeId = `${idp}story-${story.id}`
			put.push({
				...note({ id: storyShapeId, parentId, text: story.card,
					x: sx + 10, y: storyY, index: ix[n++], color: 'yellow' }),
				meta: { journey: { nodeId: story.id, kind: 'story', ...(progress ? { progress: storyProgress(progress, model, story) } : {}), ...(story.status ? { status: story.status } : {}) } },
			})
			box(`proof-${story.id}`, story.id, 'story-proof', proofText(story), sx, proofY, STORY_W, proofH,
				'grey')

			let qy = proofBottom + QUESTION_GAP
			for (const question of story.questions ?? []) {
				const h = fitHeight(questionCardText(question), STORY_W)
				const questionId = `${idp}question-${story.id}-${question.id}`
				put.push({
					...label({ id: questionId, parentId, text: questionCardText(question), x: sx, y: qy, w: STORY_W, h,
						index: ix[n++], color: QUESTION_STATUS_COLORS[question.status] ?? 'grey', size: 's', align: 'start', verticalAlign: 'start' }),
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
		box(`sys-${step.id}`, step.id, 'system', systemText(step), x, systemY, w, systemH)
		box(`rules-${step.id}`, step.id, 'constraints', ruleText(step), x, rulesY, w, rulesH, 'blue')
	}

	const s = model.status ?? {}
	const statusText = [
		`STATUS — as of ${s.as_of ?? 'unknown date'}`,
		s.unproven && `Unproven: ${s.unproven}`,
		s.unmerged && `Unmerged: ${s.unmerged}`,
		s.undeployed && `Undeployed: ${s.undeployed}`,
		s.irreversible && `Irreversible: ${s.irreversible}`,
	].filter(Boolean).join('\n')
	const statusW = Math.max(600, right - GROUP_GAP - X0)
	box('status', 'status', 'status', statusText, X0, rulesY + rulesH + 100, statusW, fitHeight(statusText, statusW), 'red')

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
		const y = rulesY + rulesH + 50
		put.push({
			...releaseLine({ id: `${idp}slice-line`, x: LANE_X, y, w: right - LANE_X, index: ix[n++], parentId }),
			meta: tag(slice.id, 'slice-line'),
		})
		const text = `SLICE\n${slice.outcome}`
		box('slice-label', slice.id, 'slice-label', text, LANE_X, y + 50, LANE_W, fitHeight(text, LANE_W))
	}
	return withStoryStatus(put, progress)
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
