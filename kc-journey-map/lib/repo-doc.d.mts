export function parseGithubBlobUrl(url: string): { owner: string; repo: string; refAndPath: string; chapter?: string } | null

export function candidateRefSplits(refAndPath: string): { ref: string; path: string }[]

export function isSafeGitToken(token: unknown): boolean
