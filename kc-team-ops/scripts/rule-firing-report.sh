#!/usr/bin/env bash
# Measure two numbers per rule: how often the user repaired your output (friction),
# and how often the rule actually fired (firing). A rule with high friction and low
# firing is not a missing rule — it is a rule with no trigger.
#
# Claude Code session logs only. Codex/other harnesses are out of scope.
set -uo pipefail

SINCE="" ; HOME_DIR="${HOME}/.claude" ; PATTERNS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --since)    SINCE="$2"; shift 2 ;;
    --home)     HOME_DIR="$2"; shift 2 ;;
    --patterns) PATTERNS="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,9p' "$0"
      echo
      echo "Usage: $0 --since YYYY-MM-DD [--home ~/.claude] [--patterns FILE]"
      echo "  --patterns  TSV: kind<TAB>label<TAB>regex   kind = friction|firing"
      exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
[ -n "$SINCE" ] || { echo "--since YYYY-MM-DD is required" >&2; exit 2; }
command -v jq >/dev/null || { echo "jq not found" >&2; exit 2; }

PROJ="$HOME_DIR/projects"
[ -d "$PROJ" ] || { echo "no session logs at $PROJ" >&2; exit 2; }

WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT

# Main-session transcripts only. Subagent logs are the agent talking to itself.
find "$PROJ" -maxdepth 2 -name '*.jsonl' -newermt "$SINCE" 2>/dev/null \
  | grep -v '/subagents/' > "$WORK/sessions.txt"
SESSIONS=$(wc -l < "$WORK/sessions.txt" | tr -d ' ')
[ "$SESSIONS" -gt 0 ] || { echo "no sessions since $SINCE" >&2; exit 1; }

# find selects files by mtime; a long-lived session file also holds turns from
# before --since, so each turn is filtered on its own timestamp as well.
# Full timestamps, and no `sort -u`: the user really does send the same sentence
# twice, and collapsing those understates how often they had to repeat it.
while IFS= read -r f; do
  proj=$(basename "$(dirname "$f")")
  jq -r --arg P "$proj" --arg SINCE "$SINCE" '
    select(.type=="user") | select((.isMeta // false) | not)
    | select((.timestamp // "") >= $SINCE)
    | (.message.content) as $c
    | (if ($c|type)=="string" then $c
       elif ($c|type)=="array" then ([$c[] | select(.type=="text") | .text] | join("\n"))
       else "" end) as $t
    | select(($t|length) > 0)
    | "\(.timestamp)\t\($P)\t\($t | gsub("\n"; " "))"
  ' "$f" 2>/dev/null
done < "$WORK/sessions.txt" | sort > "$WORK/all-user.txt"

# Drop turns the user did not type: tool plumbing, slash-command echoes, and the
# dispatch prompts the agent wrote for its own workers. Counting those as user
# corrections inflates every friction number.
# The dispatch-prompt filter is deliberately narrow: an earlier version dropped
# anything opening with "You are", which also deletes a real correction like
# "You are still ignoring the comment rule".
grep -avE '<system-reminder>|<task-notification>|<system_instruction>|<command-name>|<local-command-stdout>|tool_use_id|Review this change for security vulnerabilities|^[^\t]*\t[^\t]*\t(You are (a|an|the|Claude|Codex|Gemini|GPT)|Respond with exactly)' \
  "$WORK/all-user.txt" | grep -v $'\t-private-tmp-' > "$WORK/human.txt"

# Assistant prose AND tool calls. A rule whose only marker is "you must read
# file X" leaves no trace in prose, so counting text alone scores it zero.
while IFS= read -r f; do
  jq -r --arg SINCE "$SINCE" '
    select(.type=="assistant") | select((.timestamp // "") >= $SINCE)
    | (.message.content // [])[]
    | if .type=="text" then .text
      elif .type=="tool_use" then
        "TOOL \(.name) \(.input.file_path // .input.command // .input.pattern // "")"
      else empty end
  ' "$f" 2>/dev/null
done < "$WORK/sessions.txt" > "$WORK/assistant.txt"

HUMAN=$(wc -l < "$WORK/human.txt" | tr -d ' ')
ASST=$(wc -l < "$WORK/assistant.txt" | tr -d ' ')

if [ -z "$PATTERNS" ]; then
  PATTERNS="$WORK/default.tsv"
  # Defaults are tuned for a bilingual zh/en user. Override with --patterns.
  cat > "$PATTERNS" <<'TSV'
friction	necessity challenge	會怎樣|必要的嗎|需要嗎|還需要|價值在哪|why do we need|is this necessary
friction	rephrase demand	換句話說|太長|簡單一點|簡報|精簡|rephrase|too long
friction	undefined term	是什麼|什麼意思|是指什麼|哪來的|what is this|what do you mean
friction	status pull	還剩|可以收|下一步|回報|現況|what.s left|status\?
friction	prior-art miss	上游|重複|既有|沒看|already exists|upstream
friction	size complaint	[0-9]+ ?loc|註解|膨脹|冗余|冗餘|多餘|bloat|too many comments
TSV
fi

# -e guards a pattern that starts with `-`, which grep would otherwise read as a
# flag. grep exits 1 on no match, hence the `|| true`.
#
# Two counters, because the two halves ask different questions. Friction asks how
# many turns the user spent repairing you, so it counts turns; counting occurrences
# there once produced a 122%-of-turns row. Firing asks how many times a marker was
# emitted, so it counts occurrences and sees both markers on a shared line.
count_turns() { local n; n=$(grep -ciE -e "$2" "$1" 2>/dev/null) || true; echo "$(( ${n:-0} ))"; }
count_hits()  { local n; n=$(grep -oiE -e "$2" "$1" 2>/dev/null | wc -l) || true; echo "$(( ${n:-0} ))"; }

printf '\n%s\n' "=== volume since $SINCE ==="
printf '%-26s %s\n' "sessions"            "$SESSIONS"
printf '%-26s %s\n' "human turns"         "$HUMAN"
printf '%-26s %s\n' "assistant text lines" "$ASST"
printf '%-26s %s\n' "projects touched"    "$(cut -f2 "$WORK/human.txt" | sort -u | wc -l | tr -d ' ')"

printf '\n%s\n' "=== friction: how often the user repaired you ==="
printf '%-26s %6s  %s\n' "CATEGORY" "COUNT" "SHARE OF HUMAN TURNS"
while IFS=$'\t' read -r kind label re; do
  [ "$kind" = "friction" ] || continue
  n=$(count_turns "$WORK/human.txt" "$re")
  printf '%-26s %6s  %s%%\n' "$label" "$n" "$(( HUMAN ? n * 100 / HUMAN : 0 ))"
done < "$PATTERNS"

printf '\n%s\n' "=== firing: how often the rule actually ran ==="
FIRED=0
while IFS=$'\t' read -r kind label re; do
  [ "$kind" = "firing" ] || continue
  FIRED=1
  printf '%-26s %6s\n' "$label" "$(count_hits "$WORK/assistant.txt" "$re")"
done < "$PATTERNS"
[ "$FIRED" = 1 ] || printf '%s\n' \
  "(none declared — add 'firing<TAB>label<TAB>regex' rows for each rule with an observable marker)"
printf '%s\n' "note: a marker QUOTED without being obeyed still counts here — an agent" \
  "      reading a rule aloud looks identical to one following it. Sample the hits."

printf '\n%s\n' "=== evidence ==="
cp "$WORK/human.txt" "./rule-review-human-turns.tsv"
printf 'human turns written to ./rule-review-human-turns.tsv — read the hits before trusting any count\n\n'
