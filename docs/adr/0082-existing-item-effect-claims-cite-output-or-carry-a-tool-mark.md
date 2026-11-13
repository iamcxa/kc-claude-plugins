# 0082. Existing-item effect claims cite output or carry a tool mark

Date: 2026-11-12

## Status

Accepted

## Context

The gate-question-facts-are-checked-before-the-captain-reads-them design
extends ADR 0072's automatic disclosure. Its local proof of concept found
four false existing-item sentences among eleven matches in 111 questions;
seven matches were true. The model-reader experiment missed the false
merge-ask claims and flagged true controls. These are the design's measured
results, not a claim that word matching verifies a sentence's truth.

## Decision

**Words:** 「五份都核准（建議）」 — Captain, host question dialog,
2026-11-12, the task's ideation gate, attempt 1.

**Asked (item 2, verbatim):** 「二、問題裡的事實：工具只在「說現有任務或設計會不會受影響」的句子後面自動標上「未對過紀錄」，不擋任何問題；用另一個模型判讀的做法試作證明行不通、不做；這兩天的資料上 11 個標記有 7 個標在真的句子上。」

The bound question recommended approving each design's recommendations.
The accepted design's D1 is the automatic mark without a hold; D2 leaves
the held-task listing to held-and-closed-tasks-leave-the-design-queue.

**Amendment 1 words:** 「四張都允許（建議）」 — Captain, host question
dialog, 2026-11-12. The task's amendment 1 permits this decision-record
file, recording the ideation ruling without adding a decision.

**Options considered:**
- Write the unchecked mark automatically, without a new hold (chosen).
- Hold until FO cites output or adds a mark; rejected in favor of disclosure.
- Use a second model reader; the proof of concept did not support this route.
- Ship a task-state reader here; the accepted design assigns the listing
  to the held-and-closed task instead.

**Recommended:** Automatic marking without a hold, no model reader, and
the held-and-closed task owning the state listing, as the design recommends.

**Protects:**
- `kc-dev-flow-2/scripts/delivery_gate.py` — scope_disclosure writes the mark
- `kc-dev-flow-2/scripts/count_tokens.py` — shared Chinese/English sentence splitting and Chinese count units

The existing delivery check and gate-question commands scan prose for the
design's Chinese and English existing-item effect patterns. A sentence
citing an existing file resolving inside the task folder, or already
marked unverified, needs no added mark. Otherwise the tool writes
「（未對過紀錄）」 into the submitted question or summary. Uncited PR-body
claims are copied with the mark into the ask text, since the tool does not
edit the PR body. Existing failure exits remain; this scan adds no hold.
The existing count disclosure uses the shared sentence split and recognizes
張, 個, 次 and 項. No model or task-state reader is shipped by this task.

## Consequences

A cited file's existence establishes neither its truth nor its relevance.
Word matching misses claims without the selected words and can mark true
claims. Plain dialog questions bypass these commands. A second independent
corpus and whether the mark changes an answer remain unmeasured until
observed; the accepted design does not establish those outcomes.
Startup, idle and archive instructions gain no text. Matching invocations
print the cited/marked totals and a short diagnostic per marked sentence.
