#!/usr/bin/env node
import { fileURLToPath } from 'node:url'
import { dirname, join, resolve } from 'node:path'
import { loadModel } from './read.mjs'
import { lintJourney, longCards } from './lint.mjs'

const args = process.argv.slice(2)
const repos = {}
const positional = []
for (let i = 0; i < args.length; i++) {
	if (args[i] !== '--repo') { positional.push(args[i]); continue }
	const match = /^([^=]+)=([^@]+)(?:@(.+))?$/.exec(args[++i] ?? '')
	if (!match) {
		console.error('--repo takes <name>=<path>[@ref]')
		process.exit(2)
	}
	repos[match[1]] = { root: resolve(match[2]), ref: match[3] }
}
const [path, repoRootArg] = positional
if (!path) {
	console.error('usage: journey-lint.mjs <journey.yaml> [repoRoot] [--repo <name>=<path>[@ref]]...')
	process.exit(2)
}

const PKG_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const repoRoot = repoRootArg ? resolve(repoRootArg) : PKG_ROOT

const model = loadModel(path)
const violations = lintJourney(model, { repoRoot, journeyPath: resolve(path), repos })
for (const v of violations) console.log(`${v.lint}: ${v.detail}`)
for (const note of longCards(model)) console.log(`long-card (advisory): ${note}`)
console.log(violations.length ? `\n${violations.length} violation(s)` : '\nall lints pass')
process.exit(violations.length ? 1 : 0)
