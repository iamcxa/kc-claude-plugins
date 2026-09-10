---
title: "POC: test evidence-led dev-flow improvement on one real failure"
status: implementation
product: kc-dev-flow
sprint: S8
sprint-readiness: ready
started: 2026-09-10T04:10:01Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: 4n79qfrpfetj8vrpmdphpkwd
---

# Evidence-led dev-flow improvement POC

Decide whether a small skills-mcp-inspired change to experience capture improves dev-flow decisions enough to justify a later implementation proposal.

## Captain admission

Kent selected the dev-flow POC profile and accepted the presented experiment with "按建議" on 2026-09-10. The accepted budget is 15 minutes and at most four comparison executions. This standalone Captain-approved Exploration Brief has no Planning Receipt. Capture starts at the selected profile's first working stage after that chat admission; no ideation work is commissioned. State-only creation, stage dispatch, and evidence recording belong to this admitted run. No product commit, PR, merge, release, or terminal approval is granted.

The local S8 group is the existing kc-dev-flow slimming dogfood group; this task's question is whether additional guidance earns its cost. Scope stays on this task and does not engage other S8 tasks.

## Exploration Brief

- Decision: Is one evidence-led feedback improvement worth a separately approved delivery change?
- Falsifier: The unchanged baseline cannot reproduce a real failure, the candidate does not correct it, the normal case regresses, or the comparison is contaminated or lacks attributable evidence.
- Budget: 15 minutes from frontmatter started; at most four comparison executions in total. Preparation before admission is outside that measured experiment. No extra cycles or new paid provider arrangement.
- Stop: Stop immediately if the unchanged baseline shows no failure; otherwise finish one failing case and one normal case under baseline and candidate. At the limit record change with the strongest evidence. A normal tool call may finish, but start no additional proof after expiry.

## Accepted outcome

One evidence-backed proceed, stop, or change conclusion. Preserve actual prompts, outputs, tool effects, model/runtime identity, time and available token usage. Unknown measurements remain unknown. State the limit of a small one-run-per-condition exploration; do not claim a benchmark or population improvement.

## Non-goals

No shipped skill or kernel change, recurring harness or CI job, new feedback collector, automatic promotion, cross-project rollout, external messages, issue filing, PR, or alteration of unrelated task state. Temporary candidate instructions and scratch execution files are disposable. Durable evidence belongs only to this task's state record.

## Existing evidence to use

- Product snapshot: 6b408ac102978d4bbf3614a7109934191520aa9b.
- skills-mcp source snapshot: 5cd5389533f40b85ba6573fcb7f1d84c2086a282; engineering-journal records concrete friction and successful defaults, and its evaluation protocol separates frozen cases from answer keys.
- docs/dev/README.md, Placing a finding: existing rule-gap, enforcement-gap, local-instance and duplicate/no-change classification. Do not claim it is missing.
- Archived digest-effect-unmeasured.md, Step 0 result and Bound on this result: an earlier baseline had no measurable headroom with standing user instructions loaded. This is prior bounded evidence, not this run's result.
- Archived improvement-loop-never-ran.md, Outcome: the old transport was retired, and its proposed replacement was rejected after measurement. Do not restore it.
- Existing kc-plugin-forge clean-runner capability and kc-dev-flow skill-scenarios should be checked before inventing a mechanism. A fresh in-session agent still inherits global instructions; fresh context alone does not establish an uncontaminated baseline.

## Experiment procedure

1. Before editing a candidate, choose one real recurrence from retained dev-flow evidence and one normal control. Freeze the tasks and observable success/failure criteria. Prefer a failure where an agent adds a duplicate rule or collector instead of locating an existing rule and its execution seam.
2. Validate that the observation can distinguish no work, a bad action, and the expected action. Exercise the actual agent decision journey using one existing safe runner; prose-presence checks alone are not behavior evidence.
3. Run baseline on the failure case first. If it succeeds, stop with no measured headroom; do not use the remaining budget to hunt for a failure or change the rubric.
4. Only if it fails, create a disposable minimal candidate adding concrete request, misfiring instruction, correction, and successful counterexample capture. Run baseline normal, candidate failure, and candidate normal with the same model, runtime and input boundaries, for four executions total at most. Responders receive no answer key. Judge observed actions against the frozen criteria separately from candidate authoring; prefer deterministic outcomes. No additional model critic beyond the four-execution ceiling.
5. Return the direct POC result and evidence. Missing isolation, unavailable runner, absent usage metadata, or an unexercised seam must limit the conclusion rather than become an invented success.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  basis: One internal disposable experiment with no production data, persistent product state, consumer migration, or operational commitment.
  route: [build, prove]
  obligations:
    architecture: [Use the existing feedback placement and runner seams.]
    implementation: [Create only disposable candidate instructions and task-owned evidence.]
    testing: [Freeze a real failure and normal control, observe the baseline first, and compare only when headroom exists.]
  scope_boundary: No shipped plugin changes, recurring automation, external messages, new provider spend, issue or PR creation, or unrelated state changes.
  poc_decision: Decide whether the observed feedback improvement merits a later implementation proposal.
  poc_falsifier: Baseline succeeds already, candidate fails to improve, normal behavior regresses, or isolation and evidence are insufficient.
  poc_budget: Fifteen minutes from started and at most four comparison executions; no extra rounds.
  poc_stop_when: First baseline no-headroom result, completed four-condition comparison, inability to run validly, or budget exhaustion.
  poc_artifact: disposable
  poc_safety_boundary: none
  poc_decision_ready_minutes: 15
  promote_when: [Captain accepts retained product behavior or cross-project reuse as a separate commitment.]
  decision:
    authority: Kent
    at: 2026-09-10T04:10:01Z
```
