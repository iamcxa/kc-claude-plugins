---
title: ui design review round-3 follow-ups declined at #663 (fenced Preview candidates)
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined by FO under the round-3 rule (README review-finding disposition, step 5) on PR #663 (ui-design-review-in-ideation), 2026-10-18, on the chief-engineer's measured advice.

- Codex round 3 P2 (review:5558271854): in `kc-dev-flow-2/scripts/design_surfaces.py` the design-review `Preview:` candidates are collected from the raw task body, so a fenced example `Preview: fake.html` can bind a report. Decline reason: not P1 and not Material; 0 fenced `Preview:` lines in 258 task files across this repository's dev2 state and the subspace-web, subspace-relay and qnow state branches (chief-engineer corpus run, 2026-10-18). Fix shape: build the candidates from unfenced text.
- Not taken in #663: converting `design_surfaces.py`'s other raw reads that predate the PR (UI_PROPOSAL and PREVIEW in check_ui, check_criteria, live declarations in check_amendments); `check_db` must keep reading inside the mermaid fence.
- Update (FO, 2026-10-18): roborev 830 rated the same fenced-Preview read High on #663 e6eb277f; a roborev High counts as P1 here, so FO took the Preview candidates fix into #663 (dispatch implementation-9). Only the not-taken raw reads below remain here.
