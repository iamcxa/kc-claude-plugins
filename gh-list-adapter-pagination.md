---
title: The once-only path cannot work on a PR with more than one page of reviews
status: implementation
source: found outside the blast radius during sv's fresh-context validation, 2026-07-26
started: 2026-07-29T07:44:33Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-gh-list-adapter-pagination
issue:
pr:
design: trivial-pass
id: n9xjhpeza7q0hk3sepc6rxhc
lane: defect
---

`review_post_gh_transport`'s `list` op (`scripts/review-post.sh:233-237` on
`origin/main` at `96fe7f3`) runs

```
gh api "repos/$repo/pulls/$pr/reviews" --paginate --jq '[.[] | {id, user: .user.login, body, commit_id}]'
```

then feeds the result to `jq -cn --argjson reviews "$reviews"`. With `--paginate`, `gh` applies
the `--jq` filter **per page** and concatenates the outputs, so a two-page PR yields two
back-to-back JSON arrays. `--argjson` accepts exactly one JSON value, so it fails, the transport
returns non-zero, and both `post` and `resume` abort with rc 74.

The direction is safe — it fails closed, and it is incidentally why the `gh` adapter cannot
produce the exit-0-non-array body that `reconcile-list-element-shape` is about. But the
consequence is that **the entire once-only posting path is unusable on any PR whose reviews list
paginates**, which for a busy PR is not an exotic case. Nobody has hit it yet because
`KC_PR_FLOW_ONCE_ONLY_POST` defaults off.

CI cannot catch this: every suite drives the injected stub transport, and the `gh` adapter is
explicitly never exercised there (`scripts/review-post.sh:99-100`). So the fix needs a test that
exercises the adapter's own composition against a recorded multi-page response, not another stub
scenario.

**AC-1 — A reviews list spanning more than one page produces one usable array.**
Verified by: driving the `gh` list adapter against a recorded two-page response and asserting a
single `{reviews: [...]}` object containing every review from both pages. Falsified by: the
transport returning non-zero, or dropping the reviews from any page.

## Defect-lane classification

All four bounded-defect conditions hold:

1. Root cause is identified at `scripts/review-post.sh:233-237`: `gh --paginate`
   applies `--jq` per page, producing adjacent arrays that `jq --argjson` cannot
   consume as one value.
2. Acceptance is mechanical: the recorded two-page adapter test above must fail
   before the fix and pass after it.
3. This is one seam: the production `gh` transport's `list` composition and its
   adapter-level test. No schema, UI, or cross-layer contract changes.
4. No design choice is open: preserve the existing `{reviews: [...]}` transport
   result and combine every page before constructing it.

Design: `trivial-pass` — the fix restores the already-defined transport shape
without deciding a new interface.

Appetite: one implementation dispatch, estimated 45 minutes. Tolerance: up to
75 minutes or one correction commit; if the repair requires a new transport
schema, changes the once-only reconciliation contract, or spills into `11`
(`reconcile-list-element-shape`), return to ideation instead.

Implementation dispatch sizing: one fresh worker in one isolated worktree.
Validation remains a fresh-context gate.

## Measurement

- D1 launched 2026-07-29T08:05:41Z | tokens: n/a (Codex runtime did not expose per-worker usage)

## Stage Report: implementation — 2026-07-29

### Summary

Implemented the bounded default-`gh` adapter repair in code commit `8a0d39f`
(`fix(kc-pr-flow): combine paginated review listings`). The list operation now projects one review
object per paginated item and slurps the complete stream into the existing single
`{reviews:[...]}` transport value. No transport schema, once-only reconciliation behavior, entity
11 work, documentation contract, version, or marketplace metadata changed.

- DONE: Added `gh-reviews-two-pages.jsonl`, a recorded two-page GitHub reviews response with two
  reviews on page one and one on page two.
- DONE: Exercised `review_post_gh_transport list` itself by replaying GitHub's per-page `--jq`
  behavior; the injected posting transport remains responsible for network-free post/reconcile
  scenarios.
- DONE: Preserved all three projected review fields plus author login for every page, including
  review ids `101`, `102`, and `201`, in one usable transport object.
- DONE: Final code commit is limited to `review-post.sh`, `review-post.test.sh`, and the recorded
  two-page fixture.

### RED → GREEN evidence

- RED before the production edit: `bash kc-pr-flow/scripts/review-post.test.sh` returned
  **140 passed / 1 failed**. The new behavior assertion
  `the gh list adapter combines every review from two pages` expected one
  `{reviews:[...]}` value containing review ids `101`, `102`, and `201`, but the adapter returned
  `rc:2` when `jq --argjson` received the two adjacent per-page arrays.
- Arrangement precondition: `the gh reviews fixture records two pages` passed in the same RED run.
  This assertion is intentionally green before and after the fix; it proves the recorded response
  exercised pagination and is not a behavior claim.
- GREEN after the minimum production edit: the same command returned
  **141 passed / 0 failed**. The adapter emitted exactly one object whose reviews array contained
  all three literal expected projections.

### Existing list-arrangement audit

- Faithful/default stub-list scenarios were not edited. They still arrange one already-composed
  `{reviews:[...]}` transport response and continue to cover normal posting, ambiguous recovery,
  truly-lost retry, identity-independent marker matching, repeat posting, and authorization.
- Lagging-list scenarios at the post/resume, malformed-window, unsettled-prior-run, and
  definitively-landed-prior-run boundaries were not edited. They still arrange a usable but stale
  empty array and retain their original duplicate-suppression and local-prior-state intent.
- Unusable-list scenarios for resume, fresh post, definitively posted prior state, and unsettled
  prior state were not edited. They still arrange `{reviews:null}` and retain their original
  fail-closed and check-placement intent.
- No existing fixture was narrowed or repurposed. The new recorded-page case is separate because it
  tests production adapter composition before the shared transport contract those scenarios
  intentionally begin from.

### Verification evidence

- Scoped RED/GREEN: `bash kc-pr-flow/scripts/review-post.test.sh` —
  **140/1 RED**, then **141/0 GREEN**.
- Full workflow-earned exit suite — **939 passed / 0 failed**:
  - `review-runtime.test.sh` — **305/0**, 144.80s local.
  - `review-shadow.test.sh` — **213/0**, 317.58s local.
  - `review-runtime-benchmark.test.sh` — **135/0**, 29.78s local.
  - `review-post.test.sh` — **141/0**, 411.28s local.
  - `cross-model.test.sh` — **68/0**, 0.45s local.
  - `review-architecture-diagrams.test.sh` — **43/0**, 0.75s local.
  - `review-architecture-diagrams-validator.test.sh` — **34/0**, 0.87s local.
- `bash -n` for `review-post.sh` and `review-post.test.sh` — exit 0.
- CI-pinned ShellCheck v0.9.0 Docker command from `kc-pr-flow/CLAUDE.md` over
  `review-runtime.sh`, `review-post.sh`, `review-post.test.sh`, and `stub-transport.sh` — clean.
- `git diff --check` — exit 0. Committed scope is exactly the three n9 deliverable files above;
  code worktree clean at `8a0d39f`.

CI will newly execute the recorded two-page adapter case because both changed paths already select
`review-runtime-tests.yml`. That case adds two assertions (one arrangement precondition and one
behavior claim) and one small `jq` replay. The workflow records a 9m07s baseline under its current
20-minute cap, leaving 10m53s before this change; the complete local earned suite took about
15m06s. Exact-head CI remains the merge authority.
