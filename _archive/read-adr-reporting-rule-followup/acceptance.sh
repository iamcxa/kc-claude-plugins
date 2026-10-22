#!/usr/bin/env bash
# Offline acceptance for read-adr-reporting-rule-followup, candidate 45dcf093. Runs no agent. Writes only under a mktemp dir.
set -eu
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree
CAND=$WT/.worktrees/spacedock-ensign-read-adr-reporting-rule-followup
STATE=$WT/docs/dev2/.spacedock-state
PKG=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0
BASE=cebd0ab93c7f9b681d55434cfc99c19b2d9dd8ba
HEAD_SHA=45dcf0931b150561bd944b9ec52b8fafecef3136
ok() { echo "PASS $*"; }; bad() { echo "FAIL $*"; exit 1; }

# 1. candidate is the pinned commit; only SKILL.md changed
[ "$(git -C "$CAND" rev-parse HEAD)" = "$HEAD_SHA" ] || bad "candidate HEAD is not $HEAD_SHA"
[ "$(git -C "$CAND" diff --name-only $BASE $HEAD_SHA)" = "kc-adr/skills/read-adr/SKILL.md" ] || bad "diff touches more than SKILL.md"
ok "1 pinned commit, one file changed"

# 2. scratch copy so score.py cannot write into the state checkout
T=$(mktemp -d /tmp/acc-readadr.XXXXXX)
mkdir -p "$T/_archive/kc-decision-log-cli"
cp -R "$STATE/_archive/kc-decision-log-cli/results" "$T/_archive/kc-decision-log-cli/results"
cp -R "$STATE/read-adr-reporting-rule-followup" "$T/task"
cd "$T/task"

# 3. grader falsifiers: 32 cases, all as expected
python3 -B harness/falsifiers.py > "$T/fals.txt"
[ "$(grep -c '^ok' "$T/fals.txt")" = 32 ] && [ "$(grep -vc '^ok' "$T/fals.txt")" = 0 ] || bad "falsifiers not 32/32"
ok "3 falsifiers 32 of 32"

# 4. AC-1: 4 of 4 cells Y on the original runs (5a2e901f) and on the final bytes (45dcf093)
python3 -B harness/score.py --rule v3 >/dev/null
python3 -B harness/score.py --rule v3 --results results-fix >/dev/null
for f in results-v3.md results-v3-results-fix.md; do
  [ "$(grep -c '^| S\(9\|11\) \(claude\|codex\) .*| Y | - |$' $f)" = 4 ] || bad "AC-1 not 4/4 in $f"
done
for r in results-fix/S9-B1-claude-r7 results-fix/S9-B1-codex-r7 results-fix/S11-B1-claude-r7 results-fix/S11-B1-codex-r7; do
  grep -q '"commit": "45dcf0931b150561bd944b9ec52b8fafecef3136"' $r/meta.json || bad "$r not run on 45dcf093"
done
ok "4 AC-1 4/4 on both byte versions; fix runs carry commit 45dcf093"

# 5. S7 Claude placement: candidate before fix 0/3, shipped control 0/3 wrote story map (3/3 Y), fixed 3/3 Y
place() { python3 -B harness/score.py --rule v2 --results "$1" --run "$2" | python3 -I -c 'import sys,json;d=json.load(sys.stdin);g=d if isinstance(d,dict) else d[0];print(g["placement"]["ok"])'; }
for r in r1 r2 r3; do [ "$(place results S7-B1-claude-$r)" = False ] || bad "S7 $r expected N"; done
for r in r4 r5 r6; do [ "$(place results-control S7-B1-claude-$r)" = True ] || bad "control $r expected Y"; done
for r in r7 r8 r9; do [ "$(place results-fix S7-B1-claude-$r)" = True ] || bad "fixed S7 $r expected Y"; done
ok "5 S7 Claude placement: 5a2e901f 0/3, shipped control 3/3, 45dcf093 3/3"

# 6. AC-2: rep-1 compare on the original runs shows exactly the one S7 regression; the final-bytes grid shows none
set +e; python3 -B harness/compare.py > "$T/c1.txt"; c1=$?; set -e
[ "$c1" = 1 ] && [ "$(grep -c REGRESSION "$T/c1.txt")" = 1 ] && grep -q 'S7 | claude | placement | Y | N | REGRESSION' "$T/c1.txt" || bad "original compare not the one expected regression"
mkdir "$T/final"
for r in S6-B1-claude-r1 S6-B1-codex-r1 S7-B1-codex-r1; do cp -R results/$r "$T/final/"; done
cp -R results-fix/S7-B1-claude-r7 "$T/final/S7-B1-claude-r1"; cp -R results-fix/S9-B1-claude-r7 "$T/final/S9-B1-claude-r1"; cp -R results-fix/S9-B1-codex-r7 "$T/final/S9-B1-codex-r1"
python3 -I - "$T/final" <<'PY'
import json,sys
for r in ("S7-B1-claude-r1","S9-B1-claude-r1","S9-B1-codex-r1"):
    p=f"{sys.argv[1]}/{r}/meta.json"; m=json.load(open(p)); m["rep"]=1; m["run"]=r; json.dump(m,open(p,"w"))
PY
python3 -B harness/compare.py --new "$T/final" | tail -1 | grep -q 'stored Y 23, new Y 24, regressions 0' || bad "final-bytes grid has a regression"
ok "6 AC-2: original rep 1 = 1 regression; final-bytes grid = 0 (S6 and S7 Codex cells are from 5a2e901f)"

# 7. run counts: 20 ledger lines
[ "$(wc -l < ledger.jsonl | tr -d ' ')" = 20 ] || bad "ledger is not 20 runs"
ok "7 ledger 20 runs"

# 8. adr_lint at the candidate, exit code printed
cd "$CAND"
set +e; python3 -I "$PKG/scripts/adr_lint.py" docs/adr --since $BASE; rc=$?; set -e
echo "adr_lint exit $rc"; [ "$rc" = 0 ] || bad "adr_lint exit $rc"
ok "8 adr_lint exit 0"
rm -rf "$T"; echo "ALL PASS"
