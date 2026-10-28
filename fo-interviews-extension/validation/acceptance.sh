#!/usr/bin/env bash
set -euo pipefail

# Step 1: create a detached disposable checkout of the exact candidate.
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-fo-interviews-extension
STATE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state
WORKFLOW=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
PKG=/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1
BASE=e57feb6eec956b74a1d4b29f26f1d0a7d1693785
HEAD_SHA=5f9276bd6955c66c192f74415c685b3a09f8ac16
scratch=$(mktemp -d /tmp/feedback-acceptance.XXXXXX)
CHECKOUT="$scratch/candidate"
git -C "$REPO" worktree add --quiet --detach "$CHECKOUT" "$HEAD_SHA"
trap 'git -C "$REPO" worktree remove "$CHECKOUT"' EXIT
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = "$HEAD_SHA"
test -z "$(git -C "$CHECKOUT" status --porcelain)"
printf 'Step 1: exact candidate, detached and clean\n'

# Step 2: run repository lint and its existing negative-control tests.
cd "$CHECKOUT"
python3 -B kc-dev-flow-2/scripts/lint-skills.py
python3 -B kc-dev-flow-2/scripts/test_lint_skills.py > "$scratch/lint-tests.txt" 2>&1
tail -n 4 "$scratch/lint-tests.txt"
printf 'Step 2: lint and 45 existing tests passed\n'

# Step 3: rerun both retained recipes; these prove fixtures, not native FO behavior.
python3 - "$STATE/fo-interviews-extension.md" "$scratch" <<'PY'
from pathlib import Path
import re, sys
s=Path(sys.argv[1]).read_text()
s=s[s.index('### Reproduce the executable checks'):s.index('## Stage Report: implementation')]
blocks=re.findall(r'```python\n(.*?)\n```',s,re.S)
assert len(blocks)==2
for name,body in zip(('proof.py','measure.py'),blocks):
    (Path(sys.argv[2])/name).write_text(body+'\n')
PY
python3 -B -X pycache_prefix="$scratch/cache-proof" "$scratch/proof.py" "$CHECKOUT" "$STATE"
python3 -B -X pycache_prefix="$scratch/cache-measure" "$scratch/measure.py" "$CHECKOUT" /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3 /Users/kent/.agents/skills/paseo/SKILL.md > "$scratch/measure-output.json"
python3 - "$scratch/measure-output.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]))
assert r['moments']['startup']['delta']==599
assert r['due_round']['fixed_instructions']==3356
assert len(r['controls'])==3
print('Step 3: 30 fixture mutations; 13 respondents; startup +599 words; first round 3356 words; 3 accounting controls')
PY

# Step 4: run boundary checks and reproduce the required-ADR blocker.
python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since "$BASE"
set +e
python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since "$BASE" --require 0005 0016 0020 0035 0038
adr_exit=$?
set -e
test "$adr_exit" -eq 1
printf 'Required ADR check exit: %s (expected blocker: ADR 0005 lacks Recommended)\n' "$adr_exit"
python3 -B "$PKG/scripts/number_guards.py" check --workflow-dir "$WORKFLOW" --task "$STATE/fo-interviews-extension.md"
python3 -B "$PKG/scripts/comment_ratio.py" "$BASE" HEAD --workflow-dir "$WORKFLOW"
python3 -B "$PKG/scripts/design_surfaces.py" check "$STATE/fo-interviews-extension.md"
python3 -B "$PKG/scripts/doc_impact.py" "$BASE" HEAD
python3 -B "$PKG/scripts/dispatch_records.py" "$STATE/fo-interviews-extension"
git -C "$CHECKOUT" diff --check "$BASE" HEAD
printf 'Step 4: boundary checks passed; required ADR blocker reproduced\n'

# Step 5: verify unchanged bytes and remove this disposable checkout.
test -z "$(git -C "$CHECKOUT" status --porcelain)"
cd "$scratch"
git -C "$REPO" worktree remove "$CHECKOUT"
trap - EXIT
printf 'Step 5: candidate unchanged; disposable checkout removed\n'
printf 'REJECTED: native acceptance evidence remains missing; the expected ADR failure is not an acceptance pass.\n'
