#!/usr/bin/env bash
# Run the exact candidate's four bounded acceptance checks.
set -euo pipefail
E=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SOURCE="/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-pr-watch-tasks-foreign-worktree"
W="/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2"
SD=/Users/kent/.local/bin/spacedock
HEAD=e1fbb6ee5abbd7cefd67f57493ab1481a04ed073
export PYTHONDONTWRITEBYTECODE=1
export PR_WATCH_SOURCE_REPO="$SOURCE"
export TMPDIR=/tmp
# 1. Export the pinned candidate. Expected: the declared object exists.
git -C "$SOURCE" cat-file -e "$HEAD^{commit}"
P=$(mktemp -d /tmp/pr-watch-accept-858-XXXXXX)
printf '%s\n' "$P" > "$E/accept-scratch.txt"
git -C "$SOURCE" archive "$HEAD" | tar -x -C "$P"
# 2. Absent worktree and no-field cases. Expected: one passing test.
python3 -B "$E/probe_checks.py" AC-1 --repo "$P" > "$E/accept-AC-1.log" 2>&1
echo "AC-1 PASS: absent worktree is factual; no action or watch entry"
# 3. Preserved PR paths. Expected: three passing tests.
python3 -B "$E/probe_checks.py" AC-2 --repo "$P" > "$E/accept-AC-2.log" 2>&1
echo "AC-2 PASS: local discovery, closed-only and recorded PR"
# 4. Original public records with native status. Expected: two facts, zero provider calls or watch writes.
python3 -B "$E/probe_checks.py" AC-3 --repo "$P" --workflow "$W" --sd-bin "$SD" > "$E/accept-AC-3.log" 2>&1
echo "AC-3 PASS: two original public records; no unknown-PR instructions"
# 5. Paired lifecycle wording. Expected: all five bounded totals shrink by six words.
python3 -B "$E/probe_checks.py" AC-4 --repo "$P" > "$E/accept-AC-4.log" 2>&1
echo "AC-4 PASS: no common-text change or bounded output growth"
# 6. Remove this run's export. Expected: that exact path no longer exists.
rm -rf -- "$P"
test ! -e "$P"
echo "PASS: all four criteria; temporary export removed"
