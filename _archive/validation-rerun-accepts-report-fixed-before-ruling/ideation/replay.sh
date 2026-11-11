#!/usr/bin/env bash
# Usage: replay.sh <kc-claude-plugins checkout> <qnow checkout with origin/spacedock-state/dev2> <work dir that does not exist> [candidate dispatch_records.py]
# Builds three qnow state histories in <work dir> and runs the 0.38.0 tag and the candidate on each.
set -euo pipefail
K=$1 Q=$2 W=$3
mkdir "$W"; mkdir -p "$W/tag"
git -C "$K" archive kc-dev-flow-2-v0.38.0 kc-dev-flow-2 | tar -x -C "$W/tag"
OLD=$W/tag/kc-dev-flow-2/scripts/dispatch_records.py
if [ $# -ge 4 ]; then NEW=$4; else
  mkdir -p "$W/cand"; cp -R "$W/tag/kc-dev-flow-2" "$W/cand/"
  (cd "$W/cand" && patch -s -p1 < "$(dirname "$0")/prototype.diff"); NEW=$W/cand/kc-dev-flow-2/scripts/dispatch_records.py; fi
C=$W/qnow T=owner-cancels-booking.md R=owner-cancels-booking/dispatch/validation-2.md
git clone -q --no-checkout "$Q" "$C"
g(){ git -C "$C" -c user.name=replay -c user.email=replay@example.invalid "$@"; }
run(){ for v in "tag:$OLD" "candidate:$NEW"; do
  git -C "$C" show a1fe6eeec:owner-cancels-booking/dispatch/validation-1.md > "$C/$R"
  set +e; full=$(cd "$C" && python3 -B "${v#*:}" --names "$R" 2>/dev/null); code=$?; set -e
  out=$(printf '%s\n' "$full" | grep -o 'validation[^;]*rul[^;]*' | head -1 || true)
  echo "$1 ${v%%:*} exit=$code ${out:-<no ruling line>}"; rm -f "$C/$R"; done; }
g checkout -q -b recorded a1fe6eeec; run qnow-recorded-history
g checkout -q -b post-ruling a1fe6eeec
python3 - "$C/$T" <<'PY'
import sys; p = sys.argv[1]; s = open(p).read(); a = "implementation worktree preserved at candidate."
assert a in s; open(p, "w").write(s.replace(a, a[:-1] + " (edited after the ruling).", 1))
PY
g commit -q -m "rewrite after the amendment" -- "$T"; run rewrite-after-ruling
g checkout -q -b verdict-flip ee7a248ab
sed -i.bak 's/ is REJECTED: goal sufficiency/ is PASSED: goal sufficiency/' "$C/$T"; rm -f "$C/$T.bak"; g commit -q -m flip -- "$T"
git -C "$C" show 8419e6e2f:"$T" | sed 's/ is REJECTED: goal sufficiency/ is PASSED: goal sufficiency/' > "$C/$T"; g commit -q -m "amendment after flip" -- "$T"
run pre-ruling-verdict-flip
