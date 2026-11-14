---
id:
title: The private working repository's second laptop cell passes its selfcheck on a fresh clone and says which entries it could not check
status: validation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree: .worktrees/spacedock-ensign-private-cell-selfcheck-passes-on-a-fresh-clone-poc
pr:
gates:
    version: 1
    records:
        - id: gate:private-cell-selfcheck-passes-on-a-fresh-clone-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:private-cell-selfcheck-passes-on-a-fresh-clone-poc-backlog-1
              briefing:
                id: briefing:private-cell-selfcheck-passes-on-a-fresh-clone-poc:backlog:attempt-1:revision-1
                digest: sha256:d60d609f5b565d908092d85bb63baf775817973bdd48819fbc7e1119c62fb6ac
                room-ref: ./private-cell-selfcheck-passes-on-a-fresh-clone-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:private-cell-selfcheck-passes-on-a-fresh-clone-poc:backlog:1
                briefing: briefing:private-cell-selfcheck-passes-on-a-fresh-clone-poc:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T11:32:29.518367Z"
                decision: approve
                reason: Ordered by the reform session under the Captain's grant as the first step after the two-hour scope; small, private-repository maintenance; no public merge or outward action.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 2 as continued by the reform session, Paseo messages c998ccf1-0e7d-4197-9636-a25f2818c562 and c271575d-82b3-4a1b-a945-c7df85cea4da
              application:
                target-stage: implementation
                state: consumed
        - id: gate:private-cell-selfcheck-passes-on-a-fresh-clone-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:private-cell-selfcheck-passes-on-a-fresh-clone-poc-validation-1
              briefing:
                id: briefing:private-cell-selfcheck-passes-on-a-fresh-clone-poc:validation:attempt-1:revision-1
                digest: sha256:3512521790d628800ff1d0b85860a902ab3a0a13165fbbbd70645b06ee0993a7
                room-ref: ./private-cell-selfcheck-passes-on-a-fresh-clone-poc/review/validation/briefing-1
started: 2026-11-14T11:33:09Z
---

The clean branch pushed to the private working repository's remote on 2026-11-14 carries a cell whose `selfcheck` exits 1 on a fresh clone: nine of its fixture entries point at raw laptop outputs that are deliberately not carried. A check that fails on a fresh clone is a trap for whoever clones it next.

## Scope

- Source: the reform session's rulings under the Captain's standing grant to the second dev2 FO (Paseo 26215d96, messages c998ccf1 and c271575d, 2026-11-14): "carry a variant whose selfcheck exits 0 on the remote copy and SAYS which entries it could not check and why (printed, not skipped in silence), re-scan, push", first in the order after the two-hour scope. Admission is recorded by FO under that grant.
- Outcome: on a fresh clone of the private working repository's remote main, every cell's `selfcheck` exits 0; for the second laptop cell it prints, by name and count, the entries it could not check and why (their raw outputs stay on the laptop), and it still fails when a carried fixture's grade is wrong. On the laptop, where the raw outputs exist, the same cell still checks all of its entries.
- The deliverable is in the private working repository, named here only as that and pinned by commit SHA; nothing from a run or a case is written to this state branch. Before the push the range is scanned for the identifier classes and token shapes and reads zero; FO pushes.
- bite: a fresh clone's `selfcheck` exit 1 (FO and worker observation, 2026-11-14, reported to the reform session before the push).
- consumer: whoever next clones the private working repository, the reform session first.
Non-goals: carrying any raw run output to the remote; changing any grader, reading or committed table; the seed files' pre-existing identifier lines (recorded separately as a blocker for any public release).
Budget: 1 implementation and 1 validation cycles
Stop condition: the variant cannot exit 0 without hiding a real fixture failure; a non-zero scan before the push; a suspected key.

## Acceptance criteria

**AC-1**: On a fresh clone of the remote main after the push, `selfcheck` exits 0 for every cell and prints which entries of the second laptop cell were not checked and why; with one carried fixture's expected grade altered in a scratch copy it exits 1.
Verified by: the validator's own fresh clone, the three commands' exit codes and the printed count; the mutation run in scratch.

**AC-2**: The pushed range adds no raw run output and scans at zero in every identifier class and for token shapes.
Verified by: the scan's counts over exactly the pushed range and a listing of the changed paths, re-run by the validator.

## FO alignment

Alignment: not needed before implementation: the outcome is the reform session's sentence; the backlog gate records it under the grant.
Release review: not needed: maintenance of a private measurement repository.

## Stage Report: implementation

- DONE: On a new branch from the private working repository's remote main: the second laptop cell's selfcheck exits 0 on a tree without the raw laptop outputs and prints, by name and count, which entries it could not check and why; with the raw outputs present (the laptop branch) it still checks every entry; a carried fixture with a wrong expected grade still makes it exit 1 (shown by a mutation in scratch)
  Branch `selfcheck-fresh-clone` in the private repository, base a1068423, candidate a836cda26e38419ad4c138fb32ef7999b4d03eb9 (one commit, one file: `behaviour/run_cell.py`, +10/-1). A fresh clone of the candidate: all three cells exit 0; the second laptop cell prints `NOT CHECKED: 9 of 12 entries` and the nine names under `falsifiers/old-nine`; the other two print none.
  Rule: an entry is not checked only when its whole fixture folder is absent from the tree; a missing file inside a present folder still errors, so a deleted carried fixture exits 1. Laptop case (old-nine copied from the laptop branch into a scratch copy): 9 old-nine entries graded, 0 NOT CHECKED lines, exit 0. Mutation 1 (flagged fixture's expected verdict set to FAIL in a scratch copy): prints EXPECTED, `selfcheck FAILED`, exit 1. Mutation 2 (carried `falsifiers/flagged.md` deleted in a scratch copy): exit 1.
  Limit: `prepare` calls the same check, so on a fresh clone it passes with the nine unchecked; it already could not check them there.
- DONE: The scan over exactly the range to be pushed reads zero in every identifier class and for token shapes, and the changed-path listing shows no raw run output; report the counts and the candidate SHA to FO, who pushes. Do not push
  Range `origin/main..selfcheck-fresh-clone`, 10 added lines. Counts: private-repo 0 of 4 patterns, private-slug 0 of 1092, tailnet-host 0 of 1, home path 0, git email 0, host names 0, token shapes (key prefixes, PEM, JWT, long hex/base64) 0. Changed paths: `behaviour/run_cell.py` only. Scan reads commit author, committer and message as well as the diff.
  Author and committer on the candidate are `Kent <noreply@invalid>`, not the configured git email: the configured email scanned as one hit, so I replaced it. FO may re-author if the configured address is acceptable on that remote. Not pushed; no pull request prepared. roborev not run: private repository.
- DONE: Scratch closed
  `scratch.py close` removed the scratch folder (11042144 bytes) and archived 0 evidence files; every run output is private, so `Not archived (private): selfcheck outputs and mutation runs; reproduce: run selfcheck on each cell in a fresh clone of the candidate`. My scratch worktree went with it; I pruned its entry, and the branch is intact at the candidate.

### Summary

The second laptop cell's `selfcheck` now exits 0 on a fresh clone, naming the nine entries it cannot check. It still grades all twelve when the raw outputs are present, and still fails on a wrong expected grade or a deleted carried fixture. Candidate a836cda is scanned clean and unpushed; FO pushes. AC-1's post-push fresh clone is the validator's.

## Stage Report: implementation

- DONE: Re-make the candidate commit with the repository's configured git identity as author and committer, with the same tree and message, on the same branch; report the new SHA and confirm the tree is byte-identical to the old candidate's.
  New candidate b61e8f4be42d50e605d4e011401dcfec1b4b28b2 on `selfcheck-fresh-clone`, parent a1068423 (origin/main). `git rev-parse a836cda2^{tree}` and `b61e8f4b^{tree}` both read 7dbfd28703aa2c1e7f0eae3ff8be20cbcfc25ec1. Message compared byte for byte with the old one: identical. Author and committer email equal `git config user.email` of that repository (checked by string equality, not printed).
- DONE: Change nothing else.
  Changed path against origin/main is still `behaviour/run_cell.py` only; working tree clean. A fresh clone of the branch: all three cells' `selfcheck` exit 0. Not pushed. Identity-change findings go to FO, not into a commit, from now on. An unreferenced intermediate commit fb07f1f8 (message had one extra trailing newline) was created and replaced; nothing points at it.
- DONE: Append a complete new stage report that supersedes the earlier one.
  The scan read zero in every class on a836cda2 with the configured email replaced. The tree and message are unchanged; the one difference is the configured email now appearing as author and committer, as ruled. The scan was not re-run on b61e8f4b.

### Summary

This supersedes the earlier report. The candidate is now b61e8f4be42d50e605d4e011401dcfec1b4b28b2 with the repository's configured identity; the tree matches a836cda2 exactly. All other results of the earlier report (selfcheck on fresh clone, laptop and mutation runs, scan counts) stand, since they depend only on the tree and message. Not pushed; FO pushes.

## Stage Report: validation

- DONE: An independent verdict on AC-1 from your own fresh clone of the private working repository's remote main at b61e8f4be42d50e605d4e011401dcfec1b4b28b2: `selfcheck` for each of the three cells with exit codes; the second laptop cell prints which entries it did not check and why, by name and count; in a scratch copy, one carried fixture's expected grade altered makes it exit 1, and the old suppression is not possible for a folder that is present with a file missing
  AC-1 PASSED. Fresh clone HEAD b61e8f4b, parent a1068423. Exit codes: first laptop cell 0, second laptop cell 0, third cell 0 (evidence/validation-1/run-summary.md). The second laptop cell prints `NOT CHECKED: 9 of 12 entries, because their folder is not in this tree (...; raw outputs are not carried)` and then 9 named lines; the other two print none (same file).
  Mutations in scratch copies of the clone, all exit 1: M1, one carried entry's expected verdict flipped (prints `EXPECTED`, `selfcheck FAILED`); M2, the un-carried folder present but empty; M3, that folder with 1 of 9 files; M4, one carried file deleted with its folder present (M2 to M4 fail on `No such file or directory`). M6, nine stand-in files in that folder: 9 entries graded, 0 not checked, so a present folder is checked, never skipped (run-summary.md).
- DONE: An independent verdict on AC-2: the listing of paths changed in the pushed range and a scan of the range's patch and commit message for the identifier classes and token shapes, counts only; no raw run output on the remote main's tree (list the results folders present)
  AC-2 PASSED. Range a1068423..b61e8f4b, 1 commit; changed paths: `M behaviour/run_cell.py` only. Scan input: 10 added and 1 removed lines, matching the commit stat. Patch and message: private-repo 0 of 4, private-slug 0 of 1092, tailnet-host 0 of 1, home path 0, configured git email 0, host names 0 (of 4), key-prefix, PEM, JWT, long hex 0 (evidence/validation-1/scan-counts.txt). Author and committer metadata carry the configured git email (2 hits), which is metadata, as ruled. The scanner, given one planted value per class, reads 1 in each class (scan-falsifier.txt).
  Results folders on main: `behaviour/results/` with two cell folders, each holding only `table.md`, both added before the range. All 190 tracked files are listed. The 40 folders the runner would treat as runs (holding `manifest.json`) are synthetic fixtures (`"fixture": true`, at most 390 bytes, a manifest and nothing else). No raw run output is in the tree (run-summary.md).
- DONE: A minimal acceptance script FO can run, the limits of what you checked (including that `prepare` passes on a fresh clone with entries unchecked), and unverified obligations
  Script: `bash evidence/validation-1/acceptance.sh <owner/name of the private working repository> b61e8f4be42d50e605d4e011401dcfec1b4b28b2`. It needs a `gh` login and a working SSH key for that remote (a run with an empty environment failed to clone), plus the repository name from FO. It clones into a fresh `/tmp/acc-*` folder and removes it on exit. It exits 0 even when an expectation fails, so read its lines. Expected: step 1, main equals the SHA. Step 2, three cells each `exit 0`, one cell with `not-checked=9`, the others `not-checked=0`. Step 3, `exit 1`, last line `selfcheck FAILED`. Step 4, `exit 1`. I ran it in a fresh bash shell and got exactly those lines. It prints cell folder names to the terminal, never to a file. It does not cover the laptop case, the scan or the tree listing.
  Limits: `prepare --dry-run` on the second laptop cell exits 0 with the same 9 entries not checked (run in a scratch copy with an empty results folder; nothing was written). So on a fresh clone, prepare passes without checking those entries; it could not check them there before either. comment_ratio.py exit 0 (10 code lines, 0 comment lines). doc_impact.py exit 0, with 0 documents listed. dispatch_records.py exit 0, 3 complete. role_triggers.py exit 0. adr_lint.py docs/adr --since a1068423 exit 2: the repository has no docs/adr. That is a configuration error returned to FO, not a pass; the range adds no ADR. design_surfaces.py not run (does not apply). roborev not run (per the dispatch).
  Unverified obligation: the laptop case with the real raw outputs (all 12 entries graded, exit 0) rests only on the implementation report. My M6 used stand-ins and shows only that a present folder is graded. Not archived (private): selfcheck logs, entry names, mutation outputs and the range text; reproduce: the acceptance script above, then `git log -p a1068423..b61e8f4b` in its clone.
  scratch.py close output: `Scratch removed: /private/tmp/dev2/kc-claude-plugins-0a31751399576cc5/private-cell-selfcheck-passes-on-a-fresh-clone-poc/validation-1 (14791102 bytes)` and `Evidence: evidence/validation-1/ (4 files, 6.6 KiB)`, exit 0. The clone was removed with the scratch folder.
- F1 Deferred risk: an entire carried fixture folder that is missing turns its grade entries into `not checked`. M5 (the second laptop cell with its whole carried fixture folder deleted) printed 12 of 12 not checked, and it exited 1 only because three transcript fixtures in that same folder expect at least one breach. Each of the two laptop cells keeps such transcript fixtures beside its grade fixtures, and the third cell uses a different selfcheck. So no current cell exits 0 this way. It becomes material if a cell's carried grade fixtures sit in a folder with no fixture that must scan non-zero.
- F2 Polish: the second laptop cell's reading still says the first reading's outputs are kept as a fixture in the folder the remote does not carry. The line predates the range, and changing a reading is a Non-goal. The new printed reason now says the folder is not carried.

No boundary crossing: the range changes one runner file, writes no state, adds, edits or deletes no migration file and opens no external seam. Goal sufficiency: AC-1 and AC-2 hold on the fresh clone. Minimal necessity: the 10 added lines are the absent-folder skip (needed for exit 0) and the printed list (needed for "says which"), and nothing else.

### Summary

Recommend PASSED on AC-1 and AC-2 at b61e8f4b on the remote main. All three cells exit 0 on a fresh clone; the second laptop cell names its 9 unchecked entries; a wrong expected grade or a missing file in a present folder still exits 1. The range scans at zero and adds no raw output. For FO: adr_lint exit 2 (no docs/adr folder), the laptop run rests on the implementation report alone, and one Deferred risk (F1).
