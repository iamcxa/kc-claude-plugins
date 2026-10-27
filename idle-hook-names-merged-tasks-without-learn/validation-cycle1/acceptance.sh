#!/usr/bin/env bash
set -euo pipefail

# Step 1: open the repaired candidate in a disposable checkout.
# Expected: aa0f280f8e94f8b5549b4a8cd26fe30560a9842c.
SOURCE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-idle-hook-names-merged-tasks-without-learn
CHECKOUT=$(mktemp -d /tmp/idle-737-recheck.XXXXXX)
export PYTHONDONTWRITEBYTECODE=1
git -C "$SOURCE" worktree add --detach "$CHECKOUT" aa0f280f8e94f8b5549b4a8cd26fe30560a9842c
trap 'git -C "$SOURCE" worktree remove "$CHECKOUT"' EXIT
git -C "$CHECKOUT" rev-parse HEAD

# Step 2: test archive recovery, all-notices identity, eligibility parity and holds.
# Expected: Ran 6 tests; OK. The parity test covers 35 variant/profile pairs.
(cd "$CHECKOUT" && python3 -B kc-dev-flow-2/scripts/test_pr_watch.py \
 TasksTests.test_archive_shapes_are_sorted_deduplicated_and_guarded \
 TasksTests.test_real_claim_completed_acknowledged_and_released_jobs_suppress_repeats \
 TasksTests.test_frozen_archive_replay_recovers_all_eleven_and_suppresses_backfilled_jobs \
 TasksTests.test_archive_variant_profile_filter_matches_learning_eligibility \
 TasksTests.test_frontmatter_ineligible_learn_hold_is_skipped_without_a_record \
 TasksTests.test_other_ineligibility_reasons_may_still_repeat)

# Step 3: exercise the real recorder and watcher CLI.
# Expected: empty idle output before/after legacy-profile hold; no notices or store.
# Adding an eligible task then prints only its exact five-word reminder.
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
    task = fixture.archive("old-profile", profile="legacy")
    before = task.read_bytes()
    def idle(expected, label):
        result = subprocess.run([sys.executable, "-B", str(checks.watch.SCRIPTS/"pr_watch.py"),
            "--state", str(fixture.watch), "tasks", str(fixture.workflow)],
            capture_output=True, text=True, env={**os.environ, **fixture.sd_env()})
        assert result.returncode == 0, result.stderr + result.stdout
        assert result.stdout == expected, result.stdout
        print(label + ": " + (result.stdout.strip() or "<empty>"))
    idle("", "idle before hold")
    claim = fixture.claim_archive("old-profile", profile="legacy")
    assert claim == {"state": "ineligible", "reasons": ["profile"]}, claim
    print(json.dumps(claim))
    notices = fixture.learn("notices", "--all")
    assert notices == {"notices": []}, notices
    print(json.dumps(notices))
    idle("", "idle after hold")
    fixture.archive("eligible")
    idle("next: run kc-dev-flow-2:learn for eligible.\n", "eligible task")
    assert task.read_bytes() == before
    assert not fixture.watch.exists()
    assert not (fixture.repo/".git/kc-dev-flow-2").exists()
    print("PASS: rejected profile skipped; eligible task named; no record or task mutation")
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
