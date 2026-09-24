// Add one deferred capability to an existing journey. Named in conversation and not
// built, it gets a gap story under its step — not a redraw of the file around it.
import { readFileSync, writeFileSync } from 'node:fs'
import { Document, isMap, isSeq, parseDocument } from 'yaml'
import { WRITE_OPTS, findStep } from './read.mjs'

const allStoryIds = (steps) =>
	new Set(steps.items.flatMap((step) => (step.get('stories')?.items ?? []).map((s) => s.get?.('id')).filter(Boolean)))

const lastStoryAnywhere = (steps) =>
	steps.items.flatMap((step) => step.get('stories')?.items ?? []).at(-1)

// Copies the nearest sibling's flow and quoting: this step's last story, else the
// file's last story, else this repo's own convention — every story card in
// journey.example.yaml is double-quoted.
function matchSiblingStyle(node, list, steps) {
	const last = list?.items.at(-1) ?? lastStoryAnywhere(steps)
	node.flow = last ? Boolean(last.flow) : true
	node.get('card', true).type = last?.get?.('card', true)?.type ?? 'QUOTE_DOUBLE'
}

const lineStart = (src, offset) => src.lastIndexOf('\n', offset - 1) + 1
const afterLine = (src, offset) => {
	const end = src.indexOf('\n', offset)
	return end === -1 ? src.length : end + 1
}

function serializeItem(node, prefix) {
	const doc = new Document()
	doc.contents = node
	const lines = doc.toString(WRITE_OPTS).replace(/\n$/, '').split('\n')
	const rest = ' '.repeat(prefix.length)
	return `${lines.map((line, i) => (i === 0 ? prefix : rest) + line).join('\n')}\n`
}

// How far a block sequence's dash sits from its parent key, read from the file's
// first block story list; 2 is what this module's own serializer writes.
function seqOffset(src, steps) {
	for (const step of steps.items) {
		const list = step.get('stories')
		if (!isSeq(list) || list.flow || !list.items.length) continue
		const dash = list.items[0].range[0] - 2 - lineStart(src, list.items[0].range[0])
		return dash - (step.range[0] - lineStart(src, step.range[0]))
	}
	return 2
}

// Splices the story into the original text so the rest of the file keeps the
// wrapping and indentation it was written with. Returns null for a shape it
// cannot splice (a flow or empty stories list), where the caller re-serializes.
function splice(src, steps, step, list, story) {
	if (!isMap(step) || step.flow) return null
	if (list) {
		if (!isSeq(list) || list.flow || !list.items.length) return null
		const last = list.items.at(-1)
		const prefix = src.slice(lineStart(src, last.range[0]), last.range[0])
		const at = afterLine(src, Math.max(last.range[1] - 1, last.range[0]))
		return src.slice(0, at) + serializeItem(story, prefix) + src.slice(at)
	}
	const keyIndent = ' '.repeat(step.range[0] - lineStart(src, step.range[0]))
	const prefix = `${keyIndent}${' '.repeat(seqOffset(src, steps))}- `
	const at = afterLine(src, Math.max(step.range[1] - 1, step.range[0]))
	return `${src.slice(0, at)}${keyIndent}stories:\n${serializeItem(story, prefix)}${src.slice(at)}`
}

export function addStory(path, { stepId, id, card }, outPath = path) {
	if (!stepId) throw new Error('addStory needs stepId')
	if (!id) throw new Error('addStory needs id')
	if (!card) throw new Error('addStory needs card — the wording the person used, not a rewrite')

	const src = readFileSync(path, 'utf8')
	const doc = parseDocument(src)
	const steps = doc.get('steps')
	if (!steps) throw new Error(`${path} has no steps`)

	const step = findStep(steps, stepId)
	if (!step) throw new Error(`step "${stepId}" not found in ${path}`)

	if (allStoryIds(steps).has(id)) throw new Error(`story id "${id}" already exists in ${path}`)

	const list = step.get('stories')
	const story = doc.createNode({ id, status: 'gap', card })
	matchSiblingStyle(story, list, steps)

	let out = splice(src, steps, step, list, story)
	if (out === null) {
		const target = list ?? doc.createNode([])
		if (!list) step.set('stories', target)
		target.items.push(story)
		out = doc.toString(WRITE_OPTS)
	}
	const check = parseDocument(out)
	const placed = findStep(check.get('steps'), stepId)?.get('stories')?.items ?? []
	if (check.errors.length || !placed.some((s) => s.get?.('id') === id)) {
		throw new Error(`adding "${id}" under "${stepId}" would not leave a readable journey; ${path} was not written`)
	}

	writeFileSync(outPath, out)
	return { wrote: outPath, id, stepId }
}
