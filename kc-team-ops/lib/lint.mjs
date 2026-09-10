// Three checks the grid could never do, run against the journey file itself.
//
// A table does not notice its own drift — a cell that once cited real code goes stale
// silently when that code is renamed. `evidence-not-found` is the one of the three that
// only a program can run: it re-greps the repository every time, which is the whole
// argument for replacing the picture with a checkable schema.

import { execFileSync } from 'node:child_process'
import { resolve } from 'node:path'
import { iterStories } from './model.mjs'

// Files that grep-match a symbol, scoped to `repoRoot` via cwd (git resolves paths
// relative to the working directory, not the repository root, when none is given).
function filesCiting(symbol, repoRoot) {
	try {
		const out = execFileSync('git', ['grep', '-l', '-w', '-F', symbol], { cwd: repoRoot, encoding: 'utf8' })
		return out
			.split('\n')
			.filter(Boolean)
			.map((f) => resolve(repoRoot, f))
	} catch (err) {
		if (err.status === 1) return [] // git grep's own code for "no match", not a failure
		throw err
	}
}

export function lintNoStatus(model) {
	return iterStories(model)
		.filter((s) => !s.status)
		.map((s) => ({ lint: 'no-status', story: s.id, release: s.release, detail: `story ${s.id} (under step ${s.step.id}) carries no status` }))
}

export function lintExistsWithoutEvidence(model) {
	return iterStories(model)
		.filter((s) => s.status === 'exists' && !s.evidence)
		.map((s) => ({ lint: 'exists-without-evidence', story: s.id, release: s.release, detail: `story ${s.id} is marked exists but carries no evidence symbol` }))
}

// Excludes the journey file itself, and anything else named: a generated contract that
// merely quotes the symbol back would otherwise make the check pass on its own say-so.
export function lintEvidenceNotFound(model, { repoRoot, journeyPath, exclude = [] } = {}) {
	if (!repoRoot) throw new Error('lintEvidenceNotFound needs repoRoot to grep against')
	const ignore = new Set([journeyPath, ...exclude].filter(Boolean).map((p) => resolve(p)))
	return iterStories(model)
		.filter((s) => s.evidence)
		.filter((s) => filesCiting(s.evidence, repoRoot).filter((f) => !ignore.has(f)).length === 0)
		.map((s) => ({
			lint: 'evidence-not-found',
			story: s.id,
			release: s.release,
			detail: `evidence "${s.evidence}" for story ${s.id} does not grep anywhere in the repository outside the journey file`,
		}))
}

export function lintJourney(model, opts = {}) {
	return [...lintNoStatus(model), ...lintExistsWithoutEvidence(model), ...lintEvidenceNotFound(model, opts)]
}
