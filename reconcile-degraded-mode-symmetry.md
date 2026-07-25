---
title: post and resume disagree on an unusable reconcile read
status: backlog
source: split out of once-only-daemon-preauth-gate (vf) AC-3 on 2026-07-26 — caller-agnostic, so it should not wait on the daemon-authorization arc
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: svjp01d5dj7d9fpxacmj7qwz
---

`review-post.sh` reaches opposite verdicts on the same degraded condition. `resume` fails
**closed**: an unusable reviews-list response emits `ambiguous{reconcile_unavailable}`,
keeps the pending payload durable, and posts nothing (`:746-750`). `post` fails **open**:
an unusable list skips the marker scan, falls through to the local
`review_post_prior_attempt_state` check, and if that finds nothing it POSTs (`:569`, `:586`,
`:608-612`). Nothing records the difference as deliberate.

This is not a daemon problem. It predates the autonomous path (introduced in #56), and the
interactive caller takes exactly the same branch, so whatever is decided here changes
behaviour for every caller. It was carried as AC-3 of `once-only-daemon-preauth-gate` (vf)
only because that entity was building the authorization contract that might have expressed
it; nothing else about vf constrains it, so it is split out to ship on its own.

## The deferral rationale on record is wrong, and that changes the cost

Slice 1's validation argued the asymmetry had to stay because symmetry "would refuse even a
genuinely first post while the reviews API is degraded, and would change availability for
EVERY caller". Checked against the code, it would not. `:568` is
`reviews_json="$(review_post_transport list ...)" || return 74`, and the production `gh`
adapter returns non-zero on an API failure (`:127-128`), so a genuinely degraded reviews API
**already** aborts `post` before the usability check is reached — with the pending payload
(`:560`) and `post.intent` (`:545-549`) already durable, i.e. already resumable. The
fail-open branch is reachable only when the transport exits 0 with a body that is not a
reviews array, which the `gh` adapter cannot produce; in practice only a misbehaving custom
`KC_PR_FLOW_POST_TRANSPORT` gets there.

So the availability cost of symmetry is approximately zero, and the recommendation carried
over from vf's backlog gate is **unconditional fail-closed**: `post` emits
`ambiguous{reconcile_unavailable}` exactly as `resume` does, leaves the already-durable
pending payload, and posts nothing; a later `resume` settles it. One rule, no branch on
caller type, no new configuration. Verify that reasoning before implementing rather than
inheriting it — it is a correction to a prior stage report, and prior stage reports are
exactly the thing this repo has caught being wrong.

## Acceptance criteria

**AC-1 — `post` and `resume` reach the same verdict on an unusable reconcile read.**
Verified by: one test driving an unusable list response through both commands and asserting
the identical status, with no review written on either path. Falsified by: the two commands
disagreeing, or agreement asserted only in prose.

**AC-2 — A run that fails closed in `post` is still settleable, not stranded.**
Verified by: after the refusal, `resume` on that run reconciles or retries to a terminal
outcome once the list read is usable again, and the pending payload is still present when it
does. Falsified by: a state no later command can settle, or evidence deleted at refusal time.

## Out of scope

The event ceiling, expiry, and schema version of the autonomous gate (`vf`); freshness and
coverage rechecks (`x0`); the retention sweeper (`7j`). No change to the transport contract
or to what a non-zero transport exit means.
