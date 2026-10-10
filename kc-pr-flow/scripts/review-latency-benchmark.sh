#!/usr/bin/env bash
# Synthetic structural diagnostics. This scorer never emits promotion authority.

review_latency_here() {
  cd "$(dirname "${BASH_SOURCE[0]}")" && pwd
}

review_latency_usage() {
  printf 'usage: review-latency-benchmark.sh score --corpus FILE [--scenarios FILE]\n' >&2
}

review_latency_snapshot() {
  local source_file="$1" destination="$2" helper
  helper="$(review_latency_here)/review-runtime-safe-io.py" || return 69
  python3 "$helper" snapshot --source "$source_file" --destination "$destination" \
    --limit-bytes 1048576 >/dev/null 2>&1
}

review_latency_unique_lines() {
  local source_file="$1" output="$2" helper
  helper="$(review_latency_here)/review-runtime-safe-io.py" || return 69
  python3 "$helper" unique-json-lines <"$source_file" >"$output"
  [ -s "$source_file" ] && ! grep -q -v '^0$' "$output"
}

review_latency_sha256_file() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    return 69
  fi
}

review_latency_score() (
  local corpus="$1" scenarios="$2" temporary corpus_snapshot scenarios_snapshot status
  command -v jq >/dev/null 2>&1 || return 69
  command -v python3 >/dev/null 2>&1 || return 69
  temporary="$(mktemp -d "${TMPDIR:-/tmp}/kc-pr-flow-structural.XXXXXX")" || return 74
  chmod 700 "$temporary" || return 74
  trap 'rm -f "$temporary"/* 2>/dev/null || true; rmdir "$temporary" 2>/dev/null || true' EXIT
  corpus_snapshot="$temporary/corpus.jsonl"
  scenarios_snapshot="$temporary/scenarios.jsonl"
  review_latency_snapshot "$corpus" "$corpus_snapshot" || return 3
  review_latency_snapshot "$scenarios" "$scenarios_snapshot" || return 3
  [ "$(review_latency_sha256_file "$scenarios_snapshot")" = \
    '3292c091b41ad4b1eb4de52713a6bc12da5b71d75d8e987bd5a091a9db18f301' ] || return 3
  status="$temporary/status"
  review_latency_unique_lines "$corpus_snapshot" "$status" || return 3
  review_latency_unique_lines "$scenarios_snapshot" "$status" || return 3

  jq -S -c -e -s --slurpfile scenarios "$scenarios_snapshot" '
    def exact_keys($required): type == "object" and (keys | sort) == ($required | sort);
    def token: type == "string" and test("^[a-z][a-z0-9._-]{0,63}$");
    def tokens: type == "array" and all(.[]; token) and . == (sort | unique);
    def count: type == "number" and floor == . and . >= 0 and . <= 9007199254740991;
    def event: . == null or . == "APPROVE" or . == "COMMENT" or . == "REQUEST_CHANGES";
    def mode: . == "initial" or . == "delta" or . == "resolve";
    def timing:
      . == null or (exact_keys(["fixture_kind","review_to_confirmation_ready_ms"]) and
        .fixture_kind == "synthetic-structural" and (.review_to_confirmation_ready_ms | count));
    def scenario:
      exact_keys(["contract_truth","pair_id","schema"]) and
      .schema == "kc-pr-flow.review-latency-scenario/v1" and (.pair_id | token) and
      (.contract_truth | exact_keys(["latency_eligible","maximum_event","mode",
        "must_fix_count","required_capabilities"])) and
      (.contract_truth.latency_eligible | type == "boolean") and
      (.contract_truth.maximum_event | event) and (.contract_truth.mode | mode) and
      (.contract_truth.must_fix_count | count) and (.contract_truth.required_capabilities | tokens);
    def pair:
      exact_keys(["evidence_tier","observed","pair_id","provenance","schema"]) and
      .schema == "kc-pr-flow.review-latency-pair/v1" and
      .evidence_tier == "synthetic-structural" and (.pair_id | token) and
      (.provenance | exact_keys(["fixture_kind","scenario_sha256"])) and
      .provenance.fixture_kind == "synthetic-structural" and
      .provenance.scenario_sha256 ==
        "3292c091b41ad4b1eb4de52713a6bc12da5b71d75d8e987bd5a091a9db18f301" and
      (.observed | exact_keys(["behavior_parity","completed_capabilities",
        "control_false_positives","found_must_fix_count","identity_valid","maximum_event",
        "mode","timing","treatment_false_positives"])) and
      (.observed.behavior_parity | type == "boolean") and
      (.observed.identity_valid | type == "boolean") and
      (.observed.completed_capabilities | tokens) and
      (.observed.control_false_positives | count) and
      (.observed.found_must_fix_count | count) and
      (.observed.maximum_event | event) and (.observed.mode | mode) and
      (.observed.timing | timing) and (.observed.treatment_false_positives | count);
    ["corrupt-receipt","cross-layer-no-dispute","fix-plus-test","force-push",
      "known-fix-only","new-material-dispute","security-finding",
      "unavailable-required-lane","unrelated-new-path"] as $required_classes |
    ($scenarios | sort_by(.pair_id)) as $truth |
    sort_by(.pair_id) as $pairs |
    if (($truth | length) == 9 and all($truth[]; scenario) and
      ([$truth[].pair_id] == $required_classes) and
      ([$pairs[].pair_id] == ([$pairs[].pair_id] | unique)) and
      all($pairs[]; pair) and
      all($pairs[]; .pair_id as $id | any($truth[]; .pair_id == $id))) | not
    then empty
    else
      INDEX($truth[]; .pair_id) as $scenario_by_id |
      ([$pairs[] | select($scenario_by_id[.pair_id].contract_truth.latency_eligible)]) as $eligible |
      (($pairs | length) == 9 and ([$pairs[].pair_id] == $required_classes) and
        all($pairs[]; .observed.identity_valid)) as $q1 |
      (all($pairs[]; . as $pair | $scenario_by_id[$pair.pair_id].contract_truth as $expected |
        (($expected.required_capabilities - $pair.observed.completed_capabilities) | length) == 0)) as $q2 |
      (all($pairs[]; . as $pair | $scenario_by_id[$pair.pair_id].contract_truth.must_fix_count <=
        $pair.observed.found_must_fix_count)) as $q3 |
      (all($pairs[]; .observed.treatment_false_positives <= .observed.control_false_positives)) as $q4 |
      (all($pairs[]; . as $pair | $scenario_by_id[$pair.pair_id].contract_truth as $expected |
        $pair.observed.behavior_parity and $pair.observed.mode == $expected.mode and
        $pair.observed.maximum_event == $expected.maximum_event)) as $q5 |
      (($eligible | length) == 7 and all($eligible[];
        .observed.timing != null and
        .observed.timing.review_to_confirmation_ready_ms <= 240000) and
        all($pairs[]; . as $pair | $scenario_by_id[$pair.pair_id].contract_truth.latency_eligible or
          $pair.observed.timing == null)) as $q6 |
      {identity:$q1,required_coverage:$q2,must_fix_recall:$q3,precision:$q4,
        behavior_parity:$q5,latency:$q6} as $gates |
      ["identity","required_coverage","must_fix_recall","precision","behavior_parity","latency"] as $order |
      {
        evidence_tier:"synthetic-structural",
        first_failed_gate:(first($order[] | select($gates[.] == false)) // null),
        gate_order:$order,
        gates:$gates,
        latency:{
          eligible_runs:($eligible | length),
          excluded_initial_runs:(($pairs | length) - ($eligible | length)),
          max_ms:([$eligible[].observed.timing.review_to_confirmation_ready_ms] | max // null),
          passing_runs:([$eligible[] | select(
            .observed.timing.review_to_confirmation_ready_ms <= 240000)] | length),
          target_ms:240000
        },
        pair_count:($pairs | length),
        phase:"review-plan",
        quality_gates:{identity:$q1,required_coverage:$q2,must_fix_recall:$q3,
          precision:$q4,behavior_parity:$q5},
        schema:"kc-pr-flow.review-latency-promotion/v1",
        verdict:"do_not_promote"
      }
    end
  ' "$corpus_snapshot" || return 3
)

review_latency_main() {
  local command="${1-}" corpus='' scenarios
  scenarios="$(review_latency_here)/../test/fixtures/review-plan/phase1-promotion-scenarios.jsonl" || return 69
  [ "$#" -gt 0 ] && shift
  [ "$command" = score ] || { review_latency_usage; return 2; }
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --corpus) [ "$#" -ge 2 ] || return 2; corpus="$2"; shift 2 ;;
      --scenarios) [ "$#" -ge 2 ] || return 2; scenarios="$2"; shift 2 ;;
      *) review_latency_usage; return 2 ;;
    esac
  done
  [ -n "$corpus" ] || { review_latency_usage; return 2; }
  review_latency_score "$corpus" "$scenarios"
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  review_latency_main "$@"
fi
