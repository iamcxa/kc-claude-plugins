# Review a release as one journey

Read this for `review-release`. A caller (for example a workflow's first officer)
dispatches a fresh worker with this mode when a release changed: a task was admitted
into it, a scope ruling moved a story in or out, a UAT failure crossed tasks, or a
batch is about to enter implementation. Tasks are added one at a time; nothing else
checks that together they still form one complete journey. The Captain decides
membership. The worker writes no task field and no code.

Follow this order: **map first → path walk → slice check → task split.**

## 1. Update the map first

Propose the journey-file edit before any task is split: the stories and the release
goal as the Captain's words now stand, with `release` on each member. Reuse existing
story ids and `release-slicing.md`'s removal test. Present it as a reviewable change to
the map (a PR against the YAML, as an adopter already does) and wait for the Captain to
accept membership. Ask one decision at a time.

## 2. Walk the path

Walk from the person's first situation to the observable finish, one step at a time,
and for each actor who acts in it. Record one row per step and actor:

| Step | Actor | Observable outcome | Identity | Context | Shown | Story | Task or `none` | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Fill the three middle columns from what the release delivers at that step, not from what
the actor could infer:

- **Identity**: who the actor is at this step, and how the product knows it.
- **Context**: which tenant, brand or account they act in, and how that is chosen or shown.
- **Shown**: what the screen or output tells this actor at this step, including their own
  identity and context.

Write `unknown` where the map, the stories and the tasks do not say. Do not fill a cell
from what the product probably does.

Name every hole. There are four classes:

| Hole | Meaning |
| --- | --- |
| step with no story | someone must act here and no story lets them |
| story with no task | the map promises it and nothing builds it |
| task with no story | work admitted into the release that the map does not hold (`journey-progress.mjs` lists these as `orphans`) |
| actor without identity or context | in a step, the Identity, Context or Shown cell of any actor is `unknown`, missing or ambiguous: they cannot be told who they are, which tenant, brand or account they act in, or the screen or output does not show it |

A hole sends the worker back to step 1. Cover the whole path even when only one task
changed: a hole between two tasks is the defect this mode exists to find. Check the
three cells for every actor at every step, not only where a story mentions them.

## 3. Check the slice

Count the stories whose status is not `exists`, per journey file, against the limit
(`journey-lint.mjs` prints `slice-size`). Over it, propose sub-slices or a
`slice_because`. When releases in several journey files are one demo, add the counts
by hand and say so. Count is a load cue, not a fit test; fit stays the handoff's
appetite versus estimate.

## 4. Split into tasks

Only now list tasks, each with the `journey`, `journey-release` and `journey-story`
values the caller sets on it. Where the caller has opted into completion tracking, also
list the exhaustive task set per story so it can write `journey-required-tasks`.
One `journey-story` per task: a task that delivers several stories is a limit
`kc-journey-progress` does not read; say so and propose one task per story.

## Output

The proposed map edit; the walk table with the holes named; the slice count with its
split or reason; the task list with proposed journey fields. Report anything the walk
could not establish as unverified rather than filling it in.
