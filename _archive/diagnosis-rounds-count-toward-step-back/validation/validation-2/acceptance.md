# Acceptance at PR #771, repair head

Candidate: 7aad891353a973c7fbda2ad4214a3aadea71d2a6.
Comparison: origin/main e1bee223c47a1cd534a665a47776b683375b34fc; PR merge base 713d4e6ed6381e65fa6d8305e08b282ceb56a8fb.
There is no graphical screen. These five steps exercise the command output instead.
Requirements: the named existing source checkout and candidate object, Python 3, Git, and the named installed 0.34.0 ADR checker. No network, sign-in, or secret is needed. Git must be allowed to create/remove its own worktree metadata.

Run the following script unchanged with /bin/bash --noprofile --norc. The validator did so, exit 0.
It creates and removes one detached checkout under the assigned source worktree; it does not change Git configuration.

Expected observations:
1. The exact candidate SHA is printed.
2. Six dispatch tests pass, covering message follow-ups, grouping, numeric cutoff and strict-header behavior.
3. Nine committed-state/integration tests pass, covering dates, nested/archive paths, event independence, real idle forwarding and the merge hold.
4. Three symptom records report counted=3, reminder=True, exit=0.
5. ADR lint reports 50 records, 0 legacy; the candidate stays clean and its temporary checkout is removed.

Scope: this quick script proves the selected CLI paths at the exact commit. It does not replay the full historical corpus, repeat every mutation, authenticate the Captain's original chat, complete RoboRev, approve a merge, or prove adoption.

## Exact five-step script

```bash
#!/bin/bash
set -euo pipefail

# Step 1: Check the exact candidate in a temporary detached worktree.
SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-diagnosis-rounds-count-toward-step-back'
CANDIDATE=7aad891353a973c7fbda2ad4214a3aadea71d2a6
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

# Step 4: Observe three rounds across a plain record and two follow-up messages.
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
    assert (count, reminder, result.returncode) == (3, True, 0)
    print("Follow-up message records count, as required by Captain amendment 1.")
finally:
    case.doCleanups()
PY

# Step 5: Check the amended decision record and leave the candidate clean.
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since e1bee223c47a1cd534a665a47776b683375b34fc --require 26
test -z "$(git -C "$CHECKOUT" status --porcelain)"
printf 'STEP 5: ADR lint passed; candidate clean; temporary checkout will be removed\n'
```

## Observed output

```text
Preparing worktree (detached HEAD 7aad89135)
HEAD is now at 7aad89135 fix(kc-dev-flow-2): count follow-up messages as diagnosis rounds
STEP 1: candidate 7aad891353a973c7fbda2ad4214a3aadea71d2a6
test_different_stages_symptoms_none_fences_and_body_do_not_repeat (test_dispatch_records.SymptomDispatchTests.test_different_stages_symptoms_none_fences_and_body_do_not_repeat) ... ok
test_missing_line_hints_but_only_strict_holds_and_first_and_none_pass (test_dispatch_records.SymptomDispatchTests.test_missing_line_hints_but_only_strict_holds_and_first_and_none_pass) ... ok
test_named_record_excludes_later_records_and_folder_checks_only_each_stages_newest (test_dispatch_records.SymptomDispatchTests.test_named_record_excludes_later_records_and_folder_checks_only_each_stages_newest) ... ok
test_one_plain_and_two_messages_count_at_folder_and_named_dispatch_checks (test_dispatch_records.SymptomDispatchTests.test_one_plain_and_two_messages_count_at_folder_and_named_dispatch_checks) ... ok
test_second_symptom_prints_questions_only_on_stderr_without_changing_verdict (test_dispatch_records.SymptomDispatchTests.test_second_symptom_prints_questions_only_on_stderr_without_changing_verdict) ... ok

----------------------------------------------------------------------
Ran 5 tests in 1.995s

OK
STEP 2: dispatch checks passed
test_archived_folder_records_and_nested_state_checkout (test_role_triggers.SymptomRoundsTest.test_archived_folder_records_and_nested_state_checkout) ... ok
test_cleared_symptom_cannot_mask_another_second_event_and_owed_questions_are_not_duplicated (test_role_triggers.SymptomRoundsTest.test_cleared_symptom_cannot_mask_another_second_event_and_owed_questions_are_not_duplicated) ... ok
test_date_model_and_waiver_clear_the_third_record_once (test_role_triggers.SymptomRoundsTest.test_date_model_and_waiver_clear_the_third_record_once) ... ok
test_groups_normalize_but_keep_stages_and_symptoms_separate (test_role_triggers.SymptomRoundsTest.test_groups_normalize_but_keep_stages_and_symptoms_separate) ... ok
test_message_numbers_order_the_third_round_date_numerically (test_role_triggers.SymptomRoundsTest.test_message_numbers_order_the_third_round_date_numerically) ... ok
test_one_plain_and_two_message_records_remind_then_owe_a_dated_call (test_role_triggers.SymptomRoundsTest.test_one_plain_and_two_message_records_remind_then_owe_a_dated_call) ... ok
test_second_advises_third_owes_and_only_committed_records_count (test_role_triggers.SymptomRoundsTest.test_second_advises_third_owes_and_only_committed_records_count) ... ok
test_committed_second_symptom_round_is_forwarded_at_idle (test_pr_watch.TasksTests.test_committed_second_symptom_round_is_forwarded_at_idle) ... ok
test_third_committed_symptom_round_holds_merge_ask (test_delivery_gate.OwedRoleCallTests.test_third_committed_symptom_round_holds_merge_ask) ... ok

----------------------------------------------------------------------
Ran 9 tests in 10.333s

OK
STEP 3: committed-state and forwarding checks passed
STEP 4: three symptom records, counted=3, reminder=True, exit=0
Follow-up message records count, as required by Captain amendment 1.
50 ADR file(s) checked, 0 legacy
STEP 5: ADR lint passed; candidate clean; temporary checkout will be removed
```
