---
title: A delivery PR's review rounds stop by rule, a small fix does not queue behind a long task, and comment ratio has a threshold
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: implementation
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
started: 2026-09-30T07:22:23Z
worktree: .worktrees/spacedock-ensign-review-cadence
---

Three review-cadence defects from qnow dogfooding (2026-09-28..29) that each cost extra full cycles or hours of waiting.

## Scope

Captain 2026-09-30, approving the FO's batching of the dev2 fixes: 「可以」 — batch B (review cadence) after batch A; 2026-09-30: 「等Ｃ做完…繼續 B」 — the package release waits for batch C. This task covers issues #521, #522 and #525.
Evidence (qnow): #1243 and #1245 each went through four Codex rounds with a P1 only in round one, and the Captain ruled the stop ad hoc ("最後一輪，之後沒有 P1 就合併"); a two-line P1 fix waited several hours in the implementation queue behind a 68-file task, and a two-minute recheck waited behind a long browser validation; candidates reached validation at 12.6%, 7.5% and 6.4% added-comment ratio against a 5% target, each needing a trim round, and a comment cited the task's own ideation numbering.
Non-goals (ideation 2026-09-30): no change to Spacedock (the outcome needs none); no mechanical enforcement of the round count (the FO counts and records it); no package default for the comment-ratio value (each adopter declares its own); no new severity vocabulary (the four-field Material test stays); no re-sync of any adopter's `docs/dev2/README.md` in this task (that is a per-adopter three-way merge, listed as a follow-up).

## Acceptance criteria

All evidence below is planned for implementation and validation unless it says "current".

**AC-1 — review rounds stop by rule.** `references/sd/workflow.md` `## Review-finding disposition` gains item 5: a finding assessed Material, or labelled P1 by the external reviewer, always blocks (a reviewer P1 is fixed, or waived by the Captain with the reason recorded); from the third round on, a finding that is neither never starts a repair cycle and the FO declines it as a follow-up in the committed gate summary and a `Follow-up:` line in the successor task's Scope. Rounds 1 and 2 keep today's behaviour.
Verified by: (a) `test_sd_dispatch.py` builds an implementation and a validation dispatch from the package `workflow.md` in a disposable repository and asserts the dispatch file contains item 5's text; the falsifier deletes item 5 from the fixture and the assertion fails. (b) Current, reading only: the replay table in the Design shows rounds 3 and 4 of PR #1243 (3 and 5 findings, no P1) would have started no cycle. Limit: the FO applying the rule is prose, so no test proves an FO obeys it; qnow's next delivery PR is the only real observation.

**AC-2 — a repair does not queue behind another entity's worker.** `references/sd/workflow.md` `## Stages` states that `concurrency` limits only what `status --next` proposes, and that a feedback-reflow repair, the validation recheck of that repair, and an FO fix authorised under Review-finding disposition step 3 are dispatched at once in the entity's own worktree, after the existing overlap check against running worktrees.
Verified by: (a) Current: in a disposable repository under `/tmp` with `implementation` at `concurrency: 1` and entity A holding its worktree there, Spacedock 0.27.2 `dispatch build --feedback-reflow` for entity B exited 0 and emitted a dispatch envelope (command in the Design). (b) `test_sd_dispatch.py` gains the same case against the package `workflow.md`, asserting exit 0 with A in place; the case fails only if a future Spacedock adds a slot check to the reflow path, which is the regression it exists to catch; it does not prove any FO applies the lane. (c) The `workflow.md` text asserted by the same test as AC-1.

**AC-3 — the comment ratio is enforced above a declared maximum.** `comment_ratio.py` gains `--max PCT` and `--workflow-dir DIR` (key `comment-ratio-max:` in the workflow README frontmatter; `--max` overrides). With a maximum: exit 1 when the added-comment ratio is above it and at least 20 non-blank code lines were added; below 20 lines it prints that the ratio is not enforced and exits 0; exit 2 on an unreadable README or a non-numeric value; with no maximum the behaviour is today's (print, exit 0).
Verified by: `test_comment_ratio.py` (already run by `.github/workflows/kc-dev-flow-2-tests.yml`) adds cases: over the maximum exits 1; at the maximum exits 0; a 5-comment-of-5-line diff (the measured `dev-secrets-from-1password` case, 100%) exits 0 below the floor; no maximum exits 0; a bad README value exits 2. Mutations: flip `>` to `>=` fails the at-the-maximum case; drop the floor fails the 5-of-5 case. Replay, current: at the qnow base `3414d21a46e488c4cdf8cc04ef0e52dabd7403f8`, candidate `34523b7ca` measures 218/3404 = 6.4% (would exit 1 at 5) and `bd0deaf1a` 128/3314 = 3.9% (would exit 0 on the ratio).

**AC-4 — a comment cites an ADR or a greppable symbol, never task numbering or review provenance.** With or without a maximum, `comment_ratio.py` scans the added comment lines and exits 1 listing each `CITE <path>: <line>` that matches task-internal numbering (`Decision N`, `AC-N`, `Round N`, `Cycle N`, `Finding N`, `Task N`, `cycle-N`), review provenance (`Codex`, `review of`, `review follow-up`, `reviewer's`), a PR or issue number (`PR #N`, `#NN`) or a `file:line`; a line naming an ADR (`ADR NNNN`, `docs/adr/NNNN`) is exempt. The implementation and validation stage principles state the rule and that exit 1 is a trim (implementation) or a repair finding through feedback (validation).
Verified by: `test_comment_ratio.py` cases, one per class, plus the ADR exemption; the falsifier removes one class from the pattern and its case fails. Replay, current (a throwaway scan using the classes above, same base; the implementation's scanner replaces it): `34523b7ca` flags 34 of 218 added comments, every one a `Decision N`, `AC-N`, `cycle-N` or `Codex review of` citation (read by hand from the scan's output); `bd0deaf1a`, after the worker's own citation fix, still flags 3 (`Decision 9`, two `AC-1`), which the fix missed; over 150 older commits before the dev2 workflow (2478 added comments) it flags 25, of which one is a false positive (an ADR citation wrapped onto the next line) and the rest, read by hand, cite `AC-N`, `PR #N`, `finding N`, review provenance or a `file:line`. Limit: a pattern list finds the named classes only; other provenance wording ("as suggested in review") passes, so validation still reads every added comment.

**AC-5 — the rules reach the FO, the worker and the adopter.** Item 5 and the lane text live in `workflow.md` (the FO reads it; `## Review-finding disposition` is a `context-sections` entry of implementation and validation, so both workers receive it); the two principles files carry the exit-code handling; `references/sd/adoption.md` names `comment-ratio-max` and says an adopter picks its value and re-syncs its README from `workflow.md` to receive the rest.
Verified by: `lint-skills.py` and `test_lint_skills.py` pass; `test_sd_dispatch.py` (AC-1(a)) proves the inlining; `doc_impact.py <base> <candidate>` lists `README.md` of the package and each listed document carries `updated` or `unaffected: <reason>`.

**AC-6 — the ruling is an ADR.** One ADR for the Captain's rulings on rounds and the comment rule (Decisions: words, options considered), number from `number_guards.py reserve --kind adr`; a probe at design time printed `ADR: 0004` against `origin/main` `348c6876` and wrote nothing (the FO reserves and records it before dispatch).
Verified by: `python3 <package>/scripts/adr_lint.py docs/adr --require <number>` exits 0; `number_guards.py check` exits 0.

## Design (ideation, 2026-09-30)

### PRFAQ

**Proposition.** A delivery PR stops being reviewed by rule, not by the Captain's ad hoc word: a Material finding or a reviewer P1 always blocks, and from the third round on everything else becomes a recorded follow-up. A small repair starts at once instead of waiting for a long task in the same stage. A candidate's comments are counted against a declared maximum and cite only ADRs or symbols, and both failures exit non-zero before a validator has to find them.

**FAQ**

- *Why is the round count 2, and what does it buy?* Judgment, not measurement. qnow PR #1243 took four Codex rounds (4, 1, 3, 5 findings; the only P1 in round 1). With a cap of 2, rounds 3 and 4 (8 findings, no P1; assuming none is assessed Material, which was not read) would have started no cycle: two full implement, validate, push and CI cycles fewer. 2 also matches Spacedock's own cycle-3 escalation to the human. The Captain sets the number.
- *Is this Spacedock's cycle-3 escalation?* No, a second counter. `feedback-rejection-flow` counts rejection cycles of a feedback stage and, on cycle 3, escalates to the human; the new rule counts external-review rounds on a delivery PR, which may or may not have been routed through that flow. The escalation stays as the backstop when Material findings keep coming; the new rule supplies the recommended answer at it.
- *Who decides a finding becomes a follow-up?* The FO, under the authority Review-finding disposition step 2 already gives it for evidenced Deferred risk or Polish; the Captain sees the list and each home at the terminal gate summary. A reviewer P1 stays with the Captain because step 4 puts risk acceptance with the Captain; his words on #1246 were "a Codex P1 blocks merge until fixed and re-validated".
- *Where does a follow-up live?* In the Scope of the successor task, as qnow already did (`staff-multi-branch` carries the P2s "from Codex's last review of PR #1245"). Default successor: the open task whose Scope edits the finding's file; else a new backlog task from `spacedock new`. No new tracker.
- *What does Spacedock already do about a waiting repair, and is anything missing?* Nothing blocks it. `concurrency` is read only in `dispatchAnalysis` (`internal/status/format.go`, v0.27.2), which feeds `status --next`; that function skips an entity holding a worktree before it looks at concurrency, and `dispatch build` never reads it (only a comment in `build.go` says the word). The FO references carry no one-worker-per-stage rule; the only serial rule is bare mode, where `«async-dispatch»` is absent. So the #1246 wait (task `dev-secrets-from-1password`: validation approve recorded 11:57, implementation cycle-3 report committed 13:39, about 1h40 rather than the issue's "several hours"; the sibling `owner-vehicle-on-booking` held implementation from its 11:49 dispatch to its 13:24 report) looks like the FO reading `concurrency: 1` as a hard cap. That is consistent with the state history, not proven: the fix's dispatch time is not recorded and the FO transcript was not read. The package can state the rule; Spacedock needs no change.
- *Why not the issue's "bounded diff" or "size-aware limit"?* The size of a repair is not known before it is dispatched; ownership of a worktree is. The lane is keyed on ownership plus an authorised assignment, and a repair that grows past what its assignment names returns to the FO as a scope change (existing rule).
- *What does the lane cost?* More workers at once, and two candidates can touch the same files or a shared database branch. The existing dispatch step "check for obvious conflicts if multiple worktree stages would touch overlapping files" applies, migration numbers are per-task through `number_guards.py`, and an `Applied at:` collision on a shared non-production database branch is not detected by anything (documented limit of `## Number guards`).
- *Why a threshold with a floor?* `dev-secrets-from-1password` validated at 5 of 5 comment lines (100%), correctly: its whole diff was doc-comment replacement. A bare maximum would fail it. The floor of 20 added code lines is a choice, not a measurement; the only measured case it must clear is 5.
- *Why is the ratio's value not in the package?* Its only sources are the issue text, a qnow stage report ("the repo's 5% target (coordinator request)") and Kent's baseline of 3.0% (455 of 15145 lines added on `kc-claude-plugins` main, 2026-08-11 to 2026-08-25, from his global instructions). No repository file states 5%: qnow `AGENTS.md`, `learning.md`, `docs/dev2/README.md`, `docs/dev/README.md` and its ADRs were searched and none does. A policy value with no written source is the Captain's to set, and workflow policy is per adopter.

### Flow

```mermaid
sequenceDiagram
    participant X as External reviewer (Codex)
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

1. **The stopping rule as written**: rounds 1 and 2 as today; from round 3 only Material findings and reviewer P1 start a cycle; a reviewer P1 is never declined by the FO alone. Recommendation: approve with N = 2. Worse under it: a real defect labelled P2 that is not assessed Material is deferred to a follow-up.
2. **The comment-ratio value**: 5% for qnow (the issue's figure, no written source) and whether `kc-claude-plugins` itself declares 3.0% (Kent's measured baseline). Recommendation: the package ships no default; each adopter sets `comment-ratio-max:`; qnow 5. Worse under it: an adopter that never sets the key gets no enforcement, as today.
3. **Optional, not recommended now**: an upstream Spacedock issue for a mechanical repair lane. The package rule is enough; filing is an outward action for Kent to decide.

### Captain-run acceptance script (draft for validation to finalise, about 3 minutes)

Run from a checkout of the candidate branch, with `$PKG` set to its `kc-dev-flow-2` directory.

1. `T=$(mktemp -d) && git -C "$T" init -q -b main && cd "$T" && git -c user.name=t -c user.email=t@e.invalid commit -q --allow-empty -m base`.
2. Add `a.ts` with 40 lines of code and one comment line `// retry is idempotent`, then `git add a.ts && git -c user.name=t -c user.email=t@e.invalid commit -qm one`. Run `python3 $PKG/scripts/comment_ratio.py main~1 main --repo "$T" --max 5`: expect exit 0 (`echo $?`) and a ratio under 5%.
3. Add `b.ts` with 40 lines of code and 8 comment lines, one of them `// Decision 3: keep this`, commit, and run `python3 $PKG/scripts/comment_ratio.py main~2 main --repo "$T" --max 5`: expect exit 1, a ratio above 5%, and a `CITE b.ts:` line naming the `Decision 3` comment.
4. In a new commit that adds `c.ts` with 4 lines of code and 4 comment lines and no citation, run the tool on that one commit's range: expect a "not enforced" note (under 20 lines) and exit 0.
5. `python3 $PKG/scripts/test_comment_ratio.py`: expect `OK`.
Does not cover: an FO applying the round rule or the lane (prose, no test can prove it); Codex itself; any adopter's README.


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
