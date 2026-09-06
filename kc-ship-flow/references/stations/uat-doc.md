# uat-doc station

**Enforcing script:** `kc-ship-flow/scripts/uat-doc.py <batch-dir>`

**Input:** the batch's durable records only — `receipt/plan-receipt.json`,
`receipt/plan-approval.json`, `receipt/close-receipt(.DRAFT).json`,
`evidence/worker-evidence-<ISSUE>*.md`, and, when present, the `README.md`
"## Decisions made under `defaults`" bullets.

**Output:** the batch's UAT document, listing what the batch already recorded.

**Refusal:** it decides nothing new — a durable record it cannot read is a gap in the document, not a
value it invents.

Placed segments (`references/placement.tsv`): `d708e82924c7`.
