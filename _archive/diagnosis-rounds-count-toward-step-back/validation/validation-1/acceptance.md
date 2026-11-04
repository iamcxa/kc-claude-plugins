# Five-step acceptance script

Candidate: 97cf87965ec052a1c9f2d40a1a1d0ca83e8d2244 (PR #771).
Prerequisites: the assigned local repository has that commit, Python 3, Git, and the dispatch-named 0.34.0 ADR-lint package. No sign-in, secrets, network, or browser UI is needed.

The output is command-line text; this task has no graphical screen. Run the complete script unchanged in a fresh Bash shell. It creates and removes its own detached worktree. This is a diagnostic acceptance run: step 4 deliberately exposes the unresolved design mismatch, so an exit 0 does not mean the candidate satisfies the approved design.

## Exact commands

```bash
#!/bin/bash
set -euo pipefail

# Step 1: Check the exact candidate in a temporary detached worktree.
SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-diagnosis-rounds-count-toward-step-back'
CANDIDATE=97cf87965ec052a1c9f2d40a1a1d0ca83e8d2244
CHECK_PARENT="$(mktemp -d "$SOURCE/.acceptance-771.XXXXXX")"
CHECKOUT="$CHECK_PARENT/code"
cleanup() {
  cd "$SOURCE"
  git -C "$SOURCE" worktree remove "$CHECKOUT"
  rmdir "$CHECK_PARENT"
}
git -C "$SOURCE" worktree add --detach "$CHECKOUT" "$CANDIDATE"
trap cleanup EXIT
cd "$CHECKOUT"
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = "$CANDIDATE"
printf 'STEP 1: candidate %s\n' "$CANDIDATE"

# Step 2: Check the dispatch reminder, separation and strict-header rules.
(cd "$CHECKOUT/kc-dev-flow-2/scripts" && python3 -B -m unittest -v test_dispatch_records.SymptomDispatchTests)
printf 'STEP 2: dispatch checks passed\n'

# Step 3: Check committed counts, dated clearing, nested paths, idle and merge.
(cd "$CHECKOUT/kc-dev-flow-2/scripts" && python3 -B -m unittest -v test_role_triggers.SymptomRoundsTest test_pr_watch.TasksTests.test_committed_second_symptom_round_is_forwarded_at_idle test_delivery_gate.OwedRoleCallTests.test_third_committed_symptom_round_holds_merge_ask)
printf 'STEP 3: committed-state and forwarding checks passed\n'

# Step 4: Reproduce the unresolved follow-up-message design mismatch.
python3 -B - <<'PY'
import contextlib
import io
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path.cwd() / "kc-dev-flow-2/scripts"))
import test_dispatch_records
import role_triggers
case = test_dispatch_records.SymptomDispatchTests()
case.setUp()
try:
    case.put(2, "page freeze")
    case.put(2, "page freeze", suffix="-message-1")
    case.put(2, "page freeze", suffix="-message-2")
    result = case.cli()
    groups = role_triggers.symptom_rounds([(p.name, p.read_text()) for p in case.dispatch.glob("*.md")])
    count = len(groups[("implementation", "page freeze")])
    reminder = "step back:" in result.stderr
    print(f"STEP 4: three symptom records, counted={count}, reminder={reminder}, exit={result.returncode}")
    assert (count, reminder, result.returncode) == (1, False, 0)
    print("EXPECTED UNRESOLVED MISMATCH: approved design includes follow-up message records; candidate excludes them.")
finally:
    case.doCleanups()
PY

# Step 5: Check the amended decision record and leave the candidate clean.
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since 713d4e6ed6381e65fa6d8305e08b282ceb56a8fb --require 26
test -z "$(git -C "$CHECKOUT" status --porcelain)"
printf 'STEP 5: ADR lint passed; candidate clean; temporary checkout will be removed\n'
```

## Expected observations

- Step 1: exact candidate SHA printed.
- Step 2: 4 dispatch tests pass.
- Step 3: 7 committed-state and forwarding tests pass, including the nested checkout test.
- Step 4: three symptom records count as 1 and produce no reminder; the unresolved mismatch is explicitly printed.
- Step 5: 50 ADR files checked, 0 legacy; candidate clean; temporary checkout removed.

## Observed run

Invocation: `/bin/bash --noprofile --norc /tmp/opencode/diagnosis-validation-771/acceptance.sh`.
Exit 0. The first sandbox attempt could not create Git metadata; the identical script was rerun with the approved filesystem escalation and passed, including cleanup. This is an environment permission limit, not a product defect.

Full observed output, unabridged:

```text
Preparing worktree (detached HEAD 97cf87965)
HEAD is now at 97cf87965 feat(kc-dev-flow-2): count diagnosis rounds by symptom
STEP 1: candidate 97cf87965ec052a1c9f2d40a1a1d0ca83e8d2244
test_different_stages_symptoms_none_fences_and_body_do_not_repeat (test_dispatch_records.SymptomDispatchTests.test_different_stages_symptoms_none_fences_and_body_do_not_repeat) ... ok
test_missing_line_hints_but_only_strict_holds_and_first_and_none_pass (test_dispatch_records.SymptomDispatchTests.test_missing_line_hints_but_only_strict_holds_and_first_and_none_pass) ... ok
test_named_record_excludes_later_records_and_folder_checks_only_each_stages_newest (test_dispatch_records.SymptomDispatchTests.test_named_record_excludes_later_records_and_folder_checks_only_each_stages_newest) ... ok
test_second_symptom_prints_questions_only_on_stderr_without_changing_verdict (test_dispatch_records.SymptomDispatchTests.test_second_symptom_prints_questions_only_on_stderr_without_changing_verdict) ... ok

----------------------------------------------------------------------
Ran 4 tests in 1.385s

OK
STEP 2: dispatch checks passed
test_archived_folder_records_and_nested_state_checkout (test_role_triggers.SymptomRoundsTest.test_archived_folder_records_and_nested_state_checkout) ... ok
test_cleared_symptom_cannot_mask_another_second_event_and_owed_questions_are_not_duplicated (test_role_triggers.SymptomRoundsTest.test_cleared_symptom_cannot_mask_another_second_event_and_owed_questions_are_not_duplicated) ... ok
test_date_model_and_waiver_clear_the_third_record_once (test_role_triggers.SymptomRoundsTest.test_date_model_and_waiver_clear_the_third_record_once) ... ok
test_groups_normalize_but_keep_stages_and_symptoms_separate (test_role_triggers.SymptomRoundsTest.test_groups_normalize_but_keep_stages_and_symptoms_separate) ... ok
test_second_advises_third_owes_and_only_committed_records_count (test_role_triggers.SymptomRoundsTest.test_second_advises_third_owes_and_only_committed_records_count) ... ok
test_committed_second_symptom_round_is_forwarded_at_idle (test_pr_watch.TasksTests.test_committed_second_symptom_round_is_forwarded_at_idle) ... ok
test_third_committed_symptom_round_holds_merge_ask (test_delivery_gate.OwedRoleCallTests.test_third_committed_symptom_round_holds_merge_ask) ... ok

----------------------------------------------------------------------
Ran 7 tests in 7.147s

OK
STEP 3: committed-state and forwarding checks passed
STEP 4: three symptom records, counted=1, reminder=False, exit=0
EXPECTED UNRESOLVED MISMATCH: approved design includes follow-up message records; candidate excludes them.
50 ADR file(s) checked, 0 legacy
STEP 5: ADR lint passed; candidate clean; temporary checkout will be removed
```

This script does not cover the full historical replay, corpus compatibility, complete package suite, hosted CI, real FO behavior, or release/adoption. Those results and limits are in details.md. Step 4 prevents mistaking the passing bounded smoke tests for complete goal sufficiency.
