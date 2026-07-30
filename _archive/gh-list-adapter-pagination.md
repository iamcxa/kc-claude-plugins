---
title: The once-only path cannot work on a PR with more than one page of reviews
status: done
source: found outside the blast radius during sv's fresh-context validation, 2026-07-26
started: 2026-07-29T07:44:33Z
completed: 2026-07-30T02:17:02Z
verdict: PASSED
worktree:
issue:
pr: pr-merge:89:artifact-v1:674502ed8b79b4f7d0a80cf9acc5affba03d434491e32d769273791c2933414c
design: trivial-pass
id: n9xjhpeza7q0hk3sepc6rxhc
lane: defect
pr_artifact_v1: eyJhdWRpdF9saW5rIjoiW245XSgvaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zL2Jsb2IvMzNjNDYwNzA2NTYzNTc2OTgxMzE4YTdmNTI3MjVlMTYzZTVmZTQ4NS9naC1saXN0LWFkYXB0ZXItcGFnaW5hdGlvbi5tZCkiLCJiYXNlIjoibWFpbiIsImJhc2Vfb2lkIjoiNDEwYTAwOTY3MzlkZWQ5YTIzYmViODUzYmUyODI0Mzk4M2JlNWMwZiIsImJvZHkiOiJCdXN5IHB1bGwgcmVxdWVzdHMgY2FuIG5vdyB1c2Ugb25jZS1vbmx5IHJldmlldyBwb3N0aW5nIHdpdGhvdXQgcGFnaW5hdGlvbiBmYWlsdXJlcyBvciBzaWxlbnRseSBhY2NlcHRpbmcgcGFydGlhbCBHaXRIdWIgcmVzdWx0cy5cblxuIyMgV2hhdCBjaGFuZ2VkXG5cbi0gQ29tYmluZSByZXZpZXdzIGZyb20gZXZlcnkgcGFnaW5hdGVkIEdpdEh1YiByZXNwb25zZSBpbnRvIG9uZSB0cmFuc3BvcnQgYXJyYXkuXG4tIEZhaWwgY2xvc2VkIHdoZW4gR2l0SHViIHJldHVybnMgcGFydGlhbCBvdXRwdXQgd2l0aCBhIG5vbnplcm8gc3RhdHVzLlxuLSBBZGQgcmVjb3JkZWQtcGFnZSByZWdyZXNzaW9uIGNvdmVyYWdlIGFuZCB0aGUgYWNjZXB0ZWQtdmFsaWRhdGlvbiBsZWRnZXIgcm93LlxuXG4jIyBFdmlkZW5jZVxuXG4tIGByZXZpZXctcG9zdC50ZXN0LnNoYDogMTQyLzE0MiBwYXNzZWQ7IGVhcm5lZCBzdWl0ZTogOTQwLzk0MCBwYXNzZWQuXG4tIFBhZ2luYXRpb24gYW5kIGZhaWwtY2xvc2VkIG11dGF0aW9ucyBlYWNoIHJldHVybmVkIDE0MSBwYXNzZWQgLyAxIGZhaWxlZDsgZGlmZiBjb3ZlcmFnZSAxMDAlOyBHZW1pbmkgQ0xFQU47IENsYXVkZSBFTSBQUk9DRUVEL0hJR0guXG5cbi0tLVxuXG5bbjldKC9pYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMvYmxvYi8zM2M0NjA3MDY1NjM1NzY5ODEzMThhN2Y1MjcyNWUxNjNlNWZlNDg1L2doLWxpc3QtYWRhcHRlci1wYWdpbmF0aW9uLm1kKVxuIiwiYm9keV9zaGEyNTYiOiIxNTQ4NDczN2U5NDQ1NGFiMmYxOGFlNjAyZmFmZTJhNTU5ODdmYTRiNzNiN2MyNGNiM2U0Nzk4NjNiYjc4NzQ3IiwiZGlmZl9zaGEyNTYiOiIxM2Y3NjhiOThiYWFjZTM3NDM2YTFmZWRmNWNjZmRjOTMxMmJkZmU1ODY2MDk4YmYzY2Y1NjAxOTU0MDM0NThjIiwiaGVhZCI6InNwYWNlZG9jay1lbnNpZ24vZ2gtbGlzdC1hZGFwdGVyLXBhZ2luYXRpb24iLCJoZWFkX29pZCI6ImFmNDY1YzQyYzQxZDMzNDgzMDQ3MmVkM2Y3ZDZmNDM0OGRmMTZkM2QiLCJsaXZlX3BhdGgiOiJnaC1saXN0LWFkYXB0ZXItcGFnaW5hdGlvbi5tZCIsInJlcG8iOiJpYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMiLCJ0aXRsZSI6ImZpeChrYy1wci1mbG93KTogY29tYmluZSBwYWdpbmF0ZWQgcmV2aWV3cyBhbmQgcHJlc2VydmUgZmFpbHVyZXMifQ
mod-block:
ledger_artifact_v1: eyJhdWRpdF9saW5rIjoiW245XSgvaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zL2Jsb2IvYjEwODc3YTdkOWQxZmQxNWE1MmM2MmRkNGI4N2Q4NjY0YjY3NDM5Ny9naC1saXN0LWFkYXB0ZXItcGFnaW5hdGlvbi5tZCkiLCJiYXNlIjoibWFpbiIsImJhc2Vfb2lkIjoiNzA5MzQyMzQwNDQzZGZmN2YxN2ViMmFjNmIxNzgyMzJjZTkzODhhOSIsImJvZHkiOiJGaW5hbGl6ZSBuOeKAmXMgbGFuZGVkIG1lYXN1cmVtZW50IHJvdyBzbyBpdHMgbGlmZWN5Y2xlIGNhbiBjbG9zZSBzYWZlbHkgd2l0aCBvYnNlcnZlZCB0aW1pbmcgYW5kIGEgZGF0ZWQgZGVmZWN0IHdpbmRvdy5cblxuIyMgV2hhdCBjaGFuZ2VkXG5cbi0gUmVwbGFjZSB0aGUgd2FsbC1jbG9jayBzZW50aW5lbCB3aXRoIHRoZSBvYnNlcnZlZCAxNy42OCBob3Vycy5cbi0gQ2hhbmdlIG9ubHkgZG9jcy9kZXYvbGVkZ2VyLmNzdjogb25lIHJvdywgdHdvIGNlbGxzLlxuLSBTZXQgdGhlIGVzY2FwZWQtZGVmZWN0IGRlYWRsaW5lIHRvIDIwMjYtMDgtMDYuXG5cbiMjIEV2aWRlbmNlXG5cbi0gRW1iZWRkZWQgbGVkZ2VyIGxpZmVjeWNsZSBmaXh0dXJlOiAxLzEgcGFzc2VkLlxuLSBUZXJtaW5hbCB2ZXJpZmljYXRpb24gYW5kIGZhaWwtY2xvc2VkIG5lZ2F0aXZlIGNhc2VzOiA2LzYgcGFzc2VkLlxuXG4tLS1cblxuW245XSgvaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zL2Jsb2IvYjEwODc3YTdkOWQxZmQxNWE1MmM2MmRkNGI4N2Q4NjY0YjY3NDM5Ny9naC1saXN0LWFkYXB0ZXItcGFnaW5hdGlvbi5tZClcbiIsImJvZHlfc2hhMjU2IjoiNGE4MmE0ZTcyNzEzNGEzM2RlYmU5YTllZjkwZGI0NzAyZDRkNTlmYjk0ZTFiMGZiYTI5MTk4ZmMzNGEyMzQyMiIsImRpZmZfc2hhMjU2IjoiMTE3NmYyMmVjMzA0ZWE0MWM2ZWMxNjhhOGE1NTYxM2FmMzJhZWQxMzUxMTllNWI3YjA1YzllODg4ZWNmNzVmYyIsImhlYWQiOiJkb2NzL2Rldi1sZWRnZXItbjkiLCJoZWFkX29pZCI6IjdkNmZkYTM2YjMyNmE4MmZjOWIxZmJkNGUwOTUxZWRjODliNTc3ZDQiLCJsaXZlX3BhdGgiOiJnaC1saXN0LWFkYXB0ZXItcGFnaW5hdGlvbi5tZCIsInByb2R1Y3RfYXJ0aWZhY3Rfc2hhMjU2IjoiNjc0NTAyZWQ4Yjc5YjRmN2QwYTgwY2Y5YWNjNWFmZmJhMDNkNDM0NDkxZTMyZDc2OTI3Mzc5MWMyOTMzNDE0YyIsInByb2R1Y3RfbWVyZ2VkX2F0IjoiMjAyNi0wNy0zMFQwMToyNToyN1oiLCJwcm9kdWN0X3ByIjo4OSwicmVwbyI6ImlhbWN4YS9rYy1jbGF1ZGUtcGx1Z2lucyIsInRpdGxlIjoiZG9jcyhkZXYpOiBmaW5hbGl6ZSBsZWRnZXIgZm9yIGdoLWxpc3QtYWRhcHRlci1wYWdpbmF0aW9uIn0
ledger_pr: ledger-merge:93:artifact-v1:aa993bdda18153ba939555d91f19c2e9884c0aed2f717797ecd3fe28ad038236
archived: 2026-07-30T02:21:56Z
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
explicitly never exercised there (`scripts/review-post.sh:206-207` at the cited pre-fix head). So
the fix needs a test that
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
- D2 launched 2026-07-29T08:47:19Z | tokens: n/a (Codex runtime did not expose per-worker usage)
- D3 launched 2026-07-29T09:16:25Z | tokens: n/a (Codex runtime did not expose per-worker usage)
- D4 launched 2026-07-29T09:52:24Z | tokens: n/a (Codex runtime did not expose per-worker usage)
- D5 launched 2026-07-29T13:25:12Z | tokens: n/a (Codex runtime did not expose per-worker usage)

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

## Stage Report: validation — 2026-07-29

- DONE: Independently reproduce AC-1 through `review_post_gh_transport list` with the recorded
  two-page response; prove one reviews array preserves ids 101, 102, and 201, then run the earned
  full suite from the exact implementation head.
  Direct adapter replay emitted one object with ids `[101,102,201]`; scoped test was 141/0 and the
  exact `8a0d39fdebbadb297f506ef431523d2bb1e86a11` seven-script suite was 939/0.
- DONE: Fire correctness and silent-failure lenses, verify every citation, measure executable diff
  coverage against the 85% policy, and perform a claim-breaking mutation in a scratch copy.
  Partial-upstream failure and malformed JSON both returned rc 74; xtrace covered 2/2 changed
  production commands (100%); restoring per-page arrays made the AC test red at 140/1.
- DONE: Run an independent cross-vendor review (attempt `agy` first, then a real different-vendor
  fallback if unavailable), fill all five evidence-block lines with actual outcomes, and report
  PASS/REJECT without editing implementation files.
  `agy` 1.1.8/Gemini returned CLEAN after an explicit worktree mount; every cited range was checked
  against exact head, and no implementation file was edited.
- DONE: Verify every citation.
  Commit/root-cause and cross-vendor citations resolve; the entity's historical
  `scripts/review-post.sh:99-100` citation is a non-blocking source typo—the relevant pre-fix
  comment is at lines 206-207 of `96fe7f3`.
- DONE: Report PASS/REJECT.
  PASS — AC-1 is reproduced, falsifiable, above the diff-coverage ratchet, and regression-clean.

### Evidence block

Lenses: executable Bash response-composition/error-path diff; correctness PASS (0 findings) and
silent-failure PASS (0 findings); no auth/permission, type, concurrency, resource, or manifest lens
surface changed.
Diff coverage: 100% (2/2 added production Bash command statements traced), above the 85% policy.
Adversarial: PASS — changing the projection back to per-page arrays produced nested arrays and
failed the named AC assertion, 140 passed / 1 failed.
Cross-model: `agy` 1.1.8 (Gemini, Google) CLEAN, 0 P0-P3; four cited ranges independently verified.
E2E: N/A — this bounded network-free adapter AC is exercised directly against recorded two-page
GitHub responses; live GitHub mutation is outside this AC.

### Summary

Validation PASS on exact implementation head `8a0d39f`. AC-1 preserved all three reviews in one
array, fail-closed behavior held under two upstream failure modes, the mutation proved the test is
load-bearing, and the earned suite returned 939/0. One historical entity citation typo is recorded
above; it does not change the implementation verdict.

### Feedback Cycles

#### Cycle 1 — Claude EM high-confidence brake

- Gate result: `PROCEED / MEDIUM`, zero material findings. The confidence brake was that the new
  pipeline's upstream-error propagation depends on file-level `set -o pipefail`, while no committed
  regression test pins that dependency.
- FO verification: on exact head `8a0d39f`, disabling `pipefail` and making `gh` emit one partial
  review before returning 1 produced `rc=0` with a usable `{reviews:[...]}` value. The concern is
  real and directly within this adapter change's silent-failure scope.
- Rework instruction: retain explicit `gh ... || return 74` handling while combining page items,
  and add a test proving partial output plus upstream failure returns 74 rather than an incomplete
  successful list. Do not expand into entity `11` or other once-only behavior.
- Budget at route-back: one correction commit expected, within the declared one-correction and
  75-minute tolerance.
- Finding disposition: **accepted as a real silent-failure defect**. Correction RED before the
  production edit was **141 passed / 1 failed**: with `pipefail` disabled, the fake `gh` emitted one
  projected review and returned 1; the adapter expected `rc:74|out:` but instead returned
  `rc:0|out:{"reviews":[...]}` with the partial review presented as usable.
- Correction commit: `0748cec` (`fix(kc-pr-flow): preserve gh list failure status`). The adapter
  now captures `gh` output and status first, explicitly returns 74 on upstream failure, and only
  then slurps the successful per-item stream into the existing `{reviews:[...]}` value. This
  preserves both the pagination repair and fail-closed behavior without relying on `pipefail`.
- Correction GREEN: `bash kc-pr-flow/scripts/review-post.test.sh` returned
  **142 passed / 0 failed**. The first GREEN attempt exited 74 before reaching the new assertion
  because earlier cases leave test-level `errexit` enabled; the test arrangement was corrected to
  disable `errexit` only while capturing the expected nonzero status, with no further production
  change.
- Correction exit verification:
  - Full workflow-earned seven-script suite — **940 passed / 0 failed**, about 11m39s local:
    runtime **305/0**, shadow **213/0**, benchmark **135/0**, once-only **142/0**, cross-model
    **68/0**, architecture docs **43/0**, and architecture validator **34/0**.
  - `bash -n` for both changed scripts — exit 0.
  - CI-pinned ShellCheck v0.9.0 over the documented four-file command — clean.
  - `git diff --check` — exit 0; correction commit contains only `review-post.sh` and
    `review-post.test.sh`.
- Final disposition: **resolved** in one correction commit, exactly matching the declared
  correction budget and remaining within the 75-minute tolerance. Entity 11, transport schema,
  unrelated once-only behavior, docs outside this stage report, versions, and marketplace metadata
  were not touched.
- Re-validation dispatch D4 produced no completion signal or durable report and disappeared from
  the Codex roster with no test process remaining. It is recorded as infrastructure-incomplete,
  not PASS or REJECT. D5 is a fresh replacement on the same exact head.

## Stage Report: validation D5 — 2026-07-29

### Summary

Correction-cycle revalidation **PASS** on exact code head
`0748cec6d37c8781181af6978ed0b880b21b2893`. A fresh direct adapter replay combined the recorded
two-page response into one three-review array with ids `[101,102,201]`. With `pipefail` explicitly
disabled, a fake `gh` that emitted one usable-looking partial review and then returned 1 produced
adapter rc 74 and no output. The scoped suite returned **142 passed / 0 failed**, and the final
earned seven-script suite returned **940 passed / 0 failed**.

No implementation file was edited. The code worktree remained clean on
`spacedock-ensign/gh-list-adapter-pagination` at the exact dispatched head.

### Acceptance and correction evidence

- **AC-1 PASS:** Directly sourced `review-post.sh`, replayed
  `gh-reviews-two-pages.jsonl` through the adapter's requested per-page `--jq` filter, and invoked
  `review_post_gh_transport list`. The fixture count was 2 pages; output was one
  `{reviews:[...]}` object with array length 3 and ids `[101,102,201]`.
- **Correction guarantee PASS:** After sourcing the production adapter, set `+o pipefail`; the
  fake `gh` wrote review id 101 and returned 1. The adapter returned rc 74 with empty stdout, so
  partial upstream output was not presented as a successful list.
- **Scoped regression:** `bash kc-pr-flow/scripts/review-post.test.sh` —
  **142 passed / 0 failed**.
- **Final earned suite:** **940 passed / 0 failed**:
  `review-runtime.test.sh` **305/0**, `review-shadow.test.sh` **213/0**,
  `review-runtime-benchmark.test.sh` **135/0**, `review-post.test.sh` **142/0**,
  `cross-model.test.sh` **68/0**, `review-architecture-diagrams.test.sh` **43/0**, and
  `review-architecture-diagrams-validator.test.sh` **34/0**.
- **Static checks:** `bash -n` for `review-post.sh` and `review-post.test.sh` exited 0;
  CI-pinned ShellCheck v0.9.0 over the documented four-file command returned no diagnostics;
  `git diff --check` exited 0.

### Lens and citation verification

- **Correctness PASS, 0 findings:** Successful paginated item output is captured completely and
  slurped once into the existing flat `{reviews:[...]}` transport shape. The AC replay and
  pagination mutation independently exercised the changed composition.
- **Silent-failure PASS, 0 findings:** The `gh` command substitution's status is checked before
  `jq` consumes captured output. The direct `pipefail`-disabled failure replay and status-capture
  mutation independently exercised the guard.
- No security/auth/permission, type-design, concurrency, resource-lifecycle, or
  manifest/back-compat surface changed; the diff is limited to Bash response composition,
  explicit upstream-error handling, its test, and the recorded fixture.
- `agy` 1.1.8 returned **CLEAN**, 0 P0-P3. The CLI request named
  `gemini-3.1-pro-high`; the response self-reported **Gemini 3.6 Flash**. Both are Google models,
  so the run remains cross-vendor relative to Codex, and the model-name discrepancy is recorded
  rather than normalized away.
- All three reviewer citations were independently verified at exact head:
  `review-post.sh:233-238`, `review-post.test.sh:666-717`, and the complete two-line
  `gh-reviews-two-pages.jsonl` fixture. All cited code and test ranges matched the review; no
  citation was wrong or discarded.

### Claim-breaking mutations

- **Pagination combination:** In an isolated scratch copy, changed the adapter projection back to
  one array per page. The committed suite returned **141 passed / 1 failed**; the named two-page
  assertion observed nested page arrays instead of one flat reviews array.
- **Explicit upstream-error capture:** In a separate isolated scratch copy, restored the
  pipefail-dependent `gh | jq` pipeline while leaving pagination combination intact. The committed
  suite returned **141 passed / 1 failed**; the named partial-output assertion expected
  `rc:74|out:` but observed rc 0 with the partial review wrapped as usable output.

### Evidence block

Lenses: executable Bash response-composition/error-path diff; correctness PASS (0 findings) and
silent-failure PASS (0 findings); no other mechanical lens matched the changed surfaces.
Diff coverage: 100% — xtrace exercised 3/3 changed executable statements (`local` declaration,
explicit `gh` capture/status check, and successful `jq` slurp), including the upstream-failure
return branch; above the 85% ratchet.
Adversarial: PASS — two independent scratch mutations each made its named committed assertion red:
pagination nesting **141/1**, and missing explicit upstream-status capture **141/1**.
Cross-model: `agy` 1.1.8 / Google review CLEAN, 0 P0-P3; request specified
`gemini-3.1-pro-high`, response self-reported Gemini 3.6 Flash; 3/3 cited artifacts verified.
E2E: N/A — the ideation AC defines a network-free adapter replay against recorded GitHub pages;
live GitHub review mutation is outside this bounded acceptance criterion.

### Verdict

**PASS for correction cycle 1.** AC-1 and the explicit upstream-failure guarantee are independently
reproduced, both committed guards are claim-breaking, diff coverage is above policy, the
cross-vendor review is clean with verified citations, and the exact-head earned suite is
regression-clean. The correction remains within the declared one-commit budget and does not expand
into entity 11.

## Fresh Claude EM gate — correction cycle 1

- Verdict: **PROCEED**
- Confidence: **HIGH**
- Material findings: **none**
- Prior confidence brake: **resolved**. The adapter now checks the `gh` command substitution's
  status explicitly before parsing captured output, and the committed regression disables
  `pipefail` while proving partial output plus upstream failure returns 74 with empty stdout.
- Scope: all three changed files serve AC-1; no transport schema, reconciliation contract,
  sibling-entity, version, or marketplace surface changed.
- Evidence accepted: exact head `0748cec`, scoped **142/0**, earned suite **940/0**, two
  independent claim-breaking mutations **141/1** each, diff coverage **100%**, ShellCheck v0.9.0
  clean, and cross-vendor review clean with verified citations.

## Stage Report: validation (post-rebase premerge) — 2026-07-29

- DONE: Verify current ownership and rebase the validated fix onto the prerequisite-complete trunk.
  The clean isolated branch rebased from `0748cec` onto exact `origin/main`
  `410a0096739ded9a23beb853be28243983be5c0f` with no conflict; exact new head is
  `af465c42c41d334830472ed3f7d6f4348df16d3d`.
- DONE: Preserve the validated product fix and stop on substantive conflict or scope drift.
  Rewritten product commits are `13cd2e8` (pagination combination) and `fca5f2c` (explicit upstream
  status); the product behavior diff remains the same three n9 files with no entity-11 spill.
- DONE: Add the unique n9 accepted-validation premerge ledger row.
  Commit `af465c4` adds only `n9xjhpeza7q0hk3sepc6rxhc, gh-list-adapter-pagination, 5, 1,
  pending:done, n/a, 100, pending:merge`; the canonical premerge verifier returned
  `ledger:exact`, and terminal verification is not applicable before the product merge.
- DONE: Re-run exact-head scoped and earned verification after the rebase and ledger commit.
  Direct probes returned ids `[101,102,201]` and rc 74/empty for pipefail-disabled partial failure;
  scoped suite was **142/0** and the seven-script earned suite was **940/0**.
- DONE: Re-run both independent claim-breaking mutations and executable diff coverage.
  Pagination nesting and missing explicit status capture each made its named assertion red at
  **141/1**; xtrace covered 3/3 changed executable statements plus the failure branch (**100%**).
- DONE: Validate the workflow, ledger-only diff, and static gates.
  Spacedock returned `VALID` with only pre-existing lowercase-verdict warnings on other entities;
  the ledger word diff is one row, and `bash -n`, ShellCheck v0.9.0, and `git diff --check` are clean.
- DONE: Run fresh cross-model and Claude EM gates.
  `agy` 1.1.8 returned **CLEAN**, 0 P0-P3, self-reporting Gemini 3.6 Flash (High); all six cited
  artifacts/ranges resolved. The first Claude attempt timed out after eight silent minutes and
  produced no verdict; the bounded tool-free fresh Sonnet retry returned **PROCEED / HIGH**,
  no material findings, and marked the prior pipefail brake **RESOLVED**.
- SKIPPED: Push the product branch or create a PR.
  Explicitly outside this worker assignment; the branch remains local-only for the FO merge flow.

### Evidence block

Lenses: executable Bash response-composition/error-path plus one ledger row; correctness PASS
(0 findings), silent-failure PASS (0 findings), and ledger-contract PASS (0 findings).
Diff coverage: 100% — 3/3 changed executable statements and the upstream-failure branch traced.
Adversarial: PASS — two isolated mutations each produced its intended named **141/1** failure.
Cross-model: Google CLEAN, 0 P0-P3 with six cited artifacts verified; Claude EM PROCEED/HIGH.
E2E: N/A — ideation defines a recorded-page adapter replay; live GitHub mutation remains outside AC.

### Summary

Post-rebase premerge validation passes on exact base `410a009` and head `af465c4`. The four-file
diff is the unchanged validated adapter fix/test/fixture plus its unique truthful ledger row; no
conflict, scope drift, product push, or PR creation occurred.
