---
title: "Retire the provider-backed planning path, so dev-flow's only intake is a committed brief"
status: backlog
source: Captain ruling 2026-09-14 in FO session
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: kc-dev-flow/S10
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: f0m9yytzq7sczkam7rrq9ym3
gates:
    version: 1
    records:
        - id: gate:f0m9yytzq7sczkam7rrq9ym3:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:f0m9yytzq7sczkam7rrq9ym3-backlog-1
              briefing:
                id: briefing:f0m9yytzq7sczkam7rrq9ym3:backlog:attempt-1:revision-1
                digest: sha256:928bbdba36ae552ea731cc789b8ee494aca34d2538d925fb82d9fa56ecfdcf06
                room-ref: ./retire-the-provider-backed-planning-path/review/backlog/briefing-1
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
in Linear; dev-flow simply stops reading it. The Captain defined the plan in that ruling as what a
user journey map converts into dev-flow input, and that producer already exists and is already
aligned: `kc-journey-map`'s `plan-release` mode loads the five-section admission format from
`kc-dev-flow:adopt-dev-flow` and emits a reviewed Development Brief. Both intake paths therefore
produce the same artifact and differ only in who authored it, so no new input format is owed.

## Accepted outcome

Dev-flow has one intake: a committed Development Brief or Exploration Brief. Who authored that
brief — the Captain dictating, or `kc-journey-map`'s `plan-release` converting a journey map — is
outside dev-flow's contract, and dev-flow gains no reader for either.
`source` survives as free-text provenance and may hold a Linear URL. The Planning Receipt tuple,
its partial-tuple refusal, the engage-reconcile step, and both provider scripts leave the package
and this repository's Local Profile.

## Non-goals

- Stopping anyone from starting work in Linear, or removing Linear from the Captain's own habits.
- The `Fixes DEV-N` close line and anything else `pr-merge` or `kc-ship-flow` owns at delivery.
- Changing `kc-journey-map`, or building any second producer of a Development Brief.
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

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    Kent selected Pilot on 2026-09-14. Removing an intake path is a permanent
    contract change, not a disposable experiment. No consumer must act to take
    the new version: measured on 2026-09-14, none of the three adopter
    repositories binds the reader or comparator in its Local Profile, and the
    manifest's required_bindings carries no planning row. The one bound
    consumer is this repository, and AC-4 carries that edit.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Keep `source` as free-text provenance that may hold a Linear URL, and remove only the tuple that turned it into planning evidence.
      - Name where the removed engage-reconcile duty goes, or state that it goes nowhere because nothing consumed it.
      - Leave delivery untouched; the close line belongs to pr-merge and kc-ship-flow.
    implementation:
      - Remove both scripts, their tests, and their manifest entries in one change.
      - Strip the provider-backed route, engage reconcile, and partial-tuple refusal from shipped skills and references.
      - Edit this repository's Local Profile and `dev-52-inventory-kc-dev-flow-removal-candidates` in the same delivery.
    testing:
      - Cover the two frontmatter cases in AC-1 in the existing loader tests.
      - Run the package contract test and the existing loader and route suites; add no standing CI lane.
  scope_boundary: >-
    The accepted outcome and complete non-goal list in this task remain unchanged.
    Excludes delivery close lines, any change to kc-journey-map, other adopters'
    records, and renaming the standalone term.
  semantics_unchanged: false
  promote_when:
    - An adopter is found binding the reader or comparator and must edit owned records to upgrade.
    - Delivery close lines or another plugin's contract enters scope.
  decision:
    authority: Kent (Captain)
    at: 2026-09-14T00:00:00Z
```
