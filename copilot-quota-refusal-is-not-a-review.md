---
title: The copilot extension reads a quota-limit refusal as "Copilot not run", never as an answered review, and FO's merge ask names it unread
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:copilot-quota-refusal-is-not-a-review:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:copilot-quota-refusal-is-not-a-review-backlog-1
              briefing:
                id: briefing:copilot-quota-refusal-is-not-a-review:backlog:attempt-1:revision-1
                digest: sha256:9766c3e0940f18f3725c5b5e55fcf2f62d1430747aa870036f9e32ce88d8761a
                room-ref: ./copilot-quota-refusal-is-not-a-review/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:copilot-quota-refusal-is-not-a-review:backlog:1
                briefing: briefing:copilot-quota-refusal-is-not-a-review:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T06:56:03.975306Z"
                decision: approve
                reason: 'Captain 2026-10-13: 「是」 to the backlog gate question "Schedule this task now as Pilot and enter ideation", after asking 「Copilot 的 task是否可以先排？因為顯然會接下來一直遇到此問題」; profile pilot selected.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:copilot-quota-refusal-is-not-a-review:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:copilot-quota-refusal-is-not-a-review-ideation-1
              briefing:
                id: briefing:copilot-quota-refusal-is-not-a-review:ideation:attempt-1:revision-1
                digest: sha256:a722955d0bd9a35bb4f95ed6b0acd1e997b4416abd62e3163fb05cad3ba3be6b
                room-ref: ./copilot-quota-refusal-is-not-a-review/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:copilot-quota-refusal-is-not-a-review:ideation:1
                briefing: briefing:copilot-quota-refusal-is-not-a-review:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T07:05:21.473291Z"
                decision: approve
                reason: 'Captain 2026-10-13: 「准」 to the ideation gate question, after asking how gh can read the Copilot quota and what happens if Copilot changes its reply format; the question stated that approval accepts the recommendations for D1 (fail closed on any heading-less, comment-less answer) and D2 (no re-request after a refusal until the Captain says the quota is back).'
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-13T06:56:42Z
worktree: .worktrees/spacedock-ensign-copilot-quota-refusal-is-not-a-review
---

On 2026-10-13 FO requested Copilot on iamcxa/kc-claude-plugins #627 and #628 (task `journey-map-dev2-contract`). Six seconds later Copilot left a COMMENTED review on each: "Copilot was unable to review this pull request because the user who requested the review has reached their quota limit." `python3 <package>/extensions/copilot/copilot_review.py iamcxa/kc-claude-plugins 627` printed `answered on 32db12730: "no heading", 0 line comment(s); evidence=review:5499757433` and exited 0 (the same for #628, review:5499757731). Exit 0 is the reader's "answered" result, so a quota refusal reads like a review of the head with no findings unless FO reads the body.

## Captain's words

Captain 2026-10-13, in chat, after FO reported the quota refusal and asked whether to merge #627 without Copilot: 「不等 Copilot，也要修復它額度不足時的應對方式」

## Scope

- The reader and FO's handling when Copilot refuses for quota: it must not count as a round or as a clean read; it is reported as `copilot not run: <reason>`, as `## Extensions` already requires for a listed extension that cannot run.
- What FO does next when the second reviewer cannot run (the Captain ruled this time: do not wait).
- Non-goals: (1) changing how FO judges whether a real Copilot review is clean; (2) teaching Copilot's review layouts to the script (it still does not judge findings); (3) the Codex reader (`codex_review.py`) and kc-pr-flow, neither of which was observed to mishandle a refusal (see Upstream check); (4) fixing the requester's Copilot quota, which is the account's allowance, not the package's; (5) any change to the adopter's `## Extensions` rule, which already requires `<name> not run: <reason>`.

## Design

### Upstream check (2026-10-13, read only)

- Chain checked in order: spacedock (no Copilot logic), kc-dev-flow-2 package at `Package root` 0.21.0 whose `extensions/copilot/` is byte-identical to origin/main 133f1315 (`git show origin/main:kc-dev-flow-2/extensions/copilot/<file> | diff -q` for all three files), then kc-pr-flow.
- `codex_review.py`: no non-review-answer recognition. It stays fail-closed by construction: its EXTENSION.md Limits say "a shape it does not recognize reads as findings or as no verdict, never as clean", and a bot review without the clean sentence reads as findings. It was not observed to meet a refusal; out of scope.
- kc-pr-flow: `grep -rniE "quota|unable to review|cannot review" kc-pr-flow` finds only unrelated quota prose (Sentry, post quota). Nothing recognises a Copilot non-review answer there.
- The adopter README `## Extensions` already says: a listed extension that cannot run is `<name> not run: <reason>`, never a clean result; a merge ask names each unread listed reviewer. So the rule exists; the copilot reader gives FO no exit code that means "not run" for this case. Per the repository's own finding "a rule gap is usually an enforcement gap", the fix is in the reader and the EXTENSION.md Read paragraph, not a new rule.

### Existing-code check (bounded)

Observation, reproduced this stage: `python3 <package>/extensions/copilot/copilot_review.py iamcxa/kc-claude-plugins 627` prints `answered on 32db12730: "no heading", 0 line comment(s); evidence=review:5499757433 at 2026-10-13T06:46:13Z` and exits 0. `gh api repos/iamcxa/kc-claude-plugins/pulls/627/reviews/5499757433` and `.../628/reviews/5499757731` return body `Copilot was unable to review this pull request because the user who requested the review has reached their quota limit.` with `state: COMMENTED`, bot `copilot-pull-request-reviewer[bot]`, no line comment on either. (#628's head has since moved to 0286f8e74, so its live read is exit 4; the recorded body is the evidence.) Conclusion: repair the reader in place (about 8 changed lines plus tests), reuse `heading()` and the existing exit-code table; add nothing new. `pr_watch.py` maps unknown exit codes to `error`, so it needs one mapping line.

### PRFAQ

**Press release.** When Copilot cannot review a pull request, FO now says so: `copilot not run: <what Copilot wrote>`. The refusal is never counted as a review round, never read as a clean review, and FO does not wait for Copilot or ask again on its own. The merge ask names Copilot as not read, with Copilot's own words, and the Captain decides.

**FAQ**
- *What is a review?* An answer that has a review heading (`### ...` or `## Pull request overview`) or at least one line comment of its own. Anything else Copilot answers is "not a review", whatever the reason (quota, an error, another language, an empty body). The script does not need to know the reason; it quotes the first 120 characters.
- *Why not match the quota sentence?* A text match covers one wording in one language and fails open on the next refusal. Requiring positive review evidence fails closed on every non-review answer (the Codex reader already works this way). Cost: a future Copilot layout with no heading and no line comment reads "not run" until the script learns it, and FO reads the quoted body anyway.
- *Does a refusal erase an earlier real review of the same head?* No. The latest real review on the head decides; a refusal after it adds nothing. The refusal still answers the request, so `exit 3` (requested, waiting) ends.
- *What does FO do next?* Records `copilot not run:` in the gate summary, does not count a round, does not wait (the Captain ruled 「不等 Copilot」), keeps going with the other reviewers and gates, does not re-request Copilot for this task unless the Captain says its quota is back, and names Copilot as not read in the merge ask.
- *Who fixes the quota?* The account that requested the review (the refusal says "the user who requested the review"). Out of scope; the quote tells the Captain which allowance ran out.

### Mermaid

```mermaid
flowchart TD
    A[FO requests Copilot on the PR head] --> B[copilot_review.py reads the head]
    B --> C{Copilot reviewed since the request?}
    C -- request newer than any review --> W[exit 3 requested: FO waits, no round]
    C -- no Copilot review of the head --> N[exit 4 not reviewed: no round, merge ask names Copilot unread]
    C -- a bot review of the head exists --> D{Any review of the head has a heading or its own line comment?}
    D -- yes, latest such review --> R[exit 0 answered: evidence=review:id, one round per id; FO reads it as today]
    D -- no --> X[exit 5 not a review: answer=review:id plus first 120 chars, no evidence=]
    X --> F1[FO records 'copilot not run: reason' in the gate summary]
    F1 --> F2[No round counted, not clean, no wait, no re-request this task]
    F2 --> F3[FO continues other reviewers and gates]
    F3 --> M[Merge ask names Copilot as not read with the quote]
    M --> K{Captain decides}
    K -- merge --> Z[Captain merges]
    K -- retry after quota restored --> A
    P[pr_watch wait] -. maps exit 5 to not-run and wakes once .-> F1
```

Actors and order match the prose: the reader is the only classifier; FO acts on the exit code; the Captain owns the merge and any retry.

### Surfaces

`Surfaces: none`: no UI and no schema; PRFAQ and Mermaid only.

### Delivery shape (for implementation, not decided here)

Changes in `kc-dev-flow-2/extensions/copilot/copilot_review.py` (state(): choose real reviews, exit 5, docstring), its `test_copilot_review.py`, `kc-dev-flow-2/extensions/copilot/EXTENSION.md` (Read paragraph and Limits), and `kc-dev-flow-2/scripts/pr_watch.py` plus `test_pr_watch.py` (one mapping, one `OUTCOMES` word). Conventional-commit title `fix(kc-dev-flow-2): ...`; release-please versions it; the adopter picks it up through the normal workflow sync. A prototype in `/tmp/cq-proto` (outside the repository, disposable) ran the two recorded bodies to exit 5 and failed exactly one existing test: `test_the_answer_is_reported_the_same_whatever_copilot_found` pins `"Looks good"` with no heading as answered; that test changes under Decision D1.

## Unresolved decisions for the Captain

- **D1: fail closed on any answer with no review heading and no line comment?** Recommend yes. It makes one existing test change (a heading-less, comment-less answer such as "Looks good" becomes `not a review`) and also covers errors, empty bodies and other languages with no wording list. Worse under yes: a future Copilot layout without a heading or line comment reads "copilot not run" until the script is taught, costing one quoted-body read. The alternative, matching the quota sentence only, leaves every other non-review answer reading as answered. Not a regression of a past ruling: no `Override:` line on a Copilot or reviewer decision and no ADR under `docs/adr` mentions Copilot (`git grep 'Override:'` in this checkout and `grep -rli copilot docs/adr`, 2026-10-13).
- **D2: after a refusal, may FO request Copilot again in this task?** Recommend no, until the Captain says the quota is back; he can then ask for it, and the merge ask lists "retry" as an option. Worse under no: if the quota resets mid-task Copilot stays unread until the Captain notices. The alternative (one retry per new head) sends a request that the recorded #627 and #628 refusals show is answered in seconds with another refusal, adds a bot review to the PR each time, and gains nothing while the quota is out.

## Acceptance criteria

Evidence commands run from `<package>/extensions/copilot/` (`<package>` is the Package root), using `python3 -B`.

**AC-1** The reader exits 5, never 0, on the recorded quota refusals of iamcxa/kc-claude-plugins #627 (review:5499757433, head 32db127303d4c913839952d7732e6c1693ea2305) and #628 (review:5499757731, head 7d89898e4d7a57f83144f3d2f6310d0256ef2524), and prints no `evidence=` token. Evidence: a unit test feeds `state()` those two review objects with the body copied verbatim from `gh api repos/iamcxa/kc-claude-plugins/pulls/627/reviews/5499757433` (and `.../628/reviews/5499757731`) and zero line comments, and asserts code 5, `answer=review:<id>` in the line and `evidence=` absent; run `python3 -B -m unittest test_copilot_review`. Falsifier: at the current code the same two inputs return code 0 with `evidence=review:5499757433` (reproduced live on #627 this stage), so the test fails on 0.21.0 and passes only with the repair. Status: not yet verified (implementation).

**AC-2** Any other answer with no review heading and no line comment is also exit 5: an empty body, an unrelated error sentence, and a non-English sentence. Evidence: three unit-test inputs in the same test class assert code 5. Falsifier: a denylist that matches only the English quota sentence passes AC-1 and fails this criterion. Status: not yet verified.

**AC-3** A real review still reads as answered, with the same line as today, for each existing layout: `### 🟢 Approval recommended`, `### 🟡 Changes recommended`, `## Pull request overview`, and a body with no heading but at least one line comment of its own. Evidence: the existing tests `test_an_answer_on_the_head_names_the_review_its_heading_and_line_comments`, `test_the_latest_review_of_the_head_is_named`, `test_a_heading_cannot_carry_its_own_evidence_id` pass unchanged, plus a new test for the heading-less review with a line comment (code 0, heading `no heading`). Falsifier: requiring a heading alone would fail the new line-comment test. The one changed test is `test_the_answer_is_reported_the_same_whatever_copilot_found`, whose `"Looks good"` case moves to code 5 under Decision D1. Status: not yet verified.

**AC-4** A refusal does not erase an earlier real review of the same head and does answer a pending request. Evidence: two unit tests: (a) a real review then a later refusal, both on the head, gives code 0 naming the real review's id; (b) a request, then a refusal after it, gives code 5, while a request newer than the refusal gives code 3. Falsifier: choosing `on_head[-1]` regardless of content fails (a); excluding the refusal from the review-time comparison fails (b). Status: not yet verified.

**AC-5** `pr_watch.py` reports `copilot=not-run` for exit 5 and wakes `wait` once on that change without recording an evidence id. Evidence: a unit test calls `watch.copilot()` with the subprocess stubbed to return code 5 and the refusal line, and asserts the pair `("not-run", "-")`; a second asserts `not-run` is in the copilot wake outcomes. Falsifier: without the mapping the pair is `("error", "-")`, which also wakes but mislabels a refusal as a failure of the reader. Status: not yet verified.

**AC-6** `EXTENSION.md` tells FO what to do on exit 5, and agrees with the script: it lists exit 5 as `copilot not run: <the printed reason>`, states that it is no round, not clean, not waited for and not re-requested in the task, and that the merge ask names Copilot as not read with the printed quote; Limits records the 2026-10-13 quota refusal and the residual that a refusal carrying its own heading would read as answered. Evidence (consistency only): a command that extracts the `Exit N` lines from the `copilot_review.py` docstring and checks each N appears in `EXTENSION.md`'s Read paragraph. Evidence (behaviour, observed later): at the next Copilot refusal, the observer reads the gate summary for a `copilot not run:` line, an unchanged round count and a merge ask naming Copilot unread. Falsifier: removing the exit 5 sentence from `EXTENSION.md` fails the consistency command. Status: not yet verified; the behaviour half is verifiable only at a future refusal, and until then it is a stated limit, not a passed result.

**AC-7** No change to Codex or kc-pr-flow files. Evidence: `git diff --name-only origin/main...HEAD` of the implementation PR lists only the four files above plus their tests. Falsifier: any path under `extensions/codex/` or `kc-pr-flow/` in that list. Status: not yet verified.

## FO alignment

Alignment: not needed before ideation; the Captain's two rulings fix the direction (do not wait for Copilot; repair the quota handling, scheduled now as Pilot). Open for ideation, not a Captain question: whether other non-review Copilot answers (an error, a "cannot review" text in another language) share the fix.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

## Number guards

ADR: 0013

## Stage Report: ideation

- DONE: A design (PRFAQ and Mermaid) for how the copilot extension and FO treat a Copilot answer that is not a review (today's quota-limit refusal at minimum): reported as `copilot not run: <reason>`, never counted as a round or read as clean, and FO's next step when the second reviewer cannot run, consistent with the README's `## Extensions` rule and the Captain's rulings in the task
  `## Design` holds the upstream check, PRFAQ and flowchart; the reader gets exit 5, FO records `copilot not run:`, does not wait or re-request, and the merge ask names Copilot unread. `python3 <package>/scripts/design_surfaces.py check <task>` printed "design surfaces presentable", exit 0.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, including one that runs `copilot_review.py`'s reading logic on the recorded refusal bodies of iamcxa/kc-claude-plugins #627 (review:5499757433) and #628 (review:5499757731) and fails if they read as answered
  AC-1 is that test; a disposable prototype in `/tmp/cq-proto` (outside the repo) returned code 5 on both recorded bodies, and the unmodified 0.21.0 reader returns exit 0 on live #627. AC-1 through AC-7 each carry "Status: not yet verified" because implementation has not run.
- DONE: Unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  D1 (fail closed on any heading-less, comment-less answer; changes one existing test) and D2 (no re-request after a refusal until the Captain says quota is back), both in `## Unresolved decisions for the Captain`.

### Per-criterion evidence

- AC-1: prototype result only (exit 5 on both bodies; live #627 at 0.21.0 exits 0). Not yet verified in the repository.
- AC-2 to AC-7: designed, not yet verified; AC-6's behaviour half can only be observed at a future Copilot refusal.

### Summary

Upstream check found no existing non-review recognition in `codex_review.py` or kc-pr-flow; the `## Extensions` rule already demands `copilot not run`, so the repair is one reader branch, one `pr_watch.py` mapping and an EXTENSION.md paragraph. The prototype also showed the one cost: a heading-less, comment-less answer ("Looks good" in an existing test) stops reading as answered (D1). No repository file, branch, commit or PR comment was made.

## Stage Report: implementation

- DONE: One Draft PR (fix(kc-dev-flow-2): ...) from a branch off origin/main changing only copilot_review.py, test_copilot_review.py, extensions/copilot/EXTENSION.md, scripts/pr_watch.py, test_pr_watch.py and ADR 0013; AC-1 to AC-7 green with each falsifier shown failing by a mutation run (AC-6's behaviour half named as a limit)
  Draft PR #630 (iamcxa/kc-claude-plugins, branch spacedock-ensign/copilot-quota-refusal-is-not-a-review, commit 218645da, base 9e68eb87); `git diff --name-only origin/main...HEAD` lists exactly those six paths (AC-7).
- DONE: ADR 0013 records D1 (fail closed on any heading-less, comment-less answer) and D2 (no re-request after a refusal until the Captain says the quota is back), with the Captain's words; adr_lint.py docs/adr --require 0013 passes
  `docs/adr/0013-a-copilot-answer-without-a-review-is-not-run-and-not-asked-again.md`; adr_lint printed "13 ADR file(s) checked, 0 legacy", exit 0.
- DONE: roborev_gate.py evidence= line, CI green on the PR head, and the CI cost per PR measured or stated as not measured
  `clean on 218645da7; evidence=roborev:604`; all four PR checks pass on 218645da (unit tests 29s, version parity 47s); cost: no job or step added, last four runs of the existing workflow 35-45 s wall clock, billed minutes not measured.

### Per-criterion evidence

- AC-1: `test_the_recorded_quota_refusals_are_not_a_review` feeds the verbatim bodies of review:5499757433 and review:5499757731 (copied from `gh api .../pulls/627/reviews`, `.../628/reviews`) and asserts code 5, `answer=review:<id>`, no `evidence=`. Fails on the 0.21.0 reader (mutation: `git show HEAD:` original), passes now. Live: `copilot_review.py iamcxa/kc-claude-plugins 627` now exits 5.
- AC-2: `test_any_other_answer_without_a_heading_or_line_comment_is_not_a_review` (empty, English error, Chinese sentence) asserts code 5. A quota-sentence-only denylist mutation passes AC-1 and fails this test and the quote test.
- AC-3: the three named existing tests pass unchanged; new `test_a_heading_less_review_with_its_own_line_comment_is_an_answer` fails under a heading-only mutation. The changed existing test `test_the_answer_is_reported_the_same_whatever_copilot_found` lost its "Looks good" no-heading case (D1), now covered by the line-comment test and the exit 5 tests.
- AC-4: `test_a_refusal_does_not_erase_an_earlier_real_review_of_the_head` fails under a latest-review-only mutation; `test_a_refusal_answers_the_request_before_it_and_a_newer_request_waits` fails when refusals are excluded from the request-time comparison.
- AC-5: `test_a_copilot_refusal_is_not_run_not_a_reader_error_and_wakes_wait` asserts `("not-run", "-")` from a fake reader exiting 5 and `outcome("copilot", "requested", "not-run")`; fails when the mapping or the OUTCOMES word is removed (each mutated separately).
- AC-6: consistency check (/tmp/ac6.py, not committed) finds every `Exit N` of the docstring in the Read paragraph and fails with 5 missing when the exit 5 sentence is removed. Behaviour half: not verified; observable only at the next Copilot refusal. A limit, not a pass.
- AC-7: six paths, none under `extensions/codex/` or `kc-pr-flow/`.
- Other checks: comment_ratio.py 0 comment lines of 57 code lines, met; doc_impact.py lists 0 documents; number_guards.py PASS (no migrations-path).

### Summary

The reader treats an answer as a review only with a heading or its own line comment; anything else is exit 5 and quoted, pr_watch maps it to `not-run`, and EXTENSION.md tells FO to record `copilot not run:`, not count, wait or re-request, and name Copilot unread in the merge ask. No new probe was added; the `/copilot_internal/user` measurement is in Limits as a non-predictor. The PR is Draft and has no review requested, per instructions.

Notes for FO: my first `gh api` of the single-review path returned 404 because of a zsh word-splitting slip of mine, not a GitHub fact; reruns worked. The worktree started at e2524e93 behind origin/main and was fast-forwarded to 9e68eb87 before any edit.
