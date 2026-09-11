// Projects journey YAML onto a persisted story-map canvas.
const API = process.env.JOURNEY_API ?? `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`
import { readFileSync } from 'node:fs'
import { parse } from 'yaml'
import { buildStoryMap } from './storymap.mjs'

export function loadJourney(path) {
	return parse(readFileSync(path, 'utf8'))
}

// Report which activities each declared release covers.
export function releaseCoverage(model) {
	const steps = model.steps ?? []
	return (model.releases ?? []).map((r) => {
		const covered = steps.filter((s) => (s.stories ?? []).some((x) => x?.release === r.id)).map((s) => s.id)
		return { release: r.id, covered: covered.length, of: steps.length, missing: steps.filter((s) => !covered.includes(s.id)).map((s) => s.id) }
	})
}

// Render is a reconcile, not an append: shapes this renderer owns that the model no
// longer produces are removed. Shapes a person drew by hand carry no `meta.journey`
// and are never touched — the room is where a workshop happens, not only where a file
// is displayed.
export async function renderToRoom({ path, room, api = API }) {
	const model = loadJourney(path)
	const roomId = room ?? model.journey

	const put = buildStoryMap(model)
	const wanted = new Set(put.map((r) => r.id))

	const current = await fetch(`${api}/doc?room=${roomId}`).then((r) => r.json())
	// Only shapes are reconciled. Deleting a page would take a person's own pages with it.
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
