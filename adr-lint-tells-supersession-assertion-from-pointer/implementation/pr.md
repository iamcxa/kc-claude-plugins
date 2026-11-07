fix(kc-adr): distinguish supersession assertions from stale pointers

## Summary

The ADR pointer scan reports a protected test file as citing a superseded record when it merely asserts that record's supersession status. Skip that citation during the supersession scan when the same line states the successor recorded by the old ADR. Keep the Accepted-record pointer check and stale citations on other lines intact.

Edit kc-adr as the source, synchronize the dev2 copy with the existing script, and restore the natural ADR 0047 path in the dispatch integration test. The approved design is bounded to same-line status text; split-line assertions still fail the scan.

## Validation

- 25 kc-adr tests, 9 ADR/document checks, native Spacedock dispatch integration, repository skill lint, copy parity, number guards and design surfaces passed.
- Candidate full lint and changed-record lint requiring ADR 0064 passed on the real repository (62 records).
- Seven negative mutations were rejected; the historical unsplit-path case at ae7750375 failed under the historical checker and passed with the candidate checker.
- Added comments: 0.0%, within the 5% maximum. No CI configuration changed; CI cost per PR was not measured.
- The dispatch-required installed kc-dev-flow-2 0.35.0 checker still fails with the original ADR 0047 false positive. Its bytes match the base checker; the installed package was left unchanged. This required check remains unresolved for FO disposition.

Base: 139feeaee7ce037a0c6535568cd6bd103155cbae
Candidate: f429f0fac40511c6480fd92e2cccd4c0e94b2454

RoboRev and remote CI were not run; FO owns publication and review. No product branch push or PR creation was performed.
