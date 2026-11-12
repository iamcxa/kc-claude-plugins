#!/bin/bash
# Four-step acceptance check for the pinned candidate; no visible UI changed.
set -euo pipefail
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-new-work-checks-what-exists-first'
TASK='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/new-work-checks-what-exists-first'
PKG='/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1'
BASE=8125e6d516d32abbf79c6772de10cde2c20900a8
HEAD=1fc2f05f88b18a62d4eda598158ffa385df9fae8
SNAP="$(mktemp -d /tmp/accept-new-work-XXXXXX)"
trap 'rm -rf -- "$SNAP"' EXIT
# 1. Verify the candidate and export its tracked bytes. Expected: exact SHA and clean tree.
test "$(git -C "$WT" rev-parse HEAD)" = "$HEAD"
test -z "$(git -C "$WT" status --porcelain)"
git -C "$WT" archive "$HEAD" | tar -x -C "$SNAP"
printf 'STEP 1 PASS: pinned %s; clean code tree; archive created\n' "$HEAD"
# 2. Candidate routing passes; the old base fails. Expected: candidate 0, base 1.
python3 -B "$TASK/implementation/new_work_check.py" routing --repo "$WT" --ref "$HEAD" --base "$BASE" > "$SNAP/routing.json"
if python3 -B "$TASK/implementation/new_work_check.py" routing --repo "$WT" --ref "$BASE" --base "$BASE" > "$SNAP/base-routing.json"; then
  printf 'FAIL: old base unexpectedly satisfied the new rule\n'; exit 1
else
  test "$?" -eq 1
fi
python3 -B "$TASK/implementation/new_work_check.py" scope --repo "$WT" --ref "$HEAD" --base "$BASE" > "$SNAP/scope.json"
printf 'STEP 2 PASS: candidate routing 0; base routing 1; bounded package scope 0\n'
# 3. Run repository lint and parse the real accepted design. Expected: both exit 0.
(cd "$SNAP" && python3 -B kc-dev-flow-2/scripts/lint-skills.py)
python3 -B "$PKG/scripts/design_surfaces.py" check "$TASK.md"
printf 'STEP 3 PASS: repository lint and accepted-design parsing\n'
# 4. Validate the reserved decision record and current number reservations. Expected: both exit 0, no stale-fetch warning.
(cd "$WT" && python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since "$BASE" --require 0083)
(cd "$WT" && python3 -B "$PKG/scripts/number_guards.py" check --workflow-dir "$(dirname "$(dirname "$TASK")")" --task "$TASK.md") > "$SNAP/number-guards.log" 2>&1
cat "$SNAP/number-guards.log"
if rg -q 'warning: state fetch failed' "$SNAP/number-guards.log"; then
  printf 'FAIL: reservation freshness unverified\n'; exit 1
fi
test "$(git -C "$WT" rev-parse HEAD)" = "$HEAD"
test -z "$(git -C "$WT" status --porcelain)"
printf 'STEP 4 PASS: ADR 0083 and refreshed reservations; product unchanged\n'
printf 'ACCEPTANCE PASS. Limits: does not rerun model behavior, private census, full suite, hosted CI, release or adoption.\n'

