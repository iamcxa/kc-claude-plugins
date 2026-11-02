# Independent validation: second-round-prompts-a-step-back

Verdict: **PASSED** at the exact candidate; no product findings.

Candidate: `1c0dbb540f354300b75dba5a119d2614c8fb0c02`, [PR #766](https://github.com/iamcxa/kc-claude-plugins/pull/766).
Stack base: `3c49c24a3eba3d90093f330c051b682a3335ae23`, the live head of [PR #765](https://github.com/iamcxa/kc-claude-plugins/pull/765), verified as an ancestor.
Reviewed in detached worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-second-round-prompts-a-step-back/.context/validation-1-worktree`; original worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-second-round-prompts-a-step-back` stays on its assigned branch.
All seven task paths are byte-identical to implementation `92dbf1d32c7142e010fad6a7d9807a17ae0ce240`; the parent repair is integrated.
State corpus is pinned at `4b7b297dfd1000f9cb3d0ec59e952533287eeb89`.

## Acceptance criteria and falsifiers

| Criterion | Independently exercised evidence | Falsifying change and observed result |
| --- | --- | --- |
| AC-1 | Historical e0dc64f88 prints one 51-word reminder, exit 0; 1e17be9a0 and c03f77631 have none. StepBackTest counts each report once and excludes fences, Deferred risk and Polish. | Counting report headings makes the test fail (exit 1) and wrongly prints a reminder at c03f77631. |
| AC-2 | Historical 95c1ecc8b and ff2063c53 print the reminder. Fixture excludes Design-only replacements, Supersedes none, and mixed 1+1 counts. | Reusing the broader events count makes the fixture fail, exit 1. |
| AC-3 | TasksTests.test_second_failed_validation_is_advisory_live_and_silent_archived runs the real role checker through the idle consumer: first occurrence silent, second prints with exit 0, archived silent. | Removing exit-0 forwarding makes that test fail, exit 1. |
| AC-4 | OwedRoleCallTests.test_second_failure_prints_questions_before_ask_without_holding_and_with_other_problems runs the real checker: reminder precedes the record, ASK remains last, and a Draft-PR problem survives. | Dropping exit-0 forwarding and treating advisory output as a problem each fail the test, exit 1. |
| AC-5 | Historical 0e5b6f59a and 7d203d562 exit 1 and owe chief-engineer with all three questions, no advisory. Fixtures cover date/model floors, waivers, fourth event, combined repair/review facts, and committed versus uncommitted clearance at merge. | Clearing replacements with any earlier call fails the dated-clear fixture and wrongly clears chief-engineer at 7d203d562. |
| AC-6 | Below-threshold outputs equal the parent byte-for-byte for three historical revisions. Workflow and mod are unchanged from the actual stack base. `wc -w` independently measured 51 advisory / 68 replacement-call / 73 failure-call; the unchanged 11-word merge problem yields 79 / 84. Full suite outcome is recorded below. | Adding one standing mod line produces a nonempty diff, exit 1. Literal origin/main has eight inherited workflow lines; the task adds none, and the latest dispatch explicitly validates this stack. |
| AC-7 | Manually compared ADR 0026's final amendment to both ideation resolutions: exact 「可以」 and 「照建議」 questions, structured F-bullet count, third-event hold/waiver, chief-engineer selection and prior precedents match. | Removing the final amendment leaves the two new events in code without an ADR ruling. I inspected the omitted copy; the semantic omission is not machine-checked by ADR lint. |

Executed proof driver: `python3 -B /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-second-round-prompts-a-step-back/.context/validation-1-evidence/verify.py`.
It reuses the implementation's existing proof driver, changing only the checkout and current stack base, writes fresh logs, uses cache-free mutant copies, and does not alter product files.
The driver completed eight historical replays, three base-output comparisons, six rejected behavioral mutations, a standing-text diff control, and the ADR omission control.
`replays.log`, `mutations.log`, and the six AC mutation logs retain primary output.
The same driver compared 186 committed live/archive tasks: 12 changed outputs, every change at an approved threshold; the newly held tasks all reach three. No source facts were inferred from report headings alone.

## Required checks

Loaded validation skill package root: `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0`. The stage's package rule uses this loaded root instead of the dispatch's Claude cache path.
Commands ran from the detached candidate; `checks.json` retains exact commands, outputs and exits.

- `python3 /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since 3c49c24a3eba3d90093f330c051b682a3335ae23 --require 0026`: exit 0, 49 ADR files checked, 0 legacy. The literal `--since origin/main --require 0026` also returned exit 0.
- `comment_ratio.py`: 185 code lines, 0 comment lines, 0.0%, maximum 5% met; manually read added docstrings.
- `number_guards.py check` with explicit candidate/base/workflow/task: exit 0, no findings, migration check inapplicable.
- `design_surfaces.py check`: exit 0, presentable; no graphical user interface is in scope.
- `doc_impact.py`: ADR 0044 unaffected because optional summary/question behavior is unchanged; ADR 0049 unaffected because model rankings and floor are reused. ADR 0026 is updated.
- Installed `dispatch_records.py`: exit 1 on three final-reply records because the old installed package requires main-recipient prose. Candidate `dispatch_records.py`: exit 0, all five records complete. ADR 0048 explicitly accepts final-reply completion, and the parent implements that compatibility; this is a diagnosed installed-version limit, not a product finding.

## Full suite

**26/26 commands exit 0; 1,018 unittest cases, zero failures, seven skips.** The skipped cases are optional external corpus/configuration and integration cases already conditional in the suite; none is a new step-back test. Native dispatch/recovery both pass.

The 26 Python commands are selected directly from `.github/workflows/kc-dev-flow-2-tests.yml` by the retained `run-suite.py`, preserving their order and arguments except explicit local path substitution.
The native checks use Spacedock CLI 0.27.2 (darwin/arm64) and a fresh archive fetched from the exact CI source commit `4d158a484ec73e184861067f8ed1e20087fdc26a`.
CI uses ubuntu-latest; this local run does not claim Linux execution.
`PYTHONDONTWRITEBYTECODE=1` avoids validation-generated caches; no product/configuration edits are made.
Per-command outputs and timing are in the `*.py.log` files; `suite-results.txt` records every exit.

## Implementation limits and finding disposition

No Material, Deferred risk, Polish or Needs decision finding was established against the accepted candidate.
The admitted semantic limits remain: replacements do not prove relaxation; reports without structured F bullets are invisible; a passing report retaining a Material/Needs decision bullet still counts; any qualifying older call can clear undated validation failures; a same-day call can clear a dated amendment; the second-occurrence reminder repeats; and this code cannot grade FO answers or prove a reviewer actually asked the questions.
The historical multi-repository 5-of-13 / 221-task ideation statistics were not re-derived; they are accepted design context, not new validation evidence. The current local 186-task corpus was independently rerun.
The earlier inherited README test failure is tested at the repaired head, not excused as inherited.
Exact-head RoboRev remains delegated to FO; the older daemon failure supplies no current review result. No review, PR comment, ready transition, product push, merge, adoption, or approval is authorized by this verdict.
Hosted PR metadata was refreshed at 2026-11-02 07:39:51 UTC: PR #766 is OPEN/Draft at the exact head and all five checks succeeded; the parent's head is unchanged and its five checks also succeeded. The hosted unit-test run is [41405815562](https://github.com/iamcxa/kc-claude-plugins/actions/runs/41405815562).
CI triggers are unchanged by this task. Cost per PR was not measured; local elapsed test time is not billed CI cost.

Goal sufficiency: the approved counts produce the questions at both existing consumers, with the third-event hold and clearing rules.
Minimal necessity: role counting/formatting enables the events, both consumers must forward exit-0 advisories, the tests reject the promised errors, and ADR 0026 retains the Captain's rule. The seven-file diff adds no standing workflow instruction, new lifecycle stage, or persistent state.

## Six-step Captain acceptance script

Prerequisites: this repository at the stated worktree, Python 3, Git, the declared installed package, and the state checkout containing the named historical commits.
Run `/bin/bash --noprofile --norc acceptance.sh` from this evidence directory. It creates and removes its own detached checkout under the authorized worktree. In the validator sandbox, writing Git worktree metadata required the standard escalation; no git config or remote URL is changed.
The first draft's comment said seven StepBackTest cases; actual count is six. The corrected script below was then run unchanged in a fresh shell, exit 0, and all six STEP PASS markers were observed.
There is no changed graphical screen. This script demonstrates observable console behavior and the two local consumer seams; it does not rerun all 26 CI commands, provider review, natural FO behavior, or delivery.


```bash
#!/bin/bash
set -euo pipefail
# Step 1: check out the exact candidate, detached. Expected: exact HEAD and integrated parent.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-second-round-prompts-a-step-back'
STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
HEAD_SHA='1c0dbb540f354300b75dba5a119d2614c8fb0c02'
BASE_SHA='3c49c24a3eba3d90093f330c051b682a3335ae23'
CHECKOUT=$(mktemp -d "$WT/.context/second-round-acceptance.XXXXXX")
git -C "$WT" worktree add --detach "$CHECKOUT" "$HEAD_SHA"
trap 'cd "$WT"; git -C "$WT" worktree remove "$CHECKOUT"' EXIT
cd "$CHECKOUT"
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = "$HEAD_SHA"
git -C "$CHECKOUT" merge-base --is-ancestor "$BASE_SHA" "$HEAD_SHA"
printf 'STEP 1 PASS: exact candidate and integrated parent\n'

# Step 2: two failed validations. Expected: one advisory with all three questions, exit 0.
python3 -B kc-dev-flow-2/scripts/role_triggers.py "$STATE" paseo-codex-dispatch-practice --rev e0dc64f886cf80e7579551a4002a05b4c603f1c9
printf 'STEP 2 PASS: exit 0\n'

# Step 3: two replacing amendments. Expected: one advisory with all three questions, exit 0.
python3 -B kc-dev-flow-2/scripts/role_triggers.py "$STATE" peers-paseo-rule-matches-practice --rev ff2063c539a2fbf8c446797d7051fc34c406aff9
printf 'STEP 3 PASS: exit 0\n'

# Step 4: third replacing amendment. Expected: chief-engineer owed with three questions, exit 1.
if python3 -B kc-dev-flow-2/scripts/role_triggers.py "$STATE" peers-paseo-rule-matches-practice --rev 7d203d562789a107d651f3169b6a89b153024d33; then
  printf 'FAIL: third occurrence did not hold\n'
  exit 1
else
  test "$?" -eq 1
fi
printf 'STEP 4 PASS: exit 1 is the expected hold\n'

# Step 5: exercise thresholds, idle, and merge with the real role checker.
# Expected: all three commands report OK; 6, 1, and 2 tests respectively.
python3 -B kc-dev-flow-2/scripts/test_role_triggers.py StepBackTest
python3 -B kc-dev-flow-2/scripts/test_pr_watch.py TasksTests.test_second_failed_validation_is_advisory_live_and_silent_archived
python3 -B kc-dev-flow-2/scripts/test_delivery_gate.py OwedRoleCallTests.test_second_failure_prints_questions_before_ask_without_holding_and_with_other_problems OwedRoleCallTests.test_third_failure_holds_until_the_call_is_committed
printf 'STEP 5 PASS: thresholds and both consumers\n'

# Step 6: decision record and unchanged standing instructions. Expected: 49 records, no diff, clean tree.
python3 "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE_SHA" --require 0026
git -C "$CHECKOUT" diff --exit-code "$BASE_SHA" "$HEAD_SHA" -- kc-dev-flow-2/references/sd/workflow.md kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md
test -z "$(git -C "$CHECKOUT" status --porcelain)"
printf 'STEP 6 PASS: ADR, standing text, clean candidate\n'

```

Observed output:

```text
Preparing worktree (detached HEAD 1c0dbb540)
HEAD is now at 1c0dbb540 Merge remote-tracking branch 'origin/spacedock-ensign/model-roster-question-needs-both-families' into spacedock-ensign/second-round-prompts-a-step-back
STEP 1 PASS: exact candidate and integrated parent
next: paseo-codex-dispatch-practice has 2 validations with a Material or Needs decision finding and 0 replacing amendments: before the next step, answer: is what I am solving still the outcome first asked for; can this gap be tested now, or am I waiting; what breaks if this criterion or process is deleted?
STEP 2 PASS: exit 0
next: peers-paseo-rule-matches-practice has 1 validations with a Material or Needs decision finding and 2 replacing amendments: before the next step, answer: is what I am solving still the outcome first asked for; can this gap be tested now, or am I waiting; what breaks if this criterion or process is deleted?
STEP 3 PASS: exit 0
next: peers-paseo-rule-matches-practice has 3 replacing amendments; dispatch kc-dev-flow-2:chief-engineer on opus or gpt-6-astra with the question "is what I am solving still the outcome first asked for; can this gap be tested now, or am I waiting; what breaks if this criterion or process is deleted?" and record `Reviewer: kc-dev-flow-2:chief-engineer <model> <date> — <question>` under ## FO alignment; or, to decline, record `Reviewer: kc-dev-flow-2:chief-engineer not run <date>: <reason>` instead.
STEP 4 PASS: exit 1 is the expected hold
......
----------------------------------------------------------------------
Ran 6 tests in 5.173s

OK
.
----------------------------------------------------------------------
Ran 1 test in 0.734s

OK
..
----------------------------------------------------------------------
Ran 2 tests in 2.019s

OK
STEP 5 PASS: thresholds and both consumers
49 ADR file(s) checked, 0 legacy
STEP 6 PASS: ADR, standing text, clean candidate
```

## Per-command observed results

```text
lint-skills.py exit=0 seconds=0.18
test_lint_skills.py exit=0 seconds=9.68
test_design_surfaces.py exit=0 seconds=10.33
test_adr_doc_checks.py exit=0 seconds=1.04
test_poc_readme.py exit=0 seconds=1.39
test_comment_ratio.py exit=0 seconds=6.77
test_number_guards.py exit=0 seconds=15.85
test_codex_review.py exit=0 seconds=0.08
test_roborev_gate.py exit=0 seconds=2.06
test_copilot_review.py exit=0 seconds=0.05
test_map_footprint.py exit=0 seconds=0.26
test_release_acceptance.py exit=0 seconds=1.21
test_dispatch_records.py exit=0 seconds=84.78
test_delivery_gate.py exit=0 seconds=66.53
test_validation_security.py exit=0 seconds=0.58
test_pr_watch.py exit=0 seconds=51.73
test_replay_dispatch.py exit=0 seconds=5.24
test_decision_ledger.py exit=0 seconds=0.07
test_package_version.py exit=0 seconds=0.06
test_workflow_checkout.py exit=0 seconds=7.31
test_observer_check.py exit=0 seconds=6.38
test_role_triggers.py exit=0 seconds=24.14
test_laws_check.py exit=0 seconds=76.61
test_learning.py exit=0 seconds=46.23
test_sd_dispatch.py exit=0 seconds=45.16
test_observer_recovery.py exit=0 seconds=2.57
```

Native dispatch remains model-free: it does not prove skill discovery/reading, worker execution, human gates, delivery hook execution, or remote merge.
