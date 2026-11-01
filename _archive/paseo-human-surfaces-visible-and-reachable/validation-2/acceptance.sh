#!/bin/bash
set -euo pipefail
# 1. Create an exact detached candidate; pin the current PR base and its merge-base.
REPO='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-paseo-human-surfaces-visible-and-reachable'
PKG='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1'
STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
TASK="$STATE/paseo-human-surfaces-visible-and-reachable.md"
BASE=96b73073a1384951fab6de74ecfee94719127535
HEAD=8aa76f15f3ce56fbaa2b2e69dd0889c8bf5580fc
TMP_CHECK=$(mktemp -d "$REPO/.acceptance-757-r2.XXXXXX")
CHECK="$TMP_CHECK/checkout"
trap 'cd "$REPO"; git -C "$REPO" worktree remove "$CHECK"; rmdir "$TMP_CHECK"' EXIT
git -C "$REPO" worktree add --detach "$CHECK" "$HEAD"
cd "$CHECK"
test "$(git rev-parse HEAD)" = "$HEAD"
test -z "$(git status --porcelain)"
MERGE_BASE=$(git merge-base "$BASE" "$HEAD")
test "$MERGE_BASE" = 39fdbb28b411d44a323741f645c7c1d75c653be1
printf '%s\n' "PASS candidate $HEAD; main $BASE; merge-base $MERGE_BASE"

# 2. Match the approved one-file append and reject three document counterexamples.
python3 -B - "$TASK" "$BASE" <<'PY'
import pathlib,subprocess,sys
task=pathlib.Path(sys.argv[1]).read_text(); path='kc-dev-flow-2/extensions/paseo/EXTENSION.md'
before=subprocess.check_output(['git','show',sys.argv[2]+':'+path],text=True)
after=pathlib.Path(path).read_text()
approved=task.split('### Proposed extension text\n',1)[1].split('```text\n',1)[1].split('```',1)[0]
expected=before+'\n'+approved
assert after==expected
assert subprocess.check_output(['git','diff','--name-only',sys.argv[2]+'...HEAD'],text=True).splitlines()==[path]
for label,mutant in [('missing worker note',after.replace('For each worker needing human interaction, add to scope notes:','')),('missing section',before),('extra policy',after+'\nUse OS browser instead.\n')]:
    assert mutant!=expected
    print('REJECTED document control: '+label)
print('PASS one-file approved append; added words='+str(len(approved.split())))
PY

# 3. Run source-package lint and the installed decision-record check against main.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since "$BASE" --require 0042 0046

# 4. Check numbering, comments, affected documents, dispatch records and amendment form.
python3 -B "$PKG/scripts/number_guards.py" check --repo "$CHECK" --workflow-dir "$STATE/.." --task "$TASK" --base "$BASE" --head "$HEAD"
python3 -B "$PKG/scripts/comment_ratio.py" "$BASE" "$HEAD" --workflow-dir "$STATE/.."
python3 -B "$PKG/scripts/doc_impact.py" "$MERGE_BASE" "$HEAD"
python3 -B "$PKG/scripts/dispatch_records.py" "${TASK%.md}"
python3 -B "$PKG/scripts/dispatch_records.py" --names --strict "${TASK%.md}"/dispatch/*.md
python3 -B "$PKG/scripts/design_surfaces.py" check "$TASK"
git -C "$CHECK" diff --check "$BASE...$HEAD"

# 5. Display attributed human/cold evidence and independently read the amended device list.
cat "${TASK%.md}/human-trial/README.md" "${TASK%.md}/cold-fo/README.md"
python3 -B - "${TASK%.md}/human-trial/serve-baseline.json" <<'PY'
import json,pathlib,subprocess,sys
state=json.loads(subprocess.check_output(['/usr/local/bin/tailscale','status','--json'],text=True))
rows=[]
for device in [state['Self'],*state.get('Peer',{}).values()]:
    owner=state.get('User',{}).get(str(device.get('UserID')),{}).get('DisplayName')
    rows.append((device.get('HostName'),owner))
print('Current device list:',rows)
assert set(rows)=={('KentMacBookPro (3)','Kent Chen'),('Pixel 10 Pro XL','Kent Chen'),('Kent’s Mac mini','Kent Chen')},'Device list changed: return access question to FO'
current=json.loads(subprocess.check_output(['/usr/local/bin/tailscale','serve','status','--json'],text=True))
assert current==json.loads(pathlib.Path(sys.argv[1]).read_text()),'Serve differs from retained baseline: investigate ownership; do not reset it'
print('PASS current own-device list and unchanged Serve baseline; this is not an access-denial test')
PY
printf '%s\n' 'STATIC CHECKS PASS; HUMAN EVIDENCE IS FO-RECORDED, NOT REPLAYED. Worker execution/handback are post-delivery; Relay replay is separate under amendment 1.'
