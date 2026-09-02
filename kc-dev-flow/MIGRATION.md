# Migration

Before any brownfield migration, inventory every existing `source` field. When
an existing value is repository-local free text rather than a resolvable
planning-item link, move it to a repository-owned provenance field and remove
the canonical `source` field before either v4 admission validation or
continuation. Preserve the value; do not reinterpret it as provider identity.

## Migrating a vendored 4.x adopter to installed contracts

This migration makes the installed `kc-dev-flow` package the canonical runtime
source. The adopter retains its marked workflow README, local mods, provider
adapters, work items, and Spacedock state. It removes repository copies of the
kernel, profiles, conditional references, loader, POC close guard, and engage
comparator only after the installed route is proven.

1. Freeze the adopter revision and snapshot the complete marked Local Profile,
   each declared local-mod byte hash and mode, provider-adapter bytes, and state
   HEAD/tree/status. Inventory every canonical repository copy and verify it is
   byte-identical to the currently installed package before classifying it as a
   deletion candidate.
2. Add `Installed contract interface` with
   `kc-dev-flow-local-profile/v1` and `Local mods` to the marked Local Profile.
   Remove stored loader, contracts-root, close-guard, comparator, and
   conditional-reference installation paths. The activated `adopt-dev-flow` or
   `continue-dev-flow` skill supplies its own sibling loader path for the current
   invocation; do not search host caches or persist that path.
3. For a provider-backed repository, keep its provider reader/adapter and pass
   the installed loader path into that adapter. The adapter invokes the loader's
   sibling `engage-reconcile.py`. A standalone repository keeps neither reader
   nor adapter and invokes no comparator.
4. From at least three arbitrary package roots with Claude, Codex, Hermes, and
   Conductor discovery variables absent, run every supported profile-stage
   combination. Require the installed manifest's version/digest envelope, the
   selected kernel/base/stage only, and no unselected marker.
5. Create the state authority's stage-pin sidecar. Before dispatch, the First
   Officer writes and commits one `kc-dev-flow-stage-pin/v1` record, reruns the
   loader to read it back, and dispatches only that envelope. Same-stage re-entry
   accepts only the pinned plugin version, contract digest, work-item hash, and
   attempt. Restore missing or changed pinned bytes; do not fall back to the
   repository copies.
6. Exercise one compatible upgrade by changing package version/digest without
   changing `local_profile_interface`: the active stage must return
   `ACTIVE_STAGE_PIN_MISMATCH`, while the next stage may write the new pin.
   Exercise one incompatible interface upgrade: it must return
   `LOCAL_PROFILE_REFIT_REQUIRED` with empty stdout, name the README and declared
   local mods, and leave the prior pin and state unchanged.
   After the Captain accepts and the named bindings are refit, rerun the next
   boundary once with `--accept-local-profile-refit`.
7. Recompare every preservation snapshot. Only after the fresh-adopter,
   all-route, upgrade, refit, and preservation checks pass, delete the canonical
   repository copies and package/adopter parity machinery. Reject any remaining
   canonical copy. Run the adopter's provider, close-guard, route, and normal
   repository gates through the installed package.

Rollback before a new-stage pin restores the old installed plugin and the
atomic Local Profile/deletion commit. After a new stage is pinned, keep that
version through the active stage and schedule any downgrade for the following
boundary. Never rewrite active work-item history or unrelated Spacedock state.

## Migrating from 3.x to 4.x

Version 4 keeps one graph and three profile slugs, changes new receipts to
`kc-dev-flow-work-profile/v3`, adds the POC close guard, removes the
Production-only `release` state, and makes scheduling a loader-enforced backlog
exit requirement. It also removes the packaged GitHub Project projection: the
planning provider is replaceable, while admitted SD snapshots and active
execution remain stable. Upgrade the adopter and installed plugin as one
cutover, in this order:

1. Inventory active receipts. Finish each active v2 POC on its pinned 3.x
   package/vendor pair, or have the Captain re-record it as v3 with decision,
   falsifier, budget, and stop point. Under the old graph and loader, drain every
   entity at `status: release` to `done`; `spacedock status --where
   status=release` must return empty before the graph changes.
2. Remove `release` from the adopter's workflow graph. Bound its existing
   `## Local Profile` with one start marker
   `<!-- kc-dev-flow-static-local-profile:start -->` and one end marker
   `<!-- kc-dev-flow-static-local-profile:end -->`. Install a package whose
   manifest declares the loader, engage comparator, close guard, optional
   workspace-neutral Linear admission guard, kernel, profile tree, and
   conditional references. Delete byte-identical canonical repository copies;
   do not re-vendor the installed runtime. Keep adapters only for planning
   providers the package does not support.
   Active v2 Pilot and Production receipts remain loadable; new choices use v3.
3. Mechanically re-record each committed Production v2 receipt under its same
   Captain selection so its route is `[shape, build, verify]`.
4. Default the adopter's entity template to `sprint-readiness: defer`. Before
   continuing any item already at its first working stage, classify its Planning
   Receipt before recording scheduling fields. For provider-backed work, resolve
   the accepted planning window and outcome from `source`, have the Captain
   approve that snapshot, and record non-empty `planning-window` and
   `planning-outcome` values. For standalone work, leave `source`,
   `planning-window`, and `planning-outcome` absent and use the Captain-approved
   committed brief as planning authority. Both paths assign a non-empty local
   `sprint` execution group and set `sprint-readiness: ready`. Backlog items need
   those values only when selected; do not mark the unscheduled queue ready as a
   bulk migration.
5. Prove the drivable set with `spacedock status --where sprint=X --where
   sprint-readiness=ready`. Run the reader and comparator only for provider-backed
   work, against the provider's current Ready set plus every still-Ready snapshot
   source outside the original window/outcome. Refuse a snapshot whose items do
   not all share the engaged item's exact window and outcome. Linear-backed work
   may invoke the installed Linear admission guard; another provider invokes its
   adapter and the installed comparator with that exact source, window, and
   outcome. Standalone work skips
   both and continues from the Captain-approved committed brief. For the
   provider-backed path, only exit `0` with one parsed `status: clean` result and
   empty delta arrays continues. A delta, truncated result, invalid input, or any
   other output must stop before dispatch. Run every profile-stage load,
   guarded POC close path, package
   parity check, and normal repository gate before updating the installed
   plugin.

### Retire the planning projection

Remove the installed projector workflow, configuration, and
`.github/scripts/project-spacedock-state.py` with the package upgrade. Do not
delete provider items or repository secrets without separate
destructive-cleanup authorization.

Keep admitted Spacedock snapshots, their current `source` links, execution
history, and pull requests unchanged. If the repository changes planning
provider, migrate only open planning items that have not been admitted to SD.
An already-admitted active task keeps its existing planning item and provider
until completion, so keep the old provider and its read-only reader available
during the drain; new admissions use the replacement provider. Each item retains
one planning-item authority even while providers differ across snapshots. Do
not backfill mutable provider state into Roadmap or active tasks, and do not
replace the retired projector with an importer, polling loop, or bidirectional
sync. Reconcile remains read-only; every difference needs Captain admission
before an authorized actor commits a replacement snapshot.

Rollback the installed plugin and the whole vendored contract set together. An
adopter that does not take v4 keeps its 3.x graph and loader behavior. Do not mix
a 4.x installed plugin, loader, or close guard with a partially migrated 3.x
workflow or contract set; receipt schema v3 is part of the 4.x contract.

## Migrating from 2.x

The profile-native contract is a breaking upgrade. The installed skills and an
adopter's vendored workflow must move in one coordinated cutover. A new
`continue-dev-flow` correctly fails closed when the local profile loader,
profile contracts, or supported work-item receipt are absent; it does not fall back to
the installed package or silently run the 2.x workflow.

### Core differences

| 2.x adopter | Profile-native adopter |
|---|---|
| A workflow README and its stage-selected mods carry most policy. | `## Local Profile` locates a repository loader; it emits only the shared core, selected profile base, and current stage. |
| Normal and defect routes share one lifecycle. | Each work item selects POC, Pilot, or Production and may coexist with other profiles in the same repository. |
| A v1 or prose profile choice may inform work without driving a loader. | New choices use `kc-dev-flow-work-profile/v3`; compatible active v2 Pilot and Production receipts remain loadable. |
| Fresh EM or cross-model review may act as a general gate. | Named owners and deterministic checks hold scoped gates; Chief Engineer and Science Officer load only on their triggers. |
| Work-control prose may combine review and delivery controls. | Build emits one proportional typed observation; delivery and local controls remain with their providers. |
| Production release may share the normal terminal path. | Every profile terminalizes through the same states; Production adds a release-authorization boundary inside `validation` rather than a `release` stage. |

### Safe cutover

1. Prepare the adopter refit before updating the installed plugin. Do not run
   ordinary continuation while one side is new and the other is still 2.x.
2. Audit existing project, work-item, iteration, execution-state, delivery,
   scope, gate, and observation authorities. Preserve their working owners.
3. Add the loader and contracts root to a concise `## Local Profile`, bounded by
   exactly one start marker `<!-- kc-dev-flow-static-local-profile:start -->`
   and one end marker `<!-- kc-dev-flow-static-local-profile:end -->`. Vendor
   the shared core, profile tree, loader, and conditional references byte-for-byte.
4. Map POC, Pilot, and Production onto the existing runtime. Prove inactive
   stages can be skipped and the Production release boundary is representable.
5. Migrate work-item receipts at a stage boundary:
   - leave completed and archived items unchanged;
   - select a profile when a backlog item first enters work;
   - a Pilot or Production v1 receipt may migrate mechanically to v3 when its
     basis is unchanged;
   - a POC v1 receipt requires the Captain to record the v3 decision fields:
     decision, falsifier, budget, and stop point;
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

### Decisions that remain local

The upgrade does not decide whether an adopter keeps a mandatory EM or
cross-model gate, how a custom terminal state closes, whether RoboRev is
available, or how its PR and state-holder providers operate. Present changes to
those authority and proof semantics explicitly; do not hide them inside a
mechanical re-vendor.

## 2026-08-24 — promotion asks whether a consumer must migrate

`public compatibility` was one of the triggers that promote work to
`production`. Every change to a published package satisfies it, so in a package
repository the trigger fired on everything and sorted nothing: of thirteen
receipts here, eight selected `production`, and five of those gave the same
reason — published to consumers at a pinned tag — while stating in the same
receipt that no runtime or external state was involved. The full Production
validation bar then asked those items for rollout readiness, an operational
owner, and a monitoring handoff that none of them had.

The trigger is now **a compatibility break that makes a consumer act**: one an
existing consumer cannot absorb by taking the new version, because it must run a
migration, edit its own configuration, or rewrite records it owns. Publication is
not the test. Re-deciding the same eight receipts under this rule leaves four at
`production` — including the route-graph change, whose adopters had to drain
entities and edit their own workflow graph — and moves four to
`pilot-product-slice` with their release obligation intact.

The rule is deliberately asymmetric. Where you cannot state that consumers
upgrade without doing anything, the trigger counts as met: sending a migration
out on a shorter route costs more than paying Production's bar once.

## 2026-08-24 — the `backlog` exit bar names the admitted snapshot

The bar had two parts, what an item is and why it is worth doing, and both are
about whether a queued item is legible. Neither answers which of the queued
items to start, so selection stayed a manual read of the whole queue: this
repository reached 64 queued items against one in flight, growing eight to ten
a week, with `sprint` present on 25 of 67 items and `sprint-readiness` on none.

A third part is now required. An item leaves `backlog` only when it also carries
the planning provider's accepted `planning-window` and `planning-outcome`, a
shared SD `sprint` execution group, and `sprint-readiness: ready`. The SD field
names are fixed on purpose — the queue answers `--where sprint=X --where
sprint-readiness=ready` instead of one that must be read item by item. Which
windows and outcomes exist stays with the planning provider; the Captain admits
the resulting snapshot.

An adopter upgrades by adding the four fields to its entity template and filling
them when an item is next selected. Backfilling the whole queue is not required:
an item that never leaves `backlog` never has to answer the bar.

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
