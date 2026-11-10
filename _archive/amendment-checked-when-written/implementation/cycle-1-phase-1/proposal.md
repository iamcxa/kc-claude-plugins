# Cycle 1 phase 1: F1 investigation and proposed repair

F1 is independently reproduced at unchanged candidate `72216e2e947e962737a17c6e61ef3800f9d639c4`. Real temporary Git commits exercise the unmodified CLI: repairing AC-1 while leaving previously reported AC-2 unchanged exits 1 and reports AC-2 again, with no L3 violation. The standalone tests produce three expected assertion failures and seven passing controls, with zero errors. Product source, branch and HEAD remain unchanged.

## Cause and smallest proposed change

`l4_amendment_moves_use_fresh_ids` compares entire `("reused", amendment, ids)` tuples. A smaller id tuple is absent from the previous set, even when every id in it was already reported. Compare reused ids individually within the same amendment, then emit the existing grouped tuple containing only genuinely new ids. Keep the unmarked `(kind, amendment)` membership comparison, walker, parser, paths, event grouping and output format.

`proposed-runtime.diff` is an unapplied runtime-only proposal. After FO authorization, change only `laws_check.py` and `test_laws_check.py`: promote the three failing cases for partial repair, growth and mixed removal/addition. Retain the existing heading-only repair and once-only tests. No `design_surfaces.py`, law registry, document, version or workflow change is needed for this bug fix.

## Observed scope

- A strict decrease incorrectly adds an event. Growth and mixed removal/addition already deserve an event, but their diagnostics repeat surviving old ids; the same per-id difference removes those old ids from the diagnostic.
- Reordering and complete repair pass. Unmarked replacement has a fixed `(kind, amendment)` tuple: persistence does not repeat it, adding its marker repairs it without a new event, and removing a marker reports a new unmarked defect. A partial reused-id repair can still fail the push, but the unmarked diagnostic itself is not repeated.
- The existing first-judgeable heading-repair test passes. The proposed difference leaves parent filtering and per-amendment identity unchanged.
- All seven named historical first-parent ranges are exercised through the unchanged L4 API. Each event task has an empty previous defect list, so the analysis-only per-id delta produces exactly the same event and diagnostic payload as today. `seven-events.json` records both calculations and `seven-events.log` records current heads/diagnostics.

This is phase-1 evidence and a proposal, not an applied fix or a green candidate. The full histories were not re-run with a patched candidate. After authorization, run the named regressions, existing suites, mutation controls and complete corpus at the new candidate, then return for fresh validation. AC-7's release/adoption/hosted proof remains outside this phase.
