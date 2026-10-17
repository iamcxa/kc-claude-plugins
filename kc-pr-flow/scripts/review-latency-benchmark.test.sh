#!/usr/bin/env bash

set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCORER="$HERE/review-latency-benchmark.sh"
CORPUS="$HERE/../test/fixtures/review-plan/phase1-promotion.jsonl"
SCENARIOS="$HERE/../test/fixtures/review-plan/phase1-promotion-scenarios.jsonl"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/review-structural-test.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT

PASS=0
FAIL=0

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  if [ "$expected" = "$actual" ]; then
    PASS=$((PASS + 1))
    printf 'PASS: %s\n' "$label"
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL: %s\n  expected: %s\n  actual:   %s\n' "$label" "$expected" "$actual"
  fi
}

score_file() {
  bash "$SCORER" score --corpus "$1" --scenarios "${2:-$SCENARIOS}" 2>/dev/null
}

first_failed() {
  score_file "$1" | jq -r '.first_failed_gate // ""'
}

mutate_pair() {
  local pair_id="$1" filter="$2" output="$3"
  jq -c --arg pair_id "$pair_id" \
    "if .pair_id == \$pair_id then ($filter) else . end" "$CORPUS" >"$output"
}

expect_rejected() {
  local label="$1" corpus="$2" scenarios="${3:-$SCENARIOS}"
  if score_file "$corpus" "$scenarios" >/dev/null; then
    assert_eq "$label" rejected accepted
  else
    assert_eq "$label" rejected rejected
  fi
}

report="$(score_file "$CORPUS")"
assert_eq "every synthetic row carries closed scenario provenance" true \
  "$(jq -s -r 'all(.[]; (.provenance | keys) == ["fixture_kind","scenario_sha256"] and
    .provenance.fixture_kind == "synthetic-structural" and
    .provenance.scenario_sha256 ==
      "3292c091b41ad4b1eb4de52713a6bc12da5b71d75d8e987bd5a091a9db18f301")' "$CORPUS")"
assert_eq "nine frozen synthetic classes are accepted" 9 "$(jq -r '.pair_count' <<<"$report")"
assert_eq "seven cases are latency eligible" 7 "$(jq -r '.latency.eligible_runs' <<<"$report")"
assert_eq "ordered Q1-Q6 gates pass" \
  "identity,required_coverage,must_fix_recall,precision,behavior_parity,latency" \
  "$(jq -r '[.gate_order[] as $gate | select(.gates[$gate] == true) | $gate] | join(",")' <<<"$report")"
assert_eq "all-green structural evidence never promotes" do_not_promote "$(jq -r '.verdict' <<<"$report")"
assert_eq "report preserves the frozen closed shape" true \
  "$(jq -r 'keys == ["evidence_tier","first_failed_gate","gate_order","gates","latency",
    "pair_count","phase","quality_gates","schema","verdict"]' <<<"$report")"
assert_eq "quality gates exclude latency" \
  "behavior_parity,identity,must_fix_recall,precision,required_coverage" \
  "$(jq -r '.quality_gates | keys | join(",")' <<<"$report")"
assert_eq "two initial fallbacks are excluded" 2 "$(jq -r '.latency.excluded_initial_runs' <<<"$report")"
assert_eq "all seven eligible cases meet 240 seconds" 7 "$(jq -r '.latency.passing_runs' <<<"$report")"
assert_eq "maximum eligible duration is retained" 239000 "$(jq -r '.latency.max_ms' <<<"$report")"

mutated="$TEST_ROOT/mutated.jsonl"
jq -c 'select(.pair_id != "security-finding")' "$CORPUS" >"$mutated"
assert_eq "missing required class fails Q1 first" identity "$(first_failed "$mutated")"
mutate_pair known-fix-only '.observed.completed_capabilities=[]' "$mutated"
assert_eq "missing required capability fails Q2 first" required_coverage "$(first_failed "$mutated")"
mutate_pair known-fix-only '.observed.found_must_fix_count=0' "$mutated"
assert_eq "missed must-fix fails Q3 first" must_fix_recall "$(first_failed "$mutated")"
mutate_pair known-fix-only '.observed.treatment_false_positives=1' "$mutated"
assert_eq "new false positive fails Q4 first" precision "$(first_failed "$mutated")"
mutate_pair known-fix-only '.observed.behavior_parity=false' "$mutated"
assert_eq "behavior drift fails Q5 first" behavior_parity "$(first_failed "$mutated")"
mutate_pair known-fix-only '.observed.timing.review_to_confirmation_ready_ms=240001' "$mutated"
assert_eq "240001 milliseconds fails Q6 first" latency "$(first_failed "$mutated")"
mutate_pair known-fix-only '.caller_verdict="promote"' "$mutated"
expect_rejected "caller verdict is rejected" "$mutated"
mutate_pair known-fix-only '.evidence_tier="actual"' "$mutated"
expect_rejected "non-structural evidence tier is rejected" "$mutated"
mutate_pair known-fix-only '.observed.timing.fixture_kind="actual"' "$mutated"
expect_rejected "non-structural timing is rejected" "$mutated"

self_resealed_corpus="$TEST_ROOT/self-resealed-corpus.jsonl"
self_resealed_scenarios="$TEST_ROOT/self-resealed-scenarios.jsonl"
mutate_pair known-fix-only '.observed.mode="delta"' "$self_resealed_corpus"
jq -c 'if .pair_id == "known-fix-only" then .contract_truth.mode="delta" else . end' \
  "$SCENARIOS" >"$self_resealed_scenarios"
expect_rejected "scenario and observation cannot self-reseal together" \
  "$self_resealed_corpus" "$self_resealed_scenarios"

mutate_pair known-fix-only 'del(.provenance)' "$mutated"
expect_rejected "missing provenance is rejected" "$mutated"
mutate_pair known-fix-only '.provenance.scenario_sha256=("f" * 64)' "$mutated"
expect_rejected "mutated provenance is rejected" "$mutated"
mutate_pair known-fix-only '.provenance.extra=true' "$mutated"
expect_rejected "extra provenance is rejected" "$mutated"
jq -c '., (select(.pair_id == "known-fix-only") | .pair_id="extra-case")' \
  "$CORPUS" >"$mutated"
expect_rejected "extra pair is rejected" "$mutated"

first_line="$(sed -n '1p' "$CORPUS")"
printf '%s\n' "${first_line/\"pair_id\":/\"pair_id\":\"duplicate\",\"pair_id\":}" \
  >"$TEST_ROOT/duplicate-member.jsonl"
expect_rejected "duplicate JSON member is rejected" "$TEST_ROOT/duplicate-member.jsonl"

jq -c -s 'reverse[]' "$CORPUS" >"$TEST_ROOT/reversed.jsonl"
assert_eq "input order does not change report bytes" "$report" "$(score_file "$TEST_ROOT/reversed.jsonl")"
before="$(shasum -a 256 "$CORPUS" | awk '{print $1}')"
score_file "$CORPUS" >/dev/null
assert_eq "scoring does not mutate corpus bytes" "$before" \
  "$(shasum -a 256 "$CORPUS" | awk '{print $1}')"

ln -s "$CORPUS" "$TEST_ROOT/corpus-link.jsonl"
expect_rejected "symlink corpus is rejected" "$TEST_ROOT/corpus-link.jsonl"
mkfifo "$TEST_ROOT/corpus.fifo"
expect_rejected "FIFO corpus is rejected without blocking" "$TEST_ROOT/corpus.fifo"
dd if=/dev/zero of="$TEST_ROOT/oversized.jsonl" bs=1048576 count=2 >/dev/null 2>&1
expect_rejected "oversized corpus is rejected" "$TEST_ROOT/oversized.jsonl"

source_probe="$(bash -c '
  set -u
  umask 027
  before_pwd="$PWD"; before_flags="$-"; before_umask="$(umask)"
  . "$1"
  [ "$before_pwd" = "$PWD" ] && [ "$before_flags" = "$-" ] &&
    [ "$before_umask" = "$(umask)" ] && printf true
' _ "$SCORER")"
assert_eq "sourcing preserves cwd flags and umask" true "$source_probe"

stub_dir="$TEST_ROOT/stubs"
call_ledger="$TEST_ROOT/calls"
mkdir -p "$stub_dir"
: >"$call_ledger"
for command_name in gh curl wget nc ssh codex claude review-post.sh; do
  # The generated stub expands these variables when the stub runs.
  # shellcheck disable=SC2016
  printf '%s\n' '#!/bin/sh' \
    'printf "%s\n" "$(basename "$0") $*" >>"$REVIEW_LATENCY_CALL_LEDGER"' \
    'exit 97' >"$stub_dir/$command_name"
  chmod +x "$stub_dir/$command_name"
done
REVIEW_LATENCY_CALL_LEDGER="$call_ledger" PATH="$stub_dir:$PATH" score_file "$CORPUS" >/dev/null
assert_eq "scoring makes no network model or post call" "" "$(cat "$call_ledger")"

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
