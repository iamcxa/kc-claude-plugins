// Canonical-chapter-link parsing shared by the client (which decides whether a
// shape's URL opens the popup) and the server (which resolves it against a
// local checkout). A branch name may itself contain "/", so the URL alone
// cannot say where the ref ends and the path begins; only git can settle that
// (see candidateRefSplits below), so parsing stops at the ref/path boundary.
const GITHUB_BLOB = /^https:\/\/github\.com\/([^/]+)\/([^/]+)\/blob\/(.+?)(?:#(.+))?$/

export function parseGithubBlobUrl(url) {
	const m = GITHUB_BLOB.exec(String(url ?? ''))
	if (!m) return null
	const [, owner, repo, refAndPath, chapter] = m
	if (!refAndPath.includes('/')) return null // no path segment left for a ref-only match
	return { owner, repo, refAndPath, chapter }
}

// Ordered ref/path splits of "<ref>/<path>", most-specific ref first (longest
// prefix) down to a single leading segment — so "feature/foo" is tried before
// the shorter "feature" when both happen to resolve as refs.
export function candidateRefSplits(refAndPath) {
	const segments = String(refAndPath).split('/')
	const splits = []
	for (let i = segments.length - 1; i >= 1; i--) {
		splits.push({ ref: segments.slice(0, i).join('/'), path: segments.slice(i).join('/') })
	}
	return splits
}

// Ref and path come from an untrusted URL, not an operator: reject a leading
// "-" (git flag injection) and a ".." path segment (filesystem escape).
export function isSafeGitToken(token) {
	return typeof token === 'string' && token.length > 0 && !token.startsWith('-') && !token.split('/').includes('..')
}
