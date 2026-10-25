---
title: delivery_gate.py reads a folder task's index.md
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: done
gates:
    version: 1
    records:
        - id: gate:delivery-gate-reads-folder-tasks:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:delivery-gate-reads-folder-tasks-backlog-1
              briefing:
                id: briefing:delivery-gate-reads-folder-tasks:backlog:attempt-1:revision-1
                digest: sha256:04ce3fbc310de40dd326f41fe75d711d523c543fe4e2052007e5d609f2ff37cb
                room-ref: ./delivery-gate-reads-folder-tasks/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-gate-reads-folder-tasks:backlog:1
                briefing: briefing:delivery-gate-reads-folder-tasks:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-25T14:15:31.710779Z"
                decision: approve
                reason: Captain 「全准」 (chat, 2026-10-25) answering the batch-6 backlog sitting, which listed this task's backlog briefing-1 question
              application:
                target-stage: ideation
                state: consumed
        - id: gate:delivery-gate-reads-folder-tasks:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:delivery-gate-reads-folder-tasks-ideation-1
              briefing:
                id: briefing:delivery-gate-reads-folder-tasks:ideation:attempt-1:revision-1
                digest: sha256:3d1a40d1ac68f1d2d98a903b5e1d53c171ef72f2b3974a0411d259297cd09029
                room-ref: ./delivery-gate-reads-folder-tasks/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-gate-reads-folder-tasks:ideation:1
                briefing: briefing:delivery-gate-reads-folder-tasks:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-25T15:10:07.08743Z"
                decision: approve
                reason: Captain 「全准」 (chat, 2026-10-25) answering the batch-6 ideation sitting, which listed this task's ideation briefing-1 question with its decisions as recommended
              application:
                target-stage: implementation
                state: consumed
        - id: gate:delivery-gate-reads-folder-tasks:validation
          stage: validation
          attempts:
            - id: gate-attempt:delivery-gate-reads-folder-tasks-validation-1
              briefing:
                id: briefing:delivery-gate-reads-folder-tasks:validation:attempt-1:revision-1
                digest: sha256:e99dbb184d7ff1869f1324af5dc45559671dc68fa7a07d5b4071076695f71333
                room-ref: ./delivery-gate-reads-folder-tasks/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-gate-reads-folder-tasks:validation:1
                briefing: briefing:delivery-gate-reads-folder-tasks:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-25T17:48:13.634592Z"
                decision: approve
                reason: 'Captain 「照建議」 (chat, 2026-10-26) answering the batch-6 merge sitting, which listed this task''s validation briefing-1 question (merge #720 at 1c480fecf7d84e7bb4a15483fb8b3bc808dab630)'
              application:
                target-stage: done
                state: consumed
started: 2026-10-25T15:11:06Z
worktree: .worktrees/spacedock-ensign-delivery-gate-reads-folder-tasks
pr: pr-merge:720
verdict: PASSED
completed: 2026-10-25T18:01:58Z
archived: 2026-10-25T18:01:58Z
---

## Scope

- Source: FO, 2026-10-23, at the release-acceptance merge ask (PR #709). `delivery_gate.py check <task>/index.md` derives the dispatch folder by stripping `.md`, so it looks in `<task>/index/dispatch` and exits 2 ("no latest validation dispatch record"); passing the folder exits 2 ("Is a directory"). FO ran the check through a temporary `<name>.md` copy beside a symlink to the real folder; the record landed in the real `merge/ask-1.json`.
- Outcome: `delivery_gate.py check` accepts a folder task (its `index.md` or the folder) and reads `<task>/dispatch`, with a test.
- Upstream first: none checked yet; check whether other package scripts share the same path derivation before fixing one.
- Non-goals: other scripts' folder support unless they share the helper.
- Batch 6 (2026-10-25): the Captain 「可以」 (chat, 2026-10-25), answering 「需要你決定：這份第 6 批的清單可以嗎？」 about FO's batch-6 list, which placed this task third, after fo-written-lines-checked-before-dispatch (same script), and folded into it merge-check-reads-two-pr-tasks (whether a task may deliver through two PRs stays the Captain's at ideation).

## FO alignment

Alignment: needed at ideation: whether a task may deliver through two PRs (folded merge-check-reads-two-pr-tasks) is the Captain's.
Result: aligned 2026-10-25 at the ideation gate by the Captain's 「全准」 to the batch-6 ideation sitting, which put this task's decisions with recommendations.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Design

Ideation of 2026-10-25 against origin/main d496ac3d (`kc-dev-flow-2/scripts` is byte-identical at ac67eb0a, the 0.30.0 sync; the dispatch said 0.28.0 and the package is 0.29.0). Profile: pilot. The Scope above is untouched. This design has two parts: Part 1 (folder tasks, no Captain decision needed) and Part 2 (a task that delivers through two PRs, held on Decision D1).

### PRFAQ

**Press line.** FO's merge-ask check reads a folder-form task (`<task>/index.md`) the way it reads a flat one, and, if the Captain accepts D1, a task that delivers through two PRs can get an ask for the PR that does not carry the task's reserved ADR.

**Who uses it, and what breaks without it.** FO, at the merge ask it already runs. Without Part 1, `check <task>/index.md` looks for records in `<task>/index/dispatch`, cannot find the README, and exits 2; FO worked around it for release-acceptance (#709) with a temporary copy beside a symlink. The live folder task journey-server-host-pilot reaches its ask next. Without Part 2, new-work-starts-from-a-story-map (#704 and #705) got no ask for #704 and the check saved no record for it; the Captain merged #704 himself after FO asked in chat.

**FAQ.**
- Is this one script? No. The same `.with_suffix("")` derivation sits in four places (table below); the fix reuses `task_folder()` that `design_surfaces.py` already exports and `delivery_gate.py` already imports from.
- What does a flat one-PR task see? The same lines in the same order (AC-4). No README, skill, reference or mod text changes (AC-8).
- Why must a sibling PR's head be a dispatched `Candidate:`? Otherwise the ADR file is read at a head nobody validated.
- What does Spacedock do with two PRs? Nothing: `pr:` is one string and `pr-merge:N` one sentinel (`docs/schema/entity.mdschema.yml`, `internal/status/merge.go`, Spacedock 0.27.3), so the second PR's merge is outside Spacedock tracking either way. It has a `blocked-on` field for task order, used under option B of D1.

```mermaid
flowchart TD
  A[FO runs delivery_gate.py check on a task path] --> B{argument is a folder?}
  B -- yes --> C[use folder/index.md; no index.md is exit 2 naming the file]
  B -- no --> D[use the file as given]
  C --> E[task_folder: index.md gives its own folder, x.md gives the x folder]
  D --> E
  E --> F[read dispatch records, README above the state checkout, owed role calls by folder name, save merge record in that folder]
  F --> G{reserved ADR missing at this PR head?}
  G -- no --> H[go on to the other checks]
  G -- yes, --sibling-pr given --> I{sibling not closed, head is a dispatched Candidate, file at that head?}
  G -- yes, no flag --> J[hold: existing line, plus one next line naming --sibling-pr]
  I -- yes --> K[pass; print a sibling: line; record it]
  I -- no --> L[hold: named sibling problem]
  H --> M{any other problem?}
  K --> M
  M -- yes --> N[exit 1 or 2, no record]
  M -- no --> O[exit 0, record saved, ASK line]
```

### Existing-code check (chain order)

- Spacedock 0.27.3: entity forms are `<slug>.md` or `<slug>/index.md` (`docs/schema/entity.mdschema.yml` `filename_pattern`; `spacedock new --folder`); `gate prepare` and `gate record` need the folder form where the README declares `entity-form: folder`. This workflow's README declares none, so both forms stay legal here, and folder tasks will grow. `pr` is a single string. Nothing upstream reads a dispatch folder or a reserved ADR.
- kc-dev-flow-2: `design_surfaces.task_folder` (`path.parent if path.name == "index.md" else path.parent / path.stem`) is the existing helper; `validation_security.check_task` carries an inline copy with a mutation test that pins its source text, so it stays. `role_triggers.read_task`, `pr_watch` and `replay_dispatch` already try both forms.
- Adopters, read-only 2026-10-25: relay beirut-dev2 88 task files, 0 folder-form; web dev2-fo 47, 0; qnow not read. Here: 3 folder tasks of 141 task files (`_archive/release-acceptance`, `_archive/kc-decision-log-p1`, live `journey-server-host-pilot`); 1 of the 25 tasks with saved ask records is folder-form.

| Script | Site | Folder form today (probe on the d496ac3d scripts) | This design |
| --- | --- | --- | --- |
| `delivery_gate.py` | `dispatched_candidates`, `write_record`, the hold text, `find_readme`, `owed_role_calls` and its two messages | `check x/index.md`: README not found, records read in `x/index/dispatch`, exit 2; `check x`: "Is a directory", exit 2; the role call reads the right file by accident and names the task `index` | `task_folder` at each site; a folder argument becomes `<folder>/index.md` |
| `dispatch_records.py` | `main` (`task.with_suffix("")`), `check_task_facts` (`folder.parent / f"{folder.name}.md"`) | `index.md` argument: "no dispatch records"; `--names` on a folder task prints 0 reserved-line lines where the flat task prints 1: the check is silently off | same change, recommended inclusion (D2) |
| `validation_security.py` | `main` calls `dispatched_candidates`; `check_task` has the inline rule | right once `dispatched_candidates` is right | none |
| `design_surfaces.py`, `pr_watch.py`, `replay_dispatch.py`, `role_triggers.py` | own derivation | handle both forms | none |
| `decision_ledger.py` | `state.glob("*.md")` | folder tasks absent: 0 of 231 ledger rows come from release-acceptance (run 2026-10-25 on this state) | not here: Follow-up proposal |

### Measured today (2026-10-25)

- Fixture reproduction (`git init` state checkout, README with `trunk:`, one flat and one folder task, stub `gh`): the folder task prints three false lines, 15 + 13 + 17 = 45 words, where the flat task prints none. With the prototype the folder task, by `index.md` and by folder, prints the same lines as the flat one.
- Real-data replay of the two-PR bite (read-only `gh`; archived task copied to a temp directory; the archived `validation-4.md` names only #705's head, so one `Candidate:` line for #704's head f0d3f442 was added to the copy, the only edit): the origin/main script prints "reserved ADR 0029 has no docs/adr/0029-*.md at PR head f0d3f442d5e6" and a `next:` line; the prototype with `--sibling-pr iamcxa/kc-claude-plugins#705` prints neither (its other lines are replay artefacts: both PRs are merged, the copy is no git work tree). `gh pr view 705 --json headRefOid,state` returns `MERGED` and head 32ad029f, and the ADR directory at that head lists 0029.
- Suites, seven modules (`test_delivery_gate test_dispatch_records test_validation_security test_pr_watch test_role_triggers test_design_surfaces test_sd_dispatch`) from a `git archive` of origin/main: 444 tests OK; with the prototype 454 OK (new: 5 + 3 in `test_delivery_gate.py`, 2 in `test_dispatch_records.py`).
- Mutants (`ideation/mutate.py <tree with the prototype applied>`): 11 source mutations, each killed by at least one new test (the script runs only the new test classes); the first run of "README from the old parents" survived, and `test_the_readme_above_a_split_root_state_checkout_is_found_for_either_form` was added to kill it.

### Mechanism

1. `delivery_gate.py`: `from design_surfaces import FM_PROFILE, task_folder`; every `task.with_suffix("")` and `task.stem` becomes `task_folder(task)` or its `.name`; `find_readme` starts from `task_folder(task).parent` (the state checkout) and its parent; `owed_role_calls` passes `role_triggers.py` the folder's parent and name; in `check`, a directory argument becomes `<dir>/index.md` (a missing file is then the existing "cannot read input" exit 2).
2. `dispatch_records.py` (D2): `main` uses `task_folder(task)` for a `.md` argument; `check_task_facts` takes the task file as `<folder>/index.md` when it exists, else the flat sibling.
3. Part 2 (D1 = A): `check` gains repeatable `--sibling-pr owner/repo#N`, read only when a reserved ADR is missing at this head. Per sibling, `gh pr view --json headRefOid,state`: a CLOSED sibling holds, a head that is not a `Candidate:` line of the newest validation record holds, otherwise `adr_names` reads the ADR directory at that head. A number found there passes, prints `sibling: reserved ADR NNNN is at <pr> head <12>, a dispatched candidate of this task`, and adds a `siblings` key to the saved record. The existing hold line stays word for word; one `next:` line names the flag.
4. Prototype, not the deliverable: `delivery-gate-reads-folder-tasks/ideation/prototype.diff` in the state checkout (+49/-16 in `delivery_gate.py`, +3/-3 in `dispatch_records.py`, 94 test lines). Reproduce: `git archive d496ac3d kc-dev-flow-2 | tar -x -C <dir>`; `cd <dir> && patch -p1 < prototype.diff`; in `<dir>/kc-dev-flow-2/scripts` run `python3 -B -m unittest test_delivery_gate test_dispatch_records`.

### Past rulings

`git -C <state> grep -n 'Override:'` has no hit on a two-PR or folder-task question. ADR 0025 D2 is the bearing ruling for Part 2: "a reserved ADR with no file at the PR head holds the merge ask; FO lands the file or deletes the line", chosen over a written `parked` form (README words, a form the observer must read). Part 2 departs from the literal sentence only by letting the file be at a named sibling head the validator listed; it adds no README words and no parsed form. If D1 = A the departure is recorded in an ADR (no number; FO reserves it at implementation dispatch) rather than assumed.

### Limits

- Part 2 proves the ADR file exists at the sibling's validated head when the check runs. It does not prove the sibling merges; an ADR-carrying PR merged last is the safe order (story-map's was), the reverse order is not checked.
- Every validation record of a two-PR task must carry one `Candidate:` line per PR head. `dispatched_candidates` reads only the newest record: the archived `validation-3.md` listed both heads, `validation-4.md` (a #705 recheck) listed one, so after it #704's head would hold as "differs from dispatched candidate". The hold is the safe failure; FO writes the lines by hand.
- A flat task's companion folder passed as the argument gives "cannot read input: …/index.md". Backlog task design-surfaces-task-dir-crash decides the same resolution rule for `design_surfaces.py`; both should adopt one rule.
- `validation_security.py` and `design_surfaces.py` keep their inline copies of the folder rule (working; one has a mutation test on its text).
- qnow's folder-task count was not read.

### Follow-up proposal (not adopted, not in this design)

`decision_ledger.ledger()` globs `*.md`, so the gate rulings of folder tasks do not reach the ledger or `--summary`. Same class, a different mechanism (discovery, not path derivation). FO files it as its own backlog task if the Captain wants it.

### Decisions for the Captain

**D1. May one task deliver through two PRs? (Part 2.)** Recommend A.
- A. Yes: `--sibling-pr` as above, an ADR recording the departure from ADR 0025 D2's literal sentence. Worse: the first PR's ask no longer proves the ADR will land (see Limits); FO types one more flag and writes both `Candidate:` lines by hand; Spacedock still tracks one PR. Better: the first PR gets a saved ask record and the same gate path as any task. Evidence for need: one task in 141, but the pattern (a plugin plus the package that consumes it) is the journey-to-dev2 loop.
- B. No: a cross-plugin outcome is two tasks, the second `blocked-on` the first, the ADR on the second. Nothing to build and ADR 0025 D2 stands. Worse: two gates and two sets of criteria for one outcome; the integration criterion has one home; the shared validation story-map ran (both heads in `validation-3.md`) is gone.
- C. Leave it: FO asks the Captain in chat to merge the first PR, as for #704. Worse: no ask record; the observer sees a merge with no passing check.
Part 1 stands under every option.

**D2. Does `dispatch_records.py` join this task, though Scope's non-goal says "other scripts' folder support unless they share the helper"?** Recommend yes: after the change it imports `task_folder`, so it shares the helper; its `check_task_facts` is silently off for folder tasks (1 reserved-line finding on a flat task, 0 on the folder form); the live task fo-written-lines-checked-before-dispatch extends that same function and would inherit the gap. Worse: one more file and 2 tests in this task, and a textual neighbour of adoption-asks-which-extensions (below). If no: AC-5 drops and the gap is a follow-up.

## Acceptance criteria

**AC-1**: `delivery_gate.py check <task>/index.md …` and `check <task folder> …` exit with the same code, print the same text and save the record in `<task>/merge/ask-N.json` as the same task in flat form. Evidence: `cd kc-dev-flow-2/scripts && python3 -B -m unittest test_delivery_gate.FolderTaskTests`; the parity test compares output with the flat run. Falsifier: mutants "candidates read task.with_suffix", "record saved beside index", "directory argument not resolved" each fail it (`ideation/mutate.py`).

**AC-2**: For a folder task in a split-root state checkout the workflow README is found above the state checkout, as for a flat task. Evidence: `FolderTaskTests.test_the_readme_above_a_split_root_state_checkout_is_found_for_either_form`. Falsifier: mutant "readme looked up from the old parents" fails it.

**AC-3**: An owed role-call line and the "owes a special-role call" line name the task by folder name, never `index`, and `role_triggers.py` runs for real on the committed folder task. Evidence: `FolderTaskTests.test_an_owed_role_call_is_read_and_named_by_the_task_not_by_index`. Falsifier: mutants "role call gets folder parent and 'index'" and "names messages by stem" fail it.

**AC-4**: A flat task is unchanged: the seven modules of Measured pass without any existing assertion edited. Evidence: 444 tests OK before and, with the prototype, 454 OK; `git diff origin/main...HEAD -- 'kc-dev-flow-2/scripts/test_*.py' | grep '^-[^-]'` lists only the `run_check`, `STUB_GH` and `run_names` signature and setup lines (7 in the prototype). Falsifier: an edited assertion line appears in that grep.

**AC-5** (D2): `dispatch_records.py --names <folder-task>/dispatch/implementation-1.md` raises the same reserved-line finding as the flat task, and `dispatch_records.py <task>/index.md` names the folder's dispatch records. Evidence: `test_dispatch_records.TaskFactTests.test_a_folder_task_is_judged_for_reserved_lines_like_a_flat_task` and `…test_a_folder_task_given_by_index_names_its_dispatch_records`. Falsifier: mutants "dispatch_records: flat-only task file" and "dispatch_records: with_suffix folder" fail them.

**AC-6** (D1 = A): With `--sibling-pr o/r#N` naming a PR that is not closed, whose head is a `Candidate:` line of the newest validation record and which lists `<adr-path>/NNNN-*.md` at that head, a reserved ADR missing at this head raises no problem; the output carries the `sibling:` line and the saved record a `siblings` key. Evidence: `SiblingPrTests.test_a_reserved_adr_on_a_sibling_head_that_was_dispatched_passes_and_is_recorded`. Falsifier: mutant "sibling flag ignored" fails it.

**AC-7** (D1 = A): With no flag, with the file absent at the sibling, with a CLOSED sibling, or with a sibling head that is not a dispatched candidate, the check exits 1 and saves no record; the existing "reserved ADR … has no …" line and its `next:` line are unchanged. Evidence: `SiblingPrTests.test_without_the_flag_or_with_the_adr_nowhere_it_still_holds`, `…test_a_sibling_that_is_closed_or_not_a_dispatched_candidate_holds`, and the unedited existing test `test_a_reserved_adr_with_no_file_in_the_head_directory_holds_and_one_with_a_file_passes`. Falsifiers: mutants "closed sibling accepted" and "sibling head need not be a candidate".

**AC-8**: The change lists only `kc-dev-flow-2/scripts/delivery_gate.py`, `test_delivery_gate.py` and, per D2, `dispatch_records.py`, `test_dispatch_records.py`; with D1 = A also one ADR file (short title "A reserved ADR may land on a named sibling PR of the same task", no number). Evidence: `git diff --name-only origin/main...HEAD`; `python3 kc-dev-flow-2/scripts/adr_lint.py` on the ADR directory when an ADR lands; `python3 kc-dev-flow-2/scripts/lint-skills.py` passes. Falsifier: any other path in the diff, or a README, skill, reference or mod edit.

**AC-9** (D1 = A): The real-data replay of Measured removes the "reserved ADR 0029" problem when `--sibling-pr iamcxa/kc-claude-plugins#705` is given and keeps it without the flag. Evidence: the replay commands in the implementation report (copy of `_archive/new-work-starts-from-a-story-map*` with one `Candidate:` line added, read-only `gh`). Falsifier: the problem line prints with the flag, or is missing without it.

### Batch overlap

Files this design would change: `kc-dev-flow-2/scripts/delivery_gate.py` (imports, `dispatched_candidates`, `owed_role_calls`, `find_readme`, `write_record`, `check`, argument parser, docstring), `kc-dev-flow-2/scripts/test_delivery_gate.py` (`STUB_GH`, `run_check` signature and setup, a new `committed_folder` helper, two new test classes), `kc-dev-flow-2/scripts/dispatch_records.py` (`main`, `check_task_facts`; D2), `kc-dev-flow-2/scripts/test_dispatch_records.py` (`TaskFactTests`; D2), and with D1 = A one ADR file (no number: FO reserves it; no shared index change beyond the ADR directory listing).

| Task | State | Same file or check? | What FO needs |
| --- | --- | --- | --- |
| fo-written-lines-checked-before-dispatch | live, ideation (held for its alignment `Result:`) | yes: `delivery_gate.py` `CONFIRMATIONS`/`check`, `dispatch_records.py` `check_task_facts`, `role_triggers.py` | this task first; its worker then builds on folder-aware `check_task_facts` (Scope of that task already places this one after it, so FO decides the order) |
| comment-check-reaches-delivery-gate | live, ideation | yes: `delivery_gate.py` `write_record` (one key) and `check`, docstring, `test_delivery_gate.py` | whichever merges second rebases; conflicts are textual: the docstring, the `write_record` dict line, the end of `test_delivery_gate.py` |
| fo-write-checks-parse-top-level | live, ideation | yes: `delivery_gate.py` `declined_items`/`DECLINE_END`, docstring, `FoWriteRuleTests` | no shared function; textual conflict in the docstring and the test file's fixtures (`run_check`) |
| role-triggers-owe-ce-on-review-drift | live, ideation | only if its D2 reverses (`delivery_gate.py` role-call hold) | re-check after its gate |
| adoption-asks-which-extensions | live, ideation | `dispatch_records.py` `main`/`extension_errors` and `test_dispatch_records.py` (adjacent to my `main` line, D2) | textual neighbours; either order |
| design-surfaces-task-dir-crash | backlog | the directory-argument rule for `design_surfaces.py` | adopt one rule when it is designed |
| merge-check-reads-two-pr-tasks | backlog, folded here | this task's Part 2 | close it when this merges (D1) |
| new-work-starts-from-a-story-map, codex-reader-reads-receipt-marker, merge-ask-holds-missing-clauses, idle-names-failing-seeds, agent-reads-governing-adr, kc-decision-log-p1, kc-decision-log-cli, release-acceptance | done, archived (PRs #705, #693, #703, #694, #698, #695, #709) | already in origin/main; #703 supplies the `role_triggers.py` call this design repairs for folders | none |
| kc-decision-log-handoff-trial, pr-review-lite-value-pilot, journey-canvas-hosted-poc (other sessions, read only) | live | none names `delivery_gate.py` or `dispatch_records.py` | none |
| journey-server-host-pilot (other session, read only) | live, folder form | consumer: its merge ask is the next folder-task ask; it runs `design_surfaces.py check` and `number_guards.py` with `<task>/index.md` | implement this task before its merge ask, or FO repeats the symlink workaround |

Recommended order: fo-written-lines-checked-before-dispatch is the only task whose Scope orders itself against this one; implement this task first (smallest change, unblocks journey-server-host-pilot's ask), then comment-check-reaches-delivery-gate, then fo-write-checks-parse-top-level; the two that touch `delivery_gate.py` docstring rebase.

### Words FO reads at each moment

Counted per root `learning.md` "Measure the words FO reads at each moment": every passage and script output that instructs a step due at that moment, base (d496ac3d) against candidate. `git grep -n delivery_gate origin/main -- kc-dev-flow-2/references kc-dev-flow-2/skills` names the script at the merge ask only (`references/sd/workflow.md`, two passages of about 39 and 36 words, plus the observer skill's one sentence); startup, idle on an open PR, idle on a merged PR and after the archive do not name it. No README, skill, reference or mod text changes, so each passage is equal by construction; the new flag is taught by the hold's own `next:` line, its single home.

| Moment | Base | Candidate | Change |
| --- | --- | --- | --- |
| startup, idle on an open PR, idle on a merged PR, after the archive | script not named | same | 0 |
| merge ask, flat task, any outcome | `delivery_gate.py check` output | same lines | 0 (AC-4) |
| merge ask, folder task | 3 false lines, 45 words, exit 2 | the flat task's lines | down 45 |
| merge ask, reserved ADR missing, no flag (D1 = A) | 2 lines, 35 words | + one `next:` line, 17 words | up 17 on this hold only |
| merge ask, `--sibling-pr` used and passing (D1 = A) | not possible | + one `sibling:` line, 15 words | up 15 on that pass only |

## Number guards

ADR: 0036

## Stage Report: ideation

- DONE: Design the outcome under ## Scope: kc-dev-flow-2/scripts/delivery_gate.py check reads a folder task (its index.md or the folder) and, from the folded merge-check-reads-two-pr-tasks, a task that delivers through two PRs, so a number reserved on a sibling PR does not hold the ask; check whether other package scripts share the same path derivation; whether a task may deliver through two PRs at all is the Captain's decision to put at the gate; name every file, the falsifier and the evidence each criterion needs
  Chain read in order (Spacedock 0.27.3 schema and `merge.go`, kc-dev-flow-2 scripts at d496ac3d, relay and web state checkouts read-only); `## Design` has the derivation table (five scripts share it, `decision_ledger.py` is a separate defect), D1 (two PRs) and D2 (`dispatch_records.py` joins) for the Captain, files and falsifiers in the ACs.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (new-work-starts-from-a-story-map, codex-reader-reads-receipt-marker, merge-ask-holds-missing-clauses, fo-write-checks-parse-top-level, idle-names-failing-seeds, agent-reads-governing-adr) and live task of other sessions (kc-decision-log-p1, kc-decision-log-cli, kc-decision-log-handoff-trial, pr-review-lite-value-pilot, release-acceptance, journey-canvas-hosted-poc, journey-server-host-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Table under `### Batch overlap` with a `Recommended order:` line; the five named batch tasks and three named live ones (kc-decision-log-p1, kc-decision-log-cli, release-acceptance) are done and archived; live overlaps the dispatch omitted are fo-written-lines-checked-before-dispatch, comment-check-reaches-delivery-gate, role-triggers-owe-ce-on-review-drift and adoption-asks-which-extensions.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each moment`: only the merge ask names the script; folder task down 45 words, an ADR-missing hold up 17 and a passing sibling ask up 15 (D1 = A only); no README, skill, reference or mod text changes.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  `## Acceptance criteria` AC-1 to AC-9, each with a command and a named falsifier; D1 recommends A, D2 recommends yes, each with what gets worse. Per criterion, current evidence (a prototype, not the deliverable):
  - AC-1: prototype passes `FolderTaskTests` parity (by `index.md` and by folder); mutants "candidates read task.with_suffix", "record saved beside index", "directory argument not resolved" each fail it (`ideation/mutate.py`, 2026-10-25).
  - AC-2: prototype passes the split-root README test; mutant "readme looked up from the old parents" fails it (it survived the first test and drove that test).
  - AC-3: prototype passes the real-`role_triggers.py` test; mutants "role call gets folder parent and 'index'" and "names messages by stem" fail it.
  - AC-4: prototype 454 tests OK in seven modules against 444 OK at origin/main; 7 removed test lines, all helper plumbing. Not yet verified on the real candidate.
  - AC-5 (D2): prototype passes both new `TaskFactTests`; mutants "dispatch_records: flat-only task file" and "dispatch_records: with_suffix folder" fail them.
  - AC-6 (D1 = A): prototype passes the sibling pass test; mutant "sibling flag ignored" fails it.
  - AC-7 (D1 = A): prototype passes the two hold tests and the unedited ADR hold test; mutants "closed sibling accepted" and "sibling head need not be a candidate" fail them.
  - AC-8: not yet verified; it is a property of the implementation diff (`git diff --name-only`), the prototype touches the four script files only.
  - AC-9 (D1 = A): replay on real `gh` data (PRs #704 and #705, 2026-10-25) removes the "reserved ADR 0029" problem with the flag and keeps it without; not yet repeated against the implementation diff.
  Design checks: `python3 <package>/scripts/design_surfaces.py check <task>` printed "delivery-gate-reads-folder-tasks.md: design surfaces presentable" (exit 0).

### Summary

Folder-task support is five small edits in `delivery_gate.py` through the existing `task_folder()` helper; the probe also found README discovery and the role-call message broken for folder tasks, and `dispatch_records.py` silently skipping its reserved-line check on them (D2). The two-PR part is a `--sibling-pr` flag held on D1, with three limits stated in the design: the newest validation record must name both heads, the second PR's merge stays outside Spacedock tracking, and ADR 0025 D2's literal sentence needs an ADR if the Captain accepts. One gap for FO: `## FO alignment` says `Alignment: needed at ideation` and has no `Result:` line; I read the dispatch as routing that alignment to the gate and wrote none, so FO can add the `Result:` line before `gate prepare`.

## Stage Report: implementation

- DONE: One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/main (ac67eb0a56d6f78baa5fb2973f9727cefa3e06b9) implementing the approved design and acceptance criteria in the task file; with the Captain's decisions as recommended: D1 a task may deliver through two PRs through a repeatable --sibling-pr flag on kc-dev-flow-2/scripts/delivery_gate.py, D2 kc-dev-flow-2/scripts/dispatch_records.py joins; only the files the design names
  Draft PR iamcxa/kc-claude-plugins#720, head 1c480fec, branch spacedock-ensign/delivery-gate-reads-folder-tasks; `git diff --name-only ac67eb0a..HEAD` lists delivery_gate.py, dispatch_records.py, test_delivery_gate.py, test_dispatch_records.py and docs/adr/0036-*.md only (AC-8). Prototype applied, then test clean-ups: dropped one weak test (README found for a folder task, killed no mutant), split "merged sibling passes" into its own test, tidied `run_names`; docstring updated.
- DONE: ADR 0036 records the ruling the design names, quoting the Captain's words from the task file and its gate records
  `docs/adr/0036-a-reserved-adr-may-land-on-a-named-sibling-pr-of-the-same-task.md`, Words 「全准」 (Captain, 2026-10-25, batch-6 ideation gate record `resolution:spacedock:delivery-gate-reads-folder-tasks:ideation:1`).
- DONE: Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
  AC-1..AC-7: seven modules 454 tests OK (base 444); the only removed test lines are `run_check`/`STUB_GH`/`run_names` plumbing (AC-4). Mutation (`ideation/mutate.py .`, 11 mutants, each killed): candidates read with_suffix and record saved beside index and directory argument not resolved fail `FolderTaskTests` parity; old-parents README fails `test_the_readme_above_a_split_root_state_checkout_is_found_for_either_form`; role-call and stem-naming fail `test_an_owed_role_call_is_read_and_named_by_the_task_not_by_index`; flat-only and with_suffix dispatch_records fail the two `TaskFactTests`; sibling flag ignored fails 3 tests; closed sibling accepted and head-need-not-be-candidate fail `test_a_sibling_that_is_closed_or_not_a_dispatched_candidate_holds`. AC-9 replay on real gh data (#704/#705, archived task copy plus one Candidate line): without `--sibling-pr` the "reserved ADR 0029 has no docs/adr/0029-*.md at PR head f0d3f442d5e6" line and the `--sibling-pr` next: line print; with `--sibling-pr iamcxa/kc-claude-plugins#705` neither prints (remaining line is the replay artefact "not a git work tree").
- DONE: kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), adr_lint.py docs/adr --since <base> --require 0036 exit 0; number_guards.py check exit 0; comment_ratio.py within its maximum; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured
  lint-skills.py exit 0; `adr_lint.py docs/adr --since ac67eb0a... --require 0036` exit 0 (36 files); `number_guards.py check --repo . --workflow-dir <wf> --base ac67eb0a --task <task>` exit 0 ("PASS: no findings", base ac67eb0a56d6); comment_ratio: 148 code lines, 0 comment lines, 0.0% (maximum 5%); roborev gate `clean on 1c480fecf; evidence=roborev:1172`; plain `git push origin <branch>`; CI on head 1c480fec: adr-path-check, multi-profile route gate, unit tests (python3), version parity, GitGuardian all pass; CI cost not measured.

### Summary

Implemented the approved design from the ideation prototype (the folder rule through the existing `task_folder`, `--sibling-pr`, `dispatch_records.py` joining) with small test clean-ups, ADR 0036 and a Draft PR #720; no version bump, no review requested. FO note: the ideation report's open `Result:` line under `## FO alignment` is still FO's to add; the design's follow-up (`decision_ledger.py` globbing `*.md`) is not in this PR.

## Stage Report: validation

- DONE: Independent verdict on PR #720 head 1c480fec against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  PASSED at head 1c480fecf7d84e7bb4a15483fb8b3bc808dab630 (base ac67eb0a is current origin/main). Seven modules from a detached checkout: 454 tests OK (170s). AC-1..AC-7 and AC-9 hold; AC-4: the 7 removed test lines are `run_check`/`STUB_GH`/`run_names` plumbing, no assertion edited; AC-8: diff lists 4 scripts and ADR 0036 only; lint-skills.py exit 0. Own mutation run (`/tmp/val720-mutate.sh`, python3 -B, fresh copy per mutant): 13 of 13 killed, naming the AC-1 (3), AC-2, AC-3 (2), AC-5 (2), AC-6, AC-7 (2) mutants plus two I added (reserved-number match loosened to any ADR; sibling note not recorded), each by the test the AC names. Limits judged: file-exists-not-merges and newest-record-only are true and safe (probe: a sibling head only in an older record holds as "not a dispatched candidate"); flat-task companion folder as argument gives "cannot read input: .../index.md" exit 2 as stated; CI cost "not measured" is honest (no workflow file changed); `decision_ledger.py` follow-up is correctly outside this diff.
- DONE: Replay the #704/#705 case with and without --sibling-pr, and check ADR 0036 against ADR 0025 D2 and the Captain's gate words
  Replay (archived task copy plus the one added `Candidate:` line for f0d3f442, read-only gh, 2026-10-25): base script and candidate without the flag both print "reserved ADR 0029 has no docs/adr/0029-*.md at PR head f0d3f442d5e6"; candidate with `--sibling-pr iamcxa/kc-claude-plugins#705` does not (remaining lines are replay artefacts: PR already merged, copy is not a git work tree). ADR 0036 narrows 0025 D2 and says so ("otherwise stands"): no flag, closed sibling, undispatched head or absent file all keep 0025's hold. The ideation briefing question (`review/ideation/briefing-1`) says approving accepts D1 and D2 as recommended, so 「全准」 does cover them, and 0036 quotes the same words and the same gate record.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.29.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  Six-step script below, run with `env -i HOME PATH bash --noprofile --norc` as written, all observed outputs match. `adr_lint.py docs/adr --since ac67eb0a56d6f78baa5fb2973f9727cefa3e06b9 --require 0036`: "36 ADR file(s) checked, 0 legacy", exit 0. Also: comment_ratio 0.0% (exit 0), number_guards check PASS (exit 0), dispatch_records on this task's folder "3 dispatch record(s) complete" (exit 0), design_surfaces check presentable, `gh pr checks 720`: all 5 pass.

### Findings

- F1 Polish: `doc_impact.py ac67eb0a 1c480fec` lists `learning.md` (it names `dispatch_records.py`) and the implementation report carries no `updated` or `unaffected: <reason>` line for it. Validator's assessment: `unaffected: its dispatch_records.py passages concern is_pointer and `--names` diagnostic wording; this change only resolves a folder task's path.` No behaviour or boundary is at risk; FO may copy that line into the gate.
- F2 Deferred risk: `check` reads every `--sibling-pr` whenever the task reserves an ADR, even when the ADR is already at this PR head, so a closed or undispatched sibling then holds a ready ask (probe: ADR present at head plus a closed sibling gives exit 1, "an ADR it carries will not land"). Design Mechanism 3 said siblings are read only when the ADR is missing. Trigger needs FO to pass the flag when it is not needed; the hold's `next:` line teaches the flag only on a missing ADR. Material if FO passes the flag by habit on single-PR tasks.

No Material finding, no Needs decision. Observation for FO, not a finding: `gh pr view 720` reports `isDraft: false` at validation time although the implementation report says Draft; the state of the PR is the Captain's and I changed nothing.

### Acceptance script (run exactly as written in a fresh bash shell, 2026-10-25)

```bash
# Needs: git, python3, an authenticated gh (read-only calls), the dev2 workflow checkout below.
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree
PKG=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.29.0
CAND=1c480fecf7d84e7bb4a15483fb8b3bc808dab630
BASE=ac67eb0a56d6f78baa5fb2973f9727cefa3e06b9
T=$(mktemp -d)

echo "STEP 1: check out the candidate and the base in throwaway directories"
git -C "$REPO" fetch -q origin pull/720/head && git -C "$REPO" worktree add -q --detach "$T/cand" $CAND && mkdir "$T/base" && git -C "$REPO" archive $BASE kc-dev-flow-2/scripts | tar -x -C "$T/base"
git -C "$T/cand" rev-parse HEAD

echo "STEP 2: run the new tests (folder tasks, sibling PR, dispatch records)"
(cd "$T/cand/kc-dev-flow-2/scripts" && python3 -B -m unittest test_delivery_gate.FolderTaskTests test_delivery_gate.SiblingPrTests test_dispatch_records.TaskFactTests 2>&1 | grep -E '^(Ran|OK|FAILED)')

echo "STEP 3: a folder task (release-acceptance, PR 709): lines naming the wrong folder index/dispatch, base then candidate"
mkdir "$T/ra" && cp -R "$REPO/docs/dev2/.spacedock-state/_archive/release-acceptance" "$T/ra/" && echo gate > "$T/gate.txt"
for S in base cand; do
  printf '%s: ' $S
  python3 -B -I "$T/$S/kc-dev-flow-2/scripts/delivery_gate.py" check "$T/ra/release-acceptance/index.md" --pr iamcxa/kc-claude-plugins#709 --head d84ebde04c874524ede1d55587db9b9a1692c627 --text-file "$T/gate.txt" --workflow-dir "$REPO/docs/dev2" 2>&1 | grep -c 'index/dispatch'
done

echo "STEP 4: two-PR task (PRs 704 and 705): lines saying reserved ADR 0029 is missing, base, candidate without the flag, candidate with it"
mkdir "$T/sm" && cp -R "$REPO/docs/dev2/.spacedock-state/_archive/new-work-starts-from-a-story-map" "$REPO/docs/dev2/.spacedock-state/_archive/new-work-starts-from-a-story-map.md" "$T/sm/"
python3 -I - "$T/sm/new-work-starts-from-a-story-map/dispatch/validation-4.md" <<'PY'
import sys
p = sys.argv[1]
t = open(p).read()
first = "Candidate: 32ad029f059b5c0690344677518643a253856515\n"
open(p, "w").write(t.replace(first, first + "Candidate: f0d3f442d5e62e4876f457f01a48b63a9c15506f\n", 1))
PY
run() { python3 -B -I "$1/kc-dev-flow-2/scripts/delivery_gate.py" check "$T/sm/new-work-starts-from-a-story-map.md" --pr iamcxa/kc-claude-plugins#704 --head f0d3f442d5e62e4876f457f01a48b63a9c15506f --text-file "$T/gate.txt" --workflow-dir "$REPO/docs/dev2" "${@:2}" 2>&1 | grep -c 'reserved ADR 0029'; }
printf 'base: ';               run "$T/base"
printf 'candidate, no flag: '; run "$T/cand"
printf 'candidate, flag: ';    run "$T/cand" --sibling-pr iamcxa/kc-claude-plugins#705

echo "STEP 5: ADR lint on the candidate"
(cd "$T/cand" && python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since $BASE --require 0036; echo "exit $?")

echo "STEP 6: remove the throwaway directories"
git -C "$REPO" worktree remove --force "$T/cand" && rm -rf "$T" && echo removed
```

Observed output: STEP 1 prints `1c480fecf7d84e7bb4a15483fb8b3bc808dab630`; STEP 2 `Ran 19 tests in 2.041s` then `OK`; STEP 3 `base: 1` and `cand: 0`; STEP 4 `base: 1`, `candidate, no flag: 1`, `candidate, flag: 0`; STEP 5 `36 ADR file(s) checked, 0 legacy` and `exit 0`; STEP 6 `removed`. Any other number in STEP 3 or 4 means the folder rule or the flag is not working. Not covered: a real folder-task merge ask end to end (the replay holds for other reasons, as the merged PRs cannot pass), `--sibling-pr` against a PR that is still open, the unchanged flat-task path beyond the 454-test suite, and CI cost.

### Summary

PASSED for head 1c480fec: every criterion holds, 13 of 13 of my own mutants die to the named tests, the #704/#705 replay behaves as designed, and ADR 0036 stays inside ADR 0025 D2 and the Captain's accepted words. Two findings, both non-blocking (F1 Polish: missing `doc_impact` record for `learning.md`; F2 Deferred risk: siblings are read even when the ADR is already at this head). Throwaway worktrees and temp copies were removed; nothing was pushed, commented on or marked ready.
