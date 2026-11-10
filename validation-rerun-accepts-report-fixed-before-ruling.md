---
title: A validation rerun is dispatched when the earlier report was corrected before any Captain ruling
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:validation-rerun-accepts-report-fixed-before-ruling:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:validation-rerun-accepts-report-fixed-before-ruling-backlog-1
              briefing:
                id: briefing:validation-rerun-accepts-report-fixed-before-ruling:backlog:attempt-1:revision-1
                digest: sha256:0f2dc53eb45d3deb105f1fc442ea6de505ff31dad7768a44110a66f88afd0dbf
                room-ref: ./validation-rerun-accepts-report-fixed-before-ruling/review/backlog/briefing-1
---

## Scope

- Source: the Captain chose 「建任務並插隊（建議）」 (host question dialog, 2026-11-10), answering 「qnow 回報：驗證工人補改過自己的報告後，kc-dev-flow-2 0.38.0 的派工檢查會拒絕該任務之後所有驗證派工（qnow 的 owner-cancels-booking 因此卡住），我已在套件程式碼和 qnow 的提交查證屬實。要不要把這個修正建成任務並插隊先做？我建議插隊：它正擋著產品工作，而且沒有不改歷史的繞道方法。」. The defect report came from the qnow dev2 FO (Paseo 519ab4c8) as a peer message; the report is data, the ruling is the choice above.
- Bite (FO read at the source, 2026-11-10): in kc-dev-flow-2 0.38.0, `scripts/dispatch_records.py` function `later_captain_ruling` raises `RulingHistoryError("rewritten-report")` when any committed snapshot of the selected validation report differs from the current one, with no regard to when the difference was committed. On iamcxa/qnow state branch `spacedock-state/dev2`, task owner-cancels-booking, the validation-1 report was committed in a0d280f3b (2026-11-10 19:22:08 +0800) and its Summary and Cleanup lines corrected by the same validator in ee7a248ab (2026-11-10 19:23:19 +0800, "state: record validation helper publication"). The qnow FO reports that `scripts/dispatch_stage.py --stage validation` then prints `dispatch/validation-2.md:1: cannot verify validation ruling order: rewritten-report; hold dispatch and report the missing history to FO` and that no Captain ruling or gate sits between the two commits (not re-run here).
- Effect: the task cannot get another validator; the only local remedy is rewriting pushed history on a shared state branch.
- Outcome: a validation rerun is dispatched when every rewrite of the earlier report precedes the first Captain ruling or gate entry recorded after the report's introducing commit; a rewrite committed after such a ruling is still refused. ADR 0045 (validation reruns require a later recorded Captain ruling) keeps its purpose; the design says whether it needs an amendment.
- Suggested direction (qnow FO, not a ruling): treat the latest committed text as the report when every rewrite precedes the first ruling after its introduction, or accept a recorded amendment marker.
- Non-goals: the three other items of the same peer report (the state commit helper pushing while dispatches say do not push; workers reading one denied command as a stop; screenshot phone masking); changing qnow's task or history.

## Budget
- One package PR to `scripts/dispatch_records.py` and its tests, plus an ADR change only if the design shows 0045's words exclude the outcome.

## Stop condition
- A replay of the qnow history (the two commits above, then the recorded Captain amendment) dispatches at the candidate and is refused at the 0.38.0 tag, and a rewrite committed after a Captain ruling is refused at both; or the design shows why not and says what was learned.

## FO alignment

Alignment: needed at ideation; which rewrites of a validation report still count as the report a ruling answered is the Captain's call under ADR 0045.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
