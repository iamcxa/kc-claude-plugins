# Are all current tests necessary?

**The evidence does not establish that all 1,455 functions are necessary, or that any broad group is safe to delete.** It does identify **579 functions (39.8%) for consolidation/removal review**: constructed input edges, test-sensitivity/harness/overlap checks, and wording/count pins. These are candidates, not proven waste. Keep ordinary coverage and incident regressions out of a blanket cut.

Snapshot: local `origin/main` **6a1eaf837bd6087cd0b8b665dc19beaed3c44dff**, read without fetch or checkout. Inventory reproduces **31 product Python files / 10,731 physical lines; 29 test Python files / 24,684 LF-delimited physical lines; 1,455 named `test_` functions**. Counts include subtests once and inherited methods once at their definition. The rough 24,685-line figure counts an embedded Unicode line separator as an additional line; LF-delimited source has 24,684. Two script-style suites have zero named test functions but contain assertions.

| Class | Meaning | Functions |
|---|---|---:|
| A | Recorded real-failure regression | 64 |
| B | Constructed input edge, no observed occurrence found | 432 |
| C | Exact wording, count or duplicate-list pin | 40 |
| D | Test sensitivity, harness/fixture or trivial overlap | 107 |
| E | Ordinary unit coverage without incident history | 812 |
| **Total** | | **1,455** |

**Three largest candidate groups.** **B: 432** — removing these loses malformed/ambiguous record handling, including report nesting, fences, stale evidence and path boundaries. No evidence makes that loss acceptable. **D: 107** — 94 mutation/falsifier tests, eight replay-harness tests, four assertion overlaps, one fixture-side check. Removing all loses sensitivity checks and replay/cleanup assurance; some mutation tests also carry primary behavioral assertions. **C: 40** — removing these permits wording, length and instruction-presence drift; replacing brittle prose assertions with executable contracts needs separate validation. Even the four overlaps need a focused surviving-test proof before deletion.

**History:** definition pickaxe scanned all 1,455; line histories sampled **40 per class, 200 total**. Across all 25 retained failed workflow runs, **8 current tests verifiably failed after introduction: A 0, B 0, C 2, D 1, E 5**. Another eight failed while being introduced and are excluded. These are observed lower bounds, not lifetime zeroes: absent logs, uncommitted local failures, removed tests and cancelled/skipped paths remain unknown. A test that never failed after introduction is only a removal candidate, never proven useless. Cold reread: **3/30 disagreements (10%)**, before adjudication.

**Cost and churn:** 28 local file runs took **809.859 s** in total: 19 passed, nine failed, one additional suite skipped for the Spacedock plugin root. Export/sandbox confounds prevent treating failed timings as normal CI cost. The successful pinned CI job took **426 s (7m 6s)**; delivery (87 s), dispatch records (74 s), and stage dispatch (58 s) accounted for **51.4%**. This is one push job, not measured total per-PR or monetary cost. Latest 20 merged package PRs: tests **+1,856/−61**, product scripts **+1,143/−78**. **One PR (#846) was solely fixture repair**; four PRs (#841, #846, #854, #861) contain identified incidental wording/fixture maintenance, alongside behavior changes in three.

**Limits:** no safe-deletion verdict, no full historical execution matrix, no causal runtime attribution by class, no independent second auditor, and no claim that “no occurrence found” means impossible. Per-file counts, timings, exact test pointers and the ten densest checkers follow. No product or workflow changes were made.

---

## Classification method and tie-breaking

Each function body and immediate context was read, then its introducing commit message was checked. A named PR alone or a generic “fix” title is not evidence of an operational incident: A requires a concrete observed failure narrative or frozen real-event fixture. B covers boundary/input-shape constructions; ordinary supported success/refusal paths stay E even though their fixtures are synthetic. C is the primary wording/count assertion, not every incidental assertIn in a behavioral test. D identifies checks of test sensitivity, replay/fixture machinery or a specifically identified near-duplicate. Combined mutation tests remain D even when they contain a valuable behavioral control; that ambiguity is a reason not to delete the whole class. Recorded real behavior takes A over B/C; otherwise classify the primary purpose D, C, B, then E. These are manual judgments, not labels inferred from test names by a classifier.

Cold sample uses Python Random(20261114), 30 unique IDs. Initial labels were hidden for the body-only reread; this is same-auditor consistency, not independent agreement. IDs 131, 451 and 1070 disagreed. Adjudication: 131 becomes E (normal accepted-digest contract); 451 stays E (normal reader-error handling); 1070 becomes E (a documented nested-discovery test and fix title do not establish a recorded operational failure). History review separately moved incident-linked tests into A. `cold-initial.json`, `cold-reread.json`, `cold-differences.json` retain the pre-adjudication comparison.

## Per-file census

| Test file | A | B | C | D | E | Total | Lines |
|---|---:|---:|---:|---:|---:|---:|---:|
| extensions/codex/test_codex_review.py | 4 | 7 | 1 | 1 | 23 | 36 | 450 |
| extensions/copilot/test_copilot_review.py | 2 | 3 | 0 | 0 | 10 | 15 | 123 |
| extensions/journey-map/test_map_footprint.py | 0 | 4 | 1 | 0 | 18 | 23 | 292 |
| extensions/release-acceptance/test_release_acceptance.py | 0 | 58 | 2 | 0 | 62 | 122 | 1574 |
| extensions/roborev/test_roborev_gate.py | 0 | 0 | 0 | 0 | 5 | 5 | 89 |
| scripts/test_adr_doc_checks.py | 3 | 2 | 0 | 0 | 4 | 9 | 169 |
| scripts/test_comment_ratio.py | 1 | 3 | 0 | 0 | 10 | 14 | 168 |
| scripts/test_decision_ledger.py | 0 | 10 | 0 | 0 | 13 | 23 | 316 |
| scripts/test_delivery_gate.py | 13 | 83 | 6 | 14 | 114 | 230 | 3428 |
| scripts/test_design_surfaces.py | 2 | 82 | 7 | 72 | 71 | 234 | 2758 |
| scripts/test_dispatch_records.py | 10 | 55 | 4 | 4 | 63 | 136 | 3708 |
| scripts/test_dispatch_stage.py | 0 | 14 | 0 | 0 | 38 | 52 | 1056 |
| scripts/test_laws_check.py | 1 | 31 | 0 | 4 | 49 | 85 | 1303 |
| scripts/test_learning.py | 1 | 6 | 4 | 1 | 38 | 50 | 1261 |
| scripts/test_lint_skills.py | 6 | 10 | 2 | 0 | 29 | 47 | 330 |
| scripts/test_merge_audit.py | 0 | 5 | 0 | 0 | 12 | 17 | 258 |
| scripts/test_number_guards.py | 0 | 0 | 1 | 1 | 36 | 38 | 578 |
| scripts/test_observer_check.py | 0 | 4 | 5 | 0 | 14 | 23 | 315 |
| scripts/test_observer_recovery.py | 0 | 0 | 0 | 0 | 0 | 0 | 137 |
| scripts/test_package_version.py | 1 | 5 | 0 | 0 | 17 | 23 | 337 |
| scripts/test_poc_readme.py | 2 | 0 | 4 | 0 | 3 | 9 | 147 |
| scripts/test_pr_watch.py | 15 | 19 | 2 | 1 | 110 | 147 | 2469 |
| scripts/test_replay_dispatch.py | 0 | 0 | 0 | 8 | 0 | 8 | 161 |
| scripts/test_role_triggers.py | 3 | 17 | 1 | 0 | 42 | 63 | 956 |
| scripts/test_scratch.py | 0 | 8 | 0 | 0 | 8 | 16 | 309 |
| scripts/test_sd_dispatch.py | 0 | 0 | 0 | 0 | 0 | 0 | 1406 |
| scripts/test_task_timeline.py | 0 | 4 | 0 | 0 | 8 | 12 | 224 |
| scripts/test_validation_security.py | 0 | 0 | 0 | 1 | 4 | 5 | 179 |
| scripts/test_workflow_checkout.py | 0 | 2 | 0 | 0 | 11 | 13 | 183 |

## Historical failures

`git log -S "def <name>("` on every definition finds introduction/removal, not executions. `git log -L start,end:file` on the seeded stratified sample (Random(20261113), 40/class) traces edits; an edit is not counted as a failure. Public CI run logs supply actual failures. The test must already exist in the failing commit’s parent (local Git, then public contents API for unavailable branch commits); first-introduction failures are excluded. Current names/classes are matched exactly in CI logs; renamed historical tests can be missed. Four definitions share their bare function name with another class in the same file, so their pickaxe introduction attribution is ambiguous and marked in tests.csv; none is in the confirmed later-failure set. The oldest retained failed run is 2026-10-12 and the latest is 2026-11-11. No fetch was performed.

| Class | Pickaxe census | Line-history sample | Confirmed later failure | No confirmed later failure* |
|---|---:|---:|---:|---:|
| A | 64 | 40 | 0 | 64 |
| B | 432 | 40 | 0 | 432 |
| C | 40 | 40 | 2 | 38 |
| D | 107 | 40 | 1 | 106 |
| E | 812 | 40 | 5 | 807 |

*This column means evidence absent in the available window, not never failed. The full list of failing-run/test IDs and parent checks is in `post-intro-failures.json`; all failed runs and retrieval exits are in `ci-history-filtered.json`. Only filtered CI metadata is retained.

| Current test | Class | Confirmed later failing run |
|---|---|---|
| `ContractTests.test_extension_md_stays_within_its_word_budget` | C | [40160174769](https://github.com/iamcxa/kc-claude-plugins/actions/runs/40160174769) |
| `JourneyStoryTests.test_design_compares_story_record_to_counted_field_only_in_map_workflows` | E | [42991272542](https://github.com/iamcxa/kc-claude-plugins/actions/runs/42991272542), [42991036147](https://github.com/iamcxa/kc-claude-plugins/actions/runs/42991036147) |
| `ContextNoticeTests.test_workflow_strict_preflight_holds_then_repaired_context_reaches_real_builder_fixture` | E | [41285728665](https://github.com/iamcxa/kc-claude-plugins/actions/runs/41285728665) |
| `ContextMutationTests.test_context_boundary_falsifiers_fail_without_caches` | D | [41285728665](https://github.com/iamcxa/kc-claude-plugins/actions/runs/41285728665) |
| `ExtensionInstructionTests.test_every_shipped_instruction_is_read_from_its_extension_file` | C | [39970481878](https://github.com/iamcxa/kc-claude-plugins/actions/runs/39970481878) |
| `PackageVersionTest.test_the_package_template_carries_the_line_and_matches_its_manifest` | E | [38212469891](https://github.com/iamcxa/kc-claude-plugins/actions/runs/38212469891) |
| `DeriveTests.test_only_the_ideation_entry_and_section_are_removed` | E | [41397467433](https://github.com/iamcxa/kc-claude-plugins/actions/runs/41397467433), [41391153305](https://github.com/iamcxa/kc-claude-plugins/actions/runs/41391153305) |
| `WaitNextTests.test_a_start_that_is_not_an_outcome_prints_no_next_line` | E | [38520692074](https://github.com/iamcxa/kc-claude-plugins/actions/runs/38520692074) |

Observed examples include a 614-word extension against a 600-word cap, instruction-presence assertions, a release-version mismatch, a changed workflow entry layout, and the story fixture missing newly required Worth questions. A failure shows maintenance/detection activity; it does not alone distinguish a product regression from intentional contract changes or fixture repair.

## Runtime and CI concentration

Every file was attempted once sequentially with python3 -B and SPACEDOCK_BIN=<local path removed> A nested write sandbox restricted all fixture writes to this audit directory, with global Git configuration disabled. `runtime.csv` preserves first-run wall time, exit and log. The export sits under a Git worktree: supposed non-Git fixture directories can accidentally discover its ancestor repository. Scratch and stage-dispatch suites require fixed /tmp/dev2 paths outside the authorized write scope. Release acceptance needs an unexported sibling journey fixture. These are material environmental confounds, not established product defects. Seven selected failures were rerun with GIT_CEILING_DIRECTORIES set to the fixture boundary: five passed; the plain-copy dispatch and historical laws cases still failed with uncommitted-report. Their cause remains unresolved. These probes do not replace the original file timings or establish full-suite passes; see runtime-confound-probes.json. `test_sd_dispatch.py` was skipped because its CI-pinned Spacedock plugin root was not supplied.

The successful source-pinned job is [43401473742](https://github.com/iamcxa/kc-claude-plugins/actions/runs/43401473742). Its step timings are in `ci-step-timings.json`. `test_scratch.py` has 16 named functions but is not invoked by this CI workflow. Two script-style files (`test_sd_dispatch.py` and `test_observer_recovery.py`) have no named test functions; counting only functions omits their assertion workload. Tests inherited by multiple classes and subtests explain runtime runner totals differing from source-function counts.

| Local test file | Seconds | Exit/status |
|---|---:|---|
| test_codex_review.py | 0.144 | 0 |
| test_copilot_review.py | 0.086 | 0 |
| test_map_footprint.py | 0.327 | 0 |
| test_release_acceptance.py | 1.861 | 1 |
| test_roborev_gate.py | 2.109 | 0 |
| test_adr_doc_checks.py | 1.16 | 1 |
| test_comment_ratio.py | 6.83 | 0 |
| test_decision_ledger.py | 0.541 | 0 |
| test_delivery_gate.py | 116.195 | 1 |
| test_design_surfaces.py | 16.479 | 1 |
| test_dispatch_records.py | 122.673 | 1 |
| test_dispatch_stage.py | 121.087 | 1 |
| test_laws_check.py | 107.979 | 1 |
| test_learning.py | 50.946 | 0 |
| test_lint_skills.py | 11.015 | 0 |
| test_merge_audit.py | 13.346 | 0 |
| test_number_guards.py | 28.809 | 0 |
| test_observer_check.py | 9.649 | 0 |
| test_observer_recovery.py | 3.191 | 0 |
| test_package_version.py | 7.701 | 0 |
| test_poc_readme.py | 1.949 | 0 |
| test_pr_watch.py | 92.134 | 1 |
| test_replay_dispatch.py | 4.932 | 0 |
| test_role_triggers.py | 75.565 | 0 |
| test_scratch.py | 2.68 | 1 |
| test_sd_dispatch.py | — | skipped: requires CI-pinned Spacedock plugin root |
| test_task_timeline.py | 2.84 | 0 |
| test_validation_security.py | 0.61 | 0 |
| test_workflow_checkout.py | 7.021 | 0 |

## Last 20 merged package PRs

Requested `gh pr list --state merged --limit 40` supplied the candidate window; mergedAt was additionally retrieved, package-touching PRs filtered, then sorted by merge time. An additional merged-since-2026-11-11 query returned 28 PRs, 23 touching the package, and reproduced the same latest 20, checking for older-created PRs omitted by the initial window. Churn is package-only merge-commit diff: test_*.py versus other Python; documentation excluded from product-script totals and reported separately. Definitions and classifications are pinned; PR sampling is the observed API window.

#846 adds only two fixture lines. #841 updates exact question text/count assertions and existing seed fixtures while introducing budget behavior. #854 removes redundant fixture remote setup while adding scratch behavior. #861 adds the newly required helper to a sandbox copy list while changing observer behavior. Four is the count with identified incidental maintenance; one is the strict whole-PR fixture-only count. This does not count every test change accompanying a new behavioral requirement as wasted churn.

| PR | Tests +/− | Product scripts +/− |
|---|---:|---:|
| [864](https://github.com/iamcxa/kc-claude-plugins/pull/864) | 0/0 | 4/1 |
| [862](https://github.com/iamcxa/kc-claude-plugins/pull/862) | 0/0 | 0/0 |
| [856](https://github.com/iamcxa/kc-claude-plugins/pull/856) | 99/2 | 59/2 |
| [854](https://github.com/iamcxa/kc-claude-plugins/pull/854) | 476/6 | 279/7 |
| [857](https://github.com/iamcxa/kc-claude-plugins/pull/857) | 0/0 | 0/0 |
| [861](https://github.com/iamcxa/kc-claude-plugins/pull/861) | 102/2 | 54/33 |
| [859](https://github.com/iamcxa/kc-claude-plugins/pull/859) | 0/0 | 0/0 |
| [860](https://github.com/iamcxa/kc-claude-plugins/pull/860) | 67/8 | 4/0 |
| [858](https://github.com/iamcxa/kc-claude-plugins/pull/858) | 4/2 | 2/1 |
| [852](https://github.com/iamcxa/kc-claude-plugins/pull/852) | 224/0 | 258/0 |
| [855](https://github.com/iamcxa/kc-claude-plugins/pull/855) | 104/0 | 82/5 |
| [853](https://github.com/iamcxa/kc-claude-plugins/pull/853) | 187/1 | 134/8 |
| [850](https://github.com/iamcxa/kc-claude-plugins/pull/850) | 0/0 | 0/0 |
| [849](https://github.com/iamcxa/kc-claude-plugins/pull/849) | 38/0 | 4/2 |
| [840](https://github.com/iamcxa/kc-claude-plugins/pull/840) | 0/0 | 0/0 |
| [846](https://github.com/iamcxa/kc-claude-plugins/pull/846) | 2/0 | 0/0 |
| [841](https://github.com/iamcxa/kc-claude-plugins/pull/841) | 385/40 | 182/12 |
| [844](https://github.com/iamcxa/kc-claude-plugins/pull/844) | 122/0 | 33/7 |
| [842](https://github.com/iamcxa/kc-claude-plugins/pull/842) | 0/0 | 0/0 |
| [843](https://github.com/iamcxa/kc-claude-plugins/pull/843) | 46/0 | 48/0 |

## Ten highest concentrations

Mapping is by checker/module owning the suite, not speculative per-rule line attribution. Denominator is all physical product-file lines, including comments/blanks; numerator is named test functions. The ADR/document suite maps to both owning modules. Shared helper coverage and script-style suites are not allocated to individual rules. Density is not a necessity score.

| Checker | Functions | Product lines | Tests / 100 lines |
|---|---:|---:|---:|
| codex_review.py | 36 | 167 | 21.56 |
| dispatch_records.py | 136 | 700 | 19.43 |
| laws_check.py | 85 | 452 | 18.81 |
| delivery_gate.py | 230 | 1239 | 18.56 |
| design_surfaces.py | 234 | 1261 | 18.56 |
| dispatch_stage.py | 52 | 292 | 17.81 |
| pr_watch.py | 147 | 831 | 17.69 |
| observer_check.py | 23 | 135 | 17.04 |
| copilot_review.py | 15 | 91 | 16.48 |
| poc_readme.py | 9 | 58 | 15.52 |

## Narrow duplicate candidates

- `CodexReviewTests.test_a_stalled_review_is_neither_a_round_nor_a_clean_one` overlaps `CodexReviewTests.test_exit_6_needs_a_running_code_review_of_the_head_and_no_result_on_it`. See both pinned source ranges in tests.csv. No deletion was made or declared safe.
- `L1Test.test_observer_before_the_sentinel_is_held_and_none_is_violated` overlaps `ExitContractTest.test_held_exits_0_and_violated_exits_1`. See both pinned source ranges in tests.csv. No deletion was made or declared safe.
- `RecheckTests.test_a_number_written_outside_the_number_guards_section_reserves_nothing` overlaps `RecheckTests.test_an_added_number_the_task_did_not_reserve_is_refused`. See both pinned source ranges in tests.csv. No deletion was made or declared safe.
- `TasksTests.test_a_task_without_a_pr_is_judged_without_review_rounds` overlaps `TasksTests.test_a_live_task_owing_a_role_call_prints_the_line_until_it_is_recorded`. See both pinned source ranges in tests.csv. No deletion was made or declared safe.

All outputs are under the assigned audit folder. Raw public source/history exports are working evidence; report tables and CSVs contain only package/public-PR references. No private repository was queried.
