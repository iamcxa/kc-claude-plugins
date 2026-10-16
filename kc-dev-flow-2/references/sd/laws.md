# dev2 laws

Invariants of the committed `spacedock-state` history, checked by `<package>/scripts/laws_check.py`
and listed here so a reader can see what each law is for. A law judges only events in commits that are
strict descendants of the anchor commit the adopter names for it. A violation is a committed fact and
cannot be repaired, so it stays red until the anchor moves past it. The run reports; it does not block
`merge guard`, a dispatch or a push. `<package>/scripts/test_laws_check.py` fails when this list and the runner's
registry differ.

## L1 observer-before-sentinel

- **Rule.** When the workflow README lists `learn`, an observer report, or its `observer not run: <reason>`
  line, is committed no later than the commit that first writes `pr: pr-merge:<N>` in a task's frontmatter.
- **Event.** The first such commit per task, found by reading each candidate commit's parsed frontmatter, not
  by substring. Tasks are the top-level and `_archive/` `<slug>.md` paths whose history writes a `pr:` sentinel, live, archived or since deleted.
- **Judged by.** `<package>/scripts/observer_check.py <state> <slug> --rev <that commit>`.
- **Bit.** An adopter's first officer archived a task with no observer report (2026-10-14).
  `observer-before-merge-guard` introduced the rule; its report is committed one commit before its sentinel.
- **Bounds.** A later `merge guard --rework` that rewrites `pr:` is not judged again.

## L2 dispatch-record-complete

- **Rule.** Each dispatch record has every part `<package>/scripts/dispatch_records.py` requires and names no package script
  without its directory.
- **Event.** A `dispatch/<name>.md` record, live, under `_archive/` or since deleted, whose adding commit is after the anchor.
  Each `--diff-filter=A` commit with rename detection on is one event, so a record deleted and added
  again is judged at both adds, and archiving a task does not make its old records new.
- **Judged by.** `<package>/scripts/dispatch_records.py <task folder>` and
  `<package>/scripts/dispatch_records.py --names <records>`, both over the record and its folder as committed at the adding commit, so a later correction or deletion does not clear it.
- **Bit.** Measured 2026-10-16 on this repository's state branch at its commit `e73634e6`: 15 missing parts
  in 10 of 48 records added after commit `49da5ddb` (4 bare script names, 7 without the completion recipient
  `main`, 4 without an absolute `Package root:`).
