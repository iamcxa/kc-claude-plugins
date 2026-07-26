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

# Spelled out rather than `[ -e x ] && printf true || printf false`: that idiom
# is an SC2015 finding on the ShellCheck versions CI installs.
path_exists() {
  if [ -e "$1" ]; then printf true; else printf false; fi
}

# Fresh isolated state + stub scenario per scenario. The rollback flag
# defaults ON here so AC1-AC4/AC6 exercise the new path's own mechanics;
# dedicated blocks below unset it to prove the default-deny/rollback gate.
new_env() {
  STATE="$(mktemp -d)"
  STUB_DIR="$(mktemp -d)"
  export KC_PR_FLOW_STATE_DIR="$STATE"
  export KC_PR_FLOW_POST_TRANSPORT="$STUB"
  export KC_STUB_DIR="$STUB_DIR"
  export KC_PR_FLOW_ONCE_ONLY_POST=on
  printf '%s\n' "$HEAD" >"$STUB_DIR/head"
  printf '%s\n' "$SELF" >"$STUB_DIR/self"
  : >"$STUB_DIR/reviews.jsonl"
}
teardown_env() {
  chmod -R u+rwX "$STATE" 2>/dev/null || true
  rm -rf "$STATE" "$STUB_DIR"
  unset KC_PR_FLOW_ONCE_ONLY_POST
}

write_request() {
  local body="Looks good overall."
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
# The review key this request resolves to, mirroring review_runtime_review_key.
review_key_for() {
  printf '%s|%s|%s|%s|%s' "$REPO" "$PR" "$BASE" "$HEAD" "$CONFIG" |
    shasum -a 256 | awk '{print $1}'
}
# Authorization for a caller with no human at the confirmation gate. The
# overrides let a test bind it to the wrong review or forge a field.
write_auto_gate() {
  local key head by
  key="${1:-}"; [ -n "$key" ] || key="$(review_key_for)"
  head="${2:-$HEAD}"
  by="${3:-daemon}"
  AUTO_GATE="$STUB_DIR/auto-gate.json"
  jq -S -c -n --arg key "$key" --arg head "$head" --arg by "$by" '
    {schema:"kc-pr-flow.autonomous-post-gate/v1",authorized_by:$by,
     effective_event:"COMMENT",head_sha:$head,review_key:$key}' >"$AUTO_GATE"
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
assert_eq "clean post removes the pending payload" "false" "$(path_exists "$(run_dir_for "$run_id")/pending-post.json")"
teardown_env

# --- AC1: exactly-once under an ambiguous POST fault (request lands, response lost). ---
new_env; write_request; write_gate
printf 'ambiguous\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "ambiguous post is reported ambiguous" "ambiguous" "$(jq -r '.status' <<<"$out")"
run_id="$(jq -r '.run_id' <<<"$out")"
assert_eq "ambiguous post already landed one review remotely" "1" "$(store_count)"
assert_eq "ambiguous post leaves the pending payload durable" "true" "$(path_exists "$(run_dir_for "$run_id")/pending-post.json")"
assert_eq "ambiguous post writes NO terminal result" "" "$(run_events "$run_id" | jq -r 'select(.event_type=="post.result") | .payload.outcome')"
# Resume must reconcile the landed review and post NOTHING more.
resume_out="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id")"
assert_eq "resume reconciles the landed review" "posted_reconciled" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "resume ends with EXACTLY ONE review (no blind second POST)" "1" "$(store_count)"
assert_eq "resume records a reconciled result" "posted_reconciled" "$(run_events "$run_id" | jq -r 'select(.event_type=="post.result") | .payload.outcome')"
assert_eq "resume removes the pending payload" "false" "$(path_exists "$(run_dir_for "$run_id")/pending-post.json")"
# AC3: replaying resume again is idempotent — still one review.
resume_again="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id")"
assert_eq "second resume is idempotent" "posted_reconciled" "$(jq -r '.status' <<<"$resume_again")"
assert_eq "second resume still one review" "1" "$(store_count)"
teardown_env

# --- AC1 (truly-lost branch): request was lost, not landed — retry posts one
# review, but only once the read-after-write confirm window has passed. An
# empty reviews list is only trustworthy as "never landed" after that window;
# inside it, an empty list is indistinguishable from GitHub lag. ---
new_env; write_request; write_gate
printf 'lost\nposted\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "truly-lost post is ambiguous" "ambiguous" "$(jq -r '.status' <<<"$out")"
run_id="$(jq -r '.run_id' <<<"$out")"
assert_eq "truly-lost post recorded no review" "0" "$(store_count)"
resume_early="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id" --now-epoch 1010)"
assert_eq "resume inside the confirm window does not retry" "ambiguous" "$(jq -r '.status' <<<"$resume_early")"
assert_eq "resume inside the confirm window posts nothing" "0" "$(store_count)"
resume_out="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id" --now-epoch 5000)"
assert_eq "resume past the confirm window posts once" "posted" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "resume past the confirm window ends with one review" "1" "$(store_count)"
teardown_env

# --- Definite non-retryable failure (design step 3, validation 4xx): posts
# zero additional reviews, records a terminal failed result, resume replays
# it without any further network call, and gc eventually reclaims the
# leftover pending payload once its retention window passes. ---
new_env; write_request; write_gate
printf 'failed\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "a definite 4xx failure is reported failed" "failed" "$(jq -r '.status' <<<"$out")"
run_id="$(jq -r '.run_id' <<<"$out")"
assert_eq "a definite failure records zero reviews" "0" "$(store_count)"
assert_eq "a definite failure writes a failed terminal result" "failed" "$(run_events "$run_id" | jq -r 'select(.event_type=="post.result") | .payload.outcome')"
pending_file="$(run_dir_for "$run_id")/pending-post.json"
resume_out="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id")"
assert_eq "resume replays the failed terminal result without retrying" "failed" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "resume after a definite failure still records zero reviews" "0" "$(store_count)"
# The retention window still governs cleanup of the leftover pending file --
# a terminal failure does not delete it immediately (only posted/reconciled
# outcomes do), so the fail-safe GC invariant applies here too.
gc_within="$(bash "$POST" gc --repo "$REPO" --pr "$PR" --now-epoch 2000)"
assert_eq "within-window gc keeps a failed run's leftover pending payload" "true" "$(path_exists "$pending_file")"
gc_expired="$(bash "$POST" gc --repo "$REPO" --pr "$PR" --now-epoch 605801)"
assert_eq "past-window gc reclaims a failed run's leftover pending payload" "false" "$(path_exists "$pending_file")"
assert_eq "past-window gc records run.invalidated{expired} for a failed run" "expired" "$(run_events "$run_id" | jq -r 'select(.event_type=="run.invalidated") | .payload.reason')"
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
assert_eq "moved head writes no pending payload" "false" "$(path_exists "$(run_dir_for "$run_id")/pending-post.json")"
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
assert_eq "resume head move drops the stale pending payload" "false" "$(path_exists "$(run_dir_for "$run_id")/pending-post.json")"
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

# --- AC5/AC7: rollback flag is the operator-level default-deny kill switch,
# distinct from and layered above the per-call human-confirmation gate. Off
# (the default) denies EVERY caller -- daemon or interactive -- so "a daemon
# iteration with no preauthorization takes the new posting path zero times"
# holds by absence, with no daemon-specific code path to test separately. ---
new_env; write_request; write_gate
unset KC_PR_FLOW_ONCE_ONLY_POST
printf 'posted\n' >"$STUB_DIR/post-plan"
bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000 >/dev/null 2>&1
assert_eq "post refuses when the rollback flag is off, even with a valid gate" "3" "$?"
assert_eq "rollback-flag-off posts record zero reviews" "0" "$(store_count)"
export KC_PR_FLOW_ONCE_ONLY_POST=on
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "the same request posts once the flag is enabled" "posted" "$(jq -r '.status' <<<"$out")"
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
assert_eq "within-window pending payload survives" "true" "$(path_exists "$pending_file")"
# Past the window: expire and record run.invalidated{expired}.
gc_expired="$(bash "$POST" gc --repo "$REPO" --pr "$PR" --now-epoch 605801)"
assert_eq "past-window gc removes the pending payload" "1" "$(jq -r '.removed' <<<"$gc_expired")"
assert_eq "past-window pending payload is gone" "false" "$(path_exists "$pending_file")"
assert_eq "past-window gc records run.invalidated{expired}" "expired" "$(run_events "$run_id" | jq -r 'select(.event_type=="run.invalidated") | .payload.reason')"
teardown_env

# --- AC7: rollback preserves reconcilable evidence (nothing deletes it prematurely). ---
new_env; write_request; write_gate
printf 'ambiguous\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
run_id="$(jq -r '.run_id' <<<"$out")"
pending_file="$(run_dir_for "$run_id")/pending-post.json"
# Actually flip the rollback flag off -- the real mechanism, not a stand-in.
# The durable evidence (post.intent + pending payload) MUST survive so an
# uncertain remote result stays reconcilable, and resume/gc stay ungated.
unset KC_PR_FLOW_ONCE_ONLY_POST
assert_eq "rollback leaves the post.intent event intact" "1" "$(run_events "$run_id" | jq -s '[.[] | select(.event_type=="post.intent")] | length')"
assert_eq "rollback leaves the pending payload intact" "true" "$(path_exists "$pending_file")"
# A fresh post attempt with the flag off is refused -- rollback really did
# disable the new path for fresh invocations.
bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000 >/dev/null 2>&1
assert_eq "rollback refuses a fresh post attempt" "3" "$?"
# And the preserved evidence is still enough to reconcile later, even with
# the flag off -- resume is never gated by the flag.
resume_out="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id")"
assert_eq "preserved evidence still reconciles after rollback" "posted_reconciled" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "reconcile-after-rollback keeps exactly one review" "1" "$(store_count)"
teardown_env

# --- AC1 (reconcile fail-closed, lagging list): the reconcile read is only
# trusted when it positively confirms remote state. GitHub read-after-write lag
# returns a well-formed but stale empty list for a review that DID land; a
# blind retry there is exactly the duplicate-review bug. ---
new_env; write_request; write_gate
printf 'ambiguous\n' >"$STUB_DIR/post-plan"
printf 'lag\nlag\nlag\nlag\n' >"$STUB_DIR/list-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
run_id="$(jq -r '.run_id' <<<"$out")"
assert_eq "ambiguous post landed one review despite the lagging list" "1" "$(store_count)"
resume_out="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id" --now-epoch 1010)"
assert_eq "a lagging reconcile list never blind-retries" "ambiguous" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "a lagging reconcile list leaves EXACTLY ONE review" "1" "$(store_count)"
assert_eq "a lagging reconcile keeps the pending payload for a later retry" "true" "$(path_exists "$(run_dir_for "$run_id")/pending-post.json")"
assert_eq "a lagging reconcile writes no terminal result" "" "$(run_events "$run_id" | jq -r 'select(.event_type=="post.result") | .payload.outcome')"
teardown_env

# --- A malformed confirm-window knob must not fail open into the retry the
# window exists to prevent (same class as the gc clock guard below). ---
new_env; write_request; write_gate
printf 'ambiguous\n' >"$STUB_DIR/post-plan"
printf 'lag\nlag\nlag\nlag\n' >"$STUB_DIR/list-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
run_id="$(jq -r '.run_id' <<<"$out")"
resume_out="$(KC_PR_FLOW_RECONCILE_CONFIRM_SECONDS=not-a-number bash "$POST" resume \
  --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id" --now-epoch 1010)"
assert_eq "a malformed confirm window falls back to the safe default" "ambiguous" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "a malformed confirm window never licenses a retry" "1" "$(store_count)"
teardown_env

# --- AC1 (reconcile fail-closed, unusable list): a transport that exits 0 with
# a body that is not a reviews array must never be read as "marker absent". The
# first `list` is faithful so the POST happens at all; the unusable body is what
# resume then has to reconcile against. ---
new_env; write_request; write_gate
printf 'ambiguous\n' >"$STUB_DIR/post-plan"
printf 'faithful\nunusable\nunusable\nunusable\n' >"$STUB_DIR/list-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
run_id="$(jq -r '.run_id' <<<"$out")"
assert_eq "ambiguous post landed one review before the unusable list" "1" "$(store_count)"
resume_out="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id" --now-epoch 5000)"
assert_eq "an unusable reconcile list fails closed" "ambiguous" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "an unusable reconcile list never retries" "1" "$(store_count)"
assert_eq "an unusable reconcile keeps the pending payload" "true" "$(path_exists "$(run_dir_for "$run_id")/pending-post.json")"
teardown_env

# --- AC1 (post fails closed on the SAME condition resume does). The local intent
# check `post` used to lean on is duplicate-safe only within ONE state root: a
# wiped or reconfigured state dir, another machine, or a stateless runner leaves
# it blind, and an unusable list hides the marker that would have caught the
# duplicate. So local silence alone no longer licenses a POST. ---
# One scenario walks the whole sequence -- refuse, refuse again, then settle --
# because each `post`/`resume` invocation costs real CI seconds and this suite
# runs close to the job's budget.
new_env; write_request; write_gate
printf 'posted\n' >"$STUB_DIR/post-plan"
printf 'unusable\nunusable\n' >"$STUB_DIR/list-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
run_id="$(jq -r '.run_id' <<<"$out")"
assert_eq "post fails closed on an unusable reconcile list" "ambiguous" "$(jq -r '.status' <<<"$out")"
assert_eq "a refused post writes no review" "0" "$(store_count)"
assert_eq "a refused post keeps the pending payload" "true" "$(path_exists "$(run_dir_for "$run_id")/pending-post.json")"
assert_eq "a refused post writes no terminal result" "" "$(run_events "$run_id" | jq -r 'select(.event_type=="post.result") | .payload.outcome')"
# Symmetry, pinned to the literal verdict on BOTH sides rather than to each
# other: cross-comparing the two outputs holds in the pre-fix world too (both
# said "posted"), so it would have been decoration.
assert_eq "post names the reason resume names" "reconcile_unavailable" "$(jq -r '.reason' <<<"$out")"
resume_out="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id" --now-epoch 5000)"
assert_eq "resume reaches the same status on the same body" "ambiguous" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "resume names the same reason" "reconcile_unavailable" "$(jq -r '.reason' <<<"$resume_out")"
# AC2: refusing is not stranding. The intent and pending payload survived both
# refusals, so the next usable read settles the run.
resume_out="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id" --now-epoch 5100)"
assert_eq "a refused post settles on a later usable read" "posted" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "settling a refused post writes exactly one review" "1" "$(store_count)"
teardown_env

# --- Placement guard. The fail-closed check sits AFTER the local prior-attempt
# consultation, so the two verdicts that local durable state can reach on its own
# still win over the generic reconcile refusal. Moving the check earlier turns
# both of these into reconcile_unavailable, which is why they are pinned. ---
new_env; write_request; write_gate
printf 'posted\n' >"$STUB_DIR/post-plan"
printf 'faithful\nunusable\n' >"$STUB_DIR/list-plan"
first="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "the first post landed" "posted" "$(jq -r '.status' <<<"$first")"
second="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1100)"
assert_eq "a definitively posted prior run still reconciles under an unusable list" "posted_reconciled" "$(jq -r '.status' <<<"$second")"
assert_eq "reconciling against local state posts nothing further" "1" "$(store_count)"
teardown_env

new_env; write_request; write_gate
printf 'ambiguous\n' >"$STUB_DIR/post-plan"
printf 'faithful\nunusable\n' >"$STUB_DIR/list-plan"
first="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "the first post ended unsettled" "ambiguous" "$(jq -r '.status' <<<"$first")"
second="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1100)"
assert_eq "an unsettled prior attempt keeps its own reason under an unusable list" "prior_attempt_unsettled" "$(jq -r '.reason' <<<"$second")"
assert_eq "the unsettled prior attempt is not re-posted" "1" "$(store_count)"
teardown_env

# --- AC1 (author identity is not load-bearing): the idempotency marker alone
# identifies our landed review. A self-login that differs from the identity the
# token actually posted under must not cause a duplicate. ---
new_env; write_request; write_gate
printf 'other-bot\n' >"$STUB_DIR/self"
printf 'ambiguous\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
run_id="$(jq -r '.run_id' <<<"$out")"
assert_eq "post landed one review under a different author login" "1" "$(store_count)"
resume_out="$(bash "$POST" resume --repo "$REPO" --pr "$PR" --self "$SELF" --run-id "$run_id" --now-epoch 5000)"
assert_eq "a mismatched author login still reconciles by marker" "posted_reconciled" "$(jq -r '.status' <<<"$resume_out")"
assert_eq "a mismatched author login causes no duplicate" "1" "$(store_count)"
teardown_env

# --- AC1 (repeat fresh post): exactly-once must survive a re-invocation, not
# only a crash-resume. A prior run that already landed the identical payload is
# reconciled instead of posted again. ---
new_env; write_request; write_gate
printf 'ambiguous\n' >"$STUB_DIR/post-plan"
first="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "first post landed one review" "1" "$(store_count)"
assert_eq "first post is ambiguous" "ambiguous" "$(jq -r '.status' <<<"$first")"
second="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1100)"
assert_eq "a repeat fresh post reconciles instead of posting" "posted_reconciled" "$(jq -r '.status' <<<"$second")"
assert_eq "a repeat fresh post leaves EXACTLY ONE review" "1" "$(store_count)"
teardown_env

# --- "Not visible" is not "not posted": when the pre-POST reconcile cannot see
# a landed review (lagging list) but another run already authorized this exact
# payload and never settled, a second fresh post must defer to that run instead
# of racing a duplicate. ---
new_env; write_request; write_gate
printf 'ambiguous\nposted\n' >"$STUB_DIR/post-plan"
printf 'lag\nlag\nlag\nlag\n' >"$STUB_DIR/list-plan"
first="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "first post landed one review behind a lagging list" "1" "$(store_count)"
assert_eq "first post is ambiguous" "ambiguous" "$(jq -r '.status' <<<"$first")"
second="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1100)"
assert_eq "a second post defers to the unsettled prior attempt" "prior_attempt_unsettled" "$(jq -r '.reason // ""' <<<"$second")"
assert_eq "a second post never races a duplicate" "1" "$(store_count)"
teardown_env

# --- A prior run that definitively landed this payload must settle a later post
# even when the reconcile list cannot show it yet. ---
new_env; write_request; write_gate
printf 'posted\n' >"$STUB_DIR/post-plan"
first="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "first post landed definitively" "posted" "$(jq -r '.status' <<<"$first")"
assert_eq "first post recorded one review" "1" "$(store_count)"
printf 'lag\nlag\nlag\nlag\n' >"$STUB_DIR/list-plan"
second="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1100)"
assert_eq "a post behind a lagging list settles against the landed prior run" "posted_reconciled" "$(jq -r '.status' <<<"$second")"
assert_eq "a post behind a lagging list adds no duplicate" "1" "$(store_count)"
teardown_env

# --- ...but a prior run that landed NOTHING must not block a later post: the
# cross-run guard has to be precise, not merely conservative. ---
new_env; write_request; write_gate
printf 'failed\nposted\n' >"$STUB_DIR/post-plan"
first="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "first post failed definitively" "failed" "$(jq -r '.status' <<<"$first")"
assert_eq "first post recorded no review" "0" "$(store_count)"
second="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1100)"
assert_eq "a definitively failed prior run does not block a later post" "posted" "$(jq -r '.status' <<<"$second")"
assert_eq "a definitively failed prior run yields exactly one review" "1" "$(store_count)"
teardown_env

# --- Malformed head response must fail closed as a transport error, never be
# misread as a moved head (which would silently discard a postable review). ---
new_env; write_request; write_gate
printf 'malformed\n' >"$STUB_DIR/head-plan"
set +e
bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000 >/dev/null 2>&1
head_rc=$?
set -e
assert_eq "a malformed head response fails closed" "74" "$head_rc"
assert_eq "a malformed head response posts nothing" "0" "$(store_count)"
assert_eq "a malformed head response is never recorded as head_moved" "0" \
  "$(grep -rl head_moved "$STATE" 2>/dev/null | wc -l | tr -d ' ')"
teardown_env

# --- gc must validate its clock input: a non-numeric --now-epoch previously
# made the within-window comparison error out and fall through to deletion,
# discarding the evidence needed to reconcile an uncertain remote result. ---
new_env; write_request; write_gate
printf 'lost\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
run_id="$(jq -r '.run_id' <<<"$out")"
pending_file="$(run_dir_for "$run_id")/pending-post.json"
set +e
bash "$POST" gc --repo "$REPO" --pr "$PR" --now-epoch not-a-number >/dev/null 2>&1
gc_rc=$?
set -e
assert_eq "gc rejects a non-numeric --now-epoch" "2" "$gc_rc"
assert_eq "a rejected gc clock never deletes reconcile evidence" "true" "$(path_exists "$pending_file")"
teardown_env

# --- Autonomous (daemon) authorization: an iteration with no human at the
# confirmation gate gets the same once-only protection as an interactive post,
# which is the whole point — a daemon session dies mid-POST as a matter of
# routine, not as an edge case. ---
new_env; write_request; write_auto_gate
printf 'ambiguous\n' >"$STUB_DIR/post-plan"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$AUTO_GATE" --now-epoch 1000)"
assert_eq "an autonomous gate authorizes a post" "ambiguous" "$(jq -r '.status' <<<"$out")"
run_id="$(jq -r '.run_id' <<<"$out")"
assert_eq "the autonomous post landed one review" "1" "$(store_count)"
assert_eq "the autonomous post left durable reconcile evidence" "true" "$(path_exists "$(run_dir_for "$run_id")/pending-post.json")"
# The interrupted-iteration case: a second iteration must reconcile, not repost.
second="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$AUTO_GATE" --now-epoch 1100)"
assert_eq "a second autonomous iteration reconciles instead of reposting" "posted_reconciled" "$(jq -r '.status' <<<"$second")"
assert_eq "a second autonomous iteration leaves EXACTLY ONE review" "1" "$(store_count)"
teardown_env

# --- An autonomous gate authorizes one review, not any review. ---
new_env; write_request
printf 'posted\n' >"$STUB_DIR/post-plan"
write_auto_gate "0000000000000000000000000000000000000000000000000000000000000000"
set +e
bash "$POST" post --request-file "$REQUEST" --gate-file "$AUTO_GATE" --now-epoch 1000 >/dev/null 2>&1
rc_key=$?
set -e
assert_eq "an autonomous gate bound to another review key is refused" "3" "$rc_key"
write_auto_gate "" "cccccccccccccccccccccccccccccccccccccccc"
set +e
bash "$POST" post --request-file "$REQUEST" --gate-file "$AUTO_GATE" --now-epoch 1000 >/dev/null 2>&1
rc_head=$?
set -e
assert_eq "an autonomous gate bound to another head is refused" "3" "$rc_head"
write_auto_gate "" "$HEAD" human
set +e
bash "$POST" post --request-file "$REQUEST" --gate-file "$AUTO_GATE" --now-epoch 1000 >/dev/null 2>&1
rc_by=$?
set -e
assert_eq "an autonomous gate claiming a non-daemon authorizer is refused" "3" "$rc_by"
write_auto_gate
jq -c '. + {human_confirmed:true}' "$AUTO_GATE" >"$AUTO_GATE.tmp" && mv "$AUTO_GATE.tmp" "$AUTO_GATE"
set +e
bash "$POST" post --request-file "$REQUEST" --gate-file "$AUTO_GATE" --now-epoch 1000 >/dev/null 2>&1
rc_smuggle=$?
set -e
assert_eq "an autonomous gate smuggling human_confirmed is refused" "3" "$rc_smuggle"
assert_eq "no refused autonomous gate posted anything" "0" "$(store_count)"
teardown_env

# --- "A human confirmed" must cost more than writing the words. This component
# is the only one with posting authority, so it checks the closed key set and the
# nested confirmation itself rather than assuming the caller ran the skill's
# validator first. ---
new_env; write_request
printf 'posted\n' >"$STUB_DIR/post-plan"
forge_gate() { printf '%s' "$1" >"$STUB_DIR/forged.json"; }
try_forged() {
  set +e
  bash "$POST" post --request-file "$REQUEST" --gate-file "$STUB_DIR/forged.json" --now-epoch 1000 >/dev/null 2>&1
  printf '%s' "$?"
  set -e
}
forge_gate '{"effective_event":"COMMENT","human_confirmed":true,"schema":"kc-pr-flow.interactive-post-gate/v1"}'
assert_eq "a hand-written interactive gate with no confirmation is refused" "3" "$(try_forged)"
forge_gate '{"confirmation":null,"effective_event":"COMMENT","human_confirmed":true,"schema":"kc-pr-flow.interactive-post-gate/v1"}'
assert_eq "a null confirmation is refused" "3" "$(try_forged)"
forge_gate '{"confirmation":{"effective_event":"COMMENT","schema":"totally.made.up/v1"},"effective_event":"COMMENT","human_confirmed":true,"schema":"kc-pr-flow.interactive-post-gate/v1"}'
assert_eq "a confirmation of the wrong schema is refused" "3" "$(try_forged)"
forge_gate '{"confirmation":{"effective_event":"APPROVE","schema":"kc-pr-flow.interactive-confirmation/v1"},"effective_event":"COMMENT","human_confirmed":true,"schema":"kc-pr-flow.interactive-post-gate/v1"}'
assert_eq "a confirmation disagreeing on the event is refused" "3" "$(try_forged)"
forge_gate '{"confirmation":{"effective_event":"COMMENT","schema":"kc-pr-flow.interactive-confirmation/v1"},"effective_event":"COMMENT","extra":"x","human_confirmed":true,"schema":"kc-pr-flow.interactive-post-gate/v1"}'
assert_eq "an interactive gate with an extra key is refused" "3" "$(try_forged)"
assert_eq "no forged interactive gate posted anything" "0" "$(store_count)"
# The genuine four-key receipt still authorizes, so this is not blanket refusal.
write_gate
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$GATE" --now-epoch 1000)"
assert_eq "the genuine interactive receipt still authorizes" "posted" "$(jq -r '.status' <<<"$out")"
teardown_env

# --- The outer key set is closed; the confirmation's is deliberately NOT. A real
# typed confirmation carries a decision and blocker evidence, so closing the
# inner set too would reject the very path the typed runtime produces. ---
new_env; write_request
printf 'posted\n' >"$STUB_DIR/post-plan"
RICH_GATE="$STUB_DIR/rich-gate.json"
jq -S -c -n '{schema:"kc-pr-flow.interactive-post-gate/v1",human_confirmed:true,
  effective_event:"COMMENT",
  confirmation:{schema:"kc-pr-flow.interactive-confirmation/v1",source:"typed",
    effective_event:"COMMENT",decision:{schema:"kc-pr-flow.interactive-collation-decision/v1"},
    blocker_evidence:null,confirmed_blocker_refs:[]}}' >"$RICH_GATE"
out="$(bash "$POST" post --request-file "$REQUEST" --gate-file "$RICH_GATE" --now-epoch 1000)"
assert_eq "a confirmation carrying extra typed fields still authorizes" "posted" "$(jq -r '.status' <<<"$out")"
assert_eq "the richer receipt posted exactly one review" "1" "$(store_count)"
teardown_env

# --- The autonomous binding must be sound on its own, not by accident of a
# later check: an unresolved (empty) head must not be matched by an equally
# empty gate field. ---
new_env; write_request
printf 'posted\n' >"$STUB_DIR/post-plan"
AUTO_GATE="$STUB_DIR/auto-gate.json"
# Built directly: write_auto_gate's `${2:-$HEAD}` default would substitute a real
# head for an empty one, so the helper cannot express this case.
jq -S -c -n --arg key "$(review_key_for)" '
  {schema:"kc-pr-flow.autonomous-post-gate/v1",authorized_by:"daemon",
   effective_event:"COMMENT",head_sha:"",review_key:$key}' >"$AUTO_GATE"
set +e
bash "$POST" post --request-file "$REQUEST" --gate-file "$AUTO_GATE" --now-epoch 1000 >/dev/null 2>&1
rc_empty_head=$?
set -e
assert_eq "an empty head binding is refused rather than matched vacuously" "3" "$rc_empty_head"
jq -S -c -n --arg head "$HEAD" '
  {schema:"kc-pr-flow.autonomous-post-gate/v1",authorized_by:"daemon",
   effective_event:"COMMENT",head_sha:$head,review_key:""}' >"$AUTO_GATE"
set +e
bash "$POST" post --request-file "$REQUEST" --gate-file "$AUTO_GATE" --now-epoch 1000 >/dev/null 2>&1
rc_empty_key=$?
set -e
assert_eq "an empty review-key binding is refused" "3" "$rc_empty_key"
assert_eq "an empty binding posted nothing" "0" "$(store_count)"
teardown_env

# --- One document, not a stream. Left unslurped, `jq -e` takes its status from
# the LAST document, so a concatenation could carry a decoy ahead of a real gate.
# Nothing valid is ever a stream, so a stream is refused outright. ---
new_env; write_request
printf 'posted\n' >"$STUB_DIR/post-plan"
STREAM_GATE="$STUB_DIR/stream-gate.json"
GOOD=$(jq -S -c -n --arg key "$(review_key_for)" --arg head "$HEAD" '
  {schema:"kc-pr-flow.autonomous-post-gate/v1",authorized_by:"daemon",
   effective_event:"COMMENT",head_sha:$head,review_key:$key}')
printf '%s\n%s\n' '{"schema":null}' "$GOOD" >"$STREAM_GATE"
set +e
bash "$POST" post --request-file "$REQUEST" --gate-file "$STREAM_GATE" --now-epoch 1000 >/dev/null 2>&1
rc_stream=$?
set -e
assert_eq "a two-document gate file is refused" "3" "$rc_stream"
printf '%s\n%s\n' "$GOOD" "$GOOD" >"$STREAM_GATE"
set +e
bash "$POST" post --request-file "$REQUEST" --gate-file "$STREAM_GATE" --now-epoch 1000 >/dev/null 2>&1
rc_dup=$?
set -e
assert_eq "even a repeated valid gate is refused as a stream" "3" "$rc_dup"
# A non-string binding must reach a verdict, not depend on a jq runtime error.
jq -S -c -n --arg key "$(review_key_for)" '
  {schema:"kc-pr-flow.autonomous-post-gate/v1",authorized_by:"daemon",
   effective_event:"COMMENT",head_sha:1234,review_key:$key}' >"$STREAM_GATE"
set +e
bash "$POST" post --request-file "$REQUEST" --gate-file "$STREAM_GATE" --now-epoch 1000 >/dev/null 2>&1
rc_numeric=$?
set -e
assert_eq "a numeric head binding is refused" "3" "$rc_numeric"
assert_eq "no stream or mistyped gate posted anything" "0" "$(store_count)"
teardown_env

# --- Rollback still governs the autonomous path: the flag, not the gate, is the
# operator's kill switch, so a valid autonomous gate cannot re-enable it. ---
new_env; write_request; write_auto_gate
printf 'posted\n' >"$STUB_DIR/post-plan"
unset KC_PR_FLOW_ONCE_ONLY_POST
set +e
bash "$POST" post --request-file "$REQUEST" --gate-file "$AUTO_GATE" --now-epoch 1000 >/dev/null 2>&1
rc_rollback=$?
set -e
assert_eq "rollback refuses an autonomous post too" "3" "$rc_rollback"
assert_eq "a rolled-back autonomous post writes no review" "0" "$(store_count)"
teardown_env

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
