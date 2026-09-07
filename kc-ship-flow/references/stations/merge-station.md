# merge-station station

**Enforcing script:** `kc-ship-flow/scripts/merge-station.sh --trunk <branch> [--accepted <file>]
[--override "<reason>"] [--repo owner/name] [--wait-seconds <n>] <pr>...`

**Input:** the trunk branch name, an ordered list of PR numbers, and optionally a file of accepted
40-hex `headRefOid` SHAs (one per line) and an override reason. All `gh` calls go through
`GH=${GH:-gh}` so a fixture can replace the binary.

**Output:** marks every PR ready, waits each one to a clean merge state, then squash-merges
(`--delete-branch`, stderr visible) in the given order, printing `MERGED: #<pr> <mergeCommit>` once
per PR on success.

**Refusal:** exit 2 when a PR's `baseRefName` is not `--trunk`, or (without `--override`) when a PR's
current `headRefOid` is not listed in `--accepted`; exit 3 when a PR's `mergeable`/`mergeStateStatus`
never reaches clean within `--wait-seconds` (default 600), or any `statusCheckRollup` entry reads
conclusion `FAILURE`; exit 4 when `gh pr merge` itself fails for a PR — no later PR is touched; exit 5
when the PR immediately after a landing reads `mergeStateStatus` `CONFLICTING` (`MOVED_BASE:`) — its
base moved under it and the script refuses to resolve it rather than merge past a stale diff.

Base and accepted-head are checked for every PR before any `ready`/`merge` call; every PR is marked
ready before any is merged. This is the S36/S37/S38/S45/S46 hardening: a single hand-driven `gh pr
ready`/`gh pr merge` pair races the ready transition, can swallow a refusal, can drift past the
accepted candidate, can merge into a non-trunk base, and a printed check is not a gate.
