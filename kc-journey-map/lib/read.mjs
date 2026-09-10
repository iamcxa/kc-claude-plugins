// Reads a rendered room back and reports what a person changed on the canvas.
//
// Projections share activity and story identities but give positions different meanings.
// Changed wording is compared across projections; competing edits are reported as a
// conflict and that field is not applied.
//
// What round-trips is what a workshop actually changes — the wording of a card, the order
// of the columns, the priority of the stories under an activity. System/constraint lanes have a
// lossy inverse: a constraint is stored as a rule id and drawn as that rule's text, so
// canvas text cannot be mapped back to an id without guessing. Those are never applied.

const API = process.env.JOURNEY_API ?? `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`

import { readFileSync, writeFileSync } from 'node:fs'
import { parse, parseDocument } from 'yaml'

const STORY_PAGE = 'page:page'
const BOARD_PREFIX = 'page:jm-board-'
const isBoard = (parentId) => String(parentId).startsWith(BOARD_PREFIX)
const pageName = (parentId) =>
	parentId === STORY_PAGE ? 'storymap' : isBoard(parentId) ? `board:${String(parentId).slice(BOARD_PREFIX.length)}` : parentId === 'page:jm-funcmap' ? 'funcmap' : parentId
const NOTE_W = 200

const plain = (rich) =>
	(rich?.content ?? [])
		.map((p) => (p.content ?? []).map((t) => t.text ?? '').join(''))
		.join('\n')
		.trim()

const stripNumber = (text) => text.replace(/^\d+\.\s*/, '')

export async function readRoom({ room, api = API }) {
	const doc = await fetch(`${api}/doc?room=${room}`).then((r) => r.json())
	return (doc.snapshot?.documents ?? []).map((d) => d.state).filter((r) => r.typeName === 'shape')
}

const byKind = (shapes, kind) => shapes.filter((s) => s.meta?.journey?.kind === kind)

// A node id appearing twice means a card was duplicated. tldraw copies meta verbatim, so
// the copy is indistinguishable from its original and neither is trusted.
function duplicatesOf(shapes) {
	const seen = new Map()
	for (const s of shapes) seen.set(s.meta.journey.nodeId, (seen.get(s.meta.journey.nodeId) ?? 0) + 1)
	return [...seen.entries()].filter(([, n]) => n > 1).map(([id]) => id)
}

const indexByNode = (shapes, dupes) =>
	new Map(shapes.filter((s) => !dupes.includes(s.meta.journey.nodeId)).map((s) => [s.meta.journey.nodeId, s]))

const orderOf = (map) =>
	[...map.entries()].sort((a, b) => a[1].x - b[1].x).map(([id]) => id)

// Which column a shape sits under, measured as the share of its own width that overlaps
// each anchor. A card straddling two columns is reported rather than assigned.
function placeUnderColumn(shape, anchors) {
	const scored = anchors
		.map(({ nodeId, x, w = NOTE_W }) => ({
			nodeId,
			frac: Math.max(0, Math.min(shape.x + NOTE_W, x + w) - Math.max(shape.x, x)) / NOTE_W,
		}))
		.filter((s) => s.frac > 0)
		.sort((a, b) => b.frac - a.frac)

	const [best, second] = scored
	if (!best) return { column: null }
	if (best.frac >= 0.75 && (second?.frac ?? 0) < 0.25) return { column: best.nodeId }
	return { column: null, candidates: scored.map((s) => ({ step: s.nodeId, overlap: Number(s.frac.toFixed(2)) })) }
}

export function diffAgainstModel(shapes, model) {
	const steps = model.steps ?? []
	const modelOrder = steps.map((s) => s.id)

	// A step in two releases appears on both of their boards. That is not a duplicate, so
	// cards are collected per page and only compared within one.
	const boardPages = [...new Set(shapes.filter((s) => isBoard(s.parentId)).map((s) => s.parentId))]
	const story = shapes.filter((s) => s.parentId === STORY_PAGE)

	const perBoard = boardPages.map((pid) => {
		const page = shapes.filter((s) => s.parentId === pid)
		return { pid, cards: byKind(page, 'step-card'), activities: byKind(page, 'activity'), stories: byKind(page, 'story') }
	})
	const wholeBoard = perBoard.find((b) => b.pid === `${BOARD_PREFIX}all`)
	const cards = wholeBoard ? [...wholeBoard.cards, ...wholeBoard.activities] : []
	const activities = byKind(story, 'activity')
	const stories = byKind(story, 'story')
	const duplicated = [...new Set([
		...perBoard.flatMap((b) => [...duplicatesOf([...b.cards, ...b.activities]), ...duplicatesOf(b.stories)]),
		...duplicatesOf(activities), ...duplicatesOf(stories),
	])]
	const cardBy = indexByNode(cards, duplicated)
	const actBy = indexByNode(activities, duplicated)
	const storyBy = indexByNode(stories, duplicated)

	// ── wording ──────────────────────────────────────────────────────────────────
	// Compare changed observations with the file, so an untouched projection does not
	// veto an edit elsewhere. Distinct edits of the same field are conflicts. A duplicate
	// within any one page makes that entity ambiguous across all projections.
	const reworded = []
	const rewordConflict = []
	const observations = (records, id) => records.filter((s) => s.meta.journey.nodeId === id)
	const resolveWording = (id, field, was, records, step = null) => {
		if (duplicated.includes(id)) return
		const changed = records.map((s) => ({
			page: pageName(s.parentId),
			now: s.meta.journey.kind === 'step-card' ? stripNumber(plain(s.props?.richText)) : plain(s.props?.richText),
		})).filter((s) => s.now && s.now !== was)
		const words = [...new Set(changed.map((s) => s.now))]
		if (words.length > 1) {
			rewordConflict.push({ id, field,
				board: [...new Set(changed.filter((s) => s.page.startsWith('board:')).map((s) => s.now))].join(' | ') || null,
				storymap: changed.find((s) => s.page === 'storymap')?.now ?? null,
			})
		} else if (words.length) {
			reworded.push({ id, field, page: changed[0].page, ...(step ? { step } : {}), was, now: words[0] })
		}
	}
	const legacyCards = perBoard.flatMap((b) => b.cards)
	const allActivities = [...activities, ...perBoard.flatMap((b) => b.activities)]
	const allStories = [...stories, ...perBoard.flatMap((b) => b.stories)]
	for (const step of steps) {
		const legacy = observations(legacyCards, step.id)
		const activity = observations(allActivities, step.id)
		if (step.activity != null) {
			resolveWording(step.id, 'card', step.card, legacy)
			resolveWording(step.id, 'activity', step.activity, activity)
		} else resolveWording(step.id, 'card', step.card, [...legacy, ...activity])
		;(step.stories ?? []).forEach((s, j) => {
			const id = typeof s === 'string' ? `${step.id}-${j}` : (s.id ?? `${step.id}-${j}`)
			resolveWording(id, 'story', typeof s === 'string' ? s : s.card, observations(allStories, id), step.id)
		})
	}

	// ── column order ─────────────────────────────────────────────────────────────
	// Column order only round-trips from a whole-journey board: a release board shows a
	// subset, so its left-to-right order says nothing about the steps it does not draw.
	const boardOrder = orderOf(cardBy)
	const storyOrder = orderOf(actBy)
	const boardMoved = boardOrder.length && boardOrder.join() !== modelOrder.filter((id) => cardBy.has(id)).join()
	const storyMoved = storyOrder.length && storyOrder.join() !== modelOrder.filter((id) => actBy.has(id)).join()

	let reordered = null
	let reorderConflict = null
	if (boardMoved && storyMoved && boardOrder.join() !== storyOrder.join())
		reorderConflict = { board: boardOrder, storymap: storyOrder }
	else if (boardMoved) reordered = boardOrder
	else if (storyMoved) reordered = storyOrder

	// ── release membership ───────────────────────────────────────────────────────
	// Dragging a story across a release line is the planning gesture — it says this
	// belongs in a later release, or has been pulled into the first one. The lines are on
	// the canvas, so which band a story landed in is read from its y against them.
	const lines = byKind(story, 'release-line').sort((a, b) => a.y - b.y)
	const declaredReleases = (model.releases ?? []).map((r) => r.id)
	const bandOf = (shape) => {
		const crossed = lines.filter((l) => l.y < shape.y).length
		return declaredReleases[crossed] ?? null
	}

	const storyMeta = new Map()
	for (const step of steps) {
		;(step.stories ?? []).forEach((s, j) => {
			const id = typeof s === 'string' ? `${step.id}-${j}` : (s.id ?? `${step.id}-${j}`)
			storyMeta.set(id, { step: step.id, release: typeof s === 'string' ? null : (s.release ?? null) })
		})
	}

	const releaseMoved = []
	if (lines.length) {
		for (const [id, meta] of storyMeta) {
			const shape = storyBy.get(id)
			if (!shape) continue
			const now = bandOf(shape)
			if (now !== meta.release) releaseMoved.push({ id, step: meta.step, was: meta.release, now })
		}
	}

	// ── story priority ───────────────────────────────────────────────────────────
	// Priority runs top to bottom within a band, so only stories sharing a band compare.
	const storiesReordered = []
	for (const step of steps) {
		const inStep = [...storyMeta.entries()].filter(([, m]) => m.step === step.id).map(([id]) => id)
		const groups = new Map()
		for (const id of inStep) {
			if (!storyBy.has(id)) continue
			const band = lines.length ? bandOf(storyBy.get(id)) : storyMeta.get(id).release
            const key = band ?? 'unassigned'
			groups.set(key, [...(groups.get(key) ?? []), id])
		}
		for (const [release, present] of groups) {
			if (present.length < 2) continue
			const onCanvas = [...present].sort((a, b) => storyBy.get(a).y - storyBy.get(b).y)
			if (onCanvas.join() !== present.join())
				storiesReordered.push({ step: step.id, release, was: present, now: onCanvas })
		}
	}

	// ── cards nobody claimed ─────────────────────────────────────────────────────
	const boardAnchors = new Map(perBoard.map((b) => [b.pid, [...indexByNode([...b.cards, ...b.activities], duplicated).entries()]
		.map(([nodeId, s]) => ({ nodeId, x: s.x, w: s.props?.w ?? NOTE_W }))]))
	const storyAnchors = [...actBy.entries()].map(([nodeId, s]) => ({ nodeId, x: s.x }))

	const unclaimed = shapes
		.filter((s) => !s.meta?.journey && (s.type === 'note' || s.type === 'geo'))
		.map((s) => {
			// A page this reader does not model still names itself, so a card added on the
			// function map is not reported as if it were on the board.
			const page = pageName(s.parentId)
			const anchors = page === 'storymap' ? storyAnchors : page.startsWith('board:') ? (boardAnchors.get(s.parentId) ?? []) : []
			const placed = anchors.length ? placeUnderColumn(s, anchors) : { column: null }
			return { id: s.id, text: plain(s.props?.richText), page, ...placed }
		})
		.filter((s) => s.text)

	const presentSteps = new Set([...legacyCards, ...allActivities].map((s) => s.meta.journey.nodeId))
	const missing = modelOrder.filter((id) => !presentSteps.has(id) && !duplicated.includes(id))

	return { reordered, reorderConflict, reworded, rewordConflict, releaseMoved, storiesReordered, duplicated, unclaimed, missing }
}

// `lineWidth: 0` and `flowCollectionPadding: false` keep the writer from reflowing lines it
// did not change. Without them a one-card reorder rewrites every wrapped string in the
// file, and the diff — the reason the journey lives in git at all — stops being readable.
const WRITE_OPTS = { lineWidth: 0, flowCollectionPadding: false }

const findStep = (steps, id) => steps.items.find((item) => item.get('id') === id)

export function applyDiff(path, diff, outPath = path) {
	const doc = parseDocument(readFileSync(path, 'utf8'))
	const steps = doc.get('steps')
	const applied = []
	const skipped = []

	for (const { id, field, step, was, now } of diff.reworded) {
		if (field === 'story') {
			const node = findStep(steps, step)
			const list = node?.get('stories')
			const item = list?.items.find((s, j) => (s.get?.('id') ?? `${step}-${j}`) === id)
			if (item && (item.get ? item.get('card') : String(item)) !== was) {
				skipped.push(`${id} wording changed in the file — read the canvas again`)
				continue
			}
			if (!item) continue
			if (item.set) item.set('card', now)
			else list.items[list.items.indexOf(item)] = doc.createNode(now)
			applied.push(`reworded story ${id}`)
			continue
		}
		const node = findStep(steps, id)
		if (!node) continue
		if (node.get(field) !== was) {
			skipped.push(`${id}.${field} wording changed in the file — read the canvas again`)
			continue
		}
		node.set(field, now)
		applied.push(`reworded ${id}.${field}`)
	}

	// A story that changed release is rewritten in place; its position inside the band is
	// a separate report and applies on top.
	for (const { id, step, now } of diff.releaseMoved) {
		const node = findStep(steps, step)
		const item = node?.get('stories')?.items.find((s) => s.get && s.get('id') === id)
		if (!item) {
			skipped.push(`${id} changed release but is written as a bare string — give it an id first`)
			continue
		}
		if (now) item.set('release', now)
		else item.delete('release')
		applied.push(`${id} moved to ${now ?? 'unassigned'}`)
	}

	for (const { step, now } of diff.storiesReordered) {
		const node = findStep(steps, step)
		const list = node?.get('stories')
		if (!list) continue
		const key = (s, j) => {
			const explicit = s.get ? s.get('id') : null
			return explicit ?? `${step}-${j}`
		}
		const rank = new Map(now.map((id, i) => [id, i]))
		const withKeys = list.items.map((s, j) => ({ s, k: key(s, j) }))
		withKeys.sort((a, b) => (rank.get(a.k) ?? 1e9) - (rank.get(b.k) ?? 1e9))
		list.items = withKeys.map((w) => w.s)
		applied.push(`reprioritised stories under ${step}`)
	}

	if (diff.rewordConflict.length)
		skipped.push(`${diff.rewordConflict.length} wording conflict(s) across projections — resolve on the canvas`)

	if (diff.reorderConflict) skipped.push('reorder refused — the two pages are in different orders')
	else if (diff.reordered && diff.duplicated.length)
		skipped.push(`reorder refused — ${diff.duplicated.join(', ')} appear more than once on the canvas`)
	else if (diff.reordered) {
		const index = new Map(diff.reordered.map((id, i) => [id, i]))
		steps.items.sort((a, b) => (index.get(a.get('id')) ?? 1e9) - (index.get(b.get('id')) ?? 1e9))
		applied.push(`reordered to ${diff.reordered.join(' -> ')}`)
	}

	// A save-as is written even when nothing applied: a caller who asked for that file
	// should end up with it.
	if (applied.length || outPath !== path) writeFileSync(outPath, doc.toString(WRITE_OPTS))
	return { applied, skipped, wrote: applied.length || outPath !== path ? outPath : null }
}

export const loadModel = (path) => parse(readFileSync(path, 'utf8'))
