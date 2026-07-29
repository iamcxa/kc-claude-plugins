---
title: The once-only path cannot work on a PR with more than one page of reviews
status: validation
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
- D5 launched 2026-07-29T13:25:12Z | tokens: pending

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
