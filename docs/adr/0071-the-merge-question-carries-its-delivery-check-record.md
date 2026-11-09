# 0071. The merge question carries its delivery check record

Date: 2026-11-09

## Status

Accepted

## Context

The delivery-check-before-ask-is-provable task records five batch 17 observer
results of `can't tell`: their merge records postdated their briefing commits.
A self-reported time cannot establish that the check preceded preparation.
ADR 0051 reopens when its nearest-moment check no longer covers the observed
sequence. Spacedock already fingerprints committed `--reference` files in a
briefing; this change uses that existing seam.

## Decision

**Words:** 「核准（建議）」 — Captain, host question dialog, 2026-11-09,
ideation gate of delivery-check-before-ask-is-provable.

**Asked:** 「決定：第 18 批四張設計照下列建議進實作嗎？建議核准。(1) 驗證回答能不能合併：Claude 和 Codex 兩邊都要跑，Codex 跑不了就停下來回報，不接受只有 Claude 的結果；這次不寫決策紀錄，等第 19 批觀察者的數字出來再定。(2) 合併檢查誤判：只在引用的文件裡，把 shell 或沒標語言的程式區塊算成你要跑的步驟；問題和報告裡的區塊照舊全算。(3) 檢查跑在提問前：沒有對應的檢查紀錄就不讓準備問題，所以 PR 要先 ready、CI 綠才能開驗證關卡。(4) 數字寫明出處：learn 提案完成時，證據裡的數字在它引用的資料找不到就擋下；摘要裡的「未查核的數字：N」改由工具自己寫進去，不擋、也不用我抄（工人原案是擋到我抄上那一行）。核准即接受上列每一項建議，包括 (4) 改成工具自己寫；要改哪項直接說。」

**Options considered:**
- Hold a merge-naming `question` without a matching newest delivery check
  record, then bind that record into the briefing (chosen).
- Warn without holding; absence of the check is found only at archive.
- Compare timestamps alone; these do not bind the checked text into the briefing.

**Recommended:** The hold, including requiring a ready, green PR before
validation preparation, as item (3) of the approved question states.

**Protects:**
- `kc-dev-flow-2/scripts/delivery_gate.py` — `matching_delivery_record` and the `question` hold

When the supplied gate text names `--match-head-commit`, `question` requires
its newest `merge/ask-N.json` to match a latest dispatched Candidate, the
named merge head and the cleaned Sufficiency and Necessity clauses, each cut
at 200 characters. It prints the record path; FO state-commits it and passes
it to `gate prepare --reference`. The observer compares the bound digest,
head and clauses, and retains the time fallback for pre-rule briefings.

## Consequences

This amends ADR 0051's consequence that binding before the check is not
refused: `question` now holds preparation without the matching record.
ADR 0051's decision requiring the external round count at `check` stands.
ADR 0023's merge authority and ADR 0062's quoted-question grant are unchanged.

CI must finish and the PR must be ready before the validation sitting can be
prepared. The workflow README and its word budget are unchanged in size;
`question` adds the reference instruction only on a passing merge question.
Skipping `--reference` is detected by the observer, not by a new prepare hook.
A question naming no merge remains outside this check, and equal truncated
clauses do not prove that the entire briefing was checked. Reopen if these
limits leave another observed ordering gap.
