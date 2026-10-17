## FO steps: number guards

- **Reserve.** Before an implementation dispatch, FO runs `git -C <repo> fetch`, then
  `python3 <package>/scripts/number_guards.py reserve --kind migration|adr --workflow-dir <workflow-dir> --repo <repo> --task <task file>`
  once per kind the task needs, when the implementation dispatch is built and not
  earlier; a task holds one number per kind, and a task needing a second ADR or
  migration returns to FO. FO records each printed `Migration: NNNN` /
  `ADR: NNNN` line under `## Number guards` in the task and repeats the lines as
  dispatch scope notes.
- **Applied.** Before any push of a candidate to a persistent shared non-production
  environment (a database branch, or a separate hosting project such as a staging
  project whose database is that project's own production database), FO records `Applied at: <environment> <sha>`
  for the commit being pushed. When the push is rejected or the
  deploy is confirmed not to have run for that commit (the push's non-zero output,
  or the environment's own deploy record showing no deploy of it), FO replaces that
  one line with `Not applied: <environment> <sha> - <evidence>` and the migration is
  no longer frozen. Without that confirmation the line stays and the migration counts
  as applied. When FO dispatches validation and nothing was pushed for the task, FO
  records `Applied: none as of <candidate sha>`, so a task with neither line has a
  skipped record. A task with no `Migration:` line records no `Applied:` line.
- **POC marker.** FO presents the `boundary-crossed: persistent-state` marker at the
  validation gate. Without `migrations-path:` the migration rules are skipped, so a POC
  is not guarded until the README declares it.
- **Collision.** When two tasks hold one migration number (`check` reports R3 or R5 on
  the later candidate; nothing compares task files), the task whose migration is applied
  keeps it and the other, unapplied task renumbers, so no reset is needed. A migration
  counts as applied when its task has an `Applied at:` line or it is on the base branch;
  when both tasks are applied and neither is on the base branch, the one that merges
  first keeps the number. The renumbering task deletes its `Migration:` line, FO runs
  `reserve` again, and the task returns to implementation with the new number in its
  scope notes. When the renumbering task has an `Applied at:` line, its environment's
  database holds a migration no branch will carry, and FO holds for the Captain: a
  database branch is reset, and a shared non-production database that cannot be reset
  (a separate project's own database) is deleted and recreated by the Captain. FO then
  replaces the line with `Not applied: <environment> <sha> - database reset` so that
  `check` accepts the renumber. A branch database is reset through the provider's own API; `adoption.md` gives one
  provider's example. This step is documented, not wrapped in a tool.

