import { readFile, mkdir, readdir, writeFile } from 'node:fs/promises'
import { resolve, join } from 'node:path'
import { build as viteBuild } from 'vite'
import { build as bundle } from 'esbuild'

const root = new URL('..', import.meta.url).pathname.replace(/\/$/, '')
const args = process.argv.slice(2)
const value = flag => args[args.indexOf(flag) + 1]
if (!args.includes('--config') || !args.includes('--out') || args.some(arg => arg.startsWith('--') && !['--config', '--out', '--development'].includes(arg))) throw new Error('usage: --config <private JSON> --out <empty output directory> [--development]')
const out = resolve(value('--out')), config = JSON.parse(await readFile(resolve(value('--config')), 'utf8'))
const { outputFiles } = await bundle({ entryPoints: [join(root, 'server/sites-entry.ts')], bundle: true, format: 'esm', platform: 'browser', write: false })
const source = outputFiles[0].text
const { validateSitesJourneyConfig } = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'))
validateSitesJourneyConfig(config)
await mkdir(out, { recursive: true })
if ((await readdir(out)).length) throw new Error('Output directory must be empty; preserve earlier build receipts')
const development = args.includes('--development')
await viteBuild({ configFile: join(root, 'vite.config.mts'), base: config.pathPrefix + '/', mode: development ? 'development' : 'production',
 define: { 'import.meta.env.VITE_JOURNEY_API_URL': JSON.stringify(config.pathPrefix + '/api'), ...(development ? { 'process.env.NODE_ENV': JSON.stringify('development') } : {}) },
 build: { outDir: join(out, 'public', config.pathPrefix.slice(1)), emptyOutDir: false } })
await writeFile(join(out, 'sites-entry.mjs'), source)
await writeFile(join(out, 'sites-config.json'), JSON.stringify(config, null, 2))
await writeFile(join(out, 'build-mode.json'), JSON.stringify({ mode: development ? 'private-development' : 'production', licenseEnforcement: 'unchanged', productionLicenseConfigured: !!process.env.VITE_TLDRAW_LICENSE_KEY, assets: false }, null, 2))
console.log(JSON.stringify({ output: out, mode: development ? 'private-development' : 'production', published: false }))
