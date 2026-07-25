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

**Unblocked 2026-07-26 — premise survived a challenge.** `attended-pr-review-wait` (4p)
briefly proposed removing the unattended caller rather than bounding it, which would have
deleted this slice's reason to exist. The captain parked it the same day: unattended
operation is a standing daily need, so a bounded autonomous authorization is still required
and the four decisions below stand.

One narrower coupling remains. D1's ceiling has to be set by something outside the agent
that mints the gate, and the seat identified at the backlog gate was
`pr-review-daemon.sh:190`'s inline env prefix. 4p's parked directions (`spacedock claude`,
or a spacedock+ACP harness) would change or remove that script. **The ceiling's ordering,
cap-vs-refuse semantics, expiry, AC-3 symmetry, and schema version are all caller-agnostic
and can be built now; only which process exports the ceiling should wait for the caller's
shape to settle.** Do not over-fit the contract to today's `claude -p` daemon.

`kc-pr-review` treats §6c human confirmation as the final authority before any `gh pr review`. In daemon mode that authority is supplied by an instruction in prose: `reference/pr-review-loop.md` tells the iteration "You are running in daemon mode with no interactive terminal ... Approve posting the review. Do NOT wait for user input — there is no user." So the autonomous path's authorization today is the loop asking the model to approve itself, with nothing typed, bounded, or auditable about it.

Real guardrails do exist around it and are not in question here: the absolute rules (never merge, never force-push, never close, one PR per iteration, at most three cycles, no high-risk auto-fix, no `.env`/lock/migration edits), the `human-only` / `daemon-skip` labels, and the CI pre-flight gate. What is missing is at the posting seam itself — nothing states *who* authorized *which* review, for *which* head, with *what* ceiling, or for *how long*.

Scope: replace the prose self-approval with a typed preauthorization artifact that Step 7 must be given in daemon mode — binding the review key and head it authorizes, the maximum event it permits (so an autonomous run can be limited to COMMENT), and an expiry. Absence denies, preserving today's default-deny-by-absence rather than widening it. Slice 1 already forces this artifact to exist in skeletal form; this slice is where it becomes typed and bounded.

Out of scope: freshness and coverage rechecks (slice 3), and any change to daemon classification or fix behaviour.

### Carried in from slice 1's validation (captain-assigned 2026-07-25)

`review_post_cmd_post`'s pre-POST reconcile **fails open** when the reviews-list read is unusable, where `resume` fails closed on the identical condition. Pre-existing from #56, not introduced by slice 1, and it needs two coincident conditions: local durable state unavailable (a wiped or reconfigured state dir) **and** an unusable remote list at that moment — the local cross-run check independently blocks the ordinary crash-then-retry case.

It landed here rather than in slice 1 because making it symmetric would refuse even a genuinely first post while the reviews API is degraded, and would change availability for **every** caller rather than the daemon alone. That is a degraded-mode policy decision, and this slice is where the preauthorization contract that should express it is being built. Consider whether the answer is unconditional fail-closed or an operator-selectable degraded mode; do not leave it as an unremarked asymmetry between `post` and `resume`.

**AC-3 — `post` and `resume` treat an unusable reconcile read the same way, or the difference is documented as deliberate with its reason.**
Verified by: a test driving an unusable list read through both paths and asserting the chosen behaviour, plus the recorded rationale if they intentionally differ. Falsified by: the asymmetry persisting with no test and no stated reason.

## Acceptance criteria

**AC-1 — An autonomous post without a valid typed preauthorization is refused, and absence alone is enough to refuse.**
Verified by: a daemon-mode post attempt with no preauthorization is denied with a typed refusal; the same attempt with a valid one proceeds. Falsified by: a post proceeding on a missing, malformed, or expired preauthorization.

**AC-2 — A preauthorization cannot authorize more than it names.**
Verified by: a preauthorization bound to one review key / head / event ceiling is rejected when presented for a different review key or head, and an attempt to post REQUEST_CHANGES under a COMMENT ceiling is capped or refused. Falsified by: any post exceeding the artifact's stated scope.

## Backlog gate, 2026-07-26 — findings preserved

The gate ran (EM on fresh context, plus one cross-vendor pass on `agy`) before the captain
proposed `attended-pr-review-wait`. These findings hold whichever direction wins, so they are
recorded here rather than lost with the slice. Baseline at the time: 920 passed / 0 failed
across all 7 kc-pr-flow suites, matching #59's merge state.

**Slice 1's stated reason for deferring AC-3 is wrong.** Its validation report argued that
making `post` symmetric with `resume` "would refuse even a genuinely first post while the
reviews API is degraded, and would change availability for EVERY caller". It would not.
`review-post.sh:568` is `reviews_json="$(review_post_transport list ...)" || return 74`, and
the production `gh` adapter returns non-zero on an API failure (`:127-128`), so a genuinely
degraded reviews API already aborts `post` before the usability check is reached — with the
pending payload (`:560`) and `post.intent` (`:545-549`) already durable. The fail-open path is
reachable only when the transport exits 0 with a non-array body, which the `gh` adapter cannot
produce. Symmetry therefore costs approximately nothing, and AC-3 should take the unconditional
fail-closed branch rather than the documented-asymmetry escape hatch.

**An event ceiling minted by the daemon would constrain nothing.** The ceiling has to come from
outside the agent that mints the gate, or it is decoration. The seat exists and is already in
use: `pr-review-daemon.sh:190` passes `PR_DAEMON_MODE=1 PR_DAEMON_AUDIT=1` as an inline env
prefix on the `claude -p` call, and `read_config` (`:25-48`) already reads `daemon.yaml`. An
earlier reading of "the daemon script sets no environment" came from grepping only for `export`
and was too narrow.

**Refusing an over-ceiling event silently deletes the daemon's most valuable output.** A typed
decision carrying blockers forces `effective_event` to REQUEST_CHANGES
(`skills/kc-pr-review/SKILL.md:1385-1387`), and the daemon mints its gate from that value
(`reference/pr-review-loop.md:88`). Under a COMMENT ceiling with refuse-only semantics, every
review that found a blocker fails to post at all, with nothing recording why. The resolution is
to cap at the producer *and* mark the capping in the review body, keeping refusal at the
enforcement point as a backstop — the failure to avoid is silence, in either direction.

**Cross-vendor findings adjudicated against the code.** Accepted: implement the ceiling as
explicit set membership rather than integer ranks (integers create an accidental total order
between the two incomparable tops); type-guard the new fields before comparing, per the existing
`type == "string"`-before-`test()` idiom; assert `now < expires` *before* the TTL upper bound,
since `(( -50 <= 300 ))` is true and an expired gate would otherwise pass; validate a parsed
epoch before arithmetic, per `resume`'s existing `case *[!0-9]*` guard. Refuted: the claim that
gate expiry can strand a run — `resume` takes no `--gate-file` (it appears only in
`review_post_cmd_post`, `:462-499`) and the gate is never persisted, so the chain does not
exist. Refuted: clock skew between minter and enforcer — they share a process tree and a clock.

**One documentation obligation the design had not named.** Expiry bounds the
authorization-to-intent window only. Once `post.intent` is durable, `resume` may settle it hours
later; that window is bounded instead by `resume`'s head recheck (`:725`) and retention GC. A
reader who assumes an expired gate blocks a late resume would be wrong.
