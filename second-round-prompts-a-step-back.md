---
title: The second round on a task prompts the FO to step back
status: backlog
variant: kc-dev-flow-2
profile: pilot
---

## Scope

- Source: the Captain, chat 2026-11-02: 「第二輪可以」, then 「可以」 to 「把這項加進下一批，和模型設定那張票一起做，可以嗎？」, which named `role_triggers.py` and the idle check. Batch 12 backlog sitting: the Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」.
- Outcome: when a task's validation fails a second time, or its criteria are relaxed a second time, `role_triggers.py` prints one reminder with three questions, and the FO's idle check surfaces it too. The questions: is what I am solving still the outcome first asked for; can this gap be tested now, or am I waiting; what breaks if this criterion or process is deleted. At the third round an independent reviewer asks them.
- Bite: batch 11, 2026-10-30 to 11-02. On peers-paseo-rule-matches-practice the FO relaxed criteria repeatedly without stepping back until the Captain asked; the standing questions in the global instructions did not fire.
- Consumer: every adopter FO, through the delivery check and idle check that already run `role_triggers.py`.
- Upstream first: `scripts/role_triggers.py`, `scripts/pr_watch.py`, `references/sd/mods/kc-dev-flow-2.md`.

## Non-goals

- Grading the FO's answers; a new tool or stage.

## Budget

- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition

- A replay of a task with two failed validations and one with two relaxations each print the reminder at the delivery check and the idle check; a first-round task prints none.

## FO alignment

Alignment: needed before ideation; the scope is the Captain's ruling.
Result: aligned at backlog: Batch 12 backlog sitting: the Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」, approved the outcome and bounds in this file.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
