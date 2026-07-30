#!/usr/bin/env bash

# Bound agent-browser trace finalization and fail closed before trace analysis.
# Compatible with the Bash 3.2 shipped by macOS.

set -u

usage() {
  printf '%s\n' \
    'Usage: finalize-trace.sh --trace-path <absolute-path> --flow-verdict <verdict> [options]' \
    '' \
    'Options:' \
    '  --timeout <seconds>           Trace stop timeout (default: 60)' \
    '  --recovery-timeout <seconds>  Browser close timeout after stop failure (default: 15)' \
    '  --validation-timeout <seconds> Artifact validation timeout (default: 30)' \
    '  --result-file <path>          Result contract path (default: beside trace artifact)' \
    '  --trace-producer <name>       Producer identity from pre-capture detection' \
    '  --trace-producer-version <v>  Producer version from pre-capture detection' \
    '  --trace-format <format>       chrome-trace-json or playwright-trace-zip' \
    '  --session <name>              Named agent-browser session' \
    '  --browser-runtime <path>      Owned browser runtime executable' \
    '  --browser-run-id <id>         Owned browser run identity' \
    '  --app <id>                    Owned browser app/session identity' \
    '  --browser-receipt <path>      Owned browser receipt path' \
    '  --help                        Show this help'
}

trace_path=
flow_verdict=
stop_timeout=${E2E_TRACE_STOP_TIMEOUT:-60}
recovery_timeout=${E2E_TRACE_RECOVERY_TIMEOUT:-15}
validation_timeout=${E2E_TRACE_VALIDATION_TIMEOUT:-30}
result_file=
trace_producer=
trace_producer_version=
trace_format=
session_name=
browser_runtime=
browser_run_id=
browser_app=
browser_receipt=
agent_browser_bin=${AGENT_BROWSER_BIN:-agent-browser}
active_pid=
active_pgid=
case "$0" in
  */*) script_parent=${0%/*} ;;
  *) script_parent=. ;;
esac
script_dir=$(CDPATH='' cd -- "$script_parent" && pwd)
archive_validator=${E2E_TRACE_ARCHIVE_VALIDATOR:-"$script_dir/validate-trace-archive.py"}
chrome_validator=${E2E_CHROME_TRACE_VALIDATOR:-"$script_dir/validate-chrome-trace.py"}
identifier_validator="$script_dir/validate-trace-identifiers.sh"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --trace-path)
      [ "$#" -ge 2 ] || { printf 'Missing value for --trace-path\n' >&2; exit 64; }
      trace_path=$2
      shift 2
      ;;
    --flow-verdict)
      [ "$#" -ge 2 ] || { printf 'Missing value for --flow-verdict\n' >&2; exit 64; }
      flow_verdict=$2
      shift 2
      ;;
    --timeout)
      [ "$#" -ge 2 ] || { printf 'Missing value for --timeout\n' >&2; exit 64; }
      stop_timeout=$2
      shift 2
      ;;
    --recovery-timeout)
      [ "$#" -ge 2 ] || { printf 'Missing value for --recovery-timeout\n' >&2; exit 64; }
      recovery_timeout=$2
      shift 2
      ;;
    --validation-timeout)
      [ "$#" -ge 2 ] || { printf 'Missing value for --validation-timeout\n' >&2; exit 64; }
      validation_timeout=$2
      shift 2
      ;;
    --result-file)
      [ "$#" -ge 2 ] || { printf 'Missing value for --result-file\n' >&2; exit 64; }
      result_file=$2
      shift 2
      ;;
    --trace-producer)
      [ "$#" -ge 2 ] || { printf 'Missing value for --trace-producer\n' >&2; exit 64; }
      trace_producer=$2
      shift 2
      ;;
    --trace-producer-version)
      [ "$#" -ge 2 ] || { printf 'Missing value for --trace-producer-version\n' >&2; exit 64; }
      trace_producer_version=$2
      shift 2
      ;;
    --trace-format)
      [ "$#" -ge 2 ] || { printf 'Missing value for --trace-format\n' >&2; exit 64; }
      trace_format=$2
      shift 2
      ;;
    --session)
      [ "$#" -ge 2 ] || { printf 'Missing value for --session\n' >&2; exit 64; }
      session_name=$2
      shift 2
      ;;
    --browser-runtime)
      [ "$#" -ge 2 ] || { printf 'Missing value for --browser-runtime\n' >&2; exit 64; }
      browser_runtime=$2
      shift 2
      ;;
    --browser-run-id)
      [ "$#" -ge 2 ] || { printf 'Missing value for --browser-run-id\n' >&2; exit 64; }
      browser_run_id=$2
      shift 2
      ;;
    --app)
      [ "$#" -ge 2 ] || { printf 'Missing value for --app\n' >&2; exit 64; }
      browser_app=$2
      shift 2
      ;;
    --browser-receipt)
      [ "$#" -ge 2 ] || { printf 'Missing value for --browser-receipt\n' >&2; exit 64; }
      browser_receipt=$2
      shift 2
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 64
      ;;
  esac
done

if [ -z "$trace_path" ] || [ -z "$flow_verdict" ] ||
   [ -z "$trace_producer" ] || [ -z "$trace_producer_version" ] ||
   [ -z "$trace_format" ]; then
  printf '%s\n' \
    '--trace-path, --flow-verdict, --trace-producer, --trace-producer-version, and --trace-format are required' >&2
  usage >&2
  exit 64
fi

newline='
'
carriage_return=$(printf '\r')
reject_line_break() {
  input_name=$1
  input_value=$2
  case "$input_value" in
    *"$newline"*|*"$carriage_return"*)
      printf '%s must not contain CR or LF\n' "$input_name" >&2
      exit 64
      ;;
  esac
}

reject_line_break trace_path "$trace_path"
reject_line_break flow_verdict "$flow_verdict"
reject_line_break result_file "$result_file"
reject_line_break trace_producer "$trace_producer"
reject_line_break trace_producer_version "$trace_producer_version"
reject_line_break trace_format "$trace_format"
reject_line_break session "$session_name"
reject_line_break browser_runtime "$browser_runtime"
reject_line_break browser_run_id "$browser_run_id"
reject_line_break app "$browser_app"
reject_line_break browser_receipt "$browser_receipt"
reject_line_break validation_timeout "$validation_timeout"

case "$flow_verdict" in
  PASS|PARTIAL|FAIL) ;;
  *)
    printf 'Unsupported flow verdict: %s\n' "$flow_verdict" >&2
    exit 64
    ;;
esac

case "$trace_producer" in
  ''|[!A-Za-z0-9]*|*[!A-Za-z0-9._-]*)
    printf 'Unsafe trace producer: %s\n' "$trace_producer" >&2
    exit 64
    ;;
esac
case "$trace_producer_version" in
  ''|[!A-Za-z0-9]*|*[!A-Za-z0-9._+-]*)
    printf 'Unsafe trace producer version: %s\n' "$trace_producer_version" >&2
    exit 64
    ;;
esac
if [ "${#trace_producer}" -gt 64 ] || [ "${#trace_producer_version}" -gt 64 ]; then
  printf '%s\n' 'Trace producer and version must be at most 64 bytes' >&2
  exit 64
fi
case "$trace_format" in
  chrome-trace-json)
    expected_extension=.json
    ;;
  playwright-trace-zip)
    expected_extension=.zip
    ;;
  *)
    printf 'Unsupported trace format: %s\n' "$trace_format" >&2
    exit 64
    ;;
esac

if [ -n "$session_name" ]; then
  if [ ! -x "$identifier_validator" ]; then
    printf 'Trace identifier validator is unavailable: %s\n' "$identifier_validator" >&2
    exit 70
  fi
  "$identifier_validator" "$session_name" || exit $?
fi

owned_runtime=false
if [ -n "$browser_runtime" ] || [ -n "$browser_run_id" ] || [ -n "$browser_app" ] || [ -n "$browser_receipt" ]; then
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
  if [ -n "$browser_receipt" ]; then
    case "$browser_receipt" in
      /*) ;;
      *) printf 'Browser receipt path must be absolute: %s\n' "$browser_receipt" >&2; exit 64 ;;
    esac
    if [ -L "$browser_receipt" ] || [ ! -f "$browser_receipt" ]; then
      printf 'Browser receipt must be an existing regular file: %s\n' "$browser_receipt" >&2
      exit 64
    fi
  fi
  if [ -n "$session_name" ] && [ "$session_name" != "$browser_app" ]; then
    printf 'Legacy session and owned browser app must match: %s != %s\n' \
      "$session_name" "$browser_app" >&2
    exit 64
  fi
  owned_runtime=true
fi

case "$trace_path" in
  /*) ;;
  *)
    printf 'Trace path must be absolute: %s\n' "$trace_path" >&2
    exit 64
    ;;
esac

case "$stop_timeout" in
  ''|*[!0-9]*|0)
    printf '%s\n' 'Timeouts must be positive integer seconds' >&2
    exit 64
    ;;
esac
case "$recovery_timeout" in
  ''|*[!0-9]*|0)
    printf '%s\n' 'Timeouts must be positive integer seconds' >&2
    exit 64
    ;;
esac
case "$validation_timeout" in
  ''|*[!0-9]*|0)
    printf '%s\n' 'Timeouts must be positive integer seconds' >&2
    exit 64
    ;;
esac

trace_dir=$(dirname "$trace_path")
if [ -z "$result_file" ]; then
  result_file="$trace_dir/trace-finalization.env"
fi
case "$result_file" in
  /*) ;;
  *)
    printf 'Result path must be absolute: %s\n' "$result_file" >&2
    exit 64
    ;;
esac
result_dir=$(dirname "$result_file")
result_base=$(basename "$result_file")
mkdir -p "$trace_dir" "$result_dir" || exit 70

if [ -L "$result_file" ] || { [ -e "$result_file" ] && [ ! -f "$result_file" ]; }; then
  printf 'Result destination must be absent or a regular file: %s\n' "$result_file" >&2
  exit 64
fi

write_dependency_failure_result() {
  dependency_artifact_disposition=missing
  if [ -e "$trace_path" ] || [ -L "$trace_path" ]; then
    dependency_artifact_disposition=retained_invalid
  fi
  dependency_result_tmp=$(mktemp "$result_dir/.${result_base}.tmp.XXXXXX") || return 1
  if ! {
    printf 'flow_verdict=%s\n' "$flow_verdict"
    printf 'producer=%s\n' "$trace_producer"
    printf 'producer_version=%s\n' "$trace_producer_version"
    printf 'declared_format=%s\n' "$trace_format"
    printf 'detected_format=not_run\n'
    printf 'validator=not_run\n'
    printf 'infrastructure_result=FAIL\n'
    printf 'finalization_status=dependency_missing\n'
    printf 'stop_status=not_run\n'
    printf 'stop_exit_code=0\n'
    printf 'validation_status=not_run\n'
    printf 'recovery_status=not_needed\n'
    printf 'recovery_exit_code=0\n'
    printf 'artifact_disposition=%s\n' "$dependency_artifact_disposition"
    printf 'artifact_path=%s\n' "$trace_path"
    printf 'analysis_eligible=false\n'
    printf 'preexisting_artifact_path=\n'
    printf 'dependency_status=missing_python3\n'
  } > "$dependency_result_tmp"; then
    rm -f "$dependency_result_tmp"
    return 1
  fi
  if ! mv "$dependency_result_tmp" "$result_file"; then
    rm -f "$dependency_result_tmp"
    return 1
  fi
  [ -f "$result_file" ] && [ ! -L "$result_file" ] && [ -r "$result_file" ] || return 1
  cat "$result_file"
}

if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' 'python3 is required for isolated trace-finalizer process groups' >&2
  if ! write_dependency_failure_result; then
    printf 'Cannot write Python dependency failure result: %s\n' "$result_file" >&2
  fi
  exit 69
fi

work_dir=$(mktemp -d "${TMPDIR:-/tmp}/e2e-trace-finalize.XXXXXX") || exit 70

terminate_active_command() {
  if [ -z "$active_pid" ]; then
    return
  fi

  # The supervisor creates a new process group whose id is the supervisor pid.
  # Signal the whole group so forked descendants cannot outlive the watchdog.
  kill -TERM -- "-$active_pgid" 2>/dev/null || kill -TERM "$active_pid" 2>/dev/null || true
  sleep 1
  kill -KILL -- "-$active_pgid" 2>/dev/null || kill -KILL "$active_pid" 2>/dev/null || true
  wait "$active_pid" 2>/dev/null || true
  active_pid=
  active_pgid=
}

# Invoked indirectly by the EXIT trap.
# shellcheck disable=SC2329
cleanup_work_dir() {
  terminate_active_command
  rm -rf "$work_dir"
}

# Invoked indirectly by the signal traps.
# shellcheck disable=SC2329
handle_signal() {
  terminate_active_command
  if [ -e "$trace_path" ]; then
    signal_stamp=$(date +%Y%m%d-%H%M%S)
    case "$trace_path" in
      *.zip) signal_base=${trace_path%.zip}; signal_extension=.zip ;;
      *.json) signal_base=${trace_path%.json}; signal_extension=.json ;;
      *) signal_base=$trace_path; signal_extension=.artifact ;;
    esac
    mv "$trace_path" "${signal_base}.invalid-signal-${signal_stamp}-$$${signal_extension}" 2>/dev/null ||
      rm -f "$trace_path"
  fi
  exit 130
}

trap cleanup_work_dir EXIT
trap handle_signal HUP INT TERM

bounded_timed_out=false
bounded_exit_code=0

run_bounded() {
  bounded_timeout=$1
  bounded_log=$2
  shift 2

  : > "$bounded_log"
  python3 -c '
import os
import sys

os.setsid()
os.execvp(sys.argv[1], sys.argv[1:])
' "$@" >"$bounded_log" 2>&1 &
  bounded_pid=$!
  active_pid=$bounded_pid
  active_pgid=$bounded_pid
  bounded_started=$(date +%s)

  while kill -0 "$bounded_pid" 2>/dev/null; do
    bounded_now=$(date +%s)
    if [ $((bounded_now - bounded_started)) -ge "$bounded_timeout" ]; then
      terminate_active_command
      bounded_timed_out=true
      bounded_exit_code=124
      return 124
    fi
    sleep 1
  done

  wait "$bounded_pid"
  bounded_exit_code=$?
  active_pid=
  active_pgid=
  bounded_timed_out=false
  return "$bounded_exit_code"
}

run_browser_bounded() {
  browser_timeout=$1
  browser_log=$2
  shift 2

  if [ "$owned_runtime" = true ]; then
    if [ -n "$browser_receipt" ]; then
      run_bounded "$browser_timeout" "$browser_log" \
        "$browser_runtime" --run-id "$browser_run_id" --app "$browser_app" \
          --receipt "$browser_receipt" "$@"
    else
      run_bounded "$browser_timeout" "$browser_log" \
        "$browser_runtime" --run-id "$browser_run_id" --app "$browser_app" "$@"
    fi
  elif [ -n "$session_name" ]; then
    run_bounded "$browser_timeout" "$browser_log" \
      "$agent_browser_bin" --session "$session_name" "$@"
  else
    run_bounded "$browser_timeout" "$browser_log" "$agent_browser_bin" "$@"
  fi
}

quarantine_artifact() {
  quarantine_reason=$1
  if [ ! -e "$trace_path" ]; then
    artifact_disposition=missing
    artifact_path=$trace_path
    return
  fi

  if [ ! -f "$trace_path" ]; then
    artifact_disposition=retained_invalid
    artifact_path=$trace_path
    return
  fi

  quarantine_stamp=$(date +%Y%m%d-%H%M%S)
  case "$trace_path" in
    *.zip) quarantine_base=${trace_path%.zip}; quarantine_extension=.zip ;;
    *.json) quarantine_base=${trace_path%.json}; quarantine_extension=.json ;;
    *) quarantine_base=$trace_path; quarantine_extension=.artifact ;;
  esac
  quarantine_path="${quarantine_base}.invalid-${quarantine_reason}-${quarantine_stamp}-$$${quarantine_extension}"

  if mv "$trace_path" "$quarantine_path"; then
    artifact_disposition=quarantined
    artifact_path=$quarantine_path
  else
    artifact_disposition=retained_invalid
    artifact_path=$trace_path
  fi
}

write_result_contract() {
  result_tmp=$(mktemp "$result_dir/.${result_base}.tmp.XXXXXX") || {
    printf 'Cannot create trace finalization result temporary file in: %s\n' "$result_dir" >&2
    return 70
  }
  if ! {
    printf 'flow_verdict=%s\n' "$flow_verdict"
    printf 'producer=%s\n' "$trace_producer"
    printf 'producer_version=%s\n' "$trace_producer_version"
    printf 'declared_format=%s\n' "$trace_format"
    printf 'detected_format=%s\n' "$detected_format"
    printf 'validator=%s\n' "$validator"
    printf 'infrastructure_result=%s\n' "$infrastructure_result"
    printf 'finalization_status=%s\n' "$finalization_status"
    printf 'stop_status=%s\n' "$stop_status"
    printf 'stop_exit_code=%s\n' "$stop_exit_code"
    printf 'validation_status=%s\n' "$validation_status"
    printf 'recovery_status=%s\n' "$recovery_status"
    printf 'recovery_exit_code=%s\n' "$recovery_exit_code"
    printf 'artifact_disposition=%s\n' "$artifact_disposition"
    printf 'artifact_path=%s\n' "$artifact_path"
    printf 'analysis_eligible=%s\n' "$analysis_eligible"
    printf 'preexisting_artifact_path=%s\n' "$preexisting_artifact_path"
  } > "$result_tmp"; then
    rm -f "$result_tmp"
    printf 'Cannot write trace finalization result temporary file: %s\n' "$result_tmp" >&2
    return 70
  fi

  if ! python3 - "$result_tmp" "$result_file" <<'PY'
import os
import stat
import sys

source, destination = sys.argv[1:3]
if os.path.lexists(destination) and not stat.S_ISREG(os.lstat(destination).st_mode):
    raise SystemExit("destination is not a regular file")
os.replace(source, destination)
PY
  then
    rm -f "$result_tmp"
    printf 'Cannot write trace finalization result: %s\n' "$result_file" >&2
    return 70
  fi

  if [ ! -f "$result_file" ] || [ -L "$result_file" ] || [ ! -r "$result_file" ]; then
    printf 'Trace finalization result is not a readable regular file: %s\n' "$result_file" >&2
    return 70
  fi
  if ! cat "$result_file"; then
    printf 'Cannot read trace finalization result: %s\n' "$result_file" >&2
    return 70
  fi
}

preexisting_artifact_path=
case "$trace_path" in
  *"$expected_extension") extension_matches=true ;;
  *) extension_matches=false ;;
esac
if [ "$extension_matches" = false ]; then
  stop_status=not_run
  stop_exit_code=0
  detected_format=not_run
  validator=not_run
  validation_status=format_mismatch
  run_browser_bounded "$recovery_timeout" "$work_dir/recovery.log" close
  recovery_command_result=$?
  recovery_exit_code=$bounded_exit_code
  recovery_was_timeout=$bounded_timed_out
  if [ "$recovery_was_timeout" = true ]; then
    recovery_status=timeout
  elif [ "$recovery_command_result" -eq 0 ]; then
    recovery_status=closed
  else
    recovery_status=failed
  fi
  artifact_disposition=missing
  artifact_path=$trace_path
  if [ -e "$trace_path" ] || [ -L "$trace_path" ]; then
    artifact_disposition=retained_invalid
  fi
  analysis_eligible=false
  infrastructure_result=FAIL
  finalization_status=format_mismatch
  write_result_contract || exit $?
  exit 23
fi

if [ -e "$trace_path" ]; then
  quarantine_stamp=$(date +%Y%m%d-%H%M%S)
  case "$trace_path" in
    *.zip) quarantine_base=${trace_path%.zip}; quarantine_extension=.zip ;;
    *.json) quarantine_base=${trace_path%.json}; quarantine_extension=.json ;;
    *) quarantine_base=$trace_path; quarantine_extension=.artifact ;;
  esac
  preexisting_artifact_path="${quarantine_base}.invalid-preexisting-${quarantine_stamp}-$$${quarantine_extension}"
  if ! mv "$trace_path" "$preexisting_artifact_path"; then
    printf 'Cannot quarantine pre-existing trace artifact: %s\n' "$trace_path" >&2
    exit 70
  fi
fi

run_browser_bounded "$stop_timeout" "$work_dir/trace-stop.log" trace stop "$trace_path"
stop_command_result=$?
stop_exit_code=$bounded_exit_code
stop_was_timeout=$bounded_timed_out

if [ "$stop_was_timeout" = true ]; then
  stop_status=timeout
elif [ "$stop_command_result" -eq 0 ]; then
  stop_status=completed
else
  stop_status=failed
fi

recovery_status=not_needed
recovery_exit_code=0
if [ "$stop_status" != completed ]; then
  run_browser_bounded "$recovery_timeout" "$work_dir/recovery.log" close
  recovery_command_result=$?
  recovery_exit_code=$bounded_exit_code
  recovery_was_timeout=$bounded_timed_out

  if [ "$recovery_was_timeout" = true ]; then
    recovery_status=timeout
  elif [ "$recovery_command_result" -eq 0 ]; then
    recovery_status=closed
  else
    recovery_status=failed
  fi
fi

validation_status=not_run
detected_format=not_run
validator=not_run
if [ ! -e "$trace_path" ]; then
  validation_status=missing
elif [ ! -f "$trace_path" ]; then
  validation_status=not_regular
elif [ ! -s "$trace_path" ]; then
  validation_status=empty
elif [ ! -f "$chrome_validator" ]; then
  validation_status=validator_unavailable
else
  run_bounded "$validation_timeout" "$work_dir/format-detection.log" \
    python3 "$chrome_validator" detect "$trace_path"
  detection_result=$?
  detection_timed_out=$bounded_timed_out
  if [ "$detection_timed_out" = true ]; then
    validation_status=timeout
  elif [ "$detection_result" -eq 4 ]; then
    validation_status=resource_limit_exceeded
  elif [ "$detection_result" -ne 0 ]; then
    validation_status=validator_unavailable
  else
    detected_format=$(sed -n '1p' "$work_dir/format-detection.log")
    case "$detected_format" in
      chrome-trace-json|playwright-trace-zip|unknown) ;;
      *)
        detected_format=unknown
        validation_status=validator_unavailable
        ;;
    esac
    if [ "$validation_status" = not_run ]; then
      if [ "$detected_format" != "$trace_format" ]; then
        validation_status=format_mismatch
      elif [ "$trace_format" = chrome-trace-json ]; then
        validator=$(basename "$chrome_validator")
        run_bounded "$validation_timeout" "$work_dir/chrome-validation.log" \
          python3 "$chrome_validator" validate "$trace_path"
        chrome_validation_result=$?
        chrome_validation_timed_out=$bounded_timed_out
        if [ "$chrome_validation_timed_out" = true ]; then
          validation_status=timeout
        else
          case "$chrome_validation_result" in
            0) validation_status=valid ;;
            2) validation_status=invalid_json ;;
            3) validation_status=format_mismatch ;;
            4) validation_status=resource_limit_exceeded ;;
            *) validation_status=validator_unavailable ;;
          esac
        fi
      elif [ ! -f "$archive_validator" ]; then
        validation_status=validator_unavailable
      else
        validator=$(basename "$archive_validator")
        run_bounded "$validation_timeout" "$work_dir/archive-validation.log" \
          python3 "$archive_validator" validate "$trace_path"
        archive_validation_result=$?
        archive_validation_timed_out=$bounded_timed_out
        if [ "$archive_validation_timed_out" = true ]; then
          validation_status=timeout
        else
          case "$archive_validation_result" in
            0) validation_status=valid ;;
            2) validation_status=invalid_zip ;;
            3) validation_status=unsafe_archive ;;
            4) validation_status=missing_playwright_content ;;
            6) validation_status=resource_limit_exceeded ;;
            *) validation_status=validator_unavailable ;;
          esac
        fi
      fi
    fi
  fi
fi

artifact_disposition=accepted
artifact_path=$trace_path
analysis_eligible=false
infrastructure_result=FAIL
finalization_status=invalid_artifact
exit_code=22

if [ "$stop_status" = timeout ]; then
  finalization_status=timeout
  quarantine_artifact timeout
  exit_code=20
elif [ "$stop_status" = failed ]; then
  finalization_status=stop_failed
  quarantine_artifact stop_failed
  exit_code=21
elif [ "$validation_status" = format_mismatch ]; then
  finalization_status=format_mismatch
  quarantine_artifact format_mismatch
  exit_code=23
elif [ "$validation_status" != valid ]; then
  finalization_status=invalid_artifact
  quarantine_artifact "$validation_status"
  exit_code=22
else
  finalization_status=valid
  infrastructure_result=PASS
  analysis_eligible=true
  artifact_disposition=accepted
  artifact_path=$trace_path
  exit_code=0
fi

write_result_contract || exit $?
exit "$exit_code"
