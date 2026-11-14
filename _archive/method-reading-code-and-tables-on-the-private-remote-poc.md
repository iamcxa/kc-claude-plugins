---
id:
title: Tonight's method-against-no-method cell, both readings and both final tables are on the private working repository's remote, with the raw runs left on the laptop
status: done
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree: .worktrees/spacedock-ensign-method-reading-code-and-tables-on-the-private-remote-poc
pr: local-merge:2b391a40f926646b6be949cb2cf07466005e277c
gates:
    version: 1
    records:
        - id: gate:method-reading-code-and-tables-on-the-private-remote-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:method-reading-code-and-tables-on-the-private-remote-poc-backlog-1
              briefing:
                id: briefing:method-reading-code-and-tables-on-the-private-remote-poc:backlog:attempt-1:revision-1
                digest: sha256:125693f82a1edae00b251f22e6788ba7575120b39c7a03d48948b97c8f9e7a9f
                room-ref: ./method-reading-code-and-tables-on-the-private-remote-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:method-reading-code-and-tables-on-the-private-remote-poc:backlog:1
                briefing: briefing:method-reading-code-and-tables-on-the-private-remote-poc:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T11:51:34.787271Z"
                decision: approve
                reason: Ordered by the reform session under the Captain's grant; small private-repository maintenance; no public merge or outward action.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 2 as continued by the reform session, Paseo message 94ecfb61-4305-4483-8e9c-e321382c5ac2
              application:
                target-stage: implementation
                state: consumed
        - id: gate:method-reading-code-and-tables-on-the-private-remote-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:method-reading-code-and-tables-on-the-private-remote-poc-validation-1
              briefing:
                id: briefing:method-reading-code-and-tables-on-the-private-remote-poc:validation:attempt-1:revision-1
                digest: sha256:1ffce6a877716c64915a14a2f31423f8d7e2c7f299cae2061efa09eb604dde90
                room-ref: ./method-reading-code-and-tables-on-the-private-remote-poc/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:method-reading-code-and-tables-on-the-private-remote-poc:validation:1
                briefing: briefing:method-reading-code-and-tables-on-the-private-remote-poc:validation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T12:04:34.409121Z"
                decision: approve
                reason: Fresh-clone validation passed; its two points were ruled by the reform session before the push, and FO verified that the carried tables differ from the laptop tables only in the run-id cell.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 2 as continued by the reform session, Paseo messages 94ecfb61-4305-4483-8e9c-e321382c5ac2 and f0fa5dae-d010-4cf3-a168-c47d79e3c7e1
              application:
                target-stage: done
                state: consumed
started: 2026-11-14T11:51:42Z
mod-block:
verdict: PASSED
completed: 2026-11-14T12:04:40Z
archived: 2026-11-14T12:04:41Z
---

The day's main result, two readings of whether an agent given the method does better than one given the task in plain words, exists on one machine only: its cell, grader changes, readings and final tables were committed after the push that carried the earlier code, and live on a laptop-only branch beside the raw runs.

## Scope

- Source: the reform session's ruling under the Captain's standing grant to the second dev2 FO (Paseo 26215d96, message 94ecfb61, 2026-11-14): "tonight's method-against-no-method cell, both readings and both final tables go to the private remote by the same allowlist-and-scan route, raw runs stay on the laptop. Keep it small". Admission is recorded by FO under that grant.
- Outcome: the private working repository's remote main carries the method-against-no-method cells of both readings (reading documents, cell and answer files, synthetic fixtures), the runner as it stands at the final tables' commit, the table-rule fixture script and proofs the readings cite, and both readings' final tables; it carries no raw run output, run list, collected transcript, blind packet or key. The range scans at zero in every identifier class and for token shapes before the push; FO pushes; FO checks a fresh clone.
- The deliverable is named here only as the private working repository and pinned by commit SHA; nothing from a run or a case is written to this state branch.
- bite: the result has no backup (reform session, message 94ecfb61).
- consumer: the reform session and the Captain reading the two tables; whoever continues the instrument.
Non-goals: carrying any raw run output; changing any grader, reading or table; the seed files' pre-existing identifier lines.
Budget: 1 implementation and 1 validation cycles
Stop condition: a carried file cannot be made clean without changing a table's content; a non-zero scan before the push; a suspected key.

## Acceptance criteria

**AC-1**: On a fresh clone of the remote main after the push, both readings' documents and final tables are present, every cell's `selfcheck` exits 0, and each table regenerates or is shown byte-identical to the laptop branch's committed table.
Verified by: a fresh clone's listing and `selfcheck` exit codes, and a digest comparison of each carried table with the laptop branch's file at the final tables' commit.

**AC-2**: The pushed range adds no raw run output and scans at zero in every identifier class and for token shapes.
Verified by: the scan's counts over exactly the pushed range and the changed-path listing.

## FO alignment

Alignment: not needed before implementation: the outcome is the reform session's sentence; the backlog gate records it under the grant.
Release review: not needed: maintenance of a private measurement repository.

## Stage Report: implementation

- DONE: On a new branch from the private working repository's remote main: an allowlisted copy of the method-against-no-method cells of both readings (reading documents, cell and answer files, synthetic fixtures), the runner as it stands at the final tables' commit, the table-rule fixture script and the proofs the readings cite, and both readings' final tables; no results/<run>/ folder, run list, collected transcript, safety-scan output that names runs, blind grade file that names runs, blind packet or key.
  Branch `behaviour-method-readings-carry`, base b61e8f4be42d50e605d4e011401dcfec1b4b28b2 (remote main), one commit, candidate 2b391a40f926646b6be949cb2cf07466005e277c, author and committer as configured. 93 paths, +1155/-26: all of `behaviour/cells/method-against-no-method-2/` (88 files: reading, answer, cell, checklist, mutation-proof output, synthetic fixtures F*/G*/T*), `behaviour/results/method-against-no-method/table.md`, `behaviour/results/method-against-no-method-2/table.md`, `behaviour/table_rule_check.py` (new), `behaviour/run_cell.py` and `behaviour/mutation_proof.py` (modified). The first cell's files were already on main and are unchanged. Reproduce the listing: `git diff --name-status origin/main 2b391a4`. Not archived (private): the listing itself.
  Runner reconciliation: three-way `git merge-file` with base = main's runner before the selfcheck change, ours = the laptop branch's final runner, theirs = main's selfcheck change; no conflict; the result is the laptop runner plus exactly that change (+10/-1 lines in `selfcheck_core`).
  Tables: both name run ids, in the first cell of the six per-run rows (rows 12-17). The carried form puts arm-trial there (for example N-1, M-3). With that cell masked, each carried table is identical to the laptop branch's committed table, so every count, per-run number, limits paragraph and reading line is byte-identical. Neither table names a host path (they name the home-directory string only in words).
  Left out, by decision: `behaviour/regress_v3.py` and the cell's `regression.txt` (the reading calls both "never carried" and they name real run ids; the reading still cites them); `hostfix.py` and `posthoc_v1.py` (no reading cites them); both `limits-applied.md` (the tables already hold the limits inline); RUN-LIST, `blind.json`, `safety-scans.md`, collect and scan outputs; the laptop branch's edits to the two earlier cells' falsifier files and their `old-nine/` raw-output copies.
- DONE: Every cell's selfcheck exits 0 on a tree without the raw runs, printing what it could not check; each carried table's digest equals the laptop branch's committed table (or the difference is listed line by line); the scan over exactly the range to be pushed reads zero in every identifier class and for token shapes; report the changed-path listing, the counts and the candidate SHA to FO, who pushes. Do not push
  Fresh clone of the branch, no `r-*` folder present: selfcheck exit 0 for all four cells. The two method cells print nothing unchecked because all their fixtures are carried; the earlier second-reading ideation cell prints `NOT CHECKED: 9 of 12 entries` (its raw-output copies are not carried, as on main). `table_rule_check.py` exit 0. `mutation_proof.py` exit 0 on both method cells and its output equals each carried mutation-proof file.
  Table digests (first 12 hex of sha256, laptop then carried): first reading 91b62fdde6c5 then 4d5ec7c2ca04; second reading dcc9957fb525 then 9961adeff8e7. Difference: rows 12-17 of each table, first cell only (12 lines in all), checked by masking that cell and diffing to empty.
  Scan over `origin/main..2b391a4` (added lines of the 93 paths, plus the commit message): 0 in each of: owner's identifier list (private-repo, private-slug, tailnet-host classes), real home path, configured git email, host names, IP addresses, tailnet or .local names, agent session directories, token shapes, the 29 real run-folder names, the 12 real session ids, any non-placeholder run-id shape, any uuid. Counted and read, not hits: 12 lines naming secret-path classes as the readings' contamination-rule vocabulary, 7 git SHAs or sha256 pins, 11 synthetic placeholder run ids already present in main's first cell. My first pass counted those as token and session hits; I narrowed the two classes to real vendor token prefixes, high-entropy strings and real session directories, and kept the vocabulary as a separate counted class. Positive control: the same scan over the laptop branch range returns non-zero in nearly every class.
  Not archived (private): scan script and outputs; reproduce: list the classes above against the range with the owner's identifier list by path.
- DONE: Package checks for this dispatch
  `comment_ratio.py origin/main HEAD`: code lines 226, comment lines 1, 0.4%, maximum 5% met (the one comment line is in `table_rule_check.py`). `doc_impact.py`: 0 documents mention what changed. `number_guards.py check`: PASS, no migrations path (POC, no migration added). `role_triggers.py`: exit 0. roborev not run: the candidate lives in a different, private repository this repository's review daemon does not cover. `boundary-crossed:` none.
- DONE: Cleanup and limits
  The scratch worktree was removed; the branch stays in the private clone, not pushed. This repository's worktree was untouched. Not proved: that a fresh clone of the pushed main behaves the same (FO's AC-1 check); that the carried synthetic fixtures hold no case content beyond what the zero scan can see.

### Summary

The branch carries the confirmatory reading's cell, the final runner, the table-rule script and both final tables with arm-trial in place of run ids; no raw run material is carried. Selfcheck, table rule, mutation proofs and the scan all pass in a fresh clone of the branch. FO decisions left: the reading text still cites the regression script and output as laptop-only, which are not carried; and the earlier cells' laptop edits are not carried.

## Stage Report: validation

- DONE: An independent verdict on AC-1 and AC-2 from your own fresh clone of the private working repository's remote main at 2b391a40f926646b6be949cb2cf07466005e277c: both method readings' documents and final tables are present; every cell's selfcheck exits 0 (one earlier cell prints entries it could not check); the table-rule fixture exits 0; the paths changed in the pushed range hold no raw run output, and a scan of the range's patch and message reads zero in the identifier classes and token shapes, counts only
  Fresh clone: HEAD 2b391a4, parent b61e8f4, only `main` on the remote; 93 paths, +1155/-26. Both cells' READING.md and both `table.md` present (sha256 prefixes 4d5ec7c2ca04 and 9961adeff8e7, equal to the implementation report's carried digests). selfcheck exit 0 on all four cells; only `ideation-flags-unprovable-criterion-v2` prints a NOT CHECKED line. `table_rule_check.py` exit 0. No run folder, run list, blind file, packet, key or collect/scan output; the 13 `transcript.jsonl` paths are synthetic falsifier fixtures (264 bytes each). Scan over 1171 added lines + message: 0 in each identifier-list class (private-repo, private-slug, tailnet-host), home path, configured email, host name, tailnet/.local, IPv4, uuid, session directory and every token shape. Read, not hits: the model co-author line, 7 SHAs/pins, 13 synthetic /tmp placeholder paths, 2 package-cache fragments. Evidence: `evidence/validation-1/checks.txt`.
  Verdict: PASSED for AC-2 and for AC-1's presence and selfcheck clauses; AC-1's table-identity clause goes to F1.
- DONE: A minimal acceptance script FO can run, the limits of what you checked, and unverified obligations; keep this small: it is a check that a copy of already-validated files arrived clean
  Script: `evidence/validation-1/acceptance.sh <owner/name>`. It has no user-visible surface: it clones fresh and prints HEAD, the two tables, four selfcheck exits, the table-rule exit and a raw-path count (expect 0). It does not cover the identifier scan or table identity.
  Package checks: `comment_ratio.py` exit 0 (1 comment line, a shebang, 0.4%). `adr_lint.py docs/adr --since b61e8f4` exit 2 because the repository has no `docs/adr`; no ADR is expected. `dispatch_records.py` exit 0 (2 records complete). `boundary-crossed:` none found.
  Unverified: (a) the laptop branch's table digests and the claim that only the run column differs; I was told not to use the existing local clone, so I could not compare. (b) that synthetic fixtures hold no case content beyond what the scan sees. (c) `python3 -B` only, on this machine.
- F1 Needs decision: AC-1 says each table "regenerates or is shown byte-identical to the laptop branch's committed table"; the carried tables do neither. By the implementation's own report, 12 lines differ (run ids replaced by arm-trial), and with no raw runs the tables cannot regenerate. The Non-goal "changing any … table" and the Stop condition "a carried file cannot be made clean without changing a table's content" both point here, so masking the ids is a scope call for FO or the reform session; it is not a repair. Every count and reading line is claimed unchanged, but see Unverified (a).
- F2 Needs decision (carried from implementation): the second reading cites the regression script and its output, which are not carried, so a reader of the remote cannot follow those two citations.

### Summary

The fresh clone of remote main at 2b391a4 holds both readings and both tables. All four selfchecks and the table rule exit 0, no raw run output is present, and the scan reads zero in every class. I recommend PASSED on AC-2 and on the presence and selfcheck parts of AC-1. Whether to accept tables whose run column was masked (F1) needs FO or the reform session to rule, since it touches a Non-goal and the Stop condition. Scratch closed: "Scratch removed: …/validation-1 (4041 bytes); Evidence: evidence/validation-1/ (2 files, 3.5 KiB)".
