### `backlog`

The user selects the compatible profile and approves outcome, scope and budget.
FO records the choice; this boundary has no worker or placeholder report. FO
also records, under a `## FO alignment` heading in the task file, whether FO
direction alignment with the Captain is needed before the next declared stage
and why; a
stated reason is the whole record when not needed. On the five-stage route, FO
also records a `Surfaces:` line under the same heading: any of `ui`, `db`,
or `none`, read from the change surface rather than the diff, and next to it
a `Visible change:` line: one sentence on what a user sees or operates
differently, or `Visible change: none`.

- **Gate content:** Show the selected variant/profile, proposed outcome, scope,
  exclusions and evidence needed before the next declared stage starts, the
  `## FO alignment` need and reason, and the recorded `Surfaces:` and
  `Visible change:` lines on the five-stage route.
- **Seed check:** On the five-stage route, before `gate prepare`, FO runs
  `python3 <package>/scripts/design_surfaces.py check --seed <task>` and holds the
  gate until it exits 0. An FO that skips this step still dispatches; the worker's own
  check is the backstop.
- **Release review:** Applies to a task that belongs to a release on a journey map
  (`journey`, `journey-release`, `journey-story`); a task with no release, such as a
  bug, infrastructure or workflow maintenance, is outside it. Four signals: (1) a task
  admitted into a release; (2) a Captain scope ruling that moves a story or task into
  or out of a release or changes the goal of the release, a story or a task; (3) a UAT
  failure that crosses two or more tasks; (4) a batch about to enter implementation. Signals 1 and 2 only mark the
  release changed: FO names the release and the signal in the task's `## FO alignment`
  reason. A task whose `journey-story` is already on the map in that release passes with
  that one check and marks nothing when, since its latest `Release review:` line, the
  journey file still holds the same story ids and the same release and story `goal`
  text and no Captain ruling has changed the goal of the release, a story or a task.
  A changed goal is signal 2 although no story id moved; FO marks the release
  changed in that task's `## FO alignment` reason. Signal 4 is the single checkpoint: at the first
  implementation dispatch for a release marked changed, FO dispatches a fresh worker
  with kc-journey-map's `review-release` mode, then splits tasks from its output; an
  unchanged release proceeds. One review covers every change since the last. Signal 3
  runs the review at once. FO writes no map and no candidate; the Captain accepts
  membership in conversation or at this gate. FO records under `## FO alignment` either
  `Release review: <journey>/<release-id> at <journey-file commit>` or
  `Release review: not needed: <reason>`; no script checks that line. When FO approves
  a task into a release story at this gate it sets the three fields with
  `spacedock status --workflow-dir <dir> --set <task> journey=<the map's journey: value> journey-release=<id> journey-story=<id>`;
  a worker never edits frontmatter. Where the adopter tracks completion with
  kc-journey-progress, FO also writes `journey-required-tasks` (full task ids) and
  `journey-mapping-complete: true` on one task per story at the review's split step.
  When signal 2 moves a task out of a release, FO clears its release fields with
  `spacedock status --workflow-dir <dir> --set <task> journey= journey-release= journey-story= journey-required-tasks= journey-mapping-complete=`
  (a field set to nothing is cleared). Where kc-journey-progress is tracking, follow its
  skill for the lists; when the cleared task was the declaring one, FO moves that list and
  `journey-mapping-complete: true` to another member of the story. kc-journey-progress
  reports a story unverified until its declaration matches its members.

