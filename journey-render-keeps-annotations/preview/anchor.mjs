// Disposable ideation prototype of the proposed anchor rule; not repository code.
export const ANCHOR_KINDS = new Set(['story', 'activity', 'question', 'answer'])

const box = (s) => {
	const p = s.props ?? {}
	if (s.type === 'note') { const k = p.scale ?? 1; return [s.x, s.y, s.x + 200 * k, s.y + (200 + (p.growY ?? 0)) * k] }
	if (typeof p.w === 'number' && typeof p.h === 'number') return [s.x, s.y, s.x + p.w, s.y + p.h]
	return null
}
const area = (a, b) => Math.max(0, Math.min(a[2], b[2]) - Math.max(a[0], b[0])) * Math.max(0, Math.min(a[3], b[3]) - Math.max(a[1], b[1]))

export function carryAnnotations(currentRecords, put, remove) {
	const shapes = currentRecords.filter((r) => r.typeName === 'shape')
	const putById = new Map(put.map((r) => [r.id, r]))
	const gone = new Set(remove)
	const cards = shapes.filter((r) => ANCHOR_KINDS.has(r.meta?.journey?.kind) && String(r.parentId).startsWith('page:') && (putById.has(r.id) || gone.has(r.id)))
	const moved = [], stranded = []
	for (const a of shapes) {
		if (a.meta?.journey || !String(a.parentId).startsWith('page:') || putById.has(a.id) || gone.has(a.id)) continue
		const ab = box(a)
		if (!ab) continue
		const touching = cards.filter((c) => c.parentId === a.parentId && box(c) && area(ab, box(c)) > 0)
		if (!touching.length) continue
		const deltas = touching.map((c) => {
			if (gone.has(c.id)) return null
			const n = putById.get(c.id)
			return [n.x - c.x, n.y - c.y]
		})
		const cardIds = touching.map((c) => c.id)
		if (deltas.some((d) => d === null)) { stranded.push({ id: a.id, reason: 'card-removed', cardIds }); continue }
		const [dx, dy] = deltas[0]
		if (deltas.some(([x, y]) => x !== dx || y !== dy)) { stranded.push({ id: a.id, reason: 'cards-disagree', cardIds }); continue }
		if (dx || dy) moved.push({ id: a.id, cardIds, dx, dy, record: { ...a, x: a.x + dx, y: a.y + dy } })
	}
	return { moved, stranded }
}
