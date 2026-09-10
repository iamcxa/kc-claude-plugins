# merge-station station

**Enforcing script:** `${CLAUDE_PLUGIN_ROOT}/scripts/merge-station.sh --trunk <branch> [--accepted <file>]
[--override "<reason>"] [--repo owner/name] [--wait-seconds <n>] [--poll-seconds <n>] <pr>...`

**Input:** the trunk branch name, an ordered list of PR numbers, and optionally a file of accepted
40-hex `headRefOid` SHAs (one per line), an override reason, and a poll interval (`--poll-seconds`,
default 15s). All `gh` calls go through `GH=${GH:-gh}` so a fixture can replace the binary.

**Output:** marks every PR ready, waits each one to a clean merge state, then squash-merges
(`--delete-branch`, stderr visible) in the given order, printing `MERGED: #<pr> <mergeCommit>` once
per PR on success.

**Refusal:** exit 2 when a PR's `baseRefName` is not `--trunk`, or (without `--override`) when a PR's
current `headRefOid` is not listed in `--accepted`, or on any other usage error; exit 3 when a PR's
`mergeable`/`mergeStateStatus` never reaches clean within `--wait-seconds` (default 600), or any
`statusCheckRollup` entry reads a failing CheckRun conclusion (`FAILURE`, `TIMED_OUT`, `CANCELLED`) or
a failing legacy StatusContext state (`FAILURE`, `ERROR`) — `statusCheckRollup` mixes both shapes, and
only CheckRun entries carry `conclusion`; exit 4 when `gh pr merge` itself fails for a PR — no later PR
is touched; exit 5 when the PR immediately after a landing reads `mergeStateStatus` `DIRTY` or
`mergeable` `CONFLICTING` (`MOVED_BASE:`) — its base moved under it and the script refuses to resolve
it rather than merge past a stale diff (`CONFLICTING` is a `mergeable` value, not a
`mergeStateStatus` one — the two fields are read together for this check); exit 6 when the post-merge
read does not confirm `state` `MERGED` with a 40-hex `mergeCommit.oid` (`MERGE_UNVERIFIED:`) — a
successful `gh pr merge` exit code alone is not proof the PR landed; exit 7 when `gh pr ready` itself
fails for a PR (`READY_FAILED:`).

Base and accepted-head are checked for every PR before any `ready`/`merge` call; every PR is marked
ready before any is merged. This is the S36/S37/S38/S45/S46 hardening: a single hand-driven `gh pr
ready`/`gh pr merge` pair races the ready transition, can swallow a refusal, can drift past the
accepted candidate, can merge into a non-trunk base, and a printed check is not a gate.

A clean `statusCheckRollup` entry for a monorepo PR is also not proof that entry's check ran the
changed package — see `references/stations/ci-covers.md` (DEV-149): run `ci-covers.sh` before the
merge verdict names that check the gate for a package it may never have entered.
