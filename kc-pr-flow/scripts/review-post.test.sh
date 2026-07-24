#!/usr/bin/env bash
# Behavioral tests for once-only GitHub review posting (increment 2.3).
#
# Every acceptance criterion is exercised against the recorded stub transport
# (test/fixtures/review-post/stub-transport.sh) with NO real PR mutation. The
# load-bearing case is AC1: an ambiguous POST that still lands remotely must
# reconcile to exactly one review on resume, never a blind second POST.
# shellcheck disable=SC2317,SC2329 # Helper functions are invoked indirectly.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
POST="$HERE/review-post.sh"
STUB="$HERE/../test/fixtures/review-post/stub-transport.sh"

REPO="acme/widgets"
PR="42"
BASE="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
HEAD="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
MOVED="cccccccccccccccccccccccccccccccccccccccc"
CONFIG="dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
SELF="review-bot"

PASS=0
FAIL=0
pass() { PASS=$((PASS + 1)); }
fail() { FAIL=$((FAIL + 1)); printf 'FAIL: %s\n' "$1"; }
assert_eq() {
  if [ "$2" = "$3" ]; then pass; else fail "$1 (expected [$2], got [$3])"; fi
}

file_mode() {
  if stat -f '%Lp' "$1" >/dev/null 2>&1; then stat -f '%Lp' "$1"; else stat -c '%a' "$1"; fi
}

# Fresh isolated state + stub scenario per scenario.
new_env() {
  STATE="$(mktemp -d)"
  STUB_DIR="$(mktemp -d)"
  export KC_PR_FLOW_STATE_DIR="$STATE"
  export KC_PR_FLOW_POST_TRANSPORT="$STUB"
  export KC_STUB_DIR="$STUB_DIR"
  printf '%s\n' "$HEAD" >"$STUB_DIR/head"
  printf '%s\n' "$SELF" >"$STUB_DIR/self"
  : >"$STUB_DIR/reviews.jsonl"
}
teardown_env() {
  chmod -R u+rwX "$STATE" 2>/dev/null || true
  rm -rf "$STATE" "$STUB_DIR"
}

write_request() {
  local body="${1:-Looks good overall.}"
  REQUEST="$STUB_DIR/request.json"
  jq -S -c -n --arg repo "$REPO" --argjson pr "$PR" --arg base "$BASE" \
    --arg head "$HEAD" --arg config "$CONFIG" --arg commit "$HEAD" \
    --arg event "COMMENT" --arg body "$body" --arg self "$SELF" '
    {repo:$repo,pr:$pr,base_sha:$base,head_sha:$head,config_hash:$config,
     commit_id:$commit,event:$event,body:$body,comments:[],self_login:$self,
     retention_seconds:604800}' >"$REQUEST"
}
write_gate() {
  GATE="$STUB_DIR/gate.json"
  jq -S -c -n '{schema:"kc-pr-flow.interactive-post-gate/v1",human_confirmed:true,
    effective_event:"COMMENT",confirmation:{schema:"kc-pr-flow.interactive-confirmation/v1",
    source:"legacy",effective_event:"COMMENT"}}' >"$GATE"
}
store_count() { jq -s 'length' "$STUB_DIR/reviews.jsonl"; }
run_dir_for() { printf '%s/%s/pr-%s/%s' "$STATE" "$(printf '%s' "$REPO" | shasum -a 256 | awk '{print $1}')" "$PR" "$1"; }
run_events() { cat "$(run_dir_for "$1")/events.jsonl"; }

# --- AC-happy: a clean POST records exactly one review and a posted result. ---
new_env; write_request; write_gate
printf 'posted\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "clean post returns posted" "posted" "$(jq -r '.status' <<<"$out")"
run_id="$(jq -r '.run_id' <<<"$out")"
assert_eq "clean post records exactly one review" "1" "$(store_count)"
assert_eq "clean post writes a posted result event" "posted" "$(run_events "$run_id" | jq -r 'select(.event_type=="post.result") | .payload.outcome')"
assert_eq "clean post removes the pending payload" "false" "$([ -e "$(run_dir_for "$run_id")/pending-post.json" ] && printf true || printf false)"
teardown_env

# --- AC1: exactly-once under an ambiguous POST fault (request lands, response lost). ---
new_env; write_request; write_gate
printf 'ambiguous\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "ambiguous post is reported ambiguous" "ambiguous" "$(jq -r '.status' <<<"$out")"
run_id="$(jq -r '.run_id' <<<"$out")"
assert_eq "ambiguous post already landed one review remotely" "1" "$(store_count)"
assert_eq "ambiguous post leaves the pending payload durable" "true" "$([ -e "$(run_dir_for "$run_id")/pending-post.json" ] && printf true || printf false)"
assert_eq "ambiguous post writes NO terminal result" "" "$(run_events "$run_id" | jq -r 'select(.event_type=="post.result") | .payload.outcome')"
# Resume must reconcile the landed review and post NOTHING more.
resume_out="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id")"
assert_eq "resume reconciles the landed review" "posted_reconciled" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "resume ends with EXACTLY ONE review (no blind second POST)" "1" "$(store_count)"
assert_eq "resume records a reconciled result" "posted_reconciled" "$(run_events "$run_id" | jq -r 'select(.event_type=="post.result") | .payload.outcome')"
assert_eq "resume removes the pending payload" "false" "$([ -e "$(run_dir_for "$run_id")/pending-post.json" ] && printf true || printf false)"
# AC3: replaying resume again is idempotent — still one review.
resume_again="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id")"
assert_eq "second resume is idempotent" "posted_reconciled" "$(jq -r '.status' <<<"$resume_again")"
assert_eq "second resume still one review" "1" "$(store_count)"
teardown_env

# --- AC1 (truly-lost branch): request was lost, not landed — retry once posts one review. ---
new_env; write_request; write_gate
printf 'lost\nposted\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "truly-lost post is ambiguous" "ambiguous" "$(jq -r '.status' <<<"$out")"
run_id="$(jq -r '.run_id' <<<"$out")"
assert_eq "truly-lost post recorded no review" "0" "$(store_count)"
resume_out="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id")"
assert_eq "resume after a truly-lost POST posts once" "posted" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "resume after a truly-lost POST ends with one review" "1" "$(store_count)"
teardown_env

# --- AC2: a head that moved after authorization never posts the stale payload. ---
new_env; write_request; write_gate
printf '%s\n' "$MOVED" >"$STUB_DIR/head"
printf 'posted\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "moved head at post time invalidates" "invalidated" "$(jq -r '.status' <<<"$out")"
assert_eq "moved head reason is head_moved" "head_moved" "$(jq -r '.reason' <<<"$out")"
run_id="$(jq -r '.run_id' <<<"$out")"
assert_eq "moved head posts zero reviews" "0" "$(store_count)"
assert_eq "moved head records run.invalidated" "head_moved" "$(run_events "$run_id" | jq -r 'select(.event_type=="run.invalidated") | .payload.reason')"
assert_eq "moved head writes no pending payload" "false" "$([ -e "$(run_dir_for "$run_id")/pending-post.json" ] && printf true || printf false)"
teardown_env

# --- AC2 (resume branch): a head move between POST and resume never posts stale. ---
new_env; write_request; write_gate
printf 'lost\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
run_id="$(jq -r '.run_id' <<<"$out")"
printf '%s\n' "$MOVED" >"$STUB_DIR/head"
resume_out="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id")"
assert_eq "resume after a head move invalidates" "invalidated" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "resume head move posts zero reviews" "0" "$(store_count)"
assert_eq "resume head move drops the stale pending payload" "false" "$([ -e "$(run_dir_for "$run_id")/pending-post.json" ] && printf true || printf false)"
teardown_env

# --- AC4: pending artifact hygiene (mode 0600 in a mode-0700 dir, closed schema). ---
new_env; write_request; write_gate
printf 'ambiguous\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
run_id="$(jq -r '.run_id' <<<"$out")"
pending_file="$(run_dir_for "$run_id")/pending-post.json"
assert_eq "pending payload is mode 0600" "600" "$(file_mode "$pending_file")"
assert_eq "pending run dir is mode 0700" "700" "$(file_mode "$(run_dir_for "$run_id")")"
assert_eq "pending payload declares the closed schema" "kc-pr-flow.pending-post/v1" "$(jq -r '.schema' "$pending_file")"
assert_eq "pending payload has exactly the closed key set" \
  "authorized_at commit_id event expires_at idempotency_key payload payload_sha256 review_key run_id schema" \
  "$(jq -r 'keys | join(" ")' "$pending_file")"
if jq -e '.. | objects | (has("raw_diff") or has("prompt") or has("source_excerpt") or has("model_output"))' "$pending_file" >/dev/null 2>&1; then
  fail "pending payload leaks a forbidden raw field"
else
  pass
fi
teardown_env

# --- AC5: default-deny — posting refuses without a valid authorization gate. ---
new_env; write_request; write_gate
printf 'posted\n' >"$STUB_DIR/post-plan"
bash "$POST" post --request-file "$REQUEST" --now-epoch 1000 >/dev/null 2>&1
assert_eq "post refuses without a gate file (deny by absence)" "2" "$?"
bad_gate="$STUB_DIR/bad-gate.json"
jq -S -c -n '{schema:"kc-pr-flow.interactive-post-gate/v1",human_confirmed:false,effective_event:"COMMENT"}' >"$bad_gate"
bash "$POST" post --request-file "$REQUEST" --gate-file "$bad_gate" --now-epoch 1000 >/dev/null 2>&1
assert_eq "post refuses an unconfirmed gate" "3" "$?"
event_mismatch_gate="$STUB_DIR/event-mismatch-gate.json"
jq -S -c -n '{schema:"kc-pr-flow.interactive-post-gate/v1",human_confirmed:true,effective_event:"APPROVE"}' >"$event_mismatch_gate"
bash "$POST" post --request-file "$REQUEST" --gate-file "$event_mismatch_gate" --now-epoch 1000 >/dev/null 2>&1
assert_eq "post refuses an event-mismatched gate" "3" "$?"
assert_eq "denied posts record zero reviews" "0" "$(store_count)"
teardown_env

# --- AC6: retention fail-safe — within-window pending survives; past-window is GC'd. ---
new_env; write_request; write_gate
printf 'lost\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
run_id="$(jq -r '.run_id' <<<"$out")"
pending_file="$(run_dir_for "$run_id")/pending-post.json"
# Within the window: never GC the evidence needed to reconcile.
gc_within="$(bash "$POST" gc --repo "$REPO" --pr "$PR" --now-epoch 2000)"
assert_eq "within-window gc keeps the pending payload" "1" "$(jq -r '.kept' <<<"$gc_within")"
assert_eq "within-window gc removes nothing" "0" "$(jq -r '.removed' <<<"$gc_within")"
assert_eq "within-window pending payload survives" "true" "$([ -e "$pending_file" ] && printf true || printf false)"
# Past the window: expire and record run.invalidated{expired}.
gc_expired="$(bash "$POST" gc --repo "$REPO" --pr "$PR" --now-epoch 605801)"
assert_eq "past-window gc removes the pending payload" "1" "$(jq -r '.removed' <<<"$gc_expired")"
assert_eq "past-window pending payload is gone" "false" "$([ -e "$pending_file" ] && printf true || printf false)"
assert_eq "past-window gc records run.invalidated{expired}" "expired" "$(run_events "$run_id" | jq -r 'select(.event_type=="run.invalidated") | .payload.reason')"
teardown_env

# --- AC7: rollback preserves reconcilable evidence (nothing deletes it prematurely). ---
new_env; write_request; write_gate
printf 'ambiguous\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
run_id="$(jq -r '.run_id' <<<"$out")"
pending_file="$(run_dir_for "$run_id")/pending-post.json"
# Simulate rollback: the new posting path is simply not invoked again. The
# durable evidence (post.intent + pending payload) MUST survive so an uncertain
# remote result stays reconcilable.
assert_eq "rollback leaves the post.intent event intact" "1" "$(run_events "$run_id" | jq -s '[.[] | select(.event_type=="post.intent")] | length')"
assert_eq "rollback leaves the pending payload intact" "true" "$([ -e "$pending_file" ] && printf true || printf false)"
# And the preserved evidence is still enough to reconcile later.
resume_out="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id")"
assert_eq "preserved evidence still reconciles after rollback" "posted_reconciled" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "reconcile-after-rollback keeps exactly one review" "1" "$(store_count)"
teardown_env

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
