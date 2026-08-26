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

# The decision boundary owns one path check per invocation.  All later Git
# helpers receive only this canonical path; checking it before every Git call
# would add a Python process to each small read without improving this
# invocation's trust boundary.
review_plan_real_worktree() {
  python3 - "$1" <<'PY'
import os
import stat
import sys

raw = sys.argv[1]
if not os.path.isabs(raw) or os.path.normpath(raw) != raw:
    raise SystemExit(2)
candidate = raw
try:
    mode = os.lstat(candidate).st_mode
except OSError:
    raise SystemExit(2)
cursor = os.sep
for component in candidate.split(os.sep)[1:]:
    cursor = os.path.join(cursor, component)
    try:
        if stat.S_ISLNK(os.lstat(cursor).st_mode):
            raise SystemExit(2)
    except OSError:
        raise SystemExit(2)
if not stat.S_ISDIR(mode) or os.path.realpath(candidate) != candidate:
    raise SystemExit(2)
print(candidate)
PY
}

review_plan_git() {
  local worktree="$1"
  shift
  command git -C "$worktree" "$@"
}

review_plan_git_identity_valid() {
  local worktree="$1" object="$2"
  review_plan_git "$worktree" rev-parse --git-dir >/dev/null 2>&1 || return 1
  [ "$(review_plan_git "$worktree" cat-file -t "$object" 2>/dev/null)" = 'commit' ]
}

review_plan_ancestor() {
  review_plan_git "$1" merge-base --is-ancestor "$2" "$3"
}

review_plan_changed_paths() {
  review_plan_git "$1" diff --name-status --find-renames=50% --find-copies=50% --find-copies-harder "$2..$3"
}

review_plan_changed_object_is_safe() {
  local worktree="$1" base_sha="$2" head_sha="$3" path="$4"
  local tree_entry entry_path extra mode type object numstat added removed numstat_path
  tree_entry="$(review_plan_git "$worktree" ls-tree "$head_sha" -- "$path")" || return 1
  [ -n "$tree_entry" ] || return 1
  IFS=$'\t' read -r tree_entry entry_path extra <<<"$tree_entry"
  [ -z "$extra" ] && [ "$entry_path" = "$path" ] || return 1
  read -r mode type object <<<"$tree_entry"
  case "$mode:$type" in
    100644:blob|100755:blob) ;;
    *) return 1 ;;
  esac
  numstat="$(review_plan_git "$worktree" diff --numstat "$base_sha..$head_sha" -- "$path")" || return 1
  [ -n "$numstat" ] || return 1
  IFS=$'\t' read -r added removed numstat_path extra <<<"$numstat"
  [ -z "$extra" ] && [ "$numstat_path" = "$path" ] || return 1
  [ "$added" != '-' ] && [ "$removed" != '-' ]
}

review_plan_safe_path() {
  local path="$1"
  [ -n "$path" ] || return 1
  case "$path" in
    /*|*/|*'//'*) return 1 ;;
  esac
  case "/$path/" in
    *'/./'*|*'/../'*) return 1 ;;
  esac
  [[ "$path" != *$'\n'* && "$path" != *$'\r'* && "$path" != *\\* ]]
}

review_plan_input_identity_valid() {
  jq -e -n --arg repository "$1" --arg pr_number "$2" --arg base_sha "$3" --arg head_sha "$4" --arg config_hash "$5" '
    ($repository | test("^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")) and
    ($pr_number | test("^[1-9][0-9]*$")) and
    ($base_sha | test("^[0-9a-f]{40}$")) and
    ($head_sha | test("^[0-9a-f]{40}$")) and
    ($config_hash | test("^[0-9a-f]{64}$"))
  ' >/dev/null 2>&1
}

review_plan_build_decision() {
  local repository="$1" pr_number="$2" base_sha="$3" head_sha="$4" config_hash="$5"
  local mode="$6" reason_codes="$7" from_exclusive="$8" inherited_finding_ids="$9"
  local required_capabilities="${10}" event_ceiling="${11}" full_initial="${12}" review_key fallback
  review_key="$(printf '%s|%s|%s|%s|%s' "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" |
    review_runtime_sha256)" || return
  fallback="$(jq -S -c -n --argjson full_initial "$full_initial" \
    '{router_advisory:true,requires_existing_initial_review:$full_initial,final_verdict_authority:"existing-review-runtime"}')" || return
  jq -S -c -n \
    --arg repository "$repository" --argjson pr_number "$pr_number" --arg base_sha "$base_sha" \
    --arg head_sha "$head_sha" --arg config_hash "$config_hash" --arg review_key "$review_key" \
    --arg mode "$mode" --argjson reason_codes "$reason_codes" --argjson from_exclusive "$from_exclusive" \
    --argjson inherited_finding_ids "$inherited_finding_ids" --argjson required_capabilities "$required_capabilities" \
    --argjson event_ceiling "$event_ceiling" --argjson fallback "$fallback" \
    '{schema:"kc-pr-flow.review-plan-decision/v1",
      identity:{repository:$repository,pr_number:$pr_number,base_sha:$base_sha,head_sha:$head_sha,
        config_hash:$config_hash,review_key:$review_key},
      mode:$mode,
      reason_codes:($reason_codes | sort | unique),
      review_range:{from_exclusive:$from_exclusive,to_inclusive:$head_sha},
      inherited_finding_ids:($inherited_finding_ids | sort | unique),
      required_capabilities:($required_capabilities | sort | unique),
      event_ceiling:$event_ceiling,
      fallback:$fallback}'
}

review_plan_initial_decision() {
  review_plan_build_decision "$1" "$2" "$3" "$4" "$5" initial "[\"$6\"]" null '[]' '[]' null true
}

review_plan_snapshot_receipt() (
  local receipt="$1" snapshot_dir='' snapshot_file=''
  if [ -e "$receipt" ] || [ -L "$receipt" ]; then
    snapshot_dir="$(review_runtime_private_snapshot_dir)" || return
    snapshot_file="$snapshot_dir/receipt.json"
    trap 'review_runtime_remove_private_snapshot_dir "$snapshot_dir" "$snapshot_file"' EXIT
    review_runtime_snapshot_regular_file "$receipt" "$snapshot_file" 'delta receipt' "${KC_PR_FLOW_MAX_RECEIPT_BYTES:-1048576}" || return
    cat "$snapshot_file"
  else
    printf '%s' "$receipt"
  fi
)

review_plan_known_path() {
  jq -e --arg path "$2" '.known_findings | any(.path == $path)' <<<"$1" >/dev/null 2>&1
}

review_plan_mechanical_adjacency() {
  local worktree="$1" head_sha="$2" path="$3" receipt="$4" content finding_path basename import_path matches=0
  [[ "$path" =~ (^|/)(test|tests|__tests__|fixtures)/ ]] || return 1
  content="$(review_plan_git "$worktree" show "$head_sha:$path" 2>/dev/null)" || return 1
  while IFS= read -r finding_path; do
    basename="${finding_path##*/}"
    import_path="${finding_path%.*}"
    import_path="${import_path//\//.}"
    if printf '%s' "$content" | grep -F -q -e "$basename" -e "$import_path"; then
      matches=$((matches + 1))
    fi
  done < <(jq -r '.known_findings[].path' <<<"$receipt")
  [ "$matches" -eq 1 ]
}

review_plan_decide() {
  local repository="$1" pr_number="$2" base_sha="$3" head_sha="$4" config_hash="$5"
  local worktree="$6" predecessor_events="$7" delta_receipt="$8" canonical receipt_source predecessor_repository predecessor_pr
  local predecessor_base predecessor_head predecessor_config changed status path extra unknown=0 expanded=0 known=0
  local inherited_finding_ids required_capabilities

  review_plan_input_identity_valid "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" || return 2
  if [ "${KC_PR_FLOW_DELTA_FAST_PATH:-off}" != 'on' ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" feature_disabled
    return
  fi
  canonical="$(review_plan_real_worktree "$worktree")" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" invalid_predecessor
    return
  }
  if [ -z "$predecessor_events" ] || [ -z "$delta_receipt" ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" missing_predecessor
    return
  fi
  receipt_source="$(review_plan_snapshot_receipt "$delta_receipt")" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" invalid_predecessor
    return
  }
  review_plan_validate_receipt "$receipt_source" "$predecessor_events" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" invalid_predecessor
    return
  }
  predecessor_repository="$(jq -r '.predecessor.repository' <<<"$receipt_source")" || return 3
  predecessor_pr="$(jq -r '.predecessor.pr_number' <<<"$receipt_source")" || return 3
  predecessor_base="$(jq -r '.predecessor.base_sha' <<<"$receipt_source")" || return 3
  predecessor_head="$(jq -r '.predecessor.head_sha' <<<"$receipt_source")" || return 3
  predecessor_config="$(jq -r '.predecessor.config_hash' <<<"$receipt_source")" || return 3
  if [ "$predecessor_repository" != "$repository" ] || [ "$predecessor_pr" != "$pr_number" ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" identity_mismatch
    return
  fi
  if [ "$predecessor_base" != "$base_sha" ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" base_changed
    return
  fi
  if [ "$predecessor_config" != "$config_hash" ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" config_changed
    return
  fi
  if ! review_plan_git_identity_valid "$canonical" "$base_sha" ||
    ! review_plan_git_identity_valid "$canonical" "$predecessor_head" ||
    ! review_plan_git_identity_valid "$canonical" "$head_sha"; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" invalid_predecessor
    return
  fi
  if ! review_plan_ancestor "$canonical" "$predecessor_head" "$head_sha"; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" non_ancestor
    return
  fi
  changed="$(review_plan_changed_paths "$canonical" "$predecessor_head" "$head_sha")" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" unknown_delta
    return
  }
  [ -n "$changed" ] || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" unknown_delta
    return
  }
  while IFS=$'\t' read -r status path extra; do
    case "$status" in
      A|M) ;;
      *) unknown=1; break ;;
    esac
    review_plan_safe_path "$path" || { unknown=1; break; }
    [ -z "$extra" ] || { unknown=1; break; }
    review_plan_changed_object_is_safe "$canonical" "$predecessor_head" "$head_sha" "$path" || { unknown=1; break; }
    if review_plan_known_path "$receipt_source" "$path"; then
      known=1
    elif review_plan_mechanical_adjacency "$canonical" "$head_sha" "$path" "$receipt_source"; then
      :
    else
      expanded=1
    fi
  done <<<"$changed"
  if [ "$unknown" -ne 0 ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" unknown_delta
    return
  fi
  inherited_finding_ids="$(jq -S -c '[.known_findings[].finding_id] | sort | unique' <<<"$receipt_source")" || return 3
  required_capabilities="$(jq -S -c '.required_capabilities | sort | unique' <<<"$receipt_source")" || return 3
  if [ "$known" -ne 0 ] && [ "$expanded" -eq 0 ]; then
    review_plan_build_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" resolve \
      '["trusted_predecessor","ancestor_append","known_finding_delta"]' "\"$predecessor_head\"" \
      "$inherited_finding_ids" "$required_capabilities" '"APPROVE"' false
    return
  fi
  required_capabilities="$(jq -S -c '. + ["correctness"] | sort | unique' <<<"$required_capabilities")" || return 3
  review_plan_build_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" delta \
    '["trusted_predecessor","ancestor_append","expanded_delta"]' "\"$predecessor_head\"" \
    "$inherited_finding_ids" "$required_capabilities" '"COMMENT"' false
}

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
  local repository='' pr_number='' base_sha='' head_sha='' config_hash='' worktree=''
  local predecessor_events='' delta_receipt=''
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --repo|--pr|--base|--head|--config-hash|--repo-worktree|--predecessor-events|--delta-receipt)
        [ "$#" -ge 2 ] || { printf 'review-plan: missing value for %s\n' "$1" >&2; return 2; }
        case "$1" in
          --repo) repository="$2" ;;
          --pr) pr_number="$2" ;;
          --base) base_sha="$2" ;;
          --head) head_sha="$2" ;;
          --config-hash) config_hash="$2" ;;
          --repo-worktree) worktree="$2" ;;
          --predecessor-events) predecessor_events="$2" ;;
          --delta-receipt) delta_receipt="$2" ;;
        esac
        shift 2
        ;;
      *) printf 'review-plan: unknown decide option: %s\n' "$1" >&2; return 2 ;;
    esac
  done
  [ -n "$repository" ] && [ -n "$pr_number" ] && [ -n "$base_sha" ] && [ -n "$head_sha" ] &&
    [ -n "$config_hash" ] && [ -n "$worktree" ] || {
    printf 'review-plan: --repo, --pr, --base, --head, --config-hash, and --repo-worktree are required\n' >&2
    return 2
  }
  review_plan_decide "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" "$worktree" \
    "$predecessor_events" "$delta_receipt"
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
