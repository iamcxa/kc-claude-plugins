// A generated text projection alongside the release board: story status/evidence
// and shared activity rules, derived from the journey file.

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
