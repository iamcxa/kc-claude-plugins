# 0076. A journey workflow's new seed records its story or none

Date: 2026-11-11

## Status

Accepted

## Context

The story-done-reports-release-remaining task adds filed-task progress after an
archive. Without each admitted task recording its story or an explicit reason
for having none, that count cannot show whether work was classified. The Captain
returned the first design at ideation attempt 2, then approved the added step at
attempt 3. The source is the task's ideation gate records of 2026-11-11.

## Decision

**Words:** 「退回補上「任務必須標故事」（建議）」 — Captain, 2026-11-11,
ideation attempt 2, host question dialog.

**Asked:** 「決定：要不要核准「故事做完回報切片進度」的設計並開始實作。我建議照設計的建議核准：每張有切片的任務歸檔時，我在對話裡回報這個切片完成與剩餘的故事和每個完成故事的 PR，不自動重畫畫布；PR 連結現算、只出現在回報裡，畫布和地圖檔不變；不做故事宣告，回報裡改列「已建檔任務」的計數。核准即接受這三項；要畫布上顯示 PR 或要做故事宣告，請選對應的選項。」

The added step was accepted with 「核准（建議）」 at ideation attempt 3,
answering the proposal that every task in a workflow listing journey-map records
its story or none with a reason before the backlog gate, and a missing line holds
that gate. Workflows without journey-map remain outside this rule.

**Options considered:**
- Use the existing seed check for the story line and the design check for its
  agreement with journey-story (chosen).
- Add prose without a check; FO could skip it unnoticed.
- Add a separate extension command; the idle look would not run it.
- Require the line in every workflow; workflows without a map have no reader.

**Recommended:** The existing seed check, limited to journey-map workflows.

**Protects:**
- `kc-dev-flow-2/scripts/design_surfaces.py` — check_story_record and its seed/design call

In a workflow whose nearest workflow README lists journey-map, FO writes
`Story: <story id> (<release id>)` or `Story: none: <reason>` under FO alignment.
The seed check requires an unfenced, nonempty answer and a reason for none; both
forms pass. The design check compares a recorded story with journey-story.
Story membership is still the release review's decision. ADR 0041 otherwise stands.

## Consequences

The existing idle look names backlog tasks that still need preparation until
FO supplies their lines. Archived tasks are not backfilled. Skipping the seed
check bypasses the refusal; an unknown story can pass until release review.
Filed counts do not establish exhaustive scope or delivery acceptance. Reopen if
the supported admission path or the records it requires change.
