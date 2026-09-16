import assert from 'node:assert/strict'
import { test } from 'node:test'
import { candidateRefSplits, isSafeGitToken, parseGithubBlobUrl } from './repo-doc.mjs'

test('parses a simple ref and path with a chapter', () => {
	assert.deepEqual(parseGithubBlobUrl('https://github.com/o/r/blob/main/docs/x.md#chapter'), {
		owner: 'o',
		repo: 'r',
		refAndPath: 'main/docs/x.md',
		chapter: 'chapter',
	})
})

test('parses without a chapter', () => {
	assert.deepEqual(parseGithubBlobUrl('https://github.com/o/r/blob/main/docs/x.md'), {
		owner: 'o',
		repo: 'r',
		refAndPath: 'main/docs/x.md',
		chapter: undefined,
	})
})

test('rejects a non-blob GitHub URL', () => {
	assert.equal(parseGithubBlobUrl('https://github.com/o/r/blame/abc/docs/x.md'), null)
})

test('rejects a non-GitHub URL', () => {
	assert.equal(parseGithubBlobUrl('https://example.com/o/r/blob/main/docs/x.md'), null)
})

test('rejects a ref-only match with no path segment', () => {
	assert.equal(parseGithubBlobUrl('https://github.com/o/r/blob/main'), null)
})

test('candidate splits try the longest ref prefix first, for a branch name containing "/"', () => {
	assert.deepEqual(candidateRefSplits('feature/foo/docs/x.md'), [
		{ ref: 'feature/foo/docs', path: 'x.md' },
		{ ref: 'feature/foo', path: 'docs/x.md' },
		{ ref: 'feature', path: 'foo/docs/x.md' },
	])
})

test('candidate splits cover a single-segment ref and multi-segment path', () => {
	assert.deepEqual(candidateRefSplits('main/docs/x.md'), [
		{ ref: 'main/docs', path: 'x.md' },
		{ ref: 'main', path: 'docs/x.md' },
	])
})

test('isSafeGitToken accepts an ordinary ref or path', () => {
	assert.equal(isSafeGitToken('main'), true)
	assert.equal(isSafeGitToken('docs/x.md'), true)
})

test('isSafeGitToken rejects a leading dash (git flag injection)', () => {
	assert.equal(isSafeGitToken('--upload-pack=evil'), false)
})

test('isSafeGitToken rejects a ".." path segment (filesystem escape)', () => {
	assert.equal(isSafeGitToken('../../etc/passwd'), false)
	assert.equal(isSafeGitToken('docs/../../etc/passwd'), false)
})

test('isSafeGitToken rejects empty or non-string input', () => {
	assert.equal(isSafeGitToken(''), false)
	assert.equal(isSafeGitToken(undefined), false)
})
