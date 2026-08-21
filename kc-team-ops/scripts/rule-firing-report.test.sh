#!/usr/bin/env bash
# The incident report pairs a user turn with the assistant turn before it. With
# several sessions running at once — the normal case here — a global sort by time
# puts another session's reply in that slot, which turns a follow-through failure
# into a blind spot: the exact two the classification table exists to separate.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
P="$WORK/home/projects/proj"; mkdir -p "$P"

turn() { printf '{"type":"%s","timestamp":"%s","message":{"content":[{"type":"text","text":"%s"}]}}\n' "$2" "$1" "$3"; }

# Session A promises the deploy; session B answers something unrelated in between.
{ turn 2026-08-10T10:00:00Z assistant "I will deploy staging now"
  turn 2026-08-10T10:02:00Z user      "我自己部署好了"; } > "$P/a.jsonl"
{ turn 2026-08-10T10:01:00Z assistant "The documentation typo is fixed"; } > "$P/b.jsonl"

printf 'incident\ttakeover\t我自己部署好了\n' > "$WORK/p.tsv"
cd "$WORK" && "$HERE/rule-firing-report.sh" --since 2026-08-01 --home "$WORK/home" \
  --patterns "$WORK/p.tsv" >/dev/null 2>&1

fail=0
before=$(grep -A1 -- '--- takeover' "$WORK/rule-review-incidents.txt" 2>/dev/null | tail -1)
case "$before" in
  *"I will deploy staging now"*) echo "PASS  BEFORE came from the same session" ;;
  *"documentation typo"*)        echo "FAIL  BEFORE came from another session: $before"; fail=1 ;;
  *)                             echo "FAIL  no BEFORE line found: ${before:-<empty>}"; fail=1 ;;
esac
exit $fail
