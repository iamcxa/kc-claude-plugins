#!/usr/bin/env bash
# Fixtures: kc-ship-flow/scripts/fixtures/watch/, fixtures/fake-conductor-watch/.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/watch.sh"
FIXTURES="$HERE/fixtures/watch"
FAKE_CONDUCTOR_DIR="$HERE/fixtures/fake-conductor-watch"

PASS=0
FAIL=0
pass() { printf 'case %s: PASS - %s\n' "$1" "$2"; PASS=$((PASS + 1)); }
fail() { printf 'case %s: FAIL - %s\n' "$1" "$2"; FAIL=$((FAIL + 1)); }

TRANSCRIPTS="$(mktemp)"
cat > "$TRANSCRIPTS" <<EOF
{
  "sess-quota": "## User\n\ncontinue\n\n## Assistant\n\nYou've hit your session limit · resets 9pm (Asia/Taipei)",
  "sess-question": "## User\n\ngo\n\n## Assistant\n\nTwo files touch this rename. Should I update both, or just the one named in the task?",
  "sess-stopped": "## User\n\ngo\n\n## Assistant\n\nDone. Pushed the branch and opened the draft PR.",
  "sess-resumed-after-quota": "## Assistant\n\nYou've hit your session limit · resets 9pm (Asia/Taipei)\n\n## User\n\ncontinue\n\n## Assistant\n\nResumed and finished the refactor; running the tests now.",
  "sess-quote-slug": "## Assistant\n\nDone. Nothing else to report.",
  "sess-folder-gate": "## Assistant\n\nirrelevant -- gate-prepared must short-circuit before this is ever read.",
  "sess-question-q-marker": "## User\n\ngo\n\n## Assistant\n\nRenaming both call sites now.\n\nQ: should the deprecated alias stay for one release or be removed outright?",
  "sess-question-decision-marker": "## User\n\ngo\n\n## Assistant\n\nDecision: I will treat the missing config key as a hard failure rather than defaulting it, unless told otherwise."
}
EOF

WORKSPACE_STATUS="$FIXTURES/state/workspace-status.json"

LOG="$(mktemp)"
run_watch() {
  local state_dir="$1"
  FAKE_CONDUCTOR_TRANSCRIPTS="$TRANSCRIPTS" FAKE_CONDUCTOR_LOG="$LOG" \
    FAKE_CONDUCTOR_WORKSPACE_STATUS="$WORKSPACE_STATUS" \
    PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
    bash "$SCRIPT" ship-cloud-wrapper --once \
    --workflow-dir "$FIXTURES/dev" --state-dir "$state_dir" 2>&1
}

fresh_state() {
  local d
  d="$(mktemp -d)"
  cp -r "$FIXTURES/state/_ship_fence" "$d/"
  printf '%s' "$d"
}

STATE_A="$(fresh_state)"
: > "$LOG"
out_a1="$(run_watch "$STATE_A")"
rc_a1=$?
ok=1
[ "$rc_a1" -eq 0 ] || ok=0
grep -qx "task-gate-prepared gate-prepared" <<<"$out_a1" || ok=0
grep -qx "task-folder-gate gate-prepared" <<<"$out_a1" || ok=0
grep -q "^task-gate-prepared-no-pr question" <<<"$out_a1" || ok=0
grep -qx "task-pending pending" <<<"$out_a1" || ok=0
grep -qx "task-quota quota" <<<"$out_a1" || ok=0
grep -qx "task-question question" <<<"$out_a1" || ok=0
grep -qx "task-question-q-marker question" <<<"$out_a1" || ok=0
grep -qx "task-question-decision-marker question" <<<"$out_a1" || ok=0
grep -qx "task-stopped stopped" <<<"$out_a1" && ok=0
grep -qx "task-resumed-after-quota stopped" <<<"$out_a1" && ok=0
grep -qx "it's-a-slug stopped" <<<"$out_a1" && ok=0
if [ "$ok" = 1 ]; then
  pass a "first poll: every decisive signal fires immediately, stopped-candidates wait"
else
  printf '  out=%s\n' "$out_a1"
  fail a "first poll: every decisive signal fires immediately, stopped-candidates wait"
fi

if grep -qx "task-quota quota" <<<"$out_a1"; then
  pass b "usage-limit banner yields quota, not stopped"
else
  fail b "usage-limit banner yields quota, not stopped"
fi

if ! grep -q "sess-gate-prepared\|sess-folder-gate" "$LOG"; then
  pass c "gate-prepared short-circuits before any session/sql call"
else
  printf '  log=%s\n' "$(cat "$LOG")"
  fail c "gate-prepared short-circuits before any session/sql call"
fi

if ! grep -q "sess-gate-prepared-no-pr" "$LOG"; then
  pass q "prepared-but-empty-pr also short-circuits before any session/sql call (AC-3)"
else
  printf '  log=%s\n' "$(cat "$LOG")"
  fail q "prepared-but-empty-pr also short-circuits before any session/sql call (AC-3)"
fi

out_a2="$(run_watch "$STATE_A")"
if grep -qx "task-stopped stopped" <<<"$out_a2" \
  && grep -qx "task-resumed-after-quota stopped" <<<"$out_a2" \
  && grep -qx "it's-a-slug stopped" <<<"$out_a2"; then
  pass d "second consecutive idle poll confirms stopped"
else
  printf '  out=%s\n' "$out_a2"
  fail d "second consecutive idle poll confirms stopped"
fi
rm -rf "$STATE_A"

if grep -qx "task-resumed-after-quota stopped" <<<"$out_a2"; then
  pass e "a resolved earlier banner reads as stopped, not quota, once the tail has moved on"
else
  fail e "a resolved earlier banner reads as stopped, not quota, once the tail has moved on"
fi

if grep -qx "it's-a-slug stopped" <<<"$out_a2"; then
  pass f "a slug containing a single quote is handled as data"
else
  fail f "a slug containing a single quote is handled as data"
fi

if grep -qx "task-pending pending" <<<"$out_a1"; then
  pass g "workspace initializing reads as pending"
else
  fail g "workspace initializing reads as pending"
fi

if grep -qx "task-folder-gate gate-prepared" <<<"$out_a1"; then
  pass h "folder-form entity (<slug>/index.md) gate-prepared is read"
else
  fail h "folder-form entity (<slug>/index.md) gate-prepared is read"
fi

if grep -qx "task-question question" <<<"$out_a1" \
  && grep -qx "task-question-q-marker question" <<<"$out_a1" \
  && grep -qx "task-question-decision-marker question" <<<"$out_a1"; then
  pass i "question recognized 3/3 across the '?', 'Q:', and 'Decision:' shapes"
else
  fail i "question recognized 3/3 across the '?', 'Q:', and 'Decision:' shapes"
fi

STATE_J="$(fresh_state)"
out_j="$(FAKE_CONDUCTOR_TRANSCRIPTS="$TRANSCRIPTS" FAKE_CONDUCTOR_DROP_SHAPE="workspace status" \
  FAKE_CONDUCTOR_WORKSPACE_STATUS="$WORKSPACE_STATUS" \
  PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" ship-cloud-wrapper --once \
  --workflow-dir "$FIXTURES/dev" --state-dir "$STATE_J" 2>&1)"
rc_j=$?
rm -rf "$STATE_J"
if [ "$rc_j" -eq 5 ] && grep -q "workspace status" <<<"$out_j"; then
  pass j "used-surface contract mismatch refuses (exit 5, names the missing shape)"
else
  printf '  out=%s\n' "$out_j"
  fail j "used-surface contract mismatch refuses (exit 5, names the missing shape)"
fi

STATE_K="$(fresh_state)"
out_k="$(FAKE_CONDUCTOR_TRANSCRIPTS="$TRANSCRIPTS" FAKE_CONDUCTOR_VERSION="9.9.9" \
  FAKE_CONDUCTOR_WORKSPACE_STATUS="$WORKSPACE_STATUS" \
  PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" ship-cloud-wrapper --once \
  --workflow-dir "$FIXTURES/dev" --state-dir "$STATE_K" 2>&1)"
rc_k=$?
rm -rf "$STATE_K"
if [ "$rc_k" -eq 0 ] && grep -q "conductor 9.9.9: used surface unchanged" <<<"$out_k"; then
  pass k "version-only change proceeds and prints the version, unchanged-surface line"
else
  printf '  out=%s\n' "$out_k"
  fail k "version-only change proceeds and prints the version, unchanged-surface line"
fi

# --- sql-503-degraded path (AC-1..AC-4): same fixture entities/fence, driven through
# `session message` instead of `sql`, forced via FAKE_CONDUCTOR_SQL_FAIL. ---
SESSION_MESSAGES="$FIXTURES/session-messages.json"

DEGRADED_LOG="$(mktemp)"
run_watch_degraded() {
  local state_dir="$1"
  FAKE_CONDUCTOR_SQL_FAIL=1 FAKE_CONDUCTOR_SESSION_MESSAGES="$SESSION_MESSAGES" \
    FAKE_CONDUCTOR_LOG="$DEGRADED_LOG" \
    FAKE_CONDUCTOR_WORKSPACE_STATUS="$WORKSPACE_STATUS" \
    PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
    bash "$SCRIPT" ship-cloud-wrapper --once \
    --workflow-dir "$FIXTURES/dev" --state-dir "$state_dir" 2>&1
}

STATE_L="$(fresh_state)"
: > "$DEGRADED_LOG"
out_l1="$(run_watch_degraded "$STATE_L")"
rc_l1=$?
ok=1
[ "$rc_l1" -eq 0 ] || ok=0
grep -qx "task-gate-prepared gate-prepared" <<<"$out_l1" || ok=0
grep -qx "task-folder-gate gate-prepared" <<<"$out_l1" || ok=0
grep -q "^task-gate-prepared-no-pr question" <<<"$out_l1" || ok=0
grep -qx "task-pending pending" <<<"$out_l1" || ok=0
grep -qx "task-quota quota" <<<"$out_l1" || ok=0
grep -qx "task-question question" <<<"$out_l1" || ok=0
grep -qx "task-question-q-marker question" <<<"$out_l1" || ok=0
grep -qx "task-question-decision-marker question" <<<"$out_l1" || ok=0
grep -qx "task-stopped stopped" <<<"$out_l1" && ok=0
grep -qx "task-resumed-after-quota stopped" <<<"$out_l1" && ok=0
grep -qx "it's-a-slug stopped" <<<"$out_l1" && ok=0
if [ "$ok" = 1 ]; then
  pass l "degraded (sql-503) first poll: same decisive signals as the sql-available path (AC-2)"
else
  printf '  out=%s\n' "$out_l1"
  fail l "degraded (sql-503) first poll: same decisive signals as the sql-available path (AC-2)"
fi

if ! grep -q "session_transcripts_view" "$DEGRADED_LOG"; then
  pass m "degraded run never queries session_transcripts_view; tail reads go through session message (AC-2)"
else
  printf '  log=%s\n' "$(cat "$DEGRADED_LOG")"
  fail m "degraded run never queries session_transcripts_view; tail reads go through session message (AC-2)"
fi

out_l2="$(run_watch_degraded "$STATE_L")"
if grep -qx "task-stopped stopped" <<<"$out_l2" \
  && grep -qx "task-resumed-after-quota stopped" <<<"$out_l2" \
  && grep -qx "it's-a-slug stopped" <<<"$out_l2"; then
  pass n "degraded: second consecutive idle poll confirms stopped, same as the sql-available path (AC-3)"
else
  printf '  out=%s\n' "$out_l2"
  fail n "degraded: second consecutive idle poll confirms stopped, same as the sql-available path (AC-3)"
fi
rm -rf "$STATE_L"

STATE_O="$(fresh_state)"
run_watch_degraded "$STATE_O" >/dev/null
line_count=$(wc -l < "$STATE_O/_ship_questions/ship-cloud-wrapper.log" 2>/dev/null | tr -d ' ')
today="$(date -u +%Y-%m-%d)"
ok=1
[ "$line_count" = 1 ] || ok=0
grep -q "sql-503" "$STATE_O/_ship_questions/ship-cloud-wrapper.log" 2>/dev/null || ok=0
grep -q "$today" "$STATE_O/_ship_questions/ship-cloud-wrapper.log" 2>/dev/null || ok=0
grep -q "503" "$STATE_O/_ship_questions/ship-cloud-wrapper.log" 2>/dev/null || ok=0
if [ "$ok" = 1 ]; then
  pass o "questions log gets exactly one line naming sql-503, the probe output, and today's date (AC-4)"
else
  printf '  log=%s\n' "$(cat "$STATE_O/_ship_questions/ship-cloud-wrapper.log" 2>/dev/null)"
  fail o "questions log gets exactly one line naming sql-503, the probe output, and today's date (AC-4)"
fi
rm -rf "$STATE_O"

STATE_P="$(fresh_state)"
out_p="$(run_watch "$STATE_P")"
rc_p=$?
ok=1
[ "$rc_p" -eq 0 ] || ok=0
[ ! -e "$STATE_P/_ship_questions" ] || ok=0
rm -rf "$STATE_P"
if [ "$ok" = 1 ]; then
  pass p "sql-available run never writes the questions log (no degraded transition to record)"
else
  fail p "sql-available run never writes the questions log (no degraded transition to record)"
fi

rm -f "$TRANSCRIPTS" "$LOG" "$DEGRADED_LOG"

printf '\nwatch.test: %s passed, %s failed\n' "$PASS" "$FAIL"
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
