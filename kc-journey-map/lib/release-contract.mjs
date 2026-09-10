// The document that replaces the per-release canvas board.
//
// The journey board's unique content was never the picture — it was a citation and a
// constraint list, neither of which is spatial. This generates that content as a plain
// document instead of a room: for every story in a release, its status, its evidence
// symbol, and the rule ids that apply. Always derived from the journey file; nothing
// here is hand-authored, and there is no `--edit` path.

import { iterStories } from './model.mjs'

export function releaseContractRows(model, releaseId) {
	const release = (model.releases ?? []).find((r) => r.id === releaseId)
	if (!release) throw new Error(`no release "${releaseId}" in this journey`)

	const stories = iterStories(model).filter((s) => s.release === releaseId)
	return { release, rows: stories.map((s) => ({ ...s, rules: s.step.rules ?? [] })) }
}

export function buildReleaseContract(model, releaseId, { journeyPath = model.journey } = {}) {
	const { release, rows } = releaseContractRows(model, releaseId)
	const rulesById = new Map((model.rules ?? []).map((r) => [r.id, r.text]))

	const lines = [
		`# ${release.name} — release contract`,
		'',
		release.goal ?? '',
		'',
		`Generated from ${journeyPath}. Do not hand-edit; re-run the generator instead.`,
		'',
		'| Story | Status | Evidence | Question | Rules |',
		'|---|---|---|---|---|',
	]

	for (const row of rows) {
		const status = row.status ?? '**MISSING**'
		const evidence = row.evidence ? `\`${row.evidence}\`` : '—'
		const question = row.question ?? '—'
		const rules = row.rules.length ? row.rules.map((id) => `\`${id}\` — ${rulesById.get(id) ?? id}`).join('; ') : '—'
		lines.push(`| ${row.card} | ${status} | ${evidence} | ${question} | ${rules} |`)
	}

	return lines.join('\n') + '\n'
}
