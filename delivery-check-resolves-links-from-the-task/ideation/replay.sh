#!/usr/bin/env bash
# Replays the batch 15 (#793) and qnow #1338 Captain-steps cases against a package scripts dir.
# Usage: replay.sh <kc-dev-flow-2/scripts dir>   (default: origin/main extracted to $R/pkg)
# Needs this machine's kc-claude-plugins dev2 state and the qnow-adopt-dev2 state (read only); bounded local evidence.
set -eu
R=${R:-/tmp/dl-replay}; K=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo
KS=$K/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state; QS=$HOME/conductor/repos/qnow-adopt-dev2/docs/dev2/.spacedock-state
rm -rf "$R"; mkdir -p "$R/pkg" "$R/state" "$R/qstate" "$R/qwt"
git -C "$K" archive origin/main kc-dev-flow-2/scripts | tar -x -C "$R/pkg"
SCRIPTS=${1:-$R/pkg/kc-dev-flow-2/scripts}
sub() { grep -rlI "$2" "$1" | while read -r f; do python3 -c "import sys;p=sys.argv[1];t=open(p).read().replace(sys.argv[2],sys.argv[3]);open(p,'w').write(t)" "$f" "$2" "$3"; done; }
T=delivery-question-requires-worktree-clause
cp -R "$KS/_archive/$T" "$KS/_archive/$T.md" "$R/state/"
python3 - "$R" "$T" <<'PY'
import json, sys
R, T = sys.argv[1:]
d = json.load(open(f"{R}/state/{T}/review/validation/briefing-1/index.json"))
open(f"{R}/question.md", "w").write(d["question"] + "\n")
open(f"{R}/summary.md", "w").write(d["artifacts"][0]["summary"] + "\n")
PY
sub "$R" "$KS/$T" "$R/state/$T"
Q=preview-sign-in-wildcard
cp -R "$QS/_archive/$Q" "$QS/_archive/$Q.md" "$R/qstate/"
sub "$R/qstate" "$QS/$Q" "$R/qstate/$Q"
sub "$R/qstate" "$HOME/conductor/repos/qnow-adopt-dev2/.worktrees/spacedock-ensign-$Q" "$R/qwt"
# the waiver line was written after the failure; drop it to replay the text as first checked
grep -v '^Waiver:' "$R/qstate/$Q/captain-steps/gate-summary.md" > "$R/qsummary.md"
for d in "$K" "$R/state/$T" "$R/state"; do
  printf '#793 from %s: ' "$d"
  (cd "$d" && python3 -B "$SCRIPTS/delivery_gate.py" question "$R/state/$T.md" --text-file "$R/question.md" --summary-file "$R/summary.md" --workflow-dir "$K/.context/dev2-adoption/worktree/docs/dev2" | grep -E '^(Captain steps record fails|gate text complete)' || true)
done
for d in "$HOME/conductor/repos/qnow-adopt-dev2" "$R/qstate/$Q" "$R/qstate"; do
  printf '#1338 from %s: ' "$d"
  (cd "$d" && python3 -B "$SCRIPTS/delivery_gate.py" question "$R/qstate/$Q.md" --text-file "$R/qstate/$Q/captain-steps/gate-question.md" --summary-file "$R/qsummary.md" --workflow-dir "$HOME/conductor/repos/qnow-adopt-dev2/docs/dev2" | grep -E '^(Captain steps record fails|gate text complete)' || true)
done
