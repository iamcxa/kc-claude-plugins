#!/usr/bin/env bash
# Behavior contract for kc-ship-flow/scripts/notify.sh.

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
NOTIFY="$HERE/notify.sh"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

PASS=0
FAIL=0

pass() { printf 'ok - %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf 'not ok - %s\n' "$1"; FAIL=$((FAIL + 1)); }

doc="$TMP_DIR/doc.md"
echo "# UAT" > "$doc"

# (a) two dry-run calls for the same batch: second one skips, one marker written
state_a="$TMP_DIR/state-a"
out1=$(bash "$NOTIFY" "#ship" batch-a "$doc" --dry-run --state-dir "$state_a" 2>&1)
rc1=$?
out2=$(bash "$NOTIFY" "#ship" batch-a "$doc" --dry-run --state-dir "$state_a" 2>&1)
rc2=$?
if [ "$rc1" -eq 0 ] && [ "$rc2" -eq 0 ] && grep -q "sent" <<<"$out1" && grep -q "skip" <<<"$out2"; then
  pass "second dry-run call for the same batch id skips"
else
  printf '  out1=%s\n  out2=%s\n' "$out1" "$out2"
  fail "second dry-run call for the same batch id skips"
fi
if [ "$(find "$state_a" -maxdepth 1 -name 'sent-batch-a.json' | wc -l | tr -d ' ')" = "1" ]; then
  pass "exactly one marker file exists after two dry-run calls"
else
  fail "exactly one marker file exists after two dry-run calls"
fi
if python3 -c "import json,sys; sys.exit(0 if json.load(open(sys.argv[1])).get('dry_run') is True else 1)" \
    "$state_a/sent-batch-a.json"; then
  pass "marker records dry_run: true"
else
  fail "marker records dry_run: true"
fi
if [ ! -e "$state_a/sent-batch-a.lock" ]; then
  pass "lock dir does not persist after a successful call"
else
  fail "lock dir does not persist after a successful call"
fi

# (b) a held lock refuses a concurrent write instead of double-sending
state_b="$TMP_DIR/state-b"
mkdir -p "$state_b"
mkdir "$state_b/sent-batch-b.lock"
out3=$(bash "$NOTIFY" "#ship" batch-b "$doc" --dry-run --state-dir "$state_b" 2>&1)
rc3=$?
if [ "$rc3" -ne 0 ] && grep -qi "concurrent" <<<"$out3"; then
  pass "a held lock refuses a second writer instead of racing the marker"
else
  printf '  out3=%s\n' "$out3"
  fail "a held lock refuses a second writer instead of racing the marker"
fi
rmdir "$state_b/sent-batch-b.lock"

# (c) a non-dry-run call is refused outright when no marker exists yet
state_c="$TMP_DIR/state-c"
out4=$(bash "$NOTIFY" "#ship" batch-c "$doc" --state-dir "$state_c" 2>&1)
rc4=$?
if [ "$rc4" -ne 0 ] && grep -qi "dry-run is required" <<<"$out4"; then
  pass "a non-dry-run call with no prior marker is refused"
else
  fail "a non-dry-run call with no prior marker is refused"
fi

# (d) a non-dry-run call must NOT be skipped by a pre-existing dry-run marker
state_d="$TMP_DIR/state-d"
mkdir -p "$state_d"
cat > "$state_d/sent-batch-d.json" <<'JSON'
{"batch_id": "batch-d", "channel": "#ship", "message_id": "msg-fixture", "dry_run": true, "sent_at": "2026-01-01T00:00:00Z"}
JSON
out5=$(bash "$NOTIFY" "#ship" batch-d "$doc" --state-dir "$state_d" 2>&1)
rc5=$?
if [ "$rc5" -ne 0 ] && grep -qi "refusing" <<<"$out5" && ! grep -qi "skip" <<<"$out5"; then
  pass "a non-dry-run call is not skipped by a dry-run-only marker"
else
  printf '  out5=%s\n' "$out5"
  fail "a non-dry-run call is not skipped by a dry-run-only marker"
fi

# (e) a dry-run call after that same dry-run marker still skips normally
out6=$(bash "$NOTIFY" "#ship" batch-d "$doc" --dry-run --state-dir "$state_d" 2>&1)
rc6=$?
if [ "$rc6" -eq 0 ] && grep -qi "skip" <<<"$out6"; then
  pass "a dry-run call after a dry-run marker still skips"
else
  fail "a dry-run call after a dry-run marker still skips"
fi

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
