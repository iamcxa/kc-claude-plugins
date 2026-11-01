#!/bin/bash
set -euo pipefail
# 1. Pin the assigned source, installed package and exact stacked candidate; clean up on exit.
REPO='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-paseo-human-surfaces-visible-and-reachable'
PKG='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1'
STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
BASE=39fdbb28b411d44a323741f645c7c1d75c653be1
HEAD=8aa76f15f3ce56fbaa2b2e69dd0889c8bf5580fc
TMP_CHECK=$(mktemp -d "$REPO/.acceptance-757.XXXXXX")
CHECK="$TMP_CHECK/checkout"
trap 'cd "$REPO"; git -C "$REPO" worktree remove "$CHECK"; rmdir "$TMP_CHECK"' EXIT
git -C "$REPO" worktree add --detach "$CHECK" "$HEAD"
cd "$CHECK"
test "$(git rev-parse HEAD)" = "$HEAD"
test -z "$(git status --porcelain)"
git merge-base --is-ancestor "$BASE" HEAD
printf '%s\n' "PASS exact clean candidate $HEAD on $BASE"

# 2. Verify the single-file policy addition against the accepted text, including two negative controls.
python3 -B - "$STATE/paseo-human-surfaces-visible-and-reachable.md" "$BASE" <<'PY'
import pathlib, subprocess, sys
task=pathlib.Path(sys.argv[1]).read_text()
path='kc-dev-flow-2/extensions/paseo/EXTENSION.md'
before=subprocess.check_output(['git','show',sys.argv[2]+':'+path],text=True)
after=pathlib.Path(path).read_text()
approved=task.split('### Proposed extension text\n',1)[1].split('```text\n',1)[1].split('```',1)[0]
assert after == before+'\n'+approved
assert subprocess.check_output(['git','diff','--name-only',sys.argv[2],'HEAD'],text=True).splitlines()==[path]
for label, mutant in [('missing worker instruction',after.replace('For each worker needing human interaction, add to scope notes:', '')),('pre-change base',before)]:
    assert mutant != before+'\n'+approved
    print('REJECTED document control: '+label)
print('PASS one-file approved append; added words='+str(len(approved.split())))
PY

# 3. Run the repository lint and the installed decision-record check.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since "$BASE"

# 4. Check scope-related records and numbering using the assigned stacked base.
python3 -B "$PKG/scripts/number_guards.py" check --repo "$CHECK" --workflow-dir "$STATE/.." --task "$STATE/paseo-human-surfaces-visible-and-reachable.md" --base "$BASE" --head "$HEAD"
python3 -B "$PKG/scripts/comment_ratio.py" "$BASE" "$HEAD" --workflow-dir "$STATE/.."
python3 -B "$PKG/scripts/doc_impact.py" "$BASE" "$HEAD"
python3 -B "$PKG/scripts/dispatch_records.py" "$STATE/paseo-human-surfaces-visible-and-reachable"
python3 -B "$PKG/scripts/design_surfaces.py" check "$STATE/paseo-human-surfaces-visible-and-reachable.md"
git -C "$CHECK" diff --check "$BASE" "$HEAD"

# 5. Display the attributed attended record and its remaining real-use gaps.
cat "$STATE/paseo-human-surfaces-visible-and-reachable/human-trial/README.md"
printf '%s\n' 'STATIC CHECKS PASS; FULL PILOT ACCEPTANCE REJECTED: native worker loading/handback, excluded-device access and Relay replay remain unverified.'
