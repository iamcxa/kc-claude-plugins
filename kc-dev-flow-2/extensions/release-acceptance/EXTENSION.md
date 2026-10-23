# release-acceptance extension

Walks a release after its last story with picky-user reviewers on different Claude models, then has
the design director rule on what they found. A repository uses it by listing `release-acceptance`
under `extensions:` in its workflow README frontmatter, and only when it keeps a kc-journey-map file.

- **Needs:** python3 for `<package>/extensions/release-acceptance/release_acceptance.py` (below `ra`);
  node and a kc-journey-map release that ships `lib/journey-walk.mjs` for the walk list. The walk list is
  `release-walk/v1`, read by string only. The report is `release-acceptance/v1`; `ra schema
  release-acceptance` prints its field table and exits 1 when the table changed without a version bump.
  Every file below is JSON in `<task folder>/walk/`.
- **File the task:** an ordinary five-stage task, `Surfaces: none`, frontmatter `release-acceptance:
  <journey>/<release>` and no `journey` field. Body: `Acceptance of: <journey>/<release> at <journey file commit>`;
  `Environment:` names only (target, deployed ref, `<wrapper>`, opt-in variables, identities by role);
  `Smoke:` one passing path through the proof line and the condition it fails on; `Reviewers:` id,
  model, persona and how each operates the product, at least two, distinct personas, distinct models.
- **Instruction FO adds to an acceptance task's implementation scope notes:** "Lead the walk. Save
  `node <kc-journey-map>/lib/journey-walk.mjs <journey file> <release>` as `walk/walk.json`, run the smoke
  path into `walk/smoke.json`, write `walk/meta.json`, run `ra deferred <journey>/<release> --workflow-dir <dir>`,
  and launch each reviewer fresh and one at a time with its `model`, giving it persona, walk list, deferred
  list and environment only. Run `ra check <folder> --tier walk`, then pass 3 of `kc-dev-flow-2:design-director`
  on sonnet into `walk/ruling-sonnet.json`, `ra escalate <folder> --workflow-dir <dir>`, pass 3 on opus for the
  listed items into `walk/ruling-opus.json`, `ra build <folder>`, `ra check <folder> --tier final`, and
  `ra render <folder> > <folder>/walk/record.md`. Commit the walk folder path-scoped to the state checkout.
  Open no pull request."
- **Validation:** re-runs `check --tier final` and `render --check`, re-performs every non-`works` story
  and the proof line, and names the state commit as `Candidate:`. The gate question says approving accepts
  the walk and closes the task with no pull request, FO setting `pr: local-merge:<sha>` and running `merge
  guard --verdict passed`.
- **Close:** after the archive FO files the ruling's tasks, at most three, as backlog tasks. Each carries
  `journey-release: <release>` and one line `Walk complaints: <id>, <id>`, which the re-walk finds by the same
  scan `deferred` uses. A map edit the walk proposes (`node <kc-journey-map>/lib/journey-accept.mjs`) goes in
  its own journey pull request.
- **Re-walk:** after the fix tasks land, file a second acceptance task for the same release with `Prior walk:
  <path to the first report.json>`, relaunch each original reviewer with the same id, model and persona, and
  give it its own complaints. It marks each as `fixed`, `partly-fixed`, `deferred` with `release`, or
  `will-not-fix`, each with a reason, and may add new complaints. Run `ra build` and `ra check` with `--prior
  <that report.json>`; the task closes as above.
- **Read:** `record.md` opens with one row per complaint: its task, status and reason. `check` prints
  `reviewers: N (models: M)`, `route:` lines, `Captain decision: environment (<cause>)` and `clean: yes|no`;
  it decides nothing. `route: review-release` begins with an interrogation that needs `codex` and may print
  `interrogation not run: <reason>`.
- **Cannot see:** that reviewers obeyed their persona or that two models differ in fact; that a declared model
  ran; that smoke is rich enough; that the director is right; a story with a task and a later bug task counts two
  owners and routes to `review-release`. Acceptance tasks closed this way are outside the `learn` loop.
