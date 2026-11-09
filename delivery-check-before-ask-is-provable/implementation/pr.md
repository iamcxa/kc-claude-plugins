fix(kc-dev-flow-2): bind delivery check records before merge questions

Merge questions could be prepared before a matching delivery check existed. `question` now holds preparation unless the newest check record matches the dispatched candidate, merge head and both confirmation clauses, then prints the record path for `gate prepare --reference`.

The workflow orders the check before preparation without changing its word budget. The observer checks the committed record's digest, head and clauses, retaining the time fallback for older briefings. ADR 0071 records the Captain's approval and amends ADR 0051's ordering consequence while preserving its round-count decision.

Validation on 2026-11-09:
- Delivery-gate suite: 184 tests, one optional historical-approval replay skipped; final question checks: 21 tests, the same optional replay skipped.
- Seven code mutations rejected; native Spacedock 0.27.2 refuses uncommitted and modified records and fingerprints the committed record.
- Twelve observer replays cover bound-record mismatches, five batch 17 briefings and the earlier passing time fallback; removing that fallback loses the earlier pass.
- Workflow passage: 80 to 80 words; passing merge-question output: 92 to 107; delivery-check output unchanged.
- Repository skill lint, ADR lint, number guards, comment ratio and affected-document review pass. Supporting lint tests: 47 passed; POC README tests passed.

RoboRev and hosted CI: not run; FO owns publication, review and CI. CI cost per PR was not measured; this change edits no workflow or trigger. The first post-release observer run remains post-merge evidence. Skipping `--reference` is detected at observation, not by a new preparation hook.
