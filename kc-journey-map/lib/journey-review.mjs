#!/usr/bin/env node
// Checks the shape of a release-review record and its order against the map, not that the walk
// was done well or that the Captain was asked.
import { readFileSync, realpathSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { parse } from 'yaml'
import { normalizeStory, openQuestions } from './model.mjs'

const text = (value) => (typeof value === 'string' ? value.trim().length > 0 : value instanceof Date || typeof value === 'number')
const SAFE = /^[A-Za-z0-9][A-Za-z0-9._-]*$/
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
	if (arms.length === 0) problems.push('the Interrogation: line names no codex arm as "codex <model> <effort> lens" or "codex <model> <effort> plain: <why hard to reverse>"')
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
	if (journey !== model.journey) fail(`heading names journey ${journey}, the map is ${model.journey}`)
	if (!(model.releases ?? []).some((r) => r.id === releaseId)) fail(`heading names release ${releaseId}, which the map lacks`)
	for (const problem of interrogationProblems(lines.find((l) => l.startsWith('Interrogation:')))) fail(problem)

	const stories = (model.steps ?? []).flatMap((step) => (step.stories ?? []).map((story, j) => normalizeStory(step, story, j)))
	const onRelease = stories.filter((story) => story.release === releaseId)
	for (const story of onRelease) {
		const open = openQuestions(story)
		if (open.length) fail(`open questions on ${story.id}: ${open.map((q) => q.id).join(', ')}; the release is interrogated and asked before it is reviewed`)
		for (const q of story.questions.filter((entry) => entry.source?.kind === 'release')) {
			const where = `${story.id}/${q.id}`
			if (q.source.ref !== `${model.journey}/${releaseId}`) fail(`${where}: source.ref is ${JSON.stringify(q.source.ref)}, expected "${model.journey}/${releaseId}"`)
			if (!text(q.source.words)) fail(`${where}: source.words is empty`)
			if (!text(q.source.date)) fail(`${where}: source.date is empty`)
			if (q.answer && q.doc) fail(`${where}: holds both answer and doc; a ruling has one home`)
			if (!q.answer && !q.doc) fail(`${where}: holds neither answer nor doc`)
		}
	}

	const rows = tasksTable(record)
	if (!rows || rows.length < 2) fail('the record lacks a "## Tasks" table')
	else {
		const header = rows[0].join('|')
		if (header !== 'Task|journey-story|Required tasks|Carries') fail(`the Tasks table header is "${header}", expected Task | journey-story | Required tasks | Carries`)
		for (const cells of rows.slice(2)) {
			const [task, storyId, , carries = '-'] = cells
			const story = onRelease.find((entry) => entry.id === storyId)
			if (!story) { fail(`task ${task}: journey-story ${storyId} is not a story on release ${releaseId}`); continue }
			if (carries === '-') continue
			for (const entry of carries.split(',').map((part) => part.trim())) {
				const owed = /^ADR owed: (\S+)$/.exec(entry)
				if (!owed) fail(`task ${task}: Carries entry ${JSON.stringify(entry)} is not "ADR owed: <question id>"`)
				else if (!story.questions.some((q) => q.id === owed[1] && q.source?.kind === 'release')) fail(`task ${task}: ADR owed ${owed[1]} is not a kind: release question on ${storyId}`)
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
