# ship-debrief station

**Enforcing script:** `kc-ship-flow/scripts/ship-debrief.py <batch-dir>`

**Input:** the batch's durable records only — `receipt/close-receipt.json` (or `.DRAFT.json`) for
`defects_returned` and per-issue minutes, and `README.md`'s "## Decisions made under `defaults`"
bullets.

**Output:** a `kc-ship-close-receipt/v1` `ship_debrief` JSON object on stdout — one disposition per
defect (an undispositioned defect is flagged rather than dropped), minutes summed per station, and
each `defaults` decision marked `overturned` only when a later bullet's text carries that decision's
own leading timestamp together with "retract", "overturn", or "correction"; `candidate_correction` is
always a placeholder for the First Officer to edit, never filled in from the record.

**Refusal:** exit 2 on bad argv, a missing close receipt, a missing `README.md`, a missing per-issue
minutes field, or a close receipt that parses as JSON but is malformed or missing a field this script
reads. A `README.md` present without a `defaults` heading is a real zero decisions, not a refusal.
