#!/usr/bin/env node
// The field tables kc-journey-map produces for other tools, each with one version bound to the
// hash of its printed table in contract-versions.json.
import { createHash } from 'node:crypto'
import { readFileSync, realpathSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

export const SCHEMAS = {
	'journey-map-question': [
		['id', 'explicit string, unique inside its story; a question without one cannot be folded'],
		['ask, status, because, answer, doc', 'as `model.mjs` reads them; `status` is `open`, `answered` or `deferred`; `because` is owed when `deferred`'],
		['source', '`{kind: gate, amendment or release, ref: "<task slug>/<footprint source>" for gate and amendment, "<journey>/<release-id>" for release, words, date}`; optional; gate and amendment written by journey-fold.mjs, release by a release preparation before any task exists'],
	],
	'release-walk': [
		['schema', 'the string `release-walk/v1` (wire pin: major only)'],
		['journey, persona, one_journey', 'from the map; `persona` and `one_journey` are null when the map lacks them'],
		['release', '`{id, name, goal}` of the release walked'],
		['source', '`{file, commit}`: the journey file path relative to its git root and the last commit that touched it; `commit` is null when git cannot say or the file has uncommitted edits'],
		['proof_line', 'the release `goal`, verbatim; the walk refuses a release with no goal or no stories'],
		['stories', '`[{order, id, card, step, status, evidence, system, rules}]` in step order, then story order inside the step; `order` counts from 1; the map holds no URL or route, so no entry point is listed'],
		['stories[].step', '`{id, card, activity}` of the step the story sits under'],
		['stories[].system, rules', 'the step\'s `system` lines; `rules` is `[{id, text}]`, the step\'s rule ids joined to the map\'s `rules`, `text` being the id when the map holds no such rule'],
	],
}
export const ADR_TITLE = 'a-captain-ruling-reaches-the-map-as-a-versioned-footprint'
export const ACCEPTANCE_ADR_TITLE = 'a-release-is-accepted-by-walking-it-and-the-plugins-meet-at-two-named-schemas'
export const ADR_TITLES = { 'journey-map-question': ADR_TITLE, 'release-walk': ACCEPTANCE_ADR_TITLE }
const here = dirname(fileURLToPath(import.meta.url))
export const VERSIONS_FILE = join(here, 'contract-versions.json')

export const tableText = (name) => `| field | rule |\n|---|---|\n${SCHEMAS[name].map(([f, r]) => `| \`${f}\` | ${r} |`).join('\n')}`
export const tableHash = (name) => createHash('sha256').update(tableText(name)).digest('hex')

export const footer = (name) => [
	`Current table: node kc-journey-map/lib/schemas.mjs ${name}`,
	'Every version: kc-journey-map/CHANGELOG.md, written by release-please from each commit.',
	`First shape and each MAJOR: an ADR in the kc-claude-plugins docs/adr/ (${ADR_TITLES[name]}).`,
	'Read the CHANGELOG when a consumer refuses a version or a record carries a field you do not know; read the ADR before removing or renaming a field.',
].join('\n')

// Returns the failure text for a schema, or null when its current version binds its table.
export function versionProblem(name, versionsFile = VERSIONS_FILE) {
	if (!SCHEMAS[name]) return `unknown schema ${JSON.stringify(name)}; known: ${Object.keys(SCHEMAS).join(', ')}`
	let entry
	try { entry = JSON.parse(readFileSync(versionsFile, 'utf8'))[name] } catch { return `${name}: ${versionsFile} is unreadable` }
	if (!entry) return `${name}: ${versionsFile} lacks the schema`
	const recorded = entry.versions?.[entry.current]
	if (!recorded) return `${name}: current version ${entry.current} has no recorded hash`
	if (recorded !== tableHash(name)) return `${name}: the field table changed but version ${entry.current} did not; bump current and record the new hash ${tableHash(name)}`
	return null
}

export const currentVersion = (name, versionsFile = VERSIONS_FILE) => JSON.parse(readFileSync(versionsFile, 'utf8'))[name]?.current

if (process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) {
	const name = process.argv[2]
	const problem = versionProblem(name)
	if (SCHEMAS[name]) console.log(`${name} ${currentVersion(name)}\n${tableText(name)}\n${footer(name)}`)
	if (problem) { console.error(problem); process.exitCode = 1 }
}
