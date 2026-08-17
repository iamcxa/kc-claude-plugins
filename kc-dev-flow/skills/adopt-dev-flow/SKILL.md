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
2. Vendor `../../references/kernel.md`, the `references/profiles/` tree, and
   `../../scripts/profile-contract-loader.py` without local edits. Local
   mechanisms and exceptions stay in the workflow README.
3. Select a profile before the first working stage and store the v2 receipt in
   the existing work item. Each item selects independently; do not create a
   project-global profile or another profile registry. Invoke the loader with
   the exact work item so simultaneous items cannot borrow each other's route.
4. Map the logical routes to the runtime. A runtime with one superset graph uses:
   POC `implementation -> validation`; Pilot adds `ideation`; Production adds
   `release`. Backlog and done remain non-working states.
5. Make each working stage a small loader invocation or pointer. Do not duplicate
   the profile contracts in the workflow README.
6. Bind Captain, FO, Chief Engineer, Science Officer, deterministic gate, and
   release-owner authority. Advice never gains state or merge authority.
7. Run the profile loader contract test and the repository's normal gates.

If the workflow runtime cannot skip inactive stages or represent the Production
release boundary, record a refit requirement. Do not emulate progress with empty
review stages.

## Upgrade

Compare the adopted loader, core, and selected profile files with this source.
Present changed authority, route, and proof semantics for acceptance. Replace
accepted canonical files mechanically; do not create locally edited hybrids.
Re-run every profile-stage loader combination and prove that unselected profile
and stage markers are absent.

An existing v1 receipt remains evidence of the prior choice but cannot drive the
new loader. When its basis is unchanged, migrate it mechanically to v2 with the
same selection and derived route; do not ask the Captain to repeat the choice.
Re-select only when its basis is stale. Do not reopen completed work solely to
migrate a receipt.

## Boundary

Audit and upgrade findings do not create or schedule work. The Captain or named
iteration owner admits the change. Missing authority or an unsafe mutation path
returns `UNKNOWN` and leaves existing state unchanged.
