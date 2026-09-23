#!/usr/bin/env node
// This guard validates recorded planning evidence, not its truth or human authorship.
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { parse } from 'yaml'
import { normalizeStory, openQuestions } from './model.mjs'

const hash = (value) => createHash('sha256').update(value).digest('hex')
const canonical = (value) => JSON.stringify(value, (_, v) =>
	v && typeof v === 'object' && !Array.isArray(v)
		? Object.fromEntries(Object.keys(v).sort().map((key) => [key, v[key]])) : v)
const text = (value) => typeof value === 'string' && value.trim().length > 0
const same = (a, b) => canonical(a) === canonical(b)
const stories = (model) => (model.steps ?? []).flatMap((step) => step.stories ?? [])

function check(baseline, model, assessment) {
	const failures = []
	const require = (condition, message) => { if (!condition) failures.push(message) }
	const selected = stories(model).filter((story) => story.release === assessment.release)
	const ids = selected.map((story) => story.id)
	const release = model.releases?.find((entry) => entry.id === assessment.release)
	require(assessment.version === 1, 'unsupported assessment version')
	require(release && text(release.goal) && assessment.goal === release.goal, 'release goal missing or differs from assessment')
	require(selected.length > 0, 'selected release has no stories')
	for (const step of model.steps ?? []) (step.stories ?? []).forEach((story, j) => {
		if (story?.release !== assessment.release) return
		const open = openQuestions(normalizeStory(step, story, j))
		require(open.length === 0, `open questions on ${story.id}: ${open.map((q) => q.id).join(', ')}; answer, defer with because, or link the decision record before handoff`)
	})
	for (const source of [baseline, model]) {
		const allIds = stories(source).map((story) => story?.id)
		require(allIds.every(text) && new Set(allIds).size === allIds.length, 'source requires explicit unique story IDs')
	}

	// Compare the full pre-cut map, allowing membership and the reviewed goal to change.
	// New release bands are allowed; existing nonselected releases and requirements stay.
	const withoutCuts = (source) => {
		const result = structuredClone(source)
		delete result.releases
		for (const step of result.steps ?? []) for (const story of step.stories ?? []) delete story.release
		return result
	}
	require(same(withoutCuts(baseline), withoutCuts(model)), 'requirements changed or deleted: reconcile a new full-map baseline before slicing')
	for (const oldRelease of baseline.releases ?? []) {
		const current = model.releases?.find((entry) => entry.id === oldRelease.id)
		const before = { ...oldRelease }, after = { ...current }
		if (oldRelease.id === assessment.release) { delete before.goal; delete after.goal }
		require(same(before, after), `existing release changed beyond selected goal: ${oldRelease.id}`)
	}

	const outcome = assessment.outcome ?? {}
	require(text(outcome.start) && text(outcome.finish) && text(outcome.verification), 'observable start, finish and verification are required')
	require(outcome.complete === true, 'incomplete end-to-end journey: propose a complete smaller outcome')
	const rules = new Map((model.rules ?? []).map((rule) => [rule.id, rule]))
	const applicableRules = [...new Set((model.steps ?? []).filter((step) =>
		(step.stories ?? []).some((story) => ids.includes(story.id))).flatMap((step) => step.rules ?? []))]
	const constraints = assessment.constraints ?? []
	require(Array.isArray(constraints) && new Set(constraints.map((entry) => entry.id)).size === constraints.length, 'constraint assessments must be unique')
	for (const id of applicableRules) require(constraints.some((entry) => entry.id === id), `missing necessary constraint assessment: ${id}`)
	for (const entry of constraints) {
		require(rules.has(entry.id) && entry.preserved === true && text(entry.verification), `constraint unsupported or not preserved: ${entry.id}`)
	}

	const retained = assessment.retained ?? []
	require(Array.isArray(retained) && same(retained.map((entry) => entry.id).sort(), [...ids].sort()), 'retained assessments must match selected stories exactly')
	for (const entry of retained) {
		require(entry.necessary === true, `shrink-required: ${entry.id} can be removed; propose deferral before handoff`)
		require(text(entry.reason) && (entry.breaks === 'outcome' || constraints.some((rule) => entry.breaks === `constraint:${rule.id}`)), `removal test lacks an outcome or necessary constraint: ${entry.id}`)
	}
	for (const story of stories(baseline).filter((entry) => text(entry.release) && entry.release !== assessment.release)) {
		require(stories(model).find((entry) => entry.id === story.id)?.release === story.release, `nonselected membership changed: ${story.id}`)
	}
	const removed = stories(baseline).filter((story) => (story.release === assessment.release || !text(story.release)) && !ids.includes(story.id)).map((story) => story.id)
	const deferred = assessment.deferred ?? []
	require(Array.isArray(deferred) && same(deferred.map((entry) => entry.id).sort(), removed.sort()), 'each story removed from the release needs a deferral reason')
	for (const entry of deferred) require(text(entry.reason), `missing deferral reason: ${entry.id}`)

	require(Array.isArray(assessment.dependencies), 'dependencies must be explicitly assessed (empty array when none)')
	for (const dependency of assessment.dependencies ?? []) {
		require(ids.includes(dependency.story) && text(dependency.prerequisite) && dependency.story !== dependency.prerequisite && text(dependency.evidence) && (ids.includes(dependency.prerequisite) || dependency.available === true), 'dependency needs a retained story, factual evidence, and a retained or already available prerequisite')
	}
	require(Array.isArray(assessment.unresolved) && assessment.unresolved.length === 0, 'unresolved value, scope, acceptance or fit decisions keep handoff draft')
	const budget = assessment.budget ?? {}
	require(['hours', 'days', 'weeks'].includes(budget.unit) && Number.isFinite(budget.appetite) && budget.appetite > 0 && text(budget.user_basis), 'explicit user time appetite and its source are required')
	require(Number.isFinite(budget.estimate) && budget.estimate > 0 && text(budget.estimate_basis), 'grounded completion estimate required; do not invent fit')
	require(budget.estimate <= budget.appetite, 'oversized: propose a smaller complete slice within the agreed appetite')
	return failures
}

try {
	const [baselinePath, sourcePath, assessmentPath, briefPath, mode, outPath, ...extra] = process.argv.slice(2)
	if (!briefPath || !['--digest', '--out'].includes(mode) || (mode === '--out' && !outPath) || (mode === '--digest' && outPath) || extra.length) {
		throw new Error('usage: journey-handoff.mjs <pre-cut.yaml> <journey.yaml> <assessment.json> <brief.md> (--digest | --out <new-path>)')
	}
	// No overwrite: an earlier output is not evidence for a later attempt.
	if (mode === '--out' && existsSync(outPath)) throw new Error('output already exists; use a new attempt path and recheck its source/assessment before handoff')
	const baselineBytes = readFileSync(baselinePath)
	const sourceBytes = readFileSync(sourcePath)
	const briefBytes = readFileSync(briefPath)
	const assessment = JSON.parse(readFileSync(assessmentPath, 'utf8'))
	const failures = check(parse(baselineBytes.toString()), parse(sourceBytes.toString()), assessment)
	for (const [field, bytes] of [['baseline_sha256', baselineBytes], ['source_sha256', sourceBytes], ['brief_sha256', briefBytes]]) {
		if (assessment[field] !== hash(bytes)) failures.push(`stale or missing ${field}`)
	}
	if (!briefBytes.toString().trim()) failures.push('Development Brief is empty')
	const { acceptance, ...proposal } = assessment
	const digest = hash(canonical(proposal))
	if (mode === '--out' && (acceptance?.decision !== 'accepted' || !text(acceptance?.evidence) || acceptance?.digest !== digest)) {
		failures.push('missing acceptance or stale acceptance digest; present the changed proposal to the human')
	}
	if (failures.length) throw new Error(failures.join('\n'))
	if (mode === '--digest') console.log(digest)
	else {
		writeFileSync(outPath, briefBytes, { flag: 'wx' })
		console.log(JSON.stringify({ handoff: outPath, assessment_sha256: digest, source_sha256: hash(sourceBytes), brief_sha256: hash(briefBytes), limitation: 'Recorded planning checks passed; semantic fit, evidence truth and human approval remain reviewed judgments. Dev-flow admission still applies.' }))
	}
} catch (error) {
	console.error(`HANDOFF REFUSED: ${error.message}`)
	process.exitCode = 1
}
