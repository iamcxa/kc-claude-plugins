---
title: The journey map shows each story's evidence stage, ADR rulings by reference and where its drawing came from, and one task can serve several stories
status: backlog
variant: kc-dev-flow-2
merge: pr
---

Scope two of the kc-journey-map ↔ kc-dev-flow-2 contract, split from task `journey-map-dev2-contract` by the Captain on 2026-10-13: 「看看是否拆成兩個範圍？讓 pilot profile 更有設計餘裕？」, then 「可以」 to the FO's split. That task now covers only scope one: a ruling reaches the map. This task is designed after scope one is accepted, using the data scope one produces in active adopters.

Asked by the Captain: 「理論上範圍一合併之後應該立即會有範圍二的資料？因為 relay + qnow 都很密集的開發中」.

## Carried from the first ideation attempt of journey-map-dev2-contract

These parts of that task's `## Design` (state commit f66ed837, first `## Stage Report: ideation` that is marked DONE) are inputs here, not accepted design:

- the evidence ladder: gap → built → verified → shipped (relay defect 4);
- ADR by reference, and an ADR `Map:` line checked by `adr_lint.py --map-required`;
- "fold pending" marks read live from footprints, and the UI proposal with its preview (`journey-map-dev2-contract/preview/`);
- drawn-commit provenance on each page header (relay defect 6);
- the task tuple list form, and story id as task identity (relay defects 2 and 3, qnow gap 4);
- the map-service seam (`apiFetch` with `JOURNEY_API_TOKEN`; `/save` and `/repo-doc` behind `JOURNEY_LOCAL_OPS`), the Captain's 「照你建議」 of 2026-10-13;
- the three schemas that scope one does not take: `journey-progress`, `journey-task-tuple`, and the rest of `journey-map`;
- the draft acceptance criteria AC-3, AC-7, AC-8, AC-9 and AC-10.

Relay keeps its manual practice for defects 2, 3 and 6 until this task lands.
