#!/usr/bin/env bash
# Usage: watch.sh <sprint> [--once] [--workflow-dir DIR] [--state-dir DIR] [--stage STAGE]
# Output: one line per task, "<slug> <exit>": gate-prepared | pending | quota | question | stopped.
# `spacedock status --json` does not expose the nested gates block, so gate state is read
# from the entity frontmatter YAML directly. Transcript tail read via `conductor sql`, never
# `session message --after` (see docs/ship/runbooks/conductor-cloud.md).
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
repo_root=$(cd "$here/../.." && pwd)
contract_file="$here/../pins/conductor-cli.contract"

die() { echo "$1" >&2; exit "${2:-1}"; }

sprint=""
ONCE=0
workflow_dir="$repo_root/docs/dev"
state_dir="$repo_root/docs/ship/.spacedock-state"
stage="validation"

while [ $# -gt 0 ]; do
  case "$1" in
    --once) ONCE=1 ;;
    --workflow-dir) workflow_dir=$2; shift ;;
    --state-dir) state_dir=$2; shift ;;
    --stage) stage=$2; shift ;;
    -*) die "unknown flag $1" 2 ;;
    *) [ -z "$sprint" ] || die "unexpected argument $1" 2; sprint=$1 ;;
  esac
  shift
done
[ -n "$sprint" ] || die "usage: watch.sh <sprint> [--once] [--workflow-dir DIR] [--state-dir DIR]" 2

# contract_file: one argv shape per line; --flags checked against live --help output,
# the remaining command tokens checked as a literal substring.
check_contract() {
  [ -f "$contract_file" ] || die "conductor cli contract missing: $contract_file" 2
  local version help_text line cmd tok ok missing
  version=$(conductor --version 2>&1) || die "conductor unavailable: $version" 2
  help_text=$(conductor --help 2>&1) || die "conductor unavailable: $help_text" 2
  missing=""
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    cmd=""
    ok=1
    for tok in $line; do
      case "$tok" in
        --*)
          case "$help_text" in
            *"$tok"*) : ;;
            *) ok=0 ;;
          esac
          ;;
        *)
          cmd="${cmd:+$cmd }$tok"
          ;;
      esac
    done
    case "$help_text" in
      *"$cmd"*) : ;;
      *) ok=0 ;;
    esac
    if [ "$ok" != 1 ]; then
      missing="$cmd"
      break
    fi
  done < "$contract_file"
  if [ -n "$missing" ]; then
    die "conductor cli used-surface changed: missing shape '$missing' (re-check $contract_file against \`conductor --help\`)" 5
  fi
  echo "conductor $version: used surface unchanged"
}
check_contract

conductor auth whoami >/dev/null 2>&1 || die "conductor unavailable" 2
conductor workspace list --limit 1 >/dev/null 2>&1 || die "conductor unavailable: workspace list probe failed" 2
conductor --json sql "SELECT 1" >/dev/null 2>&1 || die "conductor unavailable: sql probe failed" 2

fence_file="$state_dir/_ship_fence/$sprint.json"
[ -f "$fence_file" ] || die "no fence records for sprint=$sprint: $fence_file" 2

poll_state_dir="$state_dir/.ship-watch-scratch"
mkdir -p "$poll_state_dir"
poll_state_file="$poll_state_dir/$sprint.json"
[ -f "$poll_state_file" ] || echo '{}' > "$poll_state_file"

idle_streak_get() {
  python3 -c "
import json, sys
path, slug = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(path))
except (OSError, ValueError):
    d = {}
print(int((d.get(slug) or {}).get('idle_streak') or 0))
" "$poll_state_file" "$1"
}

idle_streak_set() {
  python3 -c "
import json, sys
path, slug, value = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    d = json.load(open(path))
except (OSError, ValueError):
    d = {}
d[slug] = {'idle_streak': int(value)}
json.dump(d, open(path, 'w'), indent=1, sort_keys=True)
" "$poll_state_file" "$1" "$2"
}

gate_status() {
  # prints "prepared" or "not-prepared"; entity missing/unparseable counts as not-prepared.
  python3 -c "
import sys
import yaml

path, stage = sys.argv[1], sys.argv[2]
try:
    text = open(path, encoding='utf-8').read()
except OSError:
    print('not-prepared')
    raise SystemExit
if not text.startswith('---\n'):
    print('not-prepared')
    raise SystemExit
_, fm, _rest = text.split('---\n', 2)
data = yaml.safe_load(fm) or {}
if data.get('status') != stage:
    print('not-prepared')
    raise SystemExit
records = ((data.get('gates') or {}).get('records')) or []
for rec in records:
    if rec.get('stage') == stage:
        attempts = rec.get('attempts') or []
        if attempts and 'resolution' not in attempts[-1]:
            print('prepared')
            raise SystemExit
print('not-prepared')
" "$1" "$2"
}

entity_path_for() {
  local slug="$1" flat folder
  flat="$workflow_dir/.spacedock-state/$slug.md"
  if [ -f "$flat" ]; then
    printf '%s' "$flat"
    return
  fi
  folder="$workflow_dir/.spacedock-state/$slug/index.md"
  printf '%s' "$folder"
}

workspace_status() {
  local workspace_id="$1"
  conductor --json workspace status "$workspace_id" 2>/dev/null | python3 -c "
import json, sys
try:
    print(json.load(sys.stdin).get('status', ''))
except ValueError:
    print('')
"
}

transcript_exit() {
  # prints quota|question|stopped for one session id's transcript tail.
  local session_id="$1" escaped
  escaped="${session_id//\'/\'\'}"
  conductor --json sql "SELECT transcript FROM session_transcripts_view WHERE session_id = '${escaped}'" 2>/dev/null | python3 -c "
import json
import re
import sys

try:
    d = json.load(sys.stdin)
except ValueError:
    d = {}
rows = d.get('rows') or []
transcript = rows[0].get('transcript', '') if rows else ''

blocks = re.split(r'(?m)^## Assistant\$', transcript)
last_block = blocks[-1] if blocks else ''

# 'usage limit reached' is an unverified guess at a second phrasing of the same banner.
if re.search(r'hit your session limit|usage limit reached', last_block, re.IGNORECASE):
    print('quota')
    raise SystemExit

lines = [line for line in last_block.splitlines() if line.strip()]
last_line = lines[-1].strip() if lines else ''
question_line = re.compile(r'^(Q:|Question:|Decision:|Could you)', re.IGNORECASE)
is_question = last_line.endswith('?') or any(question_line.match(l.strip()) for l in lines)
print('question' if is_question else 'stopped')
"
}

slugs=$(python3 -c '
import json, sys
d = json.load(open(sys.argv[1]))
for k in sorted(d):
    print(k)
' "$fence_file")

poll_once() {
  while IFS= read -r slug; do
    [ -n "$slug" ] || continue
    entity_path=$(entity_path_for "$slug")
    gs=$(gate_status "$entity_path" "$stage")
    if [ "$gs" = prepared ]; then
      echo "$slug gate-prepared"
      idle_streak_set "$slug" 0
      continue
    fi
    ws_sess=$(python3 -c '
import json, sys
path, slug = sys.argv[1], sys.argv[2]
d = json.load(open(path))
rec = d.get(slug) or {}
print((rec.get("workspace") or "") + "\t" + (rec.get("session") or ""))
' "$fence_file" "$slug")
    workspace="${ws_sess%%$'\t'*}"
    session="${ws_sess#*$'\t'}"
    if [ -z "$workspace" ] && [ -z "$session" ]; then
      echo "$slug stopped"
      idle_streak_set "$slug" 0
      continue
    fi
    if [ -n "$workspace" ]; then
      wstatus=$(workspace_status "$workspace")
      case "$wstatus" in
        *[Ii]nitializ*)
          echo "$slug pending"
          idle_streak_set "$slug" 0
          continue
          ;;
      esac
    fi
    if [ -z "$session" ]; then
      echo "$slug pending"
      idle_streak_set "$slug" 0
      continue
    fi
    sstatus=$(conductor --json session status "$session" 2>/dev/null | python3 -c "
import json, sys
try:
    print(json.load(sys.stdin).get('status', ''))
except ValueError:
    print('')
")
    if [ "$sstatus" != idle ]; then
      idle_streak_set "$slug" 0
      continue
    fi
    verdict=$(transcript_exit "$session")
    case "$verdict" in
      quota|question)
        echo "$slug $verdict"
        idle_streak_set "$slug" 0
        continue
        ;;
    esac
    streak=$(idle_streak_get "$slug")
    streak=$((streak + 1))
    idle_streak_set "$slug" "$streak"
    if [ "$streak" -ge 2 ]; then
      echo "$slug stopped"
    fi
  done <<< "$slugs"
}

if [ "$ONCE" = 1 ]; then
  poll_once
else
  while true; do
    poll_once
    sleep "${SHIP_WATCH_POLL_S:-30}"
  done
fi
