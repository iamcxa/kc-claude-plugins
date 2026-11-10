# 0074. Special-role calls are built by the stage dispatch script

Date: 2026-11-10

## Status

Accepted

## Context

The batch 17 observer found an engineering-reviewer record written by hand
without its required parts. The existing dispatch-record checker rejected it,
but ran after the reviewer had started. ADR 0070 covers stage-worker dispatches;
Spacedock 0.27.2 has no special-role dispatch builder. The package's
`dispatch_stage.py` already owns record writing, validation and retry selection.

## Decision

**Words:** 「核准（建議）」 — Captain, host question dialog, 2026-11-10,
answering the batch 20 ideation question, whose role-record recommendation was
「(2) 特別角色派工紀錄：由腳本寫好、檢查、提交後才交給審查者；模型低於 opus 或 astra 就拒絕派；README 多 6 個字；完全手動、沒有紀錄的審查不在這張處理。」
and whose acceptance clause was
「核准即接受上列每一項建議，包括 README 合計多 8 個字（5931 到 5939）；要改哪項直接說。」.
Source: `special-role-dispatch-records-built-by-script` ideation gate,
attempt 1, recorded at 2026-11-10T06:06:50.540718Z on `spacedock-state/dev2`.

**Options considered:**
- D1: add six README words directing FO to `dispatch_stage.py --role <agent>`
  (chosen); leaving the instruction in CLI help retains the manual-writing gap.
- D2: reject supplied models below the opus floor, using `role_triggers.rank`
  (chosen); accepting any model can start a reviewer below the approved table.
- D3: leave calls made by hand without a dispatch record outside this task
  (chosen); joining every Reviewer line to a local record would affect batch-wide
  calls and ADR 0026's date-based clearing rule.

**Recommended:** D1 yes, D2 yes, D3 not in this task, as accepted at the gate.

**Protects:**
- `kc-dev-flow-2/scripts/dispatch_stage.py` — `main`, the role branch

For chief-engineer and engineering-reviewer calls, `--role` writes the record
from FO-supplied checklist and scope notes, checks the model floor and the two
record checks, then runs `spacedock state commit`. The role branch returns the
record as the prompt after a successful commit; on commit failure it retains the
record for reconciliation and withholds stdout. It skips stage building and the
pending-role hold, since this call supplies the requested role review.

Model and roster remain FO-supplied, as ADR 0070 requires. That record's stage
scope and manual follow-up rule stay in force. The supplied-model check follows
ADR 0049's ranking, without resolving a model or changing ADR 0026's clearing
rule. The README budget rises by six words at startup and resume and at the role
call; the other two words in the approved joint raise belong to the gate-reason
task.

## Consequences

Package-built role records are checked and committed before FO receives the
prompt. Direct manual calls without any record and live-reviewer follow-ups
remain outside this writer. Unknown model families are refused until the rank
table recognizes them. The opus floor does not enforce the higher prod/database
engineering-reviewer requirement; `role_triggers.py` still checks that task fact
at the next gate. FO commits task edits before building the role prompt, then
records the Reviewer line after the call. A batch review uses the first named
task's record, with the other task lines referring to it.
