// Reads a rendered room back and reports what a person changed on the canvas.
//
// It deliberately does not rewrite the whole file. Lane 2 and lane 3 are projections
// with a lossy inverse — a constraint is stored as a rule id and drawn as that rule's
// text, so text read off the canvas cannot be mapped back to an id without guessing.
// What round-trips safely is what a workshop actually changes: the wording of a card and
// the order of the columns. Everything else is reported, never applied — a badge is drawn
// from the model but is not read back off the canvas.

import { readFileSync, writeFileSync } from 'node:fs'
import { parse, parseDocument } from 'yaml'

const plain = (rich) =>
	(rich?.content ?? [])
		.map((p) => (p.content ?? []).map((t) => t.text ?? '').join(''))
		.join('\n')
		.trim()

const stripNumber = (text) => text.replace(/^\d+\.\s*/, '')

export async function readRoom({ room, api = 'http://127.0.0.1:5858' }) {
	const doc = await fetch(`${api}/doc?room=${room}`).then((r) => r.json())
	return (doc.snapshot?.documents ?? []).map((d) => d.state).filter((r) => r.typeName === 'shape')
}

export function diffAgainstModel(shapes, model) {
	const owned = shapes.filter((s) => s.meta?.journey)
	const cards = owned.filter((s) => s.meta.journey.kind === 'step-card')

	const seen = new Map()
	for (const s of cards) seen.set(s.meta.journey.nodeId, (seen.get(s.meta.journey.nodeId) ?? 0) + 1)

	// A duplicated card carries its original's nodeId. There is no honest way to tell the
	// copy from the original, so both are reported rather than one silently winning.
	const duplicated = [...seen.entries()].filter(([, n]) => n > 1).map(([id]) => id)

	const unclaimed = shapes
		.filter((s) => !s.meta?.journey && (s.type === 'note' || s.type === 'geo'))
		.map((s) => ({ id: s.id, text: plain(s.props?.richText), x: Math.round(s.x), y: Math.round(s.y) }))
		.filter((s) => s.text)

	const byNode = new Map(cards.filter((s) => !duplicated.includes(s.meta.journey.nodeId)).map((s) => [s.meta.journey.nodeId, s]))

	const order = [...byNode.entries()].sort((a, b) => a[1].x - b[1].x).map(([id]) => id)
	const modelOrder = (model.steps ?? []).map((s) => s.id)

	const reworded = (model.steps ?? [])
		.map((step) => {
			const shape = byNode.get(step.id)
			if (!shape) return null
			const onCanvas = stripNumber(plain(shape.props?.richText))
			return onCanvas && onCanvas !== step.card ? { id: step.id, was: step.card, now: onCanvas } : null
		})
		.filter(Boolean)

	const missing = modelOrder.filter((id) => !byNode.has(id) && !duplicated.includes(id))

	return {
		reordered: order.join(',') !== modelOrder.filter((id) => byNode.has(id)).join(',') ? order : null,
		reworded,
		duplicated,
		unclaimed,
		missing,
	}
}

// Applies only the safe subset, and preserves comments and field order in the file.
//
// `lineWidth: 0` and `flowCollectionPadding: false` keep the writer from reflowing lines
// it did not change. Without them a one-card reorder rewrites every wrapped string in the
// file, and the diff — the reason the journey lives in git at all — stops being readable.
const WRITE_OPTS = { lineWidth: 0, flowCollectionPadding: false }

export function applyDiff(path, diff) {
	const doc = parseDocument(readFileSync(path, 'utf8'))
	const steps = doc.get('steps')
	const applied = []
	const skipped = []

	for (const { id, now } of diff.reworded) {
		for (const item of steps.items) {
			if (item.get('id') === id) {
				item.set('card', now)
				applied.push(`reworded ${id}`)
			}
		}
	}

	// A duplicated card is missing from `reordered`, so applying the order would silently
	// move the step it belongs to. Ambiguous input is refused whole, not applied in part.
	if (diff.reordered && diff.duplicated.length) {
		skipped.push(`reorder refused — ${diff.duplicated.join(', ')} appear more than once on the canvas`)
	} else if (diff.reordered) {
		const index = new Map(diff.reordered.map((id, i) => [id, i]))
		steps.items.sort((a, b) => (index.get(a.get('id')) ?? 1e9) - (index.get(b.get('id')) ?? 1e9))
		applied.push(`reordered to ${diff.reordered.join(' -> ')}`)
	}

	if (applied.length) writeFileSync(path, doc.toString(WRITE_OPTS))
	return { applied, skipped }
}

export const loadModel = (path) => parse(readFileSync(path, 'utf8'))
