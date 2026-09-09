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

# Fail closed, never skip: a runner without the pinned Spacedock binary must
# not report a false PASS by silently exercising nothing.
if ! command -v spacedock >/dev/null 2>&1; then
  echo "spacedock required" >&2
  exit 1
fi

PASS=0
FAIL=0

pass() { printf 'case %s: PASS - %s\n' "$1" "$2"; PASS=$((PASS + 1)); }
fail() { printf 'case %s: FAIL - %s\n' "$1" "$2"; FAIL=$((FAIL + 1)); }

# --- case (a): a stage that declares a model produces a create argv
# carrying that model, and the printed message sha256 matches an independent
# hash of the artifact spacedock itself wrote to disk ---
out_a="$(bash "$STATION" "$STATE" h1 1 dev-1.g1 "$UUID" main \
  --entity-path "$FIXTURES/task-with-model.md" --stage implementation \
  --workflow-dir "$FIXTURES/task-with-model" --dry-run 2>&1)"
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
# no --model ---
out_b="$(bash "$STATION" "$STATE" h1 1 dev-1.g1 "$UUID" main \
  --entity-path "$FIXTURES/task-without-model.md" --stage implementation \
  --workflow-dir "$FIXTURES/task-without-model" --dry-run 2>&1)"
rc_b=$?
if [ "$rc_b" -eq 0 ] && ! grep -q -- "--model" <<<"$out_b"; then
  pass b "no-model stage carries no --model"
else
  printf '  out=%s\n' "$out_b"
  fail b "no-model stage carries no --model"
fi

# --- case (c): a stage the workflow README never defines makes spacedock
# dispatch build exit non-zero, and the station refuses (exit 4) rather than
# falling back to an inline message ---
out_c="$(bash "$STATION" "$STATE" h1 1 dev-1.g1 "$UUID" main \
  --entity-path "$FIXTURES/task-build-fails.md" --stage nonexistent-stage \
  --workflow-dir "$FIXTURES/task-build-fails" --dry-run 2>&1)"
rc_c=$?
if [ "$rc_c" -eq 4 ] && grep -q "dispatch build failed" <<<"$out_c"; then
  pass c "undeclared stage refuses (exit 4, dispatch build failed)"
else
  printf '  out=%s\n' "$out_c"
  fail c "undeclared stage refuses (exit 4, dispatch build failed)"
fi

# --- case (d): the message body carries no station-authored text beyond the
# one procedural checklist line -- rebuild the artifact directly through
# `spacedock dispatch build` with that exact checklist content and require a
# byte-for-byte sha256 match against the station's own printed message sha.
# Any text the station added to (or removed from) the message after dispatch
# build produced it would break this equality ---
out_d="$(bash "$STATION" "$STATE" h1 1 dev-1.g1 "$UUID" main \
  --entity-path "$FIXTURES/task-without-model.md" --stage implementation \
  --workflow-dir "$FIXTURES/task-without-model" --dry-run 2>&1)"
sha_d="$(printf '%s\n' "$out_d" | sed -n 's/^message_sha256=//p')"
checklist_d="$(mktemp)"
printf "DONE: complete stage implementation per the workflow's own stage contract.\n" >"$checklist_d"
build_d="$(spacedock dispatch build --workflow-dir "$FIXTURES/task-without-model" \
  --entity-path "$FIXTURES/task-without-model.md" --stage implementation \
  --checklist-file "$checklist_d" --host claude 2>/dev/null)"
rm -f "$checklist_d"
msg_path_d="$(printf '%s' "$build_d" | python3 -c "import json,sys; print(json.load(sys.stdin)['dispatch_file_path'])")"
want_sha_d="$(sha256sum "$msg_path_d" | cut -d' ' -f1)"
if [ -n "$sha_d" ] && [ "$sha_d" = "$want_sha_d" ]; then
  pass d "message body carries no station-authored text beyond the checklist line"
else
  printf '  sha_d=%s want=%s\n' "$sha_d" "$want_sha_d"
  fail d "message body carries no station-authored text beyond the checklist line"
fi

printf '\nfenced-dispatch.test: %s passed, %s failed\n' "$PASS" "$FAIL"
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
