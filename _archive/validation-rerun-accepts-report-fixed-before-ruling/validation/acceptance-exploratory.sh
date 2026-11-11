#!/usr/bin/env bash
set -euo pipefail
# Prerequisites: bash, git, python3; the named local repository, qnow history,
# state evidence and installed kc-dev-flow-2 0.38.0 package must exist.
# No GUI changes. This checks replay, focused guards, ADR and the withdrawal case.
# It does not prove corpus coverage, hosted CI, review, merge or installed adoption.
REPO='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-rerun-accepts-report-fixed-before-ruling'
TASK='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/validation-rerun-accepts-report-fixed-before-ruling'
PKG='/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.0'
HEAD_SHA='7d75d65ef317fc5c426eb7b0975d93a72d50acaa'
BASE_SHA='8c714a370867eccb0d26a589c5149ad3e0c911b4'
RUN=$(mktemp -d /tmp/pr834-acceptance.XXXXXX)
printf 'Evidence: %s\n' "$RUN"

# Step 1: Export the exact candidate. Expected: exact candidate SHA printed.
mkdir "$RUN/candidate"
git -C "$REPO" archive "$HEAD_SHA" --output="$RUN/candidate.tar"
tar -xf "$RUN/candidate.tar" -C "$RUN/candidate"
printf 'Step 1 candidate=%s\n' "$(git -C "$REPO" rev-parse "$HEAD_SHA")"

# Step 2: Replay actual qnow history and both negative cases.
# Expected exit pairs: 2/0, 2/2, 2/2; the flip reason is checked without filtering.
bash "$TASK/ideation/replay.sh" "$REPO" /Users/kent/conductor/repos/qnow "$RUN/replay-original" "$RUN/candidate/kc-dev-flow-2/scripts/dispatch_records.py" > "$RUN/replay.log"
cat "$RUN/replay.log"
python3 -B - "$RUN" <<'PY'
import pathlib, subprocess, sys
r=pathlib.Path(sys.argv[1]); log=(r/'replay.log').read_text()
expected=['qnow-recorded-history tag exit=2','qnow-recorded-history candidate exit=0','rewrite-after-ruling tag exit=2','rewrite-after-ruling candidate exit=2','pre-ruling-verdict-flip tag exit=2','pre-ruling-verdict-flip candidate exit=2']
assert all(x in log for x in expected), log
q=r/'replay-original/qnow'; record=q/'owner-cancels-booking/dispatch/validation-2.md'
record.write_bytes(subprocess.check_output(['git','-C',str(q),'show','a1fe6eeec:owner-cancels-booking/dispatch/validation-1.md']))
p=subprocess.run([sys.executable,'-B',str(r/'candidate/kc-dev-flow-2/scripts/dispatch_records.py'),'--names',str(record)],capture_output=True,text=True)
assert p.returncode==2 and 'rewritten-report-verdict-changed' in p.stdout, p.stdout
print('Step 2 PASS: recorded history allowed; late rewrite and verdict flip refused')
PY

# Step 3: Run the nine focused regression tests and the required ADR lint.
# Expected: nine tests OK; adr lint exit 0.
(
  cd "$RUN/candidate"
  python3 -B kc-dev-flow-2/scripts/test_dispatch_records.py \
    LiveValidationRulingTests.test_correction_before_later_ruling_clears \
    LiveValidationRulingTests.test_corrected_report_without_ruling_names_final_text_commit \
    LiveValidationRulingTests.test_rewrite_after_native_ruling_or_nonclearing_gate_is_refused \
    LiveValidationRulingTests.test_correction_committed_beside_amendment_is_refused \
    LiveValidationRulingTests.test_pre_ruling_verdict_flip_added_word_or_reordering_is_refused \
    LiveValidationRulingTests.test_rewritten_report_without_verdict_word_is_refused \
    LiveValidationRulingTests.test_old_text_returning_after_final_text_cannot_reset_clock \
    LiveValidationRulingTests.test_ruling_between_two_corrections_still_refuses \
    LiveValidationRulingTests.test_old_gate_and_prepared_briefing_allow_pre_ruling_correction
  GIT_DIR="$(git -C "$REPO" rev-parse --absolute-git-dir)" GIT_WORK_TREE="$RUN/candidate" \
    python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since "$BASE_SHA" --require 0045
)
printf 'Step 3 PASS: focused tests and ADR lint\n'

# Step 4: Exercise withdrawal added to an already-known gate attempt.
# Required by AC-2: candidate must exit 2 with rewritten-report-after-ruling.
# At the reviewed candidate it incorrectly exits 0, so this script exits 1.
mkdir "$RUN/probe"
python3 -B "$TASK/validation/withdrawal-probe.py" "$RUN/candidate" "$RUN/probe" > "$RUN/withdrawal.log"
cat "$RUN/withdrawal.log"
python3 -B - "$RUN/withdrawal.log" <<'PY'
import pathlib,sys
text=pathlib.Path(sys.argv[1]).read_text()
assert 'candidate exit=2' in text and 'rewritten-report-after-ruling' in text, 'FAIL AC-2: a report rewritten after withdrawal of an existing gate is accepted'
print('Step 4 PASS: withdrawal boundary preserved')
PY

