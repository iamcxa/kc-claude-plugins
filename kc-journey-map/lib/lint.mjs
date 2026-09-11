
import { execFileSync } from 'node:child_process'
import { extname, resolve, sep } from 'node:path'
import { iterStories, STORY_STATUSES } from './model.mjs'

// Prose/data matches must not count as executable evidence.
const EXECUTABLE_EXTENSIONS = new Set(['.mjs', '.cjs', '.js', '.jsx', '.mts', '.cts', '.ts', '.tsx', '.py', '.rb', '.sh', '.bash', '.zsh'])

const isWorkflowFile = (f) => /\.ya?ml$/.test(f) && f.split(sep).includes('.github') && f.includes(`${sep}workflows${sep}`)

const isExecutableFile = (f) => EXECUTABLE_EXTENSIONS.has(extname(f)) || isWorkflowFile(f)

// git grep returns tracked paths relative to cwd, not necessarily the repository root.
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

// Exclude generated self-citations; quoting a symbol is not executable evidence.
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
