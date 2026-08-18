---
name: adopt-dev-flow
description: Audit, adopt, or upgrade profile-native kc-dev-flow in a brownfield repository while preserving its existing tracker, iteration authority, workflow runtime, and delivery provider.
---

# Adopt Dev Flow

Bind the existing repository to one shared core and profile-native routes. Do not
replace a working tracker, roadmap, workflow runtime, or delivery provider.

## Audit

Read `../../references/kernel.md` and the existing repository authorities. Map
project context, work items, iteration, execution state, delivery, scope, and
observation. Classify the relevant seams as working, broken, stubbed, or missing;
repair the cheapest compatible seam.

## Adopt

1. Add a concise `## Local Profile` near the workflow frontmatter. Bind existing
   authorities plus the repository-local profile loader and contracts root.
2. Vendor `../../references/kernel.md`, the `references/profiles/` tree,
   `../../references/reverse-recovery-audit.md`,
   `../../references/journey-slicing.md`, and
   `../../references/retained-document-policy.md`,
   `../../references/project-context-maintenance.md`,
   `../../references/delivery-branch-base.md`,
   `../../references/pr-delivery.md`, and
   `../../scripts/profile-contract-loader.py` without local edits. The selected
   stage owns each typed conditional-reference trigger; vendoring a reference
   does not load it. The selected `build.md` owns its typed proportional observation.
   Local provider paths and exceptions stay in the workflow README.
3. Select a profile before the first working stage and store the v2 receipt in
   the existing work item. Each item selects independently; do not create a
   project-global profile or another profile registry. Invoke the loader with
   the exact work item so simultaneous items cannot borrow each other's route.
4. Map the logical routes to the runtime. A runtime with one superset graph uses:
   POC `implementation -> validation`; Pilot adds `ideation`; Production adds
   `release`. Backlog and done remain non-working states. Preserve an extra
   local terminal state only through an explicit mapping; it does not silently
   join every profile route.
5. Make each working stage a small loader invocation or pointer. Load a
   conditional reference only when the selected stage predicate fires. Bind
   `retained_document_change` to accepted or observed retained-document changes
   and `project_context_claim_may_change` to a possible changed claim in the
   repository's bound project context. Recheck both from the exact diff at
   implementation exit or validation; `receipt: null` adds no receipt. At
   implementation exit, use only the selected typed observation emitted by the
   loader. Do not duplicate the profile contracts in the workflow README.
6. Derive the two delivery triggers from the audited delivery authority rather
   than asking. Set `delivery_artifact_review` true when that authority delivers
   through a pull request, merge request, or forge equivalent — a forge remote
   plus an existing delivery-artifact history is sufficient evidence — no matter
   who owns the ceremony. Set it false only for a route that delivers without one,
   or for a repository whose recorded policy keeps every artifact on the trunk;
   record which of those applies. Set `pr_delivery_selected` true only when no
   local provider mod owns the PR ceremony. When a provider such as Spacedock
   `pr-merge` owns it, that trigger stays false and base selection still applies,
   so one delivery authority survives. Then read the owning ceremony's base
   resolution: a ceremony that resolves its base as the configured trunk and
   rebases onto it will re-target a stacked branch and open an artifact carrying
   the parent's work. Record that as a refit requirement against the local
   provider copy; do not bind a stacked default over a ceremony that discards it.
7. Bind Captain, FO, Chief Engineer, Science Officer, deterministic gate, and
   release-owner authority. Advice never gains state or merge authority.
8. Bind the local RoboRev runbook when the emitted observation is supported.
   Missing provider capability remains an honest non-gating `UNAVAILABLE` result.
9. Run the profile loader contract test and the repository's normal gates.

If the workflow runtime cannot skip inactive stages or represent the Production
release boundary, record a refit requirement. Do not emulate progress with empty
review stages.

## Upgrade

Compare the adopted loader, core, and selected profile files with this source.
Present changed authority, route, and proof semantics for acceptance. Replace
accepted canonical files mechanically; do not create locally edited hybrids.
Re-run every profile-stage loader combination and prove that unselected profile
and stage markers are absent.

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

## Boundary

Audit and upgrade findings do not create or schedule work. The Captain or named
iteration owner admits the change. Missing authority or an unsafe mutation path
returns `UNKNOWN` and leaves existing state unchanged.
