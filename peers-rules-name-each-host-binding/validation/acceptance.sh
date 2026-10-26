#!/bin/bash
# Prerequisites: git, python3, bash, the named candidate checkout and installed packages.
# No UI changed. This checks local lint, dependency logic, ADRs and reading counts;
# it does not prove live delivery, adoption enforcement or Captain authority.
# Step 1: create an exact detached candidate; expected HEAD bff1d8147b626ae91c6ca431f7dde459a63f254d.
set -euo pipefail
SOURCE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-peers-rules-name-each-host-binding
SCRATCH=$(mktemp -d /tmp/peers-730-acceptance.XXXXXX)
CHECKOUT="$SCRATCH/tree"
trap 'git -C "$SOURCE" worktree remove "$CHECKOUT"; rmdir "$SCRATCH"' EXIT
git -C "$SOURCE" worktree add --detach "$CHECKOUT" bff1d8147b626ae91c6ca431f7dde459a63f254d
cd "$CHECKOUT"
git rev-parse HEAD

# Step 2: package checks; expected PASS, 5421/5421 words, 46 tests OK.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
python3 -B kc-dev-flow-2/scripts/test_lint_skills.py

# Step 3: reserved decision record; expected 37 ADR file(s) checked, 0 legacy; exit 0.
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.31.0/scripts/adr_lint.py docs/adr --since c70f1b22cb1e4a66fd15c617647c778d54c59ec9 --require 0038

# Step 4: dependency helper, not adopter integration; expected two accepted lists and one refusal.
python3 -B - <<'PYTHON'
from pathlib import Path
import importlib.util
root=Path('kc-dev-flow-2')
spec=importlib.util.spec_from_file_location('lint',root/'scripts/lint-skills.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for selected in (['peers'],['peers','paseo'],['paseo']):
    result=m.extension_dependency_errors(root,selected)
    assert bool(result)==(selected==['paseo'])
    print(str(selected)+': '+('; '.join(result) if result else 'accepted'))
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
