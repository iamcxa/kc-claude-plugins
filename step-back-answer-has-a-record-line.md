---
title: The step-back answer has a fixed record line, and the reminder stops once it is written
variant: kc-dev-flow-2
status: backlog
---

When `role_triggers.py` prints the step-back reminder for a task, FO writes its answers to the three questions on one fixed line in the task, and `role_triggers.py` stops printing the reminder for that round once the line is there.

Source: the Captain, chat 2026-11-05: 「開」, answering 「要開這張改過的第 2 張嗎？我建議開。」, whose proposal read 「給這三題的答案一個固定欄位，寫了之後腳本就不再提醒，觀察員也能核對。」 It applies his step-back rule of 2026-11-02 (a second failed validation or second relaxation stops work until three questions are answered).

Bite: observer reports across every archived task carry 7 violations under the `role_triggers.py` rule (3 in the 12 tasks of batches 12 and 13; grep over `_archive/*/observer.md`, 2026-11-05). For claims-name-their-source, fo-answers-own-worker-permissions-by-listed-id and release-walk-due-trigger, `role_triggers.py <state> <slug> --rev <archive commit>~1` exits 0 and prints only the advisory step-back `next:` line (the `STEP_BACK` text); `delivery_gate.py` forwards exit-0 lines without holding, by design. kc-dev-flow-2 0.35.0 names no place for the answer and no reader checks one, so the reminder repeats and the observer counts each printing as a violation whether or not FO answered.

Consumer: every adopter FO at a second validation round or second relaxation, and the observer, which reads the line to tell an answered step-back from an ignored one.
