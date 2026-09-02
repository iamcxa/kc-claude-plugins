---
title: "kc-dev-flow: unify the necessity vocabulary across kernel and reverse-recovery, and bind the equivalence instrument"
status: backlog
source: https://linear.app/duckbase-co/issue/DEV-46/kc-dev-flow-unify-the-necessity-vocabulary-across-kernel-and-reverse
product: kc-dev-flow
planning-window: Linear Cycle d1c96803-02fa-4323-b3a8-2fc44cc43699 2026-09-10T16:00:00.000Z/2026-09-24T16:00:00.000Z
planning-outcome: Linear Project 4746021d-2930-4589-80a0-b7b3d1d70eeb kc-dev-flow slimming dogfood sha256:0599c390742642a1edf03e07a50c28635ff41d3ef77188e076cb2f02e6d85372
sprint: S8
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: 50c1y5wf7dzh0ww2a9qajn47
---

## The problem

Two contracts grade the same question — does a surface earn its place — in two
disjoint vocabularies, and no sentence says how the two readings compose.

`reverse-recovery-audit.md` classifies need as `REQUIRED`,
`NO_OBSERVED_CONSUMER`, or `UNKNOWN`, established by search and justified by a
named consumer or contract. `kernel.md`'s minimal-necessity condition maps a
surface to the accepted goal, a named falsifier, a safety boundary, or a
required lifecycle obligation, established by execution. A safety-boundary
surface is therefore `NO_OBSERVED_CONSUMER` under the audit and mapped under the
kernel at the same time, and nothing states which reading wins.

Two further consequences of the same split: the audit's `disproof_hook` and the
kernel's without-it observation are the same evidence primitive under two names
at two cost tiers, and the kernel's implementation-exit comparison enumerates
only added files, dependencies, abstractions, tests, and comments — no clause
grades a removal, although a removal is a change whose necessity claim is
identical in form.

Separately, a change may declare at shape that it changes no observable
semantics. Goal sufficiency binds that declaration to the accepted goal only
through the Development Brief's `AC-N`, and no contract requires that a
declared-unchanged change carry an equivalence instrument, nor that the
instrument have been seen to fail. A behaviour-preserving refactor can pass with
no instrument capable of detecting a behaviour change.

This revisits a decision that already had evidence. The completed item
`subtractive-first-bounded-irreducibility` (PR #199, verdict passed) decided to
place the subtractive predicate in the kernel and leave the reverse-recovery mod
unchanged, on the stated basis that it "already owns the three need outcomes and
the removal authority boundary." The removal-authority half of that decision
stands and is a non-goal below. The new evidence is only that the two
vocabularies were never shown to compose, and the three consequences above are
what that costs.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: production
  recommended: production
  basis: Both contracts are vendored by external adopters (subspace-relay, carlove-v1); renaming the reverse_recovery need axis is consumer-visible and may need a migration, and no evidence yet shows adopters absorb it by taking the new version.
  route: [shape, build, verify]
  obligations:
    architecture: [One necessity predicate named once with two instrument tiers and one removal authority, removal graded by the same predicate as retention, an equivalence-instrument requirement bound at a named enforcement point]
    implementation: [Edit kernel.md and reverse-recovery-audit.md canonical copies and keep the loader-served copies identical, rewrite contract-test and ablation assertions per renamed boundary without losing a regression they caught, record any adopter migration with the version that carries it]
    testing: [Contract test and minimal-stack ablation reject each renamed boundary for its named reason, a safety-boundary surface with no observed consumer classifies identically under both contracts, a declared-unchanged change without an instrument is refused at the named enforcement point and the refusal is observed]
  scope_boundary: No merge of the two contracts, no change to the removal authority boundary, no aggregate minimality gate, no new receipt or harness, no routing or gate-authority change, no fourth profile.
  decision:
    authority: person:captain
    at: 2026-09-02T07:48:50Z
```

## Accepted outcome

One necessity predicate, named once, with two instruments at two cost tiers and
one removal authority. A reader of either contract reaches the same
classification for the same surface. A removal is graded by the same predicate
as a retention. A change that declares its observable semantics unchanged names
the equivalence instrument that would have caught a change, and that instrument
has been seen to fail before it is trusted.

## Non-goals

- Do not merge `reverse-recovery-audit.md` into `kernel.md`, or fold either into
- Do not change the removal authority boundary. A search result stays a removal
- Do not make aggregate minimality a gate. LOC and file counts stay diagnostic
- Do not add a new receipt, registry, script, CI job, reviewer loop, or generic
- Do not change profile routing, stage order, gate authority, or the
- Do not add a fourth work profile for refactor-shaped work.

## Acceptance criteria

- **AC-1** The need axis of `reverse-recovery-audit.md` and the mapping targets
  of the kernel's minimal-necessity condition use one vocabulary, and a
  safety-boundary surface with no observed consumer classifies identically under
  both contracts.
- **AC-2** The audit's `disproof_hook` and the kernel's without-it observation
  are one named primitive with two declared tiers, and each contract states
  which tier it uses and what that tier can and cannot conclude.
- **AC-3** The kernel's implementation-exit comparison grades removed surfaces
  by the same predicate as retained surfaces, and a removal with no necessity
  claim is rejected for that named reason.
- **AC-4** A change that declares its observable semantics unchanged is refused
  at its verification boundary until it names an equivalence instrument and
  supplies evidence that the instrument was observed to fail against a case it
  must flag.
- **AC-5** `scripts/kc-dev-flow-contract-test.py` and the minimal-stack ablation
  test reject each renamed boundary for its named reason; no assertion that
  previously caught a semantic regression is lost in the rename.
- **AC-6** Canonical `kc-dev-flow/references/` and self-adopted
  `docs/dev/_mods/` copies of both contracts stay byte-identical, or the
  installed-plugin resolution has already removed the vendored pair.
- **AC-7** Every adopter-visible rename is reachable by taking the new plugin
  version, or the item records the exact migration an adopter must run and the
  version that carries it.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning
delta that names the changed premise, affected acceptance evidence, and
recommended change or stop.

Also route back when: a single unified vocabulary cannot express both a
search-tier and an execution-tier conclusion without weakening the removal
authority boundary; an adopter is found to parse the current `need` enum in a
way no plugin version can migrate; or the equivalence requirement cannot be
bound at a verification boundary without adding a new receipt or harness.

## Measurement

Not yet measured. Shape records the `where it touches` table and stop numbers against the delivery base; build records the diff counts as diagnostics.
