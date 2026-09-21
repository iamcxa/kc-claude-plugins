#!/usr/bin/env node
import { addStory } from './add-story.mjs'

const [path, stepId, id, card] = process.argv.slice(2)

if (!path || !stepId || !id || !card) {
	console.error('usage: journey-add-story.mjs <journey.yaml> <stepId> <storyId> "<card>"')
	console.error('  card is the words the person used, quoted verbatim — not a rewrite')
	process.exit(2)
}

try {
	const { wrote } = addStory(path, { stepId, id, card })
	console.log(`added story "${id}" under step "${stepId}" -> ${wrote}`)
	console.log(`next: node lib/journey-lint.mjs ${path} <repoRoot>`)
} catch (err) {
	console.error(err.message)
	process.exit(1)
}
