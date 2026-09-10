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
pr:
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
                state: pending
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
