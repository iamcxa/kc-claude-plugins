#!/usr/bin/env bash
# Unit tests for the append-only kc-pr-review shadow receipt runtime.
# shellcheck disable=SC2030,SC2031,SC2329 # Intentional probe subshells and dynamic function overrides.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
RUNTIME="$HERE/review-runtime.sh"
FIXTURE="$HERE/../test/fixtures/review-runtime/valid-events.jsonl"
TEST_STATE_ROOT="$(mktemp -d)"
cleanup() {
  chmod -R u+rwX "$TEST_STATE_ROOT" 2>/dev/null || true
  rm -rf "$TEST_STATE_ROOT"
}
trap cleanup EXIT
export KC_PR_FLOW_STATE_DIR="$TEST_STATE_ROOT"

PASS=0
FAIL=0

pass() {
  PASS=$((PASS + 1))
}

fail() {
  FAIL=$((FAIL + 1))
  printf 'FAIL: %s\n' "$1"
}

assert_eq() { # $1=description $2=expected $3=actual
  if [ "$2" = "$3" ]; then
    pass
  else
    fail "$1 (expected [$2], got [$3])"
  fi
}

assert_match() { # $1=description $2=extended-regex $3=actual
  if [[ "$3" =~ $2 ]]; then
    pass
  else
    fail "$1 ([$3] does not match [$2])"
  fi
}

sha256_text() {
  if command -v shasum >/dev/null 2>&1; then
    printf '%s' "$1" | shasum -a 256 | awk '{print $1}'
  else
    printf '%s' "$1" | sha256sum | awk '{print $1}'
  fi
}

file_mode() {
  if stat -f '%Lp' "$1" >/dev/null 2>&1; then
    stat -f '%Lp' "$1"
  else
    stat -c '%a' "$1"
  fi
}

rehash_event() { # $1=JSON event after semantic mutation
  local input="$1" canonical_payload payload_sha256 run_id sequence event_type
  local event_id without_integrity integrity_sha256
  canonical_payload="$(jq -S -c '.payload' <<<"$input")" || return
  payload_sha256="$(sha256_text "$canonical_payload")"
  run_id="$(jq -r '.run_id' <<<"$input")"
  sequence="$(jq -r '.sequence' <<<"$input")"
  event_type="$(jq -r '.event_type' <<<"$input")"
  event_id="$(sha256_text "$run_id|$sequence|$event_type|$payload_sha256")"
  without_integrity="$(jq -S -c \
    --arg payload_sha256 "$payload_sha256" \
    --arg event_id "$event_id" \
    'del(.integrity_sha256) | .payload_sha256=$payload_sha256 | .event_id=$event_id' <<<"$input")" || return
  integrity_sha256="$(sha256_text "$without_integrity")"
  jq -c --arg integrity_sha256 "$integrity_sha256" '. + {integrity_sha256:$integrity_sha256}' <<<"$without_integrity"
}

rehash_integrity() { # $1=JSON event after envelope-only mutation
  local without_integrity integrity_sha256
  without_integrity="$(jq -S -c 'del(.integrity_sha256)' <<<"$1")" || return
  integrity_sha256="$(sha256_text "$without_integrity")"
  jq -c --arg integrity_sha256 "$integrity_sha256" '. + {integrity_sha256:$integrity_sha256}' <<<"$without_integrity"
}

if [ ! -r "$RUNTIME" ]; then
  fail "review-runtime.sh exists before fresh-run and successor tests can execute"
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  exit 1
fi

# shellcheck source=/dev/null
. "$RUNTIME"

REPOSITORY="acme/widgets"
PR_NUMBER="42"
BASE_SHA="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
HEAD_SHA="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
CONFIG_HASH="cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
OCCURRED_AT="2026-07-22T00:00:00Z"
EXPECTED_REVIEW_KEY="$(sha256_text "$REPOSITORY|$PR_NUMBER|$BASE_SHA|$HEAD_SHA|$CONFIG_HASH")"

control_repository=$'acme/widgets\tunexpected'
control_repo_key="$(sha256_text "$control_repository")"
control_output="$(bash "$RUNTIME" start \
  --repo "$control_repository" \
  --pr "$PR_NUMBER" \
  --base "$BASE_SHA" \
  --head "$HEAD_SHA" \
  --config-hash "$CONFIG_HASH" \
  --occurred-at "$OCCURRED_AT" 2>&1)"
control_rc=$?
assert_eq "start rejects repository identity containing a tab" "2" "$control_rc"
assert_match "start reports invalid repository identity" 'invalid repository identity' "$control_output"
if [ ! -e "$TEST_STATE_ROOT/$control_repo_key" ]; then
  pass
else
  fail "invalid repository identity creates no state directory"
fi

fresh_output="$(bash "$RUNTIME" start \
  --repo "$REPOSITORY" \
  --pr "$PR_NUMBER" \
  --base "$BASE_SHA" \
  --head "$HEAD_SHA" \
  --config-hash "$CONFIG_HASH" \
  --occurred-at "$OCCURRED_AT")"
fresh_rc=$?
assert_eq "fresh start succeeds" "0" "$fresh_rc"
assert_eq "fresh start emits run.started" "run.started" "$(jq -r '.event_type' <<<"$fresh_output")"
assert_eq "review_key is deterministic for the exact head" "$EXPECTED_REVIEW_KEY" "$(jq -r '.review_key' <<<"$fresh_output")"
assert_eq "payload hash excludes jq's output newline" "$(sha256_text '{}')" "$(jq -r '.payload_sha256' <<<"$fresh_output")"
assert_eq "fresh start has no predecessor" "false" "$(jq 'has("predecessor_run_id") or (.payload | has("predecessor_run_id"))' <<<"$fresh_output")"
fresh_run_id="$(jq -r '.run_id' <<<"$fresh_output")"
assert_match "fresh start creates a unique safe run_id" '^run-[A-Za-z0-9._-]+$' "$fresh_run_id"

successor_output="$(bash "$RUNTIME" start \
  --repo "$REPOSITORY" \
  --pr "$PR_NUMBER" \
  --base "$BASE_SHA" \
  --head "$HEAD_SHA" \
  --config-hash "$CONFIG_HASH" \
  --occurred-at "$OCCURRED_AT" \
  --predecessor-run-id "$fresh_run_id" \
  --successor-reason head_appended)"
successor_rc=$?
assert_eq "successor start succeeds" "0" "$successor_rc"
assert_eq "successor points to predecessor" "$fresh_run_id" "$(jq -r '.payload.predecessor_run_id' <<<"$successor_output")"
assert_eq "successor reason is typed" "head_appended" "$(jq -r '.payload.successor_reason' <<<"$successor_output")"
successor_run_id="$(jq -r '.run_id' <<<"$successor_output")"
if [ "$fresh_run_id" != "$successor_run_id" ]; then
  pass
else
  fail "successor must create a fresh run_id"
fi

invalid_reason_output="$(bash "$RUNTIME" start \
  --repo "$REPOSITORY" \
  --pr "$PR_NUMBER" \
  --base "$BASE_SHA" \
  --head "$HEAD_SHA" \
  --config-hash "$CONFIG_HASH" \
  --occurred-at "$OCCURRED_AT" \
  --predecessor-run-id "$fresh_run_id" \
  --successor-reason arbitrary-free-text 2>&1)"
invalid_reason_rc=$?
assert_eq "free-text successor reason is rejected" "2" "$invalid_reason_rc"
assert_match "rejection names the successor reason boundary" 'invalid successor reason' "$invalid_reason_output"
for supported_reason in manual_rerun config_change head_appended head_rewritten recovery_fork; do
  if review_runtime_successor_reason_valid "$supported_reason"; then
    pass
  else
    fail "documented successor reason is accepted: $supported_reason"
  fi
done

# The fixture pins fresh and successor event envelopes independently of start.
validate_output="$(bash "$RUNTIME" validate --event-file "$FIXTURE")"
validate_rc=$?
assert_eq "valid fixture passes validation" "0" "$validate_rc"
assert_eq "validator counts both fixture records" "2" "$(jq -r '.valid' <<<"$validate_output")"
assert_eq "validator finds no invalid fixture records" "0" "$(jq -r '.invalid' <<<"$validate_output")"

append_output="$(bash "$RUNTIME" append --event-file "$FIXTURE")"
append_rc=$?
assert_eq "fixture append succeeds" "0" "$append_rc"
assert_eq "fixture append writes two records" "2" "$(jq -r '.appended' <<<"$append_output")"
assert_eq "fixture append has no duplicates" "0" "$(jq -r '.duplicate' <<<"$append_output")"

REPO_KEY="$(sha256_text "$REPOSITORY")"
FRESH_EVENTS="$TEST_STATE_ROOT/$REPO_KEY/pr-$PR_NUMBER/run-fixture-fresh/events.jsonl"
SUCCESSOR_EVENTS="$TEST_STATE_ROOT/$REPO_KEY/pr-$PR_NUMBER/run-fixture-successor/events.jsonl"
assert_eq "fresh fixture bytes are preserved" "$(sed -n '1p' "$FIXTURE")" "$(sed -n '1p' "$FRESH_EVENTS")"
assert_eq "successor fixture bytes are preserved" "$(sed -n '2p' "$FIXTURE")" "$(sed -n '1p' "$SUCCESSOR_EVENTS")"

duplicate_output="$(bash "$RUNTIME" append --event-file "$FIXTURE")"
duplicate_rc=$?
assert_eq "duplicate append succeeds as a no-op" "0" "$duplicate_rc"
assert_eq "duplicate append reports both records" "2" "$(jq -r '.duplicate' <<<"$duplicate_output")"
assert_eq "duplicate append does not add lines" "1" "$(wc -l <"$FRESH_EVENTS" | tr -d ' ')"

fresh_fixture="$(sed -n '1p' "$FIXTURE")"
future_event="$(rehash_integrity "$(jq -c '.future_optional={mode:"preserve"}' <<<"$fresh_fixture")")"
future_event="$(printf '%s' "$future_event" | sed 's/,"config_hash"/,  "config_hash"/')"
printf '%s\n' "$future_event" >"$TEST_STATE_ROOT/future-event.jsonl"
future_output="$(bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/future-event.jsonl")"
future_rc=$?
assert_eq "supported-v1 unknown optional field reaches duplicate identity check" "1" "$future_rc"
assert_eq "different event with reused event_id is quarantined" "1" "$(jq -r '.quarantined' <<<"$future_output")"
assert_eq "event_id conflict does not mutate accepted events" "1" "$(wc -l <"$FRESH_EVENTS" | tr -d ' ')"

# A new event ID with an additive optional field is accepted byte-for-byte.
optional_new="$(rehash_event "$(jq -c '.sequence=2 | .future_optional={mode:"preserve"}' <<<"$fresh_fixture")")"
optional_new="$(printf '%s' "$optional_new" | sed 's/,"config_hash"/,  "config_hash"/')"
printf '%s\n' "$optional_new" >"$TEST_STATE_ROOT/optional-new.jsonl"
optional_output="$(bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/optional-new.jsonl")"
optional_rc=$?
assert_eq "additive-v1 event appends" "0" "$optional_rc"
assert_eq "additive-v1 append reports one record" "1" "$(jq -r '.appended' <<<"$optional_output")"
assert_eq "additive-v1 original bytes are retained" "$optional_new" "$(sed -n '2p' "$FRESH_EVENTS")"

# Direct validation calls must not overwrite same-named caller variables.
reason='sentinel'
review_runtime_validate_line "$fresh_fixture" >/dev/null
direct_validate_success_rc=$?
assert_eq "direct line validation succeeds for local-scope probe" "0" "$direct_validate_success_rc"
assert_eq "successful line validation preserves caller reason" "sentinel" "$reason"
reason='sentinel'
review_runtime_validate_line '{"invalid":"event"}' >/dev/null
direct_validate_failure_rc=$?
assert_eq "direct invalid line validation fails for local-scope probe" "1" "$direct_validate_failure_rc"
assert_eq "failed line validation preserves caller reason" "sentinel" "$reason"

# The mkdir lock makes the read-check-write append boundary fail closed.
early_reservation="$(dirname "$(dirname "$FRESH_EVENTS")")/.reservation-run-fixture-fresh.lock"
mkdir "$early_reservation"
locked_event="$(rehash_event "$(jq -c '.sequence=3' <<<"$fresh_fixture")")"
printf '%s\n' "$locked_event" >"$TEST_STATE_ROOT/locked-event.jsonl"
locked_output="$(bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/locked-event.jsonl" 2>"$TEST_STATE_ROOT/locked-event.stderr")"
locked_rc=$?
rmdir "$early_reservation"
assert_eq "busy append lock returns temporary-failure status" "75" "$locked_rc"
assert_eq "busy append lock reports one blocked record" "1" "$(jq -r '.blocked' <<<"$locked_output")"
assert_eq "busy append lock leaves accepted state unchanged" "2" "$(wc -l <"$FRESH_EVENTS" | tr -d ' ')"

# Each invalid trust-boundary case is rejected and copied to typed quarantine.
unknown_major="$(rehash_integrity "$(jq -c '.schema="kc-pr-flow.review-event/v2"' <<<"$fresh_fixture")")"
unknown_type="$(rehash_event "$(jq -c '.event_type="future.unknown"' <<<"$fresh_fixture")")"
missing_required="$(rehash_integrity "$(jq -c 'del(.head_sha)' <<<"$fresh_fixture")")"
hash_mismatch="$(jq -c '.payload_sha256="dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"' <<<"$fresh_fixture")"
bad_successor="$(rehash_event "$(jq -c '.payload.successor_reason="arbitrary-free-text"' <<<"$(sed -n '2p' "$FIXTURE")")")"
forbidden_payload="$(rehash_event "$(jq -c '.payload={prompt:"do not persist me"}' <<<"$fresh_fixture")")"

invalid_index=0
for invalid_case in "$unknown_major" "$unknown_type" "$missing_required" "$hash_mismatch" "$bad_successor" "$forbidden_payload"; do
  invalid_index=$((invalid_index + 1))
  invalid_file="$TEST_STATE_ROOT/invalid-$invalid_index.jsonl"
  printf '%s\n' "$invalid_case" >"$invalid_file"
  invalid_output="$(bash "$RUNTIME" append --event-file "$invalid_file")"
  invalid_rc=$?
  assert_eq "invalid case $invalid_index returns quarantine status" "1" "$invalid_rc"
  assert_eq "invalid case $invalid_index reports one quarantined record" "1" "$(jq -r '.quarantined' <<<"$invalid_output")"
done

QUARANTINE_ROOT="$TEST_STATE_ROOT/quarantine"
assert_eq "all invalid/conflicting records have separate quarantine entries" "7" "$(find "$QUARANTINE_ROOT" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
assert_eq "quarantine records unsupported major reason" "1" "$(grep -l 'unsupported_schema_major' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"
assert_eq "quarantine records unknown event reason" "1" "$(grep -l 'unknown_event_type' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"
assert_eq "quarantine records missing-field reason" "1" "$(grep -l 'missing_required_field' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"
assert_eq "quarantine records hash mismatch reason" "1" "$(grep -l 'payload_hash_mismatch' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"
assert_eq "quarantine records successor enum reason" "1" "$(grep -l 'invalid_successor_reason' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"
assert_eq "quarantine records unsupported payload schema reason" "1" "$(grep -l 'unsupported_payload_schema' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"
conflict_dir="$(grep -l 'event_id_conflict' "$QUARANTINE_ROOT"/*/metadata.json | xargs dirname)"
assert_eq "quarantine preserves conflicting original bytes" "$future_event" "$(sed -n '1p' "$conflict_dir/event.jsonl")"
assert_eq "quarantined event file is read-only" "400" "$(file_mode "$conflict_dir/event.jsonl")"
assert_eq "quarantine metadata is read-only" "400" "$(file_mode "$conflict_dir/metadata.json")"

# T1 payload schemas are closed: innocuous keys cannot smuggle raw content.
raw_diff_event="$(rehash_event "$(jq -c '.sequence=4 | .payload={raw_diff:"secret source bytes"}' <<<"$fresh_fixture")")"
cp "$FRESH_EVENTS" "$TEST_STATE_ROOT/before-raw-diff.jsonl"
printf '%s\n' "$raw_diff_event" >"$TEST_STATE_ROOT/raw-diff.jsonl"
raw_diff_output="$(bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/raw-diff.jsonl")"
raw_diff_rc=$?
assert_eq "raw_diff payload is quarantined" "1" "$raw_diff_rc"
assert_eq "raw_diff reports one quarantined record" "1" "$(jq -r '.quarantined' <<<"$raw_diff_output")"
if cmp -s "$TEST_STATE_ROOT/before-raw-diff.jsonl" "$FRESH_EVENTS"; then
  pass
else
  fail "raw_diff rejection leaves accepted events byte-identical"
fi
for raw_variant in rawDiff model-output; do
  variant_event="$(rehash_event "$(jq -c --arg key "$raw_variant" '.sequence=4 | .payload={($key):"secret source bytes"}' <<<"$fresh_fixture")")"
  printf '%s\n' "$variant_event" >"$TEST_STATE_ROOT/raw-variant.jsonl"
  variant_stderr="$TEST_STATE_ROOT/raw-variant.stderr"
  variant_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/raw-variant.jsonl" 2>"$variant_stderr")"
  variant_rc=$?
  assert_eq "$raw_variant representation fails closed" "1" "$variant_rc"
  assert_eq "$raw_variant validation is typed" "1" "$(jq -r '.invalid' <<<"$variant_output")"
  assert_match "$raw_variant uses closed payload reason" 'unsupported_payload_schema' "$(cat "$variant_stderr")"
done

opaque_data_event="$(rehash_event "$(jq -c '.sequence=4 | .payload={data:"raw diff and model output bytes"}' <<<"$fresh_fixture")")"
printf '%s\n' "$opaque_data_event" >"$TEST_STATE_ROOT/opaque-data.jsonl"
opaque_stderr="$TEST_STATE_ROOT/opaque-data.stderr"
opaque_validate_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/opaque-data.jsonl" 2>"$opaque_stderr")"
opaque_validate_rc=$?
assert_eq "innocuous data key cannot bypass the closed T1 payload schema" "1" "$opaque_validate_rc"
assert_eq "opaque data validation counts invalid" "1" "$(jq -r '.invalid' <<<"$opaque_validate_output")"
assert_match "opaque data uses closed payload reason" 'unsupported_payload_schema' "$(cat "$opaque_stderr")"
cp "$FRESH_EVENTS" "$TEST_STATE_ROOT/before-opaque-data.jsonl"
opaque_append_output="$(bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/opaque-data.jsonl")"
opaque_append_rc=$?
assert_eq "opaque data append is quarantined" "1" "$opaque_append_rc"
assert_eq "opaque data append reports quarantine" "1" "$(jq -r '.quarantined' <<<"$opaque_append_output")"
if cmp -s "$TEST_STATE_ROOT/before-opaque-data.jsonl" "$FRESH_EVENTS"; then
  pass
else
  fail "closed payload rejection leaves accepted events byte-identical"
fi

# Existing run.started is immutable exact-head identity authority.
immutable_candidate="$(jq -c '.sequence=5 | .head_sha="dddddddddddddddddddddddddddddddddddddddd"' <<<"$fresh_fixture")"
immutable_review_key="$(sha256_text "$REPOSITORY|$PR_NUMBER|$BASE_SHA|dddddddddddddddddddddddddddddddddddddddd|$CONFIG_HASH")"
immutable_candidate="$(rehash_event "$(jq -c --arg review_key "$immutable_review_key" '.review_key=$review_key' <<<"$immutable_candidate")")"
cp "$FRESH_EVENTS" "$TEST_STATE_ROOT/before-identity-mismatch.jsonl"
printf '%s\n' "$immutable_candidate" >"$TEST_STATE_ROOT/identity-mismatch.jsonl"
immutable_output="$(bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/identity-mismatch.jsonl")"
immutable_rc=$?
assert_eq "same run_id with a different exact head is quarantined" "1" "$immutable_rc"
assert_eq "identity mismatch reports quarantine" "1" "$(jq -r '.quarantined' <<<"$immutable_output")"
assert_eq "identity mismatch has a typed quarantine reason" "1" "$(grep -l 'run_identity_mismatch' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"
if cmp -s "$TEST_STATE_ROOT/before-identity-mismatch.jsonl" "$FRESH_EVENTS"; then
  pass
else
  fail "run identity rejection leaves events.jsonl byte-identical"
fi

# A new state file can only be established by run.started sequence 1.
nonstart_first="$(rehash_event "$(jq -c '.run_id="run-first-nonstart" | .event_type="head.observed" | .sequence=1' <<<"$fresh_fixture")")"
bad_sequence_first="$(rehash_event "$(jq -c '.run_id="run-first-sequence-two" | .sequence=2' <<<"$fresh_fixture")")"
for first_case in "$nonstart_first" "$bad_sequence_first"; do
  first_run_id="$(jq -r '.run_id' <<<"$first_case")"
  printf '%s\n' "$first_case" >"$TEST_STATE_ROOT/$first_run_id.jsonl"
  first_output="$(bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/$first_run_id.jsonl")"
  first_rc=$?
  assert_eq "$first_run_id cannot establish state" "1" "$first_rc"
  assert_eq "$first_run_id reports quarantine" "1" "$(jq -r '.quarantined' <<<"$first_output")"
  if [ ! -e "$TEST_STATE_ROOT/$REPO_KEY/pr-$PR_NUMBER/$first_run_id/events.jsonl" ]; then
    pass
  else
    fail "$first_run_id must not create events.jsonl"
  fi
done
assert_eq "malformed first events use a typed reason" "2" "$(grep -l 'first_event_must_start_run' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"

# A successor is always fresh; it cannot point to its own run_id.
self_predecessor="$(rehash_event "$(jq -c '.run_id="run-self-predecessor" | .payload.predecessor_run_id="run-self-predecessor"' <<<"$(sed -n '2p' "$FIXTURE")")")"
printf '%s\n' "$self_predecessor" >"$TEST_STATE_ROOT/self-predecessor.jsonl"
self_validate_stderr="$TEST_STATE_ROOT/self-predecessor.stderr"
self_validate_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/self-predecessor.jsonl" 2>"$self_validate_stderr")"
self_validate_rc=$?
assert_eq "self predecessor fails direct validation" "1" "$self_validate_rc"
assert_eq "self predecessor validation counts invalid" "1" "$(jq -r '.invalid' <<<"$self_validate_output")"
assert_match "self predecessor validation exposes typed reason" 'self_predecessor_run_id' "$(cat "$self_validate_stderr")"
self_append_output="$(bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/self-predecessor.jsonl")"
self_append_rc=$?
assert_eq "self predecessor append is quarantined" "1" "$self_append_rc"
assert_eq "self predecessor reports quarantine" "1" "$(jq -r '.quarantined' <<<"$self_append_output")"
if [ ! -e "$TEST_STATE_ROOT/$REPO_KEY/pr-$PR_NUMBER/run-self-predecessor/events.jsonl" ]; then
  pass
else
  fail "self predecessor must not establish run state"
fi

# Direct filesystem API calls preserve a caller-selected umask on success and failure.
umask 027
before_umask="$(umask)"
review_runtime_start "$REPOSITORY" "$PR_NUMBER" "$BASE_SHA" "$HEAD_SHA" "$CONFIG_HASH" "$OCCURRED_AT" >/dev/null 2>&1
start_direct_rc=$?
after_umask="$(umask)"
assert_eq "direct start succeeds for umask probe" "0" "$start_direct_rc"
assert_eq "direct start preserves caller umask" "$before_umask" "$after_umask"

umask 027
before_umask="$(umask)"
review_runtime_append_line "$fresh_fixture" >/dev/null 2>&1
append_direct_rc=$?
after_umask="$(umask)"
assert_eq "direct duplicate append succeeds for umask probe" "0" "$append_direct_rc"
assert_eq "direct append success preserves caller umask" "$before_umask" "$after_umask"

umask 027
before_umask="$(umask)"
review_runtime_append_line "$unknown_major" >/dev/null 2>&1
append_failure_rc=$?
after_umask="$(umask)"
assert_eq "direct invalid append returns quarantine status" "1" "$append_failure_rc"
assert_eq "direct append failure preserves caller umask" "$before_umask" "$after_umask"

umask 027
before_umask="$(umask)"
review_runtime_quarantine '{"new":"invalid quarantine probe"}' invalid_json >/dev/null 2>&1
quarantine_direct_rc=$?
after_umask="$(umask)"
assert_eq "direct quarantine succeeds for umask probe" "0" "$quarantine_direct_rc"
assert_eq "direct quarantine preserves caller umask" "$before_umask" "$after_umask"
umask 022

# Fixed compatibility vector plus an explicit in-source canonicalization contract.
assert_eq "fixture review_key compatibility vector" "f7da797d4da630b15f3780db37ebb6c8c95e5a6519bf0a0eaee9e445eba5cc61" "$(jq -r '.review_key' <<<"$fresh_fixture")"
assert_eq "fixture payload hash compatibility vector" "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a" "$(jq -r '.payload_sha256' <<<"$fresh_fixture")"
assert_eq "fixture event ID compatibility vector" "0e5d2485e2fae5701e2930be4512ebe71b04813911bb200668be91032d71a547" "$(jq -r '.event_id' <<<"$fresh_fixture")"
assert_eq "fixture integrity hash compatibility vector" "355b50878d254cb42d4b1811bdabf687f87d4e0b7e748a80be23fed73ce77bd8" "$(jq -r '.integrity_sha256' <<<"$fresh_fixture")"
for contract_phrase in \
  'UTF-8 JSON bytes' \
  'jq -S -c' \
  'no trailing newline' \
  'payload_sha256 = sha256(canonical payload bytes)' \
  'event_id = sha256(run_id|sequence|event_type|payload_sha256)' \
  'review_key = sha256(repository|pr_number|base_sha|head_sha|config_hash)' \
  'excluding only integrity_sha256'; do
  if grep -F "$contract_phrase" "$RUNTIME" >/dev/null; then
    pass
  else
    fail "runtime documents canonicalization contract: $contract_phrase"
  fi
done

# Quarantine publication rejects corrupt deterministic destinations and is
# idempotent only when the complete read-only receipt matches exactly.
empty_quarantine_line='{"case":"precreated empty quarantine"}'
empty_quarantine_hash="$(sha256_text "$empty_quarantine_line")"
empty_quarantine_dir="$QUARANTINE_ROOT/$empty_quarantine_hash-invalid_json"
mkdir "$empty_quarantine_dir"
review_runtime_quarantine "$empty_quarantine_line" invalid_json >/dev/null 2>&1
empty_quarantine_rc=$?
assert_eq "precreated empty quarantine directory fails closed" "74" "$empty_quarantine_rc"

mismatch_quarantine_line='{"case":"mismatched quarantine"}'
mismatch_quarantine_hash="$(sha256_text "$mismatch_quarantine_line")"
mismatch_quarantine_dir="$QUARANTINE_ROOT/$mismatch_quarantine_hash-invalid_json"
mkdir "$mismatch_quarantine_dir"
printf '%s\n' '{"wrong":"event"}' >"$mismatch_quarantine_dir/event.jsonl"
printf '%s\n' '{"reason":"invalid_json","event_sha256":"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","quarantined_at":"2026-07-22T00:00:00Z"}' >"$mismatch_quarantine_dir/metadata.json"
chmod 0400 "$mismatch_quarantine_dir/event.jsonl" "$mismatch_quarantine_dir/metadata.json"
chmod 0500 "$mismatch_quarantine_dir"
review_runtime_quarantine "$mismatch_quarantine_line" invalid_json >/dev/null 2>&1
mismatch_quarantine_rc=$?
assert_eq "mismatched quarantine artifacts fail closed" "74" "$mismatch_quarantine_rc"

idempotent_quarantine_line='{"case":"complete idempotent quarantine"}'
idempotent_quarantine_hash="$(sha256_text "$idempotent_quarantine_line")"
idempotent_quarantine_dir="$QUARANTINE_ROOT/$idempotent_quarantine_hash-invalid_json"
review_runtime_quarantine "$idempotent_quarantine_line" invalid_json >/dev/null 2>&1
idempotent_first_rc=$?
idempotent_event_hash_before="$(review_runtime_sha256 <"$idempotent_quarantine_dir/event.jsonl")"
idempotent_metadata_hash_before="$(review_runtime_sha256 <"$idempotent_quarantine_dir/metadata.json")"
review_runtime_quarantine "$idempotent_quarantine_line" invalid_json >/dev/null 2>&1
idempotent_second_rc=$?
assert_eq "first complete quarantine publication succeeds" "0" "$idempotent_first_rc"
assert_eq "matching complete quarantine is idempotent" "0" "$idempotent_second_rc"
assert_eq "idempotent quarantine preserves event bytes" "$idempotent_event_hash_before" "$(review_runtime_sha256 <"$idempotent_quarantine_dir/event.jsonl")"
assert_eq "idempotent quarantine preserves metadata bytes" "$idempotent_metadata_hash_before" "$(review_runtime_sha256 <"$idempotent_quarantine_dir/metadata.json")"
assert_eq "idempotent quarantine event stays read-only" "400" "$(file_mode "$idempotent_quarantine_dir/event.jsonl")"
assert_eq "idempotent quarantine metadata stays read-only" "400" "$(file_mode "$idempotent_quarantine_dir/metadata.json")"
assert_eq "idempotent quarantine directory stays read-only" "500" "$(file_mode "$idempotent_quarantine_dir")"

# Quarantine uses the same owned-lock lifecycle as event append. A forced
# publication failure cleans both private temp and owned lock, then retries.
forced_quarantine_state="$(mktemp -d)"
forced_quarantine_line='{"case":"forced quarantine publication failure"}'
forced_quarantine_hash="$(sha256_text "$forced_quarantine_line")"
forced_quarantine_root="$forced_quarantine_state/quarantine"
forced_quarantine_dir="$forced_quarantine_root/$forced_quarantine_hash-invalid_json"
forced_quarantine_lock="$forced_quarantine_root/.$forced_quarantine_hash-invalid_json.lock"
( export KC_PR_FLOW_STATE_DIR="$forced_quarantine_state" KC_PR_FLOW_MAX_QUARANTINE_BYTES=1; review_runtime_quarantine "$forced_quarantine_line" invalid_json >/dev/null 2>&1 )
forced_quarantine_rc=$?
assert_eq "forced quarantine publication failure returns durability status" "73" "$forced_quarantine_rc"
assert_eq "forced quarantine failure publishes no receipt" "false" "$([ -e "$forced_quarantine_dir" ] && printf true || printf false)"
assert_eq "forced quarantine failure leaves no owned lock" "false" "$([ -e "$forced_quarantine_lock" ] && printf true || printf false)"
assert_eq "forced quarantine failure leaves no private temp" "0" "$(find "$forced_quarantine_root" -maxdepth 1 -name ".$forced_quarantine_hash-invalid_json.tmp.*" 2>/dev/null | wc -l | tr -d ' ')"
( export KC_PR_FLOW_STATE_DIR="$forced_quarantine_state"; review_runtime_quarantine "$forced_quarantine_line" invalid_json >/dev/null 2>&1 )
forced_quarantine_retry_rc=$?
assert_eq "retry publishes complete quarantine receipt" "0" "$forced_quarantine_retry_rc"
assert_eq "retry event is read-only" "400" "$(file_mode "$forced_quarantine_dir/event.jsonl")"
assert_eq "retry metadata is read-only" "400" "$(file_mode "$forced_quarantine_dir/metadata.json")"
assert_eq "retry receipt is read-only" "500" "$(file_mode "$forced_quarantine_dir")"

dead_quarantine_state="$(mktemp -d)"
dead_quarantine_line='{"case":"dead quarantine lock owner"}'
dead_quarantine_hash="$(sha256_text "$dead_quarantine_line")"
dead_quarantine_root="$dead_quarantine_state/quarantine"
dead_quarantine_lock="$dead_quarantine_root/.$dead_quarantine_hash-invalid_json.lock"
mkdir "$dead_quarantine_root" "$dead_quarantine_lock"
printf '%s\n' '999999' >"$dead_quarantine_lock/owner.pid"
( export KC_PR_FLOW_STATE_DIR="$dead_quarantine_state"; review_runtime_quarantine "$dead_quarantine_line" invalid_json >/dev/null 2>&1 )
dead_quarantine_rc=$?
assert_eq "dead quarantine lock owner is reclaimed once" "0" "$dead_quarantine_rc"
assert_eq "dead quarantine owner retry cleans lock" "false" "$([ -e "$dead_quarantine_lock" ] && printf true || printf false)"
if [ -d "$dead_quarantine_lock" ]; then rm -f "$dead_quarantine_lock/owner.pid"; rmdir "$dead_quarantine_lock"; fi

for owner_case in active malformed missing; do
  owner_state="$(mktemp -d)"
  owner_line="{\"case\":\"$owner_case quarantine lock owner\"}"
  owner_hash="$(sha256_text "$owner_line")"
  owner_root="$owner_state/quarantine"
  owner_lock="$owner_root/.$owner_hash-invalid_json.lock"
  mkdir "$owner_root" "$owner_lock"
  case "$owner_case" in
    active) printf '%s\n' "$$" >"$owner_lock/owner.pid" ;;
    malformed) printf '%s\n' 'not-a-pid' >"$owner_lock/owner.pid" ;;
    missing) : ;;
  esac
  ( export KC_PR_FLOW_STATE_DIR="$owner_state"; review_runtime_quarantine "$owner_line" invalid_json >/dev/null 2>&1 )
  owner_rc=$?
  assert_eq "$owner_case quarantine lock remains fail-closed" "75" "$owner_rc"
  assert_eq "$owner_case quarantine lock is not reclaimed" "true" "$([ -d "$owner_lock" ] && printf true || printf false)"
  rm -f "$owner_lock/owner.pid"; rmdir "$owner_lock"
done

# start publishes no run when the complete initial log cannot pass durability
# limits; private build artifacts must also be cleaned.
atomic_start_state="$(mktemp -d)"
atomic_start_output="$(KC_PR_FLOW_STATE_DIR="$atomic_start_state" KC_PR_FLOW_MAX_EVENTS_BYTES=1 bash "$RUNTIME" start \
  --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$BASE_SHA" --head "$HEAD_SHA" \
  --config-hash "$CONFIG_HASH" --occurred-at "$OCCURRED_AT" 2>&1)"
atomic_start_rc=$?
assert_eq "oversized initial log fails before publication" "73" "$atomic_start_rc"
assert_match "oversized initial log reports durability limit" 'events size limit' "$atomic_start_output"
assert_eq "failed start publishes no events file" "0" "$(find "$atomic_start_state" -name events.jsonl | wc -l | tr -d ' ')"
assert_eq "failed start publishes no run directory" "0" "$(find "$atomic_start_state" -type d -name 'run-*' | wc -l | tr -d ' ')"
assert_eq "failed start leaves no private run build" "0" "$(find "$atomic_start_state" -type d -name '.run.*' | wc -l | tr -d ' ')"

# Sequence authority and lock lifecycle use an isolated accepted log.
sequence_state="$(mktemp -d)"
sequence_seed="$TEST_STATE_ROOT/sequence-seed.jsonl"
printf '%s\n' "$fresh_fixture" >"$sequence_seed"
sequence_seed_output="$(KC_PR_FLOW_STATE_DIR="$sequence_state" bash "$RUNTIME" append --event-file "$sequence_seed")"
sequence_seed_rc=$?
assert_eq "sequence fixture seed succeeds" "0" "$sequence_seed_rc"
assert_eq "sequence fixture seed appends one" "1" "$(jq -r '.appended' <<<"$sequence_seed_output")"
sequence_events="$sequence_state/$REPO_KEY/pr-$PR_NUMBER/run-fixture-fresh/events.jsonl"

sequence_two="$(rehash_event "$(jq -c '.event_type="head.observed" | .sequence=2 | .payload={}' <<<"$fresh_fixture")")"
printf '%s\n' "$sequence_two" >"$TEST_STATE_ROOT/sequence-two.jsonl"
sequence_two_output="$(KC_PR_FLOW_STATE_DIR="$sequence_state" bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/sequence-two.jsonl")"
sequence_two_rc=$?
assert_eq "valid next sequence appends" "0" "$sequence_two_rc"
assert_eq "valid next sequence reports one append" "1" "$(jq -r '.appended' <<<"$sequence_two_output")"

sequence_before_duplicate="$TEST_STATE_ROOT/sequence-before-duplicate.jsonl"
cp "$sequence_events" "$sequence_before_duplicate"
duplicate_again_output="$(KC_PR_FLOW_STATE_DIR="$sequence_state" bash "$RUNTIME" append --event-file "$sequence_seed")"
duplicate_again_rc=$?
assert_eq "exact event-id duplicate remains a no-op before sequence gating" "0" "$duplicate_again_rc"
assert_eq "exact duplicate reports duplicate" "1" "$(jq -r '.duplicate' <<<"$duplicate_again_output")"
if cmp -s "$sequence_before_duplicate" "$sequence_events"; then pass; else fail "exact duplicate changes sequence log"; fi

duplicate_sequence="$(rehash_event "$(jq -c '.event_type="run.finished" | .sequence=2 | .payload={}' <<<"$fresh_fixture")")"
gap_sequence="$(rehash_event "$(jq -c '.event_type="run.invalidated" | .sequence=4 | .payload={}' <<<"$fresh_fixture")")"
backward_sequence="$(rehash_event "$(jq -c '.event_type="run.finished" | .sequence=1 | .payload={}' <<<"$fresh_fixture")")"
for sequence_case in "$duplicate_sequence" "$gap_sequence" "$backward_sequence"; do
  sequence_case_id="$(jq -r '.event_id' <<<"$sequence_case")"
  sequence_case_file="$TEST_STATE_ROOT/$sequence_case_id.jsonl"
  cp "$sequence_events" "$TEST_STATE_ROOT/$sequence_case_id.before"
  printf '%s\n' "$sequence_case" >"$sequence_case_file"
  sequence_case_output="$(KC_PR_FLOW_STATE_DIR="$sequence_state" bash "$RUNTIME" append --event-file "$sequence_case_file")"
  sequence_case_rc=$?
  assert_eq "noncontiguous sequence $sequence_case_id is quarantined" "1" "$sequence_case_rc"
  assert_eq "noncontiguous sequence $sequence_case_id reports quarantine" "1" "$(jq -r '.quarantined' <<<"$sequence_case_output")"
  if cmp -s "$TEST_STATE_ROOT/$sequence_case_id.before" "$sequence_events"; then pass; else fail "sequence conflict mutates accepted log: $sequence_case_id"; fi
done

sequence_run_dir="$(dirname "$sequence_events")"
sequence_lock="$(dirname "$sequence_run_dir")/.reservation-run-fixture-fresh.lock"

# An owned lock records the long-lived sourced-shell caller, not a short-lived
# command-substitution helper. A live owner must never be reclaimed.
owner_pid_lock="$(dirname "$sequence_run_dir")/.reservation-owner-pid-probe.lock"
owner_pid_ready="$TEST_STATE_ROOT/owner-pid.ready"
owner_pid_release="$TEST_STATE_ROOT/owner-pid.release"
(
  REVIEW_RUNTIME_LOCK_OWNER_PID=''
  review_runtime_acquire_owned_lock "$owner_pid_lock" || exit 75
  printf '%s\n' ready >"$owner_pid_ready"
  while [ ! -e "$owner_pid_release" ]; do sleep 0.01; done
  review_runtime_release_owned_lock "$owner_pid_lock" "$REVIEW_RUNTIME_LOCK_OWNER_PID"
) &
owner_shell_pid=$!
owner_ready_attempts=0
while [ ! -e "$owner_pid_ready" ] && kill -0 "$owner_shell_pid" 2>/dev/null && [ "$owner_ready_attempts" -lt 100 ]; do
  owner_ready_attempts=$((owner_ready_attempts + 1))
  sleep 0.01
done
stored_owner_pid="$(cat "$owner_pid_lock/owner.pid" 2>/dev/null || true)"
assert_eq "owned lock records background sourced-shell PID" "$owner_shell_pid" "$stored_owner_pid"
if kill -0 "$stored_owner_pid" 2>/dev/null; then pass; else fail "owned lock records a live owner PID"; fi
(
  REVIEW_RUNTIME_LOCK_OWNER_PID=''
  review_runtime_acquire_owned_lock "$owner_pid_lock"
)
live_owner_contender_rc=$?
assert_eq "contender cannot reclaim a live sourced-shell owner" "75" "$live_owner_contender_rc"
: >"$owner_pid_release"
wait "$owner_shell_pid"; owner_shell_rc=$?
assert_eq "background sourced-shell owner releases cleanly" "0" "$owner_shell_rc"
if [ -d "$owner_pid_lock" ]; then rm -f "$owner_pid_lock/owner.pid"; rmdir "$owner_pid_lock"; fi

dead_owner_candidate="$(rehash_event "$(jq -c '.event_type="head.observed" | .sequence=3 | .payload={}' <<<"$fresh_fixture")")"
printf '%s\n' "$dead_owner_candidate" >"$TEST_STATE_ROOT/dead-owner-candidate.jsonl"
mkdir "$sequence_lock"
printf '%s\n' '999999' >"$sequence_lock/owner.pid"
dead_owner_output="$(KC_PR_FLOW_STATE_DIR="$sequence_state" bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/dead-owner-candidate.jsonl" 2>"$TEST_STATE_ROOT/dead-owner.stderr")"
dead_owner_rc=$?
assert_eq "dead lock owner is reclaimed once" "0" "$dead_owner_rc"
assert_eq "dead-owner retry appends next event" "1" "$(jq -r '.appended' <<<"$dead_owner_output")"
assert_eq "dead-owner lock is cleaned" "false" "$([ -e "$sequence_lock" ] && printf true || printf false)"
if [ -d "$sequence_lock" ]; then chmod 0700 "$sequence_lock"; rm -f "$sequence_lock/owner.pid"; rmdir "$sequence_lock"; fi

active_owner_candidate="$(rehash_event "$(jq -c '.event_type="run.finished" | .sequence=4 | .payload={}' <<<"$fresh_fixture")")"
printf '%s\n' "$active_owner_candidate" >"$TEST_STATE_ROOT/active-owner-candidate.jsonl"
mkdir "$sequence_lock"
printf '%s\n' "$$" >"$sequence_lock/owner.pid"
active_owner_output="$(KC_PR_FLOW_STATE_DIR="$sequence_state" KC_PR_FLOW_RESERVATION_WAIT_ATTEMPTS=2 bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/active-owner-candidate.jsonl" 2>"$TEST_STATE_ROOT/active-owner.stderr")"
active_owner_rc=$?
assert_eq "active lock owner remains fail-closed" "75" "$active_owner_rc"
assert_eq "active lock owner reports blocked" "1" "$(jq -r '.blocked' <<<"$active_owner_output")"
assert_eq "active owner lock is not reclaimed" "true" "$([ -d "$sequence_lock" ] && printf true || printf false)"
rm -f "$sequence_lock/owner.pid"; rmdir "$sequence_lock"

mkdir "$sequence_lock"
printf '%s\n' 'not-a-pid' >"$sequence_lock/owner.pid"
malformed_owner_output="$(KC_PR_FLOW_STATE_DIR="$sequence_state" KC_PR_FLOW_RESERVATION_WAIT_ATTEMPTS=2 bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/active-owner-candidate.jsonl" 2>"$TEST_STATE_ROOT/malformed-owner.stderr")"
malformed_owner_rc=$?
assert_eq "malformed lock owner remains fail-closed" "75" "$malformed_owner_rc"
assert_eq "malformed lock owner reports blocked" "1" "$(jq -r '.blocked' <<<"$malformed_owner_output")"
assert_eq "malformed owner lock is not reclaimed" "true" "$([ -d "$sequence_lock" ] && printf true || printf false)"
rm -f "$sequence_lock/owner.pid"; rmdir "$sequence_lock"

atomic_before="$TEST_STATE_ROOT/atomic-before.jsonl"
cp "$sequence_events" "$atomic_before"
atomic_limit="$(wc -c <"$sequence_events" | tr -d ' ')"
atomic_append_output="$(KC_PR_FLOW_STATE_DIR="$sequence_state" KC_PR_FLOW_MAX_EVENTS_BYTES="$atomic_limit" bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/active-owner-candidate.jsonl" 2>"$TEST_STATE_ROOT/atomic-append.stderr")"
atomic_append_rc=$?
assert_eq "oversized next log fails closed" "74" "$atomic_append_rc"
assert_eq "oversized next log reports blocked" "1" "$(jq -r '.blocked' <<<"$atomic_append_output")"
if cmp -s "$atomic_before" "$sequence_events"; then pass; else fail "failed atomic append changes original events bytes"; fi
assert_eq "failed atomic append leaves no partial temp" "0" "$(find "$sequence_run_dir" -maxdepth 1 -name '.events.next.*' | wc -l | tr -d ' ')"
assert_eq "failed atomic append cleans owned lock" "false" "$([ -e "$sequence_lock" ] && printf true || printf false)"

# Existing malformed ordering blocks all mutation.
malformed_state="$(mktemp -d)"
malformed_run_dir="$malformed_state/$REPO_KEY/pr-$PR_NUMBER/run-fixture-fresh"
mkdir -p "$malformed_run_dir"
malformed_three="$(rehash_event "$(jq -c '.event_type="head.observed" | .sequence=3 | .payload={}' <<<"$fresh_fixture")")"
printf '%s\n%s\n' "$fresh_fixture" "$malformed_three" >"$malformed_run_dir/events.jsonl"
chmod 0600 "$malformed_run_dir/events.jsonl"
cp "$malformed_run_dir/events.jsonl" "$TEST_STATE_ROOT/malformed-before.jsonl"
malformed_four="$(rehash_event "$(jq -c '.event_type="head.observed" | .sequence=4 | .payload={}' <<<"$fresh_fixture")")"
printf '%s\n' "$malformed_four" >"$TEST_STATE_ROOT/malformed-four.jsonl"
malformed_output="$(KC_PR_FLOW_STATE_DIR="$malformed_state" bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/malformed-four.jsonl" 2>"$TEST_STATE_ROOT/malformed-existing.stderr")"
malformed_rc=$?
assert_eq "existing noncontiguous log blocks append" "74" "$malformed_rc"
assert_eq "existing noncontiguous log reports blocked" "1" "$(jq -r '.blocked' <<<"$malformed_output")"
if cmp -s "$TEST_STATE_ROOT/malformed-before.jsonl" "$malformed_run_dir/events.jsonl"; then pass; else fail "blocked malformed log was mutated"; fi

# Managed state components never follow symlinks.
start_link_outside="$(mktemp -d)"
start_link_root="$TEST_STATE_ROOT/start-state-link"
ln -s "$start_link_outside" "$start_link_root"
symlink_start_output="$(KC_PR_FLOW_STATE_DIR="$start_link_root" bash "$RUNTIME" start --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$BASE_SHA" --head "$HEAD_SHA" --config-hash "$CONFIG_HASH" --occurred-at "$OCCURRED_AT" 2>&1)"
symlink_start_rc=$?
assert_eq "symlink state root makes start fail closed" "74" "$symlink_start_rc"
assert_match "symlink state root reports managed-path failure" 'unsafe managed state root' "$symlink_start_output"
assert_eq "start writes nothing through state-root symlink" "0" "$(find "$start_link_outside" -mindepth 1 | wc -l | tr -d ' ')"

append_link_state="$(mktemp -d)"
append_link_outside="$(mktemp -d)"
ln -s "$append_link_outside" "$append_link_state/$REPO_KEY"
symlink_append_output="$(KC_PR_FLOW_STATE_DIR="$append_link_state" bash "$RUNTIME" append --event-file "$sequence_seed" 2>"$TEST_STATE_ROOT/symlink-append.stderr")"
symlink_append_rc=$?
assert_eq "symlink repo-key makes append fail closed" "74" "$symlink_append_rc"
assert_eq "append reports blocked for symlink component" "1" "$(jq -r '.blocked' <<<"$symlink_append_output")"
assert_eq "append writes nothing through repo-key symlink" "0" "$(find "$append_link_outside" -mindepth 1 | wc -l | tr -d ' ')"

quarantine_link_state="$(mktemp -d)"
quarantine_link_outside="$(mktemp -d)"
ln -s "$quarantine_link_outside" "$quarantine_link_state/quarantine"
( export KC_PR_FLOW_STATE_DIR="$quarantine_link_state"; review_runtime_quarantine '{"symlink":"probe"}' invalid_json >/dev/null 2>&1 )
symlink_quarantine_rc=$?
assert_eq "symlink quarantine root fails closed" "74" "$symlink_quarantine_rc"
assert_eq "quarantine writes nothing through managed symlink" "0" "$(find "$quarantine_link_outside" -mindepth 1 | wc -l | tr -d ' ')"

# Two first publishers for the same caller-supplied run_id serialize on one
# pr-level reservation. One publishes; the follower observes an exact duplicate.
concurrent_state="$(mktemp -d)"
concurrent_optional="$(awk 'BEGIN { for (i=0; i<60000; i++) printf "x" }')"
concurrent_event="$(rehash_event "$(jq -c --arg optional "$concurrent_optional" '.run_id="run-concurrent-first" | .future_optional=$optional' <<<"$fresh_fixture")")"
concurrent_file="$TEST_STATE_ROOT/concurrent-first.jsonl"
printf '%s\n' "$concurrent_event" >"$concurrent_file"
KC_PR_FLOW_STATE_DIR="$concurrent_state" bash "$RUNTIME" append --event-file "$concurrent_file" >"$TEST_STATE_ROOT/concurrent-one.out" 2>"$TEST_STATE_ROOT/concurrent-one.err" &
concurrent_one_pid=$!
KC_PR_FLOW_STATE_DIR="$concurrent_state" bash "$RUNTIME" append --event-file "$concurrent_file" >"$TEST_STATE_ROOT/concurrent-two.out" 2>"$TEST_STATE_ROOT/concurrent-two.err" &
concurrent_two_pid=$!
wait "$concurrent_one_pid"; concurrent_one_rc=$?
wait "$concurrent_two_pid"; concurrent_two_rc=$?
assert_eq "first concurrent append exits cleanly" "0" "$concurrent_one_rc"
assert_eq "second concurrent append exits cleanly" "0" "$concurrent_two_rc"
concurrent_appended=$(( $(jq -r '.appended // 0' "$TEST_STATE_ROOT/concurrent-one.out") + $(jq -r '.appended // 0' "$TEST_STATE_ROOT/concurrent-two.out") ))
concurrent_duplicates=$(( $(jq -r '.duplicate // 0' "$TEST_STATE_ROOT/concurrent-one.out") + $(jq -r '.duplicate // 0' "$TEST_STATE_ROOT/concurrent-two.out") ))
assert_eq "exactly one concurrent process performs first publication" "1" "$concurrent_appended"
assert_eq "concurrent follower resolves as duplicate" "1" "$concurrent_duplicates"
concurrent_pr_dir="$concurrent_state/$REPO_KEY/pr-$PR_NUMBER"
concurrent_events="$concurrent_pr_dir/run-concurrent-first/events.jsonl"
assert_eq "concurrent publication has one events log" "1" "$(find "$concurrent_pr_dir" -name events.jsonl | wc -l | tr -d ' ')"
assert_eq "concurrent publication has no nested private run" "0" "$(find "$concurrent_pr_dir" -type d -name '.run-new.*' | wc -l | tr -d ' ')"
assert_eq "concurrent publication has no stranded reservation" "0" "$(find "$concurrent_pr_dir" -maxdepth 1 -type d -name '.reservation-*.lock' | wc -l | tr -d ' ')"
assert_eq "append serialization leaves no inner events lock" "0" "$(find "$concurrent_pr_dir" -type d -name '.events.lock' | wc -l | tr -d ' ')"
concurrent_validate="$(KC_PR_FLOW_STATE_DIR="$concurrent_state" bash "$RUNTIME" validate --event-file "$concurrent_events")"
assert_eq "concurrent events log validates" "0" "$(jq -r '.invalid' <<<"$concurrent_validate")"

# Sourcing defines functions only: no output and no caller option/umask changes.
source_probe="$(bash -c 'before_options="$(set +o)"; before_umask="$(umask)"; output="$(. "$1")"; after_options="$(set +o)"; after_umask="$(umask)"; [ -z "$output" ] && [ "$before_options" = "$after_options" ] && [ "$before_umask" = "$after_umask" ]' _ "$RUNTIME"; printf '%s' "$?")"
assert_eq "sourcing has no output or caller-shell side effects" "0" "$source_probe"

# T2 tracer: replay and show are deterministic event-derived views. Even the
# smallest run is reconstructed from its validated run.started record.
t2_seed="$TEST_STATE_ROOT/t2-seed.jsonl"
printf '%s\n' "$fresh_fixture" >"$t2_seed"
t2_replay="$(bash "$RUNTIME" replay --event-file "$t2_seed")"
t2_replay_rc=$?
assert_eq "replay accepts a valid authoritative log" "0" "$t2_replay_rc"
assert_eq "replay emits the projection schema" "kc-pr-flow.review-projection/v1" "$(jq -r '.schema' <<<"$t2_replay")"
assert_eq "replay retains exact-head run identity" "$HEAD_SHA" "$(jq -r '.run.head_sha' <<<"$t2_replay")"
assert_eq "empty replay starts with no provider lanes" "0" "$(jq -r '.lanes | length' <<<"$t2_replay")"
t2_show="$(bash "$RUNTIME" show --event-file "$t2_seed")"
t2_show_rc=$?
assert_eq "show accepts the same authoritative log" "0" "$t2_show_rc"
assert_eq "show emits only a safe summary schema" "kc-pr-flow.review-summary/v1" "$(jq -r '.schema' <<<"$t2_show")"
assert_eq "show summarizes zero candidates" "0" "$(jq -r '.counts.candidates' <<<"$t2_show")"

# Replay must validate and project one immutable input snapshot. The override
# swaps the caller path immediately after authoritative validation returns.
t2_swap_source="$TEST_STATE_ROOT/t2-swap-source.jsonl"
t2_swap_replacement="$TEST_STATE_ROOT/t2-swap-replacement.jsonl"
printf '%s\n' "$fresh_fixture" >"$t2_swap_source"
sed -n '2p' "$FIXTURE" >"$t2_swap_replacement"
t2_swap_projection="$(
  export T2_SWAP_SOURCE="$t2_swap_source" T2_SWAP_REPLACEMENT="$t2_swap_replacement"
  eval "$(declare -f review_runtime_validate_authoritative_log | sed '1s/review_runtime_validate_authoritative_log/review_runtime_validate_authoritative_log_original/')"
  review_runtime_validate_authoritative_log() {
    local rc
    review_runtime_validate_authoritative_log_original "$@"
    rc=$?
    [ "$rc" -ne 0 ] || cp "$T2_SWAP_REPLACEMENT" "$T2_SWAP_SOURCE"
    return "$rc"
  }
  review_runtime_replay "$T2_SWAP_SOURCE"
)"
t2_swap_rc=$?
assert_eq "replay survives atomic source replacement after validation" "0" "$t2_swap_rc"
assert_eq "replay projects the same snapshot it validated" "run-fixture-fresh" "$(jq -r '.run.run_id' <<<"$t2_swap_projection")"

# T2 typed lane, candidate, finding, evidence, and usage envelopes form one
# complete event-derived receipt without granting any behavioral authority.
t2_repo="$TEST_STATE_ROOT/t2-repo"
mkdir "$t2_repo"
git -C "$t2_repo" init -q
printf 'line one\nline two\n' >"$t2_repo/evidence.txt"
mkdir "$t2_repo/dir"
printf 'nested evidence\n' >"$t2_repo/dir/nested.txt"
git -C "$t2_repo" add evidence.txt dir/nested.txt
git -C "$t2_repo" -c user.name='Review Runtime Test' -c user.email='runtime@example.invalid' commit -qm seed
git -C "$t2_repo" remote add origin 'https://github.com/acme/widgets.git'
t2_object_sha="$(git -C "$t2_repo" rev-parse HEAD)"
t2_evidence_hash="$(review_runtime_sha256 <"$t2_repo/evidence.txt")"
t2_anchor_one="$(sha256_text 'evidence.txt|RIGHT|2')"
t2_anchor_two="$(sha256_text 'evidence.txt|RIGHT|1')"
t2_candidate_one_id="$(sha256_text "run-fixture-fresh|security-1|1|$t2_evidence_hash")"
t2_candidate_two_id="$(sha256_text "run-fixture-fresh|security-1|2|$t2_evidence_hash")"
t2_merge_key="evidence.txt|RIGHT|$t2_anchor_one|security|unchecked-boundary"
t2_finding_id="$(sha256_text "$EXPECTED_REVIEW_KEY|$t2_merge_key")"
t2_pointer="$(jq -S -c -n \
  --arg repository "$REPOSITORY" --arg object_sha "$t2_object_sha" \
  --arg content_sha256 "$t2_evidence_hash" \
  '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",repository:$repository,object_sha:$object_sha,path:"evidence.txt",side:"RIGHT",line:2,locator:"review-anchor",content_sha256:$content_sha256}')"
t2_candidate_one="$(jq -S -c -n \
  --arg candidate_id "$t2_candidate_one_id" --arg review_key "$EXPECTED_REVIEW_KEY" \
  --arg anchor_sha256 "$t2_anchor_one" --argjson evidence "$t2_pointer" \
  '{schema:"kc-pr-flow.review-candidate/v1",candidate_id:$candidate_id,run_id:"run-fixture-fresh",review_key:$review_key,lane_id:"security-1",ordinal:1,path:"evidence.txt",side:"RIGHT",anchor_sha256:$anchor_sha256,category:"security",claim_key:"unchecked-boundary",evidence:$evidence}')"
t2_candidate_two="$(jq -S -c -n \
  --arg candidate_id "$t2_candidate_two_id" --arg review_key "$EXPECTED_REVIEW_KEY" \
  --arg anchor_sha256 "$t2_anchor_two" --argjson evidence "$t2_pointer" \
  '{schema:"kc-pr-flow.review-candidate/v1",candidate_id:$candidate_id,run_id:"run-fixture-fresh",review_key:$review_key,lane_id:"security-1",ordinal:2,path:"evidence.txt",side:"RIGHT",anchor_sha256:$anchor_sha256,category:"security",claim_key:"uncertain-ownership",evidence:$evidence}')"
t2_review_task="$(jq -S -c -n \
  --arg review_key "$EXPECTED_REVIEW_KEY" --arg repository "$REPOSITORY" \
  --arg base_sha "$BASE_SHA" --arg head_sha "$HEAD_SHA" --arg config_hash "$CONFIG_HASH" \
  '{schema:"kc-pr-flow.review-task/v1",run_id:"run-fixture-fresh",review_key:$review_key,lane_id:"security-1",capability:"security",repository:$repository,pr_number:42,base_sha:$base_sha,head_sha:$head_sha,config_hash:$config_hash,provider_hint:"claude"}')"
t2_usage="$(jq -S -c -n '{provenance:"reported",scope:"lane",provider_family:"claude",input_tokens:100,output_tokens:25,total_tokens:125}')"
t2_lane_result="$(jq -S -c -n \
  --arg review_key "$EXPECTED_REVIEW_KEY" --arg one "$t2_candidate_one_id" --arg two "$t2_candidate_two_id" \
  --argjson usage "$t2_usage" \
  '{schema:"kc-pr-flow.lane-result/v1",run_id:"run-fixture-fresh",review_key:$review_key,lane_id:"security-1",capability:"security",terminal_status:"succeeded",candidates:[$one,$two],usage:$usage,provider_family:"claude"}')"
t2_finding="$(jq -S -c -n \
  --arg finding_id "$t2_finding_id" --arg review_key "$EXPECTED_REVIEW_KEY" \
  --arg merge_key "$t2_merge_key" --arg anchor_sha256 "$t2_anchor_one" \
  --arg candidate_id "$t2_candidate_one_id" --argjson evidence "$t2_pointer" \
  '{schema:"kc-pr-flow.review-finding/v1",finding_id:$finding_id,review_key:$review_key,merge_key:$merge_key,path:"evidence.txt",side:"RIGHT",anchor_sha256:$anchor_sha256,category:"security",claim_key:"unchecked-boundary",candidate_ids:[$candidate_id],evidence:$evidence}')"
t2_lane_started="$(rehash_event "$(jq -c --argjson task "$t2_review_task" '.sequence=2 | .event_type="lane.started" | .payload={review_task:$task}' <<<"$fresh_fixture")")"
t2_observed_one="$(rehash_event "$(jq -c --argjson candidate "$t2_candidate_one" '.sequence=3 | .event_type="finding.observed" | .payload={candidate:$candidate}' <<<"$fresh_fixture")")"
t2_observed_two="$(rehash_event "$(jq -c --argjson candidate "$t2_candidate_two" '.sequence=4 | .event_type="finding.observed" | .payload={candidate:$candidate}' <<<"$fresh_fixture")")"
t2_lane_finished="$(rehash_event "$(jq -c --argjson result "$t2_lane_result" '.sequence=5 | .event_type="lane.finished" | .payload={lane_result:$result}' <<<"$fresh_fixture")")"
t2_synthesized="$(rehash_event "$(jq -c --argjson finding "$t2_finding" --arg uncertain "$t2_candidate_two_id" '.sequence=6 | .event_type="synthesis.finished" | .payload={findings:[$finding],uncertain_candidate_ids:[$uncertain]}' <<<"$fresh_fixture")")"
t2_log="$TEST_STATE_ROOT/t2-complete.jsonl"
printf '%s\n%s\n%s\n%s\n%s\n%s\n' "$fresh_fixture" "$t2_lane_started" "$t2_observed_one" "$t2_observed_two" "$t2_lane_finished" "$t2_synthesized" >"$t2_log"

t2_validate="$(bash "$RUNTIME" validate --event-file "$t2_log" 2>"$TEST_STATE_ROOT/t2-validate.stderr")"
t2_validate_rc=$?
assert_eq "complete T2 typed log validates" "0" "$t2_validate_rc"
assert_eq "complete T2 validation accepts every event" "6" "$(jq -r '.valid' <<<"$t2_validate")"
t2_projection="$(bash "$RUNTIME" replay --event-file "$t2_log")"
t2_projection_rc=$?
assert_eq "complete T2 log replays" "0" "$t2_projection_rc"
assert_eq "replay reconstructs lane task and result" "succeeded" "$(jq -r '.lanes[0].result.terminal_status' <<<"$t2_projection")"
assert_eq "replay preserves every candidate" "2" "$(jq -r '.candidates | length' <<<"$t2_projection")"
assert_eq "replay derives stable merged finding identity" "$t2_finding_id" "$(jq -r '.findings[0].finding_id' <<<"$t2_projection")"
assert_eq "replay retains explicit disagreement separately" "$t2_candidate_two_id" "$(jq -r '.uncertain_candidate_ids[0]' <<<"$t2_projection")"
assert_eq "synthesis exactly partitions every observed candidate" "2" "$(jq -r '([.findings[].candidate_ids[],.uncertain_candidate_ids[]] | unique | length)' <<<"$t2_projection")"
assert_eq "replay retains typed usage provenance" "reported" "$(jq -r '.usage_observations[0].provenance' <<<"$t2_projection")"
assert_eq "replay is deterministic canonical JSON" "$t2_projection" "$(bash "$RUNTIME" replay --event-file "$t2_log")"
t2_complete_show="$(bash "$RUNTIME" show --event-file "$t2_log")"
assert_eq "show summarizes findings without evidence content" "1" "$(jq -r '.counts.findings' <<<"$t2_complete_show")"
if printf '%s\n%s\n' "$t2_projection" "$t2_complete_show" | grep -E 'line one|line two|prompt|raw_(diff|output)|source_excerpt' >/dev/null 2>&1; then
  fail "projection or show leaks forbidden content"
else
  pass
fi
t2_shadow_state="$TEST_STATE_ROOT/t2-shadow-state"
mkdir "$t2_shadow_state"
t2_shadow_append="$(KC_PR_FLOW_STATE_DIR="$t2_shadow_state" bash "$RUNTIME" append --event-file "$t2_log")"
t2_shadow_append_rc=$?
assert_eq "complete T2 shadow receipt appends" "0" "$t2_shadow_append_rc"
assert_eq "complete T2 shadow receipt appends every event" "6" "$(jq -r '.appended' <<<"$t2_shadow_append")"
if grep -R -E 'line one|line two|prompt|raw_(diff|output)|source_excerpt|model_output' "$t2_shadow_state" >/dev/null 2>&1; then
  fail "durable T2 shadow state contains forbidden content"
else
  pass
fi

# Cross-event replay rejects provider results that drift from their task and
# merged findings whose candidate observations have a different merge key.
t2_wrong_capability="$(rehash_event "$(jq -c '.payload.lane_result.capability="types"' <<<"$t2_lane_finished")")"
printf '%s\n%s\n%s\n%s\n%s\n%s\n' "$fresh_fixture" "$t2_lane_started" "$t2_observed_one" "$t2_observed_two" "$t2_wrong_capability" "$t2_synthesized" >"$TEST_STATE_ROOT/t2-wrong-capability.jsonl"
bash "$RUNTIME" replay --event-file "$TEST_STATE_ROOT/t2-wrong-capability.jsonl" >/dev/null 2>&1
t2_wrong_capability_rc=$?
assert_eq "replay rejects lane capability drift" "74" "$t2_wrong_capability_rc"
t2_wrong_merge="$(rehash_event "$(jq -c --arg merged "$t2_candidate_two_id" --arg uncertain "$t2_candidate_one_id" '.payload.findings[0].candidate_ids=[$merged] | .payload.uncertain_candidate_ids=[$uncertain]' <<<"$t2_synthesized")")"
printf '%s\n%s\n%s\n%s\n%s\n%s\n' "$fresh_fixture" "$t2_lane_started" "$t2_observed_one" "$t2_observed_two" "$t2_lane_finished" "$t2_wrong_merge" >"$TEST_STATE_ROOT/t2-wrong-merge.jsonl"
bash "$RUNTIME" replay --event-file "$TEST_STATE_ROOT/t2-wrong-merge.jsonl" >/dev/null 2>&1
t2_wrong_merge_rc=$?
assert_eq "replay rejects a finding merged from a different candidate key" "74" "$t2_wrong_merge_rc"

t2_empty_synthesis="$(rehash_event "$(jq -c '.payload={findings:[],uncertain_candidate_ids:[]}' <<<"$t2_synthesized")")"
printf '%s\n%s\n%s\n%s\n%s\n%s\n' "$fresh_fixture" "$t2_lane_started" "$t2_observed_one" "$t2_observed_two" "$t2_lane_finished" "$t2_empty_synthesis" >"$TEST_STATE_ROOT/t2-empty-synthesis.jsonl"
bash "$RUNTIME" replay --event-file "$TEST_STATE_ROOT/t2-empty-synthesis.jsonl" >/dev/null 2>&1
t2_empty_synthesis_rc=$?
assert_eq "replay rejects synthesis that omits observed candidates" "74" "$t2_empty_synthesis_rc"

t2_duplicate_finding="$(rehash_event "$(jq -c --argjson finding "$t2_finding" --arg uncertain "$t2_candidate_two_id" '.payload={findings:[$finding,$finding],uncertain_candidate_ids:[$uncertain]}' <<<"$t2_synthesized")")"
printf '%s\n%s\n%s\n%s\n%s\n%s\n' "$fresh_fixture" "$t2_lane_started" "$t2_observed_one" "$t2_observed_two" "$t2_lane_finished" "$t2_duplicate_finding" >"$TEST_STATE_ROOT/t2-duplicate-finding.jsonl"
bash "$RUNTIME" replay --event-file "$TEST_STATE_ROOT/t2-duplicate-finding.jsonl" >/dev/null 2>&1
t2_duplicate_finding_rc=$?
assert_eq "replay rejects assigning one candidate to two findings" "74" "$t2_duplicate_finding_rc"
assert_eq "replay rejects duplicate finding identity and merge key" "74" "$t2_duplicate_finding_rc"

# A finished lane owns the exact set of candidates observed for that lane.
t2_unknown_candidate_id='eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
t2_unknown_result="$(jq -c --arg id "$t2_unknown_candidate_id" '.candidates=[$id]' <<<"$t2_lane_result")"
t2_unknown_finished="$(rehash_event "$(jq -c --argjson result "$t2_unknown_result" '.sequence=4 | .event_type="lane.finished" | .payload={lane_result:$result}' <<<"$fresh_fixture")")"
printf '%s\n%s\n%s\n%s\n' "$fresh_fixture" "$t2_lane_started" "$t2_observed_one" "$t2_unknown_finished" >"$TEST_STATE_ROOT/t2-unknown-result-candidate.jsonl"
bash "$RUNTIME" replay --event-file "$TEST_STATE_ROOT/t2-unknown-result-candidate.jsonl" >/dev/null 2>&1
t2_unknown_result_rc=$?
assert_eq "replay rejects an unknown lane-result candidate" "74" "$t2_unknown_result_rc"

t2_omitted_result="$(jq -c --arg id "$t2_candidate_one_id" '.candidates=[$id]' <<<"$t2_lane_result")"
t2_omitted_finished="$(rehash_event "$(jq -c --argjson result "$t2_omitted_result" '.sequence=5 | .event_type="lane.finished" | .payload={lane_result:$result}' <<<"$fresh_fixture")")"
printf '%s\n%s\n%s\n%s\n%s\n' "$fresh_fixture" "$t2_lane_started" "$t2_observed_one" "$t2_observed_two" "$t2_omitted_finished" >"$TEST_STATE_ROOT/t2-omitted-result-candidate.jsonl"
bash "$RUNTIME" replay --event-file "$TEST_STATE_ROOT/t2-omitted-result-candidate.jsonl" >/dev/null 2>&1
t2_omitted_result_rc=$?
assert_eq "replay rejects a lane result that omits an observed candidate" "74" "$t2_omitted_result_rc"

t2_types_candidate_id="$(sha256_text "run-fixture-fresh|types-1|1|$t2_evidence_hash")"
t2_types_task="$(jq -c '.lane_id="types-1" | .capability="types"' <<<"$t2_review_task")"
t2_types_started="$(rehash_event "$(jq -c --argjson task "$t2_types_task" '.sequence=3 | .event_type="lane.started" | .payload={review_task:$task}' <<<"$fresh_fixture")")"
t2_types_candidate="$(jq -c --arg id "$t2_types_candidate_id" '.candidate_id=$id | .lane_id="types-1"' <<<"$t2_candidate_one")"
t2_types_observed="$(rehash_event "$(jq -c --argjson candidate "$t2_types_candidate" '.sequence=4 | .event_type="finding.observed" | .payload={candidate:$candidate}' <<<"$fresh_fixture")")"
t2_cross_lane_result="$(jq -c --arg id "$t2_types_candidate_id" '.candidates=[$id]' <<<"$t2_lane_result")"
t2_cross_lane_finished="$(rehash_event "$(jq -c --argjson result "$t2_cross_lane_result" '.sequence=5 | .event_type="lane.finished" | .payload={lane_result:$result}' <<<"$fresh_fixture")")"
printf '%s\n%s\n%s\n%s\n%s\n' "$fresh_fixture" "$t2_lane_started" "$t2_types_started" "$t2_types_observed" "$t2_cross_lane_finished" >"$TEST_STATE_ROOT/t2-cross-lane-candidate.jsonl"
bash "$RUNTIME" replay --event-file "$TEST_STATE_ROOT/t2-cross-lane-candidate.jsonl" >/dev/null 2>&1
t2_cross_lane_rc=$?
assert_eq "replay rejects a cross-lane result candidate" "74" "$t2_cross_lane_rc"

# Replay validates lifecycle chronology before reducing events to a projection.
t2_empty_result="$(jq -c '.candidates=[]' <<<"$t2_lane_result")"
t2_finish_at_two="$(rehash_event "$(jq -c --argjson result "$t2_empty_result" '.sequence=2 | .event_type="lane.finished" | .payload={lane_result:$result}' <<<"$fresh_fixture")")"
t2_start_at_three="$(rehash_event "$(jq -c --argjson task "$t2_review_task" '.sequence=3 | .event_type="lane.started" | .payload={review_task:$task}' <<<"$fresh_fixture")")"
printf '%s\n%s\n%s\n' "$fresh_fixture" "$t2_finish_at_two" "$t2_start_at_three" >"$TEST_STATE_ROOT/t2-finish-before-start.jsonl"
bash "$RUNTIME" replay --event-file "$TEST_STATE_ROOT/t2-finish-before-start.jsonl" >/dev/null 2>&1
t2_finish_before_start_rc=$?
assert_eq "replay rejects lane finish before start" "74" "$t2_finish_before_start_rc"

t2_finish_at_three="$(rehash_event "$(jq -c --argjson result "$t2_empty_result" '.sequence=3 | .event_type="lane.finished" | .payload={lane_result:$result}' <<<"$fresh_fixture")")"
t2_observed_at_four="$(rehash_event "$(jq -c --argjson candidate "$t2_candidate_one" '.sequence=4 | .event_type="finding.observed" | .payload={candidate:$candidate}' <<<"$fresh_fixture")")"
printf '%s\n%s\n%s\n%s\n' "$fresh_fixture" "$t2_lane_started" "$t2_finish_at_three" "$t2_observed_at_four" >"$TEST_STATE_ROOT/t2-candidate-after-finish.jsonl"
bash "$RUNTIME" replay --event-file "$TEST_STATE_ROOT/t2-candidate-after-finish.jsonl" >/dev/null 2>&1
t2_candidate_after_finish_rc=$?
assert_eq "replay rejects a candidate observed after lane finish" "74" "$t2_candidate_after_finish_rc"

t2_early_synthesis="$(rehash_event "$(jq -c --argjson finding "$t2_finding" '.sequence=3 | .event_type="synthesis.finished" | .payload={findings:[$finding],uncertain_candidate_ids:[]}' <<<"$fresh_fixture")")"
printf '%s\n%s\n%s\n%s\n' "$fresh_fixture" "$t2_lane_started" "$t2_early_synthesis" "$t2_observed_at_four" >"$TEST_STATE_ROOT/t2-synthesis-before-observation.jsonl"
bash "$RUNTIME" replay --event-file "$TEST_STATE_ROOT/t2-synthesis-before-observation.jsonl" >/dev/null 2>&1
t2_early_synthesis_rc=$?
assert_eq "replay rejects synthesis before its candidate observation" "74" "$t2_early_synthesis_rc"

t2_partial_log="$TEST_STATE_ROOT/t2-valid-partial-lane.jsonl"
printf '%s\n%s\n%s\n' "$fresh_fixture" "$t2_lane_started" "$t2_observed_one" >"$t2_partial_log"
t2_partial_projection="$(bash "$RUNTIME" replay --event-file "$t2_partial_log")"
t2_partial_rc=$?
assert_eq "replay preserves a valid unfinished lane" "0" "$t2_partial_rc"
assert_eq "partial lane retains its candidate" "1" "$(jq -r '.candidates | length' <<<"$t2_partial_projection")"
assert_eq "partial lane retains a null result" "null" "$(jq -r '.lanes[0].result' <<<"$t2_partial_projection")"
assert_eq "partial lane has no synthetic usage" "0" "$(jq -r '.usage_observations | length' <<<"$t2_partial_projection")"

# Repo-relative paths are normalized at the payload boundary; empty segments
# cannot create ambiguous source identities.
t2_ambiguous_path_candidate="$(jq -c '.path="src//unsafe.sh" | .evidence.path="src//unsafe.sh"' <<<"$t2_candidate_one")"
t2_ambiguous_path_event="$(rehash_event "$(jq -c --argjson candidate "$t2_ambiguous_path_candidate" '.sequence=4 | .event_type="finding.observed" | .payload={candidate:$candidate}' <<<"$fresh_fixture")")"
printf '%s\n' "$t2_ambiguous_path_event" >"$TEST_STATE_ROOT/t2-ambiguous-path.jsonl"
t2_ambiguous_path_validate="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/t2-ambiguous-path.jsonl" 2>"$TEST_STATE_ROOT/t2-ambiguous-path.stderr")"
t2_ambiguous_path_rc=$?
assert_eq "ambiguous repo-relative path is rejected" "1" "$t2_ambiguous_path_rc"
assert_eq "ambiguous path is a typed invalid payload" "1" "$(jq -r '.invalid' <<<"$t2_ambiguous_path_validate")"

# Closed payloads reject adapter-owned authority even when all hashes are valid.
t2_authority_task="$(jq -c '. + {verdict:"APPROVE"}' <<<"$t2_review_task")"
t2_authority_event="$(rehash_event "$(jq -c --argjson task "$t2_authority_task" '.sequence=2 | .event_type="lane.started" | .payload={review_task:$task}' <<<"$fresh_fixture")")"
printf '%s\n' "$t2_authority_event" >"$TEST_STATE_ROOT/t2-authority.jsonl"
t2_authority_validation="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/t2-authority.jsonl" 2>"$TEST_STATE_ROOT/t2-authority.stderr")"
t2_authority_rc=$?
assert_eq "provider envelope cannot own verdict authority" "1" "$t2_authority_rc"
assert_eq "authority smuggling is a typed invalid payload" "1" "$(jq -r '.invalid' <<<"$t2_authority_validation")"
assert_match "authority smuggling names closed schema" 'unsupported_payload_schema' "$(cat "$TEST_STATE_ROOT/t2-authority.stderr")"

# Evidence verification hashes exact git object bytes and never emits content.
printf '%s\n' "$t2_pointer" >"$TEST_STATE_ROOT/t2-pointer.json"
t2_verified="$(bash "$RUNTIME" verify-evidence --pointer-json "$TEST_STATE_ROOT/t2-pointer.json" --repo "$t2_repo")"
t2_verified_rc=$?
assert_eq "git_blob evidence verifies exact bytes" "0" "$t2_verified_rc"
assert_eq "verified evidence returns typed status" "verified" "$(jq -r '.status' <<<"$t2_verified")"
if printf '%s' "$t2_verified" | grep -F 'line one' >/dev/null 2>&1; then fail "evidence verification emits source content"; else pass; fi

t2_pointer_swap_source="$TEST_STATE_ROOT/t2-pointer-swap.json"
t2_pointer_swap_replacement="$TEST_STATE_ROOT/t2-pointer-swap-replacement.json"
printf '%s\n' "$t2_pointer" >"$t2_pointer_swap_source"
jq -c '.content_sha256="dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"' <<<"$t2_pointer" >"$t2_pointer_swap_replacement"
t2_pointer_swap_output="$(
  export T2_POINTER_SWAP_SOURCE="$t2_pointer_swap_source" T2_POINTER_SWAP_REPLACEMENT="$t2_pointer_swap_replacement"
  eval "$(declare -f review_runtime_evidence_pointer_valid | sed '1s/review_runtime_evidence_pointer_valid/review_runtime_evidence_pointer_valid_original/')"
  review_runtime_evidence_pointer_valid() {
    local rc
    review_runtime_evidence_pointer_valid_original "$@"
    rc=$?
    [ "$rc" -ne 0 ] || cp "$T2_POINTER_SWAP_REPLACEMENT" "$T2_POINTER_SWAP_SOURCE"
    return "$rc"
  }
  review_runtime_verify_evidence "$T2_POINTER_SWAP_SOURCE" "$t2_repo"
)"
t2_pointer_swap_rc=$?
assert_eq "evidence verification survives pointer replacement after validation" "0" "$t2_pointer_swap_rc"
assert_eq "evidence verification reads the validated pointer snapshot" "verified" "$(jq -r '.status' <<<"$t2_pointer_swap_output")"

git -C "$t2_repo" remote set-url origin 'https://github.com/other/widgets.git'
t2_repo_mismatch="$(bash "$RUNTIME" verify-evidence --pointer-json "$TEST_STATE_ROOT/t2-pointer.json" --repo "$t2_repo")"
t2_repo_mismatch_rc=$?
assert_eq "git_blob evidence rejects mismatched repository identity" "1" "$t2_repo_mismatch_rc"
assert_eq "repository mismatch returns typed status" "repository_mismatch" "$(jq -r '.status' <<<"$t2_repo_mismatch")"
git -C "$t2_repo" remote set-url origin 'https://github.com/acme/widgets.git'

git -C "$t2_repo" remote remove origin
t2_repo_absent="$(bash "$RUNTIME" verify-evidence --pointer-json "$TEST_STATE_ROOT/t2-pointer.json" --repo "$t2_repo")"
t2_repo_absent_rc=$?
assert_eq "git_blob evidence rejects absent origin identity" "3" "$t2_repo_absent_rc"
assert_eq "absent origin returns typed status" "repository_unavailable" "$(jq -r '.status' <<<"$t2_repo_absent")"
git -C "$t2_repo" remote add origin 'git@github.com:acme/widgets.git'

for t2_origin_url in 'https://github.com/acme/widgets.git' 'ssh://git@github.com/acme/widgets.git' 'git@github.com:acme/widgets.git'; do
  git -C "$t2_repo" remote set-url origin "$t2_origin_url"
  t2_origin_output="$(bash "$RUNTIME" verify-evidence --pointer-json "$TEST_STATE_ROOT/t2-pointer.json" --repo "$t2_repo")"
  t2_origin_rc=$?
  assert_eq "normalized GitHub origin verifies: $t2_origin_url" "0" "$t2_origin_rc"
  assert_eq "normalized GitHub origin returns verified: $t2_origin_url" "verified" "$(jq -r '.status' <<<"$t2_origin_output")"
done

t2_tree_pointer="$(jq -c '.path="dir" | .line=null | .locator="tree-probe"' <<<"$t2_pointer")"
printf '%s\n' "$t2_tree_pointer" >"$TEST_STATE_ROOT/t2-tree-pointer.json"
t2_tree_output="$(bash "$RUNTIME" verify-evidence --pointer-json "$TEST_STATE_ROOT/t2-tree-pointer.json" --repo "$t2_repo")"
t2_tree_rc=$?
assert_eq "tree evidence is not accepted as a blob" "3" "$t2_tree_rc"
assert_eq "tree evidence returns typed not-blob status" "not_blob" "$(jq -r '.status' <<<"$t2_tree_output")"

t2_drift_pointer="$(jq -c '.content_sha256="dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"' <<<"$t2_pointer")"
printf '%s\n' "$t2_drift_pointer" >"$TEST_STATE_ROOT/t2-drift-pointer.json"
t2_drift="$(bash "$RUNTIME" verify-evidence --pointer-json "$TEST_STATE_ROOT/t2-drift-pointer.json" --repo "$t2_repo")"
t2_drift_rc=$?
assert_eq "evidence hash drift is nonzero" "1" "$t2_drift_rc"
assert_eq "evidence hash drift is typed" "hash_mismatch" "$(jq -r '.status' <<<"$t2_drift")"
t2_nonlocal="$(jq -S -c -n --arg repository "$REPOSITORY" --arg object_sha "$HEAD_SHA" --arg hash "$t2_evidence_hash" '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"pr_body",repository:$repository,object_sha:$object_sha,pr_number:42,locator:"body",content_sha256:$hash}')"
printf '%s\n' "$t2_nonlocal" >"$TEST_STATE_ROOT/t2-nonlocal-pointer.json"
t2_unavailable="$(bash "$RUNTIME" verify-evidence --pointer-json "$TEST_STATE_ROOT/t2-nonlocal-pointer.json" --repo "$t2_repo")"
t2_unavailable_rc=$?
assert_eq "non-local evidence reports unavailable without network" "3" "$t2_unavailable_rc"
assert_eq "non-local evidence status is typed" "unavailable" "$(jq -r '.status' <<<"$t2_unavailable")"

# Missing usage remains null and only comparable reported observations may be
# used for efficiency analysis.
t2_unavailable_usage='{"provenance":"unavailable","scope":"lane","provider_family":null,"input_tokens":null,"output_tokens":null,"total_tokens":null}'
printf '%s\n' "$t2_usage" >"$TEST_STATE_ROOT/t2-usage-left.json"
printf '%s\n' "$t2_usage" >"$TEST_STATE_ROOT/t2-usage-right.json"
t2_comparable="$(bash "$RUNTIME" compare-usage --left-json "$TEST_STATE_ROOT/t2-usage-left.json" --right-json "$TEST_STATE_ROOT/t2-usage-right.json")"
assert_eq "same-provider reported usage is comparable" "true" "$(jq -r '.comparable' <<<"$t2_comparable")"
t2_usage_swap_replacement="$TEST_STATE_ROOT/t2-usage-swap-replacement.json"
printf '%s\n' "$t2_unavailable_usage" >"$t2_usage_swap_replacement"
t2_usage_swap_output="$(
  export T2_USAGE_LEFT="$TEST_STATE_ROOT/t2-usage-left.json" T2_USAGE_RIGHT="$TEST_STATE_ROOT/t2-usage-right.json" T2_USAGE_REPLACEMENT="$t2_usage_swap_replacement"
  eval "$(declare -f review_runtime_usage_valid | sed '1s/review_runtime_usage_valid/review_runtime_usage_valid_original/')"
  review_runtime_usage_valid() {
    local rc
    review_runtime_usage_valid_original "$@"
    rc=$?
    if [ "$rc" -eq 0 ]; then
      cp "$T2_USAGE_REPLACEMENT" "$T2_USAGE_LEFT"
      cp "$T2_USAGE_REPLACEMENT" "$T2_USAGE_RIGHT"
    fi
    return "$rc"
  }
  review_runtime_compare_usage "$T2_USAGE_LEFT" "$T2_USAGE_RIGHT"
)"
t2_usage_swap_rc=$?
assert_eq "usage comparison survives source replacement after validation" "0" "$t2_usage_swap_rc"
assert_eq "usage comparison reads the validated snapshots" "true" "$(jq -r '.comparable' <<<"$t2_usage_swap_output")"
printf '%s\n' "$t2_usage" >"$TEST_STATE_ROOT/t2-usage-left.json"
printf '%s\n' "$t2_usage" >"$TEST_STATE_ROOT/t2-usage-right.json"
usage_file='sentinel'
review_runtime_compare_usage "$TEST_STATE_ROOT/t2-usage-left.json" "$TEST_STATE_ROOT/t2-usage-right.json" >/dev/null
direct_comparable_usage_rc=$?
assert_eq "direct comparable usage succeeds for local-scope probe" "0" "$direct_comparable_usage_rc"
assert_eq "comparable usage preserves caller loop variable" "sentinel" "$usage_file"
printf '%s\n' "$t2_unavailable_usage" >"$TEST_STATE_ROOT/t2-usage-right.json"
t2_incomparable="$(bash "$RUNTIME" compare-usage --left-json "$TEST_STATE_ROOT/t2-usage-left.json" --right-json "$TEST_STATE_ROOT/t2-usage-right.json")"
assert_eq "unavailable usage is never comparable" "false" "$(jq -r '.comparable' <<<"$t2_incomparable")"
assert_eq "unavailable efficiency remains null" "null" "$(jq -r '.efficiency' <<<"$t2_incomparable")"
usage_file='sentinel'
review_runtime_compare_usage "$TEST_STATE_ROOT/t2-usage-left.json" "$TEST_STATE_ROOT/t2-usage-right.json" >/dev/null
direct_incomparable_usage_rc=$?
assert_eq "direct incomparable usage succeeds for local-scope probe" "0" "$direct_incomparable_usage_rc"
assert_eq "incomparable usage preserves caller loop variable" "sentinel" "$usage_file"

for forbidden_command in resume gc authorize post; do
  bash "$RUNTIME" "$forbidden_command" >/dev/null 2>&1
  forbidden_rc=$?
  assert_eq "$forbidden_command command is out of scope" "2" "$forbidden_rc"
done

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
