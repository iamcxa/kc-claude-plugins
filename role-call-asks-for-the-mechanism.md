---
title: The owed chief-engineer call asks for the mechanism, and a decline names why the findings are unrelated
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:role-call-asks-for-the-mechanism:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:role-call-asks-for-the-mechanism-backlog-1
              briefing:
                id: briefing:role-call-asks-for-the-mechanism:backlog:attempt-1:revision-1
                digest: sha256:e647dad0e3c0c1bbc1712782da68f6c307d1a4399261a720e8e6b56dd1652d8f
                room-ref: ./role-call-asks-for-the-mechanism/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:role-call-asks-for-the-mechanism:backlog:1
                briefing: briefing:role-call-asks-for-the-mechanism:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-09T14:36:43.819308Z"
                decision: approve
                reason: 'The Captain chose 「進入（建議）」 (host question dialog, 2026-11-09), answering 「第 19 批：這三張（工人開工先查有沒有欠的審查、總工程師改問根本原因、跨畫面資料先寫生命週期）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構思嗎？我建議進入。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「准」 (chat, 2026-11-09, given in both the qnow dev2 FO session and this one), answering the qnow dev2 FO's question 「准不准他們照下面的條件去做？」, which put P1-P3 of /tmp/qnow-case/proposal.md and p1-revised.md (FO scratch, 2026-11-09) with their ship conditions.
- Bite: qnow task owner-vehicle-kept-after-name: 5 repair passes, 3 Material validations and 7 dispatches on one Symptom. Adopted 0.35.0 `role_triggers.py <state> <slug> --rev <state commit>` (run by the qnow dev2 FO, 2026-11-09) already owed a chief-engineer call (3 implementation dispatches on one symptom) and an engineering-reviewer call (replacing amendments 1-6) at state ee29b0a8 before implementation-4, and again at 27f04824 and 03829bf0 before implementations 5 and 6; FO never ran it and recorded neither a call nor a decline. The step-back question FO answered four times was "is what I am solving still the outcome first asked for"; it answered yes each time while validation-1 F2 and validation-2 F6 both pointed at one screen, so the outcome question did not surface the shared cause (a missing attempt identity).
- Change: the chief-engineer question for a repeated-symptom or repeated-validation call asks "what single mechanism produces these findings, and what one change closes that class?"; a decline line must say why the findings are unrelated, or it does not clear the owed call.
- Related: task step-back-answer-has-a-record-line (held at ideation 2026-11-05; its non-goal "changing the three questions" is unchanged by this task, which changes the chief-engineer call's question and the decline form only); task a-worker-holds-while-a-role-call-is-owed reads the decline form.
- Non-goals: when calls are owed; the step-back three questions.

## Budget
- One package PR; workflow word budget unchanged unless the design names a raise.

## Stop condition
- Behaviour replay on qnow validation-2's records: a chief-engineer asked the current question and one asked the mechanism question, 3 runs each; count runs whose answer names the missing attempt identity. Ships only if the mechanism question beats the current wording; otherwise this task closes with the table.
- The four recorded step-back answers fail the new decline form (mechanical).
- Results go to the qnow dev2 FO for its Captain report.

## FO alignment

Alignment: not needed; the Captain approved the direction and ship condition.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
