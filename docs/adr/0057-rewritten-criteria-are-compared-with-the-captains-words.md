# 0057. Rewritten criteria are compared with the Captain's words

Date: 2026-11-03

## Status

Accepted

## Context

In task peer-status-reaches-fresh, Captain amendment 3 withdrew the observation-time
requirement. Its replacement AC-9 added "revision/link" inside the retained sentence
"include source/time". State commit b4e88ece4 carries the validation dispatch that
passed the existing check before the added requirement failed validation.
The approved design of rewritten-criteria-checked-against-captain-words replayed
that miss and measured holds in 10 of 42 amended tasks' newest validation records.

## Decision

**Words:** 「可以」 — Captain, chat, 2026-11-03, recorded in the task's ideation gate.

**Asked:** 「決定：七張設計照建議進實作，但驗收到期提醒的 D7 改成『在 kc-journey-map 登記 journey-progress/v1，預算放寬為兩個 PR，kc-journey-map 那個先合併』，可以嗎？」
The gate accepts each design's recommendations; this task's D1 recommends the comparison below.

**Options considered:**
- Hold validation dispatches on inserted words inside kept sentences (chosen).
- Record no check, retaining observer and validator detection after dispatch.

**Recommended:** Hold validation dispatches on inserted words inside kept sentences.

**Protects:**
- `kc-dev-flow-2/scripts/design_surfaces.py` — `added_words` compares replacement and moved criterion sentences against recorded Captain words.

`dispatch_records.py --names` exits 1 for a validation record or its message
continuation when `added_words` finds an inserted or substituted word in a live
amendment replacement's sentence with word-sequence similarity at least 0.75 to
a superseded sentence. It excludes AC ids, filler words and words present in the
`Captain:` or `Asked:` lines of that amendment or a later amendment, and stops
reading a criterion at `Current evidence:`. The line names the criterion,
amendment and words; FO removes them through a worker follow-up or records a new
Captain answer. Implementation follow-ups remain available to make that repair.
L2 classifies the diagnostic as a violation when a push adds a held dispatch.

This narrowly departs from ADR 0027 D4's choice of no phrase check. ADR 0016's
amendment-form and replacement-marker checks remain; this adds no comparison of
FO prose in `Design:` and does not judge semantic fidelity.

## Consequences

The historical widening is held before validation. Whole new sentences remain
unchecked, and faithful English translations of Chinese rulings can be held until
removed or confirmed. The measured prototype held about one quarter of amended
tasks once, costing a follow-up or Captain question. Clean output and the workflow
README remain unchanged; a held dispatch adds a diagnostic. Revisit if these
holds outweigh the avoided failed rounds or a whole-sentence widening requires
a different mechanism. No CI trigger changes or cost saving is claimed.
