# 0073. A Captain gate record quotes its bound question before it is written

Date: 2026-11-10

## Status

Accepted

## Context

Issue #815 reported eleven of twelve Captain resolutions on four relay tasks
without the complete bound question. ADR 0062 D2 left backlog and ideation
mismatches report-only. The existing declaration check already runs before FO
writes a Captain record, where a correction is still possible.

## Decision

**Words:** 「核准（建議）」 — Captain, ideation gate attempt 1 of
issue-815-fo-record-gaps, 2026-11-10.

**Asked:** 「決定：第 20 批四張設計照下列建議進實作嗎？建議核准。(1) 關卡理由沒引用關卡問題：待辦、構想、驗證三種關卡都擋下，不再只是回報；這改掉 ADR 0062 只回報的做法，所以會寫一份新的決策紀錄，README 多 2 個字。(2) 特別角色派工紀錄：由腳本寫好、檢查、提交後才交給審查者；模型低於 opus 或 astra 就拒絕派；README 多 6 個字；完全手動、沒有紀錄的審查不在這張處理。(3) 修改驗收條件的檢查：做成第四條狀態規則，每次推送狀態後檢查，所以壞的提交要推上去後才會被標出；dev2 要真的用到它，得把狀態規則釘選的版本從 0.26.0 改到新版，那一步之後另外問你，這張要等一次推送印出這條規則的結果才收。(4) PR 說明的署名連結：只放行 Claude Code 自動加在最後的那一行署名，其他連結照樣要記成步驟。核准即接受上列每一項建議，包括 README 合計多 8 個字（5931 到 5939）；要改哪項直接說。」

**Options considered:**
- Hold unquoted Captain reasons before recording at backlog, ideation and
  validation, with two more workflow README words (chosen).
- Hold validation reasons alone; leave backlog and ideation report-only.
- Retain ADR 0062 D2 without the new check.

**Recommended:** Hold at every gate, with the two README words and this ADR,
as accepted by the Captain's ideation gate answer.

**Protects:**
- `kc-dev-flow-2/scripts/decision_ledger.py` — `check_reason` before its pass line

This replaces ADR 0062 D2's report-only treatment for Captain records only.
Before `gate record --actor person:captain`, FO runs `decision_ledger.py --reason
<file> --task <task>`. The declaration check also requires the reason to contain
`answering 「<bound question>」`, ignoring whitespace, using the single unresolved,
non-withdrawn attempt's briefing. Missing or ambiguous state holds with exit 2;
a missing quote holds with exit 1. A different question requires withdrawal,
preparation with the question answered, and asking the Captain again.

ADR 0062's `ASK_UNQUOTED` merge-grant rule and after-archive observer remain.
FO-delegated records are outside this check. The workflow README budget rises
by two words, read at startup, resume and before each Captain record.

## Consequences

A typo now stops a record while it can still be repaired. A shorter chat ask
can cost a withdrawal and another question. This comparison proves recorded
strings, not what the Captain read, and FO can skip the command. Reopen if the
open-attempt lookup cannot identify the question the Captain answered.
