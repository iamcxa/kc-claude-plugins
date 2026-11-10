# 0045. Validation reruns require a later recorded Captain ruling

Date: 2026-10-29

## Status

Accepted

## Context

The archived paseo-codex-dispatch-practice task returned an open Needs decision
finding, but its second and third validations ran before the Captain's ruling.
Its fourth validation followed a native hold resolution. The existing
dispatch-record names check accepted all six saved dispatch/follow-up records.

The task validation-rerun-waits-for-captain-ruling retains the source snapshots,
seven replay adjudications, and ideation gate questions. Its bounded 27-record
replay produced 15 structural passes and 12 holds: two false holds on record
additions, including one actual authorized rerun with a free-form ruling.
ADR 0017 governs historical judging; ADR 0038 retains human-source verification.

## Decision

**Words:** 「照建議」 — Captain, chat, 2026-10-29, ideation gate attempt 1.

**Asked:** 「決定：五張全照建議（一張擱著、四張照表改）；如果哪張要調整，直接說。」
The bound task question recommends native gates and Captain amendments, recording
older free-form rulings on next touch, skipping non-git records and deferring
historical judging. The batch question accepts structure-based checking, leaving
the remaining judgment to the observer.

**Words:** 「進實作」 — Captain, chat, 2026-10-29, ideation gate attempt 2.

**Asked:** 「決定：四張全准進實作，含工作流文件多 27 字？要改哪張直接說。」
The bound revised task question accepts the measured legacy compatibility cost
and the live-only scope. The workflow word increase belongs to the separate
gate-requires-recorded-reviews task, not this decision.

**Options considered:**

- Add a live predicate to the existing names check; recognize later native
  validation resolutions and Captain amendments; record verified free-form
  authority on next touch; skip non-git copies (chosen).
- Add historical-law enforcement and historical authority reconstruction
  (deferred).
- Accept arbitrary legacy Captain prose (excluded).

**Recommended:** the bounded live predicate with native gates, amendments and
on-touch source verification; leave authenticity and semantic coverage with the
First Officer and observer.

**Protects:**
- `kc-dev-flow-2/scripts/dispatch_records.py` — later_captain_ruling and its names-only caller.

For a live validation record inside its own Git root, the names check refuses
a rerun while the newest validation report has an open F-numbered Needs decision
finding and no supported Captain record first committed strictly after that
report. Native records need a validation-stage Captain resolution with time and
reason, without a withdrawal; amendments use the shared numbered-entry grammar.
Editing an older entry does not make it later. Same-commit records do not clear
the finding. Missing, shallow or ambiguous required history is an evidence hold.

Amended 2026-11-11 (Captain: 「裁示前的補改都算，結論不能改（建議）」, answering 「驗證報告被補改過之後，哪些補改還算同一份報告、可以繼續派驗證？我建議：你第一次裁示之前的補改都算，但不能改變報告的結論（通過或退回）；裁示之後才改的照舊拒絕。這是設計的方向，細節與證明仍在設計關卡由你核准。」 in the host question dialog; then 「核准（建議）」, answering 「決定：要不要核准「驗證報告在你裁示前被補改過，仍可再派驗證」的設計並開始實作。我建議核准：設計照你選的方向做，用 qnow 的真實歷史重放過三種情況，結果都符合預期。核准即接受設計裡兩項建議：一、「結論沒變」的判法是每一版報告裡 PASSED 與 REJECTED 這兩個字的出現順序完全相同；二、把這次改動記成 ADR 0045（驗證重跑前必須有你之後的裁示）的一段原地增補，不開新編號。核准後我派實作工人。」 at the ideation gate): a validation report edited in place still counts as the report a later ruling answers when every correction, including the commit that first carries the final text, precedes the first Captain record or gate entry recorded after the report appeared, and every version carries the same ordered, non-empty list of whole-word `PASSED` and `REJECTED` tokens. The later supported ruling must first appear strictly after the commit where the final text first appears. Otherwise the check holds with `rewritten-report-after-ruling`, `rewritten-report-verdict-changed` or `rewritten-report-verdict-unreadable`. The check still runs only while the newest report has an open Needs decision finding.

This predicate runs through `--names`, not `--newest` or the historical snapshot
caller. Passing establishes structure and order; the First Officer still checks
the original question and reply, per-finding coverage and permission for the
specific rerun. A partial supported ruling can pass this structural check.

## Consequences

Authorized older reruns may pause until their verified original wording and
question are faithfully recorded in a supported home. This change backfills
nothing, authenticates no Captain identity and adds no runtime hook.
Non-git copies retain existing checks but receive no new protection.

The refusal includes recovery guidance; clean checks add no output. Workflow,
law, lifecycle and CI triggers stay unchanged. Reopen when an unruled rerun
passes despite this check being run, or a later supported ruling is refused.
