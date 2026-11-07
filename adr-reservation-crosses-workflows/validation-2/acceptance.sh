#!/usr/bin/env bash
# No user interface changes. Requires this assigned repository, Python 3, Git,
# and the dispatched kc-dev-flow-2 0.35.0 install. All mutations stay in /tmp.
# This checks local behavior; it does not prove publication, atomic allocation,
# visibility of unpublished state, or successful network fetch during later use.
set -euo pipefail
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-adr-reservation-crosses-workflows
PKG=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0
HEAD_SHA=ef3ed3e05534e2a997acbdfb055a880fde1f484a
BASE_SHA=ba055b8a7a55a787ac989c4cef52d07dd75661ad
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

# 1. Export the exact candidate, without creating a Git worktree.
EXPORT_DIR=$(mktemp -d /tmp/adr-801-accept-XXXXXX)
git -C "$REPO" archive "$HEAD_SHA" | tar -x -C "$EXPORT_DIR"
printf '1/5 candidate %s exported\n' "$HEAD_SHA"

# 2. Replay the collision against local temporary repositories.
# Expected: A1 ADR: 0061; A2 FAIL R8 and exit 1; A3 PASS; B1 ADR: 0061.
bash --noprofile --norc "$HERE/replay.sh" "$EXPORT_DIR/kc-dev-flow-2/scripts/number_guards.py" > "$EXPORT_DIR/replay.log" 2>&1
cat "$EXPORT_DIR/replay.log"
python3 - "$EXPORT_DIR/replay.log" <<'CHECK'
import sys
text=open(sys.argv[1]).read()
a1=text.split('A1 reserve:',1)[1].split('A2 check, held 0060:',1)[0]
a2=text.split('A2 check, held 0060:',1)[1].split('A3 check, free 0061:',1)[0]
a3=text.split('A3 check, free 0061:',1)[1].split('B1 reserve, folder-form sibling holds 0060:',1)[0]
b1=text.split('B1 reserve, folder-form sibling holds 0060:',1)[1]
assert 'ADR: 0061' in a1 and 'ADR: 0060' not in a1
assert 'FAIL R8:' in a2 and 'origin/spacedock-state/dev2:gate-presentation.md' in a2 and 'exit 1' in a2
assert 'PASS: no findings' in a3 and 'FAIL' not in a3
assert 'ADR: 0061' in b1 and 'ADR: 0060' not in b1
print('2/5 replay expectations PASS')
CHECK

# 3. Expected: Ran 38 tests, OK.
(cd "$EXPORT_DIR" && python3 -B kc-dev-flow-2/scripts/test_number_guards.py)
printf '3/5 number guard tests PASS\n'

# 4. Expected: workflow 5933/5933, all lint checks pass.
(cd "$EXPORT_DIR" && python3 -B kc-dev-flow-2/scripts/lint-skills.py)
printf '4/5 workflow lint PASS\n'

# 5. Read-only Git metadata lets the ADR linter compare an archive with its base.
# Expected: 61 ADR file(s) checked, 0 legacy; exit 0.
GIT_META=$(git -C "$REPO" rev-parse --absolute-git-dir)
(cd "$EXPORT_DIR" && GIT_DIR="$GIT_META" GIT_WORK_TREE="$EXPORT_DIR" GIT_OPTIONAL_LOCKS=0 python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since "$BASE_SHA" --require 0002)
printf '5/5 ADR lint PASS; acceptance PASS\n'
