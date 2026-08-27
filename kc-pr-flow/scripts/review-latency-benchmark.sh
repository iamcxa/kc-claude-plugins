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

review_latency_hash_json() {
  local value="$1" filter="$2" canonical
  canonical="$(jq -S -c "$filter" <<<"$value")" || return
  printf '%s' "$canonical" | review_runtime_sha256
}

review_latency_expected_provenance() {
  # Filled from immutable sanitized sources. This pins evidence-bearing fields,
  # not whole rows, so ordered gate mutations still reach their owning gate.
  case "$1" in
    known-fix-only) printf '%s\n' '{"control_effective_sha256":"8137bbfb7ebff44922756b5b8423647c064e5739872159186c5e02cbbba476b9","expected_sha256":"801bc7562f6b772cb0ab9bb4d912bf8c379d96f695dfaeb3cce63e8fc4b1cb35","posted_source_sha256":"dcb99a3d749716770fd4207bbc577f1d050f14368dd78ae8c9739b8564b5c4db","predecessor_projection_sha256":"85dad443cb2093841c3f4616cc08efd6b8f742520941ff3b3c980fc9465398f7","review_key":"16a4a31ab16aae7b2b5f7b830ab3aeb602860df5fba4e465019f9d8b40156631","treatment_effective_sha256":"8137bbfb7ebff44922756b5b8423647c064e5739872159186c5e02cbbba476b9"}' ;;
    fix-plus-test) printf '%s\n' '{"control_effective_sha256":"7e0bc2524c296e85969765c06a725a82c33b30e4874a738026f1d76e7e9b09e3","expected_sha256":"9cb6fb9fe0068d9e0b326016159545db089849d07da238653dfc5fd30a04a0a3","posted_source_sha256":"39893d457c47cced18ecf22ac6fad39ec50f7366d4e35e0c3de32ee9d6d0782e","predecessor_projection_sha256":"bc1ab61daa93ee311344c6ece9eb4345c2b939455fe38467d09b8980251c7bbb","review_key":"eccb52f192042d4931778c1ee97a0964ae9a54ad36050b2ab7594eb79dd7c57a","treatment_effective_sha256":"7e0bc2524c296e85969765c06a725a82c33b30e4874a738026f1d76e7e9b09e3"}' ;;
    unrelated-new-path) printf '%s\n' '{"control_effective_sha256":"f7f0df5d8e4cb8264cade66fbb31ae8158006fbce238469450635bdb7cdefe62","expected_sha256":"280e8ef17934a4dd2025b13ac5772a0a284005005532d085e15a5fbca1585f73","posted_source_sha256":"586b4dea1ac1b60db04512c64f7d211a44695070721efc7a17c139dab31de69d","predecessor_projection_sha256":"500cd18d7bdc89a659a9cd4f24d54137e483b19924ecb5492dd00148ec5ac950","review_key":"85efefd21cbba5fa7932b5726da66d0306e0cb66a41f24e3cac915e981081d76","treatment_effective_sha256":"f7f0df5d8e4cb8264cade66fbb31ae8158006fbce238469450635bdb7cdefe62"}' ;;
    force-push) printf '%s\n' '{"control_effective_sha256":"d02dd6eb5207d201ef8862d0f508c1cb185610c8d8557e37069e0c7f61933106","expected_sha256":"663c4e741d28836f0562075ae35ae55446afca74a9439c9c246447af2d8a057c","posted_source_sha256":"c4cfe585289ae4083b59c10d2d7521ccd65c4ae12bf84dab8f3b620da636ef8b","predecessor_projection_sha256":null,"review_key":"98bb2f0c3be75c3f013d8edfef2da812bd94aa08df371046335f658e930e20d9","treatment_effective_sha256":"d02dd6eb5207d201ef8862d0f508c1cb185610c8d8557e37069e0c7f61933106"}' ;;
    corrupt-receipt) printf '%s\n' '{"control_effective_sha256":"c43585e2b51db034b4520f41f0524a910f1c4efa01a5ecd4344695b22449a3db","expected_sha256":"1f1ce54286fd229e0654513d56900b67447dac17d06bf724af133995f2ffd064","posted_source_sha256":"b8b84b4c3fc44f445f20f6715aebf0d29b1968afbb23511eb6c3fb484dc8ba25","predecessor_projection_sha256":null,"review_key":"2a1dc582318e9766475b93d2f5cabe382823dfcb139377f08bbe802a92a0e5d8","treatment_effective_sha256":"c43585e2b51db034b4520f41f0524a910f1c4efa01a5ecd4344695b22449a3db"}' ;;
    security-finding) printf '%s\n' '{"control_effective_sha256":"7a1f6472bce4dce518a453a2cb18b3ce86eec1eba3f40a2030f1672626a0921e","expected_sha256":"402ff73039047c52e23c8adba453ae0e8095d8b94f2692c120d02da7ff40bc04","posted_source_sha256":"9f0486e6051a6dc2a8eed96c5dbe5559b332d5da2b638a205ae3e995f97553e3","predecessor_projection_sha256":"0ad342d36b42402079e9206752e4345c97a64af11eb71a0e0ce1ce6730480028","review_key":"5a92e8dbace8db1d04e2d9b719259fdfc7060fcc8ebf8ab9272316eb2a75af73","treatment_effective_sha256":"7a1f6472bce4dce518a453a2cb18b3ce86eec1eba3f40a2030f1672626a0921e"}' ;;
    unavailable-required-lane) printf '%s\n' '{"control_effective_sha256":"a565c7818a596ab6572b0bdb8df46377a4b2508201055c1b7c65a2130950c380","expected_sha256":"0ffa74c76bd44b1e0659f10093ea771b422b2037a4252d28c23d16fa1d4eba65","posted_source_sha256":"ce9d05c1fb6a4f10e6fa21be9f338c13ae6baf657d27768d4854fc874b7b5258","predecessor_projection_sha256":"d73cd77039a6f003f04d3a8f4e61335578af36593aa7bea283533204a6f16674","review_key":"0f560cc11827b35e5a5c36f0753c962b414870892b6e62dd590f1dcfedfd31f4","treatment_effective_sha256":"a565c7818a596ab6572b0bdb8df46377a4b2508201055c1b7c65a2130950c380"}' ;;
    cross-layer-no-dispute) printf '%s\n' '{"control_effective_sha256":"a137ea9c4df7945eb08a8a8698ce3123f473e1835ce13aefbb2ec5ab1b54f718","expected_sha256":"02e8a00bb9208bbc9a27dc8891f5e7dee549ae731284f4e20b55805cf87db9be","posted_source_sha256":"fe8dcf43cf7dc03f57b3ef43c4ef9d3d1b5ab157bc2c916392c570fcb7c6dfd6","predecessor_projection_sha256":"88d76958f1e9224a77c4d9c226107fd763c5e12eaa3417ff086962c467e911f2","review_key":"debdffa76c6d088748931a2c006d316b429e49c1aeb5467aa77d647c1763dd11","treatment_effective_sha256":"a137ea9c4df7945eb08a8a8698ce3123f473e1835ce13aefbb2ec5ab1b54f718"}' ;;
    new-material-dispute) printf '%s\n' '{"control_effective_sha256":"cb89e297f7efbd9fc1dc5d81f66235d47861653b65b2a15123764ad62567af31","expected_sha256":"1e8b5e2e94823ad7346775518bf3babefbf9eedb0343b7c7998ef2f7581bec0d","posted_source_sha256":"52d9a16e4f770e28d8a29a822d4f578fe656f77acc182613951951b32ca6345f","predecessor_projection_sha256":"086485544ee7a0149d8f1d89ee8216dcbdce5e106e490233ca84d2ee72d6daab","review_key":"b2f94ca3497d6bb2ec669864a86629b4b132f0404d77bad2240919918fe5afb8","treatment_effective_sha256":"cb89e297f7efbd9fc1dc5d81f66235d47861653b65b2a15123764ad62567af31"}' ;;
    *) return 1 ;;
  esac
}

review_latency_precision_valid() {
  local pair="$1" line quoted_line pointer_hash quote_hash candidate_hash finding_id content_hash
  local valid=true
  while IFS= read -r line || [ -n "$line" ]; do
    pointer_hash="$(review_latency_hash_json "$line" '.candidate.evidence.pointer | del(.content_sha256)')" || return 1
    quoted_line="$(jq -r '.candidate.evidence.quoted_line' <<<"$line")" || return 1
    quote_hash="$(printf '%s' "$quoted_line" | review_runtime_sha256)" || return 1
    candidate_hash="$(review_latency_hash_json "$line" '.candidate | del(.candidate_id)')" || return 1
    finding_id="$(printf '%s|%s' "$(jq -r '.candidate.review_key' <<<"$line")" "$candidate_hash" |
      review_runtime_sha256)" || return 1
    content_hash="$(review_latency_hash_json "$line" 'del(.content_sha256)')" || return 1
    jq -e -n --argjson finding "$line" --arg pointer_hash "$pointer_hash" \
      --arg quote_hash "$quote_hash" --arg candidate_hash "$candidate_hash" \
      --arg finding_id "$finding_id" --arg content_hash "$content_hash" --argjson pair "$pair" '
      ($finding.candidate.evidence.pointer.content_sha256 == $pointer_hash) and
      ($finding.candidate.evidence.quoted_line_sha256 == $quote_hash) and
      ($finding.candidate.evidence.quote_verified == true) and
      ($finding.candidate.candidate_id == $candidate_hash) and
      ($finding.finding_id == $finding_id) and
      ($finding.content_sha256 == $content_hash) and
      ($finding.candidate.review_key == $pair.exact_head.review_key) and
      ($finding.candidate.evidence.pointer.review_key == $pair.exact_head.review_key) and
      ($finding.candidate.evidence.pointer.head_sha == $pair.exact_head.head_sha) and
      ($finding.candidate.path == $finding.candidate.evidence.pointer.path) and
      ($finding.candidate.side == $finding.candidate.evidence.pointer.side) and
      ($finding.candidate.anchor_sha256 == $finding.candidate.evidence.pointer.anchor_sha256) and
      ($finding.posted == true)
    ' >/dev/null 2>&1 || valid=false
  done < <(jq -S -c '.treatment.validated_findings[]' <<<"$pair")
  [ "$valid" = true ] || return 1
  jq -e '
    ([.treatment.validated_findings[].finding_id] | sort) == .treatment.finding_ids and
    ([.treatment.validated_findings[] | select(.posted == true)] | length) ==
      .treatment.adjudicated_posted and
    ([.treatment.validated_findings[] | select(.adjudication == "false_positive")] | length) ==
      .treatment.adjudicated_false_positive and
    (.treatment.validated_findings | all(.posted == true))
  ' >/dev/null 2>&1 <<<"$pair"
}

review_latency_validate_pair() {
  local pair="$1" expected_review_key identity_valid behavior_parity timing_valid precision_valid
  local repository pr_number base_sha head_sha config_hash pair_id provenance expected_hash
  local control_effective_hash control_options_hash treatment_effective_hash treatment_options_hash
  local posted_source_hash posted_payload_hash posted_idempotency_key
  local predecessor_projection_hash predecessor_receipt_hash predecessor_receipt_id
  local predecessor_review_key ancestry_hash predecessor_valid=true
  review_latency_source_runtime || return
  review_runtime_json_has_unique_members "$pair" >/dev/null 2>&1 || return 3
  repository="$(jq -r '.exact_head.repository // empty' <<<"$pair")" || return 3
  pr_number="$(jq -r '.exact_head.pr_number // empty' <<<"$pair")" || return 3
  base_sha="$(jq -r '.exact_head.base_sha // empty' <<<"$pair")" || return 3
  head_sha="$(jq -r '.exact_head.head_sha // empty' <<<"$pair")" || return 3
  config_hash="$(jq -r '.exact_head.config_hash // empty' <<<"$pair")" || return 3
  pair_id="$(jq -r '.pair_id // empty' <<<"$pair")" || return 3
  expected_review_key="$(printf '%s|%s|%s|%s|%s' \
    "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" |
    review_runtime_sha256)" || return

  jq -e -n --argjson pair "$pair" '
    def exact_keys($required): type == "object" and (keys | sort) == ($required | sort);
    def no_extra_keys($allowed): type == "object" and ((keys - $allowed) | length) == 0;
    def sha1: type == "string" and test("^[0-9a-f]{40}$");
    def sha256: type == "string" and test("^[0-9a-f]{64}$");
    def token: type == "string" and test("^[a-z][a-z0-9._-]{0,63}$");
    def run_token: type == "string" and test("^run-[A-Za-z0-9._-]+$");
    def repository: type == "string" and test("^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$");
    def safe_path: type == "string" and length > 0 and length <= 1024 and
      (startswith("/") | not) and (endswith("/") | not) and (contains("//") | not) and
      (test("(^|/)\\.\\.?(/|$)|[[:cntrl:]\\\\]") | not);
    def safe_text: type == "string" and length > 0 and length <= 1024 and (test("[[:cntrl:]]") | not);
    def safe_int: type == "number" and floor == . and . >= 0 and . <= 9007199254740991;
    def positive_int: safe_int and . > 0;
    def hashes: type == "array" and all(.[]; sha256) and . == (sort | unique);
    def tokens: type == "array" and all(.[]; token) and . == (sort | unique);
    def event: . == "APPROVE" or . == "COMMENT" or . == "REQUEST_CHANGES";
    def identity:
      exact_keys(["base_sha","config_hash","head_sha","pr_number","repository","review_key"]) and
      (.repository | repository) and (.pr_number | positive_int) and
      (.base_sha | sha1) and (.head_sha | sha1) and (.config_hash | sha256) and (.review_key | sha256);
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
        (.review_range.from_exclusive | sha1) and .fallback.requires_existing_initial_review == false and
        (if .mode == "resolve" then
          .reason_codes == ["ancestor_append","known_finding_delta","trusted_predecessor"]
         else .reason_codes == ["ancestor_append","expanded_delta","trusted_predecessor"] end)
      end);
    def behavior_hashes: exact_keys(["event_sha256","options_sha256"]) and
      (.event_sha256 | sha256) and (.options_sha256 | sha256);
    def effective_source:
      exact_keys(["confirmation_options","coverage_gap_refs","event","review_key","schema"]) and
      .schema == "kc-pr-flow.review-effective-decision/v1" and (.review_key | sha256) and
      (.event | event) and (.coverage_gap_refs | tokens) and
      (.confirmation_options | type == "array" and length > 0 and all(.[]; event) and . == (sort | unique));
    def posted_source:
      . == null or (exact_keys(["idempotency_key","payload","payload_sha256","schema"]) and
        .schema == "kc-pr-flow.posted-review-receipt/v1" and (.idempotency_key | sha256) and
        (.payload_sha256 | sha256) and
        (.payload | exact_keys(["event","finding_ids","head_sha","review_key","schema"])) and
        .payload.schema == "kc-pr-flow.posted-review-payload/v1" and
        (.payload.event | event) and (.payload.finding_ids | hashes) and
        (.payload.head_sha | sha1) and (.payload.review_key | sha256));
    def behavior_sources: exact_keys(["effective","posted"]) and
      (.effective | effective_source) and (.posted | posted_source);
    def coverage_entry: exact_keys(["capability","gap_ref","status"]) and (.capability | token) and
      (if .status == "complete" then .gap_ref == null elif .status == "gap" then (.gap_ref | token) else false end);
    def effective_evidence:
      no_extra_keys(["coverage_gap_refs","event","review_key","schema","source_sha256"]) and
      (has("schema") and has("review_key") and has("event") and has("coverage_gap_refs")) and
      .schema == "kc-pr-flow.review-event-evidence/v1" and (.review_key | sha256) and
      (.event | event) and (.coverage_gap_refs | tokens) and
      ((has("source_sha256") | not) or (.source_sha256 | type == "string"));
    def posted_evidence: . == null or
      (exact_keys(["event","review_key","schema","source_sha256"]) and
       .schema == "kc-pr-flow.posted-review-evidence/v1" and (.review_key | sha256) and
       (.event | event) and (.source_sha256 | type == "string"));
    def receipt_finding: exact_keys(["claim_key","evidence_sha256","finding_id","path","resolution_state","side"]) and
      (.claim_key | token) and (.evidence_sha256 | sha256) and (.finding_id | sha256) and
      (.path | safe_path) and (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
      .resolution_state == "unresolved";
    def predecessor_evidence: . == null or
      (exact_keys(["ancestry","projection","projection_sha256","receipt","schema"]) and
       .schema == "kc-pr-flow.review-predecessor-evidence/v1" and (.projection_sha256 | sha256) and
       (.projection | exact_keys(["base_sha","config_hash","finding_ids","head_sha","pr_number",
         "repository","required_capabilities","review_key","run_id","schema"])) and
       .projection.schema == "kc-pr-flow.review-predecessor-projection/v1" and
       (.projection.repository | repository) and (.projection.pr_number | positive_int) and
       (.projection.base_sha | sha1) and (.projection.head_sha | sha1) and
       (.projection.config_hash | sha256) and (.projection.review_key | sha256) and
       (.projection.run_id | run_token) and (.projection.finding_ids | hashes) and
       (.projection.required_capabilities | tokens) and
       (.receipt | exact_keys(["content_sha256","coverage_gap_refs","known_findings","predecessor",
         "required_capabilities","schema"])) and
       .receipt.schema == "kc-pr-flow.review-delta-receipt/v1" and (.receipt.content_sha256 | sha256) and
       (.receipt.coverage_gap_refs | tokens) and (.receipt.known_findings | type == "array" and all(.[]; receipt_finding)) and
       (.receipt.required_capabilities | tokens) and
       (.receipt.predecessor | exact_keys(["base_sha","config_hash","head_sha","pr_number","receipt_id",
         "repository","review_key","run_id"])) and
       (.receipt.predecessor.repository | repository) and (.receipt.predecessor.pr_number | positive_int) and
       (.receipt.predecessor.base_sha | sha1) and (.receipt.predecessor.head_sha | sha1) and
       (.receipt.predecessor.config_hash | sha256) and (.receipt.predecessor.review_key | sha256) and
       (.receipt.predecessor.run_id | run_token) and (.receipt.predecessor.receipt_id | sha256) and
       (.ancestry | exact_keys(["current_head_sha","predecessor_head_sha","relationship","schema","source_sha256"])) and
       .ancestry.schema == "kc-pr-flow.review-ancestry-evidence/v1" and
       (.ancestry.current_head_sha | sha1) and (.ancestry.predecessor_head_sha | sha1) and
       .ancestry.relationship == "ancestor_append" and (.ancestry.source_sha256 | sha256));
    def evidence_pointer: exact_keys(["anchor_sha256","content_sha256","head_sha","path","review_key","schema","side"]) and
      .schema == "kc-pr-flow.evidence-pointer/v1" and (.anchor_sha256 | sha256) and
      (.content_sha256 | type == "string") and (.head_sha | sha1) and (.path | safe_path) and
      (.review_key | sha256) and (.side == "LEFT" or .side == "RIGHT" or .side == "FILE");
    def candidate: exact_keys(["anchor_sha256","candidate_id","capability","category","claim_key","confidence",
      "evidence","lane_id","path","review_key","schema","severity","side","summary"]) and
      .schema == "kc-pr-flow.review-candidate/v2" and (.anchor_sha256 | sha256) and
      (.candidate_id | type == "string") and (.capability | token) and (.category | token) and
      (.claim_key | token) and (.confidence | safe_int and . >= 1 and . <= 10) and
      (.lane_id | token) and (.path | safe_path) and (.review_key | sha256) and
      (.severity == "LOW" or .severity == "MEDIUM" or .severity == "HIGH" or .severity == "CRITICAL") and
      (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and (.summary | safe_text) and
      (.evidence | exact_keys(["pointer","quote_verified","quoted_line","quoted_line_sha256"])) and
      (.evidence.pointer | evidence_pointer) and (.evidence.quote_verified | type == "boolean") and
      (.evidence.quoted_line | safe_text) and (.evidence.quoted_line_sha256 | type == "string");
    def validated_finding: exact_keys(["adjudication","candidate","content_sha256","finding_id","posted","schema"]) and
      .schema == "kc-pr-flow.review-finding-evidence/v1" and
      (.adjudication == "true_positive" or .adjudication == "false_positive") and
      (.candidate | candidate) and (.content_sha256 | type == "string") and
      (.finding_id | type == "string") and (.posted | type == "boolean");
    def timing: exact_keys(["durations_ms","lane_durations_ms","measured_by","mode","review_key","schema"]) and
      .schema == "kc-pr-flow.review-timing/v1" and (.review_key | sha256) and
      (.mode == "delta" or .mode == "resolve") and .measured_by == "review-runtime" and
      (.durations_ms | exact_keys(["collation_and_draft","confirmation_wait","external_ci_wait",
        "identity_and_plan","inventory","post_mutation","required_lanes_critical_path",
        "review_to_confirmation_ready","targeted_verification_critical_path"])) and
      ([.durations_ms.identity_and_plan,.durations_ms.inventory,.durations_ms.required_lanes_critical_path,
        .durations_ms.targeted_verification_critical_path,.durations_ms.collation_and_draft,
        .durations_ms.review_to_confirmation_ready] | all(.[]; safe_int)) and
      .durations_ms.confirmation_wait == null and .durations_ms.external_ci_wait == null and
      .durations_ms.post_mutation == null and
      (.lane_durations_ms | type == "array" and all(.[]; exact_keys(["duration_ms","lane_id","provider_family"]) and
        (.lane_id | token) and (.duration_ms | safe_int) and
        (.provider_family == null or (.provider_family | token))) and
        ([.[].lane_id] | unique | length) == length);
    ($pair | exact_keys(["control","exact_head","expected","pair_id","schema","treatment"])) and
    $pair.schema == "kc-pr-flow.review-latency-pair/v1" and ($pair.pair_id | token) and
    ($pair.exact_head | identity) and
    ($pair.expected | exact_keys(["maximum_event","mode","must_fix_finding_ids","required_capabilities"])) and
    ($pair.expected.mode == "initial" or $pair.expected.mode == "delta" or $pair.expected.mode == "resolve") and
    ($pair.expected.must_fix_finding_ids | hashes) and ($pair.expected.required_capabilities | tokens) and
    ($pair.expected.maximum_event | event) and
    ($pair.control | exact_keys(["adjudicated_false_positive","adjudicated_posted","behavior_hashes",
      "behavior_sources","finding_ids"])) and ($pair.control.finding_ids | hashes) and
    ($pair.control.adjudicated_posted | safe_int) and ($pair.control.adjudicated_false_positive | safe_int) and
    ($pair.control.behavior_hashes | behavior_hashes) and ($pair.control.behavior_sources | behavior_sources) and
    (($pair.expected.must_fix_finding_ids - $pair.control.finding_ids) | length) == 0 and
    ($pair.treatment | exact_keys(["adjudicated_false_positive","adjudicated_posted","behavior_hashes",
      "behavior_sources","capability_coverage","capability_gap_refs","event_evidence","finding_ids","plan",
      "predecessor_evidence","timing","validated_findings"])) and
    ($pair.treatment.plan | plan) and ($pair.treatment.finding_ids | hashes) and
    ($pair.treatment.adjudicated_posted | safe_int) and ($pair.treatment.adjudicated_false_positive | safe_int) and
    ($pair.treatment.behavior_hashes | behavior_hashes) and ($pair.treatment.behavior_sources | behavior_sources) and
    ($pair.treatment.capability_coverage | type == "array" and all(.[]; coverage_entry) and
      ([.[].capability] | unique | length) == length) and
    ($pair.treatment.capability_gap_refs | tokens) and
    ([$pair.treatment.capability_coverage[] | select(.status == "gap") | .gap_ref] | sort) ==
      $pair.treatment.capability_gap_refs and
    ($pair.treatment.event_evidence | exact_keys(["effective","posted"])) and
    ($pair.treatment.event_evidence.effective | effective_evidence) and
    ($pair.treatment.event_evidence.posted | posted_evidence) and
    ($pair.treatment.predecessor_evidence | predecessor_evidence) and
    ($pair.treatment.validated_findings | type == "array" and length > 0 and all(.[]; validated_finding) and
      ([.[].finding_id] | unique | length) == length) and
    (if $pair.treatment.plan.mode == "initial" then
       $pair.treatment.timing == null and $pair.treatment.predecessor_evidence == null
     else ($pair.treatment.timing | timing) and $pair.treatment.predecessor_evidence != null end)
  ' >/dev/null 2>&1 || return 3

  control_effective_hash="$(review_latency_hash_json "$pair" '.control.behavior_sources.effective')" || return 3
  control_options_hash="$(review_latency_hash_json "$pair" '.control.behavior_sources.effective.confirmation_options')" || return 3
  treatment_effective_hash="$(review_latency_hash_json "$pair" '.treatment.behavior_sources.effective')" || return 3
  treatment_options_hash="$(review_latency_hash_json "$pair" '.treatment.behavior_sources.effective.confirmation_options')" || return 3
  posted_source_hash=''
  if [ "$(jq -r '.treatment.behavior_sources.posted == null' <<<"$pair")" = false ]; then
    posted_source_hash="$(review_latency_hash_json "$pair" '.treatment.behavior_sources.posted')" || return 3
    posted_payload_hash="$(review_latency_hash_json "$pair" '.treatment.behavior_sources.posted.payload')" || return 3
    posted_idempotency_key="$(printf '%s|%s|%s' "$expected_review_key" "$head_sha" "$posted_payload_hash" |
      review_runtime_sha256)" || return 3
  fi

  if [ "$(jq -r '.treatment.plan.mode' <<<"$pair")" != initial ]; then
    predecessor_projection_hash="$(review_latency_hash_json "$pair" '.treatment.predecessor_evidence.projection')" || return 3
    predecessor_receipt_hash="$(review_latency_hash_json "$pair" '.treatment.predecessor_evidence.receipt | del(.content_sha256)')" || return 3
    predecessor_review_key="$(printf '%s|%s|%s|%s|%s' \
      "$(jq -r '.treatment.predecessor_evidence.projection.repository' <<<"$pair")" \
      "$(jq -r '.treatment.predecessor_evidence.projection.pr_number' <<<"$pair")" \
      "$(jq -r '.treatment.predecessor_evidence.projection.base_sha' <<<"$pair")" \
      "$(jq -r '.treatment.predecessor_evidence.projection.head_sha' <<<"$pair")" \
      "$(jq -r '.treatment.predecessor_evidence.projection.config_hash' <<<"$pair")" |
      review_runtime_sha256)" || return 3
    predecessor_receipt_id="$(printf '%s|%s|%s' \
      "$(jq -r '.treatment.predecessor_evidence.projection.run_id' <<<"$pair")" \
      "$predecessor_review_key" "$predecessor_projection_hash" | review_runtime_sha256)" || return 3
    ancestry_hash="$(review_latency_hash_json "$pair" '.treatment.predecessor_evidence.ancestry | del(.source_sha256)')" || return 3
    jq -e -n --argjson pair "$pair" --arg projection_hash "$predecessor_projection_hash" \
      --arg receipt_hash "$predecessor_receipt_hash" --arg review_key "$predecessor_review_key" \
      --arg receipt_id "$predecessor_receipt_id" --arg ancestry_hash "$ancestry_hash" '
      $pair.treatment.predecessor_evidence as $p |
      ($p.projection_sha256 == $projection_hash) and
      ($p.projection.review_key == $review_key) and
      ($p.receipt.content_sha256 == $receipt_hash) and
      ($p.receipt.predecessor.receipt_id == $receipt_id) and
      ($p.receipt.predecessor == ($p.projection + {receipt_id:$receipt_id} |
        del(.schema,.finding_ids,.required_capabilities))) and
      ($p.receipt.known_findings | map(.finding_id) | sort) == $p.projection.finding_ids and
      ($p.receipt.required_capabilities == $p.projection.required_capabilities) and
      ($p.ancestry.source_sha256 == $ancestry_hash) and
      ($p.ancestry.predecessor_head_sha == $p.projection.head_sha) and
      ($p.ancestry.current_head_sha == $pair.exact_head.head_sha) and
      ($p.projection.repository == $pair.exact_head.repository) and
      ($p.projection.pr_number == $pair.exact_head.pr_number) and
      ($p.projection.base_sha == $pair.exact_head.base_sha) and
      ($p.projection.config_hash == $pair.exact_head.config_hash) and
      ($pair.treatment.plan.review_range.from_exclusive == $p.projection.head_sha) and
      ($pair.treatment.plan.review_range.from_exclusive != $pair.exact_head.head_sha) and
      ($pair.treatment.plan.inherited_finding_ids | length > 0) and
      ($pair.treatment.plan.inherited_finding_ids == $p.projection.finding_ids) and
      (($pair.expected.must_fix_finding_ids - $pair.treatment.plan.inherited_finding_ids) | length == 0)
    ' >/dev/null 2>&1 || predecessor_valid=false
  fi

  provenance="$(review_latency_expected_provenance "$pair_id")" || return 3
  expected_hash="$(review_latency_hash_json "$pair" '.expected')" || return 3
  identity_valid="$(jq -r --arg expected_review_key "$expected_review_key" --arg expected_hash "$expected_hash" \
    --argjson provenance "$provenance" --arg predecessor_projection_hash "${predecessor_projection_hash:-}" \
    --argjson predecessor_valid "$predecessor_valid" '
    (.exact_head.review_key == $expected_review_key) and
    (.exact_head.review_key == $provenance.review_key) and ($expected_hash == $provenance.expected_sha256) and
    (.expected.mode == .treatment.plan.mode) and
    (.expected.required_capabilities == .treatment.plan.required_capabilities) and
    (.treatment.plan.identity == .exact_head) and
    (.treatment.plan.review_range.to_inclusive == .exact_head.head_sha) and
    (.treatment.event_evidence.effective.review_key == .exact_head.review_key) and
    (.treatment.event_evidence.posted == null or .treatment.event_evidence.posted.review_key == .exact_head.review_key) and
    (if .treatment.timing == null then .treatment.plan.mode == "initial"
     else .treatment.timing.review_key == .exact_head.review_key and .treatment.timing.mode == .treatment.plan.mode end) and
    (if .treatment.plan.mode == "initial" then $provenance.predecessor_projection_sha256 == null
     else $predecessor_valid and $predecessor_projection_hash == $provenance.predecessor_projection_sha256 end)
  ' <<<"$pair")" || return 3

  behavior_parity="$(jq -r --arg control_effective_hash "$control_effective_hash" \
    --arg control_options_hash "$control_options_hash" --arg treatment_effective_hash "$treatment_effective_hash" \
    --arg treatment_options_hash "$treatment_options_hash" --arg posted_source_hash "$posted_source_hash" \
    --arg posted_payload_hash "${posted_payload_hash:-}" --arg posted_idempotency_key "${posted_idempotency_key:-}" \
    --argjson provenance "$provenance" '
    def rank: if . == "REQUEST_CHANGES" then 0 elif . == "COMMENT" then 1 elif . == "APPROVE" then 2 else -1 end;
    (.control.behavior_hashes.event_sha256 == $control_effective_hash) and
    (.control.behavior_hashes.options_sha256 == $control_options_hash) and
    (.treatment.behavior_hashes.event_sha256 == $treatment_effective_hash) and
    (.treatment.behavior_hashes.options_sha256 == $treatment_options_hash) and
    (.treatment.event_evidence.effective.source_sha256? == $treatment_effective_hash) and
    ($control_effective_hash == $provenance.control_effective_sha256) and
    ($treatment_effective_hash == $provenance.treatment_effective_sha256) and
    (($posted_source_hash == "" and $provenance.posted_source_sha256 == null and .treatment.event_evidence.posted == null) or
      ($posted_source_hash != "" and $posted_source_hash == $provenance.posted_source_sha256 and
       .treatment.event_evidence.posted.source_sha256 == $posted_source_hash and
       .treatment.behavior_sources.posted.payload_sha256 == $posted_payload_hash and
       .treatment.behavior_sources.posted.idempotency_key == $posted_idempotency_key and
       .treatment.behavior_sources.posted.payload.review_key == .exact_head.review_key and
       .treatment.behavior_sources.posted.payload.head_sha == .exact_head.head_sha and
       .treatment.behavior_sources.posted.payload.finding_ids == .treatment.finding_ids and
       .treatment.behavior_sources.posted.payload.event == .treatment.event_evidence.posted.event)) and
    ((.treatment.event_evidence.effective.event | rank) <= (.expected.maximum_event | rank)) and
    (.treatment.event_evidence.posted == null or
      ((.treatment.event_evidence.posted.event | rank) <= (.expected.maximum_event | rank))) and
    (.treatment.plan.mode == "initial" or
      ((.treatment.plan.event_ceiling | rank) <= (.expected.maximum_event | rank) and
       (.treatment.event_evidence.effective.event | rank) <= (.treatment.plan.event_ceiling | rank) and
       (.treatment.event_evidence.posted == null or
         ((.treatment.event_evidence.posted.event | rank) <= (.treatment.plan.event_ceiling | rank)))))
  ' <<<"$pair")" || return 3

  if review_latency_precision_valid "$pair"; then precision_valid=true; else precision_valid=false; fi
  timing_valid="$(jq -r '
    if .treatment.timing == null then true else
      .treatment.timing.durations_ms as $d |
      ($d.identity_and_plan + $d.inventory + $d.required_lanes_critical_path +
       $d.targeted_verification_critical_path + $d.collation_and_draft) as $sum |
      ($d.review_to_confirmation_ready - $sum) as $remainder |
      $remainder >= 0 and $remainder <= 4
    end
  ' <<<"$pair")" || return 3

  jq -S -c --argjson identity_valid "$identity_valid" --argjson behavior_parity "$behavior_parity" \
    --argjson precision_valid "$precision_valid" --argjson timing_valid "$timing_valid" \
    '. + {_derived:{identity_valid:$identity_valid,behavior_parity:$behavior_parity,
      precision_valid:$precision_valid,timing_valid:$timing_valid}}' <<<"$pair"
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
    ["corrupt-receipt","cross-layer-no-dispute","fix-plus-test","force-push","known-fix-only",
      "new-material-dispute","security-finding","unavailable-required-lane","unrelated-new-path"] as $required_classes |
    [$pairs[] | select(latency_eligible)] as $eligible |
    (([$pairs[].pair_id] == $required_classes) and ($pairs | all(._derived.identity_valid))) as $q1 |
    ($pairs | all(required_coverage_safe)) as $q2 |
    ($pairs | all(((.expected.must_fix_finding_ids - .treatment.finding_ids) | length) == 0)) as $q3 |
    ($pairs | all(._derived.precision_valid and
      (.control.adjudicated_posted == (.control.finding_ids | length)) and
      (.control.adjudicated_false_positive <= .control.adjudicated_posted) and
      (.treatment.adjudicated_false_positive <= .control.adjudicated_false_positive))) as $q4 |
    ($pairs | all(._derived.behavior_parity)) as $q5 |
    (($eligible | length) == 7 and
      ($eligible | all(._derived.timing_valid and
        .treatment.timing.durations_ms.review_to_confirmation_ready <= 240000))) as $q6 |
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
        passing_runs:([$eligible[] | select(._derived.timing_valid and
          .treatment.timing.durations_ms.review_to_confirmation_ready <= 240000)]|length),
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
