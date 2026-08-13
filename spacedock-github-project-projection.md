---
id: qahvaf44bx0y52cwvr8t1a13
title: Project Spacedock state into GitHub Issues and Projects through a portable installer
status: backlog
source: Captain request on 2026-08-13 after live mapping against iamcxa Project #2
product: kc-dev-flow
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design: required
lane:
---

Spacedock state is authoritative but mostly invisible outside its state branch. Provide a portable, one-way projection that makes entities and their lifecycle visible as GitHub Issues and GitHub Project items without turning GitHub into a second workflow authority or assuming every Spacedock workflow uses kc-dev-flow fields.

## Problem

The current repository has a product-local sprint contract and fields such as `product` and `sprint`, but these are not generic Spacedock guarantees. Generic Spacedock guarantees the canonical entity fields `id`, `title`, `status`, `score`, `source`, and `worktree`; recognizes optional `pr`, `started`, `completed`, `verdict`, `mod-block`, `archived`, and `issue`; preserves unknown custom fields; and lets each workflow declare its own stage names in `README.md`. A projector that hard-codes kc-dev-flow's five stages or requires `product` and `sprint` would fail or misrepresent a non-kc-dev-flow workflow.

The useful GitHub representation is also not a field-for-field copy. GitHub Project fields should exist only when they drive a view, filter, grouping, chart, or audit. In the kc-dev-flow profile, `SD Product` and exact `SD Stage` are useful grouping dimensions, `started` and `completed` can support retrospective metrics, and qualified sprint identity belongs in a repository Milestone. GitHub Project `Cycle` remains a calendar timebox and must not be inferred from a product-local ordinal sprint. Priority, Size, Estimate, and Cycle remain GitHub-owned until Spacedock has an explicit authority for them.

The desired operator surface is one setup skill plus one installed GitHub Actions reconcile workflow. The skill performs capability discovery, dry-run, configuration, installation, audit, and upgrade. Runtime projection must be deterministic code, not LLM reasoning embedded in workflow YAML. The installed workflow invokes that projector against an exact state ref and updates GitHub idempotently.

There is an unresolved trigger question for split-root state. GitHub resolves a `push` workflow from the event's associated commit/ref. If `.github/workflows/spacedock-project-sync.yml` exists only on the default branch and not on `spacedock-state/dev`, a push to the state branch may not find it. The current conservative design is a default-branch `schedule` plus `workflow_dispatch` reconcile, with event-driven alternatives — a state-branch trigger workflow or a `repository_dispatch` emitted after state push — requiring a measured spike before selection.

Project #2 is user-owned. The installer must not assume the repository-scoped `GITHUB_TOKEN` can write it, and must verify the supported credential path without copying local credentials into repository secrets. The task must distinguish repository Issue writes from personal Project writes and document the minimum supported token and scopes.

## Proposed approach

Build a schema-driven projector with two layers:

1. **Generic Spacedock core**
   - Read the commissioned workflow README and exact state ref.
   - Treat `id`, slug, `title`, and `status` as the identity/lifecycle baseline.
   - Populate `SD Stage` from the workflow's declared `stages.states[]`, not a fixed enum.
   - Derive only the lossless generic GitHub Status buckets: initial stage → Backlog, terminal stage → Done, intermediate stage → In progress.
   - Project `score`, `started`, `completed`, `issue`, and `pr` only when configured and valid.
   - Preserve unknown custom fields as unmapped capabilities; never publish them based on field name alone.

2. **Optional mapping profiles**
   - The kc-dev-flow profile maps `product` to an `SD Product` single-select field and maps a valid (`product`, `sprint`) pair to a qualified repository Milestone such as `kc-pr-flow/S4 — slim the kit`.
   - It preserves the exact stage in `SD Stage` while deriving the existing five GitHub Status buckets: unscheduled backlog → Backlog, scheduled backlog → Ready, ideation/implementation → In progress, validation → In review, done → Done.
   - A missing optional field produces a partial projection, not a failed Issue projection. An invalid sprint pair blocks only the sprint/Milestone write. Identity collisions and lifecycle contradictions remain quarantined conflicts.

The minimum generic Project schema is `SD Stage` plus projector-owned `SD Projection` (`Current`, `Partial`, `Conflict`, `Stale`). Additional fields are admitted only when the selected profile gives them stable semantics and they answer a concrete view or metric question. For kc-dev-flow the candidate fields are `SD Product`, `SD Started`, and `SD Completed`; `SD Score`, `SD Lane`, `SD Design`, `SD Verdict`, and derived `SD Cycle Days` remain optional follow-ups rather than installation defaults.

Use repository Milestone as logical sprint membership. Do not create a duplicate `SD Sprint` single-select field, because it would duplicate authority, drift from the Milestone, and accumulate bounded select options. The captain constraint is that one SD sprint cannot span multiple repositories.

Store projection identity and freshness in the GitHub Issue's machine-managed block. Record both the source branch commit for audit and a per-entity content digest for freshness; comparing every item only to the moving branch head would make unchanged entities falsely stale after unrelated state commits. Do not write projection receipts back into the state branch.

Distinguish projector-created Issues from pre-existing linked Issues. Only projector-owned Issues may eventually have open/closed state managed from SD terminal status; linked Issues default to metadata-only lifecycle management. Native historical burn-up/burndown claims must state which ownership class is included, because GitHub historical completion is based on Issue/PR state.

Expected installed files:

```text
.github/workflows/spacedock-project-sync.yml
.github/spacedock-project.yml
.github/scripts/project-spacedock-state.py
```

The setup skill should be a small router with install, audit, and upgrade workflows, a shared mapping-contract reference, templates for the workflow/config, and the deterministic projector script. The target repository gets reviewable vendored bytes rather than mutable remote code.

## Acceptance criteria

### AC-1 — Generic capability discovery is schema-driven

Given two fixture workflows — this kc-dev-flow workflow and a non-kc workflow with custom stages such as `inbox → building → checking → released` and no `product` or `sprint` — the installer emits a deterministic capability report from each workflow README and state ref. The non-kc fixture remains projectable, receives exact dynamic `SD Stage` values, and does not receive `SD Product` or Milestone writes.

Verified by: fixture tests over commissioned workflow READMEs plus representative entity files, asserting the planned fields and mapping decisions. Falsified by: renaming the non-kc stages or removing its optional dates changes only the discovered profile, while any fixed kc stage list or required product causes the test to fail.

### AC-2 — Mapping is field-local and idempotent

The projector classifies every entity as `CREATE`, `UPDATE`, `NO_CHANGE`, `PARTIAL`, or `CONFLICT`. Missing optional fields cannot suppress a valid Issue identity/title/status projection. Invalid optional values suppress only their corresponding Project write. A second run over identical entity bytes and GitHub state performs no mutation.

Verified by: a fake GitHub adapter with operation receipts for a mixed ten-entity corpus, including missing product, blank sprint, existing linked Issue, terminal item, and conflicting lifecycle. Falsified by: rerunning the same input emits any create/update operation, or blank product prevents Issue creation.

### AC-3 — Project fields serve explicit views or metrics

The generic default creates only `SD Stage` and `SD Projection`. The kc-dev-flow profile may add `SD Product`, `SD Started`, and `SD Completed`; qualified sprint uses Milestone; Priority, Size, Estimate, and Cycle are never inferred. Installation prints, for every created field, its source authority, blank behavior, and intended group/filter/chart use.

Verified by: installer dry-run snapshot and Project schema fixture. Falsified by: an unknown custom field silently becomes a Project field, `sprint` writes Cycle, or the installer creates a duplicate `SD Sprint` field.

### AC-4 — Trigger topology is proven, not assumed

A live disposable-repository experiment determines whether a workflow present only on the default branch runs on a push that changes only a split state branch lacking that workflow. It records the exact refs and run IDs for both the control and experimental pushes. The chosen v1 topology must then prove automatic reconciliation without adding a hidden local hook.

The decision compares exactly three supported options:

1. default-branch `schedule` plus `workflow_dispatch` reconciliation;
2. a minimal workflow present on the state branch and triggered by state push;
3. default-branch `repository_dispatch` emitted by an authenticated state-push integration.

Selection criteria are event latency, state-branch pollution, required credential surface, retry/reconcile behavior, workflow upgrade path, and ability to prove exactly-once effects through idempotency. If immediate event-driven behavior requires changing Spacedock or installing state-branch workflow bytes, state that explicitly rather than claiming a default-branch push listener can observe the split branch.

Verified by: links to the disposable repository workflow files, commits, Actions runs or documented absence, and a decision record naming the winning v1 topology. Falsified by: the selected trigger cannot reproduce after a fresh install, or relies only on documentation interpretation without a live branch experiment.

### AC-5 — Installer skill produces reviewable, least-authority output

One setup skill supports `install`, `audit`, and `upgrade`. Install pins the target repository, state ref, workflow directory, Project owner/number/ID, mapping profile, generated field plan, and projector version. It defaults to dry-run and shows exact files and external Project mutations before applying them. It never stores or prints credential values.

Verified by: install into a fixture repository, diff of exactly the expected workflow/config/script files, and a no-secret output scan. Falsified by: installation mutates an unconfirmed Project, copies local `gh` credentials, or requires editing the installed YAML by hand to select a generic profile.

### AC-6 — GitHub authentication is explicitly supported

The workflow separately proves same-repository Issue access and user-owned Project #2 access. The setup report identifies the supported secret/token type and required permissions for personal Project writes, rejects an unsupported token before partial mutation, and documents rotation/revocation. `GITHUB_TOKEN` is used only for capabilities it actually possesses.

Verified by: read-only Project probe followed by a reversible fixture-item mutation using the documented secret in a disposable target, with negative coverage for an insufficient token. Falsified by: the workflow creates an Issue and only then discovers it cannot add or update the Project item.

### AC-7 — Projection receipts prove identity and freshness without state feedback

Every managed Issue records repository-qualified identity, SD entity ID, state ref, audit commit, entity digest, projector version, and ownership mode in one bounded machine block. Lookup by existing `issue` reference or entity ID cannot create duplicates. Freshness compares entity digest, not only branch head. No successful run writes to the SD state branch.

Verified by: duplicate/search fixtures, an unrelated state commit that leaves an entity `Current`, and a changed entity that becomes `Stale` until projected. Falsified by: an unrelated entity change marks every receipt stale or creates another Issue.

### AC-8 — One installed workflow reconciles safely

The installed workflow checks out an exact state commit, uses concurrency cancellation or serialization appropriate for projector writes, runs validation before mutation, emits a machine-readable summary, and leaves conflicts visible without overwriting human-owned Issue content. Manual dispatch and the selected automatic trigger converge through the same projector path.

Verified by: dry-run, first apply, repeated no-op apply, concurrent-run test, and one conflict fixture. Falsified by: two overlapping runs create duplicate Issues, or trigger-specific paths implement different mapping logic.

## Open questions for independent review

1. Is a default-branch workflow genuinely unable to receive a `push` event for a split state branch when the workflow file is absent from that state ref, and what is the smallest live experiment that settles it?
2. Among schedule polling, state-branch workflow, and repository dispatch, which is the smallest safe v1 given that SD state commits originate from local agents and no SD core change is currently authorized?
3. Can a user-owned GitHub Project be updated from Actions with a narrower credential than a classic user token today, or must v1 explicitly accept that limitation?
4. Which generic SD fields are stable enough for automatic Project schema creation, and which must remain opt-in profile mappings?
5. Does the proposed Issue ownership split preserve trustworthy historical charts without allowing the projector to close pre-existing human Issues?

## Out of scope

- GitHub Project changes flowing back into SD state.
- Adding `product`, `sprint`, estimate, target dates, or projection receipt fields to the generic SD entity schema.
- Inferring Priority, Size, Estimate, Cycle, dates, or sprint semantics from prose.
- Replacing repository-local sprint Milestones with GHP Iteration.
- Editing or committing workflow files during this backlog capture beyond the SD task itself.

## Sizing

Design required. Ideation must split implementation if the trigger/authentication spike and the portable installer/projector cannot stay within one bounded dispatch. The first falsifiable slice is: install into one disposable non-kc workflow, project one entity, persist its receipt, rerun to `NO_CHANGE`, and reproduce the selected automatic trigger.
