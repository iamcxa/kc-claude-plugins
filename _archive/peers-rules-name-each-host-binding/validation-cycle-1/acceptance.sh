#!/bin/bash
# Prerequisites: git, python3, bash, the named candidate checkout and installed packages.
# No UI changed. This checks local lint, repair identity, ADRs and reading counts;
# it does not prove live delivery, adoption enforcement or Captain authority.
# Step 1: create an exact detached candidate; expected HEAD dc3916fbb4ce9655dc37c5e4185653694e029de4.
set -euo pipefail
SOURCE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-peers-rules-name-each-host-binding
SCRATCH=$(mktemp -d /tmp/peers-730-cycle1-acceptance.XXXXXX)
CHECKOUT="$SCRATCH/tree"
trap 'git -C "$SOURCE" worktree remove "$CHECKOUT"; rmdir "$SCRATCH"' EXIT
git -C "$SOURCE" worktree add --detach "$CHECKOUT" dc3916fbb4ce9655dc37c5e4185653694e029de4
cd "$CHECKOUT"
git rev-parse HEAD

# Step 2: package checks; expected PASS, 5421/5421 words, 44 tests OK.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
python3 -B kc-dev-flow-2/scripts/test_lint_skills.py

# Step 3: reserved decision record; expected 37 ADR file(s) checked, 0 legacy; exit 0.
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.31.0/scripts/adr_lint.py docs/adr --since c70f1b22cb1e4a66fd15c617647c778d54c59ec9 --require 0038

# Step 4: repair identity; expected helper absent, original tier rule unchanged, policy unchanged.
python3 -B - <<'PYTHON'
from pathlib import Path
import ast, subprocess
current=Path('kc-dev-flow-2/scripts/lint-skills.py').read_text()
assert 'extension_dependency_errors' not in current
base=subprocess.check_output(['git','show','c70f1b22cb1e4a66fd15c617647c778d54c59ec9:kc-dev-flow-2/scripts/lint-skills.py'],text=True)
def tier(text):
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='extension_tier_errors')
    source=ast.get_source_segment(text,node)
    return source.split('    for name in tiers:')[0] if '    for name in tiers:' in source else source.rsplit('    return errors',1)[0]
assert tier(current)==tier(base)
changed=subprocess.check_output(['git','diff','--name-only','bff1d8147b626ae91c6ca431f7dde459a63f254d','HEAD'],text=True).splitlines()
assert set(changed)=={'kc-dev-flow-2/scripts/lint-skills.py','kc-dev-flow-2/scripts/test_lint_skills.py'}
tests=Path('kc-dev-flow-2/scripts/test_lint_skills.py').read_text()
assert 'test_peers_alone_and_optional_paseo_selection' not in tests
assert 'test_paseo_without_peers_is_refused_in_the_workflow' not in tests
print('helper/call/two tests absent; original tier-check bytes unchanged; policy unchanged')
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
