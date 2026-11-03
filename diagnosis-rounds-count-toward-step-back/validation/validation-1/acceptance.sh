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
