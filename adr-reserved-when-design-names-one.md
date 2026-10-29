---
title: An implementation dispatch for a task whose design calls for an ADR is refused until an ADR number is reserved in ## Number guards
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: validation
gates:
    version: 1
    records:
        - id: gate:adr-reserved-when-design-names-one:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-reserved-when-design-names-one-backlog-1
              briefing:
                id: briefing:adr-reserved-when-design-names-one:backlog:attempt-1:revision-1
                digest: sha256:54eb1a6854e50fa913931776a3125fcae222a0eeebabecd91f45c7e5bf00ff95
                room-ref: ./adr-reserved-when-design-names-one/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-reserved-when-design-names-one:backlog:1
                briefing: briefing:adr-reserved-when-design-names-one:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-29T00:39:44.625775Z"
                decision: approve
                reason: The Captain 「同意這些內容」 (chat, 2026-10-29), answering FO's joint batch-10 backlog sitting of six gates whose ask was 「決定：六張全照建議（五張進設計，被取代條件那張先留在待辦）？要改哪張直接說。」; accepts FO's recommendation to enter ideation on the pilot profile.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:adr-reserved-when-design-names-one:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:adr-reserved-when-design-names-one-ideation-1
              briefing:
                id: briefing:adr-reserved-when-design-names-one:ideation:attempt-1:revision-1
                digest: sha256:83190f738682111c3d9bc7c3f43d366e8560ac7c2faeda5f055a013ece56e218
                room-ref: ./adr-reserved-when-design-names-one/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-reserved-when-design-names-one:ideation:1
                briefing: briefing:adr-reserved-when-design-names-one:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-29T01:27:42.83882Z"
                decision: revise
                reason: The Captain 「照建議」 (chat, 2026-10-29), answering FO's joint batch-10 ideation sitting whose ask was 「決定：五張全照建議（一張擱著、四張照表改）；如果哪張要調整，直接說。」; accepts the direction and FO's recommendation to revise with the asks named in the gate question, and batch ruling A (a check covers the bites it can observe from structure; the observer keeps the rest).
            - id: gate-attempt:adr-reserved-when-design-names-one-ideation-2
              briefing:
                id: briefing:adr-reserved-when-design-names-one:ideation:attempt-2:revision-1
                digest: sha256:54fa2bc954c3729645b78886ac66be3efaa114dff9000a5b9dc24871c0cab832
                room-ref: ./adr-reserved-when-design-names-one/review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-reserved-when-design-names-one:ideation:2
                briefing: briefing:adr-reserved-when-design-names-one:ideation:attempt-2:revision-1
                by: person:captain
                at: "2026-10-29T03:47:43.145419Z"
                decision: approve
                reason: The Captain 「進實作」 (chat, 2026-10-29), answering FO's joint batch-10 revised-ideation sitting of four gates whose ask was 「決定：四張全准進實作，含工作流文件多 27 字？要改哪張直接說。」; accepts FO's recommendation for this task as stated in the gate question, including the +27-word workflow raise for gate-requires-recorded-reviews.
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-29T07:05:20Z
worktree: .worktrees/spacedock-ensign-adr-reserved-when-design-names-one
pr: iamcxa/kc-claude-plugins#751
---

## Scope

- Source: the Captain 「全准」 (chat, 2026-10-28), answering FO's batch-8 closing sitting, item 二 (open two package tasks so a check refuses what FO kept getting wrong).
- Bite: seed-check-requires-schema-fields (#740, 2026-10-28): its design records the ruling as an ADR, the first implementation dispatch carried no number, and the worker had to ask FO; codex-reader-same-head-unresolved (#728, 2026-10-27): an enduring ruling shipped without an ADR, fixed later by #732. dispatch-carries-reserved-adr-number was closed because the existing check only covers a number already reserved.
- Upstream first: `scripts/dispatch_records.py` (`check_task_facts`), `scripts/number_guards.py`, README Number guards.

## Non-goals

- Checking prose quality or whether a summary is faithful; only the structure the README already states.

## Budget

- One package PR; no new script.

## Stop condition

- Per the Captain's 2026-10-29 ideation-gate revise, the actual candidate check refuses the original #740 design-with-placeholder/no-reservation dispatch and accepts its correctly reserved recovery. #728 is removed from the required replay. Preserve valid reservations and unrelated baseline verdicts; stop and return to FO if this requires semantic ADR classification, a universal declaration, a new lifecycle hook or an adopter migration. Batch ruling A leaves unobservable intent and omitted obligations with the observer.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Result: aligned at backlog: the Captain 「同意這些內容」 (chat, 2026-10-29) to FO's batch-10 backlog sitting, which asked 「決定：六張全照建議（五張進設計，被取代條件那張先留在待辦）？要改哪張直接說。」, approved the outcome and bounds in this file. Where the check runs is a package design choice ideation proposes and the ideation gate rules.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-29 — batch-10 review before the joint ideation sitting: approve, revise or cut each task, the Captain's decisions, overlap and order

## PRFAQ

**Proposition.** Before an implementation worker starts, FO's existing dispatch check will refuse a Pilot/Prod task whose current design explicitly lists an unnumbered `docs/adr/` deliverable but whose `## Number guards` reserves no ADR. FO reserves through the existing allocator, records the number, copies it into the dispatch, and reruns the existing check before building the worker prompt.

**Who benefits?** FO and the implementation worker: the worker no longer has to stop the #740-shaped assignment to request a number that the design already says it needs.

**Does this decide whether a ruling deserves an ADR?** No. Batch ruling A, accepted by the Captain on 2026-10-29, means the check covers observable structure and the observer keeps the remainder. #728, whose design named no new ADR, is explicitly removed from the required replay; an enduring ruling omitted from the design remains outside this check.

**Is this a new mandatory field or native Spacedock lock?** No. It repairs `check_task_facts` in the existing pre-build `--names` command. Success stays silent; the procedural boundary still depends on FO running and honoring that command. No universal ADR yes/none declaration, semantic classifier, auto-reservation, new script, new hook or new CI trigger is introduced.

## Design

This revision supersedes the earlier held design and resolves its sole scope question through the recorded ideation-gate revise. Authority: Captain 「照建議」, 2026-10-29, and `adr-reserved-when-design-names-one/review/ideation/briefing-1/index.json` question: refuse only a design naming a docs/adr placeholder without an ADR reservation; replay #740; drop #728. Earlier Stage Report bytes below are preserved. Profile remains Pilot, one package PR, `Surfaces: none`.

### Chain, source and prior decisions

1. **Spacedock first.** Read 0.27.3's own `skills/first-officer/references/fo-dispatch-core.md`: dispatch build owns assembly/state; successful build must be followed immediately by worker spawn. There is no package-specific ADR classifier there. Keep this check before build, with no operation inserted between build and spawn.
2. **Package next.** `git fetch origin` succeeded; source is `5725d495bb83a17ec13616bb5421bf5ffdc71f70`, released manifest 0.33.0. Loaded Codex package `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0`; its dispatch checker, number parser and laws checker byte-match source. `--names` calls `check_task_facts`; `--newest` calls only `check_names`; folder completeness and `--coverage` are separate paths. Only `implementation-1.md` currently compares existing reservations with scope notes, so an empty ADR set passes. `laws_check.py:l2_dispatch_record_complete` has a closed diagnostic grammar and must recognize the added error in the same change.
3. **Adopters last, read-only.** Relay `/Users/kent/conductor/workspaces/subspace-relay/dhaka` at `5c75e36b5b220c44911c4575286d24bd973d53f6` retains the prose reservation rule. Web `/Users/kent/conductor/workspaces/subspace-web/dev2-fo` at `485195ec9b30833a3b55e937d7598041932d312e` also contains the pre-build `--names` call. This corrects the earlier report's different web checkout observation; neither is a hosted-state claim. QNow's earlier report recorded local `278f79ca3eb03a8c1286817f542c4ec4b744bfed` with the same rule and pre-build command; that checkout was not located for a fresh read in this revision, so QNow remains a prior local observation, not refreshed proof. No adopter-specific mechanism is used as the authority for Spacedock behavior.
4. **Existing seam, not a replacement.** The exact #740 CLI replay below establishes the empty-set hole. Source searches covered the checker, allocator, workflow caller and historical consumer; native enforcement outside those paths is not claimed. Read Accepted ADRs 0002 (reservation ownership), 0017 (event-time history), 0020 (reading budget), 0025 (land or release a reservation), and 0027 (structured checks at the writer). The rejected phrase classifier in ADR 0027 stays rejected. State `Override:` records supplied no permission to revive it or the closed Captain-rulings ledger. This repairs existing obligations; no new ADR or number reservation is proposed for this task.

### Exact observable boundary

- Apply the new missing-reservation predicate only to `implementation-N.md` and `implementation-N-message-M.md`, for recorded Pilot/Prod tasks. Keep flat `<slug>.md` and folder `<slug>/index.md` lookup as today. Other record names/modes keep their existing behavior. POC retains its no-number rule and does not acquire this new refusal or an ideation requirement.
- Read the current design as the last top-level `## Design` section, permitting a title suffix beginning ` — ` or `: `, including its level-three/four subsections until the next top-level heading. Headings inside fenced blocks are not section boundaries. A design written under another title, a report-only obligation or a free-form ruling is not structurally classified by this slice; the observer still reads it. This is a documented parser bound, not a new mandatory design heading for every task.
- In that section, recognize an explicit path `docs/adr/<placeholder>-short-title.md`: `<placeholder>` is a nonempty single-line angle-bracket token; the title is nonempty and may itself contain a title placeholder. Support the existing `<FO-reserved-number>` and `<reserved number>` spellings, inline code, list items and table cells. Ignore fenced code blocks and blockquotes, including space-indented blockquotes. A numbered `docs/adr/0041-title.md` citation is not an unnumbered deliverable. Do not infer from the words ADR, ruling, approved, required, or none.
- An explicit matching path in the current Design is the entire signal; prose around it is not interpreted for intent, approval or negation. Put withdrawn alternatives outside the current Design or in quoted/fenced historical material through the existing authorized correction route. Do not silently delete a Captain obligation or an old report to make the check pass. This boundary can miss unusual forms or flag a literal example left in active design prose; that limitation is visible, not disguised as semantic proof.
- Refuse when this signal exists and the existing `number_guards.task_facts(task)['adr']` set is empty. Reuse the numeric parser and allocator; their existing grammar/collision limits remain. An unrelated migration number cannot satisfy it. A reserved ADR clears only this new predicate, not other existing checks.
- Preserve the existing scope-notes comparison exactly, including its implementation-1.md boundary for ADR and Migration. FO still copies the reservation into every dispatch as the current README instructs, but this slice does not add a new missing-copy refusal on continuation records. A missing/corrected reservation produces no automatic file edit or allocation.
- Emit one record-attributed line, preserving the established `<record>:<line>:` format. Proposed text: `record.md:1: design ADR placeholder has no reserved ADR; reserve with number_guards.py, record ADR: NNNN under '## Number guards', copy it into scope notes, then rerun this check`. Retain the matched task path/line in test evidence without adding a success banner. Existing scope-copy errors retain their existing vocabulary.
- Teach the laws consumer that this diagnostic is an L2 dispatch violation, not an unparseable result. It reads the task and dispatch as of the event commit using its existing temporary snapshot, not today's repaired task. Inputs: event commit, task bytes, dispatch bytes and filename, parser version, and the existing workflow/extension inputs for the other checks. No all-history sweep, permanent-red promise, backfill or new law is added; current push-range behavior remains.
- Releasing a number under ADR 0025 does not excuse a still-current placeholder obligation. If the Captain releases the deliverable, the authorized current design revision must remove that obligation while preserving prior reports/rulings. Numeric-path-only designs, obligations recorded only in feedback, authentication of Captain approval, and whether one reserved number is the correct decision remain outside this predicate.

### Journey and stops

```mermaid
flowchart TD
    A[Captain approves design or revision] --> B[FO saves implementation record]
    B --> C[FO runs existing names check before build]
    C --> D{Current Design has ADR placeholder and no reservation?}
    D -- Yes --> E[Refuse with repair message; no build or spawn]
    E --> F[FO reserves ADR and records number in task and scope notes]
    F --> C
    D -- No --> G{Existing checks including ADR scope copy pass?}
    G -- No --> H[FO repairs the named record or returns authority question]
    H --> C
    G -- Yes --> I[Spacedock builds dispatch]
    I --> J[Immediate worker spawn]
    J --> K[Worker implements; validation checks the reserved ADR]
    K --> L[FO presents normal Captain gate]
    M[Observer checks omitted ADR obligations and intent] -.-> L
```

The POC/no-placeholder branch reaches the existing checks; it does not bypass them. FO cannot turn an authority question into a self-approved design change. Prose/diagram comparison checks actors, order, refusal/retry and approval boundary; rendering was not exercised in this revision, so no rendered-preview claim is made.

### Historical replay and current evidence

Original #740 state commit: `09da6be7ad5aaf687ea3f80e9553f3efb525cc17`. Export `seed-check-requires-schema-fields.md` and `seed-check-requires-schema-fields/dispatch/implementation-1.md` with `git -C <state> show <commit>:<path>` into the same relative temporary layout, then run `python3 -B <package>/scripts/dispatch_records.py --names <temp>/seed-check-requires-schema-fields/dispatch/implementation-1.md`.

- Task SHA-256: `9cdb2a04175c91eb996fb8c314067cfd6fe5fe4636ef399b97fc0effa4288406`; record SHA-256: `5f80555583c521fc2f21cca8ea407d542335b8d371a8f34c934e8b1b40ae6c20`.
- Observed released checker: exit 0, empty stdout. A disposable design-predicate experiment extracted `docs/adr/<FO-reserved-number>-seed-admission-enforces-required-fields.md` from Design and found no Number guards section, so the proposed decision is refuse. This is feasibility evidence, **not a candidate CLI refusal**; implementation must exercise that exact raw pair without adding intent to it.
- Provider check succeeded: `gh pr view 740 --repo iamcxa/kc-claude-plugins --json number,state,mergeCommit` returned MERGED, `60896216d1c4ca842327e6a5beb2191a64993657`. No GitHub API failure occurred in this revision. Git supplies the replay bytes independently.
- #728 is removed from the acceptance replay and remains a stated uncovered omission. The earlier report is historical evidence, not a promise to refuse it.
- The previous ADR 0043 control and already-red renumbered/amendment records are retained as corpus inputs, not a claim that all current records are green. Candidate corpus comparison, continuation missing-reservation behavior and laws classification remain implementation/validation proof obligations.

### Words FO reads at each lifecycle moment

No workflow, mod, skill, extension, adoption wording or recurring output changes. Measured with `len(text.split())` against the pinned installed package and Spacedock 0.27.3, plus actual `test_pr_watch.TasksTests` output under its disposable GitHub/Spacedock stubs. These are bounded reading scenarios, not a live FO/GitHub execution. Proposed-after figures are design targets, not candidate measurements.

| Moment | Measured before | Proposed after | Included executed output |
| --- | ---: | ---: | --- |
| startup, feedback extension unlisted | 6967 | 6967 | open PR with existing codex-error output, 37 words |
| idle on that open PR | 870 | 870 | same 37 words |
| idle on a merged PR, learn unlisted | 833 | 833 | 0 words |
| after archive, learn listed | 333 | 333 | 5 words |
| merge ask, four validation gates waiting | 2408 | 2408 | 90 words |
| valid implementation dispatch | existing task/record and checks | same | new predicate adds 0 words |
| #740 refusal, before recovery | 0 diagnostic words | 27 diagnostic words | proposed exact line above; base CLI was silent |
| recovery reread after refusal | none from this predicate | 468 existing words plus 27-word diagnostic | FO steps: number guards; allocator output counted additionally at implementation |

Reading manifest: startup = full workflow (5754) + dev skill (763) + package mod (48) + upstream pr-merge startup (365) + output (37). Each idle = package mod (48) + upstream pr-merge idle (100) + workflow Delivery authority and Extensions (685) + output. After archive = mod (48) + learn extension (280) + output (5). Merge ask = Delivery authority/Extensions (685) + upstream fo-gate-lifecycle and present-gate skills (1633) + output (90). Exact newline headings select sections, not frontmatter mentions. Count each component once per arm. Host/runtime context and variable task/review content are held constant outside this bounded comparison, not asserted to cost zero.

Reproduce outputs by importing the shipped `test_pr_watch`, invoking `TasksTests.setUp`, and always `doCleanups`: use `readme('roborev, codex')`, `task('some-task', pr='o/r#7')`, then `tasks({'pr view 7': view('OPEN')})` or `view('MERGED')`; archive uses `readme('learn')`, `archive('some-task')`, merged view; merge ask uses four `gates((slug, 'validation', 'awaiting-captain'), ...)` rows a/b/c/d and `tasks({})`. These tests create only disposable repositories; no real repository config is written. Candidate repeats the same scenarios and includes every actual new diagnostic, allocator response and retry. No total reading reduction or workflow budget increase is claimed. CI files remain unchanged; cost per PR was not measured.

### Unresolved decisions

None for this revision. The Captain already accepted the narrow structural boundary and the #728 coverage loss. Recommend proceeding with that bounded design; what gets worse remains explicit: an omitted ADR obligation or an unrecognized design form can still escape, and an actual refusal adds recovery reading. If a real corpus case demands semantic classification, a universal new declaration, adoption migration or a native lock, stop and return that scope change to FO rather than widening this implementation.

### Batch overlap

Changed files proposed: `kc-dev-flow-2/scripts/dispatch_records.py` (predicate, its CLI contract), `scripts/test_dispatch_records.py` (raw replay, limits and positive controls), `scripts/laws_check.py` and `scripts/test_laws_check.py` (diagnostic classification/event snapshot), `VALIDATION.md` (evidence and remaining limits). All abbreviated paths in this paragraph are under `kc-dev-flow-2/`. No `number_guards.py`, workflow, mod, skill, CI, adopter README, ADR file, ADR index or number namespace change is proposed.

| Other task, plain meaning | Shared file/check; implementation consequence |
| --- | --- |
| seed-check-requires-alignment-result — seed alignment presence | design_surfaces.py's existing predicate is consumed by dispatch_records.py; rerun dispatch tests, no direct proposed file overlap except any shared VALIDATION.md evidence |
| captain-amendment-form-checked — amendment form and history | direct overlap in dispatch_records.py, test_dispatch_records.py, laws_check.py, test_laws_check.py and VALIDATION.md; integrate its shared parser first |
| adr-reserved-when-design-names-one — this task | owns the five proposed files above in future implementation; only this entity body/report now |
| validation-rerun-waits-for-captain-ruling — hold unresolved validation | direct dispatch checker/tests and laws consumer/tests overlap; preserve both diagnostic vocabularies |
| gate-requires-recorded-reviews — gate review presence | delivery_gate.py/workflow path; no direct runtime overlap, check shared VALIDATION.md if its final plan edits it |
| adoption-asks-which-extensions — event-time extension context | dispatch_records.py, test_dispatch_records.py, test_laws_check.py; preserve historical workflow resolution before this integration |
| adr-required-statement — old ruling ledger | Captain closed it 2026-10-20 despite stale validation status; no active overlap/dependency, do not import ledger or occupied number |
| adr-silent-undo-probe — ADR reversal experiment | moved to dev2-poc as adr-silent-undo-poc; old ideation copy is not dispatched; no shared proposed file |
| comment-check-reaches-delivery-gate — comment evidence gate | Captain closed it 2026-10-20; no active dependency or shared proposed runtime |
| journey-canvas-hosted-poc — hosted journey canvas | kc-journey-map files; no shared proposed file/check |
| journey-server-host-pilot — private journey server | read folder task index.md, validation; kc-journey-map server/host and docs; no shared file, useful folder-task corpus input |
| ops-inbox-r1-setup-and-isolation — isolated operations intake | kc-ops-inbox files; no shared file; its pre-renumber dispatch is an existing failure to preserve |
| pr-review-lite-value-pilot — bounded review experiment | kc-pr-flow review runtime/journey artifacts; no shared proposed file/check |

Read-only sibling snapshot was taken during concurrent state work (tip observed `ceea17cae7c3a2bfb9180aa07ad0eceae6f7c365`); task-status statements describe local records, not current hosted PRs. Recommended order: adoption's event-time context, amendment parser integration, this repair, then validation-rerun on the rebased checker; run combined dispatch/laws checks after each. Seed and gate-review work may proceed independently subject to evidence-file conflicts; do not wait on closed or unrelated tasks. Pilot boundary: no production obligation or implementation authorization is added by this report.

## Acceptance criteria

**AC-1** — Raw #740 replay refuses and recovery succeeds. Export the exact task/dispatch pair and SHA-256 values above; released base must remain exit 0/empty and candidate `--names` must exit 1 with the new diagnostic. In a separately labelled recovery fixture, reserve via the existing allocator, write its ADR line under Number guards and in scope notes, then require the new refusal to disappear. Falsifiers: remove the predicate call, delete the ADR line, supply only Migration, or leave only a scope-note number; the missing-reservation case must still fail. Current evidence: actual base CLI and structural design experiment only; candidate/allocator recovery unverified.

**AC-2** — Boundary and compatibility remain explicit. Exercise flat/folder tasks, first/repeated/message implementation records, Pilot/Prod and POC, the accepted placeholder spellings, lists/tables/inline code, fences and indented blockquotes, numbered citations, last Design versus superseded reports, no-placeholder tasks and authorized removal of the current obligation. Compare pinned committed task+dispatch corpora on base/candidate, listing each changed verdict and preserving pre-existing amendment/renumber failures. Existing correctly reserved tasks retain their baseline verdicts, including the existing first-record-only scope-copy check. Falsifiers: classify a historical/fenced ADR example, require a number for POC, let an unreserved placeholder on a continuation pass, or silently change folder/newest/coverage behavior. #728 is not a required refusal. Current evidence: source and sibling reads; candidate matrix/corpus unverified.

**AC-3** — Refusal reaches the existing caller and historical consumer. Run the actual candidate CLI before a disposable dispatch sequence; nonzero means zero build/spawn calls, and corrected input reaches the normal build/immediate-spawn sequence. Exercise laws L2 over the event commit: missing reservation is a violation, not Cannot; a later task repair must not change that earlier event snapshot's result within the same tested range. Include all verdict inputs listed in Design and preserve the existing before..after event policy. Falsifiers: disconnect check_task_facts, remove the diagnostic parser arm, read today's task instead of the event bytes, or test only a helper. Current evidence: actual base command and source wiring; candidate/native sequence and laws result unverified.

**AC-4** — Reading cost and instruction ownership stay bounded. Repeat the fixed lifecycle recipes on exact base/candidate source and executed outputs, including the refusal, allocator output, existing Number guards reread and retry. Require normal-path counts unchanged, no added success/polling output and no workflow-budget change; explain every measured failure-path addition. Falsifiers: omit moved text or diagnostic consumer output, report only workflow.md's size, or silently add a universal ADR disposition field. Current evidence: base counts 6967/870/833/333/2408, actual fixture outputs and proposed 27-word error; candidate/recovery totals unverified. CI cost per PR was not measured; no CI change is in scope.

## Stage Report: ideation

- FAILED: A design for refusing an implementation dispatch for a task whose approved design or ruling calls for an ADR until ## Number guards reserves an ADR number, in kc-dev-flow-2/scripts/dispatch_records.py (check_task_facts) beside the existing number checks; the #740 (seed-check-requires-schema-fields) and #728 (codex-reader-same-head-unresolved) records replayed as refused, and current tasks that reserved their numbers passing
  Historical 09da6be7 / 4fb24769 task-and-record pairs both return 0 in 0.33.0 --names; PR 728 names no new ADR obligation. A raw refusal would require an unapproved declaration requirement or semantic inference. No candidate refusal claimed.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (seed-check-requires-alignment-result, captain-amendment-form-checked, adr-reserved-when-design-names-one, validation-rerun-waits-for-captain-ruling, gate-requires-recorded-reviews) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Batch overlap above names all thirteen tasks, minimum four files and conditional contract/budget files; closed/moved tasks are distinguished from active work.
- SKIPPED: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  No final mechanism/candidate exists pending the scope decision; lifecycle inventory above records unchanged base behavior and the exact future measurement scope, not invented numeric totals.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 through AC-4 give reproducible inputs, limits and falsifiers; one decision recommends narrowing the raw PR 728 refusal promise and explicitly states the missed-classification cost.
- DONE: AC-1 current-stage evidence
  Two original snapshots exercised, both base exit 0; candidate proof unverified, and adding intent to a fixture is explicitly forbidden as a raw-replay claim.
- DONE: AC-2 current-stage evidence
  ADR 0043 control returns 0; existing unrelated amendment/renumbering failures recorded separately; candidate corpus proof unverified.
- DONE: AC-3 current-stage evidence
  Source/caller inspection binds the existing --names seam and laws parser; native candidate proof unverified.
- DONE: AC-4 current-stage evidence
  Lifecycle measurement inputs specified; no candidate totals claimed and no CI change or measured cost per PR.

- DONE: Required design-surfaces invocation
  Supplied 0.33.0 design_surfaces.py check exits 0, 'design surfaces presentable'; this marker/AC check does not resolve the scope hold or prove an authored Mermaid, so no approval-gate readiness is claimed. git diff --check passes; prior task bytes/frontmatter are unchanged.

### Summary

Held: the assignment asks a structural check to reject an original record that never declares the new ADR obligation. FO must resolve the one scope/replay decision before the final design, numeric reading measurement and candidate refusal proof; this report does not authorize a new universal field, a prose classifier or revival of the closed ledger task. The original four checklist items are 2 DONE, 1 SKIPPED, 1 FAILED; current-stage evidence mappings are additional, not completion claims for future implementation.

## Stage Report: ideation

- DONE: Revise the design under the Captain's ideation-gate revise of 2026-10-29 (「照建議」; the asks are in the gate question): refuse only a design that names a docs/adr placeholder with no ADR reserved under ## Number guards; replay #740 as refused; drop the #728 replay; batch ruling A applies; update criteria and the stop condition to match
  Current PRFAQ/Design, AC-1 through AC-4 and Stop condition implement the accepted narrow scope; exact #740 released CLI exits 0, design predicate identifies the missing reservation, and candidate CLI refusal remains explicitly owed at implementation; #728 is removed, not relabelled as caught.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (seed-check-requires-alignment-result, captain-amendment-form-checked, adr-reserved-when-design-names-one, validation-rerun-waits-for-captain-ruling, gate-requires-recorded-reviews) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Five proposed files and all thirteen named tasks are mapped; order is adoption context, amendment parser, this repair, validation rerun; closed/moved tasks are not dependencies and no sibling was edited.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Executed shipped watcher fixtures and counted the declared instruction corpus: base 6967/870/833/333/2408; proposed normal path equal, new error 27 words plus 468-word existing recovery reread; candidate/allocator totals remain future proof, no CI cost measured.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 through AC-4 bind original bytes, compatibility, the caller/laws seam and lifecycle reading; no unresolved decision remains after the recorded revise; missed semantic omissions and failure-path reading are explicit costs.
- DONE: AC-1 current-stage evidence
  Original #740 task/record digests and CLI exit/stdout reproduced; deleting the proposed predicate would leave that baseline acceptance unchanged, so actual candidate refusal/recovery must still be proved and is not claimed here.
- DONE: AC-2 current-stage evidence
  Number parser, supported record paths and sibling contracts read; matrix and frozen corpus comparison unverified until implementation; historical/fenced examples and POC refusal are named false-positive falsifiers.
- DONE: AC-3 current-stage evidence
  Pre-build caller, immediate-spawn ownership and L2 closed diagnostic grammar read; actual base CLI exercised; candidate sequence/laws proof unverified, with disconnect/parser-arm/event-time mutations specified.
- DONE: AC-4 current-stage evidence
  Fixed watcher scenarios executed under provider stubs and instruction counts recomputed; candidate rerun must catch any normal-path increase or omitted refusal/allocator/retry text.
- DONE: Required design-surfaces invocation and state boundaries
  Supplied 0.33.0 design_surfaces.py check exits 0, 'design surfaces presentable'; git diff --check passes; frontmatter, original report and sibling files preserved; no product implementation, ADR reservation or gate mutation performed.

### Summary

Cycle 2 supersedes the earlier held report: the Captain's narrowed structural design is complete, with PRFAQ/Mermaid, four criteria, updated stop condition, all named overlaps and measured baseline reading. Source remains origin/main 5725d495bb83a17ec13616bb5421bf5ffdc71f70 / package 0.33.0; GitHub #740 read succeeded, while QNow was not freshly relocated and diagram rendering was not exercised. Candidate refusal, full compatibility and native orchestration remain implementation/validation evidence, not design-stage passes; Pilot scope and Captain gate authority remain unchanged.

## Stage Report: implementation

- SKIPPED: One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/spacedock-ensign/validation-rerun-waits-for-captain-ruling (b8a66e826c7524fa944a7165296acba94b3f5e13) implementing the approved design and acceptance criteria in the task file; the revised design approved at the ideation gate on 2026-10-29 (「進實作」): refuse only a design naming a docs/adr placeholder with no ADR reserved under ## Number guards; replay #740; no new ADR for this task; stacked on PR #750 (validation-rerun-waits-for-captain-ruling, itself on #749), all changing kc-dev-flow-2/scripts/dispatch_records.py, so write the PR text with base branch spacedock-ensign/validation-rerun-waits-for-captain-ruling; only the files the design names
  Draft creation is explicitly FO-owned in this dispatch; implementation 58c9d0f26c78b4b038668b7170389512d8e727e0 is pushed on the named base, changes the five approved files, and adds no ADR/version/workflow changes. PR text: /tmp/impl-adr-reserved-when-design-names-one-pr.md (Draft; base branch specified).
- SKIPPED: Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
  Local criteria and eleven mutations pass as detailed below; actual native worker.spawn is unavailable. Native build and immediate spawn recorder pass, but a launched model is not claimed; FO owns native-host confirmation.
- SKIPPED: kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0/scripts/adr_lint.py docs/adr --since <base> exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0/scripts/comment_ratio.py within its maximum; roborev evidence= line; push without force and without -u; PR body written for FO; FO reads CI on the PR head; CI cost measured or stated as not measured
  Required local checks pass and branch push succeeded without force/-u; RoboRev exits 3: incomplete: the roborev daemon is not running. FO must run RoboRev, open the Draft and read CI at 58c9d0f2. CI cost per PR not measured; CI files unchanged.
- DONE: Approved bounded implementation and exact artifact
  58c9d0f26c78b4b038668b7170389512d8e727e0 on spacedock-ensign/adr-reserved-when-design-names-one, base b8a66e826c7524fa944a7165296acba94b3f5e13; clean code tree, named-file commit and normal push completed.
- DONE: AC-1 raw replay and allocator recovery
  Raw #740 digests match; released 0.33.0 is exit 0/empty, candidate adds refusal. Real allocator recovery clears it; missing task ADR, migration-only and scope-only controls refuse. Stacked-base amendment-form error at task line 293 remains unchanged; full raw recovery is still red for that unrelated reason.
- DONE: AC-2 boundary matrix and pinned corpus comparison
  DesignAdrTests covers flat/folder, Pilot/Prod/POC, first/repeated/message, path/heading/list/table forms, fences/quotes, numeric citations, current Design and unchanged modes. 1,247 committed records compared on four pins in VALIDATION.md; one new refusal, this task's unquoted explanatory placeholder, follows the accepted structural boundary. No approved task prose was rewritten and no ADR was allocated for this task; FO must route correction of those examples before a later dispatch.
- DONE: AC-3 CLI caller and historical consumer within available host seam
  Actual checker refuses before any build call; actual installed Spacedock build succeeds after allocator recovery and next-call recorder is spawn. L2 reports violation rather than Cannot at flat/folder event snapshots, unchanged after later repair; range policy preserved. Native worker.spawn itself remains unverified.
- DONE: Acceptance falsifiers exercised with python3 -B and caches absent
  DesignAdrMutationTests runs eleven mutations: disable/disconnect predicate, accept scope-only/migration-only, include POC, skip continuation, classify quote/fence, retain first Design, remove diagnostic parser, read HEAD task. Each fails its named behavioral assertion; raw literals retain SHA-256 checks.
- DONE: AC-4 complete fixed lifecycle reading and recovery count
  Base/candidate executed totals equal 6967/870/833/333/2408; valid dispatch/retry adds zero output. New recovery is 27 diagnostic + 690 existing reread + 2 allocator + 0 retry = 719 words; design's 468 forecast omitted the separate 222-word Number guards section. Workflow stays 5754 words with no budget raise.
- DONE: Local tests and mandatory checks
  Dispatch 87, laws 59, watcher 129 and delivery gate 113 pass (388 total); repository lint-skills exits 0; installed design_surfaces, adr_lint (43 records) and number_guards exit 0 at 58c9d0f2. comment_ratio: code lines 583, comment lines 0, 0.0%, maximum 5% met; git diff --check passes.
- DONE: Affected-document dispositions
  doc_impact: kc-dev-flow-2/VALIDATION.md updated; docs/adr/0045-validation-reruns-require-a-later-recorded-captain-ruling.md unaffected: live validation-ruling predicate and names-only/non-git boundaries preserved by full dispatch/laws tests; learning.md unaffected: consumer/corpus/lifecycle practices were applied, no learning evaluation or rule change authorized.
- DONE: Evidence location and scope
  Shipped replay/matrix/mutation controls are in the approved tests; VALIDATION.md records corpus pins, counts, raw digests and limits. Additional local receipts/recipes: /tmp/impl-adr-reservation-evidence/{raw,corpus,reading,native}.json and corresponding .py files; these are bounded local observations, not hosted review or acceptance.

### Summary

Implemented and pushed the accepted structural refusal with existing numeric-parser recovery and event-snapshot diagnostic classification; 388 relevant tests and eleven fault mutations pass without a new ADR, workflow or CI change. FO must create the Draft from the supplied text, rerun RoboRev (daemon unavailable), read PR-head CI and confirm native spawning; this task's literal explanatory placeholders also need authorized correction before a future candidate-check dispatch, with no invented ADR obligation.


## Validation acceptance script — 2026-10-29

No graphical surface changed. Run these four steps, in order, in one fresh Bash shell (`bash --noprofile --norc`); they use a disposable local clone, the named code checkout and installed Codex package 0.33.0. This checks the CLI boundary, recovery, compatibility, eleven fault mutations, historical dispatch classification and ADR lint; it does not prove native worker spawning, hosted checks, acceptance or delivery. Expected duration: under five minutes.

1. Pin the candidate in a disposable clone.

```bash
set -euo pipefail
ADR_ACCEPT=$(mktemp -d /tmp/adr-751-acceptance.XXXXXX)
git clone --quiet --shared --no-checkout /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-adr-reserved-when-design-names-one "$ADR_ACCEPT"
git -C "$ADR_ACCEPT" checkout --quiet --detach 58c9d0f26c78b4b038668b7170389512d8e727e0
git -C "$ADR_ACCEPT" rev-parse HEAD
cd "$ADR_ACCEPT/kc-dev-flow-2/scripts"
```

Expected and observed: `58c9d0f26c78b4b038668b7170389512d8e727e0`; exit 0.

2. Exercise the accepted boundary and its falsifiers.

```bash
python3 -B -m unittest test_dispatch_records.DesignAdrTests test_dispatch_records.DesignAdrMutationTests test_laws_check.L2Test.test_missing_design_adr_is_an_event_violation_even_after_later_repair -v
cd "$ADR_ACCEPT"
```

Expected: eight tests `ok`, ending `OK`, exit 0. Observed: all eight `ok`, `Ran 8 tests in 35.821s`, `OK`; the fault tests pass only when their mutated checker fails the behavioral assertion.

3. Check decision records against the stacked base.

```bash
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0/scripts/adr_lint.py docs/adr --since b8a66e826c7524fa944a7165296acba94b3f5e13
cd /tmp
```

Expected and observed: `43 ADR file(s) checked, 0 legacy`; exit 0.

4. Remove only this acceptance clone.

```bash
python3 -c 'import shutil,sys; shutil.rmtree(sys.argv[1]); print("Acceptance clone removed")' "$ADR_ACCEPT"
```

Expected and observed: `Acceptance clone removed`; exit 0.

Validator ran exactly the concatenated commands above with `bash --noprofile --norc /tmp/validation-adr-751-evidence/acceptance.sh`; combined exit 0. Full observed output is `/tmp/validation-adr-751-evidence/acceptance.out`.

## Stage Report: validation

- DONE: Independent verdict on PR #751 head 58c9d0f2 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  REJECTED at 58c9d0f26c78b4b038668b7170389512d8e727e0 versus stacked base b8a66e826c7524fa944a7165296acba94b3f5e13: AC-1/2/4 pass within the accepted structural boundary; AC-3 lacks native spawn proof. Independent reruns and limits follow; no product repair performed.
- DONE: The revised design approved on 2026-10-29 (「進實作」): refuse only a design naming a docs/adr placeholder with no ADR reserved under ## Number guards, replay #740; PR #751 is stacked on #750 (base spacedock-ensign/validation-rerun-waits-for-captain-ruling at b8a66e826), so judge the diff against that base; the implementation reports native spawn not confirmed and this task's own explanatory placeholders needing correction before a future candidate-check dispatch; RoboRev evidence=roborev:1327 clean on 58c9d0f26, run by FO
  Five-file diff matches the approved scope; #728 remains excluded, first-record scope copying is unchanged, and the existing numeric parser is reused. Native-spawn limit remains open; this task's explanatory placeholders reproduce the single corpus change. RoboRev roborev:1327 clean and four green PR checks are FO-supplied evidence at this head, not independently fetched.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  Four exact steps and observed output are above; fresh Bash exits 0 in under five minutes. Installed Codex 0.33.0 adr_lint.py docs/adr --since b8a66e826c7524fa944a7165296acba94b3f5e13 exits 0 (43 records, 0 legacy); no ADR number is reserved or newly named by this task's implementation.
- DONE: AC-1 — raw refusal and allocator recovery
  Git-exported #740 bytes at 09da6be7ad5aaf687ea3f80e9553f3efb525cc17 match both published SHA-256 values and the shipped literals; released checker exits 0/empty, stacked base exits 1 for amendment line 293, candidate preserves that error and adds the 27-word refusal. Allocator recovery removes only the new refusal; missing task ADR, scope-only and migration-only controls restore it; disabling/disconnecting the predicate fails the raw test.
- DONE: AC-2 — supported boundary and committed corpus
  Replayed DesignAdrTests plus the four pinned corpora in candidate VALIDATION.md: 564 + 296 + 249 + 138 = 1,247 records, exactly one changed diagnostic (this task's implementation-1.md). Flat/folder, profiles, continuation/message, last Design, quotes/fences, paths and unchanged modes pass; wrong POC, continuation, quote/fence and first-Design mutations fail, while existing amendment/renumber errors stay identical.
- DONE: AC-3 — actual CLI refusal, real build and event-time consumer
  Candidate CLI exits 1 with zero build calls; actual allocator prints ADR: 0001, corrected CLI exits 0/empty and installed Spacedock builds a Codex envelope, followed immediately in the probe by a spawn recorder. Historical dispatch rule L2 judges flat/folder event bytes as a violation, unchanged after later repair within the same range; removing its diagnostic parser or reading HEAD instead of event bytes fails the control.
- FAILED: AC-3 — native worker spawning after successful build
  This host exposes no native worker.spawn; the executed probe records a call rather than launching a worker. Neither the real envelope, model-free tests, supplied CI nor this validation dispatch closes that required operational seam; F1 returns the obligation to FO.
- DONE: AC-4 — complete lifecycle reading and falsifier
  Re-executed base/candidate lifecycle recipes: 6967/870/833/333/2408 words on both, outputs 37/37/0/5/90, workflow 5754 unchanged; failure recovery is 27 diagnostic + 690 existing reread (222 + 468) + 2 allocator + 0 retry = 719. Independent success-banner mutation fails the existing CLI test with AssertionError, exit 1; no universal field, workflow-budget or CI change, and CI cost per PR remains unmeasured.
- DONE: Required checks, affected documents and necessity
  Dispatch 87, laws 59, watcher 129, delivery gate 113 pass (388); eleven shipped fault mutations plus the success-banner fault fail as intended. Repo lint, installed design_surfaces, four-record dispatch completeness, ADR lint, explicit-stacked-base number guards and diff --check pass; comment_ratio reports 583 code lines, 0 comments, 0.0% <= 5%, and added docstrings reviewed. Runtime predicate, consumer parser, proof tests and evidence doc each map to the goal or a falsifier; no extra implementation surface remains.
- DONE: Document dispositions and base-sensitive limit
  doc_impact rerun matches implementation: VALIDATION.md updated; ADR 0045 unaffected (full ruling/history controls pass); learning.md unaffected (consumer, corpus and lifecycle practices applied). Default number_guards against README origin/main exits 1 for sibling ADR 0045; explicit --base b8a66e826c7524fa944a7165296acba94b3f5e13 exits 0, so the stacked diff is clean but default trunk-based checking is not yet green.
- DONE: Evidence and immutable candidate
  Rerun recipes/results live at /tmp/validation-adr-751-evidence/{raw,corpus,reading,native}.{py,json}; raw source bytes independently compared with state Git history. Detached candidate remained clean at the exact head; local acceptance clone removed. No Git config write, PR mutation, push or candidate change; state report only.

### Findings

- F1 Needs decision: AC-3's native build/immediate-worker-start obligation remains unverified. User/workflow: FO dispatching a corrected Pilot/Prod implementation; observable harm: none demonstrated, but a recorder cannot show that a worker actually starts; boundary: value-ac[AC-3] requires the real caller/recovery sequence; trigger evidence: native.json has a real build envelope and `worker.spawn recorder`, no launched worker. Recommend FO obtain the missing host receipt before acceptance; any narrower acceptance requires the Captain's ruling, not validator substitution.
- F2 Deferred risk: a future implementation dispatch of this unchanged task using the candidate checker will refuse its own unquoted explanatory paths. User/workflow: FO re-dispatching this task; harm: future dispatch blocked until authorized example correction; boundary: captain-ruling[2026-10-29] accepts literal active-design matching and requires prior reports/obligations preserved; trigger evidence: only changed record in the fixed corpus, baseline exit 0 versus candidate exit 1. It becomes Material if this blocks a required current dispatch; keep the known correction with FO, do not invent an ADR or silently rewrite the accepted design.

### Summary

REJECTED for head 58c9d0f26c78b4b038668b7170389512d8e727e0: the structural refusal, recovery, compatibility, history consumer and reading budget are independently reproduced, with 388 tests, twelve fault controls and the fresh-shell acceptance script passing. Goal sufficiency remains unproved at native worker startup; minimal necessity is satisfied by the five-file stacked diff, and no demonstrated code defect calls for repair. FO retains the host-evidence obligation, authorized treatment of this task's explanatory examples, validation disposition and Captain delivery decision; provider checks and RoboRev are explicitly supplied evidence.
