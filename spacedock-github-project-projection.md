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
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.context/worktrees/qa-projection
issue:
pr: 227
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
   - Derive GitHub Status only through discovered target capabilities. Project #1 currently exposes `Todo`, `In Progress`, and `Done`, so the generic profile may map initial → Todo, intermediate → In Progress, and terminal → Done. If no compatible option exists, write only exact `SD Stage` rather than creating or guessing Status semantics.
   - Parse permissively enough to preserve workflow README extensions and tolerate legacy entities that omit fields listed as schema `always_present`. Project `score`, `started`, `completed`, `issue`, and `pr` only when configured and valid.
   - Never project `worktree`; it is machine-local execution state and may disclose local paths. Preserve `source` only in the bounded Issue projection block.
   - Preserve unknown custom fields as unmapped capabilities; never publish them based on field name alone.

2. **Optional mapping profiles**
   - The kc-dev-flow profile maps `product` to an `SD Product` single-select field and maps a valid (`product`, `sprint`) pair to a qualified repository Milestone such as `kc-pr-flow/S4 — slim the kit`.
   - It preserves the exact stage in `SD Stage` while deriving the existing five GitHub Status buckets: unscheduled backlog → Backlog, scheduled backlog → Ready, ideation/implementation → In progress, validation → In review, done → Done.
   - A missing optional field produces a partial projection, not a failed Issue projection. An invalid sprint pair blocks only the sprint/Milestone write. Identity collisions and lifecycle contradictions remain quarantined conflicts.

For a single selected workflow, the minimum generic Project schema is only `SD Stage`. V1 deliberately binds one installed configuration to one SD workflow and one GitHub Project, so it does not create an `SD Workflow` field or aggregate unrelated workflow semantics into one Project. A stored `SD Projection = Current` value is not a liveness signal because it cannot decay when the workflow stops. Per-item projection state stays in the Issue receipt; installation liveness uses the timestamped last-successful reconcile receipt and a configured freshness window. Additional fields are admitted only when the selected profile gives them stable semantics and they answer a concrete view or metric question. For kc-dev-flow the candidate fields are `SD Product`, `SD Started`, and `SD Completed`; `SD Score`, `SD Lane`, `SD Design`, `SD Verdict`, `mod-block`, and derived `SD Cycle Days` remain optional follow-ups rather than installation defaults.

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

1. `iamcxa/kc-claude-plugins`, workflow `docs/dev`, projects into user Project #1 (`kc-plugins`). This is the first real dogfood because it already uses kc-dev-flow and has enough tasks to exercise partial fields, grouping, and charts. Project #1 begins dogfood empty after the captain removed its five obsolete QNow items. Before bounded apply, create two deliberate receipt-less fixtures so foreign-item preservation has a non-vacuous live test: one title collision and one item with a hand-set real `SD Stage` value.
2. `spacedock-dev/subspace-relay`, workflow `docs/dev`, projects into a separate Relay Project whose number is not yet selected. Relay has its own Local Profile, sprint registry, and lifecycle policy; its adapter is validated independently rather than inheriting kc-claude-plugins field choices.
3. CarLove projects into a separate CarLove Project after the first two mappings are stable. Its higher complexity is a later compatibility test, not a reason to broaden the first Project schema.

A disposable repository and Project may still be used before dogfood to prove trigger and credential behavior. That proof environment is not counted as a dogfood target and cannot replace the kc-claude-plugins vertical slice.

## Project Status Update sibling boundary

Project Status Updates follow the same one-workflow/one-Project boundary and describe Project-level health, not item lifecycle. `COMPLETE` means the Project itself is complete, not that one sprint ended. Start and target dates remain Project-level inputs and are not inferred from an SD sprint.

The captain approved splitting status drafting and publication into the separately scheduled `spacedock-project-status-updates` sibling. This task owns only the producer seam: every successful reconcile emits a versioned deterministic status snapshot. The sibling consumes that snapshot and owns delta classification, candidate suppression, optional LLM wording, stale-manifest refusal, and human-confirmed publication.

The sibling design keeps these boundaries:

1. Every successful reconcile emits a deterministic status snapshot containing the pinned trunk/state commits, selected workflow and Project, qualified sprint identities, member-set digest, stage counts, terminal count, projection conflicts/freshness, and any available goal/exit-criterion digest.
2. Compare that snapshot with the last published update receipt, or the installation baseline before the first update. Classify changes as delivery delta (members changed stage or completed), scope delta (members entered, left, or moved sprint), and definition delta (goal, exit criterion, or sprint identity changed). A ratio change caused by a new denominator must be reported as scope change rather than work regression.
3. A weekly schedule and high-signal reconcile events may generate a candidate draft. Initial event candidates are sprint start, sprint close, and definition change. Cooldown and content digest suppress repeated drafts. Projection liveness belongs to the reconcile health surface, not a management status narrative. A schedule delay changes draft latency, not source truth.
4. GHA renders a baseline Markdown draft from deterministic facts and uploads the machine-readable manifest as a run artifact/job summary. It does not call an LLM. Missing dates, estimates, or exit criteria produce an explicit insufficient-evidence result rather than an invented health claim.
5. The sibling skill exposes `status draft`, `status preview`, `status publish`, and `status history`. `status draft` may optionally ask the host LLM to rewrite the baseline for clarity, but the model cannot calculate metrics, add unsupported claims, or publish. At publish time, every number, date, identifier, and health claim in the rewrite must be an unchanged member of the deterministic manifest fact set; omission is allowed, invention or alteration is refused.
6. `status publish` re-reads the live SD and Project inputs, rejects a stale manifest, shows the exact GraphQL payload and diff from the latest update, and requires explicit user confirmation. The published Markdown carries a bounded machine receipt with snapshot digest, source commits, projector version, and ownership mode so the next delta has a durable baseline. If the latest published update has no parsable receipt, the sibling reports `insufficient-evidence` and requires an explicit re-baseline; it never treats a foreign update as its baseline or overwrites one.

GitHub has no native draft status-update object in the current API: create, update, and delete mutations operate on published updates. Therefore a generated draft is sibling-owned derived evidence, not a hidden GitHub lifecycle state. The projection v1 emits evidence only; the sibling may add automated draft generation with manual publication. Opt-in automatic publication remains a later policy mode and must not make an LLM-authored body the unattended payload.

## Ideation working record

### Accepted outcome and authority

The accepted S3 outcome is the ROADMAP entry on `main@b9821d50580f184fc81f2363ade820fd76a30af6`: install one-way projection for one selected SD workflow and one selected GitHub Project, dogfood `kc-claude-plugins/docs/dev` against Project #1, prove idempotency and a usable stage-grouped view, and generate deterministic sprint-delta status drafts that remain human-published. Captain direction permits S3 to begin alongside remaining S2 validation and preserves S2 scope, ordering, and release hold.

The protected value is a low-maintenance external view of SD state that stays traceable to exact source revisions without becoming workflow authority. If forced to cut, keep the deterministic one-way projector, identity/freshness receipts, ten-entity dry-run, and no-op rerun. Defer richer Project fields, narrative rewriting, automatic event latency, and status drafting before weakening projection correctness or authority separation.

Non-goals remain GitHub-to-SD writeback, Relay or CarLove rollout, unattended Project Status Update publication, LLM-derived metrics, a hosted service, and a cross-Project portfolio. The riskiest assumption is that a default-branch Actions topology can obtain both split-state inputs and least-authority personal Project credentials with acceptable latency and upgrade cost.

Captain-approved appetite is eight human-hours for the POC. Stop and re-cut if the disposable trigger/credential proof consumes two hours without a reproducible supported route, if implementation requires a hosted service or a Spacedock core change, or if the first observable round trip cannot stay within one setup skill plus one deterministic projector. Preserve projection and its snapshot producer; defer Milestone writes and every status draft/publish consumer before extending the appetite.

### Inherited acceptance normalization

| Criteria | Class and disposition |
|---|---|
| AC-1, AC-2, AC-7, AC-9, AC-10 | Retain as value or authority constraints: generic portability, idempotency, traceable freshness, visible liveness failure, and safe archive semantics. |
| AC-3 | Retain the value that every field serves a view/metric/audit; the generic minimum is now only `SD Stage`, with time-bearing reconcile freshness outside stored Project enums. |
| AC-4, AC-6 | Retain as falsifiable spikes earned by the automatic reconcile and user-owned Project values. The spike selects topology and credential type; it does not pre-authorize repository or secret mutation. |
| AC-5, AC-8 | Retain the captain-selected installable skill plus GHA boundary. Exact installed filenames are mechanisms and may change if a smaller reviewed layout satisfies the same reviewability, upgrade, and single-reconcile values. |
| AC-11 | Retain as the S3 observable dogfood value and bind apply to a separately approved bounded subset after dry-run. |
| AC-12 | Narrow this task to the versioned deterministic snapshot producer. Move delta classification, drafting, optional LLM wording, and human-confirmed publication to the separately scheduled `spacedock-project-status-updates` sibling. |

### Reverse-recovery audit against `origin/main@b9821d50580f184fc81f2363ade820fd76a30af6`

Two search strategies were used over `kc-dev-flow`, repository `scripts`, and `.github/workflows`: domain/API vocabulary search (`ProjectV2`, status update, state branch, workflow dispatch, install, template) and complete file inventory by surface. External repositories, dynamic references, and unpublished branches were outside this repository audit and remain unknown.

| Surface | Completeness | Need | Evidence and recovery decision | Disproof hook |
|---|---|---|---|---|
| Skill mode router and upgrade discipline | `WORKING_UNIT_UNPROVEN` | `REQUIRED` | `kc-dev-flow/skills/adopt-dev-flow/SKILL.md:21-28` already supplies audit/adopt/upgrade routing and `:30-40` supplies reverse recovery. Reuse its interaction and authority pattern; keep projection in a distinct skill because kernel adoption and external projection have independently changeable credentials and installed bytes. | Invoke the installed skill in isolated Claude and Codex homes; inability to select and preview a mode flips it to `EXISTS_BROKEN`. |
| Deterministic bounded frontmatter/input receipts | `WORKING_UNIT_UNPROVEN` | `REQUIRED` | `scripts/dev-flow-work-context-check.py:75-84` already binds input bytes to SHA-256 and `:138-179` parses selected frontmatter fail-closed without a YAML dependency. Recover these patterns but do not import the repository-only product/sprint validator into the portable projector. | A fixture with duplicate/malformed generic fields that passes parsing flips this to `EXISTS_BROKEN`. |
| Schedule plus manual-dispatch Actions shape | `WORKING_UNIT_UNPROVEN` | `REQUIRED` | `.github/workflows/e2e-pipeline-real-browser.yml:49-56` demonstrates schedule, `workflow_dispatch`, and narrow permissions in this repository. It does not prove split-state event delivery or personal Project write permissions, so AC-4/6 retain the live spike. | A disposable split-state run that cannot reconcile from both pinned refs flips the selected topology to `EXISTS_BROKEN`. |
| GitHub Project/Issue projection adapter | `MISSING` | `REQUIRED` | Neither domain search nor the complete kc-dev-flow/scripts/workflow inventory found ProjectV2 item mutation, qualified identity lookup, or receipt reconciliation code. Add one deterministic projector only after its fake-adapter RED case fails. | Discovery of an importable existing adapter that passes the same fake/live contract changes the plan to recovery. |
| Installable projection templates/config | `MISSING` | `REQUIRED` | Existing plugin bytes contain no projection workflow/config/projector templates. Add only the target-repository bytes required by the selected spike; do not add a daemon or hosted service. | A supported host-native installation surface that can produce an auditable target diff removes the vendored-template proposal. |
| Status snapshot producer | `MISSING` | `REQUIRED` | No versioned reconcile snapshot exists. Add only the deterministic producer seam to this task; the status-update sibling owns delta rendering and publication. | An existing producer accepting projector receipts and passing stable-schema fixtures changes this to recovery. |

Audit refresh at `origin/main@5f14040b22f0c7f019398d7209981226b9782ac2`: the intervening product change only corrected adopted-mod routing and added the mechanism-necessity refusal. It introduced no ProjectV2 adapter, installable projection template, or status snapshot producer, so the table's completeness classifications remain unchanged. The new necessity rule applies to the proposed scheduled reconcile automation:

- `Criterion:` AC-5, AC-8, AC-9, and AC-11 require an installable convergence path that recovers after a missed fast-path dispatch and makes delayed reconciliation visible.
- `Alternative:` retain only explicit `workflow_dispatch` after state push. It is lower authority and remains the preferred removal target, but it is insufficient until dogfood proves missed dispatches and failed runs still meet the freshness window without schedule recovery.
- `Escape:` speculative until 2026-09-14; review backlog seed `spacedock-projector-automation-sunset-review` (`pm`). Removal is the default unless receipt history plus a schedule-disabled mutant demonstrates a named liveness failure.

### Route, carve, and pre-mortem

The smallest current route is one projection skill plus one deterministic projector whose install mode vendors the reviewed config/workflow/script bytes. No reusable workflow repository, Action package, daemon, database, webhook service, or LLM call belongs in the runtime path. The GHA file is an execution shell over the same projector used by local dry-run and manual dispatch.

The accepted carve has two slices in one projection journey. Slice 1 proves the split-state trigger and dedicated-credential topology in a disposable repository/Project, then performs a one-entity round trip and no-op rerun. Slice 2 installs into `kc-claude-plugins`, dry-runs ten entities, applies an approved bounded subset, proves foreign-fixture preservation and no-op convergence, emits the versioned status snapshot, and leaves the grouped view usable. Status draft/publish work is the named `spacedock-project-status-updates` sibling because its API, credential, baseline, and confirmation failures cannot block projection value.

Pre-mortem: the design ships and still fails because installation appears portable while every adopter needs bespoke schema, token, and trigger repair; the disproof is a second-repository dry-run that requires code edits rather than config/profile selection.

## Acceptance criteria

**AC-1 — Generic capability discovery is schema-driven**

Given the two real commissioned workflows in this repository plus a focused non-kc fixture with custom stages such as `inbox → building → checking → released` and no `product` or `sprint`, the installer emits a deterministic capability report from each workflow README and state ref. It accepts real extension keys, `id-style: slug`, an empty stored ID, absent `score`, and nullable or omitted optional structures without weakening the initial/terminal invariants. The non-kc fixture remains projectable, receives exact dynamic `SD Stage` values, and does not receive `SD Product` or Milestone writes.

Verified by: fixture tests over commissioned workflow READMEs plus representative entity files, asserting the planned fields and mapping decisions. Falsified by: renaming the non-kc stages or removing its optional dates changes only the discovered profile, while any fixed kc stage list or required product causes the test to fail.

**AC-2 — Mapping is field-local and idempotent**

The projector classifies every entity as `CREATE`, `UPDATE`, `NO_CHANGE`, `PARTIAL`, or `CONFLICT`. Missing optional fields cannot suppress a valid Issue identity/title/status projection. Every target field declares all source dependencies: for example, kc-dev-flow's scheduled-backlog → Ready mapping depends on a valid sprint pair, so a malformed sprint suppresses both Milestone and that derived Status write rather than silently treating the item as unscheduled. A second run over identical entity bytes and GitHub state performs no mutation.

Verified by: a fake GitHub adapter with operation receipts for a mixed ten-entity corpus, including missing product, blank sprint, existing linked Issue, terminal item, and conflicting lifecycle. Falsified by: rerunning the same input emits any create/update operation, or blank product prevents Issue creation.

**AC-3 — Project fields serve explicit views or metrics**

The generic default creates only `SD Stage`. The kc-dev-flow profile may add `SD Product`, `SD Started`, and `SD Completed`; qualified sprint may use Milestone in a later approved slice; Priority, Size, Estimate, and Cycle are never inferred. V1 never creates `SD Workflow`, because one configuration selects one workflow and one Project. Installation prints, for every created field, its source authority, blank behavior, and intended group/filter/chart use. Projection freshness is time-bearing reconcile evidence, never a frozen per-item `Current` enum.

Verified by: installer dry-run snapshot and Project schema fixture. Falsified by: an unknown custom field silently becomes a Project field, `sprint` writes Cycle, or the installer creates a duplicate `SD Sprint` field.

**AC-4 — Trigger topology is proven, not assumed**

A live disposable-repository experiment determines whether a workflow present only on the default branch runs on a push that changes only a split state branch lacking that workflow. It records `git ls-tree <state-ref> -- .github`, the no-workflow experimental push and documented absence, a state-ref-with-workflow positive control, and a manual-dispatch positive control with exact refs and run IDs. The chosen v1 topology must then prove automatic reconciliation without adding a hidden local hook.

The decision compares exactly three supported options:

1. default-branch `schedule` plus `workflow_dispatch` reconciliation;
2. a minimal workflow present on the state branch and triggered by state push;
3. default-branch `repository_dispatch` emitted by an authenticated state-push integration.

Selection criteria are event latency, state-branch pollution, required credential surface, retry/reconcile behavior, workflow upgrade path, and convergence through idempotent apply. V1 pre-registers option 1: default-branch schedule as the liveness safety net plus `workflow_dispatch` as the fast path. Flip away from it only if the disposable proof shows it cannot meet the configured freshness window or fresh-install dispatch is unreliable. If immediate event-driven behavior requires changing Spacedock or installing state-branch workflow bytes, state that explicitly rather than claiming a default-branch push listener can observe the split branch. An explicit setup/dev-flow operation may invoke `gh workflow run` after a successful state push without becoming a hidden git hook.

Verified by: links to the disposable repository workflow files, commits, Actions runs or documented absence, and a decision record naming the winning v1 topology. Falsified by: the selected trigger cannot reproduce after a fresh install, or relies only on documentation interpretation without a live branch experiment.

**AC-5 — Installer skill produces reviewable, least-authority output**

One setup skill supports `install` and `audit`; v1 upgrade is an install re-run that prints a target diff. Install pins the target repository, trunk ref, state ref, workflow directory, Project owner/number/ID, mapping profile, generated field plan, projector version, and projector byte digest. It defaults to dry-run and shows exact files and external Project mutations before applying them. Local dry-run executes the vendored target bytes or refuses when their digest differs from the reviewed projector. At runtime the projector re-derives capabilities from both pinned inputs and refuses mutation if they disagree with the reviewed config. It never stores or prints credential values.

Verified by: install into a fixture repository, diff of exactly the expected workflow/config/script files, and a no-secret output scan. Falsified by: installation mutates an unconfirmed Project, copies local `gh` credentials, or requires editing the installed YAML by hand to select a generic profile.

**AC-6 — GitHub authentication is explicitly supported**

The workflow separately proves same-repository Issue access and user-owned Project #1 access. Current live evidence shows Project #1 is a private user-owned Project with Board, Roadmap, and Table views; current Projects v2 REST and GraphQL surfaces both require direct capability probing rather than inheriting an older GraphQL-only assumption. The spike must test the actual REST and/or GraphQL mutations chosen by the implementation and record a fine-grained-token attempt before any classic-PAT fallback. The workflow uses a dedicated projector credential stored under a named repository secret, never the operator's ambient local `gh` credential. The setup receipt identifies token type, minimum permissions, secret name, expiry, rotation/revocation owner, and fallback blast radius; it rejects an unsupported token before partial mutation and keeps `GITHUB_TOKEN` for repository-scoped writes.

Fresh read-only evidence on 2026-08-14 confirms Project #1 ID `PVT_kwHOABc8eM4A-a-N`, zero items, and native Status options `Todo`, `In Progress`, and `Done`. Current official REST documentation for list/add/update items and add fields on a user-owned Project states that those endpoints do not support fine-grained PATs or GitHub App tokens. Therefore REST v1 must either use a dedicated classic PAT with explicit blast-radius acceptance or be displaced by a separately proven narrower GraphQL route; local ambient `gh` success does not decide the workflow credential.

Verified by: read-only Project probe followed by a reversible fixture-item mutation using the documented secret in a disposable target, with negative coverage for an insufficient token. Falsified by: the workflow creates an Issue and only then discovers it cannot add or update the Project item.

**AC-7 — Projection receipts prove identity and freshness without state feedback**

Every managed Issue records repository- and workflow-qualified identity, slug, optional non-empty SD entity ID, state ref, trunk audit commit, state audit commit, entity digest, projector version, projector byte digest, and ownership mode in one bounded machine block. Lookup by existing `issue` reference or qualified identity cannot create duplicates. Freshness compares entity digest, not only branch head. No successful run writes to the SD state branch.

Verified by: duplicate/search fixtures, an unrelated state commit that leaves an entity `Current`, and a changed entity that becomes `Stale` until projected. Falsified by: an unrelated entity change marks every receipt stale or creates another Issue.

**AC-8 — One installed workflow reconciles safely**

The installed workflow checks out exact trunk and state commits, serializes projector writes with `cancel-in-progress: false`, runs both credential preflights and all validation before mutation, emits a machine-readable summary, and leaves conflicts visible without overwriting human-owned Issue content. Manual dispatch and the selected automatic trigger converge through the same projector path. Human edits to `SD *` fields are explicitly non-authoritative and are restored on the next successful reconcile.

Verified by: dry-run, first apply, repeated no-op apply, concurrent-run test, and one conflict fixture. Falsified by: two overlapping runs create duplicate Issues, or trigger-specific paths implement different mapping logic.

**AC-9 — Liveness failure is visible**

The installation exposes when reconciliation has not completed within its configured freshness window, provisionally three times the selected schedule interval, including a disabled/delayed schedule or expired Project token. The signal compares the timestamped last-successful reconcile receipt against that window; silence cannot look like a quiet, current Project.

POC verification is local: deterministic clock fixtures cover fresh, overdue, missing-receipt, and failed-auth observations through the fake adapter. The live negative procedure — disabling the real schedule and separately using an expired/invalid GitHub credential — is deferred until production-readiness and does not block the eight-hour POC.

Verified by: local clock/receipt fixtures now; later live schedule-disable and invalid-token evidence before a production-ready claim. Falsified by: the last successful projection remains visually `Current` indefinitely or the local and live freshness decisions disagree.

**AC-10 — Archive and removal semantics are explicit**

When an entity moves to `_archive/`, the projector retains qualified identity, marks the Project item archived or an equivalent explicit terminal projection, and closes only projector-owned Issues when policy permits. A pre-existing linked Issue is never closed merely because the SD entity was archived. A foreign Project item without a projector receipt is never changed. Deletion without an archive tombstone is quarantined rather than silently removing history.

POC verification is local: fake-adapter fixtures cover projector-owned, linked, foreign, and missing-tombstone cases through create → archive → reconcile → no-op. The equivalent disposable GitHub live procedure is deferred until production-readiness and does not block the eight-hour POC.

Verified by: fake-adapter before/after operation receipts now; later disposable GitHub Issue/Project readback before a production-ready claim. Falsified by: charts retain an apparently active orphan, a linked human Issue is closed, a foreign item changes, or a missing tombstone is treated as archive.

**AC-11 — The deployed slice proves value and bounded cost**

After disposable trigger/auth proof, the first dogfood vertical slice uses `iamcxa/kc-claude-plugins` `docs/dev` with its true split state branch, checks out both refs, dry-runs ten representative entities against Project #1, then projects an explicitly approved bounded subset. Before apply it creates two deliberate receipt-less Project fixtures: one title collision and one item with a hand-set real `SD Stage`. It re-runs to zero mutations, preserves freshness after an unrelated entity change, and proves both foreign fixtures unchanged by field-level before/after readback. It records a bounded API request count and fails resumably under a simulated rate limit. The credential spike also probes whether saved-view creation is API-reachable; otherwise grouping the existing Project view is a documented manual operator step and automated evidence ends at correct field values.

Verified by: disposable proof URLs and run IDs, Project #1 dry-run/apply receipts, GraphQL or REST request log, no-op receipt, foreign-fixture before/after evidence, and either saved-view evidence or the documented manual grouping fallback. Falsified by: only fake-adapter tests pass, either receipt-less fixture changes, or the Project UI cannot answer the stated question after the supported grouping step.

**AC-12 — Reconcile emits the stable producer seam for the status sibling**

Every successful reconcile emits a versioned deterministic snapshot containing pinned trunk/state commits, workflow/Project identity, qualified sprint identities when present, member-set digest, stage counts, terminal count, projection conflicts/freshness, and available goal/exit-criterion digests. Identical inputs produce byte-identical facts apart from an explicitly excluded observation timestamp. This task performs no Project Status Update mutation and invokes no LLM.

Verified by: golden snapshot fixtures for generic and kc-dev-flow profiles plus a fake Project Status Update adapter proving zero mutations. Falsified by: the snapshot invents missing schedule/health evidence, changes metric values across identical inputs, or any runtime path drafts or publishes narrative text.

## Open questions for independent review

1. Is a default-branch workflow genuinely unable to receive a `push` event for a split state branch when the workflow file is absent from that state ref, and what is the smallest live experiment that settles it?
2. Among schedule polling, state-branch workflow, and repository dispatch, which is the smallest safe v1 given that SD state commits originate from local agents and no SD core change is currently authorized?
3. Can a user-owned GitHub Project be updated from Actions with a narrower credential than a classic user token today, or must v1 explicitly accept that limitation?
4. Which generic SD fields are stable enough for automatic Project schema creation, and which must remain opt-in profile mappings?
5. Does the proposed Issue ownership split preserve trustworthy historical charts without allowing the projector to close pre-existing human Issues?

## Independent ideation challenge — Claude Opus 5, 2026-08-14

Fresh read-only session `66e5b3f0-8f11-4d26-ba32-9d82da61b1c3` completed with reported model `claude-opus-5`, Read-only tooling, safe mode, no MCP, and no Bash/Edit/Write. The reviewer reported **narrow**, explicitly did not treat the prior review as approval, and did not run the required live GitHub experiments.

The accepted material corrections are:

- Remove the frozen `SD Projection = Current` field. Use receipt state plus a timestamped installation-level reconcile receipt and a numeric freshness window.
- Create deliberate receipt-less fixtures before Project #1 apply; an empty Project cannot prove foreign-item safety.
- Require a dedicated named projector secret with token type, least-permission attempt, expiry, rotation/revocation owner, and explicit fallback blast radius. Ambient local `gh` credentials are never installed.
- Pre-register schedule + manual dispatch as v1 and record the exact branch controls that could falsify it. Idempotent reruns prove convergence, not exactly-once delivery.
- Bind local dry-run to the installed projector byte digest, not a version label alone.
- Probe saved-view API capability and retain a documented manual grouping fallback.
- Split status draft/publish into `spacedock-project-status-updates`; this task ends at the versioned deterministic snapshot producer. The sibling must reject foreign baselines and mechanically refuse rewritten facts not present unchanged in the manifest.

The review also recommends deferring Milestone writes from the first projection slice and collapsing a separate `upgrade` mode into `install --diff`. Both fit the captain-approved eight-hour appetite and keep the first round trip to Issue + Project item + receipt + no-op convergence.

## Fresh ideation EM gate — Claude Opus 5, 2026-08-14

Read-only session `54df0ad0-656b-45a7-93c5-484ef67450cb` returned the following closed compatibility record. It ran with reported model `claude-opus-5`, Read-only tooling, safe mode, no MCP, and no Bash/Edit/Write. It did not run commands or verify the supplied digests independently.

```yaml
science_officer_em_upward_report:
  em_judgment: "Approve the ideation gate as an evidence-only judgment. The three artifacts are internally consistent and mutually traceable, all four findings hold on the text as read, and the first admissible action is fully local and reversible, so approval mints no external authority. One material limit is recorded rather than waived: AC-9 liveness and AC-10 archive carry live procedures named in neither the accepted carve nor the ROADMAP projection exit."
  evidence_synthesis: "The projection task, status sibling, and proposed ROADMAP describe the same eight-hour two-slice projection journey, two-hour trigger and credential stop, stable snapshot dependency, and local-first fake-adapter route. Every accepted Claude correction lands in a numbered falsifiable criterion. Material limits: the reviewer did not recompute supplied hashes; reverse-recovery evidence predates origin/main@5f14040b22f0c7f019398d7209981226b9782ac2; AC-9 and AC-10 live procedures exceed the recorded carve; and trigger, credential, saved-view, and mutation-surface questions remain live-unproven by design."
  risk_tradeoff_call: "Benefit: a bounded, traceable one-way SD view whose protected core is deterministic projection, receipts, ten-entity dry-run, and no-op convergence. Risk: silent appetite overrun through AC-9 and AC-10, plus an unfavorable trigger or personal-Project credential result; the two-hour stop contains the latter. Durable cost is only reviewable vendored bytes and fixtures. Returning solely to rewrite criteria would delay the empirical proof without improving the current stop rules."
  recommendation: "Record ideation approval only. Mint no token, create no repository or Project, change no secret, write nothing to Project #1, and let the stage owner advance separately. Begin only with local deterministic fixtures, fake-adapter RED cases, and vendored installer/projector bytes. Before external proof, obtain bounded approval. At design entry, explicitly defer or include AC-9 and AC-10 live procedures, and refresh reverse recovery against origin/main@5f14040b22f0c7f019398d7209981226b9782ac2."
  route: proceed
  confidence: high
  multi_model: not_needed
  fo_boundary: ""
  engineering_judgment:
    question: "Does the captain-narrowed kc-dev-flow/S3 projection pass ideation, are F1-F4 supported, and may its first action remain fully local?"
    revision: "projection 8b1de63d211bfc58cf5900b6c3bcae4012846df4 sha256 e0e6033ad05cd8af7ad1d088c394dda020c36aa821a11cb838298a8b55595c8b; status sibling 3b51fee85285047bd85227b71865047c1e1559e2 sha256 db62e7e0ede948ce9790131e0ba295339441f09aaadf81c98ee5a0ffaeb9a82b; proposed ROADMAP sha256 acdf9d4131880de29afcd594dc980962dacc9424a21313dcd408a31ca8c758cb; base origin/main@5f14040b22f0c7f019398d7209981226b9782ac2"
    evidence_synthesis: "The projection task, status sibling, and proposed ROADMAP describe the same eight-hour two-slice projection journey, two-hour trigger and credential stop, stable snapshot dependency, and local-first fake-adapter route. Every accepted Claude correction lands in a numbered falsifiable criterion. Material limits: the reviewer did not recompute supplied hashes; reverse-recovery evidence predates origin/main@5f14040b22f0c7f019398d7209981226b9782ac2; AC-9 and AC-10 live procedures exceed the recorded carve; and trigger, credential, saved-view, and mutation-surface questions remain live-unproven by design."
    adjudications:
      - finding: F1
        disposition: supported
        basis: "The carve, sizing, and ROADMAP define one observable journey from disposable proof through Project #1 stage grouping and a stable snapshot; appetite fit is protected by the recorded stop and cut order."
      - finding: F2
        disposition: supported
        basis: "The status work has its own task and acceptance criteria, depends explicitly on the snapshot, and cannot block projection because AC-12 verifies zero status-update mutations."
      - finding: F3
        disposition: supported
        basis: "All seven corrections are testable numbered clauses; remaining trigger, credential, saved-view, and API questions are bounded empirical probes rather than missing design surfaces."
      - finding: F4
        disposition: supported
        basis: "AC-1, AC-2, AC-3, AC-7, and AC-12 admit fixture and fake-adapter RED work before any external mutation; each live mutation remains separately gated."
    risk_tradeoff: "Benefit: a bounded, traceable one-way SD view whose protected core is deterministic projection, receipts, ten-entity dry-run, and no-op convergence. Risk: silent appetite overrun through AC-9 and AC-10, plus an unfavorable trigger or personal-Project credential result; the two-hour stop contains the latter. Durable cost is only reviewable vendored bytes and fixtures. Returning solely to rewrite criteria would delay the empirical proof without improving the current stop rules."
    recommendation: "Record ideation approval only. Mint no token, create no repository or Project, change no secret, write nothing to Project #1, and let the stage owner advance separately. Begin only with local deterministic fixtures, fake-adapter RED cases, and vendored installer/projector bytes. Before external proof, obtain bounded approval. At design entry, explicitly defer or include AC-9 and AC-10 live procedures, and refresh reverse recovery against origin/main@5f14040b22f0c7f019398d7209981226b9782ac2."
    route: proceed
    confidence: high
    dissent: "The criteria are broader than the accepted two-slice carve: AC-9 and AC-10 require disabled-schedule, invalid-token, and create/archive/reconcile live procedures that appear in neither the carve nor the ROADMAP projection exit. State their disposition before implementation rather than discovering the mismatch at hour eight."
    disproof_condition: "Narrow or return if fresh reverse recovery finds an importable adapter or snapshot producer, supplied digests do not match, AC-9 and AC-10 live procedures stay inside the same eight hours, the two-hour proof finds no supported trigger/credential route, the first RED case needs a live external write, or the sibling becomes a projection prerequisite."
    authority_boundary: "The captain retains scope, appetite, sequencing, deferrals, re-cut, and all external provider authority. The gate advances no stage, commits no ROADMAP, starts no implementation, and grants no repository, Project, token, secret, merge, release, or S2-hold authority."
```

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

## Stage Report: ideation

- DONE: Bound the POC to eight human-hours with a two-hour trigger/credential deviation stop, one setup skill, one deterministic projector, and no external mutation authority.
- DONE: Recovered existing router, digest, frontmatter, and Actions seams; confirmed Project adapter, installable templates, and snapshot producer remain missing at fresh `origin/main@5f14040b22f0c7f019398d7209981226b9782ac2`.
- DONE: Apply the new automation-necessity rule. The schedule serves AC-5/8/9/11, manual dispatch remains the lower-authority alternative, and backlog seed `pm` reviews removal on 2026-09-14.
- DONE: AC-1 through AC-8, AC-11, and AC-12 define local-first or bounded-live falsifiers for portability, mapping, schema, topology, install, credentials, receipts, convergence, dogfood value, and the snapshot producer.
- DONE: `spacedock status --read qa --ac-scan` resolves AC-1 through AC-12 at lines 150-224. It reports `unevidenced=true citations=0` for AC-2, AC-3, AC-4, AC-6, and AC-7 despite each containing a `Verified by:` paragraph, matching the ROADMAP's known citation-counter hazard rather than proving missing evidence.
- DONE: Fresh Claude architecture challenge returned `narrow`; its material corrections are incorporated. Fresh ideation EM session `54df0ad0-656b-45a7-93c5-484ef67450cb` returned `proceed / high / multi_model:not_needed`, supporting F1-F4 and preserving every captain/external-provider boundary.
- DONE: Captain decision on 2026-08-14 defers AC-9 liveness and AC-10 archive live procedures until production-readiness while retaining their local deterministic/fake-adapter contract fixtures in the eight-hour POC.
- PENDING DELIVERY: accept the proposed ROADMAP split that schedules `spacedock-project-status-updates` (`16`) after the projection snapshot contract. No repository commit or PR exists yet.

### Summary

Proceed after the single ROADMAP commit is accepted. The first implementation action remains local fake-adapter RED tests and vendored bytes; disposable repositories, Projects, credentials, secrets, Project #1 apply, and AC-9/AC-10 live procedures retain separate approval gates.

## Stage Report: implementation (cycle 1 — local planner)

- DONE: Initialized `setup-github-project-projection` through the canonical skill-creator scaffold with concise SKILL.md, Codex UI metadata, a progressive-loaded mapping contract, and one deterministic vendored projector asset.
- DONE: Recorded RED before implementation. `python3 kc-dev-flow/scripts/project-spacedock-state.test.py` failed because `assets/project-spacedock-state.py` did not exist.
- DONE: GREEN covers five deterministic contracts: dynamic non-kc stages with missing kc optional fields, create/apply/no-op convergence, projector-owned versus linked archive state plus foreign-item preservation, missing-tombstone conflict, and time-bearing freshness plus stable status snapshot. The suite reports 5/5 passing.
- DONE: Fresh Project #1 read-only probe confirms project ID `PVT_kwHOABc8eM4A-a-N`, zero items, 14 fields, and Status options `Todo`, `In Progress`, `Done`. The projector now negotiates those actual options and omits Status when none is compatible while always preserving exact `SD Stage`.
- DONE: Python compilation, repository skill-frontmatter lint across 41 skill directories, and `git diff --check` pass. Skill-creator `quick_validate.py` is unavailable because its host environment lacks the PyYAML module; no dependency was installed or changed.
- IN PROGRESS: file installer, Actions workflow, and GitHub adapter remain uncommitted. A non-empty disposable Project is required to observe exact `gh project item-list` bytes and prove one reversible item/field mutation before freezing the adapter.
- BLOCKED BY AUTHORITY, not implementation uncertainty: creating a disposable repository/Project, minting or storing a credential, or writing fixtures requires a separate bounded captain approval. Current official REST documentation says user-owned Project item/field endpoints reject fine-grained PATs and GitHub App tokens; the proof must compare a narrower GraphQL route before accepting a dedicated classic-PAT fallback.

### Summary

The local deterministic seam is real and testable, but it is not yet an automatic sync. Continue only after bounded approval for disposable trigger/credential/API-shape proof; Project #1 remains read-only and empty.

## Stage Report: implementation (cycle 2 — installer and live read-only proof)

- DONE: Captain approved disposable trigger/API-shape proof. Created private disposable repository `iamcxa/spacedock-projection-proof` and user Project #3; Project #1 remained read-only and empty.
- DONE: Trigger controls used a true orphan `spacedock-state/dev@ea12a0eb9df2b4971516b30005bf0a2fe15b2924` with no `.github` tree. Its push created no Actions run. A workflow-bearing control push created run `31761294869`, and default-branch manual dispatch created run `31761324704`, proving event/workflow resolution. Both positive runs stopped before runner steps because GitHub reported a failed payment or spending-limit condition, so runner execution and scheduled convergence remain unproven.
- DONE: Project #3 exposed REST 2026-03-10 fields and items as arrays keyed by numeric field IDs. The disposable `SD Stage` field is numeric ID `379617073`; the projector now normalizes numeric REST IDs rather than the CLI display key `sD Stage`.
- DONE: Added a dry-run-first installer for exactly the workflow, JSON config, and projector bytes. Generated workflow validation passes `actionlint`; it has default-branch `workflow_dispatch`, schedule convergence, separate state checkout, `issues: write`, serialized writes with `cancel-in-progress: false`, and a failure artifact path. External apply remains false unless a reviewed config records credential metadata and explicitly arms it.
- DONE: Added the REST adapter with separate repository/Project authorities, pagination, receipt recovery for an Issue stranded before Project insertion, numeric field writes, resumable create/update order, and single-select option extension that preserves observed options. The local contract suite now passes 11/11, including quoted real-world Issue references, foreign fields, archive ownership, no-op convergence, installer audit, and REST operation ordering.
- DONE: A live read-only reconcile against disposable Project #3 used trunk `411a44b07789eaaa70a8edebb7f60f12226d2bd8` and orphan state `ea12a0eb9df2b4971516b30005bf0a2fe15b2924`. It planned three creates, no schema change, zero conflicts, and emitted deterministic counts `inbox=1`, `building=1`, `released=1`; Project #3 remained one pre-existing fixture item.
- DONE: A live read-only ten-entity dogfood plan against Project #1 used trunk `5f14040b22f0c7f019398d7209981226b9782ac2` and state `6dd6001f193c1dd1e6afcd5faa5a78f7455b4e0e`. It produced 5 `CREATE` and 5 `PARTIAL` classifications, zero conflicts, ten planned entity mutations, and schema plans for `SD Stage` plus `SD Product`. Missing optional product/sprint values did not suppress any Issue projection, and quoted `issue: "189"` now resolves to linked ownership. Project #1 readback remained zero items after the run.
- BLOCKED LIVE: GitHub Actions runner proof cannot continue until the account billing/spending-limit condition is fixed. This blocks runner execution evidence, not local workflow resolution or deterministic planning.
- BLOCKED AUTHORITY: The selected user-owned Project REST endpoints do not accept fine-grained PATs or GitHub App tokens. Arming Project #1 therefore requires explicit acceptance of a dedicated classic PAT's blast radius, expiry, rotation owner, and repository secret; no token was minted, copied, or stored.
- IN PROGRESS: Product bytes remain uncommitted pending final focused review and captain confirmation of the exact commit set. AC-9/AC-10 live negative/archive procedures remain deferred under the approved POC carve.

### Summary

The installable local path and both live read-only projections are working. Automatic runner execution and any Project #1 mutation remain intentionally unclaimed until billing and credential authority are resolved.

## Stage Report: implementation (cycle 3 — focused review correction)

- DONE: Fresh read-only Claude Opus 5 High review session `9f800dfa-30c7-4272-b883-7621ca767b18` returned `narrow`. Its Critical finding was valid: comparing full receipts made unrelated trunk/state commits rewrite every entity because audit commits changed. Managed equality now compares entity-local identity/digest/ownership/archive plus projector identity while retaining trunk/state commits as non-equality audit provenance. A regression changes both commits and proves `NO_CHANGE`; a projector digest change still earns one migration update.
- DONE: Removed automatic GraphQL replacement of existing single-select option sets. A missing option is reported as `UPDATE_FIELD_OPTIONS` and apply refuses before any write, avoiding unproven option-ID preservation. Missing fields may still be created after the conflict-free schema preflight.
- DONE: Explicitly linked repository Issues are now observed even without a projection receipt. Linked title, body, and open/closed state are preserved; a missing linked Issue or duplicate Issue reference is a conflict. Projector-owned Issues receive a bounded human-readable Spacedock summary plus the machine receipt and never publish `worktree`.
- DONE: Runtime entity discovery skips non-entity Markdown, excludes private underscore directories, recognizes `_archive` at nested depths, and still rejects a file that partially declares but fails the entity baseline. Unexpected runtime exceptions now emit a failure receipt instead of losing the artifact.
- DONE: Removed the unused persisted freshness-window configuration and bounded the documentation: deterministic clock decisions exist, but a decaying last-successful liveness signal is deferred. The workflow now resolves the repository default branch through the authenticated repository API rather than assuming a schedule event payload shape.
- DONE: Registered the focused suite in `scripts/kc-dev-flow-contract-test.py`. Final local results are 17/17 projection tests, kc-dev-flow contract PASS, generated-workflow `actionlint` PASS, 41/41 skill frontmatter PASS, version parity PASS, marketplace L0-L2 PASS, and `git diff --check` PASS.
- DONE: Repeated the live Project #1 ten-entity dry-run at state `2534b88fdec5d7f02b500882268299e87f502755`. It still reports zero conflicts and ten planned entity mutations; Issues #90 and #189 are now explicitly `linked` updates while Project #1 remains at zero items.
- LIVE-UNPROVEN: The REST create/add/field-write payloads, runner execution, schedule execution, and post-apply convergence have not executed against GitHub. Product documentation and delivery must preserve that boundary until billing is fixed and a dedicated Project credential is approved.

### Summary

The focused review found and closed the cross-run idempotency defect plus linked-Issue and option-identity hazards. The remaining blockers are live provider execution and credential authority, not a known local planner/installer failure.

## Stage Report: implementation (cycle 4 — public free-runner proof)

- DONE: Captain approved the public synthetic fallback. Created public disposable repository `iamcxa/spacedock-projection-public-proof`; default branch `main@9a0b7b6105b9f4063b9ad1fe12c77b646b8ea25b` contains only synthetic workflow/config/projector bytes, and true orphan `spacedock-state/dev@03cdc090cc6eb6e8ccf4aebca18cf0f57df147ff` contains three synthetic entities with no `.github` tree.
- DONE: Public standard-runner smoke run `31766471570` completed successfully, proving the earlier private-repository billing failure can be bypassed without paid Actions minutes. Projector runs `31766507882`, `31766540815`, and `31766595885` all started runner jobs, checked out both trunk and orphan state refs, reached the deterministic reconciler, and uploaded a failure receipt.
- DONE: The projector failure is the expected authority boundary, not runner failure: built-in `GITHUB_TOKEN` receives `403 Resource not accessible by integration` when reading private user Project #3. No repository secret or ambient local credential was copied, and no GitHub Issue or Project mutation occurred.
- DONE: A local authenticated read-only reconcile over those exact public refs and Project #3 classified `alpha`, `bravo`, and `charlie` as three `CREATE` operations, zero conflicts/orphans, no Project schema change, and deterministic counts `inbox=1`, `building=1`, `released=1`, terminal `1`.
- DONE: Live runner warnings showed `actions/checkout@v4` and `actions/upload-artifact@v4` were deprecated Node 20 actions forced onto Node 24. Official latest releases were v7.0.1 for both; the installed template now uses `@v7`, its generated workflow passes `actionlint`, and run `31766595885` has no Node 20 warning. The focused suite remains 17/17 and the registered kc-dev-flow contract, frontmatter, parity, marketplace L0-L2, and diff checks pass.
- UNOBSERVED: No schedule event appeared during the bounded six-minute observation window after registration. GitHub permits scheduled-run delay, so this is latency evidence rather than a failed schedule verdict; manual dispatch is proven.
- BLOCKED AUTHORITY: A full remote apply and no-op rerun still require a dedicated supported Project credential. The built-in repository token is now live-proven insufficient, and the local OAuth token remains ambient operator authority that may not be installed as a secret.

### Summary

The no-cost hosted-runner route works and exercises the real split-ref workflow through its credential boundary. Remaining live proof is a dedicated user-Project credential plus bounded apply/no-op convergence; schedule delivery is still unobserved rather than failed.

## Stage Report: implementation (cycle 5 — live apply and no-op convergence)

- DONE: Captain supplied the named `SPACEDOCK_PROJECT_TOKEN` secret directly in the public proof repository. Its reviewed config records `classic-pat`, `project`, expiry `2026-08-21`, rotation owner `iamcxa`, and the user-Project blast radius; the secret value was never read, printed, copied, or stored locally.
- OBSERVED DEFECT: First armed run `31767953290` successfully created three Issues, added three Project items, and wrote `Status` plus `SD Stage`, then failed its post-apply convergence check. Readback isolated one residual UPDATE: non-archived terminal entity `charlie` was closed after `Status=Done`, while the projector still expected every non-archived projector-owned Issue to remain open.
- DONE: Added a RED contract proving an exact terminal stage closes a projector-owned Issue while a linked human Issue remains open. It failed `CLOSED != OPEN` before the correction. The projector now treats terminal stage or archive as closed only for projector ownership; the suite passes 18/18 after the one-rule correction.
- DONE: Corrected live run `31768086308` updated all three receipts for the new projector digest and completed successfully. Its artifact records three UPDATE classifications, six Issue/field operations, then zero post-apply mutations and zero orphans.
- DONE: Identical rerun `31768117401` completed successfully with `alpha`, `bravo`, and `charlie` all `NO_CHANGE`, zero planned mutations, zero operations, zero converged mutations, and zero orphans. Snapshot counts remain `inbox=1`, `building=1`, `released=1`, terminal `1` at state `03cdc090cc6eb6e8ccf4aebca18cf0f57df147ff`.
- DONE: Field-level readback confirms managed Issues #1/#2 remain open with `Todo/inbox` and `In Progress/building`; managed Issue #3 is closed with `Done/released`. Pre-existing foreign item `228509911` remains the original `iamcxa/spacedock-projection-proof#1`, open with `Todo/inbox`.
- DONE: Final local gates pass: 18/18 focused projection tests, registered kc-dev-flow contract, generated-workflow `actionlint`, 41-skill frontmatter lint, version parity, marketplace L0-L2, and `git diff --check`.
- STILL UNOBSERVED: No automatic schedule event has appeared yet. Manual apply and no-op convergence are live-proven; scheduled delivery remains a separate latency observation rather than a claimed pass.
- BOUNDARY: Project #1 remains untouched. This disposable proof establishes the public runner, dedicated user-Project credential, actual REST mutations, receipt migration, foreign preservation, and no-op rerun, but does not authorize kc-claude-plugins dogfood apply.

### Summary

The disposable vertical slice now passes create/apply, live field readback, post-apply convergence, and a zero-operation rerun. The live failure exposed and closed the terminal-Issue lifecycle defect; only schedule observation and separately authorized Project #1 dogfood remain outside this proof.

## Stage Report: implementation (cycle 6 — product commit and Draft PR)

- DONE: Committed the reviewed nine-file product set as `96bb66ccec2a530256dd30ef4fd834d863535221` (`feat(kc-dev-flow): add GitHub Project projection installer`) without a version bump; release-please retains version propagation authority.
- DONE: Pushed `iamcxa/spacedock-github-project-projection` and opened Draft PR #227 against `main`: https://github.com/iamcxa/kc-claude-plugins/pull/227. The PR head exactly matches the committed product SHA and remains Draft while CI and review run.
- DONE: Delivery text preserves the live-evidence boundary: manual hosted apply and identical no-op rerun are proven; automatic scheduled delivery remains unobserved; Project #1 remains untouched.
- PENDING: CI completion, review, and explicit captain authorization before any Ready transition. Project #1 dogfood apply and production-readiness AC-9/AC-10 live procedures remain separately gated.

### Summary

The implementation is now reviewable as Draft PR #227 at an exact product commit. No merge, Ready transition, Project #1 mutation, or automatic-schedule claim was made.

## Stage Report: implementation rejection (cycle 7 — strict contract audit)

- REJECTED: Draft PR #227 at `96bb66ccec2a530256dd30ef4fd834d863535221` is not admissible for validation. Review reproduced a cross-repository same-number Issue collision, untrusted receipt adoption, explicit-Issue/receipt disagreement, selection-wide orphan false positives, mutable-ref dispatch exposure, lost partial-operation evidence, and absent production-`reconcile` test coverage.
- REJECTED PROCESS: implementation opened reviewer loops, did not retain RED-before-GREEN evidence for every behavior, and opened the Draft without the repository delivery hook's exact candidate/base/body and native-stack-exception receipt. Green CI does not repair those missing implementation and delivery obligations.
- RETURN TO IDEATION: AC-5/AC-8 currently require mutation to refuse when the reviewed state commit or plan digest changes, while AC-4/AC-11 require schedule-driven projection of later state-branch changes. A static approved state/plan and unattended projection of new state bytes cannot both be true. Linked-Issue body receipts also conflict with the promise never to overwrite concurrent human content, and Project #1 exposes only `Todo`, `In Progress`, and `Done` rather than the accepted AC-2 `Ready` state.
- SIZE BASELINE: the PR adds 2,299 gross lines across nine files. Runtime Python is 1,300 gross lines and 1,162 syntax-bearing lines; tests are 671 gross lines. The 1,124-line projector contains 40 functions and two classes; `plan_projection` is the maintenance hotspot at 198 lines, followed by `apply_github_plan` at 95 lines. The total is plausible for install, parse, plan, REST reconcile, receipt, and snapshot behavior, but the current responsibility density and missing production-path coverage prevent a simplicity claim.
- PRESERVE: one setup skill, one installed GHA execution shell, one deterministic projector, no daemon/database/webhook/LLM runtime, one-way SD authority, generic capability discovery, and the separately owned Project Status Update sibling.

### Proposed ideation correction — not yet accepted

1. Replace static per-run plan approval with a default-branch **automation envelope**: pin repository/workflow/Project, installed projector digest, a non-empty allowed entity set, and each approved entity-to-Issue binding. Schedule may apply changed lifecycle bytes only inside that envelope. New entities, changed Issue bindings, installed-byte drift, or broader roots return to reviewed dry-run and explicit approval. The observed state commit remains receipt provenance rather than a value whose expected change disables automation.
2. Use full `owner/repository#number` identity everywhere. Trust a projector-owned receipt only when its exact schema is valid and either the configured Project already contains the item or a stranded Issue was authored by the configured automation identity. Ignore unrelated malformed public markers; quarantine malformed selected/managed records.
3. Keep explicitly linked human Issues read-only: never patch their title, body, or open/closed state. Bind them through the approved state/config mapping and Project item identity; keep freshness in the reconcile snapshot rather than inserting a mutable body receipt. Projector-created Issues retain the machine receipt and lifecycle writes.
4. Map Project #1 without inventing a fourth native status: backlog maps to `Todo`, active SD stages map to `In Progress`, and terminal maps to `Done`; exact `SD Stage` plus qualified sprint carries the finer distinction. Adding `Ready` remains a separately approved Project-schema choice.
5. Bound the authentication claim to what the provider exposes: validate credential metadata, repository/Project identity, config, schema, conflicts, and the complete mutation plan before writes; order writes to minimize blast radius and persist an append-only operation journal after every response. Do not claim that REST proves both credentials can write without performing a mutation.

The corrected route keeps the same lifecycle surface count. It changes authority semantics and linked-Issue ownership, so fresh ideation EM judgment and captain acceptance are required before implementation resumes.

## Fresh ideation EM gate — Claude Opus 5 High, 2026-08-14

Fresh read-only session `609d2eb0-b646-4e5f-b60a-0f121a97d141` ran with reported model `claude-opus-5`, high effort, safe mode, no tools, no MCP, and no Bash/Edit/Write. An earlier fresh attempt returned provider `529 Overloaded` with no judgment and is not counted as a gate verdict. The successful EM returned `proceed / medium / multi_model:not_needed`; it independently supports F1-F5 and requires explicit envelope expiry plus forced re-attestation.

```yaml
science_officer_em_upward_report:
  em_judgment: "Replace the jointly unsatisfiable static state/plan approval with the bounded automation envelope. Full repository-qualified identity, read-only linked Issues, existing three-option Status mapping, bounded credential claims, an operation journal, retry, and the unchanged runtime topology are professionally sound. Captain approval is still required for standing external authority."
  evidence_synthesis: "F1-F5 are supported by the supplied exact artifact and contract. Static state/plan invariance cannot process the later state commits schedule exists to reconcile; bare Issue numbers cross repository boundaries; unconditional linked-Issue PATCH can overwrite humans; REST reads do not prove write capability; and the small topology is not yet sufficient because production reconcile is untested. The EM did not independently run tools, so counts and live bytes remain supplied evidence."
  risk_tradeoff_call: "The envelope buys unattended convergence while limiting writes to pinned installed bytes, explicit entities, and fixed Issue bindings. Its standing authority is the material risk and durable maintenance cost. Require expiry, re-attestation on projector digest/entity/binding changes, blast-radius ordering, an append-only journal, and bounded retry. Manual-only per-run approval is safer but abandons the accepted schedule value."
  recommendation: "Accept the six-point corrected route only with an explicit envelope expiry no later than credential expiry and forced re-attestation on projector digest, entity set, or Issue-binding change; then return to implementation and require a production-reconcile journey test before leaving Draft."
  route: proceed
  confidence: medium
  multi_model: not_needed
  fo_boundary: ""
  engineering_judgment:
    question: "Should static per-run approval become a bounded automation envelope, with the accompanying ownership, Status, credential, and minimal-stack corrections?"
    revision: "PR head 96bb66ccec2a530256dd30ef4fd834d863535221; origin/main 029047b0e7d510b71ac260f2643ec8aef52298a5; Project #1 unmutated"
    evidence_synthesis: "F1-F5 are supported by the supplied exact artifact and contract. Static state/plan invariance cannot process the later state commits schedule exists to reconcile; bare Issue numbers cross repository boundaries; unconditional linked-Issue PATCH can overwrite humans; REST reads do not prove write capability; and the small topology is not yet sufficient because production reconcile is untested. The EM did not independently run tools, so counts and live bytes remain supplied evidence."
    adjudications:
      - finding: F1
        disposition: supported
        basis: "The expected later state commit is both schedule input and the static gate's abort condition."
      - finding: F2
        disposition: supported
        basis: "The accepted same-repository boundary requires content_type plus repository_url and Issue number, which live REST bytes expose."
      - finding: F3
        disposition: supported
        basis: "Without a demonstrated atomic compare-and-swap, unconditional linked-Issue PATCH cannot preserve concurrent human content."
      - finding: F4
        disposition: supported
        basis: "Reads prove identity, not write capability; journal and bounded retry are primary partial-write safety."
      - finding: F5
        disposition: supported
        basis: "The lifecycle topology remains workflow, config, and standard-library projector; insufficient production-path coverage requires internal repair, not new infrastructure."
    risk_tradeoff: "The envelope buys unattended convergence while limiting writes to pinned installed bytes, explicit entities, and fixed Issue bindings. Its standing authority is the material risk and durable maintenance cost. Require expiry, re-attestation on projector digest/entity/binding changes, blast-radius ordering, an append-only journal, and bounded retry. Manual-only per-run approval is safer but abandons the accepted schedule value."
    recommendation: "Accept the six-point corrected route only with an explicit envelope expiry no later than credential expiry and forced re-attestation on projector digest, entity set, or Issue-binding change; then return to implementation and require a production-reconcile journey test before leaving Draft."
    route: proceed
    confidence: medium
    dissent: "Do not permit approve-once permanence. The first apply after an envelope change remains a minimal-blast-radius probe because write capability cannot be proven before mutation."
    disproof_condition: "If apply becomes manual-only, static per-run approval is sufficient; demonstrated atomic Issue-body compare-and-swap would reopen linked receipt placement."
    authority_boundary: "Captain owns envelope authority and schema; gate/work-item authority owns ACs and stage; delivery owns Draft/merge; provider owners retain credentials and Project #1. No mutation or Ready authority is granted."
```

## Out of scope

- GitHub Project changes flowing back into SD state.
- Combining kc-claude-plugins, Relay, or CarLove in one GitHub Project, or adding a cross-project portfolio layer.
- Adding `product`, `sprint`, estimate, target dates, or projection receipt fields to the generic SD entity schema.
- Automatically publishing LLM-authored Project Status Updates or enabling any unattended publish policy before a dogfood transition rule is separately approved.
- Inferring Priority, Size, Estimate, Cycle, dates, or sprint semantics from prose.
- Replacing repository-local sprint Milestones with GHP Iteration.
- Editing or committing workflow files during this backlog capture beyond the SD task itself.

## Sizing

Design required. Eight human-hours cover the disposable proof and the smallest dogfood round trip. Stop after two hours without a reproducible trigger/credential route and re-cut before adding authority or architecture. Slice 1 proves the selected trigger, dedicated credential, one entity, one receipt, and a `NO_CHANGE` rerun in disposable targets. Slice 2 dry-runs ten kc-dev-flow entities, applies an approved bounded subset to Project #1, preserves two deliberate foreign fixtures, emits the status snapshot, and leaves exact stage grouping usable. Milestone writes and all status draft/publish behavior are deferred.
