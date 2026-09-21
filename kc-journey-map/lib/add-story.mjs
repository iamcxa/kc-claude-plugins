// Add one deferred capability to an existing journey. Named in conversation and not
// built, it gets a gap story under its step — not a redraw of the file around it.
import { readFileSync, writeFileSync } from 'node:fs'
import { parseDocument } from 'yaml'
import { WRITE_OPTS, findStep } from './read.mjs'

const allStoryIds = (steps) =>
	new Set(steps.items.flatMap((step) => (step.get('stories')?.items ?? []).map((s) => s.get?.('id')).filter(Boolean)))

function matchSiblingStyle(node, list) {
	const last = list.items.at(-1)
	node.flow = last ? Boolean(last.flow) : true
	// No sibling to copy (a step's first story): fall back to this repo's own
	// convention — every story card in journey.example.yaml is double-quoted.
	node.get('card', true).type = last?.get?.('card', true)?.type ?? 'QUOTE_DOUBLE'
}

export function addStory(path, { stepId, id, card }, outPath = path) {
	if (!stepId) throw new Error('addStory needs stepId')
	if (!id) throw new Error('addStory needs id')
	if (!card) throw new Error('addStory needs card — the wording the person used, not a rewrite')

	const doc = parseDocument(readFileSync(path, 'utf8'))
	const steps = doc.get('steps')
	if (!steps) throw new Error(`${path} has no steps`)

	const step = findStep(steps, stepId)
	if (!step) throw new Error(`step "${stepId}" not found in ${path}`)

	if (allStoryIds(steps).has(id)) throw new Error(`story id "${id}" already exists in ${path}`)

	let list = step.get('stories')
	if (!list) {
		list = doc.createNode([])
		step.set('stories', list)
	}

	const story = doc.createNode({ id, status: 'gap', card })
	matchSiblingStyle(story, list)
	list.items.push(story)

	writeFileSync(outPath, doc.toString(WRITE_OPTS))
	return { wrote: outPath, id, stepId }
}
