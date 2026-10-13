---
title: A script checks the FO-written records that the observer found wrong more than once
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Observer reports on four tasks archived 2026-10-13 (journey-map-dev2-contract, copilot-quota-refusal-is-not-a-review, workflow-checkout-must-match-trunk-readme, observer-before-merge-guard) found FO-written records that break rules the workflow README already states, and the learn evaluations returned no-change for each because the rule exists. A rule stated and not followed is an enforcement gap; `dispatch_records.py` and `design_surfaces.py` are the existing pattern for a script that checks FO's records.

## Captain's words

Captain 2026-10-13, in chat: 「向 kc-dev-flow-2 回報的問題可以回報，這個是否可以排進清單處理修復跟補強？」

## Scope

Candidates, each seen in an observer report (task named), for ideation to keep or drop:
- Dispatch checklists and scope notes name package scripts bare instead of `<package>/scripts/NAME.py` with the root substituted (workflow-checkout-must-match-trunk-readme, observer-before-merge-guard).
- A gate summary reports an unrun listed extension without the literal `<name> not run: <reason>` form (copilot-quota-refusal-is-not-a-review).
- `## FO alignment` records alignment as needed with no `Result:` line before dispatch (copilot-quota-refusal-is-not-a-review).
- A delivery gate names a PR head that no passing validation report names (observer-before-merge-guard).
- An ADR-settled decision is cited without the `Precedent: ADR <n> — 「<Words>」` form (observer-before-merge-guard).
- Wording gap: `Applied: none as of <sha>` is written for migrations; whether an ADR-only task owes it is unstated (workflow-checkout-must-match-trunk-readme).
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain asked for the fix.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
