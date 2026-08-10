---
title: Size the first accepted outcome to one releasable journey
source: Captain ruling on iterative delivery, 2026-08-10; Relay remote-review dogfood
product: kc-dev-flow
sprint:
id: nzae8nwgvrg9dhwc6kz0kfsy
status: implementation
lane: main
started: 2026-08-10T14:35:14Z
design: required
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/kc-dev-flow-iterative-outcomes
---

## Problem

The kernel defines independent surfaces and the smallest sufficient route, but the
Engineering Judgment procedure does not apply those definitions to size the accepted
outcome before acceptance criteria expand. Relay's `remote-review-entrypoint`
combined its first owner-to-reviewer-to-owner journey with a second reviewer role,
three-author aggregation, old-snapshot recovery, batch conflict handling, and
freshness behavior under a four-human-hour appetite. The resulting outcome was
coherent but not iteration-sized.

The captain's ruling is: a first release is not partially correct across the whole
problem. It is complete for one primary releasable journey while leaving independent
optional value to later iterations. Safety, data
integrity, destructive-action protection, and compatibility remain complete hard
invariants; they are not deferred coverage.

## Appetite and stop condition

One implementation session, estimated at 60 minutes. Stop and re-cut at 90 minutes
or if the change requires a kernel edit, new mod, runtime classifier, state/schema
field, or second canonical policy surface. The mirrored self-adoption copy is not a
new policy surface.

## Proposed approach

The fastest path and smallest cut are the same: add one pre-AC appetite and surface
test to the existing Engineering Judgment procedure, protect it in the existing
package contract test, and pressure-test the oversized and safe plans with fresh
Claude Opus high judgment. The unsafe plan remains a regression check for existing
kernel behavior, not a reason to add a second rule.

The more thorough option not taken is a kernel edit, new policy mod, numeric coverage
calculator, work-item field, or executable scope classifier. None is needed: the
kernel already defines independent surfaces and outcome discipline, and the EM
already loads Engineering Judgment. The `science-officer-em` skill needs no second
copy of the rule.

## Design determination

`required`. This changes the portable EM recommendation contract. The contract shape
is one judgment step using the kernel's existing definitions; no new invocation,
report field, adoption path, or runtime mechanism is introduced.

## Reverse-recovery audit

Audit target: `origin/main@334764d6779aaafcb2621e63036fadc56f3146c2`.

| Surface | State | Evidence and decision |
|---|---|---|
| Outcome authority | `WORKING_UNIT_UNPROVEN` | `kernel.md:69-86,110-156` protects an accepted route, defines lifecycle-independent surfaces, and requires falsifiable outcomes. Reuse it unchanged. |
| EM synthesis | `EXISTS_BROKEN` | `engineering-judgment.md:36-58` weighs value and cost and may return `narrow`, but has no explicit slice or appetite-fit test before `proceed`. Repair only this seam. |
| EM invocation | `WORKING_UNIT_UNPROVEN` | `science-officer-em/SKILL.md:13-44` loads and applies the selected mod. Do not duplicate the rule here; the pressure scenarios are its behavioral disproof hook. |
| Package enforcement | `WORKING_UNIT_UNPROVEN` | `scripts/kc-dev-flow-contract-test.py:286-430` checks the canonical reference and vendored copy. Extend this existing check; do not add a harness. |

Disproof hook: if the unchanged policy returns `narrow`, `proceed`, and `return`
for the three pressure plans below for the intended structural reasons, this change
has no value and should stop.

## Acceptance criteria

**AC-1 — EM sizes the outcome before AC expansion.**
Before recommending `proceed`, Engineering Judgment checks the exit criterion
against appetite and derives independently releasable value surfaces from the
kernel's existing lifecycle-independence definition. More than one defaults to
`narrow`; one primary journey with its hard invariants may `proceed`. Actor count is
evidence of possible independent obligations, not a split rule.

Verified by: the package contract test plus fresh pressure runs whose rationales cite
the new slice step: oversized Relay receives `narrow` for its appetite mismatch and
independent value surfaces, while the safe owner-reviewer journey receives `proceed`
even though its one value surface spans client entry, relay transport, and viewer
handoff. Falsified by: remove the new step; the contract test fails and the oversized
plan loses that explicit controlling rationale, even if general synthesis still
chooses `narrow` as it did at baseline.

## Test plan

1. Run the three pressure plans against the unchanged policy and record the baseline
   routes and reasons.
2. Add the package contract assertions and observe their focused RED against the
   unchanged references.
3. Make the one minimal canonical edit and mirror it byte-for-byte into this
   repository's selected `_mods`.
4. Observe the focused GREEN, then run the full kc-dev-flow and marketplace gates.
5. Run the oversized and safe plans with Claude Opus high at the exact revision and
   require the new step to control their rationales. Re-run the unsafe plan only as
   a regression check for the existing kernel clauses that already returned it.

## Engineering judgment

```yaml
engineering_judgment:
  question: Should kc-dev-flow constrain first-iteration outcome size before AC drafting?
  revision: origin/main@334764d6779aaafcb2621e63036fadc56f3146c2
  evidence_synthesis: Relay's four-hour outcome spans two non-owner reviewer roles, aggregation, cross-time recovery, and batch/freshness behavior; the current kernel and EM procedure contain no pre-AC slice test.
  adjudications:
    - finding: exit-criterion-overdesign
      disposition: supported
      basis: Relay task AC-4 and AC-5 add independently deferrable value beyond the first owner-reviewer-owner journey.
    - finding: ac-wording-alone-caused-delay
      disposition: unsupported
      basis: Broad scope can cause both longer AC prose and implementation time; the policy change targets outcome shape, not word count.
  risk_tradeoff: A narrow judgment rule buys earlier usable delivery and cheaper correction; an executable classifier would add a second mechanism and false precision, so the existing kernel plus EM mod is the cheaper alternative.
  recommendation: Add one pre-AC appetite and surface test to Engineering Judgment, then validate it with the oversized and safe pressure plans.
  route: proceed
  confidence: high
  dissent: A fixed coverage percentage has no stable denominator and must not become a policy target or gate.
  disproof_condition: The unchanged Engineering Judgment procedure already contains an explicit appetite and surface-independence test before proceed.
  authority_boundary: The captain retains scope and exceptions; EM recommends; work-item and delivery authorities retain transition and release decisions.
```

## Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is a hidden
assumption that lifecycle independence always distinguishes optional value from the
technical seams required by one journey.

## Implementation sizing

One worker session. The one policy edit and one existing contract-test edit are one
behavioral slice; the vendored copy is a mechanical mirror.

## Doc diff

None outside the authoritative Engineering Judgment reference. Package and root
READMEs list the mod and skill but do not restate its procedure.

## Out of scope

- A numeric `75%` field, score, calculator, or gate.
- A kernel edit, new mod, skill, script, schema field, or report envelope.
- Re-cutting or implementing Relay's active task in this delivery.
- Relaxing validation, exact-revision delivery, or any hard invariant.

## Stage Report: ideation

TL;DR: The second returned review hit the declared stop condition, so the task was
re-cut to one canonical Engineering Judgment edit plus one existing contract-test
edit. Actor count and `75%` are not gates; the existing kernel supplies the surface
definition unchanged.

- DONE: Bind the gap to `origin/main@334764d6779aaafcb2621e63036fadc56f3146c2`.
  The unchanged kernel defines independent surfaces and protects accepted routes;
  Engineering Judgment can return `narrow` but has no appetite or pre-AC slice-size
  trigger.
- DONE: Run the unchanged-policy pressure baseline with Claude Opus high.
  Scenario A returned `narrow` only through general synthesis and reported a partial
  policy gap because neither policy contains an appetite or sizing trigger. Scenario
  B returned `proceed` by default plus general synthesis. Scenario C returned
  `return` from existing missing-evidence and enforcement-point clauses. The current
  policy therefore reaches the desired routes, but only the unsafe deferral has an
  explicit controlling rule.
- DONE: Obtain the first fresh ideation review from Claude Opus high.
  It returned `return` with two Material findings and confirmed zero unnecessary
  surfaces or ACs: the test plan omitted the unchanged-policy baseline, and AC-3 did
  not bind a claimed surface count to the kernel's existing independence test.
  Both corrections are incorporated without a new scenario or policy surface.
- DONE: Obey the second-correction stop condition.
  The corrected task's second Opus high review returned two evidence-binding
  findings: the post-change routes could match baseline for different reasons, and
  the safe scenario did not explicitly span multiple technical components. Rather
  than add more policy, the task was re-cut from two canonical surfaces to one. AC
  pass conditions now require the new clause's rationale to differ from baseline,
  and the safe scenario spans client, relay, and viewer without becoming multiple
  value surfaces.
- DONE: Remove the over-determined hard-invariant AC after the third Opus high gate.
  The unchanged policy already returns the unsafe scenario through missing-evidence
  and enforcement-point clauses, so a new classification rule could not produce a
  failure-capable behavioral check. The scenario stays as regression coverage; the
  new policy and sole AC now address only the demonstrated appetite/surface gap.
- DONE: Converge the ideation gate.
  The third gate found no defect in the remaining AC-1 or one-surface delivery shape;
  its sole Material finding was AC-2's inability to fail. Removing that AC satisfies
  the gate's stated decision rule, leaving zero Material findings in the approved
  implementation scope.
- DONE: Apply the captain's lightness challenge.
  A fixed `75%` target is removed from policy because no stable problem-space
  denominator exists. Actor count is also removed as a mandatory split rule; it is
  evidence of possible independent obligations, while observable lifecycle
  independence remains the deciding surface test.
- DONE: Complete ideation discipline.
  Scope, appetite and stop condition, cheapest path, rejected mechanisms,
  reverse-recovery audit, design determination, one falsifiable AC, pre-mortem,
  one-worker sizing, doc diff, and explicit non-goals are recorded.

### Summary

Add one explicit pre-AC appetite and surface test to Engineering Judgment without
changing the kernel or adding an executable classifier.

## Stage Report: implementation

TL;DR: Implemented the approved one-surface change at
`e6930fe74df014370e52c8cc2d13dbd63461f270`; the canonical policy, vendored copy,
and existing contract test are the only changed files.

- DONE: Observed RED before the policy edit. The package contract failed with
  `engineering judgment is missing: before acceptance criteria expand`.
- DONE: Added the named `Iteration-size precheck`, bound surface counting to the
  kernel's `Route discipline`, and made multiple surfaces default to `narrow`
  unless an exact captain-approved exception is recorded by work-item authority.
- DONE: Kept the canonical and vendored policy copies byte-identical and bumped
  only the policy-local version from `0.1.0` to `0.2.0`; release-please retains
  ownership of plugin versions.
- DONE: Strengthened the existing contract test to pin the operative route,
  exception authority, technical-seam guard, and top-level heading structure.
- DONE: Ran the complete repository gate set. Release metadata, version parity,
  skill frontmatter, plugin release contract, work-context contract,
  kc-dev-flow contract, state prerequisite contract, mirror comparison, and
  `git diff --check` all passed.
- DONE: Stayed inside the stop condition. No kernel, skill, new mod, runtime
  classifier, schema field, or second canonical policy surface was added.
