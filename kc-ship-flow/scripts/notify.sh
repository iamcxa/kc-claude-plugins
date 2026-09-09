#!/usr/bin/env bash
# Idempotent UAT-ready ping. Usage: notify.sh <channel> <batch-id> <doc-path> --dry-run --state-dir <dir>
#
# One marker file per (batch id, state dir) claims a dry-run send; a second
# dry-run call for the same batch id and state dir finds that marker and
# skips. The marker records whether it was a dry run. This script has no
# real-send path -- a real Slack call is the First Officer's own action, not
# this script's -- so a non-dry-run call that finds a dry-run-only marker
# refuses instead of treating that marker as proof a real message was sent.
# The `mkdir` lock below is the enforcement point for "one marker write per
# batch id": two racing dry-run calls cannot both win the mkdir.
set -euo pipefail
ts() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
die() { echo "$(ts) notify: $*" >&2; exit 2; }

[ "$#" -ge 3 ] || die "usage: notify.sh <channel> <batch-id> <doc-path> --dry-run --state-dir <dir>"
channel=$1; batch_id=$2; doc_path=$3; shift 3
dry_run=0; state_dir=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) dry_run=1 ;;
    --state-dir) state_dir=$2; shift ;;
    *) die "unknown flag $1" ;;
  esac
  shift
done
[ -n "$state_dir" ] || die "--state-dir is required"
[ -f "$doc_path" ] || die "doc-path not found: $doc_path"

mkdir -p "$state_dir"
message_id="msg-$(printf '%s' "$batch_id" | sha256sum | cut -c1-12)"
marker="$state_dir/sent-$batch_id.json"
lock_dir="$state_dir/sent-$batch_id.lock"

if [ -f "$marker" ]; then
  existing_id=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['message_id'])" "$marker")
  existing_dry_run=$(python3 -c "import json,sys; print('1' if json.load(open(sys.argv[1])).get('dry_run') else '0')" "$marker")
  if [ "$dry_run" -eq 0 ] && [ "$existing_dry_run" -eq 1 ]; then
    die "refusing: existing marker for batch=$batch_id was dry_run; no real-send path exists to fulfill a non-dry-run call"
  fi
  echo "$(ts) notify: DRY-RUN skip (already sent) batch=$batch_id message_id=$existing_id"
  exit 0
fi

[ "$dry_run" -eq 1 ] || die "--dry-run is required; this script has no real-send path"

if ! mkdir "$lock_dir" 2>/dev/null; then
  die "concurrent notify in progress for batch=$batch_id"
fi
trap 'rmdir "$lock_dir" 2>/dev/null || true' EXIT

if [ -f "$marker" ]; then
  existing_id=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['message_id'])" "$marker")
  echo "$(ts) notify: DRY-RUN skip (already sent) batch=$batch_id message_id=$existing_id"
  exit 0
fi

message_file="$state_dir/message-$batch_id.md"
{
  echo "UAT ready: batch $batch_id"
  echo "Document: $doc_path"
} > "$message_file"

python3 - "$marker" "$batch_id" "$channel" "$message_id" "$doc_path" "$message_file" <<'PY'
import json, sys, datetime
marker, batch_id, channel, message_id, doc_path, message_file = sys.argv[1:7]
json.dump({
    "batch_id": batch_id,
    "channel": channel,
    "message_id": message_id,
    "doc_path": doc_path,
    "message_file": message_file,
    "dry_run": True,
    "sent_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}, open(marker, "w"), indent=2)
PY

echo "$(ts) notify: DRY-RUN sent batch=$batch_id channel=$channel message_id=$message_id doc=$doc_path"
