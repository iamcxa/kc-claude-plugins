# dev2 laws

Invariants of the committed `spacedock-state` history, checked by `<package>/scripts/laws_check.py`
and listed here so a reader can see what each law is for. Each run judges only the events the commits of
one push add, the `before..after` range GitHub reports for a push to the state branch, each read at its own
commit. A violation is reported in the run of the push that added it; the next push is judged on its own
commits, so its run is green again whether or not the violation was repaired. The run reports; it does not
block `merge guard`, a dispatch or a push. `<package>/scripts/test_laws_check.py` fails when this list and
the runner's registry differ.

## L1 observer-before-sentinel

- **Rule.** When the workflow README lists `learn`, an observer report, or its `observer not run: <reason>`
  line, is committed no later than the commit that writes `pr: pr-merge:<N>` in a task's frontmatter.
- **Event.** A commit in the range where a top-level or `_archive/` `<slug>.md` has a parsed `pr:` sentinel
  and its first parent's file, followed through a rename, did not. The sentinel is read from parsed
  frontmatter, not by substring. An archive move that leaves `pr:` unchanged is no event; a `merge guard --rework`
  that clears `pr:` and a later sentinel are two events.
- **Judged by.** `<package>/scripts/observer_check.py <state> <slug> --rev <that commit>`.
- **Bit.** An adopter's first officer archived a task with no observer report (2026-10-14).
  `observer-before-merge-guard` introduced the rule; its report is committed one commit before its sentinel.
- **Bounds.** The README is the one supplied at run time, so a re-run or a local run given a different README
  can judge the same range differently.

## L2 dispatch-record-complete

- **Rule.** Each dispatch record has every part `<package>/scripts/dispatch_records.py` requires and names no package script
  without its directory.
- **Event.** A commit in the range that adds a `dispatch/<name>.md` record, status added, or renamed from a path
  that is not a dispatch record. A record added, then corrected or deleted in a later commit of the same push, is
  judged as added; a record deleted and added again is judged at each add. Archiving a task or renaming its folder
  is no event.
- **Judged by.** `<package>/scripts/dispatch_records.py <task folder>` and
  `<package>/scripts/dispatch_records.py --names <records>`, both over the record and its folder as committed at that commit.
- **Bit.** Measured 2026-10-16 on this repository's state branch: 15 missing parts in 10 of 48 records
  added after commit `49da5ddb` at its commit `e73634e6` (4 bare script names, 7 without the completion recipient
  `main`, 4 without an absolute `Package root:`).
