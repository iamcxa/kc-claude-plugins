# journey-map extension

Carries a Captain ruling that answers a journey-map question from the task to the map. A
repository uses it by listing `journey-map` under `extensions:` in its workflow README
frontmatter, and only when the repository keeps a kc-journey-map file.

- **Needs:** python3 for `<package>/extensions/journey-map/map_footprint.py`; for the fold and the counts, node and a
  kc-journey-map release that ships `lib/journey-fold.mjs`, `lib/journey-reconcile.mjs` and `lib/schemas.mjs`
  (without one, `add`, `check` and `audit` still run and the fold is reported as not run). A task is a
  journey task when its frontmatter has both `journey` and `journey-story`; any other task is
  outside this extension.
- **Joins:** FO, at three points on a journey task.
  - Right after each `spacedock gate record` or recorded Captain amendment that answers a map
    question, FO runs `python3 <package>/extensions/journey-map/map_footprint.py add <task file>
    --question <id> --source gate-attempt:<id>|amendment:<n> --words '<his words>' --answer
    '<one line>'`, once per question answered (`--story` when the task's `journey-story` is not
    the story). A ruling that answers no map question gets no line.
  - Before `merge guard`, FO writes `Map footprints: <n> in footprints.jsonl` or `Map
    footprints: not needed: <reason>` under `## FO alignment`, runs `python3
    <package>/extensions/journey-map/map_footprint.py check <task file>`, and commits the folder
    with `spacedock state commit <slug> --workflow-dir <dir>`. Exit 1 is fixed before the merge
    guard; once archived a task's state is publish-only and takes no new line.
  - Right after the archive, FO runs `node <kc-journey-map>/lib/journey-fold.mjs <journey file>
    --footprints <task folder>/footprints.jsonl --out <draft>`, shows the draft's diff, and its
    archive message states `journey-map fold: <PR url>`, `not needed: <reason>` or `not run:
    <reason>`. The docs-only map pull request follows `## Delivery authority`; this extension
    grants no push.
- **Counts at release review:** FO runs `python3 <package>/extensions/journey-map/map_footprint.py
  audit <workflow-dir> --since <date this repository listed the extension>` (`unrecorded` and
  `invalid` must be 0) and `node <kc-journey-map>/lib/journey-reconcile.mjs <journey file>
  --workflow-dir <dir>`, with the map read from the trunk (`unfolded` and `stale-open` must be 0;
  `pending` and `unsourced` are information). A nonzero count goes to the Captain, and on his
  yes through FO's issue-filing approval into a kc-claude-plugins issue, the intake `maintain-flow`
  already serves.
- **Contract history:** the record shape is versioned, `journey-footprint/v1`, and its
  producer is this package. The current field table and version are what `python3 <package>/extensions/journey-map/map_footprint.py
  schema journey-footprint` prints, and that command exits 1 when the table changed without a
  new version. Every version is in this package's release-please `CHANGELOG.md`; the first
  shape and each MAJOR change have an ADR in the repository's `docs/adr/` (the one titled "a
  Captain ruling reaches the map as a versioned footprint"). Read the CHANGELOG when a footprint
  carries a schema string FO has not seen or a consumer refuses a major, and read the ADR
  before removing or renaming a field. The map's question fields are owned and versioned by
  kc-journey-map the same way (`node <kc-journey-map>/lib/schemas.mjs journey-map-question`).
- **Read:** a footprint is a proposal. The map file in git stays the authority until the
  Captain approves the fold pull request; the fold creates no story or question and lists one
  that is missing as `no-story` or `no-question`.
- **Cannot run:** a missing `node` or kc-journey-map is reported as `journey-map fold not run:
  <reason>`; the footprint stays in the task folder and `unfolded` counts it at the next
  release review.
- **Limits:** a ruling made in chat with no task, and a release-level task that carries
  `journey` but no `journey-story`, are outside `check` and `audit`; `stale-open` is the only net
  for a ruling nobody recorded. `audit` ignores tasks whose rulings all predate `--since`, because
  an archived task cannot take a new line.
