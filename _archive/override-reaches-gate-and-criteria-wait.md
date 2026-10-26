---
title: An Override written in a task reaches its gate record, and a superseded criterion waits in place for the worker to move it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: done
verdict: REJECTED
completed: 2026-10-26T01:18:45Z
archived: 2026-10-26T01:18:45Z
---

## Scope

- Source: the Captain's 「可以」 (chat, 2026-10-21) to FO's narrowed candidate E: 「只做第 1 和第 2 點，第 3 點留給觀察者。排在第五批最後。」
- Point 1, Override placement: the README says FO writes `Override: recommended <option>; Captain chose <option>; area: <area>` in the gate resolution reason. In batch 4 FO wrote it only inside a Captain amendment twice (fo-write-rules-checked D4, fo-batch-sittings, observer findings; decision_ledger.py shows override null for those resolutions). Shape asked for: a task file holding an `Override:` line whose gate resolution carries none holds before the gate.
- Point 2, a conflict between a check and a rule: `design_surfaces.py check` reports "supersedes AC-N but it is still declared in '## Acceptance criteria'" and so pushes FO to delete the criterion at an ideation gate where no worker runs, while the README's Captain amendments give moving a criterion to the worker and say FO "does not move or rewrite a criterion" (observer finding on fo-write-rules-checked, deleted AC-7 at 82632167; the same edit on fo-batch-sittings at d3825cab). Shape asked for: at the gate a superseded criterion stays in place marked as superseded by Amendment N, and the next worker dispatch moves it.
- Not in scope: detecting FO's own words inside an amendment's Design line (point 3); every word of that line is FO's rendering, so no script tells transcription from addition; the observer keeps it.
- Upstream first: `design_surfaces.py` (amendment checks), `decision_ledger.py` (override field), the README's Captain amendments and FO steps: review findings.
- Priority: last in batch 5 (the Captain's ruling).
- Folded 2026-10-25 into fo-written-lines-checked-before-dispatch (the Captain 「可以」 (chat, 2026-10-25), answering 「需要你決定：這份第 6 批的清單可以嗎？」 about FO's batch-6 list); not run on its own while that task is live.

## FO alignment

Alignment: not needed before ideation; the Captain chose the narrowed scope.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Closed

Closed 2026-10-26, the Captain 「可以關，如果都涵蓋了」 (chat), answering FO's ask to close the three tasks folded into fo-written-lines-checked-before-dispatch. Covered by iamcxa/kc-claude-plugins#724 (merged 1a6149f5): point 1 is that task's AC-5 (`design_surfaces.py check` notes an `Override:` line outside a gate resolution reason), point 2 is its AC-6 (a superseded criterion waits until a dispatch checklist names its amendment). Point 3 stays with the observer under the Captain's 2026-10-21 ruling.
