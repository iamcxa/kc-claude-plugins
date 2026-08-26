#!/usr/bin/env bash
# Contract tests for the trusted review delta receipt boundary.
# shellcheck disable=SC2016,SC2030,SC2031,SC2317 # Intentional generated stubs, subshells, and test overrides.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PLAN="$HERE/review-plan.sh"
RUNTIME="$HERE/review-runtime.sh"
SKILL="$HERE/../skills/kc-pr-review/SKILL.md"
REFERENCE="$HERE/../reference/review-runtime.md"
TEST_ROOT="$(cd "$(mktemp -d)" && pwd -P)"
cleanup() {
  chmod -R u+rwX "$TEST_ROOT" 2>/dev/null || true
  rm -rf "$TEST_ROOT"
}
trap cleanup EXIT

PASS=0
FAIL=0
CASE_FILTER='all'
if [ "$#" -gt 0 ]; then
  if [ "$#" -ne 2 ] || [ "$1" != '--case' ]; then
    printf 'usage: %s [--case receipt-contract|mode-router|trust-boundary|worktree-safety|skill-wiring]\n' "$0" >&2
    exit 2
  fi
  CASE_FILTER="$2"
fi

pass() { PASS=$((PASS + 1)); }
fail() { FAIL=$((FAIL + 1)); printf 'FAIL: %s\n' "$1"; }
assert_eq() {
  if [ "$2" = "$3" ]; then pass; else fail "$1 (expected [$2], got [$3])"; fi
}
assert_not_zero() {
  if [ "$2" -ne 0 ]; then pass; else fail "$1 (expected nonzero status)"; fi
}
assert_file_contains() {
  if grep -Eq "$2" "$1"; then pass; else fail "$3 (missing [$2] in $1)"; fi
}
assert_file_not_contains() {
  if grep -Fq "$2" "$1"; then fail "$3 (unexpected [$2] in $1)"; else pass; fi
}
assert_match() {
  if grep -Eq "$2" <<<"$3"; then pass; else fail "$1 (expected [$2], got [$3])"; fi
}

sha256_text() {
  if command -v shasum >/dev/null 2>&1; then
    printf '%s' "$1" | shasum -a 256 | awk '{print $1}'
  else
    printf '%s' "$1" | sha256sum | awk '{print $1}'
  fi
}

if [ "$CASE_FILTER" = 'all' ] || [ "$CASE_FILTER" = 'receipt-contract' ]; then
  if [ ! -r "$RUNTIME" ]; then
    fail 'review-runtime.sh exists';
  else
    # shellcheck source=/dev/null
    . "$RUNTIME"
    REPOSITORY='acme/widgets'
    PR_NUMBER=42
    CONFIG_HASH='cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc'
    OCCURRED_AT='2026-07-22T00:00:00Z'
    EVENT_FILE="$TEST_ROOT/terminal-events.jsonl"
    FIXTURE_REPO="$TEST_ROOT/repo"
    mkdir -p "$FIXTURE_REPO/src"
    git -C "$FIXTURE_REPO" init -q
    printf 'evidence bound review\n' >"$FIXTURE_REPO/src/review.sh"
    git -C "$FIXTURE_REPO" add src/review.sh
    git -C "$FIXTURE_REPO" -c user.name='Receipt Test' -c user.email='receipt@example.invalid' commit -qm seed
    git -C "$FIXTURE_REPO" remote add origin 'https://github.com/acme/widgets.git'
    HEAD_SHA="$(git -C "$FIXTURE_REPO" rev-parse HEAD)"
    REVIEW_KEY="$(sha256_text "$REPOSITORY|$PR_NUMBER|$HEAD_SHA|$HEAD_SHA|$CONFIG_HASH")"
    CONTENT_SHA256="$(review_runtime_sha256 <"$FIXTURE_REPO/src/review.sh")"
    RUN_ID='run-receipt-terminal'
    POINTER="$(jq -S -c -n --arg key "$REVIEW_KEY" --arg repo "$REPOSITORY" \
      --arg base "$HEAD_SHA" --arg head "$HEAD_SHA" --arg hash "$CONTENT_SHA256" \
      '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",review_key:$key,repository:$repo,
        base_sha:$base,head_sha:$head,object_sha:$head,path:"src/review.sh",side:"RIGHT",line:1,
        locator:"review-anchor",content_sha256:$hash}')"
    CANDIDATE_ID="$(review_runtime_candidate_id "$RUN_ID" security-1 1 "$CONTENT_SHA256")"
    CANDIDATE="$(jq -S -c -n --arg id "$CANDIDATE_ID" --arg key "$REVIEW_KEY" \
      --arg run "$RUN_ID" --argjson evidence "$POINTER" \
      '{schema:"kc-pr-flow.review-candidate/v1",candidate_id:$id,run_id:$run,review_key:$key,
        lane_id:"security-1",ordinal:1,path:"src/review.sh",side:"RIGHT",
        anchor_sha256:"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        category:"security",claim_key:"unchecked-boundary",evidence:$evidence}')"
    TASK="$(jq -S -c -n --arg run "$RUN_ID" --arg key "$REVIEW_KEY" --arg repo "$REPOSITORY" \
      --arg base "$HEAD_SHA" --arg head "$HEAD_SHA" --arg config "$CONFIG_HASH" \
      '{schema:"kc-pr-flow.review-task/v1",run_id:$run,review_key:$key,lane_id:"security-1",
        capability:"security",repository:$repo,pr_number:42,base_sha:$base,head_sha:$head,config_hash:$config}')"
    USAGE='{"input_tokens":100,"output_tokens":25,"provenance":"reported","provider_family":"claude","scope":"lane","total_tokens":125}'
    RESULT="$(jq -S -c -n --arg run "$RUN_ID" --arg key "$REVIEW_KEY" --arg id "$CANDIDATE_ID" \
      --argjson usage "$USAGE" \
      '{schema:"kc-pr-flow.lane-result/v1",run_id:$run,review_key:$key,lane_id:"security-1",
        capability:"security",terminal_status:"succeeded",candidates:[$id],usage:$usage,provider_family:"claude"}')"
    FINDING_ID="$(review_runtime_finding_id "$REVIEW_KEY" "src/review.sh|RIGHT|$CONTENT_SHA256|security|unchecked-boundary")"
    FINDING="$(jq -S -c -n --arg id "$FINDING_ID" --arg key "$REVIEW_KEY" --arg merge "src/review.sh|RIGHT|$CONTENT_SHA256|security|unchecked-boundary" \
      --argjson evidence "$POINTER" --arg candidate "$CANDIDATE_ID" \
      '{schema:"kc-pr-flow.review-finding/v1",finding_id:$id,review_key:$key,merge_key:$merge,
        path:"src/review.sh",side:"RIGHT",anchor_sha256:"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        category:"security",claim_key:"unchecked-boundary",candidate_ids:[$candidate],evidence:$evidence}')"
    BEHAVIOR="$(jq -S -c -n --arg hash "$CONTENT_SHA256" \
      '{body_sha256:$hash,confirmation_input_sha256:$hash,event_sha256:$hash,
        github_call_log_sha256:$hash,inline_comments_sha256:$hash,options_sha256:$hash}')"
    START="$(review_runtime_build_event "$RUN_ID" "$REVIEW_KEY" "$REPOSITORY" "$PR_NUMBER" "$HEAD_SHA" "$HEAD_SHA" "$CONFIG_HASH" 1 "$OCCURRED_AT" run.started '{}')"
    LANE_START="$(review_runtime_build_event "$RUN_ID" "$REVIEW_KEY" "$REPOSITORY" "$PR_NUMBER" "$HEAD_SHA" "$HEAD_SHA" "$CONFIG_HASH" 2 "$OCCURRED_AT" lane.started "$(jq -S -c -n --argjson value "$TASK" '{review_task:$value}')")"
    OBSERVED="$(review_runtime_build_event "$RUN_ID" "$REVIEW_KEY" "$REPOSITORY" "$PR_NUMBER" "$HEAD_SHA" "$HEAD_SHA" "$CONFIG_HASH" 3 "$OCCURRED_AT" finding.observed "$(jq -S -c -n --argjson value "$CANDIDATE" '{candidate:$value}')")"
    LANE_FINISHED="$(review_runtime_build_event "$RUN_ID" "$REVIEW_KEY" "$REPOSITORY" "$PR_NUMBER" "$HEAD_SHA" "$HEAD_SHA" "$CONFIG_HASH" 4 "$OCCURRED_AT" lane.finished "$(jq -S -c -n --argjson value "$RESULT" '{lane_result:$value}')")"
    SYNTHESIZED="$(review_runtime_build_event "$RUN_ID" "$REVIEW_KEY" "$REPOSITORY" "$PR_NUMBER" "$HEAD_SHA" "$HEAD_SHA" "$CONFIG_HASH" 5 "$OCCURRED_AT" synthesis.finished "$(jq -S -c -n --argjson value "$FINDING" '{findings:[$value],uncertain_candidate_ids:[]}')")"
    FINISHED="$(review_runtime_build_event "$RUN_ID" "$REVIEW_KEY" "$REPOSITORY" "$PR_NUMBER" "$HEAD_SHA" "$HEAD_SHA" "$CONFIG_HASH" 6 "$OCCURRED_AT" run.finished "$(jq -S -c -n --argjson value "$BEHAVIOR" '{behavior_hashes:$value}')")"
    printf '%s\n' "$START" "$LANE_START" "$OBSERVED" "$LANE_FINISHED" "$SYNTHESIZED" "$FINISHED" >"$EVENT_FILE"

    STUB_DIR="$TEST_ROOT/stubs"
    CALL_LEDGER="$TEST_ROOT/calls"
    mkdir -p "$STUB_DIR"
    : >"$CALL_LEDGER"
    for command in gh curl wget ssh codex agy; do
      printf '#!/bin/sh\nprintf "%%s\\n" "$(basename "$0") $*" >>"$CALL_LEDGER"\nexit 97\n' >"$STUB_DIR/$command"
      chmod +x "$STUB_DIR/$command"
    done

    if [ -r "$PLAN" ]; then
      # shellcheck source=/dev/null
      . "$PLAN"
      source_probe="$(bash -c 'before_flags=$-; before_umask=$(umask); before_pwd=$PWD; source "$1"; printf "%s|%s|%s|%s|%s|%s" "$before_flags" "$-" "$before_umask" "$(umask)" "$before_pwd" "$PWD"' _ "$PLAN")"
      IFS='|' read -r before_flags after_flags before_umask after_umask before_pwd after_pwd <<<"$source_probe"
      assert_eq 'sourcing preserves caller shell options' "$before_flags" "$after_flags"
      assert_eq 'sourcing preserves caller umask' "$before_umask" "$after_umask"
      assert_eq 'sourcing preserves caller working directory' "$before_pwd" "$after_pwd"
      receipt_out="$(PATH="$STUB_DIR:$PATH" bash "$PLAN" receipt --event-file "$EVENT_FILE" 2>/dev/null)"
      receipt_rc=$?
      assert_eq 'receipt command succeeds for complete replay' '0' "$receipt_rc"
      projection="$(review_runtime_replay "$EVENT_FILE")"
      assert_eq 'receipt schema' 'kc-pr-flow.review-delta-receipt/v1' "$(jq -r '.schema' <<<"$receipt_out")"
      assert_eq 'receipt keys are closed' 'content_sha256,coverage_gap_refs,known_findings,predecessor,required_capabilities,schema' "$(jq -r 'keys | sort | join(",")' <<<"$receipt_out")"
      assert_eq 'all terminal findings remain unresolved' 'unresolved' "$(jq -r '[.known_findings[].resolution_state] | unique | join(",")' <<<"$receipt_out")"
      assert_eq 'finding IDs come from replay' "$(jq -r '.findings | map(.finding_id) | sort | join(",")' <<<"$projection")" "$(jq -r '.known_findings | map(.finding_id) | sort | join(",")' <<<"$receipt_out")"
      validator_err="$TEST_ROOT/validator.err"
      review_plan_validate_receipt "$receipt_out" "$EVENT_FILE" 2>"$validator_err"
      validator_rc=$?
      assert_eq 'receipt validates against fresh projection' '0' "$validator_rc"
      assert_eq 'no transport or model stub was called' '' "$(cat "$CALL_LEDGER")"

      assert_receipt_rejected() {
        local description="$1" candidate_receipt="$2" rejected_rc
        review_plan_validate_receipt "$candidate_receipt" "$EVENT_FILE" >/dev/null 2>&1
        rejected_rc=$?
        assert_not_zero "$description" "$rejected_rc"
      }
      assert_receipt_rejected 'arbitrary receipt_id is rejected' "$(jq -S -c '.predecessor.receipt_id=("0"*64)' <<<"$receipt_out")"
      assert_receipt_rejected 'changed content_sha256 is rejected' "$(jq -S -c '.content_sha256=("0"*64)' <<<"$receipt_out")"
      assert_receipt_rejected 'changed finding_id is rejected' "$(jq -S -c '.known_findings[0].finding_id=("1"*64)' <<<"$receipt_out")"
      assert_receipt_rejected 'extra top-level member is rejected' "$(jq -S -c '.extra_key=true' <<<"$receipt_out")"
      assert_receipt_rejected 'extra predecessor member is rejected' "$(jq -S -c '.predecessor.extra_key=true' <<<"$receipt_out")"
      assert_receipt_rejected 'missing evidence hash is rejected' "$(jq -S -c 'del(.known_findings[0].evidence_sha256)' <<<"$receipt_out")"
      duplicate_receipt_raw='{"schema":"kc-pr-flow.review-delta-receipt/v1","schema":"kc-pr-flow.review-delta-receipt/v1"}'
      assert_receipt_rejected 'raw duplicate receipt member is rejected' "$duplicate_receipt_raw"

      symlink_events="$TEST_ROOT/events-link.jsonl"
      ln -s "$EVENT_FILE" "$symlink_events"
      PATH="$STUB_DIR:$PATH" bash "$PLAN" receipt --event-file "$symlink_events" >/dev/null 2>&1
      assert_not_zero 'symlink event input is rejected' "$?"

      fifo_events="$TEST_ROOT/events.fifo"
      mkfifo "$fifo_events"
      review_plan_build_receipt "$fifo_events" >/dev/null 2>&1
      assert_not_zero 'FIFO event input is rejected' "$?"

      incomplete_events="$TEST_ROOT/incomplete-events.jsonl"
      sed '$d' "$EVENT_FILE" >"$incomplete_events"
      review_plan_build_receipt "$incomplete_events" >/dev/null 2>&1
      assert_not_zero 'incomplete runtime lifecycle is rejected' "$?"

      duplicate_events="$TEST_ROOT/duplicate-events.jsonl"
      awk 'NR == 1 { sub(/^\{/, "{\"schema\":\"kc-pr-flow.review-event/v1\","); } { print }' \
        "$EVENT_FILE" >"$duplicate_events"
      review_plan_build_receipt "$duplicate_events" >/dev/null 2>&1
      assert_not_zero 'duplicate JSON member input is rejected' "$?"
      review_plan_validate_receipt "$receipt_out" "$duplicate_events" >/dev/null 2>&1
      assert_not_zero 'raw duplicate event-derived input is rejected by validator' "$?"

      oversized_events="$TEST_ROOT/oversized-events.jsonl"
      cp "$EVENT_FILE" "$oversized_events"
      KC_PR_FLOW_MAX_EVENTS_BYTES=1 review_plan_build_receipt "$oversized_events" >/dev/null 2>&1
      assert_not_zero 'oversized event input is rejected' "$?"
    else
      fail 'review-plan.sh exists after RED implementation'
    fi
  fi
fi

make_replay_receipt() {
  local fixture_repo="$1" repository="$2" pr_number="$3" base_sha="$4" reviewed_sha="$5"
  local config_hash="$6" event_file="$7" receipt_file="$8" review_key content_sha run_id pointer
  local candidate_id candidate task_correctness task_coverage result_correctness result_coverage finding_id finding behavior
  local started correctness_started coverage_started observed correctness_finished coverage_finished synthesized finished

  review_key="$(sha256_text "$repository|$pr_number|$base_sha|$reviewed_sha|$config_hash")"
  content_sha="$(git -C "$fixture_repo" show "$reviewed_sha:src/parser.py" | review_runtime_sha256)"
  run_id='run-pr1693-replay'
  pointer="$(jq -S -c -n --arg key "$review_key" --arg repo "$repository" --arg base "$base_sha" \
    --arg head "$reviewed_sha" --arg hash "$content_sha" \
    '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",review_key:$key,repository:$repo,
      base_sha:$base,head_sha:$head,object_sha:$head,path:"src/parser.py",side:"RIGHT",line:1,
      locator:"parser-anchor",content_sha256:$hash}')"
  candidate_id="$(review_runtime_candidate_id "$run_id" correctness-1 1 "$content_sha")"
  candidate="$(jq -S -c -n --arg id "$candidate_id" --arg key "$review_key" --arg run "$run_id" \
    --argjson evidence "$pointer" \
    '{schema:"kc-pr-flow.review-candidate/v1",candidate_id:$id,run_id:$run,review_key:$key,
      lane_id:"correctness-1",ordinal:1,path:"src/parser.py",side:"RIGHT",
      anchor_sha256:"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
      category:"correctness",claim_key:"empty-input-contract",evidence:$evidence}')"
  task_correctness="$(jq -S -c -n --arg run "$run_id" --arg key "$review_key" --arg repo "$repository" \
    --arg base "$base_sha" --arg head "$reviewed_sha" --arg config "$config_hash" --argjson pr "$pr_number" \
    '{schema:"kc-pr-flow.review-task/v1",run_id:$run,review_key:$key,lane_id:"correctness-1",
      capability:"correctness",repository:$repo,pr_number:$pr,base_sha:$base,head_sha:$head,config_hash:$config}')"
  task_coverage="$(jq -S -c -n --arg run "$run_id" --arg key "$review_key" --arg repo "$repository" \
    --arg base "$base_sha" --arg head "$reviewed_sha" --arg config "$config_hash" --argjson pr "$pr_number" \
    '{schema:"kc-pr-flow.review-task/v1",run_id:$run,review_key:$key,lane_id:"test-coverage-1",
      capability:"test-coverage",repository:$repo,pr_number:$pr,base_sha:$base,head_sha:$head,config_hash:$config}')"
  result_correctness="$(jq -S -c -n --arg run "$run_id" --arg key "$review_key" --arg id "$candidate_id" \
    '{schema:"kc-pr-flow.lane-result/v1",run_id:$run,review_key:$key,lane_id:"correctness-1",
      capability:"correctness",terminal_status:"succeeded",candidates:[$id],usage:{input_tokens:1,output_tokens:1,total_tokens:2,provenance:"reported",provider_family:"fixture",scope:"lane"},provider_family:"fixture"}')"
  result_coverage="$(jq -S -c -n --arg run "$run_id" --arg key "$review_key" \
    '{schema:"kc-pr-flow.lane-result/v1",run_id:$run,review_key:$key,lane_id:"test-coverage-1",
      capability:"test-coverage",terminal_status:"succeeded",candidates:[],usage:{input_tokens:1,output_tokens:1,total_tokens:2,provenance:"reported",provider_family:"fixture",scope:"lane"},provider_family:"fixture"}')"
  finding_id="$(review_runtime_finding_id "$review_key" "src/parser.py|RIGHT|$content_sha|correctness|empty-input-contract")"
  finding="$(jq -S -c -n --arg id "$finding_id" --arg key "$review_key" \
    --arg merge "src/parser.py|RIGHT|$content_sha|correctness|empty-input-contract" --arg candidate "$candidate_id" \
    --argjson evidence "$pointer" \
    '{schema:"kc-pr-flow.review-finding/v1",finding_id:$id,review_key:$key,merge_key:$merge,
      path:"src/parser.py",side:"RIGHT",anchor_sha256:"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
      category:"correctness",claim_key:"empty-input-contract",candidate_ids:[$candidate],evidence:$evidence}')"
  behavior="$(jq -S -c -n --arg hash "$content_sha" \
    '{body_sha256:$hash,confirmation_input_sha256:$hash,event_sha256:$hash,
      github_call_log_sha256:$hash,inline_comments_sha256:$hash,options_sha256:$hash}')"
  started="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$reviewed_sha" "$config_hash" 1 '2026-08-26T00:00:00Z' run.started '{}')"
  correctness_started="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$reviewed_sha" "$config_hash" 2 '2026-08-26T00:00:00Z' lane.started "$(jq -S -c -n --argjson value "$task_correctness" '{review_task:$value}')")"
  coverage_started="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$reviewed_sha" "$config_hash" 3 '2026-08-26T00:00:00Z' lane.started "$(jq -S -c -n --argjson value "$task_coverage" '{review_task:$value}')")"
  observed="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$reviewed_sha" "$config_hash" 4 '2026-08-26T00:00:00Z' finding.observed "$(jq -S -c -n --argjson value "$candidate" '{candidate:$value}')")"
  correctness_finished="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$reviewed_sha" "$config_hash" 5 '2026-08-26T00:00:00Z' lane.finished "$(jq -S -c -n --argjson value "$result_correctness" '{lane_result:$value}')")"
  coverage_finished="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$reviewed_sha" "$config_hash" 6 '2026-08-26T00:00:00Z' lane.finished "$(jq -S -c -n --argjson value "$result_coverage" '{lane_result:$value}')")"
  synthesized="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$reviewed_sha" "$config_hash" 7 '2026-08-26T00:00:00Z' synthesis.finished "$(jq -S -c -n --argjson value "$finding" '{findings:[$value],uncertain_candidate_ids:[]}')")"
  finished="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$reviewed_sha" "$config_hash" 8 '2026-08-26T00:00:00Z' run.finished "$(jq -S -c -n --argjson value "$behavior" '{behavior_hashes:$value}')")"
  printf '%s\n' "$started" "$correctness_started" "$coverage_started" "$observed" "$correctness_finished" "$coverage_finished" "$synthesized" "$finished" >"$event_file"
  bash "$PLAN" receipt --event-file "$event_file" >"$receipt_file"
  printf '%s\n' "$finding_id"
}

make_replay_repo() {
  local fixture_repo="$1" fixture="$2"
  mkdir -p "$fixture_repo"
  git -C "$fixture_repo" init -q
  git -C "$fixture_repo" config user.name 'Router Test'
  git -C "$fixture_repo" config user.email 'router@example.invalid'
  while IFS=$'\t' read -r name _; do
    while IFS=$'\t' read -r path value; do
      mkdir -p "$fixture_repo/$(dirname "$path")"
      printf '%s' "$value" >"$fixture_repo/$path"
    done < <(jq -r --arg name "$name" '.commits[] | select(.name == $name) | .files | to_entries[] | [.key,.value] | @tsv' "$fixture")
    git -C "$fixture_repo" add .
    git -C "$fixture_repo" commit -qm "$name"
    printf '%s=%s\n' "$name" "$(git -C "$fixture_repo" rev-parse HEAD)"
  done < <(jq -r '.commits[] | [.name, (.files | tojson)] | @tsv' "$fixture")
}

skill_router_snippet() {
  awk '
    /^### Step 2\.2: Trusted Post-Fix Route$/ { in_section=1; next }
    in_section && /^```bash$/ { in_code=1; next }
    in_code && /^```$/ { exit }
    in_code { print }
  ' "$SKILL"
}

skill_router_trace() {
  local stub_mode="$1" script plugin_root snippet output decision review_key receipt
  plugin_root="$TEST_ROOT/skill-router-$stub_mode"
  mkdir -p "$plugin_root/scripts"
  review_key="$(sha256_text 'acme/widgets|1693|aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa|bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb|cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc')"
  decision="$(jq -S -c -n --arg key "$review_key" '
    {schema:"kc-pr-flow.review-plan-decision/v1",
      identity:{repository:"acme/widgets",pr_number:1693,
        base_sha:"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        head_sha:"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        config_hash:"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        review_key:$key},
      mode:"resolve",
      reason_codes:["ancestor_append","known_finding_delta","trusted_predecessor"],
      review_range:{from_exclusive:"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",to_inclusive:"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},
      inherited_finding_ids:["dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"],
      required_capabilities:["correctness"],
      event_ceiling:"APPROVE",
      fallback:{router_advisory:true,requires_existing_initial_review:false,final_verdict_authority:"existing-review-runtime"}}')"
  case "$stub_mode" in
    valid-exit-0) ;;
    valid-delta-exit-0)
      decision="$(jq -S -c '
        .mode="delta" |
        .reason_codes=["ancestor_append","expanded_delta","trusted_predecessor"] |
        .event_ceiling="COMMENT"' <<<"$decision")"
      ;;
    valid-initial-exit-0)
      decision="$(jq -S -c '
        .mode="initial" |
        .reason_codes=["missing_predecessor"] |
        .review_range.from_exclusive=null |
        .inherited_finding_ids=[] |
        .required_capabilities=[] |
        .event_ceiling=null |
        .fallback.requires_existing_initial_review=true' <<<"$decision")"
      ;;
    valid-prefix-exit-9)
      decision='{"schema":"kc-pr-flow.review-plan-decision/v1"}'
      ;;
    malformed-exit-0)
      decision='not-json'
      ;;
    schema-only-exit-0)
      decision='{"schema":"kc-pr-flow.review-plan-decision/v1"}'
      ;;
    extra-member-exit-0)
      decision="$(jq -S -c '. + {unexpected:true}' <<<"$decision")"
      ;;
    wrong-type-exit-0)
      decision="$(jq -S -c '.identity.pr_number="1693"' <<<"$decision")"
      ;;
    delta-empty-range-exit-0)
      decision="$(jq -S -c '
        .mode="delta" |
        .reason_codes=["ancestor_append","expanded_delta","trusted_predecessor"] |
        .review_range.from_exclusive=.identity.head_sha |
        .event_ceiling="COMMENT"' <<<"$decision")"
      ;;
    delta-empty-capabilities-exit-0)
      decision="$(jq -S -c '
        .mode="delta" |
        .reason_codes=["ancestor_append","expanded_delta","trusted_predecessor"] |
        .required_capabilities=[] |
        .event_ceiling="COMMENT"' <<<"$decision")"
      ;;
    delta-approve-ceiling-exit-0)
      decision="$(jq -S -c '
        .mode="delta" |
        .reason_codes=["ancestor_append","expanded_delta","trusted_predecessor"]' <<<"$decision")"
      ;;
    delta-null-ceiling-exit-0)
      decision="$(jq -S -c '
        .mode="delta" |
        .reason_codes=["ancestor_append","expanded_delta","trusted_predecessor"] |
        .event_ceiling=null' <<<"$decision")"
      ;;
    resolve-empty-range-exit-0)
      decision="$(jq -S -c '.review_range.from_exclusive=.identity.head_sha' <<<"$decision")"
      ;;
    resolve-comment-ceiling-exit-0)
      decision="$(jq -S -c '.event_ceiling="COMMENT"' <<<"$decision")"
      ;;
    resolve-wrong-capabilities-exit-0)
      decision="$(jq -S -c '.required_capabilities=[]' <<<"$decision")"
      ;;
    initial-wrong-reason-exit-0)
      decision="$(jq -S -c '
        .mode="initial" |
        .reason_codes=["not_a_producer_reason"] |
        .review_range.from_exclusive=null |
        .inherited_finding_ids=[] |
        .required_capabilities=[] |
        .event_ceiling=null |
        .fallback.requires_existing_initial_review=true' <<<"$decision")"
      ;;
    *)
      fail "unknown skill router stub mode: $stub_mode"
      return
      ;;
  esac
  printf '%s\n' "$decision" >"$plugin_root/scripts/review-plan.sh.decision"
  receipt="$(jq -S -c -n '
    {predecessor:{repository:"acme/widgets",pr_number:1693,
      base_sha:"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      head_sha:"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      config_hash:"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"},
     known_findings:[{finding_id:"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"}],
     required_capabilities:["correctness"]}')"
  printf '%s\n' "$receipt" >"$plugin_root/scripts/review-plan.sh.receipt"
  {
    printf '%s\n' '#!/usr/bin/env bash'
    printf 'source %q\n' "$PLAN"
    printf 'review_plan_snapshot_receipt() { cat %q; }\n' "$plugin_root/scripts/review-plan.sh.receipt"
    printf '%s\n' 'review_plan_validate_receipt() { return 0; }'
    printf '%s\n' 'review_plan_real_worktree() { printf "%s\\n" "$1"; }'
    printf '%s\n' 'review_plan_git_identity_valid() { return 0; }'
    printf '%s\n' 'review_plan_ancestor() { return 0; }'
    printf '%s\n' 'if [ "${1:-}" = decide ]; then'
    printf '%s\n' '  cat "$(dirname "$0")/review-plan.sh.decision"'
    if [ "$stub_mode" = 'valid-prefix-exit-9' ]; then
      printf '%s\n' '  exit 9'
    else
      printf '%s\n' '  exit 0'
    fi
    printf '%s\n' 'fi'
  } >"$plugin_root/scripts/review-plan.sh"
  chmod +x "$plugin_root/scripts/review-plan.sh"
  snippet="$(skill_router_snippet)"
  if [ -z "$snippet" ]; then
    fail 'skill router snippet is extractable'
    return
  fi
  script="$TEST_ROOT/skill-router-$stub_mode.sh"
  {
    printf '%s\n' 'set -eu'
    printf '%s\n' 'REPO=acme/widgets'
    printf '%s\n' 'PR_NUMBER=1693'
    printf '%s\n' 'BASE_SHA=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    printf '%s\n' 'REVIEWED_HEAD_SHA=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
    printf '%s\n' 'CONFIG_HASH=cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc'
    printf '%s\n' 'REPO_WORKTREE=/tmp/repo'
    printf '%s\n' 'PREDECESSOR_EVENTS=/tmp/events.jsonl'
    printf '%s\n' 'DELTA_RECEIPT=/tmp/receipt.json'
    printf 'CLAUDE_PLUGIN_ROOT=%q\n' "$plugin_root"
    printf 'KC_PR_FLOW_DELTA_FAST_PATH=%q\n' "${KC_PR_FLOW_DELTA_FAST_PATH:-off}"
    printf '%s\n' "$snippet"
    printf '%s\n' 'printf "mode=%s|plan=%s|ceiling=%s|reason=%s\n" "$REVIEW_MODE" "${PLAN_JSON-unset}" "${PLAN_EVENT_CEILING-unset}" "${PLAN_REASON-unset}"'
  } >"$script"
  output="$(bash "$script")"
  printf '%s' "$output"
}

skill_router_live_identity_mismatch_trace() {
  local mismatch="$1" fixture plugin_root router_repo replay_lines base_sha reviewed_sha fixed_sha
  local repository config_hash receipt_repository receipt_pr receipt_base receipt_config
  local events receipt receipt_json receipt_rc inherited_finding_ids required_capabilities decision script snippet output
  fixture="$HERE/../test/fixtures/review-plan/pr1693-replay.json"
  plugin_root="$TEST_ROOT/skill-router-live-$mismatch"
  router_repo="$plugin_root/repo"
  mkdir -p "$plugin_root/scripts"
  # shellcheck source=/dev/null
  . "$PLAN"
  review_plan_source_runtime || return
  replay_lines="$(make_replay_repo "$router_repo" "$fixture")"
  base_sha="$(awk -F= '$1 == "base" { print $2 }' <<<"$replay_lines")"
  reviewed_sha="$(awk -F= '$1 == "reviewed" { print $2 }' <<<"$replay_lines")"
  fixed_sha="$(awk -F= '$1 == "fixed" { print $2 }' <<<"$replay_lines")"
  repository="$(jq -r '.repository' "$fixture")"
  config_hash='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
  receipt_repository="$repository"
  receipt_pr=1693
  receipt_base="$base_sha"
  receipt_config="$config_hash"
  case "$mismatch" in
    repository) receipt_repository='other/widgets' ;;
    pr_number) receipt_pr=1694 ;;
    base_sha) receipt_base="$reviewed_sha" ;;
    config_hash) receipt_config='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb' ;;
    *) fail "unknown live identity mismatch: $mismatch"; return ;;
  esac
  events="$plugin_root/predecessor-events.jsonl"
  receipt="$plugin_root/delta-receipt.json"
  make_replay_receipt "$router_repo" "$receipt_repository" "$receipt_pr" "$receipt_base" "$reviewed_sha" \
    "$receipt_config" "$events" "$receipt" >/dev/null
  receipt_json="$(cat "$receipt")"
  review_plan_validate_receipt "$receipt_json" "$events"
  receipt_rc=$?
  inherited_finding_ids="$(jq -S -c '[.known_findings[].finding_id] | sort | unique' <<<"$receipt_json")"
  required_capabilities="$(jq -S -c '.required_capabilities | sort | unique' <<<"$receipt_json")"
  decision="$(review_plan_build_decision "$repository" 1693 "$base_sha" "$fixed_sha" "$config_hash" resolve \
    '["trusted_predecessor","ancestor_append","known_finding_delta"]' "\"$reviewed_sha\"" \
    "$inherited_finding_ids" "$required_capabilities" '"APPROVE"' false)"
  printf '%s\n' "$decision" >"$plugin_root/scripts/review-plan.sh.decision"
  {
    printf '%s\n' '#!/usr/bin/env bash'
    printf 'source %q\n' "$PLAN"
    printf '%s\n' 'if [ "${1:-}" = decide ]; then'
    printf '%s\n' '  cat "$(dirname "$0")/review-plan.sh.decision"'
    printf '%s\n' 'fi'
  } >"$plugin_root/scripts/review-plan.sh"
  chmod +x "$plugin_root/scripts/review-plan.sh"
  snippet="$(skill_router_snippet)"
  script="$plugin_root/trace.sh"
  {
    printf '%s\n' 'set -eu'
    printf 'REPO=%q\n' "$repository"
    printf '%s\n' 'PR_NUMBER=1693'
    printf 'BASE_SHA=%q\n' "$base_sha"
    printf 'REVIEWED_HEAD_SHA=%q\n' "$fixed_sha"
    printf 'CONFIG_HASH=%q\n' "$config_hash"
    printf 'REPO_WORKTREE=%q\n' "$router_repo"
    printf 'PREDECESSOR_EVENTS=%q\n' "$events"
    printf 'DELTA_RECEIPT=%q\n' "$receipt"
    printf 'CLAUDE_PLUGIN_ROOT=%q\n' "$plugin_root"
    printf '%s\n' 'KC_PR_FLOW_DELTA_FAST_PATH=on'
    printf '%s\n' "$snippet"
    printf '%s\n' 'printf "mode=%s|plan=%s|ceiling=%s|reason=%s\\n" "$REVIEW_MODE" "${PLAN_JSON-unset}" "${PLAN_EVENT_CEILING-unset}" "${PLAN_REASON-unset}"'
  } >"$script"
  output="$(bash "$script")"
  printf 'receipt_rc=%s\n%s' "$receipt_rc" "$output"
}

if [ "$CASE_FILTER" = 'all' ] || [ "$CASE_FILTER" = 'skill-wiring' ]; then
  assert_file_contains "$SKILL" 'KC_PR_FLOW_DELTA_FAST_PATH=on' 'skill documents the default-off fast-path flag'
  assert_file_contains "$SKILL" 'review-plan\.sh" decide' 'skill invokes the route planner'
  assert_file_contains "$SKILL" 'mode == "initial"' 'skill documents unchanged initial mode'
  assert_file_contains "$SKILL" 'coverage gap.*COMMENT' 'skill constrains coverage gaps to COMMENT'
  assert_file_contains "$SKILL" 'Step 6c' 'skill preserves human confirmation'
  assert_file_contains "$SKILL" 'review_plan_validate_decision' 'skill validates the complete closed planner decision'
  assert_file_contains "$REFERENCE" 'kc-pr-flow\.review-delta-receipt/v1' 'runtime reference documents the delta receipt schema'
  assert_file_contains "$REFERENCE" 'kc-pr-flow\.review-plan-decision/v1' 'runtime reference documents the plan decision schema'
  for forbidden in 'gh pr review' 'review-post.sh post' 'authorization.granted' 'human_confirmed'; do
    assert_file_not_contains "$PLAN" "$forbidden" "planner has no posting authority: $forbidden"
  done

  flag_off_trace="$(KC_PR_FLOW_DELTA_FAST_PATH=off skill_router_trace valid-exit-0)"
  valid_router_trace="$(KC_PR_FLOW_DELTA_FAST_PATH=on skill_router_trace valid-exit-0)"
  valid_delta_router_trace="$(KC_PR_FLOW_DELTA_FAST_PATH=on skill_router_trace valid-delta-exit-0)"
  valid_initial_router_trace="$(KC_PR_FLOW_DELTA_FAST_PATH=on skill_router_trace valid-initial-exit-0)"
  failed_router_trace="$(KC_PR_FLOW_DELTA_FAST_PATH=on skill_router_trace valid-prefix-exit-9)"
  malformed_router_trace="$(KC_PR_FLOW_DELTA_FAST_PATH=on skill_router_trace malformed-exit-0)"
  schema_only_router_trace="$(KC_PR_FLOW_DELTA_FAST_PATH=on skill_router_trace schema-only-exit-0)"
  extra_member_router_trace="$(KC_PR_FLOW_DELTA_FAST_PATH=on skill_router_trace extra-member-exit-0)"
  wrong_type_router_trace="$(KC_PR_FLOW_DELTA_FAST_PATH=on skill_router_trace wrong-type-exit-0)"
  assert_match 'complete valid router decision is accepted' '^mode=resolve\|plan=\{.*\}\|ceiling=APPROVE\|reason=ancestor_append,known_finding_delta,trusted_predecessor$' "$valid_router_trace"
  assert_match 'complete valid delta decision is accepted' '^mode=delta\|plan=\{.*\}\|ceiling=COMMENT\|reason=ancestor_append,expanded_delta,trusted_predecessor$' "$valid_delta_router_trace"
  assert_eq 'producer initial retains byte-identical existing flow' "$flag_off_trace" "$valid_initial_router_trace"
  assert_eq 'failed router preserves byte-identical initial trace' "$flag_off_trace" "$failed_router_trace"
  assert_eq 'malformed router preserves byte-identical initial trace' "$flag_off_trace" "$malformed_router_trace"
  assert_eq 'schema-only router preserves byte-identical initial trace' "$flag_off_trace" "$schema_only_router_trace"
  assert_eq 'extra-member router preserves byte-identical initial trace' "$flag_off_trace" "$extra_member_router_trace"
  assert_eq 'wrong-type router preserves byte-identical initial trace' "$flag_off_trace" "$wrong_type_router_trace"
  for semantic_mode in \
    delta-empty-range-exit-0 \
    delta-empty-capabilities-exit-0 \
    delta-approve-ceiling-exit-0 \
    delta-null-ceiling-exit-0 \
    resolve-empty-range-exit-0 \
    resolve-comment-ceiling-exit-0 \
    resolve-wrong-capabilities-exit-0 \
    initial-wrong-reason-exit-0; do
    semantic_trace="$(KC_PR_FLOW_DELTA_FAST_PATH=on skill_router_trace "$semantic_mode")"
    assert_eq "$semantic_mode preserves byte-identical initial trace under set -e" "$flag_off_trace" "$semantic_trace"
  done
  assert_eq 'failed router leaves plan state unset' 'mode=initial|plan=unset|ceiling=unset|reason=unset' "$failed_router_trace"
  assert_eq 'skill router traces preserve planner path' "$HERE/review-plan.sh" "$PLAN"
  for identity_field in repository pr_number base_sha config_hash; do
    live_output="$(skill_router_live_identity_mismatch_trace "$identity_field")"
    live_receipt_rc="$(sed -n '1s/^receipt_rc=//p' <<<"$live_output")"
    live_trace="$(sed '1d' <<<"$live_output")"
    assert_eq "$identity_field mismatch keeps receipt/event replay valid" '0' "$live_receipt_rc"
    assert_eq "$identity_field mismatch preserves byte-identical initial trace under set -e" "$flag_off_trace" "$live_trace"
  done
fi

if [ "$CASE_FILTER" = 'all' ] || [ "$CASE_FILTER" = 'mode-router' ] || [ "$CASE_FILTER" = 'trust-boundary' ] || [ "$CASE_FILTER" = 'worktree-safety' ]; then
  # shellcheck source=/dev/null
  . "$RUNTIME"
  fixture="$HERE/../test/fixtures/review-plan/pr1693-replay.json"
  router_repo="$TEST_ROOT/router-repo"
  replay_lines="$(make_replay_repo "$router_repo" "$fixture")"
  base_sha="$(awk -F= '$1 == "base" { print $2 }' <<<"$replay_lines")"
  reviewed_sha="$(awk -F= '$1 == "reviewed" { print $2 }' <<<"$replay_lines")"
  fixed_sha="$(awk -F= '$1 == "fixed" { print $2 }' <<<"$replay_lines")"
  repo_id="$(jq -r '.repository' "$fixture")"
  config_hash='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
  router_events="$TEST_ROOT/router-events.jsonl"
  router_receipt="$TEST_ROOT/router-receipt.json"
  finding_id="$(make_replay_receipt "$router_repo" "$repo_id" 1693 "$base_sha" "$reviewed_sha" "$config_hash" "$router_events" "$router_receipt")"

  if [ "$CASE_FILTER" = 'all' ] || [ "$CASE_FILTER" = 'mode-router' ]; then
    decision="$(KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide --repo "$repo_id" --pr 1693 --base "$base_sha" --head "$fixed_sha" --config-hash "$config_hash" --repo-worktree "$router_repo" --predecessor-events "$router_events" --delta-receipt "$router_receipt")"
    assert_eq 'PR1693 shape selects resolve' 'resolve' "$(jq -r '.mode' <<<"$decision")"
    assert_eq 'resolve inherits finding IDs' "$finding_id" "$(jq -r '.inherited_finding_ids | join(",")' <<<"$decision")"
    assert_eq 'router is advisory ceiling' 'APPROVE' "$(jq -r '.event_ceiling' <<<"$decision")"
    assert_eq 'decision keys are closed' 'event_ceiling,fallback,identity,inherited_finding_ids,mode,reason_codes,required_capabilities,review_range,schema' "$(jq -r 'keys | sort | join(",")' <<<"$decision")"
    assert_eq 'replay reasons are sorted' 'ancestor_append,known_finding_delta,trusted_predecessor' "$(jq -r '.reason_codes | join(",")' <<<"$decision")"
    assert_eq 'replay capabilities are inherited' 'correctness,test-coverage' "$(jq -r '.required_capabilities | join(",")' <<<"$decision")"
    # One path canonicalization protects the router's small-read latency: Git
    # helpers consume the already validated path rather than spawning Python
    # before every object, ancestry, diff, and show read.
    # shellcheck source=/dev/null
    . "$PLAN"
    original_real_worktree="$(declare -f review_plan_real_worktree)"
    eval "$(declare -f review_plan_real_worktree | sed '1s/review_plan_real_worktree/review_plan_real_worktree_original/')"
    worktree_check_ledger="$TEST_ROOT/worktree-check-ledger"
    : >"$worktree_check_ledger"
    review_plan_real_worktree() {
      printf 'check\n' >>"$worktree_check_ledger"
      review_plan_real_worktree_original "$@"
    }
    direct_decision_file="$TEST_ROOT/direct-decision.json"
    KC_PR_FLOW_DELTA_FAST_PATH=on review_plan_decide "$repo_id" 1693 "$base_sha" "$fixed_sha" "$config_hash" "$router_repo" "$router_events" "$router_receipt" >"$direct_decision_file"
    direct_decision="$(<"$direct_decision_file")"
    assert_eq 'decision canonicalizes worktree once' '1' "$(wc -l <"$worktree_check_ledger" | tr -d ' ')"
    assert_eq 'single-canonicalization direct decision resolves' 'resolve' "$(jq -r '.mode' <<<"$direct_decision")"
    eval "$original_real_worktree"
    mkdir -p "$router_repo/docs"
    printf 'unrelated follow-up\n' >"$router_repo/docs/extra.md"
    git -C "$router_repo" add docs/extra.md
    git -C "$router_repo" commit -qm expanded
    expanded_sha="$(git -C "$router_repo" rev-parse HEAD)"
    expanded_decision="$(KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide --repo "$repo_id" --pr 1693 --base "$base_sha" --head "$expanded_sha" --config-hash "$config_hash" --repo-worktree "$router_repo" --predecessor-events "$router_events" --delta-receipt "$router_receipt")"
    assert_eq 'new unrelated ancestor path selects delta' 'delta' "$(jq -r '.mode' <<<"$expanded_decision")"
    assert_eq 'expanded delta caps only current coverage' 'COMMENT' "$(jq -r '.event_ceiling' <<<"$expanded_decision")"
    flag_off="$(bash "$PLAN" decide --repo "$repo_id" --pr 1693 --base "$base_sha" --head "$fixed_sha" --config-hash "$config_hash" --repo-worktree "$router_repo" --predecessor-events "$router_events" --delta-receipt "$router_receipt")"
    assert_eq 'flag off preserves initial flow' 'initial' "$(jq -r '.mode' <<<"$flag_off")"
    assert_eq 'flag off adds no synthetic ceiling' 'null' "$(jq -r '.event_ceiling' <<<"$flag_off")"
    replacement_receipt="$TEST_ROOT/replacement-receipt.json"
    jq -S -c '.known_findings[0].path="docs/replaced.md" | .content_sha256=("0" * 64)' "$router_receipt" >"$replacement_receipt"
    original_validate_receipt="$(declare -f review_plan_validate_receipt)"
    eval "$(declare -f review_plan_validate_receipt | sed '1s/review_plan_validate_receipt/review_plan_validate_receipt_original/')"
    review_plan_validate_receipt() {
      local result
      review_plan_validate_receipt_original "$@"
      result=$?
      cp "$replacement_receipt" "$router_receipt"
      return "$result"
    }
    replacement_decision_file="$TEST_ROOT/replacement-decision.json"
    KC_PR_FLOW_DELTA_FAST_PATH=on review_plan_decide "$repo_id" 1693 "$base_sha" "$fixed_sha" "$config_hash" "$router_repo" "$router_events" "$router_receipt" >"$replacement_decision_file"
    replacement_decision="$(<"$replacement_decision_file")"
    assert_eq 'receipt replacement after validation preserves snapshot route' 'resolve' "$(jq -r '.mode' <<<"$replacement_decision")"
    eval "$original_validate_receipt"
  fi

  if [ "$CASE_FILTER" = 'all' ] || [ "$CASE_FILTER" = 'trust-boundary' ]; then
    missing="$(KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide --repo "$repo_id" --pr 1693 --base "$base_sha" --head "$fixed_sha" --config-hash "$config_hash" --repo-worktree "$router_repo")"
    assert_eq 'missing predecessor uses initial review' 'initial' "$(jq -r '.mode' <<<"$missing")"
    assert_eq 'missing predecessor has no synthetic ceiling' 'null' "$(jq -r '.event_ceiling' <<<"$missing")"
    changed_base="$(KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide --repo "$repo_id" --pr 1693 --base "$reviewed_sha" --head "$fixed_sha" --config-hash "$config_hash" --repo-worktree "$router_repo" --predecessor-events "$router_events" --delta-receipt "$router_receipt")"
    assert_eq 'changed base uses initial review' 'initial' "$(jq -r '.mode' <<<"$changed_base")"
    changed_config="$(KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide --repo "$repo_id" --pr 1693 --base "$base_sha" --head "$fixed_sha" --config-hash "${config_hash/a/b}" --repo-worktree "$router_repo" --predecessor-events "$router_events" --delta-receipt "$router_receipt")"
    assert_eq 'changed config uses initial review' 'initial' "$(jq -r '.mode' <<<"$changed_config")"
    mutated_receipt="$TEST_ROOT/mutated-receipt.json"
    jq -S -c '.known_findings[0].evidence_sha256=("1" * 64) | .content_sha256=("0" * 64)' "$router_receipt" >"$mutated_receipt"
    mutated_decision="$(KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide --repo "$repo_id" --pr 1693 --base "$base_sha" --head "$fixed_sha" --config-hash "$config_hash" --repo-worktree "$router_repo" --predecessor-events "$router_events" --delta-receipt "$mutated_receipt")"
    assert_eq 'mutated finding evidence uses initial review' 'initial' "$(jq -r '.mode' <<<"$mutated_decision")"
    assert_eq 'mutated finding evidence has no synthetic ceiling' 'null' "$(jq -r '.event_ceiling' <<<"$mutated_decision")"
    inherited_gap="$TEST_ROOT/inherited-gap.json"
    jq -S -c '.coverage_gap_refs=["coverage-gap"] | .content_sha256=("0" * 64)' "$router_receipt" >"$inherited_gap"
    gap_decision="$(KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide --repo "$repo_id" --pr 1693 --base "$base_sha" --head "$fixed_sha" --config-hash "$config_hash" --repo-worktree "$router_repo" --predecessor-events "$router_events" --delta-receipt "$inherited_gap")"
    assert_eq 'untrusted inherited gap uses initial review' 'initial' "$(jq -r '.mode' <<<"$gap_decision")"
    assert_eq 'untrusted inherited gap has no synthetic ceiling' 'null' "$(jq -r '.event_ceiling' <<<"$gap_decision")"
    assert_changed_object_not_resolve() {
      local description="$1" candidate_head="$2" object_decision
      object_decision="$(KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide --repo "$repo_id" --pr 1693 --base "$base_sha" --head "$candidate_head" --config-hash "$config_hash" --repo-worktree "$router_repo" --predecessor-events "$router_events" --delta-receipt "$router_receipt")"
      if [ "$(jq -r '.mode' <<<"$object_decision")" = 'resolve' ]; then
        fail "$description (must not select resolve)"
      else
        pass
      fi
    }
    git -C "$router_repo" checkout -q "$fixed_sha"
    printf '\000binary parser\n' >"$router_repo/src/parser.py"
    git -C "$router_repo" add src/parser.py
    git -C "$router_repo" commit -qm binary-known-path
    binary_sha="$(git -C "$router_repo" rev-parse HEAD)"
    assert_changed_object_not_resolve 'binary known path is not resolve' "$binary_sha"
    git -C "$router_repo" checkout -q "$fixed_sha"
    rm "$router_repo/src/parser.py"
    ln -s parser-target "$router_repo/src/parser.py"
    git -C "$router_repo" add src/parser.py
    git -C "$router_repo" commit -qm symlink-known-path
    symlink_sha="$(git -C "$router_repo" rev-parse HEAD)"
    assert_changed_object_not_resolve 'symlink blob is not resolve' "$symlink_sha"
    git -C "$router_repo" checkout -q "$fixed_sha"
    git -C "$router_repo" rm -q src/parser.py
    git -C "$router_repo" update-index --add --cacheinfo "160000,$reviewed_sha,src/parser.py"
    git -C "$router_repo" commit -qm gitlink-known-path
    gitlink_sha="$(git -C "$router_repo" rev-parse HEAD)"
    assert_changed_object_not_resolve 'gitlink is not resolve' "$gitlink_sha"
    git -C "$router_repo" checkout -q "$fixed_sha"
    cp "$router_repo/src/parser.py" "$router_repo/src/parser-copy.py"
    git -C "$router_repo" add src/parser-copy.py
    git -C "$router_repo" commit -qm copied-parser
    copy_sha="$(git -C "$router_repo" rev-parse HEAD)"
    assert_changed_object_not_resolve 'copy status is not resolve' "$copy_sha"
    git -C "$router_repo" checkout -q "$fixed_sha"
    printf 'unsafe object\n' >"$router_repo/src/unsafe\\object.py"
    git -C "$router_repo" add 'src/unsafe\object.py'
    git -C "$router_repo" commit -qm unsafe-object-path
    unsafe_object_sha="$(git -C "$router_repo" rev-parse HEAD)"
    assert_changed_object_not_resolve 'unsafe changed object path is not resolve' "$unsafe_object_sha"
    git -C "$router_repo" checkout -q --orphan rewritten
    git -C "$router_repo" rm -qr --cached .
    printf 'def parse(value):\n    return None\n' >"$router_repo/src/parser.py"
    git -C "$router_repo" add src/parser.py
    git -C "$router_repo" commit -qm rewritten
    rewritten_sha="$(git -C "$router_repo" rev-parse HEAD)"
    non_ancestor="$(KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide --repo "$repo_id" --pr 1693 --base "$base_sha" --head "$rewritten_sha" --config-hash "$config_hash" --repo-worktree "$router_repo" --predecessor-events "$router_events" --delta-receipt "$router_receipt")"
    assert_eq 'rewritten history uses initial review' 'initial' "$(jq -r '.mode' <<<"$non_ancestor")"
    assert_eq 'rewritten history has no synthetic ceiling' 'null' "$(jq -r '.event_ceiling' <<<"$non_ancestor")"
  fi

  if [ "$CASE_FILTER" = 'all' ] || [ "$CASE_FILTER" = 'worktree-safety' ]; then
    unsafe_file="$TEST_ROOT/not-a-directory"
    unsafe_missing="$TEST_ROOT/missing"
    unsafe_link="$TEST_ROOT/repo-link"
    unsafe_parent="$TEST_ROOT/parent-link"
    printf 'not a directory\n' >"$unsafe_file"
    ln -s "$router_repo" "$unsafe_link"
    ln -s "$TEST_ROOT" "$unsafe_parent"
    mkdir -p "$TEST_ROOT/git-stub"
    git_ledger="$TEST_ROOT/git-ledger"
    : >"$git_ledger"
    printf '#!/bin/sh\nprintf "git\\n" >>"%s"\nexit 97\n' "$git_ledger" >"$TEST_ROOT/git-stub/git"
    chmod +x "$TEST_ROOT/git-stub/git"
    for unsafe in "$unsafe_file" "$unsafe_missing" "$unsafe_link" "$unsafe_parent/router-repo"; do
      unsafe_decision="$(PATH="$TEST_ROOT/git-stub:$PATH" KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide --repo "$repo_id" --pr 1693 --base "$base_sha" --head "$fixed_sha" --config-hash "$config_hash" --repo-worktree "$unsafe" --predecessor-events "$router_events" --delta-receipt "$router_receipt")"
      assert_eq 'unsafe worktree uses initial review' 'initial' "$(jq -r '.mode' <<<"$unsafe_decision")"
      assert_eq 'unsafe worktree has no synthetic ceiling' 'null' "$(jq -r '.event_ceiling' <<<"$unsafe_decision")"
    done
    assert_eq 'unsafe worktrees never invoke git' '' "$(cat "$git_ledger")"
    # shellcheck source=/dev/null
    . "$PLAN"
    assert_eq 'real worktree is canonical absolute path' "$router_repo" "$(review_plan_real_worktree "$router_repo")"
  fi
fi

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
