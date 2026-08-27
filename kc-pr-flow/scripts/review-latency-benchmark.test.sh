#!/usr/bin/env bash

set -u

CASE_FILTER=all
if [ "$#" -ne 0 ]; then
  if [ "$#" -ne 2 ] || [ "$1" != '--case' ] || [ "$2" != 'scenario-authority' ]; then
    printf 'usage: %s [--case scenario-authority]\n' "$0" >&2
    exit 2
  fi
  CASE_FILTER="$2"
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCHMARK="$HERE/review-latency-benchmark.sh"
FIXTURE="$HERE/../test/fixtures/review-plan/phase1-promotion.jsonl"
SCENARIOS="$HERE/../test/fixtures/review-plan/phase1-promotion-scenarios.jsonl"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/review-latency-benchmark-test.XXXXXX")"
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

sha256_file() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    sha256sum "$1" | awk '{print $1}'
  fi
}

sha256_text() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 | awk '{print $1}'
  else
    sha256sum | awk '{print $1}'
  fi
}

mutate_case() { # $1=pair id, $2=jq filter, $3=output
  local pair_id="$1" filter="$2" output="$3"
  jq -c --arg pair_id "$pair_id" \
    "if .pair_id == \$pair_id then ($filter) else . end" "$FIXTURE" >"$output"
}

score_file() {
  bash "$BENCHMARK" score --corpus "$1" 2>/dev/null
}

first_failed() {
  score_file "$1" | jq -r '.first_failed_gate // ""'
}

gate_value() { # $1=file $2=gate key
  score_file "$1" | jq -r --arg key "$2" '.gates[$key]'
}

scenario_binding_valid() { # $1=corpus
  jq -e -s --slurpfile scenarios "$SCENARIOS" '
    INDEX($scenarios[]; .pair_id) as $scenario |
    (length == 9) and (($scenarios | length) == 9) and
    ([.[].pair_id] | sort | unique | length == 9) and
    ([$scenarios[].pair_id] | sort | unique | length == 9) and
    all(.[]; . as $pair | $scenario[$pair.pair_id] as $seed |
      $seed.schema == "kc-pr-flow.review-latency-scenario/v1" and
      ($seed | keys | sort == ["change_truth","contract_truth","control_truth","identity",
        "pair_id","schema","treatment_truth"]) and
      ($seed.identity | keys | sort == ["base_sha","config_hash","head_sha","pr_number",
        "repository","review_key"]) and
      ($seed.change_truth | keys | sort == ["changed_hunks","risk_signals"]) and
      ($seed.contract_truth | keys | sort == ["maximum_event","mode","must_fix_claim_keys",
        "required_capabilities"]) and
      ($seed.control_truth | keys | sort == ["adjudication","coverage_gap_refs","event","posted"]) and
      ($seed.treatment_truth | keys | sort == ["capability_gap_refs","event","event_ceiling","finding",
        "from_exclusive","lane_outcomes","mode","raw_phase_timings","reason_codes"]) and
      ($seed.treatment_truth.finding | keys | sort == ["adjudication","capability","category",
        "confidence","posted","severity"]) and
      ($seed.change_truth.changed_hunks | type == "array" and length > 0) and
      ($seed.change_truth.risk_signals | type == "array") and
      ($pair.exact_head == $seed.identity) and
      ($pair.expected.mode == $seed.contract_truth.mode) and
      ($pair.expected.maximum_event == $seed.contract_truth.maximum_event) and
      ($pair.expected.required_capabilities == $seed.contract_truth.required_capabilities) and
      ($pair.expected.must_fix_finding_ids ==
        [$pair.treatment.validated_findings[] |
          select(.candidate.claim_key as $claim |
            $seed.contract_truth.must_fix_claim_keys | index($claim)) | .finding_id]) and
      ($pair.control.behavior_sources.effective.event == $seed.control_truth.event) and
      ($pair.control.behavior_sources.effective.coverage_gap_refs ==
        $seed.control_truth.coverage_gap_refs) and
      ($pair.control.adjudicated_posted == (if $seed.control_truth.posted then 1 else 0 end)) and
      ($pair.control.adjudicated_false_positive ==
        (if $seed.control_truth.adjudication == "false_positive" then 1 else 0 end)) and
      ($pair.treatment.plan.mode == $seed.treatment_truth.mode) and
      ($pair.treatment.plan.event_ceiling == $seed.treatment_truth.event_ceiling) and
      ($pair.treatment.plan.reason_codes == $seed.treatment_truth.reason_codes) and
      ($pair.treatment.plan.review_range.from_exclusive == $seed.treatment_truth.from_exclusive) and
      ($pair.treatment.behavior_sources.effective.event == $seed.treatment_truth.event) and
      ($pair.treatment.capability_coverage == $seed.treatment_truth.lane_outcomes) and
      ($pair.treatment.capability_gap_refs == $seed.treatment_truth.capability_gap_refs) and
      ($pair.treatment.validated_findings[0].candidate.capability ==
        $seed.treatment_truth.finding.capability) and
      ($pair.treatment.validated_findings[0].candidate.category ==
        $seed.treatment_truth.finding.category) and
      ($pair.treatment.validated_findings[0].candidate.severity ==
        $seed.treatment_truth.finding.severity) and
      ($pair.treatment.validated_findings[0].candidate.confidence ==
        $seed.treatment_truth.finding.confidence) and
      ($pair.treatment.validated_findings[0].adjudication ==
        $seed.treatment_truth.finding.adjudication) and
      ($pair.treatment.validated_findings[0].posted == $seed.treatment_truth.finding.posted) and
      (if $seed.treatment_truth.raw_phase_timings == null then
         $pair.treatment.timing == null
       else
         $pair.treatment.timing.durations_ms ==
           $seed.treatment_truth.raw_phase_timings.durations_ms and
         $pair.treatment.timing.lane_durations_ms ==
           $seed.treatment_truth.raw_phase_timings.lane_durations_ms
       end))
  ' "$1" >/dev/null 2>&1
}

expect_rejected() {
  local label="$1" corpus="$2"
  if bash "$BENCHMARK" score --corpus "$corpus" >/dev/null 2>&1; then
    assert_eq "$label" rejected accepted
  else
    assert_eq "$label" rejected rejected
  fi
}

if [ ! -x "$BENCHMARK" ]; then
  printf 'FAIL: scorer does not exist or is not executable: %s\n' "$BENCHMARK"
  exit 1
fi
if [ ! -f "$FIXTURE" ]; then
  printf 'FAIL: fixture does not exist: %s\n' "$FIXTURE"
  exit 1
fi
if [ ! -f "$SCENARIOS" ]; then
  printf 'FAIL: structural scenario authority does not exist: %s\n' "$SCENARIOS"
  exit 1
fi

report="$(score_file "$FIXTURE")"
if scenario_binding_valid "$FIXTURE"; then
  assert_eq "committed corpus is bound to independent scenario truth" true true
else
  assert_eq "committed corpus is bound to independent scenario truth" true false
fi
mutated="$TEST_ROOT/mutated.jsonl"
mutate_case known-fix-only '.expected.mode="delta" | .expected.maximum_event="COMMENT" |
  .expected.required_capabilities=["security"]' "$mutated"
if scenario_binding_valid "$mutated"; then
  assert_eq "expected-only mutation cannot rewrite observed scenario truth" rejected accepted
else
  assert_eq "expected-only mutation cannot rewrite observed scenario truth" rejected rejected
fi
baseline_observed_hash="$(jq -S -c 'select(.pair_id == "known-fix-only") |
  {control,treatment}' "$FIXTURE" | sha256_text)"
mutated_observed_hash="$(jq -S -c 'select(.pair_id == "known-fix-only") |
  {control,treatment}' "$mutated" | sha256_text)"
assert_eq "expected-only mutation leaves control and treatment bytes unchanged" \
  "$baseline_observed_hash" "$mutated_observed_hash"
if [ "$CASE_FILTER" = scenario-authority ]; then
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit
fi
assert_eq "favorable synthetic corpus is not promotable" "do_not_promote" "$(jq -r '.verdict' <<<"$report")"
assert_eq "report identifies structural evidence" "synthetic-structural" \
  "$(jq -r '.evidence_tier' <<<"$report")"
assert_eq "ordered gate schema" "identity,required_coverage,must_fix_recall,precision,behavior_parity,latency" \
  "$(jq -r '.gate_order | join(",")' <<<"$report")"
assert_eq "no failed structural gate" "" "$(jq -r '.first_failed_gate // ""' <<<"$report")"
assert_eq "target is four minutes" "240000" "$(jq -r '.latency.target_ms' <<<"$report")"
assert_eq "initial fallbacks are excluded from latency" "2" \
  "$(jq -r '.latency.excluded_initial_runs' <<<"$report")"
assert_eq "only delta and resolve are eligible" "7" \
  "$(jq -r '.latency.eligible_runs' <<<"$report")"
assert_eq "all eligible fixture runs pass latency" "7" \
  "$(jq -r '.latency.passing_runs' <<<"$report")"
assert_eq "structural timing fixture permits modeled terminal gap above four milliseconds" true \
  "$(jq -s -r '[.[] | select(.treatment.timing != null) |
    .treatment.timing.durations_ms as $d |
    $d.review_to_confirmation_ready - ($d.identity_and_plan + $d.inventory +
      $d.required_lanes_critical_path + $d.targeted_verification_critical_path +
      $d.collation_and_draft) > 4] | all' "$FIXTURE")"
assert_eq "structural timing uses the closed fixture provenance shape" true \
  "$(jq -s -r '[.[] | select(.treatment.timing != null) | .treatment.timing |
    .fixture_kind == "synthetic-structural" and
    (has("schema") | not) and (has("evidence_tier") | not) and
    (has("measured_by") | not)] | all' "$FIXTURE")"
source_probe="$(bash -c '
  set -u
  umask 027
  before_pwd="$PWD"; before_flags="$-"; before_umask="$(umask)"
  . "$1"
  if [ "$before_pwd" = "$PWD" ] && [ "$before_flags" = "$-" ] &&
    [ "$before_umask" = "$(umask)" ]; then
    printf "true\n"
  else
    printf "false\n"
  fi
' _ "$BENCHMARK")"
assert_eq "sourcing preserves cwd flags and umask" true "$source_probe"

stub_dir="$TEST_ROOT/stubs"
call_ledger="$TEST_ROOT/calls"
mkdir -p "$stub_dir"
: >"$call_ledger"
for stub_command in gh curl wget nc ssh codex claude agy review-post.sh; do
  # The generated stub expands these variables at runtime.
  # shellcheck disable=SC2016
  printf '%s\n' '#!/bin/sh' \
    'printf "%s\n" "$(basename "$0") $*" >>"$REVIEW_LATENCY_CALL_LEDGER"' \
    'exit 97' >"$stub_dir/$stub_command"
  chmod +x "$stub_dir/$stub_command"
done
REVIEW_LATENCY_CALL_LEDGER="$call_ledger" PATH="$stub_dir:$PATH" \
  bash "$BENCHMARK" score --corpus "$FIXTURE" >/dev/null
assert_eq "scoring makes no network or model call" "" "$(cat "$call_ledger")"

mutate_case known-fix-only '.treatment.plan.identity.review_key="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"' "$mutated"
assert_eq "arbitrary review key fails Q1 first" identity "$(first_failed "$mutated")"
mutate_case known-fix-only '.treatment.plan.identity.head_sha="ffffffffffffffffffffffffffffffffffffffff"' "$mutated"
assert_eq "stale head fails Q1 first" identity "$(first_failed "$mutated")"
mutate_case known-fix-only '.treatment.capability_coverage |= map(select(.capability != "test-coverage"))' "$mutated"
assert_eq "missing required capability fails Q2 first" required_coverage "$(first_failed "$mutated")"
mutate_case unavailable-required-lane '.treatment.plan.event_ceiling="APPROVE" | .treatment.event_evidence.effective.event="APPROVE"' "$mutated"
assert_eq "gap plus effective APPROVE fails Q2 first" required_coverage "$(first_failed "$mutated")"
mutate_case known-fix-only '.treatment.finding_ids=[]' "$mutated"
assert_eq "lost must-fix fails Q3 first" must_fix_recall "$(first_failed "$mutated")"
extra_finding="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
mutate_case known-fix-only '.treatment.adjudicated_false_positive=1' "$mutated"
assert_eq "new false positive fails Q4 first" precision "$(first_failed "$mutated")"
mutate_case known-fix-only ".control.finding_ids += [\"$extra_finding\"] |
  .control.finding_ids |= sort |
  .control.adjudicated_posted=2 |
  .control.adjudicated_false_positive=1 |
  .treatment.validated_findings[0].adjudication=\"false_positive\" |
  .treatment.adjudicated_false_positive=1" "$TEST_ROOT/paired-inflation-stage.jsonl"
finding_without_hash="$(jq -S -c 'select(.pair_id == "known-fix-only") |
  .treatment.validated_findings[0] | del(.content_sha256)' \
  "$TEST_ROOT/paired-inflation-stage.jsonl")"
finding_hash="$(printf '%s' "$finding_without_hash" | sha256_text)"
jq -c --arg pair_id known-fix-only --arg finding_hash "$finding_hash" '
  if .pair_id == $pair_id then
    .treatment.validated_findings[0].content_sha256=$finding_hash
  else . end' "$TEST_ROOT/paired-inflation-stage.jsonl" >"$mutated"
assert_eq "paired control and treatment inflation fails Q4 first" precision "$(first_failed "$mutated")"
mutate_case known-fix-only '.treatment.behavior_hashes.options_sha256="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"' "$mutated"
assert_eq "less conservative options fail Q5 first" behavior_parity "$(first_failed "$mutated")"
mutate_case new-material-dispute '.treatment.event_evidence.effective.event="APPROVE"' "$mutated"
assert_eq "less conservative event fails Q5 first" behavior_parity "$(first_failed "$mutated")"
mutate_case known-fix-only '.treatment.timing.durations_ms.review_to_confirmation_ready=240001' "$mutated"
assert_eq "240001 milliseconds fails Q6 first" latency "$(first_failed "$mutated")"
mutate_case known-fix-only '.treatment.timing.durations_ms.review_to_confirmation_ready=1' "$mutated"
assert_eq "falsely tiny caller total fails Q6 first" latency "$(first_failed "$mutated")"
mutate_case known-fix-only '(.treatment.timing.durations_ms |=
  (.identity_and_plan=0 | .inventory=0 | .required_lanes_critical_path=0 |
   .targeted_verification_critical_path=0 | .collation_and_draft=0 |
   .review_to_confirmation_ready=0))' "$mutated"
assert_eq "coherent zero timing self-reseal fails Q6 first" latency "$(first_failed "$mutated")"
mutate_case known-fix-only '(.treatment.timing.durations_ms |=
  (.identity_and_plan=1 | .inventory=1 | .required_lanes_critical_path=1 |
   .targeted_verification_critical_path=1 | .collation_and_draft=1))' "$mutated"
assert_eq "inconsistent producer arithmetic fails Q6 first" latency "$(first_failed "$mutated")"

mutate_case known-fix-only ".treatment.finding_ids += [\"$extra_finding\"] | .treatment.finding_ids |= sort" "$mutated"
assert_eq "unaccounted treatment finding fails Q4 first" precision "$(first_failed "$mutated")"
mutate_case known-fix-only '.treatment.adjudicated_posted=0' "$mutated"
assert_eq "posted count mismatch fails Q4 first" precision "$(first_failed "$mutated")"
mutate_case known-fix-only '.treatment.validated_findings[0].candidate.evidence.quote_verified=false' "$mutated"
assert_eq "unquoted actionable finding fails Q4 first" precision "$(first_failed "$mutated")"
mutate_case known-fix-only '.treatment.validated_findings[0].candidate.evidence.quoted_line_sha256="invalid"' "$mutated"
assert_eq "invalid actionable evidence fails Q4 first" precision "$(first_failed "$mutated")"

mutate_case known-fix-only '.treatment.plan.inherited_finding_ids=[]' "$mutated"
assert_eq "empty inherited must-fix set fails Q1 first" identity "$(first_failed "$mutated")"
mutate_case known-fix-only '.treatment.plan.review_range.from_exclusive=.exact_head.head_sha' "$mutated"
assert_eq "range beginning at current head fails Q1 first" identity "$(first_failed "$mutated")"
mutate_case known-fix-only '.treatment.predecessor_evidence.receipt.known_findings[0].path="src/attacker.txt" |
  .treatment.predecessor_evidence.receipt.known_findings[0].evidence_sha256=
    "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"' "$TEST_ROOT/predecessor-reseal-stage.jsonl"
receipt_without_hash="$(jq -S -c 'select(.pair_id == "known-fix-only") |
  .treatment.predecessor_evidence.receipt | del(.content_sha256)' \
  "$TEST_ROOT/predecessor-reseal-stage.jsonl")"
receipt_hash="$(printf '%s' "$receipt_without_hash" | sha256_text)"
jq -c --arg pair_id known-fix-only --arg receipt_hash "$receipt_hash" '
  if .pair_id == $pair_id then
    .treatment.predecessor_evidence.receipt.content_sha256=$receipt_hash
  else . end' "$TEST_ROOT/predecessor-reseal-stage.jsonl" >"$mutated"
assert_eq "same-context predecessor receipt self-reseal fails Q1 first" identity \
  "$(first_failed "$mutated")"

sed -n '1p' "$FIXTURE" >"$TEST_ROOT/subset.jsonl"
assert_eq "favorable subset has structural do-not-promote verdict" do_not_promote \
  "$(score_file "$TEST_ROOT/subset.jsonl" | jq -r '.verdict')"
assert_eq "favorable subset fails corpus identity first" identity \
  "$(first_failed "$TEST_ROOT/subset.jsonl")"
jq -c 'select(.pair_id != "security-finding")' "$FIXTURE" >"$TEST_ROOT/omitted-class.jsonl"
assert_eq "omitted required class fails structural identity" identity "$(first_failed "$TEST_ROOT/omitted-class.jsonl")"

mutate_case unavailable-required-lane '.treatment.plan.event_ceiling="COMMENT" | .treatment.event_evidence.effective.event="COMMENT" | .treatment.event_evidence.effective.coverage_gap_refs=.treatment.capability_gap_refs' "$mutated"
assert_eq "gaps capped to COMMENT pass Q2" true "$(gate_value "$mutated" required_coverage)"
mutate_case unavailable-required-lane '.treatment.plan.event_ceiling="COMMENT" | .treatment.event_evidence.effective.event="REQUEST_CHANGES" | .treatment.event_evidence.effective.coverage_gap_refs=.treatment.capability_gap_refs' "$mutated"
assert_eq "gaps capped to REQUEST_CHANGES pass Q2" true "$(gate_value "$mutated" required_coverage)"
mutate_case unavailable-required-lane '.treatment.plan.event_ceiling="APPROVE"' "$mutated"
assert_eq "gap with APPROVE ceiling fails Q2" false "$(gate_value "$mutated" required_coverage)"
mutate_case unavailable-required-lane '.treatment.event_evidence.effective.event="APPROVE"' "$mutated"
assert_eq "gap with effective APPROVE fails Q2" false "$(gate_value "$mutated" required_coverage)"
mutate_case unavailable-required-lane '.treatment.event_evidence.effective.coverage_gap_refs=[]' "$mutated"
assert_eq "gap missing evidence reference fails Q2" false "$(gate_value "$mutated" required_coverage)"
mutate_case unavailable-required-lane 'del(.treatment.event_evidence.effective.source_sha256)' "$mutated"
assert_eq "gap missing source hash fails Q2" false "$(gate_value "$mutated" required_coverage)"
mutate_case unavailable-required-lane '.treatment.event_evidence.effective.source_sha256="invalid"' "$mutated"
assert_eq "gap invalid source hash fails Q2" false "$(gate_value "$mutated" required_coverage)"
mutate_case unavailable-required-lane '.treatment.event_evidence.posted={schema:"kc-pr-flow.posted-review-evidence/v1",review_key:.exact_head.review_key,event:"APPROVE",source_sha256:.treatment.behavior_hashes.event_sha256}' "$mutated"
assert_eq "gap with posted APPROVE fails Q2" false "$(gate_value "$mutated" required_coverage)"

# The whole corpus proves initial cases participate in Q1-Q5 while staying out of Q6.
assert_eq "initial fallback passes Q1" true "$(jq -r '.gates.identity' <<<"$report")"
assert_eq "initial fallback passes Q5" true "$(jq -r '.gates.behavior_parity' <<<"$report")"
mutate_case force-push '.treatment.timing=null' "$mutated"
assert_eq "initial timing null remains structurally non-promotable" do_not_promote \
  "$(score_file "$mutated" | jq -r '.verdict')"
timing_template="$(jq -c 'select(.pair_id == "known-fix-only") | .treatment.timing' "$FIXTURE")"
jq -c --arg pair_id force-push --argjson timing "$timing_template" \
  'if .pair_id == $pair_id then .treatment.timing=$timing else . end' "$FIXTURE" >"$mutated"
expect_rejected "initial fallback carrying timing is rejected" "$mutated"

mutate_case known-fix-only '.treatment.capability_coverage += [.treatment.capability_coverage[0]]' "$mutated"
expect_rejected "duplicate capability entries are rejected" "$mutated"
mutate_case known-fix-only '.treatment.capability_gap_refs=["orphan-gap"]' "$mutated"
expect_rejected "orphan gap references are rejected" "$mutated"
mutate_case unavailable-required-lane '.treatment.capability_gap_refs += [.treatment.capability_gap_refs[0]]' "$mutated"
expect_rejected "duplicate gap references are rejected" "$mutated"
mutate_case known-fix-only '.treatment.capability_coverage[0].gap_ref="not-null"' "$mutated"
expect_rejected "complete entry with a gap is rejected" "$mutated"
mutate_case unavailable-required-lane '.treatment.capability_coverage[] |= if .status == "gap" then .gap_ref=null else . end' "$mutated"
expect_rejected "gap entry without a reference is rejected" "$mutated"
mutate_case known-fix-only '.caller_verdict="promote"' "$mutated"
expect_rejected "caller verdict is rejected as an extra key" "$mutated"
mutate_case known-fix-only '._derived={identity_valid:true,behavior_parity:true}' "$mutated"
expect_rejected "caller derived booleans are rejected" "$mutated"
mutate_case known-fix-only '.treatment.timing.durations_ms.caller_total=1' "$mutated"
expect_rejected "caller total is rejected" "$mutated"
mutate_case known-fix-only 'del(.evidence_tier)' "$mutated"
expect_rejected "missing evidence tier is rejected" "$mutated"
mutate_case known-fix-only '.evidence_tier="actual"' "$mutated"
expect_rejected "changed evidence tier is rejected" "$mutated"
mutate_case known-fix-only '.treatment.timing.evidence_tier="actual"' "$mutated"
expect_rejected "timing evidence tier claim is rejected" "$mutated"
mutate_case known-fix-only 'del(.treatment.timing.fixture_kind)' "$mutated"
expect_rejected "missing structural timing fixture kind is rejected" "$mutated"
mutate_case known-fix-only '.treatment.timing.fixture_kind="actual"' "$mutated"
expect_rejected "non-structural timing fixture kind is rejected" "$mutated"
mutate_case known-fix-only '.treatment.timing.schema="kc-pr-flow.review-timing/v1"' "$mutated"
expect_rejected "runtime timing schema claim is rejected" "$mutated"
mutate_case known-fix-only '.treatment.timing.measured_by="review-runtime"' "$mutated"
expect_rejected "runtime timing producer claim is rejected" "$mutated"
jq -c 'if .pair_id == "fix-plus-test" then .pair_id="known-fix-only" else . end' \
  "$FIXTURE" >"$mutated"
expect_rejected "duplicate pair identifiers are rejected" "$mutated"

before="$(sha256_file "$FIXTURE")"
score_file "$FIXTURE" >/dev/null
assert_eq "corpus bytes are unchanged after scoring" "$before" "$(sha256_file "$FIXTURE")"
jq -c -s 'reverse[]' "$FIXTURE" >"$TEST_ROOT/reversed.jsonl"
assert_eq "reversed corpus yields identical report bytes" "$report" "$(score_file "$TEST_ROOT/reversed.jsonl")"

ln -s "$FIXTURE" "$TEST_ROOT/corpus-link.jsonl"
expect_rejected "symlink corpus is rejected" "$TEST_ROOT/corpus-link.jsonl"
mkfifo "$TEST_ROOT/corpus.fifo"
expect_rejected "FIFO corpus is rejected without blocking" "$TEST_ROOT/corpus.fifo"
dd if=/dev/zero of="$TEST_ROOT/oversized.jsonl" bs=1048576 count=17 >/dev/null 2>&1
expect_rejected "oversized corpus is rejected" "$TEST_ROOT/oversized.jsonl"
first_line="$(sed -n '1p' "$FIXTURE")"
printf '%s\n' "${first_line/\"pair_id\":/\"pair_id\":\"duplicate\",\"pair_id\":}" >"$TEST_ROOT/duplicate.jsonl"
expect_rejected "duplicate JSON members are rejected" "$TEST_ROOT/duplicate.jsonl"
printf '%s\n' "${first_line/\"pr_number\":1693/\"pr_number\":9007199254740992}" >"$TEST_ROOT/unsafe-number.jsonl"
expect_rejected "unsafe numbers are rejected" "$TEST_ROOT/unsafe-number.jsonl"
printf '%s\n' "${first_line/\"pr_number\":1693/\"pr_number\":1693.0}" >"$TEST_ROOT/unsafe-float.jsonl"
expect_rejected "floating-point numbers are rejected" "$TEST_ROOT/unsafe-float.jsonl"
mutate_case known-fix-only '.treatment.event_evidence.effective.source_sha256="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff" | .treatment.behavior_hashes.event_sha256="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"' "$mutated"
assert_eq "self-resealed treatment behavior fails structural parity" behavior_parity "$(first_failed "$mutated")"
mutate_case known-fix-only '.control.behavior_hashes.event_sha256="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff" |
  .treatment.behavior_hashes.event_sha256="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff" |
  .treatment.event_evidence.effective.source_sha256="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"' "$mutated"
assert_eq "both-arm self-reseal fails structural parity" behavior_parity "$(first_failed "$mutated")"
mutate_case known-fix-only '.treatment.behavior_sources.posted.payload.finding_ids=[] |
  .treatment.behavior_sources.posted.payload_sha256="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff" |
  .treatment.behavior_sources.posted.idempotency_key="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff" |
  .treatment.event_evidence.posted.source_sha256="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"' "$mutated"
assert_eq "arbitrary posted source fails structural parity" behavior_parity "$(first_failed "$mutated")"

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
