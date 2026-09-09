# dev-debrief station

**Enforcing script:** `kc-ship-flow/scripts/dev-debrief.py <batch-dir>`

**Input:** the batch's durable records only — `receipt/close-receipt.json` (or `.DRAFT.json`),
`evidence/worker-evidence-<ISSUE>*.md`, `README.md`'s "## Decisions made under `defaults`" bullets,
and, when an issue has a PR, `review/disposition-<PR>*.json`.

**Output:** a `kc-ship-close-receipt/v1` `dev_debrief` JSON object on stdout — per issue, its rounds,
its without-it refusal shape read from the record, and its code refusals; `candidate_correction` is
always a placeholder for the First Officer to edit, never filled in from the record. The same object,
wrapped with `schema`/`close_receipt` keys, is also written to `--out <path>` (default
`receipt/dev-debrief.json` beside the close receipt).

**Refusal:** exit 2 on bad argv, a missing close receipt, a missing rounds field, a missing or
unresolvable worker-evidence file for a dispatched issue, or a close receipt that parses as JSON but
is malformed or missing a field this script reads. An issue whose outcome is `carried`,
`captain_stopped`, or `drift` and has no worker-evidence file is not a refusal: its entry gets an
empty refusal list and `note: "not dispatched"`.
