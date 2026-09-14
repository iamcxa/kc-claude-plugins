---
title: "Retire the provider-backed planning path, so dev-flow's only intake is a committed brief"
status: backlog
source: Captain ruling 2026-09-14 in FO session
product: kc-dev-flow
planning-window:
planning-outcome:
sprint:
sprint-readiness: defer
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: f0m9yytzq7sczkam7rrq9ym3
---

## The problem

kc-dev-flow carries two intake paths. A standalone item runs on a Captain-approved committed
brief. A provider-backed item additionally records a complete Planning Receipt
(`source`, `planning-window`, `planning-outcome`), and dev-flow then owns machinery to keep that
receipt honest: `linear-admission.py`, `engage-reconcile.py`, the engage-reconcile comparison at
every provider-backed engage, and the partial-tuple refusal. Both scripts are declared resources
in `contract-manifest.json`.

The second path is almost entirely unused. In this repository's own execution state, one active
work item of 89 carries a complete Planning Receipt — `dev-52-inventory-kc-dev-flow-removal-candidates`,
still in `backlog`, never started. Eight items including archived ones ever carried a
`planning-window`. Every other item uses `source` as free-text provenance: `captain`,
`GitHub issue`, `EM validation gate`. Of the three adopter repositories checked on 2026-09-14
(`subspace-relay`, `carlove-v1`, `subspace-v0`), none binds the reader or the comparator in its
Local Profile; `subspace-relay` records Linear as a future binding that never landed. The
manifest's `required_bindings` list contains no planning row at all, so no adopter's
`kc-dev-flow-local-profile/v1` check depends on these resources.

The Captain ruled on 2026-09-14 that work reaches dev-flow either from his own dictation or by
expanding a plan, and that the flow no longer takes over the Linear route. A user may still start
in Linear; dev-flow simply stops reading it.

## Accepted outcome

Dev-flow has one intake: a committed Development Brief or Exploration Brief. Who authored that
brief — the Captain dictating, or a planner expanding a plan — is outside dev-flow's contract.
`source` survives as free-text provenance and may hold a Linear URL. The Planning Receipt tuple,
its partial-tuple refusal, the engage-reconcile step, and both provider scripts leave the package
and this repository's Local Profile.

## Non-goals

- Stopping anyone from starting work in Linear, or removing Linear from the Captain's own habits.
- The `Fixes DEV-N` close line and anything else `pr-merge` or `kc-ship-flow` owns at delivery.
- Defining the plan object, or building any planner that produces one.
- Renaming the `standalone` term once it is the only intake.
- Editing any other adopter's records.
- Reviving the retired local Linear reader that 4.3.0 already removed.

## Acceptance criteria

- **AC-1** An item whose frontmatter carries a `source` string and empty `planning-window` and
  `planning-outcome` loads through `profile-contract-loader.py` at every working stage, and an item
  that still carries all three loads the same way with no provider invocation.
- **AC-2** `scripts/linear-admission.py` and `scripts/engage-reconcile.py`, their tests, and their
  `contract-manifest.json` entries are absent, and `kc-dev-flow-contract-test.py` exits 0.
- **AC-3** No shipped skill or reference states a provider-backed route, an engage reconcile, a
  Planning Receipt, or a partial-tuple refusal as a requirement.
- **AC-4** This repository's `docs/dev/README.md` Local Profile no longer binds a planning reader
  or comparator and no longer carries an Engage reconcile section, and the loader runs clean
  against an existing committed work item after that edit.
- **AC-5** `dev-52-inventory-kc-dev-flow-removal-candidates` keeps its Linear URL in `source`,
  carries no `planning-window` or `planning-outcome`, and loads without refusal.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names
the changed premise, affected acceptance evidence, and recommended change or stop.
