// Resolves a canonical GitHub blob URL to content from a local repository
// checkout: the server never talks to GitHub, and reads the ref pinned in the
// link via `git show <ref>:<path>`, never the working tree.
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { candidateRefSplits, isSafeGitToken } from '../lib/repo-doc.mjs'

const run = promisify(execFile)

// owner/repo -> local checkout path, from the JOURNEY_DOC_REPOS env map the
// canvas startup step sets (see references/canvas.md).
function repoMap(): Record<string, string> {
	return Object.fromEntries(
		(process.env.JOURNEY_DOC_REPOS ?? '')
			.split(',')
			.map((pair) => pair.trim())
			.filter(Boolean)
			.map((pair) => {
				const [key, ...rest] = pair.split('=')
				return [key, rest.join('=')]
			}),
	)
}

export type RepoDocResult = { state: 'ok'; content: string; sha: string } | { state: 'unavailable'; reason: string }

async function resolveRef(checkout: string, refAndPath: string): Promise<{ ref: string; path: string; sha: string } | null> {
	for (const { ref, path } of candidateRefSplits(refAndPath)) {
		if (!isSafeGitToken(ref) || !isSafeGitToken(path)) continue
		for (const candidate of [ref, `origin/${ref}`]) {
			try {
				const { stdout } = await run('git', ['-C', checkout, 'rev-parse', '--verify', '--quiet', `${candidate}^{commit}`])
				return { ref: candidate, path, sha: stdout.trim() }
			} catch {
				// not a valid ref at this split; try the next candidate
			}
		}
	}
	return null
}

export async function readRepoDoc(owner: string, repo: string, refAndPath: string): Promise<RepoDocResult> {
	const checkout = repoMap()[`${owner}/${repo}`]
	if (!checkout) return { state: 'unavailable', reason: `no local checkout configured for ${owner}/${repo}` }

	const resolved = await resolveRef(checkout, refAndPath)
	if (!resolved) return { state: 'unavailable', reason: `ref not found in local checkout for "${refAndPath}"` }

	try {
		const { stdout } = await run('git', ['-C', checkout, 'show', `${resolved.ref}:${resolved.path}`])
		return { state: 'ok', content: stdout, sha: resolved.sha }
	} catch {
		return { state: 'unavailable', reason: `"${resolved.path}" not found at ${resolved.ref}` }
	}
}
