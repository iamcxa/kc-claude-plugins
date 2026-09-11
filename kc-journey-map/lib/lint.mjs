// Checks authored story status and executable citation consistency.

import { execFileSync } from 'node:child_process'
import { extname, resolve, sep } from 'node:path'
import { iterStories, STORY_STATUSES } from './model.mjs'

// Extensions of something that runs. Prose (.md) and data (.yaml/.json/.tldr) can quote a
// symbol back without the symbol being backed by code — that is the whole defect this
// lint exists to catch, so those extensions never qualify as evidence on their own.
const EXECUTABLE_EXTENSIONS = new Set(['.mjs', '.cjs', '.js', '.jsx', '.mts', '.cts', '.ts', '.tsx', '.py', '.rb', '.sh', '.bash', '.zsh'])

// A CI workflow file is YAML that runs, unlike the YAML the journey itself is written in —
// so it earns a path-based exception rather than a blanket extension one.
const isWorkflowFile = (f) => /\.ya?ml$/.test(f) && f.split(sep).includes('.github') && f.includes(`${sep}workflows${sep}`)

const isExecutableFile = (f) => EXECUTABLE_EXTENSIONS.has(extname(f)) || isWorkflowFile(f)

// Files that grep-match a symbol, scoped to `repoRoot` via cwd (git resolves paths
// relative to the working directory, not the repository root, when none is given), and
// narrowed to files something can execute — a match in a doc or a data file is prose, not
// evidence, even when it names a real symbol.
function filesCiting(symbol, repoRoot) {
	try {
		const out = execFileSync('git', ['grep', '-l', '-w', '-F', symbol], { cwd: repoRoot, encoding: 'utf8' })
		return out
			.split('\n')
			.filter(Boolean)
			.map((f) => resolve(repoRoot, f))
			.filter(isExecutableFile)
	} catch (err) {
		if (err.status === 1) return [] // git grep's own code for "no match", not a failure
		throw err
	}
}

export function lintNoStatus(model) {
	return iterStories(model)
		.filter((s) => !STORY_STATUSES.includes(s.status))
		.map((s) => ({ lint: s.status ? 'invalid-status' : 'no-status', story: s.id, release: s.release,
			detail: s.status ? `story ${s.id} has unsupported status "${s.status}"; use ${STORY_STATUSES.join(', ')}` : `story ${s.id} (under step ${s.step.id}) carries no status` }))
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
			detail: `evidence "${s.evidence}" for story ${s.id} does not grep in any executable file outside the journey file`,
		}))
}

export function lintJourney(model, opts = {}) {
	return [...lintNoStatus(model), ...lintExistsWithoutEvidence(model), ...lintEvidenceNotFound(model, opts)]
}
