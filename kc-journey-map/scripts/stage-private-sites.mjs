import { readFile, writeFile, cp, access, mkdir } from 'node:fs/promises'
import { resolve, join } from 'node:path'

const [siteArg, buildArg] = process.argv.slice(2)
if (!siteArg || !buildArg) throw new Error('usage: <supported Sites source checkout> <generated private entry build>')
const site = resolve(siteArg), build = resolve(buildArg)
const config = JSON.parse(await readFile(join(build, 'sites-config.json'), 'utf8'))
const { validateSitesJourneyConfig } = await import(new URL('../server/sites-entry.ts', import.meta.url))
validateSitesJourneyConfig(config)
const worker = join(site, 'build/sites-worker.ts')
const before = await readFile(worker, 'utf8')
const anchor = '  fetch(request: Request, env: Cloudflare.Env, ctx: ExecutionContext<{ CONNECTORS?: ConnectorBinding }>) {'
if (before.split(anchor).length !== 2 || before.includes('journeyPrivateEntry')) throw new Error('Worker shape changed or entry already staged; inspect before integration')
const destination = join(site, 'lib/journey-private')
const assets = join(site, 'public', config.pathPrefix.slice(1))
for (const path of [destination, assets, join(build, 'sites-worker-before.ts')]) {
	try { await access(path) } catch { continue }
	throw new Error('Staging destination or receipt already exists; preserve it')
}
const imports = 'import { createSitesJourneyEntry } from "../lib/journey-private/sites-entry.mjs";\nimport journeyPrivateConfig from "../lib/journey-private/sites-config.json";\nconst journeyPrivateEntry = createSitesJourneyEntry(journeyPrivateConfig);\n'
const replacement = anchor.replace('  fetch(', '  async fetch(') + '\n    const journeyPrivate = await journeyPrivateEntry(request, env as unknown as { JOURNEY_SITES_BEARER?: string });\n    if (journeyPrivate) return journeyPrivate;'
const after = imports + before.replace(anchor, replacement)
await mkdir(destination, { recursive: true })
for (const file of ['sites-entry.mjs', 'sites-config.json', 'build-mode.json']) await cp(join(build, file), join(destination, file), { errorOnExist: true, force: false })
await cp(join(build, 'public', config.pathPrefix.slice(1)), assets, { recursive: true, errorOnExist: true, force: false })
await writeFile(join(build, 'sites-worker-before.ts'), before, { flag: 'wx', mode: 0o600 })
await writeFile(worker, after)
if (after.slice(imports.length).replace(replacement, anchor) !== before) throw new Error('Unexpected integration delta')
console.log(JSON.stringify({ staged: true, preservedExistingHandler: true, published: false, environmentKey: 'JOURNEY_SITES_BEARER' }))
