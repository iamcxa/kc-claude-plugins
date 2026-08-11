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
single-seam defects add no new ceremony. Verified by: the kernel predicate at
kc-dev-flow/references/kernel.md:138, the local gates at docs/dev/README.md:189
and docs/dev/README.md:257, and a fresh exact-revision EM exercise. Falsified by:
an addition surviving with no necessity witness or by forcing the pilot onto
the defect route.

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

## Captain scope revision — 2026-08-11

The captain accepted a second without-it pass over PR #199. The zero-consumer
product plan is a removal candidate because ROADMAP plus work-item authority
retain membership, order, ACs, and exit. The validation runbook's EM/multi-model
section is duplicate procedure already owned by the README and shipped skills.
ROADMAP keeps only iteration membership, order, dependency, and exit; task prose
stays in work-item authority. A file-specific history tombstone has no named
runtime failure and is returned. This supersedes the earlier validation cycle's
plan-retention mapping without changing AC-1 through AC-4.

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

## Stage Report: implementation

- DONE: Commit `636e6b9b100753e1fa2d566783b3de5451549f94` adds one
  portable subtractive predicate to the byte-identical canonical/vendored
  kernel pair.
- DONE: Existing surfaces now preserve `UNKNOWN` without claiming necessity;
  proposed new surfaces return on green or `UNKNOWN` and advance only on a
  named without-it AC failure plus an insufficient simpler alternative.
- DONE: The local ideation and validation stages carry explicit rejection
  predicates; known-cause single-seam defects stay exempt unless they propose a
  new surface.
- DONE: Delivery defaults to one independently deliverable smallest PR to
  `main`; a stack requires dependent, independently reviewable and verifiable
  working slices plus real wait-blocked work.
- DONE: No new file, script, policy mod, Work Control capability, reviewer loop,
  or per-edit gate was added. The existing absolutes registry received the one
  disposition required by its standing contract.
- DONE: Every changed file maps to an AC: the kernel pair and registry to AC-1,
  AC-2, and AC-3; local README to AC-1, AC-2, AC-3, and AC-4; ROADMAP and the
  existing release plan to the accepted iteration/delivery scope. No changed
  file is unmapped.
- DONE: Fresh checks pass at the committed revision: kc-dev-flow contract,
  state-prerequisite contract, 23 work-context cases, 40 skill frontmatters and
  12 lint cases, version parity, 32 release-metadata cases, release-please
  configuration, marketplace L0/L1/L2 clean-HOME installation, canonical/vendor
  byte identity, `git diff --check`, and the 389-line README budget.

### Summary

The implementation changes existing policy and authority surfaces only. Enter
fresh validation at exact revision `636e6b9b100753e1fa2d566783b3de5451549f94`.

## Validation cycle 0 — returned before product review

Fresh Claude Opus high session `a3982792-e77f-432d-875d-7edf50d5f7f5`
returned the packet because its exact revision expanded short SHA `636e6b9` to
the nonexistent `636e6b903e877456c3725243055feafebfa915f5`. It adjudicated the
seven packet routes on their premises but admitted no product evidence and made
no product finding. The actual commit is
`636e6b9b100753e1fa2d566783b3de5451549f94`. Reissue the complete artifact to a
fresh session; do not carry a verdict or product correction from cycle 0.

## Validation cycle 1 — narrow correction

Fresh Claude Opus high session `6c7bce28-08c5-4694-8ed9-902ffdfb8cf8`
reviewed the complete artifact at
`636e6b9b100753e1fa2d566783b3de5451549f94` and returned `narrow / high`,
`multi_model: not_needed`.

- AC-1 through AC-4 were met from the artifact, not the implementation report.
- P1 through P7 all routed to their expected outcomes; green and `UNKNOWN`
  cannot retain proposed additions, weak instruments return them, independently
  violable components cannot hide in one group, and stack topology remains
  conditional rather than minimality evidence.
- The six-file shape was retained: the kernel pair serves two consumers; local
  ideation and validation own independently decidable gates; the delivery row
  binds the conditional route; ROADMAP and the active plan prevent premature
  batch exit; the standing absolute registry requires one new disposition.
- One Material correction remained: inserting 15 kernel lines left twelve
  existing registry descriptions pointing at their old line numbers, including
  two entries claiming `kernel.md:138`. Commit
  `454507f7ba56ce79ca0414f1964af4e59126eea5` realigns those descriptions.
- The task's AC-2 validation anchor was corrected from README line 254 to 257.
  This is state evidence, not a product change.
- The undefined `non-trivial` qualifier remains a captain-accepted pilot scope
  and an observation target, not an implementation defect. Self-classified
  trivial work is the named escape to watch before universal adoption.

The correction changes exact HEAD, so cycle 1 does not close validation. Re-run
one fresh EM at `454507f7ba56ce79ca0414f1964af4e59126eea5`; add nothing and
reopen no already-settled packet or minimum-shape question unless the correction
changed it.

## Stage Report: validation

- DONE: AC-1 passes at exact head
  `454507f7ba56ce79ca0414f1964af4e59126eea5`: kernel line 138 carries the
  existing/proposed tri-state and README line 189 returns a new surface without
  a named without-it AC failure.
- DONE: AC-2 passes: the kernel records surface, served criterion, without-it
  instrument/result, simpler alternative/insufficiency, and the task's anchors
  at kernel 138 and README 189/257 all resolve.
- DONE: AC-3 passes: README line 257 re-challenges the retained addition,
  returns green or `UNKNOWN`, preserves existing `UNKNOWN` surfaces outside the
  claim, and keeps same-kind runtime evidence for wiring.
- DONE: AC-4 passes: README line 230 defaults to one smallest PR targeting
  `main`, requires all three stack conditions, and denies topology as minimality
  evidence; the Local Profile delivery row names the conditional route.
- DONE: `Lenses:` outcome necessity, authority, minimum shape, instrument
  validity, lifecycle independence, and delivery topology.
- DONE: `Diff coverage:` all six changed files and five logical surfaces mapped;
  removing any one loses a named consumer, gate, disposition, or batch-exit
  predicate. No new file or executable surface exists.
- DONE: `Adversarial:` cycle 1 exercised P1 through P7 from the exact shipped
  wording. Cycle 2 independently re-derived the correction and confirmed it did
  not change the settled packet routes.
- DONE: `Cross-model:` `not_needed`; both fresh EM rounds were high-confidence,
  the only Material finding was mechanical, and no contested call remains.
- DONE: `E2E:` not applicable to this policy/docs-only pilot. It makes no
  user-visible or full-stack behavior claim; real adopter behavior is the
  post-delivery pilot observation, not completion evidence for this change.
- DONE: `Origin re-observation:` not applicable. The accepted outcome is a
  bounded policy rejection predicate, not a defect observed through an external
  runtime; the seven adversarial packets exercise the claimed decision boundary.
- DONE: Fresh Claude Opus high session
  `58adac34-b674-457c-9bad-ffe8baa64ca9` returned `proceed / high`, AC 4/4,
  zero unresolved Material findings, and `multi_model: not_needed` at the exact
  corrected head.
- DONE: Fresh exact-head mechanical receipts pass: contract, canonical/vendor
  byte identity, diff check, 40 frontmatters, version parity, 389-line README,
  and task work-context. A full-file inspection accounts for all 23 kernel
  registry rows; the new row uniquely names line 138 and all twelve displaced
  rows name their current lines.

### Residual pilot observations

- The captain-approved `non-trivial` boundary may permit self-classification;
  watch that escape before deciding on universal adoption.
- The existing absolutes contract validates content hashes but not descriptive
  line locators. This correction needed manual arithmetic; that gap does not
  authorize a new checker in this task.

### Summary

`proceed / high` at `454507f7ba56ce79ca0414f1964af4e59126eea5`.
The task remains in `validation` until PR #199 merges with exact-head checks;
delivery, terminal verdict, and archive state are not claimed here.

### Exact-head PR receipt

PR #199 now points to `454507f7ba56ce79ca0414f1964af4e59126eea5`.
Portable suite, real-browser decision/proofs, version parity, and GitGuardian are
green; two conditional jobs are skipped. Fresh PR-level Claude Opus high session
`53ca4a4a-e114-4a4b-9412-ae0fbb0c0e0a` rebound all sixteen batch ACs and
returned `proceed / high`, zero Material findings, `multi_model: not_needed`.
The task is ready for review but remains non-terminal until authorized merge.
