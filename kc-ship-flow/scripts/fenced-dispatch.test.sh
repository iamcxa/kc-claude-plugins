#!/usr/bin/env bash
# Behavior contract for kc-ship-flow/scripts/fenced-dispatch.sh, driven through
# synthetic fixtures under kc-ship-flow/scripts/fixtures/dispatch/.
#
# Self-check -- prove this suite actually catches a reverted station (manual,
# not one of the cases below, and not run by this file itself):
#   cp kc-ship-flow/scripts/fenced-dispatch.sh /tmp/fenced-dispatch.sh.orig
#   git -C kc-ship-flow show HEAD~1:kc-ship-flow/scripts/fenced-dispatch.sh > kc-ship-flow/scripts/fenced-dispatch.sh
#   bash kc-ship-flow/scripts/fenced-dispatch.test.sh; echo "exit: $?"
#   cp /tmp/fenced-dispatch.sh.orig kc-ship-flow/scripts/fenced-dispatch.sh
# Expect at least one FAIL line and a non-zero exit: the pre-DEV-156 script
# takes a message-file positional and a fixed haiku-4-5/low pair, so it either
# errors on the new flag shape or never varies --model by stage.

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
STATION="$HERE/fenced-dispatch.sh"
FIXTURES="$HERE/fixtures/dispatch"
STATE="/tmp/kc-ship-flow-fenced-dispatch-test-state"
UUID="00000000-0000-0000-0000-000000000000"

PASS=0
FAIL=0

pass() { printf 'case %s: PASS - %s\n' "$1" "$2"; PASS=$((PASS + 1)); }
fail() { printf 'case %s: FAIL - %s\n' "$1" "$2"; FAIL=$((FAIL + 1)); }

# --- case (a): a stage that declares a model produces a create argv
# carrying that model, and the printed message sha256 matches an independent
# hash of the artifact spacedock itself wrote to disk ---
out_a="$(bash "$STATION" "$STATE" h1 1 dev-1.g1 "$UUID" main \
  --entity-path "$FIXTURES/task-with-model.md" --stage implementation --dry-run 2>&1)"
rc_a=$?
sha_a="$(printf '%s\n' "$out_a" | sed -n 's/^message_sha256=//p')"
build_a="$(spacedock dispatch build --workflow-dir "$FIXTURES/task-with-model" \
  --entity-path "$FIXTURES/task-with-model.md" --stage implementation \
  --checklist-file <(echo "DONE: complete stage implementation per the workflow's own stage contract.") \
  --host claude 2>/dev/null)"
msg_path_a="$(printf '%s' "$build_a" | python3 -c "import json,sys; print(json.load(sys.stdin)['dispatch_file_path'])")"
want_sha_a="$(sha256sum "$msg_path_a" | cut -d' ' -f1)"
if [ "$rc_a" -eq 0 ] && grep -q -- "--model sonnet" <<<"$out_a" && [ "$sha_a" = "$want_sha_a" ]; then
  pass a "model-declaring stage carries --model sonnet and a matching message sha256"
else
  printf '  out=%s\n  sha_a=%s want=%s\n' "$out_a" "$sha_a" "$want_sha_a"
  fail a "model-declaring stage carries --model sonnet and a matching message sha256"
fi

# --- case (b): a stage that declares no model produces a create argv with
# neither --model nor --effort ---
out_b="$(bash "$STATION" "$STATE" h1 1 dev-1.g1 "$UUID" main \
  --entity-path "$FIXTURES/task-without-model.md" --stage implementation --dry-run 2>&1)"
rc_b=$?
if [ "$rc_b" -eq 0 ] && ! grep -q -- "--model" <<<"$out_b" && ! grep -q -- "--effort" <<<"$out_b"; then
  pass b "no-model stage carries neither --model nor --effort"
else
  printf '  out=%s\n' "$out_b"
  fail b "no-model stage carries neither --model nor --effort"
fi

# --- case (c): a stage the workflow README never defines makes spacedock
# dispatch build exit non-zero, and the station refuses (exit 4) rather than
# falling back to an inline message ---
out_c="$(bash "$STATION" "$STATE" h1 1 dev-1.g1 "$UUID" main \
  --entity-path "$FIXTURES/task-build-fails.md" --stage nonexistent-stage --dry-run 2>&1)"
rc_c=$?
if [ "$rc_c" -eq 4 ] && grep -q "dispatch build failed" <<<"$out_c"; then
  pass c "undeclared stage refuses (exit 4, dispatch build failed)"
else
  printf '  out=%s\n' "$out_c"
  fail c "undeclared stage refuses (exit 4, dispatch build failed)"
fi

printf '\nfenced-dispatch.test: %s passed, %s failed\n' "$PASS" "$FAIL"
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
