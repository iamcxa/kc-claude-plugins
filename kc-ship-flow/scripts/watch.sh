#!/usr/bin/env bash
# Poll every task dispatch.sh recorded for a sprint and print one exit per task.
# Usage: watch.sh <sprint> [--once] [--workflow-dir DIR] [--state-dir DIR] [--stage STAGE]
#
# Output: one line per task, "<slug> <exit>", where <exit> is one of
#   gate-prepared | quota | question | stopped
#
# Primary signal is the docs/dev state branch (a prepared gate at --stage, default
# "validation", read from the entity file's own gates record -- `spacedock status --json`
# does not expose the nested gates block, so this reads the frontmatter YAML directly).
# Secondary signal, only consulted once a task's session reports idle, is the transcript
# tail read through `conductor sql` (never `session message --after`; see
# docs/ship/runbooks/conductor-cloud.md). A task whose session is still running is left
# out of this poll's output -- there is nothing yet to report and a caller running this
# in a loop (omitting --once) will see it on the next pass.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
repo_root=$(cd "$here/../.." && pwd)
pin_file="$here/../pins/conductor-cli.txt"

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

[ -f "$pin_file" ] || die "conductor cli pin missing: $pin_file" 2
pinned_version=$(head -n1 "$pin_file")
installed_version=$(conductor --version 2>&1) || die "conductor unavailable: $installed_version" 2
if [ "$installed_version" != "$pinned_version" ]; then
  diff <(tail -n +2 "$pin_file") <(conductor --help 2>&1) || true
  die "conductor cli changed: read the diff, then re-pin" 5
fi

conductor auth whoami >/dev/null 2>&1 || die "conductor unavailable" 2

fence_file="$state_dir/_ship_fence/$sprint.json"
[ -f "$fence_file" ] || die "no fence records for sprint=$sprint: $fence_file" 2

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

# Verified real-transcript wording (2026-09-10, via conductor sql): 'You've hit your
# session limit · resets 9pm (Asia/Taipei)'. The 'usage limit' alternative is an
# unverified guess at another phrasing of the same product banner.
if re.search(r'hit your session limit|usage limit reached', transcript, re.IGNORECASE):
    print('quota')
    raise SystemExit

blocks = re.split(r'(?m)^## Assistant\$', transcript)
last_block = blocks[-1] if blocks else ''
lines = [line for line in last_block.splitlines() if line.strip()]
last_line = lines[-1].strip() if lines else ''
print('question' if last_line.endswith('?') else 'stopped')
"
}

slugs=$(python3 -c "
import json
d = json.load(open('$fence_file'))
for k in sorted(d):
    print(k)
")

poll_once() {
  while IFS= read -r slug; do
    [ -n "$slug" ] || continue
    entity_path="$workflow_dir/.spacedock-state/$slug.md"
    gs=$(gate_status "$entity_path" "$stage")
    if [ "$gs" = prepared ]; then
      echo "$slug gate-prepared"
      continue
    fi
    session=$(python3 -c "
import json
d = json.load(open('$fence_file'))
print((d.get('$slug') or {}).get('session') or '')
")
    if [ -z "$session" ]; then
      echo "$slug stopped"
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
      continue
    fi
    echo "$slug $(transcript_exit "$session")"
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
