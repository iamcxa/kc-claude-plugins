---
title: A script checks the FO-written records that the observer found wrong more than once
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: validation
gates:
    version: 1
    records:
        - id: gate:fo-record-checks:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:fo-record-checks-backlog-1
              briefing:
                id: briefing:fo-record-checks:backlog:attempt-1:revision-1
                digest: sha256:42cf17b9eb33f344a9be0ceec170e2c302e8bb213cbfc0699d721fdf3e1a6601
                room-ref: ./fo-record-checks/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:fo-record-checks:backlog:1
                briefing: briefing:fo-record-checks:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T10:57:38.03132Z"
                decision: approve
                reason: 'Captain 2026-10-13: 「開」 to the backlog gate question "Schedule now as Pilot and enter ideation, learn-delivery-follow-through first, then fo-record-checks?", after 「向 kc-dev-flow-2 回報的問題可以回報，這個是否可以排進清單處理修復跟補強？」; profile pilot selected.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:fo-record-checks:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:fo-record-checks-ideation-1
              briefing:
                id: briefing:fo-record-checks:ideation:attempt-1:revision-1
                digest: sha256:2f42eca77abf85b4ce68a951bb4b0419ffb8e7853f0f47f2568e3dc2c537da12
                room-ref: ./fo-record-checks/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:fo-record-checks:ideation:1
                briefing: briefing:fo-record-checks:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T11:21:32.333038Z"
                decision: approve
                reason: 'Captain 2026-10-13: 「准」 to the ideation gate question; the question stated that approval accepts the recommendations for D1 (three checks, two wording changes, two drops) and D2 (hold on any head difference: FO revalidates the new head or tells the Captain before asking).'
              application:
                target-stage: implementation
                state: consumed
        - id: gate:fo-record-checks:validation
          stage: validation
          attempts:
            - id: gate-attempt:fo-record-checks-validation-1
              briefing:
                id: briefing:fo-record-checks:validation:attempt-1:revision-1
                digest: sha256:01bc1a70d53e79e3fbf9392cc65ab4817e6a827c42c515a4192c03c1cb6a37eb
                room-ref: ./fo-record-checks/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:fo-record-checks:validation:1
                briefing: briefing:fo-record-checks:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T12:00:31.926624Z"
                decision: approve
                reason: 'Captain 2026-10-13: 「准」 to the validation gate question "Deliver #640 head 63dfff51 ...: FO marks it ready and asks you to merge? Approval also covers later external-review rounds on this PR, per Delivery authority."'
              application:
                target-stage: done
                state: pending
started: 2026-10-13T10:58:03Z
worktree: .worktrees/spacedock-ensign-fo-record-checks
pr: iamcxa/kc-claude-plugins#640
---

Observer reports on four tasks archived 2026-10-13 (journey-map-dev2-contract, copilot-quota-refusal-is-not-a-review, workflow-checkout-must-match-trunk-readme, observer-before-merge-guard) found FO-written records that break rules the workflow README already states, and the learn evaluations returned no-change for each because the rule exists. A rule stated and not followed is an enforcement gap; `dispatch_records.py` and `design_surfaces.py` are the existing pattern for a script that checks FO's records.

## Captain's words

Captain 2026-10-13, in chat: 「向 kc-dev-flow-2 回報的問題可以回報，這個是否可以排進清單處理修復跟補強？」

## Scope

Candidates, each seen in an observer report (task named), for ideation to keep or drop:
- Dispatch checklists and scope notes name package scripts bare instead of `<package>/scripts/NAME.py` with the root substituted (workflow-checkout-must-match-trunk-readme, observer-before-merge-guard).
- A gate summary reports an unrun listed extension without the literal `<name> not run: <reason>` form (copilot-quota-refusal-is-not-a-review).
- `## FO alignment` records alignment as needed with no `Result:` line before dispatch (copilot-quota-refusal-is-not-a-review).
- A delivery gate names a PR head that no passing validation report names (observer-before-merge-guard).
- An ADR-settled decision is cited without the `Precedent: ADR <n> — 「<Words>」` form (observer-before-merge-guard).
- Wording gap: `Applied: none as of <sha>` is written for migrations; whether an ADR-only task owes it is unstated (workflow-checkout-must-match-trunk-readme).
- Non-goals: see `## Design`, Non-goals.

## Acceptance criteria

Replays below read the archived state under `<state>/_archive/` (the workflow's state checkout) with `PKG=<home>/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0`, the package those records were written under. Prototype scanners (disposable, outside the repository) already gave the stated results; the shipped scripts must reproduce them.

- **AC-1** `python3 <package>/scripts/dispatch_records.py --names <record file>...` exits 1 and prints `<file>:<line>: bare package script name <NAME>` for each package script (a `.py` file directly under `<package>/scripts/` or `<package>/extensions/<name>/`) written with no directory part in the `## Checklist` or `## Scope notes` section; a file with neither heading is scanned whole. Evidence: with `PKG` above, `workflow-checkout-must-match-trunk-readme/dispatch/validation-1.md` exits 1 naming `adr_lint.py` at line 10; `.../implementation-2.md` names `roborev_gate.py` at line 11; `observer-before-merge-guard/dispatch/implementation-1.md` names `roborev_gate.py` (line 10) and `lint-skills.py` (lines 10, 18); `.../validation-1.md` names `adr_lint.py` at line 11. Falsifier: a scanner that returns no findings turns all four to exit 0 and the test fails.
- **AC-2** `--names` exits 0 on a record that complies, and on a name written with any directory part. Evidence: archived `copilot-quota-refusal-is-not-a-review/dispatch/implementation-3.md` (no script named) exits 0; a copy of `observer-before-merge-guard/dispatch/implementation-1.md` with every flagged name given its absolute `<PKG>/scripts/` or `<PKG>/extensions/<name>/` path exits 0 (prototype run, exit 0); `scripts/NAME.py` and `<package>/scripts/NAME.py` are not judged. Falsifier: a scanner that flags every `.py` token fails the substituted copy; a scanner that reads only `scripts/` and not `extensions/` misses `roborev_gate.py` and fails AC-1.
- **AC-3** The default mode of `dispatch_records.py <task folder>` is unchanged. Evidence: the folder run on archived `workflow-checkout-must-match-trunk-readme`, `observer-before-merge-guard` and `copilot-quota-refusal-is-not-a-review` prints `9`, `12` and `6 dispatch record(s) complete` with exit 0 before and after (measured today on the 0.22.0 script), and the existing `test_dispatch_records.py` cases pass. Falsifier: folding the name scan into the default mode turns those three runs to exit 1.
- **AC-4** `python3 <package>/scripts/delivery_gate.py check <task file> --pr <owner/repo>#<N> --text-file <file> [--head <sha>]` takes the latest `## Stage Report: validation` section that holds `Verdict PASSED` followed within 160 characters by a hexadecimal SHA of 7 to 40 characters with a digit, as the validated candidate. It compares that SHA, as a prefix of equal length, with the PR head (`--head`, else `gh pr view <N> --repo <owner/repo> --json headRefOid`). Exit 0 equal; exit 1 differs, printing both; exit 2 when no passing report names a candidate or the head cannot be read. Evidence (task file at its final state, `--head` given): `observer-before-merge-guard` with `7679ab7a` exits 1 naming validated `40c714a6`, with `40c714a6` exits 0; `workflow-checkout-must-match-trunk-readme` with `20c9ec53`, `worker-completion-goes-to-main` with `84de8242` and `copilot-quota-refusal-is-not-a-review` with `22d9cc94` exit 0; `migration-and-number-guards` with `83cad4f70a36` exits 1 naming validated `aff49ab3`; `board-optout` (older report form, no candidate SHA) exits 2. Falsifier: taking the first passing report instead of the latest gives `0830a3be` for the observer task, so `--head 40c714a6` exits 1 and the test fails.
- **AC-5** The same command reads `--text-file` (the gate question and summary FO is about to pass to `gate prepare`). For each `Second reviewer: <X> because` in it, other than that phrase, the text must hold `<X> not run: <reason>` or, in one sentence naming `<X>`, a `review:<id>` or `comment:<id>` token; otherwise exit 1 naming `<X>`. Evidence: texts built from the archived briefings' question and artifact summaries (`<task>/review/validation/briefing-N/index.json`): `copilot-quota-refusal-is-not-a-review` briefing-1 exits 1 naming copilot; `observer-before-merge-guard` briefing-1 and briefing-2 exit 0; a text with no such line exits 0. Falsifier: accepting a `review:<id>` token anywhere in the text lets the copilot case pass on Codex's `review:5500046230`, and the test fails. Limit: 3 archived summaries carry the line, 1 violates; a false-positive rate is not measured.
- **AC-6** `references/sd/workflow.md` carries four wording changes and `lint-skills.py` passes: (a) in Stages, FO runs `dispatch_records.py --names` on the saved record before `dispatch build` and rewrites what it lists; (b) in Delivery authority, FO runs `delivery_gate.py check` before the `gate prepare` that asks for merge, an exit 1 or 2 holds the ask and FO shows the Captain what it printed; (c) in Extensions, an extension FO does not request because a ruling says not to is reported as `<name> not run: <reason>`; (d) in FO steps: number guards, a task with no `Migration:` line records no `Applied:` line. Evidence: `python3 kc-dev-flow-2/scripts/lint-skills.py` exits 0 with `WORKFLOW_WORD_BUDGET` raised by the words added (about 120, an estimate; `workflow.md` is 5415 words on origin/main and the budget is 5415, measured 2026-10-13), the reason in the same change. Falsifier: without the budget raise the lint exits 1 naming the count. Not provable here: that a live FO follows (a) to (d); the next observer report on a task dispatched after release is that evidence.
- **AC-7** The new unit tests run in CI. Evidence: `.github/workflows/kc-dev-flow-2-tests.yml` lists `test_delivery_gate.py` (one added step in the existing job, no new job or trigger; duration not measured) and `test_dispatch_records.py` keeps its step. Falsifier: remove the step and the job no longer names the file.
- **AC-8** One integration run before delivery: on a real open PR and its task file, `delivery_gate.py check` runs with live `gh`, once equal and once with a deliberately different `--head`. Evidence: both printed outputs and exit codes in the validation report. Falsifier: a unit-only run with an injected `gh` result cannot show that `gh pr view --json headRefOid` returns what the script reads.

## Design

### Chain check

- Spacedock 0.27 (`spacedock --help`, `gate prepare --help`, `dispatch build --help`, 2026-10-13): `dispatch build` takes the checklist and scope notes as files and `gate prepare` takes the question and summary as text; neither inspects their content. No Spacedock capability applies.
- `kc-dev-flow-2` at origin/main (0.22.0): `scripts/dispatch_records.py` checks four parts of a record and passes the three tasks below (9, 12 and 6 records complete), so it does not see a bare script name. The only mention of the rule is the workflow.md Stages sentence; `git grep` for `bare script`/`NAME.py` finds nothing else. `dispatch_records.py` is run by the validation worker over the whole task folder and in CI; FO's README steps do not run it. `design_surfaces.py check --seed` reads `## FO alignment` and `observer_check.py` reads `observer.md`; neither reads gate text or the PR head. `number_guards.py check` runs on the PR head before the merge ask but compares migration and ADR numbers only.
- Sibling adopters (`qnow`, `subspace-relay`, 2026-10-13): `git grep` for `dispatch_records`, `not run:` and `Precedent:` finds no script that checks FO records. Nothing to borrow.
- Existing-code check (bounded): `dispatch_records.py` is complete as a unit-tested, CI-run check but has no FO consumer; the need is the observer's repeated finding. Two searches: the `git grep` above, and the replay below (38 of 60 archived dispatch records had a bare name, replayed with the 0.21.0 package names; none was caught while FO wrote it). So: extend `dispatch_records.py`, add one new script only for the two gate-text facts.

### PRFAQ

**Press release.** Today a first officer that writes a dispatch with `adr_lint.py` where the rule asks for the absolute path learns about it from the observer after the task is archived. From the next release it runs one command on the record before building the dispatch, and one before asking for merge. Each prints what is wrong and exits 1. The observer stays as the backstop for what no script can see.

**FAQ**

- *Which of the six candidates ship as scripts?* Three: bare script names, a triggered second reviewer with no stated outcome, and a PR head that is not the validated candidate. The other three are not scripted (table below).
- *Why is the rule on bare names checkable when the others mostly are not?* It is decided by the text alone: a name that exists in the package, with no directory in front of it. Whether a decision is "settled by an ADR", or an alignment is "needed", takes a reading of meaning.
- *What is the evidence the bare-name rule matters?* Replayed with the 0.21.0 package: 38 of 60 archived dispatch records and 73 mentions, in 8 tasks (the two named in the task, `journey-map-dev2-contract`, `worker-completion-goes-to-main`, and the ideation dispatches of this task and of `learn-delivery-follow-through`). The existing check passes all three observer-named tasks.
- *What does it get wrong?* A bare name for a file the task edits (a test file next to a script it changes) is flagged; the remedy is writing the repository path, which is clearer for the worker anyway. A name with any directory part is never judged, so an unsubstituted `<package>/scripts/NAME.py` passes. `--names` is not run by validation over old records, because FO cannot honestly rewrite a record the worker already followed.
- *What happens when the head differs because trunk was merged into the PR?* Exit 1. FO revalidates the new head, or tells the Captain the difference instead of asking for merge as if it were validated (decision D2).

### Candidate dispositions

| Candidate (task named) | Disposition | Record and rule checked, or the reason |
| --- | --- | --- |
| Bare script names (workflow-checkout-must-match-trunk-readme, observer-before-merge-guard) | **Keep**, `dispatch_records.py --names` | `<task>/dispatch/<stage>-<cycle>.md`, sections `## Checklist` and `## Scope notes`; Stages: "never the bare script name". Run point: after FO saves the record, before `dispatch build`. |
| `<name> not run: <reason>` form (copilot-quota-refusal-is-not-a-review) | **Keep, narrowed**, `delivery_gate.py check` | The gate question and summary FO passes to `gate prepare`; Extensions: "reported as `<name> not run: <reason>`". Narrowed to a text that says `Second reviewer: <X> because`. Broader forms were measured and dropped: a check for any mention of codex, copilot or roborev without evidence scored 0 of 1 (the one violation passed because Codex's `review:` token sat in the same text) and flagged 7 of 81 briefings for prose that breaks no rule. Wording also changes (AC-6c): the README says "cannot run", and ADR 0013 D2 made "not requested on purpose" a second case. |
| `## FO alignment` needed with no `Result:` line (copilot-quota-refusal-is-not-a-review) | **Drop** | At the dispatch commit the record read `Alignment: not needed ...`; FO had rewritten "Needed at ideation: whether other non-review Copilot answers ... share the fix", which was an open question for the ideation worker, not a Captain alignment. A `Result:` check passes that record. 0 of the 9 task files with an `Alignment:` line say needed. The ideation principles already stop the worker on "needed with no `Result:`". A history check (briefing artifact against dispatch commit) would need a second reader of git history for one occurrence. |
| PR head versus latest passing validation (observer-before-merge-guard) | **Keep**, `delivery_gate.py check` | Delivery authority: "FO confirms the PR head equals the candidate the latest passing validation report names". The validation stage already owes "artifact identity" in its report. Run point: before the `gate prepare` that asks for merge. Replay on the 5 tasks with a parseable report and a named head: 3 matched; 2 differed, `observer-before-merge-guard` (trunk merged into the PR, disclosed and approved) and `migration-and-number-guards` (a Polish commit `83cad4f7` added after the validated `aff49ab3`, and the gate question called it the validated candidate). 5 of 21 archived task files have a parseable report; 4 of the 5 tasks dated 2026-10-13 do (`journey-map-dev2-contract`, with two PRs, does not). |
| `Precedent: ADR <n>` form (observer-before-merge-guard) | **Drop** | Absence cannot be told from text: the briefings hold about 30 `ADR <n>` mentions, most of them the task's own ADR or a reference. A check that validates a `Precedent:` line when present would have caught nothing here, since none was written (`Precedent:` appears in no archived task). The observer already reads it. |
| `Applied: none as of <sha>` for an ADR-only task (workflow-checkout-must-match-trunk-readme) | **README sentence**, no script (AC-6d) | `Applied at:` freezes migrations (`number_guards.py check` R2); an ADR-only task pushes none and nothing reads `Applied: none` for it. A script would check a line with no consumer. |

### Flow

```mermaid
sequenceDiagram
    participant FO as First officer
    participant DR as dispatch_records.py --names
    participant W as Worker
    participant DG as delivery_gate.py check
    participant C as Captain
    participant O as Observer
    FO->>FO: save dispatch record (checklist, scope notes)
    FO->>DR: run on the record
    alt a bare package script name
        DR-->>FO: exit 1, file:line and name
        FO->>FO: write the absolute path, run again
    else clean
        DR-->>FO: exit 0
    end
    FO->>W: dispatch build, then the worker runs
    W-->>FO: validation report names the candidate, Verdict PASSED
    FO->>DG: before gate prepare: task, PR, question and summary text
    alt head differs, second reviewer unstated, or cannot compare
        DG-->>FO: exit 1 or 2, what it printed
        FO->>C: shows the output; revalidates or asks, no merge ask yet
    else equal and stated
        DG-->>FO: exit 0
        FO->>C: gate prepare, then the merge ask
    end
    C-->>FO: merge, task archived
    O->>O: reads FO records at archive (backstop for what no script reads)
```

The sequence matches the prose: two FO run points, each with exit 0 / exit 1 (and exit 2 for the second), the Captain holding every merge decision, the observer unchanged.

### Files, and what is shared with learn-delivery-follow-through

Edited here: `kc-dev-flow-2/scripts/dispatch_records.py` and `test_dispatch_records.py`; new `kc-dev-flow-2/scripts/delivery_gate.py` and `test_delivery_gate.py`; `kc-dev-flow-2/references/sd/workflow.md` (Stages paragraph, Delivery authority paragraph, Extensions paragraph, FO steps: number guards, Applied bullet); `kc-dev-flow-2/scripts/lint-skills.py` (`WORKFLOW_WORD_BUDGET`); `.github/workflows/kc-dev-flow-2-tests.yml` (one step). Not edited: `skills/validation/principles.md` (its folder run keeps the default mode), the adopter copy `docs/dev2/README.md` (a sync PR after release).

Shared with `learn-delivery-follow-through` (its task file had no design when read, 2026-10-13, so this is expected, not compared): `workflow.md` Delivery authority (this task adds the `delivery_gate.py` sentence beside the merge-ask sentence; that task adds the learn PR's ready and watch steps), the `WORKFLOW_WORD_BUDGET` line in `lint-skills.py` (both raise it; certain textual conflict), and the tests workflow file (adjacent steps). Land one first; the second rebases and raises the budget again by its own words, with its own reason. Word them differently: the lint refuses a 12-word run repeated between `workflow.md` and a skill.

### Non-goals

- No check for `Precedent:`, `## FO alignment` `Result:`, or any rule that needs a reading of meaning.
- No history comparison of a task file across commits.
- No change to who authors dispatch records, and no `--names` run by validation over earlier records.
- No judgment of a name that has a directory part, and no attempt to tell an edit target from a run.
- No hook, and no change to Spacedock's `gate prepare` or `dispatch build`.
- No ADR drafted: the dispositions are this task's scope. Say if the drop reasons should stand as a rule for later work; then FO lands it as an ADR.

### Limits

- The replay of AC-1 used the 0.21.0 package names; a task written under a newer package would see newer names, which is the intended behaviour.
- `delivery_gate.py` exit 2 is common on older task files (16 of 21 had no parseable candidate). It holds the ask and shows the Captain; it does not fail silently.
- The wiring claim (a live FO runs both commands) is a README sentence; nothing here proves FO follows it.

## Unresolved decisions for the Captain

Checked: ADR 0014 D2 (strict equality, hold on difference) and ADR 0013 D2; the `Override:` lines in the state checkout (none from a gate record; the hits are prose). Approving accepts the recommendation for D1 and D2 only if the gate question says so.

- **D1 scope: ship three checks and two wording changes, drop two candidates?** Recommend yes: bare names in `dispatch_records.py --names`; PR head and the second-reviewer outcome in a new `delivery_gate.py`; wording for the `not run` case and for `Applied:` on ADR-only tasks; drop the `Result:` line and the `Precedent:` form. Worse under yes: the dropped two stay caught only by the observer after archive, and the second-reviewer check rests on three archived texts, one violating.
- **D2 head mismatch: hold on any difference?** Recommend yes, strict equality as ADR 0014 D2 chose for the README: exit 1 and FO revalidates the new head or tells you the difference before asking. Worse under yes: a PR that gets trunk merged into it after validation costs one more validation cycle (observer-before-merge-guard would have needed one). Moot if D1 drops this check.

## FO alignment

Alignment: not needed before ideation; the Captain asked for the fix.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

## Stage Report: ideation

- DONE: A design (PRFAQ and Mermaid) for a script that checks the FO-written records the observer found wrong on 2026-10-13, extending the dispatch_records.py pattern: for each candidate in the task's Scope, keep it (with the exact record and rule it checks) or drop it with a reason, including whether the Applied: none wording gap needs a README sentence instead
  `## Design` holds the chain check, PRFAQ, a sequence diagram, and a six-row disposition table: keep bare names (`dispatch_records.py --names`), keep head-vs-validated and a narrowed second-reviewer outcome (new `delivery_gate.py`), drop `Result:` and `Precedent:`, README sentence for `Applied:` (and one clause for the `not run` wording).
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, each kept check replayed against the archived records that showed the violation (named in the task) and against a record that complies
  `design_surfaces.py check fo-record-checks.md` printed "fo-record-checks.md: design surfaces presentable" (exit 0). Per criterion, current evidence:
  AC-1 bare names flagged: prototype replay on the four named archived records gave the stated file:line results with the 0.21.0 names; shipped script not yet written.
  AC-2 complying record passes: prototype exit 0 on a fully substituted copy of a real record and on a record with no script named; shipped script not yet written.
  AC-3 default mode unchanged: folder runs on three archived tasks print 9, 12, 6 records complete exit 0 on the current script; the after-change run is not yet verified.
  AC-4 head versus validated: prototype replay gave exit 1/0 as stated for six task and head pairs and exit 2 for older forms; shipped script not yet written.
  AC-5 second-reviewer outcome: prototype replay on the three archived summaries (1 flagged, 2 pass); the broader form scored 0 of 1 and 7 false flags; shipped script not yet written.
  AC-6 workflow.md wording and budget: not yet verified; lint run after the edit is the evidence; the budget (5415 words, at limit) measured today.
  AC-7 CI step: not yet verified (one step to add).
  AC-8 live `gh` integration run: not yet verified.
- DONE: Unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  D1 (scope of the three checks and two wording changes, two drops) and D2 (strict hold on head mismatch, ADR 0014 D2 precedent); ADR 0013/0014 and the `Override:` lines read, none contradicts.

### Summary

Of six candidates only the bare-script-name rule is both repeated (38 of 60 archived dispatch records, 8 tasks) and decided by the record text alone, so it extends `dispatch_records.py` with a `--names` mode run before `dispatch build`. The PR-head rule bit twice (observer-before-merge-guard, migration-and-number-guards) and the second-reviewer outcome once, so both go into one new `delivery_gate.py` run before the merge ask; the `Result:` line and `Precedent:` form are dropped because a check on the record as it stands would have passed the observed miss, and `Applied:` and the `not run` wording are README sentences. Expected shared files with learn-delivery-follow-through: `references/sd/workflow.md` (Delivery authority), the `WORKFLOW_WORD_BUDGET` line in `lint-skills.py`, and the tests workflow file; prototypes lived outside the repository and were not committed.

## Stage Report: implementation

- DONE: One Draft PR (fix(kc-dev-flow-2): ...) from a branch off origin/main with dispatch_records.py --names and its tests, the new scripts/delivery_gate.py and test_delivery_gate.py, the four references/sd/workflow.md sentences, the lint-skills.py budget raise (by the words added, reason stated) and the tests-workflow step; AC-1 to AC-7 green with each falsifier shown failing by a mutation run, replays against the archived records reproducing the design's results
  PR #640 (Draft, iamcxa/kc-claude-plugins, branch spacedock-ensign/fo-record-checks off origin/main 38c55fcf), commits 463423e1 and 63dfff51; budget 5463 to 5561 (+98) with reason in lint-skills.py.
  AC-1/2: replay with 0.21.0 names reproduces the stated file:line lists (workflow-checkout validation-1:10 adr_lint.py, implementation-2:11 roborev_gate.py; observer implementation-1:10 roborev_gate.py and lint-skills.py, :18 lint-skills.py; validation-1:11 adr_lint.py), copilot-quota implementation-3 and a fully path-substituted copy exit 0. Mutations killed: scanner returns nothing (3 tests fail), flags directory-qualified names (1), reads only scripts/ (2).
  AC-3: folder mode prints 9, 12, 6 records complete exit 0 after the change; mutation folding the name scan into folder mode fails test_the_default_mode_does_not_scan_names.
  AC-4/5: replays exit as stated (observer 7679ab7a 1, 40c714a6 0; 20c9ec53, 84de8242, 22d9cc94 0; migration 83cad4f70a36 1 naming aff49ab3; board-optout 2; copilot-quota briefing-1 1, observer briefing-1 and -2 0). Mutations killed: first instead of latest report (13 failures), review token anywhere (3), `not run:` without reason (1), exact-length compare (8).
  AC-6: lint-skills.py exits 0 at 5561; without the raise it exits 1 naming 5561 over 5463. AC-7: one step test_delivery_gate.py added, test_dispatch_records.py keeps its own; CI unit tests job passes on the PR head (below).
  Replay count over live plus archived records: 62 dispatch records, 40 with a bare name, 78 mentions, 8 tasks (design said 60, 38, 73; the difference is records written since, including this stage's own).
- DONE: AC-8: one live run of delivery_gate.py check with real gh on an open PR (equal head and a deliberately different --head), outputs and exit codes in the report
  Live gh on #639 (read only), scratch task file /tmp/fo-rc-scratch-task.md naming f16898491a5d (the real learn-delivery-follow-through.md has no passing validation report, exit 2 measured):
  no --head: `PR head f16898491a5d4fadbb189373fbbe89754013dddc equals validated candidate f16898491a5d; no second reviewer outcome is missing` exit 0.
  --head 7679ab7a: `PR head 7679ab7a differs from validated candidate f16898491a5d (latest passing validation report in /tmp/fo-rc-scratch-task.md)` exit 1.
  candidate aff49ab3 vs live head: `PR head f16898491a5d4fadbb189373fbbe89754013dddc differs from validated candidate aff49ab3 ...` exit 1.
  PR #99999: `cannot read the head of iamcxa/kc-claude-plugins#99999: gh pr view exited 1: GraphQL: Could not resolve to a PullRequest with the number of 99999.` exit 2.
- DONE: roborev_gate.py evidence= line, CI green on the PR head, lint-skills.py green, and the CI cost per PR measured or stated as not measured
  `findings on 463423e12; evidence=roborev:625`, rerun `evidence=roborev:626`, exit 1 both (finding below). CI: all 5 checks pass on PR head 63dfff51 (unit tests job 47 s, version parity 56 s); the first push 463423e1 failed unit tests on test_sd_dispatch.py and was repaired in 63dfff51. lint-skills.py exit 0. CI cost: one added step; test_delivery_gate.py takes about 1 s locally; CI duration of the step not measured.

Affected documents (doc_impact.py 38c55fcf..HEAD): kc-dev-flow-2/README.md: unaffected: it says every other test file is listed in the tests workflow, which still holds. kc-dev-flow-2/skills/maintain-flow/SKILL.md: unaffected: it describes the word-budget lint behaviour, which is unchanged.
comment_ratio.py 38c55fcf HEAD: `code lines 301, comment lines 2, 0.7%`, maximum 5% met. design_surfaces.py check: `fo-record-checks.md: design surfaces presentable`, exit 0. No ADR added or changed. Number guards: none.

### Findings for FO

- Class Deferred risk (RoboRev, High as labelled): delivery_gate.py accepts a 7 to 40 character candidate that prefixes the head. Harm needs a different commit sharing the validated short prefix. Field 3 is value-ac[AC-4], which approved prefix-of-equal-length; an exact-40 rule exits 1 on every archived report (they record 8 characters). Becomes Material if reports start recording full SHAs: then raise the minimum length.
- Change to the design: a fifth workflow.md edit, one sentence in the Number guards Applied bullet ("A task with no `Migration:` line owes none of these."), so the validator rule matches the FO step (d). Both Applied additions are appended sentences: my first wording changed text that test_sd_dispatch.py pins and CI failed on the first push (63dfff51 fixes it); test_sd_dispatch.py is unchanged.
- Limits: a sentence naming the second reviewer that also carries another reviewer's review token passes (the split is on . ! ? and newline, not on ;). The second-reviewer rule rests on three archived summaries, one violating; no false-positive rate. delivery_gate.py exit 2 is common on older task files. That a live FO runs both commands is prose-enforced. The AC-8 task file is a scratch file.
- AC-6 wording (d) is done as: a task with no `Migration:` line records no `Applied:` line.

### Summary

dispatch_records.py --names and the new delivery_gate.py reproduce every replay in the design, each falsifier fails under a mutation, and workflow.md names both run points. PR #640 is Draft; the first CI push failed on a test_sd_dispatch.py pin that my first Applied wording broke, and the second push reworded it additively.

## Stage Report: validation

- DONE: Independent verdict on #640 head 63dfff51 against AC-1 to AC-8, re-running each evidence command and at least one falsifier per criterion yourself (replays against the archived records, the default folder mode unchanged, delivery_gate.py on the named task and head pairs, lint budget, CI step, and one live gh run on an open PR read only), and judging the implementation's two changes to the design (a fifth workflow.md sentence; prefix-of-equal-length SHA comparison kept despite roborev:625/626)
  All eight criteria met at 63dfff51 in a throwaway worktree (removed). Each falsifier below was run on a copy of the script in /tmp, never on the candidate.
  AC-1: replay with the 0.21.0 names (script's `package=` argument) printed the stated file:line lists on all four archived records, exit 1 each; scanner-returns-nothing mutation gave exit 0 on validation-1 (falsifier works); scripts/-only mutation missed roborev_gate.py.
  AC-2: copilot-quota implementation-3 exit 0; observer implementation-1 with every flagged name rewritten to its absolute 0.21.0 path exit 0; flag-every-.py mutation turned that copy to exit 1. Extra probes: `scripts/x.py`, `./x.py`, `~/x.py`, a URL and a section other than Checklist/Scope notes are not judged; a quoted or backticked bare name is.
  AC-3: folder runs on the three archived tasks print 9, 12, 6 records complete, exit 0, on both the 38c55fcf script and the candidate; mutation that also runs the name scan in folder mode turned observer-before-merge-guard to exit 1.
  AC-4: all eight pairs reproduced (observer 7679ab7a exit 1 naming 40c714a6, 40c714a6 exit 0; 20c9ec53, 84de8242, 22d9cc94 exit 0; migration 83cad4f70a36 exit 1 naming aff49ab3; board-optout exit 2); first-report mutation made `--head 40c714a6` exit 1 on the observer task, naming 0830a3be.
  AC-5: built texts from all six archived briefings that carry a `Second reviewer:` line: copilot-quota exit 1 naming copilot; observer 1 and 2, worker-completion 1 and 2, workflow-checkout 1 exit 0 (the design counted three; the other three read `not triggered`, no `because`, so they are not judged); review-token-anywhere mutation turned the copilot text to exit 0.
  AC-6: lint-skills.py exit 0, `5561 of 5561 words`; copy with the budget at 5463 exits 1 (`5561 words exceeds the budget of 5463`). Base is 5463, not the 5415 the AC text says (main moved with #631 before the dispatch); +98 words against the "about 120" estimate. Wording (a) to (d) present at Stages, Delivery authority, Extensions and the number-guards FO step.
  AC-7: CI run 38391811132 on 63dfff51 lists `test_delivery_gate.py` and `test_dispatch_records.py` as passed steps; base workflow file has 0 mentions of test_delivery_gate. test_sd_dispatch.py needs a Spacedock plugin root: read from CI (passed), not run here.
  AC-8: live gh on #640 (head 63dfff51): no --head exit 0 `PR head 63dfff51915b4054b56c22ac028e9d2556636733 equals validated candidate 63dfff51915b`; `--head 463423e1` exit 1 naming both; #99999 exit 2 `cannot read the head ... Could not resolve to a PullRequest`. The task file for those runs is a scratch file naming 63dfff51915b.
  Design change 1, fifth workflow.md sentence ("A task with no `Migration:` line owes none of these.", validator bullet): accepted. number_guards.py reads only `Applied at:` (grep of the script), so the sentence matches behaviour; it is the validator-side twin of AC-6d, 9 words. FO names it in the gate summary since the Captain approved four wordings.
  Design change 2, prefix-of-equal-length compare kept despite roborev:625/626: accepted as Deferred risk (below). An exact-40 compare cannot work, because archived reports record 8 characters (AC-4 replays above would all exit 1). I read the implementation report's account of roborev:625/626, not the roborev output.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh shell from a named checkout, with its observed output
  Script below (six steps, about 10 seconds, needs network, `gh auth status` passing, and the archived task under the workflow state checkout). Run as written under `env -i HOME PATH bash --noprofile --norc -c` and `zsh -f -c`: same output both, exit codes as listed.
- DONE: adr_lint.py docs/adr --since <base> run with its exit code; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition
  `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.0/scripts/adr_lint.py docs/adr --since 38c55fcf` in the 63dfff51 worktree: `14 ADR file(s) checked, 0 legacy`, exit 0. Also run: comment_ratio.py 38c55fcf 63dfff51 `code lines 301, comment lines 2, 0.7%` exit 0; doc_impact.py lists README.md and maintain-flow/SKILL.md, both carry `unaffected:` lines in the implementation report; design_surfaces.py check exit 0; dispatch_records.py on this task's folder `3 dispatch record(s) complete` exit 0; no Number guards section.
  Verdict PASSED on candidate 63dfff51915b4054b56c22ac028e9d2556636733 (PR #640, base 38c55fcf, CI green on this head).

### Findings

None is Material. Classified by the Review-finding disposition:
- Deferred risk: prefix compare accepts a 7 to 40 character candidate that prefixes the head. Needs a different commit sharing the validated prefix; none observed. Material if validation reports start recording full SHAs or the repository gets crafted commits: then raise the minimum length.
- Deferred risk: a sentence naming the second reviewer that also carries another reviewer's `review:`/`comment:` token passes (split on `.`, `!`, `?`, newline, not `;`). Probe: `Second reviewer: copilot because x.` then `Codex review:5500046230 done; copilot not run:` exits 0. AC-5 says "one sentence", so this is the specified limit; no instance observed. Material if FO writes such a sentence for a review that did not run.
- Deferred risk: the candidate is the first 7 to 40 hex character token with a digit within 160 characters after `Verdict PASSED`. A number before the SHA (`CI run 38391811132`) is taken as the candidate and exits 1 against a correct head; a SHA written before the verdict exits 2. Both fail closed with a message, never silent. The validation checklist's wording "verdict PASSED or REJECTED naming the head" is what steers a worker to the readable form; nothing in the validation principles states it. Material if validators routinely write the other form and FO holds every gate.
- Polish: `dispatch_records.py --names <missing file>` prints a Python traceback and exits 1, the same code as a finding. FO sees the traceback; no value lost.
- Polish: AC-6 evidence text says base 5415 and about 120 words; measured base 5463 and +98 (the implementation report states the real numbers).
- Corroboration, not a finding: `--names` on this task's own three dispatch records (0.22.0 names) lists nine bare names (`dispatch_records.py`, `lint-skills.py`, `delivery_gate.py`, `roborev_gate.py`, `adr_lint.py`), all written before the check existed; this is the rule class AC-1 targets.

### Not verified

- That a live FO runs `dispatch_records.py --names` and `delivery_gate.py check` at the stated points: README prose only; the next observer report after release is the evidence.
- test_sd_dispatch.py locally (CI passed it); Codex round 1 requested at dispatch is not read by this stage; false-positive rate of the second-reviewer rule (six texts, one violating).

### Minimal acceptance script

Run in a fresh shell (bash or zsh), no comments in the block so it pastes anywhere.

```
echo "--- step 1"
D=$(mktemp -d /tmp/fo-record-checks-accept.XXXXXX) && git clone --quiet --branch spacedock-ensign/fo-record-checks --single-branch --depth 20 https://github.com/iamcxa/kc-claude-plugins "$D" && git -C "$D" checkout --quiet --detach 63dfff51 && git -C "$D" rev-parse --short=8 HEAD
G="$D/kc-dev-flow-2/scripts"
echo "--- step 2"
printf '## Checklist\n\nrun adr_lint.py on the branch\n' > "$D/bare.md"; printf '## Checklist\n\nrun %s/adr_lint.py on the branch\n' "$G" > "$D/full.md"
python3 "$G/dispatch_records.py" --names "$D/bare.md"; echo "exit $?"; python3 "$G/dispatch_records.py" --names "$D/full.md"; echo "exit $?"
echo "--- step 3"
A=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/observer-before-merge-guard.md
python3 "$G/delivery_gate.py" check "$A" --pr iamcxa/kc-claude-plugins#640 --text-file /dev/null --head 7679ab7a; echo "exit $?"; python3 "$G/delivery_gate.py" check "$A" --pr iamcxa/kc-claude-plugins#640 --text-file /dev/null --head 40c714a6; echo "exit $?"
echo "--- step 4"
printf 'Second reviewer: copilot because the change touches review rules.\n' > "$D/gate1.txt"; printf 'Second reviewer: copilot because the change touches review rules.\ncopilot not run: quota refused.\n' > "$D/gate2.txt"
python3 "$G/delivery_gate.py" check "$A" --pr iamcxa/kc-claude-plugins#640 --text-file "$D/gate1.txt" --head 40c714a6; echo "exit $?"; python3 "$G/delivery_gate.py" check "$A" --pr iamcxa/kc-claude-plugins#640 --text-file "$D/gate2.txt" --head 40c714a6; echo "exit $?"
echo "--- step 5"
printf '## Stage Report: validation\n\n- DONE: x\n  Verdict PASSED on 63dfff51915b\n' > "$D/task.md"
python3 "$G/delivery_gate.py" check "$D/task.md" --pr iamcxa/kc-claude-plugins#640 --text-file /dev/null; echo "exit $?"; python3 "$G/delivery_gate.py" check "$D/task.md" --pr iamcxa/kc-claude-plugins#640 --text-file /dev/null --head 463423e1; echo "exit $?"
echo "--- step 6"
python3 "$G/lint-skills.py" > "$D/lint.out" 2>&1; echo "lint exit $?"; grep "words" "$D/lint.out"; python3 "$G/test_dispatch_records.py" 2>&1 | tail -3; python3 "$G/test_delivery_gate.py" 2>&1 | tail -3
```

Expected, in order: step 1 prints `63dfff51`. Step 2 prints `<D>/bare.md:3: bare package script name adr_lint.py`, `exit 1`, then `exit 0`. Step 3 prints `PR head 7679ab7a differs from validated candidate 40c714a6 (latest passing validation report in .../_archive/observer-before-merge-guard.md)`, `exit 1`, then `PR head 40c714a6 equals validated candidate 40c714a6; no second reviewer outcome is missing`, `exit 0`. Step 4 prints `second reviewer copilot has no stated outcome: add 'copilot not run: <reason>' or a review:<id> or comment:<id> in a sentence naming copilot`, `exit 1`, then the `equals` line and `exit 0`. Step 5 prints `PR head 63dfff51915b4054b56c22ac028e9d2556636733 equals validated candidate 63dfff51915b; no second reviewer outcome is missing`, `exit 0`, then `PR head 463423e1 differs from validated candidate 63dfff51915b (latest passing validation report in <D>/task.md)`, `exit 1` (step 5 holds only while PR #640 head is 63dfff51). Step 6 prints `lint exit 0`, `references/sd/workflow.md: 5561 of 5561 words; no unlisted passage repeats it`, then `Ran 10 tests ... OK` and `Ran 12 tests ... OK`.

Does not cover: that FO follows the two README sentences; a second-reviewer text in a form other than `Second reviewer: <X> because`; the CI step (read from run 38391811132, not rerun); or the replays against all archived records (the 0.21.0-name replays are in the report above, not in this script).

### Summary

PASSED on 63dfff51915b: AC-1 to AC-8 reproduced with a falsifying mutation each, CI green on the head, adr_lint exit 0, no Material finding. The fifth workflow.md sentence and the prefix-of-equal-length compare are accepted; FO should name the fifth sentence to the Captain, and the three Deferred risks stay recorded with their triggers.
