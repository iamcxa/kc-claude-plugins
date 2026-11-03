#!/usr/bin/env bash
# Prerequisites: this repository, Python 3, Git, and the declared 0.34.0 package.
# No UI exists. This checks the command's observable count boundary and the
# recorded baseline discrepancy; it does not repeat live GitHub or the full suite.

# Step 1 — open the exact candidate in an isolated, detached checkout.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
TASK_WORKTREE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-gate-requires-the-question-check'
PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
CANDIDATE='6c34942164ecec9452c93f915e36241479f19dc5'
STACK_BASE='1c0dbb540f354300b75dba5a119d2614c8fb0c02'
TRUNK_AT_VALIDATION='146727ded0d4ce8014ea0b41a45dc3409d6b269b'
ACCEPTANCE_DIR=$(mktemp -d "$TASK_WORKTREE/.context/acceptance-767.XXXXXX")
CHECKOUT="$ACCEPTANCE_DIR/checkout"
trap 'cd "$TASK_WORKTREE"; if test -d "$CHECKOUT"; then git -C "$TASK_WORKTREE" worktree remove "$CHECKOUT"; fi; rmdir "$ACCEPTANCE_DIR"' EXIT
git -C "$TASK_WORKTREE" worktree add --detach "$CHECKOUT" "$CANDIDATE"
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = "$CANDIDATE"
printf 'Candidate: %s\n' "$CANDIDATE"

# Step 2 — observe the held and accepted forms using existing provider fixtures.
# Expected: missing=1/0 records; zero and detail=0/1 record; legacy question=0.
python3 -B - "$CHECKOUT" <<'PY'
import importlib.util, sys
from pathlib import Path
scripts = Path(sys.argv[1]) / 'kc-dev-flow-2/scripts'
sys.path.insert(0, str(scripts))
spec = importlib.util.spec_from_file_location('test_delivery_gate', scripts / 'test_delivery_gate.py')
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
missing = tests.run_check(rounds='')
assert missing.code == 1 and missing.written == {}
assert tests.CheckRoundCountTests.PROBLEM in missing.out
assert tests.CheckRoundCountTests.NEXT in missing.out
print('missing: exit=1, records=0')
print(missing.out, end='')
for value in ('0', '2. two reviews read'):
    result = tests.run_check(rounds=f'External rounds: {value}\n')
    assert result.code == 0 and len(result.written) == 1
    print(f'{value}: exit=0, records=1')
assert tests.QuestionTests().ask('Deliver it.') == (0, 'gate text complete\n')
print('legacy question without count: exit=0, gate text complete')
PY

# Step 3 — check the decision record and unchanged workflow budget.
# Expected: 50 ADR files, 0 legacy; lint PASS, workflow 5781 of 5781 words.
cd "$CHECKOUT"
python3 "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$STACK_BASE" --require 0051
python3 -B kc-dev-flow-2/scripts/lint-skills.py

# Step 4 — distinguish this task's empty diff from the literal AC-6 discrepancy.
# Expected: stacked diff empty; trunk diff names adoption.md and workflow.md.
git -C "$CHECKOUT" diff --exit-code "$STACK_BASE" "$CANDIDATE" -- kc-dev-flow-2/references/sd/ kc-dev-flow-2/scripts/lint-skills.py
printf 'Stacked reference and budget diff: empty\n'
if git -C "$CHECKOUT" diff --quiet "$TRUNK_AT_VALIDATION" "$CANDIDATE" -- kc-dev-flow-2/references/sd/; then
  printf 'Unexpected: literal trunk diff became empty\n'
  exit 1
else
  result=$?
  test "$result" = 1
fi
git -C "$CHECKOUT" diff --stat "$TRUNK_AT_VALIDATION" "$CANDIDATE" -- kc-dev-flow-2/references/sd/
printf 'AC-6 literal trunk comparison: UNMET; inherited changes require disposition\n'

# Step 5 — verify and remove only this script's temporary checkout.
# Expected: no changed files; cleanup complete. This is no delivery approval.
test -z "$(git -C "$CHECKOUT" status --porcelain)"
cd "$TASK_WORKTREE"
git -C "$TASK_WORKTREE" worktree remove "$CHECKOUT"
rmdir "$ACCEPTANCE_DIR"
trap - EXIT
printf 'Acceptance replay complete; temporary checkout removed\n'
