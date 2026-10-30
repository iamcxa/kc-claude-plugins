# 0044. Delivery gate summaries carry review facts with legacy-call compatibility

Date: 2026-10-29

## Status

Accepted

## Context

The operator-interview extension's validation briefing 2 omitted external
review rounds and the second-reviewer outcome from its bound summary. The
existing delivery question check could accept these facts in the question
instead. The task gate-requires-recorded-reviews records the historical replay
and the narrowed design; the separate optional-call omission in the named-batch
task cannot be inferred from supplied summary fields.

## Decision

**Words:** 「照建議」 — Captain, chat, 2026-10-29, ideation revise;
「進實作」 — Captain, chat, 2026-10-29, revised ideation approval.

**Asked:** The revise answered 「決定：五張全照建議（一張擱著、四張照表改）；如果哪張要調整，直接說。」
and accepted decision C: build the delivery-summary half, drop role-call
attestation and retain existing callers. The approval answered
「決定：四張全准進實作，含工作流文件多 27 字？要改哪張直接說。」
The task's ideation attempts 1 and 2 retain these rulings and their context.

**Options considered:**
- Add optional separate summary input to the existing delivery question check,
  opting in through its workflow recipe (chosen).
- Require a role-call inventory and make the new input mandatory for existing
  callers (withdrawn by the narrowed design).
- Keep checking combined question/summary text alone (retained for legacy
  callers, with its known summary-location gap).

**Recommended:** The optional summary-location repair, without role-call
attestation, and the exact 27-word workflow increase, as accepted at the gates.

**Protects:**
- `kc-dev-flow-2/scripts/delivery_gate.py` — optional summary branch in question

When supplied, the summary carries one external-round count and the configured
second-reviewer declaration/outcome outside fences. Existing reviewer rules
still decide which declarations are permitted. Ordinary checks use question
plus summary. Omission of the new input keeps the released combined-text path.
The workflow opts in before delivery gate preparation and instructs FO to use
the checked summary unchanged. Nonzero holds preparation; it grants no gate
approval or merge authority.

The count establishes presence and form, not actual review activity, content
quality or completeness. Optional calls, truthful counts, unchecked preparation
and later substitution remain observer responsibilities. Role triggers, initial
and ideation routes, review-round thresholds and merge checks stay as before.

## Consequences

FO can detect missing summary facts before binding a delivery gate. Each read
of the affected workflow passage costs 27 more words under ADR 0020. Existing
adopters using the legacy command retain their location gap until separately
authorized refresh. Local recipe tests do not prove native workflow compliance;
an observed adopted gate remains necessary. Reopen if this bounded input cannot
represent the required review facts or a compatibility migration is proposed.
