#!/usr/bin/env node
// Checks the shape of a release-review record and its order against the map, not that the walk
// was done well or that the Captain was asked.
import { readFileSync, realpathSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { parse } from 'yaml'
import { normalizeStory, openQuestions } from './model.mjs'

const words = (value) => typeof value === 'string' && value.trim().length > 0
const isoDay = (value) => {
	const day = value instanceof Date && !Number.isNaN(value.getTime()) ? value.toISOString().slice(0, 10) : value
	if (typeof day !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(day)) return null
	const parsed = new Date(`${day}T00:00:00Z`)
	return Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== day ? null : day
}
const SAFE = /^[A-Za-z0-9][A-Za-z0-9._-]*$/
const KINDS = ['gate', 'amendment', 'release']
const SECTIONS = ['## Map edit', '## Walk', '## Holes', '## Slice', '## Tasks']
const COUNTS = ['questions', 'dropped', 'decision rows', 'asked', 'open after']

export const recordPath = (journeyPath, model, releaseId) => {
	for (const part of [model.journey, releaseId]) {
		if (typeof part !== 'string' || !SAFE.test(part)) throw new Error(`cannot build a record path from ${JSON.stringify(part)}`)
	}
	return join(dirname(journeyPath), 'reviews', model.journey, `${releaseId}.md`)
}

function interrogationProblems(line) {
	if (line === undefined) return ['the Interrogation: line is missing; a release is interrogated before it is reviewed']
	if (/^Interrogation: interrogation not run/.test(line)) return [`interrogation did not run: ${line.slice('Interrogation: '.length)}`]
	const parts = line.slice('Interrogation: '.length).split(';').map((part) => part.trim())
	const problems = []
	if (!/^\d{4}-\d{2}-\d{2}$/.test(parts[0])) problems.push('the Interrogation: line does not start with a YYYY-MM-DD date')
	for (const count of COUNTS) {
		if (!parts.some((part) => new RegExp(`^${count} \\d+$`).test(part))) problems.push(`the Interrogation: line lacks the count "${count} <n>"`)
	}
	const arms = parts.map((part) => /^codex (\S+) (\S+) (lens|plain)(?:: (.+))?$/.exec(part)).filter(Boolean)
	if (!arms.some((arm) => arm[3] === 'lens')) problems.push('the Interrogation: line names no lens arm; "codex <model> <effort> lens" is required, "codex <model> <effort> plain: <why hard to reverse>" is extra')
	if (arms.some((arm) => arm[3] === 'plain' && !arm[4])) problems.push('a plain arm must say why the decision is hard to reverse')
	return problems
}

function tasksTable(body) {
	const at = body.search(/^## Tasks\s*$/m)
	if (at < 0) return null
	const rows = body.slice(at).split('\n').slice(1).filter((l) => l.trim().startsWith('|'))
	return rows.map((row) => row.trim().replace(/^\||\|$/g, '').split('|').map((cell) => cell.trim()))
}

export function checkRecord(record, journeyText) {
	const failures = []
	const fail = (message) => failures.push(message)
	const model = parse(journeyText)
	const lines = record.split('\n')
	const heading = /^# Release review: (\S+)\/(\S+)\s*$/.exec(lines[0] ?? '')
	if (!heading) return ['the record must start with "# Release review: <journey>/<release-id>"']
	const [, journey, releaseId] = heading
	const interrogatedOn = /^Interrogation: (\d{4}-\d{2}-\d{2})/m.exec(record)?.[1]
	if (journey !== model.journey) fail(`heading names journey ${journey}, the map is ${model.journey}`)
	if (!(model.releases ?? []).some((r) => r.id === releaseId)) fail(`heading names release ${releaseId}, which the map lacks`)
	for (const problem of interrogationProblems(lines.find((l) => l.startsWith('Interrogation:')))) fail(problem)

	const stories = (model.steps ?? []).flatMap((step) => (step.stories ?? []).map((story, j) => normalizeStory(step, story, j)))
	const onRelease = stories.filter((story) => story.release === releaseId)
	for (const story of onRelease) {
		const open = openQuestions(story)
		if (open.length) fail(`open questions on ${story.id}: ${open.map((q) => q.id).join(', ')}; the release is interrogated and asked before it is reviewed`)
		for (const q of story.questions.filter((entry) => entry.source)) {
			const where = `${story.id}/${q.id}`
			if (!KINDS.includes(q.source.kind)) { fail(`${where}: source.kind ${JSON.stringify(q.source.kind)} is not gate, amendment or release`); continue }
			if (q.source.kind !== 'release') continue
			const earlier = interrogatedOn && isoDay(q.source.date) && isoDay(q.source.date) < interrogatedOn && (model.releases ?? []).some((r) => q.source.ref === `${model.journey}/${r.id}`)
			if (q.source.ref !== `${model.journey}/${releaseId}` && !earlier) fail(`${where}: source.ref is ${JSON.stringify(q.source.ref)}, expected "${model.journey}/${releaseId}"`)
			if (!words(q.source.words)) fail(`${where}: source.words is empty or not a string`)
			if (!isoDay(q.source.date)) fail(`${where}: source.date is empty or not a YYYY-MM-DD date`)
			if (q.answer && q.doc) fail(`${where}: holds both answer and doc; a ruling has one home`)
			if (!q.answer && !q.doc) fail(`${where}: holds neither answer nor doc`)
		}
	}

	if (!/^Reviewed: \S/m.test(record)) fail('the record lacks the "Reviewed:" line')
	const at = SECTIONS.map((section) => lines.indexOf(section))
	for (const [i, section] of SECTIONS.entries()) if (at[i] < 0) fail(`the record lacks the "${section}" section`)
	const found = at.filter((index) => index >= 0)
	if (found.some((index, i) => i > 0 && index < found[i - 1])) fail(`the record sections are out of order; expected ${SECTIONS.join(', ')}`)

	const rows = tasksTable(record)
	if (!rows || rows.length < 2) fail('the record lacks a "## Tasks" table')
	else {
		const header = rows[0].join('|')
		if (header !== 'Task|journey-story|Required tasks|Carries') fail(`the Tasks table header is "${header}", expected Task | journey-story | Required tasks | Carries`)
		const separated = rows[1].every((cell) => /^:?-+:?$/.test(cell))
		if (!separated) fail('the Tasks table lacks its separator row after the header')
		for (const cells of rows.slice(separated ? 2 : 1)) {
			const [task, storyId, , carries = '-'] = cells
			const story = onRelease.find((entry) => entry.id === storyId)
			if (!story) { fail(`task ${task}: journey-story ${storyId} is not a story on release ${releaseId}`); continue }
			if (carries === '-') continue
			for (const entry of carries.split(',').map((part) => part.trim())) {
				const owed = /^ADR owed: (\S+)$/.exec(entry)
				if (!owed) fail(`task ${task}: Carries entry ${JSON.stringify(entry)} is not "ADR owed: <question id>"`)
				else {
					const asked = story.questions.find((q) => q.id === owed[1] && q.source?.kind === 'release')
					if (!asked) fail(`task ${task}: ADR owed ${owed[1]} is not a kind: release question on ${storyId}`)
					else if (asked.doc) fail(`task ${task}: ADR owed ${owed[1]} already holds doc:, so its ADR exists and is not owed`)
				}
			}
		}
	}
	return failures
}

if (process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) {
	const [command, a, b] = process.argv.slice(2)
	try {
		if (command === 'path' && a && b) {
			console.log(recordPath(a, parse(readFileSync(a, 'utf8')), b))
		} else if (command === 'check' && a && b) {
			const failures = checkRecord(readFileSync(a, 'utf8'), readFileSync(b, 'utf8'))
			if (failures.length) throw new Error(failures.join('\n'))
			console.log(`review record ok: ${a}`)
		} else {
			console.error('usage: journey-review.mjs path <journey.yaml> <release-id> | check <record.md> <journey.yaml>')
			process.exitCode = 2
		}
	} catch (error) {
		console.error(`REVIEW REFUSED: ${error.message}`)
		process.exitCode = 1
	}
}
