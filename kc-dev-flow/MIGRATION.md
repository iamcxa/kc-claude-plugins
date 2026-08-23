# Migrating from 2.x

The profile-native contract is a breaking upgrade. The installed skills and an
adopter's vendored workflow must move in one coordinated cutover. A new
`continue-dev-flow` correctly fails closed when the local profile loader,
profile contracts, or v2 work-item receipt are absent; it does not fall back to
the installed package or silently run the 2.x workflow.

## Core differences

| 2.x adopter | Profile-native adopter |
|---|---|
| A workflow README and its stage-selected mods carry most policy. | `## Local Profile` locates a repository loader; it emits only the shared core, selected profile base, and current stage. |
| Normal and defect routes share one lifecycle. | Each work item selects POC, Pilot, or Production and may coexist with other profiles in the same repository. |
| A v1 or prose profile choice may inform work without driving a loader. | A hash-bound `kc-dev-flow-work-profile/v2` receipt is required before the first working stage. |
| Fresh EM or cross-model review may act as a general gate. | Named owners and deterministic checks hold scoped gates; Chief Engineer and Science Officer load only on their triggers. |
| Work-control prose may combine review and delivery controls. | Build emits one proportional typed observation; delivery and local controls remain with their providers. |
| Production release may share the normal terminal path. | Production has an explicit `release` stage; POC and Pilot skip it without placeholder work. |

## Safe cutover

1. Prepare the adopter refit before updating the installed plugin. Do not run
   ordinary continuation while one side is new and the other is still 2.x.
2. Audit existing project, work-item, iteration, execution-state, delivery,
   scope, gate, and observation authorities. Preserve their working owners.
3. Add the loader and contracts root to a concise `## Local Profile`. Vendor the
   shared core, profile tree, loader, and conditional references byte-for-byte.
4. Map POC, Pilot, and Production onto the existing runtime. Prove inactive
   stages can be skipped and the Production release boundary is representable.
5. Migrate work-item receipts at a stage boundary:
   - leave completed and archived items unchanged;
   - select a profile when a backlog item first enters work;
   - mechanically convert v1 when its basis is unchanged;
   - mechanically encode an older explicit Captain choice only when the exact
     item records the selected profile, its authority, and an unchanged basis;
     otherwise ask for a new selection.
6. Preserve extra local terminal states only through an explicit mapping. A
   state such as a finding-only terminal does not automatically join every
   profile route; an unrepresentable transition is a refit requirement.
7. Retire old source mods by disposition. Keep provider mods and unmatched
   repository controls local instead of deleting them or copying them into the
   shared core. Preserve `retained-document-policy.md` and
   `project-context-maintenance.md` as conditional references; bind their
   retained-document and project-context triggers instead of loading either as
   standing policy. Bind `delivery_artifact_review` whenever delivery goes
   through a review artifact, including when a provider mod owns the ceremony —
   `delivery-branch-base.md` only selects the base. Bind `pr_delivery_selected`
   to the vendored `pr-delivery.md` only when no provider mod owns that ceremony.
   A vendored provider mod that resolves its base as the configured trunk must
   accept a sibling branch before a stacked base is safe there.
8. Run every profile-stage loader combination, prove unselected contracts are
   absent, exercise runtime skips, and run the repository's normal gates. Merge
   the adopter refit before updating the installed plugin used for continuation.

## Decisions that remain local

The upgrade does not decide whether an adopter keeps a mandatory EM or
cross-model gate, how a custom terminal state closes, whether RoboRev is
available, or how its PR and state-holder providers operate. Present changes to
those authority and proof semantics explicitly; do not hide them inside a
mechanical re-vendor.

## 2026-08-21 — `release` state removed from the Production route

Profile differences must live in what happens inside a stage or in which
gates fire, not in which runtime states exist — expressing them as separate
graph states let one adopter's `pilot-product-slice` item land at
`status: release`, a stage outside its declared route, with no way to reach
`done`. `ROUTES["production"]` in `profile-contract-loader.py` no longer has a
`release` key; `"validation"` now maps to `("verify", "done")`. The
`production/release.md` stage contract is deleted; its required-output
content (rollout/rollback readiness, operational owner, explicit
Captain-or-release-owner authorization) moved into `production/verify.md`'s
`## Required output`. No Spacedock capability changed: Production's
validation-gate approval now targets the terminal `done` stage, so
`gate record --consume` leaves it pending (`route=approved-awaiting-merge`)
and `spacedock merge guard <slug> --verdict passed|rejected` is the sole
terminal consumer — already-documented 0.27.0-pre8 behavior, not a new ask.
This keeps the verification ruling (validation gate's own resolution) and the
release ruling (merge guard's verdict) as two separately timestamped records
instead of collapsing them into one state transition.

An adopter whose committed workflow README already declares a `release`
state upgrades by, in order: (1) drain every entity at `status: release` to
`done` under the *old* graph first — `spacedock status --where status=release`
must return empty before editing the README, since a status value with no
matching declared state silently drops the entity from `--boot`'s dispatchable
table rather than erroring; (2) edit the vendored `docs/dev/README.md`
`stages.states` block to drop `release`; (3) re-vendor
`profile-contract-loader.py` and `kernel.md` byte-for-byte, and the
`production/verify.md` / (deleted) `production/release.md` contracts —
`scripts/kc-dev-flow-contract-test.py`'s byte-parity check fails closed on a
partial re-vendor; (4) re-record every committed Production v2 receipt
(`kc-dev-flow:choose-work-profile`, mechanically, under the same Captain
selection — the profile did not change, only its route representation): the
loader now computes `expected_route = [shape, build, verify]` for
`production`, and a receipt still reading `route: [shape, build, verify,
release]` throws `stale route for production` on next load. An adopter that
does not upgrade keeps working exactly as today (the old graph, the old
ROUTES, the same stranding risk this change closes) — this is opt-in per
adopter at their next `kc-dev-flow` tag bump, not a forced break.

## 2026-08-18 — the shared core's verification discipline was dropped, and this note is late

`e634d3e7` (`#249`) replaced `kernel.md` wholesale and removed its
`## Verification discipline` section along with the absolutes rule in
`## Outcome discipline`. That removal was collateral: neither this file nor
`#249`'s body recorded it, so an adopter bumping across that tag lost merged
rules with no signal. Four of those clauses are restored, compressed, by the
change carrying this note: a check is evidence only once it has been seen to
fail; name the falsifier's kind; prefer the cheapest instrument that can fail;
when one failure shape repeats, change the work, not the wording — plus the
absolutes rule, now sited in `## Shared boundaries`. Not restored: `an
instruction that contradicts the governing contract loses`, which `#249` removed
from `## Authority model` in the same sweep, excluded here on one ground only —
no observed occurrence; and the six verification clauses whose subject matter the
profile stage contracts now carry.
An adopter that vendored `kernel.md` between `kc-dev-flow-v3.0.0` and the release
carrying this note has been running without those five rules.
