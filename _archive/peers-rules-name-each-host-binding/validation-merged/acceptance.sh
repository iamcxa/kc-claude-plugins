#!/bin/bash
# Prerequisites: git, python3, bash, the named candidate checkout and installed packages.
# No UI changed. This checks local lint, repair identity, ADRs and reading counts;
# it does not prove live delivery, adoption enforcement or Captain authority.
# Step 1: create an exact detached candidate; expected HEAD f7516476989b59fb45e4e5cb520d41ed9bc563ce.
set -euo pipefail
SOURCE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-peers-rules-name-each-host-binding
SCRATCH=$(mktemp -d /tmp/peers-730-merge-acceptance.XXXXXX)
CHECKOUT="$SCRATCH/tree"
trap 'git -C "$SOURCE" worktree remove "$CHECKOUT"; rmdir "$SCRATCH"' EXIT
git -C "$SOURCE" worktree add --detach "$CHECKOUT" f7516476989b59fb45e4e5cb520d41ed9bc563ce
cd "$CHECKOUT"
git rev-parse HEAD

# Step 2: package checks; expected PASS, 5565/5565 words, 44 tests OK.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
python3 -B kc-dev-flow-2/scripts/test_lint_skills.py

# Step 3: reserved decision record; expected 38 ADR file(s) checked, 0 legacy; exit 0.
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.31.0/scripts/adr_lint.py docs/adr --since b8ce84e584cf5c5cb482009d9d08d7316ce2a6ac --require 0038

# Step 4: merge preservation; expected two parents, +144 budget and document guard preserved.
python3 -B - <<'PYTHON'
from pathlib import Path
import subprocess
def git(*args):
    return subprocess.check_output(['git',*args],text=True)
base='b8ce84e584cf5c5cb482009d9d08d7316ce2a6ac'
prior='dc3916fbb4ce9655dc37c5e4185653694e029de4'
assert git('show','-s','--format=%P','HEAD').strip()==prior+' '+base
source=Path('kc-dev-flow-2/scripts/lint-skills.py').read_text()
main=git('show',base+':kc-dev-flow-2/scripts/lint-skills.py')
presence='    for name in tiers:\n        if not (root / "extensions" / name / "EXTENSION.md").is_file():\n            errors.append(f"README.md: extension `{name}` has no EXTENSION.md")\n'
assert presence in source and source.replace(presence,'')==main
assert 'delta=144' in source and 'extension_dependency_errors' not in source
for name in git('diff','--name-only',base,'HEAD').splitlines():
    if name!='kc-dev-flow-2/scripts/lint-skills.py':
        assert git('show','HEAD:'+name)==git('show',prior+':'+name)
print('merge parents correct; +144 budget and document guard preserved; peer-policy bytes unchanged')
PYTHON

# Step 5: complete cold-load counts; expected 805 / 290 / 1380; proactive 2475, inbound 2185.
python3 -B - <<'PYTHON'
from pathlib import Path
peers=len(Path('kc-dev-flow-2/extensions/peers/EXTENSION.md').read_text().split())
paseo=len(Path('kc-dev-flow-2/extensions/paseo/EXTENSION.md').read_text().split())
upstream=len(Path('/Users/kent/.agents/skills/paseo/SKILL.md').read_text().split())
assert (peers,paseo,upstream)==(805,290,1380)
assert peers+paseo+upstream<=2481 and peers+upstream<=2191
print(f'peers {peers}; paseo {paseo}; upstream {upstream}; proactive {peers+paseo+upstream}; inbound {peers+upstream}')
PYTHON
git diff --exit-code
