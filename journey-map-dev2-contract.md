---
title: kc-journey-map and kc-dev-flow-2 connect through versioned input/output contracts, each schema owned by its producer, with ADR rulings shown on the map by reference
status: backlog
variant: kc-dev-flow-2
merge: pr
---

kc-journey-map (the release slice map) and kc-dev-flow-2 meet today through prose split between workflow.md's Release review section and kc-journey-progress's SKILL.md. Nothing tests that prose, and six defects found in an adopter on 2026-10-13 come from that missing interface.

## Captain's words

- 2026-10-13, answering "Should a dev2 design task in kc-claude-plugins handle the journey-map ↔ dev2 interface?": 「可以」.
- 2026-10-13, same turn: 「切片地圖似乎也很適合放 ADR 重點…怎樣同步比較省時省力？」.
- 2026-09-06, the standing ruling on flows: plan, dev and ship are independent plugins joined only by versioned input/output contracts, and each schema lives with its producer.
- Relayed by an adopter First Officer session, not heard directly: each plugin should be usable alone, with the integration a written two-sided contract, as Spacedock and Spacedock Review are.

## Inputs: defects reported by an adopter FO, 2026-10-13 (kc-journey-map 1.5.1, kc-dev-flow-2 0.20.0)

1. A slug-id workflow could not be read. Fixed in kc-journey-map 1.5.2 (#623); listed here only as the conformance case to keep.
2. An archived task becomes a permanent orphan. A story moved to another release after its task was archived stays listed under `orphans`, and `spacedock status --set` refuses an archived entity, so nothing can clear it.
3. One task can serve only one story, because `journey-story` is a scalar; a task that carries three stories by a Captain ruling shows progress for one.
4. Three meanings of "done" never meet: the map's `status` (an evidence symbol greps), the progress reader's task `done`, and the adopter's deploy record (for example a `staging-verified` commit status).
5. Answers do not flow back to the map. Captain rulings, ADRs, POC findings and validation findings land in task files and ADRs; the map's story `questions` are written by hand.
6. The canvas has no provenance: a drawing records no journey-file commit, so a map ahead of `main` looks current.
7. Release review signal 2 is honour-system: workflow.md says "no script checks that line".

## Input: ADR rulings on the map

A real adopter map (a booking product, release 8) already cites ADRs by hand in story answers and in flow and constraint text: 61 mentions in one journey file, read with `git show origin/next:docs/journey/<file>.yaml | grep -ci adr` on 2026-10-13. Two hand copies already disagree with their sources: one answer says an ADR question is "still open, to fill in", and the same file cites ADRs by two numbering schemes (a separate file `0034`, and a section `26` inside ADR 0001).

## Open for ideation

- Each schema's owner and version string: what journey-map produces (story, release, goal and question ids; drawn-commit provenance) and what dev2 produces (task tuple and declaration; answers, ADR references and new questions).
- How ADR rulings reach the map. Proposed: by reference, rendered from the ADR at draw time, so no ADR text is copied.
- One conformance test against both a slug-id and an id workflow.
- Overlap with task `release-acceptance` (defect 7 is its enforced pre-implementation review) and with `journey-canvas-hosted-poc` (defect 6).
