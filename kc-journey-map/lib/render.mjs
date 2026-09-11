// Projects a journey file onto a tldraw room.
//
// The file in the repository is the source of truth; the room is a rendering of it.
// Nothing here reads the room back — that is `read.mjs`. Positions are computed from
// the model's order, never stored in the model, so a journey file stays diffable.

const API = process.env.JOURNEY_API ?? `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`

import { readFileSync } from 'node:fs'
import { parse } from 'yaml'
import { fitHeight, indexes, label, note, page, pageLink, releaseLine, withStoryStatus } from './records.mjs'
import { STORY_PAGE_ID, buildStoryMap } from './storymap.mjs'
import { buildFunctionMap } from './funcmap.mjs'
import { normalizeStory, storyStatusLabel } from './model.mjs'

const STORY_PITCH = 240
const STORY_W = 220
const GROUP_GAP = 60
const X0 = 320
const LANE_X = 20
const LANE_W = 270
const GAP = 40
const tag = (nodeId, kind) => ({ journey: { nodeId, kind } })

// Release stories are the units under discussion. Activity-level system/rule data spans
// their group once; it is shared context, not evidence that each story is implemented.
export const boardPageId = (releaseId) => (releaseId ? `page:jm-board-${releaseId}` : 'page:jm-board-all')

export function buildJourneyBoard(model, { release = null, room = null } = {}) {
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
	const ix = indexes(20 + groups.length * 4 + groups.reduce((sum, g) => sum + g.stories.length * 2, 0))
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
		story.status && ['exists', 'gap', 'unverified'].includes(story.status) ? null : storyStatusLabel(story.status),
		story.evidence ? `Evidence: ${story.evidence}` : 'No story evidence recorded.',
		story.question && `? ${story.question}`,
	].filter(Boolean).join('\n')
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
	const systemY = proofY + proofH + GAP
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
			put.push({
				...note({ id: `${idp}story-${story.id}`, parentId, text: story.card,
					x: sx + 10, y: storyY, index: ix[n++], color: 'yellow' }),
				meta: { journey: { nodeId: story.id, kind: 'story', ...(story.status ? { status: story.status } : {}) } },
			})
			box(`proof-${story.id}`, story.id, 'story-proof', proofText(story), sx, proofY, STORY_W, proofH,
				'grey')
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
		const text = `${release.name}\n${release.goal ?? ''}\n\n${stories.filter((s) => s.status === 'exists').length}/${stories.length} stories exist\n← back to the story map`
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
	return withStoryStatus(put)
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

// A board per release when the file has releases; one whole-journey board when it does
// not, so a map drawn before anyone has sliced it still renders.
const journeyBoardPages = (model, room) => {
	const releases = model.releases ?? []
	return releases.length
		? releases.flatMap((release) => buildJourneyBoard(model, { release, room }))
		: buildJourneyBoard(model, { room })
}

// Which projections a render draws is a choice made per call, never a property of the
// file — the same journey renders one way for a stand-up and another for a release review.
export const PROJECTIONS = {
	'story-map': (model, room) => buildStoryMap(model, room),
	'journey-board': journeyBoardPages,
	'function-map': (model) => buildFunctionMap(model),
}
export const PROJECTION_KEYS = Object.keys(PROJECTIONS)
export const DEFAULT_PROJECTIONS = ['story-map']

export function buildAllPages(model, room = null, selection = DEFAULT_PROJECTIONS) {
	const chosen = selection?.length ? selection : DEFAULT_PROJECTIONS
	const unknown = chosen.filter((key) => !PROJECTIONS[key])
	if (unknown.length) throw new Error(`unknown projection(s): ${unknown.join(', ')}`)
	return PROJECTION_KEYS.filter((key) => chosen.includes(key)).flatMap((key) => PROJECTIONS[key](model, room))
}

// Untagged shapes belong to the user and must survive redraw.
export async function renderToRoom({ path, room, selection, api = API }) {
	const model = loadJourney(path)
	const roomId = room ?? model.journey

	const put = buildAllPages(model, roomId, selection)
	const wanted = new Set(put.map((r) => r.id))

	const current = await fetch(`${api}/doc?room=${roomId}`).then((r) => r.json())
	// Preserve manually created pages.
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
