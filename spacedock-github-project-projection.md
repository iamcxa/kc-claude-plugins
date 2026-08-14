---
id: qahvaf44bx0y52cwvr8t1a13
title: Project Spacedock state into GitHub Issues and Projects through a portable installer
status: ideation
source: Captain request on 2026-08-13, retargeted after live inspection from iamcxa Project #2 to Project #1
product: kc-dev-flow
sprint: S3
started: 2026-08-14
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design: required
lane: main
---

Spacedock state is authoritative but mostly invisible outside its state branch. Provide a portable, one-way projection that makes entities and their lifecycle visible as GitHub Issues and GitHub Project items without turning GitHub into a second workflow authority or assuming every Spacedock workflow uses kc-dev-flow fields.

## Problem

The current repository has a product-local sprint contract and fields such as `product` and `sprint`, but these are not generic Spacedock guarantees. Generic Spacedock guarantees the canonical entity fields `id`, `title`, `status`, `score`, `source`, and `worktree`; recognizes optional `pr`, `started`, `completed`, `verdict`, `mod-block`, `archived`, and `issue`; preserves unknown custom fields; and lets each workflow declare its own stage names in `README.md`. A projector that hard-codes kc-dev-flow's five stages or requires `product` and `sprint` would fail or misrepresent a non-kc-dev-flow workflow.

The useful GitHub representation is also not a field-for-field copy. GitHub Project fields should exist only when they drive a view, filter, grouping, chart, or audit. In the kc-dev-flow profile, `SD Product` and exact `SD Stage` are useful grouping dimensions, `started` and `completed` can support retrospective metrics, and qualified sprint identity belongs in a repository Milestone. GitHub Project `Cycle` remains a calendar timebox and must not be inferred from a product-local ordinal sprint. Priority, Size, Estimate, and Cycle remain GitHub-owned until Spacedock has an explicit authority for them.

The desired operator surface is one setup skill plus one installed GitHub Actions reconcile workflow. The skill performs capability discovery, dry-run, configuration, installation, audit, and upgrade. Runtime projection must be deterministic code, not LLM reasoning embedded in workflow YAML. The installed workflow invokes that projector against an exact state ref and updates GitHub idempotently.

There is an unresolved trigger question for split-root state. GitHub resolves a `push` workflow from the event's associated commit/ref. If `.github/workflows/spacedock-project-sync.yml` exists only on the default branch and not on `spacedock-state/dev`, a push to the state branch may not find it. The current conservative design is a default-branch `schedule` plus `workflow_dispatch` reconcile, with event-driven alternatives — a state-branch trigger workflow or a `repository_dispatch` emitted after state push — requiring a measured spike before selection.

Project #1 is user-owned. Its current title is `kc-plugins`; the captain removed its five obsolete QNow items on 2026-08-13 and a live readback showed zero items. The generic installer must still treat any pre-existing item without a matching projector receipt as foreign: report it, never delete or overwrite it, and project only into explicitly managed items. It must not assume the repository-scoped `GITHUB_TOKEN` can write the Project, and must verify the supported credential path without copying local credentials into repository secrets. The task must distinguish repository Issue writes from personal Project writes and document the minimum supported token and scopes.

## Proposed approach

Build a schema-driven projector with two layers:

1. **Generic Spacedock core**
   - Read the commissioned workflow README from a pinned trunk commit and entities from a separately pinned state commit. The README is not assumed to exist on a split state branch.
   - Use repository + workflow directory + slug as the primary identity. Treat a non-empty `id` as a stable secondary key; `id-style: slug` legitimately stores an empty `id`, and more than one commissioned workflow may exist in a repository.
   - Populate `SD Stage` from the workflow's declared `stages.states[]`, not a fixed enum.
   - Derive only the lossless generic GitHub Status buckets: initial stage → Backlog, terminal stage → Done, intermediate stage → In progress.
   - Parse permissively enough to preserve workflow README extensions and tolerate legacy entities that omit fields listed as schema `always_present`. Project `score`, `started`, `completed`, `issue`, and `pr` only when configured and valid.
   - Never project `worktree`; it is machine-local execution state and may disclose local paths. Preserve `source` only in the bounded Issue projection block.
   - Preserve unknown custom fields as unmapped capabilities; never publish them based on field name alone.

2. **Optional mapping profiles**
   - The kc-dev-flow profile maps `product` to an `SD Product` single-select field and maps a valid (`product`, `sprint`) pair to a qualified repository Milestone such as `kc-pr-flow/S4 — slim the kit`.
   - It preserves the exact stage in `SD Stage` while deriving the existing five GitHub Status buckets: unscheduled backlog → Backlog, scheduled backlog → Ready, ideation/implementation → In progress, validation → In review, done → Done.
   - A missing optional field produces a partial projection, not a failed Issue projection. An invalid sprint pair blocks only the sprint/Milestone write. Identity collisions and lifecycle contradictions remain quarantined conflicts.

For a single selected workflow, the minimum generic Project schema is `SD Stage` plus projector-owned `SD Projection` (`Current`, `Partial`, `Conflict`, `Stale`). V1 deliberately binds one installed configuration to one SD workflow and one GitHub Project, so it does not create an `SD Workflow` field or aggregate unrelated workflow semantics into one Project. Additional fields are admitted only when the selected profile gives them stable semantics and they answer a concrete view or metric question. For kc-dev-flow the candidate fields are `SD Product`, `SD Started`, and `SD Completed`; `SD Score`, `SD Lane`, `SD Design`, `SD Verdict`, `mod-block`, and derived `SD Cycle Days` remain optional follow-ups rather than installation defaults.

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

## Project boundary and dogfood sequence

A GitHub Project represents one management system: one workflow vocabulary, planning cadence, metric interpretation, status-update audience, and ownership boundary. Repository or team identity alone is insufficient. Two repositories owned by the same team may still require separate Projects when their work-item semantics differ; conversely, unrelated teams and workflows must never be combined merely to form a portfolio.

The rollout order is:

1. `iamcxa/kc-claude-plugins`, workflow `docs/dev`, projects into user Project #1 (`kc-plugins`). This is the first real dogfood because it already uses kc-dev-flow and has enough tasks to exercise partial fields, sprint Milestones, grouping, and charts. Project #1 begins dogfood empty after the captain removed its five obsolete QNow items.
2. `spacedock-dev/subspace-relay`, workflow `docs/dev`, projects into a separate Relay Project whose number is not yet selected. Relay has its own Local Profile, sprint registry, and lifecycle policy; its adapter is validated independently rather than inheriting kc-claude-plugins field choices.
3. CarLove projects into a separate CarLove Project after the first two mappings are stable. Its higher complexity is a later compatibility test, not a reason to broaden the first Project schema.

A disposable repository and Project may still be used before dogfood to prove trigger and credential behavior. That proof environment is not counted as a dogfood target and cannot replace the kc-claude-plugins vertical slice.

## Project Status Update flow

Project Status Updates follow the same one-workflow/one-Project boundary and describe Project-level health, not item lifecycle. `COMPLETE` means the Project itself is complete, not that one sprint ended. Start and target dates remain Project-level inputs and are not inferred from an SD sprint.

Separate evidence, drafting, language, and publication:

1. Every successful reconcile emits a deterministic status snapshot containing the pinned trunk/state commits, selected workflow and Project, qualified sprint identities, member-set digest, stage counts, terminal count, projection conflicts/freshness, and any available goal/exit-criterion digest.
2. Compare that snapshot with the last published update receipt, or the installation baseline before the first update. Classify changes as delivery delta (members changed stage or completed), scope delta (members entered, left, or moved sprint), and definition delta (goal, exit criterion, or sprint identity changed). A ratio change caused by a new denominator must be reported as scope change rather than work regression.
3. A weekly schedule and high-signal reconcile events may generate a candidate draft. Initial event candidates are sprint start, sprint close, definition change, projection stale, and projection conflict. Cooldown and content digest suppress repeated drafts. A schedule delay changes draft latency, not source truth.
4. GHA renders a baseline Markdown draft from deterministic facts and uploads the machine-readable manifest as a run artifact/job summary. It does not call an LLM. Missing dates, estimates, or exit criteria produce an explicit insufficient-evidence result rather than an invented health claim.
5. The setup skill exposes `status draft`, `status preview`, `status publish`, and `status history`. `status draft` may optionally ask the host LLM to rewrite the baseline for clarity, but the model cannot calculate metrics, add unsupported claims, or publish. The rewrite remains bound to the manifest and evidence links.
6. `status publish` re-reads the live SD and Project inputs, rejects a stale manifest, shows the exact GraphQL payload and diff from the latest update, and requires explicit user confirmation. The published Markdown carries a bounded machine receipt with snapshot digest, source commits, projector version, and ownership mode so the next delta has a durable baseline.

GitHub has no native draft status-update object in the current API: create, update, and delete mutations operate on published updates. Therefore a generated draft is projector-owned derived evidence, not a hidden GitHub lifecycle state. V1 defaults to automated evidence and draft generation with manual publication. Opt-in automatic publication remains a later policy mode and must not make an LLM-authored body the unattended payload.

## Acceptance criteria

### AC-1 — Generic capability discovery is schema-driven

Given the two real commissioned workflows in this repository plus a focused non-kc fixture with custom stages such as `inbox → building → checking → released` and no `product` or `sprint`, the installer emits a deterministic capability report from each workflow README and state ref. It accepts real extension keys, `id-style: slug`, an empty stored ID, absent `score`, and nullable or omitted optional structures without weakening the initial/terminal invariants. The non-kc fixture remains projectable, receives exact dynamic `SD Stage` values, and does not receive `SD Product` or Milestone writes.

Verified by: fixture tests over commissioned workflow READMEs plus representative entity files, asserting the planned fields and mapping decisions. Falsified by: renaming the non-kc stages or removing its optional dates changes only the discovered profile, while any fixed kc stage list or required product causes the test to fail.

### AC-2 — Mapping is field-local and idempotent

The projector classifies every entity as `CREATE`, `UPDATE`, `NO_CHANGE`, `PARTIAL`, or `CONFLICT`. Missing optional fields cannot suppress a valid Issue identity/title/status projection. Every target field declares all source dependencies: for example, kc-dev-flow's scheduled-backlog → Ready mapping depends on a valid sprint pair, so a malformed sprint suppresses both Milestone and that derived Status write rather than silently treating the item as unscheduled. A second run over identical entity bytes and GitHub state performs no mutation.

Verified by: a fake GitHub adapter with operation receipts for a mixed ten-entity corpus, including missing product, blank sprint, existing linked Issue, terminal item, and conflicting lifecycle. Falsified by: rerunning the same input emits any create/update operation, or blank product prevents Issue creation.

### AC-3 — Project fields serve explicit views or metrics

The generic default creates only `SD Stage` and `SD Projection`. The kc-dev-flow profile may add `SD Product`, `SD Started`, and `SD Completed`; qualified sprint uses Milestone; Priority, Size, Estimate, and Cycle are never inferred. V1 never creates `SD Workflow`, because one configuration selects one workflow and one Project. Installation prints, for every created field, its source authority, blank behavior, and intended group/filter/chart use.

Verified by: installer dry-run snapshot and Project schema fixture. Falsified by: an unknown custom field silently becomes a Project field, `sprint` writes Cycle, or the installer creates a duplicate `SD Sprint` field.

### AC-4 — Trigger topology is proven, not assumed

A live disposable-repository experiment determines whether a workflow present only on the default branch runs on a push that changes only a split state branch lacking that workflow. It records the exact refs and run IDs for both the control and experimental pushes. The chosen v1 topology must then prove automatic reconciliation without adding a hidden local hook.

The decision compares exactly three supported options:

1. default-branch `schedule` plus `workflow_dispatch` reconciliation;
2. a minimal workflow present on the state branch and triggered by state push;
3. default-branch `repository_dispatch` emitted by an authenticated state-push integration.

Selection criteria are event latency, state-branch pollution, required credential surface, retry/reconcile behavior, workflow upgrade path, and ability to prove exactly-once effects through idempotency. If immediate event-driven behavior requires changing Spacedock or installing state-branch workflow bytes, state that explicitly rather than claiming a default-branch push listener can observe the split branch. The current v1 hypothesis is default-branch schedule as the liveness safety net plus `workflow_dispatch` as the fast path; an explicit setup/dev-flow operation may invoke `gh workflow run` after a successful state push without becoming a hidden git hook. The experiment, not this hypothesis, makes the final choice.

Verified by: links to the disposable repository workflow files, commits, Actions runs or documented absence, and a decision record naming the winning v1 topology. Falsified by: the selected trigger cannot reproduce after a fresh install, or relies only on documentation interpretation without a live branch experiment.

### AC-5 — Installer skill produces reviewable, least-authority output

One setup skill supports `install`, `audit`, and `upgrade`. Install pins the target repository, trunk ref, state ref, workflow directory, Project owner/number/ID, mapping profile, generated field plan, and projector version. It defaults to dry-run and shows exact files and external Project mutations before applying them. At runtime the projector re-derives capabilities from both pinned inputs and refuses mutation if they disagree with the reviewed config. It never stores or prints credential values.

Verified by: install into a fixture repository, diff of exactly the expected workflow/config/script files, and a no-secret output scan. Falsified by: installation mutates an unconfirmed Project, copies local `gh` credentials, or requires editing the installed YAML by hand to select a generic profile.

### AC-6 — GitHub authentication is explicitly supported

The workflow separately proves same-repository Issue/Milestone access and user-owned Project #1 access. Current live evidence shows Project #1 is a private user-owned Project with Board, Roadmap, and Table views; current Projects v2 REST and GraphQL surfaces both require direct capability probing rather than inheriting an older GraphQL-only assumption. The spike must test the actual REST and/or GraphQL mutations chosen by the implementation and determine whether a fine-grained token with personal Projects permission works before falling back to a classic PAT. The setup report identifies the supported secret/token type and required permissions, rejects an unsupported token before partial mutation, documents expiry/rotation/revocation, and keeps `GITHUB_TOKEN` for repository-scoped writes rather than using one broad token for both authorities.

Verified by: read-only Project probe followed by a reversible fixture-item mutation using the documented secret in a disposable target, with negative coverage for an insufficient token. Falsified by: the workflow creates an Issue and only then discovers it cannot add or update the Project item.

### AC-7 — Projection receipts prove identity and freshness without state feedback

Every managed Issue records repository- and workflow-qualified identity, slug, optional non-empty SD entity ID, state ref, trunk audit commit, state audit commit, entity digest, projector version, and ownership mode in one bounded machine block. Lookup by existing `issue` reference or qualified identity cannot create duplicates. Freshness compares entity digest, not only branch head. No successful run writes to the SD state branch.

Verified by: duplicate/search fixtures, an unrelated state commit that leaves an entity `Current`, and a changed entity that becomes `Stale` until projected. Falsified by: an unrelated entity change marks every receipt stale or creates another Issue.

### AC-8 — One installed workflow reconciles safely

The installed workflow checks out exact trunk and state commits, serializes projector writes with `cancel-in-progress: false`, runs both credential preflights and all validation before mutation, emits a machine-readable summary, and leaves conflicts visible without overwriting human-owned Issue content. Manual dispatch and the selected automatic trigger converge through the same projector path. Human edits to `SD *` fields are explicitly non-authoritative and are restored on the next successful reconcile.

Verified by: dry-run, first apply, repeated no-op apply, concurrent-run test, and one conflict fixture. Falsified by: two overlapping runs create duplicate Issues, or trigger-specific paths implement different mapping logic.

### AC-9 — Liveness failure is visible

The installation exposes when reconciliation has not completed within its configured freshness window, including a disabled/delayed schedule or expired Project token. Silence cannot look like a quiet, current Project.

Verified by: disable the scheduled workflow and separately use an expired/invalid fixture token; each produces an observable stale/failing signal without mutating Issue state. Falsified by: the last successful projection remains visually `Current` indefinitely.

### AC-10 — Archive and removal semantics are explicit

When an entity moves to `_archive/`, the projector retains qualified identity, marks the Project item archived or an equivalent explicit terminal projection, and closes only projector-owned Issues when policy permits. A pre-existing linked Issue is never closed merely because the SD entity was archived. A foreign Project item without a projector receipt is never changed. Deletion without an archive tombstone is quarantined rather than silently removing history.

Verified by: live create → archive → reconcile for both projector-owned and linked fixture Issues. Falsified by: charts retain an apparently active orphan or a linked human Issue is closed.

### AC-11 — The deployed slice proves value and bounded cost

After disposable trigger/auth proof, the first dogfood vertical slice uses `iamcxa/kc-claude-plugins` `docs/dev` with its true split state branch, checks out both refs, dry-runs ten representative entities against Project #1, then projects an explicitly approved bounded subset. It re-runs to zero mutations, preserves freshness after an unrelated entity change, leaves all five foreign QNow items untouched, and creates a saved view grouped by `SD Stage` that answers which entities occupy a given workflow stage. It records a bounded API request count and fails resumably under a simulated rate limit.

Verified by: disposable proof URLs and run IDs, Project #1 dry-run/apply receipts, GraphQL or REST request log, no-op receipt, untouched foreign-item evidence, and saved-view evidence. Falsified by: only fake-adapter tests pass, a QNow item changes, or the Project UI cannot answer the stated question.

### AC-12 — Status drafting detects sprint deltas without surrendering publish authority

Given a prior published snapshot, changing only task stage produces a delivery delta, adding four unchanged tasks produces a scope delta and explains the changed denominator, and changing the sprint exit criterion produces a definition delta. The same deterministic manifest renders the GHA baseline and constrains an optional skill-hosted LLM rewrite. An unchanged rerun produces no new candidate. Missing schedule evidence leaves proposed health unset or explicitly insufficient rather than inferring `ON_TRACK`. No Project Status Update is created until `status publish` revalidates the manifest and receives explicit user confirmation.

Verified by: fixture sequence over baseline → delivery → scope → definition changes; golden JSON/Markdown drafts; stale-manifest refusal; fake GraphQL adapter proving zero create mutations before confirmation and one receipt-bearing mutation after it. Falsified by: scope expansion is described as work regression, an LLM changes a metric, `COMPLETE` is inferred from sprint closure, or GHA publishes an unconfirmed narrative.

## Open questions for independent review

1. Is a default-branch workflow genuinely unable to receive a `push` event for a split state branch when the workflow file is absent from that state ref, and what is the smallest live experiment that settles it?
2. Among schedule polling, state-branch workflow, and repository dispatch, which is the smallest safe v1 given that SD state commits originate from local agents and no SD core change is currently authorized?
3. Can a user-owned GitHub Project be updated from Actions with a narrower credential than a classic user token today, or must v1 explicitly accept that limitation?
4. Which generic SD fields are stable enough for automatic Project schema creation, and which must remain opt-in profile mappings?
5. Does the proposed Issue ownership split preserve trustworthy historical charts without allowing the projector to close pre-existing human Issues?

## Independent architecture review — Claude Opus 5 High, 2026-08-13

Fresh read-only review session `569fa7f4-7603-4e4b-a9f1-621d26403c91` returned **coherent with required corrections**. It had Read/Grep/Glob access only, safe mode, no MCP, no Bash/Edit/Write, and did not run the required live GitHub experiment.

### Trigger verdict

The reviewer independently reached the same high-confidence inference: a workflow present only on the default branch will not receive a push to a true orphan-like state ref whose associated commit contains no `.github/workflows` file. It warned that a casual experiment can give a false opposite result if the state branch was forked from main and inherited the workflow. The live proof must therefore record `git ls-tree state-ref -- .github`, a no-workflow experimental push, a state-ref-with-workflow positive control, and a manual-dispatch positive control.

Its recommended v1 is **default-branch schedule + workflow_dispatch through one reconcile path**. Schedule is the convergence/liveness safety net; an explicit `gh workflow run` after a successful state push is the near-immediate fast path using the operator's existing GitHub authentication. A state-branch workflow is technically event-driven but pollutes and complicates the upgrade authority of the state branch. `repository_dispatch` is not lightweight until a supported state-push integration exists; otherwise it becomes the hidden local hook and extra credential the task forbids.

This verdict remains an inference until AC-4's disposable-repository experiment runs.

### Accepted corrections

- The workflow README/config/projector live on trunk while mutable entities live on the state ref; runtime must pin and report both commits and define skew handling.
- Identity must include repository + workflow directory + slug. A stored `id` may be empty for `id-style: slug`, and one repository may contain multiple commissioned workflows.
- Runtime discovery must tolerate real workflow extensions and legacy omissions instead of treating the shipped schema's `always_present` list or `strict_canonical` declaration as a day-one parse gate.
- Generic Status mapping must verify the target Project's actual Status options; otherwise it writes only exact `SD Stage`.
- kc-dev-flow Status has a real dependency on sprint validity, so invalid sprint suppresses every dependent target write rather than only Milestone.
- A mutating reconciler must serialize with `cancel-in-progress: false`; cancelling an in-flight run can strand a partially projected Issue/item.
- Human edits to projector-owned `SD *` Project fields are overwritten by design and must be labeled as such.
- Archive/removal behavior, schedule/token liveness, and API request/rate-limit bounds need explicit acceptance criteria.
- The deployed slice must use the two real refs and produce a saved Project view that answers a user question, not stop at fake-adapter consistency.

### Rejected or unresolved reviewer claim

The reviewer claimed Projects v2 is GraphQL-only and treated the cited REST documentation as retired Projects Classic material. That is stale against current live evidence: with API version `2026-03-10`, `GET /users/iamcxa/projectsV2/2` returned Project `25139362`, number `2`, title `Secha`. Do not adopt the GraphQL-only claim. AC-6 now requires probing the actual current mutation surface and token types; whether a fine-grained personal Projects token can write Project #2 remains live-unproven.

### Smallest validated slice recommended by the review

Use one disposable repository with default-branch workflow/config/projector, a true orphan state branch containing three representative entities and no `.github/`, and one disposable user-owned Project. Run trigger controls first, then credential probes, then manual dispatch to create one Issue/item/receipt, repeat to `NO_CHANGE`, change an unrelated entity to prove digest-local freshness, and finally demonstrate a non-empty saved view grouped by `SD Stage`.

## Out of scope

- GitHub Project changes flowing back into SD state.
- Combining kc-claude-plugins, Relay, or CarLove in one GitHub Project, or adding a cross-project portfolio layer.
- Adding `product`, `sprint`, estimate, target dates, or projection receipt fields to the generic SD entity schema.
- Automatically publishing LLM-authored Project Status Updates or enabling any unattended publish policy before a dogfood transition rule is separately approved.
- Inferring Priority, Size, Estimate, Cycle, dates, or sprint semantics from prose.
- Replacing repository-local sprint Milestones with GHP Iteration.
- Editing or committing workflow files during this backlog capture beyond the SD task itself.

## Sizing

Design required. Ideation must split implementation if the trigger/authentication spike and the portable installer/projector cannot stay within one bounded dispatch. The proof slice is: install into one disposable workflow, project one entity, persist its receipt, rerun to `NO_CHANGE`, and reproduce the selected automatic trigger. The first dogfood slice then dry-runs ten kc-dev-flow entities and applies an approved bounded subset to Project #1 without mutating its five foreign QNow items.
