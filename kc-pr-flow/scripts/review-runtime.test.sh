#!/usr/bin/env bash
# Unit tests for the append-only kc-pr-review shadow receipt runtime.
# shellcheck disable=SC2002,SC2016,SC2030,SC2031,SC2317,SC2329 # Intentional literal stubs, stdin probes, subshells, and dynamic function overrides across supported ShellCheck versions.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
RUNTIME="$HERE/review-runtime.sh"
BENCHMARK="$HERE/review-runtime-benchmark.sh"
SAFE_IO="$HERE/review-runtime-safe-io.py"
FIXTURE="$HERE/../test/fixtures/review-runtime/valid-events.jsonl"
REFERENCE="$HERE/../reference/review-runtime.md"
WORKFLOW="$HERE/../../.github/workflows/review-runtime-tests.yml"
TEST_STATE_ROOT="$(mktemp -d)"
TEST_INPUT_ROOT="$(mktemp -d)"
cleanup() {
  chmod -R u+rwX "$TEST_STATE_ROOT" 2>/dev/null || true
  chmod -R u+rwX "$TEST_INPUT_ROOT" 2>/dev/null || true
  rm -rf "$TEST_STATE_ROOT" "$TEST_INPUT_ROOT"
}
trap cleanup EXIT
export KC_PR_FLOW_STATE_DIR="$TEST_STATE_ROOT"

PASS=0
FAIL=0

CASE_FILTER='all'
if [ "$#" -gt 0 ]; then
  if [ "$#" -ne 2 ] || [ "$1" != '--case' ]; then
    printf 'usage: %s [--case delta-receipt-contract|delta-receipt-files|delta-receipt-happy-path|delta-receipt-identity|s01-inertness|privacy-envelope|safe-io|evidence-binding|interactive-decision|merge-readiness]\n' "$0" >&2
    exit 2
  fi
  CASE_FILTER="$2"
fi

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

assert_not_zero() { # $1=description $2=actual status
  if [ "$2" -ne 0 ]; then
    pass
  else
    fail "$1 (expected nonzero status)"
  fi
}

sha256_text() {
  if command -v shasum >/dev/null 2>&1; then
    printf '%s' "$1" | shasum -a 256 | awk '{print $1}'
  else
    printf '%s' "$1" | sha256sum | awk '{print $1}'
  fi
}

run_s01_inertness_tests() {
  local definitions baseline candidate value phrase

  assert_eq 'runtime workflow owns the runtime reference in pull and push' 2 \
    "$(grep -cF -- '- "kc-pr-flow/reference/review-runtime.md"' "$WORKFLOW" || true)"
  assert_eq 'existing runtime job runs the core contract once' 1 \
    "$(grep -cF 'bash kc-pr-flow/scripts/review-runtime.test.sh' "$WORKFLOW" || true)"
  for phrase in 'receipt --event-file FILE --config-file FILE --repo-worktree DIR' \
    'read-only receipt authority' 'internally replays' 'raw Git' \
    'no routing, timing, network, or posting authority' 'receipt-ready v2 events without routing'; do
    assert_eq "reference documents $phrase" 1 "$(grep -cF "$phrase" "$REFERENCE" || true)"
  done
  definitions='. "$1"; declare -f review_runtime_receipt review_runtime_validate_delta_receipt_files review_runtime_build_delta_receipt review_runtime_collect_shadow_observation review_runtime_shadow'
  baseline="$(env -u KC_PR_FLOW_DELTA_FAST_PATH bash -c "$definitions" _ "$RUNTIME")"
  if [ -n "$baseline" ]; then pass; else fail 'S01 receipt and shadow authority is sourceable'; fi
  if printf '%s' "$baseline" | grep -Eq 'KC_PR_FLOW_DELTA_FAST_PATH|review[_-]?route|review[_-]?post|(^|[;&|[:space:]])(gh|curl|wget|claude|codex)([[:space:]]|$)'; then
    fail 'S01 authority contains routing, posting, network, model, or fast-path control'
  else
    pass
  fi
  baseline="$(sha256_text "$baseline")"
  for value in '' off unknown on; do
    candidate="$(KC_PR_FLOW_DELTA_FAST_PATH="$value" bash -c "$definitions" _ "$RUNTIME")"
    assert_eq "fast-path value [${value:-empty}] cannot change S01 authority" "$baseline" \
      "$(sha256_text "$candidate")"
  done
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

run_delta_receipt_happy_path_tests() {
  local root repo config events first_receipt second_receipt stub_dir call_ledger
  local repository pr_number base_sha head_sha config_hash review_key run_id occurred_at
  local content_sha256 anchor_sha256 claim_key finding_id candidate_id pointer candidate task usage result finding behavior
  local start lane_started observed lane_finished synthesized finished receipt_rc
  root="$TEST_INPUT_ROOT/delta-receipt-happy-path"
  repo="$root/repo"
  config="$root/review-config.json"
  events="$root/events.jsonl"
  first_receipt="$root/receipt-one.json"
  second_receipt="$root/receipt-two.json"
  stub_dir="$root/stubs"
  call_ledger="$root/calls"
  repository='acme/widgets'
  pr_number=42
  run_id='run-delta-receipt-happy'
  occurred_at='2026-08-30T00:00:00Z'

  mkdir -p "$repo/src" "$stub_dir"
  git -C "$repo" init -q
  printf 'evidence bound review\n' >"$repo/src/review.sh"
  printf 'first CRLF\r\nsecond CRLF\r\n' >"$repo/src/crlf.txt"
  printf 'WORKTREE filter bytes\n' >"$repo/src/filtered.txt"
  printf 'src/filtered.txt filter=receipt-test\n' >"$repo/.gitattributes"
  git -C "$repo" config filter.receipt-test.clean 'sed s/WORKTREE/RAW/'
  git -C "$repo" config filter.receipt-test.smudge 'sed s/RAW/WORKTREE/'
  git -C "$repo" add .gitattributes src/review.sh src/crlf.txt src/filtered.txt
  git -C "$repo" -c user.name='Receipt Test' -c user.email='receipt@example.invalid' commit -qm seed
  git -C "$repo" remote add origin 'https://github.com/acme/widgets.git'
  head_sha="$(git -C "$repo" rev-parse HEAD)"
  base_sha="$head_sha"
  printf '%s' "$(review_runtime_config_canonical lite mixed false false false false security)" >"$config"
  config_hash="$(review_runtime_sha256 <"$config")"
  review_key="$(review_runtime_review_key "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash")"
  content_sha256="$(review_runtime_sha256 <"$repo/src/review.sh")"
  anchor_sha256="$(python3 - "$repo/src/review.sh" <<'PY'
import hashlib
import pathlib
import sys
line = pathlib.Path(sys.argv[1]).read_bytes().splitlines()[0]
print(hashlib.sha256(line).hexdigest())
PY
)"
  pointer="$(jq -S -c -n --arg key "$review_key" --arg repo "$repository" \
    --arg base "$base_sha" --arg head "$head_sha" --arg hash "$content_sha256" \
    '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",review_key:$key,repository:$repo,
      base_sha:$base,head_sha:$head,object_sha:$head,path:"src/review.sh",side:"RIGHT",line:1,
      locator:"review-anchor",content_sha256:$hash}')"
  claim_key="$(python3 - "$pointer" <<'PY'
import hashlib
import json
import sys
pointer = json.loads(sys.argv[1])
identity = {"content_sha256": pointer["content_sha256"], "line": pointer["line"],
            "object_sha": pointer["object_sha"], "path": pointer["path"], "side": pointer["side"]}
encoded = json.dumps(identity, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
print("security-" + hashlib.sha256(encoded).hexdigest()[:16])
PY
)"
  finding_id="$(python3 - "$anchor_sha256" "$claim_key" "$pointer" "$repository" "$review_key" <<'PY'
import hashlib
import json
import sys
anchor, claim, raw_pointer, repository, review_key = sys.argv[1:]
pointer = json.loads(raw_pointer)
identity = {"content_sha256": pointer["content_sha256"], "line": pointer["line"],
            "object_sha": pointer["object_sha"], "path": pointer["path"], "side": pointer["side"]}
value = {"anchor_sha256": anchor, "category": "security", "claim_key": claim,
         "evidence": identity, "path": pointer["path"], "repository": repository,
         "review_key": review_key, "side": pointer["side"]}
encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
print(hashlib.sha256(encoded).hexdigest())
PY
)"
  candidate_id="$(review_runtime_candidate_id "$run_id" security-1 1 "$content_sha256")"
  candidate="$(jq -S -c -n --arg id "$candidate_id" --arg run "$run_id" --arg key "$review_key" \
    --arg anchor "$anchor_sha256" --arg claim "$claim_key" --argjson evidence "$pointer" '
      {schema:"kc-pr-flow.review-candidate/v2",candidate_id:$id,run_id:$run,review_key:$key,
       lane_id:"security-1",ordinal:1,path:"src/review.sh",side:"RIGHT",anchor_sha256:$anchor,
       category:"security",claim_key:$claim,evidence:$evidence}')"
  task="$(jq -S -c -n --arg run "$run_id" --arg key "$review_key" --arg repo "$repository" \
    --arg base "$base_sha" --arg head "$head_sha" --arg config "$config_hash" \
    '{schema:"kc-pr-flow.review-task/v1",run_id:$run,review_key:$key,lane_id:"security-1",
      capability:"security",repository:$repo,pr_number:42,base_sha:$base,head_sha:$head,config_hash:$config}')"
  usage='{"input_tokens":100,"output_tokens":25,"provenance":"reported","provider_family":"claude","scope":"lane","total_tokens":125}'
  result="$(jq -S -c -n --arg run "$run_id" --arg key "$review_key" --arg id "$candidate_id" \
    --argjson usage "$usage" \
    '{schema:"kc-pr-flow.lane-result/v1",run_id:$run,review_key:$key,lane_id:"security-1",
      capability:"security",terminal_status:"succeeded",candidates:[$id],usage:$usage,provider_family:"claude"}')"
  finding="$(jq -S -c -n --arg id "$finding_id" --arg key "$review_key" --arg candidate "$candidate_id" \
    --arg anchor "$anchor_sha256" --arg claim "$claim_key" --argjson evidence "$pointer" '
      {schema:"kc-pr-flow.review-finding/v2",finding_id:$id,review_key:$key,candidate_ids:[$candidate],
       path:"src/review.sh",side:"RIGHT",anchor_sha256:$anchor,category:"security",claim_key:$claim,
       evidence:$evidence}')"
  behavior="$(jq -S -c -n --arg hash "$content_sha256" \
    '{body_sha256:$hash,confirmation_input_sha256:$hash,event_sha256:$hash,
      github_call_log_sha256:$hash,inline_comments_sha256:$hash,options_sha256:$hash}')"
  start="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" 1 "$occurred_at" run.started '{}')"
  lane_started="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" 2 "$occurred_at" lane.started "$(jq -S -c -n --argjson value "$task" '{review_task:$value}')")"
  observed="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" 3 "$occurred_at" finding.observed "$(jq -S -c -n --argjson value "$candidate" '{candidate:$value}')")"
  lane_finished="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" 4 "$occurred_at" lane.finished "$(jq -S -c -n --argjson value "$result" '{lane_result:$value}')")"
  synthesized="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" 5 "$occurred_at" synthesis.finished "$(jq -S -c -n --argjson value "$finding" '{findings:[$value],uncertain_candidate_ids:[]}')")"
  finished="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" 6 "$occurred_at" run.finished "$(jq -S -c -n --argjson value "$behavior" '{behavior_hashes:$value}')")"
  printf '%s\n' "$start" "$lane_started" "$observed" "$lane_finished" "$synthesized" "$finished" >"$events"

  : >"$call_ledger"
  for command in gh curl wget claude codex agy review-runtime-append review-runtime-start review-post.sh; do
    printf '#!/bin/sh\nprintf "%%s\\n" "$(basename "$0") $*" >>"$CALL_LEDGER"\nexit 97\n' >"$stub_dir/$command"
    chmod +x "$stub_dir/$command"
  done
  PATH="$stub_dir:$PATH" CALL_LEDGER="$call_ledger" bash "$RUNTIME" receipt \
    --event-file "$events" --config-file "$config" --repo-worktree "$repo" >"$first_receipt" 2>"$root/receipt.stderr"
  receipt_rc=$?
  assert_eq 'receipt command succeeds for one complete v2 finding' '0|' \
    "$receipt_rc|$(cat "$root/receipt.stderr")"
  assert_eq 'receipt schema is v2' 'kc-pr-flow.review-delta-receipt/v2' "$(jq -r '.schema' "$first_receipt" 2>/dev/null)"
  assert_eq 'receipt top-level keys are closed' \
    'content_sha256,coverage_gap_refs,known_findings,predecessor,required_capabilities,schema' \
    "$(jq -r 'keys | sort | join(",")' "$first_receipt" 2>/dev/null)"
  assert_eq 'receipt predecessor identity comes from replay' \
    "$repository|$pr_number|$base_sha|$head_sha|$config_hash|$review_key|$run_id" \
    "$(jq -r '.predecessor | [.repository,.pr_number,.base_sha,.head_sha,.config_hash,.review_key,.run_id] | join("|")' "$first_receipt" 2>/dev/null)"
  assert_eq 'receipt capability comes from replay and config' 'security' "$(jq -r '.required_capabilities | join(",")' "$first_receipt" 2>/dev/null)"
  assert_eq 'receipt has no coverage gaps' '0' "$(jq -r '.coverage_gap_refs | length' "$first_receipt" 2>/dev/null)"
  assert_eq 'receipt finding identity comes from replay' "$finding_id|$claim_key|$anchor_sha256|unresolved" \
    "$(jq -r '.known_findings[0] | [.finding_id,.claim_key,.anchor_sha256,.resolution_state] | join("|")' "$first_receipt" 2>/dev/null)"
  assert_eq 'receipt evidence comes from replay' "$pointer" "$(jq -S -c '.known_findings[0].evidence' "$first_receipt" 2>/dev/null)"
  PATH="$stub_dir:$PATH" CALL_LEDGER="$call_ledger" bash "$RUNTIME" receipt \
    --event-file "$events" --config-file "$config" --repo-worktree "$repo" >"$second_receipt" 2>>"$root/receipt.stderr"
  receipt_rc=$?
  assert_eq 'second receipt command succeeds' '0|' \
    "$receipt_rc|$(cat "$root/receipt.stderr")"
  assert_eq 'receipt bytes are deterministic' '0' "$(cmp -s "$first_receipt" "$second_receipt"; printf '%s' "$?")"
  assert_eq 'receipt path makes no network, model, append, start, or post calls' '0' "$(wc -l <"$call_ledger" | tr -d ' ')"
}

run_delta_receipt_contract_tests() {
  local root receipt events config repo output rc validator_ledger
  local barrier_events barrier_config barrier_ledger snapshot_ledger event_hash config_hash
  local mutation_name mutation_filter candidate mutation_file
  run_delta_receipt_happy_path_tests
  root="$TEST_INPUT_ROOT/delta-receipt-happy-path"
  receipt="$root/receipt-one.json"
  events="$root/events.jsonl"
  config="$root/review-config.json"
  repo="$root/repo"
  validator_ledger="$root/validator-calls"
  : >"$validator_ledger"

  if declare -F review_runtime_validate_delta_receipt_snapshots >/dev/null 2>&1; then
    review_runtime_validate_delta_receipt_snapshots "$receipt" "$events" "$config" "$repo" >/dev/null 2>&1
    assert_eq 'sourceable receipt validator accepts the producer output' '0' "$?"
    eval "$(declare -f review_runtime_validate_delta_receipt_snapshots | sed '1s/review_runtime_validate_delta_receipt_snapshots/review_runtime_validate_delta_receipt_snapshots_original/')"
    review_runtime_validate_delta_receipt_snapshots() {
      printf 'called\n' >>"$validator_ledger"
      return 97
    }
    output="$(review_runtime_receipt "$events" "$config" "$repo" 2>/dev/null)"
    rc=$?
    assert_eq 'producer returns the shared validator failure' '97' "$rc"
    assert_eq 'producer emits no receipt when shared validation fails' '' "$output"
    assert_eq 'producer invokes the shared validator exactly once' '1' "$(wc -l <"$validator_ledger" | tr -d ' ')"
    eval "$(declare -f review_runtime_validate_delta_receipt_snapshots_original | sed '1s/review_runtime_validate_delta_receipt_snapshots_original/review_runtime_validate_delta_receipt_snapshots/')"
    unset -f review_runtime_validate_delta_receipt_snapshots_original
  else
    fail 'sourceable snapshot-only receipt validator exists for producer'
  fi

  barrier_events="$root/barrier-events.jsonl"
  barrier_config="$root/barrier-config.json"
  barrier_ledger="$root/barrier-validator"
  snapshot_ledger="$root/barrier-snapshots"
  cp "$events" "$barrier_events"
  cp "$config" "$barrier_config"
  : >"$barrier_ledger"
  : >"$snapshot_ledger"
  event_hash="$(review_runtime_sha256 <"$barrier_events")"
  config_hash="$(review_runtime_sha256 <"$barrier_config")"
  eval "$(declare -f review_runtime_snapshot_regular_file | sed '1s/review_runtime_snapshot_regular_file/review_runtime_snapshot_regular_file_original/')"
  eval "$(declare -f review_runtime_validate_delta_receipt_snapshots | sed '1s/review_runtime_validate_delta_receipt_snapshots/review_runtime_validate_delta_receipt_snapshots_original/')"
  review_runtime_snapshot_regular_file() {
    review_runtime_snapshot_regular_file_original "$@"
    rc=$?
    [ "$rc" -eq 0 ] || return "$rc"
    case "$3" in
      'event file') printf '{"replaced":true}\n' >"$1" ;;
      'review config') printf '{"replaced":true}\n' >"$1" ;;
    esac
    printf '%s\n' "$3" >>"$snapshot_ledger"
  }
  review_runtime_validate_delta_receipt_snapshots() {
    printf '%s|%s|%s|%s\n' \
      "$([ "$2" = "$barrier_events" ] && printf caller || printf snapshot)" \
      "$([ "$3" = "$barrier_config" ] && printf caller || printf snapshot)" \
      "$(review_runtime_sha256 <"$2")" "$(review_runtime_sha256 <"$3")" >>"$barrier_ledger"
    review_runtime_validate_delta_receipt_snapshots_original "$@"
  }
  output="$(review_runtime_receipt "$barrier_events" "$barrier_config" "$repo" 2>/dev/null)"
  rc=$?
  assert_eq 'receipt survives caller event/config replacement after snapshots' '0' "$rc"
  assert_eq 'barrier receipt keeps original bytes' "$(cat "$receipt")" "$output"
  assert_eq 'top-level receipt snapshots each caller input once' 'event file,review config' \
    "$(sort "$snapshot_ledger" | paste -sd, -)"
  assert_eq 'shared validator receives original immutable event/config snapshots' \
    "snapshot|snapshot|$event_hash|$config_hash" "$(cat "$barrier_ledger")"
  eval "$(declare -f review_runtime_snapshot_regular_file_original | sed '1s/review_runtime_snapshot_regular_file_original/review_runtime_snapshot_regular_file/')"
  eval "$(declare -f review_runtime_validate_delta_receipt_snapshots_original | sed '1s/review_runtime_validate_delta_receipt_snapshots_original/review_runtime_validate_delta_receipt_snapshots/')"
  unset -f review_runtime_snapshot_regular_file_original review_runtime_validate_delta_receipt_snapshots_original

  reseal_delta_receipt() {
    local value="$1" unsigned hash
    unsigned="$(printf '%s' "$value" | jq -S -c 'del(.content_sha256)')" || return
    hash="$(printf '%s' "$unsigned" | review_runtime_sha256)" || return
    printf '%s' "$unsigned" | jq -S -c --arg hash "$hash" '. + {content_sha256:$hash}'
  }
  while IFS='|' read -r mutation_name mutation_filter; do
    candidate="$(jq -S -c "$mutation_filter" "$receipt")" || return
    candidate="$(reseal_delta_receipt "$candidate")" || return
    mutation_file="$root/receipt-$mutation_name.json"
    printf '%s\n' "$candidate" >"$mutation_file"
    review_runtime_validate_delta_receipt_snapshots "$mutation_file" "$events" "$config" "$repo" >/dev/null 2>&1
    assert_not_zero "validator rejects $mutation_name mutation after self-reseal" "$?"
  done <<'EOF'
top-extra|.extra=true
top-missing|del(.coverage_gap_refs)
predecessor-extra|.predecessor.extra=true
predecessor-missing|del(.predecessor.repository)
finding-extra|.known_findings[0].extra=true
finding-missing|del(.known_findings[0].claim_key)
repository|.predecessor.repository="other/widgets"
pr-number|.predecessor.pr_number=43
base-sha|.predecessor.base_sha=("1"*40)
head-sha|.predecessor.head_sha=("2"*40)
config-hash|.predecessor.config_hash=("3"*64)
review-key|.predecessor.review_key=("4"*64)
run-id|.predecessor.run_id="run-mutated"
receipt-id|.predecessor.receipt_id=("5"*64)
finding-id|.known_findings[0].finding_id=("6"*64)
EOF
  mutation_file="$root/receipt-content-hash.json"
  jq -S -c '.content_sha256=("7"*64)' "$receipt" >"$mutation_file"
  review_runtime_validate_delta_receipt_snapshots "$mutation_file" "$events" "$config" "$repo" >/dev/null 2>&1
  assert_not_zero 'validator rejects changed content hash' "$?"
  mutation_file="$root/receipt-raw-duplicate.json"
  printf '%s\n' '{"schema":"kc-pr-flow.review-delta-receipt/v2","schema":"kc-pr-flow.review-delta-receipt/v2"}' >"$mutation_file"
  review_runtime_validate_delta_receipt_snapshots "$mutation_file" "$events" "$config" "$repo" >/dev/null 2>&1
  assert_not_zero 'validator rejects raw duplicate receipt members' "$?"
  unset -f reseal_delta_receipt
}

run_delta_receipt_file_validator_tests() {
  local root receipt events config repo output rc snapshot_ledger validator_ledger
  local barrier_receipt barrier_events barrier_config
  local missing receipt_link event_link config_link receipt_fifo event_fifo config_fifo
  local config_duplicate config_noncanonical config_extra config_empty
  local zero_events failed_events unavailable_events uncertain_events no_behavior_events mismatch_events mismatch_config
  local start_event synthesis_event finish_event mutated candidate_id status line rewritten
  local new_config_hash new_review_key repository pr_number base_sha head_sha
  run_delta_receipt_happy_path_tests
  root="$TEST_INPUT_ROOT/delta-receipt-happy-path"
  receipt="$root/receipt-one.json"
  events="$root/events.jsonl"
  config="$root/review-config.json"
  repo="$root/repo"

  if declare -F review_runtime_validate_delta_receipt_files >/dev/null 2>&1; then
    output="$(review_runtime_validate_delta_receipt_files \
      "$receipt" "$events" "$config" "$repo" 2>/dev/null)"
    rc=$?
    assert_eq 'file validator accepts one complete producer receipt without stdout' '0|' "$rc|$output"
  else
    fail 'sourceable high-level receipt file validator exists'
    return
  fi

  snapshot_ledger="$root/file-validator-snapshots"
  validator_ledger="$root/file-validator-low-level"
  barrier_receipt="$root/barrier-receipt.json"
  barrier_events="$root/barrier-events-for-file-validator.jsonl"
  barrier_config="$root/barrier-config-for-file-validator.json"
  cp "$receipt" "$barrier_receipt"
  cp "$events" "$barrier_events"
  cp "$config" "$barrier_config"
  : >"$snapshot_ledger"
  : >"$validator_ledger"
  eval "$(declare -f review_runtime_snapshot_regular_file | sed '1s/review_runtime_snapshot_regular_file/review_runtime_snapshot_regular_file_original/')"
  eval "$(declare -f review_runtime_validate_delta_receipt_snapshots | sed '1s/review_runtime_validate_delta_receipt_snapshots/review_runtime_validate_delta_receipt_snapshots_original/')"
  review_runtime_snapshot_regular_file() {
    local snapshot_rc
    printf '%s|%s\n' "$3" "$1" >>"$snapshot_ledger"
    review_runtime_snapshot_regular_file_original "$@"
    snapshot_rc=$?
    [ "$snapshot_rc" -eq 0 ] || return "$snapshot_rc"
    printf '{"replaced":true}\n' >"$1"
  }
  review_runtime_validate_delta_receipt_snapshots() {
    printf '%s|%s|%s\n' \
      "$([ "$1" = "$barrier_receipt" ] && printf caller || printf snapshot)" \
      "$([ "$2" = "$barrier_events" ] && printf caller || printf snapshot)" \
      "$([ "$3" = "$barrier_config" ] && printf caller || printf snapshot)" >>"$validator_ledger"
    review_runtime_validate_delta_receipt_snapshots_original "$@"
  }
  output="$(review_runtime_validate_delta_receipt_files \
    "$barrier_receipt" "$barrier_events" "$barrier_config" "$repo" 2>/dev/null)"
  rc=$?
  assert_eq 'file validator survives replacement of all caller paths after snapshots' '0|' "$rc|$output"
  assert_eq 'file validator snapshots each caller file exactly once' \
    'delta receipt,event file,review config' "$(cut -d '|' -f 1 "$snapshot_ledger" | paste -sd, -)"
  assert_eq 'file validator passes only private snapshots to low-level validation' \
    'snapshot|snapshot|snapshot' "$(cat "$validator_ledger")"
  eval "$(declare -f review_runtime_snapshot_regular_file_original | sed '1s/review_runtime_snapshot_regular_file_original/review_runtime_snapshot_regular_file/')"
  eval "$(declare -f review_runtime_validate_delta_receipt_snapshots_original | sed '1s/review_runtime_validate_delta_receipt_snapshots_original/review_runtime_validate_delta_receipt_snapshots/')"
  unset -f review_runtime_snapshot_regular_file_original review_runtime_validate_delta_receipt_snapshots_original

  assert_file_validator_rejected() {
    local description="$1" receipt_file="$2" event_file="$3" config_file="$4" value status_code
    value="$(review_runtime_validate_delta_receipt_files \
      "$receipt_file" "$event_file" "$config_file" "$repo" 2>/dev/null)"
    status_code=$?
    assert_not_zero "$description returns nonzero" "$status_code"
    assert_eq "$description emits no stdout" '' "$value"
  }
  assert_fifo_file_validator_rejected() {
    local description="$1" receipt_file="$2" event_file="$3" config_file="$4" result
    result="$(python3 - "$RUNTIME" "$receipt_file" "$event_file" "$config_file" "$repo" <<'PY'
import os
import signal
import subprocess
import sys

runtime, receipt, events, config, repo = sys.argv[1:]
command = '. "$1"; review_runtime_validate_delta_receipt_files "$2" "$3" "$4" "$5"'
process = subprocess.Popen(
    ["bash", "-c", command, "bash", runtime, receipt, events, config, repo],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    start_new_session=True,
)
try:
    stdout, _ = process.communicate(timeout=5)
except subprocess.TimeoutExpired:
    os.killpg(process.pid, signal.SIGKILL)
    process.wait()
    print("TIMEOUT")
else:
    print(f"{process.returncode}|{stdout.decode()}", end="")
PY
)"
    assert_match "$description is bounded, nonzero, and stdout-empty" '^[1-9][0-9]*\|$' "$result"
  }

  missing="$root/missing-input"
  assert_file_validator_rejected 'missing receipt' "$missing" "$events" "$config"
  assert_file_validator_rejected 'missing event file' "$receipt" "$missing" "$config"
  assert_file_validator_rejected 'missing config' "$receipt" "$events" "$missing"
  receipt_link="$root/receipt-link"
  event_link="$root/event-link"
  config_link="$root/config-link"
  ln -s "$receipt" "$receipt_link"
  ln -s "$events" "$event_link"
  ln -s "$config" "$config_link"
  assert_file_validator_rejected 'symlink receipt' "$receipt_link" "$events" "$config"
  assert_file_validator_rejected 'symlink event file' "$receipt" "$event_link" "$config"
  assert_file_validator_rejected 'symlink config' "$receipt" "$events" "$config_link"
  receipt_fifo="$root/receipt-fifo"
  event_fifo="$root/event-fifo"
  config_fifo="$root/config-fifo"
  mkfifo "$receipt_fifo" "$event_fifo" "$config_fifo"
  assert_fifo_file_validator_rejected 'FIFO receipt' "$receipt_fifo" "$events" "$config"
  assert_fifo_file_validator_rejected 'FIFO event file' "$receipt" "$event_fifo" "$config"
  assert_fifo_file_validator_rejected 'FIFO config' "$receipt" "$events" "$config_fifo"

  output="$(KC_PR_FLOW_MAX_RECEIPT_BYTES=1 review_runtime_validate_delta_receipt_files \
    "$receipt" "$events" "$config" "$repo" 2>/dev/null)"
  rc=$?
  assert_not_zero 'oversize receipt returns nonzero' "$rc"
  assert_eq 'oversize receipt emits no stdout' '' "$output"
  output="$(KC_PR_FLOW_MAX_EVENTS_BYTES=1 review_runtime_validate_delta_receipt_files \
    "$receipt" "$events" "$config" "$repo" 2>/dev/null)"
  rc=$?
  assert_not_zero 'oversize event file returns nonzero' "$rc"
  assert_eq 'oversize event file emits no stdout' '' "$output"
  output="$(KC_PR_FLOW_MAX_CONFIG_BYTES=1 review_runtime_validate_delta_receipt_files \
    "$receipt" "$events" "$config" "$repo" 2>/dev/null)"
  rc=$?
  assert_not_zero 'oversize config returns nonzero' "$rc"
  assert_eq 'oversize config emits no stdout' '' "$output"

  config_duplicate="$root/config-duplicate.json"
  config_noncanonical="$root/config-noncanonical.json"
  config_extra="$root/config-extra.json"
  config_empty="$root/config-empty.json"
  printf '%s' '{"schema":"kc-pr-flow.review-config/v1","schema":"kc-pr-flow.review-config/v1"}' >"$config_duplicate"
  jq . "$config" >"$config_noncanonical"
  printf '%s' "$(jq -S -c '.extra=true' "$config")" >"$config_extra"
  printf '%s' "$(jq -S -c '.capabilities=[]' "$config")" >"$config_empty"
  assert_file_validator_rejected 'duplicate-key config' "$receipt" "$events" "$config_duplicate"
  assert_file_validator_rejected 'noncanonical config' "$receipt" "$events" "$config_noncanonical"
  assert_file_validator_rejected 'extra-key config' "$receipt" "$events" "$config_extra"
  assert_file_validator_rejected 'empty-capability config' "$receipt" "$events" "$config_empty"

  assert_lifecycle_rejected() {
    local description="$1" event_file="$2" config_file="$3" value status_code
    value="$(review_runtime_receipt "$event_file" "$config_file" "$repo" 2>/dev/null)"
    status_code=$?
    assert_not_zero "producer rejects $description" "$status_code"
    assert_eq "producer emits no stdout for $description" '' "$value"
    value="$(review_runtime_validate_delta_receipt_files \
      "$receipt" "$event_file" "$config_file" "$repo" 2>/dev/null)"
    status_code=$?
    assert_not_zero "file validator rejects $description" "$status_code"
    assert_eq "file validator emits no stdout for $description" '' "$value"
  }

  zero_events="$root/events-zero-lane.jsonl"
  start_event="$(sed -n '1p' "$events")"
  synthesis_event="$(rehash_event "$(sed -n '5p' "$events" | jq -c \
    '.sequence=2 | .payload={findings:[],uncertain_candidate_ids:[]}')")"
  finish_event="$(rehash_event "$(sed -n '6p' "$events" | jq -c '.sequence=3')")"
  printf '%s\n' "$start_event" "$synthesis_event" "$finish_event" >"$zero_events"
  assert_lifecycle_rejected 'zero-lane run' "$zero_events" "$config"

  for status in failed unavailable; do
    mutated="$(rehash_event "$(sed -n '4p' "$events" | jq -c --arg status "$status" \
      '.payload.lane_result.terminal_status=$status')")"
    if [ "$status" = 'failed' ]; then
      failed_events="$root/events-failed.jsonl"
      { sed -n '1,3p' "$events"; printf '%s\n' "$mutated"; sed -n '5,6p' "$events"; } >"$failed_events"
      assert_lifecycle_rejected 'failed lane' "$failed_events" "$config"
    else
      unavailable_events="$root/events-unavailable.jsonl"
      { sed -n '1,3p' "$events"; printf '%s\n' "$mutated"; sed -n '5,6p' "$events"; } >"$unavailable_events"
      assert_lifecycle_rejected 'unavailable lane' "$unavailable_events" "$config"
    fi
  done

  uncertain_events="$root/events-uncertain.jsonl"
  candidate_id="$(sed -n '3p' "$events" | jq -r '.payload.candidate.candidate_id')"
  mutated="$(rehash_event "$(sed -n '5p' "$events" | jq -c --arg id "$candidate_id" \
    '.payload={findings:[],uncertain_candidate_ids:[$id]}')")"
  { sed -n '1,4p' "$events"; printf '%s\n' "$mutated"; sed -n '6p' "$events"; } >"$uncertain_events"
  assert_lifecycle_rejected 'nonempty uncertain set' "$uncertain_events" "$config"

  no_behavior_events="$root/events-no-behavior.jsonl"
  mutated="$(rehash_event "$(sed -n '6p' "$events" | jq -c '.payload={}')")"
  { sed -n '1,5p' "$events"; printf '%s\n' "$mutated"; } >"$no_behavior_events"
  assert_lifecycle_rejected 'missing behavior hashes' "$no_behavior_events" "$config"

  mismatch_config="$root/config-capability-mismatch.json"
  printf '%s' "$(jq -S -c '.capabilities=["types"]' "$config")" >"$mismatch_config"
  new_config_hash="$(review_runtime_sha256 <"$mismatch_config")"
  repository="$(jq -r '.repository' <<<"$start_event")"
  pr_number="$(jq -r '.pr_number' <<<"$start_event")"
  base_sha="$(jq -r '.base_sha' <<<"$start_event")"
  head_sha="$(jq -r '.head_sha' <<<"$start_event")"
  new_review_key="$(review_runtime_review_key \
    "$repository" "$pr_number" "$base_sha" "$head_sha" "$new_config_hash")"
  mismatch_events="$root/events-capability-mismatch.jsonl"
  : >"$mismatch_events"
  while IFS= read -r line; do
    rewritten="$(jq -c --arg config_hash "$new_config_hash" --arg review_key "$new_review_key" '
      .config_hash=$config_hash | .review_key=$review_key |
      if .event_type == "lane.started" then
        .payload.review_task.config_hash=$config_hash | .payload.review_task.review_key=$review_key
      elif .event_type == "finding.observed" then
        .payload.candidate.review_key=$review_key | .payload.candidate.evidence.review_key=$review_key
      elif .event_type == "lane.finished" then
        .payload.lane_result.review_key=$review_key
      elif .event_type == "synthesis.finished" then
        .payload.findings |= map(.review_key=$review_key | .evidence.review_key=$review_key)
      else . end' <<<"$line")"
    if [ "$(jq -r '.event_type' <<<"$rewritten")" = 'synthesis.finished' ]; then
      mutated="$(jq -c '.payload.findings[0]' <<<"$rewritten")"
      candidate_id="$(review_runtime_v2_finding_id "$mutated" "$repository" "$new_review_key")"
      rewritten="$(jq -c --arg finding_id "$candidate_id" '.payload.findings[0].finding_id=$finding_id' <<<"$rewritten")"
    fi
    rehash_event "$rewritten" >>"$mismatch_events"
  done <"$events"
  assert_lifecycle_rejected 'config capability mismatch' "$mismatch_events" "$mismatch_config"
  assert_lifecycle_rejected 'empty config capability set' "$events" "$config_empty"

  unset -f assert_file_validator_rejected assert_fifo_file_validator_rejected assert_lifecycle_rejected
}

run_delta_receipt_identity_tests() {
  local root receipt events config repo output rc forged_events candidate_event finding_event
  local candidate finding claim_key finding_id pointer anchor identity null_events null_receipt
  local target_events target_receipt target_path target_line blob_file content_sha256 candidate_id
  local result_event working_hash raw_hash subject_path evidence_path mutation_name mutation_line mutation_filter
  run_delta_receipt_happy_path_tests
  root="$TEST_INPUT_ROOT/delta-receipt-happy-path"
  receipt="$root/receipt-one.json"
  events="$root/events.jsonl"
  config="$root/review-config.json"
  repo="$root/repo"

  git -C "$repo" remote remove origin
  output="$(review_runtime_receipt "$events" "$config" "$repo" 2>/dev/null)"
  rc=$?
  assert_eq 'producer trusts closed event/pointer repository without repo-local remote config' \
    "0|$(cat "$receipt")" "$rc|$output"
  output="$(review_runtime_validate_delta_receipt_files \
    "$receipt" "$events" "$config" "$repo" 2>/dev/null)"
  rc=$?
  assert_eq 'file validator trusts closed event/pointer repository without repo-local remote config' \
    '0|' "$rc|$output"

  assert_identity_rejected() {
    local description="$1" event_file="$2" value status_code
    value="$(review_runtime_receipt "$event_file" "$config" "$repo" 2>/dev/null)"
    status_code=$?
    assert_not_zero "producer rejects $description" "$status_code"
    assert_eq "producer emits no stdout for $description" '' "$value"
    value="$(review_runtime_validate_delta_receipt_files \
      "$receipt" "$event_file" "$config" "$repo" 2>/dev/null)"
    status_code=$?
    assert_not_zero "file validator rejects $description" "$status_code"
    assert_eq "file validator emits no stdout for $description" '' "$value"
  }

  forged_events="$root/events-subject-path-forged.jsonl"
  candidate_event="$(sed -n '3p' "$events")"
  candidate="$(jq -c '.payload.candidate | .path="src/forged.sh"' <<<"$candidate_event")"
  claim_key="$(review_runtime_v2_claim_key "$candidate")"
  candidate="$(jq -c --arg claim "$claim_key" '.claim_key=$claim' <<<"$candidate")"
  candidate_event="$(rehash_event "$(jq -c --argjson candidate "$candidate" \
    '.payload={candidate:$candidate}' <<<"$candidate_event")")"
  finding_event="$(sed -n '5p' "$events")"
  finding="$(jq -c --arg claim "$claim_key" \
    '.payload.findings[0] | .path="src/forged.sh" | .claim_key=$claim' <<<"$finding_event")"
  finding_id="$(review_runtime_v2_finding_id "$finding" 'acme/widgets' \
    "$(jq -r '.review_key' <<<"$finding_event")")"
  finding_event="$(rehash_event "$(jq -c --argjson finding "$finding" \
    --arg id "$finding_id" '.payload.findings[0]=($finding | .finding_id=$id)' <<<"$finding_event")")"
  { sed -n '1,2p' "$events"; printf '%s\n' "$candidate_event"; sed -n '4p' "$events"; \
    printf '%s\n' "$finding_event"; sed -n '6p' "$events"; } >"$forged_events"
  assert_identity_rejected 'subject path differing from evidence path after event rehash' "$forged_events"

  write_subject_evidence_pair_events() {
    local pair_path="$1" pair_side="$2" pointer_path="$3" pointer_side="$4" destination="$5"
    local pair_candidate pair_finding pair_claim pair_id
    candidate_event="$(sed -n '3p' "$events")"
    pair_candidate="$(jq -c --arg path "$pair_path" --arg side "$pair_side" \
      --arg pointer_path "$pointer_path" --arg pointer_side "$pointer_side" \
      '.payload.candidate | .path=$path | .side=$side |
       .evidence.path=$pointer_path | .evidence.side=$pointer_side' <<<"$candidate_event")" || return
    pair_claim="$(review_runtime_v2_claim_key "$pair_candidate")" || return
    pair_candidate="$(jq -c --arg claim "$pair_claim" '.claim_key=$claim' <<<"$pair_candidate")" || return
    candidate_event="$(rehash_event "$(jq -c --argjson candidate "$pair_candidate" \
      '.payload={candidate:$candidate}' <<<"$candidate_event")")" || return
    finding_event="$(sed -n '5p' "$events")"
    pair_finding="$(jq -c --arg path "$pair_path" --arg side "$pair_side" \
      --arg pointer_path "$pointer_path" --arg pointer_side "$pointer_side" --arg claim "$pair_claim" \
      '.payload.findings[0] | .path=$path | .side=$side | .claim_key=$claim |
       .evidence.path=$pointer_path | .evidence.side=$pointer_side' <<<"$finding_event")" || return
    pair_id="$(review_runtime_v2_finding_id "$pair_finding" 'acme/widgets' \
      "$(jq -r '.review_key' <<<"$finding_event")")" || return
    finding_event="$(rehash_event "$(jq -c --argjson finding "$pair_finding" --arg id "$pair_id" \
      '.payload.findings[0]=($finding | .finding_id=$id)' <<<"$finding_event")")" || return
    { sed -n '1,2p' "$events"; printf '%s\n' "$candidate_event"; sed -n '4p' "$events"; \
      printf '%s\n' "$finding_event"; sed -n '6p' "$events"; } >"$destination"
  }

  forged_events="$root/events-subject-side-forged.jsonl"
  write_subject_evidence_pair_events 'src/review.sh' LEFT 'src/review.sh' RIGHT "$forged_events"
  assert_identity_rejected 'subject side differing from evidence side after identity rehash' "$forged_events"

  subject_path="$(printf 'src/cafe\314\201.sh')"
  evidence_path="$(printf 'src/caf\303\251.sh')"
  forged_events="$root/events-nfc-equivalent-paths.jsonl"
  write_subject_evidence_pair_events "$subject_path" RIGHT "$evidence_path" RIGHT "$forged_events"
  assert_identity_rejected 'NFC-equivalent but byte-distinct subject/evidence paths fail closed' "$forged_events"

  forged_events="$root/events-candidate-anchor-forged.jsonl"
  candidate_event="$(rehash_event "$(sed -n '3p' "$events" | jq -c \
    '.payload.candidate.anchor_sha256=("f"*64)')")"
  { sed -n '1,2p' "$events"; printf '%s\n' "$candidate_event"; sed -n '4,6p' "$events"; } >"$forged_events"
  assert_identity_rejected 'candidate anchor differing from finding after event rehash' "$forged_events"

  while IFS='|' read -r mutation_name mutation_line mutation_filter; do
    forged_events="$root/events-$mutation_name.jsonl"
    if [ "$mutation_line" = 'candidate' ]; then
      candidate_event="$(rehash_event "$(sed -n '3p' "$events" | jq -c "$mutation_filter")")"
      { sed -n '1,2p' "$events"; printf '%s\n' "$candidate_event"; sed -n '4,6p' "$events"; } >"$forged_events"
    else
      finding_event="$(sed -n '5p' "$events")"
      finding="$(jq -c ".payload.findings[0] | $mutation_filter" <<<"$finding_event")"
      if [ "$mutation_name" != 'finding-id-forged' ]; then
        finding_id="$(review_runtime_v2_finding_id "$finding" 'acme/widgets' \
          "$(jq -r '.review_key' <<<"$finding_event")")"
        finding="$(jq -c --arg id "$finding_id" '.finding_id=$id' <<<"$finding")"
      fi
      finding_event="$(rehash_event "$(jq -c --argjson finding "$finding" \
        '.payload.findings[0]=$finding' <<<"$finding_event")")"
      { sed -n '1,4p' "$events"; printf '%s\n' "$finding_event"; sed -n '6p' "$events"; } >"$forged_events"
    fi
    assert_identity_rejected "$mutation_name after event and dependent identity rehash" "$forged_events"
  done <<'EOF'
candidate-claim-forged|candidate|.payload.candidate.claim_key="security-forgedclaim"
finding-claim-forged|finding|.claim_key="security-forgedclaim"
finding-id-forged|finding|.finding_id=("f"*64)
EOF

  null_events="$root/events-file-level-null-line.jsonl"
  null_receipt="$root/receipt-file-level-null-line.json"
  pointer="$(sed -n '3p' "$events" | jq -S -c '.payload.candidate.evidence | .line=null')"
  identity="$(printf '%s' "$pointer" | jq -S -c \
    '{content_sha256,line,object_sha,path,side}')"
  anchor="$(printf '%s' "$identity" | review_runtime_sha256)"
  candidate_event="$(sed -n '3p' "$events")"
  candidate="$(jq -c --argjson evidence "$pointer" --arg anchor "$anchor" \
    '.payload.candidate | .evidence=$evidence | .anchor_sha256=$anchor' <<<"$candidate_event")"
  claim_key="$(review_runtime_v2_claim_key "$candidate")"
  candidate="$(jq -c --arg claim "$claim_key" '.claim_key=$claim' <<<"$candidate")"
  candidate_event="$(rehash_event "$(jq -c --argjson candidate "$candidate" \
    '.payload={candidate:$candidate}' <<<"$candidate_event")")"
  finding_event="$(sed -n '5p' "$events")"
  finding="$(jq -c --argjson evidence "$pointer" --arg anchor "$anchor" --arg claim "$claim_key" \
    '.payload.findings[0] | .evidence=$evidence | .anchor_sha256=$anchor | .claim_key=$claim' <<<"$finding_event")"
  finding_id="$(review_runtime_v2_finding_id "$finding" 'acme/widgets' \
    "$(jq -r '.review_key' <<<"$finding_event")")"
  finding_event="$(rehash_event "$(jq -c --argjson finding "$finding" --arg id "$finding_id" \
    '.payload.findings[0]=($finding | .finding_id=$id)' <<<"$finding_event")")"
  { sed -n '1,2p' "$events"; printf '%s\n' "$candidate_event"; sed -n '4p' "$events"; \
    printf '%s\n' "$finding_event"; sed -n '6p' "$events"; } >"$null_events"
  output="$(review_runtime_receipt "$null_events" "$config" "$repo" 2>/dev/null)"
  rc=$?
  assert_eq 'producer accepts deterministic file-level null-line anchor' '0' "$rc"
  printf '%s\n' "$output" >"$null_receipt"
  output="$(review_runtime_validate_delta_receipt_files \
    "$null_receipt" "$null_events" "$config" "$repo" 2>/dev/null)"
  rc=$?
  assert_eq 'file validator accepts deterministic file-level null-line anchor without stdout' '0|' "$rc|$output"

  forged_events="$root/events-file-level-null-anchor-forged.jsonl"
  candidate_event="$(rehash_event "$(sed -n '3p' "$null_events" | jq -c \
    '.payload.candidate.anchor_sha256=("f"*64)')")"
  finding_event="$(sed -n '5p' "$null_events")"
  finding="$(jq -c '.payload.findings[0] | .anchor_sha256=("f"*64)' <<<"$finding_event")"
  finding_id="$(review_runtime_v2_finding_id "$finding" 'acme/widgets' \
    "$(jq -r '.review_key' <<<"$finding_event")")"
  finding_event="$(rehash_event "$(jq -c --argjson finding "$finding" --arg id "$finding_id" \
    '.payload.findings[0]=($finding | .finding_id=$id)' <<<"$finding_event")")"
  { sed -n '1,2p' "$null_events"; printf '%s\n' "$candidate_event"; sed -n '4p' "$null_events"; \
    printf '%s\n' "$finding_event"; sed -n '6p' "$null_events"; } >"$forged_events"
  assert_identity_rejected 'forged deterministic null-line anchor after event rehash' "$forged_events"

  write_target_evidence_events() {
    local path="$1" line_value="$2" destination="$3" target_pointer target_anchor target_identity
    local target_candidate target_finding review_key run_id lane_id ordinal
    blob_file="$root/target-evidence-blob"
    git -C "$repo" --no-replace-objects cat-file blob "$(git -C "$repo" rev-parse HEAD):$path" >"$blob_file" || return
    content_sha256="$(review_runtime_sha256 <"$blob_file")" || return
    target_pointer="$(sed -n '3p' "$events" | jq -S -c --arg path "$path" \
      --arg hash "$content_sha256" --argjson line "$line_value" \
      '.payload.candidate.evidence | .path=$path | .content_sha256=$hash | .line=$line')" || return
    if [ "$line_value" = 'null' ]; then
      target_identity="$(printf '%s' "$target_pointer" | jq -S -c \
        '{content_sha256,line,object_sha,path,side}')" || return
      target_anchor="$(printf '%s' "$target_identity" | review_runtime_sha256)" || return
    else
      target_anchor="$(python3 - "$blob_file" "$line_value" <<'PY'
import hashlib
import pathlib
import sys
lines = pathlib.Path(sys.argv[1]).read_bytes().splitlines(keepends=True)
value = lines[int(sys.argv[2]) - 1]
for ending in (b"\r\n", b"\n", b"\r"):
    if value.endswith(ending):
        value = value[:-len(ending)]
        break
print(hashlib.sha256(value).hexdigest())
PY
)" || return
    fi
    candidate_event="$(sed -n '3p' "$events")"
    target_candidate="$(jq -c --argjson evidence "$target_pointer" --arg path "$path" \
      --arg anchor "$target_anchor" '.payload.candidate | .evidence=$evidence | .path=$path |
      .anchor_sha256=$anchor' <<<"$candidate_event")" || return
    claim_key="$(review_runtime_v2_claim_key "$target_candidate")" || return
    run_id="$(jq -r '.run_id' <<<"$target_candidate")"
    lane_id="$(jq -r '.lane_id' <<<"$target_candidate")"
    ordinal="$(jq -r '.ordinal' <<<"$target_candidate")"
    candidate_id="$(review_runtime_candidate_id "$run_id" "$lane_id" "$ordinal" "$content_sha256")" || return
    target_candidate="$(jq -c --arg claim "$claim_key" --arg id "$candidate_id" \
      '.claim_key=$claim | .candidate_id=$id' <<<"$target_candidate")" || return
    candidate_event="$(rehash_event "$(jq -c --argjson candidate "$target_candidate" \
      '.payload={candidate:$candidate}' <<<"$candidate_event")")" || return
    result_event="$(rehash_event "$(sed -n '4p' "$events" | jq -c --arg id "$candidate_id" \
      '.payload.lane_result.candidates=[$id]')")" || return
    finding_event="$(sed -n '5p' "$events")"
    target_finding="$(jq -c --argjson evidence "$target_pointer" --arg path "$path" \
      --arg anchor "$target_anchor" --arg claim "$claim_key" --arg id "$candidate_id" \
      '.payload.findings[0] | .evidence=$evidence | .path=$path | .anchor_sha256=$anchor |
      .claim_key=$claim | .candidate_ids=[$id]' <<<"$finding_event")" || return
    review_key="$(jq -r '.review_key' <<<"$finding_event")"
    finding_id="$(review_runtime_v2_finding_id "$target_finding" 'acme/widgets' "$review_key")" || return
    finding_event="$(rehash_event "$(jq -c --argjson finding "$target_finding" --arg id "$finding_id" \
      '.payload.findings[0]=($finding | .finding_id=$id)' <<<"$finding_event")")" || return
    { sed -n '1,2p' "$events"; printf '%s\n' "$candidate_event" "$result_event" "$finding_event"; \
      sed -n '6p' "$events"; } >"$destination"
  }

  target_path='src/crlf.txt'
  target_line=1
  target_events="$root/events-crlf-anchor.jsonl"
  write_target_evidence_events "$target_path" "$target_line" "$target_events"
  output="$(review_runtime_receipt "$target_events" "$config" "$repo" 2>/dev/null)"
  rc=$?
  assert_eq 'producer anchors CRLF line bytes from raw Git blob' '0' "$rc"

  target_path='src/filtered.txt'
  target_events="$root/events-filtered-raw-blob.jsonl"
  target_receipt="$root/receipt-filtered-raw-blob.json"
  write_target_evidence_events "$target_path" 1 "$target_events"
  working_hash="$(review_runtime_sha256 <"$repo/$target_path")"
  raw_hash="$content_sha256"
  assert_eq 'filter fixture working-tree bytes differ from raw Git blob' 'different' \
    "$([ "$working_hash" = "$raw_hash" ] && printf same || printf different)"
  output="$(review_runtime_receipt "$target_events" "$config" "$repo" 2>/dev/null)"
  rc=$?
  assert_eq 'producer ignores clean/smudge and attributes when anchoring raw Git blob' '0' "$rc"
  printf '%s\n' "$output" >"$target_receipt"
  output="$(review_runtime_validate_delta_receipt_files \
    "$target_receipt" "$target_events" "$config" "$repo" 2>/dev/null)"
  rc=$?
  assert_eq 'file validator accepts raw Git blob receipt without stdout' '0|' "$rc|$output"

  output="$(KC_PR_FLOW_MAX_EVIDENCE_BYTES=1 \
    review_runtime_receipt "$target_events" "$config" "$repo" 2>/dev/null)"
  rc=$?
  assert_not_zero 'producer rejects raw Git blobs over the evidence limit' "$rc"
  assert_eq 'oversize producer emits no receipt' '' "$output"
  output="$(KC_PR_FLOW_MAX_EVIDENCE_BYTES=1 review_runtime_validate_delta_receipt_files \
    "$target_receipt" "$target_events" "$config" "$repo" 2>/dev/null)"
  rc=$?
  assert_not_zero 'file validator rejects raw Git blobs over the evidence limit' "$rc"
  assert_eq 'oversize file validator emits no stdout' '' "$output"

  unset -f assert_identity_rejected write_subject_evidence_pair_events write_target_evidence_events
}

if [ "$CASE_FILTER" = 's01-inertness' ]; then
  if declare -F run_s01_inertness_tests >/dev/null; then
    run_s01_inertness_tests
  else
    fail 'runtime suite owns the S01 inertness contract'
  fi
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit $?
fi

if [ "$CASE_FILTER" = 'delta-receipt-identity' ]; then
  run_delta_receipt_identity_tests
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit $?
fi

if [ "$CASE_FILTER" = 'delta-receipt-files' ]; then
  run_delta_receipt_file_validator_tests
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit $?
fi

if [ "$CASE_FILTER" = 'delta-receipt-contract' ]; then
  run_delta_receipt_contract_tests
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit $?
fi

if [ "$CASE_FILTER" = 'delta-receipt-happy-path' ]; then
  run_delta_receipt_happy_path_tests
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit $?
fi

if [ "$CASE_FILTER" = 'all' ]; then
  run_s01_inertness_tests
  run_delta_receipt_contract_tests
  run_delta_receipt_file_validator_tests
  run_delta_receipt_identity_tests
fi

run_merge_readiness_tests() {
  local receipt="$1" ready_policy="$2" blocked_policy="$3" repo="$4"
  local base_sha="$5" head_sha="$6" config_hash="$7" review_key="$8" run_id="$9"
  local identity="${10}" producer_decision="${11}"
  local observations input_file output stderr_file rc expected_hash binding
  local stub_dir call_ledger stub_command status surface mutated reason invalid_policy
  local other_sha duplicate_input malformed_input noncanonical_input incomplete_policy
  local legacy_input legacy_file legacy_mutated legacy_case

  observations="$(jq -S -c -n --arg head_sha "$head_sha" '
    {
      schema:"kc-pr-flow.merge-readiness-observations/v1",
      observed_head_sha:$head_sha,
      ci:{
        required:true,status:"PASS",head_sha:$head_sha,
        evidence_sha256:"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
      },
      tests:{
        required:true,status:"PASS",head_sha:$head_sha,
        evidence_sha256:"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
      }
    }')"

  stub_dir="$TEST_INPUT_ROOT/merge-readiness-stubs"
  call_ledger="$TEST_INPUT_ROOT/merge-readiness-call-ledger"
  mkdir -p "$stub_dir"
  : >"$call_ledger"
  for stub_command in gh curl wget nc ssh; do
    printf '%s\n' \
      '#!/bin/sh' \
      'printf "%s\n" "$(basename "$0") $*" >>"$MERGE_READINESS_CALL_LEDGER"' \
      'exit 97' >"$stub_dir/$stub_command"
    chmod +x "$stub_dir/$stub_command"
  done
  export MERGE_READINESS_CALL_LEDGER="$call_ledger"

  input_file="$TEST_INPUT_ROOT/merge-readiness-observations.json"
  stderr_file="$TEST_INPUT_ROOT/merge-readiness-positive.stderr"
  printf '%s\n' "$observations" >"$input_file"
  output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
    --observations-file "$input_file" --event-file "$receipt" \
    --policy-file "$ready_policy" --repo-worktree "$repo" \
    --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
    --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id" \
    2>"$stderr_file")"
  rc=$?
  assert_eq "observation-only decide-merge-readiness command exists" "0" "$rc"
  assert_eq "real producer positive exact-head evidence is READY" "READY" \
    "$(jq -r '.verdict // empty' <<<"$output" 2>/dev/null)"
  assert_eq "real producer positive exact-head confidence is HIGH" "HIGH" \
    "$(jq -r '.confidence // empty' <<<"$output" 2>/dev/null)"
  assert_eq "positive decision has one canonical reason" "all-required-evidence-positive" \
    "$(jq -r '.reason_codes | join(",")' <<<"$output" 2>/dev/null)"
  assert_eq "merge readiness has the closed output schema" \
    "advisory_only,confidence,input_sha256,reason_codes,review_identity,schema,verdict" \
    "$(jq -r 'keys | sort | join(",")' <<<"$output" 2>/dev/null)"
  assert_eq "merge readiness decision is advisory only" "true" \
    "$(jq -r '.advisory_only' <<<"$output" 2>/dev/null)"
  assert_eq "merge readiness retains exact review identity" "$identity" \
    "$(jq -S -c '.review_identity' <<<"$output" 2>/dev/null)"
  binding="$(jq -S -c -n --argjson observations "$observations" \
    --argjson review_decision "$producer_decision" '
    {
      schema:"kc-pr-flow.merge-readiness-binding/v1",
      observations:$observations,
      review_decision:$review_decision
    }')"
  expected_hash="$(sha256_text "$binding")"
  assert_eq "merge readiness binds observations and exact producer decision" "$expected_hash" \
    "$(jq -r '.input_sha256' <<<"$output" 2>/dev/null)"

  noncanonical_input="$(jq '
    {
      tests:.tests,
      ci:.ci,
      observed_head_sha:.observed_head_sha,
      schema:.schema
    }' <<<"$observations")"
  printf '%s\n' "$noncanonical_input" >"$input_file"
  assert_eq "precondition: reordered pretty input has the same canonical value" \
    "$observations" "$(jq -S -c . "$input_file")"
  output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
    --observations-file "$input_file" --event-file "$receipt" \
    --policy-file "$ready_policy" --repo-worktree "$repo" \
    --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
    --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
  assert_eq "input binding normalizes key order and whitespace" "$expected_hash" \
    "$(jq -r '.input_sha256' <<<"$output" 2>/dev/null)"

  mutated="$(jq -S -c '.ci.required=false | .ci.status="NOT_REQUIRED" |
    .tests.required=false | .tests.status="NOT_REQUIRED"' <<<"$observations")"
  printf '%s\n' "$mutated" >"$input_file"
  output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
    --observations-file "$input_file" --event-file "$receipt" \
    --policy-file "$ready_policy" --repo-worktree "$repo" \
    --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
    --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
  assert_eq "non-required evidence is positive only when explicitly NOT_REQUIRED" \
    "READY|HIGH|all-required-evidence-positive" \
    "$(jq -r '[.verdict,.confidence,(.reason_codes|join(","))] | join("|")' <<<"$output")"

  for surface in ci tests; do
    mutated="$(jq -S -c --arg surface "$surface" \
      '.[$surface].status="FAIL"' <<<"$observations")"
    printf '%s\n' "$mutated" >"$input_file"
    output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
      --observations-file "$input_file" --event-file "$receipt" \
      --policy-file "$ready_policy" --repo-worktree "$repo" \
      --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
      --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
    assert_eq "$surface failure is decisively NOT_READY" "NOT_READY|HIGH|$surface-failed" \
      "$(jq -r '[.verdict,.confidence,(.reason_codes|join(","))] | join("|")' <<<"$output")"
  done

  printf '%s\n' "$observations" >"$input_file"
  output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
    --observations-file "$input_file" --event-file "$receipt" \
    --policy-file "$blocked_policy" --repo-worktree "$repo" \
    --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
    --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
  assert_eq "producer-derived confirmed review blocker is decisively NOT_READY" \
    "NOT_READY|HIGH|review-blocked" \
    "$(jq -r '[.verdict,.confidence,(.reason_codes|join(","))] | join("|")' <<<"$output")"

  mutated="$(jq -S -c '.ci.status="FAIL" | .tests.status="FAIL"' <<<"$observations")"
  printf '%s\n' "$mutated" >"$input_file"
  output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
    --observations-file "$input_file" --event-file "$receipt" \
    --policy-file "$blocked_policy" --repo-worktree "$repo" \
    --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
    --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
  assert_eq "multiple decisive negatives emit sorted unique reasons" \
    "ci-failed,review-blocked,tests-failed" \
    "$(jq -r '.reason_codes | join(",")' <<<"$output")"

  mutated="$(jq -S -c '.ci.status="FAIL" | .tests.status="PENDING"' <<<"$observations")"
  printf '%s\n' "$mutated" >"$input_file"
  output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
    --observations-file "$input_file" --event-file "$receipt" \
    --policy-file "$ready_policy" --repo-worktree "$repo" \
    --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
    --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
  assert_eq "an exact-head negative outranks another pending signal" \
    "NOT_READY|HIGH|ci-failed" \
    "$(jq -r '[.verdict,.confidence,(.reason_codes|join(","))] | join("|")' <<<"$output")"

  for surface in ci tests; do
    for status in PENDING UNKNOWN UNAVAILABLE; do
      mutated="$(jq -S -c --arg surface "$surface" --arg status "$status" \
        '.[$surface].status=$status' <<<"$observations")"
      printf '%s\n' "$mutated" >"$input_file"
      output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
        --observations-file "$input_file" --event-file "$receipt" \
        --policy-file "$ready_policy" --repo-worktree "$repo" \
        --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
        --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
      assert_eq "$surface $status is incomplete rather than positive" \
        "UNKNOWN|LOW|$surface-incomplete" \
        "$(jq -r '[.verdict,.confidence,(.reason_codes|join(","))] | join("|")' <<<"$output")"
    done
  done

  incomplete_policy="$TEST_INPUT_ROOT/merge-readiness-incomplete-policy.json"
  jq -S -c '.confirmed_blocker_refs=[]' "$blocked_policy" >"$incomplete_policy"
  printf '%s\n' "$observations" >"$input_file"
  output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
    --observations-file "$input_file" --event-file "$receipt" \
    --policy-file "$incomplete_policy" --repo-worktree "$repo" \
    --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
    --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
  assert_eq "producer-derived incomplete typed review is UNKNOWN" "UNKNOWN|LOW|review-incomplete" \
    "$(jq -r '[.verdict,.confidence,(.reason_codes|join(","))] | join("|")' <<<"$output")"

  other_sha="1111111111111111111111111111111111111111"
  for surface in observed_head_sha ci tests; do
    if [ "$surface" = observed_head_sha ]; then
      mutated="$(jq -S -c --arg sha "$other_sha" '.observed_head_sha=$sha' <<<"$observations")"
    else
      mutated="$(jq -S -c --arg surface "$surface" --arg sha "$other_sha" \
        '.[$surface].head_sha=$sha' <<<"$observations")"
    fi
    printf '%s\n' "$mutated" >"$input_file"
    output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
      --observations-file "$input_file" --event-file "$receipt" \
      --policy-file "$ready_policy" --repo-worktree "$repo" \
      --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
      --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
    assert_eq "$surface head mutation is UNKNOWN" \
      "UNKNOWN|LOW|head-or-identity-mismatch" \
      "$(jq -r '[.verdict,.confidence,(.reason_codes|join(","))] | join("|")' <<<"$output")"
  done

  for reason in coordinated-stale-key unsatisfied-clean satisfied-incomplete duplicate-lane \
    invalid-recorded-at empty-obligations malformed-pointer pointer-identity-drift \
    evidence-verification-failure; do
    invalid_policy="$TEST_INPUT_ROOT/merge-readiness-$reason-policy.json"
    case "$reason" in
      coordinated-stale-key)
        jq -S -c '.review_identity.repository="other/repo"' "$ready_policy" >"$invalid_policy"
        ;;
      unsatisfied-clean)
        jq -S -c '.obligations[] |= if .capability=="required-gap" then
          .fallback={status:"unavailable",result:null} |
          .terminal_state="clean"
          else . end' "$ready_policy" >"$invalid_policy"
        ;;
      satisfied-incomplete)
        jq -S -c '.obligations[] |= if .capability=="types" then
          .terminal_state="incomplete_required"
          else . end' "$ready_policy" >"$invalid_policy"
        ;;
      duplicate-lane)
        jq -S -c '.obligations[] |= if .capability=="types" then
          .adapter_attempts[1].lane_result_ref=.adapter_attempts[0].lane_result_ref
          else . end' "$ready_policy" >"$invalid_policy"
        ;;
      invalid-recorded-at)
        jq -S -c '.obligations[] |= if .capability=="manual-clean" then
          .fallback.result.recorded_at="2026-99-99T99:99:99Z"
          else . end' "$ready_policy" >"$invalid_policy"
        ;;
      empty-obligations)
        jq -S -c '.obligations=[]' "$ready_policy" >"$invalid_policy"
        ;;
      malformed-pointer)
        jq -S -c '.obligations[] |= if .capability=="manual-clean" then
          .fallback.result.evidence[0].unexpected=true
          else . end' "$ready_policy" >"$invalid_policy"
        ;;
      pointer-identity-drift)
        jq -S -c --arg sha "$other_sha" '.obligations[] |= if .capability=="manual-clean" then
          .fallback.result.evidence[0].head_sha=$sha
          else . end' "$ready_policy" >"$invalid_policy"
        ;;
      evidence-verification-failure)
        jq -S -c '.obligations[] |= if .capability=="manual-clean" then
          .fallback.result.evidence[0].content_sha256=
            "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
          else . end' "$ready_policy" >"$invalid_policy"
        ;;
    esac
    printf '%s\n' "$observations" >"$input_file"
    output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
      --observations-file "$input_file" --event-file "$receipt" \
      --policy-file "$invalid_policy" --repo-worktree "$repo" \
      --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
      --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
    assert_eq "producer-inconsistent $reason source fails closed" \
      "UNKNOWN|LOW|invalid-review-evidence" \
      "$(jq -r '[.verdict,.confidence,(.reason_codes|join(","))] | join("|")' <<<"$output")"
  done

  for reason in unknown-key malformed-hash invalid-required-status caller-decision-member unknown-status; do
    case "$reason" in
      unknown-key) mutated="$(jq -S -c '.unexpected=true' <<<"$observations")" ;;
      malformed-hash) mutated="$(jq -S -c '.ci.evidence_sha256="bad"' <<<"$observations")" ;;
      invalid-required-status) mutated="$(jq -S -c '.ci.status="NOT_REQUIRED"' <<<"$observations")" ;;
      caller-decision-member) mutated="$(jq -S -c --argjson decision "$producer_decision" \
        '.review_decision=$decision' <<<"$observations")" ;;
      unknown-status) mutated="$(jq -S -c '.tests.status="GREEN"' <<<"$observations")" ;;
    esac
    printf '%s\n' "$mutated" >"$input_file"
    output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
      --observations-file "$input_file" --event-file "$receipt" \
      --policy-file "$ready_policy" --repo-worktree "$repo" \
      --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
      --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
    assert_eq "$reason fails closed as invalid input" "UNKNOWN|LOW|invalid-input" \
      "$(jq -r '[.verdict,.confidence,(.reason_codes|join(","))] | join("|")' <<<"$output")"
    assert_eq "$reason cannot retain an unvalidated identity" "null|null" \
      "$(jq -r '[.review_identity,.input_sha256] | map(tostring) | join("|")' <<<"$output")"
  done

  duplicate_input="${observations#\{}"
  duplicate_input="{\"schema\":\"kc-pr-flow.merge-readiness-observations/v1\",$duplicate_input"
  printf '%s\n' "$duplicate_input" >"$input_file"
  output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
    --observations-file "$input_file" --event-file "$receipt" \
    --policy-file "$ready_policy" --repo-worktree "$repo" \
    --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
    --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
  assert_eq "duplicate JSON member fails closed" "UNKNOWN|LOW|invalid-input" \
    "$(jq -r '[.verdict,.confidence,(.reason_codes|join(","))] | join("|")' <<<"$output")"

  malformed_input='{'
  printf '%s\n' "$malformed_input" >"$input_file"
  output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
    --observations-file "$input_file" --event-file "$receipt" \
    --policy-file "$ready_policy" --repo-worktree "$repo" \
    --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
    --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
  assert_eq "malformed bounded JSON fails closed" "UNKNOWN|LOW|invalid-input" \
    "$(jq -r '[.verdict,.confidence,(.reason_codes|join(","))] | join("|")' <<<"$output")"

  mutated="$(jq -S -c '.ci.required=false' <<<"$observations")"
  printf '%s\n' "$mutated" >"$input_file"
  output="$(PATH="$stub_dir:$PATH" bash "$RUNTIME" decide-merge-readiness \
    --observations-file "$input_file" --event-file "$receipt" \
    --policy-file "$ready_policy" --repo-worktree "$repo" \
    --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$base_sha" --head "$head_sha" \
    --config-hash "$config_hash" --review-key "$review_key" --run-id "$run_id")"
  assert_eq "otherwise unreachable non-required PASS is inconsistent" \
    "UNKNOWN|LOW|inconsistent-input" \
    "$(jq -r '[.verdict,.confidence,(.reason_codes|join(","))] | join("|")' <<<"$output")"

  legacy_input="$(jq -S -c -n --argjson identity "$identity" \
    --argjson decision "$producer_decision" --arg head_sha "$head_sha" '
    {
      schema:"kc-pr-flow.merge-readiness-input/v1",
      review_identity:$identity,
      observed_head_sha:$head_sha,
      ci:{
        required:true,status:"PASS",head_sha:$head_sha,
        evidence_sha256:"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
      },
      tests:{
        required:true,status:"PASS",head_sha:$head_sha,
        evidence_sha256:"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
      },
      review_decision:$decision
    }')"
  legacy_file="$TEST_INPUT_ROOT/merge-readiness-legacy-input.json"
  for legacy_case in duplicate-lane invalid-recorded-at empty-capabilities; do
    case "$legacy_case" in
      duplicate-lane)
        legacy_mutated="$(jq -S -c '
          .review_decision.capabilities[] |= if .capability=="types" then
            .adapter_attempts[1].lane_result_ref=.adapter_attempts[0].lane_result_ref
            else . end' <<<"$legacy_input")"
        ;;
      invalid-recorded-at)
        legacy_mutated="$(jq -S -c '
          .review_decision.capabilities[] |= if .capability=="manual-clean" then
            .fallback.result.recorded_at="2026-99-99T99:99:99Z"
            else . end' <<<"$legacy_input")"
        ;;
      empty-capabilities)
        legacy_mutated="$(jq -S -c '
          .review_decision.capabilities=[] |
          .review_decision.capability_gap_refs=[] |
          .review_decision.confirmation_input.gap_refs=[]
        ' <<<"$legacy_input")"
        ;;
    esac
    printf '%s\n' "$legacy_mutated" >"$legacy_file"
    output="$(bash "$RUNTIME" decide-merge-readiness --input-file "$legacy_file" 2>/dev/null)"
    rc=$?
    assert_eq "legacy caller decision $legacy_case is refused at the command boundary" "2" "$rc"
  done

  # Regression-only transport invariant, not behavior RED evidence: the old
  # adapter also performed no transport calls. Local git is intentionally not
  # stubbed because the reused producer verifies evidence in the supplied repo.
  assert_eq "merge-readiness CLI performs no network, GitHub, post, or merge call" \
    "" "$(cat "$call_ledger")"
}

run_interactive_decision_tests() {
  local receipt policy repo output rc before_hash after_hash
  local measurement_target measurement receipt_content receipt_id
  local control_file control_artifact control_hash raw_event_hash
  local canonical_decision treatment_units control_units measurement_binding binding_hash
  local run_id content_hash anchor candidate_id merge_key finding_id pointer candidate
  local task usage result finding behavior_hashes start lane_started observed lane_finished synthesized finished
  local types_task_one types_task_two types_result_one types_result_two types_started_one types_started_two types_finished_one types_finished_two
  local interactive_head interactive_base interactive_key identity manual_clean manual_na review_config
  local CONFIG_HASH
  local bad_policy bad_receipt mutated identity_case bad_repo bad_pr bad_base bad_head bad_config bad_key bad_run
  local mode merge_policy merge_manual merge_decision
  mode="${1:-full}"
  receipt="$TEST_INPUT_ROOT/interactive-terminal.jsonl"
  policy="$TEST_INPUT_ROOT/interactive-policy.json"
  repo="$TEST_INPUT_ROOT/interactive-repo"
  run_id='run-interactive-terminal'
  review_config="$(review_runtime_config_canonical lite mixed false false false false \
    'manual-clean,manual-na,required-gap,security,types')"
  CONFIG_HASH="$(printf '%s' "$review_config" | review_runtime_sha256)"
  mkdir -p "$repo/src"
  git -C "$repo" init -q
  printf 'evidence bound review\n' >"$repo/src/review.sh"
  git -C "$repo" add src/review.sh
  git -C "$repo" -c user.name='Runtime Test' -c user.email='runtime@example.invalid' commit -qm seed
  git -C "$repo" remote add origin 'https://github.com/acme/widgets.git'
  interactive_head="$(git -C "$repo" rev-parse HEAD)"
  interactive_base="$interactive_head"
  interactive_key="$(sha256_text "$REPOSITORY|$PR_NUMBER|$interactive_base|$interactive_head|$CONFIG_HASH")"
  content_hash="$(review_runtime_sha256 <"$repo/src/review.sh")"
  anchor='eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
  candidate_id="$(review_runtime_candidate_id "$run_id" security-1 1 "$content_hash")"
  pointer="$(jq -S -c -n --arg key "$interactive_key" --arg repo "$REPOSITORY" \
    --arg base "$interactive_base" --arg head "$interactive_head" --arg hash "$content_hash" \
    '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",review_key:$key,repository:$repo,
      base_sha:$base,head_sha:$head,object_sha:$head,path:"src/review.sh",side:"RIGHT",line:1,
      locator:"review-anchor",content_sha256:$hash}')"
  candidate="$(jq -S -c -n --arg id "$candidate_id" --arg key "$interactive_key" \
    --arg run "$run_id" --arg anchor "$anchor" --argjson evidence "$pointer" \
    '{schema:"kc-pr-flow.review-candidate/v1",candidate_id:$id,run_id:$run,review_key:$key,
      lane_id:"security-1",ordinal:1,path:"src/review.sh",side:"RIGHT",anchor_sha256:$anchor,
      category:"security",claim_key:"unchecked-boundary",evidence:$evidence}')"
  task="$(jq -S -c -n --arg run "$run_id" --arg key "$interactive_key" \
    --arg repo "$REPOSITORY" --arg base "$interactive_base" --arg head "$interactive_head" --arg config "$CONFIG_HASH" \
    '{schema:"kc-pr-flow.review-task/v1",run_id:$run,review_key:$key,lane_id:"security-1",
      capability:"security",repository:$repo,pr_number:42,base_sha:$base,head_sha:$head,config_hash:$config}')"
  usage='{"input_tokens":100,"output_tokens":25,"provenance":"reported","provider_family":"claude","scope":"lane","total_tokens":125}'
  result="$(jq -S -c -n --arg run "$run_id" --arg key "$interactive_key" \
    --arg id "$candidate_id" --argjson usage "$usage" \
    '{schema:"kc-pr-flow.lane-result/v1",run_id:$run,review_key:$key,lane_id:"security-1",
      capability:"security",terminal_status:"succeeded",candidates:[$id],usage:$usage,provider_family:"claude"}')"
  merge_key="src/review.sh|RIGHT|$content_hash|security|unchecked-boundary"
  finding_id="$(review_runtime_finding_id "$interactive_key" "$merge_key")"
  finding="$(jq -S -c -n --arg id "$finding_id" --arg key "$interactive_key" \
    --arg merge "$merge_key" --arg anchor "$anchor" --arg candidate "$candidate_id" \
    --argjson evidence "$pointer" \
    '{schema:"kc-pr-flow.review-finding/v1",finding_id:$id,review_key:$key,merge_key:$merge,
      path:"src/review.sh",side:"RIGHT",anchor_sha256:$anchor,category:"security",
      claim_key:"unchecked-boundary",candidate_ids:[$candidate],evidence:$evidence}')"
  behavior_hashes="$(jq -S -c -n --arg hash "$content_hash" \
    '{body_sha256:$hash,confirmation_input_sha256:$hash,event_sha256:$hash,
      github_call_log_sha256:$hash,inline_comments_sha256:$hash,options_sha256:$hash}')"
  types_task_one="$(jq -c '.lane_id="types-1" | .capability="types"' <<<"$task")"
  types_task_two="$(jq -c '.lane_id="types-2" | .capability="types"' <<<"$task")"
  types_result_one="$(jq -c '.lane_id="types-1" | .capability="types" | .terminal_status="failed" | .candidates=[]' <<<"$result")"
  types_result_two="$(jq -c '.lane_id="types-2" | .capability="types" | .terminal_status="succeeded" | .candidates=[]' <<<"$result")"
  start="$(review_runtime_build_event "$run_id" "$interactive_key" "$REPOSITORY" "$PR_NUMBER" \
    "$interactive_base" "$interactive_head" "$CONFIG_HASH" 1 "$OCCURRED_AT" run.started '{}')"
  lane_started="$(review_runtime_build_event "$run_id" "$interactive_key" "$REPOSITORY" "$PR_NUMBER" \
    "$interactive_base" "$interactive_head" "$CONFIG_HASH" 2 "$OCCURRED_AT" lane.started \
    "$(jq -S -c -n --argjson value "$task" '{review_task:$value}')")"
  observed="$(review_runtime_build_event "$run_id" "$interactive_key" "$REPOSITORY" "$PR_NUMBER" \
    "$interactive_base" "$interactive_head" "$CONFIG_HASH" 3 "$OCCURRED_AT" finding.observed \
    "$(jq -S -c -n --argjson value "$candidate" '{candidate:$value}')")"
  lane_finished="$(review_runtime_build_event "$run_id" "$interactive_key" "$REPOSITORY" "$PR_NUMBER" \
    "$interactive_base" "$interactive_head" "$CONFIG_HASH" 4 "$OCCURRED_AT" lane.finished \
    "$(jq -S -c -n --argjson value "$result" '{lane_result:$value}')")"
  types_started_one="$(review_runtime_build_event "$run_id" "$interactive_key" "$REPOSITORY" "$PR_NUMBER" \
    "$interactive_base" "$interactive_head" "$CONFIG_HASH" 5 "$OCCURRED_AT" lane.started \
    "$(jq -S -c -n --argjson value "$types_task_one" '{review_task:$value}')")"
  types_finished_one="$(review_runtime_build_event "$run_id" "$interactive_key" "$REPOSITORY" "$PR_NUMBER" \
    "$interactive_base" "$interactive_head" "$CONFIG_HASH" 6 "$OCCURRED_AT" lane.finished \
    "$(jq -S -c -n --argjson value "$types_result_one" '{lane_result:$value}')")"
  types_started_two="$(review_runtime_build_event "$run_id" "$interactive_key" "$REPOSITORY" "$PR_NUMBER" \
    "$interactive_base" "$interactive_head" "$CONFIG_HASH" 7 "$OCCURRED_AT" lane.started \
    "$(jq -S -c -n --argjson value "$types_task_two" '{review_task:$value}')")"
  types_finished_two="$(review_runtime_build_event "$run_id" "$interactive_key" "$REPOSITORY" "$PR_NUMBER" \
    "$interactive_base" "$interactive_head" "$CONFIG_HASH" 8 "$OCCURRED_AT" lane.finished \
    "$(jq -S -c -n --argjson value "$types_result_two" '{lane_result:$value}')")"
  synthesized="$(review_runtime_build_event "$run_id" "$interactive_key" "$REPOSITORY" "$PR_NUMBER" \
    "$interactive_base" "$interactive_head" "$CONFIG_HASH" 9 "$OCCURRED_AT" synthesis.finished \
    "$(jq -S -c -n --argjson value "$finding" '{findings:[$value],uncertain_candidate_ids:[]}')")"
  finished="$(review_runtime_build_event "$run_id" "$interactive_key" "$REPOSITORY" "$PR_NUMBER" \
    "$interactive_base" "$interactive_head" "$CONFIG_HASH" 10 "$OCCURRED_AT" run.finished \
    "$(jq -S -c -n --argjson value "$behavior_hashes" '{behavior_hashes:$value}')")"
  printf '%s\n' "$start" "$lane_started" "$observed" "$lane_finished" \
    "$types_started_one" "$types_finished_one" "$types_started_two" "$types_finished_two" \
    "$synthesized" "$finished" >"$receipt"

  identity="$(jq -S -c -n --arg repo "$REPOSITORY" --argjson pr "$PR_NUMBER" \
    --arg base "$interactive_base" --arg head "$interactive_head" --arg config "$CONFIG_HASH" \
    --arg key "$interactive_key" --arg run "$run_id" \
    '{repository:$repo,pr_number:$pr,base_sha:$base,head_sha:$head,config_hash:$config,review_key:$key,run_id:$run}')"
  manual_clean="$(jq -S -c -n --argjson identity "$identity" --argjson evidence "$pointer" \
    '{schema:"kc-pr-flow.manual-capability-result/v1",review_identity:$identity,capability:"manual-clean",
      terminal_assessment:"clean",candidate_ids:[],evidence:[$evidence],recorded_by:"interactive-human",
      recorded_at:"2026-07-23T00:00:00Z"}')"
  manual_na="$(jq -S -c -n --argjson identity "$identity" --argjson evidence "$pointer" \
    '{schema:"kc-pr-flow.manual-capability-result/v1",review_identity:$identity,capability:"manual-na",
      terminal_assessment:"evidence_backed_na",candidate_ids:[],evidence:[$evidence],recorded_by:"interactive-human",
      recorded_at:"2026-07-23T00:00:00Z"}')"
  jq -S -c -n --argjson identity "$identity" --argjson evidence "$pointer" \
    --argjson review_config "$review_config" \
    --argjson manual_clean "$manual_clean" --argjson manual_na "$manual_na" --arg blocker "$finding_id" '
    {
      schema:"kc-pr-flow.capability-policy/v1",
      review_identity:$identity,
      review_config:$review_config,
      confirmed_blocker_refs:[$blocker],
      obligations:[
        {capability:"security",required:true,activation_condition:"configured",
         adapter_attempts:[{ordinal:1,result:"succeeded",lane_result_ref:"security-1"}],
         evidence:[$evidence],fallback:{status:"not_needed",result:null},terminal_state:"findings"},
        {capability:"types",required:true,activation_condition:"configured",
         adapter_attempts:[{ordinal:1,result:"transient_failure",lane_result_ref:"types-1"},
                           {ordinal:2,result:"succeeded",lane_result_ref:"types-2"}],
         evidence:[$evidence],fallback:{status:"not_needed",result:null},terminal_state:"clean"},
        {capability:"manual-clean",required:true,activation_condition:"configured",adapter_attempts:[],
         evidence:[],fallback:{status:"provided",result:$manual_clean},terminal_state:"clean"},
        {capability:"manual-na",required:true,activation_condition:"configured",adapter_attempts:[],
         evidence:[],fallback:{status:"provided",result:$manual_na},terminal_state:"evidence_backed_na"},
        {capability:"required-gap",required:true,activation_condition:"configured",adapter_attempts:[],
         evidence:[],fallback:{status:"unavailable",result:null},terminal_state:"incomplete_required"},
        {capability:"optional-gap",required:false,activation_condition:"observed_optional",adapter_attempts:[],
         evidence:[],fallback:{status:"unavailable",result:null},terminal_state:"incomplete_optional"}
      ]
    }' >"$policy"
  before_hash="$(sha256_text "$(cat "$receipt")")"
  output="$(bash "$RUNTIME" rehydrate-interactive \
    --event-file "$receipt" --policy-file "$policy" --repo-worktree "$repo" \
    --repo "$REPOSITORY" --pr "$PR_NUMBER" \
    --base "$interactive_base" --head "$interactive_head" \
    --config-hash "$CONFIG_HASH" --review-key "$interactive_key" \
    --run-id run-interactive-terminal 2>&1)"
  rc=$?
  assert_eq "rehydrate-interactive command exists" "0" "$rc"
  assert_eq "interactive decision uses the closed schema" \
    "kc-pr-flow.interactive-collation-decision/v1" \
    "$(jq -r '.schema // empty' <<<"$output" 2>/dev/null)"
  assert_eq "decision has exact closed top-level keys" \
    "approve_eligible,capabilities,capability_gap_refs,confirmation_input,confirmed_blocker_refs,coverage,effective_event,mode,review_identity,schema" \
    "$(jq -r 'keys | sort | join(",")' <<<"$output")"
  assert_eq "required gap makes coverage incomplete" "incomplete" "$(jq -r '.coverage' <<<"$output")"
  assert_eq "blocker precedence selects REQUEST_CHANGES" "REQUEST_CHANGES" "$(jq -r '.effective_event' <<<"$output")"
  assert_eq "blocker prevents approval" "false" "$(jq -r '.approve_eligible' <<<"$output")"
  assert_eq "all five terminal states are reachable" \
    "clean,evidence_backed_na,findings,incomplete_optional,incomplete_required" \
    "$(jq -r '[.capabilities[].terminal_state] | unique | sort | join(",")' <<<"$output")"
  assert_eq "optional failure remains visible without becoming a required gap" \
    "optional-gap|false|incomplete_optional" \
    "$(jq -r '.capabilities[] | select(.capability=="optional-gap") | [.capability,.required,.terminal_state] | join("|")' <<<"$output")"
  assert_eq "transient failure has exactly one retry and no inferred result" \
    "transient_failure,succeeded" \
    "$(jq -r '.capabilities[] | select(.capability=="types") | [.adapter_attempts[].result] | join(",")' <<<"$output")"
  assert_eq "valid evidence-bound manual fallback satisfies clean" "clean" \
    "$(jq -r '.capabilities[] | select(.capability=="manual-clean") | .terminal_state' <<<"$output")"
  assert_eq "decision retains exact run identity" "run-interactive-terminal" "$(jq -r '.review_identity.run_id' <<<"$output")"
  assert_eq "confirmation input is derived from decision refs" \
    "$(jq -c '[.confirmed_blocker_refs,.capability_gap_refs]' <<<"$output")" \
    "$(jq -c '[.confirmation_input.blocker_refs,.confirmation_input.gap_refs]' <<<"$output")"
  if grep -E 'prompt|raw_(diff|output)|source_excerpt|line one|line two' <<<"$output" >/dev/null 2>&1; then
    fail "interactive decision persists forbidden raw content"
  else
    pass
  fi
  after_hash="$(sha256_text "$(cat "$receipt")")"
  assert_eq "rehydration never appends or rewrites the receipt" "$before_hash" "$after_hash"

  if [ "$mode" = 'merge-positive-only' ]; then
    merge_policy="$TEST_INPUT_ROOT/interactive-merge-ready-policy.json"
    merge_manual="$(jq -S -c '.capability="required-gap"' <<<"$manual_clean")"
    jq -S -c --argjson manual "$merge_manual" '
      .confirmed_blocker_refs=[] |
      .obligations[] |= if .capability=="required-gap" then
        .fallback={status:"provided",result:$manual} |
        .terminal_state="clean"
      else . end
    ' "$policy" >"$merge_policy"
    merge_decision="$(bash "$RUNTIME" rehydrate-interactive \
      --event-file "$receipt" --policy-file "$merge_policy" --repo-worktree "$repo" \
      --repo "$REPOSITORY" --pr "$PR_NUMBER" \
      --base "$interactive_base" --head "$interactive_head" \
      --config-hash "$CONFIG_HASH" --review-key "$interactive_key" \
      --run-id "$run_id" 2>&1)"
    rc=$?
    # Arrangement-only precondition: it proves the readiness matrix begins with
    # a successful real producer result and is not behavior RED evidence.
    assert_eq "precondition: merge-ready fixture is produced by terminal rehydration" "0" "$rc"
    run_merge_readiness_tests "$receipt" "$merge_policy" "$policy" "$repo" \
      "$interactive_base" "$interactive_head" "$CONFIG_HASH" "$interactive_key" \
      "$run_id" "$identity" "$merge_decision"
    return
  fi

  measurement_target="$TEST_INPUT_ROOT/interactive-measurement-target.json"
  control_file="$TEST_INPUT_ROOT/interactive-full-review-control.json"
  receipt_content="$(review_runtime_sha256 <"$receipt")"
  receipt_id="$(sha256_text "$run_id|$interactive_key|$receipt_content")"
  canonical_decision="$(jq -S -c . <<<"$output")"
  control_artifact="$(jq -S -c -n --argjson identity "$identity" --arg hash "$content_hash" '
    {
      schema:"kc-pr-flow.full-review-rerun-control/v1",
      pair_id:"interactive-terminal",review_identity:$identity,
      operation:"designed-full-review-rerun",counter:"canonical-artifact-bytes/v1",
      full_review_rerun_units:4096,artifact_sha256:$hash
    }')"
  printf '%s\n' "$control_artifact" >"$control_file"
  control_hash="$(sha256_text "$control_artifact")"
  raw_event_hash="$(review_runtime_sha256 <"$receipt")"
  treatment_units="$(LC_ALL=C printf '%s' "$canonical_decision" | wc -c | tr -d '[:space:]')"
  control_units="$(jq -r '.full_review_rerun_units' <<<"$control_artifact")"
  measurement_binding="$(jq -S -c -n \
    --arg raw_event_sha256 "$raw_event_hash" \
    --arg decision_sha256 "$(sha256_text "$canonical_decision")" \
    --arg control_sha256 "$control_hash" \
    --argjson treatment_units "$treatment_units" --argjson control_units "$control_units" '
    {
      schema:"kc-pr-flow.local-measurement-binding/v1",
      counter:"canonical-artifact-bytes/v1",
      raw_event_sha256:$raw_event_sha256,decision_sha256:$decision_sha256,
      full_review_control_sha256:$control_sha256,
      terminal_rehydration_units:$treatment_units,
      full_review_rerun_units:$control_units
    }')"
  binding_hash="$(printf '%s' "$measurement_binding" | jq -S -c '{
    counter,decision_sha256,full_review_control_sha256,
    full_review_rerun_units,raw_event_sha256,terminal_rehydration_units
  }' | review_runtime_sha256)"
  measurement_binding="$(jq -S -c --arg hash "$binding_hash" \
    '.measurement_binding_sha256=$hash' <<<"$measurement_binding")"
  jq -S -c -n --arg pair_id interactive-terminal \
    --arg repository "$REPOSITORY" --argjson pr_number "$PR_NUMBER" \
    --arg base_sha "$interactive_base" --arg head_sha "$interactive_head" \
    --arg config_hash "$CONFIG_HASH" --arg review_key "$interactive_key" \
    --arg run_id "$run_id" --arg receipt_id "$receipt_id" \
    --arg content_sha256 "$receipt_content" --argjson binding "$measurement_binding" '
    {
      schema:"kc-pr-flow.local-measurement-target/v1",pair_id:$pair_id,
      exact_head:{
        repository:$repository,pr_number:$pr_number,base_sha:$base_sha,
        head_sha:$head_sha,config_hash:$config_hash,review_key:$review_key
      },
      receipt:{
        schema:"kc-pr-flow.review-receipt-identity/v1",run_id:$run_id,
        review_key:$review_key,receipt_id:$receipt_id,content_sha256:$content_sha256
      },
      measurement_binding:$binding
    }' >"$measurement_target"
  measurement="$(bash "$BENCHMARK" measure-local --runtime "$RUNTIME" \
    --target "$measurement_target" --event-file "$receipt" --policy-file "$policy" \
    --control-file "$control_file" --repo-worktree "$repo")"
  assert_eq "local measurement executes the real interactive rehydration runtime" \
    "kc-pr-flow.interactive-collation-decision/v1" \
    "$(jq -r '.observations[0].decision.schema' <<<"$measurement")"
  assert_eq "local measurement binds the exact runtime receipt" "$receipt_id" \
    "$(jq -r '.observations[0].terminal_receipt_id' <<<"$measurement")"
  assert_eq "local measurement records only deterministic local work" \
    "canonical-artifact-bytes/v1|0|0" \
    "$(jq -r '.observations[0] | [.counter,.model_calls,.remote_calls] | join("|")' <<<"$measurement")"

  bad_policy="$TEST_INPUT_ROOT/no-blocker-policy.json"
  jq '.confirmed_blocker_refs=[]' "$policy" >"$bad_policy"
  output="$(bash "$RUNTIME" rehydrate-interactive --event-file "$receipt" --policy-file "$bad_policy" \
    --repo-worktree "$repo" --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$interactive_base" \
    --head "$interactive_head" --config-hash "$CONFIG_HASH" --review-key "$interactive_key" --run-id "$run_id")"
  assert_eq "required gap without blocker has COMMENT ceiling" "COMMENT" "$(jq -r '.effective_event' <<<"$output")"

  bad_receipt="$TEST_INPUT_ROOT/second-transient.jsonl"
  identity_case="$(rehash_event "$(jq -c '.payload.lane_result.terminal_status="failed"' <<<"$types_finished_two")")"
  { head -n 7 "$receipt"; printf '%s\n' "$identity_case"; tail -n +9 "$receipt"; } >"$bad_receipt"
  bad_policy="$TEST_INPUT_ROOT/second-transient-policy.json"
  jq '.obligations[] |= if .capability=="types" then
    .adapter_attempts[1].result="transient_failure" |
    .fallback={status:"unavailable",result:null} |
    .terminal_state="incomplete_required" |
    .evidence=[]
    else . end' "$policy" >"$bad_policy"
  output="$(bash "$RUNTIME" rehydrate-interactive --event-file "$bad_receipt" --policy-file "$bad_policy" \
    --repo-worktree "$repo" --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$interactive_base" \
    --head "$interactive_head" --config-hash "$CONFIG_HASH" --review-key "$interactive_key" --run-id "$run_id")"
  assert_eq "second transient failure closes after exactly one retry" "incomplete_required" \
    "$(jq -r '.capabilities[] | select(.capability=="types") | .terminal_state' <<<"$output")"

  for identity_case in repository pr base head config review_key run; do
    bad_repo="$REPOSITORY"; bad_pr="$PR_NUMBER"; bad_base="$interactive_base"; bad_head="$interactive_head"
    bad_config="$CONFIG_HASH"; bad_key="$interactive_key"; bad_run="$run_id"
    case "$identity_case" in
      repository) bad_repo='other/repo' ;;
      pr) bad_pr=43 ;;
      base) bad_base='1111111111111111111111111111111111111111' ;;
      head) bad_head='2222222222222222222222222222222222222222' ;;
      config) bad_config='eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee' ;;
      review_key) bad_key='ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' ;;
      run) bad_run='run-other' ;;
    esac
    bash "$RUNTIME" rehydrate-interactive --event-file "$receipt" --policy-file "$policy" \
      --repo-worktree "$repo" --repo "$bad_repo" --pr "$bad_pr" --base "$bad_base" \
      --head "$bad_head" --config-hash "$bad_config" --review-key "$bad_key" --run-id "$bad_run" >/dev/null 2>&1
    assert_eq "$identity_case identity mutation fails closed" "3" "$?"
  done

  for mutated in requiredness-downgrade activation-drift missing-obligation third-attempt missing-fallback-disposition invalid-fallback invalid-recorded-at fake-fallback-finding pointer pointer-base pointer-head pointer-review-key object content; do
    bad_policy="$TEST_INPUT_ROOT/$mutated-policy.json"
    case "$mutated" in
      requiredness-downgrade) jq '.obligations[] |= if .capability=="security" then .required=false else . end' "$policy" >"$bad_policy" ;;
      activation-drift) jq '.obligations[] |= if .capability=="security" then .activation_condition="optional" else . end' "$policy" >"$bad_policy" ;;
      missing-obligation) jq '.obligations |= map(select(.capability!="types"))' "$policy" >"$bad_policy" ;;
      third-attempt) jq '.obligations[] |= if .capability=="types" then .adapter_attempts += [{ordinal:3,result:"succeeded",lane_result_ref:"types-2"}] else . end' "$policy" >"$bad_policy" ;;
      missing-fallback-disposition) jq '.obligations[] |= if .capability=="required-gap" then .fallback={status:"not_needed",result:null} else . end' "$policy" >"$bad_policy" ;;
      invalid-fallback) jq '.obligations[] |= if .capability=="manual-clean" then .fallback.result.evidence=[] else . end' "$policy" >"$bad_policy" ;;
      invalid-recorded-at) jq '.obligations[] |= if .capability=="manual-clean" then .fallback.result.recorded_at="2026-99-99T99:99:99Z" else . end' "$policy" >"$bad_policy" ;;
      fake-fallback-finding) jq '.obligations[] |= if .capability=="manual-clean" then
        .terminal_state="findings" |
        .fallback.result.terminal_assessment="findings" |
        .fallback.result.candidate_ids=["ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"]
        else . end' "$policy" >"$bad_policy" ;;
      pointer) jq '.obligations[1].evidence[0].path="missing.sh"' "$policy" >"$bad_policy" ;;
      pointer-base) jq '.obligations[1].evidence[0].base_sha="1111111111111111111111111111111111111111"' "$policy" >"$bad_policy" ;;
      pointer-head) jq '.obligations[1].evidence[0].head_sha="2222222222222222222222222222222222222222"' "$policy" >"$bad_policy" ;;
      pointer-review-key) jq '.obligations[1].evidence[0].review_key="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"' "$policy" >"$bad_policy" ;;
      object) jq '.obligations[1].evidence[0].object_sha="1111111111111111111111111111111111111111"' "$policy" >"$bad_policy" ;;
      content) jq '.obligations[1].evidence[0].content_sha256="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"' "$policy" >"$bad_policy" ;;
    esac
    bash "$RUNTIME" rehydrate-interactive --event-file "$receipt" --policy-file "$bad_policy" \
      --repo-worktree "$repo" --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$interactive_base" \
      --head "$interactive_head" --config-hash "$CONFIG_HASH" --review-key "$interactive_key" --run-id "$run_id" >/dev/null 2>&1
    assert_eq "$mutated policy mutation fails closed" "3" "$?"
  done

  bad_receipt="$TEST_INPUT_ROOT/bad-event.jsonl"
  { head -n 9 "$receipt"; } >"$bad_receipt"
  bash "$RUNTIME" rehydrate-interactive --event-file "$bad_receipt" --policy-file "$policy" \
    --repo-worktree "$repo" --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$interactive_base" \
    --head "$interactive_head" --config-hash "$CONFIG_HASH" --review-key "$interactive_key" --run-id "$run_id" >/dev/null 2>&1
  assert_eq "incomplete event mutation fails closed" "3" "$?"

  for mutated in candidate finding; do
    bad_receipt="$TEST_INPUT_ROOT/bad-$mutated.jsonl"
    if [ "$mutated" = candidate ]; then
      identity_case="$(rehash_event "$(jq -c '.payload.candidate.candidate_id="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"' <<<"$observed")")"
      { head -n 2 "$receipt"; printf '%s\n' "$identity_case"; tail -n +4 "$receipt"; } >"$bad_receipt"
    else
      identity_case="$(rehash_event "$(jq -c '.payload.findings[0].finding_id="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"' <<<"$synthesized")")"
      { head -n 8 "$receipt"; printf '%s\n' "$identity_case"; tail -n +10 "$receipt"; } >"$bad_receipt"
    fi
    bash "$RUNTIME" rehydrate-interactive --event-file "$bad_receipt" --policy-file "$policy" \
      --repo-worktree "$repo" --repo "$REPOSITORY" --pr "$PR_NUMBER" --base "$interactive_base" \
      --head "$interactive_head" --config-hash "$CONFIG_HASH" --review-key "$interactive_key" --run-id "$run_id" >/dev/null 2>&1
    assert_eq "$mutated identity mutation fails closed" "3" "$?"
  done

  for forbidden_command in resume lock-recover gc retain authorize post; do
    bash "$RUNTIME" "$forbidden_command" >/dev/null 2>&1
    assert_eq "$forbidden_command remains outside runtime authority" "2" "$?"
  done
}

if [ "$CASE_FILTER" = 'merge-readiness' ]; then
  run_interactive_decision_tests merge-positive-only
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit
fi

# Keep the contract, including a real rehydrated producer fixture, in the
# default CI run as well as the focused diagnostic case above.
if [ "$CASE_FILTER" = 'all' ]; then
  run_interactive_decision_tests merge-positive-only
fi

if [ "$CASE_FILTER" = 'interactive-decision' ]; then
  run_interactive_decision_tests
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit
fi

run_privacy_envelope_tests() {
  local fixture_event extension_event maximum_extension_event unsafe_count_event
  local unknown_event unknown_file unknown_output unknown_rc
  local raw_event raw_file raw_output raw_rc raw_hash raw_bytes quarantine_dir metadata_file
  local successor_event top_duplicate payload_duplicate extension_duplicate duplicate_event duplicate_index
  local duplicate_file duplicate_output duplicate_rc fresh_events successor_events
  local bad_extension dependency_state dependency_rc

  fixture_event="$(sed -n '1p' "$FIXTURE")"
  extension_event="$(rehash_event "$(jq -c '
    .sequence=2 |
    .extensions=[{
      namespace:"com.acme.review",
      key:"provider_receipt",
      value_sha256:"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
      byte_count:128
    }]' <<<"$fixture_event")")"
  printf '%s\n' "$extension_event" >"$TEST_INPUT_ROOT/valid-extension.jsonl"
  bash "$RUNTIME" validate --event-file "$TEST_INPUT_ROOT/valid-extension.jsonl" >/dev/null 2>&1
  assert_eq "typed hash-only extension validates" "0" "$?"

  maximum_extension_event="$(rehash_event "$(jq -c '
    .sequence=2 |
    .extensions=[{
      namespace:"com.acme.review",
      key:"maximum_receipt",
      value_sha256:"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
      byte_count:9007199254740991
    }]' <<<"$fixture_event")")"
  printf '%s\n' "$maximum_extension_event" >"$TEST_INPUT_ROOT/maximum-extension.jsonl"
  bash "$RUNTIME" validate --event-file "$TEST_INPUT_ROOT/maximum-extension.jsonl" >/dev/null 2>&1
  assert_eq "maximum jq-safe extension byte count validates" "0" "$?"

  unsafe_count_event="$(rehash_event "$(jq -c '
    .sequence=2 |
    .extensions=[{
      namespace:"com.acme.review",
      key:"unsafe_count_receipt",
      value_sha256:"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
      byte_count:9007199254740992
    }]' <<<"$fixture_event")")"
  printf '%s\n' "$unsafe_count_event" >"$TEST_INPUT_ROOT/unsafe-count-extension.jsonl"
  bash "$RUNTIME" validate --event-file "$TEST_INPUT_ROOT/unsafe-count-extension.jsonl" >/dev/null 2>&1
  assert_eq "extension byte count above jq-safe maximum is rejected" "1" "$?"

  unknown_event="$(rehash_event "$(jq -c '.sequence=2 | .future_optional={mode:"preserve"}' <<<"$fixture_event")")"
  unknown_file="$TEST_INPUT_ROOT/unknown-envelope.jsonl"
  printf '%s\n' "$unknown_event" >"$unknown_file"
  unknown_output="$(bash "$RUNTIME" validate --event-file "$unknown_file" 2>"$TEST_STATE_ROOT/unknown-envelope.stderr")"
  unknown_rc=$?
  assert_eq "unknown top-level event key is rejected" "1" "$unknown_rc"
  assert_eq "unknown top-level event key counts invalid" "1" "$(jq -r '.invalid' <<<"$unknown_output")"
  assert_match "unknown top-level event key has a typed reason" 'unsupported_event_envelope' "$(cat "$TEST_STATE_ROOT/unknown-envelope.stderr")"

  for bad_extension in \
    '{"namespace":"com.acme.review","key":"provider_receipt","value_sha256":"not-a-hash","byte_count":128}' \
    '{"namespace":"com.acme.review","key":"provider_receipt","value_sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","byte_count":-1}' \
    '{"namespace":"com.acme.review","key":"provider_receipt","value_sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","byte_count":128,"value":"raw provider bytes"}' \
    '{"namespace":"com.acme.review","key":"provider_receipt","value_sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","byte_count":128,"payload":{"raw":"raw provider bytes"}}'; do
    raw_event="$(rehash_event "$(jq -c --argjson extension "$bad_extension" '.sequence=2 | .extensions=[$extension]' <<<"$fixture_event")")"
    raw_file="$TEST_INPUT_ROOT/invalid-extension.jsonl"
    printf '%s\n' "$raw_event" >"$raw_file"
    bash "$RUNTIME" validate --event-file "$raw_file" >/dev/null 2>&1
    assert_eq "malformed or semantic extension is rejected" "1" "$?"
  done

  bash "$RUNTIME" append --event-file "$FIXTURE" >/dev/null
  cp "$TEST_STATE_ROOT/$(sha256_text "$REPOSITORY")/pr-$PR_NUMBER/run-fixture-fresh/events.jsonl" "$TEST_STATE_ROOT/before-private-rejection.jsonl"
  raw_event="$(rehash_event "$(jq -c '.sequence=2 | .extensions=[{namespace:"com.acme.review",key:"provider_receipt",value_sha256:"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",byte_count:128,content:"secret rejected bytes"}]' <<<"$fixture_event")")"
  raw_file="$TEST_INPUT_ROOT/private-rejection.jsonl"
  printf '%s\n' "$raw_event" >"$raw_file"
  raw_output="$(bash "$RUNTIME" append --event-file "$raw_file")"
  raw_rc=$?
  assert_eq "semantic extension append is quarantined" "1" "$raw_rc"
  assert_eq "semantic extension reports one quarantine" "1" "$(jq -r '.quarantined' <<<"$raw_output")"
  if cmp -s "$TEST_STATE_ROOT/before-private-rejection.jsonl" "$TEST_STATE_ROOT/$(sha256_text "$REPOSITORY")/pr-$PR_NUMBER/run-fixture-fresh/events.jsonl"; then
    pass
  else
    fail "rejected extension leaves accepted state byte-identical"
  fi

  raw_hash="$(sha256_text "$raw_event")"
  raw_bytes="$(printf '%s' "$raw_event" | wc -c | tr -d ' ')"
  if [ -d "$TEST_STATE_ROOT/quarantine" ]; then
    quarantine_dir="$(find "$TEST_STATE_ROOT/quarantine" -mindepth 1 -maxdepth 1 -type d -name "$raw_hash-*" -print)"
  else
    quarantine_dir=''
  fi
  if [ -n "$quarantine_dir" ]; then
    metadata_file="$quarantine_dir/metadata.json"
    assert_eq "quarantine publishes metadata only" "1" "$(find "$quarantine_dir" -mindepth 1 -maxdepth 1 -type f | wc -l | tr -d ' ')"
    assert_eq "quarantine metadata has exactly four keys" '["byte_count","input_sha256","quarantined_at","reason_code"]' "$(jq -c 'keys | sort' "$metadata_file")"
    assert_eq "quarantine records typed reason" "unsupported_event_envelope" "$(jq -r '.reason_code' "$metadata_file")"
    assert_eq "quarantine records rejected input hash" "$raw_hash" "$(jq -r '.input_sha256' "$metadata_file")"
    assert_eq "quarantine records rejected input byte count" "$raw_bytes" "$(jq -r '.byte_count' "$metadata_file")"
    if grep -R -E 'secret rejected bytes|raw provider bytes' "$TEST_STATE_ROOT" >/dev/null 2>&1; then
      fail "managed state never stores rejected content"
    elif grep -R -F "$raw_file" "$TEST_STATE_ROOT" >/dev/null 2>&1; then
      fail "managed state never stores the rejected input path"
    elif [ "$(find "$TEST_STATE_ROOT" -type l | wc -l | tr -d ' ')" != '0' ]; then
      fail "managed state never contains a link to rejected input"
    else
      pass
    fi
  else
    fail "rejected input produces metadata-only quarantine"
  fi

  successor_event="$(sed -n '2p' "$FIXTURE")"
  top_duplicate='{"extensions":[{"content":"hidden top-level secret"}],"extensions":[],'"${fixture_event#\{}"
  payload_duplicate="$(printf '%s' "$successor_event" | sed 's/"payload":{/"payload":{"successor_reason":"hidden payload secret",/')"
  extension_duplicate="$(printf '%s' "$successor_event" | sed 's/"key":"fixture_receipt"/"key":"hidden extension secret","key":"fixture_receipt"/')"
  fresh_events="$TEST_STATE_ROOT/$(sha256_text "$REPOSITORY")/pr-$PR_NUMBER/run-fixture-fresh/events.jsonl"
  successor_events="$TEST_STATE_ROOT/$(sha256_text "$REPOSITORY")/pr-$PR_NUMBER/run-fixture-successor/events.jsonl"
  cp "$fresh_events" "$TEST_STATE_ROOT/before-duplicate-fresh.jsonl"
  cp "$successor_events" "$TEST_STATE_ROOT/before-duplicate-successor.jsonl"
  duplicate_index=0
  for duplicate_event in "$top_duplicate" "$payload_duplicate" "$extension_duplicate"; do
    duplicate_index=$((duplicate_index + 1))
    duplicate_file="$TEST_INPUT_ROOT/duplicate-member-$duplicate_index.jsonl"
    printf '%s\n' "$duplicate_event" >"$duplicate_file"
    bash "$RUNTIME" validate --event-file "$duplicate_file" >"$TEST_INPUT_ROOT/duplicate-validate-$duplicate_index.out" 2>"$TEST_INPUT_ROOT/duplicate-validate-$duplicate_index.err"
    assert_eq "duplicate JSON member $duplicate_index fails validation" "1" "$?"
    assert_match "duplicate JSON member $duplicate_index has a typed validation reason" 'duplicate_json_member' "$(cat "$TEST_INPUT_ROOT/duplicate-validate-$duplicate_index.err")"
    duplicate_output="$(bash "$RUNTIME" append --event-file "$duplicate_file")"
    duplicate_rc=$?
    assert_eq "duplicate JSON member $duplicate_index append is quarantined" "1" "$duplicate_rc"
    assert_eq "duplicate JSON member $duplicate_index reports one quarantine" "1" "$(jq -r '.quarantined' <<<"$duplicate_output")"
  done
  assert_eq "all duplicate-member inputs use the typed quarantine reason" "3" "$(grep -l 'duplicate_json_member' "$TEST_STATE_ROOT"/quarantine/*/metadata.json | wc -l | tr -d ' ')"
  if cmp -s "$TEST_STATE_ROOT/before-duplicate-fresh.jsonl" "$fresh_events" &&
    cmp -s "$TEST_STATE_ROOT/before-duplicate-successor.jsonl" "$successor_events"; then
    pass
  else
    fail "duplicate-member rejection leaves all accepted state byte-identical"
  fi
  if grep -R -E 'hidden (top-level|payload|extension) secret' "$TEST_STATE_ROOT" >/dev/null 2>&1; then
    fail "managed state never stores hidden duplicate-member content"
  else
    pass
  fi
  assert_eq "duplicate-member quarantines are metadata-only" "0" "$(find "$TEST_STATE_ROOT/quarantine" -mindepth 2 -type f ! -name metadata.json | wc -l | tr -d ' ')"

  dependency_state="$(mktemp -d)"
  (
    export KC_PR_FLOW_STATE_DIR="$dependency_state"
    review_runtime_require_python() { return 69; }
    review_runtime_validate_line "$fixture_event" >/dev/null 2>&1
  )
  dependency_rc=$?
  assert_eq "direct validation returns 69 when duplicate checker dependency is absent" "69" "$dependency_rc"
  (
    export KC_PR_FLOW_STATE_DIR="$dependency_state"
    review_runtime_require_python() { return 69; }
    review_runtime_validate_file "$FIXTURE" >/dev/null 2>&1
  )
  dependency_rc=$?
  assert_eq "file validation returns 69 when duplicate checker dependency is absent" "69" "$dependency_rc"
  (
    export KC_PR_FLOW_STATE_DIR="$dependency_state"
    review_runtime_require_python() { return 69; }
    review_runtime_append_file "$FIXTURE" >/dev/null 2>&1
  )
  dependency_rc=$?
  assert_eq "append returns 69 before state mutation when duplicate checker dependency is absent" "69" "$dependency_rc"
  assert_eq "dependency failure creates no managed state" "0" "$(find "$dependency_state" -mindepth 1 | wc -l | tr -d ' ')"
  (
    export KC_PR_FLOW_STATE_DIR="$dependency_state"
    review_runtime_require_python() { return 69; }
    review_runtime_replay "$FIXTURE" >/dev/null 2>&1
  )
  dependency_rc=$?
  assert_eq "replay returns 69 when duplicate checker dependency is absent" "69" "$dependency_rc"
  chmod -R u+rwX "$dependency_state" 2>/dev/null || true
  rm -rf "$dependency_state"
}

run_safe_io_tests() {
  local source_file destination_file helper_output helper_rc
  local empty_file exact_file fifo_file socket_file socket_ready socket_pid socket_rc
  local race_source race_destination race_rc capability_open_rc unknown_open_rc missing_source
  local oversized_file existing_contents mutation_rc capability_rc durability_rc flags_rc cleanup_swap_rc
  local fixture_event impossible_event leap_event invalid_limit_state dependency_state
  local batch_file batch_output batch_rc maximum_usage unsafe_usage float_usage exponent_usage usage_output
  local one_review_key integer_event float_event exponent_event fixture_bytes oversize_limit stdin_state
  local rfc_state rfc_rc
  local runtime_snapshot_root runtime_snapshot_observation fake_helper runtime_snapshot_rc

  source_file="$TEST_INPUT_ROOT/safe-source.json"
  destination_file="$TEST_INPUT_ROOT/safe-destination.json"
  printf '%s' '{"safe":true}' >"$source_file"
  helper_output="$(python3 "$SAFE_IO" snapshot --source "$source_file" --destination "$destination_file" --limit-bytes 64 2>"$TEST_INPUT_ROOT/snapshot.stderr")"
  helper_rc=$?
  assert_eq "descriptor snapshot succeeds" "0" "$helper_rc"
  assert_eq "descriptor snapshot writes no stdout" "" "$helper_output"
  assert_eq "descriptor snapshot preserves bytes" '{"safe":true}' "$(cat "$destination_file" 2>/dev/null)"
  assert_eq "descriptor snapshot destination is mode 0600" "600" "$(file_mode "$destination_file" 2>/dev/null)"

  empty_file="$TEST_INPUT_ROOT/empty-source.json"
  : >"$empty_file"
  rm -f "$destination_file"
  python3 "$SAFE_IO" snapshot --source "$empty_file" --destination "$destination_file" --limit-bytes 1 >/dev/null 2>&1
  assert_eq "empty regular source snapshots successfully" "0" "$?"
  assert_eq "empty source produces an empty destination" "0" "$(wc -c <"$destination_file" | tr -d ' ')"

  exact_file="$TEST_INPUT_ROOT/exact-limit-source.json"
  printf '%064d' 0 >"$exact_file"
  rm -f "$destination_file"
  python3 "$SAFE_IO" snapshot --source "$exact_file" --destination "$destination_file" --limit-bytes 64 >/dev/null 2>&1
  assert_eq "source exactly at the limit snapshots successfully" "0" "$?"
  assert_eq "exact-limit snapshot preserves all bytes" "64" "$(wc -c <"$destination_file" | tr -d ' ')"

  rm -f "$destination_file"
  python3 - "$SAFE_IO" "$source_file" "$destination_file" <<'PY'
import importlib.util
import os
import sys

helper_path, source, destination = sys.argv[1:]
spec = importlib.util.spec_from_file_location("review_runtime_safe_io_flags", helper_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
real_open = module.os.open
source_opens = []

def tracked_open(path, flags, *args):
    if path == source:
        source_opens.append(flags)
    return real_open(path, flags, *args)

module.os.open = tracked_open
rc = module.main(["snapshot", "--source", source, "--destination", destination, "--limit-bytes", "64"])
required = module.os.O_NOFOLLOW | module.os.O_CLOEXEC
valid = (
    rc == 0
    and len(source_opens) == 1
    and (source_opens[0] & module.os.O_ACCMODE) == module.os.O_RDONLY
    and (source_opens[0] & required) == required
)
raise SystemExit(0 if valid else 1)
PY
  flags_rc=$?
  assert_eq "source is opened exactly once with read-only no-follow close-on-exec flags" "0" "$flags_rc"

  rm -f "$destination_file"
  ln -s "$source_file" "$TEST_INPUT_ROOT/source-link.json"
  python3 "$SAFE_IO" snapshot --source "$TEST_INPUT_ROOT/source-link.json" --destination "$destination_file" --limit-bytes 64 >/dev/null 2>&1
  assert_eq "symlink source is rejected as unsafe" "2" "$?"
  assert_eq "symlink rejection creates no destination" "false" "$([ -e "$destination_file" ] && printf true || printf false)"

  python3 "$SAFE_IO" snapshot --source "$TEST_INPUT_ROOT" --destination "$destination_file" --limit-bytes 64 >/dev/null 2>&1
  assert_eq "non-regular source is rejected as unsafe" "2" "$?"

  fifo_file="$TEST_INPUT_ROOT/source-fifo"
  mkfifo "$fifo_file"
  python3 "$SAFE_IO" snapshot --source "$fifo_file" --destination "$destination_file" --limit-bytes 64 >/dev/null 2>&1
  assert_eq "FIFO source is rejected without blocking" "2" "$?"

  socket_file="$TEST_INPUT_ROOT/source.sock"
  socket_ready="$TEST_INPUT_ROOT/source-socket.ready"
  python3 - "$socket_file" "$socket_ready" <<'PY' &
import os
import socket
import sys
import time

socket_path, ready_path = sys.argv[1:]
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    server.bind(socket_path)
    server.listen(1)
    with open(ready_path, "x", encoding="utf-8") as ready:
        ready.write("ready\n")
    time.sleep(10)
finally:
    server.close()
    for path in (ready_path, socket_path):
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
PY
  socket_pid=$!
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    [ -S "$socket_file" ] && [ -f "$socket_ready" ] && break
    sleep 0.05
  done
  python3 "$SAFE_IO" snapshot --source "$socket_file" --destination "$destination_file" --limit-bytes 64 >/dev/null 2>&1
  socket_rc=$?
  kill "$socket_pid" 2>/dev/null || true
  wait "$socket_pid" 2>/dev/null || true
  rm -f "$socket_file" "$socket_ready"
  assert_eq "Unix-domain socket source is rejected as non-regular" "2" "$socket_rc"

  missing_source="$TEST_INPUT_ROOT/missing-source.json"
  python3 "$SAFE_IO" snapshot --source "$missing_source" --destination "$destination_file" --limit-bytes 64 >/dev/null 2>&1
  assert_eq "initially missing source is rejected as unsafe input" "2" "$?"

  race_source="$TEST_INPUT_ROOT/regular-then-missing.json"
  race_destination="$TEST_INPUT_ROOT/regular-then-missing.snapshot"
  printf '%s' '{"race":true}' >"$race_source"
  python3 - "$SAFE_IO" "$race_source" "$race_destination" <<'PY'
import importlib.util
import os
import sys

helper_path, source, destination = sys.argv[1:]
spec = importlib.util.spec_from_file_location("review_runtime_safe_io_race", helper_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
real_lstat = module.os.lstat

def disappearing_lstat(path):
    result = real_lstat(path)
    if path == source:
        os.unlink(source)
    return result

module.os.lstat = disappearing_lstat
raise SystemExit(module.main(["snapshot", "--source", source, "--destination", destination, "--limit-bytes", "64"]))
PY
  race_rc=$?
  assert_eq "regular source disappearing after preclassification is a race" "74" "$race_rc"
  assert_eq "regular-to-missing race creates no snapshot" "false" "$([ -e "$race_destination" ] && printf true || printf false)"

  python3 - "$SAFE_IO" "$source_file" "$destination_file" <<'PY'
import errno
import importlib.util
import sys

helper_path, source, destination = sys.argv[1:]
spec = importlib.util.spec_from_file_location("review_runtime_safe_io_unsupported", helper_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
real_open = module.os.open
source_opens = {"count": 0}

def unsupported_open(path, flags, *args):
    if path == source:
        source_opens["count"] += 1
        raise OSError(errno.EOPNOTSUPP, "injected O_NOFOLLOW capability failure")
    return real_open(path, flags, *args)

module.os.open = unsupported_open
rc = module.main(["snapshot", "--source", source, "--destination", destination, "--limit-bytes", "64"])
raise SystemExit(0 if rc == 69 and source_opens["count"] == 1 else 1)
PY
  capability_open_rc=$?
  assert_eq "regular-file EOPNOTSUPP is a missing no-follow capability" "0" "$capability_open_rc"

  python3 - "$SAFE_IO" "$source_file" "$destination_file" <<'PY'
import errno
import importlib.util
import sys

helper_path, source, destination = sys.argv[1:]
spec = importlib.util.spec_from_file_location("review_runtime_safe_io_eio", helper_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
real_open = module.os.open

def failed_open(path, flags, *args):
    if path == source:
        raise OSError(errno.EIO, "injected unknown source I/O failure")
    return real_open(path, flags, *args)

module.os.open = failed_open
raise SystemExit(0 if module.main(["snapshot", "--source", source, "--destination", destination, "--limit-bytes", "64"]) == 74 else 1)
PY
  unknown_open_rc=$?
  assert_eq "unknown regular-file open EIO remains a durability failure" "0" "$unknown_open_rc"

  printf '%s' 'existing destination bytes' >"$destination_file"
  existing_contents="$(cat "$destination_file")"
  python3 "$SAFE_IO" snapshot --source "$source_file" --destination "$destination_file" --limit-bytes 64 >/dev/null 2>&1
  assert_eq "pre-existing destination fails closed" "74" "$?"
  assert_eq "pre-existing destination is not overwritten" "$existing_contents" "$(cat "$destination_file")"
  rm -f "$destination_file"

  oversized_file="$TEST_INPUT_ROOT/oversized.json"
  printf '%065d' 0 >"$oversized_file"
  python3 "$SAFE_IO" snapshot --source "$oversized_file" --destination "$destination_file" --limit-bytes 64 >/dev/null 2>&1
  assert_eq "oversized source returns configuration status" "73" "$?"
  assert_eq "oversized source creates no destination" "false" "$([ -e "$destination_file" ] && printf true || printf false)"
  python3 "$SAFE_IO" snapshot --source "$source_file" --destination "$destination_file" --limit-bytes 9007199254740992 >/dev/null 2>&1
  assert_eq "jq-unsafe snapshot limit is rejected" "73" "$?"

  python3 - "$SAFE_IO" "$source_file" "$destination_file" <<'PY'
import importlib.util
import os
import sys

helper_path, source, destination = sys.argv[1:]
spec = importlib.util.spec_from_file_location("review_runtime_safe_io", helper_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
real_fstat = module.os.fstat
calls = {"count": 0}

def changed_fstat(fd):
    stat_result = real_fstat(fd)
    calls["count"] += 1
    if calls["count"] == 2:
        os.utime(source, ns=(stat_result.st_atime_ns, stat_result.st_mtime_ns + 1_000_000_000))
        return real_fstat(fd)
    return stat_result

module.os.fstat = changed_fstat
raise SystemExit(module.main(["snapshot", "--source", source, "--destination", destination, "--limit-bytes", "64"]))
PY
  mutation_rc=$?
  assert_eq "descriptor mutation is detected" "74" "$mutation_rc"
  assert_eq "mutation failure creates no destination" "false" "$([ -e "$destination_file" ] && printf true || printf false)"

  python3 - "$SAFE_IO" "$source_file" "$TEST_INPUT_ROOT" <<'PY'
import errno
import importlib.util
import os
import stat
import sys

helper_path, source, root = sys.argv[1:]
base_open = os.open
base_write = os.write
base_fsync = os.fsync
base_close = os.close

def load(name):
    spec = importlib.util.spec_from_file_location(name, helper_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

for operation in ("write", "fsync", "close"):
    os.open = base_open
    os.write = base_write
    os.fsync = base_fsync
    os.close = base_close
    module = load("review_runtime_safe_io_" + operation)
    destination = os.path.join(root, "failed-" + operation + ".json")
    destination_fd = {"value": None}
    raised = {"value": False}

    def tracked_open(path, flags, *args):
        fd = base_open(path, flags, *args)
        if path == destination:
            destination_fd["value"] = fd
        return fd

    module.os.open = tracked_open
    if operation == "write":
        module.os.write = lambda *_: (_ for _ in ()).throw(OSError(errno.EIO, "injected write failure"))
    elif operation == "fsync":
        module.os.fsync = lambda *_: (_ for _ in ()).throw(OSError(errno.EIO, "injected fsync failure"))
    else:
        def failed_close(fd):
            if fd == destination_fd["value"] and not raised["value"]:
                raised["value"] = True
                raise OSError(errno.EIO, "injected close failure")
            return base_close(fd)
        module.os.close = failed_close

    rc = module.snapshot(source, destination, 64)
    valid_partial = (
        rc == 74
        and os.path.isfile(destination)
        and stat.S_IMODE(os.lstat(destination).st_mode) == 0o600
    )
    if not valid_partial:
        raise SystemExit(1)
    os.unlink(destination)
os.open = base_open
os.write = base_write
os.fsync = base_fsync
os.close = base_close
raise SystemExit(0)
PY
  durability_rc=$?
  assert_eq "write fsync and close failures return 74 and leave mode-0600 partial destinations" "0" "$durability_rc"

  python3 - "$SAFE_IO" "$source_file" "$destination_file" "$TEST_INPUT_ROOT/saved-owned-partial.json" <<'PY'
import errno
import importlib.util
import os
import sys

helper_path, source, destination, saved = sys.argv[1:]
spec = importlib.util.spec_from_file_location("review_runtime_safe_io_cleanup_swap", helper_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
real_lstat = module.os.lstat
real_write = module.os.write
swapped = {"value": False}

def cleanup_swap_lstat(path):
    result = real_lstat(path)
    if path == destination and not swapped["value"]:
        os.replace(destination, saved)
        with open(destination, "wb") as replacement:
            replacement.write(b"replacement-must-survive")
        swapped["value"] = True
    return result

def failed_write(fd, content):
    raise OSError(errno.EIO, "injected write failure")

module.os.lstat = cleanup_swap_lstat
module.os.write = failed_write
rc = module.snapshot(source, destination, 64)
if not swapped["value"]:
    if os.path.lexists(destination):
        os.replace(destination, saved)
    with open(destination, "wb") as replacement:
        replacement.write(b"replacement-must-survive")
replacement_survived = False
try:
    try:
        with open(destination, "rb") as replacement:
            replacement_survived = replacement.read() == b"replacement-must-survive"
    except FileNotFoundError:
        replacement_survived = False
finally:
    module.os.lstat = real_lstat
    module.os.write = real_write
    for path in (destination, saved):
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
raise SystemExit(0 if rc == 74 and replacement_survived else 1)
PY
  cleanup_swap_rc=$?
  assert_eq "helper failure never deletes a pathname replacement during cleanup" "0" "$cleanup_swap_rc"

  runtime_snapshot_root="$TEST_STATE_ROOT/runtime-snapshot-temp"
  runtime_snapshot_observation="$TEST_INPUT_ROOT/runtime-snapshot-observation.txt"
  fake_helper="$TEST_INPUT_ROOT/failing-safe-io.py"
  mkdir "$runtime_snapshot_root"
  printf '%s\n' \
    '#!/usr/bin/env python3' \
    'import os' \
    'import stat' \
    'import sys' \
    'command = sys.argv[1]' \
    'if command in ("rfc3339-utc", "unique-json"):' \
    '    raise SystemExit(0)' \
    'if command not in ("snapshot", "snapshot-stdin"):' \
    '    raise SystemExit(2)' \
    'destination = sys.argv[sys.argv.index("--destination") + 1]' \
    'parent = os.path.dirname(destination)' \
    'mode = stat.S_IMODE(os.stat(parent).st_mode)' \
    'with open(os.environ["T7_HELPER_OBSERVATION"], "w", encoding="utf-8") as receipt:' \
    '    receipt.write("private-700" if mode == 0o700 and os.path.dirname(parent) == os.environ["TMPDIR"] else "unsafe-parent")' \
    'fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)' \
    'os.fchmod(fd, 0o600)' \
    'os.write(fd, b"partial")' \
    'os.close(fd)' \
    'raise SystemExit(74)' >"$fake_helper"
  chmod 0700 "$fake_helper"
  (
    export TMPDIR="$runtime_snapshot_root" T7_HELPER_OBSERVATION="$runtime_snapshot_observation"
    review_runtime_safe_io_helper() { printf '%s\n' "$fake_helper"; }
    review_runtime_validate_file "$FIXTURE" >/dev/null 2>&1
  )
  runtime_snapshot_rc=$?
  assert_eq "runtime propagates helper snapshot failure" "74" "$runtime_snapshot_rc"
  assert_eq "runtime passes helper a destination in a private mode-0700 directory" "private-700" "$(cat "$runtime_snapshot_observation" 2>/dev/null)"
  assert_eq "runtime removes its private snapshot directory and partial contents after failure" "0" "$(find "$runtime_snapshot_root" -mindepth 1 | wc -l | tr -d ' ')"

  python3 - "$SAFE_IO" "$source_file" "$destination_file" <<'PY'
import importlib.util
import sys

helper_path, source, destination = sys.argv[1:]
spec = importlib.util.spec_from_file_location("review_runtime_safe_io", helper_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
delattr(module.os, "O_NOFOLLOW")
raise SystemExit(module.main(["snapshot", "--source", source, "--destination", destination, "--limit-bytes", "64"]))
PY
  capability_rc=$?
  assert_eq "missing O_NOFOLLOW capability returns dependency status" "69" "$capability_rc"

  dependency_state="$(mktemp -d)"
  (
    export KC_PR_FLOW_STATE_DIR="$dependency_state"
    review_runtime_safe_io_helper() { printf '%s\n' "$TEST_INPUT_ROOT/missing-helper.py"; }
    review_runtime_append_file "$FIXTURE" >/dev/null 2>&1
  )
  assert_eq "missing helper fails before append mutation" "69" "$?"
  assert_eq "dependency failure leaves managed state empty" "0" "$(find "$dependency_state" -mindepth 1 | wc -l | tr -d ' ')"
  rm -rf "$dependency_state"

  fixture_event="$(sed -n '1p' "$FIXTURE")"
  (
    review_runtime_rfc3339_utc_valid() { return 69; }
    review_runtime_validate_start_input "$REPOSITORY" "$PR_NUMBER" "$BASE_SHA" "$HEAD_SHA" "$CONFIG_HASH" "$OCCURRED_AT" '' '' >/dev/null 2>&1
  )
  rfc_rc=$?
  assert_eq "direct start-input validation propagates RFC dependency status" "69" "$rfc_rc"
  (
    review_runtime_rfc3339_utc_valid() { return 69; }
    review_runtime_validate_line "$fixture_event" >/dev/null 2>&1
  )
  rfc_rc=$?
  assert_eq "direct event validation propagates RFC dependency status" "69" "$rfc_rc"

  rfc_state="$TEST_STATE_ROOT/rfc-validate-file"
  mkdir "$rfc_state"
  (
    export KC_PR_FLOW_STATE_DIR="$rfc_state"
    review_runtime_rfc3339_utc_valid() { return 69; }
    review_runtime_validate_file "$FIXTURE" >/dev/null 2>&1
  )
  rfc_rc=$?
  assert_eq "file validation propagates RFC dependency status" "69" "$rfc_rc"
  assert_eq "RFC dependency failure during file validation creates no managed state" "0" "$(find "$rfc_state" -mindepth 1 | wc -l | tr -d ' ')"

  rfc_state="$TEST_STATE_ROOT/rfc-append-line"
  mkdir "$rfc_state"
  (
    export KC_PR_FLOW_STATE_DIR="$rfc_state"
    review_runtime_rfc3339_utc_valid() { return 69; }
    review_runtime_append_line "$fixture_event" >/dev/null 2>&1
  )
  rfc_rc=$?
  assert_eq "direct append propagates RFC dependency status" "69" "$rfc_rc"
  assert_eq "RFC dependency failure during direct append creates no state or quarantine" "0" "$(find "$rfc_state" -mindepth 1 | wc -l | tr -d ' ')"

  rfc_state="$TEST_STATE_ROOT/rfc-append-file"
  mkdir "$rfc_state"
  (
    export KC_PR_FLOW_STATE_DIR="$rfc_state"
    review_runtime_rfc3339_utc_valid() { return 69; }
    review_runtime_append_file "$FIXTURE" >/dev/null 2>&1
  )
  rfc_rc=$?
  assert_eq "file append propagates RFC dependency status" "69" "$rfc_rc"
  assert_eq "RFC dependency failure during file append creates no state or quarantine" "0" "$(find "$rfc_state" -mindepth 1 | wc -l | tr -d ' ')"

  invalid_limit_state="$(mktemp -d)"
  (
    export KC_PR_FLOW_STATE_DIR="$invalid_limit_state" KC_PR_FLOW_MAX_EVENTS_BYTES=9007199254740992
    review_runtime_append_file "$FIXTURE" >/dev/null 2>&1
  )
  assert_eq "jq-unsafe configured event limit returns 73" "73" "$?"
  assert_eq "invalid event limit fails before state mutation" "0" "$(find "$invalid_limit_state" -mindepth 1 | wc -l | tr -d ' ')"
  rm -rf "$invalid_limit_state"

  fixture_bytes="$(wc -c <"$FIXTURE" | tr -d ' ')"
  oversize_limit=$((fixture_bytes - 1))
  stdin_state="$TEST_STATE_ROOT/stdin-validate-exact"
  mkdir "$stdin_state"
  ( export KC_PR_FLOW_STATE_DIR="$stdin_state" KC_PR_FLOW_MAX_EVENTS_BYTES="$fixture_bytes"; cat "$FIXTURE" | bash "$RUNTIME" validate --event-file - >/dev/null 2>&1 )
  assert_eq "stdin event input exactly at the limit validates" "0" "$?"
  assert_eq "stdin validation does not mutate managed state" "0" "$(find "$stdin_state" -mindepth 1 | wc -l | tr -d ' ')"

  stdin_state="$TEST_STATE_ROOT/stdin-append-exact"
  mkdir "$stdin_state"
  ( export KC_PR_FLOW_STATE_DIR="$stdin_state" KC_PR_FLOW_MAX_EVENTS_BYTES="$fixture_bytes"; cat "$FIXTURE" | bash "$RUNTIME" append --event-file - >/dev/null 2>&1 )
  assert_eq "stdin event input exactly at the limit appends" "0" "$?"
  assert_eq "exact-limit stdin append writes both accepted run logs" "2" "$(find "$stdin_state" -name events.jsonl -type f | wc -l | tr -d ' ')"

  stdin_state="$TEST_STATE_ROOT/stdin-validate-oversize"
  mkdir "$stdin_state"
  ( export KC_PR_FLOW_STATE_DIR="$stdin_state" KC_PR_FLOW_MAX_EVENTS_BYTES="$oversize_limit"; cat "$FIXTURE" | bash "$RUNTIME" validate --event-file - >/dev/null 2>&1 )
  assert_eq "stdin validation limit plus one returns 73" "73" "$?"
  assert_eq "oversized stdin validation creates no state or quarantine" "0" "$(find "$stdin_state" -mindepth 1 | wc -l | tr -d ' ')"

  stdin_state="$TEST_STATE_ROOT/stdin-append-oversize"
  mkdir "$stdin_state"
  ( export KC_PR_FLOW_STATE_DIR="$stdin_state" KC_PR_FLOW_MAX_EVENTS_BYTES="$oversize_limit"; cat "$FIXTURE" | bash "$RUNTIME" append --event-file - >/dev/null 2>&1 )
  assert_eq "stdin append limit plus one returns 73" "73" "$?"
  assert_eq "oversized stdin append creates no accepted state or quarantine" "0" "$(find "$stdin_state" -mindepth 1 | wc -l | tr -d ' ')"

  maximum_usage='{"provenance":"reported","scope":"lane","provider_family":"claude","input_tokens":9007199254740991,"output_tokens":0,"total_tokens":9007199254740991}'
  unsafe_usage='{"provenance":"reported","scope":"lane","provider_family":"claude","input_tokens":9007199254740992,"output_tokens":0,"total_tokens":9007199254740992}'
  printf '%s\n' "$maximum_usage" >"$TEST_INPUT_ROOT/maximum-usage.json"
  printf '%s\n' "$maximum_usage" >"$TEST_INPUT_ROOT/maximum-usage-peer.json"
  usage_output="$(bash "$RUNTIME" compare-usage --left-json "$TEST_INPUT_ROOT/maximum-usage.json" --right-json "$TEST_INPUT_ROOT/maximum-usage-peer.json")"
  assert_eq "maximum jq-safe usage remains comparable" "true" "$(jq -r '.comparable' <<<"$usage_output")"
  printf '%s\n' "$unsafe_usage" >"$TEST_INPUT_ROOT/unsafe-usage.json"
  bash "$RUNTIME" compare-usage --left-json "$TEST_INPUT_ROOT/unsafe-usage.json" --right-json "$TEST_INPUT_ROOT/maximum-usage.json" >/dev/null 2>&1
  assert_eq "adjacent jq-unsafe usage integer is rejected before comparison" "2" "$?"
  float_usage='{"provenance":"reported","scope":"lane","provider_family":"claude","input_tokens":1.00000000000000001,"output_tokens":0,"total_tokens":1.00000000000000001}'
  exponent_usage='{"provenance":"reported","scope":"lane","provider_family":"claude","input_tokens":1e0,"output_tokens":0,"total_tokens":1e0}'
  printf '%s\n' "$float_usage" >"$TEST_INPUT_ROOT/float-usage.json"
  printf '%s\n' "$exponent_usage" >"$TEST_INPUT_ROOT/exponent-usage.json"
  bash "$RUNTIME" compare-usage --left-json "$TEST_INPUT_ROOT/float-usage.json" --right-json "$TEST_INPUT_ROOT/maximum-usage.json" >/dev/null 2>&1
  assert_eq "fractional usage lexeme that collapses to an integer is rejected losslessly" "2" "$?"
  bash "$RUNTIME" compare-usage --left-json "$TEST_INPUT_ROOT/exponent-usage.json" --right-json "$TEST_INPUT_ROOT/maximum-usage.json" >/dev/null 2>&1
  assert_eq "exponent usage lexeme is rejected before jq normalization" "2" "$?"

  one_review_key="$(sha256_text "$REPOSITORY|1|$BASE_SHA|$HEAD_SHA|$CONFIG_HASH")"
  integer_event="$(rehash_integrity "$(jq -c --arg review_key "$one_review_key" '.pr_number=1 | .review_key=$review_key' <<<"$fixture_event")")"
  float_event="$(printf '%s' "$integer_event" | sed 's/"pr_number":1/"pr_number":1.00000000000000001/')"
  exponent_event="$(printf '%s' "$integer_event" | sed 's/"pr_number":1/"pr_number":1e0/')"
  printf '%s\n' "$float_event" >"$TEST_INPUT_ROOT/float-event.jsonl"
  printf '%s\n' "$exponent_event" >"$TEST_INPUT_ROOT/exponent-event.jsonl"
  bash "$RUNTIME" validate --event-file "$TEST_INPUT_ROOT/float-event.jsonl" >/dev/null 2>&1
  assert_eq "fractional event lexeme that collapses to an integer is rejected losslessly" "1" "$?"
  bash "$RUNTIME" validate --event-file "$TEST_INPUT_ROOT/exponent-event.jsonl" >/dev/null 2>&1
  assert_eq "exponent event lexeme is rejected before jq normalization" "1" "$?"
  impossible_event="$(rehash_integrity "$(jq -c '.occurred_at="2026-02-30T12:00:00Z"' <<<"$fixture_event")")"
  printf '%s\n' "$impossible_event" >"$TEST_INPUT_ROOT/impossible-date.jsonl"
  bash "$RUNTIME" validate --event-file "$TEST_INPUT_ROOT/impossible-date.jsonl" >/dev/null 2>&1
  assert_eq "impossible calendar timestamp is rejected" "1" "$?"
  leap_event="$(rehash_integrity "$(jq -c '.occurred_at="2024-02-29T23:59:59.123Z"' <<<"$fixture_event")")"
  printf '%s\n' "$leap_event" >"$TEST_INPUT_ROOT/leap-date.jsonl"
  bash "$RUNTIME" validate --event-file "$TEST_INPUT_ROOT/leap-date.jsonl" >/dev/null 2>&1
  assert_eq "real leap-day RFC3339 UTC timestamp validates" "0" "$?"

  printf '%s\n' temporary quarantine >"$TEST_INPUT_ROOT/mixed-batch.txt"
  batch_file="$TEST_INPUT_ROOT/mixed-batch.txt"
  batch_output="$({
    review_runtime_append_line() {
      case "$1" in
        temporary) printf '%s\n' blocked; return 75 ;;
        quarantine) printf '%s\n' quarantined; return 1 ;;
      esac
    }
    review_runtime_append_file "$batch_file"
  })"
  batch_rc=$?
  assert_eq "later quarantine cannot downgrade temporary block" "75" "$batch_rc"
  assert_eq "temporary and quarantine counts remain visible" '{"appended":0,"duplicate":0,"quarantined":1,"blocked":1}' "$batch_output"

  printf '%s\n' quarantine temporary >"$TEST_INPUT_ROOT/mixed-batch-reverse.txt"
  batch_output="$({
    review_runtime_append_line() {
      case "$1" in
        temporary) printf '%s\n' blocked; return 75 ;;
        quarantine) printf '%s\n' quarantined; return 1 ;;
      esac
    }
    review_runtime_append_file "$TEST_INPUT_ROOT/mixed-batch-reverse.txt"
  })"
  batch_rc=$?
  assert_eq "earlier quarantine cannot mask a later temporary block" "75" "$batch_rc"
  assert_eq "reverse temporary and quarantine counts remain visible" '{"appended":0,"duplicate":0,"quarantined":1,"blocked":1}' "$batch_output"

  printf '%s\n' durable quarantine >"$TEST_INPUT_ROOT/mixed-durable-batch.txt"
  batch_output="$({
    review_runtime_append_line() {
      case "$1" in
        durable) printf '%s\n' blocked; return 74 ;;
        quarantine) printf '%s\n' quarantined; return 1 ;;
      esac
    }
    review_runtime_append_file "$TEST_INPUT_ROOT/mixed-durable-batch.txt"
  })"
  batch_rc=$?
  assert_eq "later quarantine cannot downgrade durability block" "74" "$batch_rc"
  assert_eq "durability and quarantine counts remain visible" '{"appended":0,"duplicate":0,"quarantined":1,"blocked":1}' "$batch_output"

  printf '%s\n' quarantine durable >"$TEST_INPUT_ROOT/mixed-durable-batch-reverse.txt"
  batch_output="$({
    review_runtime_append_line() {
      case "$1" in
        durable) printf '%s\n' blocked; return 74 ;;
        quarantine) printf '%s\n' quarantined; return 1 ;;
      esac
    }
    review_runtime_append_file "$TEST_INPUT_ROOT/mixed-durable-batch-reverse.txt"
  })"
  batch_rc=$?
  assert_eq "earlier quarantine cannot mask a later durability block" "74" "$batch_rc"
  assert_eq "reverse durability and quarantine counts remain visible" '{"appended":0,"duplicate":0,"quarantined":1,"blocked":1}' "$batch_output"
}

run_evidence_binding_tests() {
  local fixture_event pointer candidate candidate_id candidate_event
  local merge_key finding_id finding finding_event evidence_hash changed_hash
  local mutation_name mutation_filter mutated_event reason validator_probe
  local old_candidate_id old_merge_key old_finding_id
  local scoped_kind scoped_pointer scoped_candidate scoped_finding scoped_event standalone_pointer

  fixture_event="$(sed -n '1p' "$FIXTURE")"
  evidence_hash='dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd'
  changed_hash='eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
  candidate_id="$(sha256_text "run-fixture-fresh|security-1|1|$evidence_hash")"
  merge_key="src/review.sh|RIGHT|$evidence_hash|security|unchecked-boundary"
  finding_id="$(sha256_text "$EXPECTED_REVIEW_KEY|$merge_key")"
  pointer="$(jq -S -c -n \
    --arg review_key "$EXPECTED_REVIEW_KEY" --arg repository "$REPOSITORY" \
    --arg base_sha "$BASE_SHA" --arg head_sha "$HEAD_SHA" \
    --arg content_sha256 "$evidence_hash" \
    '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",review_key:$review_key,repository:$repository,base_sha:$base_sha,head_sha:$head_sha,object_sha:$head_sha,path:"src/review.sh",side:"RIGHT",line:7,locator:"review-anchor",content_sha256:$content_sha256}')"
  candidate="$(jq -S -c -n \
    --arg candidate_id "$candidate_id" --arg review_key "$EXPECTED_REVIEW_KEY" \
    --argjson evidence "$pointer" \
    '{schema:"kc-pr-flow.review-candidate/v1",candidate_id:$candidate_id,run_id:"run-fixture-fresh",review_key:$review_key,lane_id:"security-1",ordinal:1,path:"src/review.sh",side:"RIGHT",anchor_sha256:"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",category:"security",claim_key:"unchecked-boundary",evidence:$evidence}')"
  candidate_event="$(rehash_event "$(jq -c --argjson candidate "$candidate" '.sequence=2 | .event_type="finding.observed" | .payload={candidate:$candidate}' <<<"$fixture_event")")"
  finding="$(jq -S -c -n \
    --arg finding_id "$finding_id" --arg review_key "$EXPECTED_REVIEW_KEY" \
    --arg merge_key "$merge_key" --argjson evidence "$pointer" \
    --arg candidate_id "$candidate_id" \
    '{schema:"kc-pr-flow.review-finding/v1",finding_id:$finding_id,review_key:$review_key,merge_key:$merge_key,path:"src/review.sh",side:"RIGHT",anchor_sha256:"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",category:"security",claim_key:"unchecked-boundary",candidate_ids:[$candidate_id],evidence:$evidence}')"
  finding_event="$(rehash_event "$(jq -c --argjson finding "$finding" '.sequence=3 | .event_type="synthesis.finished" | .payload={findings:[$finding],uncertain_candidate_ids:[]}' <<<"$fixture_event")")"

  if review_runtime_evidence_pointer_valid "$pointer"; then
    pass
  else
    fail "shared evidence validator accepts one exact-head RIGHT pointer"
  fi
  reason="$(review_runtime_validate_line "$candidate_event")"
  assert_eq "exact-head candidate event validates" "" "$reason"
  reason="$(review_runtime_validate_line "$finding_event")"
  assert_eq "evidence-hash-bound finding event validates" "" "$reason"
  mutated_event="$(rehash_event "$(jq -c '.payload.findings[0].evidence.review_key="eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"' <<<"$finding_event")")"
  reason="$(review_runtime_validate_line "$mutated_event")"
  assert_eq "finding evidence review key must equal containing event" "evidence_identity_mismatch" "$reason"

  for scoped_kind in pr_body review_comment; do
    if [ "$scoped_kind" = 'pr_body' ]; then
      scoped_pointer="$(jq -S -c -n \
        --arg review_key "$EXPECTED_REVIEW_KEY" --arg repository "$REPOSITORY" \
        --arg base_sha "$BASE_SHA" --arg head_sha "$HEAD_SHA" \
        --arg content_sha256 "$evidence_hash" \
        '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"pr_body",review_key:$review_key,repository:$repository,base_sha:$base_sha,head_sha:$head_sha,object_sha:$head_sha,pr_number:42,locator:"body",content_sha256:$content_sha256}')"
    else
      scoped_pointer="$(jq -S -c -n \
        --arg review_key "$EXPECTED_REVIEW_KEY" --arg repository "$REPOSITORY" \
        --arg base_sha "$BASE_SHA" --arg head_sha "$HEAD_SHA" \
        --arg content_sha256 "$evidence_hash" \
        '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"review_comment",review_key:$review_key,repository:$repository,base_sha:$base_sha,head_sha:$head_sha,object_sha:$head_sha,pr_number:42,comment_id:9001,path:"src/review.sh",side:"RIGHT",line:7,locator:"comment",content_sha256:$content_sha256}')"
    fi

    scoped_candidate="$(jq -c --argjson evidence "$scoped_pointer" '.evidence=$evidence' <<<"$candidate")"
    scoped_event="$(rehash_event "$(jq -c --argjson candidate "$scoped_candidate" '.sequence=2 | .event_type="finding.observed" | .payload={candidate:$candidate}' <<<"$fixture_event")")"
    reason="$(review_runtime_validate_line "$scoped_event")"
    assert_eq "$scoped_kind candidate accepts matching PR locator" "" "$reason"
    mutated_event="$(rehash_event "$(jq -c '.payload.candidate.evidence.pr_number=43' <<<"$scoped_event")")"
    standalone_pointer="$(jq -c '.payload.candidate.evidence' <<<"$mutated_event")"
    if review_runtime_evidence_pointer_valid "$standalone_pointer"; then
      pass
    else
      fail "$scoped_kind standalone pointer keeps its own typed PR locator"
    fi
    reason="$(review_runtime_validate_line "$mutated_event")"
    assert_eq "$scoped_kind candidate rejects another PR locator" "evidence_identity_mismatch" "$reason"

    scoped_finding="$(jq -c --argjson evidence "$scoped_pointer" '.evidence=$evidence' <<<"$finding")"
    scoped_event="$(rehash_event "$(jq -c --argjson finding "$scoped_finding" '.sequence=3 | .event_type="synthesis.finished" | .payload={findings:[$finding],uncertain_candidate_ids:[]}' <<<"$fixture_event")")"
    reason="$(review_runtime_validate_line "$scoped_event")"
    assert_eq "$scoped_kind finding accepts matching PR locator" "" "$reason"
    mutated_event="$(rehash_event "$(jq -c '.payload.findings[0].evidence.pr_number=43' <<<"$scoped_event")")"
    reason="$(review_runtime_validate_line "$mutated_event")"
    assert_eq "$scoped_kind finding rejects another PR locator" "evidence_identity_mismatch" "$reason"
  done

  scoped_pointer="$(jq -S -c -n \
    --arg review_key "$EXPECTED_REVIEW_KEY" --arg repository "$REPOSITORY" \
    --arg base_sha "$BASE_SHA" --arg head_sha "$HEAD_SHA" \
    --arg content_sha256 "$evidence_hash" \
    '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"issue",review_key:$review_key,repository:$repository,base_sha:$base_sha,head_sha:$head_sha,object_sha:$head_sha,issue_number:43,locator:"issue",content_sha256:$content_sha256}')"
  scoped_candidate="$(jq -c --argjson evidence "$scoped_pointer" '.evidence=$evidence' <<<"$candidate")"
  scoped_event="$(rehash_event "$(jq -c --argjson candidate "$scoped_candidate" '.sequence=2 | .event_type="finding.observed" | .payload={candidate:$candidate}' <<<"$fixture_event")")"
  reason="$(review_runtime_validate_line "$scoped_event")"
  assert_eq "issue candidate locator remains independent from PR number" "" "$reason"
  scoped_finding="$(jq -c --argjson evidence "$scoped_pointer" '.evidence=$evidence' <<<"$finding")"
  scoped_event="$(rehash_event "$(jq -c --argjson finding "$scoped_finding" '.sequence=3 | .event_type="synthesis.finished" | .payload={findings:[$finding],uncertain_candidate_ids:[]}' <<<"$fixture_event")")"
  reason="$(review_runtime_validate_line "$scoped_event")"
  assert_eq "issue finding locator remains independent from PR number" "" "$reason"

  while IFS='|' read -r mutation_name mutation_filter; do
    [ -n "$mutation_name" ] || continue
    mutated_event="$(rehash_event "$(jq -c "$mutation_filter" <<<"$candidate_event")")"
    reason="$(review_runtime_validate_line "$mutated_event")"
    assert_eq "$mutation_name" "evidence_identity_mismatch" "$reason"
  done <<'MUTATIONS'
nested review key must equal containing event|.payload.candidate.evidence.review_key="eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
nested base SHA must equal containing event|.payload.candidate.evidence.base_sha="1111111111111111111111111111111111111111"
nested head SHA must equal containing event|.payload.candidate.evidence.head_sha="2222222222222222222222222222222222222222"
RIGHT git blob must bind object SHA to head|.payload.candidate.evidence.object_sha=.base_sha
FILE git blob must bind object SHA to head|.payload.candidate.side="FILE" | .payload.candidate.evidence.side="FILE" | .payload.candidate.evidence.object_sha=.base_sha
LEFT git blob must bind object SHA to base|.payload.candidate.side="LEFT" | .payload.candidate.evidence.side="LEFT" | .payload.candidate.evidence.object_sha=.head_sha
MUTATIONS

  validator_probe="$TEST_STATE_ROOT/evidence-validator-probe"
  (
    export T8_VALIDATOR_PROBE="$validator_probe"
    review_runtime_evidence_pointer_valid() {
      : >"$T8_VALIDATOR_PROBE"
      return 1
    }
    review_runtime_validate_line "$candidate_event" >/dev/null
  )
  if [ -f "$validator_probe" ]; then
    pass
  else
    fail "event validation and verify-evidence share one pointer validator"
  fi

  old_candidate_id="$candidate_id"
  mutated_event="$(rehash_event "$(jq -c --arg hash "$changed_hash" '.payload.candidate.evidence.content_sha256=$hash' <<<"$candidate_event")")"
  reason="$(review_runtime_validate_line "$mutated_event")"
  assert_eq "candidate identity changes with evidence content hash" "candidate_id_mismatch" "$reason"
  assert_eq "candidate test retains the original identity for the drift probe" "$old_candidate_id" "$(jq -r '.payload.candidate.candidate_id' <<<"$mutated_event")"

  old_merge_key="$merge_key"
  old_finding_id="$finding_id"
  mutated_event="$(rehash_event "$(jq -c --arg hash "$changed_hash" '.payload.findings[0].evidence.content_sha256=$hash' <<<"$finding_event")")"
  reason="$(review_runtime_validate_line "$mutated_event")"
  assert_eq "merge identity changes with evidence content hash" "merge_key_mismatch" "$reason"
  assert_eq "finding drift probe retains the old merge key" "$old_merge_key" "$(jq -r '.payload.findings[0].merge_key' <<<"$mutated_event")"
  assert_eq "finding drift probe retains the old finding id" "$old_finding_id" "$(jq -r '.payload.findings[0].finding_id' <<<"$mutated_event")"
  mutated_event="$(rehash_event "$(jq -c --arg hash "$changed_hash" --arg merge_key "src/review.sh|RIGHT|$changed_hash|security|unchecked-boundary" '.payload.findings[0].evidence.content_sha256=$hash | .payload.findings[0].merge_key=$merge_key' <<<"$finding_event")")"
  reason="$(review_runtime_validate_line "$mutated_event")"
  assert_eq "finding identity changes after evidence-bound merge key changes" "finding_id_mismatch" "$reason"
}

if [ "$CASE_FILTER" = 'privacy-envelope' ]; then
  run_privacy_envelope_tests
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit $?
elif [ "$CASE_FILTER" = 'safe-io' ]; then
  run_safe_io_tests
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit $?
elif [ "$CASE_FILTER" = 'evidence-binding' ]; then
  run_evidence_binding_tests
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit $?
elif [ "$CASE_FILTER" != 'all' ]; then
  printf 'unknown test case: %s\n' "$CASE_FILTER" >&2
  exit 2
fi

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
future_event="$(rehash_integrity "$(jq -c '.occurred_at="2026-07-22T00:00:01Z"' <<<"$fresh_fixture")")"
future_event="$(printf '%s' "$future_event" | sed 's/,"config_hash"/,  "config_hash"/')"
printf '%s\n' "$future_event" >"$TEST_STATE_ROOT/future-event.jsonl"
future_output="$(bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/future-event.jsonl")"
future_rc=$?
assert_eq "same event ID with changed envelope reaches duplicate identity check" "1" "$future_rc"
assert_eq "different event with reused event_id is quarantined" "1" "$(jq -r '.quarantined' <<<"$future_output")"
assert_eq "event_id conflict does not mutate accepted events" "1" "$(wc -l <"$FRESH_EVENTS" | tr -d ' ')"

# A new event ID with an unknown top-level field is rejected before append.
optional_new="$(rehash_event "$(jq -c '.sequence=2 | .future_optional={mode:"preserve"}' <<<"$fresh_fixture")")"
optional_new="$(printf '%s' "$optional_new" | sed 's/,"config_hash"/,  "config_hash"/')"
printf '%s\n' "$optional_new" >"$TEST_STATE_ROOT/optional-new.jsonl"
optional_output="$(bash "$RUNTIME" append --event-file "$TEST_STATE_ROOT/optional-new.jsonl")"
optional_rc=$?
assert_eq "unknown top-level v1 event is quarantined" "1" "$optional_rc"
assert_eq "unknown top-level v1 event reports one quarantine" "1" "$(jq -r '.quarantined' <<<"$optional_output")"
assert_eq "unknown top-level v1 event leaves accepted events unchanged" "1" "$(wc -l <"$FRESH_EVENTS" | tr -d ' ')"

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
assert_eq "busy append lock leaves accepted state unchanged" "1" "$(wc -l <"$FRESH_EVENTS" | tr -d ' ')"

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
assert_eq "all invalid/conflicting records have separate quarantine entries" "8" "$(find "$QUARANTINE_ROOT" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
assert_eq "quarantine records unsupported major reason" "1" "$(grep -l 'unsupported_schema_major' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"
assert_eq "quarantine records unknown event reason" "1" "$(grep -l 'unknown_event_type' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"
assert_eq "quarantine records missing-field reason" "1" "$(grep -l 'missing_required_field' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"
assert_eq "quarantine records hash mismatch reason" "1" "$(grep -l 'payload_hash_mismatch' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"
assert_eq "quarantine records successor enum reason" "1" "$(grep -l 'invalid_successor_reason' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"
assert_eq "quarantine records unsupported payload schema reason" "1" "$(grep -l 'unsupported_payload_schema' "$QUARANTINE_ROOT"/*/metadata.json | wc -l | tr -d ' ')"
conflict_dir="$(grep -l 'event_id_conflict' "$QUARANTINE_ROOT"/*/metadata.json | xargs dirname)"
assert_eq "quarantine stores one metadata file only" "metadata.json" "$(find "$conflict_dir" -mindepth 1 -maxdepth 1 -type f -exec basename {} \;)"
assert_eq "quarantine metadata uses the closed four-key envelope" '["byte_count","input_sha256","quarantined_at","reason_code"]' "$(jq -c 'keys | sort' "$conflict_dir/metadata.json")"
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
nonstart_first="$(rehash_event "$(jq -c '.run_id="run-first-nonstart" | .event_type="head.observed" | .sequence=1 | .payload={head_sha:.head_sha}' <<<"$fresh_fixture")")"
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
printf '%s\n' '{"reason":"invalid_json","event_sha256":"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","quarantined_at":"2026-07-22T00:00:00Z"}' >"$mismatch_quarantine_dir/metadata.json"
chmod 0400 "$mismatch_quarantine_dir/metadata.json"
chmod 0500 "$mismatch_quarantine_dir"
review_runtime_quarantine "$mismatch_quarantine_line" invalid_json >/dev/null 2>&1
mismatch_quarantine_rc=$?
assert_eq "mismatched quarantine artifacts fail closed" "74" "$mismatch_quarantine_rc"

idempotent_quarantine_line='{"case":"complete idempotent quarantine"}'
idempotent_quarantine_hash="$(sha256_text "$idempotent_quarantine_line")"
idempotent_quarantine_dir="$QUARANTINE_ROOT/$idempotent_quarantine_hash-invalid_json"
review_runtime_quarantine "$idempotent_quarantine_line" invalid_json >/dev/null 2>&1
idempotent_first_rc=$?
idempotent_metadata_hash_before="$(review_runtime_sha256 <"$idempotent_quarantine_dir/metadata.json")"
review_runtime_quarantine "$idempotent_quarantine_line" invalid_json >/dev/null 2>&1
idempotent_second_rc=$?
assert_eq "first complete quarantine publication succeeds" "0" "$idempotent_first_rc"
assert_eq "matching complete quarantine is idempotent" "0" "$idempotent_second_rc"
assert_eq "idempotent quarantine preserves metadata bytes" "$idempotent_metadata_hash_before" "$(review_runtime_sha256 <"$idempotent_quarantine_dir/metadata.json")"
assert_eq "idempotent quarantine remains metadata-only" "1" "$(find "$idempotent_quarantine_dir" -mindepth 1 -maxdepth 1 -type f | wc -l | tr -d ' ')"
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
assert_eq "retry receipt contains metadata only" "1" "$(find "$forced_quarantine_dir" -mindepth 1 -maxdepth 1 -type f | wc -l | tr -d ' ')"
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

sequence_two="$(rehash_event "$(jq -c '.event_type="head.observed" | .sequence=2 | .payload={head_sha:.head_sha}' <<<"$fresh_fixture")")"
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
gap_sequence="$(rehash_event "$(jq -c '.event_type="run.invalidated" | .sequence=4 | .payload={reason:"head_moved"}' <<<"$fresh_fixture")")"
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

dead_owner_candidate="$(rehash_event "$(jq -c '.event_type="head.observed" | .sequence=3 | .payload={head_sha:.head_sha}' <<<"$fresh_fixture")")"
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
assert_eq "oversized next log returns the typed oversize status" "73" "$atomic_append_rc"
assert_eq "oversized next log reports blocked" "1" "$(jq -r '.blocked' <<<"$atomic_append_output")"
if cmp -s "$atomic_before" "$sequence_events"; then pass; else fail "failed atomic append changes original events bytes"; fi
assert_eq "failed atomic append leaves no partial temp" "0" "$(find "$sequence_run_dir" -maxdepth 1 -name '.events.next.*' | wc -l | tr -d ' ')"
assert_eq "failed atomic append cleans owned lock" "false" "$([ -e "$sequence_lock" ] && printf true || printf false)"

# Existing malformed ordering blocks all mutation.
malformed_state="$(mktemp -d)"
malformed_run_dir="$malformed_state/$REPO_KEY/pr-$PR_NUMBER/run-fixture-fresh"
mkdir -p "$malformed_run_dir"
malformed_three="$(rehash_event "$(jq -c '.event_type="head.observed" | .sequence=3 | .payload={head_sha:.head_sha}' <<<"$fresh_fixture")")"
printf '%s\n%s\n' "$fresh_fixture" "$malformed_three" >"$malformed_run_dir/events.jsonl"
chmod 0600 "$malformed_run_dir/events.jsonl"
cp "$malformed_run_dir/events.jsonl" "$TEST_STATE_ROOT/malformed-before.jsonl"
malformed_four="$(rehash_event "$(jq -c '.event_type="head.observed" | .sequence=4 | .payload={head_sha:.head_sha}' <<<"$fresh_fixture")")"
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
concurrent_event="$(rehash_event "$(jq -c '
  .run_id="run-concurrent-first" |
  .extensions=[range(0; 300) as $index | {
    namespace:"org.kc.concurrency",
    key:("probe_" + ($index | tostring)),
    value_sha256:"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
    byte_count:$index
  }]' <<<"$fresh_fixture")")"
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
t2_merge_key="evidence.txt|RIGHT|$t2_evidence_hash|security|unchecked-boundary"
t2_finding_id="$(sha256_text "$EXPECTED_REVIEW_KEY|$t2_merge_key")"
t2_pointer="$(jq -S -c -n \
  --arg review_key "$EXPECTED_REVIEW_KEY" --arg repository "$REPOSITORY" \
  --arg base_sha "$BASE_SHA" --arg head_sha "$HEAD_SHA" \
  --arg content_sha256 "$t2_evidence_hash" \
  '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",review_key:$review_key,repository:$repository,base_sha:$base_sha,head_sha:$head_sha,object_sha:$head_sha,path:"evidence.txt",side:"RIGHT",line:2,locator:"review-anchor",content_sha256:$content_sha256}')"
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
t2_verify_pointer="$(jq -S -c -n \
  --arg review_key "$EXPECTED_REVIEW_KEY" --arg repository "$REPOSITORY" \
  --arg object_sha "$t2_object_sha" --arg content_sha256 "$t2_evidence_hash" \
  '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",review_key:$review_key,repository:$repository,base_sha:$object_sha,head_sha:$object_sha,object_sha:$object_sha,path:"evidence.txt",side:"RIGHT",line:2,locator:"review-anchor",content_sha256:$content_sha256}')"
printf '%s\n' "$t2_verify_pointer" >"$TEST_STATE_ROOT/t2-pointer.json"
t2_verified="$(bash "$RUNTIME" verify-evidence --pointer-json "$TEST_STATE_ROOT/t2-pointer.json" --repo "$t2_repo")"
t2_verified_rc=$?
assert_eq "git_blob evidence verifies exact bytes" "0" "$t2_verified_rc"
assert_eq "verified evidence returns typed status" "verified" "$(jq -r '.status' <<<"$t2_verified")"
if printf '%s' "$t2_verified" | grep -F 'line one' >/dev/null 2>&1; then fail "evidence verification emits source content"; else pass; fi

t2_pointer_swap_source="$TEST_STATE_ROOT/t2-pointer-swap.json"
t2_pointer_swap_replacement="$TEST_STATE_ROOT/t2-pointer-swap-replacement.json"
printf '%s\n' "$t2_verify_pointer" >"$t2_pointer_swap_source"
jq -c '.content_sha256="dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"' <<<"$t2_verify_pointer" >"$t2_pointer_swap_replacement"
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

t2_tree_pointer="$(jq -c '.path="dir" | .line=null | .locator="tree-probe"' <<<"$t2_verify_pointer")"
printf '%s\n' "$t2_tree_pointer" >"$TEST_STATE_ROOT/t2-tree-pointer.json"
t2_tree_output="$(bash "$RUNTIME" verify-evidence --pointer-json "$TEST_STATE_ROOT/t2-tree-pointer.json" --repo "$t2_repo")"
t2_tree_rc=$?
assert_eq "tree evidence is not accepted as a blob" "3" "$t2_tree_rc"
assert_eq "tree evidence returns typed not-blob status" "not_blob" "$(jq -r '.status' <<<"$t2_tree_output")"

t2_drift_pointer="$(jq -c '.content_sha256="dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"' <<<"$t2_verify_pointer")"
printf '%s\n' "$t2_drift_pointer" >"$TEST_STATE_ROOT/t2-drift-pointer.json"
t2_drift="$(bash "$RUNTIME" verify-evidence --pointer-json "$TEST_STATE_ROOT/t2-drift-pointer.json" --repo "$t2_repo")"
t2_drift_rc=$?
assert_eq "evidence hash drift is nonzero" "1" "$t2_drift_rc"
assert_eq "evidence hash drift is typed" "hash_mismatch" "$(jq -r '.status' <<<"$t2_drift")"
t2_nonlocal="$(jq -S -c -n --arg review_key "$EXPECTED_REVIEW_KEY" --arg repository "$REPOSITORY" --arg base_sha "$BASE_SHA" --arg head_sha "$HEAD_SHA" --arg hash "$t2_evidence_hash" '{schema:"kc-pr-flow.evidence-pointer/v1",kind:"pr_body",review_key:$review_key,repository:$repository,base_sha:$base_sha,head_sha:$head_sha,object_sha:$head_sha,pr_number:42,locator:"body",content_sha256:$hash}')"
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

# Once-only posting (increment 2.3): the five reserved receipt events close
# their payload schema instead of accepting an empty placeholder, and
# authorization.granted / post.intent additionally bind a T2 idempotency key
# derived from review_key|commit_id|payload_sha256 (A2 design). The runtime
# still grants these events no posting or GitHub authority — see the
# "command is out of scope" assertions above, which stay unchanged.
once_only_commit_id="$HEAD_SHA"
once_only_payload_sha256="$(sha256_text 'kc-pr-flow.once-only-posting-payload-fixture')"
once_only_idempotency_key="$(review_runtime_idempotency_key "$EXPECTED_REVIEW_KEY" "$once_only_commit_id" "$once_only_payload_sha256")"

once_only_head_observed_valid="$(rehash_event "$(jq -c --arg head_sha "$HEAD_SHA" '.sequence=2 | .event_type="head.observed" | .payload={head_sha:$head_sha}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_head_observed_valid" >"$TEST_STATE_ROOT/once-only-head-observed-valid.jsonl"
once_only_head_observed_valid_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-head-observed-valid.jsonl")"
assert_eq "head.observed with a bound head_sha validates" "1" "$(jq -r '.valid' <<<"$once_only_head_observed_valid_output")"

once_only_head_observed_empty="$(rehash_event "$(jq -c '.sequence=2 | .event_type="head.observed" | .payload={}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_head_observed_empty" >"$TEST_STATE_ROOT/once-only-head-observed-empty.jsonl"
once_only_head_observed_empty_stderr="$TEST_STATE_ROOT/once-only-head-observed-empty.stderr"
once_only_head_observed_empty_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-head-observed-empty.jsonl" 2>"$once_only_head_observed_empty_stderr")"
assert_eq "head.observed no longer accepts an empty placeholder payload" "1" "$(jq -r '.invalid' <<<"$once_only_head_observed_empty_output")"
assert_match "head.observed empty payload uses the closed schema reason" 'unsupported_payload_schema' "$(cat "$once_only_head_observed_empty_stderr")"

once_only_authorization_granted_valid="$(rehash_event "$(jq -c --arg commit_id "$once_only_commit_id" --arg payload_sha256 "$once_only_payload_sha256" --arg idempotency_key "$once_only_idempotency_key" '.sequence=2 | .event_type="authorization.granted" | .payload={commit_id:$commit_id,event:"APPROVE",idempotency_key:$idempotency_key,payload_sha256:$payload_sha256}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_authorization_granted_valid" >"$TEST_STATE_ROOT/once-only-authorization-granted-valid.jsonl"
once_only_authorization_granted_valid_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-authorization-granted-valid.jsonl")"
assert_eq "authorization.granted with a bound idempotency key validates" "1" "$(jq -r '.valid' <<<"$once_only_authorization_granted_valid_output")"

once_only_authorization_granted_mismatch="$(rehash_event "$(jq -c --arg commit_id "$once_only_commit_id" --arg payload_sha256 "$once_only_payload_sha256" --arg idempotency_key "$(sha256_text 'wrong-idempotency-key')" '.sequence=2 | .event_type="authorization.granted" | .payload={commit_id:$commit_id,event:"APPROVE",idempotency_key:$idempotency_key,payload_sha256:$payload_sha256}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_authorization_granted_mismatch" >"$TEST_STATE_ROOT/once-only-authorization-granted-mismatch.jsonl"
once_only_authorization_granted_mismatch_stderr="$TEST_STATE_ROOT/once-only-authorization-granted-mismatch.stderr"
once_only_authorization_granted_mismatch_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-authorization-granted-mismatch.jsonl" 2>"$once_only_authorization_granted_mismatch_stderr")"
assert_eq "authorization.granted rejects a recomputed idempotency-key mismatch" "1" "$(jq -r '.invalid' <<<"$once_only_authorization_granted_mismatch_output")"
assert_match "idempotency-key mismatch is T2-typed" 'idempotency_key_mismatch' "$(cat "$once_only_authorization_granted_mismatch_stderr")"

once_only_moved_commit_id="dddddddddddddddddddddddddddddddddddddddd"
once_only_moved_idempotency_key="$(review_runtime_idempotency_key "$EXPECTED_REVIEW_KEY" "$once_only_moved_commit_id" "$once_only_payload_sha256")"
once_only_authorization_head_mismatch="$(rehash_event "$(jq -c --arg commit_id "$once_only_moved_commit_id" --arg payload_sha256 "$once_only_payload_sha256" --arg idempotency_key "$once_only_moved_idempotency_key" '.sequence=2 | .event_type="authorization.granted" | .payload={commit_id:$commit_id,event:"APPROVE",idempotency_key:$idempotency_key,payload_sha256:$payload_sha256}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_authorization_head_mismatch" >"$TEST_STATE_ROOT/once-only-authorization-head-mismatch.jsonl"
once_only_authorization_head_mismatch_stderr="$TEST_STATE_ROOT/once-only-authorization-head-mismatch.stderr"
once_only_authorization_head_mismatch_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-authorization-head-mismatch.jsonl" 2>"$once_only_authorization_head_mismatch_stderr")"
assert_eq "authorization.granted binds commit_id to the exact reviewed head" "1" "$(jq -r '.invalid' <<<"$once_only_authorization_head_mismatch_output")"
assert_match "authorization head mismatch is T2-typed" 'authorization_head_mismatch' "$(cat "$once_only_authorization_head_mismatch_stderr")"

once_only_post_intent_valid="$(rehash_event "$(jq -c --arg commit_id "$once_only_commit_id" --arg payload_sha256 "$once_only_payload_sha256" --arg idempotency_key "$once_only_idempotency_key" '.sequence=2 | .event_type="post.intent" | .payload={commit_id:$commit_id,idempotency_key:$idempotency_key,payload_sha256:$payload_sha256}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_post_intent_valid" >"$TEST_STATE_ROOT/once-only-post-intent-valid.jsonl"
once_only_post_intent_valid_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-post-intent-valid.jsonl")"
assert_eq "post.intent with a bound idempotency key validates" "1" "$(jq -r '.valid' <<<"$once_only_post_intent_valid_output")"

once_only_post_intent_mismatch="$(rehash_event "$(jq -c --arg commit_id "$once_only_commit_id" --arg payload_sha256 "$once_only_payload_sha256" --arg idempotency_key "$(sha256_text 'wrong-idempotency-key')" '.sequence=2 | .event_type="post.intent" | .payload={commit_id:$commit_id,idempotency_key:$idempotency_key,payload_sha256:$payload_sha256}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_post_intent_mismatch" >"$TEST_STATE_ROOT/once-only-post-intent-mismatch.jsonl"
once_only_post_intent_mismatch_stderr="$TEST_STATE_ROOT/once-only-post-intent-mismatch.stderr"
once_only_post_intent_mismatch_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-post-intent-mismatch.jsonl" 2>"$once_only_post_intent_mismatch_stderr")"
assert_eq "post.intent rejects a recomputed idempotency-key mismatch" "1" "$(jq -r '.invalid' <<<"$once_only_post_intent_mismatch_output")"
assert_match "post.intent idempotency-key mismatch is T2-typed" 'idempotency_key_mismatch' "$(cat "$once_only_post_intent_mismatch_stderr")"

once_only_post_intent_head_mismatch="$(rehash_event "$(jq -c --arg commit_id "$once_only_moved_commit_id" --arg payload_sha256 "$once_only_payload_sha256" --arg idempotency_key "$once_only_moved_idempotency_key" '.sequence=2 | .event_type="post.intent" | .payload={commit_id:$commit_id,idempotency_key:$idempotency_key,payload_sha256:$payload_sha256}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_post_intent_head_mismatch" >"$TEST_STATE_ROOT/once-only-post-intent-head-mismatch.jsonl"
once_only_post_intent_head_mismatch_stderr="$TEST_STATE_ROOT/once-only-post-intent-head-mismatch.stderr"
once_only_post_intent_head_mismatch_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-post-intent-head-mismatch.jsonl" 2>"$once_only_post_intent_head_mismatch_stderr")"
assert_eq "post.intent binds commit_id to the exact reviewed head" "1" "$(jq -r '.invalid' <<<"$once_only_post_intent_head_mismatch_output")"
assert_match "post.intent head mismatch is T2-typed" 'authorization_head_mismatch' "$(cat "$once_only_post_intent_head_mismatch_stderr")"

once_only_post_result_posted="$(rehash_event "$(jq -c --arg idempotency_key "$once_only_idempotency_key" '.sequence=2 | .event_type="post.result" | .payload={outcome:"posted",remote_review_id:987654321,idempotency_key:$idempotency_key}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_post_result_posted" >"$TEST_STATE_ROOT/once-only-post-result-posted.jsonl"
once_only_post_result_posted_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-post-result-posted.jsonl")"
assert_eq "post.result posted outcome with a remote review id validates" "1" "$(jq -r '.valid' <<<"$once_only_post_result_posted_output")"

once_only_post_result_reconciled="$(rehash_event "$(jq -c --arg idempotency_key "$once_only_idempotency_key" '.sequence=2 | .event_type="post.result" | .payload={outcome:"posted_reconciled",remote_review_id:987654321,idempotency_key:$idempotency_key}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_post_result_reconciled" >"$TEST_STATE_ROOT/once-only-post-result-reconciled.jsonl"
once_only_post_result_reconciled_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-post-result-reconciled.jsonl")"
assert_eq "post.result posted_reconciled outcome with a remote review id validates" "1" "$(jq -r '.valid' <<<"$once_only_post_result_reconciled_output")"

once_only_post_result_failed="$(rehash_event "$(jq -c --arg idempotency_key "$once_only_idempotency_key" '.sequence=2 | .event_type="post.result" | .payload={outcome:"failed",idempotency_key:$idempotency_key}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_post_result_failed" >"$TEST_STATE_ROOT/once-only-post-result-failed.jsonl"
once_only_post_result_failed_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-post-result-failed.jsonl")"
assert_eq "post.result failed outcome without a remote review id validates" "1" "$(jq -r '.valid' <<<"$once_only_post_result_failed_output")"

once_only_post_result_failed_with_id="$(rehash_event "$(jq -c --arg idempotency_key "$once_only_idempotency_key" '.sequence=2 | .event_type="post.result" | .payload={outcome:"failed",remote_review_id:1,idempotency_key:$idempotency_key}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_post_result_failed_with_id" >"$TEST_STATE_ROOT/once-only-post-result-failed-with-id.jsonl"
once_only_post_result_failed_with_id_stderr="$TEST_STATE_ROOT/once-only-post-result-failed-with-id.stderr"
once_only_post_result_failed_with_id_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-post-result-failed-with-id.jsonl" 2>"$once_only_post_result_failed_with_id_stderr")"
assert_eq "post.result rejects a failed outcome carrying a remote review id" "1" "$(jq -r '.invalid' <<<"$once_only_post_result_failed_with_id_output")"
assert_match "failed-with-id uses the closed schema reason" 'unsupported_payload_schema' "$(cat "$once_only_post_result_failed_with_id_stderr")"

once_only_post_result_posted_missing_id="$(rehash_event "$(jq -c --arg idempotency_key "$once_only_idempotency_key" '.sequence=2 | .event_type="post.result" | .payload={outcome:"posted",idempotency_key:$idempotency_key}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_post_result_posted_missing_id" >"$TEST_STATE_ROOT/once-only-post-result-posted-missing-id.jsonl"
once_only_post_result_posted_missing_id_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-post-result-posted-missing-id.jsonl")"
assert_eq "post.result rejects a posted outcome missing the remote review id" "1" "$(jq -r '.invalid' <<<"$once_only_post_result_posted_missing_id_output")"

once_only_post_result_unknown_outcome="$(rehash_event "$(jq -c --arg idempotency_key "$once_only_idempotency_key" '.sequence=2 | .event_type="post.result" | .payload={outcome:"pending",idempotency_key:$idempotency_key}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_post_result_unknown_outcome" >"$TEST_STATE_ROOT/once-only-post-result-unknown-outcome.jsonl"
once_only_post_result_unknown_outcome_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-post-result-unknown-outcome.jsonl")"
assert_eq "post.result rejects an unenumerated outcome" "1" "$(jq -r '.invalid' <<<"$once_only_post_result_unknown_outcome_output")"

for once_only_reason in head_moved payload_changed identity_changed expired; do
  once_only_invalidated_valid="$(rehash_event "$(jq -c --arg reason "$once_only_reason" '.sequence=2 | .event_type="run.invalidated" | .payload={reason:$reason}' <<<"$fresh_fixture")")"
  printf '%s\n' "$once_only_invalidated_valid" >"$TEST_STATE_ROOT/once-only-invalidated-$once_only_reason.jsonl"
  once_only_invalidated_valid_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-invalidated-$once_only_reason.jsonl")"
  assert_eq "run.invalidated accepts reason $once_only_reason" "1" "$(jq -r '.valid' <<<"$once_only_invalidated_valid_output")"
done

once_only_invalidated_unknown_reason="$(rehash_event "$(jq -c '.sequence=2 | .event_type="run.invalidated" | .payload={reason:"scope_creep"}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_invalidated_unknown_reason" >"$TEST_STATE_ROOT/once-only-invalidated-unknown.jsonl"
once_only_invalidated_unknown_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-invalidated-unknown.jsonl")"
assert_eq "run.invalidated rejects an unenumerated reason" "1" "$(jq -r '.invalid' <<<"$once_only_invalidated_unknown_output")"

once_only_invalidated_extra_field="$(rehash_event "$(jq -c '.sequence=2 | .event_type="run.invalidated" | .payload={reason:"head_moved",note:"unexpected"}' <<<"$fresh_fixture")")"
printf '%s\n' "$once_only_invalidated_extra_field" >"$TEST_STATE_ROOT/once-only-invalidated-extra-field.jsonl"
once_only_invalidated_extra_field_output="$(bash "$RUNTIME" validate --event-file "$TEST_STATE_ROOT/once-only-invalidated-extra-field.jsonl")"
assert_eq "run.invalidated payload is closed to extra fields" "1" "$(jq -r '.invalid' <<<"$once_only_invalidated_extra_field_output")"

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
