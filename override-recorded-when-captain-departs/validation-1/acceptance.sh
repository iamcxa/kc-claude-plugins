#!/usr/bin/env bash
set -euo pipefail
# Requires this declared checkout and python3; no UI or service login is involved.
# 1. Pin the checkout. Expected: the exact candidate SHA below.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-override-recorded-when-captain-departs'
cd "$WT"
test "$(git -C "$WT" rev-parse HEAD)" = 69d62c772c5f4fd28d9105c6f5d49516d559c947
git -C "$WT" diff --quiet HEAD
git -C "$WT" rev-parse HEAD
scratch=$(mktemp -d "$WT/.context/override-acceptance.XXXXXX")
trap 'rm -rf "$scratch"' EXIT
reason="$scratch/reason.txt"
check() {
  local expected="$1" actual=0
  python3 -B "$WT/kc-dev-flow-2/scripts/decision_ledger.py" --reason "$reason" || actual=$?
  printf 'exit=%s (expected %s)\n' "$actual" "$expected"
  test "$actual" = "$expected"
}
# 2. Omit the declaration. Expected: missing declaration, exit 1.
printf '%s\n' 'Captain approved the proposal.' > "$reason"
check 1
# 3. Declare agreement. Expected: reason: followed, exit 0.
printf '%s\n' 'Recommendation: followed' > "$reason"
check 0
# 4. Declare a departure. Expected: reason: override (area: design), exit 0.
printf '%s\n' 'Override: recommended approve; Captain chose revise; area: design' > "$reason"
check 0
# 5. Supply both forms. Expected: both declarations, exit 1.
printf '%s\n' 'Recommendation: followed' >> "$reason"
check 1
# 6. Empty input. Expected: empty file, exit 2.
: > "$reason"
check 2
