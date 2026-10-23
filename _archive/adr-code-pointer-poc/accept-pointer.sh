#!/bin/sh
# usage: accept-pointer.sh <state-checkout>   (fresh shell; needs git, python3 and node; puts node on PATH itself if missing)
set -eu
command -v node >/dev/null 2>&1 || PATH=/Users/kent/n/bin:$PATH
FREEZE=29fae05982e6fe5d45d97c5bb1e3d6ac05c09107
S="${1:?state checkout path}"; T=$(mktemp -d)
git -C "$S" archive HEAD adr-code-pointer-poc _archive/adr-hidden-reason-poc/harness | tar -x -C "$T"
H="$T/adr-code-pointer-poc"; OLD="$T/_archive/adr-hidden-reason-poc/harness"; fail() { echo "REJECTED: $1"; exit 1; }
# 1 pre-registration: the freeze commit is in history and no harness file changed after it
git -C "$S" merge-base --is-ancestor "$FREEZE" HEAD || fail "freeze commit not in history"
[ -z "$(git -C "$S" log --format=%h $FREEZE..HEAD -- adr-code-pointer-poc/harness)" ] || fail "harness changed after $FREEZE"
CT=$(git -C "$S" show -s --format=%ct "$FREEZE")
# 2 only the arm differs: four files differ from the archived harness, and the P world differs from the A0 world by exactly the one comment line
(cd "$T" && diff -rq "$OLD" "$H/harness" | sed -e "s#$OLD/##" -e "s#$H/harness/##" | sort > "$T/differs.txt" || true)
printf 'Files .* and expected_world.json differ\nFiles .* and run.py differ\nFiles .* and score.py differ\nFiles .* and world.py differ\n' > "$T/want.txt"
[ "$(wc -l < "$T/differs.txt" | tr -d ' ')" = 4 ] && [ "$(sed -e 's#^Files .* and \(.*\) differ$#\1#' "$T/differs.txt" | tr '\n' ' ')" = "expected_world.json run.py score.py world.py " ] || fail "unexpected harness differences: $(cat "$T/differs.txt")"
(cd "$H/harness" && python3 -I -B - <<'PY') || fail "P world is not the A0 world plus one comment line"
import subprocess, sys, tempfile, pathlib
sys.path.insert(0, ".")
import world
a, b = pathlib.Path(tempfile.mkdtemp()), pathlib.Path(tempfile.mkdtemp())
world.build(a); world.build(b, pointer=True)
out = subprocess.run(["diff", "-r", "-x", ".git", str(a), str(b)], capture_output=True, text=True).stdout.splitlines()
added = [l for l in out if l.startswith(">")]; other = [l for l in out if l.startswith("<")]
assert len(added) == 1 and not other, out
assert added[0].lstrip("> ").startswith("// ") and "docs/adr/0024-report-emails-are-sent-from-the-stored-copy.md" in added[0], added
assert sum(1 for l in out if l.startswith("diff ")) == 1 and "mira-app/src/report_mailer.js" in out[0], out
PY
# 3 ledger: 4 rows, one per cell, all started after the freeze commit
python3 -I - "$H/ledger.jsonl" "$CT" <<'PY' || fail "ledger"
import json,sys
rows=[json.loads(l) for l in open(sys.argv[1])]
assert len(rows)==4, len(rows)
assert sorted((r["arm"],r["host"],r["rep"]) for r in rows)==sorted(("P",h,n) for h in ("claude","codex") for n in (1,2))
assert min(r["started"] for r in rows) > int(sys.argv[2]), "a run started before the freeze commit"
PY
# 4 regrade matches the stored table and json
(cd "$H/harness" && python3 -B score.py --rule s14 > "$T/regrade.md")
diff "$H/results-s14.md" "$T/regrade.md" >/dev/null || fail "regrade table differs from stored results-s14.md"
git -C "$S" show HEAD:adr-code-pointer-poc/results-s14.json | diff - "$H/results-s14.json" >/dev/null || fail "regrade json differs"
# 5 the archived falsifiers still pass against this harness
(cd "$H/harness" && python3 -B falsifiers-s14.py > "$T/fals.txt")
[ "$(grep -c '^ok ' "$T/fals.txt")" = 18 ] && ! grep -q '^FAIL' "$T/fals.txt" || fail "falsifiers not 18 ok"
# 6 run identity: clean exits, the P world, every cell answered
python3 -I - "$H" <<'PY' || fail "run identity"
import json,glob,sys
exp=json.load(open(sys.argv[1]+"/harness/expected_world.json"))
ms=glob.glob(sys.argv[1]+"/results/S14-P-*/meta.json"); assert len(ms)==4, len(ms)
for r in ms:
    m=json.load(open(r)); assert m["arm"]=="P" and m["exit_code"]==0 and not m["timed_out"] and m["answered"], r
    assert m["world"]["A0"]==exp["A0_pointer"], r
PY
# 7 the comment diagnostic matches the stored one
(cd "$H" && python3 -I -B comment_check.py > "$T/cc.md")
diff "$H/comment-check.md" "$T/cc.md" >/dev/null || fail "comment_check output differs from stored comment-check.md"
python3 -I - "$H/results-s14.json" "$T/cc.md" <<'PY'
import json,sys
g=json.load(open(sys.argv[1]))
print(f"P: undone {sum(1 for x in g if x['verdict']=='fail')}/{len(g)}, passed {sum(1 for x in g if x['verdict']=='pass')}/{len(g)}, ungradable {sum(1 for x in g if x['verdict']=='ungradable')}/{len(g)}, opened the protecting ADR {sum(1 for x in g if x['read_protecting_adr'])}/{len(g)}")
print(open(sys.argv[2]).read())
PY
echo "PASSED: evidence intact (frozen since $FREEZE, only the arm differs, 4 runs after the freeze, regrade matches, 18 falsifiers ok); this checks the record, it does not choose between the options"
