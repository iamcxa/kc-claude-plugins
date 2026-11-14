# Test-value pass on five merged PRs

The pass found **one confirmed false-confidence case among 37 added or changed test methods**. All 37 methods pass at their own PR merge commits. The case is an ineffective negative assertion inside a useful contract test, so it is a reason to strengthen that assertion, not to delete the whole test. No product, test, README or script in the product checkout changed.

## Counts and exact revisions

Counts are generated in [counts.json](../evidence/implementation-1/counts.json). The complete method inventory, including file and line at the named merge commit, is in [inventory.tsv](../evidence/implementation-1/inventory.tsv); [audit.json](../evidence/implementation-1/audit.json) records the covered code, its callers and the individual reading conclusion for every method.

| PR | Merge commit | N: added/changed methods | F: flagged methods | F_ok: confirmed |
| --- | --- | ---: | ---: | ---: |
| #858 | `9bdc9f73083d8b2cf6a317a10f91a10a3d9fbb58` | 1 | 0 | 0 |
| #860 | `c7d4464c5da2611d2653d3732f05a1c17eff5a9e` | 6 | 0 | 0 |
| #859 | `c8d6dd40cf12ff6d9047e42e4d1041afa3bcf694` | 0 | 0 | 0 |
| #861 | `629180e576a8b7dafd6d9bf12202f7d66958bd6e` | 8 | 0 | 0 |
| #870 | `c2f035b6612f5edb42220576b3414e993531ffd6` | 22 | 1 | 1 |
| Total | | **37** | **1** | **1** |

N counts unittest methods whose complete source changed, or was added, between the merge commit and its first parent. It counts methods once per PR, not assertions, parameter combinations or subtests. There are 31 additions and six modifications; #858's renamed method is one modification. Changed setup/helpers are listed separately in [inventory.json](../evidence/implementation-1/inventory.json), without counting every indirectly affected existing method. #859 changes principles and an architectural decision record, and changes no test file; its N is zero, not a skipped test run or evidence about worker compliance.

## Confirmed flag: false-confidence

At #870, `kc-dev-flow-2/scripts/test_task_timeline.py:196`, `TimelineTests.test_ask_cli_appends_utc_questions_and_rejects_empty_without_write` executes two valid asks with `--holds task --by "test FO"`. Its blank-input assertion at line 205 instead calls `self.cli("demo", "ask", "  ")` and checks only exit 2 and unchanged bytes.

**What it stood in for:** proof that the CLI rejects an empty question without writing a record. The actual call is rejected for a missing owner before reaching question validation.

The complete test and its helpers were read. The covered production path is `task_timeline.main` (lines 510 onward), its required-owner check (543–548), `write_event` (318 onward), and `validate_revision` (291–293), called from `write_event` at 376–377. The normal CLI calls `main`, and `references/sd/workflow.md:259` instructs the First Officer to use that CLI with both `--holds` and `--by`. The positive branches exercise persistence and timeline counting, and are valuable.

**Observed execution:** the whole method passes in [pr-870-tests.log](../evidence/implementation-1/pr-870-tests.log). Two further unmodified CLI executions are retained in [blank-question-probe.json](../evidence/implementation-1/blank-question-probe.json):

| Probe | Exit | Observed rejection | Record written |
| --- | ---: | --- | --- |
| Same blank call as the test | 2 | `ask needs --by with the FO session name` | no |
| Blank call with valid owner and hold | 2 | `question needs nonempty asked and holds task\|acceptance\|nothing` | no |

**Falsifier and limit:** source control flow plus the first probe establish that the assertion cannot detect removal of the later blank-question check: it would still stop at the earlier owner check. This is a causal reading, not an executed mutation; no implementation was edited. The second probe establishes that the current product does reject empty questions correctly. The public-contract exception retains the method's useful append, UTC, persistence and count coverage. A separately authorized repair could give the negative call valid `--by` and `--holds` values and require the intended error cause; this report authorizes no repair or deletion.

No implementation-coupled, duplicate or test-only-seam test was confirmed in this set. Similar input fixtures at separate consumers were retained because bypassing a consumer's wiring can break one while the others pass. Redundant individual assertions were not inflated into duplicate test-method findings.

## Unflagged sample and why it passes the bar

These are samples from the 36 unflagged methods; [audit.json](../evidence/implementation-1/audit.json) covers all 37 method readings. Paths below are under `kc-dev-flow-2/scripts` at the PR's exact merge revision.

| PR / method | Why keep it; change that would fail it |
| --- | --- |
| #858 `TasksTests.test_an_empty_pr_whose_worktree_is_gone_is_a_fact_and_one_with_no_worktree_field_stays_silent` | Builds real task/state repositories and removes a fixture worktree, then runs the actual `pr_watch.main -> tasks` path. Reverting `fact:` to a PR-recording `next:` fails. GitHub and workflow-runtime stubs are environmental boundaries, not replacements for the changed missing-directory branch. |
| #860 `TaskArgumentTests.test_same_named_directory_checks_the_sibling_task_in_both_modes` | Invokes the real CLI subprocess with explicit and bare paths, including dots, with and without seed mode. Removing directory-to-sibling resolution fails. This is CLI contract behavior, not source-text containment. |
| #860 `TaskArgumentTests.test_resolving_a_name_preserves_a_failing_verdict` | Creates an actually invalid surface and proves both argument forms retain exit 1. A resolver that always returns success fails. Other argument tests exercise distinct precedence/error branches. |
| #861 `L1Test.test_l1_uses_the_shared_extension_list_forms_and_ignores_comment_words` | Creates a real Git history with a missing-observer sentinel, then runs the history-law checker. Disabling judging for selected learn, or enabling it from comment text, changes the observed verdict. |
| #861 `TasksTests.test_a_merged_task_pr_with_the_report_committed_lets_pr_merge_record_it_and_names_the_steps_after` | Executes the observer command printed by the real watcher in a detached state checkout, before and after archive, then switches learn off. Omitting forwarded `--readme` fails. Parser tests alone do not cover this wiring. |
| #861 `RecoveryCommandQuotingTest.test_the_printed_late_report_commands_run_when_the_state_path_has_whitespace` | Executes the emitted Git recovery commands in a whitespace path and verifies the report is committed. Broken quoting fails; this is not a text-only command pin. |
| #870 `QuestionRecordTests.test_missing_record_refuses_and_present_record_passes_in_split_root_worktree` | Uses actual adoption commits and a linked Git worktree, and compares missing versus present question records through the CLI. Disabling omission refusal fails. The adoption constant is setup, not the only assertion. |
| #870 `TimelineTests.test_contract_writer_refuses_every_event_after_closing_except_one_acted` | Tests the documented event-state protocol and compares persisted bytes after refusal. Allowing a second acted event fails; the public-protocol exception protects this boundary. |
| #870 `TimelineTests.test_readme_plain_open_entrance_and_mixed_gate_rows_have_question_text` | Runs plain and JSON CLI entrances with both native gate and question rows. Omitting question text fails the entrance, including the plain formatter, rather than only an internal helper. |
| #870 `TimelineTests.test_replayed_fourteen_questions_at_declared_synthetic_times` | Exercises the real CLI at synthetic open/closed boundaries and compares question identities and fields. Keep for record selection and protocol integration; expected minutes reuse production `mins`, so it is not independent proof of minute arithmetic or historical response time. |

## Method, source checks and exceptions

The five diffs were read with `git diff <merge>^ <merge>`. Tests ran with `python3 -B -m unittest -v <selected methods>` from exports created by `git archive` at each merge revision. `TMPDIR` was inside dispatch scratch and bytecode writing was disabled. No product Git worktree, branch or configuration was changed to run them. Logs preserve the actual commands, unittest totals, outcomes and exit status: [#858](../evidence/implementation-1/pr-858-tests.log), [#860](../evidence/implementation-1/pr-860-tests.log), [#861](../evidence/implementation-1/pr-861-tests.log), [#870](../evidence/implementation-1/pr-870-tests.log). Machine-readable results are [tests.json](../evidence/implementation-1/tests.json) and [tests.xml](../evidence/implementation-1/tests.xml).

The original Compound Engineering `ce-simplify-code/references/personas/test-value-reviewer.md` was not found in the installed plugin sources checked. This is explicitly an application of the task's quoted four classes and run/read/caller rule, together with the dispatch's public-contract, protocol and security exceptions; it does not claim to reproduce unquoted persona instructions. Every test method was run and read before the final classification. No flag was based on mocks or direct helper calls alone.

Existing package skills and workflow instructions supplied the actual callers. Architectural decision records 0072 (saved count evidence), 0079 (retain public evidence and close scratch), 0083 (check existing sources) and 0086 (question record contract) were consulted at the pinned task base. They retain their Accepted status; their exact commits and digests are in [adr-sources.json](../evidence/implementation-1/adr-sources.json). No new ruling or architecture record is produced by this measurement. The exact inspected source bytes, compared unchanged against Git after execution, are recorded in [source-locks.json](../evidence/implementation-1/source-locks.json).

To reproduce, run the retained `reproduce.py` with Python 3.12 or newer, Git, a repository containing the five commits, and a fresh scratch directory. From the task folder, for example:

```sh
python3 -B evidence/implementation-1/reproduce.py --repo <repository-root> --scratch <new-scratch-directory>
```

The script exports the named commits and runs exactly the inventoried methods and both blank-input probes. It leaves its outputs for inspection. It never changes the supplied repository or publishes anything. No network or authenticated GitHub access is required to rerun the measurement once those commits exist locally.

The retained reproducer was itself executed once in fresh scratch: all 37 selected methods passed again, and both blank-input error causes were reproduced. This is a second execution of the same 37 methods, not 37 additional distinct tests. See [reproduction-summary.json](../evidence/implementation-1/reproduction-summary.json) and [reproduction.log](../evidence/implementation-1/reproduction.log).

## Stop condition, stage checks and limits

The stop condition was applied: stop if more than one third of flagged tests is overturned after reading. One test method was flagged, one was confirmed by execution and whole-test/code/caller reading, and zero were overturned: `0 / 1`, so the condition did not fire. No rejected flag was removed from the denominator. No initial text-only suspicion was counted as a confirmed flag.

[stage-checks.json](../evidence/implementation-1/stage-checks.json) records the ancillary checks at unchanged base/candidate `c2f035b6612f5edb42220576b3414e993531ffd6`:

- Comment ratio: exit 0, zero code and comment lines changed.
- Document impact: exit 0, zero affected product documents.
- Number guards: exit 0, no findings; migration guard skipped because no migrations path is declared, and state-fetch failure means reservation refs may be stale. No migration or number reservation was added.
- Design surfaces: **not applicable to this POC route**, per FO's explicit dispatch correction: the README limits the seed check to the five-stage route. An exploratory invocation exited 1 on absent `Surfaces:` and `Visible change:` fields; its raw output is preserved, but is not a task failure. The accepted body was not rewritten by the worker.

This is one implementation cycle, for the bounded five-PR set chosen in one trial. It measures neither package-wide prevalence, false-negative rate, review savings, CI cost nor test-suite completeness. Only the 37 in-scope methods were run, not the package suite. A passing test log is not proof of a live day of human question recording, cold-worker rule compliance or remote-reader compatibility. RoboRev was not run: there is no code candidate. Independent validation, FO disposition and any Captain-authorized deletion or repair remain separate.

## Handoff

Product branch: `spacedock-ensign/test-value-pass-on-route-trial-prs-poc`. Base and unchanged candidate: `c2f035b6612f5edb42220576b3414e993531ffd6`. No product commit, push or pull request; prepared PR text is not applicable to this read-only task. The report and evidence belong only to this task on the shared state branch. FO's final dispatch correction explicitly owns the state commit, without worker escalation, because the sandbox refuses Git-directory writes. State files are handed back for that commit; no worker state commit or push was attempted. FO also owns the copy beside the study and the independent validation dispatch. Scratch close-out is recorded in the entity's implementation Stage Report.
