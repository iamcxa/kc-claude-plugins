#!/usr/bin/env bash
# Behavior contract for kc-ship-flow/scripts/watch.sh, against the fixtures under
# kc-ship-flow/scripts/fixtures/watch/. Requires the real `conductor` CLI on PATH (used
# only for --version/--help, which the fake conductor delegates to it) -- fails closed
# rather than skipping when absent, so a runner missing it never reports a false PASS.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/watch.sh"
FIXTURES="$HERE/fixtures/watch"
FAKE_CONDUCTOR_DIR="$HERE/fixtures/fake-conductor-watch"

if ! command -v conductor >/dev/null 2>&1; then
  echo "conductor required on PATH" >&2
  exit 1
fi
REAL_CONDUCTOR="$(command -v conductor)"

PASS=0
FAIL=0
pass() { printf 'case %s: PASS - %s\n' "$1" "$2"; PASS=$((PASS + 1)); }
fail() { printf 'case %s: FAIL - %s\n' "$1" "$2"; FAIL=$((FAIL + 1)); }

TRANSCRIPTS="$(mktemp)"
cat > "$TRANSCRIPTS" <<EOF
{
  "sess-quota": "## User\n\ncontinue\n\n## Assistant\n\nYou've hit your session limit · resets 9pm (Asia/Taipei)",
  "sess-question": "## User\n\ngo\n\n## Assistant\n\nTwo files touch this rename. Should I update both, or just the one named in the task?",
  "sess-stopped": "## User\n\ngo\n\n## Assistant\n\nDone. Pushed the branch and opened the draft PR."
}
EOF

LOG="$(mktemp)"
run_watch() {
  FAKE_CONDUCTOR_REAL="$REAL_CONDUCTOR" FAKE_CONDUCTOR_TRANSCRIPTS="$TRANSCRIPTS" FAKE_CONDUCTOR_LOG="$LOG" \
    PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
    bash "$SCRIPT" ship-cloud-wrapper --once \
    --workflow-dir "$FIXTURES/dev" --state-dir "$FIXTURES/state" 2>&1
}

# --- case (a): one line per task, the four expected exits, gate-prepared without any
# session/sql call (checked via the log: no session-status or sql call for that slug's
# session id) ---
out_a="$(run_watch)"
rc_a=$?
: > "$LOG"
if [ "$rc_a" -eq 0 ] \
  && grep -qx "task-gate-prepared gate-prepared" <<<"$out_a" \
  && grep -qx "task-quota quota" <<<"$out_a" \
  && grep -qx "task-question question" <<<"$out_a" \
  && grep -qx "task-stopped stopped" <<<"$out_a"; then
  pass a "one line per task with the four expected exits"
else
  printf '  out=%s\n' "$out_a"
  fail a "one line per task with the four expected exits"
fi

# --- case (b): the usage-limit banner in a transcript yields quota, not stopped, even
# though the transcript also ends the assistant turn with plain prose (proves the quota
# check runs before the question/stopped fallback) ---
if grep -qx "task-quota quota" <<<"$out_a"; then
  pass b "usage-limit banner yields quota, not stopped"
else
  fail b "usage-limit banner yields quota, not stopped"
fi

# --- case (c): a gate already prepared is reported without consulting the session at
# all -- the fixture's session id for that task (sess-gate-prepared) never appears in
# either fake conductor's session-status or sql calls ---
run_watch >/dev/null
if ! grep -q "sess-gate-prepared" "$LOG"; then
  pass c "gate-prepared short-circuits before any session/sql call"
else
  printf '  log=%s\n' "$(cat "$LOG")"
  fail c "gate-prepared short-circuits before any session/sql call"
fi

# --- case (d): the CLI pin mismatch refusal applies to watch.sh too -- exit 5, a diff
# printed, and no other call made (the fake conductor errors loudly on anything past
# --version/--help when the pin does not match, since the script must not get there) ---
BAD_PIN_DIR="$(mktemp -d)"
mkdir -p "$BAD_PIN_DIR/kc-ship-flow/scripts" "$BAD_PIN_DIR/kc-ship-flow/pins"
cp "$SCRIPT" "$BAD_PIN_DIR/kc-ship-flow/scripts/watch.sh"
printf '9.9.9\nsomething else entirely\n' > "$BAD_PIN_DIR/kc-ship-flow/pins/conductor-cli.txt"
out_d="$(FAKE_CONDUCTOR_REAL="$REAL_CONDUCTOR" FAKE_CONDUCTOR_TRANSCRIPTS="$TRANSCRIPTS" \
  PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$BAD_PIN_DIR/kc-ship-flow/scripts/watch.sh" ship-cloud-wrapper --once \
  --workflow-dir "$FIXTURES/dev" --state-dir "$FIXTURES/state" 2>&1)"
rc_d=$?
rm -rf "$BAD_PIN_DIR"
if [ "$rc_d" -eq 5 ] && grep -q "conductor cli changed" <<<"$out_d"; then
  pass d "pin mismatch refuses (exit 5, conductor cli changed)"
else
  printf '  out=%s\n' "$out_d"
  fail d "pin mismatch refuses (exit 5, conductor cli changed)"
fi

rm -f "$TRANSCRIPTS" "$LOG"

printf '\nwatch.test: %s passed, %s failed\n' "$PASS" "$FAIL"
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
