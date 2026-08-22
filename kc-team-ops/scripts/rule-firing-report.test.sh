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

# The shipped incident patterns decide whether a turn is read as a blind spot, and a
# loose one sends the audit looking for a vacancy that never happened. "掃掉" alone
# scored a routine "file a ticket to clean this up" as destroyed work.
P3="$WORK/home3/projects/proj"; mkdir -p "$P3"
{ turn 2026-08-10T10:00:00Z user "開一張掃掉"
  turn 2026-08-10T10:01:00Z user "我掃掉了另一個 session 三個未提交的檔案"; } > "$P3/d.jsonl"

cd "$WORK" && "$HERE/rule-firing-report.sh" --since 2026-08-01 --home "$WORK/home3" \
  --out "$WORK/runs3" >/dev/null 2>&1
R3="$(ls -1dt "$WORK/runs3"/*/ 2>/dev/null | head -1)report.txt"
loss=$(grep -E '^loss or recovery' "$R3" 2>/dev/null | awk '{print $NF}')
if [ "${loss:-x}" = "1" ]; then
  echo "PASS  loss pattern counted the real incident and not the ticket"
else
  echo "FAIL  loss or recovery = ${loss:-<none>}, want 1"; fail=1
fi

# A marker inside a multi-line command must not be counted as the agent saying it.
# The prose filter tags tool calls with a TOOL prefix; if the command is not flattened
# first, only its opening line carries that tag and everything after it — the body of
# a heredoc, a PR description — reads as conversation. That is the normal shape for a
# rule about PR bodies, and the single-line cases the earlier tests used all passed.
P4="$WORK/home4/projects/proj"; mkdir -p "$P4"
python3 - "$P4/e.jsonl" <<'PYEOF'
import json, sys
cmd = "gh pr create --body \"$(cat <<EOF\n## MARKER-XYZ\n\nbody text\nEOF\n)\""
rows = [
  {"type": "assistant", "timestamp": "2026-08-10T10:00:00Z",
   "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": cmd}}]}},
  {"type": "user", "timestamp": "2026-08-10T10:01:00Z",
   "message": {"content": [{"type": "text", "text": "ok"}]}},
]
open(sys.argv[1], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PYEOF

printf 'firing\tmarker\tMARKER-XYZ\n' > "$WORK/p4.tsv"
cd "$WORK" && "$HERE/rule-firing-report.sh" --since 2026-08-01 --home "$WORK/home4" \
  --patterns "$WORK/p4.tsv" --out "$WORK/runs4" >/dev/null 2>&1
R4="$(ls -1dt "$WORK/runs4"/*/ 2>/dev/null | head -1)report.txt"
mk=$(grep -E '^marker' "$R4" 2>/dev/null | awk '{print $2}')
if [ "${mk:-x}" = "0" ]; then
  echo "PASS  marker inside a multi-line command scored zero prose hits"
else
  echo "FAIL  marker prose count = ${mk:-<none>}, want 0 (the heredoc body leaked)"; fail=1
fi

exit $fail
