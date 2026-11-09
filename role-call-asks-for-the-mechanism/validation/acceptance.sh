#!/usr/bin/env bash
set -euo pipefail
# Requirements: this repository clone, bash, git, tar, Python 3, and the installed
# kc-dev-flow-2 0.36.0 package at the absolute path below. No secrets required.
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-role-call-asks-for-the-mechanism
PACKAGE=/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0
HEAD_SHA=ebbac3de0dbf3b9bf9bf4c59611ff06bb5eb4fe9
BASE_SHA=82c9e67ae892b80647c3f6a8b6929f993e42dbc2
CHECK_DIR=$(mktemp -d /tmp/pr821-acceptance.XXXXXX)

# 1. Export the exact candidate and base. Expect the two pinned revisions.
mkdir -p "$CHECK_DIR/candidate" "$CHECK_DIR/base"
git -C "$REPO" archive "$HEAD_SHA" > "$CHECK_DIR/candidate.tar"
tar -xf "$CHECK_DIR/candidate.tar" -C "$CHECK_DIR/candidate"
git -C "$REPO" archive "$BASE_SHA" > "$CHECK_DIR/base.tar"
tar -xf "$CHECK_DIR/base.tar" -C "$CHECK_DIR/base"
printf 'Candidate: %s\nBase: %s\n' "$HEAD_SHA" "$BASE_SHA"

# 2. Exercise the actual CLI against a committed throwaway task. Expect an owed
# mechanism question for a plain decline (exit 1), then a reasoned clear (exit 0).
cd "$CHECK_DIR/candidate/kc-dev-flow-2/scripts"
python3 -B - <<'PY'
import test_role_triggers as t
f = t.Fixture()
f.setUp()
try:
    failures = t.validations(*([t.StepBackTest.failed] * 3))
    for reason, expected in [('the outcome is unchanged; the gap is testable now', 1), ('unrelated: F1 home exit; F2 late response', 0)]:
        f.put(t.task(extra=f'Reviewer: {t.CE} not run 2026-11-09: {reason}') + failures)
        code, out = t.run(f.state, t.SLUG)
        assert code == expected, (code, out)
        assert (t.MECHANISM in out) == bool(expected), out
        print(f'decline exit={code}: {out.strip()}')
finally:
    f.doCleanups()
PY

# 3. Run six focused acceptance cases. Expect six tests, OK.
python3 -B -m unittest \
  test_role_triggers.RoleTriggersTest.test_repair_and_review_only_events_keep_the_smallest_next_step_question \
  test_role_triggers.StepBackTest.test_third_failure_owes_one_mechanism_call_even_with_repairs_and_rounds \
  test_role_triggers.StepBackTest.test_a_third_findings_or_amendment_call_suppresses_the_second_event_reminder \
  test_role_triggers.SymptomRoundsTest.test_both_findings_events_require_distinct_causes_in_the_decline \
  test_role_triggers.SymptomRoundsTest.test_recorded_outcome_answers_leave_both_findings_calls_owed \
  test_role_triggers.SymptomRoundsTest.test_cleared_symptom_cannot_mask_another_second_event_and_owed_questions_are_not_duplicated

# 4. Reintroduce the old checker in a separate directory. Expect exit 1 and
# eight assertion failures: the old version wrongly clears all four answers
# for each of the two findings events. The candidate export stays untouched.
mkdir "$CHECK_DIR/old-checker"
cp test_role_triggers.py "$CHECK_DIR/old-checker/"
cp "$CHECK_DIR/base/kc-dev-flow-2/scripts/role_triggers.py" "$CHECK_DIR/old-checker/"
cd "$CHECK_DIR/old-checker"
OLD_EXIT=0
python3 -B -m unittest test_role_triggers.SymptomRoundsTest.test_recorded_outcome_answers_leave_both_findings_calls_owed > "$CHECK_DIR/old-checker.log" 2>&1 || OLD_EXIT=$?
test "$OLD_EXIT" -eq 1
python3 - "$CHECK_DIR/old-checker.log" <<'PY'
from pathlib import Path
import sys
text = Path(sys.argv[1]).read_text()
assert text.count('FAIL: ') == 8 and 'ERROR:' not in text, text
print('Old checker rejected: 8 assertion failures, no test errors')
PY

# 5. Check the decision record and unchanged workflow. Expect 64 ADR files
# checked, zero legacy, and PASS. Git metadata is read only for this command.
cd "$CHECK_DIR/candidate"
GIT_DIR=$(git -C "$REPO" rev-parse --absolute-git-dir) GIT_WORK_TREE="$CHECK_DIR/candidate" \
  python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE_SHA" --require 0026
cmp "$CHECK_DIR/base/kc-dev-flow-2/references/sd/workflow.md" "$CHECK_DIR/candidate/kc-dev-flow-2/references/sd/workflow.md"
printf 'PASS: five acceptance steps; evidence remains at %s\n' "$CHECK_DIR"
# Covers CLI behavior, six focused cases, the old-version falsifier and ADR
# structure. Does not re-grade model answers, run all suites, perform a live
# model consultation, prove deployment/adoption, or authorize merge.
