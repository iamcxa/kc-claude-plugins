#!/usr/bin/env node
import { readProgress, readReport } from './progress.mjs'
import { loadJourney, renderToRoom, PROJECTION_KEYS } from './render.mjs'

const usage = 'usage: journey-progress.mjs <journey.yaml> --workflow-dir <dir> [--report <slug> | --draw <room>] [--pages story-map,journey-board,function-map]'
let progress
try {
	const [path, ...args] = process.argv.slice(2)
	const options = {}
	if (!path || path.startsWith('--')) throw new Error(usage)
	for (let i = 0; i < args.length; i += 2) {
		const flag = args[i], value = args[i + 1]
		if (!['--workflow-dir', '--draw', '--pages', '--report'].includes(flag) || options[flag] || !value || value.startsWith('--')) throw new Error(usage)
		options[flag] = value
	}
	const selection = options['--pages']?.split(',')
	if (!options['--workflow-dir'] || (options['--report'] && options['--draw']) || (selection && (!options['--draw'] || selection.some((p) => !PROJECTION_KEYS.includes(p))))) throw new Error(usage)
	const model = loadJourney(path)
	if (options['--report']) {
		console.log(readReport(model, options['--workflow-dir'], options['--report']))
	} else {
		progress = readProgress(model, options['--workflow-dir'])
		if (options['--draw']) {
			const drawn = await renderToRoom({ path, room: options['--draw'], selection, progress })
			if (drawn.status < 200 || drawn.status >= 300) throw new Error(`Drawing failed: ${drawn.status} ${drawn.body}`)
			console.log(JSON.stringify({ progress, drawn }, null, 2))
		} else console.log(JSON.stringify(progress, null, 2))
		if (progress.stories.some((s) => s.status === 'unverified') || progress.diagnostic || progress.orphans.length || !progress.stories.length || progress.releases.some((r) => r.status === 'unverified')) process.exitCode = 1
	}
} catch (error) {
	if (error.exitCode === 1) {
		console.log(`journey progress not run: ${error.message.replace(/\s+/g, ' ')}`)
		process.exitCode = 1
	} else {
		console.error(JSON.stringify({ error: error.message, ...(progress ? { progress, drawn: false } : {}) }, null, 2))
		process.exitCode = progress ? 1 : 2
	}
}
