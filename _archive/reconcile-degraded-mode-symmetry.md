---
title: post and resume disagree on an unusable reconcile read
status: done
source: split out of once-only-daemon-preauth-gate (vf) AC-3 on 2026-07-26 — caller-agnostic, so it should not wait on the daemon-authorization arc
started: 2026-07-25T18:49:04Z
completed: 2026-07-26T05:44:07Z
verdict: passed
worktree: .worktrees/sv-reconcile-symmetry
issue:
pr: pr-merge:63
design: required
id: svjp01d5dj7d9fpxacmj7qwz
archived: 2026-07-26T05:44:07Z
---

`review-post.sh` reaches opposite verdicts on the same degraded condition. `resume` fails
**closed**: an unusable reviews-list response emits `ambiguous{reconcile_unavailable}`,
keeps the pending payload durable, and posts nothing (`:746-750`). `post` fails **open**:
an unusable list skips the marker scan, falls through to the local
`review_post_prior_attempt_state` check, and if that finds nothing it POSTs (`:569`, `:586`,
`:608-612`).

This is not a daemon problem. It predates the autonomous path (introduced in #56), and the
interactive caller takes exactly the same branch, so whatever is decided here changes
behaviour for every caller. It was carried as AC-3 of `once-only-daemon-preauth-gate` (vf)
only because that entity was building the authorization contract that might have expressed
it; nothing else about vf constrains it, so it is split out to ship on its own.

## This overturns a recorded decision, not an unclaimed accident

An earlier draft of this entity said nothing recorded the asymmetry as deliberate. That was
wrong, and the EM gate caught it. `reference/review-runtime.md:212` states it normatively:

> When that pre-POST read is unusable, `post` proceeds only if no other run for the PR
> recorded a `post.intent` for the same idempotency key; otherwise it fails closed rather
> than risk a duplicate.

Its rationale is **not** slice 1's availability argument, which is separately wrong (`:568` is
`reviews_json="$(review_post_transport list ...)" || return 74` and the production `gh`
adapter returns non-zero on API failure at `:127-128`, so a genuinely degraded reviews API
already aborts `post` before the usability check — with the pending payload `:560` and
`post.intent` `:545-549` already durable). The recorded rationale is stronger: *the local
intent check is sufficient, because if no local run ever recorded an intent for this exact
payload hash then this machine has never POSTed it.*

**That argument is correct inside its own model, and only inside it.** It holds for a single
durable state root. Wipe or reconfigure the state directory, move to another machine, or run
on a stateless CI runner, and the local check is blind; combine that with an unusable list
hiding the marker and `post` writes a duplicate of a review that is already live. Failing
closed waits for a usable list, whose marker scan then reconciles instead of duplicating.
This is the same two-coincident-conditions residual vf's AC-3 originally named.

Note also that the same document contradicts itself. One paragraph earlier it states a
general rule with no exception: "A list response that is not a reviews array is never read as
'marker absent'; it fails closed (`ambiguous{reason: reconcile_unavailable}`, pending kept, no
POST)." The change aligns the code with the document's own general rule and removes the carve-out.

Cost is approximately zero: the fail-open branch is reachable only when a transport exits 0
with a non-array body, which the `gh` adapter structurally cannot produce.

## Design determination: `required`

Overturning a normative sentence in the runtime-adapter protocol document is a contract
change, so this is not a trivial-pass. The attached decision is the placement below.

**The fail-closed check goes after the local check, immediately before the POST.** The local
`prior_attempt_state` block (`:584-604`) has two outcomes that must survive: a prior run that
definitively posted settles as `posted_reconciled` (`:598`), and an unsettled prior attempt
emits `ambiguous{prior_attempt_unsettled}` (`:602`). Returning early at `:569` would collapse
both into a bare `reconcile_unavailable` and discard information the process already holds.
Guarding the complement — refuse when neither source gave positive confirmation — leaves
exactly one path to the POST: usable array, marker absent, no local intent.

The status vocabulary is reused verbatim from `resume`, which is what makes AC-1 literally
true rather than approximately true. Both the EM and the cross-vendor pass judged that a
caller needs no new handling: the required recovery action is identical (keep the payload,
resume when the read is healthy), and the daemon already treats `ambiguous` that way
(`reference/pr-review-loop.md:92`).

## Acceptance criteria

**AC-1 — `post` and `resume` reach the same verdict on an unusable reconcile read.**
Verified by: a `kc-pr-flow/scripts/review-post.test.sh` scenario driving the stub transport's
`unusable` list behaviour (`kc-pr-flow/test/fixtures/review-post/stub-transport.sh`) through both
commands and asserting the identical status and reason, with no review written on either path.
Falsified by: the two commands disagreeing, or agreement asserted only in prose.

**AC-2 — A run that fails closed in `post` is still settleable, not stranded.**
Verified by: the same `kc-pr-flow/scripts/review-post.test.sh` scenario continuing past the
refusal — `resume` reconciles or retries to a terminal outcome once the list read is usable
again, with the pending payload written by `kc-pr-flow/scripts/review-post.sh` still present when
it does. Falsified by: a state no later command can settle, or evidence deleted at refusal time.

## Test plan (RED before GREEN)

The stub transport already models this exact condition: `list-plan` accepts `unusable`, which
returns `{"reviews":null}` at exit 0 (`test/fixtures/review-post/stub-transport.sh:76-78`).
An existing block at `scripts/review-post.test.sh:321-333` drives it through `resume`; these
mirror its shape.

1. **RED for AC-1** — `post` with an unusable list and no prior local state. Today it writes
   one review (reproduced by the EM against the real CLI, not inferred). Required: `ambiguous`,
   reason `reconcile_unavailable`, store count 0, pending payload present, and no `post.result`
   event on the run.
2. **Symmetry** — the same unusable response through `post` and through `resume` yields the
   identical `.status` and `.reason`.
3. **RED for AC-2** — after that refusal, `resume` with a usable list reaches a terminal
   outcome, and the pending payload was present at refusal time.
4. **Regression guard for the placement decision** — two halves, both green before and after:
   an unusable list plus a prior run that already posted must still emit `posted_reconciled`;
   an unusable list plus an *unsettled* prior attempt must still emit `prior_attempt_unsettled`,
   not `reconcile_unavailable`. The second half is the one the existing suite cannot pin, because
   `:366-375` uses `lag`, which passes the usability gate.

Verify with CI's pinned ShellCheck **v0.9.0**, never the local Homebrew build — both parity
commands are in `kc-pr-flow/CLAUDE.md`.

## Doc diff

`reference/review-runtime.md:212` — **rewrite** the normative sentence quoted above (not an
addition). It becomes: the pre-POST reconcile fails closed on an unusable read exactly as
`resume` does, so the general rule stated one paragraph earlier now holds without a carve-out.
Record why the local-intent argument was insufficient (it is sound only within one state root).

`kc-pr-flow/CLAUDE.md` — the once-only posting section gains the same one-rule statement.

## Named residuals (not fixed here)

- **Shape-valid, content-invalid list.** `{"reviews":[42]}` passes `review_post_reviews_usable`
  (`:328-330`); `review_post_scan_marker`'s jq then errors mid-expression and the result reads
  as "marker absent". `resume` has the byte-identical hole (`:746` passes, `:751` errors), and a
  fix (`all(.reviews[]; type == "object")`) changes both commands, so it is its own entity.
- **A `post` refusal and an ambiguous POST are indistinguishable in the durable log**, because
  the ambiguous branch appends no event (`:645-648`). Pre-existing observability gap; this
  change adds a second way to reach that state but does not create it.

## Out of scope

The event ceiling, expiry, and schema version of the autonomous gate (`vf`); freshness and
coverage rechecks (`x0`); the retention sweeper (`7j`). No change to the transport contract
or to what a non-zero transport exit means.

## Stage Report: implementation

TL;DR — `post` now refuses an unusable reconcile read exactly as `resume` does, with the
refusal placed after the local prior-attempt check so the two verdicts local durable state can
positively reach still win. review-post **137/0** (122 before), full suite **935/0** against a
re-measured 920/0 baseline, ShellCheck v0.9.0 clean. PR #63 (draft).

(The 138/936 first written here was stale by one: the second commit merged two scenarios and
dropped a duplicate assertion. Corrected after the fresh-context validator reproduced 137/935
independently — a self-reported number nobody re-derives is exactly the kind that rots.)

- **DONE: AC-1** — `post` and `resume` reach the same verdict. RED recorded first against the
  pre-change code: 130 passed / 8 failed, including
  `post fails closed on an unusable reconcile list (expected [ambiguous], got [posted])` and
  `a refused post writes no review (expected [0], got [1])`. The fail-open was reproduced
  through the real CLI, not inferred from reading.
- **DONE: AC-2** — the refusal is settleable. The run keeps its `post.intent` and pending
  payload; a later `resume` against a usable list retries the identical payload once the confirm
  window has elapsed and reaches `posted`, with exactly one review in the store.
- **DONE: placement pinned.** Moving the guard before the local check in a scratch edit turned
  exactly the two placement tests red (`expected [posted_reconciled], got [ambiguous]`;
  `expected [prior_attempt_unsettled], got [reconcile_unavailable]`) and nothing else. The
  design decision is guarded, not incidental.
- **DONE: doc diff applied.** `reference/review-runtime.md:212`'s normative sentence rewritten
  (the carve-out removed, so rule (1) one paragraph earlier now holds without exception) and
  `kc-pr-flow/CLAUDE.md`'s once-only section carries the same one-rule statement.

### Two test-authoring corrections, recorded on purpose

1. The pre-existing unusable-list block's setup **depended on the fail-open it was not
   testing** — with all `list` calls unusable, `post` used to POST, which is what gave `resume`
   something to reconcile. Its first call is now `faithful`. A suite whose fixture leans on the
   bug under repair is a trap for the next person.
2. My own symmetry assertion originally compared `post`'s output against `resume`'s. That holds
   in the pre-fix world too (both said `posted`), so it would have passed in both worlds —
   decoration, not evidence. Both sides are now pinned to the literal verdict, which is why the
   clean RED shows 8 failures rather than 5.

### Not done, by scope

The shape-valid / content-invalid list (`{"reviews":[42]}`) is filed as
`reconcile-list-element-shape`; it needs a fix that changes both commands. The inability to
distinguish a `post` refusal from an ambiguous POST in the durable log is pre-existing and
unchanged.

## Stage Report: validation

TL;DR — **PASS with findings, all fixed.** A fresh-context validator reproduced both ACs
independently, a silent-failure lens and a codex cross-model round ran alongside, and 15 of 15
entity citations resolved exactly. Four defects surfaced; three are fixed and one NIT is declined
with a reason. The load-bearing one was mine: the sentence this task added to the protocol
document claimed an invariant the code does not hold. CI green on `553f935`.

### Per-AC results

- **AC-1 — `post` and `resume` reach the same verdict.** PASS, and stronger than the AC asks.
  Guard at `kc-pr-flow/scripts/review-post.sh:614-618`, asserted by
  `kc-pr-flow/scripts/review-post.test.sh:350-360`. The validator drove both commands through the
  CLI and got **byte-identical JSON**:
  `{"idempotency_key":"7530…","reason":"reconcile_unavailable","run_id":"run-piG63I","status":"ambiguous"}`,
  zero reviews in the store, pending payload kept, no `post.result` on the run. The pre-change
  behaviour was reproduced too, not inferred: on `origin/main` the same input returns
  `{"status":"posted"}` and writes a review, from the fall-through at
  `kc-pr-flow/scripts/review-post.sh:569`.
- **AC-2 — a refused run is settleable, not stranded.** PASS. The intent and pending payload the
  refusal preserves are written at `kc-pr-flow/scripts/review-post.sh:545-549` and
  `kc-pr-flow/scripts/review-post.sh:560`; settlement asserted by
  `kc-pr-flow/scripts/review-post.test.sh:363-365`. Three settlement paths exercised — `resume`
  against a usable list (`posted`, exactly one review, pending cleared, via
  `kc-pr-flow/scripts/review-post.sh:787-817`), `gc` inside and outside its window
  (`{"kept":1,"removed":0}` then `{"kept":0,"removed":1}` plus `run.invalidated{expired}`, via
  `kc-pr-flow/scripts/review-post.sh:869-894`), and a subsequent `post`
  (`prior_attempt_unsettled`, writes nothing, `kc-pr-flow/scripts/review-post.sh:601-603`).
  Worst-case ordering also held: two refused runs, resume the second then the first, **one review
  on the PR**.

Suites: review-post **137/0**, full seven **935/0** (305/213/135/137/68/43/34), against a
re-measured baseline of 920/0. Local and CI figures agree line by line.

### Reviewer rounds and how they were adjudicated

Three rounds ran: a fresh-context validator, `pr-review-toolkit:silent-failure-hunter`, and a
codex cross-model pass the validator drove. **Zero fabricated citations** in any round — 15/15
entity citations exact; codex 14/15 exact with one block-level imprecision, far under the
one-third discard threshold, so no round was discarded.

One finding was **adjudicated down against the code**. The silent-failure lens rated the
durable-log ambiguity MEDIUM on the reasoning that "pre-diff, reaching the log-ends-at-post.intent
signature required an actual network POST whose response was undecidable". That is false:
`review-post.sh:601-603`'s `prior_attempt_unsettled` path already writes the intent, makes **no**
POST, appends no event and returns 0. The equivalence class predates this change; this task adds
one more path into it and does not create it. The gap itself remains a named residual, as before.

### Defects found and fixed this round

1. **The doc claimed a guarantee the code does not make — mine, and a repeat of slice 1's P1.**
   The sentence added to `reference/review-runtime.md` said the refusal "leaves exactly one path
   to the POST". Reproduced against the *fixed* code: a body of `{"reviews":[42]}` passes
   `review_post_reviews_usable`, the marker scan errors mid-expression, its empty output reads as
   "marker absent", and `post` returns `status:"posted"` with a `remote_review_id`. Fixed by
   stating the guarantee as bounded by that validator's strength. The code-side gap stays
   deferred (it changes both commands; the shipped `gh` adapter cannot construct such a body),
   but an absolute claim in the document adapter authors treat as ground truth is not deferrable.
2. **Self-reported suite numbers were stale by one.** The implementation report and PR body said
   138/936; the second commit had merged two scenarios and dropped a duplicate assertion. 137/935
   is what the validator and CI both reproduce. Corrected in both places.
3. **`docs/review-runtime.md` was not synced.** Its reason table and `post` paragraph still
   described the fail-closed rule as resume-only, contrary to this plugin's own
   documentation-sync rule. Fixed.
4. **Declined, NIT** — `review-post.sh:601`'s stderr says "resume it instead", which is unhelpful
   when the list is still unusable, since resume would also refuse. No functional impact: the
   caller-visible status is `ambiguous` either way and the skill handles both identically.
   Declining rather than churning a message with no behavioural consequence.

### Adversarial spot-checks

Two, by different hands, both bit:

- Mine: moving the guard before the local check turned exactly the two placement tests red
  (`expected [posted_reconciled], got [ambiguous]`; `expected [prior_attempt_unsettled], got
  [reconcile_unavailable]`) and nothing else.
- The validator's, aimed at AC-2's own falsifier — injecting `rm -f pending-post.json` into the
  refusal branch — produced 132/5, including `a refused post keeps the pending payload
  (true→false)` and `settling a refused post writes exactly one review (1→0)`.

It also independently reproduced the RED (130 passed / 7 failed against my recorded 130 / 8); the
passed counts match exactly and the one-failure difference is precisely the assertion the second
commit merged away. Self-consistent, not contradictory.

### Correction-round budget

One round. Ideation estimate: one implementation session inside ~90 minutes. Actual: the
implementation commit plus two correction commits (CI budget, then the doc-honesty fix), inside
tolerance, no design reset. Disposition: **4 found, 3 fixed, 1 declined with reason, 0
fabricated**.

### Named residuals, all filed

- `reconcile-list-element-shape` — the shape-valid / content-invalid list. Sharpened this round:
  element **order** decides the outcome, and a bad element *before* the match reaches a live POST,
  so this task's fail-closed guarantee is bounded by `review_post_reviews_usable`'s strength.
  `review-post.sh:570` is also the one jq call in that function with no `|| return` guard.
- `gh-list-adapter-pagination` — found outside the blast radius: `gh api --paginate` combined with
  `--jq` emits one array per page, so `--argjson` fails and the transport aborts. The once-only
  path is therefore unusable on any PR whose reviews list paginates. Fail-closed, untouched here,
  and invisible to CI because every suite drives the injected stub instead of the `gh` adapter.
- `review-post-suite-cost` — measured this round rather than guessed: `python3` costs **565 ms**
  per launch here at 0% CPU against `jq`'s 6.8 ms, and one `post` spawns **65** of them.

### Other gates

ShellCheck **v0.9.0** (CI's pin, via the pinned image) clean on all eight files the workflow
checks. Cross-model gate satisfied by codex. Coverage: no diff-coverage tooling exists yet
(`executable-diff-coverage-ratchet` is still backlog), so waived as precedent allows, with the
manual check recorded — the three added executable lines (`:565`, `:569`, `:614-618`) are all
executed, and the spot-checks prove that coverage is load-bearing rather than incidental.

### Process miss, recorded

This task never wrote a `## Stage Report: ideation`, because backlog and ideation were presented
to the EM as one combined gate. The ideation content exists in the body as prose sections, but
`status --ac-scan` reads stage reports, so the gate's AC cross-check had nothing to anchor
against and passed by absence — exactly the failure the README's `--ac-scan` clause describes.
The clause caught it only retrospectively here because the scan was run late.
