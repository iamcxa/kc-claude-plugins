---
title: Derive release story progress from local development tasks
status: implementation
product: kc-journey-map
source:
planning-window:
planning-outcome:
sprint: S1
sprint-readiness: ready
started: 2026-09-10T16:09:10Z
completed:
verdict:
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-stack-recut
issue:
pr: iamcxa/kc-claude-plugins#417
mod-block:
id: 91n5fvm5qtpf6gxd4bwhxxkg
gates:
    version: 1
    records:
        - id: gate:91n5fvm5qtpf6gxd4bwhxxkg:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:91n5fvm5qtpf6gxd4bwhxxkg-backlog-1
              briefing:
                id: briefing:91n5fvm5qtpf6gxd4bwhxxkg:backlog:attempt-1:revision-1
                digest: sha256:0a602c42d8b37ea7b1b47e1afb24c4de0ead2a31e0dfa988f4bb23b04d441834
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:91n5fvm5qtpf6gxd4bwhxxkg:backlog:1
                briefing: briefing:91n5fvm5qtpf6gxd4bwhxxkg:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T16:07:48.101427Z"
                decision: approve
                reason: Kent approved the concrete two-skill task scope with 那就按這樣繼續 and answered 可以 to adopting Pilot and the shape/build/verify route for this task. Admit this standalone brief to ideation only; the prior border commit and later implementation/delivery gates retain their authority.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:91n5fvm5qtpf6gxd4bwhxxkg:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:91n5fvm5qtpf6gxd4bwhxxkg-ideation-1
              briefing:
                id: briefing:91n5fvm5qtpf6gxd4bwhxxkg:ideation:attempt-1:revision-1
                digest: sha256:29015547bdc32627615c8b8935dfa223eef7d62baba299f7d03613a1498d939d
                room-ref: ./review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:91n5fvm5qtpf6gxd4bwhxxkg:ideation:1
                briefing: briefing:91n5fvm5qtpf6gxd4bwhxxkg:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T16:29:10.956787Z"
                decision: approve
                reason: Kent approved ideation briefing 29015547 and entering implementation, including the task-owned complete required-task mapping, separate local progress skill, source-preserving rendering, three-color development semantics, pending delivery acceptance, and the 10-file/700-line/260-reader-line stop thresholds. Kent separately approved the predecessor 12-file border local commit as the dependency base. This grants implementation and validation, not a product commit for the new progress feature or push/PR/merge/release.
              application:
                target-stage: implementation
                state: consumed
        - id: gate:91n5fvm5qtpf6gxd4bwhxxkg:validation
          stage: validation
          attempts:
            - id: gate-attempt:91n5fvm5qtpf6gxd4bwhxxkg-validation-1
              briefing:
                id: briefing:91n5fvm5qtpf6gxd4bwhxxkg:validation:attempt-1:revision-1
                digest: sha256:b88365b91c640c1549daede74139a46ba7ab6651b53f7c56829d9306cda4dea1
                room-ref: ./review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:91n5fvm5qtpf6gxd4bwhxxkg:validation:1
                briefing: briefing:91n5fvm5qtpf6gxd4bwhxxkg:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T17:08:39.651976Z"
                decision: approve
                reason: 'Kent approved validation briefing b88365b9 and the exact ten-file local commit in .context/journey-progress-commit-review.md, subject feat(kc-journey-map): derive release progress from local tasks. Authority is local validation and this local commit only. Keep validation status and terminal application unconsumed; product push, PR creation, merge, release and delivery acceptance remain separate.'
              application:
                target-stage: done
                state: superseded
            - id: gate-attempt:91n5fvm5qtpf6gxd4bwhxxkg-validation-2
              briefing:
                id: briefing:91n5fvm5qtpf6gxd4bwhxxkg:validation:attempt-2:revision-1
                digest: sha256:53e89c1b9cbe750196e01913dabb9e4d81004f9fb7cf80c7e3e7b70394049dd1
                room-ref: ./review/validation/briefing-2
              withdrawal:
                by: agent:first-officer
                at: "2026-09-10T18:49:46.913016Z"
                reason: Kent explicitly requested the dev-flow kernel minimal-stack and without-it checks before local commit approval. The prior review proves behavior and recut safety, not complete minimal necessity; hold this proposal pending that bounded audit.
review-round:
    id: round:91n5fvm5qtpf6gxd4bwhxxkg:validation:3
    stage: validation
    cycle: 3
    briefing:
        id: briefing:91n5fvm5qtpf6gxd4bwhxxkg:validation:round-3
        digest: sha256:5c4768c7a9d3173fd2e6b1d06a9fa65cdb823af734c354c68e4f55b28c8dfddb
        room-ref: ./review/validation/round-3
---

## The problem

Journey-map currently counts authored story status values. Its executable-symbol
lint checks citations but does not derive development progress. Kent approved a
separate optional skill that reads local Spacedock tasks, maps them to release
stories, and supplies progress to the independently usable drawing skill.

This is a kc-journey-map product deliverable under the existing docs/dev workflow,
not workflow maintenance or a replacement planning provider.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    Kent selected Pilot for this retained local plugin feature. Task access is
    read-only; drawing-only consumers keep working without a migration. There
    is no unattended operation or production commitment.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Keep task reading outside the independently usable drawing core.
      - Keep journey intent authoritative and derived progress out of readback writes.
    implementation:
      - Add one optional progress skill with explicit local refresh and optional drawing.
      - Resolve complete required mappings by journey, release, and story identity.
      - Separate development completion from delivery acceptance using the three existing colors.
    testing:
      - Exercise the actual local task reader and projection seam.
      - Falsify missing mappings, identity collisions, reopened tasks, and vacuous completion.
      - Prove source preservation and all-done pending-delivery-acceptance behavior.
  scope_boundary: >-
    Local read-only task progress and optional drawing integration within
    kc-journey-map. Excludes plan-flow consolidation, provider changes, global
    sprint migration, background operation, consumer migration, and delivery authority.
  semantics_unchanged: false
  promote_when:
    - Existing drawing-only consumers must migrate records or configuration.
    - Production exposure, unattended operation, or long-term support is accepted.
  decision:
    authority: Kent
    at: 2026-09-10T16:06:47.619756Z
```

Kent answered "可以" to the explicit Pilot selection question for this new task.
The standalone Development Brief supplies planning authority; no Planning Receipt
or planning-provider invocation is needed. Use the existing local kc-journey-map
S1 execution group for this continuation of release-story inspection; this legacy
scheduler field is not a journey release mapping or a time-cycle commitment.

## Accepted outcome

Kent can explicitly refresh a journey's release progress from local Spacedock
tasks and draw the result in one operation, while drawing remains independently
usable without Spacedock. Both skills live in kc-journey-map; this does not add a
third top-level planning/development flow.

Task records point to stable journey, release, and story identities. One story
may require multiple tasks. Count a story as development-complete only when its
required task mapping is complete and every required task is done. Calculate
release progress from stories rather than substituting a release-wide task ratio.
A release whose required stories are all development-complete is pending
delivery acceptance, not accepted, released, or proven usable by its target user.

Use the existing three colors. Task-derived green means development-complete,
with provenance that distinguishes it from journey acceptance. Missing or
uncertain mappings must not invent completion or turn existing untracked
functionality into a confirmed gap. Drawing-only use retains its existing
authored status/evidence route. Progress is a derived input, not a second
editable source of truth in the journey file.

## Non-goals

- Merge kc-plan-flow into journey-map or change its admission/backlog gates.
- Migrate the repository-wide sprint vocabulary or rewrite active tasks'
  execution grouping. Use release terminology in the new product interface;
  any narrowly required legacy adapter must be explicit and must not equate
  a time grouping with a user-value release by inference.
- Change planning-provider defaults, integrate or project to Linear, or write
  external issues. This item reads local development state only.
- Add a daemon, background synchronization, generic provider framework, another
  top-level workflow, new standing gates, or new CI lanes.
- Treat task status as journey acceptance, introduce a fourth border state, or
  strengthen source-symbol lint into a separate implementation-proof system.
- Modify the frozen border candidate, its approval record, existing task states,
  user rooms, or valuable journey source files during validation.
- Prove the deferred live host-selection story or redo unrelated border work.
- Commit product changes without exact-file approval; push, create PRs, merge,
  release, or accept delivery without the corresponding authority.
- Bump plugin versions or require existing drawing-only consumers to migrate.

## Acceptance criteria

- **AC-1**: Drawing works without Spacedock installed or configured; an optional
  progress skill in the same plugin can refresh and draw in one invocation.
- **AC-2**: Progress is resolved by journey/release/story identity and all required
  tasks per story. A mixed multi-task example demonstrates that task and story
  completion ratios differ; cross-release or cross-journey collisions do not
  contribute to the selected story.
- **AC-3**: Empty, missing, ambiguous, incomplete, or unreadable task mappings do
  not become complete. Reopening a required task removes the story from the
  completed count on the next refresh; archived done tasks remain discoverable
  through the declared local reader when they belong to the mapping.
- **AC-4**: All required stories complete yields pending delivery acceptance.
  The board's existing three colors and progress labels expose the distinction
  between development completion and journey acceptance without claiming either
  source-symbol presence or a task status proves user usability.
- **AC-5**: Explicit refresh supplies derived progress to rendering without
  changing authoritative journey intent, persisting derived statuses through
  canvas readback, or mutating task states. A before/after source comparison and
  a real local reader-to-board exercise provide evidence.

## Route-back conditions

Return to Kent if the smallest implementation requires consumer migration,
unattended operation, provider writes, a new standing policy, materially broader
files/dependencies, a different completion meaning, or changing the approved
standalone drawing behavior. If task metadata cannot establish complete required
mapping, keep that result unverified and present the missing mapping contract
during shape rather than inventing an accepted scope.

## Delivery and preservation

The existing product home is kc-journey-map. The default dependency base is the
reviewed journey-map work, not an unrelated trunk snapshot. Draft PR #394
(iamcxa/journey-map-skill-merge -> main) is open; current border work is frozen in
/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-board-stories
at HEAD 697525fe1e647dcea67663bc19b5519b70dfa5b3 plus its exact validated 12-file
uncommitted delta. That delta is still awaiting separate local-commit approval.
Do not absorb or alter it. Resolve an isolated dependent candidate at the
implementation boundary after checking live ownership and delivery state.

## Captain direction

Kent approved the preceding two-skill division with "那就按這樣繼續".
This authorizes preparing and continuing this integration task. Kent subsequently selected Pilot for this item. It does not approve the earlier
border commit.
The Planning Receipt is absent: use this standalone Captain-approved brief and
invoke no planning-provider reader or comparator.


## Ideation design

One optional `kc-journey-progress` skill calls a bounded local reader/calculator and optionally supplies its in-memory result to the existing drawing entry. This is one integrated Pilot slice. `semantics_unchanged: false`: it adds opt-in task mapping metadata, an explicit refresh command, and task-derived display provenance; it changes no journey-file format, task status, planning provider, or delivery authority.

### Dependency base and implementation boundary

The measured dependency base is the content tree at `codex/journey-board-stories` HEAD `697525fe1e647dcea67663bc19b5519b70dfa5b3` **plus** the frozen 12-file border delta (+141/-51, 192 changed lines). Its candidate manifest SHA-256 is `60b578fb74c774be3e76bf5a1e11d58fd8b6324ea84de9b28d2a2c53668d7019`; all 21 cumulative file hashes matched during this stage. The 12-file delta is inherited, excluded from this task's table and stop counts, and was not staged or changed.

Live GitHub listing found Draft PR #394, `iamcxa/journey-map-skill-merge -> main`, at `1166747c22f0d6c62db098e5f8cad61bf81174bd`; no newer open journey-progress artifact was listed. A clean committed dependent base **requires separate approval of the exact existing border commit first**, then its owner commits the approved delta. At implementation entry, verify that commit's tree against this manifest, recheck branch ownership/open PRs, and create a fresh isolated worktree from that resulting predecessor commit. Record its SHA as this task's diff base and target the reviewed predecessor branch according to the dependency-aware local delivery policy. Do not base new work on bare `697525fe`, silently absorb the border diff into this task, or commit product work during shape. Shape approval does not itself approve the border commit, later product commit, push, or delivery.

### Smallest explicit mapping contract

Each opted-in task has scalar `journey`, `journey-release`, and `journey-story` values matching the journey's explicit stable identifiers; the legacy `sprint` is ignored. One task belongs to one tuple in this slice. Positional fallback story IDs, duplicate story identities in the selected journey, and missing journey/release identities are not accepted for derived completion; standalone drawing retains its existing permissive route.

Exactly one existing member task is the mapping authority for that tuple. It additionally carries `journey-required-tasks`, a quoted JSON string containing the complete nonempty set of full stored task IDs, and `journey-mapping-complete: true`. For the two-task fixture, the scalar is `'["000000000000000000000001","000000000000000000000002"]'`. The other task carries no copy of that set. There is no new mapping entity/file, mirrored task status, expected-count registry, or second maintained tracker.

The task scope owner confirms the list is exhaustive when the story's development split is agreed, and updates that same declaration when required scope changes, before claiming refreshed completion. This is an explicit scope assertion in the existing task record, not a fact inferred from matching rows, a new standing gate, or an authenticated approval protocol. The reader cannot discover work omitted from both the assertion and task metadata; without that human assertion the result stays `unverified`. Opting into this metadata does not migrate drawing-only consumers. The ideation gate reviews this contract with the slice; no additional product-scope choice is proposed.

The calculator requires one complete declaration, unique nonempty IDs including the declaring task, exact set equality with all tasks carrying the selected tuple, and readable records for every required ID with the same tuple. An extra matching task, a missing required ID, conflicting declarations, malformed JSON, ambiguous identity, false/absent confirmation, unreadable input, or an empty set yields `unverified`, never vacuous completion. A complete mapping with any required task other than literal `done` is development-incomplete; every required task `done` is development-complete. Archived `done` participates. Reopening a required task removes completion on the next explicit refresh.

The release denominator is the stories explicitly assigned to that release in the journey, not a task count. Unknown mappings remain in the denominator and outside the numerator. Zero required stories is not all-done. All nonempty required stories development-complete yields `pending delivery acceptance`; neither task status nor a cited source symbol establishes acceptance, release, deployment, or target-user usability.

### Real-reader and source-preservation observations

All following observations used existing programs, not a new reader implementation. The disposable standalone workflow was created under this entity's `.ideation-reader-probe/` directory and removed before the report write; no live task states or rooms were changed.

- **OBSERVED — local JSON:** `/Users/kent/.local/bin/spacedock status --workflow-dir <fixture> --archived --all-fields --limit 0 --json` returned all five fixture tasks; pagination values were strings, including `has_next: "false"`. With `--limit 2 --page 1/2/3`, the counts were 2/2/1 and `has_next` was `"true"/"true"/"false"`. Reading only page 1 omits the unfinished required task, a concrete false-completion falsifier.
- **OBSERVED — metadata:** `status --read <fixture>/a.md --json` preserved the quoted JSON ID list and scalar `true` as strings. Nested objects and YAML sequences appeared as empty strings in `frontmatter` and were omitted from the all-fields entity rows. The contract therefore uses scalar fields and does not assume nested custom data survives this API.
- **OBSERVED — stable IDs and archives:** the live `kc-journey-map` query returned display prefix `91`, while `status --read <entity-path> --json` returned stored ID `91n5fvm5qtpf6gxd4bwhxxkg`. The live archived query exposed 76 done records. `status --resolve workflow-verification-bootstrap --archived --json` returned `_archive/workflow-verification-bootstrap.md` and full stored ID `te82apnehg989v4enz9e6wf6`; omitting `--archived` failed. `--read` combined with `--archived` failed; resolving first and reading the returned absolute archive path succeeded in the fixture. Reading a missing path failed with exit 1.
- **OBSERVED — identity and reopening:** fixture `demo/R1/alpha` had a=done and b=implementation; `demo/R1/beta` had archived c=done. Two done collision tasks in `other/R1/alpha` and `demo/R2/alpha` were excluded by the three explicit filters. After adding one complete declaration per fixture story, actual rows support the manual expected result **2/3 tasks, 1/2 stories**. Changing only fixture a from done to implementation was visible on the next read; its original bytes were restored. The calculator result itself is DESIGNED, not yet executable proof.
- **OBSERVED — standalone drawing:** with Node's `PATH` empty, existing `buildAllPages(fixtureModel, null, ['story-map','journey-board'])` built three pages without Spacedock lookup. The same entry rejected `['invalid']`, proving the invocation can fail. This is a real in-process drawing observation, not a browser/server delivery claim.
- **OBSERVED — readback falsifier:** adding only `meta.journey.progress` and a separate tagged progress label to the existing rendered records left `diffAgainstModel` clean and `applyDiff` wrote nothing to a disposable source copy (SHA-256 `d4e23feaed0efcedcd9c86c50642604a79a727ad4b439d84f632f6c1cb3d2ec9` before/after). Appending progress to a story's rich text instead produced one authoritative wording edit. This rejects putting derived labels inside editable story text. The in-memory source model also remained unchanged.

### Designed journey and recovery

1. **DESIGNED:** the optional skill invokes `node lib/journey-progress.mjs <journey.yaml> --workflow-dir <dir> [--draw <room>] [--pages ...]`. Without `--draw` it prints the derived snapshot; with it, the same invocation refreshes once and calls the existing room renderer. Default drawing selection remains story-map. No planning receipt, provider call, automatic metadata write, or background refresh is involved.
2. **DESIGNED:** `lib/progress.mjs` executes local `spacedock status --archived --all-fields --limit 0 --json` with argument arrays, bounded timeout/output, and no shell interpolation. It requires `has_next === "false"` and a complete, consistent total; it refuses a truncated/unknown envelope instead of treating the first page as complete. No generic pagination/provider framework is needed. It filters locally so a workflow lacking custom fields becomes unknown rather than failing an unknown-field query.
3. **DESIGNED:** for matching rows and declared IDs, the reader uses `--resolve <slug-or-full-id> --archived --json`, then `--read <resolved-path> --json` without `--archived`. It compares full identities, tuples, declarations, and states, and checks a final selected listing for drift. A detected change, ambiguous resolve, unreadable record, unavailable binary, timeout, or malformed JSON produces a visible unverified diagnostic and no complete claim. This is a bounded observation, not an atomic filesystem snapshot guarantee. Retrying is another explicit refresh.
4. **DESIGNED:** the calculator produces an ephemeral result keyed by journey/release/story with required/done counts, one of the existing `exists/gap/unverified` display values, and provenance (local task source, full IDs, observation time). Missing mappings use violet even if authored evidence says exists; the authored evidence remains visible and is not rewritten. Green means development-complete; red means declared required development remains, not proof that user functionality is absent. The contextual three-color legend explains these meanings. Drawing without progress keeps the existing authored legend and evidence route.
5. **DESIGNED:** `renderToRoom`/`buildAllPages` accept optional derived input and pass it to the two story projections; they do not import the local task reader. `storyBorder` consumes the derived display value separately from authored status, so the existing client border synchronization also preserves it. Release labels count completed stories, and the existing proof/status areas show task provenance and pending delivery acceptance. Story card text, IDs, membership, and authoritative model values remain intact. Function maps and source-authored release contracts remain on their existing routes.
6. **DESIGNED:** derived fields and labels are tagged rendering metadata, ignored by the existing `read.mjs` safe subset. Explicit native wording/order/release edits still round-trip, but progress does not. No new readback writer is planned. If drawing fails after the read, report the failed draw with the computed observation; do not call it drawn. A process crash or abandoned invocation leaves no persisted progress cache or task mutation to recover; an existing room remains a timestamped rendering until another explicit refresh.

### Where it touches

Counts below are actual current lines in the frozen dependency tree and estimated final lines, not inherited estimates. Paths are relative to `kc-journey-map/`; new files currently have zero lines.

| Path | Lines now | Estimated after | Journey purpose |
|---|---:|---:|---|
| `skills/kc-journey-progress/SKILL.md` | 0 | 45 | Explicit refresh/draw usage and the one mapping-contract home |
| `lib/progress.mjs` | 0 | 180 | Read actual local tasks and calculate story/release progress |
| `lib/journey-progress.mjs` | 0 | 40 | Bounded command arguments, snapshot output, optional render call |
| `lib/progress.test.mjs` | 0 | 200 | Real-reader fixtures and projection/readback falsifiers |
| `lib/render.mjs` | 202 | 218 | Optional snapshot input, board proof and release count labels |
| `lib/storymap.mjs` | 258 | 272 | Same snapshot on story map and release labels |
| `lib/records.mjs` | 184 | 224 | Shared derived border selection and contextual three-color legend |
| `skills/kc-journey-map/SKILL.md` | 156 | 160 | Optional skill pointer and separate derived display route |
| `skills/kc-journey-map/references/canvas.md` | 249 | 259 | Snapshot rendering and unchanged readback boundary |
| `skills/kc-journey-map/references/cell-contract.md` | 121 | 128 | Development completion versus authored evidence and acceptance |

Existing `lib/read.mjs` (306 lines), `server/client/App.tsx` (65), journey files, package manifests/lockfiles, and CI need no planned edits; they are consumers exercised by the checks. Estimated net addition is 556 lines across 10 product files. Stop and report before continuing if the incremental diff against the approved predecessor content exceeds **10 changed product files**, **700 added+deleted product lines**, or **260 added+deleted lines in `lib/progress.mjs` plus `lib/journey-progress.mjs`**. Also stop for a new dependency, new CI lane, task writes, a required drawing-only migration, or a new source/readback writer. State reports and the inherited 192 border lines are excluded. No CI trigger changes are proposed; cost per PR was not measured.

### Acceptance checks to implement, not claimed passes

Use the existing Node test runner: `node --test lib/progress.test.mjs`; tests that exercise the real reader declare the installed Spacedock CLI as a local validation prerequisite and do not substitute a fake reader or silently skip it. Existing focused readback tests remain available with `node --test --test-name-pattern='fresh release boards|editing a release story|same wording' lib/read.test.mjs`. Do not rerun a broad suite to replace these falsifiers.

- **AC-1:** empty-PATH drawing still works; a disposable real Spacedock fixture feeds the new refresh-plus-draw invocation into a disposable local canvas. Removing the optional snapshot pass-through must lose the derived release label, while drawing-only still works. Existing standalone observation above proves only the reused in-process seam; the complete CLI/server loop awaits implementation.
- **AC-2:** actual-reader fixture gives 2/3 done tasks but 1/2 complete stories; other-journey/release same-story IDs do not contribute. A mutation that drops either tuple component, counts tasks instead of stories, or trusts display prefixes must fail.
- **AC-3:** empty/absent/unconfirmed/partial/conflicting declarations, extra matching task, duplicate IDs, missing record, unreadable response, truncated pagination, and missing explicit story identity stay unverified. Archived c remains discoverable; reopening a required task reduces the next numerator. An all-done query without a scope declaration must still fail completion; `every([])` or checking only page 1 must fail the tests.
- **AC-4:** all required stories done displays green with explicit local-task provenance and `pending delivery acceptance`, never accepted/released. A no-mapping authored-existing story stays unknown for development counting and does not become a confirmed gap. Draw-only still uses authored evidence, all three border colors, and the original source-symbol lint. Verify both projections and the client synchronization seam through the shared border function.
- **AC-5:** compare journey bytes and all disposable task bytes before/after actual reader-to-room render and real readback; derived fields remain absent from source. Then reword one native card and verify only its wording changes. Putting progress into story text, persisting derived status, or rendering from a mutated source model must fail. A targeted browser observation must confirm readable provenance/legend and no new overlap; no existing user room is a fixture.

### Conditional shape receipts

`reverse_recovery`: trigger=brownfield capability addition; boundary=`kc-journey-map` entry, model, render, records, readback, and installed Spacedock status surfaces. `render.mjs:buildAllPages`, `records.mjs:storyBorder`, and `read.mjs:diffAgainstModel/applyDiff` are WORKING/REQUIRED by the executed standalone and readback observations. Spacedock status/resolve/read is WORKING/REQUIRED by the actual fixture and archived observations. The optional task reader/calculator and snapshot pass-through are MISSING/REQUIRED for the accepted outcome: file inventory and independent content search for `journey-progress|required.tasks|mapping.complete|spacedock status|--all-fields|--archived` found no implementation inside the plugin. Installed plugins outside the pinned source were not treated as this deliverable. Disproof hook: run those searches plus the proposed CLI on this dependency tree; finding an existing reader or working optional input invalidates the missing classification. Decision=use the working seams and build only the bounded missing path.

`project_context`: impact=none; authority=root `PRODUCT.md`, `ARCHITECTURE.md`, `CLAUDE.md`; surface=repository plugin catalog and existing workflow/provider/delivery boundaries; stale_claim=none introduced by this slice; approved_change=none; landed_change=none; planned_check=compare the exact incremental diff and refresh command behavior against those boundaries; validation_evidence=pending. The existing catalog's omission of the already-extracted journey plugin predates this task and is not silently widened into a catalog repair.

Retained-document trigger=true for the new optional skill and bounded existing reference edits: apply Rules 1-4 and 6-8 of the loaded policy. Per-section overlap check keeps mapping/refresh usage in the new skill, canvas display/readback in `canvas.md`, evidence meanings in `cell-contract.md`, and only a pointer in the drawing skill; no copied live task lists or chronological status documentation. Project-context and reverse-recovery references were loaded; multi-slice=false because one integrated route suffices. Delivery-artifact review=true with the dependency base above; portable PR ceremony=false because the local Spacedock mod owns it.

## Stage Report: ideation

- DONE: Resolve the smallest local task-to-story progress contract and its unknown/completion/acceptance semantics, with a falsifiable real-reader observation for AC-1, AC-2, and AC-3.
  AC-1: empty-PATH in-process drawing built three pages; invalid selection refused. The new optional CLI is designed, not implemented; see Real-reader observations and Acceptance checks.
  AC-2: real fixture returned a=done, b=implementation, archived c=done with exact tuple collision exclusion; manual expected task/story ratios are 2/3 and 1/2, conditional on the explicit complete declarations.
  AC-3: actual reader exposed string pagination, scalar-only custom fields, archived resolve/path-read behavior, missing-path refusal, and fixture reopen visibility; missing/unconfirmed mappings are explicitly unverified in the designed contract.
- DONE: Shape the source-preserving renderer integration for AC-4 and AC-5, including standalone use, readback, exact touched-file estimates, dependency base, and proportional stop thresholds.
  AC-4: designed green=development-complete, red=required work remains, violet=unknown; all-done is pending delivery acceptance. The 10-file estimate and 700-line/260-reader-line stops exclude the inherited 12-file delta.
  AC-5: existing readback ignored separate derived metadata/label without source writes; putting progress in story text produced one unwanted wording edit. Full reader-to-canvas and native edit proof remain implementation/validation checks.
- DONE: Commit one durable ideation report with explicit AC-1 through AC-5 evidence citations and observed/designed boundaries; preserve product candidates and all existing task and room state.
  This entity is the sole retained stage artifact; disposable fixtures removed; all 21 candidate manifest hashes and its HEAD matched. State commit is scoped to this entity; no product commit, task transition, or room mutation was performed.
- SKIPPED: Product implementation and delivery.
  This stage authorizes shape only. A clean dependent build base first needs separate approval and owner commit of the frozen border delta; the optional feature then needs its normal implementation authority.

### Summary

A complete task mapping needs one explicit scope assertion in an existing task, not a count of whatever metadata happens to be present. The local CLI can carry that scalar contract, and the existing drawing/readback seam can display a derived snapshot while preserving journey intent. One bounded implementation route is ready for ideation review; task-derived usability or delivery acceptance is not claimed.


## Stage Report: implementation

- DONE: Implement the approved optional progress skill and real local task reader/calculator with complete mapping, full identity, archived/reopened-task handling, and honest development progress for AC-1, AC-2, and AC-3.
  AC-1: `implementation-evidence/final-scoped-tests.txt` exercises empty-PATH drawing, invalid-argument refusal and real CLI-to-canvas drawing; `without-snapshot.txt` fails when the renderer stops consuming the snapshot.
  AC-2: the real fixture yields 2/3 done tasks but 1/2 complete stories with archived task readback and full stored IDs; dropping journey/release identity or using task totals fails the named mutations in `implementation-evidence/mutations.json`.
  AC-3: actual missing/partial/conflicting/duplicate/short-ID/malformed record cases stay unverified, actual truncated pagination refuses, and reopening removes completion; empty scope and all-done-without-declaration cannot complete (`final-scoped-tests.txt`).
- DONE: Integrate the derived snapshot into both story projections without coupling drawing to Spacedock or leaking progress through readback; prove the real CLI/canvas seam and three-color pending-acceptance behavior for AC-4 and AC-5.
  AC-4: `mixed-storymap.png` shows red/green/violet with task provenance; `all-done-board.png` and `all-done-cli.json` show 2/2 stories development-complete, pending delivery acceptance. Removing shared derived-border selection fails `without-derived-border.txt`; authored executable-symbol lint remains green (`authored-lint-tests.txt`).
  AC-5: `native-edit-proof.json` and `native-save-as.txt` bind real native wording edit to the sole expected YAML text change; no progress fields persist. CLI fixture source/task bytes remain unchanged, and injecting progress into wording fails `wording-leak.txt`.
- DONE: Record the exact uncommitted candidate, proportional green/red evidence, measured scope and minimal necessity in a durable report; preserve the approved base, task states, source journeys, user rooms and services.
  `implementation-evidence/candidate-manifest.json` SHA-256 f0261937f5c5a92455add6e86215c1a7d2444dec1b6fcd6e3e70bbe537128e99 binds 10 product files / 460 changed lines / 125 reader+CLI lines against bc51b2464659594d3c06806442c77ec15319962b (limits 10 / 700 / 260). Product staging is empty; no product commit was made.
  Six producer mutations failed; restored candidate passed five progress checks, three focused existing readback checks, three authored lint checks and diff whitespace validation. `implementation-evidence/README.md` maps each retained file and comment decision to its necessity and lists the exact commands.
  Project-context receipt: impact=none; authority=PRODUCT.md/ARCHITECTURE.md/CLAUDE.md; surface=plugin and workflow/provider/delivery boundaries; stale_claim/approved_change/landed_change=none; implementation evidence=exact diff plus exercised read-only/standalone route; independent validation still owns fresh validation_evidence. Existing catalog omission not widened.
  Optional implementation observation: UNAVAILABLE(reason: unsupported); pinned exact-input protocol cannot bind this uncommitted candidate to a Git tip object. RoboRev v0.62.0 capability help read, request/confirmation counts 0/0; no provider job, no convenience commit. Details and configuration hash are in `implementation-evidence/README.md`.
  Preserved original listeners 3737/3741/5858 and their existing room list; isolated preview only on 3743/5863. Existing App.tsx, read.mjs, manifests/lockfiles and valuable journey files remain unchanged. Dependency symlink and preview cleanup condition are explicitly recorded.

### Summary

The optional skill now derives development progress through the real local task CLI and renders it through the existing canvas/readback seams. Preview links, partial/all-done PNGs, exact manifest, necessity observations and limits are retained in `implementation-evidence/README.md`; fixtures do not represent real-project delivery. The 10-file candidate is frozen uncommitted for independent validation, with no product delivery or acceptance action authorized.

## Stage Report: validation

- DONE: Bind the exact frozen candidate and independently assess AC-1, AC-2, and AC-3 against the approved mapping/progress contract and actual producer red/green evidence; attack any material unowned claim without duplicating owned passing checks.
  Entry/exit matched all ten files, empty product index, branch `codex/journey-progress`, HEAD/base `bc51b2464659594d3c06806442c77ec15319962b`, manifest SHA-256 `f0261937f5c5a92455add6e86215c1a7d2444dec1b6fcd6e3e70bbe537128e99`; see `validation-evidence/exit-binding.json`.
  AC-1: producer actual CLI pass and `without-snapshot.txt` fail prove the existing room seam; empty-PATH standalone pass/refusal was inspected. Independent real CLI refreshed/drew a new room, successful HTTP 200 while unknown R2 correctly returned exit 1 (`validation-evidence/refresh.json`).
  AC-2: inspected real-CLI 2/3 task versus 1/2 story evidence and both tuple mutations plus task-ratio mutation, each exit 1 for the expected mismatch; full stored-ID reads and exact membership comparison agree with approved contract.
  AC-3: inspected real missing/partial/conflicting/duplicate/malformed/short-ID/archive/reopen and pagination refusals. Independently reopened only copied b: saved snapshot remained green before explicit refresh, then changed to gap/red and 1/2 stories; `snapshot-before-refresh.json` / `snapshot-after-refresh.json` falsify stale auto-sync assumptions.
- DONE: Inspect partial/all-done story projections and independently exercise the new derived display/native-edit/readback seam for AC-4 and AC-5 while preserving source, task state, rooms, services, and candidate hashes.
  AC-4: inspected preserved PNGs and actual partial/all-done pages at readable zoom; `mixed-live.png` / `all-done-live.png` show three meanings, local source/time, and 2/2 pending delivery acceptance. Producer derived-border mutation fails; source-symbol lint remains an independent authored route.
  AC-5: new room only: programmatic edit entry plus native keyboard typing, Escape, real CLI readback and browser reload preserved authored exists/derived gap/red border. `native-readback-proof.json` proves the sole YAML change is the intended wording; source/tasks unchanged. Producer wording-leak mutation demonstrates a failing instrument.
  Original room DB bytes gained browser user records only; existing shape clocks remained at producer values, not source/story edits. Candidate services remained live without restart; named browser closed. See evidence README for honest pointer/keyboard attempts, recovery, and cleanup condition.
- DONE: Record a durable validation verdict with explicit per-criterion evidence, measured scope, remaining limits, and preview links; leave product commits and delivery to Captain authority.
  PASS for the authorized local Pilot slice; no blocking product findings. Scope independently measured 10 files / 460 changed lines / 125 reader+CLI lines against 10 / 700 / 260 stops. All retained surfaces have a purpose and inspected without-it evidence; documentation overlap and actual claimed seams were independently checked.
  Project-context receipt: impact=none; authority=PRODUCT.md/ARCHITECTURE.md/CLAUDE.md; surface=plugin/workflow/provider/delivery boundaries; stale_claim/approved_change/landed_change=none introduced; validation_evidence=`validation-evidence/README.md` exact diff and executed refresh/native preservation. No unrelated catalog repair.
  Pinned 4.1.1 validation loader accepted its stage pin; optional observation UNAVAILABLE is non-gating. No Planning Receipt/provider operation, new dependency, CI or product commit. CI cost per PR unmeasured; unchanged. PR #394 remains an open precursor; no progress PR exists.
  Human previews: [partial map](http://127.0.0.1:3743/?room=progress-mixed&d=v-287.-371.2015.1511.page), [all-done R1](http://127.0.0.1:3743/?room=progress-all-done&d=v-568.-617.2576.1932.jm-board-R1), [native edit](http://127.0.0.1:3743/?room=progress-validation-native&d=v-568.-617.2576.1932.jm-board-R1). These corrected camera URLs replace 800% placeholder views without product edits.

### Summary

Independent local validation passes the frozen candidate; the fresh material challenge covered timestamped versus refreshed task state and native edit/reload/source safety, with producer red/green evidence inspected rather than duplicated. This proves the bounded fixture journey, not wholly omitted task scope, atomic observation, hosted delivery or actual-user acceptance; product commit and subsequent delivery remain Captain-owned, and preview cleanup follows review.

## Stage Report: validation (cycle 2)

- DONE: Commit exactly the Captain-approved ten-file journey-progress candidate after matching the validated manifest; change no source and do not repeat passing validation.
  Local commit receipt: `947501df45dea7d139ff030eed4549701170fcab`, subject `feat(kc-journey-map): derive release progress from local tasks`, parent `bc51b2464659594d3c06806442c77ec15319962b`, tree `8b20fa206a9203c84ea0ddcdc3c058b262a2c0ae`, branch `codex/journey-progress`.
  Manifest SHA-256 `f0261937f5c5a92455add6e86215c1a7d2444dec1b6fcd6e3e70bbe537128e99` and every bound file hash matched before staging and again in committed blobs. The commit changed exactly the ten approved paths (+433/-27); `git diff --check` and staged whitespace checks passed. No source or version edit and no repeated test suite.
  Exact file set: `kc-journey-map/lib/journey-progress.mjs`; `kc-journey-map/lib/progress.mjs`; `kc-journey-map/lib/progress.test.mjs`; `kc-journey-map/lib/records.mjs`; `kc-journey-map/lib/render.mjs`; `kc-journey-map/lib/storymap.mjs`; `kc-journey-map/skills/kc-journey-map/SKILL.md`; `kc-journey-map/skills/kc-journey-map/references/canvas.md`; `kc-journey-map/skills/kc-journey-map/references/cell-contract.md`; `kc-journey-map/skills/kc-journey-progress/SKILL.md`.
- DONE: Record the local commit, verified tree and empty product index in the existing entity; preserve approved validation and pending delivery authority, previews, and unrelated work.
  Post-commit index and tracked working tree are empty; the sole untracked path is the pre-existing `kc-journey-map/node_modules` setup symlink. No `.context` artifact or symlink entered the product commit; no preview/service/room operation occurred in this continuation.
  AC-1, AC-2, AC-3, AC-4, and AC-5 retain the preceding independent validation verdict and its exact-byte evidence; the commit/tree checks bind that same validated content to the new Git object rather than claiming a new validation run.
  Authority: Kent's recorded approval of briefing `b88365b91c640c1549daede74139a46ba7ab6651b53f7c56829d9306cda4dea1` grants this local commit only. Pinned kc-dev-flow 4.1.1 accepted `local-commit-stage-pin.json`, attempt `spacedock-ensign-91n5fvm5qt-local-commit`. Task frontmatter, gate records, prior pins and reports remain intact; terminal application stays pending.

### Summary

The approved ten-file candidate is now a verified local commit without changing its validated bytes. Product push, PR creation, merge, release, delivery acceptance, terminal consumption and preview cleanup remain outside this continuation; existing previews stay available for the next Captain decision.


## Stage Report: implementation (cycle 2)

- DONE: Prepare five isolated cumulative layer candidates following the Captain-approved three-way split plus existing borders and progress; preserve original branches and exact final semantics.
  Kent's "確認這樣拆" authorizes this bounded delivery recut; `stack-recut-evidence/README.md` explains the grouping, preservation, and separate remaining local-commit/PR gates without rewriting earlier approvals.
  Layer 1 preserves the legacy team-ops drawing surface until layer 2 replaces it; early runtime, docs, examples, render/read/tests and CI contain only their available capabilities.
- DONE: Run meaningful per-layer validation, prove final cumulative tree equivalence to the merge of current main with the approved product, and report exact files, sizes, trees, and limits.
  `stack-recut-evidence/manifest.json` binds layer sizes 24/+6023/-0, 24/+1075/-334, 34/+1966/-139, 21/+625/-376, 10/+433/-27; generated shares and every path are recorded there.
  `equivalence.json` and `patch-proof.json` prove zero differences for the three expected merge trees and replay all five patches; layer 5 is `cefe085d5d9b12b5679421b5607c808d6989a1b7` on pinned main `c9c5752f`.
  Native canvas: clean dependency install, isolated marketplace install with resolved skill path, malformed-record refusal, live editor/UI change, restart/reopen, native export/import and PNG export passed; losing persistence or the skill path falsifies these checks.
  Story planning: 17 tests plus live wording/order/release/save-as and duplicate-identity refusal passed; accepting a straddled card, trusting a duplicate or changing source bytes falsifies these checks.
  Full layers 3/4/5: 44/67/72 tests and isolated five-page boot/render/readback passed; dropped records or fresh-room drift falsifies the smoke. Version parity passed for all layers; dependency manifests and locks are byte-identical.
  AC-1: layer 5's empty-PATH drawing and real refresh-CLI-to-canvas checks passed; a mandatory task-reader dependency in drawing would fail them.
  AC-2: real task fixtures retain full identity and produce 2/3 done tasks versus 1/2 done stories; dropping identity scope or counting tasks as stories fails the assertions.
  AC-3: actual missing/partial/duplicate/malformed/short-ID mappings and truncated pages refuse completion; archived tasks read and reopening removes completion.
  AC-4: all-done real fixtures yield pending delivery acceptance with the existing three borders; equating done with acceptance or losing provenance fails the checks.
  AC-5: actual refresh/readback preserves source and task bytes, and native-compatible wording edits change only expected intent; persisting derived status fails the assertions.
- DONE: Retain a concise implementation report and concrete local commit review packet; no product commits, pushes, PR creation, or destructive rewriting.
  `stack-recut-evidence/README.md` is the review packet; raw patches/logs/browser files remain in task `.context/journey-stack-recut`. Five patch replays and snapshot/index comparisons passed; parent code worktree remains clean.
  GitHub Actions cost per PR is unmeasured. The optional RoboRev observation is UNAVAILABLE(reason: unsupported), requests/confirmations 0/0: no committed recut product tip exists, so no ambient old HEAD was reviewed.
  Limits: inherited layer-3 EOF whitespace remains to preserve exact source; temporary proxy blocked toolbar CDN assets, so browser proof covers native records/editing/portability, not complete icon appearance. Fresh independent intermediate-layer review remains required.
  Project-context receipt: impact=none; authority=PRODUCT.md/ARCHITECTURE.md/CLAUDE.md; existing accepted product/provider/delivery boundaries unchanged. This recut changes delivery grouping only; no new project-context claim was authored.

### Summary

Five exact cumulative candidates and replayable patches are ready for independent validation and a concrete local-commit decision. The original 10-file/460-line progress feature and all three approved product endpoints are preserved; no product delivery or task terminalization occurred.

## Stage Report: validation (cycle 3)

- FAILED: Verify that each intermediate layer is independently usable, accurately documented, and free of missing or hidden later-layer dependencies; attack a concrete isolation or safety claim not settled by the producer checks.
  Layer 2 real API edit plus `journey-read --out` silently writes the first same-wording story instead of the edited second ID, exit 0; distinct-wording control passes and both source hashes stay unchanged. `stack-recut-independent-validation/initial/same-wording-proof.json` is the decisive refusal falsifier (expected safe identity handling, observed no refusal/wrong target).
  Cause: layer-2 `lib/read.mjs:176` selects by old text; layer 3 retains it, layer 4 already selects by ID. Layer 1 legacy registration/skill/template and available installed commands are intact; layer 2 source imports show no hidden later board/function/evidence/selection/progress implementation.
- DONE: Audit the exact five candidate tree/file manifests, relevant producer check evidence and final equality proof without redundantly rerunning owned green deterministic checks.
  Reviewed `stack-recut-evidence/{manifest,validation-summary,equivalence,patch-proof}.json`, producer browser readback log and layer-5 test/smoke output; snapshot working files match their own indexes (`snapshot-audit.json`). No full suite or deterministic equality replay was repeated.
  Exact trees: layer 1 `feec1a91f7479f9f1ff15b8a0bf8650d86271421`; layer 2 `9c3eb9fd9ace855df2654f3f122ed8d270cf6a3b`; layer 3 `55b4416f5b37649fc0fec4d7eeddcef3561bad9c`; layer 4 `6b4d5e8a747d9d13a4c8d2a832e0b9395b04beff`; layer 5 `cefe085d5d9b12b5679421b5607c808d6989a1b7`.
  AC-1: retained empty-PATH and actual refresh/draw evidence plus source-isolated early drawing route; adding a mandatory task reader breaks standalone drawing.
  AC-2: retained full-identity and task-versus-story ratio checks; scope dropping or task-count substitution fails their assertions.
  AC-3: retained missing/ambiguous/partial/unreadable mapping, archive/reopen and pagination checks; empty/all-done without complete mapping cannot count complete.
  AC-4: retained all-done pending-acceptance and three-border/provenance checks; treating development completion as acceptance fails them.
  AC-5: retained final source/task-byte and derived readback checks remain bound to layer 5; this independent predecessor failure disproves safe story-intent readback for layer 2 and the same source defect persists in layer 3.
- DONE: Append an independent validation report with scoped findings or PASS, original AC coverage and delivery-only limits; preserve candidate bytes, original branches, rooms, and old approvals.
  `stack-recut-independent-validation/initial/README.md` retains diagnosis, repro/control, limits and ownership; no product edits/commits, task status/gates, provider writes, existing-room writes or listener termination. The sole owned API process stopped.
  No new exact-candidate PR exists; old #394 is preserved history, not clean feedback for the recut. CI cost is unmeasured; dependency reuse and blocked external-icon appearance remain limits. Layer-3 inherited EOF whitespace is nonblocking formatting and unchanged.
  Neutral round publication is not recorded: no entity Briefing/log exists and exposed installed review tooling supplies presentation, not a noninteractive two-file room producer; the First Officer received the capability gap.
  First Officer assigned one producer correction: promote only existing ID-selection safety hunk into layers 2/3, remove it from layer 4 delta, qualify layer-3 equality and retain exact layer-4/5 endpoints; independent focused re-review remains pending.

### Summary

FAIL for independently safe intermediate delivery: same-wording stories can be written to the wrong stable ID in layers 2/3. Final progress semantics and original AC evidence are not regressed by this finding; producer correction and one focused independent re-review are required before exact local-commit approval.


## Stage Report: implementation (cycle 3)

- DONE: Promote the existing stable-ID writeback safety hunk to layers2/3, preserving rejected evidence and final layer4/5 exact trees.
  The sole independent finding is addressed by promoting the existing layer-4 +5/-1 `read.mjs` block: select the stable story ID and refuse stale source wording. No new final code/tests, feature, dependency, or scope was added.
  Initial snapshots survive as code-worktree `.context/rejected-layer-2` and `rejected-layer-3`; raw/state `initial-rejected/` packets and the reviewer's initial evidence remain unchanged.
  Corrected layer 2 is `9702db9d0b908b03d44e92dcc87ec20a16a61731`; layer 3 is `1738d173046d750819cd40e8ee838dd3eace114e`. `stack-recut-evidence/equivalence.json` proves each differs only by that existing hunk; layer-3 original extraction equality is qualified by the precise promoted patch.
  Final layer 4 remains `6b4d5e8a747d9d13a4c8d2a832e0b9395b04beff`; layer 5 remains `cefe085d5d9b12b5679421b5607c808d6989a1b7`, both equal the original expected current-main merge trees. Layer 1 also remains unchanged.
- DONE: Prove the same-wording second-story edit targets the correct ID in both affected layers, and refresh exact candidate manifests/patches/size counts.
  The same real API PATCH -> journey-read CLI --out instrument failed same-wording cases in both original layers and passed distinct-wording controls. Both cases now pass at both corrected trees with CLI exit 0, correct second-ID updates and unchanged source hashes; reverting to text selection restores the recorded red result.
  Stale source wording is refused in both corrected layers, with zero applied writes and unchanged bytes. A temporary probe covers this existing safety block without adding final product tests.
  Affected read tests passed 10/10 and 16/16; layer-2 one-page and layer-3 five-page boot/render/readback passed. Unchanged install/persistence/export and full layer-4/5 suites were not rerun.
  Updated adjacent counts: 24/+6023/-0, 24/+1079/-334, 34/+1966/-139, 21/+620/-375, 10/+433/-27. `manifest.json` includes every path/generated share/hash; `patch-proof.json` replays all five corrected patches to their exact trees and confirms snapshot/index agreement.
- DONE: Record closure evidence and a concrete updated local-commit packet in durable state; no product commits or provider effects.
  Immutable closure: `stack-recut-evidence/correction/README.md`, SHA-256 `eb8601c22d0d6d84e099af605a6ec60613f9ee31289440f7a22344fd9081a8b0`, binds the exact patch and red/green/control results through `closure-proof.json`. Focused independent re-review remains pending.
  `stack-recut-evidence/local-commit-review.md` replaces the stale proposal with current trees, hashes, paths and sizes, explicitly pending re-review and Kent's local-commit approval. No product commit/push/PR, task status/gate/approval write, provider request, or existing-service mutation occurred.
  AC-1: unchanged standalone drawing and optional real refresh path retain prior exact final-tree evidence; introducing mandatory Spacedock in drawing would fail the empty-PATH check.
  AC-2: unchanged final full-identity/task-versus-story evidence remains valid; the promoted early write path now also respects the requested stable story ID.
  AC-3: unchanged final missing/partial/duplicate/unreadable/archived/reopened mapping checks retain their evidence; early source-staleness refusal passed independently.
  AC-4: unchanged final three-color/provenance and pending-delivery-acceptance evidence remains bound to the unchanged layer-5 tree.
  AC-5: the failed intermediate same-wording writeback now preserves story identity and source bytes in both layers; final derived-progress readback/source/task preservation remains unchanged.
  CI cost remains unmeasured. RoboRev observation remains UNAVAILABLE(reason: unsupported), requests/confirmations 0/0, because this recut still has no authorized committed product tip. Existing inherited whitespace and external-icon proof limits remain unchanged.

### Summary

The single intermediate-layer safety finding has producer closure evidence from the same falsifiable runtime scenario and its passing control. Corrected exact candidates and the updated local-commit proposal are ready for the one focused independent re-review; final product endpoints and earlier approvals remain unchanged.

## Stage Report: validation (cycle 4)

- DONE: Verify that each intermediate layer is independently usable, accurately documented, and free of missing or hidden later-layer dependencies; attack a concrete isolation or safety claim not settled by the producer checks.
  PASS: the original real API PATCH -> `journey-read --out` falsifier now updates only second ID `a-2` for same-wording stories in corrected layers 2/3; distinct-wording controls also pass, all four CLI exits are zero, source hashes stay unchanged, and full output-model comparison shows only the intended wording change. Evidence: `stack-recut-independent-validation/rereview/layer-{2,3}/same-wording-proof.json` and `full-model-proof.json`.
  The original negative/control evidence remains under `stack-recut-independent-validation/initial`; replacing ID selection with old-text search recreates that observed failure. Earlier verified layer-1 legacy/available-command preservation and layer-2 module isolation remain unchanged by this sole +5/-1 existing block.
- DONE: Audit the exact five candidate tree/file manifests, relevant producer check evidence and final equality proof without redundantly rerunning owned green deterministic checks.
  Reviewed updated `stack-recut-evidence/{manifest,equivalence,patch-proof}.json`, `local-commit-review.md`, frozen correction README/closure proof and promoted patch. `rereview/binding.json` matches both corrected read-file hashes and frozen README SHA-256 `eb8601c22d0d6d84e099af605a6ec60613f9ee31289440f7a22344fd9081a8b0`; both snapshots have no unstaged tracked changes.
  Exact trees: layer 1 `feec1a91f7479f9f1ff15b8a0bf8650d86271421`; layer 2 `9702db9d0b908b03d44e92dcc87ec20a16a61731`; layer 3 `1738d173046d750819cd40e8ee838dd3eace114e`; layer 4 `6b4d5e8a747d9d13a4c8d2a832e0b9395b04beff`; layer 5 `cefe085d5d9b12b5679421b5607c808d6989a1b7`.
  The promoted stable-ID selector/stale-wording refusal is the only layer-2/3 correction; layer-3 original-tree equality is qualified by that exact patch. Final layers 4/5 retain exact original merge equality. No unaffected full suite, install, layout run or equality replay was repeated.
  AC-1: unchanged final standalone drawing/optional refresh proof remains bound; a mandatory reader would fail the retained empty-PATH observation.
  AC-2: unchanged full journey/release/story identity and differing task/story ratio proof remains bound; early writer now also respects the requested story ID.
  AC-3: retained missing/partial/ambiguous/unreadable/archive/reopen/pagination checks remain valid; producer stale-wording guard evidence covers the promoted refusal branch.
  AC-4: unchanged final three-color/provenance and pending-delivery-acceptance proof remains bound; development completion still does not assert acceptance.
  AC-5: independent corrected intermediate readback preserves source bytes and all model fields except the requested wording; final derived-progress and task/source preservation evidence remains bound to unchanged layer 5.
- DONE: Append an independent validation report with scoped findings or PASS, original AC coverage and delivery-only limits; preserve candidate bytes, original branches, rooms, and old approvals.
  `stack-recut-independent-validation/rereview/README.md` records PASS and reproduction. Both owned ephemeral API servers stopped; no product source/commit/provider/room/status/gate changes, and original FAIL plus FO-recorded validation/1 correction round remain intact.
  No unresolved finding remains in this focused scope. CI cost is unmeasured; shared-install and blocked external-icon appearance limits remain, and inherited layer-3 EOF whitespace is unchanged. Exact local-commit approval and all later delivery authorities remain outstanding.

### Summary

PASS for the corrected five-layer local delivery proposal: the sole reported intermediate writeback safety failure is fixed and independently exercised on both affected trees. The exact candidate packet can proceed to Kent's local-commit review; no commit, PR, merge or delivery acceptance is granted by this validation.

## Stage Report: validation (cycle 5)

- FAILED: Apply the pinned dev-flow kernel Minimal necessity and verification discipline to the exact final candidate, mapping every retained changed surface to an accepted goal, named falsifier, safety boundary or required lifecycle obligation.
  Exact final tree `cefe085d5d9b12b5679421b5607c808d6989a1b7`; [60/60-path mapping](minimal-necessity-evidence/surface-map.md) finds unused frame helper, removable CORS/compiler dependencies and stale documentation. Goal sufficiency does not imply minimal necessity.
- DONE: Run task-owned without-it observations with explicit removed mechanisms, actual failure/control results and falsifier kinds; separately evaluate PR layers and material smaller equivalent dependency/design alternatives.
  [Observed removals/controls](minimal-necessity-evidence/README.md): no-disk loses hand note after restart, no-reconciliation retains deleted story, no-bands loses unassigned story, no-borders loses colors, prose-only evidence falsely passes; each intended failure has preserved original control.
- DONE: Report concrete keep/merge/remove findings, comment/document retention and deletion candidates with evidence and limits in durable state; preserve all frozen product candidates and do not claim minimality from green tests or smaller LOC alone.
  [Document/comment dispositions](minimal-necessity-evidence/documents-comments.md) retain unique contracts with two-search second-home accounting; no whole-document deletion. All frozen candidates/history preserved; local-commit packet remains held.

### Summary

Minimal necessity is **FAIL / needs reduction**. Remove unused frame, CORS registration/dependency and unused compiler; the coherent smaller browser/CLI path also works without React Fast Refresh plugin, but preserve the plugin in the recommended repair to avoid that developer tooling loss. The six removed lock nodes describe the tested three-dependency alternative, not the recommended two-dependency reduction. Keep existing schema-error boundary: lean prototype proves invalid-batch 400 and atomic rejection, not correct unexpected-server-error classification.

Recommend three review units (complete editable planning, optional evidence/detail with status borders, explicit local-task progress), using current cumulative trees 2/4/5 as grouping inputs; four remains defensible if separate infrastructure ownership is required. This is a defined reviewability/temporary-adaptation tradeoff, not mathematical minimality; no revised product candidate exists yet.

AC-1..AC-5 retain prior behavior evidence and six producer mutations bound by exact final blob SHA-256 values; this audit separately covers predecessor canvas/story/evidence mechanisms. Same-wording ID/text corruption evidence and distinct-wording control remain frozen in initial/rereview records. No product commits, PR/provider actions, task acceptance or source deletion occurred; CI cost per PR is unmeasured. First Officer owns bounded reduction/topology disposition and producer routing.

## Stage Report: implementation (cycle 4)

- DONE: Implement only the Captain-approved unused-code/dependency and bounded documentation reductions while preserving Fast Refresh, schema diagnostics, source safety and independent drawing.
  Three new snapshots preserve former trees 2/4/5. Removed unused frame, direct CORS/compiler dependencies and registration; actual lock reduction is five nodes, no additions/upgrades. Retained React Vite plugin and existing schema diagnostics. Scoped prose and illustrative example updates preserve unique contracts; original dated source is retained. [Immutable closure and code identity](three-unit-reduction-evidence/README.md).
- DONE: Prepare three cumulative independently usable delivery units with exact changed-file/tree manifests and an uncommitted local-commit review packet.
  Final trees and exact adjacent stats/paths/patches are in [trees.json](three-unit-reduction-evidence/trees.json) and the [held local-commit packet](three-unit-reduction-evidence/local-commit-review.md). Exact patch replay succeeds; scratch dependency links are not product paths. Old five snapshots/evidence remain frozen; no product commits or branch changes.
- DONE: Run proportional real checks on the actual two-dependency package and changed behavior, bind retained without-it evidence, and durably report results, limits and preservation.
  Fresh private npm ci passed. Actual suites: unit 1 17/17; unit 2 67/67; unit 3 affected progress/example 9/9. All three version-parity checks pass. Distinct-origin browser WebSocket/Node REST, native edit/reload and server restart persistence, reconciliation, atomic malformed-batch 400, five-page native export/import/no-drift readback and PNG export pass. Independent artifact assertions retain unverified host status and corrected authored-order limits. 17 projection equivalence comparisons pass; removed frame absent. Existing negative/control necessity observations and six progress mutations carry forward only with source-identity binding.
  AC-1: standalone drawing and optional progress preserved; AC-2: unchanged explicit journey/release/story mapping and ratio distinction; AC-3: existing refusal/ambiguity/archive/reopen/pagination behavior unchanged; AC-4: standard borders/provenance and pending delivery acceptance retained; AC-5: real same-wording/second-ID and distinct-wording controls preserve original source bytes. Supporting outputs and binding limitations are in the immutable closure. No provider read or planning receipt; no task/gate/PR mutations. Optional implementation-exit RoboRev UNAVAILABLE on uncommitted trees, zero requests. CI cost per PR unmeasured. Owned services stopped.

### Summary

The Captain-approved three-unit reduction is implemented and producer-verified, with exact candidate/file manifests and retained historical/negative/control proof. The packet remains held for focused independent validation and later exact local-commit approval; no delivery authority is implied.

## Stage Report: validation (cycle 6)

- FAILED: Independently verify the exact approved two-dependency, unused-code and bounded document reductions close prior minimal-necessity findings while preserving required behavior and safety.
  Behavior and approved reductions pass; one retained schema comment falsely says malformed records would be accepted by storage. Prior no-prevalidation probe returns native rejection/500; preserved boundary supplies atomic detailed 400. [Exact finding and smallest comment-only correction](three-unit-independent-validation/finding.json).
- DONE: Verify the three cumulative delivery units and exact-file/tree packet, using focused falsifiable checks and accurately bound reused evidence rather than repeated broad verification.
  Trees `063df758d06b2b2170a3378cdff01c4195fbc2b0`, `a117b410f9b7dde03ee081f5545b4d9755d77e7b`, `b52f204f4c6a2b6ec09f2657adcca272e97dc1a0` match independent file/numstat/hash/patch replay. Actual two dependencies/five nodes removed; Fast Refresh/schema diagnostics retained. Projection comparison detects missing borders; doctor check rejects old false fallback; native example check rejects a green host border before accepting violet.
- DONE: Durably report verdict, AC coverage, changed-surface necessity, evidence limits and preservation; leave product commits and delivery authority pending.
  [Independent report](three-unit-independent-validation/README.md) binds AC-1..AC-5 and reused core/progress negative controls, independently disposes document blocks and supports three workflow units. Mutable commit subjects use `kc-journey-map`; packet remains held for the single documentation correction. No source/self-repair, product commit, service/room mutation or provider action.

### Summary

Behavior, exact candidate integrations, approved code/dependency reductions and three-unit reviewability pass at Pilot depth; documentation completion is held by one false retained schema rationale, not a runtime defect. First Officer should route only the stated comment correction while preserving all diagnostics, then bind the refreshed candidate; no broad rerun or new design loop is justified. Producer fresh install/browser/runtime evidence was reviewed, not independently repeated; CI cost per PR remains unmeasured and delivery acceptance pending.

## Stage Report: implementation (cycle 5)

- DONE: Apply only the exact reviewer-prescribed schema rationale comment to the three new cumulative candidates, preserving every executable byte and all other blobs.
  Replaced the three-line false rationale with the exact one-line PATCH/HTTP 400 diagnostic comment. [Immutable closure](schema-comment-correction-evidence/README.md) and [exact byte/tree proof](schema-comment-correction-evidence/comment-only-proof.json) show only this comment differs in each new candidate; all other blobs/modes and executable bytes are identical.
- DONE: Bind the exact comment-only old/new trees and refresh the concrete uncommitted local-commit packet without rerunning unchanged behavior or overwriting prior evidence.
  [Final trees and counts](schema-comment-correction-evidence/trees.json), exact file lists/patches and [held local-commit packet](schema-comment-correction-evidence/local-commit-review.md) use `feat(kc-journey-map):` subjects. Unit 1 loses only two comment lines; units 2/3 adjacent patches are unchanged. [Independent cycle 6 evidence](three-unit-independent-validation/README.md) and [prior AC-1..AC-5 producer evidence](three-unit-reduction-evidence/README.md) are retained through the exact comment-only binding; prior reviewer verdict is not overwritten. No fresh runtime/test/install/reviewer run or product commit occurred. Pilot, absent Planning Receipt, source/services preservation and delivery limits remain unchanged.

### Summary

The sole prescribed comment correction is complete and bound to three corrected cumulative trees. The packet is held for the Captain decision through First Officer orchestration; this closure adds no independent runtime verdict or delivery authority.

## Stage Report: implementation (cycle 6)

- DONE: Create exactly the three Captain-approved local commits with exact tree/parent/file/subject equality while preserving existing worktrees and unrelated changes.
  Approval provenance: Kent answered **批准** to accepting the round-3 exact schema comment correction and approving the local-commit packet. Created `codex/journey-planning` at `0d69be164ccdcd1b3509f3577d6bd03a468f8f36`, `codex/journey-release-inspection` at `818260a8c14b504dae8d3989ba9c710226255b74`, and `codex/journey-local-progress` at `aabb8e7e8320b65fa852feae961df2e438d8f002`, each with the approved single parent/tree/subject/path set. [Exact commit evidence](local-stack-commit-evidence/commits.json) and [preservation/limits](local-stack-commit-evidence/README.md). Ordinary commits, no hook bypass, no new code edits or tests. Root and all pre-existing worktree tuples unchanged; three owned isolated commit worktrees added. Retained version parity and AC-1..AC-5 source/runtime evidence carry through exact approved tree equality.
- DONE: Prepare full three-unit Draft PR bindings and exact body files with pinned pair preflight, then durably report completed local commits and pending delivery authority.
  [Complete unpublished stack draft](local-stack-commit-evidence/draft-stack-review.md) and [canonical delivery tuples](local-stack-commit-evidence/draft-units.json) bind actual mode-0600 body files, hashes, full candidate/base SHAs, explicit code repository and immutable split-root audit links. Live main is `c1564b218799b3baf07fc5e6c346bb6dcc476a7e`; no rebase. All three exact pair merge-tree preflights pass; bottom combined tree `3319ba6f63257f636ea848a56443cbe9b73bc1c0`. No runtime claim attaches to that merged tree. Draft bodies use relevant retained 17/17, 67/67, 9/9 evidence; CI cost is unmeasured. No push/PR/link/ready/merge/release/provider/reviewer/gate action ran. Existing Draft #394 and prior immutable verdicts remain unchanged.

### Summary

Exactly three authorized local product commits are complete. The full native-stack Draft delivery package is concrete and held for separate Captain push/PR approval; task status remains implementation.

## Stage Report: implementation (cycle 7)

- DONE: Repair only the observed missing Spacedock prerequisite in the existing top-layer CI job with a pinned, verified installation and unchanged matrix/triggers/test meaning.
  Published Drafts #415/#416/#417 are linked in native stack #418 at unchanged approved heads. Hosted run 34548053072 reports 4/72 missing-reader failures on both Node matrix entries. Added only a 15-line pinned v0.27.2 setup in `.github/workflows/kc-journey-map-tests.yml`, following the existing repository checksum pattern. Official Linux amd64 archive digest/checksums verified; parsed YAML equals the original after removing only the new step, and Bash syntax passes. [Diagnosis and evidence](ci-reader-bootstrap-evidence/README.md).
- DONE: Provide actual missing/present-reader evidence, exact one-file uncommitted patch, CI cost limits and a concrete local-commit packet while preserving all published candidates and state history.
  Existing real-reader tests reproduce 4/5 failures without the CLI and pass 5/5 with the freshly verified v0.27.2 reader on macOS ARM64. No test/semantic/dependency/matrix/trigger changes, fake reader, new environment or review loop. Exact Linux amd64 hosted verification remains pending a later approved commit/push; CI cost per PR unmeasured. Base `aabb8e7e8320b65fa852feae961df2e438d8f002`, candidate tree `64ca7b19f431188830b43f6824f485e7c90206df`; [one-file manifest](ci-reader-bootstrap-evidence/manifest.json), [exact patch](ci-reader-bootstrap-evidence/candidate.patch) and [local-commit packet](ci-reader-bootstrap-evidence/local-commit-review.md). Product commit/push/PR edits/ready/merge remain unauthorized. Published heads/bodies, lower layers, original root, user source/rooms and prior evidence remain unchanged. AC-1..AC-5 product evidence is retained; this change repairs only the CI execution prerequisite.

### Summary

The bounded CI reader bootstrap correction is prepared, uncommitted, with actual missing/present-reader proof and explicit hosted-verification limits. First Officer owns the next exact local-commit authority.

## Stage Report: implementation (cycle 8)

- DONE: Trim only PR415 descriptive comments to the Captain-approved standard, preserving indispensable library/data-safety/licence facts and all executable behavior.
  Approval provenance: Kent raised excess PR415 comments and approved the specified trim standard with **好**. Removed method/history/tutorial and adjacent-code/test narration; retained concise library/data-safety warnings and exact MIT attribution. Same metric: 164/1,428 comment/total lines → 17/1,281; 17 files, +12/-159. [Measured scope and retained reasons](planning-comment-trim-evidence/README.md).
- DONE: Prove the exact comment-only delta, measure before/after and retained reasons, preserve sibling/CI work, and prepare a compact uncommitted exact-file packet.
  Exact noncomment lines and existing esbuild compiled output match; shell/heredoc comparison and syntax pass. In-memory executable mutation changes compiler output; no runtime suite/install/reviewer run. Base `0d69be164ccdcd1b3509f3577d6bd03a468f8f36`, candidate tree `d6a0ff4ac49e6a2fca2ebc070259dd89b5c76c1b`; [manifest](planning-comment-trim-evidence/manifest.json), [equivalence proof](planning-comment-trim-evidence/executable-equivalence.json), [pending local-commit packet](planning-comment-trim-evidence/local-commit-review.md). Read-only sibling overlap is 14 paths with PR416 and 3 with PR417; no propagation/restack attempted. The separate pending CI patch hash remains unchanged. Published candidates/bodies, original root, source/rooms, old evidence and AC-1..AC-5 executable behavior are preserved; no fresh runtime PASS is claimed.

### Summary

The authorized PR415 comment-only draft is concrete and uncommitted, with measured reduction, retained reasons and executable-equivalence proof. Captain local-commit authority is next; sibling restacking and the separate CI repair remain pending.

## Stage Report: implementation (cycle 9)

- DONE: PR416 incremental comments are concise under the approved standard, with consistent before/after counts and representative reasons.
  Approval provenance: Kent said “416 也有一樣的問題” under the accepted PR415 standard. Published incremental comment lines 148 → 17; whole-source comments 301 → 170, with all 153 inherited lines untouched. Exactly 20 files, +13/-144. Removed method/history/usage/test narration; kept terse library/evidence/readback safety facts. Two mixed inherited blocks are deliberately deferred to bottom-trim propagation. [Counts and reasons](release-inspection-comment-trim-evidence/README.md).
- DONE: Exact executable equality passes and PR415 trim plus PR417 CI repair remain byte-identical; concrete uncommitted patch and local-commit packet are reported.
  Existing compiler and exact noncomment comparisons pass for all 20 files, with inherited comment/licence/directive preservation and separate shell/heredoc handling. No runtime/install/reviewer run. Base `818260a8c14b504dae8d3989ba9c710226255b74`, candidate tree `7711a3d343cedaae24bc007928c2cc32702d0d57`; [manifest](release-inspection-comment-trim-evidence/manifest.json), [equivalence](release-inspection-comment-trim-evidence/executable-equivalence.json), [local-commit packet](release-inspection-comment-trim-evidence/local-commit-review.md). Pending sibling patches match their exact prior hashes; no restack or published mutation. PR417 propagation overlaps records/render/storymap only. AC-1..AC-5 executable behavior and prior evidence remain unchanged; no new runtime PASS is asserted.

### Summary

The PR416-only comment draft is complete and uncommitted, with consistent incremental counts and exact executable proof. Captain local-commit authority and later sibling propagation remain pending.

## Stage Report: implementation (cycle 10)

- DONE: Exact approved single-file CI repair is committed with matching parent/tree/subject, with sibling comment drafts preserved.
  Approval provenance: Kent answered **批准** to the exact missing-reader CI repair commit. Ordinary commit `a5c08cbdf812826125decb6b55a286c4bcd2f1be`, parent `aabb8e7e8320b65fa852feae961df2e438d8f002`, tree `64ca7b19f431188830b43f6824f485e7c90206df`; approved subject and workflow +15/-0/file hash match. Target clean; both pending comment patches byte-identical. [Commit evidence](ci-reader-bootstrap-commit-evidence/commit.json). No product edits, hook bypass, tests/install/reviewer rerun or version bump.
- DONE: Concrete PR417 push and full-body update packet is prepared without publication; local proof versus hosted pending is explicit.
  [Full publication packet](ci-reader-bootstrap-commit-evidence/push-review.md) and [exact tuple/body hashes](ci-reader-bootstrap-commit-evidence/publication.json) preserve live title/base and relevant body content, adding only CI prerequisite/evidence/totals and the new Candidate. Existing stack 418 stays ordered 415/416/417; top-only fast-forward needs no restack. Exact base/candidate preflight passes. Local reader 5/5 remains distinct from pending Linux hosted verification; CI cost unmeasured. No push or gh write call. Earlier acceptance evidence and sibling drafts remain unchanged.

### Summary

The exact authorized CI repair local commit is complete. PR417 publication and exact body update are concrete and held for a separate Captain decision.

## Stage Report: implementation (cycle 11)

- DONE: Both exact comment drafts are committed and propagated through the local three-layer stack with clean owned worktrees and preserved CI/runtime behavior.
  Approval provenance: Kent instructed “移除冗餘後提交”. Exact ordinary commits: planning `c035e3ee792effb2708f646c2761d70ac17d9dbb`; inspection `77732892d2024abdae7589d576f2e3aabca01275`, matching approved trees/parents/subjects. Explicit-base rebases preserved all feature/CI commits and resolved overlapping comments only. Final heads: `c035e3ee792effb2708f646c2761d70ac17d9dbb` → `d339355faf2c2833df91cf9dde42a5ee12098341` → `36a969a6f890a63c541fad4bfa30071ac7115c64`. [Exact original/final stack and conflict disposition](comment-trim-commit-evidence/README.md).
- DONE: Exact comment-only equivalence and final ancestry are recorded; one concrete stack publication packet is ready without any remote mutation.
  Exact noncomment/compiler comparisons pass for each starting/final layer, shell/heredoc handled separately; removed explanatory blocks are absent, CI workflow hash unchanged, and owned worktrees clean. Whole-source comments 164→17, 301→31, 300→32 include inherited propagation. No runtime/install/reviewer reruns or new PR417 audit. [Equivalence](comment-trim-commit-evidence/final-equivalence.json), [final paths/stats](comment-trim-commit-evidence/final-stack.json) and [complete publication packet](comment-trim-commit-evidence/push-review.md) retain live old heads, exact proposed bases/candidates and body hashes plus explicit per-ref leases. All pair preflights pass. Hosted checks at new heads remain pending; prior CI proof is historical and CI cost unmeasured. AC-1..AC-5 executable behavior is unchanged. No remote push/PR edit/Ready/merge occurred.

### Summary

Both authorized comment removals are committed and inherited through the clean local stack. The exact three-PR push/body-update package is ready for the Captain's separate publication decision.
