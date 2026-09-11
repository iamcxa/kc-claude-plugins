Go test-only changes should pass default surface mapping without requiring non-test implementation evidence.

## What changed

- Add `_test.go` to default test exclusions.
- Preserve strict mode, explicit mappings, and ordinary Go enforcement.
- Extend the existing Git-backed regression cases with bounded checker timeouts.

## Evidence

- Focused surface-map contract scenarios: 13/13 passed, including seven existing and six Go scenarios.
- Independent checks: 11/11 passed, detecting old, overbroad, and explicit-mapping-bypass producers.

Same-fixture default result changed from failure to success; strict mode still refused missing evidence. The full suite was not rerun; CI status is pending.

Candidate: 715f8871ee33e7d42e3f22b6b346ac3a3e05938a

---
[3w8 — local Pilot review record](/iamcxa/kc-claude-plugins/blob/03582b667be624e83bf7d1a156ca682a4203e0b1/dev-flow-manual-improvement-pilot/index.md)
