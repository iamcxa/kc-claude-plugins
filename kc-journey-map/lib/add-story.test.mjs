import assert from 'node:assert/strict'
import { test } from 'node:test'
import { execFileSync } from 'node:child_process'
import { mkdtempSync, readFileSync, writeFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { addStory } from './add-story.mjs'
import { loadModel } from './read.mjs'
import { lintJourney } from './lint.mjs'

const FIXTURE = `# header comment survives an add\njourney: fixture\nsteps:\n  - id: find-shop\n    card: "Find a shop"\n    stories:\n      - {id: enter-by-qr, release: r1, status: exists, evidence: EnterByQr, card: "Scan the shop's QR code"}\n      - {id: pick-nearby, status: gap, card: "Pick a nearby shop"}\n  - id: no-stories-yet\n    card: "A step with nothing under it yet"\n  - id: block-style\n    card: "A step whose stories are written block style, not flow"\n    stories:\n      - id: block-existing\n        card: "An existing block-style story"\n        status: exists\n        evidence: BlockExisting\n`

function fixture(t) {
	const dir = mkdtempSync(join(tmpdir(), 'add-story-'))
	t.after(() => rmSync(dir, { recursive: true, force: true }))
	execFileSync('git', ['init', '-q'], { cwd: dir })
	execFileSync('git', ['config', 'user.email', 'a@b.c'], { cwd: dir })
	execFileSync('git', ['config', 'user.name', 'test'], { cwd: dir })
	const path = join(dir, 'journey.yaml')
	writeFileSync(path, FIXTURE)
	execFileSync('git', ['add', '-A'], { cwd: dir })
	execFileSync('git', ['commit', '-q', '-m', 'init'], { cwd: dir })
	return { dir, path }
}

test('addStory inserts exactly one story line under the named step and touches nothing else', (t) => {
	const { path } = fixture(t)
	const before = readFileSync(path, 'utf8')
	addStory(path, { stepId: 'find-shop', id: 'shop-should-self-book', card: 'The shop should be able to create a booking itself' })
	const after = readFileSync(path, 'utf8')

	const beforeLines = before.split('\n')
	const afterLines = after.split('\n')
	assert.equal(afterLines.length, beforeLines.length + 1, 'exactly one line was added')
	// Every original line is still present, in order, somewhere in the new file.
	let cursor = 0
	for (const line of beforeLines) {
		cursor = afterLines.indexOf(line, cursor)
		assert.notEqual(cursor, -1, `original line dropped or reordered: ${JSON.stringify(line)}`)
		cursor += 1
	}
	assert.match(after, /^# header comment survives an add$/m, 'the header comment was preserved')
	assert.match(after, /\{id: shop-should-self-book, status: gap, card: "The shop should be able to create a booking itself"\}/, 'new story matches the flow/quote style of its siblings and carries no release')
})

test('addStory writes gap status and no evidence, and the file still lints clean for the new story', (t) => {
	const { dir, path } = fixture(t)
	addStory(path, { stepId: 'find-shop', id: 'new-one', card: 'A deferred capability' })
	const model = loadModel(path)
	const story = model.steps[0].stories.find((s) => s.id === 'new-one')
	assert.equal(story.status, 'gap')
	assert.equal(story.evidence, undefined)
	assert.equal(story.release, undefined)

	const violations = lintJourney(model, { repoRoot: dir, journeyPath: path })
	assert.deepEqual(violations.filter((v) => v.story === 'new-one'), [], 'the added story introduces no lint violation of its own')
})

test('addStory creates a stories list on a step that has none yet', (t) => {
	const { path } = fixture(t)
	addStory(path, { stepId: 'no-stories-yet', id: 'first-one', card: 'The first story under this step' })
	const model = loadModel(path)
	const step = model.steps.find((s) => s.id === 'no-stories-yet')
	assert.deepEqual(step.stories.map((s) => s.id), ['first-one'])
})

test('addStory matches a block-style sibling instead of defaulting to flow', (t) => {
	const { path } = fixture(t)
	addStory(path, { stepId: 'block-style', id: 'block-new', card: 'A new block-style story' })
	const after = readFileSync(path, 'utf8')
	assert.match(after, /- id: block-new\n\s+status: gap\n\s+card: "A new block-style story"/, 'the new story is written block style like its sibling, not flow')
	assert.doesNotMatch(after, /\{id: block-new/, 'the new story must not fall back to flow style next to a block-style sibling')
})

test('addStory refuses an unknown step', (t) => {
	const { path } = fixture(t)
	assert.throws(() => addStory(path, { stepId: 'nope', id: 'x', card: 'y' }), /step "nope" not found/)
})

test('addStory refuses a duplicate story id', (t) => {
	const { path } = fixture(t)
	assert.throws(() => addStory(path, { stepId: 'find-shop', id: 'pick-nearby', card: 'y' }), /"pick-nearby" already exists/)
})

test('addStory refuses missing stepId, id or card', (t) => {
	const { path } = fixture(t)
	assert.throws(() => addStory(path, { id: 'x', card: 'y' }), /stepId/)
	assert.throws(() => addStory(path, { stepId: 'find-shop', card: 'y' }), /needs id/)
	assert.throws(() => addStory(path, { stepId: 'find-shop', id: 'x' }), /needs card/)
})

// A journey written by a person or another tool: sequences not indented under
// their key, and a long card folded at its own width. Neither is the shape this
// module's serializer would choose, so re-serializing the file rewrites both.
const WRAPPED = `journey: wrapped
one_journey: A sentence long enough that the file's own writer folded it across two lines, which
  the serializer this module uses would unfold into one.
steps:
- id: enter
  card: Enter this review
  stories:
  - id: first
    card: The first story, whose card is also long enough that it was folded by the file's writer
      onto a second line
    release: r1
    status: gap
  rules:
  - some-rule
- id: read
  card: Read it
`

test('addStory appends only the new story to a file whose wrapping and indentation it would not choose', (t) => {
	const { path } = fixture(t)
	writeFileSync(path, WRAPPED)
	addStory(path, { stepId: 'enter', id: 'second', card: 'Show the current version number somewhere, so after an update I can tell which one I am on' })
	const after = readFileSync(path, 'utf8')
	const added = '  - id: second\n    status: gap\n    card: Show the current version number somewhere, so after an update I can tell which one I am on\n'
	assert.equal(after, WRAPPED.replace('    status: gap\n  rules:', `    status: gap\n${added}  rules:`), 'only the new story is added; every other byte is unchanged')
	const model = loadModel(path)
	assert.deepEqual(model.steps[0].stories.map((s) => s.id), ['first', 'second'])
	assert.deepEqual(model.steps[0].rules, ['some-rule'], 'the step keys after stories stay attached to the same step')
})

test('addStory adds a stories list to a step that has none, in the indentation the file already uses', (t) => {
	const { path } = fixture(t)
	writeFileSync(path, WRAPPED)
	addStory(path, { stepId: 'read', id: 'only', card: 'The first story here' })
	const after = readFileSync(path, 'utf8')
	assert.equal(after, `${WRAPPED}  stories:\n  - id: only\n    status: gap\n    card: The first story here\n`)
})
