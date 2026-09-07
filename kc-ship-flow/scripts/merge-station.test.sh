#!/usr/bin/env bash
# Behavior contract for kc-ship-flow/scripts/merge-station.sh, driven through
# the fixture at kc-ship-flow/scripts/fixtures/fake-gh-merge/gh.

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
MERGE_STATION="$HERE/merge-station.sh"
FAKE_GH_DIR="$HERE/fixtures/fake-gh-merge"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

PASS=0
FAIL=0

pass() { printf 'case %s: PASS - %s\n' "$1" "$2"; PASS=$((PASS + 1)); }
fail() { printf 'case %s: FAIL - %s\n' "$1" "$2"; FAIL=$((FAIL + 1)); }

run_ms() {
  local scenario="$1" log="$2"; shift 2
  : > "$log"
  FAKE_GH_SCENARIO="$scenario" FAKE_GH_LOG="$log" PATH="$FAKE_GH_DIR:$PATH" MERGE_STATION_POLL_SECONDS=0 \
    bash "$MERGE_STATION" "$@"
}

first_line_matching() {
  grep -n "$1" "$2" | head -1 | cut -d: -f1
}

last_line_matching() {
  grep -n "$1" "$2" | tail -1 | cut -d: -f1
}

# --- case (a): refuses a non-trunk base before any ready/merge call ---
scenario_a="$TMP_DIR/a.json"
cat > "$scenario_a" <<'JSON'
{"201": {"baseRefName": "feature-other"}}
JSON
log_a="$TMP_DIR/a.log"
out_a="$(run_ms "$scenario_a" "$log_a" --trunk main 201 2>&1)"
rc_a=$?
if [ "$rc_a" -eq 2 ] && grep -q "BASE_NOT_TRUNK" <<<"$out_a" && ! grep -qE '^pr (ready|merge)' "$log_a"; then
  pass a "refuses a non-trunk base before any ready/merge call"
else
  printf '  out=%s\n  log=%s\n' "$out_a" "$(cat "$log_a")"
  fail a "refuses a non-trunk base before any ready/merge call"
fi

# --- case (b): refuses a head not in --accepted, proceeds with --override ---
scenario_b="$TMP_DIR/b.json"
cat > "$scenario_b" <<'JSON'
{"202": {
  "baseRefName": "main",
  "headRefOid": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "states": [{"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "statusCheckRollup": []}],
  "ready": "ok", "merge": "ok",
  "mergeCommit": "cccccccccccccccccccccccccccccccccccccccc"
}}
JSON
accepted_b="$TMP_DIR/accepted-b.txt"
echo "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" > "$accepted_b"

log_b1="$TMP_DIR/b1.log"
out_b1="$(run_ms "$scenario_b" "$log_b1" --trunk main --accepted "$accepted_b" 202 2>&1)"
rc_b1=$?
if [ "$rc_b1" -eq 2 ] && grep -q "HEAD_NOT_ACCEPTED" <<<"$out_b1" && ! grep -qE '^pr (ready|merge)' "$log_b1"; then
  pass b "refuses a head not in --accepted before any ready/merge call"
else
  printf '  out=%s\n  log=%s\n' "$out_b1" "$(cat "$log_b1")"
  fail b "refuses a head not in --accepted before any ready/merge call"
fi

log_b2="$TMP_DIR/b2.log"
out_b2="$(run_ms "$scenario_b" "$log_b2" --trunk main --accepted "$accepted_b" --override "manual approval" 202 2>&1)"
rc_b2=$?
if [ "$rc_b2" -eq 0 ] && grep -q "OVERRIDE: manual approval" <<<"$out_b2" && grep -q "MERGED: #202 cccccccccccccccccccccccccccccccccccccccc" <<<"$out_b2"; then
  pass b "proceeds past a non-accepted head with --override"
else
  printf '  out=%s\n' "$out_b2"
  fail b "proceeds past a non-accepted head with --override"
fi

# --- case (c) / (g): two-PR happy path -- ready-all-before-merge order,
# and MERGED lines printed in order ---
scenario_cg="$TMP_DIR/cg.json"
cat > "$scenario_cg" <<'JSON'
{
  "301": {
    "baseRefName": "main",
    "states": [{"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "statusCheckRollup": []}],
    "ready": "ok", "merge": "ok",
    "mergeCommit": "1111111111111111111111111111111111111c"
  },
  "302": {
    "baseRefName": "main",
    "precheck": {"mergeStateStatus": "CLEAN"},
    "states": [{"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "statusCheckRollup": []}],
    "ready": "ok", "merge": "ok",
    "mergeCommit": "2222222222222222222222222222222222222c"
  }
}
JSON
log_cg="$TMP_DIR/cg.log"
out_cg="$(run_ms "$scenario_cg" "$log_cg" --trunk main 301 302 2>&1)"
rc_cg=$?

last_ready="$(last_line_matching '^pr ready' "$log_cg")"
first_merge="$(first_line_matching '^pr merge' "$log_cg")"
if [ "$rc_cg" -eq 0 ] && [ -n "$last_ready" ] && [ -n "$first_merge" ] && [ "$last_ready" -lt "$first_merge" ]; then
  pass c "marks all ready before merging any"
else
  printf '  log=%s\n' "$(cat "$log_cg")"
  fail c "marks all ready before merging any"
fi

expected_order="MERGED: #301 1111111111111111111111111111111111111c
MERGED: #302 2222222222222222222222222222222222222c"
if [ "$rc_cg" -eq 0 ] && [ "$(grep '^MERGED:' <<<"$out_cg")" = "$expected_order" ]; then
  pass g "happy path prints MERGED lines in order"
else
  printf '  out=%s\n' "$out_cg"
  fail g "happy path prints MERGED lines in order"
fi

# --- case (d): first merge refused -> exit 4 naming the PR, no merge call
# for the second PR ---
scenario_d="$TMP_DIR/d.json"
cat > "$scenario_d" <<'JSON'
{
  "401": {
    "baseRefName": "main",
    "states": [{"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "statusCheckRollup": []}],
    "ready": "ok", "merge": "refuse"
  },
  "402": {
    "baseRefName": "main",
    "states": [{"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "statusCheckRollup": []}],
    "ready": "ok", "merge": "ok",
    "mergeCommit": "4444444444444444444444444444444444444c"
  }
}
JSON
log_d="$TMP_DIR/d.log"
out_d="$(run_ms "$scenario_d" "$log_d" --trunk main 401 402 2>&1)"
rc_d=$?
if [ "$rc_d" -eq 4 ] && grep -q "MERGE_FAILED" <<<"$out_d" && grep -q "401" <<<"$out_d" && ! grep -qE '^pr merge 402' "$log_d"; then
  pass d "first merge refused exits 4 naming the PR and never merges the next"
else
  printf '  out=%s\n  log=%s\n' "$out_d" "$(cat "$log_d")"
  fail d "first merge refused exits 4 naming the PR and never merges the next"
fi

# --- case (e): next PR CONFLICTING after a landing -> exit 5 with
# MOVED_BASE ---
scenario_e="$TMP_DIR/e.json"
cat > "$scenario_e" <<'JSON'
{
  "501": {
    "baseRefName": "main",
    "states": [{"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "statusCheckRollup": []}],
    "ready": "ok", "merge": "ok",
    "mergeCommit": "5555555555555555555555555555555555555c"
  },
  "502": {
    "baseRefName": "main",
    "precheck": {"mergeStateStatus": "CONFLICTING"},
    "ready": "ok"
  }
}
JSON
log_e="$TMP_DIR/e.log"
out_e="$(run_ms "$scenario_e" "$log_e" --trunk main 501 502 2>&1)"
rc_e=$?
if [ "$rc_e" -eq 5 ] && grep -q "MERGED: #501 5555555555555555555555555555555555555c" <<<"$out_e" \
    && grep -q "MOVED_BASE: 502" <<<"$out_e" && ! grep -qE '^pr merge 502' "$log_e"; then
  pass e "next PR CONFLICTING after a landing exits 5 with MOVED_BASE"
else
  printf '  out=%s\n  log=%s\n' "$out_e" "$(cat "$log_e")"
  fail e "next PR CONFLICTING after a landing exits 5 with MOVED_BASE"
fi

# --- case (f): a check with FAILURE -> exit 3 ---
scenario_f="$TMP_DIR/f.json"
cat > "$scenario_f" <<'JSON'
{
  "601": {
    "baseRefName": "main",
    "states": [{"mergeable": "UNSTABLE", "mergeStateStatus": "UNSTABLE", "statusCheckRollup": [{"conclusion": "FAILURE"}]}],
    "ready": "ok"
  }
}
JSON
log_f="$TMP_DIR/f.log"
out_f="$(run_ms "$scenario_f" "$log_f" --trunk main 601 2>&1)"
rc_f=$?
if [ "$rc_f" -eq 3 ] && grep -q "CHECK_FAILURE" <<<"$out_f" && ! grep -qE '^pr merge' "$log_f"; then
  pass f "a status check with conclusion FAILURE exits 3"
else
  printf '  out=%s\n  log=%s\n' "$out_f" "$(cat "$log_f")"
  fail f "a status check with conclusion FAILURE exits 3"
fi

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
