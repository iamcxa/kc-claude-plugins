#!/usr/bin/env bash
# Contract tests for the best-effort kc-pr-review shadow receipt seam.
# shellcheck disable=SC2016 # Assertions intentionally match literal skill text.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
RUNTIME="$HERE/review-runtime.sh"
SKILL="$HERE/../skills/kc-pr-review/SKILL.md"
TEST_ROOT="$(mktemp -d)"
STATE_ROOT="$TEST_ROOT/state"
CALL_LOG="$TEST_ROOT/observer-calls.log"
LEGACY_PAYLOAD="$TEST_ROOT/legacy-payload.bin"
GITHUB_TRANSCRIPT="$TEST_ROOT/github-transcript.bin"
trap 'chmod -R u+rwX "$TEST_ROOT" 2>/dev/null || true; rm -rf "$TEST_ROOT"' EXIT

PASS=0
FAIL=0
pass() { PASS=$((PASS + 1)); }
fail() { FAIL=$((FAIL + 1)); printf 'FAIL: %s\n' "$1"; }

assert_eq() { # $1=description $2=expected $3=actual
  if [ "$2" = "$3" ]; then pass; else fail "$1 (expected [$2], got [$3])"; fi
}

assert_match() { # $1=description $2=extended-regex $3=actual
  if [[ "$3" =~ $2 ]]; then pass; else fail "$1 ([$3] does not match [$2])"; fi
}

sha256_text() {
  if command -v shasum >/dev/null 2>&1; then
    printf '%s' "$1" | shasum -a 256 | awk '{print $1}'
  else
    printf '%s' "$1" | sha256sum | awk '{print $1}'
  fi
}

file_sha256() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    sha256sum "$1" | awk '{print $1}'
  fi
}

tree_receipt() { # $1=state root
  local root="$1"
  if [ ! -d "$root" ]; then
    printf 'absent\n'
    return
  fi
  find "$root" -type f -print | LC_ALL=C sort | while IFS= read -r file; do
    printf '%s  %s\n' "$(file_sha256 "$file")" "${file#"$root"/}"
  done
}

REPOSITORY='acme/widgets'
PR_NUMBER='42'
BASE_SHA='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
HEAD_SHA='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
MOVED_HEAD='dddddddddddddddddddddddddddddddddddddddd'
CONFIG_HASH='cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc'
REVIEW_KEY="$(sha256_text "$REPOSITORY|$PR_NUMBER|$BASE_SHA|$HEAD_SHA|$CONFIG_HASH")"
REPO_KEY="$(sha256_text "$REPOSITORY")"
OCCURRED_AT='2026-07-22T00:00:00Z'

mkdir -p "$STATE_ROOT"
start_output="$(KC_PR_FLOW_STATE_DIR="$STATE_ROOT" bash "$RUNTIME" start \
  --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$BASE_SHA" --head "$HEAD_SHA" \
  --config-hash "$CONFIG_HASH" --occurred-at "$OCCURRED_AT")"
run_id="$(jq -r '.run_id' <<<"$start_output")"
EVENT_FILE="$STATE_ROOT/$REPO_KEY/pr-$PR_NUMBER/$run_id/events.jsonl"

# Source the production implementation, then wrap only the public observer call
# so tests can count it while still executing the original implementation.
# shellcheck source=/dev/null
. "$RUNTIME"
if declare -F review_runtime_observe >/dev/null; then
  original_observe_definition="$(declare -f review_runtime_observe | sed '1s/review_runtime_observe/review_runtime_observe_actual/')"
  eval "$original_observe_definition"
else
  review_runtime_observe_actual() { return 127; }
fi
review_runtime_observe() {
  printf 'observe\n' >>"$CALL_LOG"
  review_runtime_observe_actual "$@"
}

# Fixed compatibility vector for the sole executable config-hash authority.
# Duplicate/out-of-order capabilities must normalize to sorted unique values.
EXPECTED_CONFIG_JSON='{"capabilities":["code_correctness","security","test_coverage"],"modes":{"agent_tier":"standard","cross_model":true,"full_pass":true,"noise_filter":false,"pr_archetype":"bugfix","probe_required":true},"schema":"kc-pr-flow.review-config/v1"}'
EXPECTED_CONFIG_HASH='770f5d63259827eed61b039ca571cdfea628183c71598399b225caed2f909592'
config_json="$(review_runtime_config_canonical \
  standard bugfix true true true false \
  'security,code_correctness,test_coverage,security' 2>"$TEST_ROOT/config-canonical.err")"
config_json_rc=$?
assert_eq 'config canonical helper accepts the fixed vector' '0' "$config_json_rc"
assert_eq 'config canonical helper emits exact compact sorted v1 JSON' "$EXPECTED_CONFIG_JSON" "$config_json"

config_hash="$(bash "$RUNTIME" config-hash \
  --agent-tier standard \
  --pr-archetype bugfix \
  --full-pass true \
  --probe-required true \
  --cross-model true \
  --noise-filter false \
  --capabilities 'security,code_correctness,test_coverage,security' 2>"$TEST_ROOT/config-hash.err")"
config_hash_rc=$?
assert_eq 'config-hash CLI accepts the fixed vector' '0' "$config_hash_rc"
assert_eq 'config-hash CLI matches the macOS SHA-256 compatibility vector' "$EXPECTED_CONFIG_HASH" "$config_hash"

EXPECTED_DEFAULT_CONFIG_JSON='{"capabilities":[],"modes":{"agent_tier":"lite","cross_model":false,"full_pass":false,"noise_filter":false,"pr_archetype":"mixed","probe_required":false},"schema":"kc-pr-flow.review-config/v1"}'
EXPECTED_DEFAULT_CONFIG_HASH='e16f8b06a9597dff07f99f8253b105b2e01c432f97bbb8d3478a5bd8a8306de1'
default_json="$(review_runtime_config_canonical lite mixed false false false false '' 2>/dev/null)"
assert_eq 'config canonical defaults are explicit and stable' "$EXPECTED_DEFAULT_CONFIG_JSON" "$default_json"
default_hash="$(bash "$RUNTIME" config-hash 2>/dev/null)"
assert_eq 'config-hash CLI defaults are stable' "$EXPECTED_DEFAULT_CONFIG_HASH" "$default_hash"

review_runtime_config_canonical lite mixed yes false false false '' >/dev/null 2>&1
invalid_boolean_rc=$?
assert_eq 'config canonical helper rejects non-boolean mode values' '2' "$invalid_boolean_rc"

review_runtime_config_canonical '' mixed false false false false '' >/dev/null 2>&1
empty_helper_tier_rc=$?
assert_eq 'config canonical helper rejects an explicitly empty tier' '2' "$empty_helper_tier_rc"
review_runtime_config_canonical lite '' false false false false '' >/dev/null 2>&1
empty_helper_archetype_rc=$?
assert_eq 'config canonical helper rejects an explicitly empty archetype' '2' "$empty_helper_archetype_rc"

bash "$RUNTIME" config-hash --agent-tier '' >/dev/null 2>&1
empty_cli_tier_rc=$?
assert_eq 'config-hash CLI rejects an explicitly empty tier option' '2' "$empty_cli_tier_rc"
bash "$RUNTIME" config-hash --pr-archetype '' >/dev/null 2>&1
empty_cli_archetype_rc=$?
assert_eq 'config-hash CLI rejects an explicitly empty archetype option' '2' "$empty_cli_archetype_rc"
for boolean_option in --full-pass --probe-required --cross-model --noise-filter; do
  bash "$RUNTIME" config-hash "$boolean_option" '' >/dev/null 2>&1
  empty_boolean_rc=$?
  assert_eq "config-hash CLI rejects empty $boolean_option" '2' "$empty_boolean_rc"
done

# Direct observer contract remains read-only, typed, and exact-head bound.
before_receipt="$(tree_receipt "$STATE_ROOT")"
observe_output="$(review_runtime_observe_actual "$EVENT_FILE" "$HEAD_SHA" "$REVIEW_KEY" 2>"$TEST_ROOT/observe.err")"
observe_rc=$?
after_receipt="$(tree_receipt "$STATE_ROOT")"
assert_eq 'observe accepts an authoritative exact-head event log' '0' "$observe_rc"
assert_eq 'observe emits the typed observer status schema' 'kc-pr-flow.review-observer-status/v1' "$(jq -r '.schema // empty' <<<"$observe_output" 2>/dev/null)"
assert_eq 'observe reports success without review authority' 'observed' "$(jq -r '.status // empty' <<<"$observe_output" 2>/dev/null)"
assert_eq 'observe reports the exact run identity' "$run_id" "$(jq -r '.run_id // empty' <<<"$observe_output" 2>/dev/null)"
assert_eq 'observe derives no body, comments, event, verdict, or authorization' 'false' "$(jq 'has("authorized") or has("event") or has("verdict") or has("body") or has("comments")' <<<"$observe_output" 2>/dev/null)"
assert_eq 'actual observe leaves the complete receipt tree byte-identical' "$before_receipt" "$after_receipt"

mismatch_output="$(review_runtime_observe_actual "$EVENT_FILE" "$MOVED_HEAD" "$REVIEW_KEY" 2>/dev/null)"
mismatch_rc=$?
assert_eq 'direct observe rejects an exact-head mismatch' '3' "$mismatch_rc"
assert_eq 'direct mismatch is a typed non-observation' 'exact_head_mismatch' "$(jq -r '.reason // empty' <<<"$mismatch_output" 2>/dev/null)"

# Immutable legacy artifacts model the exact payload/transcript the legacy path
# already produced before entering the production shadow seam.
printf '%s\036%s\036%s\036%s\000tail' \
  $'## Review\nSENTINEL raw body' \
  '[{"path":"src/app.sh","body":"SENTINEL raw comment"}]' \
  '1|2|3|4|D' 'COMMENT' >"$LEGACY_PAYLOAD"
printf '%s\r\n%s\r\n' \
  'GET /repos/acme/widgets/pulls/42 -> headRefOid=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb' \
  'legacy mutation transcript: empty' >"$GITHUB_TRANSCRIPT"
legacy_before="$(file_sha256 "$LEGACY_PAYLOAD")"
github_before="$(file_sha256 "$GITHUB_TRANSCRIPT")"

run_shadow() { # $1=enabled $2=head-check-status $3=live-head $4=event-file-or-empty $5=state-root
  local enabled="$1" head_status="$2" live_head="$3" event_file="$4" state_root="$5"
  KC_PR_FLOW_STATE_DIR="$state_root" review_runtime_shadow \
    "$enabled" "$head_status" "$live_head" \
    "$REPOSITORY" "$PR_NUMBER" "$BASE_SHA" "$HEAD_SHA" "$CONFIG_HASH" "$OCCURRED_AT" "$event_file"
}

assert_legacy_unchanged() {
  assert_eq "$1 preserves the full legacy payload byte-for-byte" "$legacy_before" "$(file_sha256 "$LEGACY_PAYLOAD")"
  assert_eq "$1 preserves the full mocked GitHub transcript byte-for-byte" "$github_before" "$(file_sha256 "$GITHUB_TRANSCRIPT")"
}

# Unset and unknown gates execute the production seam but never the observer.
: >"$CALL_LOG"
unset_output="$(run_shadow '' ok "$HEAD_SHA" "$EVENT_FILE" "$STATE_ROOT")"
assert_eq 'unset gate is disabled' 'disabled' "$(jq -r '.status // empty' <<<"$unset_output" 2>/dev/null)"
assert_eq 'unset gate makes zero observer calls' '0' "$(wc -l <"$CALL_LOG" | tr -d ' ')"
assert_legacy_unchanged 'unset gate'

: >"$CALL_LOG"
unknown_output="$(run_shadow banana ok "$HEAD_SHA" "$EVENT_FILE" "$STATE_ROOT")"
assert_eq 'unknown gate is disabled' 'disabled' "$(jq -r '.status // empty' <<<"$unknown_output" 2>/dev/null)"
assert_eq 'unknown gate makes zero observer calls' '0' "$(wc -l <"$CALL_LOG" | tr -d ' ')"
assert_legacy_unchanged 'unknown gate'

# Enabled exact-head path calls the actual observer exactly once and cannot
# alter receipt state, legacy payload, or the GitHub transcript.
: >"$CALL_LOG"
before_receipt="$(tree_receipt "$STATE_ROOT")"
on_output="$(run_shadow on ok "$HEAD_SHA" "$EVENT_FILE" "$STATE_ROOT")"
after_receipt="$(tree_receipt "$STATE_ROOT")"
assert_eq 'enabled exact-head shadow observes the receipt' 'observed' "$(jq -r '.status // empty' <<<"$on_output" 2>/dev/null)"
assert_eq 'enabled exact-head shadow invokes observe exactly once' '1' "$(wc -l <"$CALL_LOG" | tr -d ' ')"
assert_eq 'production shadow with prepared receipt leaves receipt tree byte-identical' "$before_receipt" "$after_receipt"
assert_legacy_unchanged 'enabled exact-head shadow'

# Missing event-file triggers deterministic typed preparation through start,
# then invokes the actual observer exactly once against that new run.
PREPARED_ROOT="$TEST_ROOT/prepared-state"
: >"$CALL_LOG"
prepared_output="$(run_shadow on ok "$HEAD_SHA" '' "$PREPARED_ROOT")"
assert_eq 'missing receipt is prepared and observed' 'observed' "$(jq -r '.status // empty' <<<"$prepared_output" 2>/dev/null)"
assert_eq 'prepared path invokes observe exactly once' '1' "$(wc -l <"$CALL_LOG" | tr -d ' ')"
assert_eq 'prepared status derives the canonical review key' "$REVIEW_KEY" "$(jq -r '.review_key // empty' <<<"$prepared_output" 2>/dev/null)"
assert_eq 'typed preparation creates exactly one authoritative event log' '1' "$(find "$PREPARED_ROOT" -name events.jsonl -type f | wc -l | tr -d ' ')"

# Invalid/missing receipt and a missing jq dependency still call observe once,
# fail open with typed status, and preserve all legacy bytes.
: >"$CALL_LOG"
invalid_output="$(run_shadow on ok "$HEAD_SHA" "$TEST_ROOT/missing-events.jsonl" "$STATE_ROOT" 2>/dev/null)"
assert_eq 'invalid receipt fails open as typed non-observation' 'not_observed' "$(jq -r '.status // empty' <<<"$invalid_output" 2>/dev/null)"
assert_eq 'invalid receipt still invokes observe exactly once' '1' "$(wc -l <"$CALL_LOG" | tr -d ' ')"
assert_legacy_unchanged 'invalid receipt'

original_require_jq_definition="$(declare -f review_runtime_require_jq | sed '1s/review_runtime_require_jq/review_runtime_require_jq_actual/')"
eval "$original_require_jq_definition"
review_runtime_require_jq() { return 69; }
: >"$CALL_LOG"
dependency_output="$(run_shadow on ok "$HEAD_SHA" "$EVENT_FILE" "$STATE_ROOT" 2>/dev/null)"
assert_match 'dependency failure remains typed without jq' '"status":"not_observed"' "$dependency_output"
assert_eq 'dependency failure still invokes observe exactly once' '1' "$(wc -l <"$CALL_LOG" | tr -d ' ')"
assert_legacy_unchanged 'dependency failure'
eval "$(declare -f review_runtime_require_jq_actual | sed '1s/review_runtime_require_jq_actual/review_runtime_require_jq/')"

# Failed/moved head checks block observation in the production seam.
: >"$CALL_LOG"
head_failure_output="$(run_shadow on failed '' "$EVENT_FILE" "$STATE_ROOT")"
assert_eq 'head-check failure is typed' 'head_check_failed' "$(jq -r '.reason // empty' <<<"$head_failure_output" 2>/dev/null)"
assert_eq 'head-check failure prevents observe' '0' "$(wc -l <"$CALL_LOG" | tr -d ' ')"
assert_legacy_unchanged 'head-check failure'

: >"$CALL_LOG"
moved_output="$(run_shadow on ok "$MOVED_HEAD" "$EVENT_FILE" "$STATE_ROOT")"
assert_eq 'moved head is typed' 'exact_head_mismatch' "$(jq -r '.reason // empty' <<<"$moved_output" 2>/dev/null)"
assert_eq 'moved head prevents observe' '0' "$(wc -l <"$CALL_LOG" | tr -d ' ')"
assert_legacy_unchanged 'moved head'

# Skill structure calls the production seam once after collation and before 6c,
# defines every identity input, and delegates preparation/review-key derivation.
shadow_heading_count="$(grep -c '^### 6b-shadow\. Best-effort Shadow Receipt Observer$' "$SKILL" || true)"
shadow_call_count="$(grep -cF '"$CLAUDE_PLUGIN_ROOT/scripts/review-runtime.sh" shadow' "$SKILL" || true)"
shadow_line="$(grep -n '^### 6b-shadow\. Best-effort Shadow Receipt Observer$' "$SKILL" | cut -d: -f1)"
arch_line="$(grep -n '^### 6b-arch\. Optional Architecture Explanation$' "$SKILL" | cut -d: -f1)"
confirm_line="$(grep -n '^### 6c\. User confirmation gate$' "$SKILL" | cut -d: -f1)"
assert_eq 'skill defines exactly one 6b-shadow section' '1' "$shadow_heading_count"
assert_eq 'skill invokes the production shadow seam exactly once' '1' "$shadow_call_count"
if [ -n "$shadow_line" ] && [ -n "$arch_line" ] && [ -n "$confirm_line" ] && [ "$arch_line" -lt "$shadow_line" ] && [ "$shadow_line" -lt "$confirm_line" ]; then
  pass
else
  fail '6b-shadow is the one post-collation seam immediately before 6c'
fi
assert_eq 'skill defines normalized repository identity' '1' "$(grep -cF 'SHADOW_REPOSITORY = normalized `owner/repo`' "$SKILL" || true)"
assert_eq 'skill defines config hash derivation' '1' "$(grep -cF 'SHADOW_CONFIG_HASH = SHA-256' "$SKILL" || true)"
assert_eq 'skill invokes the executable config-hash authority exactly once' '1' "$(grep -cF '"$CLAUDE_PLUGIN_ROOT/scripts/review-runtime.sh" config-hash' "$SKILL" || true)"
assert_eq 'skill delegates review-key derivation to runtime' '1' "$(grep -cF 'derives `SHADOW_REVIEW_KEY`' "$SKILL" || true)"
assert_eq 'skill makes explicit on call once after fresh head success' '1' "$(grep -cF 'exactly one production shadow call' "$SKILL" || true)"
assert_eq 'skill makes failure explicitly fail-open' '1' "$(grep -cF '**Fail open:**' "$SKILL" || true)"

# Runtime seam exposes no network/model/post authority.
shadow_block="$(sed -n '/^review_runtime_shadow() (/,/^)/p' "$RUNTIME")"
if printf '%s\n' "$shadow_block" | grep -Eq '(^|[;&|[:space:]])(gh|curl|codex|gemini)([[:space:]]|$)'; then
  fail 'production shadow seam invokes a network or model tool'
else
  pass
fi
assert_eq 'production shadow seam contains one observer call site' '1' "$(printf '%s\n' "$shadow_block" | grep -c 'review_runtime_observe ' || true)"
if grep -R -F -e 'SENTINEL raw body' -e 'SENTINEL raw comment' "$STATE_ROOT" "$PREPARED_ROOT" >/dev/null 2>&1 ||
  printf '%s' "$on_output$prepared_output$invalid_output$dependency_output" | grep -F 'SENTINEL raw' >/dev/null 2>&1; then
  fail 'shadow durable state or output contains raw review content'
else
  pass
fi

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
