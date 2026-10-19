---
title: The Number guards passage of the workflow README shrinks to what number_guards.py cannot tell its reader
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:number-guards-readme-shrink:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:number-guards-readme-shrink-backlog-1
              briefing:
                id: briefing:number-guards-readme-shrink:backlog:attempt-1:revision-1
                digest: sha256:12b30dc0c3e9ea1e4d878894053b72844eea50863fc36c9673d6876daef9ffcd
                room-ref: ./number-guards-readme-shrink/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:number-guards-readme-shrink:backlog:1
                briefing: briefing:number-guards-readme-shrink:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-18T16:57:03.744159Z"
                decision: approve
                reason: Captain approved in chat (「批准這些作為第三批」) the five batch-3 backlog gates presented together, accepting the recommended profiles and the stated grouping and order
              application:
                target-stage: ideation
                state: consumed
        - id: gate:number-guards-readme-shrink:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:number-guards-readme-shrink-ideation-1
              briefing:
                id: briefing:number-guards-readme-shrink:ideation:attempt-1:revision-1
                digest: sha256:c75f5b551e751353fa195a470d3e206272d960afb292c5033db6822034378105
                room-ref: ./number-guards-readme-shrink/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:number-guards-readme-shrink:ideation:1
                briefing: briefing:number-guards-readme-shrink:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-19T00:43:58.011424Z"
                decision: approve
                reason: Captain approved in chat (「照建議」) the four batch-3 ideation gates presented together, accepting each task's stated decisions and FO's implementation order
              application:
                target-stage: implementation
                state: pending
started: 2026-10-18T16:57:47Z
---

Filed under D4 of workflow-budget-ratchet, approved by the Captain on 2026-10-17 (「那就照建議」 to the batch-2 ideation gates, whose question said approving accepts D4: "Number guards becomes a follow-up task").

## Scope

- Measured by workflow-budget-ratchet's ideation on 0.24.0: the Number guards passage of `kc-dev-flow-2/references/sd/workflow.md` is 745 words, 13.6% of the README, the largest single candidate for the ratchet's shrink rule; its script messages were not read there.
- Apply the ratchet's rule: read each `kc-dev-flow-2/scripts/number_guards.py` failure message first; a rule the script enforces and whose message tells the reader what to do shrinks to one pointer sentence; the budget falls by the words removed in the same change.
- Bite to confirm at ideation: the observer's count of number-guard violations (an ADR number reserved after the first implementation dispatch happened twice, on prod-security-review-gates 2026-10-16/17).

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it as a follow-up of workflow-budget-ratchet D4.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

## Design

### PRFAQ

**Press release.** The Number guards passage of the workflow README loses 55 of its 745 words (README 5429 to 5374), and the three clauses it loses are the three that `number_guards.py` already prints with the next step. Every clause the script cannot say stays, each pinned by a test, so the cut cannot silently drop a rule.

**FAQ**

- *Why only 55 words, when the backlog item called this the largest candidate?* The passage is the largest, but 690 of its 745 words say what the script cannot: when to run it, what FO records, the `Applied:`/`Not applied:` vocabulary the script never reads, the POC marker and the collision procedure. Measured clause by clause below.
- *Why not cut Reserve or Collision?* The script prints no reserve timing, no scope-notes rule and no renumber step. `R3`/`R5` print only `base already has NNNN (name)`. Cutting them would repeat the 15-word loss that Codex found on #658 (learning.md, "Compare a shrunk rule with what its script rejects before cutting it").
- *Does the cut change what FO or a worker does?* No script changes. A reader who now meets a failure reads the script's line, which carries the same instruction.
- *What about the ADR line missing from implementation scope notes?* A README cut cannot fix it, because nothing checks it. See "ADR-line miss" below; the check belongs to `fo-write-checks`, and this task leaves the Reserve bullet untouched.
- *What does the Captain see?* Nothing (`Visible change: none`).

```mermaid
flowchart TD
    A[Reader meets a Number guards rule] --> B{Does number_guards.py print\nthe fact AND the next step?}
    B -- yes: R2 edit/rename/delete, R6, flags and R1-R6 via --help, no-base --> C[README keeps one pointer clause\nbudget step lowered by the words cut]
    B -- fact only: R3/R5, 'guard skipped' + PASS, wrong adr-path passes --> D[README keeps the clause\npinned by a need string]
    B -- script never sees it: Reserve timing, scope notes, Applied: none, Not applied, boundary-crossed marker, reserves no number --> D
    C --> E[lint-skills.py: count must equal START plus deltas, so the cut step is required]
    D --> E
    E --> F[recount words per moment, base vs candidate, independent script]
    F --> G{any moment above base?}
    G -- yes --> H[stop: restore the clause]
    G -- no --> I[validation, PR, Captain merge]
```

### Existing-code check

Chain, in order. Spacedock: ADR 0002 (2026-09-30) records that it has no migration or number concept; not re-read against the installed 0.27.0. kc-dev-flow-2 at origin/main (0.25.0): `number_guards.py` (232 lines) and the budget ratchet in `lint-skills.py` already exist and are all this task uses; ADR 0020 owns the rule that a cut lowers the budget in the same change. Adopters (relay, qnow, ss-web): not read; they receive this README by workflow sync, so there is nothing to build there. Nothing new is added: three README clauses go, one budget step is added, test pins are added.

### Measured, 2026-10-19 (origin/main c60e89e1; the cached 0.25.0 `number_guards.py` and `dispatch_records.py` are byte-identical to origin/main)

Each failure message was run on a throwaway fixture repository (`/tmp/ng-fixture`, outside this repository). Clause by clause:

| README clause (words) | What the script printed | Disposition |
|---|---|---|
| Config paragraph: reads `trunk:`, optional `migrations-path:`, `adr-path:`, task section; `--help` lists flags (39) | no base: `number_guards: no base: pass --base, or --workflow-dir whose README declares trunk:` exit 2. Surfaces db without path: `...pass --migrations-path or set migrations-path: in the workflow README` exit 2. `--help` prints R1 to R6, the reserve rule, Limits and the `## Number guards` section | Shrink to 22 words. Keep `adr-path:` default `docs/adr`: with a wrong `--adr-path`, a duplicate ADR number passed (`PASS: no findings`, exit 0), so the script cannot tell it |
| Applied, first sentence: frozen, edit, delete and renumber fail `check` (19) | edit: `FAIL R2: db/0003_c.sql: M since 6dfbc3891545, applied at uat; revert it and add a new migration`; rename and delete: the same with `D` | Shrink to `check` freezes it (R2). Keep the rest of the bullet: the script reads only `Applied at:`; it ignores `Applied: none` and `Not applied:` and never reports a missing record |
| POC: "When the README declares `migrations-path:`, `check` runs for it at the same three points, and exit 1 `FAIL R6` lists each path ..." (about 30) | `FAIL R6: db/0003_new.sql: A under the migrations directory; a POC task changes none of it`, exit 1 | Cut. The Check bullet already gives the three points. Keep `FAIL R6` as the trigger, the `boundary-crossed: persistent-state` marker and "not repaired in place": the R6 line prints neither (ADR 0002 amendment, Captain 「可以」) |
| POC: "reserves no number" | `reserve --kind migration` on a `profile: poc` task prints `Migration: 0003`, exit 0; `--kind adr` prints `ADR: 0002` | Keep; the script lets it through |
| POC marker: "Without `migrations-path:` the migration rules are skipped ..." | `migration guard skipped: no migrations-path declared`, then `PASS: no findings`, exit 0 | Keep: the message gives the fact and then PASS, not a next step |
| Applies-when, Check (three points, exit 2 is a hold), Reserve, Applied (FO step), Collision | Reserve: nothing reads timing or scope notes. Check: exit 2 prints only the message. Collision: R3/R5 print `base already has NNNN (name)` | Keep, unchanged |

Candidate text (simulation in `/tmp/ng-after.md`, base copy `/tmp/ng-workflow.md`; not in the repository): C1 `` `python3 <package>/scripts/number_guards.py --help` lists the flags and rules R1 to R6; `trunk:`, `migrations-path:` and `adr-path:` (default `docs/adr`) come from this README's frontmatter. ``; C2 `` - **Applied.** `check` freezes a migration in a commit recorded `Applied at:` (R2). ``; C3 drops the one POC sentence and keeps the rest with its line breaks (the `test_poc_readme.py` pin matches `not repaired in` + newline + two spaces + `place`).

Simulated at the candidate (copy of origin/main in `/tmp/ng-tree`): README 5374 words; `lint-skills.py` prints `5374 words is 55 under the budget of 5429; add a cut step of -55 with a 'why' to WORKFLOW_BUDGET_STEPS`; `test_number_guards.py` 23 tests OK; `test_sd_dispatch.py` PASS; `test_poc_readme.py` fails once, on the `migrations-path:` pin, as designed (it passes at base).

### Words FO reads at each moment (base vs candidate)

Counted with `len(text.split())` over the passage text and the script lines named; the implementation recounts with an independent copy. Script output is unchanged by this design, so each script line counts the same on both sides.

| Moment | What is read | Base | Candidate |
|---|---|---|---|
| FO startup or resume | whole Number guards and FO-steps passage | 745 | 690 |
| FO builds an implementation dispatch | opening, config paragraph, Reserve bullet, `reserve` line (2) | 172 | 155 |
| Implementation worker starts | Number guards section (context-section) | 277 | 222 |
| Validation worker starts | the same section | 277 | 222 |
| `check` prints R6 | POC bullet plus the R6 line (15) | 94 | 64 |
| `check` prints R2 | Applied bullet plus the R2 line (16) | 84 | 76 |
| Merge ask (`check` on the PR head) | Check bullet | 44 | 44 |
| Collision | Collision bullet | 200 | 200 |
| Idle on an open PR, idle on a merged PR, after archive | not read: `git grep` for `number_guards` and `Number guards` in `references/sd/mods` and `extensions` at origin/main finds none | 0 | 0 |

The learning's "each moment below its base" cannot hold for the two moments whose clauses the script cannot say; the criterion below reads "no moment above its base, every moment with a cut below".

### ADR-line miss

The Reserve bullet says FO "repeats the lines as dispatch scope notes". Nothing checks it: `dispatch_records.py` on a record with no `ADR: 0002` while the task holds one prints `1 dispatch record(s) complete`, exit 0 (fixture `/tmp/ng-fixture/st`), and `laws_check.py`, `delivery_gate.py` and `observer_check.py` contain no `ADR` or `Number guards` check (`grep`, 2026-10-19).

Measured over the archived tasks (`_archive/*.md` plus `dispatch/implementation-*.md`, literal `ADR: NNNN` in the Scope notes): 18 tasks hold a reserved line, 11 of them have implementation records, **8 of those 11 lack the line in implementation-1** and 3 lack it in every record. Observer reports name 6: three where the number was reserved after the first dispatch (dev2-laws-check, amendment-form-check, prod-security-review-gates, all 2026-10-17 12:18 to 12:20) and three where the task held it before dispatch but the scope notes never carried it (prod-security-validation-gate, workflow-budget-ratchet, ui-design-review-in-ideation). Two more (fo-lifecycle-mod, journey-map-dev2-contract) have no number in implementation-1 at all and were not named. The backlog text said the reserve-after-dispatch happened twice; the observer reports show three, plus the omissions. The rule dates from 2026-09-30 (#533), before all of these.

Words in the README did not prevent it: the clause was present in each case. This is an enforcement gap. The check this task hands to `fo-write-checks` (its Scope already lists the miss): at dispatch write, the new `implementation-N` record's scope notes must hold every `Migration:`/`ADR:` line the task's `## Number guards` holds at that moment; a miss prints `implementation-1.md: scope notes lack 'ADR: 0020' held by the task's Number guards; copy it into the scope notes`. Limit: it catches the three omissions; it cannot catch a number reserved after the dispatch, because the file shows no line at that time. Only after such a check exists can the Reserve clause shrink, as a later step by that task.

### Batch overlap

Files this design would change: `kc-dev-flow-2/references/sd/workflow.md` (Number guards section: config paragraph, Applied first sentence, POC bullet); `kc-dev-flow-2/scripts/lint-skills.py` (one `WORKFLOW_BUDGET_STEPS` cut step); `kc-dev-flow-2/scripts/test_poc_readme.py` (pin); `kc-dev-flow-2/scripts/test_number_guards.py` (message pins). `number_guards.py` is not changed.

| Other batch-3 task | Same file or check | Effect on order |
|---|---|---|
| fo-write-checks | `workflow.md` (its Reserve and observer-class lines, a different hunk from mine); `lint-skills.py` budget steps (same list); owns the ADR-line check in `dispatch_records.py` and `test_dispatch_records.py` | No hunk conflict in `workflow.md`; the step list conflicts and the later PR recounts (ADR 0020). Its Reserve cut waits for its own check. |
| chat-only-evidence-observer-blind | `workflow.md` (validation, Delivery authority, Decision records), possibly a raise step in `lint-skills.py`; `observer_check.py`/observer agent | Step list and README count only |
| captain-question-load | `workflow.md` (gate and Delivery authority lines), possible budget step | Step list and README count only |
| this task | as above | |

Not read yet: the three siblings' designs (not yet written when this was read, 2026-10-19), so their file lists come from their Scope text. Recommended order: this task first. It is a pure cut with no dependency, and the siblings then recount from 5374. If a sibling lands first, this task recounts and keeps a cut of the same 55 words.

## Acceptance criteria

- **AC-1** The Number guards passage is at most 690 words and the README count equals `WORKFLOW_BUDGET_START` plus every step, with one new step whose `delta` is minus the words removed (-55 for the candidate text above). Evidence: `python3 -B kc-dev-flow-2/scripts/lint-skills.py` at the candidate prints `5374 of 5374 words`. Falsifier: with the step left out it prints `55 under the budget of 5429` (reproduced in `/tmp/ng-tree`).
- **AC-2** Each cut clause points at output the script really prints. Evidence: at the candidate, the fixture commands in the table above give the same lines: R2 for an edit, a rename and a delete, R6 for a `poc` task, the no-base and no-migrations-path messages, and `--help` listing R1 to R6; the stage report names each command and exit code. Falsifier: a message that no longer carries its next step (for R2, `revert it and add a new migration`) makes the pointer false.
- **AC-3** The message words the README now relies on are pinned in `test_number_guards.py`: the R2 tail, the R6 tail `a POC task changes none of it`, and `--help` naming R1 to R6. Evidence: `python3 -B kc-dev-flow-2/scripts/test_number_guards.py` passes; changing each message tail alone makes exactly one test fail (currently none of the three is pinned: grep of the file at base finds only `migration guard skipped`).
- **AC-4** Every kept clause the script lets through is pinned. `test_poc_readme.py` asserts `FAIL R6`, `boundary-crossed: persistent-state`, `not repaired in\n  place` and `reserves no number` in the derived POC bullet; one pin holds `(default `docs/adr`)`. Evidence: tests pass at the candidate; deleting each phrase alone fails its pin. Falsifier: at base the `migrations-path:` pin fails once the clause is cut, which is why that pin is replaced, not kept.
- **AC-5** No moment is above its base and each moment with a cut is below, by the table above (745 to 690, 172 to 155, 277 to 222 twice, 94 to 64, 84 to 76; 44 and 200 equal). Evidence: a recount script that is not the one used here, run on the base and candidate commits, printed in the stage report. Falsifier: any moment above base, or a moment missing from the table.
- **AC-6** The Reserve bullet is byte-identical at base and candidate, and `number_guards.py` is unchanged. Evidence: `git diff <base> <candidate> -- kc-dev-flow-2/scripts/number_guards.py` is empty and the `workflow.md` diff has no hunk inside the Reserve bullet. Falsifier: a hunk in either.
- **AC-7** The ADR-line check specification above is carried to `fo-write-checks` by FO, with the measured 8 of 11. Evidence: the `fo-write-checks` task file cites it or records why not. Not verifiable here until that task designs; stated honestly as not yet verified.
- **AC-8** Retained documents: implementation runs `python3 <package>/scripts/doc_impact.py <base> <candidate>` and records `updated` or `unaffected: <reason>` per listed document; the derived POC README (`poc_readme.py check`) is regenerated where the adopted copy is kept. Falsifier: a listed document with no entry.

## Unresolved decisions

- **D1: build a 55-word task at all?** Recommend yes. It is a small cut (README 1.0%, passage 7.4%), the rule it applies is ADR 0020's direction, and the pins it adds make later cuts of this passage safe. Gets worse: the README stays about 5374 words, and the largest remaining lever, the roughly 200-word Collision bullet, stays. Moving Collision to an on-demand home needs a loading trigger that the script's R3/R5 lines do not give, so it is a separate design, not part of this one. Alternative: close this task and fold the three cuts into `fo-write-checks` so one README edit carries both; that couples two gates.
- **D2: who owns the ADR-line check?** Recommend `fo-write-checks` (dispatch write time, `dispatch_records.py`), not `number_guards.py`. Gets worse: until it lands the miss continues (8 of 11 implementation-1 records at base), and the Reserve clause cannot shrink.

## Stage Report: ideation

- DONE: A design (PRFAQ and Mermaid) for the Number guards passage of kc-dev-flow-2/references/sd/workflow.md shrunk under the budget ratchet's rule (read each kc-dev-flow-2/scripts/number_guards.py failure message first; shrink only what the script enforces and whose message tells the reader what to do; lower the budget step), with the words FO reads at each moment before and after, and a check on the ADR-line-in-scope-notes miss this passage covers
  `## Design`: every message run on a fixture; three clauses cut (-55 words, 745 to 690, budget step -55); the miss measured at 8 of 11 tasks with implementation records and shown unchecked (`dispatch_records.py` exit 0).
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch-3 task (fo-write-checks, chat-only-evidence-observer-blind, captain-question-load, number-guards-readme-shrink) that changes the same file or check, so FO can order implementation
  `### Batch overlap` names four files and the three siblings; siblings had no design yet, so their files come from Scope text.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each moment`: nine moments, none above base; two unchanged moments stated as equal, not below.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  `## Acceptance criteria` AC-1 to AC-8, `## Unresolved decisions` D1, D2.
- DONE: `design_surfaces.py check` on the task
  `number-guards-readme-shrink.md: design surfaces presentable`, exit 0.
- DONE: AC-1 evidence now
  Simulated at the candidate in `/tmp/ng-tree`: lint prints `5374 words is 55 under the budget of 5429`, which the cut step resolves; not yet run in the repository.
- DONE: AC-2 evidence now
  R2 (edit, rename, delete), R6, no-base, no-migrations-path and `--help` output captured on `/tmp/ng-fixture` with the 0.25.0 script, byte-identical to origin/main.
- SKIPPED: AC-3 pins, AC-4 pins, AC-5 recount, AC-6 diff, AC-7 handoff, AC-8 doc_impact
  Implementation-time proofs, not yet verified; AC-4's replaced pin is shown failing at the candidate (`test_poc_readme.py`, one failure) and passing at base.

### Summary

The Number guards passage can lose only 55 of 745 words, because the script prints the next step for three clauses only; the rest it cannot say, and three of those were shown by running the script (reserve on a POC task, a wrong `adr-path`, the `PASS` after `guard skipped`). The bigger finding is that the ADR-line miss is unenforced (8 of 11 implementation-1 records lack the line), so it goes to `fo-write-checks` as a check, not to a README edit. Decisions for the Captain: whether a 55-word task is worth building (D1) and who owns the check (D2).
