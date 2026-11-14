#!/usr/bin/env bash
# Run from the workspace root that contains .context/. Exit 0 = pass.
set -eu
S=.context/dev2-poc-route/docs/dev2-poc/.spacedock-state
T=shared-assumption-replay-on-archived-tasks-poc
F=c24854032f31aa6281810d7d0c492ebb206d1f6d
python3 -I $S/$T/evidence/implementation-1/verify_replay.py --workspace-root . --state-root $S >/dev/null
git -C $S merge-base --is-ancestor $F HEAD
fz=$(git -C $S show -s --format=%cI $F | python3 -I -c 'import sys,datetime;print(datetime.datetime.fromisoformat(sys.stdin.read().strip()).timestamp())')
python3 -I - "$S/$T/evidence/implementation-1" "$fz" <<'PY'
import json,sys,datetime
d,fz=sys.argv[1],float(sys.argv[2])
log=json.load(open(d+"/third-dispatch-read-log.json"))
assert len(log)==5
for r in log:
    assert datetime.datetime.fromisoformat(r["opened_at"]).timestamp()>fz,r["task"]
c=json.load(open(d+"/counts.json"))
assert c["literal_causal_matches"]==2 and c["matched_tasks"]==["dev2-laws-check","delivery-gate-verdict-form"]
assert c["independent_blind_predictions_demonstrated"]==0 and c["stop_triggered_by_literal_count"] is False
print("accept: ok")
PY
