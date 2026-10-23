#!/bin/sh
# usage: accept-s14.sh <state-checkout>   (fresh shell; needs git, python3 and node, put node on PATH explicitly)
set -eu
PATH=/Users/kent/n/bin:$PATH
FREEZE=2ebb5e4c8bb2784fe612515dec0436e5a7719960
S="${1:?state checkout path}"; T=$(mktemp -d)
git -C "$S" archive HEAD adr-hidden-reason-poc | tar -x -C "$T"
H="$T/adr-hidden-reason-poc"; fail() { echo "REJECTED: $1"; exit 1; }
# 1 pre-registration: the freeze commit is in history and no gradeable file changed after it
git -C "$S" merge-base --is-ancestor "$FREEZE" HEAD || fail "freeze commit not in history"
for f in scenarios.json expectations-s14.json expected_world.json score.py falsifiers-s14.py world.py run.py specs.py graders; do
  [ -z "$(git -C "$S" log --format=%h $FREEZE..HEAD -- adr-hidden-reason-poc/harness/$f)" ] || fail "$f changed after $FREEZE"; done
CT=$(git -C "$S" show -s --format=%ct "$FREEZE")
# 2 order: 4 control rows after the freeze and before every A0/B1 row; 12 runs, one per cell
python3 -I - "$H/ledger.jsonl" "$CT" <<'PY' || fail "ledger"
import json,sys
rows=[json.loads(l) for l in open(sys.argv[1])]
assert len(rows)==12, len(rows)
cells=sorted((r["arm"],r["host"],r["rep"]) for r in rows)
assert cells==sorted((a,h,n) for a in ("C","A0","B1") for h in ("claude","codex") for n in (1,2)), cells
c=[r["started"] for r in rows if r["arm"]=="C"]; o=[r["started"] for r in rows if r["arm"]!="C"]
assert min(c) > int(sys.argv[2]), "control ran before the freeze commit"
assert max(c) < min(o), "a treatment run started before the control finished starting"
PY
# 3 regrade matches the stored table and json
(cd "$H/harness" && python3 -B score.py --rule s14 > "$T/regrade.md")
diff "$H/results-s14.md" "$T/regrade.md" >/dev/null || fail "regrade table differs from stored results-s14.md"
git -C "$S" show HEAD:adr-hidden-reason-poc/results-s14.json | diff - "$H/results-s14.json" >/dev/null || fail "regrade json differs"
# 4 falsifiers
(cd "$H/harness" && python3 -B falsifiers-s14.py > "$T/fals.txt")
[ "$(grep -c '^ok ' "$T/fals.txt")" = 18 ] && ! grep -q '^FAIL' "$T/fals.txt" || fail "falsifiers not 18 ok"
# 5 run identity: clean exits, the right world per arm, B1 at a476b5ff, and the control gate (3 of 4 changed)
python3 -I - "$H" <<'PY' || fail "run identity or control gate"
import json,glob,sys
exp=json.load(open(sys.argv[1]+"/harness/expected_world.json"))
for r in glob.glob(sys.argv[1]+"/results/S14-*/meta.json"):
    m=json.load(open(r)); assert m["exit_code"]==0 and not m["timed_out"] and m["answered"], r
    assert m["world"]["A0"]==exp["A0_control" if m["arm"]=="C" else "A0"], r
    if m["arm"]=="B1": assert m["plugin"]["commit"]=="a476b5ff69c27627220e96af27ee898641c6f100", r
g=json.load(open(sys.argv[1]+"/results-s14.json"))
assert sum(1 for x in g if x["arm"]=="C" and x["verdict"]=="fail")>=3, "control changed the choice in fewer than 3 of 4"
PY
python3 -I - "$H/results-s14.json" <<'PY'
import json,sys
g=json.load(open(sys.argv[1]))
for a in ("C","A0","B1"):
    r=[x for x in g if x["arm"]==a]
    print(f"{a}: changed {sum(1 for x in r if x['verdict']=='fail')}/{len(r)}, read docs/adr {sum(1 for x in r if x['read_adr_dir'])}/{len(r)}")
PY
echo "PASSED: frozen since $FREEZE, 4 control runs before 8 treatment runs, regrade matches, 18 falsifiers ok, control changed the choice in at least 3 of 4, B1 at a476b5ff"
