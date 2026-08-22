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
  --patterns "$WORK/p.tsv" --out "$WORK/runs" >/dev/null 2>&1
RUN="$(ls -1dt "$WORK/runs"/*/ 2>/dev/null | head -1)"

fail=0
before=$(grep -A1 -- '--- takeover' "${RUN:-$WORK}incidents.txt" 2>/dev/null | tail -1)
case "$before" in
  *"I will deploy staging now"*) echo "PASS  BEFORE came from the same session" ;;
  *"documentation typo"*)        echo "FAIL  BEFORE came from another session: $before"; fail=1 ;;
  *)                             echo "FAIL  no BEFORE line found: ${before:-<empty>}"; fail=1 ;;
esac
# The filter that separates "the user typed this" from "the agent wrote this for its
# own worker" decides every friction number, and it had no test while two dispatch
# prompts survived it in real data.
P2="$WORK/home2/projects/proj"; mkdir -p "$P2"
{ turn 2026-08-10T10:00:00Z user "You are a read-only reviewer. Do not edit files."
  turn 2026-08-10T10:01:00Z user "You are still ignoring the comment rule"
  turn 2026-08-10T10:02:00Z user "Respond with exactly: OK"
  turn 2026-08-10T10:03:00Z user "這個檔案沒有會怎樣"; } > "$P2/c.jsonl"

printf 'friction	anything	.
' > "$WORK/p2.tsv"
cd "$WORK" && "$HERE/rule-firing-report.sh" --since 2026-08-01 --home "$WORK/home2" \
  --patterns "$WORK/p2.tsv" --out "$WORK/runs2" >/dev/null 2>"$WORK/stderr.txt"
H="$(ls -1dt "$WORK/runs2"/*/ 2>/dev/null | head -1)human-turns.tsv"

check() { # description, pattern, expected-count
  n=$(grep -c "$2" "$H" 2>/dev/null || true)
  if [ "${n:-0}" = "$3" ]; then echo "PASS  $1"; else echo "FAIL  $1 (got ${n:-0}, want $3)"; fail=1; fi
}
check "dispatch prompt dropped"       'You are a read-only'      0
check "'Respond with exactly' dropped" 'Respond with exactly'    0
check "real correction kept"          'still ignoring'           1
check "ordinary turn kept"            '沒有會怎樣'                1

# A clean run must say nothing on stderr. Every defect that reached a user here
# was a tool-dialect one — a flag this platform's head or awk does not have — and
# each announced itself there while the script carried on and reported numbers
# anyway. Asserting silence catches the whole class, including the next one.
if [ -s "$WORK/stderr.txt" ]; then
  echo "FAIL  clean run wrote to stderr:"; sed 's/^/        /' "$WORK/stderr.txt"; fail=1
else
  echo "PASS  clean run wrote nothing to stderr"
fi

exit $fail
