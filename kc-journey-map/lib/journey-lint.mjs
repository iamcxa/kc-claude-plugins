#!/usr/bin/env node
import { fileURLToPath } from 'node:url'
import { dirname, join, resolve } from 'node:path'
import { loadModel } from './read.mjs'
import { lintJourney } from './lint.mjs'

const [path, repoRootArg] = process.argv.slice(2)
if (!path) {
	console.error('usage: journey-lint.mjs <journey.yaml> [repoRoot]')
	process.exit(2)
}

const PKG_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const repoRoot = repoRootArg ? resolve(repoRootArg) : PKG_ROOT

const violations = lintJourney(loadModel(path), { repoRoot, journeyPath: resolve(path) })
for (const v of violations) console.log(`${v.lint}: ${v.detail}`)
console.log(violations.length ? `\n${violations.length} violation(s)` : '\nall lints pass')
process.exit(violations.length ? 1 : 0)
