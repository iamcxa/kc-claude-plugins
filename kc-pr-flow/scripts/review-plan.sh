#!/usr/bin/env bash
# review-plan.sh — read-only exact-head planning for kc-pr-review.

review_plan_source_runtime() {
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || return 69
  # shellcheck source=/dev/null
  . "$here/review-runtime.sh" || return 69
}

review_plan_content_sha256() {
  jq -S -c 'del(.content_sha256)' | review_runtime_sha256
}

review_plan_build_receipt() (
  local event_file="$1" projection projection_hash receipt_id canonical content_sha256
  [ "$#" -eq 1 ] || return 2
  projection="$(review_runtime_replay "$event_file")" || return 3
  jq -e '.lifecycle.complete == true' >/dev/null <<<"$projection" || return 3
  projection_hash="$(printf '%s' "$projection" | jq -S -c . | review_runtime_sha256)" || return
  receipt_id="$(printf '%s' "$(jq -r '.run.run_id + "|" + .run.review_key' <<<"$projection")|$projection_hash" |
    review_runtime_sha256)" || return
  canonical="$(jq -S -c --arg receipt_id "$receipt_id" '
    .run as $run |
    {
      schema:"kc-pr-flow.review-delta-receipt/v1",
      predecessor:{
        repository:$run.repository,pr_number:$run.pr_number,
        base_sha:$run.base_sha,head_sha:$run.head_sha,
        config_hash:$run.config_hash,review_key:$run.review_key,
        run_id:$run.run_id,
        receipt_id:$receipt_id
      },
      known_findings:(.findings | map({
        finding_id,claim_key,
        evidence_sha256:.evidence.content_sha256,
        path,side,resolution_state:"unresolved"
      }) | sort_by(.finding_id)),
      required_capabilities:(.lanes | map(.capability) | sort | unique),
      coverage_gap_refs:[]
    }' <<<"$projection")" || return 3
  content_sha256="$(printf '%s' "$canonical" | review_runtime_sha256)" || return
  jq -S -c --arg hash "$content_sha256" '. + {content_sha256:$hash}' <<<"$canonical"
)

review_plan_validate_receipt() (
  local receipt='' event_file='' projection receipt_hash projection_hash expected_review_key expected_receipt_id expected_content_sha256
  local receipt_source projection_source
  [ "$#" -eq 2 ] || return 2
  receipt="$1"
  event_file="$2"
  receipt_source="$receipt"

  # Reject duplicate members before jq parses either value. A path argument is
  # accepted only when it is an ordinary file; callers normally pass JSON text.
  if [ -f "$receipt" ] && [ ! -L "$receipt" ]; then
    receipt_source="$(cat "$receipt")" || return 3
  fi
  review_runtime_json_has_unique_members "$receipt_source" >/dev/null 2>&1 || return 3
  # Freshness is part of this public boundary: callers provide only the event
  # file, and the projection is always rebuilt through review-runtime replay.
  projection="$(review_runtime_replay "$event_file")" || return 3
  projection_source="$projection"
  receipt_hash="$(printf '%s' "$receipt_source" | jq -S -c . 2>/dev/null)" || return 3
  projection_hash="$(printf '%s' "$projection_source" | jq -S -c . 2>/dev/null | review_runtime_sha256)" || return 3
  expected_review_key="$(printf '%s|%s|%s|%s|%s' \
    "$(jq -r '.run.repository' <<<"$projection_source")" \
    "$(jq -r '.run.pr_number' <<<"$projection_source")" \
    "$(jq -r '.run.base_sha' <<<"$projection_source")" \
    "$(jq -r '.run.head_sha' <<<"$projection_source")" \
    "$(jq -r '.run.config_hash' <<<"$projection_source")" | review_runtime_sha256)" || return
  expected_receipt_id="$(printf '%s' "$(jq -r '.run.run_id' <<<"$projection_source")|$expected_review_key|$projection_hash" |
    review_runtime_sha256)" || return
  # jq emits a line terminator; hash the canonical JSON value itself, matching
  # the producer's command-substitution boundary rather than that terminator.
  expected_content_sha256="$(printf '%s' "$receipt_hash" | jq -S -c 'del(.content_sha256)' 2>/dev/null)" || return 3
  expected_content_sha256="$(printf '%s' "$expected_content_sha256" | review_runtime_sha256)" || return

  jq -e -n \
    --argjson receipt "$receipt_source" \
    --argjson projection "$projection_source" \
    --arg expected_review_key "$expected_review_key" \
    --arg expected_receipt_id "$expected_receipt_id" \
    --arg expected_content_sha256 "$expected_content_sha256" \
    '
      def exact_keys($required):
        (type == "object" and (keys | sort) == ($required | sort));
      def sha256: type == "string" and test("^[0-9a-f]{64}$");
      def sha1: type == "string" and test("^[0-9a-f]{40}$");
      def token: type == "string" and test("^[a-z][a-z0-9._-]{0,63}$");
      def run_token: type == "string" and test("^run-[A-Za-z0-9._-]+$");
      def positive_integer:
        type == "number" and floor == . and . > 0 and . <= 9007199254740991;
      def safe_path:
        type == "string" and length > 0 and length <= 1024 and
        (startswith("/") | not) and (endswith("/") | not) and
        (contains("//") | not) and
        (test("(^|/)\\.\\.?(/|$)|[[:cntrl:]\\\\]") | not);
      def repository: type == "string" and test("^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$");
      def identity:
        exact_keys(["base_sha","config_hash","head_sha","pr_number","receipt_id","repository","review_key","run_id"]) and
        (.repository | repository) and (.pr_number | positive_integer) and
        (.base_sha | sha1) and (.head_sha | sha1) and (.config_hash | sha256) and
        (.review_key | sha256) and (.run_id | run_token) and (.receipt_id | sha256);
      def projection_run:
        exact_keys(["base_sha","config_hash","head_sha","pr_number","repository","review_key","run_id","schema"]) and
        .schema == "kc-pr-flow.review-event/v1" and
        (.repository | repository) and (.pr_number | positive_integer) and
        (.base_sha | sha1) and (.head_sha | sha1) and (.config_hash | sha256) and
        (.review_key | sha256) and (.run_id | run_token);
      def projection_finding:
        type == "object" and
        ([.finding_id,.review_key,.anchor_sha256,.evidence.content_sha256] | all(sha256)) and
        (.claim_key | token) and (.path | safe_path) and
        (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
        (.evidence | type == "object");
      def projection_lane:
        type == "object" and
        exact_keys(["capability","lane_id","result","task"]) and
        (.capability | token) and (.lane_id | token);
      def projection:
        exact_keys(["behavior_hashes","candidates","findings","lanes","lifecycle","run","schema","uncertain_candidate_ids","usage_observations"]) and
        .schema == "kc-pr-flow.review-projection/v1" and
        (.run | projection_run) and
        (.lanes | type == "array" and length > 0 and all(projection_lane) and
          ([.[].capability] | . == (sort | unique))) and
        (.findings | type == "array" and all(projection_finding) and
          ([.[].finding_id] | . == (sort | unique))) and
        (.uncertain_candidate_ids | type == "array" and all(sha256) and
          (unique | length) == length) and
        (.lifecycle | type == "object" and .complete == true) and
        (.behavior_hashes | type == "object") and
        (.candidates | type == "array") and
        (.usage_observations | type == "array");
      def receipt_finding:
        type == "object" and
        exact_keys(["claim_key","evidence_sha256","finding_id","path","resolution_state","side"]) and
        (.finding_id | sha256) and (.claim_key | token) and
        (.evidence_sha256 | sha256) and (.path | safe_path) and
        (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
        .resolution_state == "unresolved";
      ($projection | projection) and
      ($receipt | exact_keys(["content_sha256","coverage_gap_refs","known_findings","predecessor","required_capabilities","schema"])) and
      $receipt.schema == "kc-pr-flow.review-delta-receipt/v1" and
      ($receipt.content_sha256 == $expected_content_sha256) and
      ($receipt.predecessor | identity) and
      ($receipt.known_findings | type == "array" and all(receipt_finding) and
        ([.[].finding_id] | . == (sort | unique))) and
      ($receipt.required_capabilities | type == "array" and all(token) and
        . == (sort | unique)) and
      ($receipt.coverage_gap_refs | type == "array" and all(token) and
        . == (sort | unique)) and
      ($receipt.predecessor.review_key == $expected_review_key) and
      ($receipt.predecessor.receipt_id == $expected_receipt_id) and
      ([$receipt.predecessor.repository,$receipt.predecessor.pr_number,
        $receipt.predecessor.base_sha,$receipt.predecessor.head_sha,
        $receipt.predecessor.config_hash,$receipt.predecessor.review_key,
        $receipt.predecessor.run_id] ==
       [$projection.run.repository,$projection.run.pr_number,$projection.run.base_sha,
        $projection.run.head_sha,$projection.run.config_hash,$projection.run.review_key,
        $projection.run.run_id]) and
      ($receipt.coverage_gap_refs == []) and
      ($receipt.known_findings == ($projection.findings | map({
        finding_id,claim_key,evidence_sha256:.evidence.content_sha256,
        path,side,resolution_state:"unresolved"
      }) | sort_by(.finding_id))) and
      ($receipt.required_capabilities == ($projection.lanes | map(.capability) | sort | unique))
    ' >/dev/null 2>&1
)

review_plan_usage() {
  printf 'usage: %s receipt --event-file FILE\n' "${0##*/}" >&2
  printf '       %s decide ...\n' "${0##*/}" >&2
}

review_plan_main_receipt() {
  local event_file=''
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --event-file)
        [ "$#" -ge 2 ] || { printf 'review-plan: missing value for --event-file\n' >&2; return 2; }
        event_file="$2"
        shift 2
        ;;
      *)
        printf 'review-plan: unknown receipt option: %s\n' "$1" >&2
        return 2
        ;;
    esac
  done
  [ -n "$event_file" ] || { printf 'review-plan: --event-file is required\n' >&2; return 2; }
  review_plan_build_receipt "$event_file"
}

review_plan_main_decide() {
  review_plan_usage
  return 2
}

review_plan_main() {
  local command="${1:-}"
  [ "$#" -gt 0 ] && shift
  case "$command" in
    receipt) review_plan_main_receipt "$@" ;;
    decide) review_plan_main_decide "$@" ;;
    *) review_plan_usage; return 2 ;;
  esac
}

review_plan_source_runtime || return 69 2>/dev/null || exit 69
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  review_plan_main "$@"
fi
