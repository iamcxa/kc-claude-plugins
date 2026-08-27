#!/usr/bin/env bash
# review-latency-benchmark.sh — ordered Phase 1 latency promotion scoring.
#
# Source-safe: this file declares functions only unless executed directly.

review_latency_require_tools() {
  command -v jq >/dev/null 2>&1 || {
    printf 'review-latency-benchmark: jq is required\n' >&2
    return 69
  }
  command -v python3 >/dev/null 2>&1 || {
    printf 'review-latency-benchmark: python3 is required\n' >&2
    return 69
  }
}

review_latency_source_runtime() {
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || return 69
  # shellcheck source=/dev/null
  . "$here/review-runtime.sh" || return 69
}

review_latency_safe_io_helper() {
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || return 69
  printf '%s\n' "$here/review-runtime-safe-io.py"
}

review_latency_snapshot_corpus() {
  local source_file="$1" snapshot_file="$2" helper rc
  helper="$(review_latency_safe_io_helper)" || return 69
  if [ ! -f "$helper" ] || [ -L "$helper" ] || [ ! -r "$helper" ]; then
    printf 'review-latency-benchmark: safe I/O helper is unavailable\n' >&2
    return 69
  fi
  python3 "$helper" snapshot --source "$source_file" --destination "$snapshot_file" \
    --limit-bytes 16777216 >/dev/null 2>&1
  rc=$?
  case "$rc" in
    0) return 0 ;;
    2)
      printf 'review-latency-benchmark: corpus is not a safe regular file\n' >&2
      return 2
      ;;
    69) return 69 ;;
    73)
      printf 'review-latency-benchmark: corpus exceeds the 16777216-byte limit\n' >&2
      return 73
      ;;
    *) return 74 ;;
  esac
}

review_latency_validate_pair() {
  local pair="$1" expected_review_key identity_valid behavior_parity
  local repository pr_number base_sha head_sha config_hash
  review_latency_source_runtime || return
  review_runtime_json_has_unique_members "$pair" >/dev/null 2>&1 || return 3
  repository="$(jq -r '.exact_head.repository // empty' <<<"$pair")" || return 3
  pr_number="$(jq -r '.exact_head.pr_number // empty' <<<"$pair")" || return 3
  base_sha="$(jq -r '.exact_head.base_sha // empty' <<<"$pair")" || return 3
  head_sha="$(jq -r '.exact_head.head_sha // empty' <<<"$pair")" || return 3
  config_hash="$(jq -r '.exact_head.config_hash // empty' <<<"$pair")" || return 3
  expected_review_key="$(printf '%s|%s|%s|%s|%s' \
    "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" |
    review_runtime_sha256)" || return

  jq -e -n --argjson pair "$pair" '
    def exact_keys($required): type == "object" and (keys | sort) == ($required | sort);
    def no_extra_keys($allowed): type == "object" and ((keys - $allowed) | length) == 0;
    def sha1: type == "string" and test("^[0-9a-f]{40}$");
    def sha256: type == "string" and test("^[0-9a-f]{64}$");
    def token: type == "string" and test("^[a-z][a-z0-9._-]{0,63}$");
    def repository: type == "string" and test("^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$");
    def safe_int: type == "number" and floor == . and . >= 0 and . <= 9007199254740991;
    def positive_int: safe_int and . > 0;
    def hashes: type == "array" and all(.[]; sha256) and . == (sort | unique);
    def tokens: type == "array" and all(.[]; token) and . == (sort | unique);
    def event: . == "APPROVE" or . == "COMMENT" or . == "REQUEST_CHANGES";
    def identity:
      exact_keys(["base_sha","config_hash","head_sha","pr_number","repository","review_key"]) and
      (.repository | repository) and (.pr_number | positive_int) and
      (.base_sha | sha1) and (.head_sha | sha1) and
      (.config_hash | sha256) and (.review_key | sha256);
    def fallback:
      exact_keys(["final_verdict_authority","requires_existing_initial_review","router_advisory"]) and
      .router_advisory == true and (.requires_existing_initial_review | type == "boolean") and
      .final_verdict_authority == "existing-review-runtime";
    def plan:
      exact_keys(["event_ceiling","fallback","identity","inherited_finding_ids","mode",
        "reason_codes","required_capabilities","review_range","schema"]) and
      .schema == "kc-pr-flow.review-plan-decision/v1" and (.identity | identity) and
      (.mode == "initial" or .mode == "delta" or .mode == "resolve") and
      (.reason_codes | type == "array" and length > 0 and tokens) and
      (.review_range | exact_keys(["from_exclusive","to_inclusive"])) and
      (.review_range.from_exclusive == null or (.review_range.from_exclusive | sha1)) and
      (.review_range.to_inclusive | sha1) and
      (.inherited_finding_ids | hashes) and (.required_capabilities | tokens) and
      (.event_ceiling == null or .event_ceiling == "APPROVE" or .event_ceiling == "COMMENT") and
      (.fallback | fallback) and
      (if .mode == "initial" then
        .review_range.from_exclusive == null and .inherited_finding_ids == [] and
        .required_capabilities == [] and .event_ceiling == null and
        .fallback.requires_existing_initial_review == true and
        (.reason_codes == ["base_changed"] or .reason_codes == ["config_changed"] or
         .reason_codes == ["feature_disabled"] or .reason_codes == ["identity_mismatch"] or
         .reason_codes == ["invalid_predecessor"] or .reason_codes == ["missing_predecessor"] or
         .reason_codes == ["non_ancestor"] or .reason_codes == ["unknown_delta"])
      else
        (.review_range.from_exclusive | sha1) and
        .fallback.requires_existing_initial_review == false and
        (if .mode == "resolve" then
          .reason_codes == ["ancestor_append","known_finding_delta","trusted_predecessor"]
         else .reason_codes == ["ancestor_append","expanded_delta","trusted_predecessor"] end)
      end);
    def behavior_hashes:
      exact_keys(["event_sha256","options_sha256"]) and
      (.event_sha256 | sha256) and (.options_sha256 | sha256);
    def coverage_entry:
      exact_keys(["capability","gap_ref","status"]) and (.capability | token) and
      (if .status == "complete" then .gap_ref == null
       elif .status == "gap" then (.gap_ref | token)
       else false end);
    def effective_evidence:
      no_extra_keys(["coverage_gap_refs","event","review_key","schema","source_sha256"]) and
      (has("schema") and has("review_key") and has("event") and has("coverage_gap_refs")) and
      .schema == "kc-pr-flow.review-event-evidence/v1" and (.review_key | sha256) and
      (.event | event) and (.coverage_gap_refs | type == "array" and all(.[]; token) and . == (sort | unique)) and
      ((has("source_sha256") | not) or (.source_sha256 | type == "string"));
    def posted_evidence:
      . == null or
      (exact_keys(["event","review_key","schema","source_sha256"]) and
       .schema == "kc-pr-flow.posted-review-evidence/v1" and
       (.review_key | sha256) and (.event | event) and (.source_sha256 | sha256));
    def timing:
      exact_keys(["durations_ms","lane_durations_ms","measured_by","mode","review_key","schema"]) and
      .schema == "kc-pr-flow.review-timing/v1" and (.review_key | sha256) and
      (.mode == "delta" or .mode == "resolve") and .measured_by == "review-runtime" and
      (.durations_ms | exact_keys(["collation_and_draft","confirmation_wait","external_ci_wait",
        "identity_and_plan","inventory","post_mutation","required_lanes_critical_path",
        "review_to_confirmation_ready","targeted_verification_critical_path"])) and
      ([.durations_ms.identity_and_plan,.durations_ms.inventory,
        .durations_ms.required_lanes_critical_path,
        .durations_ms.targeted_verification_critical_path,
        .durations_ms.collation_and_draft,
        .durations_ms.review_to_confirmation_ready] | all(.[]; safe_int)) and
      .durations_ms.confirmation_wait == null and .durations_ms.external_ci_wait == null and
      .durations_ms.post_mutation == null and
      (.lane_durations_ms | type == "array" and all(.[];
        exact_keys(["duration_ms","lane_id","provider_family"]) and
        (.lane_id | token) and (.duration_ms | safe_int) and
        (.provider_family == null or (.provider_family | token))) and
        ([.[].lane_id] | unique | length) == length);
    ($pair | exact_keys(["control","exact_head","expected","pair_id","schema","treatment"])) and
    $pair.schema == "kc-pr-flow.review-latency-pair/v1" and ($pair.pair_id | token) and
    ($pair.exact_head | identity) and
    ($pair.expected | exact_keys(["maximum_event","mode","must_fix_finding_ids","required_capabilities"])) and
    ($pair.expected.mode == "initial" or $pair.expected.mode == "delta" or $pair.expected.mode == "resolve") and
    ($pair.expected.must_fix_finding_ids | hashes) and
    ($pair.expected.required_capabilities | tokens) and ($pair.expected.maximum_event | event) and
    ($pair.control | exact_keys(["adjudicated_false_positive","adjudicated_posted","behavior_hashes","finding_ids"])) and
    ($pair.control.finding_ids | hashes) and
    ($pair.control.adjudicated_posted | safe_int) and ($pair.control.adjudicated_false_positive | safe_int) and
    $pair.control.adjudicated_false_positive <= $pair.control.adjudicated_posted and
    ($pair.control.behavior_hashes | behavior_hashes) and
    (($pair.expected.must_fix_finding_ids - $pair.control.finding_ids) | length) == 0 and
    ($pair.treatment | exact_keys(["adjudicated_false_positive","adjudicated_posted","behavior_hashes",
      "capability_coverage","capability_gap_refs","event_evidence","finding_ids","plan","timing"])) and
    ($pair.treatment.plan | plan) and ($pair.treatment.finding_ids | hashes) and
    ($pair.treatment.adjudicated_posted | safe_int) and
    ($pair.treatment.adjudicated_false_positive | safe_int) and
    $pair.treatment.adjudicated_false_positive <= $pair.treatment.adjudicated_posted and
    ($pair.treatment.behavior_hashes | behavior_hashes) and
    ($pair.treatment.capability_coverage | type == "array" and all(.[]; coverage_entry) and
      ([.[].capability] | unique | length) == length) and
    ($pair.treatment.capability_gap_refs | type == "array" and all(.[]; token) and . == (sort | unique)) and
    ([$pair.treatment.capability_coverage[] | select(.status == "gap") | .gap_ref] | sort) ==
      $pair.treatment.capability_gap_refs and
    ($pair.treatment.event_evidence | exact_keys(["effective","posted"])) and
    ($pair.treatment.event_evidence.effective | effective_evidence) and
    ($pair.treatment.event_evidence.posted | posted_evidence) and
    (if $pair.treatment.plan.mode == "initial" then $pair.treatment.timing == null
     else ($pair.treatment.timing | timing) end)
  ' >/dev/null 2>&1 || return 3

  identity_valid="$(jq -r --arg expected_review_key "$expected_review_key" '
    (.exact_head.review_key == $expected_review_key) and
    (.expected.mode == .treatment.plan.mode) and
    (.expected.required_capabilities == .treatment.plan.required_capabilities) and
    (.treatment.plan.identity == .exact_head) and
    (.treatment.plan.review_range.to_inclusive == .exact_head.head_sha) and
    (.treatment.event_evidence.effective.review_key == .exact_head.review_key) and
    (.treatment.event_evidence.posted == null or
      .treatment.event_evidence.posted.review_key == .exact_head.review_key) and
    (if .treatment.timing == null then .treatment.plan.mode == "initial"
     else .treatment.timing.review_key == .exact_head.review_key and
       .treatment.timing.mode == .treatment.plan.mode end)
  ' <<<"$pair")" || return 3

  behavior_parity="$(jq -r '
    def rank: if . == "REQUEST_CHANGES" then 0 elif . == "COMMENT" then 1
      elif . == "APPROVE" then 2 else -1 end;
    (.control.behavior_hashes == .treatment.behavior_hashes) and
    (.treatment.event_evidence.effective.source_sha256? == .treatment.behavior_hashes.event_sha256) and
    ((.treatment.event_evidence.effective.event | rank) <= (.expected.maximum_event | rank)) and
    (.treatment.event_evidence.posted == null or
      ((.treatment.event_evidence.posted.event | rank) <= (.expected.maximum_event | rank))) and
    (.treatment.plan.mode == "initial" or
      ((.treatment.plan.event_ceiling | rank) <= (.expected.maximum_event | rank) and
       (.treatment.event_evidence.effective.event | rank) <= (.treatment.plan.event_ceiling | rank) and
       (.treatment.event_evidence.posted == null or
         ((.treatment.event_evidence.posted.event | rank) <= (.treatment.plan.event_ceiling | rank)))))
  ' <<<"$pair")" || return 3

  jq -S -c --argjson identity_valid "$identity_valid" --argjson behavior_parity "$behavior_parity" \
    '. + {_derived:{identity_valid:$identity_valid,behavior_parity:$behavior_parity}}' <<<"$pair"
}

phase1_promotion() {
  jq -S -c -s '
    def event_at_or_below_comment: . == "COMMENT" or . == "REQUEST_CHANGES";
    def hash64: type == "string" and test("^[0-9a-f]{64}$");
    def event_evidence_valid($gaps):
      .treatment.event_evidence as $e |
      ($e.effective.source_sha256? | hash64) and
      ($e.effective.source_sha256 == .treatment.behavior_hashes.event_sha256) and
      ($e.effective.coverage_gap_refs == $gaps) and
      ($e.effective.event | event_at_or_below_comment) and
      ($e.posted == null or
        (($e.posted.source_sha256 | hash64) and ($e.posted.event | event_at_or_below_comment)));
    def required_coverage_safe:
      .expected.required_capabilities as $required |
      .treatment.capability_gap_refs as $gaps |
      [.treatment.capability_coverage[] | select(.status == "complete") | .capability] as $completed |
      [.treatment.capability_coverage[] | select(.status == "gap") | .capability] as $documented_gaps |
      ($required - $completed) as $missing |
      if ($missing | length) == 0 and ($gaps | length) == 0 then true
      else (($missing - $documented_gaps) | length) == 0 and
        (($gaps | length) > 0) and .treatment.plan.event_ceiling == "COMMENT" and
        event_evidence_valid($gaps)
      end;
    def latency_eligible: .treatment.plan.mode == "delta" or .treatment.plan.mode == "resolve";
    sort_by(.pair_id) as $pairs |
    [$pairs[] | select(latency_eligible)] as $eligible |
    ($pairs | all(._derived.identity_valid)) as $q1 |
    ($pairs | all(required_coverage_safe)) as $q2 |
    ($pairs | all(((.expected.must_fix_finding_ids - .treatment.finding_ids) | length) == 0)) as $q3 |
    ($pairs | all(.treatment.adjudicated_false_positive <= .control.adjudicated_false_positive)) as $q4 |
    ($pairs | all(._derived.behavior_parity)) as $q5 |
    (($eligible | length) > 0 and
      ($eligible | all(.treatment.timing.durations_ms.review_to_confirmation_ready <= 240000))) as $q6 |
    {identity:$q1,required_coverage:$q2,must_fix_recall:$q3,precision:$q4,
      behavior_parity:$q5,latency:$q6} as $gates |
    ["identity","required_coverage","must_fix_recall","precision","behavior_parity","latency"] as $order |
    {
      schema:"kc-pr-flow.review-latency-promotion/v1",phase:"review-plan",gate_order:$order,
      gates:$gates,
      quality_gates:{identity:$q1,required_coverage:$q2,must_fix_recall:$q3,
        precision:$q4,behavior_parity:$q5},
      latency:{target_ms:240000,eligible_runs:($eligible|length),
        excluded_initial_runs:([$pairs[] | select(.treatment.plan.mode == "initial")]|length),
        passing_runs:([$eligible[] | select(.treatment.timing.durations_ms.review_to_confirmation_ready <= 240000)]|length),
        max_ms:([$eligible[].treatment.timing.durations_ms.review_to_confirmation_ready]|max // null)},
      first_failed_gate:(first($order[] | select($gates[.] == false)) // null),
      verdict:(if $q1 and $q2 and $q3 and $q4 and $q5 and $q6
        then "promote" else "do_not_promote" end)
    }
  '
}

review_latency_score() (
  local corpus="$1" snapshot_dir='' snapshot_file='' validated_file='' unique_file='' line validated
  review_latency_require_tools || return
  snapshot_dir="$(mktemp -d "${TMPDIR:-/tmp}/kc-pr-flow-latency.XXXXXX")" || return 74
  chmod 700 "$snapshot_dir" || return 74
  snapshot_file="$snapshot_dir/corpus.jsonl"
  validated_file="$snapshot_dir/validated.jsonl"
  unique_file="$snapshot_dir/unique-status"
  trap 'rm -f "$snapshot_file" "$validated_file" "$unique_file" 2>/dev/null || true; rmdir "$snapshot_dir" 2>/dev/null || true' EXIT
  review_latency_snapshot_corpus "$corpus" "$snapshot_file" || return
  : >"$validated_file"
  chmod 600 "$validated_file" || return 74
  python3 "$(review_latency_safe_io_helper)" unique-json-lines <"$snapshot_file" >"$unique_file" || return 3
  [ -s "$snapshot_file" ] || return 3
  if grep -q -v '^0$' "$unique_file"; then
    printf 'review-latency-benchmark: corpus contains invalid JSON\n' >&2
    return 3
  fi
  while IFS= read -r line || [ -n "$line" ]; do
    [ -n "$line" ] || return 3
    validated="$(review_latency_validate_pair "$line")" || {
      printf 'review-latency-benchmark: invalid promotion pair\n' >&2
      return 3
    }
    printf '%s\n' "$validated" >>"$validated_file" || return 74
  done <"$snapshot_file"
  [ "$(wc -l <"$unique_file" | tr -d '[:space:]')" = \
    "$(wc -l <"$validated_file" | tr -d '[:space:]')" ] || return 3
  [ "$(jq -r '.pair_id' "$validated_file" | sort | uniq -d | wc -l | tr -d '[:space:]')" = '0' ] || return 3
  phase1_promotion <"$validated_file"
)

review_latency_usage() {
  printf 'usage: review-latency-benchmark.sh score --corpus FILE\n' >&2
}

review_latency_main() {
  local command="${1:-}" corpus=''
  [ "$#" -gt 0 ] && shift
  [ "$command" = 'score' ] || { review_latency_usage; return 2; }
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --corpus)
        [ "$#" -ge 2 ] || { review_latency_usage; return 2; }
        corpus="$2"
        shift 2
        ;;
      *) review_latency_usage; return 2 ;;
    esac
  done
  [ -n "$corpus" ] || { review_latency_usage; return 2; }
  review_latency_score "$corpus"
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  review_latency_main "$@"
fi
