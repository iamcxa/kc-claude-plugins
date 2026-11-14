#!/usr/bin/env bash
# usage: bash acceptance.sh <owner/name of the private working repository> <expected main sha>
set -u
REPO=$1; WANT=$2; D=$(mktemp -d /tmp/acc-XXXXXX); trap 'rm -rf "$D"' EXIT
gh repo clone "$REPO" "$D/clone" -- -q || exit 3
cd "$D/clone" || exit 3
echo "1. main is $(git rev-parse HEAD); expected $WANT"
echo "2. selfcheck per cell (expect every exit 0; one cell not-checked=9, the others 0):"
for c in behaviour/cells/*/; do
  n=$(basename "$c"); python3 -B behaviour/run_cell.py selfcheck "$c" > "$D/$n.log" 2>&1; rc=$?
  echo "   $n: exit $rc, not-checked=$(grep -c '^  not checked ' "$D/$n.log"), summary: $(grep '^NOT CHECKED' "$D/$n.log" | cut -c1-40)"
done
CELL=$(grep -l '^NOT CHECKED' "$D"/*.log | head -1 | xargs basename | sed 's/\.log$//')
FOLDER=$(grep '^  not checked ' "$D/$CELL.log" | head -1 | sed 's/^  not checked //' | xargs dirname)
cp -R "$D/clone" "$D/m1"
python3 -I - "$D/m1/behaviour/cells/$CELL" <<'PY'
import json, sys, pathlib
cell = pathlib.Path(sys.argv[1]); p = cell / "answer.json"; a = json.load(open(p))
rel = next(r for r in a["selfcheck"] if (cell / r).exists())
a["selfcheck"][rel]["verdict"] = "FAIL" if a["selfcheck"][rel]["verdict"] == "PASS" else "PASS"
json.dump(a, open(p, "w"), indent=2)
PY
(cd "$D/m1" && python3 -B behaviour/run_cell.py selfcheck "behaviour/cells/$CELL" > "$D/m1.out" 2>&1); echo "3. one carried entry's expected verdict flipped: exit $? (expect 1), last line: $(tail -1 "$D/m1.out")"
cp -R "$D/clone" "$D/m2"; mkdir -p "$D/m2/behaviour/cells/$CELL/$FOLDER"
(cd "$D/m2" && python3 -B behaviour/run_cell.py selfcheck "behaviour/cells/$CELL" > "$D/m2.out" 2>&1); echo "4. un-carried folder present but empty: exit $? (expect 1)"
