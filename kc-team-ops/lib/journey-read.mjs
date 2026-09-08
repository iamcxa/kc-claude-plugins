#!/usr/bin/env node
// node lib/journey-read.mjs <journey.yaml> <roomId> [--write]
import { applyDiff, diffAgainstModel, loadModel, readRoom } from './read.mjs'

const [path, room, ...flags] = process.argv.slice(2)
if (!path || !room) {
	console.error('usage: journey-read.mjs <journey.yaml> <roomId> [--write]')
	process.exit(2)
}

const diff = diffAgainstModel(await readRoom({ room }), loadModel(path))
console.log(JSON.stringify(diff, null, 2))

if (flags.includes('--write')) {
	const { applied, skipped } = applyDiff(path, diff)
	console.log(applied.length ? `applied:\n  ${applied.join('\n  ')}` : 'nothing safe to apply')
	if (skipped.length) console.log(`skipped:\n  ${skipped.join('\n  ')}`)
}
