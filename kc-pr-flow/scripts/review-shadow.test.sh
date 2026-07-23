#!/usr/bin/env bash
# Contract tests for the closed kc-pr-review production shadow collector.
# shellcheck disable=SC2016 # Assertions intentionally match literal skill/runtime text.
# shellcheck disable=SC2317 # The dependency probe invokes this dynamic command override indirectly.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
RUNTIME="$HERE/review-runtime.sh"
SKILL="$HERE/../skills/kc-pr-review/SKILL.md"
TEST_ROOT="$(mktemp -d)"
trap 'chmod -R u+rwX "$TEST_ROOT" 2>/dev/null || true; rm -rf "$TEST_ROOT"' EXIT

CASE_FILTER='all'
if [ "$#" -gt 0 ]; then
  if [ "$#" -ne 2 ] || [ "$1" != '--case' ]; then
    printf 'usage: %s [--case production-collector|typed-interactive-seam]\n' "$0" >&2
    exit 2
  fi
  CASE_FILTER="$2"
fi
if [ "$CASE_FILTER" != 'all' ] && [ "$CASE_FILTER" != 'production-collector' ] &&
  [ "$CASE_FILTER" != 'typed-interactive-seam' ]; then
  printf 'unknown test case: %s\n' "$CASE_FILTER" >&2
  exit 2
fi

PASS=0
FAIL=0
pass() { PASS=$((PASS + 1)); }
fail() { FAIL=$((FAIL + 1)); printf 'FAIL: %s\n' "$1"; }
assert_eq() {
  if [ "$2" = "$3" ]; then pass; else fail "$1 (expected [$2], got [$3])"; fi
}
assert_match() {
  if [[ "$3" =~ $2 ]]; then pass; else fail "$1 ([$3] does not match [$2])"; fi
}

run_typed_interactive_seam_tests() {
  local recipe="$TEST_ROOT/typed-interactive-recipe.sh"
  local mock_runtime="$TEST_ROOT/mock-typed-runtime.sh"
  local typed_log="$TEST_ROOT/typed.log"
  local mutation_log="$TEST_ROOT/typed-mutation.log"
  local sampled result

  sed -n '/^# typed-interactive-recipe:start$/,/^# typed-interactive-recipe:end$/p' "$SKILL" |
    sed '1d;$d' >"$recipe"
  # shellcheck source=/dev/null
  . "$recipe"
  if ! declare -F review_interactive_sample_mode >/dev/null ||
    ! declare -F review_interactive_prepare_confirmation >/dev/null; then
    fail 'typed interactive recipe exposes executable mode and confirmation functions'
    printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
    return 1
  fi
  pass

  cat >"$mock_runtime" <<'MOCK'
#!/usr/bin/env bash
printf 'typed\n' >>"$MOCK_TYPED_LOG"
if [ "${MOCK_TYPED_RESULT:-valid}" = invalid ]; then
  printf '%s\n' '{"reason":"invalid_receipt","schema":"kc-pr-flow.interactive-collation-status/v1","status":"invalid"}'
  exit 3
fi
if [ "${MOCK_TYPED_RESULT:-valid}" = malformed ]; then
  printf '%s\n' '{"schema":"kc-pr-flow.interactive-collation-decision/v1"}'
  exit 0
fi
printf '%s\n' '{"approve_eligible":false,"capabilities":[],"capability_gap_refs":[],"confirmation_input":{"blocker_refs":["blocker-1"],"coverage_summary":"typed-derived","gap_refs":[],"identity_summary":"typed-derived","verdict_summary":"typed-derived"},"confirmed_blocker_refs":["blocker-1"],"coverage":"complete","effective_event":"REQUEST_CHANGES","mode":"typed","review_identity":{"base_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","config_hash":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","head_sha":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","pr_number":42,"repository":"acme/widgets","review_key":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","run_id":"run-typed"},"schema":"kc-pr-flow.interactive-collation-decision/v1"}'
MOCK
  chmod 0700 "$mock_runtime"
  : >"$typed_log"
  : >"$mutation_log"
  export MOCK_TYPED_LOG="$typed_log"

  for mode in unset off unknown; do
    case "$mode" in
      unset) unset KC_PR_FLOW_REVIEW_TYPED ;;
      *) KC_PR_FLOW_REVIEW_TYPED="$mode"; export KC_PR_FLOW_REVIEW_TYPED ;;
    esac
    sampled="$(review_interactive_sample_mode)"
    assert_eq "$mode samples legacy before dispatch" legacy "$sampled"
    result="$(review_interactive_prepare_confirmation "$sampled" COMMENT "$mock_runtime")"
    assert_eq "$mode preserves legacy confirmation source" legacy "$(jq -r '.source' <<<"$result")"
    assert_eq "$mode keeps confirmation mandatory" true "$(jq -r '.confirmation_required' <<<"$result")"
  done
  assert_eq 'legacy modes never invoke typed runtime' 0 "$(wc -l <"$typed_log" | tr -d ' ')"

  KC_PR_FLOW_REVIEW_TYPED=on
  export KC_PR_FLOW_REVIEW_TYPED
  sampled="$(review_interactive_sample_mode)"
  KC_PR_FLOW_REVIEW_TYPED=off
  export KC_PR_FLOW_REVIEW_TYPED
  result="$(MOCK_TYPED_RESULT=valid review_interactive_prepare_confirmation "$sampled" COMMENT "$mock_runtime")"
  assert_eq 'enabled mode consumes typed authority' typed "$(jq -r '.source' <<<"$result")"
  assert_eq 'mid-run switch cannot change sampled typed mode' REQUEST_CHANGES "$(jq -r '.effective_event' <<<"$result")"
  assert_eq 'typed valid path keeps confirmation mandatory' true "$(jq -r '.confirmation_required' <<<"$result")"
  assert_eq 'typed valid path invokes runtime exactly once' 1 "$(wc -l <"$typed_log" | tr -d ' ')"

  result="$(MOCK_TYPED_RESULT=invalid review_interactive_prepare_confirmation "$sampled" APPROVE "$mock_runtime")"
  assert_eq 'typed invalid state stays typed instead of legacy fallback' typed "$(jq -r '.source' <<<"$result")"
  assert_eq 'typed invalid state fails closed to COMMENT' COMMENT "$(jq -r '.effective_event' <<<"$result")"
  assert_eq 'typed invalid state exposes an explicit coverage gap' typed-runtime-invalid \
    "$(jq -r '.capability_gap_refs[0]' <<<"$result")"
  assert_eq 'typed invalid path keeps confirmation mandatory' true "$(jq -r '.confirmation_required' <<<"$result")"
  result="$(MOCK_TYPED_RESULT=malformed review_interactive_prepare_confirmation "$sampled" APPROVE "$mock_runtime")"
  assert_eq 'malformed typed decision also fails closed' COMMENT "$(jq -r '.effective_event' <<<"$result")"
  assert_eq 'no posting mutation occurs before confirmation' 0 "$(wc -c <"$mutation_log" | tr -d ' ')"
}

if [ "$CASE_FILTER" = 'typed-interactive-seam' ]; then
  run_typed_interactive_seam_tests
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit
fi

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
tree_receipt() {
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
OCCURRED_AT='2026-07-22T00:00:00Z'
EVIDENCE_HASH='eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
UNCERTAIN_HASH='ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'

# Fixed compatibility vectors and invalid-input guards remain part of the
# shadow contract because the skill uses both executable hash authorities.
EXPECTED_CONFIG_JSON='{"capabilities":["code_correctness","security","test_coverage"],"modes":{"agent_tier":"standard","cross_model":true,"full_pass":true,"noise_filter":false,"pr_archetype":"bugfix","probe_required":true},"schema":"kc-pr-flow.review-config/v1"}'
EXPECTED_CONFIG_HASH='770f5d63259827eed61b039ca571cdfea628183c71598399b225caed2f909592'
config_json="$(bash "$RUNTIME" config-hash --agent-tier standard --pr-archetype bugfix \
  --full-pass true --probe-required true --cross-model true --noise-filter false \
  --capabilities 'security,code_correctness,test_coverage,security' 2>/dev/null)"
assert_eq 'config-hash retains the fixed canonical vector' "$EXPECTED_CONFIG_HASH" "$config_json"
# shellcheck source=/dev/null
. "$RUNTIME"
canonical_config="$(review_runtime_config_canonical standard bugfix true true true false \
  'security,code_correctness,test_coverage,security' 2>/dev/null)"
assert_eq 'config canonical JSON remains sorted and deduplicated' "$EXPECTED_CONFIG_JSON" "$canonical_config"
for invalid_config_args in \
  '--agent-tier invalid' \
  '--pr-archetype invalid' \
  '--full-pass yes' \
  '--probe-required yes' \
  '--cross-model yes' \
  '--noise-filter yes'; do
  # Word splitting is intentional: each fixture is one option/value pair.
  # shellcheck disable=SC2086
  bash "$RUNTIME" config-hash $invalid_config_args >/dev/null 2>&1
  assert_eq "config-hash rejects $invalid_config_args" '2' "$?"
done
for empty_config_option in --agent-tier --pr-archetype --full-pass --probe-required --cross-model --noise-filter; do
  bash "$RUNTIME" config-hash "$empty_config_option" '' >/dev/null 2>&1
  assert_eq "config-hash rejects empty $empty_config_option" '2' "$?"
done

runtime_review_key="$(bash "$RUNTIME" review-key --repo "$REPOSITORY" --pr "$PR_NUMBER" \
  --base "$BASE_SHA" --head "$HEAD_SHA" --config-hash "$CONFIG_HASH" 2>/dev/null)"
assert_eq 'runtime is the executable review-key authority' "$REVIEW_KEY" "$runtime_review_key"
invalid_review_key_output="$(bash "$RUNTIME" review-key --repo $'acme/widgets\tbad' --pr "$PR_NUMBER" \
  --base "$BASE_SHA" --head "$HEAD_SHA" --config-hash "$CONFIG_HASH" 2>&1)"
invalid_review_key_rc=$?
assert_eq 'review-key rejects invalid identity' '2' "$invalid_review_key_rc"
assert_match 'review-key reports invalid repository identity' 'invalid repository identity' "$invalid_review_key_output"

# Six legacy artifacts are frozen separately. They model the actual values the
# existing prose flow has already produced before the one production seam.
BODY="$TEST_ROOT/body.bin"
INLINE_COMMENTS="$TEST_ROOT/inline-comments.bin"
EVENT="$TEST_ROOT/event.bin"
OPTIONS="$TEST_ROOT/options.bin"
CONFIRMATION_INPUT="$TEST_ROOT/confirmation-input.bin"
GITHUB_CALL_LOG="$TEST_ROOT/github-call-log.bin"
MUTATION_LOG="$TEST_ROOT/mutation.log"
printf '%s\n' '## Review' 'SENTINEL raw body that must never enter receipt state' >"$BODY"
printf '%s\000' '[{"path":"src/app.sh","body":"SENTINEL raw comment"}]' >"$INLINE_COMMENTS"
printf '%s' 'COMMENT' >"$EVENT"
printf '%s\n' '1' '2' '3' '4' 'D' >"$OPTIONS"
printf '%s\r\n' 'option=2' >"$CONFIRMATION_INPUT"
printf '%s\r\n' 'GET /repos/acme/widgets/pulls/42 -> exact head' >"$GITHUB_CALL_LOG"
: >"$MUTATION_LOG"

artifact_files=("$BODY" "$INLINE_COMMENTS" "$EVENT" "$OPTIONS" "$CONFIRMATION_INPUT" "$GITHUB_CALL_LOG")
artifact_names=('body' 'inline comments' 'event' 'options' 'confirmation input' 'GitHub call log')
artifact_hashes=()
for artifact in "${artifact_files[@]}"; do artifact_hashes+=("$(file_sha256 "$artifact")"); done

assert_legacy_unchanged() {
  local label="$1" index=0
  while [ "$index" -lt "${#artifact_files[@]}" ]; do
    assert_eq "$label preserves ${artifact_names[$index]} byte-for-byte" \
      "${artifact_hashes[$index]}" "$(file_sha256 "${artifact_files[$index]}")"
    index=$((index + 1))
  done
  assert_eq "$label performs no mocked GitHub mutation" '0' "$(wc -c <"$MUTATION_LOG" | tr -d ' ')"
}

POINTER="$(jq -S -c -n \
  --arg repository "$REPOSITORY" --arg review_key "$REVIEW_KEY" \
  --arg base_sha "$BASE_SHA" --arg head_sha "$HEAD_SHA" --arg content_sha256 "$EVIDENCE_HASH" '
  {schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",repository:$repository,
   review_key:$review_key,base_sha:$base_sha,head_sha:$head_sha,object_sha:$head_sha,
   content_sha256:$content_sha256,path:"src/app.sh",side:"RIGHT",line:7,locator:null}')"
UNCERTAIN_POINTER="$(jq -S -c -n \
  --arg repository "$REPOSITORY" --arg review_key "$REVIEW_KEY" \
  --arg base_sha "$BASE_SHA" --arg head_sha "$HEAD_SHA" --arg content_sha256 "$UNCERTAIN_HASH" '
  {schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",repository:$repository,
   review_key:$review_key,base_sha:$base_sha,head_sha:$head_sha,object_sha:$head_sha,
   content_sha256:$content_sha256,path:"src/uncertain.sh",side:"FILE",line:null,locator:null}')"

OBSERVATION="$TEST_ROOT/observation.json"
jq -S -c -n \
  --arg repository "$REPOSITORY" --argjson pr_number "$PR_NUMBER" \
  --arg base_sha "$BASE_SHA" --arg head_sha "$HEAD_SHA" \
  --arg config_hash "$CONFIG_HASH" --arg occurred_at "$OCCURRED_AT" \
  --arg body_sha256 "$(file_sha256 "$BODY")" \
  --arg inline_comments_sha256 "$(file_sha256 "$INLINE_COMMENTS")" \
  --arg event_sha256 "$(file_sha256 "$EVENT")" \
  --arg options_sha256 "$(file_sha256 "$OPTIONS")" \
  --arg confirmation_input_sha256 "$(file_sha256 "$CONFIRMATION_INPUT")" \
  --arg github_call_log_sha256 "$(file_sha256 "$GITHUB_CALL_LOG")" \
  --argjson evidence "$POINTER" --argjson uncertain_evidence "$UNCERTAIN_POINTER" '
  {
    schema:"kc-pr-flow.shadow-observation/v1",
    identity:{repository:$repository,pr_number:$pr_number,base_sha:$base_sha,head_sha:$head_sha,config_hash:$config_hash,occurred_at:$occurred_at},
    behavior_hashes:{body_sha256:$body_sha256,inline_comments_sha256:$inline_comments_sha256,event_sha256:$event_sha256,options_sha256:$options_sha256,confirmation_input_sha256:$confirmation_input_sha256,github_call_log_sha256:$github_call_log_sha256},
    lanes:[
      {lane_id:"correctness",capability:"code_correctness",provider_family:"claude",terminal_status:"succeeded",
       usage:{input_tokens:100,output_tokens:20,total_tokens:120,provenance:"reported",provider_family:"claude",scope:"lane"},
       candidates:[{ordinal:1,path:"src/app.sh",side:"RIGHT",anchor_sha256:$evidence.content_sha256,category:"correctness",claim_key:"missing_guard",evidence:$evidence}]},
      {lane_id:"security",capability:"security",terminal_status:"unavailable",
       usage:{input_tokens:null,output_tokens:null,total_tokens:null,provenance:"unavailable",provider_family:null,scope:"lane"},
       candidates:[{ordinal:1,path:"src/uncertain.sh",side:"FILE",anchor_sha256:$uncertain_evidence.content_sha256,category:"security",claim_key:"uncertain_boundary",evidence:$uncertain_evidence}]}
    ],
    synthesis:{
      findings:[{path:"src/app.sh",side:"RIGHT",anchor_sha256:$evidence.content_sha256,category:"correctness",claim_key:"missing_guard",evidence:$evidence,candidate_refs:[{lane_id:"correctness",ordinal:1}]}],
      uncertain_candidate_refs:[{lane_id:"security",ordinal:1}]
    }
  }' >"$OBSERVATION"

run_shadow_executable() { # gate, head-status, live-head, observation, state-root
  KC_PR_FLOW_STATE_DIR="$5" bash "$RUNTIME" shadow \
    --enabled "$1" --head-check-status "$2" --live-head "$3" --observation-file "$4"
}

# Identity-only state is never a successful observation.
IDENTITY_ROOT="$TEST_ROOT/identity-state"
identity_start="$(KC_PR_FLOW_STATE_DIR="$IDENTITY_ROOT" bash "$RUNTIME" start \
  --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$BASE_SHA" --head "$HEAD_SHA" \
  --config-hash "$CONFIG_HASH" --occurred-at "$OCCURRED_AT")"
identity_run_id="$(jq -r '.run_id' <<<"$identity_start")"
identity_event_file="$(find "$IDENTITY_ROOT" -path "*/$identity_run_id/events.jsonl" -type f)"
identity_status="$(bash "$RUNTIME" observe --event-file "$identity_event_file" \
  --expected-head "$HEAD_SHA" --expected-review-key "$REVIEW_KEY" 2>/dev/null)"
assert_eq 'identity-only receipt is not observed' 'not_observed' "$(jq -r '.status' <<<"$identity_status")"
assert_eq 'identity-only receipt has a typed incomplete reason' 'incomplete_receipt' "$(jq -r '.reason' <<<"$identity_status")"

# Off, on, and collector failure all enter the same executable shadow seam and
# prove parity against six separately frozen artifacts.
OFF_ROOT="$TEST_ROOT/off-state"
off_output="$(run_shadow_executable '' ok "$HEAD_SHA" "$OBSERVATION" "$OFF_ROOT")"
assert_eq 'unset gate is typed disabled' 'disabled' "$(jq -r '.status' <<<"$off_output")"
assert_eq 'off gate creates no receipt' '0' "$(find "$OFF_ROOT" -name events.jsonl -type f 2>/dev/null | wc -l | tr -d ' ')"
assert_legacy_unchanged 'unset gate'
UNKNOWN_ROOT="$TEST_ROOT/unknown-state"
unknown_output="$(run_shadow_executable banana ok "$HEAD_SHA" "$OBSERVATION" "$UNKNOWN_ROOT")"
assert_eq 'unknown gate is typed disabled' 'disabled' "$(jq -r '.status' <<<"$unknown_output")"
assert_eq 'unknown gate creates no receipt' '0' "$(find "$UNKNOWN_ROOT" -name events.jsonl -type f 2>/dev/null | wc -l | tr -d ' ')"
assert_legacy_unchanged 'unknown gate'

ON_ROOT="$TEST_ROOT/on-state"
on_output="$(run_shadow_executable on ok "$HEAD_SHA" "$OBSERVATION" "$ON_ROOT")"
assert_eq 'closed observation is accepted only after complete replay' 'observed' "$(jq -r '.status' <<<"$on_output")"
assert_eq 'observed result reports two declared lanes' '2' "$(jq -r '.counts.lanes' <<<"$on_output")"
assert_eq 'observed result preserves the uncertain candidate' '1' "$(jq -r '.counts.uncertain_candidates' <<<"$on_output")"
on_event_file="$(find "$ON_ROOT" -name events.jsonl -type f)"
assert_eq 'collector publishes exactly one authoritative event log' '1' "$(find "$ON_ROOT" -name events.jsonl -type f | wc -l | tr -d ' ')"
actual_lifecycle="$(jq -r '.event_type' "$on_event_file" | paste -sd, -)"
assert_eq 'collector emits the deterministic complete lifecycle' \
  'run.started,lane.started,finding.observed,lane.finished,lane.started,finding.observed,lane.finished,synthesis.finished,run.finished' \
  "$actual_lifecycle"
assert_eq 'run.finished durably binds all six behavior hashes' \
  "$(jq -S -c '.behavior_hashes' "$OBSERVATION")" \
  "$(jq -S -c 'select(.event_type == "run.finished") | .payload.behavior_hashes' "$on_event_file")"
replayed_on="$(bash "$RUNTIME" replay --event-file "$on_event_file")"
assert_eq 'replay exposes the exact frozen body hash' "$(file_sha256 "$BODY")" \
  "$(jq -r '.behavior_hashes.body_sha256' <<<"$replayed_on")"
assert_eq 'observer exposes the exact frozen body hash' "$(file_sha256 "$BODY")" \
  "$(jq -r '.behavior_hashes.body_sha256' <<<"$on_output")"
assert_legacy_unchanged 'enabled collector'

# Provider identity and usage provenance are compatible without inventing
# unavailable usage ownership. Known and unknown providers may both be
# unavailable with null usage family; reported/estimated mismatches are closed.
UNKNOWN_UNAVAILABLE="$TEST_ROOT/unknown-unavailable.json"
cp "$OBSERVATION" "$UNKNOWN_UNAVAILABLE"
review_runtime_shadow_observation_valid "$UNKNOWN_UNAVAILABLE"
assert_eq 'unknown-provider unavailable observation validates' '0' "$?"
KNOWN_UNAVAILABLE="$TEST_ROOT/known-unavailable.json"
jq -c '.lanes[1].provider_family="gemini"' "$OBSERVATION" >"$KNOWN_UNAVAILABLE"
review_runtime_shadow_observation_valid "$KNOWN_UNAVAILABLE"
assert_eq 'known-provider unavailable observation validates with null usage family' '0' "$?"
KNOWN_UNAVAILABLE_ROOT="$TEST_ROOT/known-unavailable-state"
known_unavailable_output="$(run_shadow_executable on ok "$HEAD_SHA" "$KNOWN_UNAVAILABLE" "$KNOWN_UNAVAILABLE_ROOT")"
assert_eq 'known-provider unavailable observation completes collection' 'observed' "$(jq -r '.status' <<<"$known_unavailable_output")"
known_unavailable_events="$(find "$KNOWN_UNAVAILABLE_ROOT" -name events.jsonl -type f)"
assert_eq 'known provider remains on unavailable lane result' 'gemini' \
  "$(jq -r 'select(.event_type == "lane.finished" and .payload.lane_result.lane_id == "security") | .payload.lane_result.provider_family' "$known_unavailable_events")"
assert_eq 'unavailable usage provider remains null' 'null' \
  "$(jq -r 'select(.event_type == "lane.finished" and .payload.lane_result.lane_id == "security") | .payload.lane_result.usage.provider_family' "$known_unavailable_events")"
for mismatch_provenance in reported estimated; do
  MISMATCH_OBSERVATION="$TEST_ROOT/$mismatch_provenance-provider-mismatch.json"
  jq -c --arg provenance "$mismatch_provenance" \
    '.lanes[0].usage.provenance=$provenance | .lanes[0].usage.provider_family="gemini"' \
    "$OBSERVATION" >"$MISMATCH_OBSERVATION"
  review_runtime_shadow_observation_valid "$MISMATCH_OBSERVATION" >/dev/null 2>&1
  assert_eq "$mismatch_provenance provider-family mismatch is rejected" '1' "$?"
done

# Changing only one frozen behavior hash changes the authoritative terminal
# event while preserving all legacy bytes and typed review state.
CHANGED_OBSERVATION="$TEST_ROOT/changed-observation.json"
CHANGED_BODY_HASH='9999999999999999999999999999999999999999999999999999999999999999'
jq -c --arg hash "$CHANGED_BODY_HASH" '.behavior_hashes.body_sha256=$hash' \
  "$OBSERVATION" >"$CHANGED_OBSERVATION"
CHANGED_ROOT="$TEST_ROOT/changed-state"
changed_output="$(run_shadow_executable on ok "$HEAD_SHA" "$CHANGED_OBSERVATION" "$CHANGED_ROOT")"
changed_event_file="$(find "$CHANGED_ROOT" -name events.jsonl -type f)"
assert_eq 'single behavior-hash change remains a complete observation' 'observed' "$(jq -r '.status' <<<"$changed_output")"
assert_eq 'changed body hash is replayed exactly' "$CHANGED_BODY_HASH" \
  "$(bash "$RUNTIME" replay --event-file "$changed_event_file" | jq -r '.behavior_hashes.body_sha256')"
assert_match 'body-hash change changes the authoritative run.finished payload hash' '^false$' \
  "$(jq -n --arg left "$(jq -r 'select(.event_type == "run.finished") | .payload_sha256' "$on_event_file")" \
    --arg right "$(jq -r 'select(.event_type == "run.finished") | .payload_sha256' "$changed_event_file")" '$left == $right')"
assert_legacy_unchanged 'changed behavior hash'

# A complete observer is read-only and exact-head bound.
before_direct_observe="$(tree_receipt "$ON_ROOT")"
direct_observe="$(review_runtime_observe "$on_event_file" "$HEAD_SHA" "$REVIEW_KEY")"
direct_observe_rc=$?
after_direct_observe="$(tree_receipt "$ON_ROOT")"
assert_eq 'direct observer accepts the complete exact-head log' '0' "$direct_observe_rc"
assert_eq 'direct observer returns observed for complete state' 'observed' "$(jq -r '.status' <<<"$direct_observe")"
assert_eq 'direct observer leaves the receipt tree byte-identical' "$before_direct_observe" "$after_direct_observe"
direct_mismatch="$(review_runtime_observe "$on_event_file" "$MOVED_HEAD" "$REVIEW_KEY" 2>/dev/null)"
direct_mismatch_rc=$?
assert_eq 'direct observer exact-head mismatch is typed' '3' "$direct_mismatch_rc"
assert_eq 'direct observer reports exact-head mismatch' 'exact_head_mismatch' "$(jq -r '.reason' <<<"$direct_mismatch")"

INVALID_OBSERVATION="$TEST_ROOT/invalid-observation.json"
jq -c '.raw_provider_output="SENTINEL raw provider output"' "$OBSERVATION" >"$INVALID_OBSERVATION"
FAIL_ROOT="$TEST_ROOT/failure-state"
failure_output="$(run_shadow_executable on ok "$HEAD_SHA" "$INVALID_OBSERVATION" "$FAIL_ROOT" 2>/dev/null)"
assert_eq 'collector failure is typed not_observed' 'not_observed' "$(jq -r '.status' <<<"$failure_output")"
assert_eq 'invalid closed input is rejected before receipt publication' '0' "$(find "$FAIL_ROOT" -name events.jsonl -type f 2>/dev/null | wc -l | tr -d ' ')"
assert_legacy_unchanged 'collector failure'

# Closed schema and reference integrity reject every authority-smuggling shape
# before state publication.
assert_invalid_observation() { # label, jq mutation
  local label="$1" mutation="$2" file root output
  file="$TEST_ROOT/invalid-$FAIL.json"
  root="$TEST_ROOT/invalid-$FAIL-state"
  jq -c "$mutation" "$OBSERVATION" >"$file"
  output="$(run_shadow_executable on ok "$HEAD_SHA" "$file" "$root" 2>/dev/null)"
  assert_eq "$label is typed not_observed" 'not_observed' "$(jq -r '.status' <<<"$output")"
  assert_eq "$label publishes no accepted receipt" '0' "$(find "$root" -name events.jsonl -type f 2>/dev/null | wc -l | tr -d ' ')"
}
assert_invalid_observation 'candidate runtime ID' '.lanes[0].candidates[0].candidate_id="forbidden"'
assert_invalid_observation 'raw provider value' '.lanes[0].provider_payload={raw:"provider text"}'
assert_invalid_observation 'unresolved candidate reference' '.synthesis.findings[0].candidate_refs[0].ordinal=99'
assert_invalid_observation 'uncertain and finding overlap' '.synthesis.uncertain_candidate_refs=[{lane_id:"correctness",ordinal:1}]'
assert_invalid_observation 'inconsistent finding evidence' '.synthesis.findings[0].evidence.content_sha256="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"'

# Exact-head failures do not collect and cannot mutate the legacy artifacts.
HEAD_ROOT="$TEST_ROOT/head-state"
head_output="$(run_shadow_executable on ok "$MOVED_HEAD" "$OBSERVATION" "$HEAD_ROOT")"
assert_eq 'moved head is typed not_observed' 'exact_head_mismatch' "$(jq -r '.reason' <<<"$head_output")"
assert_eq 'moved head creates no receipt' '0' "$(find "$HEAD_ROOT" -name events.jsonl -type f 2>/dev/null | wc -l | tr -d ' ')"
assert_legacy_unchanged 'moved head'
FAILED_HEAD_ROOT="$TEST_ROOT/failed-head-state"
failed_head_output="$(run_shadow_executable on failed '' "$OBSERVATION" "$FAILED_HEAD_ROOT")"
assert_eq 'failed head check has a distinct typed reason' 'head_check_failed' "$(jq -r '.reason' <<<"$failed_head_output")"
assert_eq 'failed head check creates no receipt' '0' "$(find "$FAILED_HEAD_ROOT" -name events.jsonl -type f 2>/dev/null | wc -l | tr -d ' ')"
assert_legacy_unchanged 'failed head check'

# The production seam invokes the observer exactly once dynamically.
original_observe_definition="$(declare -f review_runtime_observe | sed '1s/review_runtime_observe/review_runtime_observe_actual/')"
eval "$original_observe_definition"
OBSERVER_CALL_LOG="$TEST_ROOT/observer-calls.log"
: >"$OBSERVER_CALL_LOG"
review_runtime_observe() {
  printf 'observe\n' >>"$OBSERVER_CALL_LOG"
  review_runtime_observe_actual "$@"
}
DYNAMIC_ROOT="$TEST_ROOT/dynamic-state"
dynamic_output="$(KC_PR_FLOW_STATE_DIR="$DYNAMIC_ROOT" review_runtime_shadow on ok "$HEAD_SHA" "$OBSERVATION")"
assert_eq 'dynamic production seam completes' 'observed' "$(jq -r '.status' <<<"$dynamic_output")"
assert_eq 'dynamic production seam invokes observer exactly once' '1' "$(wc -l <"$OBSERVER_CALL_LOG" | tr -d ' ')"
eval "$(declare -f review_runtime_observe_actual | sed '1s/review_runtime_observe_actual/review_runtime_observe/')"

# Missing jq is fail-open and the status encoder has a dependency-free JSON
# fallback. A deterministic post-start build failure is typed and never observed.
original_require_jq_definition="$(declare -f review_runtime_require_jq | sed '1s/review_runtime_require_jq/review_runtime_require_jq_actual/')"
eval "$original_require_jq_definition"
review_runtime_require_jq() { return 69; }
MISSING_JQ_ROOT="$TEST_ROOT/missing-jq-state"
missing_jq_output="$(KC_PR_FLOW_STATE_DIR="$MISSING_JQ_ROOT" review_runtime_shadow on ok "$HEAD_SHA" "$OBSERVATION" 2>/dev/null)"
assert_eq 'missing jq is typed not_observed' 'not_observed' "$(jq -r '.status' <<<"$missing_jq_output")"
assert_eq 'missing jq creates no receipt' '0' "$(find "$MISSING_JQ_ROOT" -name events.jsonl -type f 2>/dev/null | wc -l | tr -d ' ')"
eval "$(declare -f review_runtime_require_jq_actual | sed '1s/review_runtime_require_jq_actual/review_runtime_require_jq/')"

# shellcheck disable=SC2329 # Indirectly invoked by review_runtime_shadow_status.
command() {
  if [ "${1:-}" = '-v' ] && [ "${2:-}" = 'jq' ]; then return 1; fi
  builtin command "$@"
}
fallback_status="$(review_runtime_shadow_status not_observed collector_error)"
unset -f command
assert_match 'status fallback is valid typed JSON without jq' '"status":"not_observed"' "$fallback_status"

original_build_event_definition="$(declare -f review_runtime_build_event | sed '1s/review_runtime_build_event/review_runtime_build_event_actual/')"
eval "$original_build_event_definition"
review_runtime_build_event() {
  if [ "${10:-}" != 'run.started' ]; then return 71; fi
  review_runtime_build_event_actual "$@"
}
POST_START_ROOT="$TEST_ROOT/post-start-state"
post_start_output="$(KC_PR_FLOW_STATE_DIR="$POST_START_ROOT" review_runtime_shadow on ok "$HEAD_SHA" "$OBSERVATION" 2>/dev/null)"
post_start_rc=$?
assert_eq 'post-start failure remains fail-open' '0' "$post_start_rc"
assert_eq 'post-start failure emits typed not_observed' 'not_observed' "$(jq -r '.status' <<<"$post_start_output")"
assert_eq 'post-start failure never reports observed' 'false' "$(jq -r '.status == "observed"' <<<"$post_start_output")"
assert_eq 'post-start failure leaves one defined incomplete log' '1' "$(find "$POST_START_ROOT" -name events.jsonl -type f | wc -l | tr -d ' ')"
assert_eq 'post-start partial log contains only run.started' 'run.started' \
  "$(jq -r '.event_type' "$(find "$POST_START_ROOT" -name events.jsonl -type f)")"
eval "$(declare -f review_runtime_build_event_actual | sed '1s/review_runtime_build_event_actual/review_runtime_build_event/')"

# Skill and runtime use the same sole executable collector seam after collation.
shadow_heading_count="$(grep -c '^### 6b-shadow\. Best-effort Shadow Receipt Collector$' "$SKILL" || true)"
shadow_call_count="$(grep -cF '"$CLAUDE_PLUGIN_ROOT/scripts/review-runtime.sh" shadow' "$SKILL" || true)"
shadow_line="$(grep -n '^### 6b-shadow\. Best-effort Shadow Receipt Collector$' "$SKILL" | cut -d: -f1)"
arch_line="$(grep -n '^### 6b-arch\. Optional Architecture Explanation$' "$SKILL" | cut -d: -f1)"
confirm_line="$(grep -n '^### 6c\. User confirmation gate$' "$SKILL" | cut -d: -f1)"
assert_eq 'skill defines exactly one collector section' '1' "$shadow_heading_count"
assert_eq 'skill invokes the production collector executable exactly once' '1' "$shadow_call_count"
if [ -n "$shadow_line" ] && [ -n "$arch_line" ] && [ -n "$confirm_line" ] && \
  [ "$arch_line" -lt "$shadow_line" ] && [ "$shadow_line" -lt "$confirm_line" ]; then
  pass
else
  fail '6b-shadow is the one post-collation seam immediately before 6c'
fi
assert_eq 'skill defines one closed observation file' '1' "$(grep -cF '`SHADOW_OBSERVATION_FILE` = that one file' "$SKILL" || true)"
assert_eq 'skill passes the closed observation to runtime' '1' "$(grep -cF -- '--observation-file "$SHADOW_OBSERVATION_FILE"' "$SKILL" || true)"
assert_eq 'skill invokes the executable review-key authority exactly once' '1' "$(grep -cF '"$CLAUDE_PLUGIN_ROOT/scripts/review-runtime.sh" review-key' "$SKILL" || true)"
assert_eq 'skill requires all six frozen behavior hashes' '6' "$(grep -oE '(body|inline_comments|event|options|confirmation_input|github_call_log)_sha256' "$SKILL" | sort -u | wc -l | tr -d ' ')"
assert_eq 'skill states one production call after collation' '1' "$(grep -cF 'exactly one production shadow call' "$SKILL" || true)"
assert_eq 'skill makes failure explicitly fail-open' '1' "$(grep -cF '**Fail open:**' "$SKILL" || true)"

ledger_heading_count="$(grep -c '^### 4-shadow\. Typed Shadow Ledger (when shadow is on)$' "$SKILL" || true)"
ledger_line="$(grep -n '^### 4-shadow\. Typed Shadow Ledger (when shadow is on)$' "$SKILL" | cut -d: -f1)"
step_five_line="$(grep -n '^## Step 5: Compliance Audit$' "$SKILL" | cut -d: -f1)"
ledger_block="$(sed -n '/^### 4-shadow\. Typed Shadow Ledger (when shadow is on)$/,/^## Step 5: Compliance Audit$/p' "$SKILL")"
assert_eq 'skill defines one early typed shadow ledger' '1' "$ledger_heading_count"
if [ -n "$ledger_line" ] && [ -n "$step_five_line" ] && [ "$ledger_line" -lt "$step_five_line" ]; then
  pass
else
  fail 'typed shadow ledger is established before synthesis'
fi
assert_eq 'ledger assigns stable dispatch lane IDs' '1' "$(printf '%s' "$ledger_block" | grep -cF 'Assign `lane_id` at dispatch from a stable safe source slug' || true)"
assert_eq 'ledger maps capabilities independently of provider names' '1' "$(printf '%s' "$ledger_block" | grep -cF 'Map each lane to its typed review capability, not its provider name' || true)"
assert_eq 'ledger defines terminal status rules' '1' "$(printf '%s' "$ledger_block" | grep -cF '`succeeded`, `failed`, or `unavailable`' || true)"
assert_eq 'ledger forbids partial reported usage' '1' "$(printf '%s' "$ledger_block" | grep -cF 'reported only when all provider token counts are complete' || true)"
assert_eq 'ledger preserves every provider observation' '1' "$(printf '%s' "$ledger_block" | grep -cF 'Every provider observation becomes one candidate' || true)"
assert_eq 'ledger defines deterministic candidate sorting' '1' "$(printf '%s' "$ledger_block" | grep -cF 'stable sort by `path`, `side`, `anchor_sha256`, `category`, `claim_key`, and evidence `content_sha256`' || true)"
assert_eq 'ledger partitions every candidate exactly once' '1' "$(printf '%s' "$ledger_block" | grep -cF 'partition every candidate exactly once' || true)"
assert_eq 'ledger creates a private 0700 directory' '1' "$(printf '%s' "$ledger_block" | grep -cF 'mktemp -d' || true)"
assert_eq 'ledger makes the observation file 0600' '1' "$(printf '%s' "$ledger_block" | grep -cF 'chmod 0600' || true)"
assert_eq 'ledger uses jq for closed serialization' '1' "$(printf '%s' "$ledger_block" | grep -cF 'jq -S -c -n' || true)"
assert_eq 'ledger cleans the exact file without recursive deletion' '1' "$(printf '%s' "$ledger_block" | grep -cF 'rm -f "$SHADOW_OBSERVATION_FILE"' || true)"
assert_eq 'ledger initializes a separate serialization readiness flag' '1' "$(printf '%s' "$ledger_block" | grep -cF "SHADOW_OBSERVATION_READY='false'" || true)"
assert_eq 'ledger marks readiness only after secure serialization' '1' "$(printf '%s' "$ledger_block" | grep -cF "SHADOW_OBSERVATION_READY='true'" || true)"
if printf '%s' "$ledger_block" | grep -Eq "chmod 0700 .*\|\| SHADOW_TMP_DIR=''|chmod 0600 .*\|\| SHADOW_OBSERVATION_FILE=''"; then
  fail 'serialization failure clears an exact cleanup handle'
else
  pass
fi
assert_eq 'collector call is gated by the separate readiness flag' '1' "$(grep -cF 'if [ "${SHADOW_OBSERVATION_READY:-false}" = true ]; then' "$SKILL" || true)"
if printf '%s' "$ledger_block" | grep -F 'umask 077' >/dev/null 2>&1; then
  fail 'typed shadow recipe mutates ambient umask'
else
  pass
fi
if printf '%s' "$ledger_block" | grep -F 'rm -rf' >/dev/null 2>&1; then
  fail 'typed shadow ledger uses recursive deletion'
else
  pass
fi

# Execute the documented recipe, not a test-local reconstruction. The recipe
# must initialize every JSON aggregate, deterministically finalize one lane and
# synthesis, write a validator-accepted closed observation, then clean exactly.
DOCUMENTED_RECIPE="$TEST_ROOT/documented-shadow-recipe.sh"
sed -n '/^# shadow-ledger-recipe:start$/,/^# shadow-ledger-recipe:end$/p' "$SKILL" |
  sed '1d;$d' >"$DOCUMENTED_RECIPE"
DOCUMENTED_RESULT="$TEST_ROOT/documented-result.json"
(
  # shellcheck source=/dev/null
  . "$DOCUMENTED_RECIPE"
  if ! declare -F shadow_ledger_register_lane >/dev/null ||
    ! declare -F shadow_ledger_finish_lane >/dev/null ||
    ! declare -F shadow_ledger_finalize_synthesis >/dev/null ||
    ! declare -F shadow_ledger_finalize_behavior_hashes >/dev/null ||
    ! declare -F shadow_ledger_write_observation >/dev/null ||
    ! declare -F shadow_ledger_cleanup >/dev/null; then
    jq -n '{recipe_loaded:false,valid:false,cleaned:false}' >"$DOCUMENTED_RESULT"
    exit 0
  fi
  shadow_ledger_register_lane correctness code_correctness claude
  documented_candidates="$(jq -c -n --argjson evidence "$POINTER" \
    '[{path:"src/app.sh",side:"RIGHT",anchor_sha256:$evidence.content_sha256,category:"correctness",claim_key:"missing_guard",evidence:$evidence}]')"
  documented_usage='{"input_tokens":100,"output_tokens":20,"total_tokens":120,"provenance":"reported","provider_family":"claude","scope":"lane"}'
  shadow_ledger_finish_lane correctness succeeded claude "$documented_usage" "$documented_candidates"
  documented_findings="$(jq -c -n --argjson evidence "$POINTER" \
    '[{path:"src/app.sh",side:"RIGHT",anchor_sha256:$evidence.content_sha256,category:"correctness",claim_key:"missing_guard",evidence:$evidence,candidate_refs:[{lane_id:"correctness",ordinal:1}]}]')"
  shadow_ledger_finalize_synthesis "$documented_findings" '[]'
  shadow_ledger_finalize_behavior_hashes \
    "$(file_sha256 "$BODY")" "$(file_sha256 "$INLINE_COMMENTS")" "$(file_sha256 "$EVENT")" \
    "$(file_sha256 "$OPTIONS")" "$(file_sha256 "$CONFIRMATION_INPUT")" "$(file_sha256 "$GITHUB_CALL_LOG")"
  # shellcheck disable=SC2034 # Indirectly consumed by the sourced documented recipe.
  SHADOW_REPOSITORY="$REPOSITORY" SHADOW_PR_NUMBER="$PR_NUMBER" SHADOW_BASE_SHA="$BASE_SHA" \
    REVIEWED_HEAD_SHA="$HEAD_SHA" SHADOW_CONFIG_HASH="$CONFIG_HASH" SHADOW_OCCURRED_AT="$OCCURRED_AT"
  shadow_ledger_write_observation
  documented_file="$SHADOW_OBSERVATION_FILE"
  documented_dir="$SHADOW_TMP_DIR"
  documented_valid=false
  if [ "$SHADOW_OBSERVATION_READY" = true ] && review_runtime_shadow_observation_valid "$documented_file"; then
    documented_valid=true
  fi
  documented_lane="$(jq -c '.lanes[0] | {lane_id,ordinal:(.candidates[0].ordinal)}' "$documented_file" 2>/dev/null || true)"
  shadow_ledger_cleanup
  documented_cleaned=false
  if [ ! -e "$documented_file" ] && [ ! -e "$documented_dir" ]; then documented_cleaned=true; fi
  jq -n --argjson valid "$documented_valid" --argjson cleaned "$documented_cleaned" \
    --argjson lane "${documented_lane:-null}" \
    '{recipe_loaded:true,valid:$valid,cleaned:$cleaned,lane:$lane}' >"$DOCUMENTED_RESULT"
)
assert_eq 'documented recipe loads executable ledger functions' 'true' "$(jq -r '.recipe_loaded' "$DOCUMENTED_RESULT")"
assert_eq 'documented recipe writes a valid closed observation' 'true' "$(jq -r '.valid' "$DOCUMENTED_RESULT")"
assert_eq 'documented recipe assigns deterministic first ordinal' '1' "$(jq -r '.lane.ordinal // empty' "$DOCUMENTED_RESULT")"
assert_eq 'documented recipe cleans exact file and directory' 'true' "$(jq -r '.cleaned' "$DOCUMENTED_RESULT")"

collector_block="$(sed -n '/^review_runtime_collect_shadow_observation() (/,/^)/p' "$RUNTIME")"
shadow_block="$(sed -n '/^review_runtime_shadow() (/,/^)/p' "$RUNTIME")"
if printf '%s\n%s\n' "$collector_block" "$shadow_block" | \
  grep -Eq '(^|[;&|[:space:]])(gh|curl|codex|gemini)([[:space:]]|$)'; then
  fail 'production collector invokes a network or model tool'
else
  pass
fi
if grep -R -F -e 'SENTINEL raw body' -e 'SENTINEL raw comment' -e 'SENTINEL raw provider output' \
  "$ON_ROOT" "$FAIL_ROOT" >/dev/null 2>&1; then
  fail 'shadow durable state contains raw legacy or provider content'
else
  pass
fi

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
