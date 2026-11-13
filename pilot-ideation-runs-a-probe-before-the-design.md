---
title: A Pilot task's ideation runs a working probe and its criteria's proofs before the design is written
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「開」 (chat, 2026-11-13), answering FO's item 「要不要開「Pilot 流程改動」的任務（你上一則問的後續，我建議開，拆成先進套件的和維持逐批授權的兩段）。」, after his 「那接下來要怎樣才能改？目前的證據顯示進步了多少？可以說品質也有進步，因為更早開始迭代嗎？」 (chat, 2026-11-13). His standing priority (chat, 2026-11-12): Pilot is too heavy; POC stays; Pilot may share POC's stages with its own bars; Prod stays rigorous.
- Outcome, the first of the two parts FO proposed: on the five-stage Pilot route, the ideation worker may build a throwaway working probe on a local branch that is never pushed, runs it on the real cases the task names, runs each acceptance criterion's evidence command once on it and records command, exit and saved output, and lists what cannot be run under a "Not provable now" heading the Captain sees at the design gate. The design gate stays as it is.
- Evidence (FO's hand-kept logs of 2026-11-12 and 2026-11-13, two rounds, ten small package tasks chosen by FO): with a probe in ideation, 0 of 7 built tasks changed design or a criterion after approval; without one, 2 of 2 did; one task ended in 15 minutes when its probe showed the premise was already fixed. Not shown: any gain in time from dispatch to merge (none was measured), fewer defects in what is delivered (not measured; two counterexamples recorded), or anything about tasks with ui, db or more than one component.
- What exists: the released workflow says ideation writes no repository file, branch or commit; the POC workflow has no ideation stage; the Worth questions (0.39.0) and the existing-chain check (0.40.0, ADR 0083) already cover need, upstream and cheaper-way; FO has carried the probe permission and the proof-run wording by hand in ten dispatch records.
- Open for the design: the exact words that replace the ideation write ban and what bounds the probe (local only, never pushed, no deploy, no credential, no shared environment); whether the probe is allowed, expected, or expected unless the worker says why not; where the probe's branch and commit are recorded and when the branch is removed; what the change deletes or shortens so the workflow does not only grow, with the word counts before and after.
- Non-goals: the second part FO proposed, which stays a per-batch grant from the Captain: the same worker continuing from ideation into implementation; FO recording the design gate when no stop fired; any change to Prod or to the POC workflow; a contract probe for tasks with more than one component (a separate proposal).

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- An ideation dispatch built from the candidate text carries the probe permission and the proof-run requirement with no hand-written line from FO, and a replay of two of the ten recorded dispatches shows it. Return to the Captain if the design cannot name what it removes, or if it needs to touch the design gate, Prod or the POC workflow.

## FO alignment

Alignment: not needed before ideation: his words admit the first part and name the second as staying with him; the wording is ruled at the design gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
