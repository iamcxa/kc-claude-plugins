#!/usr/bin/env bash
set -euo pipefail
# Step 1: export exactly the reviewed head; no product files are edited.
repo=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-counts-name-the-run-that-produced-them
candidate=90f43f801be3d03ebd7d98d1a41ad78801aea54d
scratch=$(mktemp -d /tmp/pr822-captain.XXXXXX)
git -C "$repo" archive "$candidate" | tar -x -C "$scratch"
export PYTHONDONTWRITEBYTECODE=1
cd "$scratch/kc-dev-flow-2/scripts"
printf 'Exported %s\n' "$candidate"
# Step 2: unsupported learn counts refuse while the same token remains correctable.
python3 -B -m unittest test_learning.LearningTests.test_evidence_count_refusal_leaves_pending_token_correctable test_learning.LearningTests.test_completed_legacy_counts_remain_readable
# Step 3: both gate entrances write their counts, preserve existing holds and bound diagnostics.
python3 -B -m unittest test_delivery_gate.CountDisclosureTests test_poc_readme.DeriveTests.test_delivery_recipe_holds_nonzero_and_forwards_checked_summary_in_both_routes
# Step 4: expose the current ordinal-reference false refusal; this is a limit, not approval.
python3 -B - <<'PY'
import test_learning as t
f=t.LearningTests();f.setUp()
try:
    f.pack['evidence']=['Source: first-cycle officer feedback'];f.write_pack();claim=f.claim()
    entry=dict(t.NEW,Evidence='See the Cycle 1 FO line.')
    decision=dict(f.decision('add',entry),evidence=f.pack['evidence'])
    refused=f.complete(claim,f.result_file([decision]),code=1)
    assert f.cli('read','--job',claim['job'])['state']=='pending'
    print('KNOWN LIMIT: Cycle 1 FO line refused; claim remains pending')
    entry['Evidence']='See the first-cycle FO line.'
    assert f.complete(claim,f.result_file([decision]))['state']=='completed'
    print('SAME EVIDENCE: wording change completes')
finally:
    f.doCleanups()
PY
