#!/usr/bin/env bash
# Contract tests for the trusted review delta receipt boundary.
# shellcheck disable=SC2016,SC2030,SC2031,SC2317 # Intentional generated stubs, subshells, and test overrides.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PLAN="$HERE/review-plan.sh"
RUNTIME="$HERE/review-runtime.sh"
TEST_ROOT="$(mktemp -d)"
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
    printf 'usage: %s [--case receipt-contract]\n' "$0" >&2
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
      receipt_out="$(PATH="$STUB_DIR:$PATH" bash "$PLAN" receipt --event-file "$EVENT_FILE" 2>/dev/null)"
      receipt_rc=$?
      assert_eq 'receipt command succeeds for complete replay' '0' "$receipt_rc"
      projection="$(review_runtime_replay "$EVENT_FILE")"
      assert_eq 'receipt schema' 'kc-pr-flow.review-delta-receipt/v1' "$(jq -r '.schema' <<<"$receipt_out")"
      assert_eq 'receipt keys are closed' 'content_sha256,coverage_gap_refs,known_findings,predecessor,required_capabilities,schema' "$(jq -r 'keys | sort | join(",")' <<<"$receipt_out")"
      assert_eq 'all terminal findings remain unresolved' 'unresolved' "$(jq -r '[.known_findings[].resolution_state] | unique | join(",")' <<<"$receipt_out")"
      assert_eq 'finding IDs come from replay' "$(jq -r '.findings | map(.finding_id) | sort | join(",")' <<<"$projection")" "$(jq -r '.known_findings | map(.finding_id) | sort | join(",")' <<<"$receipt_out")"
      validator_err="$TEST_ROOT/validator.err"
      review_plan_validate_receipt "$receipt_out" "$projection" 2>"$validator_err"
      validator_rc=$?
      assert_eq 'receipt validates against fresh projection' '0' "$validator_rc"
      assert_eq 'no transport or model stub was called' '' "$(cat "$CALL_LEDGER")"

      assert_receipt_rejected() {
        local description="$1" candidate_receipt="$2" rejected_rc
        review_plan_validate_receipt "$candidate_receipt" "$projection" >/dev/null 2>&1
        rejected_rc=$?
        assert_not_zero "$description" "$rejected_rc"
      }
      assert_receipt_rejected 'arbitrary receipt_id is rejected' "$(jq -S -c '.predecessor.receipt_id=("0"*64)' <<<"$receipt_out")"
      assert_receipt_rejected 'changed content_sha256 is rejected' "$(jq -S -c '.content_sha256=("0"*64)' <<<"$receipt_out")"
      assert_receipt_rejected 'changed finding_id is rejected' "$(jq -S -c '.known_findings[0].finding_id=("1"*64)' <<<"$receipt_out")"
      assert_receipt_rejected 'extra top-level member is rejected' "$(jq -S -c '.extra_key=true' <<<"$receipt_out")"
      assert_receipt_rejected 'extra predecessor member is rejected' "$(jq -S -c '.predecessor.extra_key=true' <<<"$receipt_out")"
      assert_receipt_rejected 'missing evidence hash is rejected' "$(jq -S -c 'del(.known_findings[0].evidence_sha256)' <<<"$receipt_out")"

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

      oversized_events="$TEST_ROOT/oversized-events.jsonl"
      cp "$EVENT_FILE" "$oversized_events"
      KC_PR_FLOW_MAX_EVENTS_BYTES=1 review_plan_build_receipt "$oversized_events" >/dev/null 2>&1
      assert_not_zero 'oversized event input is rejected' "$?"
    else
      fail 'review-plan.sh exists after RED implementation'
    fi
  fi
fi

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
