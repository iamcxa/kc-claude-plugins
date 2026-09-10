---
title: Show release stories on journey boards with shared activity context
status: ideation
source:
product: kc-journey-map
planning-window:
planning-outcome:
sprint: S1
sprint-readiness: ready
started: 2026-09-10T09:34:23Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: wwn8jfrh1f6k6zyj5tfcjb23
gates:
    version: 1
    records:
        - id: gate:wwn8jfrh1f6k6zyj5tfcjb23:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:wwn8jfrh1f6k6zyj5tfcjb23-backlog-1
              briefing:
                id: briefing:wwn8jfrh1f6k6zyj5tfcjb23:backlog:attempt-1:revision-1
                digest: sha256:1f42307ebe5318d7f9f9508d14936bdc5d9c93a37ae01179502ac4c528348d15
                room-ref: ./show-release-stories-on-journey-boards/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:wwn8jfrh1f6k6zyj5tfcjb23:backlog:1
                briefing: briefing:wwn8jfrh1f6k6zyj5tfcjb23:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T09:24:50.160423Z"
                decision: approve
                reason: 'Kent approved the presented Pilot admission: release story boards, gap/unverified/exists, deferred host-selection verification, and preparation of the required local execution group.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:wwn8jfrh1f6k6zyj5tfcjb23:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:wwn8jfrh1f6k6zyj5tfcjb23-ideation-1
              briefing:
                id: briefing:wwn8jfrh1f6k6zyj5tfcjb23:ideation:attempt-1:revision-1
                digest: sha256:d8622096fe6798dc93dde21729f9501d82edbcee4c78e07dccdde77feffae3dc
                room-ref: ./show-release-stories-on-journey-boards/review/ideation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-09-10T09:50:50.348896Z"
                reason: The committed ideation analysis covers all six criteria, but the stage report uses an AC-1 through AC-6 range that the required scanner does not expand. Add explicit per-criterion citations to the existing report before presentation; no scope or product change.
            - id: gate-attempt:wwn8jfrh1f6k6zyj5tfcjb23-ideation-2
              briefing:
                id: briefing:wwn8jfrh1f6k6zyj5tfcjb23:ideation:attempt-2:revision-1
                digest: sha256:14f60796cb791988e5b95555b6d6034c4b8e97f49a68940f8b42c44afd60d07b
                room-ref: ./show-release-stories-on-journey-boards/review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:wwn8jfrh1f6k6zyj5tfcjb23:ideation:2
                briefing: briefing:wwn8jfrh1f6k6zyj5tfcjb23:ideation:attempt-2:revision-1
                by: person:captain
                at: "2026-09-10T09:55:13.06185Z"
                decision: approve
                reason: 'Kent approved the presented second ideation briefing (14f60796): implement the release-story board and three-state consistency, repair stale activity wording, preserve the bounded Pilot scope, and defer full sprint-to-release migration and live host-selection proof.'
              application:
                target-stage: implementation
                state: pending
---

## The problem

The release journey board displays green activity cards, while the story map
uses yellow stories as release scope. A person reviewing a release cannot see
which individual stories the detailed board covers or where each story lacks
evidence. Activity-level system flow must not imply per-story implementation.

This is a product behavior change in kc-journey-map, tracked by docs/dev. It is
separate from the existing standalone extraction task, whose scope excluded
renderer behavior changes. It is not a workflow-maintenance task.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    Kent will use and retain this local plugin feature to review release
    stories and round-trip edits to valuable journey files. The scope stays
    within local development use, with no production deployment or migration
    required of consumers; legacy activity cards remain readable.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Keep the journey file authoritative and activity context shared.
      - Preserve legacy canvas readback without requiring consumer migration.
    implementation:
      - Show selected release stories under their activity groups.
      - Use gap, unverified and exists consistently across the model and projections.
      - Apply wording by story identity and refuse ambiguous edits.
    testing:
      - Verify all three statuses and the implemented-story count.
      - Verify render/readback round trips, conflicts and duplicate identities.
      - Inspect each release canvas and exercise a browser edit through the server.
  scope_boundary: >-
    Local journey-board behavior and three story statuses only. Excludes
    plan-flow integration, provider changes, per-story system mapping,
    host-selection execution proof, production rollout and consumer migration.
  semantics_unchanged: false
  promote_when:
    - A consumer must migrate owned records or change configuration to upgrade.
    - Production exposure, unattended operation or long-term support is accepted.
  decision:
    authority: Kent
    at: 2026-09-10T09:02:18Z
```

The Captain selected Pilot in this session. Stage dispatch requires the state
prerequisite, committed receipt readback and admission to be satisfied.
The Planning Receipt is absent; use this standalone Captain-approved brief
without a Linear reader or comparator.

## Accepted outcome

A person can inspect each release's yellow story cards beneath green activity
groups, see each story's status, evidence and open question, and read the shared
system flow and constraints once per activity. Edited story/activity wording
round-trips to the journey file with conflicts and duplicates reported safely.
Release-detail positioning does not change the full journey order, release
membership, or priority. Existing boards remain available for comparison.

The Captain has approved three story statuses:

- `gap`: the story is known to lack implementation.
- `unverified`: the required behavior has not yet been verified; existing
  instructions or code do not settle that question on their own.
- `exists`: implementation evidence supports the story at its relevant execution
  boundary. This is not delivery acceptance or release completion.

The host-selection story is classified as `unverified`, with the actual host
verification deferred. The model, board labels, documentation and worked example
should use these meanings consistently. Missing evidence alone must not be
presented as proof that implementation is absent. Only `exists` contributes to
the implemented-story count.

## Non-goals

- Merge plan-flow into journey-map or change development providers.
- Invent per-story system mappings or turn implementation evidence into release acceptance.
- Implement or execute the deferred host-selection verification; this change records its unverified status only.
- Publish, merge, commit product code, or mark this task done without the corresponding authorization.

## Acceptance criteria

- **AC-1** Each release board displays its selected yellow story cards beneath green activity groups; system flow and constraints appear once per activity and are labeled as shared context.
- **AC-2** The journey model, rendered story/status labels, documented semantics and worked example distinguish `gap` (known missing implementation), `unverified` (behavior not yet verified), and `exists` (supported implementation). Missing evidence alone is not rendered as proof of absence, and only `exists` contributes to the implemented-story count.
- **AC-3** The host-selection story is recorded and displayed as `unverified`; the deferred host exercise is not claimed as passed or required for completion of this bounded renderer change.
- **AC-4** Activity/story wording changes read back from the story map and release boards to the correct model identities. Competing edits and duplicate identities are reported without silently choosing a winner. Existing legacy activity cards remain readable.
- **AC-5** Moving cards or groups on a release detail page does not change global activity order, release membership or story priority. Those gestures retain their documented projection-specific meanings.
- **AC-6** The three release pages are visually inspected in the browser; a story edit persists through the server and is read back into a separate output file. Existing user rooms and unrelated source/state changes are preserved. Local verification does not imply merge, release or journey-level delivery acceptance.

## Existing local observations

Existing local artifacts to inspect in the selected working stage; these are
not retrospective Spacedock stage receipts. These results predate the approved
three-status change and do not verify its implementation:

- Worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-board-stories
- Branch: codex/journey-board-stories, uncommitted changes based on 1166747c22f0d6c62db098e5f8cad61bf81174bd.
- Scope: lib/render.mjs, lib/read.mjs, lib/read.test.mjs, lib/render.test.mjs,
  skills/kc-journey-map/references/canvas.md under kc-journey-map/.
- Review record: /Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-story-change-review-20260910.md
- Unit tests: /Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-story-tests-20260910.log (59/59 passed).
- Isolated server: /Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-story-smoke-20260910.log (191 shapes across 5 pages; clean readback).
- Browser preview: http://localhost:3737/?room=v4-story-release-boards-20260910
- Three release PNGs, portable tldraw file, and a separate browser-to-YAML
  save-as check are linked from the review record. Preview descriptions were
  refreshed in a local YAML copy; the tracked example remains unchanged.
- Delivery context: PR #394 is a draft for the preceding extraction work.
  This uncommitted change is not in its current head.

## Route-back conditions

Stop and return to the Captain if the accepted outcome changes, per-story
system/rule fields become necessary, the candidate checkout is owned by another
session, or delivery needs a different PR boundary. Do not absorb unrelated
state or source changes.

## Measurement

Observed local implementation exists under the Captain's direct-FO exception.
Review is pending. Task creation must not be presented as proof that the prior
implementation traversed Spacedock stages. All local checks passing means
pending delivery acceptance, not release completion.

## Deferred host-selection verification

The story "Ask which boards to draw, through the host's selection UI" is
included only for status classification in this change. Its skill instructions
exist, while no recorded host run proves the complete selection-to-render
behavior. Record `unverified` in the story and show the same meaning on the board;
it remains excluded from the exists count. The actual host exercise is deferred.

A later check should invoke the skill in the actual host, record the presented
choices and the user's selection, and compare the resulting canvas pages with
that selection. Also check the documented default when the host tool is
unavailable. Code-symbol lookup alone does not prove this host interaction.
Do not claim the complete release journey is accepted before this story's
required evidence is resolved.

### Feedback Cycles

#### Captain continuation — release terminology and local admission

Kent authorized the proposed local docs/dev/ROADMAP.md registration and use
before merge: "我授權，但希望之後全部改成 release 稱呼". The release
delivers the existing accepted journey value without a fixed time cycle. The
legacy `sprint: S1` and heading are compatibility identifiers for the current
installed loader. A complete sprint-to-release terminology, field, command and
record migration is deferred until the journey-map slice is satisfactory; this
does not add that migration to the present implementation scope.

The FO corrected an omitted profile declaration to `semantics_unchanged: false`
from the already accepted story projection and status behavior changes. This
repairs receipt capture; it does not change the selected Pilot, scope, non-goals,
or claim any worker evidence. No worker was spawned before the loader refused
the incomplete receipt.

## Ideation: one integrated release-review journey

Decision: recover the existing candidate, finish three-status semantics in place, and extend the existing stale-wording guard to activity/card fields. No new service, model format, mapping layer, provider, dependency, or separate slice is needed. The accepted outcome, six ACs and complete non-goal list above remain authoritative; `semantics_unchanged: false` covers the added `unverified` value, explicit status labels, release-story projection, and safe wording application. Command grammar, YAML authority, release membership and priority semantics remain unchanged.

Contract: Pilot shape, kc-dev-flow 4.1.1, digest `9a592aa4b6a1b06ebad5125241f8d902e04afbbc84437cd55a2b5bf41bc9e776`; the committed `show-release-stories-on-journey-boards/ideation-stage-pin.json` is unchanged. The loader output is the task-supplied `.context/journey-board-admission-proposal/ideation-contract.txt`. Reverse recovery, retained-document policy and project-context assessment apply; one integrated slice suffices, so the multi-slice reference does not activate. Planning Receipt is absent; no provider read was performed.

### Actor and program sequence

1. **DESIGNED — Kent and the host agent:** choose the requested projections and record story status/evidence/question in the repository journey YAML. `skills/kc-journey-map/SKILL.md` owns host prompting; actual selection-to-render host execution remains unverified and deferred. No answer follows the existing story-map default; cancelling before the render command leaves files and rooms untouched.
2. **OBSERVED — Node `journey-lint.mjs` / `lint.mjs`:** load the YAML via `model.mjs`; current missing-status and exists-without-evidence refusals were exercised. **DESIGNED delta:** accept `gap`, `unverified`, `exists`, diagnose an unsupported value, and never infer absence from missing evidence. Executable-symbol lookup remains a consistency check, not proof of the complete host journey.
3. **OBSERVED — Node `journey-render.mjs` / `buildAllPages`:** build story-map and selected release-board records with `meta.journey` identity. Fresh unit execution proves selected yellow stories, green activity headings, once-per-activity shared context and safe readback. **DESIGNED delta:** every approved state has a distinct truthful label on both projections; only `exists` enters either count.
4. **OBSERVED, inherited pre-status observation — `renderToRoom` -> Fastify `PATCH /doc` -> `TLSocketRoom` / SQLite -> React `App.tsx`:** prior smoke/browser artifacts show render, browser edit persistence and save-as. This is wiring evidence for the existing candidate, not new-status acceptance. **DESIGNED verification:** use a new named room, inspect all three release pages, edit one story in the browser, reload, and observe the persisted record. A render failure/timeout is not success; inspect the new room before retrying the deterministic reconcile. Do not restart or kill existing services.
5. **OBSERVED — Node `journey-read.mjs` -> `readRoom` -> `diffAgainstModel`:** identity-based wording, same-page duplicate detection, cross-projection conflicts and legacy `step-card` readback pass focused cases. Release-detail drags are presentation changes; story-map movements continue to control ordering/membership/priority. **DESIGNED delta:** after a newer YAML activity/card edit, `applyDiff` skips stale canvas wording, as it already does for stories.
6. **OBSERVED — `applyDiff` -> separate YAML output:** unit save-as preserves the original and refuses competing story edits. **DESIGNED integrated check:** browser edit -> server snapshot -> CLI `--out` -> parse and compare the separate file by story ID; conflicts remain reported and unresolved identities are not guessed. Abandoning before `--write`/`--out` leaves YAML unchanged. A write/process failure is reported without claiming durability; keep the original and regenerate/re-read into a new output path. No crash-atomic in-place-write promise is added.

Persistence boundary: repository YAML is semantic authority; SQLite room state is an editable projection/cache, and portable `.tldr` is derived. Before rerendering an edited room, read/export edits; reconcile can replace renderer-owned records. Do not use whole-document import on an existing room. Existing v3 rooms, `v4-story-release-boards-20260910`, tacoma `package-lock.json`, and `kc-team-ops/.rooms/` are outside mutation scope. Browser validation uses a fresh alphanumeric/hyphen room name, explicit room directory/ports if an isolated server is needed, and separate output. Resolve the supplied candidate's ignored dependency links through its declared Node >=22.13.0/package-lock installation for reproducible validation; do not treat those machine-local links as a clean-install result.

### Reverse recovery tied to acceptance

Search boundary: candidate `kc-journey-map/{lib,server,skills/kc-journey-map}`; trace imports and exported call sites, then inspect named implementations/tests. The source at delivery base `1166747c22f0d6c62db098e5f8cad61bf81174bd` was exercised for the without-candidate comparison. External host adapters, plan-flow and providers were excluded. No layer is classified MISSING or NO_OBSERVED_CONSUMER; the existing seams are sufficient.

| Surface / AC | Location | Completeness / need | Evidence and disproof hook | Route |
|---|---|---|---|---|
| Host entry / AC-3 | `SKILL.md:75`, `render.mjs:171` | WORKING_UNIT_UNPROVEN / REQUIRED | Default projection unit cases pass; actual host selection is unobserved. A real host run selecting boards that produces different pages would disprove wiring. | Keep entry, mark story unverified, defer host execution. |
| Story contract/lint / AC-2 | `model.mjs:8`, `lint.mjs:39` | EXISTS_BROKEN / REQUIRED | Runtime probe: `lintNoStatus` accepts `status: made-up`; missing-status and exists-without-evidence fixtures do produce diagnostics. | Add the small supported-status check through existing normalization/lint, retaining evidence checks. |
| Story-map projection / AC-2, AC-3 | `storymap.mjs:176,213` | EXISTS_BROKEN / REQUIRED | Three-state probe draws GAP only; unverified and exists lack status badges. Count is already 1/3. | Extend existing status label branch; preserve count derivation. |
| Release-board projection / AC-1, AC-2 | `render.mjs:29,57,132` | EXISTS_BROKEN / REQUIRED | Base produces zero `kind: story` records for a selected one-story release; candidate produces that story. Three-state candidate displays `UNASSESSED` for unverified while count remains 1/3. | Retain candidate grouping/shared context, correct status labels. |
| Generated release contract / AC-2 | `release-contract.mjs:11,35` | WORKING_UNIT_UNPROVEN / REQUIRED | Runtime output preserves an unverified row as `unverified`; release-scope/unknown-release tests pass. Mutation of status passthrough must fail a three-state contract check. | Reuse generator; correct its obsolete replacement-board comment, no new renderer. |
| Canvas identity and YAML application / AC-4, AC-5 | `read.mjs:41,79,107,137,222` | EXISTS_BROKEN / REQUIRED | Fresh tests cover duplicates/conflicts/save-as/legacy and detail-drag boundaries. Temp-file probe showed stale activity diff overwrites `Newer file edit` with `Canvas edit`, skipped=[]. | Extend existing story `was` comparison to activity/card wording and test it. |
| Server/browser persistence / AC-6 | `server/canvas-server.ts:68,74`, `server/rooms.ts:18`, `server/client/App.tsx:20` | WORKING / REQUIRED for inherited pre-status seam | Supplied smoke/browser artifacts show save-as through server; current three-state/browser result remains unverified. Reload + CLI save-as by ID can falsify persistence. | Reuse, rerun bounded browser acceptance after the delta. |
| Documented model/example / AC-2, AC-3 | `SKILL.md:44,55`, `cell-contract.md:57`, `canvas.md:134`, `journey.example.yaml:51` | EXISTS_BROKEN / REQUIRED | Two-state prose and example classify host selection as gap; the host story's runtime-loaded record confirms it. A render/contract from the revised example must show unverified and exclude it from counts. | Repair in place and regenerate the shipped example board. |

Receipt: `reverse_recovery.trigger = brownfield_capability_change`; boundary and layers are the table above; `decision = recover`. Fresh `node --test lib/*.test.mjs` passed 59/59 in this stage. These existing tests prove their named candidate behavior, not the missing status delta or new browser acceptance. The failing behavior probes above are current evidence, not retrospective stage receipts.

### Where it touches

Paths below are relative to candidate `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-board-stories`. Counts were read from that tree; after counts are estimates. Existing candidate changes are retained, not committed by ideation.

| Path | Lines now | Lines after (estimate) | Journey reason |
|---|---:|---:|---|
| `kc-journey-map/lib/model.mjs` | 22 | 28 | Shared supported-status vocabulary if needed by lint/projections; no separate framework. |
| `kc-journey-map/lib/lint.mjs` | 71 | 82 | Step 2: diagnose unsupported states. |
| `kc-journey-map/lib/lint.test.mjs` | 140 | 165 | State/refusal instrument. |
| `kc-journey-map/lib/storymap.mjs` | 280 | 284 | Step 3: three status labels. |
| `kc-journey-map/lib/storymap.test.mjs` | 103 | 128 | Labels/count and cross-band regression. |
| `kc-journey-map/lib/render.mjs` | 202 | 204 | Step 3: retain candidate and fix unverified label. |
| `kc-journey-map/lib/render.test.mjs` | 60 | 86 | Selected stories/shared context/three states. |
| `kc-journey-map/lib/read.mjs` | 302 | 310 | Step 5: stale activity/card guard. |
| `kc-journey-map/lib/read.test.mjs` | 303 | 335 | Stale activity/card safety, existing identity/gesture cases. |
| `kc-journey-map/lib/release-contract.mjs` | 43 | 40 | Step 3: retain status passthrough; repair misleading header comment. |
| `kc-journey-map/lib/release-contract.test.mjs` | 40 | 52 | All three states preserved in generated contract. |
| `kc-journey-map/lib/journey-example.test.mjs` | 46 | 66 | Host remains unverified, not counted; revised example behavior. |
| `kc-journey-map/skills/kc-journey-map/SKILL.md` | 156 | 160 | Step 1: consistent status rules, reference canonical meanings. |
| `kc-journey-map/skills/kc-journey-map/references/cell-contract.md` | 113 | 119 | Canonical meaning of the three states and evidence limits. |
| `kc-journey-map/skills/kc-journey-map/references/canvas.md` | 233 | 237 | Gesture semantics, status display and diagnostic commands. |
| `kc-journey-map/skills/kc-journey-map/references/journey.example.yaml` | 219 | 219 | Host classification and stale render/read descriptions in worked source. |
| `kc-journey-map/skills/kc-journey-map/references/example/README.md` | 41 | 41 | Generated board's new page description; correct readback source path. |
| `kc-journey-map/skills/kc-journey-map/references/example/draw-a-journey.tldr` | 1 logical line, no newline; 78,485 bytes | 1 compact logical line | Regenerate from the revised example in a new room, not manually authored. |
| `docs/dev/ROADMAP.md` | 465 | 465 | Already-authorized local registration, no further planned edit. |
| `kc-journey-map/lib/journey-render.mjs`, `lib/journey-read.mjs` | 24 / 29 | 24 / 29 | Existing CLI entrypoints, read-only dependencies. |
| `kc-journey-map/server/client/App.tsx`, `server/canvas-server.ts`, `server/rooms.ts` | 43 / 114 / 48 | 43 / 114 / 48 | Existing browser/HTTP/SQLite seams, read-only dependencies. |

Reconciliation: steps 1–6 map to the rows above; shared `records.mjs`, unchanged function-map/tldraw helpers and package dependency files are exercised transitively and need no product edit. No new retained document is proposed. Apply retained-document Rules 1–3 and 6–8 in place: keep semantic definitions in `cell-contract.md`, operational gestures/checks in `canvas.md`, entry guidance in SKILL, and observed task history here. The worked YAML/board remains a generated example pair, not a second live task tracker. Do not broaden this into cleanup of unrelated catalog/history prose.

### Delivery base and implementation stops

Delivery base: Draft PR #394 source `iamcxa/journey-map-skill-merge`, exact `1166747c22f0d6c62db098e5f8cad61bf81174bd`, supplied as live-verified by the FO; local candidate HEAD was independently checked at that SHA. This stage did not make a provider read or claim present PR acceptance. All measurements include the inherited candidate and local ROADMAP registration against that base, not just the future status patch.

Current diff: 6 files, 681 added+deleted lines including the untracked 60-line `render.test.mjs`; tracked additions/deletions are 319/302. Source runtime `.mjs` changes are 409 added+deleted lines (read 122, render 287). Count untracked intended files explicitly; plain `git diff` omits them.

Implementation stops and reports on **20 changed files**, **1,400 added+deleted lines**, or **650 added+deleted lines in non-test `kc-journey-map/lib/*.mjs`** against the pinned base. Stop also on any new service, dependency, provider, per-story system mapping, consumer migration, or workspace ownership change. These are halt thresholds, not budgets or pass/fail scores. Preserve compact `.tldr` serialization; a generated-file reformat counts toward the same line threshold. File/line estimates are planning evidence, not a completed implementation.

### Falsifiable implementation and validation checks

- **AC-1 / mutation (remove candidate) then positive:** run a selected one-story release through base and candidate `buildJourneyBoard`; observed base yields no story record, candidate yields the selected ID. Final tests must reject wrong-release cards and duplicated shared flow/rules. A renderer that falls back to activity-only cards or copies system context per story must fail them.
- **AC-2 / refusal and mutation:** before fixing, exercise unsupported `status: made-up` through lint and a three-story gap/unverified/exists model through both projections; observed missing diagnostic, missing map badges and `UNASSESSED` prove the instrument has a red case. Final checks require supported values, truthful labels and 1/3 implemented count, plus release-contract passthrough. Mutating the count predicate to count unverified must fail. Preserve existing missing-status, missing-evidence and prose-only-symbol refusal fixtures; symbol search cannot prove execution-boundary acceptance.
- **AC-3 / mutation:** load the tracked example, identify `ask-which-boards-to-draw`, assert unverified, render both projections and contract, and compare counts excluding it. Reverting that source to gap or exists must fail. No host launch is part of this check; its actual host exercise stays deferred.
- **AC-4 / refusal and mutation:** retain same/different wording, duplicate IDs within one page, identical text on different story IDs, legacy cards and separate-output assertions. Temp-file stale activity probe already failed safely expected behavior: `applyDiff` overwrote a newer file value. After repair, activity/card and story stale changes must be reported/skipped with the newer value preserved; removing the `was` guard must fail. Do not silently select one competing edit.
- **AC-5 / mutation:** move release-detail groups/cards across x/y and assert unchanged global order, membership and priority; then move a story-map card across a release line and assert that membership does change. Removing page scoping must fail the first assertion; ignoring all movement must fail the second.
- **AC-6 / real seam:** after the implementation delta, check service ownership and use a fresh named room/session. Inspect all three release pages at readable zoom for yellow selected stories, green groups, shared context and status labels without clipping. Edit a story in the browser, reload to prove server persistence, run `journey-read.mjs <source> <new-room> --out <separate-file>`, parse by ID and compare original/source and existing-room snapshots. A no-op browser edit, wrong identity or dropped server save must fail. Regenerate the portable example from that revised source and verify its readback. Keep evidence separate from prior preview artifacts and preserve existing services.

Implementation runs the affected Node tests and the declared example lint; validation then exercises the final integrated browser path and existing smoke at a task-owned room directory. Do not run redundant broad suites after the required checks pass without a new failure/change. No CI change is planned; CI cost was not measured, and no cost claim is made.

### Project-context assessment and deferred boundaries

`project_context`: impact **none**; authority **root PRODUCT.md + ARCHITECTURE.md + CLAUDE.md**, as bound by `docs/dev/README.md` Local Profile; claim_locator **Repository plugin catalog / Repository layout / repo-wide release policy**; surface **existing standalone plugin projections and local registration**; stale_claim **none caused by this slice**; approved_change **none**; landed_change **none**; planned_check **compare the delivered diff with those authority sections and run projection/default-selection/legacy-readback cases; fail this classification if it changes catalog identity, provider authority, server/persistence architecture, command grammar or consumer upgrade obligations**; validation_evidence **pending final-candidate verification**. The seven-plugin catalog omission predates this delivery base and is not repaired by expanding this renderer task. Plugin-specific status/gesture claims are repaired in their existing skill references, with no new project-context document.

Release means one delivered user-journey value with no fixed timebox. Kent authorized the exact local ROADMAP registration and use before main merge; `sprint: S1` is the current loader's compatibility identifier, not a completed rename. Deferred work, recorded here rather than in a parallel tracker: full sprint-to-release terminology/field/CLI/parser/schema/history migration, including loader/admission, workflow README/ROADMAP, work-context validator and adoption/profile skills/tests. Plan-flow integration, provider migration and per-story system mappings remain out of scope. Actual host-selection verification remains deferred; unverified is excluded from implemented counts and cannot be promoted through symbol lookup.

## Stage Report: ideation

- DONE: Prove the minimum delta against the existing candidate: release stories and shared context, gap/unverified/exists semantics, and a code-grounded reverse-recovery assessment tied to AC-1 through AC-6.
  The recovery table maps each acceptance criterion to source/runtime evidence; fresh 59/59 tests preserve candidate logic, while three-state and stale-activity probes expose concrete failures to repair.
- DONE: Record one integrated actor/program journey with observed versus designed seams, safe persistence and recovery, file-level touch estimates, delivery-base-scoped stop numbers, and falsifiable implementation/validation checks.
  The sequence, file table and checks above bind the single route to 1166747c22f0d6c62db098e5f8cad61bf81174bd; final browser/status proof remains designed, not claimed.
- DONE: Preserve the candidate and user rooms; record release terminology intent, the authorized local scheduling exception, and deferred host-selection proof without expanding into plan-flow or the repository-wide field migration.
  No product or room mutation was performed; state-only report append preserves frontmatter and the stage pin. Deferred terminology and host work remain in this entity.

- AC-1: Observed `render.mjs:29` base/candidate probe: zero versus one selected story record; `render.test.mjs` exercises yellow stories and once-per-activity context. Final browser layout remains validation work.
- AC-2: Observed `lint.mjs:39`, `storymap.mjs:213`, `render.mjs:57` probes expose unsupported-status acceptance, absent badges and UNASSESSED; final three-state/count repair checks are designed above.
- AC-3: Observed runtime-loaded `journey.example.yaml:51` still marks host selection gap; change to unverified and projection/count checks are designed, while actual host execution remains deferred.
- AC-4: Observed `read.test.mjs` identity/conflict/legacy cases pass; the `applyDiff` temp-file probe overwrites newer activity wording. The existing guard extension and stale-edit refusal check remain implementation/validation work.
- AC-5: Observed `read.test.mjs` release-detail movement refusal and story-map cross-band membership cases pass; final candidate must preserve these projection-specific semantics.
- AC-6: Inherited smoke/browser save-as evidence is in Existing local observations; no new-status browser proof is claimed. Fresh three-page inspection and browser-to-server-to-separate-YAML checks remain designed above.

### Summary

Recover the existing release-story candidate, finish the three-status model/projections/documentation/example, and extend its stale-wording guard to activity/card fields. The approved scope fits one Pilot slice with explicit refusal, mutation and browser checks; implementation authorization and final-candidate validation remain with the next workflow boundary.
