
## Stage Report: implementation

- DONE: Apply Captain amendments Amendment 1 and Amendment 2 together; implementation-1-message-1 is withdrawn where it says five.
  The Reviewer line is recorded under FO alignment and `role-triggers.log` exits 0 for two events; Amendment 2's 「這張就做到 7 次」 and Design line govern the per-entry skip. No original Captain metadata or withdrawn Design prose was rewritten.
- DONE: Move the AC-4 block verbatim under Amendment 1's Superseded text and write the replacement under a fresh id naming both amendments.
  Live AC-8 says "Amended by Captain, amendment 1, and by amendment 2"; `superseded-ac-4.md` and `criterion-move.json` prove the exact old block, unchanged amendment metadata/frontmatter and no live AC-4. `task-design.log` exits 0 and `amendment-added-words.json` is empty.
- DONE: Narrow the product skip in only the design's named files, with tests and the whole-file-skip falsifier.
  Candidate `72216e2e947e962737a17c6e61ef3800f9d639c4` filters entries whose own spans contain parser issues and removes L4's file-level/first-parent structural gate. Three new tests fail on prior candidate `71eb2ec42` (`red.log`) and pass now; restoring the whole-file skip fails `L4Test.test_unrelated_broken_entry_does_not_hide_valid_move` (`mutation-whole-file-entry-skip-0.log`).
- DONE: Show that a later push repairing only a broken heading reports a never-reported defect and does not repeat a reported sibling defect.
  `L4Test.test_repaired_heading_reports_previously_unjudged_defect` asserts both reuse/unmarked diagnostics at the heading-repair commit; restoring the first-parent gate fails it (`mutation-whole-file-parent-skip-0.log`). `test_repairing_an_unrelated_heading_does_not_repeat_reported_defect` asserts zero later L4 events; `l4-tests.log`: all 11 pass.
- DONE: AC-8 — replay all seven capability-table events at the new candidate and keep every local acceptance criterion's evidence in the task folder.
  Full root-to-tip CLI runs pinned at dev2 `2a42fbb15e0f`, qnow `c36650727548`, relay `fd1481da6295` report 3/3/1 L4 events, exactly the seven expected commits, no extra. `corpus-reconciliation.json` and `corpus-*.log` include ranges/output; complete CLI exits 2 on existing L3 history debt while the L4-specific verification passes. `recovered-dev2.log` and `recovered-relay.log` show both previously missed commits now reported.
- DONE: AC-1 — the original bite and its reuse/marker falsifiers.
  `candidate-bite.log` reports one event, reused AC-1/AC-2/AC-4 and unmarked amendment 1; the full base-package replay `base-bite.log` has no L4. Removing either predicate removes its diagnostic and fails its fixture (`mutation-reuse-bite.log`, `mutation-marker-bite.log`).
- DONE: AC-2 and AC-3 — legitimate moves remain green and an existing defect is not re-reported.
  `laws-tests.log`: 76 run, 75 passed, one optional environment fixture skipped; record-only, marked/waived moves, defect introductions, post-defect ranges and repair are exercised. Removing the payload gate or first-parent suppression fails its named case (`mutation-payload-0.log`, `mutation-parent-0.log`); judging the broken entry itself fails its skip case (`mutation-judge-broken-entry-0.log`).
- DONE: AC-5 — registry, documentation word bound and FO reading boundaries.
  `laws.md` adds 242 words (1345 to 1587, below 250); the registry test passes and deleting its L4 heading fails (`mutation-heading-0.log`). `artifact.json` lists only four approved product files; workflow, dispatch_records.py, skills, CI template and versions are unchanged.
- DONE: AC-6 — one shared marker predicate with unchanged design-check behavior.
  Both callers use `unmarked`; unchanged `test_design_surfaces.py` runs 217 tests, 213 passed and four optional environment fixtures skipped (`design-tests.log`). Disabling the shared marker fails one test in each suite; all nine mutation test runs reject their regressions with absent caches and python3 -B (`mutations.json`). All 1032 pinned check/seed verdicts match the base (`check-comparison.json`).
- SKIPPED: AC-7 — hosted dev2 activation and the old-pin hosted falsifier.
  Deferred by approved D2 until a containing release, Captain-approved pin change and one observed state-push L4 headline. This worker changed no adopter pin and claims no hosted activation; local evidence is not that proof.
- DONE: Repository skill lint, package ADR lint, number guards and comment ratio at the new candidate.
  All exit 0: `lint.log`, `adr-lint.log` (65 ADR records, none newly added), `number-guards.log` (no findings), `comment-ratio.log` (0/205 = 0.0%, maximum 5%); base `6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1`.
- DONE: doc-impact — docs/adr/0041-seed-admission-enforces-required-fields.md is unaffected.
  Seed admission remains unchanged; all pinned check/seed verdicts match the base. `doc-verdicts.json` records this disposition beside raw `doc-impact.json`.
- DONE: doc-impact — docs/adr/0057-rewritten-criteria-are-compared-with-the-captains-words.md is unaffected.
  `added_words` and its dispatch comparison remain unchanged; the replacement criterion passes that check (`amendment-added-words.json`). Disposition: `doc-verdicts.json`.
- DONE: doc-impact — kc-dev-flow-2/references/sd/laws.md is updated.
  L4 documents per-entry structural skips and the first-judgeable heading-repair event. Disposition: `doc-verdicts.json`; registry and heading mutation exercise its entry point.
- DONE: doc-impact — learning.md is unaffected.
  Historical practices still apply; the word, history-input, consumer and corpus checks were followed without rewriting the records. Disposition: `doc-verdicts.json`.
- DONE: Keep the candidate, evidence and falsifiers durably reviewable in the task folder.
  Evidence home: `amendment-checked-when-written/implementation/amendment-2/`; `artifact.json` binds code hashes and candidate, `manifest.json` seals the files, and `README.md` explains replay. `acceptance.json` records six local criteria passed and AC-7 deferred; the prior failed AC-4 is superseded, not reused.
- DONE: Commit locally without product push and update the PR text for FO.
  Branch `spacedock-ensign/amendment-checked-when-written`, base `6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1`, new candidate `72216e2e947e962737a17c6e61ef3800f9d639c4`, clean product worktree. `/tmp/impl-amendment-checked-when-written-pr.md` and evidence `pr-draft.md` carry the scoped Conventional Commit title/body; no version bump or empty commit.
- SKIPPED: Product push, opening the Draft PR, RoboRev and hosted CI review.
  No PR opened: no push grant; these steps remain FO-owned and not run by this worker. CI cost per PR and per state push is not measured; no trigger, job or adopter pin was changed.
- DONE: Append one complete new Stage Report: implementation with each item followed by its own indented evidence line.
  This complete report uses the exact heading and DONE/SKIPPED forms, with evidence per item including all four document dispositions; evidence copy: `stage-report.md`.

### Summary

This report supersedes every earlier implementation report: both Captain amendments are applied, the seven-event acceptance criterion is green at `72216e2e947e962737a17c6e61ef3800f9d639c4`, and restoring either structural skip fails a named test. The prior whole-file miss is repaired without hiding a previously unjudged defect on a later heading-only repair; AC-7 and FO-owned publication/reviews remain explicitly open.
