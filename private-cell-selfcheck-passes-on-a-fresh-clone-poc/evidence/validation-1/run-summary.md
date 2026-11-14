# validation-1 run summary (counts only)

Artifact: the private working repository's remote main, fresh clone, HEAD b61e8f4be42d50e605d4e011401dcfec1b4b28b2, parent a1068423cbf5459dc17b88d3247c8df0a7f7f1dd.
Cells: A = the first laptop cell, B = the second laptop cell, C = the third cell (grader 3, separate selfcheck path the candidate does not touch).

## AC-1: selfcheck on the fresh clone

| Cell | exit | `not checked` lines | `NOT CHECKED:` summary |
| --- | --- | --- | --- |
| A | 0 | 0 | absent |
| B | 0 | 9 | `NOT CHECKED: 9 of 12 entries, because their folder is not in this tree (<one folder>; raw outputs are not carried):`, then 9 distinct entry names |
| C | 0 | 0 | absent |

## AC-1: mutations, each in its own scratch copy of the clone (cell B)

| Probe | exit | observed |
| --- | --- | --- |
| M1 one carried entry's expected verdict flipped PASS to FAIL | 1 | that entry prints `EXPECTED`, last line `selfcheck FAILED` |
| M2 the un-carried folder created empty (folder present, every file missing) | 1 | `run_cell: [Errno 2] No such file or directory` |
| M3 the un-carried folder with 1 of 9 files present | 1 | same error |
| M4 one carried fixture file deleted, its folder present | 1 | same error |
| M5 the whole carried fixture folder deleted | 1 | 12 of 12 grade entries `not checked`; the 3 transcript fixtures with min 1 scan 0 and fail |
| M6 the un-carried folder filled with 9 stand-in files | 1 | 9 entries graded, 0 `NOT CHECKED`, 9 `EXPECTED` (stand-ins grade wrong): present entries are checked, not skipped |

## AC-2: the pushed range a1068423..b61e8f4b (1 commit)

Changed paths: `M behaviour/run_cell.py` (only path).
Scan: see scan-counts.txt (patch and message: 0 in every class; author/committer metadata: the configured git email twice, by ruling metadata, not a content hit). Scanner falsifier: scan-falsifier.txt (each planted class reads 1).
Scan input: the range text holds 10 added and 1 removed lines, matching the commit stat.
Tree listing (190 tracked files, full listing read): `behaviour/results/` has two cell folders, each holding only `table.md` (committed tables, added before the range). The runner treats a folder holding `manifest.json` as a run directory; the tree has 40 such folders, all under the two laptop cells' `falsifiers/capped/` and `falsifiers/halted/`, each holding only a `manifest.json` of at most 390 bytes with `"fixture": true` (synthetic state fixtures, added before the range). No run output file (graded text or transcript of a run) is in those folders. The range adds none of these.

## Package checks

- comment_ratio.py a1068423 b61e8f4b: exit 0, `code lines 10, comment lines 0, 0.0%` (maximum not enforced under 20 lines).
- adr_lint.py docs/adr --since a1068423: exit 2, `fatal: cannot change to 'docs/adr'`; the repository has no docs/adr folder and the range adds no ADR (configuration fact for FO; no ADR expected).
- doc_impact.py a1068423 b61e8f4b: exit 0, `0 document(s) mention what changed`.
- dispatch_records.py <task folder>: exit 0, `3 dispatch record(s) complete`.
- role_triggers.py: exit 0.
- prepare <cell B> --dry-run --results <empty scratch folder>, in a scratch copy: exit 0, prints the same `NOT CHECKED: 9 of 12` block and `launch records so far: 0 of 18`; the copy's tree and the results folder stayed unchanged.
- Acceptance script, run in a fresh bash shell against the remote: exit 0; steps 1-4 printed as the script says.

Not archived (private): selfcheck logs, entry names, mutation outputs and the scanned range text; reproduce: `bash acceptance.sh <owner/name> b61e8f4be42d50e605d4e011401dcfec1b4b28b2`, then `git log -p a1068423..b61e8f4b` in that clone for the scan.
