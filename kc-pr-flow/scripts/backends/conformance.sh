#!/bin/bash
# Conformance check for a review backend. See CONTRACT.md.
#
# Exercises the failure and status paths, which need no real work created. The
# success path of `create` is inherently side-effecting and is therefore checked
# by one real dispatch, not here — this script's job is to catch a backend that
# gets the argument handling or the status vocabulary wrong.

set -uo pipefail

B="${1:-}"
[[ -x "$B" ]] || { echo "usage: conformance.sh <backend-path>" >&2; exit 2; }

pass=0; fail=0
ok()   { printf 'PASS  %s\n' "$1"; pass=$((pass+1)); }
bad()  { printf 'FAIL  %s\n    %s\n' "$1" "$2"; fail=$((fail+1)); }

run() { # run <verb> <args...> -> sets OUT, ERR, RC
  local tmp_o tmp_e
  tmp_o=$(mktemp); tmp_e=$(mktemp)
  "$B" "$@" >"$tmp_o" 2>"$tmp_e"; RC=$?
  OUT=$(cat "$tmp_o"); ERR=$(cat "$tmp_e")
  rm -f "$tmp_o" "$tmp_e"
}

run
[[ $RC -ne 0 ]] && ok "no verb exits non-zero" || bad "no verb exits non-zero" "rc=$RC"

run bogus-verb
[[ $RC -ne 0 ]] && ok "unknown verb exits non-zero" || bad "unknown verb exits non-zero" "rc=$RC"

run create
if [[ $RC -ne 0 && -n "$ERR" && -z "$OUT" ]]; then
  ok "create with no args: non-zero, reason on stderr, stdout clean"
else
  bad "create with no args" "rc=$RC stdout='$OUT'"
fi

run create acme/widgets 1 https://example.com/pr/1 main /nonexistent/prompt.md
if [[ $RC -ne 0 && -z "$OUT" ]]; then
  ok "create with unreadable prompt: non-zero, stdout clean"
else
  bad "create with unreadable prompt" "rc=$RC stdout='$OUT'"
fi

run status
[[ $RC -ne 0 ]] && ok "status with no args exits non-zero" || bad "status with no args exits non-zero" "rc=$RC"

run status conformance-nonexistent-job-id
if [[ $RC -eq 0 ]]; then
  case "$OUT" in
    running|done|error) ok "status of unknown job prints one contract word ($OUT)" ;;
    *) bad "status of unknown job" "stdout='$OUT', expected running|done|error" ;;
  esac
else
  # Permitted: the backend could not reach its service. Undetermined must never
  # be reported as a completion.
  ok "status of unknown job: undetermined, non-zero (listener will re-ask)"
fi

printf '\n%d passed, %d failed\n' "$pass" "$fail"
[[ $fail -eq 0 ]]
