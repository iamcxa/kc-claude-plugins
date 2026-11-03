# Validation cycle 2: PR #766

Verdict: **PASSED** at `0d8cb2b13be65d6cd8917d343797e8fa515e155f`, compared with fetched `origin/main` `84e3e492e512efad6e8b5b5b9764e4b13eb8a445`. No Review-finding disposition findings. This is independent Pilot validation, not gate approval or merge authority.

## Identity and execution boundary

- Code source: `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-second-round-prompts-a-step-back`, branch `spacedock-ensign/second-round-prompts-a-step-back`; tracked tree clean before and after.
- All checks ran against its detached `.context/validation-2-candidate` checkout at the named head. Both that checkout and the acceptance script's detached checkout were removed after verification.
- PR #766 is OPEN, base main, exact assigned head, with five successful hosted checks. PRs #763, #764 and #765 were verified MERGED at `52e8eba7bf3746fd93d9132548a8163c66a7a26b`, `e891e83582ac10936ffd67fb083b530b009ad847` and `84e3e492e512efad6e8b5b5b9764e4b13eb8a445`. The last is an ancestor of the candidate.
- The loaded validation skill resolves package scripts to `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0`; its package-root rule takes precedence over the dispatch's Claude cache path. No alternate package search was used.
- No agents spawned, product edit/commit/push, PR comment, review request, ready transition, approval or merge. State report/evidence alone follow the dispatched scoped state helper.

## Evidence per criterion

| Criterion | Observed proof | Falsifier run independently |
| --- | --- | --- |
| AC-1 | All three specified historical commands match their exits/reminders; passing reports, repeated findings within one report, fenced findings and Deferred risk controls pass. | Counting headings fails the named test and wrongly prints a reminder at c03f77631. |
| AC-2 | Both specified amendment revisions remind. A Design-only amendment and mixed one-plus-one counts stay silent. | Reusing the broader existing amendment events fails its test. |
| AC-3 | Real role checker through idle tasks yields one advisory and exit 0; first occurrence and archived controls are silent. Both repaired masking combinations reach this consumer. | Removing exit-0 forwarding fails the existing idle fixture. |
| AC-4 | Real checker through merge preserves advisory before record/ASK, ASK last, and unrelated problems. Both repaired masking combinations pass. A genuine origin/main script copy and candidate produce byte-identical first-occurrence output. | Dropping exit-0 forwarding or classifying the advisory as a problem each fails the existing merge fixture. |
| AC-5 | Both specified third-occurrence historical commands exit 1 with chief-engineer and three questions. Model/date/waiver, fourth occurrence, combined repair/review facts and committed-clearance fixtures pass. | Letting any chief-engineer call clear replacements fails the test and wrongly clears 7d203d562. |
| AC-6 | The literal `git diff --stat origin/main -- kc-dev-flow-2/references/sd/workflow.md kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md` prints nothing. Lint and all 26 CI commands pass. Three low-count historical byte comparisons match actual main. `wc -w` gives 51 advisory, 68/73 call, 79/84 including merge problem. | Adding a mod line to a disposable copy gives a nonempty diff and exit 1. |
| AC-7 | Both Captain ideation replies/questions, D1–D3 and their precedents match ADR 0026; its second amendment matches Captain amendment 1's masking repair. Installed ADR lint with `--since origin/main --require 0026` and candidate literal criterion command both exit 0: 49 records, 0 legacy. | Removed both new amendment paragraphs in a disposable copy and manually compared it to the live code and gate records: the new events and independent-reminder rule lack a decision. This semantic check is not proved by structural lint. |

AC-6 is satisfied as written **now**. The prior report used the integrated parent and noted eight inherited workflow lines against then-main; that old comparison is not reused as a pass for this head.

The review's precise masking claim was read from PR comment 4439960039. Candidate tests with the actual pre-repair `1c0dbb540` role checker fail in both directions. Five further mutations fail: omit either count, restore maximum-only selection tested in each direction, and remove three-question deduplication. At counts three and four, a cleared event leaves the other count's second-occurrence advisory visible. An ordinary repair-call line preserves the reminder; a third-event call already asking the three questions suppresses the duplicate.

Evidence: `replays.log`, `mutations.log`, `AC-*.log`, `masking-mutations.log`, `*-before.log`, `consumer-replays.log`, `first-occurrence-merge-bytes.log`, `word-counts.log`, `merge-word-counts.log`, `checks.json`.

## Whole suite and required checks

The runner reads the 26 Python command lines directly from the candidate's `.github/workflows/kc-dev-flow-2-tests.yml`. Each exits 0: **1,021 unittest cases, 0 failures, 7 skips**, plus native dispatch and observer-recovery scripts. Exact commands and output are in `run-suite.py`, `suite-results.txt` and each `*.py.log`.

Native checks use Spacedock 0.27.2 on darwin/arm64 and source downloaded from the exact CI pin `4d158a484ec73e184861067f8ed1e20087fdc26a`; URL and archive identity are in `pin.txt`. The hosted unit job at the same head succeeded on ubuntu-latest (run 41426741617), as recorded in `pr-766.json`. Skips and model-free native fixtures do not prove real model behavior. CI triggers did not change; cost per PR was not measured.

Installed `number_guards.py check`, `design_surfaces.py check`, `comment_ratio.py` and `dispatch_records.py` pass. Comments: 219 code lines, 0 comment lines, 0.0%, maximum 5% met; added script docstrings describe the resulting behavior. Both installed and candidate dispatch checkers report seven complete records; the prior report's installed-checker incompatibility does not reproduce with the currently installed package. `doc_impact.py` lists ADR 0044 (unaffected: optional question/summary contract unchanged) and ADR 0049 (unaffected: same model floor/defaults). ADR 0026 is updated.

The base/candidate corpus replay pins state `438554d2f89b6d125cf41413e7dc44bf290446e4`: 186 committed live/archive tasks, 13 changed outputs. Four newly hold (kc-decision-log-cli, paseo-codex-dispatch-practice, peer-status-reaches-fresh, peers-paseo-rule-matches-practice); each reaches at least one third-occurrence threshold. The other nine retain their exit and gain approved reminders or question text. The new thirteenth changed task, model-roster-question-needs-both-families, has two failed validations. All are intended under the approved separate counts and clearing rules; details are in `corpus.log`.

## Goal sufficiency, necessity and limits

The accepted outcome is supported at the declared Pilot depth: historical state reaches the real role script, both consumers surface the second occurrence without adding a hold, and committed third-occurrence clearance controls the merge ask. Removing event counting, either consumer forwarding, date clearing or the repair changes an observed outcome. The three implementation files, three corresponding test files and ADR 0026 each serve that behavior, its falsifiers or its required decision record; standing workflow text and versions stay unchanged.

Accepted limits re-judged, not repaired:
- Structured Material/Needs decision bullets count reports, not prose verdicts. Reports without them remain unseen; retained bullets in a nominally passed report still count. The five-of-thirteen historical omission is an accepted design finding, not a newly remeasured three-repository corpus result.
- Replacing amendments count regardless of direction; Design-only and Supersedes-none entries do not count for this reminder.
- Undated validation events can be cleared by an earlier qualified chief-engineer call/waiver. Replacement events use the third amendment's date; a fourth creates no new call requirement. This matches ADR 0026 and the accepted design.
- Second-occurrence reminders repeat without an answer record. Both role calls may be owed on the same task. These are approved costs.
- Fixture/historical stdout does not prove an FO reads or answers well, a real reviewer asks the questions, actual permission recovery, adoption or remote delivery. Native dispatch tests explicitly exclude worker execution and real human gates.
- The previous RoboRev daemon failures at old heads are not review evidence for this candidate. Exact-head RoboRev remains delegated to FO and was not run by this validator.
- Earlier implementation limits concerning unpublished repair/head and parent status have been superseded by the verified current PR/main identities and fresh hosted results above.

## Minimal acceptance script

This change has no graphical screen; readable CLI output is the acceptance surface. The six steps take well under five minutes here and require Bash, Python 3, Git, the named local repository with the candidate/base objects, the named state checkout with historical revisions and the explicitly named installed package. It covers the thresholds, repaired masking and consumer wiring; it does not replace the full suite, mutations, corpus review or prove human compliance.

Run unchanged in a fresh shell:

```sh
/bin/bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/second-round-prompts-a-step-back/validation-2/acceptance.sh'
```

The exact six steps (comments state expected outputs):



```bash
#!/bin/bash
set -euo pipefail
# Step 1: check out the exact candidate, detached. Expected: exact HEAD and integrated main.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-second-round-prompts-a-step-back'
STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
HEAD_SHA='0d8cb2b13be65d6cd8917d343797e8fa515e155f'
BASE_SHA='84e3e492e512efad6e8b5b5b9764e4b13eb8a445'
CHECKOUT=$(mktemp -d "$WT/.context/second-round-acceptance.XXXXXX")
git -C "$WT" worktree add --detach "$CHECKOUT" "$HEAD_SHA"
trap 'cd "$WT"; git -C "$WT" worktree remove "$CHECKOUT"' EXIT
cd "$CHECKOUT"
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = "$HEAD_SHA"
git -C "$CHECKOUT" merge-base --is-ancestor "$BASE_SHA" "$HEAD_SHA"
printf 'STEP 1 PASS: exact candidate and integrated main\n'

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
# Expected: all three commands report OK; 9, 1, and 2 tests respectively.
python3 -B kc-dev-flow-2/scripts/test_role_triggers.py StepBackTest
python3 -B kc-dev-flow-2/scripts/test_pr_watch.py TasksTests.test_second_failed_validation_is_advisory_live_and_silent_archived
python3 -B kc-dev-flow-2/scripts/test_delivery_gate.py OwedRoleCallTests.test_second_failure_prints_questions_before_ask_without_holding_and_with_other_problems OwedRoleCallTests.test_third_failure_holds_until_the_call_is_committed
printf 'STEP 5 PASS: thresholds and both consumers\n'

# Step 6: decision record and unchanged standing instructions. Expected: 49 records, no diff, clean tree.
python3 "$PACKAGE/scripts/adr_lint.py" docs/adr --since origin/main --require 0026
git -C "$CHECKOUT" diff --stat origin/main -- kc-dev-flow-2/references/sd/workflow.md kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md
git -C "$CHECKOUT" diff --exit-code origin/main -- kc-dev-flow-2/references/sd/workflow.md kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md
test -z "$(git -C "$CHECKOUT" status --porcelain)"
printf 'STEP 6 PASS: ADR, standing text, clean candidate\n'

```

Observed, unchanged fresh-shell run: **exit 0**.

```text
Preparing worktree (detached HEAD 0d8cb2b13)
HEAD is now at 0d8cb2b13 Merge remote-tracking branch 'origin/main' into spacedock-ensign/second-round-prompts-a-step-back
STEP 1 PASS: exact candidate and integrated main
next: paseo-codex-dispatch-practice has 2 validations with a Material or Needs decision finding and 0 replacing amendments: before the next step, answer: is what I am solving still the outcome first asked for; can this gap be tested now, or am I waiting; what breaks if this criterion or process is deleted?
STEP 2 PASS: exit 0
next: peers-paseo-rule-matches-practice has 1 validations with a Material or Needs decision finding and 2 replacing amendments: before the next step, answer: is what I am solving still the outcome first asked for; can this gap be tested now, or am I waiting; what breaks if this criterion or process is deleted?
STEP 3 PASS: exit 0
next: peers-paseo-rule-matches-practice has 3 replacing amendments; dispatch kc-dev-flow-2:chief-engineer on opus or gpt-6-astra with the question "is what I am solving still the outcome first asked for; can this gap be tested now, or am I waiting; what breaks if this criterion or process is deleted?" and record `Reviewer: kc-dev-flow-2:chief-engineer <model> <date> — <question>` under ## FO alignment; or, to decline, record `Reviewer: kc-dev-flow-2:chief-engineer not run <date>: <reason>` instead.
STEP 4 PASS: exit 1 is the expected hold
.........
----------------------------------------------------------------------
Ran 9 tests in 6.206s

OK
.
----------------------------------------------------------------------
Ran 1 test in 0.688s

OK
..
----------------------------------------------------------------------
Ran 2 tests in 2.397s

OK
STEP 5 PASS: thresholds and both consumers
49 ADR file(s) checked, 0 legacy
STEP 6 PASS: ADR, standing text, clean candidate
```
