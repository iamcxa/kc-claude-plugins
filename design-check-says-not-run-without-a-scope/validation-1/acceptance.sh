#!/usr/bin/env bash
# Verify PR #807 from fresh exports; requires bash, git, tar, python3 and both local repositories below.
# Creates only a temporary export and a standalone Relay clone; no worktrees, source edits or publication.
set -euo pipefail
CODE_REPO=${CODE_REPO:-/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-design-check-says-not-run-without-a-scope}
RELAY_REPO=${RELAY_REPO:-/Users/kent/conductor/workspaces/subspace-relay/dhaka}
CANDIDATE=2760f259379e9c3bb43bab9efa56d90c5b657ab1
BASE=139feeaee7ce037a0c6535568cd6bd103155cbae
REPLAY=6008953a2501c4ff82bfb50b9d76f649259802a8
export PYTHONDONTWRITEBYTECODE=1
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE PYTHONPATH || true

# Step 1. Export the exact candidate and base, and clone the recorded Relay state.
# Expected: identity line naming the candidate; no source repository changes.
CHECK_DIR=$(mktemp -d /tmp/design-scope-acceptance.XXXXXX)
mkdir -p "$CHECK_DIR/candidate" "$CHECK_DIR/base"
git -C "$CODE_REPO" archive "$CANDIDATE" | tar -x -C "$CHECK_DIR/candidate"
git -C "$CODE_REPO" archive "$BASE" | tar -x -C "$CHECK_DIR/base"
git clone --quiet --no-hardlinks --no-checkout --single-branch --branch spacedock-state/dev2 "$RELAY_REPO" "$CHECK_DIR/relay"
git -C "$CHECK_DIR/relay" checkout --quiet --detach "$REPLAY"
printf 'STEP 1 PASS candidate %s; Relay %s; evidence %s\n' "$CANDIDATE" "$REPLAY" "$CHECK_DIR"

# Step 2. Run the original Relay task through the candidate CLI.
# Expected: presentable, then the exact not-run reason; exit 0 and no Scope changed.
python3 -B "$CHECK_DIR/candidate/kc-dev-flow-2/scripts/design_surfaces.py" check "$CHECK_DIR/relay/llms-teaches-versions.md" > "$CHECK_DIR/candidate.log"
python3 - "$CHECK_DIR/candidate.log" <<'PY_CHECK'
from pathlib import Path
import sys
text = Path(sys.argv[1]).read_text()
assert text.splitlines()[:2] == ['llms-teaches-versions.md: design surfaces presentable', 'scope check not run: backlog briefing binds llms-teaches-versions/review/backlog-gate.md, not this task file'], text
assert 'Scope changed' not in text, text
print(text, end='')
print('STEP 2 PASS original false hold is not run (exit 0)')
PY_CHECK

# Step 3. Run the same original task through the base CLI as the negative control.
# Expected: exit 1 and Scope changed after the backlog gate (01d0e0e4).
BASE_EXIT=0
python3 -B "$CHECK_DIR/base/kc-dev-flow-2/scripts/design_surfaces.py" check "$CHECK_DIR/relay/llms-teaches-versions.md" > "$CHECK_DIR/base.log" || BASE_EXIT=$?
test "$BASE_EXIT" -eq 1
python3 - "$CHECK_DIR/base.log" <<'PY_CHECK'
from pathlib import Path
import sys
text = Path(sys.argv[1]).read_text()
assert 'Scope changed after the backlog gate (01d0e0e4)' in text, text
print(text, end='')
print('STEP 3 PASS base reproduces the false hold (exit 1)')
PY_CHECK

# Step 4. Exercise real Scope additions/removals, folder/archive paths, foreign Scope and amendments.
# Expected: all ScopeCheckTests pass; the real added-line case asserts CLI exit 1.
(cd "$CHECK_DIR/candidate/kc-dev-flow-2/scripts" && python3 -B -m unittest -v test_design_surfaces.ScopeCheckTests)
printf 'STEP 4 PASS real Scope changes remain held; foreign bindings and amendments behave as accepted\n'
printf 'ACCEPTANCE PASS; does not cover full-suite regressions, hosted review, merge or plugin installation.\n'
