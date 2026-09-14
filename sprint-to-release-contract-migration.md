---
title: "Rename the execution-grouping contract from sprint to release, so the execution record matches the planning artifact"
status: backlog
source:
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
id: tjxctad7413wyp3acfx8wzzp
---

## The problem

`kc-journey-map` now plans a release into a Development Brief (PR #419, merged 2026-09-11),
so the unit a planner hands to dev-flow is a release. The execution record still calls that
unit a sprint: `profile-contract-loader.py` reads `^sprint:` and `^sprint-readiness:` with two
hard-coded regexes and refuses dispatch when either is absent or not `ready`
(`frontmatter sprint must name an iteration`, `frontmatter sprint-readiness must be 'ready'`).
`docs/dev/ROADMAP.md` records the split twice in its own text: the `kc-journey-map` S1 and S2
headings each say the stored `sprint: SN` is a compatibility identifier held "until the separate
sprint-to-release contract migration". This is that migration.

Two boundaries are already known. Spacedock does not own the field — `internal/status/parse.go`
classifies `sprint`/`sprint-readiness` under the schema's `permissive_additions`, so the engine
needs no change and `spacedock refit` is not in the chain. And `release` is not a free word inside
kc-dev-flow: it was a Production route step, `route: [shape, build, verify, release]`, deleted in
the v3 route change, and a stale receipt still carrying it throws `stale route for production`. A third meaning is already live in this repository's Local Profile, where `planning-outcome` is described as a Linear Project held as one user-value `release package`; grouping cannot simply reuse that field, because a standalone item records no `planning-outcome` at all.

## Accepted outcome

An adopter names its execution group `release` in work-item frontmatter and dev-flow dispatches on
it, while an adopter that has not migrated keeps dispatching on `sprint` unchanged. The package
documents which word means the grouping field and which means the deleted route step, so neither
`MIGRATION.md` nor a receipt error reads as a return to the retired route.

## Non-goals

- Changing Spacedock canonical fields, the entity schema, or anything `spacedock refit` syncs.
- Changing planning-provider semantics: a Linear Cycle stays the planning window and a Linear
  Project stays the planning outcome.
- Rewriting adopter state automatically, or migrating `subspace-relay`, `carlove-v1`, or
  `subspace-v0` inside this item.
- Reviving the deleted `release` route step.

## Acceptance criteria

- **AC-1** A work item whose frontmatter carries `release` and `release-readiness: ready` and no
  `sprint` key loads through `profile-contract-loader.py` at a first working stage without a
  `ContractError`.
- **AC-2** A work item carrying only `sprint` and `sprint-readiness: ready` still loads, and
  `profile-contract-loader.test.py` and `profile-spacedock-route.test.py` exit 0.
- **AC-3** An item carrying both keys with conflicting values is refused by a named error rather
  than silently resolved to one of them.
- **AC-4** `kc-dev-flow/MIGRATION.md` carries a dated entry naming the two meanings of `release`
  (grouping field, deleted route step) and stating that migration is opt-in per adopter.
- **AC-5** `docs/dev/ROADMAP.md`'s `kc-journey-map` S1 and S2 headings no longer defer to an
  unscheduled migration.

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
    Kent selected Pilot on 2026-09-14. The contract change stays in the package
    permanently rather than being a disposable experiment, and adopters are
    expected to migrate one at a time. No consumer must act to take the new
    version, so no Production compatibility trigger fires.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Keep the grouping field distinct from the deleted `release` route step and from the Linear Project release package named by `planning-outcome`.
      - Leave the Spacedock schema untouched; the field stays a workflow-owned permissive addition.
      - Decide the second key pair's exact names before implementation, and record which one the loader reports in a refusal.
    implementation:
      - Change only the loader's frontmatter reading and the package documents that state the grouping contract.
      - Migrate this repository's own `docs/dev` records and ROADMAP headings; leave other adopters unmigrated.
    testing:
      - Cover the three frontmatter cases named in AC-1 to AC-3 in the existing loader tests.
      - Run the existing loader and route test suites; add no standing CI lane.
  scope_boundary: >-
    The accepted outcome and complete non-goal list in this task remain unchanged.
    Excludes Spacedock schema or refit changes, planning-provider semantics,
    automatic migration of other adopters, and reviving the deleted release route step.
  semantics_unchanged: false
  promote_when:
    - An adopter must edit owned records or configuration to take the new version.
    - The deleted `release` route step or a Spacedock canonical field enters scope.
  decision:
    authority: Kent (Captain)
    at: 2026-09-14T00:00:00Z
```
