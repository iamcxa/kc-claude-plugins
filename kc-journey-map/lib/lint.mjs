
import { execFileSync } from 'node:child_process'
import { extname, resolve, sep } from 'node:path'
import { iterStories, openQuestions, QUESTION_STATUSES, STORY_STATUSES } from './model.mjs'
import { textWidth } from './records.mjs'

// Prose/data matches must not count as executable evidence.
const EXECUTABLE_EXTENSIONS = new Set(['.mjs', '.cjs', '.js', '.jsx', '.mts', '.cts', '.ts', '.tsx', '.py', '.rb', '.sh', '.bash', '.zsh', '.go'])

const isWorkflowFile = (f) => /\.ya?ml$/.test(f) && f.split(sep).includes('.github') && f.includes(`${sep}workflows${sep}`)

const isExecutableFile = (f) => EXECUTABLE_EXTENSIONS.has(extname(f)) || isWorkflowFile(f)

// git grep returns tracked paths relative to cwd, not necessarily the repository root.
function filesCiting(symbol, repoRoot, ref) {
	try {
		const out = execFileSync('git', ['grep', '-l', '-w', '-F', symbol, ...(ref ? [ref] : [])], { cwd: repoRoot, encoding: 'utf8' })
		return out
			.split('\n')
			.filter(Boolean)
			.map((f) => resolve(repoRoot, ref ? f.slice(ref.length + 1) : f))
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

// A typo'd status silently reads as not-open to `openQuestions`, bypassing the
// exists-with-open-question gate below.
export function lintQuestionStatus(model) {
	return iterStories(model).flatMap((s) => (s.questions ?? [])
		.filter((q) => q.status !== undefined && (!QUESTION_STATUSES.includes(q.status) || (q.status === 'deferred' && !q.because)))
		.map((q) => ({ lint: 'invalid-question-status', story: s.id, release: s.release,
			detail: QUESTION_STATUSES.includes(q.status)
				? `question ${q.id} on story ${s.id} is deferred without a "because"`
				: `question ${q.id} on story ${s.id} has unsupported status "${q.status}"; use ${QUESTION_STATUSES.join(', ')}` })))
}

export function lintExistsWithOpenQuestion(model) {
	return iterStories(model)
		.filter((s) => s.status === 'exists' && openQuestions(s).length)
		.map((s) => ({ lint: 'exists-with-open-question', story: s.id, release: s.release,
			detail: `story ${s.id} is marked exists while these questions have no answer: ${openQuestions(s).map((q) => q.id).join(', ')}` }))
}

const QUALIFIED_EVIDENCE = /^([A-Za-z0-9][\w.-]*):(\S+)$/

export function lintEvidenceNotFound(model, { repoRoot, journeyPath, exclude = [], repos = {} } = {}) {
	if (!repoRoot) throw new Error('lintEvidenceNotFound needs repoRoot to grep against')
	const ignore = new Set([journeyPath, ...exclude].filter(Boolean).map((p) => resolve(p)))
	return iterStories(model)
		.filter((s) => s.evidence)
		.flatMap((s) => {
			const qualified = QUALIFIED_EVIDENCE.exec(s.evidence)
			const repo = qualified ? repos[qualified[1]] : { root: repoRoot }
			if (!repo) return [{ lint: 'evidence-repo-unknown', story: s.id, release: s.release,
				detail: `evidence "${s.evidence}" for story ${s.id} names repository "${qualified[1]}"; pass it with --repo ${qualified[1]}=<path>[@ref]` }]
			const symbol = qualified ? qualified[2] : s.evidence
			if (filesCiting(symbol, repo.root, repo.ref).filter((f) => !ignore.has(f)).length) return []
			return [{ lint: 'evidence-not-found', story: s.id, release: s.release,
				detail: `evidence "${s.evidence}" for story ${s.id} does not grep in any executable file outside the journey file` }]
		})
}

export const DEFAULT_SLICE_LIMIT = 5

const validSliceLimit = (v) => typeof v === 'number' && Number.isInteger(v) && v > 0

// A typo'd limit would otherwise read as the default and silence nothing.
export function lintSliceLimit(model) {
	if (model.slice_limit === undefined || validSliceLimit(model.slice_limit)) return []
	return [{ lint: 'invalid-slice-limit', detail: `slice_limit ${JSON.stringify(model.slice_limit)} is not a positive integer` }]
}

// The renderer reads `board !== false`, so a string "false" would still draw the board.
export function lintReleaseBoard(model) {
	return (model.releases ?? [])
		.filter((r) => r && typeof r === 'object' && r.board !== undefined && typeof r.board !== 'boolean')
		.map((r) => ({ lint: 'invalid-board', release: r.id, detail: `release ${r.id} has board ${JSON.stringify(r.board)}; use true or false` }))
}

// Advisory: count is a load cue for a reader, not a fit test; fit stays with the handoff appetite check.
export function oversizedSlices(model) {
	const limit = validSliceLimit(model.slice_limit) ? model.slice_limit : DEFAULT_SLICE_LIMIT
	const open = new Map()
	for (const s of iterStories(model)) if (s.release && s.status !== 'exists') open.set(s.release, (open.get(s.release) ?? 0) + 1)
	return [...open].filter(([, n]) => n > limit).map(([id, n]) => {
		const because = (model.releases ?? []).find((r) => r.id === id)?.slice_because
		const held = `release ${id} holds ${n} stories that do not exist yet (limit ${limit})`
		return typeof because === 'string' && because.trim()
			? { kind: 'accepted', text: `${held} because ${because.trim()}` }
			: { kind: 'advisory', text: `${held}; split into sub-slices or record slice_because` }
	})
}

export function lintJourney(model, opts = {}) {
	return [...lintNoStatus(model), ...lintExistsWithoutEvidence(model), ...lintQuestionStatus(model), ...lintExistsWithOpenQuestion(model), ...lintSliceLimit(model), ...lintReleaseBoard(model), ...lintEvidenceNotFound(model, opts)]
}

// Card text past this width reads as a paragraph; detail belongs behind an answer's doc link.
export const CARD_TEXT_LIMIT = 80

export function longCards(model) {
	const out = []
	for (const step of model.steps ?? []) {
		for (const story of step.stories ?? []) {
			if (typeof story !== 'object') continue
			if (textWidth(story.card ?? '') > CARD_TEXT_LIMIT) out.push(`story ${story.id} card is ${textWidth(story.card)} columns wide`)
			for (const q of story.questions ?? []) {
				if (textWidth(q.ask ?? '') > CARD_TEXT_LIMIT) out.push(`question ${story.id}/${q.id} is ${textWidth(q.ask)} columns wide`)
				if (textWidth(q.answer ?? '') > CARD_TEXT_LIMIT) out.push(`answer ${story.id}/${q.id} is ${textWidth(q.answer)} columns wide — put detail behind its doc link`)
			}
		}
		(step.system ?? []).forEach((line, i) => {
			if (textWidth(line) > CARD_TEXT_LIMIT) out.push(`flow ${step.id} line ${i + 1} is ${textWidth(line)} columns wide`)
		})
		if (textWidth(step.note ?? '') > CARD_TEXT_LIMIT) out.push(`note ${step.id} is ${textWidth(step.note)} columns wide`)
	}
	for (const rule of model.rules ?? []) {
		if (textWidth(rule.text ?? '') > CARD_TEXT_LIMIT) out.push(`rule ${rule.id} is ${textWidth(rule.text)} columns wide`)
	}
	for (const [field, value] of Object.entries(model.status ?? {})) {
		if (typeof value === 'string' && textWidth(value) > CARD_TEXT_LIMIT) out.push(`status ${field} is ${textWidth(value)} columns wide`)
	}
	return out
}
