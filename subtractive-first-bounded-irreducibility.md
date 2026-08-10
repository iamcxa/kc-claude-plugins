---
title: "kc-dev-flow: prove bounded surface necessity before adding layers"
source: "Captain-approved subtractive-first pilot for PR #199, 2026-08-11"
product: kc-dev-flow
sprint: S1
status: implementation
lane: main
design: required
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/kc-dev-flow-release-batch
pr: "#199"
id: mwb53mqbayj4rrbx62zxsyer
started: 2026-08-10T22:53:00Z
---

## Problem

Agents can satisfy additive workflow guidance by keeping every proposed layer;
the current reverse-recovery and changed-file-to-AC rules do not require an
observed without-it failure before a new surface survives. This makes "smallest
sufficient" reviewable but does not make subtraction the operational default.

## End value

For non-trivial brownfield work, planning derives the candidate surface set
backward from the accepted outcome, tries subtraction before addition, and
retains a new surface only with bounded evidence that removing or bypassing it
breaks a named acceptance criterion. Unknown obligations never authorize
deletion. Known-cause single-seam defects keep the lean route.

## Scope

- Add a tri-state subtractive-first rule to the portable kernel and existing
  local stage gates, reusing reverse-recovery's classifications unchanged:
  bounded retention, removal candidate, or `UNKNOWN`.
- Require a compact necessity witness for each retained new surface or genuinely
  inseparable surface group.
- Default delivery to one independently deliverable minimal PR targeting trunk;
  permit a stacked PR only for dependent, independently reviewable and
  verifiable working slices when waiting for the lower PR blocks useful work.
- Pilot the rule in this repository before considering universal adoption.

No new registry, script, workflow capability, dependency engine, reviewer loop,
or per-edit behavioral gate is in scope. Stacked PR shape is not minimality
evidence. Physical removal and accepted scope changes remain captain-owned.

## Smallest route and reverse-recovery audit

| Surface | Completeness | Need | Decision |
|---|---|---|---|
| Kernel route/outcome discipline | `WORKING_UNIT_UNPROVEN` | `REQUIRED` | Extend its existing sufficient-seam rule with one subtractive predicate; do not add a second policy file. |
| Reverse-recovery audit | `WORKING` | `REQUIRED` | Reuse its completeness/need classification, bounded absence, and captain-owned removal rules unchanged. |
| Local ideation/validation gates | `EXISTS_BROKEN` | `REQUIRED` | They ask for the smallest cut but do not reject a retained addition lacking a without-it failure. |
| Work Control Profile | `WORKING` | `NO_OBSERVED_CONSUMER` for this pilot | Do not add a capability or adapter; the accepted pilot requires judgment packets, not a new executable surface. |
| PR delivery binding | `WORKING` | `REQUIRED` | Keep direct-to-trunk as default and add one conditional stack exception locally. |

The smallest route changes the canonical/vendored kernel pair, the already
mandatory local README, and the existing sprint order. It does not change the
reverse-recovery mod because that file already owns the three need outcomes and
the removal authority boundary. The disproof hook is an ideation packet whose
new surface has no named without-it failure: it must not advance.

## Mechanism necessity

- `Criterion:` AC-1 through AC-4.
- `Alternative:` add only local README wording; insufficient because the
  subtractive rule is portable outcome discipline and adopters must receive it.
- `Alternative:` add a Work Control Profile capability and adapter;
  insufficient because the pilot has no stable provider baseline and would add
  the enforcement surface it is trying to avoid.
- `Escape:` without the predicate, an agent can retain a new layer by reporting
  green tests or an unclosed search instead of demonstrating the named failure
  that makes the layer necessary.

## Design determination

`required` — this changes the ideation and validation rejection predicates and
the local delivery route.

## Acceptance criteria

**AC-1 — Non-trivial brownfield plans start from subtraction.**

The plan traces candidate surfaces backward from the accepted outcome and
records one of three results per existing surface: a named AC failure after
removal or bypass supports bounded retention; green governing evidence with
closed need and observation boundaries makes it a removal candidate; an
unclosed obligation or inadequate instrument records `UNKNOWN`, preserves the
existing surface, and cannot support deletion or an irreducibility claim. A
proposed new surface advances only on the first outcome; green or `UNKNOWN`
returns the addition. Verified by: three adversarial ideation packets covering
all outcomes. Falsified by: a plan retaining a new surface without a named
without-it failure, or treating `UNKNOWN` as deletion evidence.

**AC-2 — Addition grows only from the residual tree.**

After captain-approved removals, implementation sizes against the remaining
tree and adds only the smallest seam that turns the first relevant red AC green.
Each retained addition records the surface, served AC, without-it mutation or
bypass, observed failure, cheaper alternative, and insufficiency. Known-cause
single-seam defects add no new ceremony. Verified by: the local ideation and
validation predicates plus a fresh exact-revision EM exercise. Falsified by: an
addition surviving with no necessity witness or by forcing the pilot onto the
defect route.

**AC-3 — Validation rejects reducible additions without over-deleting.**

Validation challenges every retained new surface or genuinely inseparable group
with the cheapest instrument able to fail and preserves same-kind runtime
observation for wiring claims. A new surface with green or `UNKNOWN` evidence
returns to implementation or ideation instead of shipping. For an existing
surface, green evidence creates only a captain-disposed removal candidate and
`UNKNOWN` preserves it outside the bounded claim. Verified by: adversarial
validation packets and exact-head EM review. Falsified by: self-attested
irreducibility, unit-only wiring proof, or physical deletion without captain
authority.

**AC-4 — PR topology remains lean and conditional.**

One independently deliverable minimal PR targeting trunk is the default. A
stack is allowed only when it contains at least two dependent working slices,
each independently reviewable and verifiable, and waiting for the lower PR to
merge blocks useful work. Verified by: local delivery wording and one stack/no-
stack decision exercise. Falsified by: stacked PR as the default or as proof of
minimality.

## Appetite and pilot observations

One policy-only worker. Keep the local workflow README below 700 lines and add
no executable enforcement surface. Observe first-draft additions converted to
reuse or removal, materially reverted removals, escaped obligations, and
validation time against the captain's declared appetite. Pilot evidence, not a
second model opinion, decides whether the rule becomes a universal default.

## Ideation EM judgment

Fresh high-reasoning EM reviewed conversation artifact `subtractive-first-v1`
against product revision `c48a9e97f1614d80d8220ac4c80b4df993db09fb` and
returned `narrow / high`, `multi_model: not_needed`. It supported the reversed
burden of proof and bounded ablation, rejected green evidence as deletion
authority, kept stacked PR conditional, and required the tri-state rule plus a
reversible non-trivial brownfield pilot. The captain accepted that narrowed
route in this task's source conversation.

## Stage Report: ideation

- DONE: The captain accepted a reversible, non-trivial brownfield pilot and kept
  known-cause single-seam defects on the lean route.
- DONE: Reverse recovery found no missing policy layer: extend the existing
  kernel and local stage gates; do not change the working audit mod or add an
  executable control.
- DONE: The three outcomes distinguish existing surfaces from proposed new
  surfaces so `UNKNOWN` cannot become either deletion authority or an additive
  escape hatch.
- DONE: One direct-to-trunk minimal PR remains the default; a stack is a
  conditional throughput route and never minimality evidence.
- DONE: Fresh high-reasoning EM returned `narrow / high`; multi-model review was
  not recommended because the unresolved cost claim needs pilot observation.

### Summary

Proceed with one kernel predicate, local gate/delivery wording, and three
adversarial packets. Add no enforcement mechanism.
