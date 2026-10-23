#!/usr/bin/env node
// Prints the release-walk/v1 list a walker follows. It reads the map and writes nothing.
import { execFileSync } from 'node:child_process'
import { readFileSync, realpathSync } from 'node:fs'
import { basename, dirname, relative, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { parse } from 'yaml'
import { iterStories } from './model.mjs'

export const WALK_SCHEMA = 'release-walk/v1'

const git = (dir, ...args) => execFileSync('git', ['-C', dir, ...args], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim()

export function sourceOf(path) {
	const file = resolve(path)
	const dir = dirname(file)
	try {
		const root = realpathSync(git(dir, 'rev-parse', '--show-toplevel'))
		const rel = relative(root, realpathSync(file))
		const dirty = git(dir, 'status', '--porcelain', '--', file) !== ''
		const commit = dirty ? '' : git(dir, 'log', '-1', '--format=%H', '--', file)
		return { file: rel, commit: commit || null }
	} catch {
		return { file: basename(file), commit: null }
	}
}

export function buildWalk(model, releaseId, source) {
	const release = (model.releases ?? []).find((r) => r.id === releaseId)
	if (!release) throw new Error(`no release "${releaseId}" in this journey`)
	if (typeof release.goal !== 'string' || !release.goal.trim()) throw new Error(`release "${releaseId}" has no goal, so the walk has no proof line`)
	const rows = iterStories(model).filter((s) => s.release === releaseId)
	if (!rows.length) throw new Error(`release "${releaseId}" holds no stories`)
	const rules = new Map((model.rules ?? []).map((r) => [r.id, r.text]))
	return {
		schema: WALK_SCHEMA,
		journey: model.journey,
		persona: model.persona ?? null,
		one_journey: model.one_journey ?? null,
		release: { id: release.id, name: release.name ?? null, goal: release.goal },
		source,
		proof_line: release.goal,
		stories: rows.map((row, i) => ({
			order: i + 1,
			id: row.id,
			card: row.card,
			step: { id: row.step.id, card: row.step.card ?? null, activity: row.step.activity ?? null },
			status: row.status ?? null,
			evidence: row.evidence ?? null,
			system: row.step.system ?? [],
			rules: (row.step.rules ?? []).map((id) => ({ id, text: rules.get(id) ?? id })),
		})),
	}
}

if (process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) {
	const [path, releaseId] = process.argv.slice(2)
	if (!path || !releaseId) {
		console.error('usage: journey-walk.mjs <journey.yaml> <releaseId>')
		process.exitCode = 2
	} else {
		try {
			const doc = buildWalk(parse(readFileSync(path, 'utf8')), releaseId, sourceOf(path))
			console.log(JSON.stringify(doc, null, 2))
		} catch (error) {
			console.error(`WALK REFUSED: ${error.message}`)
			process.exitCode = 1
		}
	}
}
