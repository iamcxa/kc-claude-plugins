---
name: kc-journey-progress
description: Use when explicitly refreshing release story development progress from local Spacedock tasks, optionally drawing the observation on the journey canvas. Drawing alone uses kc-journey-map.
---

Refresh local task progress once, then optionally draw that observation. Resolve this
plugin root from this skill location. Use its existing canvas setup from
`../kc-journey-map/references/canvas.md`; Node >=22.13 and the plugin dependencies
are required. The optional reader also requires `spacedock` on PATH.

```bash
node <plugin-root>/lib/journey-progress.mjs <journey.yaml> --workflow-dir <workflow-dir>
node <plugin-root>/lib/journey-progress.mjs <journey.yaml> --workflow-dir <workflow-dir> --draw <room> --pages story-map,journey-board
```

Omitting `--pages` draws the story map. Refresh-only prints JSON. `JOURNEY_API`
selects the existing canvas endpoint. Exit 1 accompanies unverified observations
or a failed draw; exit 2 reports invalid arguments/input. A failed draw retains the
computed observation in the error output, without claiming that it was drawn.

## Declare the required work in its existing tasks

Each opted-in task has scalar `journey`, `journey-release`, and `journey-story`
matching explicit journey/release/story IDs in the journey file. Positional IDs
and duplicate story IDs cannot establish completion. Legacy `sprint` is ignored.
One existing member task carries the complete declaration:

```yaml
journey: example-journey
journey-release: first-release
journey-story: inspect-result
journey-required-tasks: '["full-stored-task-id", "another-full-stored-task-id"]'
journey-mapping-complete: true
```

The task scope owner confirms that nonempty list is exhaustive and includes the
declaring task, updating that same declaration when required scope changes. Other
members carry the tuple, without duplicating the declaration. Full stored IDs
come from `spacedock status --workflow-dir <dir> --resolve <slug> --archived --json`
(`stored_id`), not display prefixes. The reader does not write this metadata.

`lib/progress.mjs` requires one confirmed declaration, unique full IDs, exact
matching membership, and readable required records. Missing/extra tasks, partial
or conflicting declarations, unavailable reads and detected drift are unverified.
Archived tasks participate; literal `done` completes a task, and reopening it
reduces the next explicit refresh. Work omitted from both the declaration and
metadata cannot be discovered; this is a scope assertion, not authenticated approval.

## Read the observation

Release ratios count complete stories, including unknown stories in the denominator.
See `../kc-journey-map/references/cell-contract.md` for the three development color
meanings and acceptance boundary. Canvas input/readback lives in `canvas.md` in
that same reference directory. The observation has full task IDs, local source and
time; it is bounded by a 30-second/8-MiB-per-response reader and a final listing
comparison, not an atomic filesystem snapshot. Retry by explicitly refreshing.
No progress cache, background refresh, or task/journey status write is performed.
Exercise the contract with `node --test <plugin-root>/lib/progress.test.mjs`.
