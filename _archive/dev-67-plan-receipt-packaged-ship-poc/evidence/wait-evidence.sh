#!/usr/bin/env bash
# wait-evidence.sh <ISSUE_ID> [max_iters] -> polls conductor sql every 30s until Evidence block; writes /tmp/poc2/<id>/evidence.txt
ID=$1; N=${2:-60}; OLD=${3:-}; D=/tmp/poc2/$ID; SID=$(grep -o 'session=[^ ]*' /tmp/poc2/claims/$ID | cut -d= -f2)
for i in $(seq 1 $N); do
  if /tmp/poc2/read-evidence.sh "$SID" > "$D/evidence.txt" 2>/dev/null && ! grep -q "CANDIDATE_SHA: $OLD" "$D/evidence.txt"; then printf 'evidence_at=%s\n' "$(date -u +%FT%TZ)" >> /tmp/poc2/claims/$ID; echo "EVIDENCE $ID after $((i*30))s"; cat "$D/evidence.txt"; exit 0; fi
  S=$(conductor session status "$SID" --json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['status'])"); echo "t=$((i*30))s $ID session=$S"; sleep 30
done; echo "TIMEOUT $ID"; exit 1
