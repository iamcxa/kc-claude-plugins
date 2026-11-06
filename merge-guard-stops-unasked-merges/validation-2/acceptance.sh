#!/bin/bash
set -euo pipefail
# Step 1: Export the exact reviewed revision. Expected: candidate export matches.
MG_REPO='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-guard-stops-unasked-merges'
MG_HEAD=b82f20de6c8e5b868695d03aa4bbcb97e77dd877
MG_BASE=b804d81d3abc94c9c321326dc75e7cac927c5252
test "$(git -C "$MG_REPO" rev-parse HEAD)" = "$MG_HEAD"
test -z "$(git -C "$MG_REPO" status --porcelain)"
MG_EXPORT=$(mktemp -d /tmp/merge-guard-acceptance.XXXXXX)
git -C "$MG_REPO" archive "$MG_HEAD" | tar -x -C "$MG_EXPORT"
cd "$MG_EXPORT"
printf 'Step 1: candidate export matches %s\n' "$MG_HEAD"
# Step 2: Run guard, discovery and record tests. Expected: 45 tests, OK.
python3 -B kc-dev-flow-2/scripts/test_merge_guard.py
# Step 3: Observe stop, record, pass, moved-head stop without running gh.
python3 -B - "$MG_EXPORT" <<'PY'
import contextlib, importlib.util, io, tempfile
from pathlib import Path
import sys
root=Path(sys.argv[1]); script=root/'kc-dev-flow-2/scripts/merge_guard.py'
spec=importlib.util.spec_from_file_location('guard',script)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
with tempfile.TemporaryDirectory(prefix='merge-record-demo-',dir='/tmp') as d:
 state=Path(d); head='1'*40
 command='gh pr merge 1 --repo example/does-not-exist --match-head-commit '+head
 assert g.verdict(command,root,[state])[0]=='stop'
 print('uncarried: stop')
 question=state/'question.txt';question.write_text('Merge #1 at 1111111?')
 with contextlib.redirect_stdout(io.StringIO()):
  assert g.record([str(state),'--pr','example/does-not-exist#1','--head',head,'--question-file',str(question),'--answer','fixture only'])==0
 print('record: saved in temporary state')
 assert g.verdict(command,root,[state])[0]=='pass'
 print('carried: pass')
 assert g.verdict(command.replace(head,'2'*40),root,[state])[0]=='stop'
 print('moved-head: stop')
 for label, cmd in [('auto',command+' --auto'), ('REST async','gh api -X PUT repos/example/does-not-exist/pulls/1/merge-async'), ('GraphQL','gh api graphql --input request.json')]:
  assert g.verdict(cmd,root,[state])[0]=='stop'
  print(label+': stop despite matching record')
PY
# Step 4: Check existing delivery behavior and package routing. Expected: 157 tests, one skip; lint PASS.
python3 -B kc-dev-flow-2/scripts/test_delivery_gate.py
python3 -B kc-dev-flow-2/scripts/lint-skills.py
# Step 5: Check decision records against the pinned base. Expected: 62 ADRs, 0 legacy.
cd "$MG_REPO"
python3 /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since "$MG_BASE" --require 0063
printf 'Acceptance passed; no hook installed and no merge executed.\n'

