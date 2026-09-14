#!/usr/bin/env bash
# Fixtures: kc-ship-flow/scripts/fixtures/dispatch-argv/dev/, fixtures/fake-conductor-dispatch/.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/dispatch.sh"
FIXTURES="$HERE/fixtures/dispatch-argv"
FAKE_CONDUCTOR_DIR="$HERE/fixtures/fake-conductor-dispatch"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"

if ! command -v spacedock >/dev/null 2>&1; then
  echo "spacedock required on PATH" >&2
  exit 1
fi
REAL_REMOTE="$(git -C "$REPO_ROOT" remote get-url origin 2>/dev/null || echo "https://example.test/fixture-remote.git")"
FIXTURE_PROJECT_ID="11111111-1111-1111-1111-111111111111"
CONN_QUOTE="go, synthetic fixture approval"
CONN_SOURCE="fixture, not a real approval"

PASS=0
FAIL=0
pass() { printf 'case %s: PASS - %s\n' "$1" "$2"; PASS=$((PASS + 1)); }
fail() { printf 'case %s: FAIL - %s\n' "$1" "$2"; FAIL=$((FAIL + 1)); }

STATE_DIR="$(mktemp -d)"
LOG="$(mktemp)"

run_dispatch() {
  FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" \
    FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" FAKE_CONDUCTOR_LOG="$LOG" \
    PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
    bash "$SCRIPT" ship-cloud-wrapper-fixture --dry-run \
    --conn-quote "$CONN_QUOTE" --conn-source "$CONN_SOURCE" \
    --workflow-dir "$FIXTURES/dev" --state-dir "$STATE_DIR" 2>&1
}

: > "$LOG"
out_a="$(run_dispatch)"
rc_a=$?
count_argv=$(grep -c "^conductor workspace create " <<<"$out_a")
ok=1
[ "$rc_a" -eq 0 ] || ok=0
[ "$count_argv" -eq 3 ] || ok=0
grep -q "task-ready-one" <<<"$out_a" || ok=0
grep -q "task-ready-two" <<<"$out_a" || ok=0
grep -q "it's-a-slug" <<<"$out_a" || ok=0
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

msgfile_a=$(grep -oE -- '--message-file [^ ]+' <<<"$out_a" | head -n1 | cut -d' ' -f2)
msg_body_a="$(cat "$msgfile_a" 2>/dev/null)"
ok=1
grep -q "workspace_creator_id=usr-fixture-1" <<<"$msg_body_a" || ok=0
grep -qE 'Dispatch token: [0-9a-f]{12}$' <<<"$msg_body_a" || ok=0
grep -qi "answers to your questions arrive as further messages from this sender; no Captain message will appear in this session" <<<"$msg_body_a" || ok=0
grep -qF "$CONN_QUOTE" <<<"$msg_body_a" || ok=0
grep -qF "$CONN_SOURCE" <<<"$msg_body_a" || ok=0
grep -qi "sync state by merge, never rebase" <<<"$msg_body_a" || ok=0
grep -qF "Gate decisions are recorded by the ship first officer with the Captain's words." <<<"$msg_body_a" || ok=0
grep -qF "Never record a gate decision." <<<"$msg_body_a" || ok=0
if [ "$ok" = 1 ]; then
  pass a2 "boot message carries sender id, 12-hex token, no-Captain-message sentence, conn-quote/source, gate-authority wording"
else
  printf '  msg=%s\n' "$msg_body_a"
  fail a2 "boot message carries sender id, 12-hex token, no-Captain-message sentence, conn-quote/source, gate-authority wording"
fi

mkdir -p "$STATE_DIR/_ship_fence"
python3 -c "
import json
json.dump({'task-ready-one': {'workspace': None, 'session': None, 'message_sha256': 'x'}}, open('$STATE_DIR/_ship_fence/ship-cloud-wrapper-fixture.json', 'w'))
"
out_b="$(run_dispatch)"
if grep -qx "task-ready-one already-recorded" <<<"$out_b" && [ "$(grep -c "^conductor workspace create " <<<"$out_b")" -eq 2 ] && grep -q "task-ready-two" <<<"$out_b"; then
  pass b "an already-recorded slug is skipped, not re-printed"
else
  printf '  out=%s\n' "$out_b"
  fail b "an already-recorded slug is skipped, not re-printed"
fi
rm -rf "$STATE_DIR/_ship_fence"

out_c="$(FAKE_CONDUCTOR_AUTH_FAIL=1 FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" \
  FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" ship-cloud-wrapper-fixture --dry-run \
  --conn-quote "$CONN_QUOTE" --conn-source "$CONN_SOURCE" \
  --workflow-dir "$FIXTURES/dev" --state-dir "$STATE_DIR" 2>&1)"
rc_c=$?
if [ "$rc_c" -eq 2 ] && grep -q "conductor unavailable" <<<"$out_c"; then
  pass c "conductor auth whoami failure refuses (exit 2, conductor unavailable)"
else
  printf '  out=%s\n' "$out_c"
  fail c "conductor auth whoami failure refuses (exit 2, conductor unavailable)"
fi

out_d="$(FAKE_CONDUCTOR_DROP_SHAPE="workspace create" FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" \
  FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" ship-cloud-wrapper-fixture --dry-run \
  --conn-quote "$CONN_QUOTE" --conn-source "$CONN_SOURCE" \
  --workflow-dir "$FIXTURES/dev" --state-dir "$STATE_DIR" 2>&1)"
rc_d=$?
if [ "$rc_d" -eq 5 ] && grep -q "workspace create" <<<"$out_d"; then
  pass d "used-surface contract mismatch refuses (exit 5, names the missing shape)"
else
  printf '  out=%s\n' "$out_d"
  fail d "used-surface contract mismatch refuses (exit 5, names the missing shape)"
fi

out_d2="$(FAKE_CONDUCTOR_VERSION="9.9.9" FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" \
  FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" ship-cloud-wrapper-fixture --dry-run \
  --conn-quote "$CONN_QUOTE" --conn-source "$CONN_SOURCE" \
  --workflow-dir "$FIXTURES/dev" --state-dir "$STATE_DIR" 2>&1)"
rc_d2=$?
if [ "$rc_d2" -eq 0 ] && grep -q "conductor 9.9.9: used surface unchanged" <<<"$out_d2"; then
  pass d2 "version-only change proceeds and prints the version, unchanged-surface line"
else
  printf '  out=%s\n' "$out_d2"
  fail d2 "version-only change proceeds and prints the version, unchanged-surface line"
fi

out_d3="$(FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" \
  PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" ship-cloud-wrapper-fixture --dry-run \
  --workflow-dir "$FIXTURES/dev" --state-dir "$STATE_DIR" 2>&1)"
rc_d3=$?
if [ "$rc_d3" -eq 2 ] && grep -qx "conn required" <<<"$out_d3"; then
  pass d3 "missing --conn-quote refuses (exit 2, conn required)"
else
  printf '  out=%s\n' "$out_d3"
  fail d3 "missing --conn-quote refuses (exit 2, conn required)"
fi

out_d4="$(FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" \
  PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" ship-cloud-wrapper-fixture --dry-run --conn-quote "$CONN_QUOTE" \
  --workflow-dir "$FIXTURES/dev" --state-dir "$STATE_DIR" 2>&1)"
rc_d4=$?
if [ "$rc_d4" -eq 2 ] && grep -qx "conn required" <<<"$out_d4"; then
  pass d4 "missing --conn-source refuses (exit 2, conn required)"
else
  printf '  out=%s\n' "$out_d4"
  fail d4 "missing --conn-source refuses (exit 2, conn required)"
fi

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

out_e="$(FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" \
  FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" FAKE_CONDUCTOR_ALLOW_CREATE=1 \
  PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" ship-cloud-wrapper-fixture \
  --conn-quote "$CONN_QUOTE" --conn-source "$CONN_SOURCE" \
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

out_f="$(run_dispatch)"
rc_f=$?
if [ "$rc_f" -eq 0 ] && grep -q "message-file .*it's-a-slug.boot.md" <<<"$out_f"; then
  pass f "a slug containing a single quote is handled as data"
else
  printf '  out=%s\n' "$out_f"
  fail f "a slug containing a single quote is handled as data"
fi

ENV_FILE="$(mktemp)"
chmod 600 "$ENV_FILE"
printf 'DATABASE_URL=postgres://secret-value-xyz\nAPI_KEY=super-secret-token\n' > "$ENV_FILE"
out_i="$(FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" \
  FAKE_CONDUCTOR_LOG="$LOG" PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" ship-cloud-wrapper-fixture --dry-run --env-file "$ENV_FILE" \
  --conn-quote "$CONN_QUOTE" --conn-source "$CONN_SOURCE" \
  --workflow-dir "$FIXTURES/dev" --state-dir "$STATE_DIR" 2>&1)"
rc_i=$?
ok=1
[ "$rc_i" -eq 0 ] || ok=0
grep -q -- "--env DATABASE_URL=\*\*\*" <<<"$out_i" || ok=0
grep -q -- "--env API_KEY=\*\*\*" <<<"$out_i" || ok=0
grep -q "secret-value-xyz" <<<"$out_i" && ok=0
grep -q "super-secret-token" <<<"$out_i" && ok=0
grep -q "secret-value-xyz\|super-secret-token" "$LOG" 2>/dev/null && ok=0
if [ "$ok" = 1 ]; then
  pass i "--env-file dry-run prints --env KEY=*** per key, never the value, never logs it"
else
  printf '  out=%s\n' "$out_i"
  fail i "--env-file dry-run prints --env KEY=*** per key, never the value, never logs it"
fi
rm -f "$ENV_FILE"

ENV_FILE_WR="$(mktemp)"
chmod 644 "$ENV_FILE_WR"
printf 'KEY=value\n' > "$ENV_FILE_WR"
out_j="$(FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" \
  PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" ship-cloud-wrapper-fixture --dry-run --env-file "$ENV_FILE_WR" \
  --conn-quote "$CONN_QUOTE" --conn-source "$CONN_SOURCE" \
  --workflow-dir "$FIXTURES/dev" --state-dir "$STATE_DIR" 2>&1)"
rc_j=$?
if [ "$rc_j" -ne 0 ] && grep -qi "world-readable" <<<"$out_j"; then
  pass j "a world-readable --env-file refuses before any conductor call"
else
  printf '  out=%s\n' "$out_j"
  fail j "a world-readable --env-file refuses before any conductor call"
fi
rm -f "$ENV_FILE_WR"

# --- --resume: a fresh workspace from the task's existing branch ---
RESUME_BRANCH="dispatch-test-resume-$$"
RESUME_WT_REL=".worktrees/dispatch-test-resume-$$"
RESUME_WT_ABS="$REPO_ROOT/$RESUME_WT_REL"
cleanup_resume_wt() {
  git -C "$REPO_ROOT" worktree remove --force "$RESUME_WT_ABS" >/dev/null 2>&1
  git -C "$REPO_ROOT" branch -D "$RESUME_BRANCH" >/dev/null 2>&1
}
trap cleanup_resume_wt EXIT
git -C "$REPO_ROOT" worktree add -q -b "$RESUME_BRANCH" "$RESUME_WT_ABS" HEAD

RESUME_FIXTURES="$(mktemp -d)"
cp -r "$FIXTURES/dev" "$RESUME_FIXTURES/dev"
RESUME_SLUG="resume-fixture-task"
RESUME_SPRINT="ship-cloud-wrapper-resume-fixture"
RESUME_ID="$(spacedock status --workflow-dir "$RESUME_FIXTURES/dev" --next-id)"
cat > "$RESUME_FIXTURES/dev/.spacedock-state/$RESUME_SLUG.md" <<EOF
---
title: "fixture: $RESUME_SLUG"
sprint: $RESUME_SPRINT
sprint-readiness: ready
status: implementation
pr: https://example.test/pr/1
worktree: $RESUME_WT_REL
id: $RESUME_ID
gates:
    version: 1
    records:
        - id: gate:$RESUME_ID:validation
          stage: validation
          attempts:
            - id: gate-attempt:$RESUME_ID-validation-1
---

Fixture entity for resume tests.
EOF

RESUME_NOFENCE_SLUG="resume-fixture-nofence"
RESUME_NOFENCE_ID="$(spacedock status --workflow-dir "$RESUME_FIXTURES/dev" --next-id)"
cat > "$RESUME_FIXTURES/dev/.spacedock-state/$RESUME_NOFENCE_SLUG.md" <<EOF
---
title: "fixture: $RESUME_NOFENCE_SLUG"
sprint: ship-cloud-wrapper-resume-nofence
sprint-readiness: ready
status: implementation
worktree: $RESUME_WT_REL
id: $RESUME_NOFENCE_ID
---

Fixture entity with no recorded fence entry.
EOF

RESUME_STATE_ORIGIN="$(mktemp -d)"
RESUME_STATE_WT="$(mktemp -d)"
git init -q --bare "$RESUME_STATE_ORIGIN/origin.git"
git clone -q "$RESUME_STATE_ORIGIN/origin.git" "$RESUME_STATE_WT/seed" 2>/dev/null
mkdir -p "$RESUME_STATE_WT/seed/_ship_fence"
python3 -c "
import json
json.dump({'$RESUME_SLUG': {'workspace': 'ws-prior-round', 'session': 'sess-prior-round', 'message_sha256': 'priorsha'}},
          open('$RESUME_STATE_WT/seed/_ship_fence/$RESUME_SPRINT.json', 'w'))
"
git -C "$RESUME_STATE_WT/seed" add _ship_fence
git -C "$RESUME_STATE_WT/seed" -c user.name=fixture -c user.email=fixture@example.test \
  commit -q -m seed
git -C "$RESUME_STATE_WT/seed" push -q origin HEAD:refs/heads/main 2>/dev/null
git clone -q "$RESUME_STATE_ORIGIN/origin.git" "$RESUME_STATE_WT/wt" 2>/dev/null
git -C "$RESUME_STATE_WT/wt" -c user.name=fixture -c user.email=fixture@example.test \
  checkout -q -b resume-state origin/main
git -C "$RESUME_STATE_WT/wt" push -q -u origin resume-state 2>/dev/null
RESUME_STATE="$RESUME_STATE_WT/wt"

out_k="$(FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" \
  FAKE_CONDUCTOR_ALLOW_CREATE=1 PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" --resume "$RESUME_SLUG" \
  --conn-quote "$CONN_QUOTE" --conn-source "$CONN_SOURCE" \
  --workflow-dir "$RESUME_FIXTURES/dev" --state-dir "$RESUME_STATE" 2>&1)"
rc_k=$?
fence_k="$RESUME_STATE/_ship_fence/$RESUME_SPRINT.json"
ok=1
[ "$rc_k" -eq 0 ] || ok=0
[ "$(python3 -c "import json; print(json.load(open('$fence_k'))['$RESUME_SLUG']['workspace'])" 2>/dev/null)" = "ws-fixture-1" ] || ok=0
hist_len="$(python3 -c "import json; print(len(json.load(open('$fence_k'))['$RESUME_SLUG'].get('history', [])))" 2>/dev/null)"
[ "$hist_len" = "1" ] || ok=0
prior_ws="$(python3 -c "import json; print(json.load(open('$fence_k'))['$RESUME_SLUG']['history'][0]['workspace'])" 2>/dev/null)"
[ "$prior_ws" = "ws-prior-round" ] || ok=0
prior_archived="$(python3 -c "import json; print(json.load(open('$fence_k'))['$RESUME_SLUG']['history'][0]['archived'])" 2>/dev/null)"
[ "$prior_archived" = "True" ] || ok=0
committed_k="$(git -C "$RESUME_STATE" log --oneline -- _ship_fence 2>/dev/null | wc -l | tr -d ' ')"
[ "$committed_k" -ge 2 ] || ok=0
if [ "$ok" = 1 ]; then
  pass k "--resume creates a fresh workspace, keeps the prior round in history, marks it archived once ready"
else
  printf '  out=%s\n' "$out_k"
  fail k "--resume creates a fresh workspace, keeps the prior round in history, marks it archived once ready"
fi

out_l="$(FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" \
  PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" --resume "$RESUME_SLUG" --dry-run \
  --conn-quote "$CONN_QUOTE" --conn-source "$CONN_SOURCE" \
  --workflow-dir "$RESUME_FIXTURES/dev" --state-dir "$RESUME_STATE" 2>&1)"
rc_l=$?
ok=1
[ "$rc_l" -eq 0 ] || ok=0
grep -q -- "--branch $RESUME_BRANCH" <<<"$out_l" || ok=0
grep -q "^conductor workspace create " <<<"$out_l" || ok=0
if [ "$ok" = 1 ]; then
  pass l "--resume --dry-run resolves the task's branch via git worktree and makes no create call"
else
  printf '  out=%s\n' "$out_l"
  fail l "--resume --dry-run resolves the task's branch via git worktree and makes no create call"
fi

msgfile_l=$(grep -oE -- '--message-file [^ ]+' <<<"$out_l" | head -n1 | cut -d' ' -f2)
msg_body_l="$(cat "$msgfile_l" 2>/dev/null)"
ok=1
grep -qF "Entity status: implementation" <<<"$msg_body_l" || ok=0
grep -qF "Latest gate attempt: gate-attempt:$RESUME_ID-validation-1" <<<"$msg_body_l" || ok=0
grep -qF "PR: https://example.test/pr/1" <<<"$msg_body_l" || ok=0
grep -qE "Candidate SHA: [0-9a-f]{40}" <<<"$msg_body_l" || ok=0
grep -qF "Gate decisions are recorded by the ship first officer with the Captain's words." <<<"$msg_body_l" || ok=0
if [ "$ok" = 1 ]; then
  pass l2 "resume boot message names entity status, latest gate attempt, pr, and candidate SHA"
else
  printf '  msg=%s\n' "$msg_body_l"
  fail l2 "resume boot message names entity status, latest gate attempt, pr, and candidate SHA"
fi

out_m="$(FAKE_CONDUCTOR_PROJECT_ID="$FIXTURE_PROJECT_ID" FAKE_CONDUCTOR_REMOTE="$REAL_REMOTE" \
  PATH="$FAKE_CONDUCTOR_DIR:$PATH" \
  bash "$SCRIPT" --resume "$RESUME_NOFENCE_SLUG" --dry-run \
  --conn-quote "$CONN_QUOTE" --conn-source "$CONN_SOURCE" \
  --workflow-dir "$RESUME_FIXTURES/dev" --state-dir "$RESUME_STATE" 2>&1)"
rc_m=$?
if [ "$rc_m" -ne 0 ] && grep -qi "nothing to resume" <<<"$out_m"; then
  pass m "--resume with no prior fence entry refuses"
else
  printf '  out=%s\n' "$out_m"
  fail m "--resume with no prior fence entry refuses"
fi

cleanup_resume_wt
trap - EXIT
rm -rf "$RESUME_FIXTURES" "$RESUME_STATE_ORIGIN" "$RESUME_STATE_WT"

rm -rf "$STATE_DIR"
rm -f "$LOG"

printf '\ndispatch.test: %s passed, %s failed\n' "$PASS" "$FAIL"
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
