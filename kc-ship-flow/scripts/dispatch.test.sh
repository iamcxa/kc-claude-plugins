#!/usr/bin/env bash
# Behavior contract for kc-ship-flow/scripts/dispatch.sh, against the fixture workflow under
# kc-ship-flow/scripts/fixtures/dispatch-argv/dev/. Requires the real `conductor` CLI on PATH
# (used only for --version/--help, which the fake conductor delegates to it) and `spacedock`
# (to resolve entity paths) -- fails closed rather than skipping when either is absent.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/dispatch.sh"
FIXTURES="$HERE/fixtures/dispatch-argv"
FAKE_CONDUCTOR_DIR="$HERE/fixtures/fake-conductor-dispatch"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"

if ! command -v conductor >/dev/null 2>&1; then
  echo "conductor required on PATH" >&2
  exit 1
fi
if ! command -v spacedock >/dev/null 2>&1; then
  echo "spacedock required on PATH" >&2
  exit 1
fi
REAL_CONDUCTOR="$(command -v conductor)"
REAL_REMOTE="$(git -C "$REPO_ROOT" remote get-url origin)"
FIXTURE_PROJECT_ID="11111111-1111-1111-1111-111111111111"

PASS=0
FAIL=0
pass() { printf 'case %s: PASS - %s\n' "$1" "$2"; PASS=$((PASS + 1)); }
fail() { printf 'case %s: FAIL - %s\n' "$1" "$2"; FAIL=$((FAIL + 1)); }

STATE_DIR="$(mktemp -d)"
LOG="$(mktemp)"

run_dispatch() {
  FAKE_CONDUCTOR_REAL="$REAL_CONDUCTOR" FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" \
    FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" FAKE_CONDUCTOR_LOG="$LOG" \
    PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
    bash "$SCRIPT" ship-cloud-wrapper-fixture --dry-run \
    --workflow-dir "$FIXTURES/dev" --state-dir "$STATE_DIR" 2>&1
}

# --- case (a): one create argv per ready task (the sprint-readiness: blocked fixture is
# excluded), each carrying --project-id resolved from the repo remote and a --message-file
# whose sha256 matches the printed message_sha256 line, and exit 0. No `workspace create`
# call happens (the fake conductor exits 64 if it ever sees one). ---
: > "$LOG"
out_a="$(run_dispatch)"
rc_a=$?
count_argv=$(grep -c "^conductor workspace create " <<<"$out_a")
ok=1
[ "$rc_a" -eq 0 ] || ok=0
[ "$count_argv" -eq 2 ] || ok=0
grep -q "task-ready-one" <<<"$out_a" || ok=0
grep -q "task-ready-two" <<<"$out_a" || ok=0
grep -q "task-not-ready" <<<"$out_a" && ok=0
grep -q -- "--project-id $FIXTURE_PROJECT_ID" <<<"$out_a" || ok=0
if grep -q "workspace create" "$LOG" 2>/dev/null; then ok=0; fi
while IFS= read -r msgfile; do
  sha="$(sha256sum "$msgfile" | cut -d' ' -f1)"
  grep -q "message_sha256=$sha" <<<"$out_a" || ok=0
done < <(grep -oE -- '--message-file [^ ]+' <<<"$out_a" | cut -d' ' -f2)
if [ "$ok" = 1 ]; then
  pass a "one argv per ready task, project-id resolved, message sha256 matches, no create call"
else
  printf '  out=%s\n' "$out_a"
  fail a "one argv per ready task, project-id resolved, message sha256 matches, no create call"
fi

# --- case (b): a re-run against the same sprint after one task's fence record is already
# recorded reports that task already-recorded instead of printing another argv for it ---
mkdir -p "$STATE_DIR/_ship_fence"
python3 -c "
import json
json.dump({'task-ready-one': {'workspace': None, 'session': None, 'message_sha256': 'x'}}, open('$STATE_DIR/_ship_fence/ship-cloud-wrapper-fixture.json', 'w'))
"
out_b="$(run_dispatch)"
if grep -qx "task-ready-one already-recorded" <<<"$out_b" && [ "$(grep -c "^conductor workspace create " <<<"$out_b")" -eq 1 ] && grep -q "task-ready-two" <<<"$out_b"; then
  pass b "an already-recorded slug is skipped, not re-printed"
else
  printf '  out=%s\n' "$out_b"
  fail b "an already-recorded slug is skipped, not re-printed"
fi
rm -rf "$STATE_DIR/_ship_fence"

# --- case (c): conductor auth whoami failing refuses with exit 2 and "conductor unavailable",
# even in --dry-run ---
out_c="$(FAKE_CONDUCTOR_AUTH_FAIL=1 FAKE_CONDUCTOR_REAL="$REAL_CONDUCTOR" FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" \
  FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" ship-cloud-wrapper-fixture --dry-run \
  --workflow-dir "$FIXTURES/dev" --state-dir "$STATE_DIR" 2>&1)"
rc_c=$?
if [ "$rc_c" -eq 2 ] && grep -q "conductor unavailable" <<<"$out_c"; then
  pass c "conductor auth whoami failure refuses (exit 2, conductor unavailable)"
else
  printf '  out=%s\n' "$out_c"
  fail c "conductor auth whoami failure refuses (exit 2, conductor unavailable)"
fi

# --- case (d): a conductor CLI pin mismatch refuses (exit 5), prints a diff, and never
# reaches auth whoami or project list (the fake conductor errors loudly on anything past
# --version/--help) ---
BAD_PIN_DIR="$(mktemp -d)"
mkdir -p "$BAD_PIN_DIR/kc-ship-flow/scripts" "$BAD_PIN_DIR/kc-ship-flow/pins"
cp "$SCRIPT" "$BAD_PIN_DIR/kc-ship-flow/scripts/dispatch.sh"
printf '9.9.9\nsomething else entirely\n' > "$BAD_PIN_DIR/kc-ship-flow/pins/conductor-cli.txt"
out_d="$(FAKE_CONDUCTOR_REAL="$REAL_CONDUCTOR" FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" \
  FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$BAD_PIN_DIR/kc-ship-flow/scripts/dispatch.sh" ship-cloud-wrapper-fixture --dry-run \
  --workflow-dir "$FIXTURES/dev" --state-dir "$STATE_DIR" 2>&1)"
rc_d=$?
rm -rf "$BAD_PIN_DIR"
if [ "$rc_d" -eq 5 ] && grep -q "conductor cli changed" <<<"$out_d"; then
  pass d "pin mismatch refuses (exit 5, conductor cli changed, no other call)"
else
  printf '  out=%s\n' "$out_d"
  fail d "pin mismatch refuses (exit 5, conductor cli changed, no other call)"
fi

# --- case (e): real (non-dry-run) mode against a local bare-origin state checkout with no
# upstream configured on the created branch -- the claim fence commits locally (no-origin
# carve-out) and the workspace/session ids returned by `workspace create` land in the fence
# file, keyed by slug ---
REAL_STATE_ORIGIN="$(mktemp -d)"
REAL_STATE_WT="$(mktemp -d)"
git init -q --bare "$REAL_STATE_ORIGIN/origin.git"
git clone -q "$REAL_STATE_ORIGIN/origin.git" "$REAL_STATE_WT/seed" 2>/dev/null
git -C "$REAL_STATE_WT/seed" -c user.name=fixture -c user.email=fixture@example.test \
  commit -q --allow-empty -m seed
git -C "$REAL_STATE_WT/seed" push -q origin HEAD:refs/heads/main 2>/dev/null
git clone -q "$REAL_STATE_ORIGIN/origin.git" "$REAL_STATE_WT/wt" 2>/dev/null
git -C "$REAL_STATE_WT/wt" -c user.name=fixture -c user.email=fixture@example.test \
  checkout -q -b detached-no-upstream
REAL_STATE="$REAL_STATE_WT/wt"

out_e="$(FAKE_CONDUCTOR_REAL="$REAL_CONDUCTOR" FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" \
  FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" FAKE_CONDUCTOR_ALLOW_CREATE=1 \
  PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" ship-cloud-wrapper-fixture \
  --workflow-dir "$FIXTURES/dev" --state-dir "$REAL_STATE" 2>&1)"
rc_e=$?
fence_e="$REAL_STATE/_ship_fence/ship-cloud-wrapper-fixture.json"
recorded_ws="$(python3 -c "import json; print(json.load(open('$fence_e'))['task-ready-one']['workspace'])" 2>/dev/null)"
committed="$(git -C "$REAL_STATE" log --oneline -- _ship_fence 2>/dev/null | wc -l | tr -d ' ')"
rm -rf "$REAL_STATE_ORIGIN" "$REAL_STATE_WT"
if [ "$rc_e" -eq 0 ] && [ "$recorded_ws" = "ws-fixture-1" ] && [ "$committed" -ge 1 ]; then
  pass e "real mode commits the fence file locally and records the returned workspace id"
else
  printf '  out=%s recorded_ws=%s committed=%s\n' "$out_e" "$recorded_ws" "$committed"
  fail e "real mode commits the fence file locally and records the returned workspace id"
fi

rm -rf "$STATE_DIR"
rm -f "$LOG"

printf '\ndispatch.test: %s passed, %s failed\n' "$PASS" "$FAIL"
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
