---
name: adopt-dev-flow
description: Audit, adopt, or upgrade profile-native kc-dev-flow in a brownfield repository while preserving any existing local execution grouping, workflow runtime, and delivery provider.
---

# Adopt Dev Flow

Bind the existing repository to one shared core and profile-native routes. Do not
replace a working workflow runtime or delivery provider.

## Audit

Read `../../references/kernel.md` and the existing repository authorities. Map
project context, required briefs, local execution groups, execution state,
delivery, scope, and observation. Every item uses its Captain-approved committed
brief — a Development Brief or Exploration Brief — as its sole planning
authority; `source` is free-text provenance, may hold a Linear URL or any other
reference, and is never parsed or read. The workflow runtime owns only its
admitted snapshot, execution record, and evidence. Each item has one planning
authority and one execution-record authority. Classify the relevant seams as
working, broken, stubbed, or missing; repair the cheapest compatible seam.

## Adopt

1. Add a concise `## Local Profile` near the workflow frontmatter, bounded by
   exactly one start marker `<!-- kc-dev-flow-static-local-profile:start -->`
   and one end marker `<!-- kc-dev-flow-static-local-profile:end -->`. Bind
   existing authorities and their architecture entry: Pilot/Production requires
   a useful repository-root `docs/architecture.md`, linking existing details without
   duplication; POC creation is exempt. Follow `project-context-maintenance.md`.
   Also bind `Installed contract interface`, `Local mods`, and
   the repository's work-item and state authorities. The activated skill anchors
   its own package root and supplies `../../scripts/profile-contract-loader.py`
   for that invocation; do not persist an installation path. Every adopter binds
   the Captain-approved committed brief as its sole planning authority and
   installs no provider reader, adapter, or comparator. Do not mirror live
   provider status into a Roadmap or execution record.
2. Read `../../contract-manifest.json` beside the activated skill. It declares
   the contract interface, Local Profile interface, and exact plugin-owned
   runtime resources. Run its sibling installed loader from that same package;
   do not search host caches, inspect host names, copy canonical resources into
   the repository, or add a repository fallback. The selected stage owns each
   typed conditional-reference trigger; installation does not load a reference.
   Local provider paths, README policy, local mods, and Spacedock state remain
   repository-owned. The manifest's `resources` list is the boundary for what
   adoption adds to the repository: adoption binds existing repository
   authorities and adds no repository-owned reader, adapter, script, test, or
   check for a capability a declared resource already supplies. A capability the
   package lacks is a refit requirement raised against the package.
3. Select a profile before the first working stage and store the v3 receipt in
   the existing work item. Each item selects independently; do not create a
   project-global profile or another profile registry. Invoke the loader with
   the exact work item so simultaneous items cannot borrow each other's route.
   Require the Development Brief for Pilot and Production or the v3 Exploration
   Brief for POC. Local `sprint` and `sprint-readiness` remain runtime grouping
   and readiness mechanics, not planning evidence; `release` and
   `release-readiness` are the scalar alternative naming one journey release,
   qualified as `<journey>/<release-id>` and refused unqualified, never both
   pairs on one item. A Development Brief used for admission has this body
   shape without a `## Human-readable release brief` wrapper:

   ```markdown
   ## The problem

   ## Accepted outcome

   ## Non-goals

   ## Acceptance criteria

   - **AC-1** <observable condition>

   ## Route-back conditions

   The accepted outcome or non-goals changed. Stop and return a structured planning
   delta that names the changed premise, affected acceptance evidence, and
   recommended change or stop.
   ```
4. Map the logical routes to the runtime. A runtime with one superset graph uses:
   POC `implementation -> validation`; Pilot and Production add `ideation`. No
   profile adds a state the others skip, so a runtime that owns one stage graph
   per workflow cannot strand an item outside its declared route. Production's
   release authorization is a terminal-approval boundary inside `validation`,
   not a state: its gate approval targets the terminal state and the delivery
   provider's merge verdict is the sole terminal consumer. Backlog and done
   remain non-working states. Preserve an extra local terminal state only
   through an explicit mapping; it does not silently join every profile route.
5. Make each working stage a small installed-loader invocation or pointer. Pass
   the exact work item, marked Local Profile, stage-pin sidecar, and runtime-owned
   attempt identity. Before dispatch, write and commit one
   `kc-dev-flow-stage-pin/v1` record, re-read it, and dispatch only its emitted
   contract. Same-stage re-entry requires its exact plugin version, contract
   digest, work-item hash, and attempt. A compatible installed upgrade may create
   the next stage's pin; `LOCAL_PROFILE_REFIT_REQUIRED` stops before pin write or
   dispatch and names the README and declared local mods requiring review. Load a
   conditional reference only when the selected stage predicate fires. Bind
   `retained_document_change` to accepted or observed retained-document changes
   and `project_context_claim_may_change` to a missing Pilot/Production map, an
   initial retained explanation or a possible changed bound-context claim.
   Every continuation/worker reads the map before exploration; route a missing
   non-POC map's bounded bootstrap before feature work, including recovery build. Recheck both
   from the exact diff at
   implementation exit or validation; `receipt: null` adds no receipt. At
   implementation exit, use only the selected typed observation emitted by the
   loader. Do not duplicate the profile contracts in the workflow README.
6. Derive the two delivery triggers from the audited delivery authority rather
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
   When that local provider copy is Spacedock `pr-merge`, write
   `../../references/pr-merge-extension.md` verbatim between its
   `<!-- kc-dev-flow runtime extension:start -->` and
   `<!-- kc-dev-flow runtime extension:end -->` markers in the repository's
   `_mods/pr-merge.md` — append that marker pair after the released mod body if
   absent — and never edit the released body above it. This is prose sync, not
   a script: the repository's own contract test is the only drift detector, so
   compare the marked block byte-for-byte against the resource after writing it.
   That drift comparison is bounded at the `:end` marker; an adopter may add its
   own local prose after it, and `pr-merge-extension.md`'s own opening section
   states the declared precedence for that region against the marked block.
   The title refusal's self-test is grounded only against the fixture's
   captured release-please version; when the repository's own release-please
   version differs, stop and report the skew upstream to `kc-dev-flow`
   rather than trusting a green self-test or re-deriving the fixture
   locally, as `pr-merge-extension.md`'s "The title rule's oracle" section
   directs. A missing delivery authority is a refit requirement. Do not classify its
   absence as a route that delivers without a review artifact, do not invent
   direct Git delivery, a trunk push, forge ceremony, merge guard, or release
   owner, and stop before delivery until the repository names that authority.
7. Bind Captain, FO, Chief Engineer, Science Officer, deterministic gate, and
   release-owner authority. Advice never gains state or merge authority.
8. Resolve the implementation-exit observation by its precondition first. The
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
9. From at least one arbitrary installed root with host-specific environment
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

Re-run every profile-stage combination and prove
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
| `engineering-judgment.md` | Remove an unchanged vendored copy. Stage perspectives, Chief Engineer, and Science Officer own its surviving duties; preserve a repository-specific extension as local policy. |
| `work-control-profile.md` | Map each activated capability first. Bound-field checks stay repository-local, review convergence moves to the selected build observation, and delivery controls stay with the provider. Preserve any unmatched control locally before removing the vendored source. |

Keep `retained-document-policy.md` and `project-context-maintenance.md` as typed
installed conditional references; do not copy them into the repository, fold
them into the shared core, or load either for an unrelated work record.

## Boundary

Audit and upgrade findings do not create or schedule work. The Captain admits
the change. Missing authority or an unsafe mutation path
returns `UNKNOWN` and leaves existing state unchanged.
