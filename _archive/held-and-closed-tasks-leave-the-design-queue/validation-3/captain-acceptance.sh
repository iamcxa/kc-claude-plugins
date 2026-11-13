#!/bin/bash
set -euo pipefail
# Four observable steps; no product worktree, private repository, or network is needed.
# Requires Git, tar, wc, Python 3.11 with PyYAML/pytest, and Spacedock 0.27.2.
EVIDENCE="$(cd "$(dirname "$0")" && pwd)"
STATE="$(cd "$EVIDENCE/../.." && pwd)"
CANDIDATE=5859c3ccd25a86c79df3b36cafdda9762bd8142e
BASE=46e9d0ed4bb86889022457adcdf656965dc97e73
export PATH="/Users/kent/.pyenv/versions/3.11.14/bin:$PATH"
export SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock PYTHONDONTWRITEBYTECODE=1
CHECK_ROOT="${CAPTAIN_SCRATCH:-$(mktemp -d /tmp/captain-acceptance-v3.XXXXXX)}"
OUTPUT="${CAPTAIN_EVIDENCE:-$CHECK_ROOT/results}"
mkdir -p "$CHECK_ROOT" "$OUTPUT" "$CHECK_ROOT/tmp"
export TMPDIR="$CHECK_ROOT/tmp" GIT_CEILING_DIRECTORIES="$CHECK_ROOT/tmp"
# Step 1: Export and verify the exact source. Expected: EXPORT <full SHA>.
git -C "$STATE" archive "$CANDIDATE" | tar -x -C "$CHECK_ROOT"
git -C "$CHECK_ROOT" init -q -b main
OBJECTS="$(git -C "$STATE" rev-parse --path-format=absolute --git-common-dir)/objects"
printf '%s\n' "$OBJECTS" > "$CHECK_ROOT/.git/objects/info/alternates"
git -C "$CHECK_ROOT" update-ref refs/heads/main "$CANDIDATE"
git -C "$CHECK_ROOT" read-tree "$CANDIDATE"
printf 'EXPORT %s\n' "$(git -C "$CHECK_ROOT" rev-parse HEAD)"
# Step 2: Export the recorded public held inputs. Expected: NATIVE INPUTS 15.
python3 - "$CHECK_ROOT" "$STATE" "$EVIDENCE" <<'PY'
from pathlib import Path
import io,json,subprocess,sys,tarfile
root,source,ev=map(Path,sys.argv[1:]);rev=json.loads((ev/'context.json').read_text())['state_head']
rows=json.loads((ev/'held-live.json').read_text())['entities']
tracked=set(subprocess.check_output(['git','-C',str(source),'ls-tree','-r','--name-only',rev],text=True).splitlines())
files=['README.md']+[r['slug']+'.md' if r['slug']+'.md' in tracked else r['slug']+'/index.md' for r in rows]
state=root/'docs/dev2/.spacedock-state';state.mkdir(parents=True)
data=subprocess.check_output(['git','-C',str(source),'archive',rev,*files])
tarfile.open(fileobj=io.BytesIO(data)).extractall(state,filter='data')
subprocess.run(['git','-C',str(state),'init','-q'],check=True)
assert len(rows)==15
print('NATIVE INPUTS 15')
PY
# Step 3: Test the changed behavior and decision record. Expected: 11 passed; ADR exit 0.
cd "$CHECK_ROOT"
python3 -B -m pytest --rootdir="$CHECK_ROOT" -q kc-dev-flow-2/scripts/test_pr_watch.py -k held --junitxml="$OUTPUT/held-tests.xml"
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1/scripts/adr_lint.py docs/adr --since "$BASE" --require 0081
# Step 4: Count the output and reject one-word-over-bound cases.
# Expected: ONE 17/21; CURRENT 33/35; LARGER 145/145; three REJECTED counterexamples.
python3 -B "$EVIDENCE/measure.py" --candidate "$CHECK_ROOT" --workflow "$CHECK_ROOT/docs/dev2" --scratch "$CHECK_ROOT/measure" --output "$OUTPUT"
printf 'PASS: exact candidate held behavior, ADR and amendment-4 counts\n'
# This does not close or edit live tasks, prove semantic labels, run the full suite, or approve delivery.
# Validation retains its explicit scratch until evidence is committed; ordinary runs remove their own root.
if [ -z "${CAPTAIN_SCRATCH:-}" ]; then rm -rf -- "$CHECK_ROOT"; fi
