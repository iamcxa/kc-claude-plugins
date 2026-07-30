#!/usr/bin/env bash

# Persistent Teams runner trace lifecycle with run identity and idempotent delivery.
# Compatible with Bash 3.2 shipped by macOS.

set -u

usage() {
  printf '%s\n' \
    'Usage:' \
    '  team-trace-lifecycle.sh begin --report-dir <absolute> --flow-run-id <id> --session <id> [owned-runtime options]' \
    '  team-trace-lifecycle.sh finalize --report-dir <absolute> --flow-run-id <id> --session <id> --flow-verdict <verdict> [owned-runtime options]' \
    '' \
    'Owned-runtime options (provide all or none):' \
    '  --browser-runtime <absolute-executable>' \
    '  --browser-run-id <id>' \
    '  --app <id>'
}

[ "$#" -ge 1 ] || { usage >&2; exit 64; }
command_name=$1
shift

report_dir=
flow_run_id=
session_name=
flow_verdict=
browser_runtime=
browser_run_id=
browser_app=

while [ "$#" -gt 0 ]; do
  case "$1" in
    --report-dir)
      [ "$#" -ge 2 ] || { usage >&2; exit 64; }
      report_dir=$2
      shift 2
      ;;
    --flow-run-id)
      [ "$#" -ge 2 ] || { usage >&2; exit 64; }
      flow_run_id=$2
      shift 2
      ;;
    --session)
      [ "$#" -ge 2 ] || { usage >&2; exit 64; }
      session_name=$2
      shift 2
      ;;
    --flow-verdict)
      [ "$#" -ge 2 ] || { usage >&2; exit 64; }
      flow_verdict=$2
      shift 2
      ;;
    --browser-runtime)
      [ "$#" -ge 2 ] || { usage >&2; exit 64; }
      browser_runtime=$2
      shift 2
      ;;
    --browser-run-id)
      [ "$#" -ge 2 ] || { usage >&2; exit 64; }
      browser_run_id=$2
      shift 2
      ;;
    --app)
      [ "$#" -ge 2 ] || { usage >&2; exit 64; }
      browser_app=$2
      shift 2
      ;;
    *)
      printf 'Unknown lifecycle argument: %s\n' "$1" >&2
      exit 64
      ;;
  esac
done

case "$command_name" in
  begin|finalize) ;;
  *) usage >&2; exit 64 ;;
esac

if [ -z "$report_dir" ] || [ -z "$flow_run_id" ] || [ -z "$session_name" ]; then
  usage >&2
  exit 64
fi
case "$report_dir" in
  /*) ;;
  *) printf 'Report directory must be absolute: %s\n' "$report_dir" >&2; exit 64 ;;
esac
case "$report_dir" in
  *'
'*|*''*) printf '%s\n' 'Report directory must not contain CR or LF' >&2; exit 64 ;;
esac

script_dir=$(CDPATH='' cd -- "$(dirname "$0")" && pwd)
identifier_validator="$script_dir/validate-trace-identifiers.sh"
finalizer="$script_dir/finalize-trace.sh"
trace_contract_cli="$script_dir/../bin/e2e-trace-contract.js"
agent_browser_bin=${AGENT_BROWSER_BIN:-agent-browser}

"$identifier_validator" "$flow_run_id" || exit $?
"$identifier_validator" "$session_name" || exit $?

owned_runtime=false
if [ -n "$browser_runtime" ] || [ -n "$browser_run_id" ] || [ -n "$browser_app" ]; then
  if [ -z "$browser_runtime" ] || [ -z "$browser_run_id" ] || [ -z "$browser_app" ]; then
    printf '%s\n' '--browser-runtime, --browser-run-id, and --app must be provided together' >&2
    exit 64
  fi
  case "$browser_runtime" in
    /*) ;;
    *) printf 'Browser runtime path must be absolute: %s\n' "$browser_runtime" >&2; exit 64 ;;
  esac
  if [ ! -f "$browser_runtime" ] || [ ! -x "$browser_runtime" ]; then
    printf 'Browser runtime must be an executable regular file: %s\n' "$browser_runtime" >&2
    exit 64
  fi
  case "$browser_run_id" in
    ''|[!a-z0-9]*|*[!a-z0-9-]*)
      printf 'Unsafe browser run identity: %s\n' "$browser_run_id" >&2
      exit 64
      ;;
  esac
  if [ "${#browser_run_id}" -lt 3 ] || [ "${#browser_run_id}" -gt 128 ]; then
    printf 'Browser run identity must be 3-128 bytes: %s\n' "$browser_run_id" >&2
    exit 64
  fi
  "$identifier_validator" "$browser_app" || exit $?
  if [ "$session_name" != "$browser_app" ]; then
    printf 'Legacy session and owned browser app must match: %s != %s\n' \
      "$session_name" "$browser_app" >&2
    exit 64
  fi
  owned_runtime=true
fi

run_browser() {
  if [ "$owned_runtime" = true ]; then
    "$browser_runtime" --run-id "$browser_run_id" --app "$browser_app" "$@"
  else
    "$agent_browser_bin" --session "$session_name" "$@"
  fi
}

run_finalizer() {
  finalizer_verdict=$1
  if [ "$owned_runtime" = true ]; then
    "$finalizer" \
      --session "$session_name" \
      --browser-runtime "$browser_runtime" \
      --browser-run-id "$browser_run_id" \
      --app "$browser_app" \
      --trace-path "$trace_path" \
      --flow-verdict "$finalizer_verdict" \
      --trace-producer "$trace_producer" \
      --trace-producer-version "$trace_producer_version" \
      --trace-format "$trace_format" \
      --result-file "$result_file"
  else
    "$finalizer" \
      --session "$session_name" \
      --trace-path "$trace_path" \
      --flow-verdict "$finalizer_verdict" \
      --trace-producer "$trace_producer" \
      --trace-producer-version "$trace_producer_version" \
      --trace-format "$trace_format" \
      --result-file "$result_file"
  fi
}

run_dir="$report_dir/runs/$flow_run_id"
trace_path=
trace_producer=
trace_producer_version=
trace_format=
trace_extension=
result_file="$run_dir/trace-finalization.env"
state_file="$report_dir/.trace-lifecycle.env"

regular_destination_or_absent() {
  destination=$1
  [ ! -L "$destination" ] &&
    { [ ! -e "$destination" ] || [ -f "$destination" ]; }
}

atomic_replace() {
  replace_source=$1
  replace_destination=$2
  python3 - "$replace_source" "$replace_destination" <<'PY'
import os
import stat
import sys

source, destination = sys.argv[1:3]
if os.path.lexists(destination) and not stat.S_ISREG(os.lstat(destination).st_mode):
    raise SystemExit("destination is not a regular file")
os.replace(source, destination)
PY
}

read_state_field() {
  field_name=$1
  [ -f "$state_file" ] && [ ! -L "$state_file" ] && [ -r "$state_file" ] || return 1
  sed -n "s/^${field_name}=//p" "$state_file" | head -n 1
}

load_trace_state() {
  trace_producer=$(read_state_field trace_producer) || return 1
  trace_producer_version=$(read_state_field trace_producer_version) || return 1
  trace_format=$(read_state_field trace_format) || return 1
  trace_path=$(read_state_field trace_path) || return 1
  case "$trace_format" in
    chrome-trace-json) trace_extension=.json ;;
    playwright-trace-zip) trace_extension=.zip ;;
    *) return 1 ;;
  esac
  [ "$trace_producer" = agent-browser ] &&
    [ -n "$trace_producer_version" ] &&
    [ "$trace_path" = "$run_dir/trace$trace_extension" ]
}

detect_trace_contract() {
  [ -f "$trace_contract_cli" ] || {
    printf 'Trace capability detector is unavailable: %s\n' "$trace_contract_cli" >&2
    return 1
  }
  resolved_agent_browser=$(command -v "$agent_browser_bin" 2>/dev/null || true)
  case "$resolved_agent_browser" in
    /*) ;;
    *)
      printf 'agent-browser executable could not be resolved: %s\n' "$agent_browser_bin" >&2
      return 1
      ;;
  esac
  contract_file="$run_dir/trace-contract.env"
  contract_tmp=$(mktemp "$run_dir/.trace-contract.tmp.XXXXXX") || return 1
  if ! node "$trace_contract_cli" \
      --agent-browser "$resolved_agent_browser" \
      --output env > "$contract_tmp"; then
    rm -f "$contract_tmp"
    return 1
  fi
  if ! atomic_replace "$contract_tmp" "$contract_file"; then
    rm -f "$contract_tmp"
    return 1
  fi
  trace_producer=$(sed -n 's/^trace_producer=//p' "$contract_file")
  trace_producer_version=$(sed -n 's/^trace_producer_version=//p' "$contract_file")
  trace_format=$(sed -n 's/^trace_format=//p' "$contract_file")
  trace_extension=$(sed -n 's/^trace_extension=//p' "$contract_file")
  case "$trace_format:$trace_extension" in
    chrome-trace-json:.json|playwright-trace-zip:.zip) ;;
    *)
      printf 'Trace capability detector returned an invalid format contract\n' >&2
      return 1
      ;;
  esac
  [ "$trace_producer" = agent-browser ] || return 1
  case "$trace_producer_version" in
    ''|*[!A-Za-z0-9._+-]*) return 1 ;;
  esac
  trace_path="$run_dir/trace$trace_extension"
}

write_state() {
  state_status=$1
  regular_destination_or_absent "$state_file" || return 1
  state_tmp=$(mktemp "$report_dir/.trace-lifecycle.tmp.XXXXXX") || return 1
  if ! {
    printf 'status=%s\n' "$state_status"
    printf 'flow_run_id=%s\n' "$flow_run_id"
    printf 'session=%s\n' "$session_name"
    printf 'browser_run_id=%s\n' "$browser_run_id"
    printf 'browser_app=%s\n' "$browser_app"
    printf 'trace_producer=%s\n' "$trace_producer"
    printf 'trace_producer_version=%s\n' "$trace_producer_version"
    printf 'trace_format=%s\n' "$trace_format"
    printf 'trace_path=%s\n' "$trace_path"
  } > "$state_tmp"; then
    rm -f "$state_tmp"
    return 1
  fi
  if ! atomic_replace "$state_tmp" "$state_file"; then
    rm -f "$state_tmp"
    return 1
  fi
  [ "$(read_state_field status)" = "$state_status" ] &&
    [ "$(read_state_field flow_run_id)" = "$flow_run_id" ] &&
    [ "$(read_state_field session)" = "$session_name" ] &&
    [ "$(read_state_field browser_run_id)" = "$browser_run_id" ] &&
    [ "$(read_state_field browser_app)" = "$browser_app" ] &&
    [ "$(read_state_field trace_producer)" = "$trace_producer" ] &&
    [ "$(read_state_field trace_producer_version)" = "$trace_producer_version" ] &&
    [ "$(read_state_field trace_format)" = "$trace_format" ] &&
    [ "$(read_state_field trace_path)" = "$trace_path" ]
}

print_begin_result() {
  begin_status=$1
  printf 'flow_run_id=%s\n' "$flow_run_id"
  printf 'begin_status=%s\n' "$begin_status"
  printf 'trace_producer=%s\n' "$trace_producer"
  printf 'trace_producer_version=%s\n' "$trace_producer_version"
  printf 'trace_format=%s\n' "$trace_format"
  printf 'trace_path=%s\n' "$trace_path"
  printf 'trace_finalization_result_path=%s\n' "$result_file"
}

mkdir -p "$report_dir" || exit 70
if ! regular_destination_or_absent "$state_file"; then
  printf 'Lifecycle state destination must be absent or a regular file: %s\n' "$state_file" >&2
  exit 64
fi
if ! regular_destination_or_absent "$result_file"; then
  printf 'Lifecycle result destination must be absent or a regular file: %s\n' "$result_file" >&2
  exit 64
fi
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' 'python3 is required before starting a Teams trace lifecycle' >&2
  exit 69
fi

if [ "$command_name" = begin ]; then
  current_status=$(read_state_field status 2>/dev/null || true)
  current_flow_run_id=$(read_state_field flow_run_id 2>/dev/null || true)
  current_session=$(read_state_field session 2>/dev/null || true)
  current_browser_run_id=$(read_state_field browser_run_id 2>/dev/null || true)
  current_browser_app=$(read_state_field browser_app 2>/dev/null || true)
  if [ -f "$result_file" ]; then
    if [ "$current_flow_run_id" != "$flow_run_id" ] ||
       [ "$current_session" != "$session_name" ] ||
       [ "$current_browser_run_id" != "$browser_run_id" ] ||
       [ "$current_browser_app" != "$browser_app" ]; then
      printf 'Finalized trace ownership does not match flow run: %s\n' "$flow_run_id" >&2
      exit 66
    fi
    if ! load_trace_state; then
      printf 'Finalized trace format contract is invalid for flow run: %s\n' "$flow_run_id" >&2
      exit 66
    fi
    print_begin_result already_finalized
    exit 0
  fi

  if [ "$current_status" = active ]; then
    if [ "$current_flow_run_id" = "$flow_run_id" ] &&
       [ "$current_session" = "$session_name" ] &&
       [ "$current_browser_run_id" = "$browser_run_id" ] &&
       [ "$current_browser_app" = "$browser_app" ]; then
      if ! load_trace_state; then
        printf 'Active trace format contract is invalid for flow run: %s\n' "$flow_run_id" >&2
        exit 66
      fi
      print_begin_result replayed
      exit 0
    fi
    printf 'Another flow run is still active: %s\n' "$current_flow_run_id" >&2
    exit 66
  fi

  mkdir -p "$run_dir" || exit 70
  if ! detect_trace_contract; then
    printf 'Trace capability detection failed before capture for flow run %s\n' "$flow_run_id" >&2
    exit 72
  fi
  run_browser trace start
  start_result=$?
  if [ "$start_result" -ne 0 ]; then
    printf 'Trace start failed for flow run %s (exit %s)\n' "$flow_run_id" "$start_result" >&2
    exit 71
  fi
  if ! write_state active; then
    printf 'Cannot persist active trace lifecycle state; stopping trace\n' >&2
    run_finalizer FAIL >/dev/null 2>&1 || true
    exit 70
  fi
  print_begin_result started
  exit 0
fi

current_status=$(read_state_field status 2>/dev/null || true)
current_flow_run_id=$(read_state_field flow_run_id 2>/dev/null || true)
current_session=$(read_state_field session 2>/dev/null || true)
current_browser_run_id=$(read_state_field browser_run_id 2>/dev/null || true)
current_browser_app=$(read_state_field browser_app 2>/dev/null || true)
if [ -f "$result_file" ]; then
  if [ "$current_flow_run_id" != "$flow_run_id" ] ||
     [ "$current_session" != "$session_name" ] ||
     [ "$current_browser_run_id" != "$browser_run_id" ] ||
     [ "$current_browser_app" != "$browser_app" ]; then
    printf 'Finalized trace ownership does not match flow run: %s\n' "$flow_run_id" >&2
    exit 66
  fi
  if ! load_trace_state; then
    printf 'Finalized trace format contract is invalid for flow run: %s\n' "$flow_run_id" >&2
    exit 66
  fi
  if ! cat "$result_file"; then
    printf 'Cannot read trace finalization result: %s\n' "$result_file" >&2
    exit 70
  fi
  exit 0
fi

if [ "$current_status" != active ] ||
   [ "$current_flow_run_id" != "$flow_run_id" ] ||
   [ "$current_session" != "$session_name" ] ||
   [ "$current_browser_run_id" != "$browser_run_id" ] ||
   [ "$current_browser_app" != "$browser_app" ]; then
  printf 'Flow run is not the active trace: %s\n' "$flow_run_id" >&2
  exit 66
fi
if ! load_trace_state; then
  printf 'Active trace format contract is invalid for flow run: %s\n' "$flow_run_id" >&2
  exit 66
fi

case "$flow_verdict" in
  PASS|PARTIAL|FAIL) ;;
  *) printf 'Unsupported flow verdict: %s\n' "$flow_verdict" >&2; exit 64 ;;
esac

run_finalizer "$flow_verdict" >/dev/null
finalizer_result=$?

if [ ! -f "$result_file" ]; then
  printf 'Trace finalizer did not write its result: %s\n' "$result_file" >&2
  exit 70
fi

if ! write_state finalized; then
  printf 'Cannot persist finalized trace lifecycle state\n' >&2
  exit 70
fi
if ! cat "$result_file"; then
  printf 'Cannot read trace finalization result: %s\n' "$result_file" >&2
  exit 70
fi
exit "$finalizer_result"
