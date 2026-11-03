---
title: A rewritten acceptance criterion is checked against the Captain's words
status: backlog
variant: kc-dev-flow-2
---

## Scope
- Source: Batch 13 sitting, the Captain, chat 2026-11-03: 「ABC 都開，不屬於套件的本身也要討論一下」, answering 「決定：A、B、C 三個都開成 dev2 任務，跟 #768 一起發版嗎？要刪哪個直接說。」; and 「先不合併，我想要把這些也評估修復後，再一起發版」 about Release PR #768. FO had proposed it as 「FO 改寫驗收條件後，要和你的原話比對」.
- Outcome: when FO or a worker rewrites an acceptance criterion, the rewrite is compared with the Captain's own words before dispatch, so a requirement he never stated does not reach validation.
- Gap: today `design_surfaces.py check` holds a changed Scope and the amendment rules hold FO words in an amendment, but nothing reads a rewritten acceptance criterion against his words.
- Bite: on this workflow's task for PR #756 (batch 11) FO rewrote 「附上來源」 as "the source's commit or link", which failed one validation round. The agent-observatory reports of 2026-11-03 (sampled) show the relay and web FOs stating verdicts before reading the artifacts and using a worker count measured in another repository.
- Consumer: every adopter FO at the ideation gate and the dispatch that follows it.
- Upstream first: `scripts/design_surfaces.py`, `scripts/dispatch_records.py`, the Captain amendments rules in the workflow template.

## Non-goals
- Judging whether a criterion is good; translating his words; rewriting criteria for the FO.

## Budget
- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## FO alignment
Alignment: needed before ideation; the scope is the Captain's ruling and the evidence is an observatory sample, which ideation must check against its source first.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Stop condition
- A replay of the #756 rewrite is held before dispatch with the added words named, and a rewrite that adds nothing to his words passes.
