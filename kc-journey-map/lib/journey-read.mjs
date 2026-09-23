#!/usr/bin/env node
import { applyDiff, diffAgainstModel, loadModel, readRoom, removeAbsorbedNotes } from './read.mjs'

const argv = process.argv.slice(2)
const outIndex = argv.indexOf('--out')
const outPath = outIndex >= 0 ? argv[outIndex + 1] : undefined
const outValueIndex = outIndex >= 0 ? outIndex + 1 : -1
const positional = argv.filter((a, i) => !a.startsWith('--') && i !== outValueIndex)
const [path, room] = positional

if (!path || !room || (outIndex >= 0 && !outPath)) {
	console.error('usage: journey-read.mjs <journey.yaml> <roomId> [--write] [--out <path>]')
	process.exit(2)
}

const diff = diffAgainstModel(await readRoom({ room }), loadModel(path))
console.log(JSON.stringify(diff, null, 2))

if (argv.includes('--write') || outPath) {
	const target = outPath ?? path
	const { applied, skipped, wrote, absorbed } = applyDiff(path, diff, target)
	console.log(applied.length ? `applied:\n  ${applied.join('\n  ')}` : 'nothing safe to apply')
	if (skipped.length) console.log(`skipped:\n  ${skipped.join('\n  ')}`)
	if (diff.questionsDeleted.length || diff.answersDeleted.length) {
		console.log('reported, not applied — a deleted question or answer is a decision to show, not to infer:')
		for (const d of diff.questionsDeleted) console.log(`  question ${d.id} on ${d.story} (${d.page}) was removed on the canvas`)
		for (const d of diff.answersDeleted) console.log(`  answer to ${d.question} on ${d.story} (${d.page}) was removed on the canvas`)
	}
	if (wrote) console.log(`wrote: ${wrote}`)

	// Only an in-place --write confirms the note's content landed in the canonical file;
	// a --out save-as leaves the source (and the room) untouched, so nothing is removed.
	if (wrote === path && absorbed.length) {
		const ids = [...new Set(absorbed.map((a) => a.shapeId))]
		const r = await removeAbsorbedNotes({ room, ids })
		console.log(`removed ${r.removed} absorbed note(s) from the room: ${ids.join(', ')}`)
	}
}
