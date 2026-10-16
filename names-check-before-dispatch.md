---
title: The dispatch_records.py --names check runs only if FO remembers to run it before dispatch build
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:names-check-before-dispatch:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:names-check-before-dispatch-backlog-1
              briefing:
                id: briefing:names-check-before-dispatch:backlog:attempt-1:revision-1
                digest: sha256:f5c4f4725e70e4780f45771d090a39a1e631de67a884c2f3be3a591dcae294b2
                room-ref: ./names-check-before-dispatch/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:names-check-before-dispatch:backlog:1
                briefing: briefing:names-check-before-dispatch:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-16T03:13:44.729269Z"
                decision: approve
                reason: 'Captain approved batch 1 (「批准」): schedule as Pilot and enter ideation; as the gate question states, this accepts profile pilot and five parallel ideations with dev2-laws-check''s design read by the other four for overlap.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:names-check-before-dispatch:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:names-check-before-dispatch-ideation-1
              briefing:
                id: briefing:names-check-before-dispatch:ideation:attempt-1:revision-1
                digest: sha256:3264c41be765a0f6ec250a28b9183c864e9ade63ccc06b394b6ed2e9160ba37a
                room-ref: ./names-check-before-dispatch/review/ideation/briefing-1
started: 2026-10-16T03:14:56Z
---

Filed from a learn package-issue candidate the Captain approved on 2026-10-14 (「1,3」), after the observer report on task `followup-dispatch-records-checked` (PR #642) found bare package-script names in FO's own dispatch records `implementation-1.md` and `-2.md`, because FO ran `dispatch_records.py --names` after `dispatch build` instead of before. The same happened on that task's first implementation dispatch and on the fo-lifecycle-mod implementation dispatch the same day (caught before launch the second time).

## Scope

- The gap is enforcement: the README Stages rule says "before `dispatch build`, FO runs `python3 <package>/scripts/dispatch_records.py --names <record>` on the saved record", but nothing runs it; `spacedock dispatch build` neither calls it nor refuses a checklist naming a bare script, and the folder-mode check at validation does not include `--names`.
- Learn's no-change reason for job 49a91123 said the task's own Package root check enforces this practice; it does not (the Package root rule checks a different line and runs at validation).
- Candidate routes: a pre-send single-record mode (declined as D2 of `followup-dispatch-records-checked`, to be filed "if the late catch bites again"; it has bitten twice since), or folding `--names` into the validation-time folder run. Which is for ideation.
- Related: `extension-instruction-reaches-dispatch` (another dispatch-time check).
- Non-goals: to be set at ideation.

## Design

### PRFAQ

**Press release (future).** When FO saves a worker's dispatch record and forgets to run `dispatch_records.py --names`, the next time FO's idle hook runs it is told so in the same `next:` lines it already follows: the record, the bare script names it holds, and what to do while the worker is still running. On a workflow whose newest records are clean the hook prints nothing new, and no README or mod word is added. This is detection after the record is committed, not prevention before `dispatch build` sends it: the package has no point before the send that FO does not choose to pass.

**FAQ.**

- *Why is this not a pre-send check?* Nothing before `dispatch build` runs unless FO runs it. `spacedock dispatch build --help` (spacedock 0.27.2, 2026-10-16) lists no workflow-declared check hook; it reads only the checklist and scope-notes files it is handed. The mod hooks are `startup`, `idle` and `merge` (`first-officer-shared-core.md`, "Mod Hook Convention"). Two of the three missed records are headed "Follow-up message to the live implementation worker", so no built dispatch file reached that worker, and a worker-side check in the stage skills would miss them. The saved record is the one artifact all three share.
- *What is a "pre-send single-record mode"?* It already exists: `dispatch_records.py --names <record>` takes one record. The gap is the run, not the mode, so a new mode of that kind adds no enforcement.
- *Why the newest record only?* A flag on an older record has no remedy. `fo-record-checks` (FAQ "What does it get wrong?") ruled that FO cannot honestly rewrite a record the worker already followed, and 50 of the 55 records the replay flags were committed on 2026-10-13, the day the rule shipped. A newer clean record (the corrected follow-up) clears the flag, so the line ends when FO has done the one useful thing.
- *What does FO do on the line?* If the worker is live, send a follow-up writing each name with its absolute package path and save that as the next record; if the worker is done, nothing, and the line ends at that task's next dispatch.
- *What does it get wrong?* The `--names` shape filter flags a repository file whose name equals a package script name (a test file the task edits): 4 of the 8 flagged mentions in the three missed records are `test_*.py` files, because those tasks edit the package itself. The line cannot tell, and would repeat on each idle pass until the task's next record.
- *Cost?* One `git log` per task with a `status` on each idle pass. Not measured. The new tests join `test_dispatch_records.py` and `test_pr_watch.py`, which `.github/workflows/kc-dev-flow-2-tests.yml` already runs; no new CI job, added seconds not measured.

### Chain check (said before building)

- **Spacedock 0.27.2:** no pre-dispatch hook; `gh search issues --repo spacedock-dev/spacedock` for "pre-dispatch", "dispatch hook" and "dispatch build check" (2026-10-16) found only #164 and #232, neither about this. ADR 0014 reached the same wall for `workflow_checkout.py` and says "Reopen if Spacedock gains a pre-dispatch hook". I filed nothing.
- **kc-dev-flow-2 0.23.0 at origin/main (1383c911):** `dispatch_records.py --names` exists and works (replay below). `pr_watch.py tasks` already reads every task with a `status`, prints `next:` lines FO must follow, and calls sibling scripts by subprocess (`observer_check.py`); the idle mod's step 2 already says "Do each `next:` line it prints". `fo-lifecycle-mod` moved FO's remembered delivery steps into exactly these lines. So the capability to extend is `pr_watch.py tasks`, not a new script, mod or wrapper.
- **Sibling adopters (read-only, 2026-10-16):** `git grep` on subspace-relay `origin/HEAD` finds the same synced sentence at `docs/dev2/README.md` and `docs/dev2-poc/README.md` and no local check. qnow and ss-web checkouts are not under `~/conductor/repos`; not read.
- **Bounded existing-code check:** `dispatch_records.py` is complete and unit-tested but has no FO consumer; the need is the replay below (5 of the 71 records committed from 2026-10-14 on were flagged at commit time), not the observer's word alone.

### Replay on the records it missed

Prototype of the proposed selection (newest record by `git log --diff-filter=A` under `<slug>/dispatch/`, then the package's own `bare_names`), run read-only against `spacedock-state/dev2` with the 0.23.0 script names; the script lives in `/tmp/names-proto/` and is not a repository file.

| State checked out | Newest record | Flagged (line: name) | Other active tasks flagged |
| --- | --- | --- | --- |
| `e081c5f2` | followup-dispatch-records-checked `implementation-1` | 8: test_dispatch_records.py, 8: lint-skills.py, 9: roborev_gate.py, 9: lint-skills.py | none |
| `c3935e01` | same task `implementation-2` | 10: test_sd_dispatch.py, 11: test_observer_recovery.py (`implementation-1` is older and not named) | none |
| `d6182ead` | delivery-gate-verdict-form `implementation-3` | 18: delivery_gate.py, 18: test_delivery_gate.py | none |

Over the whole branch: 149 active-task record additions; at the commit where each was newest, 55 were flagged, 50 of them dated 2026-10-13 (the day `--names` shipped, in 0.22.1, #640) and 5 of the 71 dated 2026-10-14 or later: the three above, `fo-lifecycle-mod` `implementation-11` (its final text still names `delivery_gate.py`, line 11) and `delivery-gate-verdict-form` `implementation-4` (clean in its final text, so FO rewrote it after the commit; the hook reads the file on disk and would not flag it). This proves detection of those records, not timing: whether the line would reach FO before the worker read the record is not measured, and the idle hook's firing point is read from `fo-dispatch-core.md` ("Retry empty once"), not observed live.

### Words FO reads at each moment

Counted with `len(text.split())` on `origin/main` (the budget's own counter, `lint-skills.py` `workflow_size_and_duplicates`); candidate = the design as written.

| Moment | What FO reads | Base | Candidate |
| --- | --- | --- | --- |
| Save a record, before `dispatch build` | README sentence "A checklist or scope-notes line that names a package script ... rewrites each name it lists." | 41 | 41 (unchanged; still the earliest catch) |
| Startup | idle mod `references/sd/mods/kc-dev-flow-2.md` plus `pr_watch.py tasks` output | 48 plus output | 48 plus byte-identical output while the newest records are clean |
| Idle, nothing flagged | same | 48 plus output | same |
| Idle, a record flagged | same, plus one `next:` line | not applicable | about 41 words for a three-name record (drafted, to be measured) |
| README total | `references/sd/workflow.md` | 5495 of 5511 | 5495 of 5511 (16 words of headroom left untouched for the other four batch tasks) |

No moment's text rises; the only added words are the line FO is told to act on, and only while a record is flagged.

### Sequence

```mermaid
sequenceDiagram
    participant FO
    participant State as state checkout (record files)
    participant Hook as idle hook: pr_watch.py tasks
    participant Rec as dispatch_records.py --newest
    participant W as worker
    FO->>State: save and state-commit the record
    opt FO runs --names before build (README step, unchanged)
        FO->>Rec: --names record
        Rec-->>FO: bare names listed, FO rewrites them
    end
    FO->>W: dispatch build, send
    Note over FO,Hook: next scheduler pass finds nothing ready
    FO->>Hook: idle hook runs the mod
    Hook->>Rec: --newest state slug, once per task with a status
    Rec->>State: newest committed record, read as on disk
    alt clean, or a later clean follow-up is newest
        Rec-->>Hook: exit 0, no output
        Hook-->>FO: output unchanged
    else a bare name remains
        Rec-->>Hook: exit 1, file:line lines
        Hook-->>FO: one next: line
        alt worker is live
            FO->>W: follow-up with absolute paths
            FO->>State: save and commit it as the next record
        else worker is done
            Note over FO: nothing to send; the line ends at the task's next dispatch
        end
    else state not readable as git
        Rec-->>Hook: exit 2
        Hook-->>FO: next: report slug to the Captain, exit 2
    end
```

### Mechanism

- `dispatch_records.py --newest <state checkout> <slug>`: finds the newest record as the file added by the latest commit that adds a file under `<slug>/dispatch/`, runs the `--names` scan on that file as it is on disk, prints the same `file:line: bare package script name NAME` lines, exit 1 when any, 0 when none or the task has no `dispatch/` folder, 2 when the state cannot be read as git.
- `pr_watch.py tasks` calls it per task with a `status`, before the no-PR `continue`, by subprocess as it already does for `observer_check.py`, and prints one `next:` line per flagged record; exit 2 keeps its current meaning ("a task cannot be read") for an unreadable state.
- No change to `references/sd/workflow.md`, the mod, `lint-skills.py`, Spacedock or any state file.

### Limits (known, not untested)

- Detection happens after the record is committed and, normally, after the worker has it; it narrows "caught at archive by the observer" to "caught at the next idle pass", it does not stop the send.
- An uncommitted record is invisible until FO commits it; a record whose newer sibling is clean is never re-flagged.
- The `--names` shape filter's false positive on repository files (above) carries over and repeats on each idle pass until the task's next record.
- Only the bare-name rule is swept. Other record parts (the completion line a follow-up lacked in `followup-dispatch-records-checked` `implementation-3`) stay with the validation-time folder run.
- If FO does not act on the `next:` line the check has still run; the observer remains the net after that.

### Non-goals

No Spacedock change or request filed; no wrapper around `dispatch build`; no README, mod or budget edit; no state file or per-session "reported once" memory; no sweep of archived tasks or older records; no CI job on the state branch; no profile change (Pilot: no production data, credentials, broad exposure or recurring unattended operation).

### Unresolved decisions for the Captain

- **D1: which run point?** Recommend the idle-hook `next:` line above. Options: (a) that; (b) fold `--names` into the validation-time folder run `dispatch_records.py <task folder>`; (c) wait for a Spacedock pre-dispatch hook. Worse under (a): the line is still prose-enforced at its last step (FO can ignore it) and fires after the send; it costs one `git log` per task per idle pass and carries the repository-file false alarm, which repeats on each idle pass until the task's next record instead of showing once. Why not (b): it fires one whole stage later, after the PR exists, its exit 1 would fail every older record in a folder (the replay flags 50 of the 78 records committed before 2026-10-14), and `fo-record-checks` ruled against running `--names` over records FO cannot honestly rewrite. Why not (c): no such hook exists or is requested, and ADR 0014 already waits on it. Past ruling named: `followup-dispatch-records-checked` D2 (「准」, 2026-10-14) kept its own check at validation only and said to file the pre-send run "if the late catch bites again"; it has, and this task is that filing, so (a) goes beyond D2 only in adding an automatic run point, not in changing its decision. No `Override:` line bears (`git grep -n 'Override:'` on `.spacedock-state`, 2026-10-16: prose in earlier decision lists only).
- **D2: ask Spacedock for a pre-dispatch hook point?** Recommend yes, as a separate Captain-approved issue; it is the only route that prevents instead of detects, and it would also let ADR 0014's `workflow_checkout.py` be enforced. Worse under yes: no date, and nothing changes meanwhile; D1 does not wait on it.

### Batch overlap

Files this design would change, all under `kc-dev-flow-2/scripts/`: `dispatch_records.py` (the `Usage:` docstring block, a `--newest` branch in `main`, one helper), `test_dispatch_records.py`, `pr_watch.py` (`tasks`, one call and one `next:` line), `test_pr_watch.py`. It does not change `references/sd/workflow.md`, `references/sd/mods/kc-dev-flow-2.md` or `lint-skills.py`. Read from the task files on 2026-10-16: extension-instruction-reaches-dispatch holds a design (read below); dev2-laws-check, prod-security-review-gates and amendment-form-check held only briefs, so their rows come from the briefs and must be rechecked when their designs land.

| Other batch-1 task | Same file or check | Effect on ordering |
| --- | --- | --- |
| extension-instruction-reaches-dispatch | `dispatch_records.py` `main()` and `Usage:` docstring, and `test_dispatch_records.py` (its design: one new folder-run part, a `--readme FILE` option; mine: a `--newest` branch). Its design leaves `workflow.md` alone, as mine does | Textual conflict in one function: land this task first, as that design also asks. Its text says its check will "join the pre-send mode" of this task; this design recommends no pre-send mode (a `--names <record>` single-record run already exists and adds no enforcement), so that join does not exist as written. If the Captain wants its check at hook time too, `--newest` can call it when the newest record is `<stage>-1`, passing the workflow README it already holds (`pr_watch.py tasks` has the path); that is a later change, not part of this design, and its Decision 1 wording should be rechecked after D1 here is ruled. |
| dev2-laws-check | The `--names` check itself (its brief lists `dispatch_records.py` among laws to join its list) and the run point (its candidate is CI on each push to the state branch) | No file overlap with the four above unless its law list wraps `dispatch_records.py`. Not exclusive: CI exists only where an adopter adds it and reports after the push; the hook runs where FO already runs `pr_watch.py tasks`. It should list `--newest` as a law, not replace it. |
| prod-security-review-gates | None expected (stage and profile text). Shared constraint: `workflow.md` has 16 words of budget headroom and `lint-skills.py` carries `WORKFLOW_WORD_BUDGET` | This task takes none of it. If that task raises the budget, the raise is its own change; no ordering needed. |
| amendment-form-check | None expected (`design_surfaces.py`). Another FO-remembered check, run at the design gate | No ordering. If its design also adds a `next:` line to `pr_watch.py tasks`, the two edit the same function and need a merge order. |

## Acceptance criteria

Source for every criterion: the Captain's approval of this task's filing (「1,3」, 2026-10-14, per the task body) and the checklist's ask that the check run without FO remembering it; the mechanism is the recommended D1(a), so AC-1 to AC-7 bind only if D1(a) is approved.

**AC-1** `python3 <package>/scripts/dispatch_records.py --newest <state checkout> <slug>` prints the `--names` lines (`<record>:<line>: bare package script name <NAME>`) for the newest committed dispatch record of the task and exits 1; it exits 0 with no output when that record is clean. Evidence: in a throwaway clone of `spacedock-state/dev2` checked out at each of `e081c5f2`, `c3935e01` and `d6182ead`, the output names exactly the lines in the replay table above (followup `implementation-1`, followup `implementation-2` without naming `implementation-1`, delivery-gate `implementation-3`). Falsifier: a mutation that scans every record of the task prints `implementation-1` at `c3935e01`, and one that takes the lowest-numbered record names the wrong file; the test asserting the exact output fails under each.

**AC-2** A task whose older record is bare and whose newest record is clean exits 0 with no output. Evidence: a fixture git state checkout with two committed records, run through the real script. Falsifier: the scan-every-record mutation of AC-1 exits 1 on it.

**AC-3** `python3 <package>/scripts/pr_watch.py tasks <workflow dir>`, run as a real subprocess (no mocked `dispatch_records.py`) on a fixture workflow with a task that has a `status`, no `pr`, and a newest record naming a bare script, prints one `next:` line holding the record path and each bare name, and exits 0. Evidence: that test's output. Falsifier: deleting the call, or placing it after the no-PR `continue` in `tasks`, leaves no line and fails the test.

**AC-4** On a fixture whose newest records are all clean, `pr_watch.py tasks` prints byte-identical stdout and the same exit code as the 0.23.0 `pr_watch.py` on the same fixture. Evidence: both versions run on one fixture and `diff` of the two stdout files is empty. Falsifier: a mutation printing any "checked" or summary line when nothing is flagged makes the diff non-empty.

**AC-5** No word is added to what FO reads at the save-a-record, startup or clean-idle moments: `git diff origin/main -- kc-dev-flow-2/references/sd/workflow.md kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md kc-dev-flow-2/scripts/lint-skills.py` is empty, and the report gives the measured word count (`len(line.split())`) of the flagged-record line for a three-name record. Falsifier: any edit to the three files, including a raised `WORKFLOW_WORD_BUDGET`.

**AC-6** An unreadable state is loud and a task without records is silent. `--newest` exits 2 when the state checkout cannot be read as git, and `pr_watch.py tasks` then prints `next: report <slug> to the Captain: ...` and exits 2; a task with no `dispatch/` folder prints nothing and does not change the exit code. Evidence: two fixtures, one a plain directory and one a git checkout without `dispatch/`. Falsifier: a catch-all returning 0 on the unreadable fixture, or an error on the no-folder fixture, fails its test.

**AC-7** Replay over the branch history with the real mode: in a throwaway clone, running `--newest` at each commit that adds a non-archived dispatch record flags the five records from 2026-10-14 on named in the replay section, including the three missed ones; the counts (149 additions, 55 flagged, 5 of 71) are re-measured at the state HEAD the implementer reads and reported with any difference. Evidence: the loop command and its output in the report. Falsifier: a mode that scans nothing reports 0 flagged; the five named records are the fixed expectation. Limit stated in the report, not asserted: this proves detection, not that a line would have reached FO before the worker read the record.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

## Stage Report: ideation

- DONE: A design (PRFAQ and Mermaid) for how the kc-dev-flow-2/scripts/dispatch_records.py --names check runs without FO remembering it before dispatch build (a pre-send single-record mode, the validation-time folder run, or another route), with a replay on the records it missed (implementation-1 and -2 of followup-dispatch-records-checked, implementation-3 of delivery-gate-verdict-form)
  `## Design`: PRFAQ, sequence diagram, chain check; recommended route is an idle-hook `next:` line from `pr_watch.py tasks` (detection after commit, not prevention). Prototype replay in `/tmp/names-proto/` flags exactly the three records at `e081c5f2`, `c3935e01`, `d6182ead`; `design_surfaces.py check` printed "design surfaces presentable", exit 0.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch-1 task (prod-security-review-gates, dev2-laws-check, extension-instruction-reaches-dispatch, names-check-before-dispatch, amendment-form-check) that changes the same file or check, so FO can order implementation
  Four files named under `kc-dev-flow-2/scripts/`; four rows for the other tasks. Only extension-instruction-reaches-dispatch had a design to read, and it conflicts in `dispatch_records.py`; its "join the pre-send mode" assumption does not hold under this design. The other three rows come from briefs.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each moment`: README sentence 41 to 41, idle mod 48 to 48, `workflow.md` 5495 to 5495 of 5511 (`len(text.split())` on origin/main); clean-workflow output byte-identical by AC-4; flagged line about 41 words, drafted. Whole-moment totals (startup and so on) were not recounted; only the delta is claimed.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  `## Acceptance criteria` holds AC-1 to AC-7, each with an evidence clause and a falsifier; D1 (run point) and D2 (ask Spacedock for a pre-dispatch hook) with recommendations and worse-under lines; ADR 0014, `followup-dispatch-records-checked` D2 and the `Override:` grep read.
  AC-1 current evidence: prototype output matches the replay table at the three SHAs; the shipped `--newest` mode is not written, not yet verified.
  AC-2 current evidence: prototype does not flag older `implementation-1` at `c3935e01`; fixture test not yet written, not yet verified.
  AC-3 not yet verified: no `pr_watch.py` change exists; needs the real-subprocess test.
  AC-4 not yet verified: needs 0.23.0 versus candidate run on one fixture.
  AC-5 base counts measured (41, 48, 5495); the empty candidate diff is not yet verified.
  AC-6 not yet verified: loud-failure and no-folder fixtures not written.
  AC-7 current evidence: prototype over 149 additions flagged 55, 5 of 71 from 2026-10-14 on, including the three; rerun with the shipped mode not yet verified, and timing before the worker reads is not measured.

### Summary

The check cannot be forced before `dispatch build` from this package (Spacedock has no pre-dispatch hook, ADR 0014 hit the same wall), so the design adds an automatic run at FO's idle hook: `pr_watch.py tasks` prints a `next:` line when the newest committed record still holds a bare package script name, adding no README or mod words. Two decisions go to the Captain: the run point (recommended: the idle-hook line over a validation-time fold or waiting for Spacedock) and whether to ask Spacedock for a pre-dispatch hook. A prototype replay found all three named records; timing against the worker's read is unmeasured.
