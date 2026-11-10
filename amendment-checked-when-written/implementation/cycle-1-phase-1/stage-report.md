
## Stage Report: implementation

- DONE: Phase 1 only of the Cycle 1 repair: reproduce finding F1 as a failing test at head 72216e2e and propose the smallest fix; report and stop with no product commit or product push until FO authorizes the fix.
  Independent `ReusedIdEvents.test_partial_repair_adds_no_event` uses real temporary Git commits and the unmodified CLI: expected exit 0, observed exit 1 re-reporting unchanged AC-2, with L3 clean. `tests.log`/`tests.json`: 10 tests, three expected failures (partial repair, growth diagnostics, mixed removal/addition), seven passing controls, zero errors. `proposed-runtime.diff` is unapplied; proposed product scope is only `laws_check.py` plus the three regressions in `test_laws_check.py`.
- DONE: Say whether the same whole-tuple comparison affects the unmarked-replacement defect or any other L4 event, and whether the fix changes any of the seven corpus events.
  `scenarios.json` shows strict decreases create false events; growth/mixed changes repeat surviving old ids. Unmarked `(kind, amendment)` identity is stable: persistence, marker repair/removal controls behave correctly; the existing first-judgeable heading-repair test also passes. `seven-events.json` exercises all seven named first-parent ranges: each event task's previous defect list is empty, so the analysis-only per-id delta preserves all seven event/diagnostic payloads. This is not patched-candidate or full-history validation; details and repair scope are in `proposal.md`.
- DONE: Append one complete Stage Report: implementation, every item followed by its own indented evidence line, with evidence kept in the task folder in the state checkout.
  Durable evidence: `amendment-checked-when-written/implementation/cycle-1-phase-1/`; `README.md` gives exact reproduction commands, `identity.json` binds candidate/source hashes and clean product status, and `manifest.json` seals the evidence. This report is copied to `stage-report.md`; existing reports, findings, criterion text and amendment records remain untouched.
- SKIPPED: Apply the proposed fix, create a product commit, push the product branch, or run fixed-candidate validation.
  Phase 1 grants investigation only. Candidate remains `72216e2e947e962737a17c6e61ef3800f9d639c4`; no product bytes, commit, PR text or remote publication changed. Await FO fix authorization, then re-run the named regressions, existing suites, mutation controls and full corpus at the new candidate before fresh validation.

### Summary

This report supersedes earlier implementation readiness claims: phase 1 independently confirms F1 and the candidate remains rejected on AC-3. The smallest proposed repair compares reused ids individually within each amendment while retaining the unmarked comparison and grouped output; the seven named events are unchanged in the scoped data comparison, but no repair has been applied or validated.
