#!/usr/bin/env bash
# Step 1: Create an exact detached candidate; remove it on exit.
# Expected: candidate=159b21232dea8ce68fcf9402461e185ff59d327c.
set -eu
source_path='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-journey-probe-finds-nested-maps'
acceptance_tree=$(mktemp -d "$source_path/.acceptance-XXXXXX")
git -C "$source_path" worktree add --detach "$acceptance_tree" 159b21232dea8ce68fcf9402461e185ff59d327c
trap 'git -C "$source_path" worktree remove "$acceptance_tree"' EXIT
cd "$acceptance_tree"
test -z "$(git status --porcelain)"
printf 'candidate=%s\n' "$(git rev-parse HEAD)"

# Step 2: Run the documented probe in seven positive and negative fixtures.
# Expected: Ran 1 test, OK.
python3 -B kc-dev-flow-2/scripts/test_lint_skills.py RouteMutationTests.test_documented_journey_probe_finds_regular_yaml_at_each_depth

# Step 3: Check package rules and unchanged workflow reading budget.
# Expected: PASS; 5565 of 5565 words; host/workflow behavior not checked.
python3 -B kc-dev-flow-2/scripts/lint-skills.py

# Step 4: Confirm the exact approved replacement and two-file scope.
# Expected: adoption=2069->2085; Extensions=350->366; scope=2 files; policy preserved.
python3 -B - <<'PY'
from pathlib import Path
import subprocess
base = '8bf4f3582411e8e4238f19fbadda8ddeca6767be'
path = 'kc-dev-flow-2/references/sd/adoption.md'
before = subprocess.check_output(['git', 'show', f'{base}:{path}'], text=True)
after = Path(path).read_text()
old = '`release-acceptance` needs a `docs/journey/*.yaml` file, `python3` and `node`;'
new = "`release-acceptance` needs a `.yaml` file under `docs/journey/`, including product folders\n   (`find docs/journey -type f -name '*.yaml' -print` from the code root), `python3` and `node`;"
assert before.count(old) == 1 and after == before.replace(old, new)
def counts(text):
    return len(text.split()), len(text.split('## Extensions\n')[1].split('\n## Before activation')[0].split())
assert counts(before) == (2069, 350) and counts(after) == (2085, 366)
files = subprocess.check_output(['git', 'diff', '--name-only', base, 'HEAD'], text=True).splitlines()
assert files == [path, 'kc-dev-flow-2/scripts/test_lint_skills.py']
print('adoption=2069->2085; Extensions=350->366; scope=2 files; policy preserved')
PY

# Step 5: Check decision records at the pinned base and candidate.
# Expected: 39 ADR file(s) checked, 0 legacy; exit 0.
python3 -B '/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/adr_lint.py' docs/adr --since 8bf4f3582411e8e4238f19fbadda8ddeca6767be
test -z "$(git status --porcelain)"

