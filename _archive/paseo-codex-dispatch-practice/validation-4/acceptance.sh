#!/bin/bash
set -eu
# Requires this Mac's unchanged candidate checkout, Codex package 0.32.1,
# and the committed validation-4 receipts. No user-visible screen changed.
# Five steps; expected overall exit 0. Replays retained evidence without
# creating an agent or establishing hosted CI, merge, adoption or savings.

# 1. Expect the exact head, clean checkout and exactly three approved paths.
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-paseo-codex-dispatch-practice
E=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/paseo-codex-dispatch-practice/validation-4
cd "$WT"
test "$(git -C "$WT" rev-parse HEAD)" = 9a70a3350436fac9e51d0795b3b4299693f020f8
test -z "$(git -C "$WT" status --porcelain)"
git -C "$WT" diff --name-only e57feb6eec956b74a1d4b29f26f1d0a7d1693785 HEAD

# 2. Expect PASS; workflow 5576 of 5576 words.
python3 -B kc-dev-flow-2/scripts/lint-skills.py

# 3. Expect 41 ADR file(s) checked, 0 legacy; exit 0.
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1/scripts/adr_lint.py docs/adr --since e57feb6eec956b74a1d4b29f26f1d0a7d1693785 --require 0042

# 4. Expect PASS for the native prompt, first assignment read and runtime;
# seven deliberately changed prompt/provider/model/thinking/mode/cwd/workspace values fail.
python3 -B - "$WT" "$E" <<'PY'
import hashlib,json,sys
from pathlib import Path
wt=sys.argv[1]; e=Path(sys.argv[2])
raw=(e/'generated-prompt.txt').read_bytes()
assert raw.endswith(b'\n') and not raw.endswith(b'\n\n')
payload=raw[:-1] # command substitution removes the output-terminating newline
native=(e/'native-prompt.txt').read_bytes()
assert payload==native==(e/'build-output.txt').read_bytes().splitlines()[-1]
assert len(payload)==206
assert hashlib.sha256(payload).hexdigest()=='23d03db76299dafc69584f1fe071950a0872cd3eda5d4acbaa2f9b7dcd375de3'
assignment=(e/'assignment.md').read_bytes()
assert assignment==(e/'assignment-first-read.md').read_bytes()
assert hashlib.sha256(assignment).hexdigest()=='aaf3881ac0baef72d55622205b7f5810e20f38a6693a98a0a12593dfc23ee512'
s=json.loads((e/'self-status.json').read_text())['snapshot']
expected={'provider':'codex','model':'gpt-6-astra','thinkingOptionId':'high','currentModeId':'auto-review','cwd':wt,'workspaceId':'wks_31fac51fb7a34677'}
assert all(s[k]==v for k,v in expected.items())
assert s['runtimeInfo']['modeId']=='auto-review'
assert payload.decode() in json.loads((e/'self-activity.json').read_text())['content']
spawn=(e/'spawn.json').read_text()
assert s['id'] in spawn and s['workspaceId'] in spawn and wt in spawn
for k in expected:
 bad=dict(s); bad[k]='wrong'
 assert not all(bad[key]==value for key,value in expected.items())
assert payload+b' wrapper'!=native
print('PASS: 206-byte native prompt; 6107-byte first assignment read; runtime; 7 altered values rejected.')
PY

# 5. Expect PASS: one build/spawn host call, only tail/cat prompt transport;
# the prior real two-intermediate-call trace and inserted state commit fail.
# This checks the corrected FO receipt; it is not an independent FO transcript audit.
python3 -B - "$E" <<'PY'
import json,re,sys
from pathlib import Path
e=Path(sys.argv[1])
receipt=(e/'build-and-spawn.md').read_text()
correction=receipt.split('## Correction, 2026-10-28 (FO)',1)[1]
cmd=re.search(r'````bash\n(.*?)\n````',correction,re.S).group(1)
bridge=' > /tmp/v4.out 2>&1 && tail -1 /tmp/v4.out > /tmp/v4-prompt.txt && paseo agent run '
def forwarding_only(command):
 return (command.count('validate.py paseo-codex-dispatch-practice 742 ')==1
         and bridge in command and '--new-workspace local --cwd "$WT"' in command
         and '--json "$(cat /tmp/v4-prompt.txt)" > /tmp/v4-spawn.json 2>&1;' in command)
assert forwarding_only(cmd)
assert not forwarding_only(cmd.replace('&& paseo agent run ','&& spacedock state commit task && paseo agent run ',1))
prior=(e/'prior-failed-sequence.md').read_text()
calls=[json.loads(x) for x in re.findall(r'````json\n(.*?)\n````',prior,re.S)]
assert len(calls)==4 and 'validate.py' in calls[0]['command'] and 'paseo agent run' in calls[-1]['command']
assert len(calls)-2==2
assert '2026-10-28T14:42:10.210Z' in correction
s=json.loads((e/'self-status.json').read_text())['snapshot']
assert '2026-10-28T14:42:10.210Z' < s['createdAt'] < '2026-10-28T14:42:17.000Z'
print('PASS: corrected single build/spawn call; only prompt forwarding; prior 2-call violation and inserted commit rejected.')
print('LIMIT: FO supplied the command/timestamps; no build-time assignment hash was retained.')
PY
