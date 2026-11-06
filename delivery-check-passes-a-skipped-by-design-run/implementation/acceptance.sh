#!/usr/bin/env bash
set -euo pipefail
WT=${1:?absolute candidate worktree}
TASK_ROOT=${2:?absolute task evidence folder}
OUT=${3:?absolute output folder}
PACKAGE=${4:?absolute declared kc-dev-flow-2 package}
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
BASE=ba055b8a7a55a787ac989c4cef52d07dd75661ad
mkdir -p "$OUT"
test -z "$(git -C "$WT" status --porcelain)"
test "$(git -C "$WT" branch --show-current)" = spacedock-ensign/delivery-check-passes-a-skipped-by-design-run
python3 -B "$TASK_ROOT/ideation/replay.py" "$WT/kc-dev-flow-2/scripts" "$TASK_ROOT/ideation/pr1338.json" > "$OUT/candidate-replay.log"
python3 -B - "$OUT/candidate-replay.log" <<'PY'
import re, sys
from pathlib import Path
rows = re.findall(r'^== (.*): exit (\d+), printed words (\d+)$', Path(sys.argv[1]).read_text(), re.M)
assert [(int(code), int(words)) for _, code, words in rows] == [(0, 84), (1, 85), (1, 85), (1, 49), (1, 58), (1, 56)], rows
PY
(
    cd "$WT/kc-dev-flow-2/scripts"
    python3 -B -m unittest test_delivery_gate.RequiredChecksTests test_delivery_gate.SettledChecksTests > "$OUT/acceptance-tests.log" 2>&1
)
python3 -B "$HERE/mutations.py" "$WT" "$OUT" > "$OUT/mutations.log"
python3 -B "$PACKAGE/scripts/doc_impact.py" --repo "$WT" "$BASE" HEAD --json > "$OUT/doc-impact.json"
python3 -B "$HERE/scope-proof.py" "$WT" "$OUT" > "$OUT/scope-proof.log"
test -z "$(git -C "$WT" status --porcelain)"
printf 'PASS: replay exits/words, required-check boundaries, mutation falsifiers and product scope\n'
