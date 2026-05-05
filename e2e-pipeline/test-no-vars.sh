#!/usr/bin/env bash
set -euo pipefail

# DO NOT EDIT -- regenerate with: e2e-compile test-no-vars
# Source: compiler/test/fixtures/no-vars-flow.yaml
# Mapping: compiler/test/fixtures/test-app.yaml
# Generated: 2026-03-17T18:18:25.105Z
# SHA-256: e0cdd87a129fb8738bfaa88fec8648790af87545ffe77b84e1a5bcc3af471d68

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Runtime flags
CONTINUE_ON_ERROR=false
RETRIES=0
JUNIT_OUTPUT=""
METRICS_OUTPUT=""
_POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --continue-on-error)
      CONTINUE_ON_ERROR=true
      shift
      ;;
    --retries)
      RETRIES="$2"
      shift 2
      ;;
    --junit)
      JUNIT_OUTPUT="$2"
      shift 2
      if [ -z "$JUNIT_OUTPUT" ]; then
        echo "ERROR: --junit requires a path argument"
        exit 1
      fi
      ;;
    --metrics-output)
      METRICS_OUTPUT="$2"
      shift 2
      if [ -z "$METRICS_OUTPUT" ]; then
        echo "ERROR: --metrics-output requires a path argument"
        exit 1
      fi
      ;;
    *)
      _POSITIONAL+=("$1")
      shift
      ;;
  esac
done
set -- "${_POSITIONAL[@]:-}"

# Usage: test-no-vars.sh [base_url]
# Parameters:
# $1 BASE_URL -- optional (or set E2E_BASE_URL, default: http://localhost:3000)
BASE_URL="${1:-${E2E_BASE_URL:-http://localhost:3000}}"

BASE_URL="${BASE_URL%/}"

# Failure accumulator
_FAILED_STEPS=()
_HAD_RETRIES=false
# Attempt tracking (FLAKY-02)
_TOTAL_ATTEMPTS=1
_ATTEMPT_NUM=1
# JUnit step tracking arrays (FLAG-01)
_STEP_NAMES=()
_STEP_RESULTS=()
_STEP_FAILURES=()
_STEP_TIMES=()
_FLOW_START=$SECONDS
_handle_failure() {
  local _step_id="$1"
  local _msg="$2"
  echo "FAIL: $_step_id -- $_msg"
  local _msg_clean
  _msg_clean=$(printf '%s' "$_msg" | sed 's/\x1b\[[0-9;]*m//g' | tr -d '\000-\010\013\014\016-\037')
  _STEP_FAILURES+=("$_msg_clean")
  if [ "$CONTINUE_ON_ERROR" = "true" ]; then
    _FAILED_STEPS+=("$_step_id")
  else
    exit 1
  fi
  return 0
}

# Poll-until helpers (CODEGEN-01)
_poll_visible() {
  local _sel="$1"
  local _step_id="$2"
  local _timeout="${3:-10}"
  local _session="${4:-}"
  local _count=0
  local _result
  while [ "$_count" -lt "$_timeout" ]; do
    if [ -n "$_session" ]; then
      _result=$(agent-browser --session "$_session" is visible "$_sel" 2>/dev/null) || true
    else
      _result=$(agent-browser is visible "$_sel" 2>/dev/null) || true
    fi
    [ "$_result" = "true" ] && return 0
    sleep 1
    _count=$((_count + 1))
  done
  return 1
}

_poll_not_visible() {
  local _sel="$1"
  local _step_id="$2"
  local _timeout="${3:-10}"
  local _session="${4:-}"
  local _count=0
  local _result
  while [ "$_count" -lt "$_timeout" ]; do
    if [ -n "$_session" ]; then
      _result=$(agent-browser --session "$_session" is visible "$_sel" 2>/dev/null) || true
    else
      _result=$(agent-browser is visible "$_sel" 2>/dev/null) || true
    fi
    [ "$_result" = "false" ] && return 0
    sleep 1
    _count=$((_count + 1))
  done
  return 1
}

_poll_url_contains() {
  local _value="$1"
  local _step_id="$2"
  local _timeout="${3:-10}"
  local _count=0
  local _url
  while [ "$_count" -lt "$_timeout" ]; do
    _url=$(agent-browser get url 2>/dev/null) || true
    [[ "$_url" == *"$_value"* ]] && return 0
    sleep 1
    _count=$((_count + 1))
  done
  return 1
}

_poll_url_not_contains() {
  local _value="$1"
  local _step_id="$2"
  local _timeout="${3:-10}"
  local _count=0
  local _url
  while [ "$_count" -lt "$_timeout" ]; do
    _url=$(agent-browser get url 2>/dev/null) || true
    [[ "$_url" != *"$_value"* ]] && return 0
    sleep 1
    _count=$((_count + 1))
  done
  return 1
}

_poll_or_visible() {
  local _step_id="$1"
  local _timeout="$2"
  local _session="$3"
  shift 3
  local _count=0
  local _result
  local _found
  while [ "$_count" -lt "$_timeout" ]; do
    _found=false
    for _sel in "$@"; do
      if [ -n "$_session" ]; then
        _result=$(agent-browser --session "$_session" is visible "$_sel" 2>/dev/null) || true
      else
        _result=$(agent-browser is visible "$_sel" 2>/dev/null) || true
      fi
      if [ "$_result" = "true" ]; then _found=true; break; fi
    done
    [ "$_found" = "true" ] && return 0
    sleep 1
    _count=$((_count + 1))
  done
  return 1
}

_emit_junit() {
  local _out="$1"
  local _total=${#_STEP_NAMES[@]}
  local _failures=0
  local _skipped=0
  local _duration=$(( SECONDS - _FLOW_START ))
  local _i
  for _i in "${!_STEP_RESULTS[@]}"; do
    case "${_STEP_RESULTS[$_i]}" in
      fail) _failures=$(( _failures + 1 )) ;;
      skip) _skipped=$(( _skipped + 1 )) ;;
    esac
  done
  {
    printf '<?xml version="1.0" encoding="UTF-8"?>\n'
    printf '<testsuites>\n'
    printf '  <testsuite name="test-no-vars" tests="%s" failures="%s" skipped="%s" time="%s" timestamp="%s">\n' \
      "$_total" "$_failures" "$_skipped" "$_duration" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    for _i in "${!_STEP_NAMES[@]}"; do
      local _sname="${_STEP_NAMES[$_i]}"
      local _sresult="${_STEP_RESULTS[$_i]}"
      local _stime="${_STEP_TIMES[$_i]}"
      local _sfail="${_STEP_FAILURES[$_i]}"
      if [ "$_sresult" = "skip" ]; then
        printf '    <testcase classname="test-no-vars" name="%s" time="%s"><skipped/></testcase>\n' \
          "$_sname" "$_stime"
      elif [ "$_sresult" = "fail" ]; then
        printf '    <testcase classname="test-no-vars" name="%s" time="%s"><failure message="%s"/></testcase>\n' \
          "$_sname" "$_stime" "$_sfail"
      else
        printf '    <testcase classname="test-no-vars" name="%s" time="%s"/>\n' \
          "$_sname" "$_stime"
      fi
    done
    printf '  </testsuite>\n'
    printf '</testsuites>\n'
  } > "$_out"
}

_emit_metrics() {
  local _out="$1"
  local _total=${#_STEP_NAMES[@]}
  local _passed=0
  local _failed=0
  local _skipped=0
  local _i
  for _i in "${!_STEP_RESULTS[@]}"; do
    case "${_STEP_RESULTS[$_i]}" in
      pass) _passed=$(( _passed + 1 )) ;;
      fail) _failed=$(( _failed + 1 )) ;;
      skip) _skipped=$(( _skipped + 1 )) ;;
    esac
  done
  local _exit_fail=0
  [ "${#_FAILED_STEPS[@]}" -gt 0 ] && _exit_fail=1
  local _passed_first_try=false
  local _flaky_pass=false
  if [ "$_exit_fail" -eq 0 ] && [ "$_HAD_RETRIES" = "false" ]; then
    _passed_first_try=true
  fi
  if [ "$_exit_fail" -eq 0 ] && [ "$_HAD_RETRIES" = "true" ]; then
    _flaky_pass=true
  fi
  {
    printf '{"flow":"' ; printf '%s' "test-no-vars" ; printf '",'
    printf '"timestamp":"%s",' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '"attempt":%s,' "$_ATTEMPT_NUM"
    printf '"total_attempts":%s,' "$_TOTAL_ATTEMPTS"
    printf '"passed_first_try":%s,' "$_passed_first_try"
    printf '"flaky_pass":%s,' "$_flaky_pass"
    printf '"steps":[' 
    local _first=true
    for _i in "${!_STEP_NAMES[@]}"; do
      local _sname="${_STEP_NAMES[$_i]}"
      local _sresult="${_STEP_RESULTS[$_i]}"
      local _stime="${_STEP_TIMES[$_i]}"
      local _sfail="${_STEP_FAILURES[$_i]}"
      local _sfail_esc
      _sfail_esc=$(printf '%s' "$_sfail" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n')
      if [ "$_first" = "true" ]; then _first=false; else printf ','; fi
      printf '{"id":"%s","result":"%s","time_s":%s,"failure_msg":"%s"}' \
        "$_sname" "$_sresult" "$_stime" "$_sfail_esc"
    done
    printf '],"summary":{"total":%s,"passed":%s,"failed":%s,"skipped":%s,"flaky_pass":%s}}' \
      "$_total" "$_passed" "$_failed" "$_skipped" "$_flaky_pass"
    printf '\n'
  } > "$_out"
}

cleanup() {
  agent-browser close 2>/dev/null || true
}
trap cleanup EXIT

echo "[1/2] navigate-to-login: Navigate to /login"
_STEP_START=$SECONDS
_retry=0
_step_ok=true
while true; do
  agent-browser open "${BASE_URL}/login" && break
  _retry=$((_retry + 1))
  if [ "$_retry" -ge "$RETRIES" ] || [ "$RETRIES" -eq 0 ]; then
    _step_ok=false
    break
  fi
  _HAD_RETRIES=true
  echo "RETRY [$_retry/$RETRIES]: navigate-to-login"
  sleep 2
done
_elapsed=$(( SECONDS - _STEP_START ))
if [ "$_step_ok" = "true" ]; then
  _STEP_NAMES+=("navigate-to-login")
  _STEP_RESULTS+=("pass")
  _STEP_FAILURES+=("")
  _STEP_TIMES+=("$_elapsed")
else
  _STEP_NAMES+=("navigate-to-login")
  _STEP_RESULTS+=("fail")
  _STEP_TIMES+=("$_elapsed")
  _handle_failure "navigate-to-login" "navigate to /login failed"
fi

echo "[2/2] click-submit: Click login_button on login"
_STEP_START=$SECONDS
_retry=0
_step_ok=true
while true; do
  agent-browser click '[role="button"][aria-label="Sign In"]' && break
  _retry=$((_retry + 1))
  if [ "$_retry" -ge "$RETRIES" ] || [ "$RETRIES" -eq 0 ]; then
    _step_ok=false
    break
  fi
  _HAD_RETRIES=true
  echo "RETRY [$_retry/$RETRIES]: click-submit"
  sleep 2
done
_elapsed=$(( SECONDS - _STEP_START ))
if [ "$_step_ok" = "true" ]; then
  _STEP_NAMES+=("click-submit")
  _STEP_RESULTS+=("pass")
  _STEP_FAILURES+=("")
  _STEP_TIMES+=("$_elapsed")
else
  _STEP_NAMES+=("click-submit")
  _STEP_RESULTS+=("fail")
  _STEP_TIMES+=("$_elapsed")
  _handle_failure "click-submit" "click action failed"
fi

# Emit metrics JSON if --metrics-output path was provided (FLAKY-02)
if [ -n "$METRICS_OUTPUT" ]; then _emit_metrics "$METRICS_OUTPUT"; fi
# Emit JUnit XML if --junit path was provided (FLAG-01)
if [ -n "$JUNIT_OUTPUT" ]; then _emit_junit "$JUNIT_OUTPUT"; fi
# Exit summary
if [ ${#_FAILED_STEPS[@]} -gt 0 ]; then
  echo "FAIL: ${#_FAILED_STEPS[@]} steps failed: ${_FAILED_STEPS[*]}"
  exit 1
fi
if [ "$_HAD_RETRIES" = "true" ]; then
  echo "PASS (FLAKY): test-no-vars (2/2 steps, 0 skipped)"
else
  echo "PASS: test-no-vars (2/2 steps, 0 skipped)"
fi
exit 0