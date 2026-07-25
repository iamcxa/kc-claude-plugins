---
title: Once-only posting active daemon preauthorization gate
status: backlog
source: deferred from safe-resume-once-only-post (PR3) gate decision D4 cut-order first item; re-scoped 2026-07-25 as slice 2 of 3, depends on daemon-once-only-posting
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: vf88cvthkhh9je2ng71xbbs9
---

Slice 2 of 3 for daemon posting safety. Depends on `daemon-once-only-posting` (slice 1); `daemon-preauth-freshness-coverage` (slice 3) depends on this.

`kc-pr-review` treats §6c human confirmation as the final authority before any `gh pr review`. In daemon mode that authority is supplied by an instruction in prose: `reference/pr-review-loop.md` tells the iteration "You are running in daemon mode with no interactive terminal ... Approve posting the review. Do NOT wait for user input — there is no user." So the autonomous path's authorization today is the loop asking the model to approve itself, with nothing typed, bounded, or auditable about it.

Real guardrails do exist around it and are not in question here: the absolute rules (never merge, never force-push, never close, one PR per iteration, at most three cycles, no high-risk auto-fix, no `.env`/lock/migration edits), the `human-only` / `daemon-skip` labels, and the CI pre-flight gate. What is missing is at the posting seam itself — nothing states *who* authorized *which* review, for *which* head, with *what* ceiling, or for *how long*.

Scope: replace the prose self-approval with a typed preauthorization artifact that Step 7 must be given in daemon mode — binding the review key and head it authorizes, the maximum event it permits (so an autonomous run can be limited to COMMENT), and an expiry. Absence denies, preserving today's default-deny-by-absence rather than widening it. Slice 1 already forces this artifact to exist in skeletal form; this slice is where it becomes typed and bounded.

Out of scope: freshness and coverage rechecks (slice 3), and any change to daemon classification or fix behaviour.

## Acceptance criteria

**AC-1 — An autonomous post without a valid typed preauthorization is refused, and absence alone is enough to refuse.**
Verified by: a daemon-mode post attempt with no preauthorization is denied with a typed refusal; the same attempt with a valid one proceeds. Falsified by: a post proceeding on a missing, malformed, or expired preauthorization.

**AC-2 — A preauthorization cannot authorize more than it names.**
Verified by: a preauthorization bound to one review key / head / event ceiling is rejected when presented for a different review key or head, and an attempt to post REQUEST_CHANGES under a COMMENT ceiling is capped or refused. Falsified by: any post exceeding the artifact's stated scope.
