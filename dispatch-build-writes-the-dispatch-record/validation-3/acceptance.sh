#!/usr/bin/env bash
set -euo pipefail
# Requires this declared repository, Python 3, Git, tar, and Spacedock 0.27.2.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record'
HEAD_SHA=778367adde2e20e0b3e51966ddba2d9f77f9e614
BASE_SHA=334d91e3165953b2ca7191e3308d80b6c02c4a99
SD=/Users/kent/.local/bin/spacedock
EVIDENCE_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:?absolute directory for acceptance evidence}"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
# 1. Export the fixed candidate; expected: exact SHA, clean tree, binary 0.27.2.
test "$(git -C "$WT" rev-parse HEAD)" = "$HEAD_SHA"
test -z "$(git -C "$WT" status --porcelain)"
CHECK_ROOT="$(mktemp -d /tmp/pr812-captain.XXXXXX)"
git -C "$WT" archive "$HEAD_SHA" | tar -x -C "$CHECK_ROOT"
"$SD" --version > "$OUT/version.log"
grep -q '^spacedock 0\.27\.2$' "$OUT/version.log"
printf '%s\n' "$CHECK_ROOT" > "$OUT/export.txt"
cd "$CHECK_ROOT"
printf '%s\n' 'PASS 1: clean exact candidate exported; Spacedock 0.27.2'
# 2. Exercise creation, holds, retries, and advance; expected: seven selected tests OK.
SPACEDOCK_BIN="$SD" PYTHONDONTWRITEBYTECODE=1 python3 -B kc-dev-flow-2/scripts/test_dispatch_stage.py  DispatchStageTests.test_stamp_commits_complete_record_and_exact_inputs  DispatchStageTests.test_incomplete_record_does_not_build_or_change_state  DispatchStageTests.test_validation_candidate_is_required_before_build  DispatchStageTests.test_failed_stamp_removes_uncommitted_record_and_passes_error  DispatchStageTests.test_identical_retry_reuses_only_at_adding_commit  DispatchStageTests.test_changed_checklist_creates_next_committed_record  DispatchStageTests.test_advance_commits_record_and_withholds_envelope_on_commit_failure > "$OUT/seam.log" 2>&1
grep -q '^Ran 7 tests' "$OUT/seam.log"
grep -q '^OK$' "$OUT/seam.log"
printf '%s\n' 'PASS 2: 7 selected real-binary dispatch tests passed'
# 3. Verify the reduced README and observer coupling; expected: 5931/5931.
python3 -B kc-dev-flow-2/scripts/lint-skills.py > "$OUT/words.log" 2>&1
grep -q '5931 of 5931 words' "$OUT/words.log"
printf '%s\n' 'PASS 3: workflow and observer contracts passed at 5931/5931 words'
# 4. Refuse a missing real binary; expected: exit 1 naming SPACEDOCK_BIN.
set +e
env -u SPACEDOCK_BIN python3 -B kc-dev-flow-2/scripts/test_dispatch_stage.py > "$OUT/missing-binary.log" 2>&1
MISSING_RC=$?
set -e
test "$MISSING_RC" -eq 1
grep -q 'SPACEDOCK_BIN' "$OUT/missing-binary.log"
printf '%s\n' 'PASS 4: unset SPACEDOCK_BIN refused with exit 1'
# 5. Check ADR 0070 with the authorized candidate checker; preserve product tree.
META="$(git -C "$WT" rev-parse --absolute-git-dir)"
GIT_DIR="$META" GIT_WORK_TREE="$CHECK_ROOT" python3 -B kc-dev-flow-2/scripts/adr_lint.py docs/adr --since "$BASE_SHA" --require 0070 > "$OUT/adr.log" 2>&1
git -C "$WT" diff --check "$BASE_SHA" "$HEAD_SHA"
test "$(git -C "$WT" rev-parse HEAD)" = "$HEAD_SHA"
test -z "$(git -C "$WT" status --porcelain)"
printf '%s\n' 'PASS 5: candidate ADR checker passed; product tree unchanged'

# 6. Check both retry boundaries; expected: dirty same-task refuses, clean same-task follows amended AC-9.
SPACEDOCK_BIN="$SD" PYTHONDONTWRITEBYTECODE=1 python3 -B "$EVIDENCE_DIR/retry-index-probe.py" "$CHECK_ROOT" > "$OUT/retry-index.json"
python3 - "$OUT/retry-index.json" <<'CHECK'
import json, sys
r=json.load(open(sys.argv[1]))
if r['exit'] != 1 or not r['index_preserved'] or not r['worktree_preserved'] or not r['head_preserved']:
    sys.exit('FAIL 6: immediate retry discarded staged-only dispatch content')
print('PASS 6a: dirty same-task retry refused; staged content preserved')
CHECK

SPACEDOCK_BIN="$SD" PYTHONDONTWRITEBYTECODE=1 python3 -B "$EVIDENCE_DIR/outside-staged-retry.py" "$CHECK_ROOT" > "$OUT/outside-staged-retry.json"
python3 - "$OUT/outside-staged-retry.json" <<'CHECK'
import json, sys
rows=json.load(open(sys.argv[1]))
assert len(rows)==2 and all(r['first_exit']==0 and r['all_state_preserved'] and not r['record_two_exists'] for r in rows)
assert all(r['retry_exit']==1 and not r['retry_stdout'] and r['recovery_after_unstaging_other_task_exit']==0 for r in rows)
print('PASS 6: AC-9 outside-staged retry refuses without data changes in both layouts; clean retry recovers')
CHECK
