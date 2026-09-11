#!/usr/bin/env node
import { writeFileSync } from 'node:fs'
import { loadModel } from './read.mjs'
import { buildReleaseContract } from './release-contract.mjs'

const argv = process.argv.slice(2)
const outIndex = argv.indexOf('--out')
const outPath = outIndex >= 0 ? argv[outIndex + 1] : undefined
const outValueIndex = outIndex >= 0 ? outIndex + 1 : -1
const [path, releaseId] = argv.filter((a, i) => !a.startsWith('--') && i !== outValueIndex)

if (!path || !releaseId) {
	console.error('usage: journey-contract.mjs <journey.yaml> <releaseId> [--out <path>]')
	process.exit(2)
}

const doc = buildReleaseContract(loadModel(path), releaseId, { journeyPath: path })
if (outPath) {
	writeFileSync(outPath, doc)
	console.log(`wrote ${outPath}`)
} else {
	process.stdout.write(doc)
}
