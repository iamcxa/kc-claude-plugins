## Number guards

Applies when the task's `Surfaces:` includes `db`, or the task lands an ADR, including one first required by a ruling in a worker report or mid-stage feedback, whose number FO reserves before the next dispatch; the POC bullet below applies to every `poc` task.
`python3 <package>/scripts/number_guards.py` takes `trunk:`, the optional `migrations-path:`
(the adopter's migration directory) and `adr-path:` (default `docs/adr`) from this workflow's README
frontmatter (`--workflow-dir <workflow-dir>`) and a task's numbers and applied
deploys from its `## Number guards` section; `--help` lists the flags.

- **Applied.** A migration in a commit recorded `Applied at:` is frozen for the task:
  edit, delete and renumber fail `check`. `Applied: none as of <sha>` records that
  nothing was pushed up to that commit; a validator that finds none of `Applied at:`,
  `Not applied:` or `Applied: none` reports the missing record to FO instead of
  re-checking deploys. A task with no `Migration:` line owes none of these.
- **Check.** `python3 <package>/scripts/number_guards.py check --workflow-dir <workflow-dir> --task <task file>`
  runs at implementation exit, at validation and, after `git -C <repo> fetch`, on the PR
  head before FO asks for merge. Exit 2 is a configuration error, which returns to FO
  as a hold.
- **POC.** A task whose recorded `profile` is `poc` adds, edits and deletes no migration
  file and reserves no number. When the README declares `migrations-path:`, `check` runs
  for it at the same three points, and exit 1 `FAIL R6` lists each path under that
  directory that differs from the merge-base. A `FAIL R6` crosses the POC boundary
  (a schema change persists across sessions): the worker records
  `boundary-crossed: persistent-state` naming the path, and the task is not repaired in
  place.

