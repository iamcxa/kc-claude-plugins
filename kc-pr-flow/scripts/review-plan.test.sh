#!/usr/bin/env bash
# Contract tests for the trusted review delta receipt boundary.
# shellcheck disable=SC2016,SC2030,SC2031,SC2317,SC2329 # Intentional generated stubs, subshells, and test overrides.

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
    printf 'usage: %s [--case receipt-contract|mode-router|trust-boundary|worktree-safety|skill-wiring|event-ceiling]\n' "$0" >&2
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
      assert_eq 'receipt finding keys are closed' \
        'anchor_sha256,category,claim_key,evidence,evidence_sha256,finding_id,path,resolution_state,side' \
        "$(jq -r '.known_findings[0] | keys | sort | join(",")' <<<"$receipt_out")"
      assert_eq 'finding anchor comes from replay' \
        "$(jq -S -c '.findings[0].anchor_sha256' <<<"$projection")" \
        "$(jq -S -c '.known_findings[0].anchor_sha256' <<<"$receipt_out")"
      assert_eq 'finding category comes from replay' \
        "$(jq -S -c '.findings[0].category' <<<"$projection")" \
        "$(jq -S -c '.known_findings[0].category' <<<"$receipt_out")"
      assert_eq 'closed evidence pointer comes from replay' \
        "$(jq -S -c '.findings[0].evidence' <<<"$projection")" \
        "$(jq -S -c '.known_findings[0].evidence' <<<"$receipt_out")"
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

      rehash_receipt() {
        local candidate="$1" canonical hash
        canonical="$(jq -S -c 'del(.content_sha256)' <<<"$candidate")" || return
        hash="$(printf '%s' "$canonical" | review_runtime_sha256)" || return
        jq -S -c --arg hash "$hash" '.content_sha256=$hash' <<<"$candidate"
      }

      missing_anchor_receipt="$(rehash_receipt "$(jq -S -c 'del(.known_findings[0].anchor_sha256)' <<<"$receipt_out")")"
      assert_receipt_rejected 'missing replay-derived anchor is rejected' "$missing_anchor_receipt"

      mutated_evidence_receipt="$(rehash_receipt "$(jq -S -c \
        '.known_findings[0].evidence.content_sha256=("1"*64) |
         .known_findings[0].evidence_sha256=("1"*64)' <<<"$receipt_out")")"
      assert_receipt_rejected 'mutated replay-derived evidence is rejected' "$mutated_evidence_receipt"

      receipt_from_projection() {
        local replay="$1" replay_hash replay_receipt_id canonical hash
        replay_hash="$(printf '%s' "$replay" | jq -S -c . | review_runtime_sha256)" || return
        replay_receipt_id="$(printf '%s' "$(jq -r '.run.run_id + "|" + .run.review_key' <<<"$replay")|$replay_hash" |
          review_runtime_sha256)" || return
        canonical="$(jq -S -c --arg receipt_id "$replay_receipt_id" '
          .run as $run |
          {
            schema:"kc-pr-flow.review-delta-receipt/v1",
            predecessor:{repository:$run.repository,pr_number:$run.pr_number,
              base_sha:$run.base_sha,head_sha:$run.head_sha,config_hash:$run.config_hash,
              review_key:$run.review_key,run_id:$run.run_id,receipt_id:$receipt_id},
            known_findings:(.findings | map({finding_id,claim_key,anchor_sha256,category,evidence,
              evidence_sha256:.evidence.content_sha256,path,side,resolution_state:"unresolved"}) |
              sort_by(.finding_id)),
            required_capabilities:(.lanes | map(.capability) | sort | unique),
            coverage_gap_refs:[]
          }' <<<"$replay")" || return
        hash="$(printf '%s' "$canonical" | review_runtime_sha256)" || return
        jq -S -c --arg hash "$hash" '. + {content_sha256:$hash}' <<<"$canonical"
      }

      receipt_from_events() {
        local events="$1" replay
        replay="$(review_runtime_replay "$events")" || return
        receipt_from_projection "$replay"
      }

      assert_predecessor_state_rejected() {
        local description="$1" events="$2" candidate rc
        review_plan_build_receipt "$events" >/dev/null 2>&1
        rc=$?
        assert_not_zero "$description is rejected by receipt producer" "$rc"
        candidate="$(receipt_from_events "$events")" || {
          fail "$description fixture replays"
          return
        }
        review_plan_validate_receipt "$candidate" "$events" >/dev/null 2>&1
        rc=$?
        assert_not_zero "$description is rejected by receipt validator" "$rc"
      }

      zero_lane_projection="$(jq -S -c '.lanes=[] | .lifecycle.complete=true' <<<"$projection")"
      (
        review_runtime_replay() { printf '%s\n' "$zero_lane_projection"; }
        review_plan_build_receipt "$EVENT_FILE" >/dev/null 2>&1
      )
      assert_not_zero 'zero-lane predecessor is rejected by receipt producer' "$?"

      zero_lane_receipt="$(receipt_from_projection "$zero_lane_projection")"
      (
        review_runtime_replay() { printf '%s\n' "$zero_lane_projection"; }
        review_plan_validate_receipt "$zero_lane_receipt" "$EVENT_FILE" >/dev/null 2>&1
      )
      assert_not_zero 'zero-lane fresh replay is rejected by receipt validator' "$?"

      (
        review_plan_required_capabilities() { printf '%s\n' '[]'; }
        review_plan_build_receipt "$EVENT_FILE" >/dev/null 2>&1
      )
      assert_not_zero 'empty derived required capabilities are rejected by receipt producer' "$?"

      empty_capabilities_receipt="$(rehash_receipt "$(jq -S -c '.required_capabilities=[]' <<<"$receipt_out")")"
      review_plan_validate_receipt "$empty_capabilities_receipt" "$EVENT_FILE" >/dev/null 2>&1
      assert_not_zero 'empty receipt required capabilities are rejected by receipt validator' "$?"

      failed_events="$TEST_ROOT/failed-events.jsonl"
      failed_task="$(jq -S -c '.lane_id="test-coverage-1" | .capability="test-coverage"' <<<"$TASK")"
      failed_started="$(review_runtime_build_event "$RUN_ID" "$REVIEW_KEY" "$REPOSITORY" "$PR_NUMBER" "$HEAD_SHA" "$HEAD_SHA" "$CONFIG_HASH" 2 "$OCCURRED_AT" lane.started "$(jq -S -c -n --argjson value "$failed_task" '{review_task:$value}')")"
      failed_result="$(jq -S -c '.lane_id="test-coverage-1" | .capability="test-coverage" |
        .terminal_status="failed" | .candidates=[]' <<<"$RESULT")"
      failed_finished="$(review_runtime_build_event "$RUN_ID" "$REVIEW_KEY" "$REPOSITORY" "$PR_NUMBER" "$HEAD_SHA" "$HEAD_SHA" "$CONFIG_HASH" 3 "$OCCURRED_AT" lane.finished "$(jq -S -c -n --argjson value "$failed_result" '{lane_result:$value}')")"
      empty_synthesized="$(review_runtime_build_event "$RUN_ID" "$REVIEW_KEY" "$REPOSITORY" "$PR_NUMBER" "$HEAD_SHA" "$HEAD_SHA" "$CONFIG_HASH" 4 "$OCCURRED_AT" synthesis.finished '{"findings":[],"uncertain_candidate_ids":[]}')"
      short_finished="$(review_runtime_build_event "$RUN_ID" "$REVIEW_KEY" "$REPOSITORY" "$PR_NUMBER" "$HEAD_SHA" "$HEAD_SHA" "$CONFIG_HASH" 5 "$OCCURRED_AT" run.finished "$(jq -S -c -n --argjson value "$BEHAVIOR" '{behavior_hashes:$value}')")"
      printf '%s\n' "$START" "$failed_started" "$failed_finished" "$empty_synthesized" "$short_finished" >"$failed_events"
      assert_predecessor_state_rejected 'failed predecessor lane' "$failed_events"

      unavailable_events="$TEST_ROOT/unavailable-events.jsonl"
      unavailable_result="$(jq -S -c '.terminal_status="unavailable"' <<<"$failed_result")"
      unavailable_finished="$(review_runtime_build_event "$RUN_ID" "$REVIEW_KEY" "$REPOSITORY" "$PR_NUMBER" "$HEAD_SHA" "$HEAD_SHA" "$CONFIG_HASH" 3 "$OCCURRED_AT" lane.finished "$(jq -S -c -n --argjson value "$unavailable_result" '{lane_result:$value}')")"
      printf '%s\n' "$START" "$failed_started" "$unavailable_finished" "$empty_synthesized" "$short_finished" >"$unavailable_events"
      assert_predecessor_state_rejected 'unavailable predecessor lane' "$unavailable_events"

      uncertain_events="$TEST_ROOT/uncertain-events.jsonl"
      uncertain_synthesized="$(review_runtime_build_event "$RUN_ID" "$REVIEW_KEY" "$REPOSITORY" "$PR_NUMBER" "$HEAD_SHA" "$HEAD_SHA" "$CONFIG_HASH" 5 "$OCCURRED_AT" synthesis.finished "$(jq -S -c -n --arg candidate "$CANDIDATE_ID" '{findings:[],uncertain_candidate_ids:[$candidate]}')")"
      printf '%s\n' "$START" "$LANE_START" "$OBSERVED" "$LANE_FINISHED" "$uncertain_synthesized" "$FINISHED" >"$uncertain_events"
      assert_predecessor_state_rejected 'uncertain predecessor candidate' "$uncertain_events"

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
  local config_hash="$6" event_file="$7" receipt_file="$8" fixture="$9"
  local finding_meta path side anchor_sha256 category claim_key evidence_kind evidence_line evidence_locator
  local review_key object_sha content_sha run_id pointer merge_key
  local candidate_id candidate task_correctness task_coverage result_correctness result_coverage finding_id finding behavior
  local started correctness_started coverage_started observed correctness_finished coverage_finished synthesized finished

  finding_meta="$(jq -e -S -c '
    def token: type == "string" and test("^[a-z][a-z0-9._-]{0,63}$");
    def sha256: type == "string" and test("^[0-9a-f]{64}$");
    def positive_integer: type == "number" and floor == . and . > 0 and . <= 9007199254740991;
    def safe_path:
      type == "string" and length > 0 and length <= 1024 and
      (startswith("/") | not) and (endswith("/") | not) and
      (contains("//") | not) and
      (test("(^|/)\\.\\.?(/|$)|[[:cntrl:]\\\\]") | not);
    .known_findings |
    select(type == "array" and length == 1) |
    .[0] |
    select((keys | sort) == ["anchor_sha256","category","claim_key","evidence","path","side"]) |
    select((.anchor_sha256 | sha256) and (.category | token) and (.claim_key | token) and
      (.path | safe_path) and (.side == "LEFT" or .side == "RIGHT" or .side == "FILE")) |
    select(.evidence | type == "object" and
      (keys | sort) == ["kind","line","locator"] and
      .kind == "git_blob" and (.line | positive_integer) and (.locator | token))
  ' "$fixture")" || return 2
  path="$(jq -r '.path' <<<"$finding_meta")" || return
  side="$(jq -r '.side' <<<"$finding_meta")" || return
  anchor_sha256="$(jq -r '.anchor_sha256' <<<"$finding_meta")" || return
  category="$(jq -r '.category' <<<"$finding_meta")" || return
  claim_key="$(jq -r '.claim_key' <<<"$finding_meta")" || return
  evidence_kind="$(jq -r '.evidence.kind' <<<"$finding_meta")" || return
  evidence_line="$(jq -r '.evidence.line' <<<"$finding_meta")" || return
  evidence_locator="$(jq -r '.evidence.locator' <<<"$finding_meta")" || return
  if [ "$side" = 'LEFT' ]; then object_sha="$base_sha"; else object_sha="$reviewed_sha"; fi
  review_key="$(sha256_text "$repository|$pr_number|$base_sha|$reviewed_sha|$config_hash")"
  content_sha="$(git -C "$fixture_repo" show "$object_sha:$path" | review_runtime_sha256)" || return
  run_id='run-pr1693-replay'
  pointer="$(jq -S -c -n --arg key "$review_key" --arg repo "$repository" --arg base "$base_sha" \
    --arg head "$reviewed_sha" --arg object "$object_sha" --arg path "$path" --arg side "$side" \
    --arg kind "$evidence_kind" --arg locator "$evidence_locator" --arg hash "$content_sha" \
    --argjson line "$evidence_line" \
    '{schema:"kc-pr-flow.evidence-pointer/v1",kind:$kind,review_key:$key,repository:$repo,
      base_sha:$base,head_sha:$head,object_sha:$object,path:$path,side:$side,line:$line,
      locator:$locator,content_sha256:$hash}')"
  candidate_id="$(review_runtime_candidate_id "$run_id" correctness-1 1 "$content_sha")"
  candidate="$(jq -S -c -n --arg id "$candidate_id" --arg key "$review_key" --arg run "$run_id" \
    --arg path "$path" --arg side "$side" --arg anchor "$anchor_sha256" \
    --arg category "$category" --arg claim "$claim_key" --argjson evidence "$pointer" \
    '{schema:"kc-pr-flow.review-candidate/v1",candidate_id:$id,run_id:$run,review_key:$key,
      lane_id:"correctness-1",ordinal:1,path:$path,side:$side,anchor_sha256:$anchor,
      category:$category,claim_key:$claim,evidence:$evidence}')"
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
  merge_key="$path|$side|$content_sha|$category|$claim_key"
  finding_id="$(review_runtime_finding_id "$review_key" "$merge_key")"
  finding="$(jq -S -c -n --arg id "$finding_id" --arg key "$review_key" \
    --arg merge "$merge_key" --arg candidate "$candidate_id" --arg path "$path" --arg side "$side" \
    --arg anchor "$anchor_sha256" --arg category "$category" --arg claim "$claim_key" \
    --argjson evidence "$pointer" \
    '{schema:"kc-pr-flow.review-finding/v1",finding_id:$id,review_key:$key,merge_key:$merge,
      path:$path,side:$side,anchor_sha256:$anchor,category:$category,claim_key:$claim,
      candidate_ids:[$candidate],evidence:$evidence}')"
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
    while IFS= read -r path; do
      mkdir -p "$fixture_repo/$(dirname "$path")"
      jq -j --arg name "$name" --arg path "$path" \
        '.commits[] | select(.name == $name) | .files[$path]' "$fixture" >"$fixture_repo/$path"
    done < <(jq -r --arg name "$name" '.commits[] | select(.name == $name) | .files | keys[]' "$fixture")
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

skill_interactive_snippet() {
  sed -n '/^# typed-interactive-recipe:start$/,/^# typed-interactive-recipe:end$/p' "$SKILL" |
    sed '1d;$d'
}

event_plan_decision() {
  local mode="$1" ceiling="$2" head_sha="${3:-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb}"
  local review_key reason from_sha capabilities inherited fallback_initial
  review_key="$(sha256_text "acme/widgets|1693|aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa|$head_sha|cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc")"
  case "$mode" in
    initial)
      reason='["missing_predecessor"]'
      from_sha=null
      capabilities='[]'
      inherited='[]'
      fallback_initial=true
      ;;
    delta)
      reason='["ancestor_append","expanded_delta","trusted_predecessor"]'
      from_sha='"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"'
      capabilities='["correctness"]'
      inherited='["dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"]'
      fallback_initial=false
      ;;
    *) return 2 ;;
  esac
  jq -S -c -n --arg key "$review_key" --arg mode "$mode" --arg head "$head_sha" \
    --argjson reason "$reason" --argjson from "$from_sha" --argjson capabilities "$capabilities" \
    --argjson inherited "$inherited" --argjson ceiling "$ceiling" \
    --argjson fallback_initial "$fallback_initial" '
    {schema:"kc-pr-flow.review-plan-decision/v1",
      identity:{repository:"acme/widgets",pr_number:1693,
        base_sha:"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",head_sha:$head,
        config_hash:"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        review_key:$key},mode:$mode,reason_codes:$reason,
      review_range:{from_exclusive:$from,to_inclusive:$head},
      inherited_finding_ids:$inherited,required_capabilities:$capabilities,
      event_ceiling:$ceiling,
      fallback:{router_advisory:true,requires_existing_initial_review:$fallback_initial,
        final_verdict_authority:"existing-review-runtime"}}'
}

event_ceiling_case_status() {
  local sequence="$1" flag_after="$2" mutation="$3" seam="$4" requested_event="$5"
  local entry_flag="${6:-on}" optional_inputs="${7:-defined}"
  local plugin_root router_snippet interactive_snippet entry_plan rerun_plan script output
  plugin_root="$TEST_ROOT/event-ceiling-$sequence-$entry_flag-$flag_after-$optional_inputs-$mutation-$seam-$requested_event"
  mkdir -p "$plugin_root/scripts"
  case "$sequence" in
    initial)
      entry_plan="$(event_plan_decision initial null)"
      rerun_plan="$entry_plan"
      ;;
    initial-then-delta)
      entry_plan="$(event_plan_decision initial null)"
      rerun_plan="$(event_plan_decision delta '"COMMENT"')"
      ;;
    delta)
      entry_plan="$(event_plan_decision delta '"COMMENT"')"
      rerun_plan="$entry_plan"
      ;;
    delta-then-stale)
      entry_plan="$(event_plan_decision delta '"COMMENT"')"
      rerun_plan="$(jq -S -c '.required_capabilities=["correctness","security"]' <<<"$entry_plan")"
      ;;
    *) return 2 ;;
  esac
  printf '%s\n' "$entry_plan" >"$plugin_root/scripts/entry.json"
  printf '%s\n' "$rerun_plan" >"$plugin_root/scripts/rerun.json"
  {
    printf '%s\n' '#!/usr/bin/env bash'
    printf 'source %q\n' "$PLAN"
    printf '%s\n' 'review_plan_validate_decision() { return 0; }'
    printf '%s\n' 'if [ "${1:-}" = decide ]; then'
    printf '%s\n' '  count_file="$(dirname "$0")/count"'
    printf '%s\n' '  count=0; [ ! -f "$count_file" ] || count="$(cat "$count_file")"'
    printf '%s\n' '  count=$((count + 1)); printf "%s\n" "$count" >"$count_file"'
    printf '%s\n' '  if [ "$count" -eq 1 ]; then cat "$(dirname "$0")/entry.json"; else cat "$(dirname "$0")/rerun.json"; fi'
    printf '%s\n' '  exit 0'
    printf '%s\n' 'fi'
  } >"$plugin_root/scripts/review-plan.sh"
  chmod 0700 "$plugin_root/scripts/review-plan.sh"
  cat >"$plugin_root/scripts/typed-approve.sh" <<'MOCK'
#!/usr/bin/env bash
printf '%s\n' '{"approve_eligible":true,"capabilities":[],"capability_gap_refs":[],"confirmation_input":{"blocker_refs":[],"coverage_summary":"typed-derived","gap_refs":[],"identity_summary":"typed-derived","verdict_summary":"typed-derived"},"confirmed_blocker_refs":[],"coverage":"complete","effective_event":"APPROVE","mode":"typed","review_identity":{"base_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","config_hash":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","head_sha":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","pr_number":1693,"repository":"acme/widgets","review_key":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","run_id":"run-typed"},"schema":"kc-pr-flow.interactive-collation-decision/v1"}'
MOCK
  chmod 0700 "$plugin_root/scripts/typed-approve.sh"
  router_snippet="$(skill_router_snippet)"
  interactive_snippet="$(skill_interactive_snippet)"
  script="$plugin_root/run.sh"
  {
    printf '%s\n' 'set -u'
    printf '%s\n' 'REPO=acme/widgets'
    printf '%s\n' 'PR_NUMBER=1693'
    printf '%s\n' 'BASE_SHA=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    printf '%s\n' 'REVIEWED_HEAD_SHA=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
    printf '%s\n' 'CONFIG_HASH=cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc'
    printf '%s\n' 'REPO_WORKTREE=/tmp/repo'
    case "$optional_inputs" in
      defined)
        printf '%s\n' 'PREDECESSOR_EVENTS=/tmp/events.jsonl'
        printf '%s\n' 'DELTA_RECEIPT=/tmp/receipt.json'
        ;;
      unset)
        printf '%s\n' 'unset PREDECESSOR_EVENTS DELTA_RECEIPT'
        ;;
      *) return 2 ;;
    esac
    printf 'CLAUDE_PLUGIN_ROOT=%q\n' "$plugin_root"
    case "$entry_flag" in
      on) printf '%s\n' 'KC_PR_FLOW_DELTA_FAST_PATH=on' ;;
      off) printf '%s\n' 'KC_PR_FLOW_DELTA_FAST_PATH=off' ;;
      unset) printf '%s\n' 'unset KC_PR_FLOW_DELTA_FAST_PATH' ;;
      *) return 2 ;;
    esac
    printf '%s\n' "$router_snippet"
    case "$flag_after" in
      on) printf '%s\n' 'KC_PR_FLOW_DELTA_FAST_PATH=on' ;;
      off) printf '%s\n' 'KC_PR_FLOW_DELTA_FAST_PATH=off' ;;
      unset) printf '%s\n' 'unset KC_PR_FLOW_DELTA_FAST_PATH' ;;
      *) return 2 ;;
    esac
    case "$mutation" in
      none) ;;
      missing) printf '%s\n' 'unset PLAN_JSON' ;;
      mutated) printf '%s\n' 'PLAN_JSON="$(jq -S -c '\''.reason_codes += ["tampered"]'\'' <<<"$PLAN_JSON")"' ;;
      identity) printf '%s\n' 'PLAN_JSON="$(jq -S -c '\''.identity.head_sha="9999999999999999999999999999999999999999"'\'' <<<"$PLAN_JSON")"' ;;
      *) return 2 ;;
    esac
    printf '%s\n' "$interactive_snippet"
    printf '%s\n' 'identity='\''{"base_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","config_hash":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","head_sha":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","pr_number":1693,"repository":"acme/widgets","review_key":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","run_id":"run-typed"}'\'''
    printf '%s\n' 'status=0'
    printf '%s\n' 'result='\'''\'''
    case "$seam" in
      direct)
        printf 'review_plan_event_allowed %q >/dev/null 2>&1 || status=$?\n' "$requested_event"
        ;;
      legacy-edit)
        printf '%s\n' 'confirmation="$(review_interactive_prepare_confirmation legacy COMMENT null null true)" || status=$?'
        printf 'if [ "$status" -eq 0 ]; then review_interactive_apply_event_edit "$confirmation" %q >/dev/null 2>&1 || status=$?; fi\n' "$requested_event"
        ;;
      typed-present)
        printf 'review_interactive_prepare_confirmation typed COMMENT "$identity" null %q >/dev/null 2>&1 || status=$?\n' "$plugin_root/scripts/typed-approve.sh"
        ;;
      typed-invalid-identity)
        printf '%s\n' 'result="$(review_interactive_prepare_confirmation typed COMMENT null null true)" || status=$?'
        ;;
      confirmed)
        printf '%s\n' 'confirmation="$(review_interactive_prepare_confirmation legacy COMMENT null null true)" || status=$?'
        printf 'if [ "$status" -eq 0 ]; then review_interactive_confirm_post "$confirmation" %q confirmed >/dev/null 2>&1 || status=$?; fi\n' "$requested_event"
        ;;
      interactive-pre-post)
        printf '%s\n' 'confirmation="$(review_interactive_prepare_confirmation legacy COMMENT null null true)" || status=$?'
        printf '%s\n' 'gate="$(review_interactive_confirm_post "$confirmation" COMMENT confirmed)" || status=$?'
        printf 'if [ "$status" -eq 0 ]; then gate="$(jq -S -c --arg event %q '\''.effective_event=$event | .confirmation.effective_event=$event'\'' <<<"$gate")"; review_interactive_post_gate_valid "$gate" >/dev/null 2>&1 || status=$?; fi\n' "$requested_event"
        ;;
      autonomous)
        printf 'review_autonomous_post_gate "$(printf '\''d%%0.s'\'' {1..64})" "$(printf '\''b%%0.s'\'' {1..40})" %q daemon >/dev/null 2>&1 || status=$?\n' "$requested_event"
        ;;
      autonomous-pre-post)
        printf '%s\n' 'gate="$(review_autonomous_post_gate "$(printf '\''d%0.s'\'' {1..64})" "$(printf '\''b%0.s'\'' {1..40})" COMMENT daemon)" || status=$?'
        printf 'if [ "$status" -eq 0 ]; then gate="$(jq -S -c --arg event %q '\''.effective_event=$event'\'' <<<"$gate")"; review_autonomous_post_gate_valid "$gate" >/dev/null 2>&1 || status=$?; fi\n' "$requested_event"
        ;;
      *) return 2 ;;
    esac
    if [ "$seam" = typed-invalid-identity ]; then
      printf '%s\n' 'printf "%s|%s\n" "$status" "$result"'
    else
      printf '%s\n' 'printf "%s\n" "$status"'
    fi
  } >"$script"
  output="$("$BASH" "$script" 2>/dev/null)"
  printf '%s' "$output"
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
    printf '%s\n' 'review_plan_worktree_binding() { printf "%s\\n" '\''{"device":1,"inode":1,"path":"/tmp/repo"}'\''; }'
    printf '%s\n' 'review_plan_git_identity_valid() { return 0; }'
    printf '%s\n' 'review_plan_ancestor() { return 0; }'
    printf 'review_plan_route_delta() { jq -S -c '\''{classification:.mode,required_capabilities:[]}'\'' %q; }\n' \
      "$plugin_root/scripts/review-plan.sh.decision"
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
    "$receipt_config" "$events" "$receipt" "$fixture" >/dev/null
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
  assert_eq 'producer initial retains planner-state parity' "$flag_off_trace" "$valid_initial_router_trace"
  assert_eq 'failed router preserves planner-state parity' "$flag_off_trace" "$failed_router_trace"
  assert_eq 'malformed router preserves planner-state parity' "$flag_off_trace" "$malformed_router_trace"
  assert_eq 'schema-only router preserves planner-state parity' "$flag_off_trace" "$schema_only_router_trace"
  assert_eq 'extra-member router preserves planner-state parity' "$flag_off_trace" "$extra_member_router_trace"
  assert_eq 'wrong-type router preserves planner-state parity' "$flag_off_trace" "$wrong_type_router_trace"
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
    assert_eq "$semantic_mode preserves planner-state parity under set -e" "$flag_off_trace" "$semantic_trace"
  done
  assert_eq 'failed router leaves plan state unset' 'mode=initial|plan=unset|ceiling=unset|reason=unset' "$failed_router_trace"
  assert_eq 'skill router traces preserve planner path' "$HERE/review-plan.sh" "$PLAN"
  for identity_field in repository pr_number base_sha config_hash; do
    live_output="$(skill_router_live_identity_mismatch_trace "$identity_field")"
    live_receipt_rc="$(sed -n '1s/^receipt_rc=//p' <<<"$live_output")"
    live_trace="$(sed '1d' <<<"$live_output")"
    assert_eq "$identity_field mismatch keeps receipt/event replay valid" '0' "$live_receipt_rc"
    assert_eq "$identity_field mismatch preserves planner-state parity under set -e" "$flag_off_trace" "$live_trace"
  done
fi

if [ "$CASE_FILTER" = 'all' ] || [ "$CASE_FILTER" = 'event-ceiling' ]; then
  assert_eq 'flag-off before engagement preserves legacy APPROVE' '0' \
    "$(event_ceiling_case_status initial off none direct APPROVE off unset)"
  assert_eq 'flag-on missing optional inputs preserves fresh initial legacy APPROVE' '0' \
    "$(event_ceiling_case_status initial on none direct APPROVE on unset)"
  assert_eq 'fresh initial under flag-on preserves legacy APPROVE' '0' \
    "$(event_ceiling_case_status initial on none direct APPROVE)"
  assert_not_zero 'no-engagement delta rerun blocks legacy authority' \
    "$(event_ceiling_case_status initial-then-delta on none direct COMMENT)"

  assert_eq 'engaged COMMENT ceiling permits COMMENT after flag loss' '0' \
    "$(event_ceiling_case_status delta off none direct COMMENT)"
  assert_eq 'engaged COMMENT ceiling permits REQUEST_CHANGES after flag unexport' '0' \
    "$(event_ceiling_case_status delta unset none direct REQUEST_CHANGES)"
  assert_not_zero 'engaged COMMENT ceiling blocks APPROVE after flag loss' \
    "$(event_ceiling_case_status delta off none direct APPROVE)"
  assert_not_zero 'engaged COMMENT ceiling blocks APPROVE after flag unexport' \
    "$(event_ceiling_case_status delta unset none direct APPROVE)"
  assert_not_zero 'missing engaged plan blocks authority' \
    "$(event_ceiling_case_status delta off missing direct COMMENT)"
  assert_not_zero 'mutated engaged plan blocks authority' \
    "$(event_ceiling_case_status delta off mutated direct COMMENT)"
  assert_not_zero 'identity-mismatched engaged plan blocks authority' \
    "$(event_ceiling_case_status delta off identity direct COMMENT)"
  assert_not_zero 'stale engaged plan blocks authority' \
    "$(event_ceiling_case_status delta-then-stale on none direct COMMENT)"

  assert_not_zero 'legacy event edit cannot escalate COMMENT plan to APPROVE' \
    "$(event_ceiling_case_status delta on none legacy-edit APPROVE)"
  assert_not_zero 'typed effective event cannot escalate COMMENT plan to APPROVE' \
    "$(event_ceiling_case_status delta on none typed-present APPROVE)"
  assert_not_zero 'confirmed gate cannot escalate COMMENT plan to APPROVE' \
    "$(event_ceiling_case_status delta on none confirmed APPROVE)"
  assert_not_zero 'interactive immediate-pre-post gate rechecks COMMENT ceiling' \
    "$(event_ceiling_case_status delta on none interactive-pre-post APPROVE)"
  assert_not_zero 'autonomous gate cannot escalate COMMENT plan to APPROVE' \
    "$(event_ceiling_case_status delta on none autonomous APPROVE)"
  assert_not_zero 'autonomous immediate-pre-post gate rechecks COMMENT ceiling' \
    "$(event_ceiling_case_status delta on none autonomous-pre-post APPROVE)"

  for invalid_plan_case in missing mutated identity stale; do
    case "$invalid_plan_case" in
      stale)
        invalid_plan_trace="$(event_ceiling_case_status delta-then-stale on none typed-invalid-identity COMMENT)"
        ;;
      *)
        invalid_plan_trace="$(event_ceiling_case_status delta on "$invalid_plan_case" typed-invalid-identity COMMENT)"
        ;;
    esac
    invalid_plan_status="${invalid_plan_trace%%|*}"
    invalid_plan_payload="${invalid_plan_trace#*|}"
    assert_not_zero "typed invalid identity with $invalid_plan_case plan fails closed at presentation" \
      "$invalid_plan_status"
    assert_eq "typed invalid identity with $invalid_plan_case plan emits no confirmation" '' \
      "$invalid_plan_payload"
  done
fi

if [ "$CASE_FILTER" = 'all' ] || [ "$CASE_FILTER" = 'mode-router' ] || [ "$CASE_FILTER" = 'trust-boundary' ] || [ "$CASE_FILTER" = 'worktree-safety' ]; then
  # shellcheck source=/dev/null
  . "$RUNTIME"
  # shellcheck source=/dev/null
  . "$PLAN"
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
  finding_id="$(make_replay_receipt "$router_repo" "$repo_id" 1693 "$base_sha" "$reviewed_sha" "$config_hash" "$router_events" "$router_receipt" "$fixture")"

  if [ "$CASE_FILTER" = 'all' ] || [ "$CASE_FILTER" = 'mode-router' ]; then
    fixture_finding="$(jq -S -c '.known_findings[0]' "$fixture")"
    receipt_fixture_finding="$(jq -S -c '.known_findings[0] | {
      anchor_sha256,category,claim_key,
      evidence:{kind:.evidence.kind,line:.evidence.line,locator:.evidence.locator},path,side
    }' "$router_receipt")"
    assert_eq 'PR1693 receipt finding metadata comes from fixture' "$fixture_finding" "$receipt_fixture_finding"

    invalid_metadata_fixture="$TEST_ROOT/pr1693-invalid-metadata.json"
    jq -S '.known_findings[0].unexpected=true' "$fixture" >"$invalid_metadata_fixture"
    make_replay_receipt "$router_repo" "$repo_id" 1693 "$base_sha" "$reviewed_sha" "$config_hash" \
      "$TEST_ROOT/invalid-metadata-events.jsonl" "$TEST_ROOT/invalid-metadata-receipt.json" \
      "$invalid_metadata_fixture" >/dev/null 2>&1
    assert_not_zero 'PR1693 fixture finding metadata rejects extra members' "$?"

    mutated_metadata_fixture="$TEST_ROOT/pr1693-mutated-metadata.json"
    jq -S '
      .known_findings[0].anchor_sha256=("f"*64) |
      .known_findings[0].category="security" |
      .known_findings[0].claim_key="mutated-empty-input-contract" |
      .known_findings[0].evidence.line=2 |
      .known_findings[0].evidence.locator="mutated-parser-anchor"
    ' "$fixture" >"$mutated_metadata_fixture"
    mutated_metadata_events="$TEST_ROOT/mutated-metadata-events.jsonl"
    mutated_metadata_receipt="$TEST_ROOT/mutated-metadata-receipt.json"
    make_replay_receipt "$router_repo" "$repo_id" 1693 "$base_sha" "$reviewed_sha" "$config_hash" \
      "$mutated_metadata_events" "$mutated_metadata_receipt" "$mutated_metadata_fixture" >/dev/null
    assert_eq 'mutated fixture receipt validates against fresh replay' '0' "$?"
    mutated_fixture_finding="$(jq -S -c '.known_findings[0]' "$mutated_metadata_fixture")"
    mutated_receipt_finding="$(jq -S -c '.known_findings[0] | {
      anchor_sha256,category,claim_key,
      evidence:{kind:.evidence.kind,line:.evidence.line,locator:.evidence.locator},path,side
    }' "$mutated_metadata_receipt")"
    assert_eq 'mutated fixture metadata changes generated receipt' "$mutated_fixture_finding" "$mutated_receipt_finding"
    review_plan_validate_receipt "$(cat "$mutated_metadata_receipt")" "$mutated_metadata_events" >/dev/null 2>&1
    assert_eq 'mutated fixture receipt remains replay-valid' '0' "$?"

    decision="$(KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide --repo "$repo_id" --pr 1693 --base "$base_sha" --head "$fixed_sha" --config-hash "$config_hash" --repo-worktree "$router_repo" --predecessor-events "$router_events" --delta-receipt "$router_receipt")"
    assert_eq 'PR1693 shape selects resolve' 'resolve' "$(jq -r '.mode' <<<"$decision")"
    assert_eq 'resolve inherits finding IDs' "$finding_id" "$(jq -r '.inherited_finding_ids | join(",")' <<<"$decision")"
    assert_eq 'router is advisory ceiling' 'APPROVE' "$(jq -r '.event_ceiling' <<<"$decision")"
    assert_eq 'decision keys are closed' 'event_ceiling,fallback,identity,inherited_finding_ids,mode,reason_codes,required_capabilities,review_range,schema' "$(jq -r 'keys | sort | join(",")' <<<"$decision")"
    assert_eq 'replay reasons are sorted' 'ancestor_append,known_finding_delta,trusted_predecessor' "$(jq -r '.reason_codes | join(",")' <<<"$decision")"
    assert_eq 'replay capabilities are inherited' 'correctness,test-coverage' "$(jq -r '.required_capabilities | join(",")' <<<"$decision")"
    # shellcheck source=/dev/null
    . "$PLAN"
    original_worktree_adapter="$(declare -f review_plan_worktree_adapter)"
    eval "$(declare -f review_plan_worktree_adapter | sed '1s/review_plan_worktree_adapter/review_plan_worktree_adapter_original/')"
    worktree_bind_ledger="$TEST_ROOT/worktree-bind-ledger"
    git_call_ledger="$TEST_ROOT/git-call-ledger"
    : >"$worktree_bind_ledger"
    : >"$git_call_ledger"
    review_plan_worktree_adapter() {
      if [ "$1" = 'bind' ]; then
        printf 'bind\n' >>"$worktree_bind_ledger"
      elif [ "$1" = 'git' ]; then
        printf 'git\n' >>"$git_call_ledger"
      fi
      review_plan_worktree_adapter_original "$@"
    }
    direct_decision_file="$TEST_ROOT/direct-decision.json"
    KC_PR_FLOW_DELTA_FAST_PATH=on review_plan_decide "$repo_id" 1693 "$base_sha" "$fixed_sha" "$config_hash" "$router_repo" "$router_events" "$router_receipt" >"$direct_decision_file"
    direct_decision="$(<"$direct_decision_file")"
    worktree_bind_count="$(wc -l <"$worktree_bind_ledger" | tr -d ' ')"
    git_call_count="$(wc -l <"$git_call_ledger" | tr -d ' ')"
    assert_eq 'decision binds the worktree identity once' '1' "$worktree_bind_count"
    if [ "$git_call_count" -gt 1 ]; then pass; else fail 'router exercises more than one fd-gated Git invocation'; fi
    assert_eq 'per-operation fd validation still resolves mapped hunks' 'resolve' "$(jq -r '.mode' <<<"$direct_decision")"
    eval "$original_worktree_adapter"

    decide_candidate() {
      KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide --repo "$repo_id" --pr 1693 \
        --base "$base_sha" --head "$1" --config-hash "$config_hash" \
        --repo-worktree "$router_repo" --predecessor-events "$router_events" \
        --delta-receipt "$router_receipt"
    }

    decide_signal_replay() {
      local name="$1" signal_fixture signal_repo signal_lines signal_base signal_reviewed signal_fixed
      local signal_events signal_receipt
      signal_fixture="$TEST_ROOT/$name-fixture.json"
      signal_repo="$TEST_ROOT/$name-repo"
      signal_events="$TEST_ROOT/$name-events.jsonl"
      signal_receipt="$TEST_ROOT/$name-receipt.json"
      jq -S --arg name "$name" '.signal_replays[] | select(.name == $name) | .fixture' \
        "$fixture" >"$signal_fixture"
      signal_lines="$(make_replay_repo "$signal_repo" "$signal_fixture")"
      signal_base="$(awk -F= '$1 == "base" { print $2 }' <<<"$signal_lines")"
      signal_reviewed="$(awk -F= '$1 == "reviewed" { print $2 }' <<<"$signal_lines")"
      signal_fixed="$(awk -F= '$1 == "fixed" { print $2 }' <<<"$signal_lines")"
      make_replay_receipt "$signal_repo" "$repo_id" 1693 "$signal_base" "$signal_reviewed" "$config_hash" \
        "$signal_events" "$signal_receipt" "$signal_fixture" >/dev/null
      KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide --repo "$repo_id" --pr 1693 \
        --base "$signal_base" --head "$signal_fixed" --config-hash "$config_hash" \
        --repo-worktree "$signal_repo" --predecessor-events "$signal_events" \
        --delta-receipt "$signal_receipt"
    }

    security_policy_decision="$(decide_signal_replay security-policy-correctness)"
    assert_eq 'security and policy paths cannot borrow a correctness mapping' 'delta' \
      "$(jq -r '.mode' <<<"$security_policy_decision")"
    assert_eq 'security and policy paths require security coverage' 'security' \
      "$(jq -r '.required_capabilities | map(select(. == "security")) | join(",")' <<<"$security_policy_decision")"

    uv_lock_decision="$(decide_signal_replay uv-lock-correctness)"
    assert_eq 'uv.lock cannot borrow a correctness mapping' 'delta' "$(jq -r '.mode' <<<"$uv_lock_decision")"
    assert_eq 'uv.lock requires supply-chain coverage' 'supply-chain' \
      "$(jq -r '.required_capabilities | map(select(. == "supply-chain")) | join(",")' <<<"$uv_lock_decision")"

    mapped_security_decision="$(decide_signal_replay mapped-security)"
    assert_eq 'same-hunk security finding maps a security signal' 'resolve' \
      "$(jq -r '.mode' <<<"$mapped_security_decision")"
    assert_eq 'mapped security retains the inherited ceiling' 'APPROVE' \
      "$(jq -r '.event_ceiling' <<<"$mapped_security_decision")"

    git -C "$router_repo" checkout -q "$fixed_sha"
    printf '\ndef unrelated_append():\n    return "ordinary"\n' >>"$router_repo/src/parser.py"
    git -C "$router_repo" add src/parser.py
    git -C "$router_repo" commit -qm same-known-file-unrelated-hunk
    unrelated_hunk_sha="$(git -C "$router_repo" rev-parse HEAD)"
    unrelated_hunk_decision="$(decide_candidate "$unrelated_hunk_sha")"
    assert_eq 'two hunks in one known file do not share finding authority' 'delta' "$(jq -r '.mode' <<<"$unrelated_hunk_decision")"
    assert_eq 'ordinary unrelated append is capped' 'COMMENT' "$(jq -r '.event_ceiling' <<<"$unrelated_hunk_decision")"

    git -C "$router_repo" checkout -q "$fixed_sha"
    printf '\ndef unrelated_authorization_bypass():\n    return True\n' >>"$router_repo/src/parser.py"
    git -C "$router_repo" add src/parser.py
    git -C "$router_repo" commit -qm same-known-file-security-hunk
    security_hunk_sha="$(git -C "$router_repo" rev-parse HEAD)"
    security_hunk_decision="$(decide_candidate "$security_hunk_sha")"
    assert_eq 'authorization bypass append cannot resolve' 'delta' "$(jq -r '.mode' <<<"$security_hunk_decision")"
    assert_eq 'security-shaped append requires security coverage' 'security' \
      "$(jq -r '.required_capabilities | map(select(. == "security")) | join(",")' <<<"$security_hunk_decision")"
    review_plan_validate_decision "$security_hunk_decision" "$repo_id" 1693 "$base_sha" "$security_hunk_sha" \
      "$config_hash" "$router_events" "$router_receipt" "$router_repo"
    assert_eq 'security delta validates against fresh hunk routing' '0' "$?"

    git -C "$router_repo" checkout -q "$fixed_sha"
    printf '\ndef test_unrelated_behavior():\n    assert True\n' >>"$router_repo/tests/test_parser.py"
    git -C "$router_repo" add tests/test_parser.py
    git -C "$router_repo" commit -qm test-hunk-without-reference
    unreferenced_test_sha="$(git -C "$router_repo" rev-parse HEAD)"
    unreferenced_test_decision="$(decide_candidate "$unreferenced_test_sha")"
    assert_eq 'file-level import cannot map an unrelated test hunk' 'delta' "$(jq -r '.mode' <<<"$unreferenced_test_decision")"

    git -C "$router_repo" checkout -q "$fixed_sha"
    printf '{"dependencies":{"left-pad":"1.3.0"}}\n' >"$router_repo/package.json"
    git -C "$router_repo" add package.json
    git -C "$router_repo" commit -qm dependency-signal
    dependency_sha="$(git -C "$router_repo" rev-parse HEAD)"
    dependency_decision="$(decide_candidate "$dependency_sha")"
    assert_eq 'dependency signal uses expanded delta' 'delta' "$(jq -r '.mode' <<<"$dependency_decision")"
    assert_eq 'dependency signal requires supply-chain coverage' 'supply-chain' \
      "$(jq -r '.required_capabilities | map(select(. == "supply-chain")) | join(",")' <<<"$dependency_decision")"
    review_plan_validate_decision "$dependency_decision" "$repo_id" 1693 "$base_sha" "$dependency_sha" \
      "$config_hash" "$router_events" "$router_receipt" "$router_repo"
    assert_eq 'dependency delta validates against fresh hunk routing' '0' "$?"

    git -C "$router_repo" checkout -q "$fixed_sha"
    mkdir -p "$router_repo/.github/workflows"
    printf 'name: ci\non: push\njobs: {}\n' >"$router_repo/.github/workflows/ci.yml"
    git -C "$router_repo" add .github/workflows/ci.yml
    git -C "$router_repo" commit -qm workflow-signal
    workflow_sha="$(git -C "$router_repo" rev-parse HEAD)"
    workflow_decision="$(decide_candidate "$workflow_sha")"
    assert_eq 'workflow signal uses expanded delta' 'delta' "$(jq -r '.mode' <<<"$workflow_decision")"
    assert_eq 'workflow signal requires GitHub Actions coverage' 'github-actions' \
      "$(jq -r '.required_capabilities | map(select(. == "github-actions")) | join(",")' <<<"$workflow_decision")"
    review_plan_validate_decision "$workflow_decision" "$repo_id" 1693 "$base_sha" "$workflow_sha" \
      "$config_hash" "$router_events" "$router_receipt" "$router_repo"
    assert_eq 'workflow delta validates against fresh hunk routing' '0' "$?"

    git -C "$router_repo" checkout -q "$fixed_sha"
    mkdir -p "$router_repo/.github/workflows"
    printf '{"unknown":"workflow-shape"}\n' >"$router_repo/.github/workflows/ci.json"
    git -C "$router_repo" add .github/workflows/ci.json
    git -C "$router_repo" commit -qm unclassifiable-workflow-signal
    unclassifiable_workflow_sha="$(git -C "$router_repo" rev-parse HEAD)"
    unclassifiable_workflow_decision="$(decide_candidate "$unclassifiable_workflow_sha")"
    assert_eq 'unclassifiable workflow surface uses initial review' 'initial' \
      "$(jq -r '.mode' <<<"$unclassifiable_workflow_decision")"

    git -C "$router_repo" checkout -q "$fixed_sha"
    mkdir -p "$router_repo/.github/actions/policy-check"
    printf 'name: policy check\nruns:\n  using: composite\n  steps: []\n' \
      >"$router_repo/.github/actions/policy-check/action.yml"
    git -C "$router_repo" add .github/actions/policy-check/action.yml
    git -C "$router_repo" commit -qm composite-action-signal
    composite_sha="$(git -C "$router_repo" rev-parse HEAD)"
    composite_decision="$(decide_candidate "$composite_sha")"
    assert_eq 'composite action signal uses expanded delta' 'delta' "$(jq -r '.mode' <<<"$composite_decision")"
    assert_eq 'composite action signal requires GitHub Actions coverage' 'github-actions' \
      "$(jq -r '.required_capabilities | map(select(. == "github-actions")) | join(",")' <<<"$composite_decision")"

    git -C "$router_repo" checkout -q "$fixed_sha"
    mkdir -p "$router_repo/security"
    printf 'version = 1\n' >"$router_repo/security/uv.lock"
    git -C "$router_repo" add security/uv.lock
    git -C "$router_repo" commit -qm mixed-security-dependency-signals
    mixed_signal_sha="$(git -C "$router_repo" rev-parse HEAD)"
    mixed_signal_decision="$(decide_candidate "$mixed_signal_sha")"
    assert_eq 'mixed safe signals use expanded delta' 'delta' "$(jq -r '.mode' <<<"$mixed_signal_decision")"
    assert_eq 'mixed signals require every corresponding capability' 'security,supply-chain' \
      "$(jq -r '[.required_capabilities[] | select(. == "security" or . == "supply-chain")] | join(",")' \
        <<<"$mixed_signal_decision")"

    git -C "$router_repo" checkout -q "$fixed_sha"
    ext_diff_ledger="$TEST_ROOT/ext-diff-ledger"
    textconv_ledger="$TEST_ROOT/textconv-ledger"
    ext_diff_driver="$TEST_ROOT/ext-diff-driver"
    textconv_driver="$TEST_ROOT/textconv-driver"
    : >"$ext_diff_ledger"
    : >"$textconv_ledger"
    printf '#!/bin/sh\nprintf "ext-diff\\n" >>"%s"\nexit 97\n' "$ext_diff_ledger" >"$ext_diff_driver"
    printf '#!/bin/sh\nprintf "textconv\\n" >>"%s"\ncat "$1"\n' "$textconv_ledger" >"$textconv_driver"
    chmod +x "$ext_diff_driver" "$textconv_driver"
    printf 'src/parser.py diff=review-plan-ledger\n' >"$router_repo/.gitattributes"
    git -C "$router_repo" config diff.review-plan-ledger.command "$ext_diff_driver"
    router_binding="$(review_plan_worktree_binding "$router_repo")"
    review_plan_changed_diff "$router_binding" "$reviewed_sha" "$fixed_sha" >/dev/null 2>&1
    assert_eq 'content diff disables external diff commands' '' "$(cat "$ext_diff_ledger")"
    git -C "$router_repo" config --unset diff.review-plan-ledger.command
    git -C "$router_repo" config diff.review-plan-ledger.textconv "$textconv_driver"
    review_plan_changed_diff "$router_binding" "$reviewed_sha" "$fixed_sha" >/dev/null 2>&1
    assert_eq 'content diff disables textconv commands' '' "$(cat "$textconv_ledger")"
    git -C "$router_repo" config --unset diff.review-plan-ledger.textconv
    rm "$router_repo/.gitattributes"

    git -C "$router_repo" checkout -q "$fixed_sha"
    original_changed_diff="$(declare -f review_plan_changed_diff 2>/dev/null || true)"
    review_plan_changed_diff() {
      printf '%s\n' 'diff --git a/src/parser.py b/src/parser.py' \
        '--- a/src/parser.py' '+++ b/src/parser.py' '@@ malformed @@' '+unsafe'
    }
    malformed_diff_decision_file="$TEST_ROOT/malformed-diff-decision.json"
    KC_PR_FLOW_DELTA_FAST_PATH=on review_plan_decide "$repo_id" 1693 "$base_sha" "$fixed_sha" "$config_hash" \
      "$router_repo" "$router_events" "$router_receipt" >"$malformed_diff_decision_file"
    malformed_diff_decision="$(<"$malformed_diff_decision_file")"
    assert_eq 'malformed zero-context diff falls back to initial' 'initial' "$(jq -r '.mode' <<<"$malformed_diff_decision")"
    if [ -n "$original_changed_diff" ]; then eval "$original_changed_diff"; else unset -f review_plan_changed_diff; fi

    git -C "$router_repo" checkout -q "$fixed_sha"
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

    real_git="$(command -v git)"
    run_open_fd_race() {
      local replacement_kind="$1" race_repo race_lines race_base race_reviewed race_fixed
      local race_events race_receipt race_ready race_proceed race_stub replacement_ledger
      local swapper_pid race_decision
      race_repo="$TEST_ROOT/race-$replacement_kind-repo"
      race_lines="$(make_replay_repo "$race_repo" "$fixture")"
      race_base="$(awk -F= '$1 == "base" { print $2 }' <<<"$race_lines")"
      race_reviewed="$(awk -F= '$1 == "reviewed" { print $2 }' <<<"$race_lines")"
      race_fixed="$(awk -F= '$1 == "fixed" { print $2 }' <<<"$race_lines")"
      race_events="$TEST_ROOT/race-$replacement_kind-events.jsonl"
      race_receipt="$TEST_ROOT/race-$replacement_kind-receipt.json"
      make_replay_receipt "$race_repo" "$repo_id" 1693 "$race_base" "$race_reviewed" "$config_hash" \
        "$race_events" "$race_receipt" "$fixture" >/dev/null
      cp -R "$race_repo" "$race_repo-replacement"

      race_ready="$TEST_ROOT/race-$replacement_kind-ready"
      race_proceed="$TEST_ROOT/race-$replacement_kind-proceed"
      mkfifo "$race_ready" "$race_proceed"
      replacement_ledger="$TEST_ROOT/race-$replacement_kind-ledger"
      : >"$replacement_ledger"
      race_stub="$TEST_ROOT/race-$replacement_kind-git-stub"
      mkdir -p "$race_stub"
      printf '#!/bin/sh\nif [ "$(pwd -P)" != "%s" ]; then printf "replacement\\n" >>"%s"; fi\nexec "%s" "$@"\n' \
        "$race_repo-held" "$replacement_ledger" "$real_git" >"$race_stub/git"
      chmod +x "$race_stub/git"

      (
        IFS= read -r _ <"$race_ready"
        mv "$race_repo" "$race_repo-held"
        if [ "$replacement_kind" = 'symlink' ]; then
          ln -s "$race_repo-replacement" "$race_repo"
        else
          mv "$race_repo-replacement" "$race_repo"
        fi
        printf 'continue\n' >"$race_proceed"
      ) &
      swapper_pid=$!
      exec 8<>"$race_ready"
      exec 9<>"$race_proceed"
      race_decision="$(PATH="$race_stub:$PATH" KC_PR_FLOW_TEST_GIT_OPEN_READY_FD=8 \
        KC_PR_FLOW_TEST_GIT_OPEN_PROCEED_FD=9 KC_PR_FLOW_DELTA_FAST_PATH=on \
        review_plan_decide "$repo_id" 1693 "$race_base" "$race_fixed" "$config_hash" \
          "$race_repo" "$race_events" "$race_receipt")"
      exec 8>&-
      exec 9>&-
      wait "$swapper_pid"
      assert_eq "$replacement_kind replacement after fd validation fails closed" 'initial' \
        "$(jq -r '.mode' <<<"$race_decision")"
      assert_eq "$replacement_kind replacement repository is never read" '' "$(cat "$replacement_ledger")"
    }
    run_open_fd_race directory
    run_open_fd_race symlink
  fi
fi

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
