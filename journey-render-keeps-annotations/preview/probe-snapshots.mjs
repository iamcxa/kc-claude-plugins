// Disposable probe: the proposed anchor rule against the three recorded room snapshots (SNAPSHOT_DIR, outside this repository).
import { readFileSync } from 'node:fs'
const { carryAnnotations } = await import('./anchor.mjs')
const D = process.env.SNAPSHOT_DIR.replace(/\/?$/, '/')
const load = (f) => { const d = JSON.parse(readFileSync(D + f, 'utf8')); return Array.isArray(d) ? d : d.snapshot.documents.map((x) => x.state) }
const before = load('draft-room.json'), stranded = load('draft-before-frame-fix.json'), after = load('draft-after-fix.json')
const gen = (rs) => rs.filter((r) => r.typeName === 'shape' && r.meta?.journey)
const put = gen(stranded), remove = gen(before).filter((r) => !put.some((p) => p.id === r.id)).map((r) => r.id)
const { moved, stranded: st } = carryAnnotations(before, put, remove)
const byId = new Map(after.filter((r) => r.typeName === 'shape').map((r) => [r.id, r]))
const strandedById = new Map(stranded.filter((r) => r.typeName === 'shape').map((r) => [r.id, r]))
const handFixed = [...strandedById.keys()].filter((id) => !strandedById.get(id).meta?.journey && (strandedById.get(id).x !== byId.get(id).x || strandedById.get(id).y !== byId.get(id).y))
console.log('put', put.length, 'remove', remove.length, '| moved', moved.length, 'reported', st.length, '| hand-repaired', handFixed.length)
const movedIds = new Set(moved.map((m) => m.id))
console.log('moved & hand-repaired:', handFixed.filter((i) => movedIds.has(i)).length, '| hand-repaired not moved:', handFixed.filter((i) => !movedIds.has(i)).length, '| moved not hand-repaired:', [...movedIds].filter((i) => !handFixed.includes(i)).length)
const exact = moved.filter((m) => { const a = byId.get(m.id); return a.x === m.record.x && a.y === m.record.y })
console.log('moved to exactly the hand-repaired position:', exact.length, 'of', moved.filter((m) => handFixed.includes(m.id)).length)
console.log('reported', JSON.stringify(st.map((s) => [s.id.slice(-12), s.reason])))
console.log('moved-not-handfixed deltas', moved.filter((m) => !handFixed.includes(m.id)).map((m) => [m.id.slice(-14), m.dx, m.dy]))
console.log('hand-fixed not moved', handFixed.filter((i) => !movedIds.has(i)).map((i) => i.slice(-12)))
// what does the stranded record keep relative to the fixed one for the moved ones
