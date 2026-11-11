feat(kc-dev-flow-2): hold dispatches past cycle budgets

Countable task budgets now show implementation and validation cycles spent and
hold the first overrun for the Captain. A later amendment can raise the bound
when its Budget value occurs verbatim in Asked or Captain. Stage records carry
the budget; tasks whose first saved record predates that header remain exempt.

New seeds require either fixed cycle form. Ideation designs require the three
worth questions, and countable tasks stop printing the advisory step-back
reminder. ADR 0077 records the ruling and amends ADR 0026. No version changes.

Refs #837.

This PR text is prepared for FO; the candidate is held, not ready to publish:
- AC-5: four consumer-fixture assertions still require authorized changes in
  test_pr_watch.py and test_delivery_gate.py, outside the design's file list.
- AC-7: backlog Gate content conflicts with the approved no-backlog-addition
  design; no gate-content edits were made pending clarification.

Validation run 2026-11-11: repository lint, installed ADR linter (0077), number
guards and 3.8% comment ratio passed. Eleven mutation falsifiers were caught.
The relay history first holds at implementation-2 (42317d0c); the base does not.
Four pinned state corpora and per-moment reading cost were recounted in the
implementation evidence. Existing delivery/watch suites retain the four fixture
failures above; the full suite needs an exact-candidate rerun after authorization.

RoboRev and hosted CI not run: FO owns those. CI cost not measured; CI triggers
and workflows were unchanged. No product push or PR was performed by the worker.

A later Captain amendment 3 adds total dispatch limits and a default
preserve/report/stop result. It is not implemented by this saved candidate; FO
must dispatch the amended scope before publication.
