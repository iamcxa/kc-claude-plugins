---
title: "Replace kc-dev-flow contract-test phrase pins with behaviour assertions a mutation can redden"
status: ideation
source: https://linear.app/duckbase-co/issue/DEV-51/replace-kc-dev-flow-contract-test-phrase-pins-with-behaviour
product: kc-dev-flow
planning-window: Linear Cycle d1c96803-02fa-4323-b3a8-2fc44cc43699 2026-09-10T16:00:00.000Z/2026-09-24T16:00:00.000Z
planning-outcome: Linear Project 4746021d-2930-4589-80a0-b7b3d1d70eeb kc-dev-flow slimming dogfood sha256:0599c390742642a1edf03e07a50c28635ff41d3ef77188e076cb2f02e6d85372
sprint: S8
sprint-readiness: ready
started: 2026-09-02T14:23:40Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: m29y546p4sh77vbs2dv09gkp
gates:
    version: 1
    records:
        - id: gate:m29y546p4sh77vbs2dv09gkp:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:m29y546p4sh77vbs2dv09gkp-backlog-1
              briefing:
                id: briefing:m29y546p4sh77vbs2dv09gkp:backlog:attempt-1:revision-1
                digest: sha256:7ae98598b34e8752d28496fb24b9d24a58db08b6fc675d9dcd83c2e78b21e62a
                room-ref: ./dev-51-behaviour-assertions-for-contract-pins/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:m29y546p4sh77vbs2dv09gkp:backlog:1
                briefing: briefing:m29y546p4sh77vbs2dv09gkp:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-02T14:10:08.252464Z"
                decision: approve
                reason: 'Captain approved DEV-51 into Pilot ideation: Project kc-dev-flow slimming dogfood, Cycle 2, sprint S8; semantics_unchanged true, the equivalence instrument is the item''s own deliverable.'
              application:
                target-stage: ideation
                state: consumed
---

## The problem

`scripts/kc-dev-flow-contract-test.py` guards the kc-dev-flow contracts largely by wording. Nineteen `phrase in normalized_<document>` loop sites pin sentences in `kernel.md`, `continue-dev-flow/SKILL.md`, the package README, the workflow README, adopter and migration documents, and others (count taken 2026-09-02 by grepping the require lines). A slimming deletes wording by definition, so this instrument reddens when a sentence is shortened and stays green when a rule is dropped but its pinned words survive elsewhere. It cannot distinguish "rule kept, said shorter" from "rule removed". Mutation-style checks exist in the file, but for guard code paths, not for the prose rules the pins cover.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: Bounded real use by this repository's own CI; the change touches only repo-local test files and behavior-diff cases, no adopter-visible contract, release, or rollback obligation, and iteration is expected as pin groups are converted in batches.
  route: [shape, build, verify-deliver]
  obligations:
    architecture: [Two-tier instrument model — deterministic assertions on loader, guard, and close-guard observable outputs for enforced rules, sampled behavior-diff cases for agent-only prose rules, wording-only pins recorded with a reason]
    implementation: [Replace pins in scripts/kc-dev-flow-contract-test.py per tier without removing any pin before its replacement reddened on the same removal, keep the multi-profile gate and ablation green, measure and record per-case behavior-diff cost]
    testing: [Every tier-1 replacement has a recorded mutation run, every tier-2 case has with-and-without runs plus one deliberately removed rule it flags, the old assertion is run against each mutation its replacement claims to cover before the old one is removed]
  scope_boundary: No contract slimming, no generic without-it harness, no model-backed check in CI, no change to loader or guard behaviour, no pin deleted without a reddened replacement.
  semantics_unchanged: true
  decision:
    authority: person:captain
    at: 2026-09-02T14:07:13Z
```

## Accepted outcome

The contract test grades the behaviour a rule produces, at two tiers, and every replacement has been seen to fail before the pin it replaces is removed.

* Tier 1, deterministic: a rule that the profile loader, admission guard, POC close guard, or contract test itself enforces is asserted through that mechanism's observable output (loader field, refusal message, exit code), not through the sentence that describes it.
* Tier 2, sampled: a rule only an agent interprets gets one recorded `behavior-diff` case (the same task run with and without the rule) or is recorded as wording-only with the reason it cannot be sampled.
* Proof per replacement: remove the rule, observe the new assertion or case redden and name the rule, restore it, observe green. A pin whose replacement was not seen to fail on the same removal stays in place.

## Non-goals

- Do not slim any contract in this item. The knife is a later item.
- Do not add a generic without-it harness or a model-backed check to CI; the per-case cost of `behavior-diff` is unmeasured until this item measures it.
- Do not change the behaviour of the loader, guards, or close guard.
- Do not delete a pin whose replacement has not reddened on the same deliberate removal.
- Do not lower coverage: an old assertion is run against each mutation its replacement claims to cover before the old one is removed.

## Acceptance criteria

- **AC-1** A table lists every phrase-pin loop site with its tier (1, 2, or wording-only) and one reason each.
- **AC-2** Every tier-1 replacement has a recorded mutation run: rule removed, new assertion fails naming the rule, rule restored, assertion passes.
- **AC-3** Every tier-2 case has a recorded run with and without the rule, plus one deliberately removed rule that the case flags; the wall-clock and token cost per case is measured and recorded.
- **AC-4** For each removed pin, the old assertion was run against the same mutation and its result recorded, so no regression the old check caught is lost without being named.
- **AC-5** `python3 scripts/kc-dev-flow-contract-test.py` passes on the unchanged tree after the change, and the count of remaining wording-only pins is recorded with a reason each.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

Also route back when a tier-2 case cannot be made to redden for a rule the slimming intends to touch, or when the measured per-case cost makes sampling every touched rule unaffordable; either is a planning delta, not a reason to keep the wording pin and call it behaviour.

## Measurement

Not yet measured. Shape records the pin inventory (20 loop sites, 31 require lines on main at f47fd8ca), the `where it touches` table, and stop numbers; build records per-case behavior-diff cost and the count of remaining wording-only pins.
