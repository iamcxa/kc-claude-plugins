#!/usr/bin/env bash
# Four observable checks of the pinned candidate; no user interface changes.
set -euo pipefail
SOURCE=${1:?pass the pinned product checkout}
QNOW_STATE=${2:?pass a local read-only source containing the recorded qnow state commits}
PACKAGE=${3:?pass the installed kc-dev-flow-2 0.38.1 package}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HEAD_SHA=0a5c37f091daec6909a76d443219c655b17d534e
BASE_SHA=546a136386c94c58e430c91a6f3457b38bd73880

# 1. Export the exact candidate and released baseline. Expected: PASS export.
test "$(git -C "$SOURCE" rev-parse HEAD)" = "$HEAD_SHA"
test -z "$(git -C "$SOURCE" status --porcelain -- docs/adr kc-dev-flow-2)"
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/val844-acceptance.XXXXXX")
trap 'rm -rf -- "$SCRATCH"; printf "Removed scratch: %s\n" "$SCRATCH"' EXIT
mkdir "$SCRATCH/candidate" "$SCRATCH/tag" "$SCRATCH/tmp"
export TMPDIR="$SCRATCH/tmp" PYTHONDONTWRITEBYTECODE=1
git -C "$SOURCE" archive --output="$SCRATCH/candidate.tar" "$HEAD_SHA"
git -C "$SOURCE" archive --output="$SCRATCH/tag.tar" kc-dev-flow-2-v0.38.1 kc-dev-flow-2
tar -xf "$SCRATCH/candidate.tar" -C "$SCRATCH/candidate"
tar -xf "$SCRATCH/tag.tar" -C "$SCRATCH/tag"
printf 'PASS export %s\n' "$HEAD_SHA"

# 2. Exercise repaired and deliberately held histories. Expected: 12 tests, OK.
cd "$SCRATCH/candidate/kc-dev-flow-2/scripts"
python3 -B -m unittest test_dispatch_records.RepairedRulingHistoryTests test_dispatch_records.LiveValidationRulingTests.test_old_and_same_commit_rulings_do_not_clear
printf 'PASS repaired-history and same-commit controls\n'

# 3. Replay the real task at nine pinned revisions. Expected: five 2/0, two 1/1,
#    two 2/2; equal exits must preserve the entire diagnostic.
#    Only this disposable clone is checked out; the source repository is read-only.
git clone --quiet --shared --no-checkout "$QNOW_STATE" "$SCRATCH/state"
python3 -B - "$HERE/../implementation" "$SCRATCH" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from replay import compare, module
scratch = Path(sys.argv[2])
old = module(scratch / 'tag/kc-dev-flow-2/scripts/dispatch_records.py', 'released')
new = module(scratch / 'candidate/kc-dev-flow-2/scripts/dispatch_records.py', 'candidate')
cases = [('f6c94d50', 1, 1), ('78a76aa2', 1, 1), ('03838f91', 2, 2),
         ('a28d69b5', 2, 2), ('071fe3b6', 2, 0), ('cf9560fc', 2, 0),
         ('744eaa08', 2, 0), ('5868a574', 2, 0), ('b99a7543', 2, 0)]
for rev, a, b in cases:
    pair = compare(scratch / 'state', rev, 'owner-cancels-booking/dispatch/validation-3.md', old, new)
    assert [p['exit'] for p in pair] == [a, b], (rev, pair)
    assert a != b or pair[0] == pair[1], (rev, pair)
    print(f'PASS {rev}: released={a} candidate={b}')
PY

# 4. Check the decision record on the verified exact checkout. Expected: exit 0.
cd "$SOURCE"
python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE_SHA" --require 0045
printf 'PASS ADR lint; acceptance complete\n'
