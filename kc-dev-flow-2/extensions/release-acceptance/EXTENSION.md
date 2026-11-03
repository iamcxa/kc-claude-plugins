# release-acceptance extension

Walks a release after its last story with picky-user reviewers on different Claude models;
the design director rules on their findings. Enabled by workflow README frontmatter
listing `release-acceptance` under `extensions:` and a kc-journey-map file under `docs/journey/`; otherwise no step.

- **Needs:** python3 for `<package>/extensions/release-acceptance/release_acceptance.py` (`ra`);
  node and kc-journey-map's `lib/journey-walk.mjs`. Input: `release-walk/v1`, read by string;
  report: `release-acceptance/v1`. `ra schema release-acceptance` prints the field table,
  refusing an unversioned change. JSON lives in `<task folder>/walk/`.
  README records `walk-environment`, `production-environment`, `release-doc`; missing keys hold:
  ask the four questions in [Release environments](../../references/sd/adoption.md#release-environments).
- **File the task:** five stages, `Surfaces: none`, frontmatter `release-acceptance: <journey>/<release>`,
  no `journey` field. Body: `Acceptance of: <journey>/<release> at <journey file commit>`;
  `Environment:` names only (README's `walk-environment`, deployed ref, `<wrapper>`, opt-in variables, identities by role);
  `Smoke:` passing proof-line path and failure condition; `Reviewers:` id, model, persona and operating
  method; at least two, distinct personas and models.
- **Acceptance task's implementation scope notes:** FO adds to its first implementation record only:
  "Lead the walk. Save `node <kc-journey-map>/lib/journey-walk.mjs <journey file> <release>`
  as `walk/walk.json`, smoke as `walk/smoke.json`. Run `ra deferred <journey>/<release> --workflow-dir <dir>`.
  Launch reviewers fresh, sequentially, on their models, given only persona, walk list, deferred list
  and environment. Walk on `walk-environment`; for `local`, record a `not_tested` entry starting
  `not deployed:` naming untested deployment behavior. Write `walk/meta.json`; `director_model` follows
  `ra director-model <folder> --workflow-dir <dir>`: opus when any release task's ideation used opus,
  else sonnet. Run `ra check <folder> --tier walk`, `kc-dev-flow-2:design-director` pass 3 on that
  model into `walk/ruling.json`, `ra build <folder>`, `ra check <folder> --tier final`,
  `ra render <folder> > <folder>/walk/record.md`. Commit the walk folder path-scoped to state;
  open no pull request."
- **Validation:** re-runs `check --tier final`, `render --check`, every non-`works` story and the
  proof line; `Candidate:` names the state commit. Gate question: approving accepts the walk
  and closes without a pull request; FO sets `pr: local-merge:<sha>`, runs `merge guard --verdict passed`;
  production waits for `ra accepted`.
- **Close:** after archive, FO files up to three ruling tasks as backlog, each with
  `journey-release: <release>` and `Walk complaints: <id>, <id>`; the re-walk finds them through
  `deferred`'s scan. Proposed map edits (`node <kc-journey-map>/lib/journey-accept.mjs`) get their own journey pull request.
- **Production waits:** FO quotes `ra accepted <journey>/<release> --workflow-dir <dir>`'s accepted
  line before saying ready: the newest archived walk needs `local-merge:` and a clean report.
  Follow `release-doc`; dev2 releases nothing.
- **Re-walk:** after fixes land, file another acceptance task with `Prior walk: <immediately preceding walk's report.json>`
  (absolute or state-relative). Relaunch that walk's reviewers with unchanged id/model/persona and their
  own complaints, including inherited `partly-fixed` and `deferred` marks. Each marks them `fixed`,
  `partly-fixed`, `deferred` with `release`, or `will-not-fix`, with reasons; new complaints allowed.
  Use that same report for `--prior` in both `ra build` and `ra check`;
  close as above. Each re-walk extends this chain.
- **Read:** `record.md` opens with complaint/task/status/reason rows. `check` prints `environment:`,
  `reviewers: N (models: M)`, `route:`, `Captain decision: environment (<cause>)`, `clean: yes|no`;
  decides nothing. `route: review-release` needs `codex` interrogation, possibly
  `interrogation not run: <reason>`.
- **Cannot see:** persona obedience, actual model diversity/execution, smoke sufficiency, director correctness;
  it cannot verify environment identity or stop releases bypassing FO. A story's task plus later bug task means two
  owners: `review-release`. These acceptance tasks stay outside `learn`.
