// Constraint text has no safe inverse to rule IDs; readback never guesses.

const API = process.env.JOURNEY_API ?? `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`

import { readFileSync, writeFileSync } from 'node:fs'
import { parse, parseDocument } from 'yaml'
import { QUESTION_GAP, QUESTION_PITCH } from './render.mjs'
import { isQuestionAnswered, iterStories } from './model.mjs'

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

// tldraw duplicates metadata verbatim, so duplicated node IDs cannot be trusted.
function duplicatesOf(shapes) {
	const seen = new Map()
	for (const s of shapes) seen.set(s.meta.journey.nodeId, (seen.get(s.meta.journey.nodeId) ?? 0) + 1)
	return [...seen.entries()].filter(([, n]) => n > 1).map(([id]) => id)
}

const indexByNode = (shapes, dupes) =>
	new Map(shapes.filter((s) => !dupes.includes(s.meta.journey.nodeId)).map((s) => [s.meta.journey.nodeId, s]))

const orderOf = (map) =>
	[...map.entries()].sort((a, b) => a[1].x - b[1].x).map(([id]) => id)

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

// Native tldraw "+" lands a new note exactly on the grid render.mjs itself draws: a new
// question keeps its source's x (added downward) and a new answer keeps its source's y
// (added sideways). QUESTION_GAP is that render's own gutter between one story's answer
// slot and its neighbour's question column — the two can sit as little as 20px apart, so
// the same gutter is also the tolerance a hand-placed note must land inside to read
// unambiguously as one or the other, never both.
const PLACEMENT_TOL = QUESTION_GAP

// Read a board page's hand-added notes as new questions/answers, and its generated
// question/answer notes for edits or deletions — against the model's own declared
// questions, not the page's own layout math, so a dragged story or question still reads
// correctly relative to wherever it actually sits.
function questionsAndAnswers(shapes, perBoard, duplicated, model) {
	const modelStories = new Map(iterStories(model).map((s) => [s.id, s]))
	const questionsAdded = [], questionsReworded = [], questionsDeleted = []
	const answersAdded = [], answersReworded = [], answersDeleted = []
	const claimedIds = new Set()

	for (const b of perBoard) {
		const pg = pageName(b.pid)
		const storiesOnPage = indexByNode(b.stories, duplicated)
		const questionsOnPage = indexByNode(b.questions, duplicated)
		const answersOnPage = indexByNode(b.answers, duplicated)

		for (const [storyId] of storiesOnPage) {
			const story = modelStories.get(storyId)
			if (!story) continue
			for (const q of story.questions ?? []) {
				const qShape = questionsOnPage.get(q.id)
				if (!qShape) {
					questionsDeleted.push({ story: storyId, step: story.step.id, id: q.id, was: q.ask, page: pg })
					continue
				}
				const nowAsk = plain(qShape.props?.richText)
				if (nowAsk && nowAsk !== q.ask)
					questionsReworded.push({ story: storyId, step: story.step.id, id: q.id, was: q.ask, now: nowAsk, page: pg })

				if (!isQuestionAnswered(q)) continue
				const aShape = answersOnPage.get(q.id)
				if (!aShape) {
					answersDeleted.push({ story: storyId, step: story.step.id, question: q.id, was: { answer: q.answer, doc: q.doc }, page: pg })
					continue
				}
				const nowAnswer = plain(aShape.props?.richText) || undefined
				const nowDoc = aShape.props?.url || undefined
				if (nowAnswer !== q.answer || nowDoc !== q.doc)
					answersReworded.push({ story: storyId, step: story.step.id, question: q.id,
						was: { answer: q.answer, doc: q.doc }, now: { answer: nowAnswer, doc: nowDoc }, page: pg })
			}
		}

		// A story's own x is already its questions' x (records.mjs draws both at the same
		// column offset); an answer's slot is its question's x shifted one pitch to the right.
		const storyAnchors = [...storiesOnPage.entries()].map(([nodeId, s]) => ({ nodeId, x: s.x, y: s.y }))
		const questionAnchors = [...questionsOnPage.entries()].map(([nodeId, s]) => ({
			nodeId, story: s.meta.journey.story, x: s.x, y: s.y, answered: answersOnPage.has(nodeId),
		}))
		const untagged = shapes
			.filter((s) => s.parentId === b.pid && !s.meta?.journey && (s.type === 'note' || s.type === 'geo'))
			.sort((a, c) => a.y - c.y || a.x - c.x)
		const usedIds = new Map()

		for (const shape of untagged) {
			const text = plain(shape.props?.richText)
			const url = shape.props?.url || ''
			if (!text && !url) continue

			const columnHits = storyAnchors
				.filter((s) => shape.y > s.y)
				.map((s) => ({ kind: 'question', story: s.nodeId, d: Math.abs(shape.x - s.x) }))
			const rowHits = questionAnchors
				.filter((q) => !q.answered)
				.map((q) => ({ kind: 'answer', question: q.nodeId, story: q.story,
					d: Math.max(Math.abs(shape.x - (q.x + QUESTION_PITCH)), Math.abs(shape.y - q.y)) }))
			const passing = [...columnHits, ...rowHits].filter((c) => c.d <= PLACEMENT_TOL).sort((a, c) => a.d - c.d)
			if (passing.length !== 1) continue // none, or a tie inside the gutter — leave for the generic unclaimed report

			const hit = passing[0]
			if (hit.kind === 'answer') {
				answersAdded.push({ story: hit.story, step: modelStories.get(hit.story)?.step.id, question: hit.question,
					...(text ? { answer: text } : {}), ...(url ? { doc: url } : {}), page: pg, shapeId: shape.id })
				claimedIds.add(shape.id)
				continue
			}
			if (!text) continue // a link-only note that matched no row cannot become a question
			const storyId = hit.story
			const used = usedIds.get(storyId) ?? new Set(questionAnchors.filter((q) => q.story === storyId).map((q) => q.nodeId))
			let k = 0
			while (used.has(`${storyId}-q${k}`)) k++
			const id = `${storyId}-q${k}`
			used.add(id)
			usedIds.set(storyId, used)
			questionsAdded.push({ story: storyId, step: modelStories.get(storyId)?.step.id, id, ask: text, page: pg, shapeId: shape.id })
			claimedIds.add(shape.id)
			questionAnchors.push({ nodeId: id, story: storyId, x: shape.x, y: shape.y, answered: false })
		}
	}
	return { questionsAdded, questionsReworded, questionsDeleted, answersAdded, answersReworded, answersDeleted, claimedIds }
}

export function diffAgainstModel(shapes, model) {
	const steps = model.steps ?? []
	const modelOrder = steps.map((s) => s.id)

	// Activity IDs repeated across release pages are not duplicates.
	const boardPages = [...new Set(shapes.filter((s) => isBoard(s.parentId)).map((s) => s.parentId))]
	const story = shapes.filter((s) => s.parentId === STORY_PAGE)

	const perBoard = boardPages.map((pid) => {
		const page = shapes.filter((s) => s.parentId === pid)
		return { pid, cards: byKind(page, 'step-card'), activities: byKind(page, 'activity'), stories: byKind(page, 'story'),
			questions: byKind(page, 'question'), answers: byKind(page, 'answer') }
	})
	const wholeBoard = perBoard.find((b) => b.pid === `${BOARD_PREFIX}all`)
	const cards = wholeBoard ? [...wholeBoard.cards, ...wholeBoard.activities] : []
	const activities = byKind(story, 'activity')
	const stories = byKind(story, 'story')
	const duplicated = [...new Set([
		...perBoard.flatMap((b) => [...duplicatesOf([...b.cards, ...b.activities]), ...duplicatesOf(b.stories), ...duplicatesOf(b.questions), ...duplicatesOf(b.answers)]),
		...duplicatesOf(activities), ...duplicatesOf(stories),
	])]
	const cardBy = indexByNode(cards, duplicated)
	const actBy = indexByNode(activities, duplicated)
	const storyBy = indexByNode(stories, duplicated)

	// A duplicate on any page makes that entity ambiguous across projections.
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

	// Release pages omit activities, so their column order cannot define whole-journey order.
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

	const boardAnchors = new Map(perBoard.map((b) => [b.pid, [...indexByNode([...b.cards, ...b.activities], duplicated).entries()]
		.map(([nodeId, s]) => ({ nodeId, x: s.x, w: s.props?.w ?? NOTE_W }))]))
	const storyAnchors = [...actBy.entries()].map(([nodeId, s]) => ({ nodeId, x: s.x }))

	const qa = questionsAndAnswers(shapes, perBoard, duplicated, model)

	const unclaimed = shapes
		.filter((s) => !s.meta?.journey && (s.type === 'note' || s.type === 'geo') && !qa.claimedIds.has(s.id))
		.map((s) => {
			const page = pageName(s.parentId)
			const anchors = page === 'storymap' ? storyAnchors : page.startsWith('board:') ? (boardAnchors.get(s.parentId) ?? []) : []
			const placed = anchors.length ? placeUnderColumn(s, anchors) : { column: null }
			return { id: s.id, text: plain(s.props?.richText), page, ...placed }
		})
		.filter((s) => s.text)

	const presentSteps = new Set([...legacyCards, ...allActivities].map((s) => s.meta.journey.nodeId))
	const missing = modelOrder.filter((id) => !presentSteps.has(id) && !duplicated.includes(id))

	return { reordered, reorderConflict, reworded, rewordConflict, releaseMoved, storiesReordered, duplicated, unclaimed, missing,
		questionsAdded: qa.questionsAdded, questionsReworded: qa.questionsReworded, questionsDeleted: qa.questionsDeleted,
		answersAdded: qa.answersAdded, answersReworded: qa.answersReworded, answersDeleted: qa.answersDeleted }
}

// Preserve untouched YAML wrapping when writing individual edits.
export const WRITE_OPTS = { lineWidth: 0, flowCollectionPadding: false }

export const findStep = (steps, id) => steps.items.find((item) => item.get('id') === id)

// A story is found by its explicit id, falling back to the same `${step}-${index}`
// default `normalizeStory` uses — the only way a bare-string story can be located at all.
function findStoryNode(steps, stepId, storyId) {
	const list = findStep(steps, stepId)?.get('stories')
	const j = list?.items.findIndex((s, idx) => ((s.get ? s.get('id') : null) ?? `${stepId}-${idx}`) === storyId)
	return j >= 0 ? list.items[j] : null
}

// A story's questions may be authored three ways: a `questions:` list, the singular
// `question:` sugar, or neither. Every write path converges on a `questions:` list so a
// new question always has somewhere to land, preserving whatever sugar entry already
// existed rather than re-deriving its text.
function ensureQuestionsList(doc, storyNode) {
	const existingList = storyNode.get('questions')
	if (existingList) return existingList
	const sugar = storyNode.has('question') ? storyNode.get('question', true) : null
	if (storyNode.has('question')) storyNode.delete('question')
	const list = doc.createNode(sugar ? [sugar] : [])
	storyNode.set('questions', list)
	return list
}

const questionKey = (item, storyId, j) => (item?.get ? item.get('id') : null) ?? `${storyId}-q${j}`

const findQuestionIndex = (list, storyId, questionId) =>
	list.items.findIndex((item, j) => questionKey(item, storyId, j) === questionId)

// Upgrading a bare-string question to a map is only needed to attach a field a plain
// string cannot hold (answer/doc); rewording its ask alone stays a plain replacement,
// exactly like a bare-string story already does.
function questionAsMap(doc, list, storyId, index) {
	const item = list.items[index]
	if (item?.get) return item
	const upgraded = doc.createNode({ id: questionKey(item, storyId, index), ask: String(item) })
	list.items[index] = upgraded
	return upgraded
}

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

	// Shape ids of hand-added notes whose content is now confirmed written into this file —
	// safe for the caller to remove from the room, and nothing else.
	const absorbed = []

	for (const { story, step, id, ask, page, shapeId } of diff.questionsAdded) {
		const storyNode = findStoryNode(steps, step, story)
		if (!storyNode?.get) {
			skipped.push(`${story} could not take a new question — story is a bare string, give it an id first`)
			continue
		}
		const list = ensureQuestionsList(doc, storyNode)
		list.items.push(doc.createNode({ id, ask }))
		applied.push(`added question ${id} to ${story}`)
		absorbed.push({ shapeId, page })
	}

	for (const { story, step, id, was, now } of diff.questionsReworded) {
		const storyNode = findStoryNode(steps, step, story)
		if (!storyNode?.get) continue
		const list = ensureQuestionsList(doc, storyNode)
		const j = findQuestionIndex(list, story, id)
		if (j < 0) continue
		const item = list.items[j]
		if ((item.get ? item.get('ask') : String(item)) !== was) {
			skipped.push(`${id} wording changed in the file — read the canvas again`)
			continue
		}
		if (item.get) item.set('ask', now)
		else list.items[j] = doc.createNode(now)
		applied.push(`reworded question ${id}`)
	}

	for (const { story, step, question, answer, doc: docUrl, page, shapeId } of diff.answersAdded) {
		const storyNode = findStoryNode(steps, step, story)
		if (!storyNode?.get) {
			skipped.push(`${question} answer could not be attached — story is a bare string, give it an id first`)
			continue
		}
		const list = ensureQuestionsList(doc, storyNode)
		const j = findQuestionIndex(list, story, question)
		if (j < 0) {
			skipped.push(`${question} answer could not be attached — question not found in the file`)
			continue
		}
		const item = questionAsMap(doc, list, story, j)
		if (answer !== undefined) item.set('answer', answer)
		if (docUrl !== undefined) item.set('doc', docUrl)
		applied.push(`answered question ${question}`)
		absorbed.push({ shapeId, page })
	}

	for (const { story, step, question, was, now } of diff.answersReworded) {
		const storyNode = findStoryNode(steps, step, story)
		if (!storyNode?.get) continue
		const list = ensureQuestionsList(doc, storyNode)
		const j = findQuestionIndex(list, story, question)
		if (j < 0) continue
		const item = list.items[j]
		const currentAnswer = item.get ? item.get('answer') : undefined
		const currentDoc = item.get ? item.get('doc') : undefined
		if (currentAnswer !== was.answer || currentDoc !== was.doc) {
			skipped.push(`${question} answer changed in the file — read the canvas again`)
			continue
		}
		const mapped = questionAsMap(doc, list, story, j)
		if (now.answer !== undefined) mapped.set('answer', now.answer)
		else mapped.delete('answer')
		if (now.doc !== undefined) mapped.set('doc', now.doc)
		else mapped.delete('doc')
		applied.push(`reworded answer to ${question}`)
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

	if (applied.length || outPath !== path) writeFileSync(outPath, doc.toString(WRITE_OPTS))
	return { applied, skipped, wrote: applied.length || outPath !== path ? outPath : null, absorbed }
}

export const loadModel = (path) => parse(readFileSync(path, 'utf8'))

// Deletes exactly the given shape ids from the room — the same incremental PATCH
// contract render.mjs:renderToRoom uses, but with nothing to `put`: this only removes
// hand-added notes readback has already absorbed into the file, never redraws anything.
export async function removeAbsorbedNotes({ room, ids, api = API }) {
	if (!ids.length) return { status: 200, removed: 0 }
	const res = await fetch(`${api}/doc?room=${room}`, {
		method: 'PATCH',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ remove: ids }),
	})
	return { status: res.status, removed: ids.length, body: await res.text() }
}
