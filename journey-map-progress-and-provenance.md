---
title: The journey map shows each story's evidence stage, ADR rulings by reference and where its drawing came from, and one task can serve several stories
status: backlog
variant: kc-dev-flow-2
merge: pr
---

Scope two of the kc-journey-map ↔ kc-dev-flow-2 contract, split from task `journey-map-dev2-contract` by the Captain on 2026-10-13: 「看看是否拆成兩個範圍？讓 pilot profile 更有設計餘裕？」, then 「可以」 to the FO's split. That task now covers only scope one: a ruling reaches the map. This task is designed after scope one is accepted, using the data scope one produces in active adopters.

Asked by the Captain: 「理論上範圍一合併之後應該立即會有範圍二的資料？因為 relay + qnow 都很密集的開發中」.

## Relay contract gaps folded in

Folded in on the Captain's 「確認」 (2026-10-14), answering FO's recommendation to fold three gaps the spacedock-dev/subspace-relay FO reported into this task rather than file them separately. Evidence (read only): `/Users/kent/conductor/workspaces/subspace-relay/dhaka/.context/task-story-backfill.md` (2026-10-14), a backfill over relay dev2, relay dev2-poc, subspace-v0 dev2 and subspace-web dev2 state branches: 91 tasks, 21 carry `journey-story`, 16 are infra, 4 have no story, and no story carries `journey-required-tasks`; `journey-progress.mjs docs/journey/spacedock-review.yaml --workflow-dir docs/dev2` on relay (kc-journey-map 1.6.1) reports 142 stories `unverified`, 2 `gap`, none green.

- Gap 1, an unmapped task is ambiguous and unchecked: the backlog Release review lets a task with no release be outside it, and "no script checks that line"; a task without journey fields can mean infra or a forgotten mapping (34 of 49 relay dev2 tasks have no `journey-story`; the backfill proposes 20 of those belong to a story). Relay's suggestion: every task records its story or `no story: <reason>` at the backlog gate, and the seed check refuses neither.
- Gap 2, the progress declaration is written only at the release review's split step: FO writes `journey-required-tasks` and `journey-mapping-complete: true` there, and relay never ran that step, so no story was declared. Relay's suggestion: add a task to its story's declaration when FO approves it into that story at the backlog gate.
- Gap 3, one journey spans several workflows: relay's map is delivered by tasks in relay, subspace-v0 and subspace-web dev2 workflows, but `journey-progress.mjs` takes one `--workflow-dir` and required task ids must resolve in it. Relay's suggestion: accept several `--workflow-dir` with repository-qualified task ids, or let the journey file name the delivering workflows.
- Relay's interim practice (its Captain's approval, 2026-10-14): every relay backlog gate states "belongs to story <card text> (<release>)" or "infra: <reason>"; completed tasks are not backfilled.

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
