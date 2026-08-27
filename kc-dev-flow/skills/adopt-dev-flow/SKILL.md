---
name: adopt-dev-flow
description: Audit, adopt, or upgrade profile-native kc-dev-flow in a brownfield repository while preserving its existing planning provider, local execution grouping, workflow runtime, and delivery provider.
---

# Adopt Dev Flow

Bind the existing repository to one shared core and profile-native routes. Do not
replace a working planning provider, workflow runtime, or delivery provider.

## Audit

Read `../../references/kernel.md` and the existing repository authorities. Map
project context, planning items, planning windows, planning outcomes, local SD
execution groups, execution state, delivery, scope, and observation. Confirm
that the planning provider owns discussion, acceptance, priority, human-facing
status, time windows, and accepted outcomes; and Spacedock owns the admitted
snapshot, execution record, and evidence. Each item has one planning-item
authority and one execution-record authority. Classify the relevant seams as
working, broken, stubbed, or missing; repair the cheapest compatible seam.

## Adopt

1. Add a concise `## Local Profile` near the workflow frontmatter. Bind existing
   authorities plus the repository-local profile loader and contracts root.
   Bind the planning provider plus a repository-local read-only planning reader
   and the vendored repository-local read-only engage comparator.
   The reader must normalize the union of current Ready items for one planning
   window/outcome and every currently Ready snapshot source even when it moved.
   It must refuse a truncated result and expose source identity, accepted goal,
   and non-goals without writing either system. A new Spacedock task stores
   those bindings in `source`,
   `planning-window`, and `planning-outcome`; every task in the admitted set
   shares one `sprint` execution-group value. Its required `what` and `why` are
   an admission snapshot and execution evidence, not a second accepted-goal
   authority. Do not mirror live provider status into a Roadmap or SD record.
2. Vendor `../../references/kernel.md`, the `references/profiles/` tree,
   `../../references/reverse-recovery-audit.md`,
   `../../references/journey-slicing.md`, and
   `../../references/retained-document-policy.md`,
   `../../references/project-context-maintenance.md`,
   `../../references/delivery-branch-base.md`,
   `../../references/pr-delivery.md`,
   `../../references/roborev-implementation-exit.md`,
   `../../scripts/profile-contract-loader.py`,
   `../../scripts/engage-reconcile.py`, and
   `../../scripts/poc-close-guard.py` without local edits. The selected
   stage owns each typed conditional-reference trigger; vendoring a reference
   does not load it. The selected `build.md` owns its typed proportional observation.
   Local provider paths and exceptions stay in the workflow README.
3. Select a profile before the first working stage and store the v3 receipt in
   the existing work item. Each item selects independently; do not create a
   project-global profile or another profile registry. Invoke the loader with
   the exact work item so simultaneous items cannot borrow each other's route.
   Default the entity template to `sprint-readiness: defer`. Before an item
   enters its first working stage, bind non-empty `planning-window` and
   `planning-outcome` values from the accepted planning item, assign the shared
   non-empty `sprint` execution group, and set `sprint-readiness: ready`; do not
   mark the unscheduled backlog ready during adoption. Materialize one SD task
   for every Ready planning item in that window and outcome. The committed SD
   entity set is the admitted snapshot.
4. At every engage, the engage reconcile is read-only: invoke the reader and
   normalize the provider's current Ready set and committed SD snapshot into
   ephemeral comparator inputs. Refuse a snapshot whose items do not all share
   the engaged item's exact `planning-window` and `planning-outcome`. Bind that
   exact source, window, and outcome when invoking the vendored comparator;
   exit `0` continues, exit `1` reports the
   classified delta and stops, and exit `2` reports unavailable input and
   stops.
   Report added, removed, changed, and moved items and stop before new dispatch
   or state mutation when any difference exists. The Captain admits every delta
   before an authorized actor commits a replacement snapshot. Never mutate
   either side automatically or cancel a running worker.
5. Map the logical routes to the runtime. A runtime with one superset graph uses:
   POC `implementation -> validation`; Pilot and Production add `ideation`. No
   profile adds a state the others skip, so a runtime that owns one stage graph
   per workflow cannot strand an item outside its declared route. Production's
   release authorization is a terminal-approval boundary inside `validation`,
   not a state: its gate approval targets the terminal state and the delivery
   provider's merge verdict is the sole terminal consumer. Backlog and done
   remain non-working states. Preserve an extra local terminal state only
   through an explicit mapping; it does not silently join every profile route.
6. Make each working stage a small loader invocation or pointer. Load a
   conditional reference only when the selected stage predicate fires. Bind
   `retained_document_change` to accepted or observed retained-document changes
   and `project_context_claim_may_change` to a possible changed claim in the
   repository's bound project context. Recheck both from the exact diff at
   implementation exit or validation; `receipt: null` adds no receipt. At
   implementation exit, use only the selected typed observation emitted by the
   loader. Do not duplicate the profile contracts in the workflow README.
7. Derive the two delivery triggers from the audited delivery authority rather
   than asking. Set `delivery_artifact_review` true when that authority delivers
   through a pull request, merge request, or forge equivalent — a forge remote
   plus an existing delivery-artifact history is sufficient evidence — no matter
   who owns the ceremony. Set it false only for a route that delivers without
   one. A repository that must keep every artifact on the trunk keeps the trigger
   true and records that as the reference's local base policy; binding the
   trigger false would misstate how the repository delivers. Set
   `pr_delivery_selected` true only when no
   local provider mod owns the PR ceremony. When a provider such as Spacedock
   `pr-merge` owns it, that trigger stays false and base selection still applies,
   so one delivery authority survives. Then read the owning ceremony's base
   resolution: a ceremony that resolves its base as the configured trunk and
   rebases onto it will re-target a stacked branch and open an artifact carrying
   the parent's work. Record that as a refit requirement against the local
   provider copy; do not bind a stacked default over a ceremony that discards it.
7. Bind Captain, FO, Chief Engineer, Science Officer, deterministic gate, and
   release-owner authority. Advice never gains state or merge authority.
8. Resolve the implementation-exit observation by its precondition first. The
   vendored `roborev-implementation-exit.md` claims single-flight through a
   Spacedock-registered state holder, so the observation is in scope only for a
   repository running Spacedock with kc-dev-flow. Without that state authority,
   record the observation as out of scope once and leave its trigger false. That
   is a declared boundary — do not treat it as a missing binding, a refit
   requirement, or a recurring `UNAVAILABLE`.

   In scope, the repository owns four bindings: the fixed reviewer policy, the
   registered state holder, its clean-holder prerequisite, and the durability
   command. Record agent `codex`, model `gpt-5.6-terra`, reasoning `medium`, and
   `panel: none`; the actual host and implementation family are provenance only.
   Resolve the other three bindings from the repository's own state authority
   rather than copying another repository's paths. Then probe once — provider
   CLI present, fixed reviewer available and
   authenticated, state holder resolvable — and report each binding as bound or
   unbound. An absent CLI, agent, or authentication is an environment result and
   stays an honest non-gating `UNAVAILABLE`. A binding never recorded is an
   adoption defect: the observation would emit and resolve nothing at every
   future implementation exit, so record it as a refit requirement instead of
   leaving a permanent silent `UNAVAILABLE`.
9. Re-run every profile-stage loader combination this repository will run and
   prove that unselected profile and stage markers are absent from each result,
   then run the repository's normal gates. Vendor no test: the packaged loader
   contract test resolves the loader as its own sibling, so pointing it at the
   vendored copy would mean copying a test file into a repository that has no
   other use for it, and running the packaged copy would exercise the package
   rather than this adoption.

If the workflow runtime cannot skip inactive stages or represent the Production
release boundary, record a refit requirement. Do not emulate progress with empty
review stages.

## Upgrade

Compare the adopted loader, engage comparator, core, and selected profile files
with this source. Present changed authority, route, and proof semantics for
acceptance. Replace accepted canonical files mechanically; do not create
locally edited hybrids. Against the adopted comparator, run one clean, one
delta, and one invalid-input invocation; then re-run every profile-stage loader
combination and prove that unselected profile and stage markers are absent.

A reference that exists in this source and not in the adopter is a missing
capability, not an intentional omission. Compare the source reference set with
the vendored one, vendor each absent file, and bind its trigger by the adopt
rules above. The loader enforces presence: `check_conditional_references` refuses
a stage contract that declares a reference the adopter has not vendored, so an
incomplete re-vendor stops the route instead of silently dropping the capability.
It checks presence only — the reference still stays unread until its trigger
fires. That is the path by which a repository upgraded before a reference existed
picks it up.

An existing v1 receipt remains evidence of the prior choice but cannot drive the
new loader. When its basis is unchanged, migrate it mechanically to v2 with the
same selection and derived route; do not ask the Captain to repeat the choice.
Re-select only when its basis is stale. Do not reopen completed work solely to
migrate a receipt.

An older explicit Captain choice outside the v1 schema may also migrate without
another question only when the exact work item names the selected profile, the
Captain as its authority, and an unchanged basis. Record those legacy sources,
set the canonical route, and use the selected profile as the prior
recommendation. A missing, ambiguous, or stale element requires a new selection.

Retire old source mods by disposition, not by filename alone:

| Retired source mod | Upgrade disposition |
|---|---|
| `engineering-judgment.md` | Remove an unchanged vendored copy. Stage perspectives, Chief Engineer, and Science Officer own its surviving duties; preserve a repository-specific extension as local policy. |
| `work-control-profile.md` | Map each activated capability first. Bound-field checks stay repository-local, review convergence moves to the selected build observation, and delivery controls stay with the provider. Preserve any unmatched control locally before removing the vendored source. |

Preserve the surviving `retained-document-policy.md` and
`project-context-maintenance.md` references byte-for-byte. They remain typed
conditional references; do not fold either into the shared core or load it for
an unrelated work record.

Changing the planning provider is item-scoped. Migrate only open planning items
that have not been admitted to Spacedock. An already-admitted active task keeps
its existing planning item and provider until completion; the old provider must
remain available for those items. New admissions use the replacement provider.
During the drain, providers may differ across snapshots, but each item retains
one planning-item authority. Keep active Spacedock snapshots, their planning
bindings, execution history, and delivery artifacts unchanged. Reconcile each
snapshot through its own provider's reader. Do not install an SD projector,
provider importer, polling loop, or bidirectional sync.

## Boundary

Audit and upgrade findings do not create or schedule work. The Captain admits
the change. Missing authority or an unsafe mutation path
returns `UNKNOWN` and leaves existing state unchanged.
