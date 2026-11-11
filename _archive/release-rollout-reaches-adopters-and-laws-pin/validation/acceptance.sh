#!/usr/bin/env bash
set -euo pipefail

# 1. Export the exact reviewed commit; no worktree is created or changed.
rollout_repo=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-rollout-reaches-adopters-and-laws-pin
rollout_head=61529999eb4184b44328fe2fbad545b1b0b0ed92
rollout_dir=$(mktemp -d /tmp/rollout-838-acceptance.XXXXXX)
git -C "$rollout_repo" archive "$rollout_head" > "$rollout_dir/source.tar"
tar -xf "$rollout_dir/source.tar" -C "$rollout_dir"
cd "$rollout_dir"
printf 'Candidate %s exported\n' "$rollout_head"

# 2. Exercise every rollout and existing single-README regression case.
python3 -B kc-dev-flow-2/scripts/test_package_version.py

# 3. See both owed actions in order and a separate unreadable row, using fake GitHub.
python3 -B - <<'PY'
import importlib.util
from pathlib import Path
p = Path('kc-dev-flow-2/scripts/test_package_version.py')
s = importlib.util.spec_from_file_location('rollout_tests', p)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
c = m.RolloutTest()
c.setUp()
try:
    c.row('both', pin=c.old)
    repo = c.row('missing')
    c.content(repo, 'docs/dev2/README.md', 'main', error='Not Found (HTTP 404)')
    c.content(c.repo, c.workflow, c.latest, c.readme('0.38.1') + 'Changed rule.\n')
    c.content(c.repo, c.laws[0], c.latest, 'changed laws\n')
    r = c.run_rollout()
    expected = ('fleet/both docs/dev2 README:0.38.0 released:0.38.1 sync owed; laws: '
                + c.old + ' pin owed; sync README, merge, then move pin\n'
                + 'fleet/missing docs/dev2 unreadable: "Not Found (HTTP 404)"\n')
    assert r.returncode == 1 and r.stdout == expected and not r.stderr
    print(r.stdout, end='')
    print('Expected rollout exit: 1')
finally:
    c.doCleanups()
PY

# 4. Check the package instructions, release marker and word/repetition budget.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
printf 'Acceptance passed\n'
