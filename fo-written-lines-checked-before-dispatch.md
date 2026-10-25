---
title: Three FO-written lines are checked before dispatch and gate, not found by the observer after merge
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:fo-written-lines-checked-before-dispatch:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:fo-written-lines-checked-before-dispatch-backlog-1
              briefing:
                id: briefing:fo-written-lines-checked-before-dispatch:backlog:attempt-1:revision-1
                digest: sha256:6667a4ab51adf17bf65b0f6113bfca69dbe1a538dc9e7a44a6d71c2f9c00e3b4
                room-ref: ./fo-written-lines-checked-before-dispatch/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:fo-written-lines-checked-before-dispatch:backlog:1
                briefing: briefing:fo-written-lines-checked-before-dispatch:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-25T14:15:20.477144Z"
                decision: approve
                reason: Captain 「全准」 (chat, 2026-10-25) answering the batch-6 backlog sitting, which listed this task's backlog briefing-1 question
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: handed over by the kc-adr FO (Paseo session 1bcf070c), 2026-10-25, relaying the Captain's 「開，但是直接轉交給dev2 fo不要開issue」 answering 「要不要開這三個 issue？」 (relayed; no GitHub issues). Filed here as one task; ideation may split it.
- Gap 1, amendment entries carry FO words. README `## Captain amendments`: "FO adds no words of its own"; `Asked:` is verbatim. Seen: `_archive/kc-adr-format-source/observer.md` (FO parenthetical on `Captain:`, half a question with JSON `\"` escapes on `Asked:`, a `Design:` naming a Scope non-goal); `_archive/release-acceptance/observer.md` (FO prose on `Asked:` of Amendments 1 to 3); `_archive/release-walk-picky-reviewers-and-director/observer.md` (Amendment 1 `Design:`). The existing amendment-form check (`design_surfaces.py check`) reads moved criteria and `Supersedes:`, not these lines.
- Gap 2, `Alignment: needed` dispatched with no `Result:` line. README `## Stages` (ideation): "FO records the alignment result as a `Result:` line before dispatching the worker." Seen: `_archive/adr-protected-path-guard/observer.md`, and this batch's `release-review-staleness-held-at-dispatch`, `release-acceptance`, `kc-adr-tools-with-dev2-copy` and `release-walk-picky-reviewers-and-director` observer reports. `dispatch build --stamp` does not refuse; `dispatch_records.py --names` does not read it.
- Gap 3, the delivery gate question lacks "unless he says he merges or holds". README `## Delivery authority`. Seen: `_archive/adr-protected-path-guard/observer.md`. `delivery_gate.py check` requires only the `Sufficiency:` and `Necessity:` clauses, second-reviewer outcomes and bracketed declines (2026-10-25, 0.29.0 `CONFIRMATIONS`); `gate prepare` reads no question text.
- Bite: each was caught only by the observer after merge; about 25 FO record errors this batch (FO count, 2026-10-23 to 2026-10-25); record reliability is the main risk for the autopilot path.
- Upstream first: dev2 scripts `design_surfaces.py` (amendment form, FO alignment), `delivery_gate.py`, `dispatch_records.py`, `role_triggers.py`; Spacedock `dispatch build` and `gate prepare` take no FO-text precondition (0.27.x).
- Non-goals: any other FO-write rule; changing what the README requires.
- Measured 2026-10-25 over the 14 most recent `_archive/*/observer.md` files (`grep -c '^violation'`, then the rule text grouped): 46 violations. By rule: missing `Result:` line before an alignment-needed dispatch 6; FO words in amendment entries 4; `Override:` placed outside the gate resolution reason 5 (two wordings); a ruling bound to a question put after it 3; `role_triggers.py` calls owed and not made before the merge ask 2; approved budget or stop condition not kept in the body 2; one each for eight other rules. The first three gaps above cover 10 of 46; the `Override:` placement and the owed role calls (7 more) are the next candidates for the same kind of check.
- Batch 6 (2026-10-25): the Captain 「可以」 (chat, 2026-10-25), answering 「需要你決定：這份第 6 批的清單可以嗎？」 about FO's batch-6 list, which placed this task first and folded into it override-reaches-gate-and-criteria-wait, override-recorded-when-captain-departs and the stalled ideation task fo-write-checks-parse-top-level (same scripts, `delivery_gate.py` and `design_surfaces.py`); their Scopes are this task's input, read from their own files.

## FO alignment

Alignment: needed before ideation: which checks run where (dispatch, gate, observer) is a design choice the Captain may want to see.
Result: aligned 2026-10-25 on the outcome by the Captain's 「全准」 answering this task's backlog briefing-1 question, which named the four line classes to check; where each check runs (dispatch, gate prepare, delivery_gate.py, observer) is put to him as a decision at the ideation gate. Recorded after the first ideation dispatch, which held for its absence (FO error, the gap this task closes).
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Stage Report: ideation

- FAILED: Design checks for the four FO-written line classes under ## Scope (Result line before an alignment-needed dispatch, FO words in Captain amendment entries, the delivery question's merges-or-holds clause, Override placement in the gate resolution reason), reading the folded tasks from their own files; say where each check runs, what it refuses, and the falsifier; name every file and the evidence each criterion needs
  Held, no design started: `## FO alignment` records `Alignment: needed before ideation` and the task has no `Result:` line (`grep -n Result` on this file hits only Scope lines 35 and 40, which quote the rule). The ideation stage text and `skills/ideation/principles.md` say to stop and report in that case.
- FAILED: A `### Batch overlap` section naming each file the design would change and each other batch or live task
  Not started; depends on the design.
- FAILED: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Not started; depends on the design.
- FAILED: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  Not started; no `## Acceptance criteria` section written.

### Summary

This task was dispatched into ideation while it is itself an instance of Gap 2 (alignment needed, no `Result:` line), so the package rule held the worker. To release it, FO records a `Result:` line under `## FO alignment` (the alignment question is "which checks run where: dispatch, gate prepare, observer"; the Captain's batch-6 「可以」 and backlog 「全准」 are the only recorded words, and neither is a Result). Then FO re-dispatches ideation or messages this worker to continue. No other file was changed.
