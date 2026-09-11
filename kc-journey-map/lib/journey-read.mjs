#!/usr/bin/env node
// node lib/journey-read.mjs <journey.yaml> <roomId> [--write] [--out <path>]
//
// Without --write it only reports. With --write it applies the safe subset over the
// same file; add --out to save the result somewhere else and leave the original alone.
import { applyDiff, diffAgainstModel, loadModel, readRoom } from './read.mjs'

const argv = process.argv.slice(2)
const outIndex = argv.indexOf('--out')
const outPath = outIndex >= 0 ? argv[outIndex + 1] : undefined
// Guard the -1: without --out, `outIndex + 1` is 0 and would drop the first positional.
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
	const { applied, skipped, wrote } = applyDiff(path, diff, outPath ?? path)
	console.log(applied.length ? `applied:\n  ${applied.join('\n  ')}` : 'nothing safe to apply')
	if (skipped.length) console.log(`skipped:\n  ${skipped.join('\n  ')}`)
	if (wrote) console.log(`wrote: ${wrote}`)
}
