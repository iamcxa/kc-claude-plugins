#!/usr/bin/env node
// Counts what has not reached a journey file: rulings recorded as footprints on archived tasks
// that the file does not hold (`unfolded`), and open questions on stories whose tasks are all
// archived (`stale-open`). Prints no timestamp, so two runs on the same inputs print the same bytes.
import { execFileSync } from 'node:child_process'
import { existsSync, readFileSync, realpathSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { parse } from 'yaml'
import { FAILING, planFold, readFootprints } from './journey-fold.mjs'
import { taskListing } from './progress.mjs'

const hasText = (v) => typeof v === 'string' && v.trim().length > 0
const questionsOf = (story) => (Array.isArray(story.questions) ? story.questions : story.question ? [story.question] : [])
  .filter((q) => q && typeof q === 'object')

// answered: the file holds answer text or a doc link; deferred: no answer but a reason; else open.
export const stateOf = (q) => (hasText(q.answer) || hasText(q.doc) ? 'answered' : q.status === 'deferred' && hasText(q.because) ? 'deferred' : 'open')

export function reconcile(src, tasks) {
	const model = parse(src)
	const stories = (model.steps ?? []).flatMap((s) => (s.stories ?? []).filter((x) => x && typeof x === 'object'))
	const questions = stories.flatMap((s) => questionsOf(s).map((q) => ({ story: s.id, ...q })))
	const ids = new Map()
	for (const q of questions) ids.set(q.id, (ids.get(q.id) ?? new Set()).add(q.story))
	const storyIds = stories.map((s) => s.id)
	const count = (state) => questions.filter((q) => stateOf(q) === state).length
	const mine = tasks.filter((t) => t.journey === model.journey && hasText(t.story))
	const archived = mine.filter((t) => t.archived)
	const pending = mine.filter((t) => !t.archived).flatMap((t) => t.footprints.map((fp) => fp.id))
	const { results } = planFold(src, archived.flatMap((t) => t.footprints))
	const unfolded = results.filter((r) => r.outcome !== 'already').map((r) => `${r.outcome} ${r.id}${r.detail ? ` ${r.detail}` : ''}`)
	const live = new Set(mine.filter((t) => !t.archived).map((t) => t.story))
	const staleStories = new Set(archived.map((t) => t.story).filter((id) => !live.has(id)))
	const stale = questions.filter((q) => staleStories.has(q.story) && stateOf(q) === 'open').map((q) => `${q.story}/${q.id}`)
	const counts = [
		['journey', model.journey],
		['stories', stories.length],
		['duplicate-story-ids', storyIds.length - new Set(storyIds).size],
		['questions', questions.length],
		['answered', count('answered')],
		['open', count('deferred') + count('open')],
		['deferred', count('deferred')],
		['plain-open', count('open')],
		['repeated-question-ids', [...ids.values()].filter((set) => set.size > 1).length],
		['unsourced', questions.filter((q) => stateOf(q) === 'answered' && !q.source).length],
		['unfolded', unfolded.length],
		['stale-open', stale.length],
		['pending', pending.length],
	]
	const skipped = tasks.flatMap((t) => t.skipped ?? []).map((s) => `skipped ${s.id ?? '?'} kind ${JSON.stringify(s.kind)}`)
	const lines = [
		...counts.map(([k, v]) => `${k} ${v}`),
		...unfolded.map((l) => `unfolded: ${l}`), ...stale.map((l) => `stale-open: ${l}`),
		...pending.map((l) => `pending: ${l}`), ...skipped,
	]
	return { lines, failing: unfolded.length > 0 || stale.length > 0, duplicateStories: storyIds.length !== new Set(storyIds).size }
}

// Reads journey tasks through the Spacedock CLI: the listing, then each journey task's folder.
export function readTasks(workflowDir) {
	const dir = resolve(workflowDir)
	if (!existsSync(join(dir, 'README.md'))) throw new Error(`${dir} is not a workflow directory: ${join(dir, 'README.md')} does not exist`)
	const run = (...args) => JSON.parse(execFileSync('spacedock', ['status', '--workflow-dir', dir, ...args, '--json'],
		{ encoding: 'utf8', maxBuffer: 8 * 1024 * 1024, stdio: ['ignore', 'pipe', 'pipe'] }))
	return taskListing(run('--archived', '--all-fields', '--limit', '0'))
		.filter((row) => hasText(row.journey) && hasText(row['journey-story']))
		.map((row) => {
			const file = run('--resolve', row.slug, '--archived').path
			const folder = file.replace(/\.md$/, '')
			const path = `${folder}/footprints.jsonl`
			const { lines, skipped } = existsSync(path) ? readFootprints(path) : { lines: [], skipped: [] }
			return { slug: row.slug, journey: row.journey, story: row['journey-story'], archived: file.split('/').includes('_archive'), footprints: lines, skipped }
		})
}

function main(argv) {
	const [path, flag, workflowDir, ...extra] = argv
	if (!path || flag !== '--workflow-dir' || !workflowDir || extra.length) {
		throw new Error('usage: journey-reconcile.mjs <journey.yaml> --workflow-dir <dir>')
	}
	const { lines, failing, duplicateStories } = reconcile(readFileSync(path, 'utf8'), readTasks(workflowDir))
	console.log(lines.join('\n'))
	return failing || duplicateStories ? 1 : 0
}

if (process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) {
	try { process.exitCode = main(process.argv.slice(2)) } catch (error) { console.error(error.message); process.exitCode = 1 }
}

export { FAILING }
