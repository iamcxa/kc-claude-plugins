#!/usr/bin/env node
// Turns a release-acceptance/v1 report into proposed map edits. It reads both files and writes neither.
import { readFileSync, realpathSync } from 'node:fs'
import { pathToFileURL } from 'node:url'
import { parse } from 'yaml'
import { iterStories } from './model.mjs'

export const REPORT_SCHEMA = 'release-acceptance/v1'
const RESULTS = ['works', 'broken', 'missing-entry-point', 'not-reachable']

export function proposeEdits(model, report) {
	if (report?.schema !== REPORT_SCHEMA) throw new Error(`report schema is ${JSON.stringify(report?.schema)}, not ${REPORT_SCHEMA}`)
	const releaseId = report.walk?.release
	if (report.walk?.journey !== model.journey) throw new Error(`report walks journey ${JSON.stringify(report.walk?.journey)}, the map is ${model.journey}`)
	if (!(model.releases ?? []).some((r) => r.id === releaseId)) throw new Error(`report walks release ${JSON.stringify(releaseId)}, which the map lacks`)
	const onRelease = new Map(iterStories(model).filter((s) => s.release === releaseId).map((s) => [s.id, s]))
	const rows = Array.isArray(report.stories) ? report.stories : []
	const strangers = rows.filter((row) => !onRelease.has(row?.id)).map((row) => row?.id)
	if (strangers.length) throw new Error(`report stories not on release ${releaseId}: ${strangers.join(', ')}`)
	const odd = rows.filter((row) => !RESULTS.includes(row.result))
	if (odd.length) throw new Error(`result outside ${RESULTS.join(', ')}: ${odd.map((row) => `${row.id}=${JSON.stringify(row.result)}`).join(', ')}`)

	const proposals = []
	for (const row of rows) {
		const status = onRelease.get(row.id).status
		if (row.result === 'broken' && status === 'exists') proposals.push({ story: row.id, from: status, to: 'unverified', because: 'the walk found it broken, so `exists` is not supported' })
		if (row.result === 'missing-entry-point' && (status === 'exists' || status === 'unverified')) proposals.push({ story: row.id, from: status, to: 'gap', because: 'the walk found no way in; a handler with no route is `gap` (cell-contract.md)' })
	}
	const unreachable = rows.filter((row) => row.result === 'not-reachable').map((row) => row.id)
	const untested = Array.isArray(report.not_tested) ? report.not_tested.filter((t) => typeof t === 'string' && t.trim()) : []
	const parts = []
	if (unreachable.length) parts.push(`Not reachable in the release walk: ${unreachable.join(', ')}.`)
	if (untested.length) parts.push(`Not tested: ${untested.join('; ')}.`)
	return {
		journey: model.journey,
		release: releaseId,
		proposals,
		unproven: { current: model.status?.unproven ?? null, proposed: parts.length ? parts.join(' ') : null },
		note: 'A proposal only: the map is changed by the Captain accepting a docs pull request. A story that works changes nothing.',
	}
}

if (process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) {
	const [path, reportPath] = process.argv.slice(2)
	if (!path || !reportPath) {
		console.error('usage: journey-accept.mjs <journey.yaml> <report.json>')
		process.exitCode = 2
	} else {
		try {
			console.log(JSON.stringify(proposeEdits(parse(readFileSync(path, 'utf8')), JSON.parse(readFileSync(reportPath, 'utf8'))), null, 2))
		} catch (error) {
			console.error(`ACCEPT REFUSED: ${error.message}`)
			process.exitCode = 1
		}
	}
}
