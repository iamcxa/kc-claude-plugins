---
title: A delivery PR's review rounds stop by rule, a small fix does not queue behind a long task, and comment ratio has a threshold
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: validation
gates:
    version: 1
    records:
        - id: gate:review-cadence:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:review-cadence-backlog-1
              briefing:
                id: briefing:review-cadence:backlog:attempt-1:revision-1
                digest: sha256:608d22d74a1f3b6b267bee3a16ae8a3ef907fbb3b465410173b7caa42e93050a
                room-ref: ./review-cadence/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:review-cadence:backlog:1
                briefing: briefing:review-cadence:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-30T07:22:01.817477Z"
                decision: approve
                reason: 'Captain 2026-09-30: 「請你關掉 523, 524，然後繼續 B」'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:review-cadence:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:review-cadence-ideation-1
              briefing:
                id: briefing:review-cadence:ideation:attempt-1:revision-1
                digest: sha256:986837622b1c9cb0d262d85b48f44fb29a72139d78295422d404ace99c1ab94b
                room-ref: ./review-cadence/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:review-cadence:ideation:1
                briefing: briefing:review-cadence:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-30T07:43:44.12037Z"
                decision: approve
                reason: 'Captain 2026-09-30: 「核准」 — with two amendments he approved: the package defaults comment-ratio-max to 5 (his standing rule: baseline 3%, target 5%), overridable by the adopter''s workflow README key or --max; the round rule (N = 2) applies to any external reviewer (Codex, RoboRev, others), not Codex only'
              application:
                target-stage: implementation
                state: consumed
        - id: gate:review-cadence:validation
          stage: validation
          attempts:
            - id: gate-attempt:review-cadence-validation-1
              briefing:
                id: briefing:review-cadence:validation:attempt-1:revision-1
                digest: sha256:b58e0a0e0778cd0da16384803badc57be77ce3799a87f0adfed827fcd01c4b5c
                room-ref: ./review-cadence/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:review-cadence:validation:1
                briefing: briefing:review-cadence:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-30T08:16:00.945753Z"
                decision: revise
                reason: 'Captain 2026-09-30: 「退回補」 — four repairs: AC/Finding/Task citation tests; unresolvable ref exits 2; ADR 0004 verbatim words and no unproven cause; item 5 maps a reviewer without P1 labels by its highest severity; constructed false-positive classes declined as a known limit'
            - id: gate-attempt:review-cadence-validation-2
              briefing:
                id: briefing:review-cadence:validation:attempt-2:revision-1
                digest: sha256:8197e25df3ca5cc58d67046aae94cbbb06fa6bb440fa28dfb0e9898986226da3
                room-ref: ./review-cadence/review/validation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:review-cadence:validation:2
                briefing: briefing:review-cadence:validation:attempt-2:revision-1
                by: agent:first-officer
                at: "2026-09-30T08:28:36.79654Z"
                decision: approve
                reason: Validation PASSED on e98bd8b2 plus the FO-authorized one-phrase ADR fix a8079edf (diff read by the FO); opening a Draft PR only; merge stays with the Captain
                conn:
                    quote: 'No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar'
                    source: ~/.claude/CLAUDE.md, Autonomous action boundaries
              application:
                target-stage: done
                state: pending
started: 2026-09-30T07:22:23Z
worktree: .worktrees/spacedock-ensign-review-cadence
---

Three review-cadence defects from qnow dogfooding (2026-09-28..29) that each cost extra full cycles or hours of waiting.

## Scope

Captain 2026-09-30, approving the FO's batching of the dev2 fixes: 「可以」 — batch B (review cadence) after batch A; 2026-09-30: 「等Ｃ做完…繼續 B」 — the package release waits for batch C. This task covers issues #521, #522 and #525.
Evidence (qnow): #1243 and #1245 each went through four Codex rounds with a P1 only in round one, and the Captain ruled the stop ad hoc ("最後一輪，之後沒有 P1 就合併"); a two-line P1 fix waited several hours in the implementation queue behind a 68-file task, and a two-minute recheck waited behind a long browser validation; candidates reached validation at 12.6%, 7.5% and 6.4% added-comment ratio against a 5% target, each needing a trim round, and a comment cited the task's own ideation numbering.
Captain amendments at the ideation gate, 2026-09-30 (「核准」): the package defaults the comment-ratio maximum to 5 percent (his standing rule: baseline 3%, target 5%), an adopter overrides it with `comment-ratio-max:` in its workflow README frontmatter and `--max` overrides both for one run; the round rule applies to any external reviewer of the delivery (Codex on the PR, RoboRev or another), not Codex only.
Non-goals (ideation 2026-09-30): no change to Spacedock (the outcome needs none); no mechanical enforcement of the round count (the FO counts and records it); no size-based lane (the lane keys on worktree ownership); no new severity vocabulary (the four-field Material test stays); no re-sync of any adopter's `docs/dev2/README.md` in this task (that is a per-adopter three-way merge, listed as a follow-up).

## Acceptance criteria

All evidence below is planned for implementation and validation unless it says "current".

**AC-1 — review rounds stop by rule.** `references/sd/workflow.md` `## Review-finding disposition` gains item 5: a finding assessed Material, or labelled P1 by the external reviewer (Codex on the PR, RoboRev or another), blocks in every round (a reviewer P1 is fixed, or waived by the Captain with the reason recorded); from the third round on, a finding that is neither never starts a repair cycle and the FO declines it as a follow-up in the committed gate summary and a `Follow-up:` line in the successor task's Scope. For an external reviewer that has no P1 label, its highest severity level counts as P1 (e.g. RoboRev). Rounds 1 and 2 keep today's behaviour.
Verified by: (a) `test_sd_dispatch.py` builds an implementation and a validation stage definition (what `dispatch show-stage-def` prints and the dispatch file tells the worker to fetch) from the package `workflow.md` in a disposable repository on both hosts and asserts it contains item 5's text, including the sentence that maps a reviewer without a P1 label to its highest severity; a second fixture with item 5 deleted must not print it, and deleting item 5 from the package `workflow.md` makes the assertion fail (run at implementation). (b) Current, reading only: the replay table in the Design shows rounds 3 and 4 of PR #1243 (3 and 5 findings, no P1) would have started no cycle. Limit: the FO applying the rule is prose, so no test proves an FO obeys it; qnow's next delivery PR is the only real observation.

**AC-2 — a repair does not queue behind another entity's worker.** `references/sd/workflow.md` `## Stages` states that `concurrency` limits only what `status --next` proposes, and that a feedback-reflow repair, the validation recheck of that repair, and an FO fix authorised under Review-finding disposition step 3 are dispatched at once in the entity's own worktree, after the existing overlap check against running worktrees.
Verified by: (a) Current, design time: in a disposable repository under `/tmp` with `implementation` at `concurrency: 1` and entity A holding its worktree there, Spacedock 0.27.2 `dispatch build --feedback-reflow` for entity B exited 0 and emitted a dispatch envelope (command in the Design). (b) `test_sd_dispatch.py` gains the same case against the package `workflow.md` (two entities each holding an `implementation` worktree at `concurrency: 1`, then a `--feedback-reflow` build for the second), asserting exit 0 and the feedback context in the dispatch file; the case fails only if a future Spacedock adds a slot check to the reflow path, which is the regression it exists to catch; it does not prove any FO applies the lane. (c) The `workflow.md` lane sentences asserted as text by the same test (a substring check on the source, not proof that an FO applies it).

**AC-3 — the comment ratio is enforced above a maximum that defaults to 5 percent.** `comment_ratio.py` gains `--max PCT` and `--workflow-dir DIR` (key `comment-ratio-max:` in the workflow README frontmatter). The maximum is `--max`, else the README key, else the package default of 5 percent. Exit 1 when the added-comment ratio is above it and at least 20 non-blank code lines were added; below 20 lines it prints that the ratio is not enforced and exits 0; exit 2 on an unreadable README, a `--max` or key value that is not a non-negative number, or a base or candidate ref git cannot diff (one line naming the ref, no traceback).
Verified by: `test_comment_ratio.py` (already run by `.github/workflows/kc-dev-flow-2-tests.yml`) adds cases: over the maximum exits 1; at the maximum exits 0; a 5-comment-of-5-line diff (the measured `dev-secrets-from-1password` case, 100%) exits 0 below the floor; with no flag and no key a 10% diff exits 1 at the package default of 5; a README key of 10 lets it pass and `--max 5` overrides that key; a missing README, a non-numeric value, a negative value, `--max nan` and an unresolvable ref (`comment_ratio.py nope main`: one stderr line naming `nope`, no traceback) exit 2. Mutations, each run and each failing the named case: flip `>` to `>=` fails the at-the-maximum case; drop the floor fails the 5-of-5 case; make `--max` ignored fails the override case. Replay, current: at the qnow base `3414d21a46e488c4cdf8cc04ef0e52dabd7403f8`, candidate `34523b7ca` measures 218/3404 = 6.4% (would exit 1 at the default 5) and `bd0deaf1a` 128/3314 = 3.9% (would exit 0 on the ratio); these are read numbers, not rerun at implementation.

**AC-4 — a comment cites an ADR or a greppable symbol, never task numbering or review provenance.** With or without a maximum, `comment_ratio.py` scans the added comment lines and exits 1 listing each `CITE <path>: <line>` that matches task-internal numbering (`Decision N`, `AC-N`, `Round N`, `Cycle N`, `Finding N`, `Task N`, `cycle-N`), review provenance (`Codex`, `review of`, `review follow-up`, `reviewer's`), a PR or issue number (`PR #N`, `#NN`) or a `file:line`; a line naming an ADR (`ADR NNNN`, `docs/adr/NNNN`) is exempt. The implementation and validation stage principles state the rule and that exit 1 is a trim (implementation) or a repair finding through feedback (validation).
Verified by: `test_comment_ratio.py` cases, one per class, plus the ADR exemption; the falsifier removes one class or alternative from the pattern, or the ADR exemption, and its case fails (run at implementation, one mutation each). Cases include one each for `Decision`, `AC`, `Round`, `Cycle`, `Finding` and `Task` numbering, so removing any of the six from the pattern fails its own case (run at implementation). Replay, current (a throwaway scan using the classes above, same base; the implementation's scanner replaces it): `34523b7ca` flags 34 of 218 added comments, every one a `Decision N`, `AC-N`, `cycle-N` or `Codex review of` citation (read by hand from the scan's output); `bd0deaf1a`, after the worker's own citation fix, still flags 3 (`Decision 9`, two `AC-1`), which the fix missed; over 150 older commits before the dev2 workflow (2478 added comments) it flags 25, of which one is a false positive (an ADR citation wrapped onto the next line) and the rest, read by hand, cite `AC-N`, `PR #N`, `finding N`, review provenance or a `file:line`. Limit: a pattern list finds the named classes only, and also flags text that only looks like a citation (a `#333` colour, `step #1`, a URL fragment, asyncio "Task 3", "a code review of the parser", "the Codex CLI"; 1 false positive in 38 hits on the last 150 commits of origin/main, read by validation), which the Captain declined as a known limit 2026-09-30 (「退回補」), documented in `adoption.md` and ADR 0004; other provenance wording ("as suggested in review") passes, so validation still reads every added comment.

**AC-5 — the rules reach the FO, the worker and the adopter.** Item 5 and the lane text live in `workflow.md` (the FO reads it; `## Review-finding disposition` is a `context-sections` entry of implementation and validation, so both workers receive it); the two principles files carry the exit-code handling; `references/sd/adoption.md` names `comment-ratio-max`, the package default of 5, and says an adopter overrides it there and re-syncs its README from `workflow.md` to receive the rest.
Verified by: `lint-skills.py` and `test_lint_skills.py` pass; `test_sd_dispatch.py` (AC-1(a)) proves the inlining; `doc_impact.py <base> <candidate>` lists `README.md` of the package and each listed document carries `updated` or `unaffected: <reason>`.

**AC-6 — the ruling is an ADR.** One ADR for the Captain's rulings on rounds and the comment rule and his two amendments (Decisions: his words verbatim, in order, and options considered; the 1h40 wait's cause stated as consistent with the state history, not proven), `docs/adr/0004-review-rounds-stop-by-rule-and-comments-are-counted.md`, number reserved under `## Number guards`.
Verified by: `python3 <package>/scripts/adr_lint.py docs/adr --require <number>` exits 0; `number_guards.py check` exits 0.

## Design (ideation, 2026-09-30)

### PRFAQ

**Proposition.** A delivery PR stops being reviewed by rule, not by the Captain's ad hoc word: a Material finding or a reviewer P1 always blocks, and from the third round on everything else becomes a recorded follow-up. A small repair starts at once instead of waiting for a long task in the same stage. A candidate's comments are counted against a maximum (5 percent by default) and cite only ADRs or symbols, and both failures exit non-zero before a validator has to find them.

**FAQ**

- *Why is the round count 2, and what does it buy?* Judgment, not measurement. qnow PR #1243 took four Codex rounds (4, 1, 3, 5 findings; the only P1 in round 1). With a cap of 2, rounds 3 and 4 (8 findings, no P1; assuming none is assessed Material, which was not read) would have started no cycle: two full implement, validate, push and CI cycles fewer. 2 also matches Spacedock's own cycle-3 escalation to the human. The Captain sets the number.
- *Is this Spacedock's cycle-3 escalation?* No, a second counter. `feedback-rejection-flow` counts rejection cycles of a feedback stage and, on cycle 3, escalates to the human; the new rule counts external-review rounds on a delivery PR, which may or may not have been routed through that flow. The escalation stays as the backstop when Material findings keep coming; the new rule supplies the recommended answer at it.
- *Who decides a finding becomes a follow-up?* The FO, under the authority Review-finding disposition step 2 already gives it for evidenced Deferred risk or Polish; the Captain sees the list and each home at the terminal gate summary. A reviewer P1 stays with the Captain because step 4 puts risk acceptance with the Captain; his words on #1246 were "a Codex P1 blocks merge until fixed and re-validated".
- *Where does a follow-up live?* In the Scope of the successor task, as qnow already did (`staff-multi-branch` carries the P2s "from Codex's last review of PR #1245"). Default successor: the open task whose Scope edits the finding's file; else a new backlog task from `spacedock new`. No new tracker.
- *What does Spacedock already do about a waiting repair, and is anything missing?* Nothing blocks it. `concurrency` is read only in `dispatchAnalysis` (`internal/status/format.go`, v0.27.2), which feeds `status --next`; that function skips an entity holding a worktree before it looks at concurrency, and `dispatch build` never reads it (only a comment in `build.go` says the word). The FO references carry no one-worker-per-stage rule; the only serial rule is bare mode, where `«async-dispatch»` is absent. So the #1246 wait (task `dev-secrets-from-1password`: validation approve recorded 11:57, implementation cycle-3 report committed 13:39, about 1h40 rather than the issue's "several hours"; the sibling `owner-vehicle-on-booking` held implementation from its 11:49 dispatch to its 13:24 report) looks like the FO reading `concurrency: 1` as a hard cap. That is consistent with the state history, not proven: the fix's dispatch time is not recorded and the FO transcript was not read. The package can state the rule; Spacedock needs no change.
- *Why not the issue's "bounded diff" or "size-aware limit"?* The size of a repair is not known before it is dispatched; ownership of a worktree is. The lane is keyed on ownership plus an authorised assignment, and a repair that grows past what its assignment names returns to the FO as a scope change (existing rule).
- *What does the lane cost?* More workers at once, and two candidates can touch the same files or a shared database branch. The existing dispatch step "check for obvious conflicts if multiple worktree stages would touch overlapping files" applies, migration numbers are per-task through `number_guards.py`, and an `Applied at:` collision on a shared non-production database branch is not detected by anything (documented limit of `## Number guards`).
- *Why a threshold with a floor?* `dev-secrets-from-1password` validated at 5 of 5 comment lines (100%), correctly: its whole diff was doc-comment replacement. A bare maximum would fail it. The floor of 20 added code lines is a choice, not a measurement; the only measured case it must clear is 5.
- *Where does the ratio's value come from?* Captain amendment 2026-09-30: the package defaults to 5 percent (his standing rule: baseline 3.0%, 455 of 15145 lines added on `kc-claude-plugins` main, 2026-08-11 to 2026-08-25; target 5%); an adopter overrides it with `comment-ratio-max:` in its workflow README frontmatter, and `--max` overrides both for one run. Before the amendment the design shipped no default because no repository file states 5%; the Captain's ruling is now the source.

### Flow

```mermaid
sequenceDiagram
    participant X as External reviewer (Codex, RoboRev or another)
    participant FO as First officer
    participant W as Worker (repair lane)
    participant V as Validation worker
    participant C as Captain
    X->>FO: verdict on the PR head (round N)
    alt any Material finding or reviewer P1
        FO->>W: repair assignment, dispatched at once in the entity's own worktree
        W->>V: candidate (comment_ratio.py exit 0 required)
        V->>FO: recheck verdict, also dispatched at once
        FO->>X: push; next round
        Note over FO,C: a reviewer P1 the FO believes wrong goes to the Captain to waive with a reason
    else only other findings and N is 1 or 2
        FO->>W: repair what triage keeps, same lane (today's behaviour)
    else only other findings and N is 3 or more
        FO->>FO: decline in the committed gate summary
        FO->>FO: Follow-up line in the successor task's Scope
        FO->>C: terminal gate lists each follow-up and its home
    end
    Note over FO,C: a further repair cycle for Material findings past Spacedock's cycle 3 escalates to the Captain
```

### Chain check (what exists, where)

| Layer | Found | Where |
| --- | --- | --- |
| spacedock 0.27.2 | `concurrency` only feeds `status --next`; `--feedback-reflow` is not slot-checked; cycle-3 escalation for feedback-stage rejections; reuse of the `feedback-to` worker when addressable | `internal/status/format.go` `dispatchAnalysis`, `skills/feedback-rejection-flow/SKILL.md`, `skills/first-officer/references/fo-dispatch-core.md` at tag `v0.27.2` (`~/conductor/repos/spacedock-v1`); installed skills cache is 0.27.0, binary 0.27.2 |
| kc-dev-flow-2 | `comment_ratio.py` prints and always exits 0 (62 lines); stage principles run it and report the output; Review-finding disposition (four-field Material test, FO decline of Deferred risk or Polish, risk acceptance to the Captain); no round rule, no threshold, no citation rule | `kc-dev-flow-2/scripts/comment_ratio.py`, `skills/*/principles.md`, `references/sd/workflow.md` |
| kc-dev-flow | one RoboRev observation at implementation exit (not a stop rule); "change the work, not the wording" | `references/roborev-implementation-exit.md`, `references/kernel.md` |
| kc-pr-flow | self-review capped at 3 rounds, then proceed (own scope, not an external reviewer) | `kc-pr-flow/skills/kc-pr-create/SKILL.md` Step 10 |
| carlove | "Converge by naming residuals"; a P1 is fixed or waived with a recorded reason | `docs/dev/README.md` `validation` stage |
| subspace-relay | "fixing every finding a reviewer raises moves the scope decision to the reviewer"; `concurrency: 2` | `docs/dev/README.md` |
| qnow | `concurrency: 1` on implementation and validation; deferred P2s carried into a successor's Scope; no comment-ratio target written anywhere | `docs/dev2/README.md`, `.spacedock-state/staff-multi-branch.md` |

Reuse: every part reuses an existing mechanism (disposition vocabulary, FO decline authority, successor Scope, `number_guards.py`'s README-frontmatter reading, the existing CI test file). Nothing is new but the round rule, the lane sentence and one script's exit codes.

### Round replay (reading, not running)

| PR | Rounds (findings) | P1 | Under N = 2 |
| --- | --- | --- | --- |
| #1243 `shop-onboarding-script` | 4, 1, 3, 5 | round 1 only (issue #521) | rounds 3 and 4 start no cycle unless a finding is Material; their P2s become follow-ups (the ones actually deferred went into `operator-onboarding-api` Scope) |
| #1245 `operator-onboarding-api` | four rounds (issue #521); validation cycles 1 to 4, implementation cycles 1 to 3 | not stated in the issue | not replayed: per-round severities were not read |
| #1246 `dev-secrets-from-1password` | one P1 (no-args guard, two lines); repaired in implementation cycle 3, rechecked in validation cycle 2 | the whole PR | blocks; repaired and rechecked in the lane, not queued |

### Spike (lane), reproducible

Disposable repository `/tmp/rc-lane` (removed at the end of this stage): `wf/README.md` with `implementation` at `concurrency: 1`, entities `a` and `b` both at `implementation` with a worktree; `spacedock status --workflow-dir wf --next` listed nothing; `spacedock dispatch build --workflow-dir /tmp/rc-lane/wf --entity-path /tmp/rc-lane/wf/b.md --stage implementation --checklist-file chk.txt --feedback-context-file fb.txt --feedback-reflow` exited 0 with a dispatch envelope. This shows Spacedock does not refuse the dispatch; it does not show whether a reflowing entity's status returns to `implementation` and so counts toward that stage for `--next` (not verified, and irrelevant to the lane).

### Files the implementation touches

`kc-dev-flow-2/scripts/comment_ratio.py`, `test_comment_ratio.py`, `test_sd_dispatch.py`; `references/sd/workflow.md` (`## Stages` lane sentence, disposition item 5, one line each in `### implementation` and `### validation`); `skills/implementation/principles.md`, `skills/validation/principles.md`; `references/sd/adoption.md`; `docs/adr/NNNN-*.md`. CI: no new job; the existing `kc-dev-flow-2-tests.yml` runs the two test files (added seconds, not measured). Commit and PR title `feat(kc-dev-flow-2): ...`; no version edits.

### Needs the Captain

Resolved at the ideation gate, 2026-09-30 (「核准」): the stopping rule as written with N = 2, applying to any external reviewer; the comment-ratio value 5 percent as the package default, overridable by README key and `--max`. Not taken: an upstream Spacedock issue for a mechanical repair lane (the package rule is enough; filing stays Kent's decision).

### Captain-run acceptance script (run at implementation, about 3 minutes)

Run from a checkout of the candidate branch, with `$PKG` set to its `kc-dev-flow-2` directory. Steps 1 to 6 are one shell session; the whole script was run at implementation and printed the output named in each step.

1. `T=$(mktemp -d) && cd "$T" && git init -q -b main && git -c user.name=t -c user.email=t@e.invalid commit -q --allow-empty -m base`.
2. Write `a.ts` as one line `// retry is idempotent` then 40 lines `const a1 = 1;` .. `const a40 = 40;` (`{ echo '// retry is idempotent'; for i in $(seq 40); do echo "const a$i = $i;"; done; } > a.ts`), `git add a.ts`, commit. Run `python3 $PKG/scripts/comment_ratio.py main~1 main --repo "$T"`: expect `code lines 41, comment lines 1, 2.4%`, `maximum 5% (package default) met`, exit 0 (`echo $?`).
3. Write `b.ts` as 7 lines `// note N`, the line `// Decision 3: keep this` and 40 code lines, commit, run the tool on `main~1 main`: expect `code lines 48, comment lines 8, 16.7%`, `FAIL: 16.7% is above the maximum 5% (package default)`, `CITE b.ts: // Decision 3: keep this`, exit 1.
4. `mkdir wf && printf -- '---\ncomment-ratio-max: 20\n---\n' > wf/README.md`, run step 3's command with `--workflow-dir "$T/wf"`: expect `maximum 20% (comment-ratio-max in .../wf/README.md) met`, no `FAIL` line, the `CITE` line still there, exit 1.
5. Commit `c.ts` with 2 lines `// plain note N` and 2 code lines and run the tool on that one commit (`main~1 main`): expect `code lines 4, comment lines 2, 50.0%` and `not enforced: 4 code lines added, fewer than 20`, exit 0.
6. `python3 $PKG/scripts/comment_ratio.py nope main --repo "$T"; echo $?`: expect one line `error: cannot diff nope...main: ...` and `2`, no traceback.
7. `python3 $PKG/scripts/test_comment_ratio.py`: expect `OK`.
Does not cover: an FO applying the round rule or the lane (prose, no test can prove it); Codex or RoboRev themselves; any adopter's README; the dispatch inlining (`test_sd_dispatch.py`, which CI runs).


## FO alignment

Needed at ideation: the stopping rule for review rounds on a delivery PR (what always blocks, what becomes a follow-up after how many rounds, and where the follow-up is recorded); how a small rework avoids waiting behind a long task in the same stage, and whether that needs Spacedock or only the package; the comment-ratio threshold, where it is enforced, and the rule for what a comment may cite.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none

## Number guards

ADR: 0004

## Stage Report: ideation

- DONE: Design, in the task file, the kc-dev-flow-2 package change for issues #521, #522 and #525 (stopping rule, small-rework lane, comment-ratio threshold and citation rule)
  `## Design (ideation, 2026-09-30)`: PRFAQ, sequence diagram, replay table and the "Needs the Captain" list; rule 1 is disposition item 5 (Material or reviewer P1 always blocks, N = 2, FO declines the rest as a Follow-up in the successor task's Scope); rule 2 is a `## Stages` lane sentence; rule 3 is `--max`/`comment-ratio-max:`, a 20-line floor and a citation scan in `comment_ratio.py`.
- DONE: Check the chain first: spacedock, kc-dev-flow-2, kc-dev-flow and adopters (qnow, subspace-relay, carlove) for an existing rule
  Design "Chain check" table with locations; Spacedock `concurrency` is read only by `status --next` (`dispatchAnalysis`, tag v0.27.2) and a reflow dispatch built with exit 0 while another entity held the only slot (disposable repo, removed); no round rule or ratio threshold exists in kc-dev-flow-2, kc-dev-flow or qnow; carlove and relay carry the prose precedents.
- DONE: ACs with evidence plans; whether an ADR is needed; what needs the Captain; the Captain-run minimal acceptance script
  Six ACs with `Verified by:`; one ADR, a design-time `number_guards.py reserve` probe printed `ADR: 0004` against origin/main 348c6876 and wrote nothing; three Captain items and a draft five-step script in the Design.
- DONE: AC-1 review rounds stop by rule
  Current: replay by reading only (PR #1243: 4, 1, 3, 5 findings, P1 in round 1); not yet verified: the dispatch-inlining test and the FO obeying the rule.
- DONE: AC-2 a repair does not queue behind another entity's worker
  Current: `spacedock dispatch build --feedback-reflow` exit 0 with entity A holding the only `implementation` slot (Spacedock 0.27.2, disposable repo); not yet verified: the package test and text.
- DONE: AC-3 comment ratio enforced above a declared maximum
  Current: `comment_ratio.py` today only prints (62 lines, always exit 0); qnow replay measured 6.4% at `34523b7ca` and 3.9% at `bd0deaf1a` against base `3414d21a4`; not yet verified: the new exit codes and tests.
- DONE: AC-4 comments cite an ADR or a symbol, never task numbering or review provenance
  Current: a throwaway scan flagged 34 of 218 comments at `34523b7ca` (all true by hand), 3 of 128 at `bd0deaf1a`, 25 of 2478 over 150 older commits (1 false positive); not yet verified: the scanner and its tests.
- DONE: AC-5 the rules reach the FO, the worker and the adopter
  Not yet verified (implementation): reach is designed through `workflow.md` and `context-sections: Review-finding disposition`; `design_surfaces.py check` on this task printed "design surfaces presentable".
- DONE: AC-6 the ruling is an ADR
  Not yet verified (implementation): the FO reserves and records the number under `## Number guards` before dispatch.

### Summary

The three fixes are a package-only change: a round rule in Review-finding disposition, a lane sentence in `workflow.md` (Spacedock 0.27.2 never slot-checks a repair, so it needs no change), and `comment_ratio.py` gaining a maximum, a floor and a citation scan with exit codes. Two facts limit it: the 5% ratio has no written source anywhere (only the issue and a qnow stage report), and the FO transcript for the #1246 wait was not read, so the lane's cause is consistent with the state history but not proven. The Captain decides the round rule with N = 2 and the ratio value; the adopters' READMEs (this repo's and qnow's already lack the newer `context-sections`) need a separate sync for the rules to reach them.

## Stage Report: implementation

- DONE: Implement review-cadence's approved design (Captain 2026-09-30 「核准」) with his two amendments: (1) the package defaults the added-comment maximum to 5 percent (his standing rule: baseline 3%, target 5%); an adopter overrides it with `comment-ratio-max:` in its workflow README frontmatter, and `--max` overrides both for one run; (2) the round rule (N = 2; Material or reviewer P1 always blocks; from round 3 the rest become follow-ups) applies to any external reviewer of the delivery (Codex on the PR, RoboRev, or another), not Codex only. Update the design text, ACs and acceptance script to match both amendments.
  Candidate 408e8bf84c8f (branch spacedock-ensign/review-cadence, one commit on 348c6876): `comment_ratio.py` (default 5, README key, `--max`, floor 20, CITE scan), `workflow.md` (lane paragraph, item 5, two pointer lines), both principles files, `adoption.md`; task Scope, AC-1..AC-3, AC-5, AC-6, FAQ, flow, Needs-the-Captain and the acceptance script rewritten for both amendments.
- DONE: Every AC with the evidence its "Verified by" names that implementation can produce, including the mutations; the replay numbers stay as current evidence, not rerun claims.
  AC-1(a), AC-2(b), AC-3, AC-4 by tests, all CI list entries green at the candidate; AC-1(b), AC-2(a) and the replay numbers stay read-only current evidence. Lane test proves exit 0 only; nothing proves an FO obeys the round rule or lane. `test_comment_ratio.py` (13 tests): mutations run one at a time, each failed only the named case: `>` to `>=` (at-the-maximum, README override); floor dropped (5-of-5 and two more); `--max` ignored (override); each CITE alternative removed (its case); ADR exemption removed (ADR case); PR/issue class removed (both #N cases). `test_sd_dispatch.py`: stage definitions for both stages on both hosts carry item 5 (four phrases); a fixture without item 5 does not; deleting item 5 from `workflow.md` failed the assertion (run). Reflow build exits 0 while another entity holds the `implementation` slot.
- DONE: ADR 0004 in docs/adr (the task's `## Number guards` holds `ADR: 0004`); the decider's words are the Captain's 「核准」 at the ideation gate on 2026-09-30 plus the two amendments above.
  `docs/adr/0004-review-rounds-stop-by-rule-and-comments-are-counted.md`; `adr_lint.py docs/adr --require 0004` exit 0 (4 files); `number_guards.py check` exit 0 at head 408e8bf84c8f, base 348c6876f8bd.
- DONE: Follow this repo's CLAUDE.md: Conventional Commits scoped `feat(kc-dev-flow-2): …`, no version edits, stage files explicitly; the candidate's own `comment_ratio.py` exits 0 at the new default on this diff; `doc_impact.py` reported; exact candidate SHA; the Captain-run minimal acceptance script.
  Commit `feat(kc-dev-flow-2): stop review rounds by rule and enforce the added-comment maximum`, 8 files named, no version files; `comment_ratio.py 348c6876 HEAD`: code lines 179, comment lines 0, 0.0%, "maximum 5% (package default) met", exit 0. `doc_impact.py`: `kc-dev-flow-2/README.md` unaffected: it names only the two test commands, which run unchanged; `references/sd/adoption.md` updated (new section). Acceptance script in the task's Design, run once end to end (exits 0, 1, 1, 0, OK). CI list at 408e8bf84c8f: lint-skills, test_lint_skills, test_design_surfaces, test_adr_doc_checks, test_poc_readme, test_comment_ratio, test_number_guards, test_learning and test_sd_dispatch (Spacedock 0.27.2) all exit 0; the lane sentence's "only" cites Spacedock 0.27.2 and `<package>/scripts/test_sd_dispatch.py`. #535 (d0f91b48) is already an ancestor of the branch and `origin/main` is 348c6876 (fetched), so there was nothing to merge.

### Summary

The package now stops external-review rounds by rule (item 5 in Review-finding disposition), states the repair lane in Stages, and `comment_ratio.py` exits 1 above a 5 percent default maximum (README key or `--max` override, 20-line floor) and on a comment citing task numbering, review provenance, a PR or issue number or a `file:line`; ADR 0004 records the ruling with the Captain's two amendments. Limits: the round rule and the lane are prose an FO applies and only an adopter's next delivery PR observes them; the citation scan finds its named classes only (`#333` in a comment is a false positive); an external reviewer without a P1 label needs the FO to map its blocking severity, which the Captain has not ruled on; the FO's note that origin/main is d0f91b48 is stale (it is 348c6876, a descendant).

## Stage Report: validation
- DONE: Reproduce the CI workflow's suite list on a `git archive` copy of 408e8bf84c8f
  lint-skills, test_lint_skills, test_design_surfaces, test_adr_doc_checks, test_poc_readme, test_comment_ratio (13), test_number_guards, test_learning and test_sd_dispatch (Spacedock 0.27.2, plugin root = v0.27.2 archive) each exit 0.
- DONE: Reproduce each `test_comment_ratio.py` mutation the report names, one at a time
  `>` to `>=` fails at-the-maximum and README-override; floor dropped fails 5-of-5 and two more; `--max` ignored fails at-the-maximum and README-override; ADR exemption removed fails both ADR cases; Decision, cycle, Round, Codex, review of, review follow-up, reviewer's, `#N` and `file:line` each fail their own case; floor 20 to 5, default 5 to 10 and README key ignored also fail.
- FAILED: AC-4 "removes one class or alternative ... its case fails (one mutation each)", and the implementation report's "each CITE alternative removed (its case)"
  Removing `AC`, `Finding` or `Task` from the task-numbering pattern leaves `test_comment_ratio.py` green (run, exit 0 each); no case names them, and `AC-N` is the class the qnow replay's 3 misses belong to. Not Material by the four fields (a regression-guard gap, no current harm); the repair is three cases, or the FO declines it as Polish.
- DONE: Reproduce the item-5 falsifier in test_sd_dispatch.py, and the reflow-while-slot-held case
  Deleting item 5 from `workflow.md` fails at "A round is one verdict..." (claude, implementation); deleting the lane phrase fails the LANE_RULE assert; a shim `spacedock` refusing `--feedback-reflow` fails the lane build (exit 1), so the case does catch a future slot check; the clean run builds the reflow with exit 0 while the other entity holds `implementation`.
- DONE: Run `comment_ratio.py` on the qnow replay with the default maximum
  Base 3414d21a4: `34523b7ca` 218/3404 = 6.4%, exit 1, FAIL plus 34 CITE lines (design: 6.4%, 34); `bd0deaf1a` 128/3314 = 3.9%, ratio met but exit 1 on 3 CITE lines (`Decision 9`, two `AC-1`; design: 3.9%, 3). The design says "would exit 0 on the ratio"; the exit code of the whole run is 1.
- DONE: Judge the citation scan's false-positive rate on this repository's history
  Last 150 commits of origin/main (348c6876, combined diff): 38 hits of 495 added comments (hit rate 7.7%); false positives 1 of 38, the class "markdown fixture text inside a Python string, a line starting `#`" (`## Stage Report: implementation (cycle 2)`, poc-close-guard.test.py); the other 37 name AC/finding/cycle numbering or a PR number, read by hand. Constructed and run through `cited()`, these also flag: `#333` colour, `step #1` ordinal, URL fragment `docs#2`, "Task 3" of asyncio, "a code review of the parser", "the Codex CLI". Last 340 commits: 104 hits of 2037 comments, many issue-number and `file:line` citations in e2e-pipeline; the false-positive count there was not read.
- DONE: Read ADR 0004 (adr_lint), workflow.md item 5 and lane paragraph, both principles files, adoption.md, every added comment line, `doc_impact.py`
  `adr_lint.py docs/adr --require 0004` exit 0; `number_guards.py check --base 348c6876 --head 408e8bf8` exit 0; `doc_impact.py`: README `review` (names only the two unchanged test commands, so unaffected holds), adoption.md `updated`; `comment_ratio.py 348c6876 408e8bf8` 179 code lines, 0 comment lines, exit 0; the diff adds no `#` or `//` comment, only a 5-line module docstring in comment_ratio.py.
- DONE: Note the ADR 0004 and script polish findings for FO disposition (Polish, none Material)
  ADR Context says the P1 repair "waited about 1h40 behind another task's worker" while the design says the cause is "consistent with the state history, not proven", and the amendment "Words" are the FO's paraphrase of the gate reason (labelled "Recorded from the gate resolution"), not the Captain's verbatim words; `comment_ratio.py` with an unresolvable ref prints a CalledProcessError traceback and exits 1, the same code as a trim, so a validator reading exit 1 as a repair finding would misroute it (run: `comment_ratio.py nope main`).
- DONE: Run the Captain acceptance script as written
  Steps 2 to 5 printed the named output and exits 0, 1, 1, 0; step 6 `test_comment_ratio.py` OK; run in a `mktemp -d` repository against the archive copy.
- DONE: State, as a finding for the FO, how the round rule treats an external reviewer with no P1 label as shipped
  Item 5 blocks a finding only if the FO assesses it Material or the reviewer labels it P1 and names no mapping from another reviewer's severity, so a RoboRev finding (repo `.roborev.toml` sets `review_min_severity = "high"`, no P1 vocabulary) that the FO does not assess Material starts no repair cycle from round 3 and becomes a follow-up; rounds 1 and 2 follow steps 1 to 4. ADR 0004 Consequences says the FO "needs to map its blocking severity", which `workflow.md` (the FO's text) does not say.
- DONE: Confirm the code worktree is unchanged
  `git status --short` in the code worktree is empty; spikes and mutation copies only under /tmp.

### Summary

Recommendation: PASSED with one FAILED evidence item. Suites, item-5 and lane falsifiers, the qnow replay (numbers match the design), the acceptance script and ADR checks reproduce; AC-4's "one mutation each" is not met for the `AC`, `Finding` and `Task` alternatives, which no test guards, and the implementation report's "each CITE alternative removed (its case)" is therefore false for those three. The FO dispositions that gap (repair with three cases, or decline as Polish); the RoboRev-severity gap is open for the Captain, unruled here.

## Stage Report: implementation (cycle 2)
- DONE: Apply the four Captain-authorized repairs (2026-09-30 「退回補」) on top of 408e8bf84c8f in the same worktree, keeping everything already shipped; update the task's ACs, design text and acceptance script where they change.
  Candidate e98bd8b2f8e2354ce75f3bc739b9a657416705b7 (branch spacedock-ensign/review-cadence, one commit on 408e8bf84c8f, 6 files); AC-1, AC-3, AC-4, AC-6 and the acceptance script (new step 6, tests now step 7) updated in this task file.
- DONE: Repair 1, the three new citation cases and the removal of each alternative failing its own case.
  `test_comment_ratio.py` adds Round, AC, Finding and Task cases (14 tests); dropping AC, Finding, Task, Round or Decision from the pattern each fails only its named subtest, where before AC, Finding and Task left the suite green.
- DONE: Repair 2, an unresolvable ref exits 2 with one line and no traceback.
  `comment_ratio.py nope main` prints `error: cannot diff nope...main: fatal: bad revision 'nope...main'`, exit 2; the new test asserts exit 2, one stderr line, the ref named, no Traceback, and fails when the git-failure check is disabled (run).
- DONE: Repair 3, ADR 0004 quotes the Captain verbatim and states no unproven cause.
  `adr_lint.py docs/adr --require 0004` exit 0; Words lists his five quotes in order (three questions, 「核准」, 「退回補」); Context says the 1h40 wait is consistent with `concurrency: 1` read as a cap, cause not proven.
- DONE: Repair 4, item 5 maps a reviewer without a P1 label to its highest severity; ADR and test match.
  `workflow.md` item 5 adds that sentence; ADR Consequences cites it; `test_sd_dispatch.py` ROUND_RULE asserts it in both stages on both hosts, and removing the sentence from `workflow.md` fails the assertion (run, AssertionError on that phrase).
- DONE: State the declined false-positive classes as a known limit where the rule is documented.
  `references/sd/adoption.md` and ADR Consequences name the six constructed classes and the measured 1 false positive in 38 hits on the last 150 commits of origin/main.
- DONE: Rerun the CI suite list; doc_impact.py and comment_ratio.py from 348c6876 to the new head.
  lint-skills, test_lint_skills, test_design_surfaces, test_adr_doc_checks, test_poc_readme, test_comment_ratio, test_number_guards, test_learning, test_sd_dispatch (Spacedock 0.27.2, root = v0.27.2 archive) all exit 0; `doc_impact.py` exit 0 (README `review` unaffected: only test commands named; adoption.md `updated`); `comment_ratio.py 348c6876 HEAD`: 200 code lines, 0 comment lines, exit 0; acceptance script steps 2-6 print the named output with exits 0, 1, 1, 0, 2.

### Summary

The four repairs are in one commit on top of 408e8bf84c8f: each task-numbering alternative has its own case, an undiffable ref exits 2 with one line, ADR 0004 carries the Captain's words verbatim and no unproven cause, and item 5 counts a reviewer's highest severity as P1 when it has no P1 label. The false-positive classes are stated as a known limit in adoption.md and the ADR. Limit unchanged: the round rule and the lane are prose an FO applies.

## Stage Report: validation (cycle 2)
- DONE: Reproduce the CI workflow's suite list on a `git archive` copy of e98bd8b2f8e2 (one commit on 408e8bf84c8f)
  lint-skills, test_lint_skills, test_design_surfaces, test_adr_doc_checks, test_poc_readme, test_comment_ratio (14 tests), test_number_guards, test_learning and test_sd_dispatch (plugin root = v0.27.2 archive, the CI pin 4d158a48) each exit 0.
- DONE: Remove each of AC, Finding, Task, Round and Decision from the task-numbering pattern; each fails its own case
  Removing AC, Finding, Task fails only subtest `task numbering AC`/`Finding`/`Task`; Round fails `task numbering Round` plus the with-or-without-maximum test; Decision fails `task numbering`; Cycle (extra) fails `task numbering cycle`; before the repair AC, Finding and Task left the suite green.
- DONE: `comment_ratio.py nope main` exits 2 with one line and no traceback, and the test fails when the check is disabled
  With `--repo` a real repository: `error: cannot diff nope...main: fatal: bad revision 'nope...main'`, exit 2, no Traceback; replacing `if run.returncode:` by `if False:` fails `test_an_unresolvable_ref_exits_2_with_one_line_naming_it` (`0 != 2`).
- DONE: Remove the item-5 highest-severity sentence from workflow.md; test_sd_dispatch.py fails
  Run on a mutated copy: exit 1, `AssertionError: ('claude', 'implementation', 'For an external reviewer that has no P1 label, its highest severity level counts as P1 (e.g. RoboRev)')`; the unmutated copy exits 0.
- DONE: Read ADR 0004 with adr_lint; Words match the Captain's five quotes verbatim and in order; Context states no unproven cause
  `adr_lint.py docs/adr --require 0004` exit 0; a script checked each of the five quoted strings from the feedback context is a substring of the ADR, in that order; Context says the state history is consistent with `concurrency: 1` read as a cap and the cause is not proven.
- DONE: Read the known-limit text in adoption.md and every added comment line
  adoption.md `## Comment ratio and review rounds` names the six constructed classes and 1 false positive in 38 hits (the cycle 1 measurement, not re-run); the range diff adds no `#`, `//` or block comment in code (grep over `*.py`), only the module docstring line in comment_ratio.py.
- DONE: Run the candidate's own `comment_ratio.py` from 348c6876 to the candidate
  `code lines 200, comment lines 0, 0.0%`, `maximum 5% (package default) met`, exit 0; `number_guards.py check --base 348c6876 --head e98bd8b2f8e2` exit 0; `doc_impact.py 408e8bf8 e98bd8b2` lists README (`review`, test commands only) and adoption.md (`updated`).
- DONE: Run the Captain acceptance script as written
  Steps 2 to 7 in a `mktemp -d` repository against the archive copy print the named output with exits 0, 1, 1, 0, 2 and `OK` (14 tests); step 6 prints one line `error: cannot diff nope...main: fatal: bad revision 'nope...main'`.
- DONE: Note findings for FO disposition (Polish, none Material) and unverified obligations
  (1) ADR Context says the P1 repair "waited about 1h40 for its implementation dispatch", but the design's 1h40 is validation-approve 11:57 to cycle-3 report 13:39 and the dispatch time is not recorded; (2) outside a git repository the exit-2 line ends in git's usage text (`--output <file> ...`), naming the refs but not the cause; (3) item 5 says a reviewer's "highest severity level" counts as P1, and `roborev review --help` lists critical, high, medium, low, so for RoboRev it reads as critical while `.roborev.toml` `review_min_severity = "high"` — as the Captain worded it, not a defect; unverified: an FO applying the round rule or the lane, RoboRev itself, any adopter README, the 1 in 38 rate (not re-run).
- DONE: Confirm the code worktree is unchanged
  `git status --short` in the code worktree is empty, HEAD is e98bd8b2f8e2354ce75f3bc739b9a657416705b7; spikes and mutation copies only under /tmp (rc-val, rc-val-sd, rc-mut).

### Summary

Recommendation: PASSED. All four Captain-authorized repairs reproduce: each task-numbering alternative fails its own case, an unresolvable ref exits 2 with one line and a test that fails when the check is off, ADR 0004 carries the Captain's five quotes verbatim with no unproven cause, and the item-5 sentence is asserted by test_sd_dispatch.py. Cycle 1's other results are untouched by this diff except where re-run above. Three Polish observations and the unverified obligations are listed for FO disposition; none is Material.

### Polish fix

FO-authorized (validation cycle 2 finding 1, step 3): ADR 0004 Context now says the P1 repair "took about 1h40 from the validation approval to its report (dispatch time not recorded)"; nothing else changed. New candidate a8079edf89052650be4f6ad5864205dd9a0c81fa (one file); `adr_lint.py docs/adr --require 0004` and `test_adr_doc_checks.py` exit 0.
