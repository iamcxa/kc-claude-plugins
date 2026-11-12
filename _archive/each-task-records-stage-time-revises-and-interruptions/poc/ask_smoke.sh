#!/bin/bash
# Records two asks outside a gate on a throwaway state checkout and reads them back.
# Usage: bash ask_smoke.sh <task_timeline.py>
set -euo pipefail
TT=$1
D=$(mktemp -d /tmp/tt-ask-smoke.XXXXXX); trap 'rm -rf "$D"; echo "removed $D"' EXIT
git -C "$D" init -q
printf -- '---\ntitle: t\nstatus: ideation\n---\n\n## Scope\n' > "$D/demo.md"
git -C "$D" add demo.md
GIT_AUTHOR_DATE=2026-11-12T05:00:00Z git -C "$D" -c user.name=t -c user.email=t@t commit -qm "dispatch: demo entering ideation"
python3 -B "$TT" "$D" demo
python3 -B "$TT" "$D" demo ask "Push to the relay repo needs your yes: may I push?"
python3 -B "$TT" "$D" demo ask "上一題答完了，這題：要不要先合併 #850？"
python3 -B "$TT" "$D" demo
python3 -B "$TT" "$D" demo --json | python3 -c 'import json,sys; t=json.load(sys.stdin); assert t["asks_outside_gate"] == 2, t; print("asks_outside_gate == 2")'
python3 -B "$TT" "$D" demo ask "" && { echo "empty ask accepted"; exit 1; } || echo "empty ask refused"
