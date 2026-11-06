#!/usr/bin/env bash
set -euo pipefail
REPO=${1:?absolute assigned candidate worktree}
TASK=${2:?absolute task evidence folder}
PACKAGE=${3:?absolute declared kc-dev-flow-2 package}
HEAD_PIN=1ca2625de0706e5494f73e010a394f8e5194b2a1
BASE=ba055b8a7a55a787ac989c4cef52d07dd75661ad
OUT=$(mktemp -d /tmp/skipped-run-acceptance-XXXXXX)

# 1. Export the pinned candidate and base; leave the worktree untouched.
test "$(git -C "$REPO" rev-parse HEAD)" = "$HEAD_PIN"
GIT_META=$(git -C "$REPO" rev-parse --absolute-git-dir)
mkdir -p "$OUT/candidate" "$OUT/base" "$OUT/evidence"
git -C "$REPO" archive "$HEAD_PIN" | tar -x -C "$OUT/candidate"
git -C "$REPO" archive "$BASE" | tar -x -C "$OUT/base"
printf 'PASS 1: exported candidate %s and base %s\n' "$HEAD_PIN" "$BASE"

# 2. Replay the six accepted scenarios and check exits and printed word counts.
python3 -B "$TASK/ideation/replay.py" "$OUT/candidate/kc-dev-flow-2/scripts" "$TASK/ideation/pr1338.json" > "$OUT/evidence/candidate-replay.log"
python3 -B "$TASK/ideation/replay.py" "$OUT/base/kc-dev-flow-2/scripts" "$TASK/ideation/pr1338.json" > "$OUT/evidence/base-replay.log"
python3 -B - "$OUT/evidence" <<'PY'
import pathlib, re, sys
root = pathlib.Path(sys.argv[1])
for name, expected in [('candidate', [(0,84),(1,85),(1,85),(1,49),(1,58),(1,56)]), ('base',[(1,56),(1,87),(1,87),(1,58),(1,58),(1,56)])]:
    text = (root/(name+'-replay.log')).read_text()
    rows = [(int(c),int(w)) for c,w in re.findall(r'^== .*: exit (\d+), printed words (\d+)$', text, re.M)]
    assert rows == expected, (name, rows)
    if name == 'candidate':
        assert "required check without a pass on this head: 'ci-gate'" in text
print('PASS 2: intended skip 1 -> 0; five failing cases remain held; word counts match')
PY

# 3. Exercise pass/hold/read-error and exact-call boundaries.
(cd "$OUT/candidate/kc-dev-flow-2/scripts" && python3 -B -m unittest test_delivery_gate.RequiredChecksTests test_delivery_gate.SettledChecksTests > "$OUT/evidence/boundaries.log" 2>&1)
printf 'PASS 3: required-check and settled-check tests\n'

# 4. Reject all ten behavioral mutants and the workflow-text mutant.
python3 -B "$TASK/implementation/mutations.py" "$OUT/candidate" "$OUT/evidence" > "$OUT/evidence/mutations.log"
GIT_DIR="$GIT_META" GIT_WORK_TREE="$OUT/candidate" python3 -B "$PACKAGE/scripts/doc_impact.py" --repo "$OUT/candidate" "$BASE" "$HEAD_PIN" --json > "$OUT/evidence/doc-impact.json"
GIT_DIR="$GIT_META" GIT_WORK_TREE="$OUT/candidate" python3 -B "$TASK/implementation/scope-proof.py" "$OUT/candidate" "$OUT/evidence" > "$OUT/evidence/scope-proof.log"
printf 'PASS 4: ten behavioral mutants caught; only two approved product files differ; FO text unchanged\n'

# 5. Check architecture decision records against the pinned base.
(cd "$OUT/candidate" && GIT_DIR="$GIT_META" GIT_WORK_TREE="$OUT/candidate" python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE" > "$OUT/evidence/adr-lint.log" 2>&1)
printf 'PASS 5: ADR lint exit 0\nEvidence: %s/evidence\n' "$OUT"
