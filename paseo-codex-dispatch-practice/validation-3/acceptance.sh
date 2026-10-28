#!/bin/bash
set -eu
# No user-visible screen changed. Requires this Mac's candidate checkout,
# Codex package 0.32.1 and the committed validation-3 receipts.
# Expected final exit: 1, because the real immediate-spawn trace fails AC-2.
# This replays retained evidence; it does not create agents or prove merge/CI.

# 1. Expect exact head, clean checkout, and the three approved changed paths.
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-paseo-codex-dispatch-practice
E=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/paseo-codex-dispatch-practice/validation-3
cd "$WT"
test "$(git -C "$WT" rev-parse HEAD)" = 9a70a3350436fac9e51d0795b3b4299693f020f8
test -z "$(git -C "$WT" status --porcelain)"
git -C "$WT" diff --name-only e57feb6eec956b74a1d4b29f26f1d0a7d1693785 HEAD

# 2. Expect PASS; workflow 5576 of 5576 words.
python3 -B kc-dev-flow-2/scripts/lint-skills.py

# 3. Expect 41 ADR file(s) checked, 0 legacy; exit 0.
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1/scripts/adr_lint.py docs/adr --since e57feb6eec956b74a1d4b29f26f1d0a7d1693785 --require 0042

# 4. Expect PASS for exact prompt/assignment/runtime and six rejected mutants.
python3 -B - "$WT" "$E" <<'PY'
import hashlib,json,sys
from pathlib import Path
wt=sys.argv[1]; e=Path(sys.argv[2])
prompt=(e/'generated-prompt.txt').read_bytes()
assert prompt.endswith(b'\n') and not prompt.endswith(b'\n\n')
payload=prompt[:-1] # shell command substitution removes the output terminator
assert payload==(e/'native-prompt.txt').read_bytes()
assert payload==(e/'v3.out').read_bytes().splitlines()[-1]
assert hashlib.sha256(payload).hexdigest()=='23d03db76299dafc69584f1fe071950a0872cd3eda5d4acbaa2f9b7dcd375de3'
assert hashlib.sha256((e/'assignment.md').read_bytes()).hexdigest()=='5014b07f4b1ad9eb87e3a0b8a1912e14a728dbc541161baf7961ee229d02ef21'
s=json.loads((e/'self-status.json').read_text())['snapshot']
expected={'provider':'codex','model':'gpt-6-astra','thinkingOptionId':'high','currentModeId':'auto-review','cwd':wt,'workspaceId':'wks_c4f3d3de2a4e440b'}
assert all(s[k]==v for k,v in expected.items())
assert s['runtimeInfo']['modeId']=='auto-review'
trial=json.loads((e/'workspaceid-status.json').read_text())['snapshot']
assert trial['cwd']==wt and trial['workspaceId']=='wks_89650ac90ec290d6' and trial['currentModeId']=='auto-review'
assert json.loads((e/'workspaceid-activity.json').read_text())['content'].count(wt)==2
for k in ['model','thinkingOptionId','currentModeId','cwd','workspaceId']:
 bad=dict(s); bad[k]='wrong'
 assert not all(bad[key]==value for key,value in expected.items())
assert payload+b' wrapper'!=(e/'native-prompt.txt').read_bytes()
print('PASS: 206-byte prompt, assignment SHA256 and native runtime match; 6 mutants rejected.')
PY

# 5. Expect FAIL: AC-2 has 2 intervening calls; final exit 1.
# A zero-intermediate synthetic control passes the predicate, not the live route.
python3 -B - "$E" <<'PY'
import json,re,sys
from pathlib import Path
text=(Path(sys.argv[1])/'build-to-spawn-sequence.md').read_text()
calls=[json.loads(x) for x in re.findall(r'````json\n(.*?)\n````',text,re.S)]
assert len(calls)==4 and 'validate.py' in calls[0]['command']
assert 'paseo agent run' in calls[-1]['command']
assert '--new-workspace local' in calls[-1]['command'] and '--cwd' in calls[-1]['command']
assert len([calls[0],calls[-1]])-2==0
intervening=len(calls)-2
print(f'FAIL: AC-2 immediate spawn: {intervening} intervening calls (activity read; receipt write/state commit).')
sys.exit(1 if intervening else 0)
PY
