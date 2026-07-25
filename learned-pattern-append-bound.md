---
title: The learned-pattern corpus has no bound on its write path
status: backlog
source: split from learned-pattern-selection during 2026-07-26 sprint planning — read and write paths sized as two sessions
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: 3wkc15xdf63tpm6cvd4856ys
---

Sibling of `learned-pattern-selection`, which fixes the read path. This is the write path:
`kc-pr-review` Step 8 D1 and `kc-pr-review-resolve` Step 9 D1 both auto-append to
`reference/learned-patterns.md` with no confirmation gate and no duplicate check, so the
corpus can only grow. Selection makes a large corpus affordable to read; it does not stop it
becoming large, and a corpus that doubles keeps re-earning the migration cost.

Scope: dedup or supersede on append — a pattern that restates or replaces an existing entry
updates it instead of adding a 104th sibling. Deliberately not eviction-by-age; an old pattern
that still fires is not stale, and deleting on a timer would throw away the entries most worth
keeping.

Depends on `learned-pattern-selection` for the trigger metadata a dedup check needs.

**AC-1 — Appending a pattern that duplicates or supersedes an existing entry does not add a whole entry.**
Verified by: appending a near-duplicate of a known entry and asserting the corpus entry count
is unchanged and the surviving entry carries the newer content. Falsified by: entry count
growing, or the older text winning.
