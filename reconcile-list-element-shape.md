---
title: A shape-valid but content-invalid reviews list reads as "marker absent"
status: validation
source: named residual from reconcile-degraded-mode-symmetry (sv) EM gate, 2026-07-26
started: 2026-07-30T02:56:12Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-reconcile-list-element-shape
issue:
pr:
design: trivial-pass
id: 11785c6he7dv034qb970tqm0
lane: main
---

## Problem

`review_post_reviews_usable` currently checks only that an exit-0 transport response is an
object whose `.reviews` value is an array. A body such as `{"reviews":[42]}` therefore passes.
The marker scan then assumes that every element and its `body` are scan-safe. A jq failure is
not distinguished from marker absence at any of the three reconcile sites, so malformed content
can license a POST or retry, or can collapse the post-retry result to an untyped `ambiguous`.

This is a contract-boundary defect. The shipped `gh` adapter normalizes reviews to objects and
cannot produce this body; the reachable boundary is a custom `KC_PR_FLOW_POST_TRANSPORT`, a proxy
that rewrites the response, or a future adapter.

## Reverse-recovery audit

Audited against live `origin/main` at
`f7c44efcd0f2587e004dcb3ff6f90896a385e1ab`:

- Transport seam — WORKING: `review_post_transport` accepts an executable custom transport;
  the shipped `gh` list adapter emits normalized review objects.
- Outer usability check — EXISTS_BROKEN: `review_post_reviews_usable` validates the outer object
  and array but not each `reviews[]` element.
- Marker scanner — WORKING status signal, BROKEN consumption: `review_post.sh` has
  `set -uo pipefail`, so malformed element/body input makes `review_post_scan_marker` return
  nonzero, but fresh post, resume, and post-retry reconciliation do not inspect that status.
- Fresh-post refusal — WORKING ordering: `sv` deliberately places the generic
  `reconcile_unavailable` refusal after local `posted_reconciled` and
  `prior_attempt_unsettled` decisions.
- Test seam — EXISTS_BROKEN: the stub models faithful, lagging, and outer-shape-unusable lists,
  but not malformed elements or marker-scan errors.

No new abstraction is missing. Repair the existing validator and consume the existing scan status.

## Scope

Harden reconcile reads against malformed `reviews[]` values at the existing custom-transport
boundary:

1. Keep validation in `review_post_reviews_usable` and require both an outer reviews array and
   `all(.reviews[]; type == "object")`. `{"reviews":[]}` remains usable.
2. Check the existing pipefail-preserved exit status of `review_post_scan_marker` in all three
   reconciliation contexts: fresh post, resume, and post-retry reconciliation.
3. On fresh-post scan failure, clear the candidate id and mark the read unusable, but continue
   through the existing local prior-state check before the generic refusal. Do not early-return
   ahead of `sv` ordering.
4. Sync only the existing runtime-contract documentation that describes unusable reconcile reads
   and retry safety.

## Proposed approach

Take the cheapest sufficient path: strengthen the existing validator and add explicit status
guards at the three current callers. Do not introduce a new tri-state scanner API, a full GitHub
review schema, or a transport redesign; the current function already returns a usable nonzero
signal under the script's existing `pipefail`.

The fastest path and the smallest cut are the same change. The more thorough alternative would
validate every GitHub review field or redesign the transport contract, but neither is needed to
prevent malformed content from being read as marker absence.

## Design determination

`trivial-pass` — this restores the already documented fail-closed reconcile contract. It does not
decide a new UI, schema, interface, or contract shape.

## Acceptance criteria

**AC-1 — Malformed review elements fail closed.**

For an exit-0 list response containing any non-object `reviews[]` element, fresh post, resume,
and post-retry reconciliation treat the read as unusable rather than marker-absent. Absent `sv`'s
local positive-state overrides, each context emits
`ambiguous{reason:"reconcile_unavailable"}`, retains the pending payload, and permits no further
POST or retry. If an earlier ambiguous POST landed, a malformed resume leaves the remote review
count at exactly one.

Fresh post preserves `sv` ordering: a definitively posted local prior attempt still yields
`posted_reconciled`, and an unsettled prior attempt still yields `prior_attempt_unsettled`.

Verified by: the injected transport drives scalar-element responses through fresh post, resume,
and post-retry reconciliation; assertions pin the typed reason, pending file, POST count, remote
review count, and the two existing local-state outcomes. Falsified by: any path posting or
retrying after the malformed read, losing pending state, returning an untyped result, or replacing
either `sv` local-state outcome with `reconcile_unavailable`.

**AC-2 — Marker-scan failure is never absence.**

At all three reconciliation contexts, any nonzero `review_post_scan_marker` status is converted
to the same unusable-read outcome, regardless of whether the scan emitted an id before failing.
It is never consumed as marker-found or marker-absent.

A reviews object with a numeric `body` exercises this guard independently of the non-object
element validator. In fresh post, scan failure marks the read unusable and flows through the
existing post-local-state refusal point rather than returning at the scan site.

Verified by: numeric-body responses exercise fresh post, resume, and post-retry reconciliation;
marker-before-error and error-before-marker orders both produce typed `reconcile_unavailable`
without a further POST or retry. Falsified by: ignoring any caller's scan status, accepting partial
stdout from a failed scan, or early-returning before fresh post consults local durable state.

## Test plan

- Extend the injectable list stub with malformed element/object modes that can coexist with an
  already populated remote review store.
- Pin `{"reviews":[]}` as usable.
- Fresh post with a scalar element: no POST, typed `reconcile_unavailable`, pending retained.
- Resume after an ambiguous POST that landed, with a malformed list: review count remains exactly
  one and pending remains.
- Exercise numeric-`body` scan failure in fresh post, resume, and post-retry reconciliation.
- Put a genuine marker before and after a numeric-body object. Both orders refuse; the marker-first
  case pins nonzero status even when stdout is nonempty.
- Pin post-retry scan failure to typed `reconcile_unavailable`, pending retained, and no further
  retry.
- Preserve the existing `posted_reconciled` and `prior_attempt_unsettled` placement tests.

E2E-first skip: this is a network-free transport-boundary defect. The supported injectable
transport exercises the real `review-post.sh` CLI flow without mutating a live PR.

## Mutation plan

Each mutation must make a relevant test fail:

- Revert element validation to outer-array-only.
- Ignore scan status independently at fresh post.
- Ignore scan status independently at resume.
- Ignore scan status independently at post-retry reconciliation.
- Accept nonempty scan stdout despite a nonzero status.
- Move fresh-post unusable refusal ahead of `sv` local-state handling.
- Make an empty reviews array unusable.

## Spike evidence

No further spike is needed. Direct jq probes on the audited main revision established:

- scalar element: scan exit 5 with empty stdout;
- numeric body: scan exit 5 with empty stdout;
- genuine marker before a malformed element: scan exit 5 with stdout containing the marker id;
- the strengthened `all(...; type == "object")` predicate accepts an empty reviews array.

These probes show that the scan signal already exists and that output emptiness cannot substitute
for checking its status.

## Appetite and sizing

One implementation worker, target at most 90 minutes. Declared tolerance is 135 minutes total.
Stop and re-cut instead of continuing if the repair requires a new transport abstraction, a full
review schema, or work outside the named code/test/doc surfaces. One worker owns complete
RED-to-GREEN behavior slices; do not split tests from implementation.

## Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is a hidden assumption that
another jq pipeline or caller also converts partial output plus nonzero status into positive remote
evidence.

## Doc diff

- `reference/review-runtime.md`: change rule (1) from only “not a reviews array” to “not a reviews
  array of objects, or a marker scan that exits nonzero regardless of partial output”; replace the
  tracked element-shape gap with the enforced three-site guarantee.
- `docs/review-runtime.md`: define `reconcile_unavailable` as an unusable element set or failed
  marker scan, not only an unusable outer array.
- `CLAUDE.md` and `README.md`: make the same bounded wording change in their once-only posting
  summaries.
- No `PRODUCT.md` or `ARCHITECTURE.md` change: this restores their existing fail-closed behavior
  rather than changing product direction or architecture.

## Out of scope

- `vf` / `x0` daemon preauthorization, expiry, freshness, ceilings, keychain, or coverage work.
- Pagination, author matching, concurrency, retention, GC, or idempotency redesign.
- Full transport redesign or full GitHub review-schema validation.
- Auth schemas, `SKILL.md`, and the broader review-kit or automated reviewer-repair loop.
- Versioning, release work, or unrelated documentation changes.

## Independent shaping review

A single bounded direct Claude review ran under OAuth with no model tool use or session
persistence. Observable model identity was Claude Opus 5. It returned `REVISE` with High
confidence before the 180-second hard cap interrupted its paste-ready appendix; no retry ran.

Accepted findings:

- Do not early-return fresh-post scan failure before `sv` local-state ordering.
- Name post-retry reconciliation in AC-1 and say “no further POST or retry”.
- Treat nonzero scan status as unusable even when stdout already contains an id.
- Exercise numeric-body scan failure at all three callers and keep malformed-list shape independent
  from the remote review store.
- Preserve empty-array usability.

Rejected or narrowed findings:

- The claim that `jq | head` made status unobservable was rejected: `review-post.sh:26` already
  enables `pipefail`, and live probes returned exit 5 through the assignment.
- A new tri-state scanner API was rejected as unnecessary; explicit guards around the existing
  status are smaller.
- A separate two-axis stub architecture was narrowed to the observable need: malformed list modes
  must coexist with the existing remote store, without prescribing a redesign.

The corrected ACs and ordering above incorporate every accepted material finding.

## Stage Report: ideation

- DONE: Re-anchored the defect and all three callers on live `origin/main`.
  `review-post.sh:433-450`, `:673-725`, `:866-882`, and `:919-935` establish the
  outer-only validator, scan assumption, and three distinct consumption sites.
- DONE: Preserved `sv` local-positive ordering as an explicit implementation constraint.
  `review-post.sh:693-725` and existing placement tests
  `review-post.test.sh:368-390` pin `posted_reconciled` and
  `prior_attempt_unsettled` before the generic refusal (AC-1).
- DONE: Recorded the cheapest sufficient mechanism and rejected broader schema/transport work.
- DONE: Recorded `design: trivial-pass` with its contract-restoration reason.
- DONE: Defined two parseable, falsifiable ACs with value/mechanism pairing. AC-1 is the
  end-value guarantee; AC-2 guards the scan-status mechanism serving it.
- DONE: Defined integration tests, order cases, and caller-specific mutations. Direct probes
  against `review-post.sh:26,440-450` returned exit 5 for scalar and numeric-body failures,
  including exit 5 plus nonempty stdout when a genuine marker preceded the bad element (AC-2).
- DONE: Recorded spike evidence, appetite, tolerance, sizing, and pre-mortem.
- DONE: Proposed bounded runtime-documentation diffs from the known-gap contract at
  `reference/review-runtime.md:210-212`.
- DONE: Adjudicated the bounded Claude Opus review against live code.
- DONE: Kept every named out-of-scope surface excluded.

10 done, 0 skipped, 0 failed.

### Outcome

Corrected ideation is complete and ready for the EM ideation gate. Captain-approved scope has been
preserved; no product worktree, code, test, documentation, PR, or release mutation has started.

## Stage Report: implementation

- DONE: RED before GREEN, with evidence.
  Baseline was 142 passed / 0 failed in 331.48s. Test-and-stub-only RED was 148 passed /
  7 failed in 341.29s; the seven claim failures covered scalar fresh/resume/post-retry,
  numeric fresh, marker-first resume, error-first post-retry, and numeric unsettled placement.
- DONE: Count new assertions against the RED output.
  The behavior assertions above failed before production changed; arrangement probes for
  scan rc 5 in both orders, empty-array usability, outer-unusable placement, and
  numeric posted-prior placement intentionally stayed green.
- DONE: When you change a behavior, audit the tests that arrange the old one.
  Existing `posted_reconciled` and `prior_attempt_unsettled` placement cases were extended,
  not narrowed; both retain their original local-positive ordering under scan failure.
- DONE: Implement the minimum approved behavioral repair.
  `review_post_reviews_usable` now requires object elements, and all three scan callers
  consume nonzero status; fresh post clears partial ids but reaches the existing local check.
- DONE: Apply the approved documentation diff.
  `CLAUDE.md`, `README.md`, and both runtime summaries describe the same bounded
  three-caller fail-closed rule, including partial output and local-state ordering.
- DONE: Scoped tests in the loop, full suite plus ripple at the exit.
  Fresh recovery GREEN: `bash kc-pr-flow/scripts/review-post.test.sh` returned
  155 passed / 0 failed in 403.25s; removing any caller guard or the element predicate
  makes the named RED behavior fail again.
- DONE: Name what CI will do differently, before pushing.
  The scoped suite grew 71.77s versus the 331.48s baseline. Applied to the workflow's
  recorded 9m07s job, the 20-minute cap retains about 9m41s planning margin; exact-head
  CI remains authoritative.
- DONE: Run the diff-earned static gates.
  `bash -n`, pinned ShellCheck v0.9.0, and `git diff --check` all exited 0 on the
  changed shell surfaces.
- DONE: Commit the self-contained product deliverable.
  Commit `335722edf48018c16342216351c7229670b2e222` contains exactly the seven authorized
  runtime, test, fixture, and documentation files; the product worktree is clean.
- DONE: Preserve recovery and downstream-review boundaries.
  Recovery found the seven-file residue uncommitted with no test process, retained it
  byte-for-byte until fresh verification, and did not run agy, Claude, product push, or PR work.

### Summary

The two ACs now fail closed at the custom-transport boundary without changing the shipped
adapter or `sv` ordering. A corrected fixture-syntax false start was excluded from RED evidence.
Independent validation and agy code review remain next; Claude EM remains the landing gate and
must not be inferred from this implementation receipt.

## Stage Report: validation

- DONE: Reproduce both approved ACs with fresh executable evidence.
  Exact-head `review-post.test.sh` returned 155 passed / 0 failed in 290.83s; scalar and
  numeric-body fresh, resume, post-retry, partial-output, and local-order assertions all ran.
- DONE: Run all earned seven suites once at the end.
  Runtime 305/0 (81.66s), shadow 213/0 (138.06s), benchmark 135/0 (19.60s),
  post 155/0 (317.03s), cross-model 68/0 (0.34s), diagrams 43/0 and 34/0.
- DONE: Run the diff-earned static gates.
  `bash -n`, pinned ShellCheck v0.9.0, and `git diff --check` each exited 0.
- DONE: Confirm the authorized scope and documentation guarantees.
  Diff is exactly seven files; four docs match the three caller guards and local-state
  ordering, with no `agy`-first policy, `vf`, `x0`, version, or broader review-kit work.
- DONE: Compute executable diff coverage for changed shell command starts.
  Bash xtrace covered 93/96; two locally stderr-suppressed scan calls were proven by their
  `5|7` and `5|` assertions, for 95/96 = 98.96%; only test line 830 was unexecuted.
- FAILED: Kill the element-validator boundary mutation.
  Reverting to outer-array-only survived the full suite at 155/0 in 423.84s because scan
  guards compensated; no direct assertion pins `{"reviews":[42]}` as unusable.
- DONE: Kill the fresh, resume, and post-retry scan-status mutations.
  They returned 154/1 in 427.45s, 154/1 in 458.90s, and 154/1 in 451.66s, with each
  named caller assertion observing a POST/duplicate or untyped ambiguity.
- DONE: Kill partial-output acceptance, early refusal, and empty-array rejection.
  They returned 154/1 in 429.19s, 151/4 in 419.29s, and 96/59 in 352.36s; all failures
  were task assertions rather than harness errors.
- DONE: Run the mandatory whole-diff agy/Gemini review.
  `gemini-3.1-pro-high` accepted the same P2 missing-boundary-test finding; its P3 missing
  fixture-file concern was rejected because the only caller creates `reviews.jsonl`.
- DONE: Preserve exact-head product state.
  Product remained clean at `335722edf48018c16342216351c7229670b2e222`, parent/base
  `f7c44efcd0f2587e004dcb3ff6f90896a385e1ab`; no product edit, push, PR, or version ran.
- SKIPPED: Exercise a live GitHub PR E2E.
  Ideation records the network-free custom-transport boundary; the supported injected CLI
  runtime exercised real `post` and `resume` behavior without mutating a live PR.

### Evidence block

- Lenses: correctness FAIL (1 mutation-proof gap); security PASS (0);
  silent-failure PASS (0); no type, concurrency, resource, or manifest lens fired.
- Diff coverage: 98.96% (95/96 changed executable command starts).
- Adversarial: FAIL — 6/7 required mutations killed; outer-only validation survived.
- Cross-model: Gemini 3.1 Pro High REVISE; one P2 accepted, one P3 rejected.
- E2E: N/A — approved network-free transport seam; exact CLI integration ran 155/0.

### Summary

AC-1 and AC-2 behavior pass and the seven-suite ripple is green, but the approved
element-validator mechanism is not independently falsifiable. Return to implementation for one
direct scalar-element usability assertion, then rerun the scoped suite and this mutation.
