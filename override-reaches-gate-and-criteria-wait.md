---
title: An Override written in a task reaches its gate record, and a superseded criterion waits in place for the worker to move it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain's 「可以」 (chat, 2026-10-21) to FO's narrowed candidate E: 「只做第 1 和第 2 點，第 3 點留給觀察者。排在第五批最後。」
- Point 1, Override placement: the README says FO writes `Override: recommended <option>; Captain chose <option>; area: <area>` in the gate resolution reason. In batch 4 FO wrote it only inside a Captain amendment twice (fo-write-rules-checked D4, fo-batch-sittings, observer findings; decision_ledger.py shows override null for those resolutions). Shape asked for: a task file holding an `Override:` line whose gate resolution carries none holds before the gate.
- Point 2, a conflict between a check and a rule: `design_surfaces.py check` reports "supersedes AC-N but it is still declared in '## Acceptance criteria'" and so pushes FO to delete the criterion at an ideation gate where no worker runs, while the README's Captain amendments give moving a criterion to the worker and say FO "does not move or rewrite a criterion" (observer finding on fo-write-rules-checked, deleted AC-7 at 82632167; the same edit on fo-batch-sittings at d3825cab). Shape asked for: at the gate a superseded criterion stays in place marked as superseded by Amendment N, and the next worker dispatch moves it.
- Not in scope: detecting FO's own words inside an amendment's Design line (point 3); every word of that line is FO's rendering, so no script tells transcription from addition; the observer keeps it.
- Upstream first: `design_surfaces.py` (amendment checks), `decision_ledger.py` (override field), the README's Captain amendments and FO steps: review findings.
- Priority: last in batch 5 (the Captain's ruling).

## FO alignment

Alignment: not needed before ideation; the Captain chose the narrowed scope.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
