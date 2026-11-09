---
title: A worker holds before work while a special-role call is owed and unrecorded
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:a-worker-holds-while-a-role-call-is-owed:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:a-worker-holds-while-a-role-call-is-owed-backlog-1
              briefing:
                id: briefing:a-worker-holds-while-a-role-call-is-owed:backlog:attempt-1:revision-1
                digest: sha256:deb0f461d712825a818f0fedce964b1b569bea2a906df4bf3b8ce46a876ba2ae
                room-ref: ./a-worker-holds-while-a-role-call-is-owed/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:a-worker-holds-while-a-role-call-is-owed:backlog:1
                briefing: briefing:a-worker-holds-while-a-role-call-is-owed:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-09T14:36:35.693096Z"
                decision: approve
                reason: 'The Captain chose 「進入（建議）」 (host question dialog, 2026-11-09), answering 「第 19 批：這三張（工人開工先查有沒有欠的審查、總工程師改問根本原因、跨畫面資料先寫生命週期）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構思嗎？我建議進入。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: the Captain 「准」 (chat, 2026-11-09, given in both the qnow dev2 FO session and this one), answering the qnow dev2 FO's question 「准不准他們照下面的條件去做？」, which put P1-P3 of /tmp/qnow-case/proposal.md and p1-revised.md (FO scratch, 2026-11-09) with their ship conditions.
- Bite: qnow task owner-vehicle-kept-after-name: 5 repair passes, 3 Material validations and 7 dispatches on one Symptom. Adopted 0.35.0 `role_triggers.py <state> <slug> --rev <state commit>` (run by the qnow dev2 FO, 2026-11-09) already owed a chief-engineer call (3 implementation dispatches on one symptom) and an engineering-reviewer call (replacing amendments 1-6) at state ee29b0a8 before implementation-4, and again at 27f04824 and 03829bf0 before implementations 5 and 6; FO never ran it and recorded neither a call nor a decline.
- Placement: every implementation and validation worker loads its kc-dev-flow-2 stage skill however it was dispatched (a qnow worker dispatched by plain `spacedock dispatch build` ran 0.36.0's dispatch_records.py from its skill). Its first step runs `role_triggers.py` from the adopted package root named on the dispatch's `Package root:` line (or names the version it ran); on exit 1 with no Reviewer line or committed decline for the owed call, or on exit 2, it writes a stage report whose only result is the hold and stops before any code or check. `dispatch_stage.py` refuses the same dispatch earlier. `delivery_gate.py` already holds the merge ask (since 0.35.0) and stays the last backstop.
- A decline line clears the hold only when it carries the reason form of task role-call-asks-for-the-mechanism (why the findings are unrelated).
- Verified 2026-11-09: `spacedock dispatch build --help` exposes no pre-dispatch hook; the adopted README says "An FO that skips this step still dispatches; no runtime hook blocks it."
- Non-goals: changing when role_triggers.py owes a call; a Spacedock change.

## Budget
- One package PR (stage skills implementation and validation, dispatch_stage.py, tests); workflow word budget unchanged unless the design names a raise.

## Stop condition
- Mechanical: on copies of qnow state at ee29b0a8, 27f04824 and 03829bf0 the worker-start check holds; adding a Reviewer line releases it; a decline without the reason form still holds.
- Behaviour replay: an implementation worker on the revised skill, dispatched from plain `spacedock dispatch build` output on the ee29b0a8 copy, stops with the hold report before touching code in 3 of 3 Codex runs; the current 0.36.0 skill on the same copy proceeds (control). Ships only when both pass.
- Results go to the qnow dev2 FO for its Captain report.

## FO alignment

Alignment: not needed; the Captain approved the direction and ship conditions.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
