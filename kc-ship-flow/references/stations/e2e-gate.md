# e2e-gate station

**Enforcing script:** `kc-ship-flow/scripts/e2e-gate.py <plan-receipt.json> <close-receipt.json>`

**Input:** the batch's plan receipt (`dispatch_order`, `milestones`) and close receipt
(per-issue `candidate`).

**Output:** for a milestone with a flow file, runs `e2e-cli.sh` at the resolved head and reports its
log path and exit code; for a milestone with no flow file, records `e2e: not applicable` and exits 0.

**Refusal:** no milestone named exits non-zero and the batch is not UAT-ready.

A Milestone's CLI journey lives at `docs/ship-flow/flows/<milestone-slug>.yaml`, consumed read-only by
`e2e-cli.sh`. `e2e-gate.py` computes the slug: lowercase, keep every Unicode letter and digit,
collapse every other run of characters (including underscore) to a single hyphen, strip
leading/trailing hyphens — a name that slugifies to empty refuses with exit 2.

Placed segments (`references/placement.tsv`): `5aa826f86c91`, `d7132b42e5fa`.
