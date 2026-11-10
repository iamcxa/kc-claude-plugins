#!/usr/bin/env bash
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE
PROOF_DIR="$(cd "$(dirname "$0")" && pwd)"
PRODUCT_REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-amendment-checked-when-written
STATE_REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state
PACKAGE=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0
CHECK_DIR="$(mktemp -d /tmp/pr828-acceptance.XXXXXX)"
export PYTHONDONTWRITEBYTECODE=1

# Step 1: export the fixed candidate and baseline; expect the two pinned revisions to resolve.
git -C "$PRODUCT_REPO" cat-file -e 72216e2e947e962737a17c6e61ef3800f9d639c4^{commit}
mkdir "$CHECK_DIR/candidate" "$CHECK_DIR/base"
git -C "$PRODUCT_REPO" archive 72216e2e947e962737a17c6e61ef3800f9d639c4 | tar -x -C "$CHECK_DIR/candidate"
git -C "$PRODUCT_REPO" archive 6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1 | tar -x -C "$CHECK_DIR/base"
printf 'STEP 1 PASS: exported candidate 72216e2e947e and base 6a495cb8c405\n'

# Step 2: replay the original defect; expect one L4 event with both diagnostics, absent at base.
for VERSION in candidate base; do
    CODE=0
    python3 -B "$CHECK_DIR/$VERSION/kc-dev-flow-2/scripts/laws_check.py" "$STATE_REPO" --before b91e7434adde --after a113aa3e9 --readme "$(dirname "$STATE_REPO")/README.md" > "$CHECK_DIR/$VERSION-bite.log" 2>&1 || CODE=$?
    test "$CODE" -eq 1
done
python3 - "$CHECK_DIR" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); current=(p/'candidate-bite.log').read_text(); base=(p/'base-bite.log').read_text()
lines=[s for s in current.splitlines() if s.startswith(('L4 ', 'violation: L4 '))]
assert len(lines)==3 and '1 events judged' in lines[0] and '1 violated' in lines[0]
assert 'reused ids: AC-1, AC-2, AC-4' in lines[1] and 'unmarked replacement' in lines[2]
assert not any(s.startswith(('L4 ', 'violation: L4 ')) for s in base.splitlines())
print('\n'.join(lines)); print('STEP 2 PASS: candidate flags the bite; base has no L4')
PY

# Step 3: exercise valid moves, first-parent history and heading repairs; expect 12 tests, OK.
(cd "$CHECK_DIR/candidate/kc-dev-flow-2/scripts" && python3 -B -m unittest test_laws_check.L4Test test_laws_check.RegistryTest.test_laws_file_matches_registry)
printf 'STEP 3 PASS: L4 and registry tests\n'

# Step 4: check decision records with the declared package; expect 65 ADR files, exit 0.
(cd "$CHECK_DIR/candidate" && GIT_DIR="$(git -C "$PRODUCT_REPO" rev-parse --absolute-git-dir)" GIT_WORK_TREE="$CHECK_DIR/candidate" python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since 6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1)
printf 'STEP 4 PASS: ADR lint\n'

# Step 5: repair one of two already reported ids; AC-3 requires exit 0 and no new L4 event.
python3 -B "$PROOF_DIR/partial-repair-acceptance.py" "$CHECK_DIR/candidate"
printf 'STEP 5 PASS: partial repair does not repeat old debt\n'
