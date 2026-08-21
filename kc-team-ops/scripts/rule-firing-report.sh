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

# Chronological user+assistant stream. An incident turn is unreadable without the
# assistant turn before it: "I fixed it myself" means one thing after silence and
# another after the agent offered to do it and stopped.
while IFS= read -r f; do
  jq -r --arg SINCE "$SINCE" '
    select(.type=="user" or .type=="assistant") | select((.timestamp // "") >= $SINCE)
    | . as $r | (.message.content) as $c
    | (if ($c|type)=="string" then $c
       elif ($c|type)=="array" then ([$c[] | select(.type=="text") | .text] | join(" "))
       else "" end) as $t
    | select(($t|length) > 0)
    | ($t | gsub("\n"; " ")) as $flat
    | "\(.timestamp)\t\($r.type)\t\($flat|length)\t\($flat[0:600])"
  ' "$f" 2>/dev/null
done < "$WORK/sessions.txt" | sort > "$WORK/stream.txt"

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
incident	cross-session relay	另外一個 ?agent|另一個 ?agent|另一個 session|平行 agent|其他 workspace|another session|the other agent
incident	user took it over	我(自己|先|去)?(做|改|弄|處理|修|部署|合)(好|完|了)|我已經(自己|先)|I fixed it|I did it myself|I went ahead and|I had to do it
incident	loss or recovery	救回|覆蓋掉|掃掉|had to recover|overwrote|clobber
codify	asked to make it a rule	以後(都|請|先|就)|寫回去|寫進.*claude|寫進規則|變成規則|下次(記得|不要)|記住這個|from now on|make (this|that) a rule
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

printf '\n%s\n' "=== incidents: work you did that the agent never offered ==="
printf '%-26s %6s\n' "CATEGORY" "TURNS"
INC=0
while IFS=$'\t' read -r kind label re; do
  [ "$kind" = "incident" ] || continue
  INC=1
  printf '%-26s %6s\n' "$label" "$(count_turns "$WORK/human.txt" "$re")"
done < "$PATTERNS"
[ "$INC" = 1 ] || printf '%s\n' "(none declared)"
if [ "$INC" = 1 ]; then
  : > ./rule-review-incidents.txt
  while IFS=$'\t' read -r kind label re; do
    case "$kind" in incident|codify) ;; *) continue ;; esac
    awk -F'\t' -v RE="$re" -v LABEL="$label" '
      $2=="assistant" { prev=$4 }
      $2=="user" && tolower($4) ~ tolower(RE) {
        print "--- " LABEL " @ " $1
        print "  BEFORE (agent): " (prev=="" ? "(nothing)" : substr(prev,1,300))
        print "  THEN  (user):   " substr($4,1,300)
        print ""
      }' "$WORK/stream.txt" >> ./rule-review-incidents.txt
  done < "$PATTERNS"
  printf 'matched incidents with the turn before them: ./rule-review-incidents.txt\n'
fi
printf '%s\n' "note: these are CANDIDATES, not counts. A blind spot leaves no friction — the" \
  "      user never corrected you, because you never gave them anything to correct." \
  "      Read every hit. Normal division of labour looks identical to a blind spot here."

printf '\n%s\n' "=== codification: rules you asked for ==="
while IFS=$'\t' read -r kind label re; do
  [ "$kind" = "codify" ] || continue
  printf '%-26s %6s\n' "$label" "$(count_turns "$WORK/human.txt" "$re")"
done < "$PATTERNS"
printf '%s\n' "Each one has two ways to fail: never written into the rule file, or written and" \
  "never firing. The second is harder to see and is why this audit usually gets started."

printf '\n%s\n' "=== coverage: what this pass cannot see ==="
awk -F'\t' '
  $2=="assistant" { prev=$3+0; next }
  $2=="user" && prev>0 {
    b = prev<500 ? "under 500" : prev<1500 ? "500-1500" : prev<3000 ? "1500-3000" : "3000+"
    n[b]++
    if ($4 ~ /換句話說|白話|太長|簡單一點|是什麼|什麼意思|沒看懂|看不懂|rephrase|what do you mean/) d[b]++
    prev=0
  }
  END {
    printf "%-22s%11s%10s%8s\n", "my previous message", "your turns", "decoding", "rate"
    split("under 500,500-1500,1500-3000,3000+", o, ",")
    for (i=1;i<=4;i++) { b=o[i]; if (n[b]) printf "%-22s%11d%10d%7d%%\n", b, n[b], d[b], 100*d[b]/n[b] }
  }' "$WORK/stream.txt"
printf '%s\n' \
  "Voiced friction is the only kind the columns above can count. When the user stops" \
  "correcting and starts adapting to you, nothing is said and nothing is matched. Length" \
  "is the one proxy that does not need the complaint to be spoken: if the decoding rate" \
  "climbs with your message length, assume the unspoken cost climbs with it too."

printf '\n%s\n' "=== evidence ==="
cp "$WORK/human.txt" "./rule-review-human-turns.tsv"
printf 'human turns written to ./rule-review-human-turns.tsv — read the hits before trusting any count\n\n'
