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

rm -f "$TRANSCRIPTS" "$LOG"

printf '\nwatch.test: %s passed, %s failed\n' "$PASS" "$FAIL"
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
