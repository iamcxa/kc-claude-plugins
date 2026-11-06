# 0064. A round-three declined finding becomes a backlog task only with a bite

Date: 2026-11-07

## Status

Accepted

## Context

ADR 0010 made every finding declined from external-review round three its own
backlog task. The task decline-becomes-task-only-with-a-bite records 20 archived
follow-ups: two built after observed failures and 18 closed together, mostly as
already done elsewhere; 11 more remained untouched. This meets 0010's reopen
condition, "these tasks pile up unscheduled". Three batch 12 and 13 observer
reports treated reasoned declines without tasks as violations of that rule.
ADR 0025's bracketed reason remains the committed decline record.

## Decision

**Words:** 「可以，但是該怎樣紀錄合理的followup」 — Captain, chat, 2026-11-05,
answering 「這張擱置，改開「刪掉第三輪婉拒要開待辦」的小任務，好嗎？」.

「核准（建議）」 — Captain, backlog gate, 2026-11-06.

**Asked:** 「決定：第 16 批這五張（跳過的 CI 不擋、Codex 只貼安全摘要時提醒、交付檢查的相對路徑、ADR 編號跨流程預留、婉拒只在出過事時開任務）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？核准即接受「婉拒只在出過事時開任務」任務裡寫的標準（指出真的錯並說得出誰受害、再次出現、或你要求）。要改哪張直接說。」

「核准（建議）」 — Captain, ideation gate, 2026-11-07.

**Asked:** 「決定：「婉拒只在出過事時開任務」這份設計進入實作嗎？核准即接受 D1（另開新 ADR 取代 ADR 0010）與 D2（擱置中的 gate-summary-names-each-decline 恢復時拿掉它的第 3 條）。」

**Options considered:**
- Keep the finding and reason in the gate summary; create or reuse a backlog
  task on an observed failure naming who it hurts, a repeat in a later round
  or task, or a Captain ask (chosen).
- Keep ADR 0010's option E: every round-three decline gets a backlog task.
- ADR 0010's option F: close round-three declines without carrying them anywhere.

**Recommended:** The first option, superseding ADR 0010 (D1), and removing
rule 3 and AC-3 from the held gate-summary-names-each-decline design when it
resumes (D2), as the approved design recommends.

**Protects:**
- `kc-dev-flow-2/scripts/test_sd_dispatch.py` — `ROUND_RULE` and the `follow-up-reason` wording pins.

From round three, a finding that is neither Material nor reviewer P1 starts
no repair cycle. FO records the finding and its bracketed reason in the
committed gate summary. It becomes a backlog task when it meets the chosen
bar; reuse an existing task when one holds it. It never enters an open task's
Scope, and the terminal gate lists each such task. This supersedes ADR 0010
while keeping its no-Scope boundary. The observer judges whether a decline
meets the bar; no prose-quality check is added to delivery_gate.py.

## Consequences

A decline without a bite is found by grepping gate summaries rather than the
backlog board. An observed failure without a task is caught by the observer
at archive, after merge. The workflow reading budget does not rise. Reopen
if a declined finding without a task is later hit and was not caught as a
repeat. Retiring existing follow-up tasks remains outside this decision.
