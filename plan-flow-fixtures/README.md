# plan-flow fixtures

Linear project snapshots taken 2026-09-05 with plan-lint v0's exact GraphQL query, so a
worker without `LINEAR_API_KEY` can lint offline. `blocks-edges` are (blocker -> blocked)
as plan-lint v0 reads them from `inverseRelations`.

- `dev67-inverted-relations.snapshot.json` — DEV-64/65/66. **Relations are inverted (S22):**
  the recorded edges say 66 -> 65 -> 64, the intended dispatch order was 64 -> 65 -> 66.
  A lint consistent with its own input passed this; L6 must not.
- `dev89-runA-correct-relations.snapshot.json` — DEV-90/91/92, relations correct
  (90 -> 91 -> 92). Also the by-product fixture: DEV-91's only surface is
  `scripts/kc-dev-flow-contract-test.py`, which DEV-90 also names (S26).
- `plan-lint.v0.py` — the eight-rule lint as it ran in DEV-67/DEV-89, reads live Linear.
