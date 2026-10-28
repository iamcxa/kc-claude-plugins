set -eu
# 1. Expect the exact candidate SHA and exactly three changed paths.
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-paseo-codex-dispatch-practice
cd "$WT"
test "$(git -C "$WT" rev-parse HEAD)" = 9a70a3350436fac9e51d0795b3b4299693f020f8
git -C "$WT" diff --name-only e57feb6eec956b74a1d4b29f26f1d0a7d1693785 HEAD
# 2. Expect PASS and workflow 5576 of 5576 words.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
# 3. Expect 41 ADR file(s) checked, 0 legacy; exit 0.
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1/scripts/adr_lint.py docs/adr --since e57feb6eec956b74a1d4b29f26f1d0a7d1693785 --require 0042
# 4. Expect Ran 5 tests; OK.
python3 -B kc-dev-flow-2/extensions/roborev/test_roborev_gate.py
# 5. Expect PASS: saved success cwd matches; inherited control differs.
python3 -B - "$WT" /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/paseo-codex-dispatch-practice/validation-1 <<'CHECK'
import json,sys
from pathlib import Path
p=Path(sys.argv[2]); success=json.loads((p/'placement-success.json').read_text()); control=json.loads((p/'placement-control.json').read_text())
assert success['cwd']==sys.argv[1]
assert control['cwd']=='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo' and control['cwd']!=success['cwd']
print('PASS: saved success cwd matches; inherited control differs.')
CHECK
