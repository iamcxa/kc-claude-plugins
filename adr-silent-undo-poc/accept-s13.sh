#!/bin/sh
# usage: accept-s13.sh <state-checkout>   (fresh shell; needs git, python3, node)
set -eu
S="${1:?state checkout path}"; T=$(mktemp -d)
git -C "$S" archive HEAD adr-silent-undo-poc | tar -x -C "$T"
H="$T/adr-silent-undo-poc"; fail() { echo "REJECTED: $1"; exit 1; }
# 1 pre-registration: no gradeable file changed after 12bc4a2d, and it precedes the first run
for f in scenarios.json expectations-s13.json expected_world.json score.py falsifiers-s13.py world.py run.py graders; do
  [ -z "$(git -C "$S" log --format=%h 12bc4a2d..HEAD -- adr-silent-undo-poc/harness/$f)" ] || fail "$f changed after 12bc4a2d"; done
CT=$(git -C "$S" show -s --format=%ct 12bc4a2d)
python3 -I - "$H/ledger.jsonl" "$CT" <<'PY' || fail "ledger"
import json,sys
rows=[json.loads(l) for l in open(sys.argv[1])]
assert len(rows)==4, len(rows)
assert min(r["started"] for r in rows) > int(sys.argv[2]), "run before commit"
assert sorted((r["arm"],r["host"]) for r in rows)==[("A0","claude"),("A0","codex"),("B1","claude"),("B1","codex")]
PY
# 2 regrade matches stored table and json
(cd "$H/harness" && python3 -B score.py --rule s13 > "$T/regrade.md")
git -C "$S" show HEAD:adr-silent-undo-poc/results-s13.md | diff - "$T/regrade.md" >/dev/null || fail "regrade table differs from stored results-s13.md"
git -C "$S" show HEAD:adr-silent-undo-poc/results-s13.json | diff - "$H/results-s13.json" >/dev/null || fail "regrade json differs"
[ "$(grep -c '| pass | unchanged |' "$T/regrade.md")" = 4 ] || fail "not 4 pass/unchanged"
# 3 falsifiers
(cd "$H/harness" && python3 -B falsifiers-s13.py > "$T/fals.txt")
[ "$(grep -c '^ok ' "$T/fals.txt")" = 11 ] && ! grep -q '^FAIL\|^not ok' "$T/fals.txt" || fail "falsifiers not 11 ok"
# 4 B1 plugin identity
python3 -I - "$H" <<'PY' || fail "B1 plugin identity or exit codes"
import json,glob,sys
for r in glob.glob(sys.argv[1]+"/results/S13-B1-*/meta.json"):
    assert json.load(open(r))["plugin"]["commit"].startswith("a476b5ff"), r
for r in glob.glob(sys.argv[1]+"/results/S13-*/meta.json"):
    m=json.load(open(r)); assert m["exit_code"]==0 and not m["timed_out"], r
PY
echo "PASSED: regrade matches (4 pass via unchanged), 11 falsifiers ok, harness frozen since 12bc4a2d, 4 runs A0/B1 x claude/codex, B1 at a476b5ff"
