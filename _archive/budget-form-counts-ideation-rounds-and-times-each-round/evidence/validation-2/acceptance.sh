#!/usr/bin/env bash
# Five checks, no screen: requires git, Python 3, and this public state checkout.
# Does not cover hosted CI completion, full corpus, or a released live dispatch.
set -euo pipefail
E=$(cd -- "$(dirname -- "$0")" && pwd)
STATE=$(git -C "$E" rev-parse --show-toplevel)
HEAD_CODE=a4f2fc41413866f0148e1f176f447e81216ca6cf
BASE_CODE=bfc53d82510006b52baf41569c1e25176e99d87a
SNAPSHOT=92c5db58613592dd25ae54f1184249fafbb3899d
RUNTIME_ROOT=${TMPDIR:-/tmp}
X=$(mktemp -d "$RUNTIME_ROOT/.acceptance-runtime.XXXXXX")
trap 'rm -rf -- "$X"' EXIT
export PYTHONDONTWRITEBYTECODE=1
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR
mkdir -p "$X/candidate" "$X/base" "$X/tmp"
export TMPDIR="$X/tmp"
echo '1/5: export exact candidate and base; expect the pinned candidate SHA'
git -C "$STATE" archive "$HEAD_CODE" | tar -x -C "$X/candidate"
git -C "$STATE" archive "$BASE_CODE" kc-dev-flow-2 | tar -x -C "$X/base"
git -C "$STATE" rev-parse "$HEAD_CODE"
git clone -q --no-hardlinks "$STATE" "$X/replay"
git -C "$X/replay" update-ref refs/remotes/origin/spacedock-state/dev2 "$SNAPSHOT"
PKG="$X/candidate/kc-dev-flow-2/scripts"
echo '2/5: legacy grammar and third-round replay; expect unchanged old forms and exits 0/1/0/0/1/1'
python3 -B "$E/grammar.py" "$X/base/kc-dev-flow-2/scripts" "$PKG"
python3 -B - "$E" "$PKG" "$X" <<'PYCODE'
from pathlib import Path
import subprocess,sys
E,P,X=map(Path,sys.argv[1:])
cases=[('2 ideation, 1 implementation and 2 validation cycles',2,0),('2 ideation, 1 implementation and 2 validation cycles',3,1),('3 ideation, 1 implementation and 2 validation cycles',3,0),('1 implementation and 2 validation cycles',2,0),('1 implementation and 2 validation cycles',3,1),('two ideation, one implementation and two validation cycles, in one package PR.',3,1)]
for i,(budget,n,expected) in enumerate(cases,1):
 r=subprocess.run(['bash',str(E/'replay.sh'),str(P),str(X),'merge-ask-holds-missing-clauses',budget,str(n)],capture_output=True,text=True)
 assert r.returncode==expected,(i,r.returncode,r.stdout,r.stderr)
 assert ('budget exceeded; hold for the Captain' in r.stdout)==bool(expected),(i,r.stdout)
 print(f'replay {i}: exit {r.returncode}, expected {expected}')
PYCODE
echo '3/5: recorded timeline; expect three rounds: 43.6 withdrawn, 562.2 revise, 97.0 approve'
python3 -B "$PKG/task_timeline.py" "$STATE" merge-ask-holds-missing-clauses --json > "$X/timeline.json"
python3 -B - "$X/timeline.json" <<'PYCODE'
import json,sys
row=next(r for r in json.load(open(sys.argv[1]))['stages'] if r['stage']=='ideation')
assert [(r['minutes'],r['result']) for r in row['rounds']]==[(43.6,'withdrawn'),(562.2,'revise'),(97.0,'approve')]
for r in row['rounds']:
 assert r['start'] and r['end']
 print(r)
PYCODE
echo '4/5: lint and ADR 0085; expect 6097 of 6097 words and exit zero'
python3 -B "$PKG/lint-skills.py"
python3 -B "$PKG/adr_lint.py" "$X/candidate/docs/adr" --root "$X/candidate" --require 0085
echo '5/5: derive POC; expect four stages, no ideation budget, discoverable five-stage prefix'
python3 -B - "$PKG" <<'PYDERIVE'
import sys,re
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from poc_readme import derive
source=(Path(sys.argv[1]).parent/'references/sd/workflow.md').read_text()
derived=derive(source)
assert [l.split(': ')[1] for l in derived.splitlines() if l.startswith('    - name: ')]==['backlog','implementation','validation','done']
assert not [l for l in derived.splitlines() if 'ideation' in l.lower() and 'the POC adaptation' not in l and 'removes ideation from both' not in l]
assert 'See stage prefixes;' in source.split('## Batch gates')[0]
assert 'Prefix `N ideation,`:' in source.split('### `ideation`')[1].split('### `implementation`')[0]
lines=source.split('\n'); entry=lines.index('    - name: ideation'); start=lines.index('### `ideation`');end=lines.index('### `implementation`');after=next(i for i in range(entry+1,len(lines)) if not lines[i].startswith('      '))
assert derived=='\n'.join(lines[:entry]+lines[after:start]+lines[end:])
print('PASS: four-stage derivation drops the budget prefix; five-stage reader can find it')
PYDERIVE
echo 'PASS: five acceptance checks'
