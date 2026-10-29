---
title: An implementation dispatch for a task whose design calls for an ADR is refused until an ADR number is reserved in ## Number guards
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
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

- The check refuses each bite in the replay and passes every current task file that follows the README.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Result: aligned at backlog: the Captain 「同意這些內容」 (chat, 2026-10-29) to FO's batch-10 backlog sitting, which asked 「決定：六張全照建議（五張進設計，被取代條件那張先留在待辦）？要改哪張直接說。」, approved the outcome and bounds in this file. Where the check runs is a package design choice ideation proposes and the ideation gate rules.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-29 — batch-10 review before the joint ideation sitting: approve, revise or cut each task, the Captain's decisions, overlap and order

## Ideation findings — held for one scope decision

The assigned positive replay cannot yet be promised: the two historical inputs have different missing facts. No product file, branch, implementation candidate, ADR number or sibling task was changed. Profile remains Pilot. This is a handback, not a completed design or a recommendation to present the ideation approval gate.

### Chain and existing seam

1. Spacedock 0.27.3's own `skills/first-officer/references/fo-dispatch-core.md` owns build, spawn and state transitions; its dispatch sequence has no package ADR classifier. Its instructions require the worker spawn to be the next host action after a successful build. The package check must therefore remain before build, not be inserted between build and spawn. This is a documented procedural check, not an unskippable Spacedock interception.
2. After successful `git fetch origin`, source is `5725d495bb83a17ec13616bb5421bf5ffdc71f70`, manifest 0.33.0. `dispatch_records.py`, `number_guards.py` and `laws_check.py` in the dispatched Codex 0.33.0 package are byte-identical to that source. `--names` invokes `check_task_facts`; `--newest` only invokes `check_names`, and the folder mode is a different completeness check. In `check_task_facts`, only `implementation-1.md` compares already-reserved ADR/Migration numbers with scope notes. An empty reservation set makes that comparison vacuously pass. `number_guards.task_facts` reads numeric lines under `## Number guards`; it does not identify an enduring ruling or an obligation to create a new ADR.
3. Consumer: `laws_check.py:l2_dispatch_record_complete` explicitly parses the `--names` diagnostic vocabulary. Any added diagnostic needs its parser and tests changed in the same PR; otherwise an intended violation becomes an unjudgeable run. The existing laws snapshots must be judged at their recorded event, not silently against today's edited task.
4. Siblings were read without edits or fetches. Relay local clone HEAD `a378b62f423d3510ecda60a80c2fdb132f78cf6e` and QNow local clone HEAD `278f79ca3eb03a8c1286817f542c4ec4b744bfed` have the same prose reservation obligation; QNow also names the pre-build `--names` command. Web local clone HEAD `1f8c4b25268dc05ac77be5cdf33148bd6806dba9` has only `docs/dev/README.md` in the inspected docs tree, a native Spacedock workflow without these dev2 checks. These are local snapshots, not claims about the latest hosted adopter state. No adopter workaround supplies the missing semantic classification.

This is a repair of the named `check_task_facts` seam, with an unresolved input contract, not a reason to build another checker. The source search covered the dispatch checker, number parser, caller and workflow; it does not prove what humans read in other sessions.

### Historical replay actually run

The following state commits are the commits that added the first implementation record, before later reservations or reports repaired the visible task:

| Case | State commit | Task SHA-256 | `--names` result |
| --- | --- | --- | --- |
| seed-check-requires-schema-fields, PR 740 | `09da6be7ad5aaf687ea3f80e9553f3efb525cc17` | `9cdb2a04175c91eb996fb8c314067cfd6fe5fe4636ef399b97fc0effa4288406` | exit 0, empty stdout, no reserved ADR |
| codex-reader-same-head-unresolved, PR 728 | `4fb24769b7e81bc1e87b07ae4a461d402a8a72d4` | `93cb1bbbde35233789280b1272a302f17c69d32f80e2cac74882d9a915edd43d` | exit 0, empty stdout, no reserved ADR |

Reproduce with the dispatched package: for each row use `git -C <state> show <commit>:<slug>.md` and `git -C <state> show <commit>:<slug>/dispatch/implementation-1.md` to materialize those two files in a temporary directory, preserving that relative layout; run `python3 -B <package>/scripts/dispatch_records.py --names <temporary>/<slug>/dispatch/implementation-1.md`. The two snapshots were exercised with `dispatch_records.main(['--names', record])`, the CLI's entry function, stdout captured and the return value inspected. No proposed refusal was implemented or passed off as an observed candidate result.

PR 740's approved design explicitly lists `docs/adr/<FO-reserved-number>-seed-admission-enforces-required-fields.md` as a deliverable. PR 728's design lists only its Codex reader and test file as changed files. Its D1 resolves whether a GitHub resolved-thread mark clears a finding, cites existing ADRs 0004 and 0013 as precedents, but names no new ADR deliverable or reservation. Its later implementation report even says it skipped the ADR because D1 was settled at the gate. The enduring-ruling classification is a human conclusion; recognizing an `ADR` citation would confuse an existing precedent with a new deliverable.

Positive control run: current `_archive/batch-reaches-each-gate-together.md` reserves ADR 0043; `check_task_facts` across its three implementation records returns 0 with empty stdout. Current ops-inbox reserves 0040 but its old first record still carries an earlier number and is already refused. Current seed-check's original record is already refused after its later task reservation. Journey-server records already produce amendment diagnostics. These existing failures must remain visible in a base-versus-candidate comparison; they are not evidence that every currently reserved task is globally green.

Provider access: `gh pr view 740 --repo iamcxa/kc-claude-plugins --json number,state,mergeCommit` succeeded: MERGED at `60896216d1c4ca842327e6a5beb2191a64993657`. No GitHub API access failure was observed. Historical task/dispatch facts above come from Git, not from this provider result.

### Rulings that constrain the proposal

Read Accepted ADRs 0002 (reservation ownership), 0025 (land or release a reservation), 0027 (structured FO-write checks) and 0020 (workflow word budget) at the pinned source. ADR 0027 records the Captain's rejection of the four-verb phrase check: matching words could not stop the error class. The state `Override:` search showed no authorization to substitute an arbitrary ADR prose classifier here.

The sibling `adr-required-statement` is explicitly closed by the Captain's 2026-10-20 ruling despite stale validation frontmatter. Its unshipped Captain-rulings ledger must not be imported as an available mechanism. `comment-check-reaches-delivery-gate` is also explicitly closed. `adr-silent-undo-probe` was moved to the POC workflow by amendment; its old copy is not an active implementation dependency.

## Unresolved decision for the Captain

**May PR 728 remain an explicit uncovered counterexample rather than a required raw-record refusal in this bounded repair?** Recommendation: yes; keep the change about an explicitly declared new ADR obligation, and have FO return a narrowed replay criterion for approval before design resumes. That avoids inferring intent from arbitrary prose or silently adding a mandatory yes/none field to every implementation dispatch. What gets worse: a missed human classification like PR 728 can still escape; this repair would not solve that broader omission.

If the required outcome remains refusal of both original inputs, the prerequisite is approval of a new structured ADR-disposition requirement at implementation dispatch, including its treatment of old legitimate no-ADR tasks, repeated dispatches and POC. Such a requirement may refuse both originals for a missing declaration, but it does not establish that a declared `none` is truthful. It changes the current promise to pass every task already following the README and must be designed and measured as that scope change. No such approval is inferred here, and no new field grammar is imposed by this report.

## Design boundary pending that decision

**Proposition:** the existing pre-build `dispatch_records.py --names` check should tell FO about a missing ADR reservation before a worker is spawned. FO then reserves using the existing command, records the number under `## Number guards`, copies it into the dispatch scope notes, reruns the check and uses the ordinary Spacedock build/spawn sequence.

**Why not choose a regex now?** Existing-record citations, declined alternatives, historical reports, fenced examples, negative statements and superseded requirements are all possible false positives. A bounded structured declaration can be tested, but which declarations are required is the unresolved scope decision. No semantic classifier, automatic reservation, gate approval, history rewrite, backfill, new script or CI trigger is proposed.

**Integration if resumed:** keep the refusal beside existing number checks in `check_task_facts`; explicitly cover resumed `implementation-N.md` and `implementation-N-message-M.md` records if an obligation arises after the first dispatch. Preserve existing numeric allocation/collision rules and migration behavior. Keep success silent and emit a path-and-line diagnostic with a repair action on failure. Update the laws consumer in the same change. A folder-mode, newest-mode or native Spacedock claim needs its own exercised call path; none is implied by a unit helper passing.

No final PRFAQ/Mermaid gate artifact was produced because selecting the branch condition would decide the missing scope. The applicable ideation/ensign rule is to return unclear requirements to FO rather than guess.

### Words FO reads at each lifecycle moment

| Moment | Before | After this held ideation | Candidate evidence still owed |
| --- | --- | --- | --- |
| Startup/resume | Current workflow and loaded mod passages | Identical; no package text changed | Count all added declaration instructions and any on-touch migration wording, not just workflow.md |
| Before valid implementation dispatch | Task design, Number guards, saved record and existing checks | Identical | Actual candidate stdout and any required new statement |
| Refused implementation dispatch | Both original replays print 0 diagnostic words | Still 0; no candidate exists | Exact diagnostic plus recovery instruction and reread passages |
| Idle on an open PR | Existing watcher/mod passages and outputs | Identical | Verify no new poll/output is introduced |
| Idle on a merged PR | Existing merged-state output and mod | Identical | Verify unchanged, or count changed lines |
| After archive | Existing archive/learn passages and output | Identical | Verify unchanged, including diagnostic consumers |
| Merge ask | Existing delivery instructions and printed verdict | Identical | Verify number-check and delivery messages remain unchanged |

This is a change inventory, not a completed numeric before/after candidate measurement. Absolute lifecycle totals and a candidate delta are deliberately unclaimed. On resume, count exact passages plus exercised outputs with `len(text.split())` on the same fixed scenarios and pinned base/candidate; include the failure/retry path. Any positive workflow-budget step requires the ADR 0020 ruling and its load moment. No CI change was made; cost per PR was not measured.

### Batch overlap

Minimum proposed runtime/test files, after the scope decision: `kc-dev-flow-2/scripts/dispatch_records.py`, `scripts/test_dispatch_records.py`, `scripts/laws_check.py`, `scripts/test_laws_check.py`. A new declaration contract would additionally affect `references/sd/workflow.md`, its budget in `scripts/lint-skills.py`, workflow/POC pins in `scripts/test_sd_dispatch.py`, and whichever existing authoring reference owns the declaration. Those conditional files are not approved scope. `number_guards.py` need not change for the established numeric reservation; any parser change needs a separately justified reason. No ADR number is assigned; a newly approved enduring rule would need an unnumbered ADR draft before FO reserves it, sharing `docs/adr/` with other tasks.

| Named task | Same file/check or namespace |
| --- | --- |
| seed-check-requires-alignment-result — require alignment result at seed | design_surfaces.py and tests only; its unchanged predicate is consumed by dispatch_records.py; rerun dispatch regressions |
| captain-amendment-form-checked — validate amendment structure/history | Direct overlap in dispatch_records.py, its tests, laws_check.py and its tests; shared task parsing |
| adr-reserved-when-design-names-one — this task | Files above; owns only this entity body/report in this dispatch |
| validation-rerun-waits-for-captain-ruling — hold premature reruns | Direct overlap in all four runtime/test files, event snapshot handling; possible ADR namespace |
| gate-requires-recorded-reviews — require review records before gate | Its recorded scope names delivery_gate.py, role_triggers.py and gate preparation; no established direct file overlap; recheck completed design |
| adoption-asks-which-extensions — read dispatch-time extension list | dispatch_records.py, test_dispatch_records.py, test_laws_check.py; adjacent historical context and number_guards.frontmatter refactor |
| adr-required-statement — old ADR ledger proposal | Closed; historical workflow/parser/ADR overlap only; do not revive its branch or reuse its ledger |
| adr-silent-undo-probe — measure reversal of a ruling | Moved to POC; no runtime file overlap in the old task |
| comment-check-reaches-delivery-gate — bind comment proof to delivery | Closed; its historical delivery/test/validation edits do not overlap the minimum four files |
| journey-canvas-hosted-poc — hosted canvas experiment | kc-journey-map hosting scope; no dispatch-checker overlap established |
| journey-server-host-pilot — private hosted journey server | kc-journey-map server/docs; no dispatch-checker overlap; shared ADR number namespace and real corpus control |
| ops-inbox-r1-setup-and-isolation — isolate operations intake | kc-ops-inbox files; no dispatch-checker overlap; shared ADR namespace, existing renumbered historical record |
| pr-review-lite-value-pilot — bounded review comparison | kc-pr-flow review runtime and journey documents; no dispatch-checker overlap established |

Recommended order: FO resolves the single scope/replay decision first; coordinate adoption's historical context and the amendment parser before serially integrating this task and validation-rerun. Rerun combined dispatch/laws tests after each rebase. Do not wait on the explicitly closed or unrelated product tasks; do not message or edit their sessions. Pilot boundary: no production obligations or implementation authority were added.

## Acceptance criteria

These are the proof obligations to settle when resuming; they do not amend the accepted Scope or Stop condition.

**AC-1 — Historical claims match original bytes.** Replay the two pinned task/dispatch pairs above with base and candidate, preserving layout and digests; print each exit and diagnostic. A modified fixture containing an added ADR-intent line must be labeled a normalized fixture, never an original replay. Falsifier: remove that added line or use the original PR 728 snapshot; a claimed raw-record refusal must still occur. Current evidence: both base runs return 0; candidate refusal is unverified and blocked by the scope decision.

**AC-2 — Existing valid reservations and unrelated tasks retain their verdicts.** At fixed state/adopter commits compare base/candidate exits and messages for every committed dispatch record and task, including archive and folder-form tasks, in the affected `--names` mode and the unaffected folder/newest/coverage modes. Explain each changed verdict; keep baseline amendment/renumbering failures distinct. Test missing, fenced, quoted, negative, existing-ADR-reference and later-required-ADR cases plus recorded release of an obligation. Falsifiers: cite an existing ADR to create a false refusal, delete a required reservation without refusal, or classify a later task edit as a historical violation. Current evidence: ADR 0043's three records pass check_task_facts; the broader candidate comparison is unverified.

**AC-3 — Refusal reaches the existing seam and consumer.** Exercise the actual `--names` command before a scratch dispatch build; show nonzero stops the procedural sequence and a correctly reserved/repeated line permits it. Feed the diagnostic through laws_check's event snapshot path and assert violation rather than Cannot, without changing `--newest` into an unannounced enforcement mode. Falsifiers: disconnect check_task_facts, remove consumer classification, or only test a helper without the CLI path. Current evidence: source/callers inspected; candidate/native behavior unverified.

**AC-4 — Reading cost and retained instructions are explicit.** Measure the fixed lifecycle scenarios above on exact base/candidate text and exercised stdout with the same counting method, include every newly required declaration and retry, and check workflow budget equality and any Captain-backed increase. Falsifiers: move text into a mod/output and exclude it, count only workflow.md, or silently reopen the closed ledger proposal. Current evidence: no source wording changed; numeric candidate comparison unverified.

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
