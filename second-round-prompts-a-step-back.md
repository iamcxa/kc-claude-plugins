---
title: The second round on a task prompts the FO to step back
status: backlog
variant: kc-dev-flow-2
---

When a task's validation fails a second time, or its criteria are relaxed a second time, `role_triggers.py` prints one reminder with three questions, and the FO's idle check surfaces it too.

Source: the Captain, chat 2026-11-02: 「第二輪可以」 to the trigger, then 「可以」 to FO's ask 「把這項加進下一批，和模型設定那張票一起做，可以嗎？」, which named `role_triggers.py` and the idle check.

The three questions, as FO proposed them and he accepted the trigger: is what I am solving still the outcome first asked for; can this gap be tested now, or am I waiting; what breaks if this criterion or process is deleted. At the third round an independent reviewer asks them.

Bite: batch 11, 2026-10-30 to 11-02. On peers-paseo-rule-matches-practice the FO relaxed criteria repeatedly without stepping back until the Captain asked; the standing questions in the global instructions did not fire.

Consumer: every adopter FO, through the delivery check and idle check that already run `role_triggers.py`.
