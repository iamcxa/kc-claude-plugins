#!/usr/bin/env node
// Folds journey-footprint/v1 lines into a draft of a journey file by splicing text, so every
// byte outside the folded questions' own lines stays as written. The source file is never written.
import { readFileSync, realpathSync, writeFileSync } from 'node:fs'
import { pathToFileURL } from 'node:url'
import { isDeepStrictEqual } from 'node:util'
import { isMap, isSeq, parse, parseDocument } from 'yaml'
import { afterLine, lineStart } from './add-story.mjs'

export const FOOTPRINT_WIRE = 'journey-footprint/v1'
const REQUIRED = ['id', 'task', 'journey', 'story', 'question', 'words', 'date', 'source', 'answer']
const text = (value) => typeof value === 'string' && value.trim().length > 0
const quote = (value) => JSON.stringify(value)

// A line of another major refuses the whole file; an unknown kind is returned as skipped.
export function readFootprints(path) {
	const lines = [], skipped = []
	readFileSync(path, 'utf8').split('\n').forEach((raw, i) => {
		if (!raw.trim()) return
		let line
		try { line = JSON.parse(raw) } catch { throw new Error(`${path}:${i + 1}: not JSON`) }
		if (line?.schema !== FOOTPRINT_WIRE) throw new Error(`${path}:${i + 1}: schema ${JSON.stringify(line?.schema)} is not ${FOOTPRINT_WIRE}`)
		if (line.kind !== 'answered') return skipped.push(line)
		const missing = REQUIRED.filter((f) => !text(line[f]))
		if (missing.length) throw new Error(`${path}:${i + 1}: missing ${missing.join(', ')}`)
		lines.push(line)
	})
	return { lines, skipped }
}

const keyOf = (pair) => pair.key?.value
const pairOf = (map, key) => map.items.find((p) => keyOf(p) === key)
const idOf = (map) => pairOf(map, 'id')?.value?.value

function findStories(doc, id) {
	const found = []
	for (const step of doc.get('steps')?.items ?? []) {
		for (const story of step.get?.('stories')?.items ?? []) if (isMap(story) && idOf(story) === id) found.push(story)
	}
	return found
}

function findQuestions(story, id) {
	const list = story.get('questions', true)
	const single = story.get('question', true)
	const items = isSeq(list) ? list.items : isMap(single) ? [single] : []
	return items.filter((q) => isMap(q) && idOf(q) === id)
}

const sourceOf = (fp) => ({ kind: fp.source.startsWith('amendment:') ? 'amendment' : 'gate', ref: `${fp.task}/${fp.source}`, words: fp.words, date: fp.date })
const sourceText = (s) => `{kind: ${s.kind}, ref: ${quote(s.ref)}, words: ${quote(s.words)}, date: ${quote(s.date)}}`

function editsFor(src, q, fp, have) {
	const edits = []
	const fresh = []
	const set = (key, textValue) => {
		const pair = pairOf(q, key)
		if (!pair) return fresh.push([key, textValue])
		if (!pair.value) return fresh.push([key, textValue])
		edits.push({ start: pair.value.range[0], end: pair.value.range[1], text: textValue })
	}
	if (have.answer !== fp.answer) set('answer', quote(fp.answer))
	if (have.status !== 'answered') set('status', 'answered')
	fresh.push(['source', sourceText(sourceOf(fp))])
	if (q.flow) {
		const end = Math.max(...q.items.map((p) => (p.value?.range ?? p.key.range)[1]))
		edits.push({ start: end, end, text: fresh.map(([k, v]) => `, ${k}: ${v}`).join('') })
	} else {
		const end = Math.max(...q.items.map((p) => (p.value?.range ?? p.key.range)[1]))
		const first = q.items[0].key.range[0]
		const indent = ' '.repeat(first - lineStart(src, first))
		const at = afterLine(src, Math.max(end - 1, first))
		const lead = at > 0 && src[at - 1] !== '\n' ? '\n' : ''
		edits.push({ start: at, end: at, text: lead + fresh.map(([k, v]) => `${indent}${k}: ${v}\n`).join('') })
	}
	return edits
}

// Returns {draft, results}; each result is {id, outcome, detail}. Throws before returning a
// draft that differs from the source by anything other than the folded questions' fields.
export function planFold(src, footprints) {
	const doc = parseDocument(src)
	if (doc.errors.length) throw new Error(`journey file is not readable YAML: ${doc.errors[0].message}`)
	const journey = doc.get('journey')
	const expected = parse(src)
	const results = [], edits = [], touched = new Map()
	const result = (fp, outcome, detail = '') => results.push({ id: fp.id, outcome, detail })
	for (const fp of footprints) {
		if (fp.journey !== journey) { result(fp, 'wrong-journey', `${fp.journey} is not ${journey}`); continue }
		const stories = findStories(doc, fp.story)
		if (!stories.length) { result(fp, 'no-story', fp.story); continue }
		if (stories.length > 1) { result(fp, 'ambiguous', `story ${quote(fp.story)} matches ${stories.length} stories`); continue }
		const questions = findQuestions(stories[0], fp.question)
		if (!questions.length) { result(fp, 'no-question', `${fp.story}/${fp.question}`); continue }
		if (questions.length > 1) { result(fp, 'ambiguous', `question ${quote(fp.question)} in story ${quote(fp.story)} matches ${questions.length} questions`); continue }
		const q = questions[0]
		const key = `${fp.story}/${fp.question}`
		const prior = touched.get(key)
		const have = prior ?? {
			answer: pairOf(q, 'answer')?.value?.value,
			status: pairOf(q, 'status')?.value?.value,
			ref: pairOf(q, 'source')?.value?.get?.('ref'),
		}
		const ref = sourceOf(fp).ref
		if (have.ref === ref) {
			if (have.answer === fp.answer && have.status === 'answered') result(fp, 'already')
			else result(fp, 'conflict', `${key} was folded from this ruling but its ${have.answer === fp.answer ? 'status' : 'answer'} no longer matches`)
			continue
		}
		if (have.ref || (have.answer && have.answer !== fp.answer)) { result(fp, 'conflict', `${key} already holds a different ${have.ref ? 'source' : 'answer'}`); continue }
		edits.push(...editsFor(src, q, fp, have))
		touched.set(key, { answer: fp.answer, status: 'answered', ref })
		const target = expected.steps.flatMap((s) => s.stories ?? []).find((s) => s?.id === fp.story)
		const list = Array.isArray(target.questions) ? target.questions : [target.question]
		const mirror = list.find((x) => x?.id === fp.question)
		Object.assign(mirror, { answer: fp.answer, status: 'answered', source: sourceOf(fp) })
		result(fp, 'applied', key)
	}
	let draft = src
	for (const e of edits.sort((a, b) => b.start - a.start || b.end - a.end)) draft = draft.slice(0, e.start) + e.text + draft.slice(e.end)
	const check = parseDocument(draft)
	if (check.errors.length || !isDeepStrictEqual(parse(draft), expected)) {
		throw new Error('the folded draft would differ from the source by more than the folded questions; no draft written')
	}
	return { draft, results }
}

export const FAILING = new Set(['conflict', 'ambiguous', 'no-story', 'no-question', 'wrong-journey'])

function main(argv) {
	const usage = 'usage: journey-fold.mjs <journey.yaml> --footprints <footprints.jsonl> [--footprints <more>] --out <draft.yaml>'
	const [path, ...rest] = argv
	const footprints = []
	let out
	for (let i = 0; i < rest.length; i += 2) {
		if (rest[i] === '--footprints' && rest[i + 1]) footprints.push(rest[i + 1])
		else if (rest[i] === '--out' && rest[i + 1] && !out) out = rest[i + 1]
		else throw new Error(usage)
	}
	if (!path || !footprints.length || !out) throw new Error(usage)
	const read = footprints.map(readFootprints)
	const { draft, results } = planFold(readFileSync(path, 'utf8'), read.flatMap((r) => r.lines))
	const ambiguous = results.filter((r) => r.outcome === 'ambiguous')
	if (ambiguous.length) throw new Error(`refused, no draft written: ${ambiguous.map((r) => `${r.id} ${r.detail}`).join('; ')}`)
	// 'wx': an earlier draft is not evidence for this run.
	writeFileSync(out, draft, { flag: 'wx' })
	for (const r of results) console.log(`${r.outcome} ${r.id}${r.detail ? ` ${r.detail}` : ''}`)
	for (const s of read.flatMap((r) => r.skipped)) console.log(`skipped ${s.id ?? '?'} kind ${JSON.stringify(s.kind)}`)
	console.log(`draft ${out}`)
	return results.some((r) => FAILING.has(r.outcome)) ? 1 : 0
}

if (process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) {
	try { process.exitCode = main(process.argv.slice(2)) } catch (error) { console.error(error.message); process.exitCode = 1 }
}
