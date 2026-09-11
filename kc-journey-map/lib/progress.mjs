import { execFileSync } from 'node:child_process'
import { realpathSync } from 'node:fs'
import { resolve } from 'node:path'

const fields = ['journey', 'journey-release', 'journey-story', 'journey-required-tasks', 'journey-mapping-complete', 'status']
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

export function calculateProgress(model, tasks, diagnostic = null) {
	const releases = model.releases ?? []
	const stories = (model.steps ?? []).flatMap((step) => step.stories ?? [])
	return stories.map((story) => {
		const identity = [model.journey, story?.release, story?.id]
		const result = { journey: identity[0], release: identity[1], story: identity[2], status: 'unverified', requiredTasks: 0, doneTasks: 0, taskIds: [] }
		try {
			if (diagnostic) fail(diagnostic)
			if (!identity.every(nonempty) || stories.filter((s) => s?.id === story.id).length !== 1 ||
				releases.filter((r) => r.id === story.release).length !== 1) fail('Missing or duplicate explicit journey/release/story identity')
			const members = tasks.filter((t) => key(tuple(t)) === key(identity))
			const declarations = members.filter((t) => fields.slice(3, 5).some((f) => Object.hasOwn(t, f)))
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

export function readProgress(model, workflowDir) {
	const source = resolve(workflowDir)
	const deadline = Date.now() + 30_000
	const run = (...args) => {
		const timeout = deadline - Date.now()
		if (timeout <= 0) fail('Task observation exceeded 30 seconds')
		return JSON.parse(execFileSync('spacedock', ['status', '--workflow-dir', source, ...args, '--json'],
			{ encoding: 'utf8', timeout, maxBuffer: 8 * 1024 * 1024, stdio: ['ignore', 'pipe', 'pipe'] }))
	}
	let tasks = [], diagnostic = null
	try {
		const wanted = new Set((model.steps ?? []).flatMap((s) => (s.stories ?? []).map((t) => key([model.journey, t?.release, t?.id]))))
		const selected = (rows) => rows.filter((r) => wanted.has(key(tuple(r))))
		const list = () => taskListing(run('--archived', '--all-fields', '--limit', '0'))
		const initial = selected(list())
		const read = (ref) => {
			const resolved = run('--resolve', ref, '--archived')
			if (!nonempty(resolved.path) || !nonempty(resolved.stored_id)) fail('Ambiguous task resolution')
			const record = run('--read', resolved.path)
			if (realpathSync(record.path) !== realpathSync(resolved.path) || record.frontmatter?.id !== resolved.stored_id) fail('Resolved task identity changed')
			return { resolved, task: record.frontmatter }
		}
		for (const row of initial) {
			const { resolved, task } = read(row.slug)
			if (resolved.slug !== row.slug || !task.id.startsWith(row.id) || fields.some((f) => (row[f] ?? '') !== (task[f] ?? ''))) fail('Task changed during observation')
			tasks.push(task)
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
	const stories = calculateProgress(model, tasks, diagnostic)
	return { schema: 'journey-progress/v1', journey: model.journey, source, observedAt: new Date().toISOString(), diagnostic, stories,
		releases: (model.releases ?? []).map((release) => {
			const members = stories.filter((s) => s.release === release.id)
			const doneStories = members.filter((s) => s.status === 'exists').length
			return { release: release.id, totalStories: members.length, doneStories,
				requiredTasks: members.reduce((n, s) => n + s.requiredTasks, 0), doneTasks: members.reduce((n, s) => n + s.doneTasks, 0),
				status: members.length && doneStories === members.length ? 'exists' : members.some((s) => s.status === 'gap') ? 'gap' : 'unverified',
				acceptance: members.length && doneStories === members.length ? 'pending delivery acceptance' : 'delivery acceptance not established' }
		}) }
}
