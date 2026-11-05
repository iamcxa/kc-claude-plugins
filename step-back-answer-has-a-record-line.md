---
title: The step-back answer has a fixed record line, and the reminder stops once it is written
variant: kc-dev-flow-2
status: ideation
profile: pilot
merge: pr
gates:
    version: 1
    records:
        - id: gate:step-back-answer-has-a-record-line:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:step-back-answer-has-a-record-line-backlog-1
              briefing:
                id: briefing:step-back-answer-has-a-record-line:backlog:attempt-1:revision-1
                digest: sha256:ec5681ebf0f86939bc3531f916dee2f7fbfe35519d450ab5f0ffb9700098a049
                room-ref: ./step-back-answer-has-a-record-line/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:step-back-answer-has-a-record-line:backlog:1
                briefing: briefing:step-back-answer-has-a-record-line:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-05T09:12:42.508999Z"
                decision: approve
                reason: The Captain 「准」 (chat, 2026-11-05), answering 「決定：這批五張（派工交代句的檢查、退一步答案欄位、漏寫 Override、婉拒要寫明、閘門一次問一件事）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構思嗎？其中「婉拒要寫明」照我提的三項範圍（沒寫 Declined 標籤的婉拒、沒有 F 條目的審查者、沒指明接手任務）。要改哪張直接說。」; accepts the outcome, scope, budget and stop condition in this file, Pilot.
              application:
                target-stage: ideation
                state: consumed
---

When `role_triggers.py` prints the step-back reminder for a task, FO writes its answers to the three questions on one fixed line in the task, and `role_triggers.py` stops printing the reminder for that round once the line is there.

Source: the Captain, chat 2026-11-05: 「開」, answering 「要開這張改過的第 2 張嗎？我建議開。」, whose proposal read 「給這三題的答案一個固定欄位，寫了之後腳本就不再提醒，觀察員也能核對。」 It applies his step-back rule of 2026-11-02 (a second failed validation or second relaxation stops work until three questions are answered).

Bite: observer reports across every archived task carry 7 violations under the `role_triggers.py` rule (3 in the 12 tasks of batches 12 and 13; grep over `_archive/*/observer.md`, 2026-11-05). For claims-name-their-source, fo-answers-own-worker-permissions-by-listed-id and release-walk-due-trigger, `role_triggers.py <state> <slug> --rev <archive commit>~1` exits 0 and prints only the advisory step-back `next:` line (the `STEP_BACK` text); `delivery_gate.py` forwards exit-0 lines without holding, by design. kc-dev-flow-2 0.35.0 names no place for the answer and no reader checks one, so the reminder repeats and the observer counts each printing as a violation whether or not FO answered.

Consumer: every adopter FO at a second validation round or second relaxation, and the observer, which reads the line to tell an answered step-back from an ignored one.

## Scope

- Upstream first: `role_triggers.py` (`STEP_BACK`, exit-0 advisory `next:` line) and `delivery_gate.py`, which forwards that line without holding; the observer, which reports each printed `next:` line.
- Non-goals: changing when the reminder fires or the three questions themselves.
- Batch 14: the Captain 「可以」 (chat, 2026-11-05), answering 「這 5 張當下一批，可以嗎？」, which named this task.

## Budget
- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- `role_triggers.py` keeps printing the step-back reminder for a round until the task carries that round's answer line, then stops; replays of the three batch 12 and 13 tasks without the line still print it, with the line do not, and the observer can tell the two apart.

## FO alignment

Alignment: needed at ideation; the line records his 2026-11-02 rule, so its form is his to accept.
Result: aligned at backlog: Batch 14 backlog sitting, the Captain 「准」 (chat, 2026-11-05), answering 「決定：這批五張（派工交代句的檢查、退一步答案欄位、漏寫 Override、婉拒要寫明、閘門一次問一件事）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構思嗎？其中「婉拒要寫明」照我提的三項範圍（沒寫 Declined 標籤的婉拒、沒有 F 條目的審查者、沒指明接手任務）。要改哪張直接說。」, approved the outcome and bounds in this file.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
