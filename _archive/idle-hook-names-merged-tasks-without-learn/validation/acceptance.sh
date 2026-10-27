#!/usr/bin/env bash
set -euo pipefail

# Step 1: open the exact candidate in a disposable checkout.
# Expected: HEAD is 207c0a7eb51d08c00e68dbe52e9b364793750484.
SOURCE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-idle-hook-names-merged-tasks-without-learn
CHECKOUT=$(mktemp -d /tmp/idle-737-acceptance.XXXXXX)
export PYTHONDONTWRITEBYTECODE=1
git -C "$SOURCE" worktree add --detach "$CHECKOUT" 207c0a7eb51d08c00e68dbe52e9b364793750484
trap 'git -C "$SOURCE" worktree remove "$CHECKOUT"' EXIT
git -C "$CHECKOUT" rev-parse HEAD

# Step 2: exercise discovery, all-notices subtraction, replay and provider failures.
# Expected: Ran 5 tests; OK.
(cd "$CHECKOUT" && python3 -B kc-dev-flow-2/scripts/test_pr_watch.py \
 TasksTests.test_archive_shapes_are_sorted_deduplicated_and_guarded \
 TasksTests.test_real_claim_completed_acknowledged_and_released_jobs_suppress_repeats \
 TasksTests.test_frozen_archive_replay_recovers_all_eleven_and_suppresses_backfilled_jobs \
 TasksTests.test_archive_provider_reads_only_state_and_preserves_qualified_repository \
 TasksTests.test_keyed_uncertain_notices_without_input_are_inspected_and_malformed_lists_hold)

# Step 3: use the real recorder and watcher CLI to expose the amendment conflict.
# Expected: both idle passes name old-profile; ineligible/profile; empty notices.
# This reproduces the finding, not compliance with the Captain's no-repeat words.
python3 -B - "$CHECKOUT" <<'PY'
import importlib.util, json, os, subprocess, sys
from pathlib import Path
root = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("checks", root/"kc-dev-flow-2/scripts/test_pr_watch.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)
fixture = checks.TasksTests()
fixture.setUp()
try:
    fixture.readme("learn")
    task = fixture.archive("old-profile")
    before = task.read_bytes()
    def idle():
        result = subprocess.run([sys.executable, "-B", str(checks.watch.SCRIPTS/"pr_watch.py"),
            "--state", str(fixture.watch), "tasks", str(fixture.workflow)],
            capture_output=True, text=True, env={**os.environ, **fixture.sd_env()})
        assert result.returncode == 0, result.stderr + result.stdout
        assert result.stdout == "next: run kc-dev-flow-2:learn for old-profile.\n", result.stdout
        print(result.stdout, end="")
    idle()
    claim = fixture.claim_archive("old-profile", profile="legacy")
    assert claim == {"state": "ineligible", "reasons": ["profile"]}, claim
    print(json.dumps(claim))
    notices = fixture.learn("notices", "--all")
    assert notices == {"notices": []}, notices
    print(json.dumps(notices))
    idle()
    assert task.read_bytes() == before
    assert not fixture.watch.exists()
    print("AMENDMENT CONFLICT: ineligible task is named again; closed task unchanged.")
finally:
    fixture.doCleanups()
PY

# Step 4: check architecture decision records.
# Expected: 39 ADR file(s) checked, 0 legacy; adr_lint exit=0.
(cd "$CHECKOUT" && python3 /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/adr_lint.py docs/adr --since 8bf4f3582411e8e4238f19fbadda8ddeca6767be)
echo "adr_lint exit=0"

# Step 5: remove only this disposable checkout.
# Expected: cleanup complete.
git -C "$SOURCE" worktree remove "$CHECKOUT"
trap - EXIT
echo "cleanup complete"

