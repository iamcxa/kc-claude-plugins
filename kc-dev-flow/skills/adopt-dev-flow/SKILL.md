---
name: adopt-dev-flow
description: Audit, adopt, or upgrade profile-native kc-dev-flow in a brownfield repository while preserving any existing planning provider, local execution grouping, workflow runtime, and delivery provider.
---

# Adopt Dev Flow

Bind the existing repository to one shared core and profile-native routes. Do not
replace a working planning provider, workflow runtime, or delivery provider.

## Audit

Read `../../references/kernel.md` and the existing repository authorities. Map
project context, required briefs, any planning provider, local execution
groups, execution state, delivery, scope, and observation. A provider-backed
item keeps one external planning authority and a complete Planning Receipt; a
standalone item uses its Captain-approved committed brief. The workflow runtime
owns only its admitted snapshot, execution record, and evidence. Each item has
one planning authority and one execution-record authority. Classify the relevant
seams as working, broken, stubbed, or missing; repair the cheapest compatible
seam. Before interpreting an existing `source` as Planning Receipt data,
preserve repository-local free text in a repository-owned field and remove the
canonical `source` field. Do not reinterpret provenance as provider identity.

## Adopt

1. Add a concise `## Local Profile` near the workflow frontmatter, bounded by
   exactly one start marker `<!-- kc-dev-flow-static-local-profile:start -->`
   and one end marker `<!-- kc-dev-flow-static-local-profile:end -->`. Bind
   existing authorities plus `Installed contract interface`, `Local mods`, and
   the repository's work-item and state authorities. The activated skill anchors
   its own package root and supplies `../../scripts/profile-contract-loader.py`
   for that invocation; do not persist an installation path. A
   repository that supports Planning Receipts binds its provider, read-only
   reader, and installed engage comparator. Linear uses installed sibling
   `linear-admission.py`; other providers keep a repository-local adapter. That
   sibling runs against three host preconditions: `LINEAR_API_KEY` and
   `CONDUCTOR_WORKSPACE_ID` in the invoking process environment, and a state
   authority at `<workflow-dir>/.spacedock-state` that is its own committed git
   root. A repository whose state lives inline in the workflow directory has no
   such root; the reader refuses it with `state authority is not
   <workflow-dir>/.spacedock-state`, so raise that layout as a refit requirement
   against the package and keep the repository-local adapter until then. The
   reader normalizes the union of current Ready
   items for one planning window/outcome and every currently Ready snapshot
   source even when it moved; it refuses a truncated result and exposes source
   identity, accepted goal, and non-goals without writing either system. A
   standalone adopter binds the Captain-approved committed brief and installs no
   provider adapter. Do not mirror live provider status into a Roadmap or
   execution record.
2. Read `../../contract-manifest.json` beside the activated skill. It declares
   the contract interface, Local Profile interface, and exact plugin-owned
   runtime resources. Run its sibling installed loader from that same package;
   do not search host caches, inspect host names, copy canonical resources into
   the repository, or add a repository fallback. Provider-backed work uses its
   reader and installed `engage-reconcile.py`; standalone uses neither. The
   selected stage owns each typed conditional-reference trigger; installation
   does not load a reference. Local provider paths, README policy, local mods,
   and Spacedock state remain repository-owned. The manifest's `resources` list
   is the boundary for what adoption adds to the repository: adoption binds
   existing repository authorities and adds no repository-owned reader,
   adapter, script, test, or check for a capability a declared resource already
   supplies. A capability the package lacks is a refit requirement raised
   against the package, with one exception: a planning provider the package
   does not support keeps a repository-local adapter.
3. Select a profile before the first working stage and store the v3 receipt in
   the existing work item. Each item selects independently; do not create a
   project-global profile or another profile registry. Invoke the loader with
   the exact work item so simultaneous items cannot borrow each other's route.
   Require the Development Brief for Pilot and Production or the v3 Exploration
   Brief for POC. A Planning Receipt is complete or absent: provider-backed work
   records `source`, `planning-window`, and `planning-outcome`; standalone work
   records none of them. A partial tuple stops. Local `sprint` and
   `sprint-readiness` remain runtime grouping and readiness mechanics, not
   planning evidence. When the provider uses Issue bodies as admission packets,
   each body starts directly with `## The problem` and omits both an
   `## Agent execution contract` section and a `## Human-readable release brief`
   wrapper, carrying these headings in this order:

   ```markdown
   ## The problem

   ## Goal

   ## Non-goals

   ## Acceptance criteria

   - **AC-1** <observable condition>

   ## Route-back conditions

   The accepted outcome or non-goals changed. Stop and return a structured planning
   delta that names the changed premise, affected acceptance evidence, and
   recommended change or stop.
   ```

   `linear-admission.py` reads the accepted goal from `## Goal` or from
   `## Accepted outcome` and refuses a body carrying both; it reads Non-goals
   from `- ` or `* ` bullets. The committed work item is the separate document
   whose Development Brief heading is `## Accepted outcome`, and
   `profile-contract-loader.py` reads its Non-goals from `- ` bullets, so a
   snapshot copied out of an Issue rewrites `* ` as `- `.
4. For a complete Planning Receipt, the engage reconcile is read-only: invoke
   the reader and normalize the provider's current Ready set and committed
   execution snapshot into ephemeral comparator inputs. Refuse a snapshot whose
   items do not all share the engaged item's exact `planning-window` and
   `planning-outcome`. Bind that exact source, window, and outcome when invoking
   the installed sibling comparator.
   Only exit `0` with one parsed `status: clean` result and empty delta arrays
   continues. Any other output stops: exit `1` reports the classified delta,
   while exit `2` or an invalid exit-`0` payload reports unavailable input.
   Report added, removed, changed, and moved items and stop before new dispatch
   or state mutation when any difference exists. The Captain admits every delta
   before an authorized actor commits a replacement snapshot. Never mutate
   either side automatically or cancel a running worker. Without a Planning
   Receipt, skip the provider reader and comparator and use the Captain-approved
   committed brief as planning authority.
5. Map the logical routes to the runtime. A runtime with one superset graph uses:
   POC `implementation -> validation`; Pilot and Production add `ideation`. No
   profile adds a state the others skip, so a runtime that owns one stage graph
   per workflow cannot strand an item outside its declared route. Production's
   release authorization is a terminal-approval boundary inside `validation`,
   not a state: its gate approval targets the terminal state and the delivery
   provider's merge verdict is the sole terminal consumer. Backlog and done
   remain non-working states. Preserve an extra local terminal state only
   through an explicit mapping; it does not silently join every profile route.
6. Make each working stage a small installed-loader invocation or pointer. Pass
   the exact work item, marked Local Profile, stage-pin sidecar, and runtime-owned
   attempt identity. Before dispatch, write and commit one
   `kc-dev-flow-stage-pin/v1` record, re-read it, and dispatch only its emitted
   contract. Same-stage re-entry requires its exact plugin version, contract
   digest, work-item hash, and attempt. A compatible installed upgrade may create
   the next stage's pin; `LOCAL_PROFILE_REFIT_REQUIRED` stops before pin write or
   dispatch and names the README and declared local mods requiring review. Load a
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
   A missing delivery authority is a refit requirement. Do not classify its
   absence as a route that delivers without a review artifact, do not invent
   direct Git delivery, a trunk push, forge ceremony, merge guard, or release
   owner, and stop before delivery until the repository names that authority.
8. Bind Captain, FO, Chief Engineer, Science Officer, deterministic gate, and
   release-owner authority. Advice never gains state or merge authority.
9. Resolve the implementation-exit observation by its precondition first. The
   installed `roborev-implementation-exit.md` claims single-flight through a
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
10. From at least one arbitrary installed root with host-specific environment
   variables absent, re-run every profile-stage combination this repository will
   use and prove that unselected profile and stage markers are absent. Snapshot
   README policy, local-mod bytes and modes, provider adapters, and state before
   migration; compare them after adoption and compatible upgrade. Delete
   byte-identical canonical repository copies and parity machinery only after
   these proofs pass, then run the repository's normal gates. Record the
   matrix, falsifiers, and probe results in the delivery artifact and the
   workflow's debrief or handoff mechanism. An adoption record written for the
   Captain to read may exist in the working tree; commit it only when the
   Captain names a consumer that reads it, because it pins one plugin version
   and revision that the next compatible upgrade invalidates and no gate
   re-checks.

If the workflow runtime cannot skip inactive stages or represent the Production
release boundary, record a refit requirement. Do not emulate progress with empty
review stages.

## Upgrade

Compare the active stage pin with the currently installed manifest. During an
active stage, any version or digest change returns `ACTIVE_STAGE_PIN_MISMATCH`;
restore the pinned install instead of mixing bytes. At the next boundary, an
unchanged Local Profile interface is compatible and may bind the new version and
digest. An interface change returns `LOCAL_PROFILE_REFIT_REQUIRED` with empty
stdout and no pin or state mutation. Present changed authority, route, and proof
semantics for Captain acceptance before refitting the named README or local mod.
After that accepted refit, the next-stage invocation explicitly adds
`--accept-local-profile-refit`; an ordinary compatible upgrade never uses it.

For a provider-backed adopter, run one clean, one delta, and one invalid-input
comparator invocation through the installed package. A standalone adopter has
no comparator to exercise. Re-run every profile-stage combination and prove
that unselected profile and stage markers are absent. The manifest makes a
missing declared reference an installed-package defect; do not repair it by
creating a repository copy.

An existing v1 receipt remains evidence of the prior choice but cannot drive the
new loader. A Pilot or Production v1 receipt with an unchanged basis may migrate
mechanically to v3 with the same selection and derived route; do not ask the
Captain to repeat the choice. A POC v1 receipt cannot supply the v3 decision,
falsifier, budget, and stop point, so the Captain records those fields before it
continues. Re-select only when the basis is stale. Do not reopen completed work
solely to migrate a receipt.

An older explicit Captain choice outside the v1 schema may also migrate without
another question only when the exact work item names the selected profile, the
Captain as its authority, and an unchanged basis. Record those legacy sources,
set the canonical route, and use the selected profile as the prior
recommendation. A POC still requires all v3 decision fields. A missing,
ambiguous, or stale element requires a new selection.

Retire old source mods and repository-local copies of a capability the package
now declares by disposition, not by filename alone:

| Retired repository artifact | Upgrade disposition |
|---|---|
| a repository-local Linear planning reader, built as this skill instructed before the package declared `scripts/linear-admission.py` | Delete the reader and its tests. The installed sibling `linear-admission.py` owns the current Ready read, carried snapshot sources, and comparator invocation. It reads `LINEAR_API_KEY` through `os.environ` in `linear-admission.py` and has no `.env` reader, so a key kept in a `.env` file moves into the invoking environment before the first engage. |
| `engineering-judgment.md` | Remove an unchanged vendored copy. Stage perspectives, Chief Engineer, and Science Officer own its surviving duties; preserve a repository-specific extension as local policy. |
| `work-control-profile.md` | Map each activated capability first. Bound-field checks stay repository-local, review convergence moves to the selected build observation, and delivery controls stay with the provider. Preserve any unmatched control locally before removing the vendored source. |

Keep `retained-document-policy.md` and `project-context-maintenance.md` as typed
installed conditional references; do not copy them into the repository, fold
them into the shared core, or load either for an unrelated work record.

Changing the planning provider is item-scoped. Migrate only open planning items
that have not been admitted to execution. An admitted provider-backed item keeps
its existing planning item and provider until completion; the old provider must
remain available for those items. A standalone item has no provider to migrate.
New provider-backed admissions use the replacement provider. During the drain,
providers may differ across snapshots, but each item retains one planning
authority. Keep admitted execution snapshots, planning bindings, execution
history, and delivery artifacts unchanged. Reconcile each provider-backed
snapshot through its own reader. Do not install an execution-to-provider
projector, provider importer, polling loop, or bidirectional sync.

## Boundary

Audit and upgrade findings do not create or schedule work. The Captain admits
the change. Missing authority or an unsafe mutation path
returns `UNKNOWN` and leaves existing state unchanged.
