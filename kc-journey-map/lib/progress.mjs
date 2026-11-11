import { execFileSync } from 'node:child_process'
import { realpathSync } from 'node:fs'
import { resolve } from 'node:path'

const fields = ['journey', 'journey-release', 'journey-story', 'journey-required-tasks', 'journey-mapping-complete', 'status', 'pr']
const tuple = (task) => [task.journey, task['journey-release'], task['journey-story']]
const key = (parts) => JSON.stringify(parts)
const nonempty = (value) => typeof value === 'string' && value.trim().length > 0
const fail = (message) => { throw new Error(message) }

export function taskListing(response) {
	const { entities, pagination: p } = response ?? {}
	if (!Array.isArray(entities) || p?.has_next !== 'false' || !/^\d+$/.test(p?.total ?? '') ||
		Number(p.total) !== entities.length || p.page !== '1' || p.limit !== '0' ||
		entities.some((r) => !r || !nonempty(r.slug) || !nonempty(r.id))) fail('Incomplete or malformed task listing')
	return entities
}

const onMap = (model) => new Set((model.steps ?? []).flatMap((step) => (step.stories ?? []).map((s) => key([model.journey, s?.release, s?.id]))))

// A task that names this journey but a release/story pair the map does not hold was admitted before the map was updated.
export function findOrphans(model, rows) {
	const wanted = onMap(model)
	return rows.filter((r) => r.journey === model.journey && !wanted.has(key(tuple(r))))
		.map((r) => ({ slug: r.slug, id: r.id, release: r['journey-release'] ?? null, story: r['journey-story'] ?? null }))
}

function pullRequestRef(value, origin) {
	const repo = origin?.match(/^(?:git@github\.com:|https:\/\/github\.com\/|ssh:\/\/git@github\.com\/)([^/]+\/[^/]+?)(?:\.git)?\/?$/)?.[1]
	const number = value.match(/^(?:pr-merge:|#)?(\d+)$/)?.[1]
	if (number) return `${repo ?? ''}#${number}`
	const url = value.match(/^https:\/\/github\.com\/([^/]+\/[^/]+)\/pull\/(\d+)\/?$/)
	if (url) return `${url[1]}#${url[2]}`
	return value.replace(/^local-merge:([0-9a-f]+)$/i, (_, sha) => `local merge ${sha.slice(0, 7)}`)
}

export function calculateProgress(model, tasks, diagnostic = null, origin = null) {
	const releases = model.releases ?? []
	const stories = (model.steps ?? []).flatMap((step) => step.stories ?? [])
	return stories.map((story) => {
		const identity = [model.journey, story?.release, story?.id]
		const members = tasks.filter((t) => key(tuple(t)) === key(identity))
		const done = members.filter((t) => t.status === 'done')
		const result = { journey: identity[0], release: identity[1], story: identity[2], status: 'unverified', requiredTasks: 0, doneTasks: 0, taskIds: [],
			members: { tasks: members.length, done: done.length, prs: done.filter((t) => nonempty(t.pr)).map((t) => ({ task: t.slug, ref: pullRequestRef(t.pr, origin) })) } }
		try {
			if (diagnostic) fail(diagnostic)
			if (!identity.every(nonempty) || stories.filter((s) => s?.id === story.id).length !== 1 ||
				releases.filter((r) => r.id === story.release).length !== 1) fail('Missing or duplicate explicit journey/release/story identity')
			const declarations = members.filter((t) => fields.slice(3, 5).some((f) => nonempty(String(t[f] ?? ''))))
			if (declarations.length !== 1 || declarations[0]['journey-mapping-complete'] !== 'true') fail('One confirmed complete mapping is required')
			const owner = declarations[0]
			const required = JSON.parse(owner['journey-required-tasks'])
			if (!Array.isArray(required) || !required.length || !required.every(nonempty) || new Set(required).size !== required.length ||
				!required.includes(owner.id)) fail('Required IDs must be unique, nonempty full IDs including the declaring task')
			if (new Set(members.map((t) => t.id)).size !== members.length || members.some((t) => !nonempty(t.status)) ||
				key([...required].sort()) !== key(members.map((t) => t.id).sort())) fail('Required mapping differs from readable task membership')
			result.taskIds = [...required].sort()
			result.requiredTasks = required.length
			result.doneTasks = members.filter((t) => t.status === 'done').length
			result.status = result.doneTasks === required.length ? 'exists' : 'gap'
		} catch (error) { result.diagnostic = error.message }
		return result
	})
}

function observeProgress(model, workflowDir) {
	const source = resolve(workflowDir)
	const deadline = Date.now() + 30_000
	const run = (...args) => {
		const timeout = deadline - Date.now()
		if (timeout <= 0) fail('Task observation exceeded 30 seconds')
		return JSON.parse(execFileSync('spacedock', ['status', '--workflow-dir', source, ...args, '--json'],
			{ encoding: 'utf8', timeout, maxBuffer: 8 * 1024 * 1024, stdio: ['ignore', 'pipe', 'pipe'] }))
	}
	let tasks = [], listed = [], orphans = [], diagnostic = null, origin = null
	try { origin = execFileSync('git', ['-C', source, 'remote', 'get-url', 'origin'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim() } catch {}
	try {
		const wanted = onMap(model)
		const selected = (rows) => rows.filter((r) => wanted.has(key(tuple(r))))
		const list = () => taskListing(run('--archived', '--all-fields', '--limit', '0'))
		listed = list()
		orphans = findOrphans(model, listed)
		const initial = selected(listed)
		const read = (ref) => {
			const resolved = run('--resolve', ref, '--archived')
			if (!nonempty(resolved.path)) fail('Ambiguous task resolution')
			const stored = nonempty(resolved.stored_id) ? resolved.stored_id : ''
			const identity = stored || (nonempty(resolved.slug) && resolved.id === resolved.slug ? resolved.slug : fail('Ambiguous task resolution'))
			const record = run('--read', resolved.path)
			if (realpathSync(record.path) !== realpathSync(resolved.path) || (record.frontmatter?.id ?? '') !== stored) fail('Resolved task identity changed')
			return { resolved, task: { ...record.frontmatter, id: identity } }
		}
		for (const row of initial) {
			const { resolved, task } = read(row.slug)
			if (resolved.slug !== row.slug || !task.id.startsWith(row.id) || fields.some((f) => (row[f] ?? '') !== (task[f] ?? ''))) fail('Task changed during observation')
			tasks.push({ ...task, slug: row.slug })
		}
		for (const owner of tasks.filter((t) => Object.hasOwn(t, 'journey-required-tasks'))) {
			let ids
			try { ids = JSON.parse(owner['journey-required-tasks']) } catch { continue }
			if (!Array.isArray(ids) || !ids.every(nonempty)) continue
			for (const id of new Set(ids)) {
				const { task } = read(id)
				const member = tasks.find((t) => t.id === id)
				if (task.id !== id || !member || fields.some((f) => task[f] !== member[f])) fail('Required full ID is missing, mismatched, or changed')
			}
		}
		const stamp = (rows) => key(rows.map((r) => [r.slug, r.id, ...fields.map((f) => r[f])]).sort((a, b) => key(a).localeCompare(key(b))))
		if (stamp(initial) !== stamp(selected(list()))) fail('Task listing changed during observation; refresh again')
	} catch (error) { diagnostic = `Local task observation unavailable: ${String(error.message).slice(0, 300)}` }
	const stories = calculateProgress(model, tasks, diagnostic, origin)
	const progress = { schema: 'journey-progress/v1', journey: model.journey, source, observedAt: new Date().toISOString(), diagnostic, orphans, stories,
		releases: (model.releases ?? []).map((release) => {
			const members = stories.filter((s) => s.release === release.id)
			const doneStories = members.filter((s) => s.status === 'exists').length
			return { release: release.id, totalStories: members.length, doneStories,
				requiredTasks: members.reduce((n, s) => n + s.requiredTasks, 0), doneTasks: members.reduce((n, s) => n + s.doneTasks, 0),
				status: members.length && doneStories === members.length ? 'exists' : members.some((s) => s.status === 'gap') ? 'gap' : 'unverified',
				acceptance: members.length && doneStories === members.length ? 'pending delivery acceptance' : 'delivery acceptance not established',
				members: { storiesDone: members.filter((s) => s.members.tasks > 0 && s.members.done === s.members.tasks).length,
					storiesOpen: members.filter((s) => s.members.tasks > s.members.done).length,
					storiesEmpty: members.filter((s) => s.members.tasks === 0).length } }
		}) }
	return { progress, listed }
}

export function readProgress(model, workflowDir) {
	return observeProgress(model, workflowDir).progress
}

export function readReport(model, workflowDir, slug) {
	const { progress, listed } = observeProgress(model, workflowDir)
	if (progress.diagnostic) throw Object.assign(new Error(progress.diagnostic), { exitCode: 1 })
	const task = listed.find((t) => t.slug === slug && t.journey === model.journey)
	const release = progress.releases.find((r) => r.release === task?.['journey-release'])
	if (!task || !release) throw new Error(`Task ${slug} names no release of this map`)
	const stories = progress.stories.filter((s) => s.release === release.release)
	const done = stories.filter((s) => s.members.tasks > 0 && s.members.done === s.members.tasks)
	const open = stories.filter((s) => s.members.tasks > s.members.done)
	const noStory = listed.filter((t) => t.journey === model.journey && t['journey-release'] === release.release && !nonempty(t['journey-story']))
	const noStoryDone = noStory.filter((t) => t.status === 'done').length
	const orphans = progress.orphans.filter((o) => o.release === release.release && nonempty(o.story)).length
	const current = stories.find((s) => s.story === task['journey-story'])
	const refs = (s) => [...new Set(s.members.prs.map((p) => p.ref))]
	const list = (rows, show, limit) => rows.length ? rows.slice(0, limit).map(show).concat(rows.length > limit ? [`and ${rows.length - limit} more`] : []).join(', ') : 'none'
	const complete = stories.length > 0 && done.length === stories.length && noStoryDone === noStory.length && !orphans
	const lines = (limit) => [
		`journey progress: ${model.journey}/${release.release} after ${slug} (${task.status})`,
		...(nonempty(task['journey-story']) ? [
			`story ${task['journey-story']}: ${current?.members.done ?? 0} of ${current?.members.tasks ?? 0} filed tasks done; declared: ${current?.status ?? 'none'}`,
			`pull requests: ${current ? list(refs(current), (ref) => ref, 3) : 'none recorded'}`.replace(/: none$/, ': none recorded'),
		] : []),
		`release ${release.release}: ${done.length} of ${stories.length} stories have every filed task done; ${open.length} in progress; ${release.members.storiesEmpty} have no task${complete ? '; complete by filed tasks' : ''}`,
		`done: ${list(done, (s) => `${s.story} (${refs(s).slice(0, 3).join(', ') || 'none recorded'})`, limit)}`,
		`in progress: ${list(open, (s) => `${s.story} ${s.members.done}/${s.members.tasks}`, limit)}`,
		...(noStory.length ? [`release tasks with no story: ${noStoryDone} of ${noStory.length} done`] : []),
		...(orphans ? [`not on the map: ${orphans} tasks name a story this map does not hold`] : []),
		'canvas: not redrawn; draw it with kc-journey-progress',
	]
	let limit = 5
	while (limit > 0 && lines(limit).join('\n').split(/\s+/).length > 160) limit--
	return lines(limit).join('\n')
}
