#!/usr/bin/env bash
# Behavior contract for kc-ship-flow/scripts/merge-station.sh, driven through
# the fixture at kc-ship-flow/scripts/fixtures/fake-gh-merge/gh.
#
# Self-check -- prove this suite actually catches a broken station (manual,
# not one of the cases below, and not run by this file itself):
#   cp kc-ship-flow/scripts/merge-station.sh /tmp/merge-station.sh.orig
#   sed -i.bak 's/"DIRTY"/"NEVER"/' kc-ship-flow/scripts/merge-station.sh
#   bash kc-ship-flow/scripts/merge-station.test.sh; echo "exit: $?"
#   cp /tmp/merge-station.sh.orig kc-ship-flow/scripts/merge-station.sh
#   rm -f kc-ship-flow/scripts/merge-station.sh.bak
# Expect at least one "FAIL" line (case e1) and a non-zero exit.

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
  FAKE_GH_SCENARIO="$scenario" FAKE_GH_LOG="$log" PATH="$FAKE_GH_DIR:$PATH" \
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
    "mergeCommit": "111111111111111111111111111111111111111c"
  },
  "302": {
    "baseRefName": "main",
    "precheck": {"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN"},
    "states": [{"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "statusCheckRollup": []}],
    "ready": "ok", "merge": "ok",
    "mergeCommit": "222222222222222222222222222222222222222c"
  }
}
JSON
log_cg="$TMP_DIR/cg.log"
out_cg="$(run_ms "$scenario_cg" "$log_cg" --trunk main --poll-seconds 0 301 302 2>&1)"
rc_cg=$?

last_ready="$(last_line_matching '^pr ready' "$log_cg")"
first_merge="$(first_line_matching '^pr merge' "$log_cg")"
if [ "$rc_cg" -eq 0 ] && [ -n "$last_ready" ] && [ -n "$first_merge" ] && [ "$last_ready" -lt "$first_merge" ]; then
  pass c "marks all ready before merging any"
else
  printf '  log=%s\n' "$(cat "$log_cg")"
  fail c "marks all ready before merging any"
fi

expected_order="MERGED: #301 111111111111111111111111111111111111111c
MERGED: #302 222222222222222222222222222222222222222c"
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
    "mergeCommit": "666666666666666666666666666666666666666c"
  }
}
JSON
log_d="$TMP_DIR/d.log"
out_d="$(run_ms "$scenario_d" "$log_d" --trunk main --poll-seconds 0 401 402 2>&1)"
rc_d=$?
if [ "$rc_d" -eq 4 ] && grep -q "MERGE_FAILED" <<<"$out_d" && grep -q "401" <<<"$out_d" && ! grep -qE '^pr merge 402' "$log_d"; then
  pass d "first merge refused exits 4 naming the PR and never merges the next"
else
  printf '  out=%s\n  log=%s\n' "$out_d" "$(cat "$log_d")"
  fail d "first merge refused exits 4 naming the PR and never merges the next"
fi

# --- case (e1) / (e2): next PR reads mergeStateStatus DIRTY or mergeable
# CONFLICTING after a landing -> exit 5 with MOVED_BASE. Each signal is
# isolated from the other (the sibling field set to a non-triggering value)
# so a mutation of either branch alone is caught -- this is what the
# header's documented self-check relies on. ---
scenario_e1="$TMP_DIR/e1.json"
cat > "$scenario_e1" <<'JSON'
{
  "511": {
    "baseRefName": "main",
    "states": [{"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "statusCheckRollup": []}],
    "ready": "ok", "merge": "ok",
    "mergeCommit": "511151115111511151115111511151115111511c"
  },
  "512": {
    "baseRefName": "main",
    "precheck": {"mergeable": "MERGEABLE", "mergeStateStatus": "DIRTY"},
    "ready": "ok"
  }
}
JSON
log_e1="$TMP_DIR/e1.log"
out_e1="$(run_ms "$scenario_e1" "$log_e1" --trunk main --poll-seconds 1 --wait-seconds 2 511 512 2>&1)"
rc_e1=$?
if [ "$rc_e1" -eq 5 ] && grep -q "MERGED: #511 511151115111511151115111511151115111511c" <<<"$out_e1" \
    && grep -q "MOVED_BASE: 512" <<<"$out_e1" && ! grep -qE '^pr merge 512' "$log_e1"; then
  pass e "mergeStateStatus DIRTY alone (mergeable MERGEABLE) after a landing exits 5 with MOVED_BASE"
else
  printf '  out=%s\n  log=%s\n' "$out_e1" "$(cat "$log_e1")"
  fail e "mergeStateStatus DIRTY alone (mergeable MERGEABLE) after a landing exits 5 with MOVED_BASE"
fi

scenario_e2="$TMP_DIR/e2.json"
cat > "$scenario_e2" <<'JSON'
{
  "521": {
    "baseRefName": "main",
    "states": [{"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "statusCheckRollup": []}],
    "ready": "ok", "merge": "ok",
    "mergeCommit": "521252125212521252125212521252125212521c"
  },
  "522": {
    "baseRefName": "main",
    "precheck": {"mergeable": "CONFLICTING", "mergeStateStatus": "BLOCKED"},
    "ready": "ok"
  }
}
JSON
log_e2="$TMP_DIR/e2.log"
out_e2="$(run_ms "$scenario_e2" "$log_e2" --trunk main --poll-seconds 1 --wait-seconds 2 521 522 2>&1)"
rc_e2=$?
if [ "$rc_e2" -eq 5 ] && grep -q "MERGED: #521 521252125212521252125212521252125212521c" <<<"$out_e2" \
    && grep -q "MOVED_BASE: 522" <<<"$out_e2" && ! grep -qE '^pr merge 522' "$log_e2"; then
  pass e "mergeable CONFLICTING alone (mergeStateStatus BLOCKED) after a landing exits 5 with MOVED_BASE"
else
  printf '  out=%s\n  log=%s\n' "$out_e2" "$(cat "$log_e2")"
  fail e "mergeable CONFLICTING alone (mergeStateStatus BLOCKED) after a landing exits 5 with MOVED_BASE"
fi

# --- case (f): a CheckRun-shaped conclusion FAILURE -> exit 3 ---
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
out_f="$(run_ms "$scenario_f" "$log_f" --trunk main --poll-seconds 0 601 2>&1)"
rc_f=$?
if [ "$rc_f" -eq 3 ] && grep -q "CHECK_FAILURE" <<<"$out_f" && ! grep -qE '^pr merge' "$log_f"; then
  pass f "a CheckRun conclusion FAILURE exits 3"
else
  printf '  out=%s\n  log=%s\n' "$out_f" "$(cat "$log_f")"
  fail f "a CheckRun conclusion FAILURE exits 3"
fi

# --- case (h): a legacy StatusContext-shaped failure (state, no conclusion)
# -> exit 3 ---
scenario_h="$TMP_DIR/h.json"
cat > "$scenario_h" <<'JSON'
{
  "602": {
    "baseRefName": "main",
    "states": [{"mergeable": "UNSTABLE", "mergeStateStatus": "UNSTABLE", "statusCheckRollup": [{"state": "ERROR"}]}],
    "ready": "ok"
  }
}
JSON
log_h="$TMP_DIR/h.log"
out_h="$(run_ms "$scenario_h" "$log_h" --trunk main --poll-seconds 0 602 2>&1)"
rc_h=$?
if [ "$rc_h" -eq 3 ] && grep -q "CHECK_FAILURE" <<<"$out_h" && ! grep -qE '^pr merge' "$log_h"; then
  pass h "a legacy StatusContext state ERROR (no conclusion) exits 3"
else
  printf '  out=%s\n  log=%s\n' "$out_h" "$(cat "$log_h")"
  fail h "a legacy StatusContext state ERROR (no conclusion) exits 3"
fi

# --- case (i): not-clean on the first poll, clean on the second -> merges
# after the second poll ---
scenario_i="$TMP_DIR/i.json"
cat > "$scenario_i" <<'JSON'
{
  "701": {
    "baseRefName": "main",
    "states": [
      {"mergeable": "UNKNOWN", "mergeStateStatus": "UNKNOWN", "statusCheckRollup": []},
      {"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "statusCheckRollup": []}
    ],
    "ready": "ok", "merge": "ok",
    "mergeCommit": "777777777777777777777777777777777777777c"
  }
}
JSON
log_i="$TMP_DIR/i.log"
out_i="$(run_ms "$scenario_i" "$log_i" --trunk main --poll-seconds 0 701 2>&1)"
rc_i=$?
poll_calls_i="$(grep -cE '^pr view 701 --json mergeable,mergeStateStatus,statusCheckRollup' "$log_i")"
if [ "$rc_i" -eq 0 ] && grep -q "MERGED: #701 777777777777777777777777777777777777777c" <<<"$out_i" && [ "$poll_calls_i" -ge 2 ]; then
  pass i "merges after a second poll observes clean"
else
  printf '  out=%s\n  log=%s\n' "$out_i" "$(cat "$log_i")"
  fail i "merges after a second poll observes clean"
fi

# --- case (j): never becomes clean -> WAIT_TIMEOUT exit 3 naming the PR ---
scenario_j="$TMP_DIR/j.json"
cat > "$scenario_j" <<'JSON'
{
  "801": {
    "baseRefName": "main",
    "states": [{"mergeable": "UNKNOWN", "mergeStateStatus": "UNKNOWN", "statusCheckRollup": []}],
    "ready": "ok"
  }
}
JSON
log_j="$TMP_DIR/j.log"
out_j="$(run_ms "$scenario_j" "$log_j" --trunk main --wait-seconds 2 --poll-seconds 1 801 2>&1)"
rc_j=$?
if [ "$rc_j" -eq 3 ] && grep -q "WAIT_TIMEOUT" <<<"$out_j" && grep -q "801" <<<"$out_j"; then
  pass j "never-clean PR times out with WAIT_TIMEOUT naming the PR"
else
  printf '  out=%s\n' "$out_j"
  fail j "never-clean PR times out with WAIT_TIMEOUT naming the PR"
fi

# --- case (k): an unknown flag exits 2 with a USAGE token ---
scenario_k="$TMP_DIR/k.json"
echo '{}' > "$scenario_k"
log_k="$TMP_DIR/k.log"
out_k="$(run_ms "$scenario_k" "$log_k" --trunk main --bogus-flag 901 2>&1)"
rc_k=$?
if [ "$rc_k" -eq 2 ] && grep -q "USAGE: unknown flag: --bogus-flag" <<<"$out_k"; then
  pass k "an unknown flag exits 2 with a USAGE token"
else
  printf '  out=%s\n' "$out_k"
  fail k "an unknown flag exits 2 with a USAGE token"
fi

# --- case (l): missing --trunk exits 2 with a USAGE token ---
log_l="$TMP_DIR/l.log"
out_l="$(run_ms "$scenario_k" "$log_l" 902 2>&1)"
rc_l=$?
if [ "$rc_l" -eq 2 ] && grep -q "USAGE: --trunk is required" <<<"$out_l"; then
  pass l "missing --trunk exits 2 with a USAGE token"
else
  printf '  out=%s\n' "$out_l"
  fail l "missing --trunk exits 2 with a USAGE token"
fi

# --- case (m): zero PRs exits 2 with a USAGE token ---
log_m="$TMP_DIR/m.log"
out_m="$(run_ms "$scenario_k" "$log_m" --trunk main 2>&1)"
rc_m=$?
if [ "$rc_m" -eq 2 ] && grep -q "USAGE: at least one PR is required" <<<"$out_m"; then
  pass m "zero PRs exits 2 with a USAGE token"
else
  printf '  out=%s\n' "$out_m"
  fail m "zero PRs exits 2 with a USAGE token"
fi

# --- case (n): a missing --accepted file exits 2 with a USAGE token ---
scenario_n="$TMP_DIR/n.json"
cat > "$scenario_n" <<'JSON'
{"903": {"baseRefName": "main"}}
JSON
log_n="$TMP_DIR/n.log"
out_n="$(run_ms "$scenario_n" "$log_n" --trunk main --accepted "$TMP_DIR/does-not-exist.txt" 903 2>&1)"
rc_n=$?
if [ "$rc_n" -eq 2 ] && grep -q "USAGE: --accepted file not found" <<<"$out_n"; then
  pass n "a missing --accepted file exits 2 with a USAGE token"
else
  printf '  out=%s\n' "$out_n"
  fail n "a missing --accepted file exits 2 with a USAGE token"
fi

# --- case (o): --repo owner/name is passed on every gh call ---
scenario_o="$TMP_DIR/o.json"
cat > "$scenario_o" <<'JSON'
{
  "1001": {
    "baseRefName": "main",
    "states": [{"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "statusCheckRollup": []}],
    "ready": "ok", "merge": "ok",
    "mergeCommit": "333333333333333333333333333333333333333c"
  },
  "1002": {
    "baseRefName": "main",
    "precheck": {"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN"},
    "states": [{"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "statusCheckRollup": []}],
    "ready": "ok", "merge": "ok",
    "mergeCommit": "444444444444444444444444444444444444444c"
  }
}
JSON
log_o="$TMP_DIR/o.log"
out_o="$(run_ms "$scenario_o" "$log_o" --trunk main --repo acme/widgets --poll-seconds 0 1001 1002 2>&1)"
rc_o=$?
total_lines_o="$(wc -l < "$log_o" | tr -d ' ')"
repo_lines_o="$(grep -c -- '--repo acme/widgets' "$log_o")"
if [ "$rc_o" -eq 0 ] && [ "$total_lines_o" -gt 0 ] && [ "$total_lines_o" = "$repo_lines_o" ]; then
  pass o "--repo owner/name is present on every gh call"
else
  printf '  out=%s\n  log=%s\n' "$out_o" "$(cat "$log_o")"
  fail o "--repo owner/name is present on every gh call"
fi

# --- case (p): the post-merge read does not confirm MERGED with a 40-hex
# oid -> exit 6 MERGE_UNVERIFIED ---
scenario_p="$TMP_DIR/p.json"
cat > "$scenario_p" <<'JSON'
{
  "1101": {
    "baseRefName": "main",
    "states": [{"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "statusCheckRollup": []}],
    "ready": "ok", "merge": "ok",
    "state": "OPEN"
  }
}
JSON
log_p="$TMP_DIR/p.log"
out_p="$(run_ms "$scenario_p" "$log_p" --trunk main --poll-seconds 0 1101 2>&1)"
rc_p=$?
if [ "$rc_p" -eq 6 ] && grep -q "MERGE_UNVERIFIED" <<<"$out_p" && grep -q "1101" <<<"$out_p"; then
  pass p "an unmerged/invalid post-merge read exits 6 with MERGE_UNVERIFIED"
else
  printf '  out=%s\n' "$out_p"
  fail p "an unmerged/invalid post-merge read exits 6 with MERGE_UNVERIFIED"
fi

# --- case (q): gh pr ready itself fails -> exit 7 READY_FAILED ---
scenario_q="$TMP_DIR/q.json"
cat > "$scenario_q" <<'JSON'
{
  "1201": {
    "baseRefName": "main",
    "ready": "refuse"
  }
}
JSON
log_q="$TMP_DIR/q.log"
out_q="$(run_ms "$scenario_q" "$log_q" --trunk main --poll-seconds 0 1201 2>&1)"
rc_q=$?
if [ "$rc_q" -eq 7 ] && grep -q "READY_FAILED" <<<"$out_q" && grep -q "1201" <<<"$out_q" && ! grep -qE '^pr merge' "$log_q"; then
  pass q "gh pr ready itself failing exits 7 with READY_FAILED"
else
  printf '  out=%s\n  log=%s\n' "$out_q" "$(cat "$log_q")"
  fail q "gh pr ready itself failing exits 7 with READY_FAILED"
fi

printf '\nmerge-station.test: %s passed, %s failed\n' "$PASS" "$FAIL"
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
