#!/usr/bin/env bash
# review-runtime-benchmark.sh — deterministic scoring for sanitized paired receipts.
#
# Source-safe: this file declares functions only unless executed directly.

review_benchmark_require_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    printf 'review-runtime-benchmark: jq is required\n' >&2
    return 69
  fi
}

review_benchmark_safe_io_helper() {
  local benchmark_source="${BASH_SOURCE[0]}"
  local benchmark_dir
  benchmark_dir="$(cd "$(dirname "$benchmark_source")" && pwd)" || return 69
  printf '%s\n' "$benchmark_dir/review-runtime-safe-io.py"
}

review_benchmark_snapshot_corpus() {
  local source_file="$1" snapshot_file="$2" helper rc
  if ! command -v python3 >/dev/null 2>&1; then
    printf 'review-runtime-benchmark: python3 is required for safe corpus ingestion\n' >&2
    return 69
  fi
  helper="$(review_benchmark_safe_io_helper)" || return 69
  if [ ! -f "$helper" ] || [ -L "$helper" ] || [ ! -r "$helper" ]; then
    printf 'review-runtime-benchmark: safe I/O helper is unavailable\n' >&2
    return 69
  fi
  python3 "$helper" snapshot \
    --source "$source_file" \
    --destination "$snapshot_file" \
    --limit-bytes 16777216 >/dev/null 2>&1
  rc=$?
  case "$rc" in
    0) return 0 ;;
    2)
      printf 'review-runtime-benchmark: corpus is not a safe regular file: %s\n' "$source_file" >&2
      return 2
      ;;
    69)
      printf 'review-runtime-benchmark: safe corpus ingestion is unsupported\n' >&2
      return 69
      ;;
    73)
      printf 'review-runtime-benchmark: corpus exceeds the 16777216-byte limit\n' >&2
      return 73
      ;;
    *)
      printf 'review-runtime-benchmark: unable to create private corpus snapshot\n' >&2
      return 74
      ;;
  esac
}

review_benchmark_sha256() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum | awk '{print $1}'
  else
    printf 'review-runtime-benchmark: sha256 tool unavailable\n' >&2
    return 69
  fi
}

# Compatibility boundary shared with review-runtime.sh.
review_benchmark_review_key() {
  printf '%s|%s|%s|%s|%s' "$1" "$2" "$3" "$4" "$5" | review_benchmark_sha256
}

review_benchmark_fingerprint_id() {
  local canonical
  canonical="$(jq -S -c 'del(.fingerprint_id)')" || return
  printf '%s' "$canonical" | review_benchmark_sha256
}

review_benchmark_candidate_id() {
  printf '%s|%s' "$1" "$2" | review_benchmark_sha256
}

review_benchmark_receipt_id() {
  printf '%s|%s|%s' "$1" "$2" "$3" | review_benchmark_sha256
}

review_benchmark_arm_content_sha256() {
  local canonical
  canonical="$(jq -S -c '{
    behavior,
    lanes:(.lanes | sort_by(.capability,.lane_id)),
    candidates:(.observed_candidates | sort_by(.candidate_id)),
    findings:(.observed_findings | sort_by(.finding_id,.candidate_id)),
    uncertain_candidate_refs:(.uncertain_candidate_ids | sort),
    usage
  }')" || return
  printf '%s' "$canonical" | review_benchmark_sha256
}

review_benchmark_validate_corpus() {
  local corpus_file="$1"

  jq -e -s '
    def exact_keys($required; $optional):
      . as $object |
      type == "object" and
      ((keys - $required - $optional) | length == 0) and
      all($required[]; . as $key | $object | has($key));
    def safe_token:
      type == "string" and test("^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$");
    def provider_token:
      type == "string" and test("^[a-z][a-z0-9._-]{0,63}$");
    def sha40: type == "string" and test("^[0-9a-f]{40}$");
    def sha256: type == "string" and test("^[0-9a-f]{64}$");
    # Keep byte-for-byte semantics aligned with review-runtime.sh safe_path.
    def safe_path:
      type == "string" and length > 0 and length <= 1024 and
      (startswith("/") | not) and (endswith("/") | not) and (contains("//") | not) and
      (test("(^|/)\\.\\.?(/|$)|[[:cntrl:]\\\\]") | not);
    def unique_sha_array:
      type == "array" and all(.[]; sha256) and (unique | length) == length;
    def usage:
      exact_keys(["input_tokens","output_tokens","provenance","provider_family","scope","total_tokens"]; []) and
      (.provenance == "reported" or .provenance == "estimated" or .provenance == "unavailable") and
      (.provider_family == null or (.provider_family | provider_token)) and
      (.scope == "lane" or .scope == "run") and
      all([.input_tokens,.output_tokens,.total_tokens][];
        . == null or (type == "number" and floor == . and . >= 0 and . <= 9007199254740991)) and
      (if .provenance == "unavailable" then all([.input_tokens,.output_tokens,.total_tokens][]; . == null) else true end);
    def lane:
      exact_keys(["capability","lane_id","terminal_status"]; []) and
      (.capability | safe_token) and (.lane_id | safe_token) and
      (.terminal_status == "completed" or .terminal_status == "incomplete" or .terminal_status == "unavailable");
    def behavior:
      exact_keys(["body_sha256","event_sha256","payload_sha256"]; []) and
      (.body_sha256 | sha256) and (.event_sha256 | sha256) and (.payload_sha256 | sha256);
    def receipt:
      exact_keys(["content_sha256","receipt_id","review_key","run_id","schema"]; []) and
      .schema == "kc-pr-flow.review-receipt-identity/v1" and
      (.run_id | type == "string" and test("^run-[A-Za-z0-9._-]+$")) and
      (.review_key | sha256) and (.receipt_id | sha256) and (.content_sha256 | sha256);
    def fingerprint:
      exact_keys(["anchor_sha256","category","claim_key","evidence_sha256","fingerprint_id","path","schema","side"]; []) and
      .schema == "kc-pr-flow.review-candidate-fingerprint/v1" and
      (.fingerprint_id | sha256) and (.anchor_sha256 | sha256) and (.evidence_sha256 | sha256) and
      (.category | safe_token) and (.claim_key | safe_token) and
      (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
      (.path | safe_path);
    def candidate:
      exact_keys(["candidate_id","fingerprint","run_id"]; []) and
      (.candidate_id | sha256) and
      (.run_id | type == "string" and test("^run-[A-Za-z0-9._-]+$")) and
      (.fingerprint | fingerprint);
    def observed_finding:
      exact_keys(["candidate_id","evidence_sha256","finding_id"]; []) and
      (.candidate_id | sha256) and (.evidence_sha256 | sha256) and (.finding_id | sha256);
    def expected_finding:
      exact_keys(["candidate_fingerprint_id","evidence_sha256","finding_id"]; []) and
      (.candidate_fingerprint_id | sha256) and (.evidence_sha256 | sha256) and (.finding_id | sha256);
    def arm:
      . as $arm |
      exact_keys(["behavior","lanes","observed_candidates","observed_findings","receipt","uncertain_candidate_ids","usage"]; []) and
      (.behavior | behavior) and (.receipt | receipt) and
      (.lanes | type == "array" and all(.[]; lane) and ((map(.lane_id) | unique | length) == length)) and
      (.observed_candidates | type == "array" and all(.[]; candidate) and
        ((map(.candidate_id) | unique | length) == length) and
        ((map(.fingerprint.fingerprint_id) | unique | length) == length)) and
      all(.observed_candidates[]; .run_id == $arm.receipt.run_id) and
      (.observed_findings | type == "array" and all(.[]; observed_finding) and
        ((map(.finding_id) | unique | length) == length)) and
      all(.observed_findings[]; . as $finding |
        ($arm.observed_candidates | map(select(
          .candidate_id == $finding.candidate_id and
          .fingerprint.evidence_sha256 == $finding.evidence_sha256
        )) | length) == 1) and
      (.uncertain_candidate_ids | unique_sha_array) and
      all(.uncertain_candidate_ids[]; . as $id | ($arm.observed_candidates | map(.candidate_id)) | index($id) != null) and
      (.usage | usage);
    def exact_head:
      exact_keys(["base_sha","config_hash","head_sha","pr_number","repository","review_key"]; []) and
      (.repository | type == "string" and length > 0 and (test("[\u0000-\u001f\u007f]") | not)) and
      (.pr_number | type == "number" and floor == . and . > 0) and
      (.base_sha | sha40) and (.head_sha | sha40) and (.config_hash | sha256) and (.review_key | sha256);
    def pair:
      . as $pair |
      exact_keys(["baseline","disagreement_candidate_fingerprint_ids","exact_head","expected_capability_ids","expected_findings","pair_id","schema","shadow","stability_group"]; []) and
      .schema == "kc-pr-flow.review-benchmark-pair/v1" and
      (.pair_id | safe_token) and (.stability_group | safe_token) and
      (.exact_head | exact_head) and
      (.expected_findings | type == "array" and all(.[]; expected_finding) and
        ((map(.finding_id) | unique | length) == length)) and
      (.expected_capability_ids | type == "array" and length > 0 and all(.[]; safe_token) and
        . == (sort | unique)) and
      (.baseline | arm) and (.shadow | arm) and
      (.baseline.lanes | map(.capability) | sort) == .expected_capability_ids and
      (.shadow.lanes | map(.capability) | sort) == .expected_capability_ids and
      .baseline.receipt.review_key == .exact_head.review_key and
      .shadow.receipt.review_key == .exact_head.review_key and
      .baseline.receipt.run_id != .shadow.receipt.run_id and
      .baseline.receipt.receipt_id != .shadow.receipt.receipt_id and
      all(.expected_findings[]; . as $finding |
        (($pair.baseline.observed_candidates + $pair.shadow.observed_candidates) |
          map(select(
            .fingerprint.fingerprint_id == $finding.candidate_fingerprint_id and
            .fingerprint.evidence_sha256 == $finding.evidence_sha256
          )) | length) > 0) and
      all([$pair.baseline,$pair.shadow][]; . as $arm |
        all($arm.observed_findings[]; . as $observed |
          ($pair.expected_findings | map(select(.finding_id == $observed.finding_id))) as $expected |
          if ($expected | length) == 0 then true
          else
            ($arm.observed_candidates | map(select(.candidate_id == $observed.candidate_id)) | first) as $candidate |
            $observed.evidence_sha256 == $expected[0].evidence_sha256 and
            $candidate.fingerprint.evidence_sha256 == $expected[0].evidence_sha256 and
            $candidate.fingerprint.fingerprint_id == $expected[0].candidate_fingerprint_id
          end)) and
      (($pair.baseline.observed_candidates + $pair.shadow.observed_candidates |
        group_by(.fingerprint.fingerprint_id)) |
        all(.[]; (map(.fingerprint) | unique | length) == 1)) and
      (.disagreement_candidate_fingerprint_ids | unique_sha_array) and
      all(.disagreement_candidate_fingerprint_ids[]; . as $id |
        (($pair.baseline.observed_candidates + $pair.shadow.observed_candidates |
          map(.fingerprint.fingerprint_id)) | index($id) != null));
    length > 0 and all(.[]; pair) and ((map(.pair_id) | unique | length) == length) and
    ([.[] | (.baseline.observed_candidates + .shadow.observed_candidates)[]] |
      group_by(.candidate_id) | all(.[]; (map(.run_id) | unique | length) == 1)) and
    ([.[] as $pair | [$pair.baseline.receipt,$pair.shadow.receipt][] |
      . + {exact_head_review_key:$pair.exact_head.review_key}] |
      group_by(.run_id) | all(.[]; (map(.exact_head_review_key) | unique | length) == 1)) and
    ([.[] | .baseline.receipt,.shadow.receipt] |
      group_by(.receipt_id) | all(.[]; (map([.run_id,.review_key,.content_sha256]) | unique | length) == 1))
  ' "$corpus_file" >/dev/null 2>&1
}

review_benchmark_validate_authority() {
  local corpus_file="$1"
  local repository pr_number base_sha head_sha config_hash actual expected
  local candidate candidate_id fingerprint fingerprint_id run_id review_key content_sha256 receipt_id arm
  local records

  records="$(jq -r '[.exact_head.repository,.exact_head.pr_number,.exact_head.base_sha,.exact_head.head_sha,.exact_head.config_hash,.exact_head.review_key] | @tsv' "$corpus_file")" || return
  while IFS=$'\t' read -r repository pr_number base_sha head_sha config_hash actual; do
    expected="$(review_benchmark_review_key "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash")" || return
    [ "$actual" = "$expected" ] || return 1
  done <<<"$records"

  records="$(jq -c '(.baseline.observed_candidates + .shadow.observed_candidates)[]' "$corpus_file")" || return
  while IFS= read -r candidate; do
    [ -n "$candidate" ] || continue
    fingerprint="$(printf '%s' "$candidate" | jq -c '.fingerprint')" || return
    actual="$(printf '%s' "$fingerprint" | jq -r '.fingerprint_id')" || return
    expected="$(printf '%s' "$fingerprint" | review_benchmark_fingerprint_id)" || return
    [ "$actual" = "$expected" ] || return 1
    fingerprint_id="$actual"
    run_id="$(printf '%s' "$candidate" | jq -r '.run_id')" || return
    candidate_id="$(printf '%s' "$candidate" | jq -r '.candidate_id')" || return
    expected="$(review_benchmark_candidate_id "$run_id" "$fingerprint_id")" || return
    [ "$candidate_id" = "$expected" ] || return 1
  done <<<"$records"

  records="$(jq -c '.baseline,.shadow' "$corpus_file")" || return
  while IFS= read -r arm; do
    [ -n "$arm" ] || continue
    run_id="$(printf '%s' "$arm" | jq -r '.receipt.run_id')" || return
    review_key="$(printf '%s' "$arm" | jq -r '.receipt.review_key')" || return
    content_sha256="$(printf '%s' "$arm" | jq -r '.receipt.content_sha256')" || return
    expected="$(printf '%s' "$arm" | review_benchmark_arm_content_sha256)" || return
    [ "$content_sha256" = "$expected" ] || return 1
    receipt_id="$(printf '%s' "$arm" | jq -r '.receipt.receipt_id')" || return
    expected="$(review_benchmark_receipt_id "$run_id" "$review_key" "$content_sha256")" || return
    [ "$receipt_id" = "$expected" ] || return 1
  done <<<"$records"
}

review_benchmark_score() (
  local corpus_file="$1"
  local snapshot_dir='' snapshot_file='' snapshot_rc

  review_benchmark_require_jq || return
  if [ ! -d "${TMPDIR:-/tmp}" ] || [ -L "${TMPDIR:-/tmp}" ]; then
    printf 'review-runtime-benchmark: temporary directory is unavailable\n' >&2
    return 74
  fi
  snapshot_dir="$(mktemp -d "${TMPDIR:-/tmp}/kc-pr-flow-review-benchmark.XXXXXX")" || return 74
  if ! chmod 0700 "$snapshot_dir" || [ ! -d "$snapshot_dir" ] || [ -L "$snapshot_dir" ]; then
    [ -d "$snapshot_dir" ] && [ ! -L "$snapshot_dir" ] && rmdir "$snapshot_dir" 2>/dev/null || true
    printf 'review-runtime-benchmark: unable to create private corpus snapshot\n' >&2
    return 74
  fi
  snapshot_file="$snapshot_dir/corpus.jsonl"
  trap 'if [ -d "$snapshot_dir" ] && [ ! -L "$snapshot_dir" ]; then rm -f "$snapshot_file" 2>/dev/null || true; rmdir "$snapshot_dir" 2>/dev/null || true; fi' EXIT
  review_benchmark_snapshot_corpus "$corpus_file" "$snapshot_file"
  snapshot_rc=$?
  [ "$snapshot_rc" -eq 0 ] || return "$snapshot_rc"
  if ! review_benchmark_validate_corpus "$snapshot_file"; then
    printf 'review-runtime-benchmark: invalid sanitized corpus\n' >&2
    return 2
  fi
  if ! review_benchmark_validate_authority "$snapshot_file"; then
    printf 'review-runtime-benchmark: invalid canonical identity\n' >&2
    return 2
  fi

  jq -S -c -s '
    def intersection($left; $right):
      [$left[] as $item | select($right | index($item) != null) | $item] | unique | sort;
    def difference($left; $right):
      [$left[] as $item | select($right | index($item) == null) | $item] | unique | sort;
    def recall($expected; $observed):
      intersection($expected; $observed) as $matched |
      {expected_count:($expected | length),matched_count:($matched | length),matched_finding_ids:$matched,
       rate:(if ($expected | length) == 0 then null else (($matched | length) / ($expected | length)) end)};
    def lane_coverage($arm; $expected):
      ([$arm.lanes[] | select(.terminal_status == "completed") | .capability] | unique | sort) as $completed |
      {
        expected_capability_ids:$expected,
        expected_count:($expected | length),
        completed_count:($completed | length),
        completion_rate:(($completed | length) / ($expected | length)),
        completed_capabilities:$completed,
        incomplete_capabilities:([$arm.lanes[] | select(.terminal_status == "incomplete") | .capability] | unique | sort),
        unavailable_capabilities:([$arm.lanes[] | select(.terminal_status == "unavailable") | .capability] | unique | sort),
        lanes:($arm.lanes | sort_by(.capability,.lane_id))
      };
    def behavior_parity($baseline; $shadow):
      ["body_sha256","event_sha256","payload_sha256"] as $marker_names |
      ([$marker_names[] as $name | select($baseline[$name] != $shadow[$name]) | $name] | sort) as $mismatches |
      {
        matches:($mismatches | length == 0),
        verdict:(if ($mismatches | length) == 0 then "pass" else "fail" end),
        mismatched_markers:$mismatches,
        markers:{baseline:$baseline,shadow:$shadow}
      };
    def stability($pair):
      ($pair.baseline.observed_findings | map(.finding_id) | sort) as $baseline_finding_ids |
      ($pair.shadow.observed_findings | map(.finding_id) | sort) as $shadow_finding_ids |
      ($pair.baseline.observed_candidates | map(.candidate_id) | sort) as $baseline_candidate_ids |
      ($pair.shadow.observed_candidates | map(.candidate_id) | sort) as $shadow_candidate_ids |
      ($pair.baseline.observed_candidates | map(.fingerprint.fingerprint_id) | sort) as $baseline_fingerprints |
      ($pair.shadow.observed_candidates | map(.fingerprint.fingerprint_id) | sort) as $shadow_fingerprints |
      {
        stability_group:$pair.stability_group,
        common_finding_ids:intersection($baseline_finding_ids; $shadow_finding_ids),
        baseline_only_finding_ids:difference($baseline_finding_ids; $shadow_finding_ids),
        shadow_only_finding_ids:difference($shadow_finding_ids; $baseline_finding_ids),
        baseline_candidate_ids:$baseline_candidate_ids,
        shadow_candidate_ids:$shadow_candidate_ids,
        common_candidate_fingerprint_ids:intersection($baseline_fingerprints; $shadow_fingerprints),
        baseline_only_candidate_fingerprint_ids:difference($baseline_fingerprints; $shadow_fingerprints),
        shadow_only_candidate_fingerprint_ids:difference($shadow_fingerprints; $baseline_fingerprints),
        disagreement_candidate_fingerprint_ids:($pair.disagreement_candidate_fingerprint_ids | sort),
        baseline_uncertain_candidate_ids:($pair.baseline.uncertain_candidate_ids | sort),
        shadow_uncertain_candidate_ids:($pair.shadow.uncertain_candidate_ids | sort)
      };
    def usage_complete($usage):
      all([$usage.input_tokens,$usage.output_tokens,$usage.total_tokens][];
        type == "number" and floor == . and . >= 0 and . <= 9007199254740991);
    def usage_comparison($baseline; $shadow):
      ($baseline.provenance == "reported" and $shadow.provenance == "reported" and
       $baseline.provider_family != null and $baseline.provider_family == $shadow.provider_family and
       $baseline.scope == $shadow.scope and usage_complete($baseline) and usage_complete($shadow)) as $comparable |
      {
        baseline:$baseline,
        shadow:$shadow,
        comparable:$comparable,
        provider_family:(if $comparable then $baseline.provider_family else null end),
        scope:(if $comparable then $baseline.scope else null end),
        efficiency_verdict:(if $comparable then "measured" else "unavailable" end),
        deltas:(if $comparable then {
          input_tokens:($shadow.input_tokens - $baseline.input_tokens),
          output_tokens:($shadow.output_tokens - $baseline.output_tokens),
          total_tokens:($shadow.total_tokens - $baseline.total_tokens)
        } else null end)
      };
    {
      schema:"kc-pr-flow.review-benchmark-report/v1",
      measure_order:["evidence_recall","lane_capability_coverage","external_behavior_parity","finding_candidate_stability","usage_comparability"],
      pairs:(sort_by(.pair_id) | map(. as $pair | {
        pair_id:$pair.pair_id,
        exact_head:$pair.exact_head,
        receipts:{baseline:$pair.baseline.receipt,shadow:$pair.shadow.receipt},
        evidence_recall:{
          expected_finding_ids:($pair.expected_findings | map(.finding_id) | sort),
          baseline:recall(($pair.expected_findings | map(.finding_id)); ($pair.baseline.observed_findings | map(.finding_id))),
          shadow:recall(($pair.expected_findings | map(.finding_id)); ($pair.shadow.observed_findings | map(.finding_id)))
        },
        lane_capability_coverage:{
          baseline:lane_coverage($pair.baseline; $pair.expected_capability_ids),
          shadow:lane_coverage($pair.shadow; $pair.expected_capability_ids)
        },
        external_behavior_parity:behavior_parity($pair.baseline.behavior; $pair.shadow.behavior),
        finding_candidate_stability:stability($pair),
        usage_comparability:usage_comparison($pair.baseline.usage; $pair.shadow.usage)
      }))
    }
  ' "$snapshot_file" || {
    printf 'review-runtime-benchmark: malformed corpus\n' >&2
    return 2
  }
)

review_benchmark_usage() {
  printf '%s\n' 'usage: review-runtime-benchmark.sh score --corpus FILE' >&2
}

review_benchmark_main() {
  local command="${1:-}"
  local corpus_file=''
  [ "$#" -gt 0 ] && shift

  if [ "$command" != 'score' ]; then
    review_benchmark_usage
    return 2
  fi
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --corpus)
        [ "$#" -ge 2 ] || { review_benchmark_usage; return 2; }
        corpus_file="$2"
        shift 2
        ;;
      *)
        printf 'review-runtime-benchmark: unknown option: %s\n' "$1" >&2
        return 2
        ;;
    esac
  done
  [ -n "$corpus_file" ] || { review_benchmark_usage; return 2; }
  review_benchmark_score "$corpus_file"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  review_benchmark_main "$@"
fi
