---
title: A count or measured number names the command and run that produced it
status: backlog
variant: kc-dev-flow-2
---

## Scope

- Outcome: When FO or a worker states a count or a measured number (cells run, tests passed, rounds, tokens), it names the command or run that produced it, so a wrong count is visible as unchecked.
- Source: the Captain, chat 2026-11-04: 「甲」, answering 「決定：來源標註照現狀出貨，K 情境 3/6 記成已知限制，另開一張專門處理數字附出處的追蹤任務，可以嗎？」
- Batch 18 scope: the Captain 「可以」 (chat, 2026-11-09), answering FO's batch 18 recommendation, which listed this task as 「數字要寫明是哪次執行算出來的，順便涵蓋 learn 的證據」.
- Bite: claims-name-their-source AC-8 evidence (state checkout, validation/implementation-2 and implementation-3): with the new written rule, the K scenario (the kc-adr count that said two cells were unmeasured where it was three) labelled the wrong count in 3 of 6 Claude runs, against 0 of 3 before; the P scenario reached 6 of 6. Its K grader false-passed the base, as its validation-1 F1 found.
- Second bite: iamcxa/kc-claude-plugins issue #811 (2026-11-08): a learn evidence line quoted a count from an earlier review pass (18) where a verified recount said 15.
- Consumer: every adopter FO and its workers, at gate summaries, PR bodies and Captain messages.
- Non-goals: re-measuring past counts; a general claim-source rule beyond counts and measured numbers.

## Budget
- One package PR; workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- A count or measured number in a gate summary, PR body or learn evidence that names no command or run is visible as unchecked, with a falsifier.

## FO alignment

Alignment: not needed; the Captain opened it and chose it for batch 18.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
