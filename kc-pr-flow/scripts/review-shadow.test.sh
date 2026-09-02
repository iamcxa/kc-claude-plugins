#!/usr/bin/env bash
# Contract tests for the closed kc-pr-review production shadow collector.
# shellcheck disable=SC2016 # Assertions intentionally match literal skill/runtime text.
# shellcheck disable=SC2317 # The dependency probe invokes this dynamic command override indirectly.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
RUNTIME="$HERE/review-runtime.sh"
SKILL="${KC_PR_FLOW_SHADOW_TEST_SKILL:-$HERE/../skills/kc-pr-review/SKILL.md}"
SHADOW_WORKFLOW="$HERE/../../.github/workflows/review-shadow-tests.yml"
TEST_ROOT="$(mktemp -d)"
trap 'chmod -R u+rwX "$TEST_ROOT" 2>/dev/null || true; rm -rf "$TEST_ROOT"' EXIT

CASE_FILTER='all'
if [ "$#" -gt 0 ]; then
  if [ "$#" -ne 2 ] || [ "$1" != '--case' ]; then
    printf 'usage: %s [--case production-collector|s01-skill-inertness|typed-interactive-seam|skill-slimming|skill-slimming-handoff]\n' "$0" >&2
    exit 2
  fi
  CASE_FILTER="$2"
fi
if [ "$CASE_FILTER" != 'all' ] && [ "$CASE_FILTER" != 'production-collector' ] &&
  [ "$CASE_FILTER" != 's01-skill-inertness' ] &&
  [ "$CASE_FILTER" != 'typed-interactive-seam' ] &&
  [ "$CASE_FILTER" != 'skill-slimming' ] &&
  [ "$CASE_FILTER" != 'skill-slimming-handoff' ]; then
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
finish_case() { printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"; [ "$FAIL" -eq 0 ]; exit; }

sha256_text() {
  if command -v shasum >/dev/null 2>&1; then
    printf '%s' "$1" | shasum -a 256 | awk '{print $1}'
  else
    printf '%s' "$1" | sha256sum | awk '{print $1}'
  fi
}

TEST_CONFIG_HASH=cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc TEST_OCCURRED_AT=2026-07-22T00:00:00Z
extract_shadow_skill() {
  SHADOW_TEST_CONSTRUCTOR="$TEST_ROOT/$1-constructor.sh" SHADOW_TEST_HANDOFF="$TEST_ROOT/$1-handoff.sh"
  sed -n '/^# shadow-observation-constructor:start$/,/^# shadow-observation-constructor:end$/p' "$SKILL" | sed '1d;$d' >"$SHADOW_TEST_CONSTRUCTOR"
  sed -n '/^[[:space:]]*# shadow-observation-handoff:start$/,/^[[:space:]]*# shadow-observation-handoff:end$/p' "$SKILL" | sed '1d;$d;s/^   //' >"$SHADOW_TEST_HANDOFF"
  # shellcheck source=/dev/null
  . "$SHADOW_TEST_CONSTRUCTOR"
}

run_shadow_handoff() { # repo plugin state-dir base head behavior lanes synthesis report-state
  local repo="$1" plugin="$2" state_dir="$3" base="$4" head="$5" behavior="$6" lanes="$7" synthesis="$8" report_state="$9"
  (
    cd "$repo" || exit 1
    CLAUDE_PLUGIN_ROOT="$plugin" KC_PR_FLOW_STATE_DIR="$state_dir"
    SHADOW_REPOSITORY=acme/widgets SHADOW_PR_NUMBER=42 SHADOW_BASE_SHA="$base" REVIEWED_HEAD_SHA="$head"
    SHADOW_CONFIG_HASH="$TEST_CONFIG_HASH" SHADOW_OCCURRED_AT="$TEST_OCCURRED_AT"
    SHADOW_BEHAVIOR_HASHES_JSON="$behavior" SHADOW_LANES_JSON="$lanes" SHADOW_SYNTHESIS_JSON="$synthesis"
    SHADOW_HEAD_STATUS=ok FRESH_HEAD_SHA="$head"
    export CLAUDE_PLUGIN_ROOT KC_PR_FLOW_STATE_DIR SHADOW_REPOSITORY SHADOW_PR_NUMBER SHADOW_BASE_SHA REVIEWED_HEAD_SHA SHADOW_CONFIG_HASH SHADOW_OCCURRED_AT
    export SHADOW_BEHAVIOR_HASHES_JSON SHADOW_LANES_JSON SHADOW_SYNTHESIS_JSON SHADOW_HEAD_STATUS FRESH_HEAD_SHA SHADOW_TEST_MOCK_LOG
    # shellcheck source=/dev/null
    . "$SHADOW_TEST_HANDOFF"
    if [ "$report_state" = true ]; then
      printf '%s\n%s\n%s\n%s\n%s\n%s|%s\n%s\n' "$SHADOW_TEST_PREPARED_FILE" "$SHADOW_TEST_PREPARED_DIR" "$SHADOW_TEST_PREPARED_SHA" "$([ -e "$SHADOW_TEST_PREPARED_FILE" ] && printf true || printf false)" "$([ -e "$SHADOW_TEST_PREPARED_DIR" ] && printf true || printf false)" "$SHADOW_OBSERVATION_FILE" "$SHADOW_TMP_DIR" "$SHADOW_OBSERVATION_READY"
    else
      printf '%s' "$SHADOW_STATUS"
    fi
  )
}

run_skill_slimming_integration_tests() {
  local repo head key evidence_a evidence_z pointer_a pointer_z lanes synthesis behavior constructed_a constructed_b status
  repo="$TEST_ROOT/slimming-repo"; mkdir -p "$repo/src"; git -C "$repo" init -q
  printf '%s\n' 'review evidence' >"$repo/src/app.sh"; printf '%s\n' 'second evidence' >"$repo/src/z.sh"; git -C "$repo" add src
  git -C "$repo" -c user.name='Shadow Test' -c user.email='shadow@example.invalid' commit -qm seed
  head="$(git -C "$repo" rev-parse HEAD)"
  key="$(sha256_text "acme/widgets|42|$head|$head|$TEST_CONFIG_HASH")"
  evidence_a="$(shasum -a 256 "$repo/src/app.sh" | awk '{print $1}')"; evidence_z="$(shasum -a 256 "$repo/src/z.sh" | awk '{print $1}')"
  pointer_a="$(jq -S -c -n --arg head "$head" --arg key "$key" --arg evidence "$evidence_a" '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",repository:"acme/widgets",review_key:$key,base_sha:$head,head_sha:$head,object_sha:$head,content_sha256:$evidence,path:"src/app.sh",side:"RIGHT",line:1,locator:null}')"; pointer_z="$(jq -S -c -n --arg head "$head" --arg key "$key" --arg evidence "$evidence_z" '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",repository:"acme/widgets",review_key:$key,base_sha:$head,head_sha:$head,object_sha:$head,content_sha256:$evidence,path:"src/z.sh",side:"RIGHT",line:1,locator:null}')"
  lanes="$(jq -S -c -n --argjson pointer_a "$pointer_a" --argjson pointer_z "$pointer_z" --arg evidence_a "$evidence_a" --arg evidence_z "$evidence_z" '[{lane_id:"z-lane",capability:"security",provider_family:"claude",terminal_status:"succeeded",usage:{input_tokens:1,output_tokens:1,total_tokens:2,provenance:"reported",provider_family:"claude",scope:"lane"},candidates:[{path:"src/z.sh",side:"RIGHT",anchor_sha256:$evidence_z,category:"correctness",claim_key:"z_guard",evidence:$pointer_z},{path:"src/app.sh",side:"RIGHT",anchor_sha256:$evidence_a,category:"correctness",claim_key:"a_guard",evidence:$pointer_a}]},{lane_id:"a-lane",capability:"code_correctness",provider_family:"claude",terminal_status:"succeeded",usage:{input_tokens:1,output_tokens:1,total_tokens:2,provenance:"reported",provider_family:"claude",scope:"lane"},candidates:[{path:"src/z.sh",side:"RIGHT",anchor_sha256:$evidence_z,category:"correctness",claim_key:"z_guard",evidence:$pointer_z},{path:"src/app.sh",side:"RIGHT",anchor_sha256:$evidence_a,category:"correctness",claim_key:"a_guard",evidence:$pointer_a}]}]')"
  synthesis="$(jq -S -c -n --argjson pointer_a "$pointer_a" --argjson pointer_z "$pointer_z" --arg evidence_a "$evidence_a" --arg evidence_z "$evidence_z" '{findings:[{path:"src/z.sh",side:"RIGHT",anchor_sha256:$evidence_z,category:"correctness",claim_key:"z_guard",evidence:$pointer_z,candidate_refs:[{lane_id:"z-lane",ordinal:2},{lane_id:"a-lane",ordinal:2}]},{path:"src/app.sh",side:"RIGHT",anchor_sha256:$evidence_a,category:"correctness",claim_key:"a_guard",evidence:$pointer_a,candidate_refs:[{lane_id:"z-lane",ordinal:1},{lane_id:"a-lane",ordinal:1}]}],uncertain_candidate_refs:[]}')"
  behavior="$(jq -S -c -n '{body_sha256:("a"*64),inline_comments_sha256:("b"*64),event_sha256:("c"*64),options_sha256:("d"*64),confirmation_input_sha256:("e"*64),github_call_log_sha256:("f"*64)}')"
  extract_shadow_skill integration
  if ! declare -F shadow_observation_build >/dev/null || [ ! -s "$SHADOW_TEST_HANDOFF" ]; then fail 'skill exposes the executable shadow observation constructor and handoff'; return; fi
  pass
  constructed_a="$TEST_ROOT/constructed-a.json"; constructed_b="$TEST_ROOT/constructed-b.json"
  shadow_observation_build "$constructed_a" acme/widgets 42 "$head" "$head" "$TEST_CONFIG_HASH" "$TEST_OCCURRED_AT" "$behavior" "$lanes" "$synthesis"
  shadow_observation_build "$constructed_b" acme/widgets 42 "$head" "$head" "$TEST_CONFIG_HASH" "$TEST_OCCURRED_AT" "$behavior" "$(jq -c 'reverse | map(.candidates |= reverse)' <<<"$lanes")" "$(jq -c '.findings |= reverse | .findings |= map(.candidate_refs |= reverse)' <<<"$synthesis")"
  assert_eq 'completion order yields identical closed observation bytes' "$(shasum -a 256 "$constructed_a" | awk '{print $1}')" "$(shasum -a 256 "$constructed_b" | awk '{print $1}')"
  assert_eq 'constructor canonicalizes candidate ordinals, findings, and references' '{"lanes":[{"lane_id":"a-lane","candidates":[["a_guard",1],["z_guard",2]]},{"lane_id":"z-lane","candidates":[["a_guard",1],["z_guard",2]]}],"findings":[{"claim_key":"a_guard","candidate_refs":[["a-lane",1],["z-lane",1]]},{"claim_key":"z_guard","candidate_refs":[["a-lane",2],["z-lane",2]]}]}' "$(jq -c '{lanes:[.lanes[]|{lane_id,candidates:[.candidates[]|[.claim_key,.ordinal]]}],findings:[.synthesis.findings[]|{claim_key,candidate_refs:[.candidate_refs[]|[.lane_id,.ordinal]]}]}' "$constructed_a")"
  status="$(run_shadow_handoff "$repo" "$(cd "$HERE/.." && pwd)" "$TEST_ROOT/slimming-state" "$head" "$head" "$behavior" "$(jq -c 'map(select(.lane_id=="a-lane"))' <<<"$lanes")" "$(jq -c '.findings |= map(.candidate_refs |= map(select(.lane_id=="a-lane")))' <<<"$synthesis")" false)"
  assert_eq 'enabled skill handoff reaches the runtime collector' observed "$(jq -r '.status' <<<"$status")"
  assert_eq 'skill has no duplicate executable shadow recipe' 0 "$(grep -c '^# shadow-ledger-recipe:start$' "$SKILL" || true)"
  assert_eq 'skill delegates one closed observation to the runtime owner' 1 "$(grep -cF -- '--observation-file "$SHADOW_OBSERVATION_FILE"' "$SKILL" || true)"
}

if [ "$CASE_FILTER" = 'skill-slimming' ]; then
  run_skill_slimming_integration_tests; finish_case
fi

run_skill_slimming_handoff_tests() {
  local original_prepare mock_root mock_runtime state prepared_file prepared_sha
  extract_shadow_skill fast
  if ! declare -F shadow_observation_prepare >/dev/null || [ ! -s "$SHADOW_TEST_HANDOFF" ]; then fail 'fast handoff exposes constructor and executable handoff'; return; fi
  original_prepare="$(declare -f shadow_observation_prepare | sed '1s/shadow_observation_prepare/shadow_observation_prepare_actual/')"
  eval "$original_prepare"
  shadow_observation_prepare() {
    shadow_observation_prepare_actual "$@"
    SHADOW_TEST_PREPARED_FILE="$SHADOW_OBSERVATION_FILE"
    SHADOW_TEST_PREPARED_DIR="$SHADOW_TMP_DIR"
    SHADOW_TEST_PREPARED_SHA="$(shasum -a 256 "$SHADOW_OBSERVATION_FILE" | awk '{print $1}')"
    export SHADOW_TEST_PREPARED_FILE SHADOW_TEST_PREPARED_DIR SHADOW_TEST_PREPARED_SHA
  }
  mock_root="$TEST_ROOT/fast-shadow-plugin"
  mock_runtime="$mock_root/scripts/review-runtime.sh"
  SHADOW_TEST_MOCK_LOG="$TEST_ROOT/fast-shadow-runtime.log"
  mkdir -p "$mock_root/scripts"
  cat >"$mock_runtime" <<'MOCK'
#!/usr/bin/env bash
observation_file=''
while [ "$#" -gt 0 ]; do
  if [ "$1" = --observation-file ]; then observation_file="$2"; break; fi; shift
done
exists=false; readable=false; [ ! -f "$observation_file" ] || exists=true; [ ! -r "$observation_file" ] || readable=true
input_sha="$(shasum -a 256 "$observation_file" | awk '{print $1}')"
printf 'read\t%s\t%s\t%s\t%s\t%s\t%s\n' "$exists" "$readable" "$observation_file" "$input_sha" "$(stat -f '%Lp' "$(dirname "$observation_file")" 2>/dev/null || stat -c '%a' "$(dirname "$observation_file")")" "$(stat -f '%Lp' "$observation_file" 2>/dev/null || stat -c '%a' "$observation_file")" >"$SHADOW_TEST_MOCK_LOG"
input_mutated=false; printf '\nmutation-attempt\n' >>"$observation_file" && input_mutated=true
SHADOW_OBSERVATION_FILE=/tmp/forged; SHADOW_OBSERVATION_READY=true
printf 'mutate\t%s\t%s\t%s\n' "$input_mutated" "$SHADOW_OBSERVATION_FILE" "$SHADOW_OBSERVATION_READY" >>"$SHADOW_TEST_MOCK_LOG"
printf '{"status":"mocked"}\n'
MOCK
  chmod 0700 "$mock_runtime"
  state="$(run_shadow_handoff "$TEST_ROOT" "$mock_root" "$TEST_ROOT/fast-state" aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb '{}' '[]' "$(jq -cn '{findings:[],uncertain_candidate_refs:[]}')" true)"
  prepared_file="$(sed -n '1p' <<<"$state")"; prepared_sha="$(sed -n '3p' <<<"$state")"
  assert_eq 'fast runtime reads exact 0700/0600 private input and immutable bytes' "$(printf 'read\ttrue\ttrue\t%s\t%s\t700\t600' "$prepared_file" "$prepared_sha")" "$(sed -n '1p' "$SHADOW_TEST_MOCK_LOG")"
  assert_eq 'fast runtime attempts input and caller mutation' "$(printf 'mutate\ttrue\t/tmp/forged\ttrue')" "$(sed -n '2p' "$SHADOW_TEST_MOCK_LOG")"
  assert_eq 'fast cleanup removes private observation file' false "$(sed -n '4p' <<<"$state")"
  assert_eq 'fast cleanup removes private observation directory' false "$(sed -n '5p' <<<"$state")"
  assert_eq 'fast cleanup resets private handles' '|' "$(sed -n '6p' <<<"$state")"
  assert_eq 'fast cleanup resets readiness' false "$(sed -n '7p' <<<"$state")"
  if grep -F 'rm -f "$SHADOW_OBSERVATION_FILE"' <<<"$(declare -f shadow_observation_cleanup)" >/dev/null && grep -F 'rmdir "$SHADOW_TMP_DIR"' <<<"$(declare -f shadow_observation_cleanup)" >/dev/null && ! grep -F 'rm -rf' <<<"$(declare -f shadow_observation_cleanup)" >/dev/null; then pass; else fail 'fast cleanup requires exact file unlink and empty-directory removal without recursion'; fi
}

if [ "$CASE_FILTER" = 'skill-slimming-handoff' ]; then
  run_skill_slimming_handoff_tests; finish_case
fi

run_s01_skill_inertness_tests() {
  local owner
  for owner in 'kc-pr-flow/scripts/review-shadow.test.sh' 'kc-pr-flow/skills/kc-pr-review/SKILL.md'; do
    assert_eq "shadow workflow owns $owner in pull and push" 2 \
      "$(grep -cF -- "- \"$owner\"" "$SHADOW_WORKFLOW" || true)"
  done
  assert_eq 'existing shadow job runs the shadow contract once' 1 \
    "$(grep -cF 'bash kc-pr-flow/scripts/review-shadow.test.sh' "$SHADOW_WORKFLOW" || true)"
  assert_eq 'production skill has no receipt authority call' 0 \
    "$(grep -cE 'review-runtime\.sh.*[[:space:]]receipt([[:space:]]|$)' "$SKILL" || true)"
}

run_typed_interactive_seam_tests() {
  local recipe="$TEST_ROOT/typed-interactive-recipe.sh"
  local mock_runtime="$TEST_ROOT/mock-typed-runtime.sh"
  local typed_log="$TEST_ROOT/typed.log"
  local mutation_log="$TEST_ROOT/typed-mutation.log"
  local sampled result decision forged_confirmation post_block identity
  local evidence evidence_binding bare_evidence drifted_evidence hash_drift_evidence
  local matching_evidence inconsistent_evidence post_gate

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
if [ "${MOCK_TYPED_RESULT:-valid}" = inconsistent ]; then
  printf '%s\n' '{"approve_eligible":true,"capabilities":[],"capability_gap_refs":["required-gap"],"confirmation_input":{"blocker_refs":[],"coverage_summary":"typed-derived","gap_refs":[],"identity_summary":"typed-derived","verdict_summary":"typed-derived"},"confirmed_blocker_refs":[],"coverage":"complete","effective_event":"APPROVE","mode":"typed","review_identity":{"base_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","config_hash":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","head_sha":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","pr_number":42,"repository":"acme/widgets","review_key":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","run_id":"run-typed"},"schema":"kc-pr-flow.interactive-collation-decision/v1"}'
  exit 0
fi
if [ "${MOCK_TYPED_RESULT:-valid}" = approve ]; then
  printf '%s\n' '{"approve_eligible":true,"capabilities":[],"capability_gap_refs":[],"confirmation_input":{"blocker_refs":[],"coverage_summary":"typed-derived","gap_refs":[],"identity_summary":"typed-derived","verdict_summary":"typed-derived"},"confirmed_blocker_refs":[],"coverage":"complete","effective_event":"APPROVE","mode":"typed","review_identity":{"base_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","config_hash":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","head_sha":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","pr_number":42,"repository":"acme/widgets","review_key":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","run_id":"run-typed"},"schema":"kc-pr-flow.interactive-collation-decision/v1"}'
  exit 0
fi
printf '%s\n' '{"approve_eligible":false,"capabilities":[],"capability_gap_refs":[],"confirmation_input":{"blocker_refs":["ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"],"coverage_summary":"typed-derived","gap_refs":[],"identity_summary":"typed-derived","verdict_summary":"typed-derived"},"confirmed_blocker_refs":["ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"],"coverage":"complete","effective_event":"REQUEST_CHANGES","mode":"typed","review_identity":{"base_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","config_hash":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","head_sha":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","pr_number":42,"repository":"acme/widgets","review_key":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","run_id":"run-typed"},"schema":"kc-pr-flow.interactive-collation-decision/v1"}'
MOCK
  chmod 0700 "$mock_runtime"
  : >"$typed_log"
  : >"$mutation_log"
  export MOCK_TYPED_LOG="$typed_log"
  identity='{"base_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","config_hash":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","head_sha":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","pr_number":42,"repository":"acme/widgets","review_key":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","run_id":"run-typed"}'
  evidence='{"blockers":[{"evidence_sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","finding_id":"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"}],"confirmed_at":"2026-07-23T00:00:00Z","confirmed_by":"interactive-human","review_identity":{"base_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","config_hash":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","head_sha":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","pr_number":42,"repository":"acme/widgets","review_key":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","run_id":"run-typed"},"schema":"kc-pr-flow.confirmed-blocker-evidence/v1"}'
  evidence_binding="$(sha256_text "$(jq -S -c . <<<"$evidence")")"
  evidence="$(jq -S -c --arg binding "$evidence_binding" \
    '. + {binding_sha256:$binding}' <<<"$evidence")"
  bare_evidence='["ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"]'
  drifted_evidence="$(jq -S -c \
    '.review_identity.head_sha="9999999999999999999999999999999999999999" |
     del(.binding_sha256)' <<<"$evidence")"
  evidence_binding="$(sha256_text "$drifted_evidence")"
  drifted_evidence="$(jq -S -c --arg binding "$evidence_binding" \
    '. + {binding_sha256:$binding}' <<<"$drifted_evidence")"
  hash_drift_evidence="$(jq -S -c \
    '.binding_sha256="9999999999999999999999999999999999999999999999999999999999999999"' \
    <<<"$evidence")"
  matching_evidence="$evidence"
  inconsistent_evidence="$(jq -S -c \
    '.blockers=[{"evidence_sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                 "finding_id":"9999999999999999999999999999999999999999999999999999999999999999"}] |
     del(.binding_sha256)' <<<"$evidence")"
  evidence_binding="$(sha256_text "$inconsistent_evidence")"
  inconsistent_evidence="$(jq -S -c --arg binding "$evidence_binding" \
    '. + {binding_sha256:$binding}' <<<"$inconsistent_evidence")"

  for mode in unset off unknown; do
    case "$mode" in
      unset) unset KC_PR_FLOW_REVIEW_TYPED ;;
      *) KC_PR_FLOW_REVIEW_TYPED="$mode"; export KC_PR_FLOW_REVIEW_TYPED ;;
    esac
    sampled="$(review_interactive_sample_mode)"
    assert_eq "$mode samples legacy before dispatch" legacy "$sampled"
    result="$(review_interactive_prepare_confirmation \
      "$sampled" COMMENT null null "$mock_runtime")"
    assert_eq "$mode preserves legacy confirmation source" legacy "$(jq -r '.source' <<<"$result")"
    assert_eq "$mode keeps confirmation mandatory" true "$(jq -r '.confirmation_required' <<<"$result")"
  done
  assert_eq 'legacy modes never invoke typed runtime' 0 "$(wc -l <"$typed_log" | tr -d ' ')"

  KC_PR_FLOW_REVIEW_TYPED=on
  export KC_PR_FLOW_REVIEW_TYPED
  sampled="$(review_interactive_sample_mode)"
  KC_PR_FLOW_REVIEW_TYPED=off
  export KC_PR_FLOW_REVIEW_TYPED
  result="$(MOCK_TYPED_RESULT=valid review_interactive_prepare_confirmation \
    "$sampled" COMMENT "$identity" null "$mock_runtime")"
  assert_eq 'enabled mode consumes typed authority' typed "$(jq -r '.source' <<<"$result")"
  assert_eq 'mid-run switch cannot change sampled typed mode' REQUEST_CHANGES "$(jq -r '.effective_event' <<<"$result")"
  assert_eq 'typed valid path keeps confirmation mandatory' true "$(jq -r '.confirmation_required' <<<"$result")"
  assert_eq 'typed valid path invokes runtime exactly once' 1 "$(wc -l <"$typed_log" | tr -d ' ')"

  decision="$(MOCK_TYPED_RESULT=valid "$mock_runtime")"
  review_interactive_decision_valid "$decision"
  assert_eq 'decision blocker authority does not require a duplicate expected array' 0 "$?"
  result="$(MOCK_TYPED_RESULT=valid review_interactive_prepare_confirmation \
    "$sampled" COMMENT "$identity" null "$mock_runtime")"
  assert_eq 'omitting duplicate blocker input cannot erase a valid decision blocker' REQUEST_CHANGES \
    "$(jq -r '.effective_event' <<<"$result")"
  assert_eq 'valid blocker decision remains the confirmation authority' \
    kc-pr-flow.interactive-collation-decision/v1 "$(jq -r '.decision.schema // empty' <<<"$result")"

  result="$(MOCK_TYPED_RESULT=invalid review_interactive_prepare_confirmation \
    "$sampled" APPROVE "$identity" null "$mock_runtime")"
  assert_eq 'typed invalid state stays typed instead of legacy fallback' typed "$(jq -r '.source' <<<"$result")"
  assert_eq 'typed invalid state cannot trust a bare expected-blocker array' COMMENT \
    "$(jq -r '.effective_event' <<<"$result")"
  assert_eq 'typed invalid state emits no unbound blocker references' 0 \
    "$(jq -r '.confirmed_blocker_refs | length' <<<"$result")"
  assert_eq 'typed invalid state exposes an explicit coverage gap' typed-runtime-invalid \
    "$(jq -r '.capability_gap_refs[0]' <<<"$result")"
  assert_eq 'typed invalid path keeps confirmation mandatory' true "$(jq -r '.confirmation_required' <<<"$result")"
  result="$(MOCK_TYPED_RESULT=invalid review_interactive_prepare_confirmation \
    "$sampled" APPROVE "$identity" "$evidence" "$mock_runtime")"
  assert_eq 'valid independent blocker evidence preserves REQUEST_CHANGES' REQUEST_CHANGES \
    "$(jq -r '.effective_event' <<<"$result")"
  assert_eq 'valid independent blocker evidence remains bound in confirmation' \
    kc-pr-flow.confirmed-blocker-evidence/v1 \
    "$(jq -r '.blocker_evidence.schema // empty' <<<"$result")"
  assert_eq 'valid independent blocker evidence derives blocker references' \
    ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff \
    "$(jq -r '.confirmed_blocker_refs[0]' <<<"$result")"
  post_gate="$(review_interactive_confirm_post "$result" REQUEST_CHANGES confirmed)"
  review_interactive_post_gate_valid "$post_gate"
  assert_eq 'post gate accepts decisionless REQUEST_CHANGES only with bound evidence' 0 "$?"

  # --- autonomous (daemon) posting authorization -----------------------------
  # A daemon iteration has no human at the confirmation gate. Its authorization
  # is a sibling schema, never the interactive one: human_confirmed must stay
  # unforgeable, so it is not a field an autonomous caller can set at all.
  local auto_key auto_head auto_gate
  auto_key=0000000000000000000000000000000000000000000000000000000000000001
  auto_head=1111111111111111111111111111111111111111
  auto_gate="$(review_autonomous_post_gate "$auto_key" "$auto_head" COMMENT daemon)"
  review_autonomous_post_gate_valid "$auto_gate"
  assert_eq 'autonomous gate produced for a daemon validates' 0 "$?"
  assert_eq 'autonomous gate declares its own schema' \
    kc-pr-flow.autonomous-post-gate/v1 "$(jq -r '.schema' <<<"$auto_gate")"
  assert_eq 'autonomous gate carries no human_confirmed field at all' null \
    "$(jq -r '.human_confirmed | type' <<<"$auto_gate")"
  assert_eq 'autonomous gate binds the review key it authorizes' "$auto_key" \
    "$(jq -r '.review_key' <<<"$auto_gate")"
  assert_eq 'autonomous gate binds the head it authorizes' "$auto_head" \
    "$(jq -r '.head_sha' <<<"$auto_gate")"

  review_autonomous_post_gate "$auto_key" "$auto_head" COMMENT human >/dev/null 2>&1
  assert_eq 'autonomous gate refuses an authorizer it does not know' 3 "$?"
  # A short call must refuse, not abort on an unbound variable under set -u.
  review_autonomous_post_gate "$auto_key" "$auto_head" >/dev/null 2>&1
  assert_eq 'autonomous gate refuses a short call cleanly' 3 "$?"
  review_autonomous_post_gate >/dev/null 2>&1
  assert_eq 'autonomous gate refuses an argumentless call cleanly' 3 "$?"
  review_autonomous_post_gate "$auto_key" not-a-sha COMMENT daemon >/dev/null 2>&1
  assert_eq 'autonomous gate refuses a malformed head' 3 "$?"

  review_autonomous_post_gate_valid "$(jq -c '.authorized_by = "human"' <<<"$auto_gate")" 2>/dev/null
  assert_eq 'autonomous validator refuses a forged authorizer' 3 "$?"
  review_autonomous_post_gate_valid "$(jq -c '. + {human_confirmed:true}' <<<"$auto_gate")" 2>/dev/null
  assert_eq 'autonomous validator refuses a smuggled human_confirmed field' 3 "$?"
  review_interactive_post_gate_valid "$auto_gate" 2>/dev/null
  assert_eq 'the interactive validator never accepts an autonomous gate' 3 "$?"

  result="$(MOCK_TYPED_RESULT=invalid review_interactive_prepare_confirmation \
    "$sampled" APPROVE "$identity" "$bare_evidence" "$mock_runtime")"
  assert_eq 'bare blocker array cannot preserve REQUEST_CHANGES' COMMENT \
    "$(jq -r '.effective_event' <<<"$result")"
  assert_eq 'bare blocker array is discarded rather than retained' null \
    "$(jq -r '.blocker_evidence | type' <<<"$result")"
  result="$(MOCK_TYPED_RESULT=invalid review_interactive_prepare_confirmation \
    "$sampled" APPROVE "$identity" "$drifted_evidence" "$mock_runtime")"
  assert_eq 'exact-identity drift discards independent blocker authority' COMMENT \
    "$(jq -r '.effective_event' <<<"$result")"
  result="$(MOCK_TYPED_RESULT=invalid review_interactive_prepare_confirmation \
    "$sampled" APPROVE "$identity" "$hash_drift_evidence" "$mock_runtime")"
  assert_eq 'binding hash drift discards independent blocker authority' COMMENT \
    "$(jq -r '.effective_event' <<<"$result")"

  result="$(MOCK_TYPED_RESULT=valid review_interactive_prepare_confirmation \
    "$sampled" COMMENT "$identity" "$matching_evidence" "$mock_runtime")"
  assert_eq 'consistent valid decision and evidence retain decision authority' REQUEST_CHANGES \
    "$(jq -r '.effective_event' <<<"$result")"
  result="$(MOCK_TYPED_RESULT=valid review_interactive_prepare_confirmation \
    "$sampled" COMMENT "$identity" "$inconsistent_evidence" "$mock_runtime")"
  assert_eq 'inconsistent valid decision and evidence fail closed at COMMENT' COMMENT \
    "$(jq -r '.effective_event' <<<"$result")"
  assert_eq 'inconsistent parallel evidence cannot leave decision authority' true \
    "$(jq '.decision == null and .confirmed_blocker_refs == []' <<<"$result")"

  result="$(MOCK_TYPED_RESULT=invalid review_interactive_prepare_confirmation \
    "$sampled" APPROVE "$identity" null "$mock_runtime")"
  assert_eq 'typed invalid state without blockers has COMMENT ceiling' COMMENT \
    "$(jq -r '.effective_event' <<<"$result")"
  result="$(MOCK_TYPED_RESULT=malformed review_interactive_prepare_confirmation \
    "$sampled" APPROVE "$identity" null "$mock_runtime")"
  assert_eq 'malformed typed decision has no independent blocker authority' COMMENT \
    "$(jq -r '.effective_event' <<<"$result")"
  result="$(MOCK_TYPED_RESULT=inconsistent review_interactive_prepare_confirmation \
    "$sampled" APPROVE "$identity" null "$mock_runtime")"
  assert_eq 'same-schema identity and reference inconsistency fails closed' COMMENT \
    "$(jq -r '.effective_event' <<<"$result")"
  assert_eq 'same-schema inconsistent decision is not retained as authority' true \
    "$(jq '.decision == null' <<<"$result")"

  result="$(MOCK_TYPED_RESULT=valid review_interactive_prepare_confirmation \
    "$sampled" COMMENT "$identity" null "$mock_runtime")"
  review_interactive_apply_event_edit "$result" APPROVE >/dev/null 2>&1
  assert_eq 'typed blocker decision cannot be edited to APPROVE' 3 "$?"
  result="$(MOCK_TYPED_RESULT=invalid review_interactive_prepare_confirmation \
    "$sampled" APPROVE "$identity" null "$mock_runtime")"
  review_interactive_apply_event_edit "$result" APPROVE >/dev/null 2>&1
  assert_eq 'typed invalid COMMENT ceiling cannot be edited to APPROVE' 3 "$?"

  result="$(MOCK_TYPED_RESULT=approve review_interactive_prepare_confirmation \
    "$sampled" COMMENT "$identity" null "$mock_runtime")"
  review_interactive_confirm_post "$result" APPROVE pending >/dev/null 2>&1
  assert_eq 'typed post gate requires explicit human confirmation' 3 "$?"
  result="$(review_interactive_confirm_post "$result" APPROVE confirmed)"
  assert_eq 'eligible typed APPROVE survives explicit human post gate' APPROVE \
    "$(jq -r '.effective_event' <<<"$result")"
  assert_eq 'post gate receipt records human confirmation' true \
    "$(jq -r '.human_confirmed' <<<"$result")"
  forged_confirmation='{"blocker_evidence":null,"capability_gap_refs":["required-gap"],"confirmation_required":true,"confirmed_blocker_refs":[],"decision":null,"effective_event":"APPROVE","review_identity":{"base_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","config_hash":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","head_sha":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","pr_number":42,"repository":"acme/widgets","review_key":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","run_id":"run-typed"},"schema":"kc-pr-flow.interactive-confirmation/v1","source":"typed"}'
  review_interactive_confirm_post "$forged_confirmation" APPROVE confirmed >/dev/null 2>&1
  assert_eq 'typed post gate rejects a decisionless forged confirmation' 3 "$?"
  post_block="$(sed -n '/^## Step 7: Post Review$/,/^## Step 8: Learning/p' "$SKILL")"
  assert_eq 'Step 7 requires the closed interactive post-gate receipt' 1 \
    "$(printf '%s' "$post_block" | grep -cF 'kc-pr-flow.interactive-post-gate/v1' || true)"
  assert_eq 'no posting mutation occurs before confirmation' 0 "$(wc -c <"$mutation_log" | tr -d ' ')"
}

# `all` has to mean all: this group was previously reachable only by naming it
# explicitly, so its assertions never ran in CI (which invokes this script with
# no arguments) — including every check on posting authority.
if [ "$CASE_FILTER" = 's01-skill-inertness' ] || [ "$CASE_FILTER" = 'all' ]; then
  run_s01_skill_inertness_tests
  if [ "$CASE_FILTER" = 's01-skill-inertness' ]; then
    printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
    [ "$FAIL" -eq 0 ]
    exit
  fi
fi

if [ "$CASE_FILTER" = 'typed-interactive-seam' ] || [ "$CASE_FILTER" = 'all' ]; then
  run_typed_interactive_seam_tests
  if [ "$CASE_FILTER" = 'typed-interactive-seam' ]; then
    printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
    [ "$FAIL" -eq 0 ]
    exit
  fi
fi

if [ "$CASE_FILTER" = 'all' ]; then
  run_skill_slimming_handoff_tests
fi

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
MOVED_HEAD='dddddddddddddddddddddddddddddddddddddddd'
CONFIG_HASH='cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc'
SHADOW_REPO="$TEST_ROOT/shadow-repo"
mkdir -p "$SHADOW_REPO/src"
git -C "$SHADOW_REPO" init -q
printf '%s\n' one two three four five six 'evidence line' >"$SHADOW_REPO/src/app.sh"
printf 'uncertain file\n' >"$SHADOW_REPO/src/uncertain.sh"
git -C "$SHADOW_REPO" add src/app.sh src/uncertain.sh
git -C "$SHADOW_REPO" -c user.name='Shadow Test' -c user.email='shadow@example.invalid' commit -qm seed
HEAD_SHA="$(git -C "$SHADOW_REPO" rev-parse HEAD)"
BASE_SHA="$HEAD_SHA"
REVIEW_KEY="$(sha256_text "$REPOSITORY|$PR_NUMBER|$BASE_SHA|$HEAD_SHA|$CONFIG_HASH")"
OCCURRED_AT='2026-07-22T00:00:00Z'
EVIDENCE_HASH="$(file_sha256 "$SHADOW_REPO/src/app.sh")"
UNCERTAIN_HASH="$(file_sha256 "$SHADOW_REPO/src/uncertain.sh")"
EVIDENCE_ANCHOR="$(sha256_text 'evidence line')"

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
UNCERTAIN_ANCHOR="$(sha256_text "$(printf '%s' "$UNCERTAIN_POINTER" | jq -S -c \
  '{content_sha256,line,object_sha,path,side}')")"

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
  --argjson evidence "$POINTER" --argjson uncertain_evidence "$UNCERTAIN_POINTER" \
  --arg evidence_anchor "$EVIDENCE_ANCHOR" --arg uncertain_anchor "$UNCERTAIN_ANCHOR" '
  {
    schema:"kc-pr-flow.shadow-observation/v1",
    identity:{repository:$repository,pr_number:$pr_number,base_sha:$base_sha,head_sha:$head_sha,config_hash:$config_hash,occurred_at:$occurred_at},
    behavior_hashes:{body_sha256:$body_sha256,inline_comments_sha256:$inline_comments_sha256,event_sha256:$event_sha256,options_sha256:$options_sha256,confirmation_input_sha256:$confirmation_input_sha256,github_call_log_sha256:$github_call_log_sha256},
    lanes:[
      {lane_id:"correctness",capability:"code_correctness",provider_family:"claude",terminal_status:"succeeded",
       usage:{input_tokens:100,output_tokens:20,total_tokens:120,provenance:"reported",provider_family:"claude",scope:"lane"},
       candidates:[{ordinal:1,path:"src/app.sh",side:"RIGHT",anchor_sha256:$evidence_anchor,category:"correctness",claim_key:"missing_guard",evidence:$evidence}]},
      {lane_id:"security",capability:"security",terminal_status:"unavailable",
       usage:{input_tokens:null,output_tokens:null,total_tokens:null,provenance:"unavailable",provider_family:null,scope:"lane"},
       candidates:[{ordinal:1,path:"src/uncertain.sh",side:"FILE",anchor_sha256:$uncertain_anchor,category:"security",claim_key:"uncertain_boundary",evidence:$uncertain_evidence}]}
    ],
    synthesis:{
      findings:[{path:"src/app.sh",side:"RIGHT",anchor_sha256:$evidence_anchor,category:"correctness",claim_key:"missing_guard",evidence:$evidence,candidate_refs:[{lane_id:"correctness",ordinal:1}]}],
      uncertain_candidate_refs:[{lane_id:"security",ordinal:1}]
    }
  }' >"$OBSERVATION"

run_shadow_executable() { # gate, head-status, live-head, observation, state-root
  KC_PR_FLOW_STATE_DIR="$5" bash "$RUNTIME" shadow \
    --enabled "$1" --head-check-status "$2" --live-head "$3" --observation-file "$4" \
    --repo-worktree "$SHADOW_REPO"
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

# A terminal shadow lifecycle must converge on the current v2 receipt authority.
MINT_REPO="$TEST_ROOT/mint-repo"
MINT_ROOT="$TEST_ROOT/mint-state"
MINT_OBSERVATION="$TEST_ROOT/mint-observation.json"
MINT_CONFIG="$TEST_ROOT/mint-config.json"
MINT_RECEIPT="$TEST_ROOT/mint-receipt.json"
mkdir -p "$MINT_REPO/src"
git -C "$MINT_REPO" init -q
printf '%s\n' one two three four five six 'evidence line' >"$MINT_REPO/src/app.sh"
git -C "$MINT_REPO" add src/app.sh
git -C "$MINT_REPO" -c user.name='Shadow Test' -c user.email='shadow@example.invalid' commit -qm seed
MINT_HEAD="$(git -C "$MINT_REPO" rev-parse HEAD)"
printf '%s' "$(review_runtime_config_canonical lite bugfix false false false false code_correctness)" >"$MINT_CONFIG"
MINT_CONFIG_HASH="$(file_sha256 "$MINT_CONFIG")"
MINT_REVIEW_KEY="$(review_runtime_review_key "$REPOSITORY" "$PR_NUMBER" "$MINT_HEAD" "$MINT_HEAD" "$MINT_CONFIG_HASH")"
MINT_CONTENT_HASH="$(file_sha256 "$MINT_REPO/src/app.sh")"
MINT_ANCHOR="$(sha256_text 'evidence line')"
MINT_POINTER="$(jq -S -c -n --arg repository "$REPOSITORY" --arg review_key "$MINT_REVIEW_KEY" \
  --arg sha "$MINT_HEAD" --arg content "$MINT_CONTENT_HASH" '
  {schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",repository:$repository,
   review_key:$review_key,base_sha:$sha,head_sha:$sha,object_sha:$sha,
   content_sha256:$content,path:"src/app.sh",side:"RIGHT",line:7,locator:null}')"
jq -S -c --arg base "$MINT_HEAD" --arg head "$MINT_HEAD" --arg config "$MINT_CONFIG_HASH" \
  --argjson evidence "$MINT_POINTER" --arg anchor "$MINT_ANCHOR" '
  .identity.base_sha=$base | .identity.head_sha=$head | .identity.config_hash=$config |
  .lanes=[(.lanes[0] | .candidates=[
    (.candidates[0] | .evidence=$evidence | .anchor_sha256=$anchor | .claim_key="caller-claim"),
    (.candidates[0] | .ordinal=2 | .category="performance" | .evidence=$evidence |
      .anchor_sha256=$anchor | .claim_key="second-claim")])] |
  .synthesis.findings=[
    (.synthesis.findings[0] | .evidence=$evidence | .anchor_sha256=$anchor | .claim_key="caller-claim"),
    (.synthesis.findings[0] | .category="performance" | .evidence=$evidence |
      .anchor_sha256=$anchor | .claim_key="second-claim" | .candidate_refs[0].ordinal=2)] |
  .synthesis.uncertain_candidate_refs=[]' "$OBSERVATION" >"$MINT_OBSERVATION"
MINT_OUTPUT="$(KC_PR_FLOW_STATE_DIR="$MINT_ROOT" \
  review_runtime_shadow on ok "$MINT_HEAD" "$MINT_OBSERVATION" "$MINT_REPO")"
assert_eq 'receipt-ready shadow observation completes' observed "$(jq -r '.status' <<<"$MINT_OUTPUT")"
MINT_EVENTS="$(find "$MINT_ROOT" -name events.jsonl -type f)"
assert_eq 'shadow candidates and findings converge on v2 identity' \
  'kc-pr-flow.review-candidate/v2,kc-pr-flow.review-candidate/v2,kc-pr-flow.review-finding/v2,kc-pr-flow.review-finding/v2' \
  "$(jq -r 'if .event_type == "finding.observed" then .payload.candidate.schema
    elif .event_type == "synthesis.finished" then .payload.findings[].schema else empty end' \
    "$MINT_EVENTS" | paste -sd, -)"
bash "$RUNTIME" receipt --event-file "$MINT_EVENTS" --config-file "$MINT_CONFIG" \
  --repo-worktree "$MINT_REPO" >"$MINT_RECEIPT" 2>/dev/null
assert_eq 'terminal shadow log mints a current delta receipt' 0 "$?"
assert_eq 'receipt preserves two distinct v2 findings' 2 "$(jq '.known_findings | length' "$MINT_RECEIPT")"
review_runtime_validate_delta_receipt_files \
  "$MINT_RECEIPT" "$MINT_EVENTS" "$MINT_CONFIG" "$MINT_REPO" >/dev/null 2>&1
assert_eq 'shared file validator accepts the minted shadow receipt' 0 "$?"

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
dynamic_output="$(KC_PR_FLOW_STATE_DIR="$DYNAMIC_ROOT" review_runtime_shadow on ok "$HEAD_SHA" "$OBSERVATION" "$SHADOW_REPO")"
assert_eq 'dynamic production seam completes' 'observed' "$(jq -r '.status' <<<"$dynamic_output")"
assert_eq 'dynamic production seam invokes observer exactly once' '1' "$(wc -l <"$OBSERVER_CALL_LOG" | tr -d ' ')"
eval "$(declare -f review_runtime_observe_actual | sed '1s/review_runtime_observe_actual/review_runtime_observe/')"

# Missing jq is fail-open and the status encoder has a dependency-free JSON
# fallback. A deterministic post-start build failure is typed and never observed.
original_require_jq_definition="$(declare -f review_runtime_require_jq | sed '1s/review_runtime_require_jq/review_runtime_require_jq_actual/')"
eval "$original_require_jq_definition"
review_runtime_require_jq() { return 69; }
MISSING_JQ_ROOT="$TEST_ROOT/missing-jq-state"
missing_jq_output="$(KC_PR_FLOW_STATE_DIR="$MISSING_JQ_ROOT" review_runtime_shadow on ok "$HEAD_SHA" "$OBSERVATION" "$SHADOW_REPO" 2>/dev/null)"
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
post_start_output="$(KC_PR_FLOW_STATE_DIR="$POST_START_ROOT" review_runtime_shadow on ok "$HEAD_SHA" "$OBSERVATION" "$SHADOW_REPO" 2>/dev/null)"
post_start_rc=$?
assert_eq 'post-start failure remains fail-open' '0' "$post_start_rc"
assert_eq 'post-start failure emits typed not_observed' 'not_observed' "$(jq -r '.status' <<<"$post_start_output")"
assert_eq 'post-start failure never reports observed' 'false' "$(jq -r '.status == "observed"' <<<"$post_start_output")"
assert_eq 'post-start failure leaves one defined incomplete log' '1' "$(find "$POST_START_ROOT" -name events.jsonl -type f | wc -l | tr -d ' ')"
assert_eq 'post-start partial log contains only run.started' 'run.started' \
  "$(jq -r '.event_type' "$(find "$POST_START_ROOT" -name events.jsonl -type f)")"
eval "$(declare -f review_runtime_build_event_actual | sed '1s/review_runtime_build_event_actual/review_runtime_build_event/')"

run_skill_slimming_integration_tests

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
