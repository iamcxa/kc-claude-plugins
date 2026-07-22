#!/usr/bin/env bash
# review-runtime.sh — append-only shadow receipt primitives for kc-pr-review.
#
# This file is both a source-safe function library and a small local CLI. It
# deliberately owns no review verdict, confirmation, authorization, posting,
# GitHub, resume, or garbage-collection behavior.

review_runtime_sha256() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum | awk '{print $1}'
  else
    printf 'review-runtime: sha256 tool unavailable\n' >&2
    return 69
  fi
}

review_runtime_require_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    printf 'review-runtime: jq is required\n' >&2
    return 69
  fi
}

review_runtime_snapshot_regular_file() {
  local source_file="$1"
  local snapshot_file="$2"
  local label="$3"
  if [ ! -f "$source_file" ] || [ -L "$source_file" ]; then
    printf 'review-runtime: %s is not a safe regular file: %s\n' "$label" "$source_file" >&2
    return 2
  fi
  if ! cat "$source_file" >"$snapshot_file" || ! chmod 0600 "$snapshot_file"; then
    printf 'review-runtime: unable to snapshot %s\n' "$label" >&2
    return 74
  fi
}

review_runtime_state_root() {
  printf '%s\n' "${KC_PR_FLOW_STATE_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/kc-pr-flow}"
}

review_runtime_real_directory() {
  [ -d "$1" ] && [ ! -L "$1" ]
}

review_runtime_prepare_state_root() {
  local state_root
  state_root="$(review_runtime_state_root)" || return
  if [ -L "$state_root" ] || { [ -e "$state_root" ] && [ ! -d "$state_root" ]; }; then
    printf 'review-runtime: unsafe managed state root: %s\n' "$state_root" >&2
    return 74
  fi
  if [ ! -d "$state_root" ]; then
    mkdir -p "$state_root" || return 74
  fi
  if ! review_runtime_real_directory "$state_root"; then
    printf 'review-runtime: unsafe managed state root: %s\n' "$state_root" >&2
    return 74
  fi
  printf '%s\n' "$state_root"
}

review_runtime_prepare_child_directory() {
  local parent="$1"
  local segment="$2"
  local child
  review_runtime_real_directory "$parent" || return 74
  [[ "$segment" =~ ^[A-Za-z0-9._-]+$ ]] && [ "$segment" != '.' ] && [ "$segment" != '..' ] || return 74
  child="$parent/$segment"
  if [ -L "$child" ] || { [ -e "$child" ] && [ ! -d "$child" ]; }; then
    printf 'review-runtime: unsafe managed directory: %s\n' "$child" >&2
    return 74
  fi
  if [ ! -d "$child" ]; then
    mkdir "$child" 2>/dev/null || review_runtime_real_directory "$child" || return 74
  fi
  if ! review_runtime_real_directory "$child"; then
    printf 'review-runtime: unsafe managed directory: %s\n' "$child" >&2
    return 74
  fi
  printf '%s\n' "$child"
}

review_runtime_existing_child_directory() {
  local parent="$1"
  local segment="$2"
  local child
  review_runtime_real_directory "$parent" || return 74
  [[ "$segment" =~ ^[A-Za-z0-9._-]+$ ]] && [ "$segment" != '.' ] && [ "$segment" != '..' ] || return 74
  child="$parent/$segment"
  review_runtime_real_directory "$child" || return 74
  printf '%s\n' "$child"
}

review_runtime_events_size_within_limit() {
  local events_file="$1"
  local limit="${KC_PR_FLOW_MAX_EVENTS_BYTES:-16777216}"
  local size
  [[ "$limit" =~ ^[1-9][0-9]*$ ]] || {
    printf 'review-runtime: invalid events size limit\n' >&2
    return 73
  }
  size="$(wc -c <"$events_file" | tr -d ' ')" || return
  if [ "$size" -gt "$limit" ]; then
    printf 'review-runtime: events size limit exceeded (%s > %s)\n' "$size" "$limit" >&2
    return 73
  fi
}

review_runtime_remove_private_run() {
  local run_dir="$1"
  [ -d "$run_dir" ] && [ ! -L "$run_dir" ] || return 0
  chmod 0700 "$run_dir" 2>/dev/null || true
  chmod 0600 "$run_dir/events.jsonl" 2>/dev/null || true
  rm -f "$run_dir/events.jsonl"
  rmdir "$run_dir" 2>/dev/null || true
}

review_runtime_repo_key() {
  printf '%s' "$1" | review_runtime_sha256
}

review_runtime_review_key() {
  printf '%s|%s|%s|%s|%s' "$1" "$2" "$3" "$4" "$5" | review_runtime_sha256
}

review_runtime_repository_identity_valid() {
  [ -n "$1" ] || return 1
  ! printf '%s' "$1" | LC_ALL=C grep '[[:cntrl:]]' >/dev/null 2>&1
}

review_runtime_successor_reason_valid() {
  case "$1" in
    manual_rerun | config_change | head_appended | head_rewritten | recovery_fork)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

review_runtime_validate_start_input() {
  local repository="$1"
  local pr_number="$2"
  local base_sha="$3"
  local head_sha="$4"
  local config_hash="$5"
  local occurred_at="$6"
  local predecessor_run_id="$7"
  local successor_reason="$8"

  review_runtime_repository_identity_valid "$repository" || {
    printf 'review-runtime: invalid repository identity\n' >&2
    return 2
  }
  [[ "$pr_number" =~ ^[1-9][0-9]*$ ]] || {
    printf 'review-runtime: invalid PR number\n' >&2
    return 2
  }
  [[ "$base_sha" =~ ^[0-9a-f]{40}$ ]] || {
    printf 'review-runtime: invalid base SHA\n' >&2
    return 2
  }
  [[ "$head_sha" =~ ^[0-9a-f]{40}$ ]] || {
    printf 'review-runtime: invalid head SHA\n' >&2
    return 2
  }
  [[ "$config_hash" =~ ^[0-9a-f]{64}$ ]] || {
    printf 'review-runtime: invalid config hash\n' >&2
    return 2
  }
  [[ "$occurred_at" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?Z$ ]] || {
    printf 'review-runtime: invalid occurred_at; expected RFC3339 UTC\n' >&2
    return 2
  }

  if [ -n "$predecessor_run_id" ] || [ -n "$successor_reason" ]; then
    [[ "$predecessor_run_id" =~ ^run-[A-Za-z0-9._-]+$ ]] || {
      printf 'review-runtime: invalid predecessor run ID\n' >&2
      return 2
    }
    if ! review_runtime_successor_reason_valid "$successor_reason"; then
      printf 'review-runtime: invalid successor reason\n' >&2
      return 2
    fi
  fi
}

# Canonicalization and hashing contract (v1 compatibility boundary):
# - Inputs are UTF-8 JSON bytes parsed and serialized with jq -S -c.
# - Hash the resulting compact byte sequence with no trailing newline.
# - payload_sha256 = sha256(canonical payload bytes)
# - event_id = sha256(run_id|sequence|event_type|payload_sha256)
# - review_key = sha256(repository|pr_number|base_sha|head_sha|config_hash)
# - integrity_sha256 hashes the full canonical event object after excluding only integrity_sha256.
# The fixed JSONL fixture is an independent compatibility vector for these
# formulas. Supported-v1 optional fields participate in integrity hashing even
# though their original accepted line bytes are retained verbatim on disk.
review_runtime_build_event() {
  local run_id="$1"
  local review_key="$2"
  local repository="$3"
  local pr_number="$4"
  local base_sha="$5"
  local head_sha="$6"
  local config_hash="$7"
  local sequence="$8"
  local occurred_at="$9"
  local event_type="${10}"
  local payload="${11}"
  local canonical_payload payload_sha256 event_id without_integrity integrity_sha256

  canonical_payload="$(printf '%s' "$payload" | jq -S -c .)" || return
  payload_sha256="$(printf '%s' "$canonical_payload" | review_runtime_sha256)" || return
  event_id="$(printf '%s|%s|%s|%s' "$run_id" "$sequence" "$event_type" "$payload_sha256" | review_runtime_sha256)" || return
  without_integrity="$(jq -S -c -n \
    --arg schema 'kc-pr-flow.review-event/v1' \
    --arg event_id "$event_id" \
    --arg run_id "$run_id" \
    --arg review_key "$review_key" \
    --arg repository "$repository" \
    --argjson pr_number "$pr_number" \
    --arg base_sha "$base_sha" \
    --arg head_sha "$head_sha" \
    --arg config_hash "$config_hash" \
    --argjson sequence "$sequence" \
    --arg occurred_at "$occurred_at" \
    --arg event_type "$event_type" \
    --argjson payload "$canonical_payload" \
    --arg payload_sha256 "$payload_sha256" \
    '{schema:$schema,event_id:$event_id,run_id:$run_id,review_key:$review_key,repository:$repository,pr_number:$pr_number,base_sha:$base_sha,head_sha:$head_sha,config_hash:$config_hash,sequence:$sequence,occurred_at:$occurred_at,event_type:$event_type,payload:$payload,payload_sha256:$payload_sha256}')" || return
  integrity_sha256="$(printf '%s' "$without_integrity" | review_runtime_sha256)" || return
  printf '%s' "$without_integrity" | jq -S -c --arg integrity_sha256 "$integrity_sha256" '. + {integrity_sha256:$integrity_sha256}'
}

review_runtime_start() (
  local repository="$1"
  local pr_number="$2"
  local base_sha="$3"
  local head_sha="$4"
  local config_hash="$5"
  local occurred_at="$6"
  local predecessor_run_id="${7:-}"
  local successor_reason="${8:-}"
  local state_root repo_key repo_dir pr_dir temp_run_dir run_suffix run_id run_dir
  local review_key payload event rc

  review_runtime_require_jq || return
  review_runtime_validate_start_input "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" "$occurred_at" "$predecessor_run_id" "$successor_reason" || return

  umask 077
  state_root="$(review_runtime_prepare_state_root)" || return
  repo_key="$(review_runtime_repo_key "$repository")" || return
  repo_dir="$(review_runtime_prepare_child_directory "$state_root" "$repo_key")" || return
  pr_dir="$(review_runtime_prepare_child_directory "$repo_dir" "pr-$pr_number")" || return
  temp_run_dir="$(mktemp -d "$pr_dir/.run.XXXXXX")" || return
  review_runtime_real_directory "$temp_run_dir" || return 74
  trap '[ -z "$temp_run_dir" ] || review_runtime_remove_private_run "$temp_run_dir"' EXIT
  trap 'exit 129' HUP
  trap 'exit 130' INT
  trap 'exit 143' TERM
  run_suffix="${temp_run_dir##*.run.}"
  run_id="run-$run_suffix"
  run_dir="$pr_dir/$run_id"

  review_key="$(review_runtime_review_key "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash")" || {
    review_runtime_remove_private_run "$temp_run_dir"
    return 1
  }
  if [ -n "$predecessor_run_id" ]; then
    payload="$(jq -S -c -n --arg predecessor_run_id "$predecessor_run_id" --arg successor_reason "$successor_reason" '{predecessor_run_id:$predecessor_run_id,successor_reason:$successor_reason}')" || {
      review_runtime_remove_private_run "$temp_run_dir"
      return 1
    }
  else
    payload='{}'
  fi
  event="$(review_runtime_build_event "$run_id" "$review_key" "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" 1 "$occurred_at" run.started "$payload")" || {
    review_runtime_remove_private_run "$temp_run_dir"
    return 1
  }
  if ! printf '%s\n' "$event" >"$temp_run_dir/events.jsonl" ||
    ! review_runtime_validate_authoritative_log "$temp_run_dir/events.jsonl" >/dev/null; then
    review_runtime_remove_private_run "$temp_run_dir"
    return 74
  fi
  review_runtime_events_size_within_limit "$temp_run_dir/events.jsonl"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    review_runtime_remove_private_run "$temp_run_dir"
    return "$rc"
  fi
  if ! chmod 0600 "$temp_run_dir/events.jsonl" || ! chmod 0700 "$temp_run_dir"; then
    review_runtime_remove_private_run "$temp_run_dir"
    return 74
  fi
  if [ -e "$run_dir" ] || [ -L "$run_dir" ] || ! mv "$temp_run_dir" "$run_dir"; then
    review_runtime_remove_private_run "$temp_run_dir"
    return 74
  fi
  temp_run_dir=''
  printf '%s\n' "$event"
)

review_runtime_event_type_valid() {
  case "$1" in
    run.started | head.observed | lane.started | lane.finished | finding.observed | synthesis.finished | authorization.granted | post.intent | post.result | run.invalidated | run.finished)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# The event envelope is additive within v1, but payloads are closed at their
# owning event boundary. This prevents provider adapters from smuggling review
# authority or raw model/source content into the durable receipt.
review_runtime_payload_matches_v1_schema() {
  local line="$1"
  local event_type="$2"
  printf '%s' "$line" | jq -e --arg event_type "$event_type" '
    def exact_keys($required; $optional):
      ((keys - ($required + $optional)) | length) == 0 and
      (($required - keys) | length) == 0;
    def sha256: type == "string" and test("^[0-9a-f]{64}$");
    def sha1: type == "string" and test("^[0-9a-f]{40}$");
    def safe_token: type == "string" and test("^[a-z][a-z0-9._-]{0,63}$");
    def safe_metadata: type == "string" and length > 0 and length <= 128 and (test("[[:cntrl:]]") | not);
    def safe_path:
      type == "string" and length > 0 and length <= 1024 and
      (startswith("/") | not) and (endswith("/") | not) and (contains("//") | not) and
      (test("(^|/)\\.\\.?(/|$)|[[:cntrl:]\\\\]") | not);
    def nullable_token: . == null or safe_token;
    def positive_integer: type == "number" and floor == . and . > 0;
    def usage:
      type == "object" and
      exact_keys(["input_tokens","output_tokens","provenance","provider_family","scope","total_tokens"]; []) and
      (.provenance == "reported" or .provenance == "estimated" or .provenance == "unavailable") and
      (.scope == "lane" or .scope == "run") and
      (.provider_family == null or (.provider_family | safe_token)) and
      ([.input_tokens,.output_tokens,.total_tokens] | all(. == null or (type == "number" and floor == . and . >= 0))) and
      (if .provenance == "unavailable" then [.input_tokens,.output_tokens,.total_tokens] | all(. == null) else true end);
    def evidence:
      type == "object" and .schema == "kc-pr-flow.evidence-pointer/v1" and
      (.kind == "git_blob" or .kind == "pr_body" or .kind == "issue" or .kind == "review_comment" or .kind == "command" or .kind == "test") and
      (.repository | type == "string" and length > 0 and (test("[[:cntrl:]]") | not)) and
      (.object_sha | sha1) and (.content_sha256 | sha256) and
      if .kind == "git_blob" then
        exact_keys(["content_sha256","kind","line","locator","object_sha","path","repository","schema","side"]; []) and
        (.path | safe_path) and (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
        (.line == null or (.line | positive_integer)) and (.locator | nullable_token)
      elif .kind == "pr_body" then
        exact_keys(["content_sha256","kind","locator","object_sha","pr_number","repository","schema"]; []) and
        (.pr_number | positive_integer) and (.locator | safe_token)
      elif .kind == "issue" then
        exact_keys(["content_sha256","issue_number","kind","locator","object_sha","repository","schema"]; []) and
        (.issue_number | positive_integer) and (.locator | safe_token)
      elif .kind == "review_comment" then
        exact_keys(["comment_id","content_sha256","kind","line","locator","object_sha","path","pr_number","repository","schema","side"]; []) and
        (.pr_number | positive_integer) and (.comment_id | positive_integer) and (.path | safe_path) and
        (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
        (.line == null or (.line | positive_integer)) and (.locator | safe_token)
      else
        exact_keys(["content_sha256","kind","locator","object_sha","path","repository","schema"]; []) and
        (.path | safe_path) and (.locator | safe_token)
      end;
    def review_task:
      type == "object" and
      exact_keys(["base_sha","capability","config_hash","head_sha","lane_id","pr_number","repository","review_key","run_id","schema"]; ["provider_hint"]) and
      .schema == "kc-pr-flow.review-task/v1" and
      (.run_id | type == "string" and test("^run-[A-Za-z0-9._-]+$")) and
      (.review_key | sha256) and (.lane_id | safe_token) and (.capability | safe_token) and
      (.repository | type == "string" and length > 0) and (.pr_number | positive_integer) and
      (.base_sha | sha1) and (.head_sha | sha1) and (.config_hash | sha256) and
      ((has("provider_hint") | not) or (.provider_hint | safe_metadata));
    def lane_result:
      type == "object" and
      exact_keys(["candidates","capability","lane_id","review_key","run_id","schema","terminal_status","usage"]; ["provider_family"]) and
      .schema == "kc-pr-flow.lane-result/v1" and
      (.run_id | type == "string" and test("^run-[A-Za-z0-9._-]+$")) and
      (.review_key | sha256) and (.lane_id | safe_token) and (.capability | safe_token) and
      (.terminal_status == "succeeded" or .terminal_status == "failed" or .terminal_status == "unavailable") and
      (.candidates | type == "array" and all(sha256) and (unique | length) == length) and
      (.usage | usage) and
      ((has("provider_family") | not) or (.provider_family | safe_token));
    def candidate:
      type == "object" and
      exact_keys(["anchor_sha256","candidate_id","category","claim_key","evidence","lane_id","ordinal","path","review_key","run_id","schema","side"]; []) and
      .schema == "kc-pr-flow.review-candidate/v1" and (.candidate_id | sha256) and
      (.run_id | type == "string" and test("^run-[A-Za-z0-9._-]+$")) and (.review_key | sha256) and
      (.lane_id | safe_token) and (.ordinal | positive_integer) and (.path | safe_path) and
      (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
      (.anchor_sha256 | sha256) and (.category | safe_token) and (.claim_key | safe_token) and (.evidence | evidence);
    def finding:
      type == "object" and
      exact_keys(["anchor_sha256","candidate_ids","category","claim_key","evidence","finding_id","merge_key","path","review_key","schema","side"]; []) and
      .schema == "kc-pr-flow.review-finding/v1" and (.finding_id | sha256) and (.review_key | sha256) and
      (.merge_key | type == "string" and length > 0 and length <= 1400 and (test("[[:cntrl:]]") | not)) and
      (.path | safe_path) and (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
      (.anchor_sha256 | sha256) and (.category | safe_token) and (.claim_key | safe_token) and
      (.candidate_ids | type == "array" and length > 0 and all(sha256) and (unique | length) == length) and (.evidence | evidence);
    if $event_type == "run.started" then
      (.payload == {}) or ((.payload | keys | sort) == ["predecessor_run_id","successor_reason"])
    elif $event_type == "lane.started" then
      (.payload | exact_keys(["review_task"]; []) and (.review_task | review_task))
    elif $event_type == "lane.finished" then
      (.payload | exact_keys(["lane_result"]; []) and (.lane_result | lane_result))
    elif $event_type == "finding.observed" then
      (.payload | exact_keys(["candidate"]; []) and (.candidate | candidate))
    elif $event_type == "synthesis.finished" then
      (.payload | exact_keys(["findings","uncertain_candidate_ids"]; []) and
        (.findings | type == "array" and all(finding)) and
        (.uncertain_candidate_ids | type == "array" and all(sha256) and (unique | length) == length))
    else
      .payload == {}
    end' >/dev/null 2>&1
}

review_runtime_validate_t2_identity() {
  local line="$1"
  local event_type="$2"
  local expected actual run_id lane_id ordinal evidence_hash candidate_id
  local finding_count finding index merge_key finding_id
  case "$event_type" in
    lane.started)
      printf '%s' "$line" | jq -e '
        .payload.review_task as $task |
        [$task.run_id,$task.review_key,$task.repository,$task.pr_number,$task.base_sha,$task.head_sha,$task.config_hash]
        == [.run_id,.review_key,.repository,.pr_number,.base_sha,.head_sha,.config_hash]' >/dev/null 2>&1 || {
        printf '%s' 'provider_envelope_identity_mismatch'
        return 1
      }
      ;;
    lane.finished)
      printf '%s' "$line" | jq -e '
        .payload.lane_result as $result |
        [$result.run_id,$result.review_key] == [.run_id,.review_key] and
        ((($result | has("provider_family")) | not) or $result.provider_family == $result.usage.provider_family)' >/dev/null 2>&1 || {
        printf '%s' 'provider_envelope_identity_mismatch'
        return 1
      }
      ;;
    finding.observed)
      if ! printf '%s' "$line" | jq -e '
        .payload.candidate as $candidate |
        [$candidate.run_id,$candidate.review_key,$candidate.evidence.repository]
        == [.run_id,.review_key,.repository]' >/dev/null 2>&1; then
        printf '%s' 'candidate_identity_mismatch'
        return 1
      fi
      run_id="$(printf '%s' "$line" | jq -r '.run_id')"
      lane_id="$(printf '%s' "$line" | jq -r '.payload.candidate.lane_id')"
      ordinal="$(printf '%s' "$line" | jq -r '.payload.candidate.ordinal')"
      evidence_hash="$(printf '%s' "$line" | jq -r '.payload.candidate.evidence.content_sha256')"
      candidate_id="$(printf '%s|%s|%s|%s' "$run_id" "$lane_id" "$ordinal" "$evidence_hash" | review_runtime_sha256)" || return
      actual="$(printf '%s' "$line" | jq -r '.payload.candidate.candidate_id')"
      if [ "$actual" != "$candidate_id" ]; then
        printf '%s' 'candidate_id_mismatch'
        return 1
      fi
      ;;
    synthesis.finished)
      finding_count="$(printf '%s' "$line" | jq -r '.payload.findings | length')" || return
      index=0
      while [ "$index" -lt "$finding_count" ]; do
        finding="$(printf '%s' "$line" | jq -c --argjson index "$index" '.payload.findings[$index]')" || return
        if [ "$(printf '%s' "$finding" | jq -r '.review_key')" != "$(printf '%s' "$line" | jq -r '.review_key')" ] ||
          [ "$(printf '%s' "$finding" | jq -r '.evidence.repository')" != "$(printf '%s' "$line" | jq -r '.repository')" ]; then
          printf '%s' 'finding_identity_mismatch'
          return 1
        fi
        merge_key="$(printf '%s' "$finding" | jq -r '[.path,.side,.anchor_sha256,.category,.claim_key] | join("|")')" || return
        actual="$(printf '%s' "$finding" | jq -r '.merge_key')"
        if [ "$actual" != "$merge_key" ]; then
          printf '%s' 'merge_key_mismatch'
          return 1
        fi
        expected="$(printf '%s|%s' "$(printf '%s' "$line" | jq -r '.review_key')" "$merge_key" | review_runtime_sha256)" || return
        finding_id="$(printf '%s' "$finding" | jq -r '.finding_id')"
        if [ "$finding_id" != "$expected" ]; then
          printf '%s' 'finding_id_mismatch'
          return 1
        fi
        index=$((index + 1))
      done
      ;;
  esac
}

review_runtime_validate_line() {
  local line="$1"
  local required field schema event_type run_id review_key repository pr_number
  local base_sha head_sha config_hash sequence occurred_at payload payload_sha256
  local expected_payload_sha256 expected_event_id expected_review_key
  local without_integrity expected_integrity_sha256 integrity_sha256
  local has_predecessor has_reason predecessor_run_id successor_reason reason

  review_runtime_require_jq || return
  if ! printf '%s' "$line" | jq -e 'type == "object"' >/dev/null 2>&1; then
    printf '%s' 'invalid_json'
    return 1
  fi

  required='schema event_id run_id review_key repository pr_number base_sha head_sha config_hash sequence occurred_at event_type payload payload_sha256 integrity_sha256'
  for field in $required; do
    if ! printf '%s' "$line" | jq -e --arg field "$field" 'has($field)' >/dev/null 2>&1; then
      printf '%s' 'missing_required_field'
      return 1
    fi
  done

  schema="$(printf '%s' "$line" | jq -r '.schema')"
  if [ "$schema" != 'kc-pr-flow.review-event/v1' ]; then
    case "$schema" in
      kc-pr-flow.review-event/v*) printf '%s' 'unsupported_schema_major' ;;
      *) printf '%s' 'invalid_schema' ;;
    esac
    return 1
  fi

  if ! printf '%s' "$line" | jq -e '
    (.schema | type == "string") and
    (.event_id | type == "string") and
    (.run_id | type == "string") and
    (.review_key | type == "string") and
    (.repository | type == "string" and length > 0) and
    (.pr_number | type == "number" and (floor == .) and . > 0) and
    (.base_sha | type == "string") and
    (.head_sha | type == "string") and
    (.config_hash | type == "string") and
    (.sequence | type == "number" and (floor == .) and . > 0) and
    (.occurred_at | type == "string") and
    (.event_type | type == "string") and
    (.payload | type == "object") and
    (.payload_sha256 | type == "string") and
    (.integrity_sha256 | type == "string")' >/dev/null 2>&1; then
    printf '%s' 'invalid_field_type'
    return 1
  fi

  run_id="$(printf '%s' "$line" | jq -r '.run_id')"
  review_key="$(printf '%s' "$line" | jq -r '.review_key')"
  repository="$(printf '%s' "$line" | jq -r '.repository')"
  pr_number="$(printf '%s' "$line" | jq -r '.pr_number')"
  base_sha="$(printf '%s' "$line" | jq -r '.base_sha')"
  head_sha="$(printf '%s' "$line" | jq -r '.head_sha')"
  config_hash="$(printf '%s' "$line" | jq -r '.config_hash')"
  sequence="$(printf '%s' "$line" | jq -r '.sequence')"
  occurred_at="$(printf '%s' "$line" | jq -r '.occurred_at')"
  event_type="$(printf '%s' "$line" | jq -r '.event_type')"
  payload_sha256="$(printf '%s' "$line" | jq -r '.payload_sha256')"
  integrity_sha256="$(printf '%s' "$line" | jq -r '.integrity_sha256')"

  if ! [[ "$run_id" =~ ^run-[A-Za-z0-9._-]+$ ]] ||
    ! [[ "$review_key" =~ ^[0-9a-f]{64}$ ]] ||
    ! [[ "$base_sha" =~ ^[0-9a-f]{40}$ ]] ||
    ! [[ "$head_sha" =~ ^[0-9a-f]{40}$ ]] ||
    ! [[ "$config_hash" =~ ^[0-9a-f]{64}$ ]] ||
    ! [[ "$payload_sha256" =~ ^[0-9a-f]{64}$ ]] ||
    ! [[ "$integrity_sha256" =~ ^[0-9a-f]{64}$ ]] ||
    ! [[ "$occurred_at" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?Z$ ]]; then
    printf '%s' 'invalid_field_value'
    return 1
  fi
  if ! review_runtime_repository_identity_valid "$repository"; then
    printf '%s' 'invalid_repository_identity'
    return 1
  fi
  if ! review_runtime_event_type_valid "$event_type"; then
    printf '%s' 'unknown_event_type'
    return 1
  fi

  if ! review_runtime_payload_matches_v1_schema "$line" "$event_type"; then
    printf '%s' 'unsupported_payload_schema'
    return 1
  fi

  if [ "$event_type" = 'run.started' ]; then
    has_predecessor="$(printf '%s' "$line" | jq -r '.payload | has("predecessor_run_id")')"
    has_reason="$(printf '%s' "$line" | jq -r '.payload | has("successor_reason")')"
    if [ "$has_predecessor" != "$has_reason" ]; then
      printf '%s' 'incomplete_successor_metadata'
      return 1
    fi
    if [ "$has_predecessor" = 'true' ]; then
      predecessor_run_id="$(printf '%s' "$line" | jq -r '.payload.predecessor_run_id')"
      successor_reason="$(printf '%s' "$line" | jq -r '.payload.successor_reason')"
      if ! [[ "$predecessor_run_id" =~ ^run-[A-Za-z0-9._-]+$ ]]; then
        printf '%s' 'invalid_predecessor_run_id'
        return 1
      fi
      if [ "$predecessor_run_id" = "$run_id" ]; then
        printf '%s' 'self_predecessor_run_id'
        return 1
      fi
      if ! review_runtime_successor_reason_valid "$successor_reason"; then
        printf '%s' 'invalid_successor_reason'
        return 1
      fi
    fi
  fi

  if ! reason="$(review_runtime_validate_t2_identity "$line" "$event_type")"; then
    printf '%s' "$reason"
    return 1
  fi

  payload="$(printf '%s' "$line" | jq -S -c '.payload')" || return
  expected_payload_sha256="$(printf '%s' "$payload" | review_runtime_sha256)" || return
  if [ "$payload_sha256" != "$expected_payload_sha256" ]; then
    printf '%s' 'payload_hash_mismatch'
    return 1
  fi

  expected_event_id="$(printf '%s|%s|%s|%s' "$run_id" "$sequence" "$event_type" "$payload_sha256" | review_runtime_sha256)" || return
  if [ "$(printf '%s' "$line" | jq -r '.event_id')" != "$expected_event_id" ]; then
    printf '%s' 'event_id_mismatch'
    return 1
  fi

  expected_review_key="$(review_runtime_review_key "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash")" || return
  if [ "$review_key" != "$expected_review_key" ]; then
    printf '%s' 'review_key_mismatch'
    return 1
  fi

  without_integrity="$(printf '%s' "$line" | jq -S -c 'del(.integrity_sha256)')" || return
  expected_integrity_sha256="$(printf '%s' "$without_integrity" | review_runtime_sha256)" || return
  if [ "$integrity_sha256" != "$expected_integrity_sha256" ]; then
    printf '%s' 'integrity_hash_mismatch'
    return 1
  fi
}

review_runtime_same_run_identity() {
  jq -e -n --argjson authority "$1" --argjson candidate "$2" '
    [$authority.repository,$authority.pr_number,$authority.base_sha,$authority.head_sha,$authority.config_hash,$authority.review_key,$authority.run_id]
    ==
    [$candidate.repository,$candidate.pr_number,$candidate.base_sha,$candidate.head_sha,$candidate.config_hash,$candidate.review_key,$candidate.run_id]' >/dev/null 2>&1
}

review_runtime_validate_authoritative_log() {
  local events_file="$1"
  local line reason authority_line='' sequence expected_sequence=1 count=0
  [ -f "$events_file" ] && [ ! -L "$events_file" ] || return 74
  while IFS= read -r line || [ -n "$line" ]; do
    count=$((count + 1))
    if ! reason="$(review_runtime_validate_line "$line")"; then
      printf 'review-runtime: existing event %s failed validation: %s\n' "$count" "$reason" >&2
      return 74
    fi
    sequence="$(printf '%s' "$line" | jq -r '.sequence')"
    if [ "$sequence" != "$expected_sequence" ]; then
      printf 'review-runtime: existing event sequence is not contiguous at %s\n' "$count" >&2
      return 74
    fi
    if [ "$count" -eq 1 ]; then
      if [ "$(printf '%s' "$line" | jq -r '.event_type')" != 'run.started' ] || [ "$sequence" != '1' ]; then
        printf 'review-runtime: existing log has no authoritative run start\n' >&2
        return 74
      fi
      authority_line="$line"
    elif ! review_runtime_same_run_identity "$authority_line" "$line"; then
      printf 'review-runtime: existing log contains mixed run identity\n' >&2
      return 74
    fi
    expected_sequence=$((expected_sequence + 1))
  done <"$events_file"
  [ "$count" -gt 0 ] || return 74
  printf '%s\n' "$count"
}

review_runtime_file_mode() {
  if stat -f '%Lp' "$1" >/dev/null 2>&1; then
    stat -f '%Lp' "$1"
  else
    stat -c '%a' "$1"
  fi
}

review_runtime_quarantine_complete() {
  local quarantine_dir="$1"
  local line="$2"
  local reason="$3"
  local line_sha="$4"
  local expected_event_file_sha actual_event_file_sha

  [ -d "$quarantine_dir" ] && [ ! -L "$quarantine_dir" ] || return 1
  [ -f "$quarantine_dir/event.jsonl" ] && [ ! -L "$quarantine_dir/event.jsonl" ] || return 1
  [ -f "$quarantine_dir/metadata.json" ] && [ ! -L "$quarantine_dir/metadata.json" ] || return 1
  [ "$(review_runtime_file_mode "$quarantine_dir")" = '500' ] || return 1
  [ "$(review_runtime_file_mode "$quarantine_dir/event.jsonl")" = '400' ] || return 1
  [ "$(review_runtime_file_mode "$quarantine_dir/metadata.json")" = '400' ] || return 1

  expected_event_file_sha="$(printf '%s\n' "$line" | review_runtime_sha256)" || return
  actual_event_file_sha="$(review_runtime_sha256 <"$quarantine_dir/event.jsonl")" || return
  [ "$expected_event_file_sha" = "$actual_event_file_sha" ] || return 1
  jq -e \
    --arg reason "$reason" \
    --arg event_sha256 "$line_sha" \
    '.reason == $reason and
     .event_sha256 == $event_sha256 and
     (.quarantined_at | type == "string" and test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"))' \
    "$quarantine_dir/metadata.json" >/dev/null 2>&1
}

review_runtime_remove_quarantine_temp() {
  local temp_dir="$1"
  [ -d "$temp_dir" ] || return 0
  chmod 0700 "$temp_dir" 2>/dev/null || true
  chmod 0600 "$temp_dir/event.jsonl" "$temp_dir/metadata.json" 2>/dev/null || true
  rm -f "$temp_dir/event.jsonl" "$temp_dir/metadata.json"
  rmdir "$temp_dir" 2>/dev/null || true
}

review_runtime_quarantine_size_within_limit() {
  local event_file="$1"
  local metadata_file="$2"
  local limit="${KC_PR_FLOW_MAX_QUARANTINE_BYTES:-4194304}"
  local event_size metadata_size total_size
  [[ "$limit" =~ ^[1-9][0-9]*$ ]] || {
    printf 'review-runtime: invalid quarantine size limit\n' >&2
    return 73
  }
  event_size="$(wc -c <"$event_file" | tr -d ' ')" || return
  metadata_size="$(wc -c <"$metadata_file" | tr -d ' ')" || return
  total_size=$((event_size + metadata_size))
  if [ "$total_size" -gt "$limit" ]; then
    printf 'review-runtime: quarantine size limit exceeded (%s > %s)\n' "$total_size" "$limit" >&2
    return 73
  fi
}

review_runtime_quarantine() (
  local line="$1"
  local reason="$2"
  local state_root line_sha quarantine_root quarantine_dir quarantine_lock
  local temp_dir='' metadata lock_owner_pid rc

  case "$reason" in
    *[!a-z0-9_]*) reason='validation_failed' ;;
  esac
  state_root="$(review_runtime_prepare_state_root)" || return
  line_sha="$(printf '%s' "$line" | review_runtime_sha256)" || return
  quarantine_root="$(review_runtime_prepare_child_directory "$state_root" quarantine)" || return
  quarantine_dir="$quarantine_root/$line_sha-$reason"
  quarantine_lock="$quarantine_root/.$line_sha-$reason.lock"
  umask 077
  REVIEW_RUNTIME_LOCK_OWNER_PID=''
  if ! review_runtime_acquire_owned_lock "$quarantine_lock"; then
    return 75
  fi
  lock_owner_pid="$REVIEW_RUNTIME_LOCK_OWNER_PID"
  trap '[ -z "$temp_dir" ] || review_runtime_remove_quarantine_temp "$temp_dir"; review_runtime_release_owned_lock "$quarantine_lock" "$lock_owner_pid"' EXIT
  trap 'exit 129' HUP
  trap 'exit 130' INT
  trap 'exit 143' TERM

  if [ -e "$quarantine_dir" ] || [ -L "$quarantine_dir" ]; then
    if review_runtime_quarantine_complete "$quarantine_dir" "$line" "$reason" "$line_sha"; then
      return 0
    fi
    return 74
  fi

  temp_dir="$(mktemp -d "$quarantine_root/.$line_sha-$reason.tmp.XXXXXX")" || {
    return 1
  }
  if ! printf '%s\n' "$line" >"$temp_dir/event.jsonl"; then
    return 1
  fi
  metadata="$(jq -S -c -n \
    --arg reason "$reason" \
    --arg event_sha256 "$line_sha" \
    --arg quarantined_at "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    '{reason:$reason,event_sha256:$event_sha256,quarantined_at:$quarantined_at}')" || {
    return 1
  }
  if ! printf '%s\n' "$metadata" >"$temp_dir/metadata.json"; then
    return 1
  fi
  review_runtime_quarantine_size_within_limit "$temp_dir/event.jsonl" "$temp_dir/metadata.json"
  rc=$?
  [ "$rc" -eq 0 ] || return "$rc"
  if ! chmod 0400 "$temp_dir/event.jsonl" "$temp_dir/metadata.json" ||
    ! chmod 0500 "$temp_dir"; then
    return 1
  fi
  if [ -e "$quarantine_dir" ] || [ -L "$quarantine_dir" ]; then
    return 74
  fi
  if ! mv "$temp_dir" "$quarantine_dir"; then
    return 1
  fi
  temp_dir=''
  if ! review_runtime_quarantine_complete "$quarantine_dir" "$line" "$reason" "$line_sha"; then
    return 74
  fi
)

review_runtime_release_owned_lock() {
  local lock_dir="$1"
  local expected_pid="$2"
  local actual_pid
  review_runtime_real_directory "$lock_dir" || return 0
  [ -f "$lock_dir/owner.pid" ] && [ ! -L "$lock_dir/owner.pid" ] || return 0
  actual_pid="$(cat "$lock_dir/owner.pid" 2>/dev/null)" || return 0
  [ "$actual_pid" = "$expected_pid" ] || return 0
  rm -f "$lock_dir/owner.pid"
  rmdir "$lock_dir" 2>/dev/null || true
}

review_runtime_acquire_owned_lock() {
  local lock_dir="$1"
  local attempt=0 owner_file owner_pid owner_count current_pid owner_temp ps_output

  while [ "$attempt" -le 1 ]; do
    if mkdir "$lock_dir" 2>/dev/null; then
      review_runtime_real_directory "$lock_dir" || return 75
      owner_temp="$(mktemp "$lock_dir/.owner.XXXXXX")" || {
        rmdir "$lock_dir" 2>/dev/null || true
        return 75
      }
      if ! sh -c 'printf "%s\n" "$PPID"' >"$owner_temp"; then
        rm -f "$owner_temp"
        rmdir "$lock_dir" 2>/dev/null || true
        return 75
      fi
      current_pid="$(cat "$owner_temp")" || {
        rm -f "$owner_temp"
        rmdir "$lock_dir" 2>/dev/null || true
        return 75
      }
      if ! [[ "$current_pid" =~ ^[1-9][0-9]*$ ]] || ! chmod 0600 "$owner_temp" || ! mv "$owner_temp" "$lock_dir/owner.pid"; then
        rm -f "$owner_temp"
        rmdir "$lock_dir" 2>/dev/null || true
        return 75
      fi
      REVIEW_RUNTIME_LOCK_OWNER_PID="$current_pid"
      return 0
    fi

    [ "$attempt" -eq 0 ] || return 75
    review_runtime_real_directory "$lock_dir" || return 75
    owner_file="$lock_dir/owner.pid"
    [ -f "$owner_file" ] && [ ! -L "$owner_file" ] || return 75
    owner_count="$(find "$lock_dir" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')" || return 75
    [ "$owner_count" = '1' ] || return 75
    [ "$(wc -l <"$owner_file" | tr -d ' ')" = '1' ] || return 75
    owner_pid="$(cat "$owner_file")" || return 75
    [[ "$owner_pid" =~ ^[1-9][0-9]*$ ]] || return 75
    if kill -0 "$owner_pid" 2>/dev/null; then
      return 75
    fi
    command -v ps >/dev/null 2>&1 || return 75
    ps_output="$(ps -p "$owner_pid" -o pid= 2>/dev/null || true)"
    [ -z "$ps_output" ] || return 75
    rm -f "$owner_file" || return 75
    rmdir "$lock_dir" 2>/dev/null || return 75
    attempt=$((attempt + 1))
  done
  return 75
}

review_runtime_acquire_run_reservation() {
  local lock_dir="$1"
  local attempts=0
  local max_attempts="${KC_PR_FLOW_RESERVATION_WAIT_ATTEMPTS:-120}"
  [[ "$max_attempts" =~ ^[1-9][0-9]*$ ]] || return 75
  while [ "$attempts" -lt "$max_attempts" ]; do
    if review_runtime_acquire_owned_lock "$lock_dir"; then
      return 0
    fi
    attempts=$((attempts + 1))
    [ "$attempts" -lt "$max_attempts" ] && sleep 0.05
  done
  return 75
}

review_runtime_append_line() (
  local line="$1"
  local reason repository pr_number run_id event_type sequence repo_key
  local state_root repo_dir pr_dir run_dir events_file lock_dir lock_owner_pid=''
  local existing_line existing_id existing_integrity event_id integrity_sha256
  local authority_line last_sequence expected_sequence duplicate_integrity=''
  local temp_events='' temp_run_dir='' rc

  if ! reason="$(review_runtime_validate_line "$line")"; then
    review_runtime_quarantine "$line" "$reason" || return
    printf '%s\n' 'quarantined'
    return 1
  fi

  repository="$(printf '%s' "$line" | jq -r '.repository')"
  pr_number="$(printf '%s' "$line" | jq -r '.pr_number')"
  run_id="$(printf '%s' "$line" | jq -r '.run_id')"
  event_type="$(printf '%s' "$line" | jq -r '.event_type')"
  sequence="$(printf '%s' "$line" | jq -r '.sequence')"
  event_id="$(printf '%s' "$line" | jq -r '.event_id')"
  integrity_sha256="$(printf '%s' "$line" | jq -r '.integrity_sha256')"
  umask 077
  state_root="$(review_runtime_prepare_state_root)" || return
  repo_key="$(review_runtime_repo_key "$repository")" || return
  repo_dir="$(review_runtime_prepare_child_directory "$state_root" "$repo_key")" || return
  pr_dir="$(review_runtime_prepare_child_directory "$repo_dir" "pr-$pr_number")" || return
  run_dir="$pr_dir/$run_id"
  events_file="$run_dir/events.jsonl"
  lock_dir="$pr_dir/.reservation-$run_id.lock"
  REVIEW_RUNTIME_LOCK_OWNER_PID=''
  review_runtime_acquire_run_reservation "$lock_dir" || {
    printf 'review-runtime: run reservation busy for %s\n' "$run_id" >&2
    return 75
  }
  lock_owner_pid="$REVIEW_RUNTIME_LOCK_OWNER_PID"
  trap '[ -z "$temp_events" ] || rm -f "$temp_events"; [ -z "$temp_run_dir" ] || review_runtime_remove_private_run "$temp_run_dir"; review_runtime_release_owned_lock "$lock_dir" "$lock_owner_pid"' EXIT
  trap 'exit 129' HUP
  trap 'exit 130' INT
  trap 'exit 143' TERM

  if [ -e "$run_dir" ] || [ -L "$run_dir" ]; then
    run_dir="$(review_runtime_existing_child_directory "$pr_dir" "$run_id")" || return 74
    events_file="$run_dir/events.jsonl"

    if [ -L "$events_file" ] || [ ! -f "$events_file" ]; then
      printf 'review-runtime: unsafe events path for %s\n' "$run_id" >&2
      return 74
    fi
    last_sequence="$(review_runtime_validate_authoritative_log "$events_file")" || return 74
    authority_line="$(sed -n '1p' "$events_file")"
    if ! review_runtime_same_run_identity "$authority_line" "$line"; then
      review_runtime_quarantine "$line" 'run_identity_mismatch' || return
      printf '%s\n' 'quarantined'
      return 1
    fi
    while IFS= read -r existing_line || [ -n "$existing_line" ]; do
      existing_id="$(printf '%s' "$existing_line" | jq -r '.event_id')"
      if [ "$existing_id" = "$event_id" ]; then
        duplicate_integrity="$(printf '%s' "$existing_line" | jq -r '.integrity_sha256')"
        break
      fi
    done <"$events_file"
    if [ -n "$duplicate_integrity" ]; then
      existing_integrity="$duplicate_integrity"
      if [ "$existing_integrity" = "$integrity_sha256" ]; then
        printf '%s\n' 'duplicate'
        return 0
      fi
      review_runtime_quarantine "$line" 'event_id_conflict' || return
      printf '%s\n' 'quarantined'
      return 1
    fi
    expected_sequence=$((last_sequence + 1))
    if [ "$sequence" != "$expected_sequence" ]; then
      review_runtime_quarantine "$line" 'event_sequence_conflict' || return
      printf '%s\n' 'quarantined'
      return 1
    fi

    temp_events="$(mktemp "$run_dir/.events.next.XXXXXX")" || return 74
    if ! cat "$events_file" >"$temp_events" || ! printf '%s\n' "$line" >>"$temp_events"; then
      return 74
    fi
    review_runtime_validate_authoritative_log "$temp_events" >/dev/null || return 74
    review_runtime_events_size_within_limit "$temp_events"
    rc=$?
    [ "$rc" -eq 0 ] || return "$rc"
    chmod 0600 "$temp_events" || return 74
    if [ -L "$events_file" ] || [ ! -f "$events_file" ] || ! mv -f "$temp_events" "$events_file"; then
      return 74
    fi
    temp_events=''
    printf '%s\n' 'appended'
    return 0
  fi

  if [ "$event_type" != 'run.started' ] || [ "$sequence" != '1' ]; then
    review_runtime_quarantine "$line" 'first_event_must_start_run' || return
    printf '%s\n' 'quarantined'
    return 1
  fi
  temp_run_dir="$(mktemp -d "$pr_dir/.run-new.XXXXXX")" || return 74
  review_runtime_real_directory "$temp_run_dir" || return 74
  if ! printf '%s\n' "$line" >"$temp_run_dir/events.jsonl" ||
    ! review_runtime_validate_authoritative_log "$temp_run_dir/events.jsonl" >/dev/null; then
    return 74
  fi
  review_runtime_events_size_within_limit "$temp_run_dir/events.jsonl"
  rc=$?
  [ "$rc" -eq 0 ] || return "$rc"
  chmod 0600 "$temp_run_dir/events.jsonl" || return 74
  chmod 0700 "$temp_run_dir" || return 74
  if [ -e "$run_dir" ] || [ -L "$run_dir" ] || ! mv "$temp_run_dir" "$run_dir"; then
    return 74
  fi
  temp_run_dir=''
  printf '%s\n' 'appended'
)

review_runtime_validate_file() {
  local event_file="$1"
  local line reason line_number=0 valid=0 invalid=0
  local input_file cleanup_file=''

  if [ "$event_file" = '-' ]; then
    input_file="$(mktemp)" || return
    cleanup_file="$input_file"
    cat >"$input_file" || {
      rm -f "$cleanup_file"
      return 1
    }
  else
    input_file="$event_file"
  fi
  if [ ! -f "$input_file" ] || [ -L "$input_file" ]; then
    printf 'review-runtime: event file is not a safe regular file: %s\n' "$event_file" >&2
    [ -n "$cleanup_file" ] && rm -f "$cleanup_file"
    return 2
  fi
  while IFS= read -r line || [ -n "$line" ]; do
    line_number=$((line_number + 1))
    if reason="$(review_runtime_validate_line "$line")"; then
      valid=$((valid + 1))
    else
      invalid=$((invalid + 1))
      printf 'review-runtime: line %s: %s\n' "$line_number" "$reason" >&2
    fi
  done <"$input_file"
  [ -n "$cleanup_file" ] && rm -f "$cleanup_file"
  jq -c -n --argjson valid "$valid" --argjson invalid "$invalid" '{valid:$valid,invalid:$invalid}'
  [ "$invalid" -eq 0 ]
}

review_runtime_append_file() {
  local event_file="$1"
  local input_file cleanup_file='' line status rc
  local appended=0 duplicate=0 quarantined=0 blocked=0 overall_rc=0

  if [ "$event_file" = '-' ]; then
    input_file="$(mktemp)" || return
    cleanup_file="$input_file"
    cat >"$input_file" || {
      rm -f "$cleanup_file"
      return 1
    }
  else
    input_file="$event_file"
  fi
  if [ ! -f "$input_file" ] || [ -L "$input_file" ]; then
    printf 'review-runtime: event file is not a safe regular file: %s\n' "$event_file" >&2
    [ -n "$cleanup_file" ] && rm -f "$cleanup_file"
    return 2
  fi
  while IFS= read -r line || [ -n "$line" ]; do
    status="$(review_runtime_append_line "$line")"
    rc=$?
    case "$status" in
      appended) appended=$((appended + 1)) ;;
      duplicate) duplicate=$((duplicate + 1)) ;;
      quarantined)
        quarantined=$((quarantined + 1))
        overall_rc=1
        ;;
      *)
        blocked=$((blocked + 1))
        [ "$rc" -eq 75 ] && overall_rc=75 || overall_rc=74
        ;;
    esac
  done <"$input_file"
  [ -n "$cleanup_file" ] && rm -f "$cleanup_file"
  jq -c -n \
    --argjson appended "$appended" \
    --argjson duplicate "$duplicate" \
    --argjson quarantined "$quarantined" \
    --argjson blocked "$blocked" \
    '{appended:$appended,duplicate:$duplicate,quarantined:$quarantined,blocked:$blocked}'
  return "$overall_rc"
}

review_runtime_evidence_pointer_valid() {
  jq -e '
    def exact_keys($required): (keys | sort) == ($required | sort);
    def sha256: type == "string" and test("^[0-9a-f]{64}$");
    def sha1: type == "string" and test("^[0-9a-f]{40}$");
    def safe_token: type == "string" and test("^[a-z][a-z0-9._-]{0,63}$");
    def safe_path:
      type == "string" and length > 0 and length <= 1024 and
      (startswith("/") | not) and (endswith("/") | not) and (contains("//") | not) and
      (test("(^|/)\\.\\.?(/|$)|[[:cntrl:]\\\\]") | not);
    def positive_integer: type == "number" and floor == . and . > 0;
    type == "object" and .schema == "kc-pr-flow.evidence-pointer/v1" and
    (.kind == "git_blob" or .kind == "pr_body" or .kind == "issue" or .kind == "review_comment" or .kind == "command" or .kind == "test") and
    (.repository | type == "string" and length > 0 and (test("[[:cntrl:]]") | not)) and
    (.object_sha | sha1) and (.content_sha256 | sha256) and
    if .kind == "git_blob" then
      exact_keys(["content_sha256","kind","line","locator","object_sha","path","repository","schema","side"]) and
      (.path | safe_path) and (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
      (.line == null or (.line | positive_integer)) and (.locator == null or (.locator | safe_token))
    elif .kind == "pr_body" then
      exact_keys(["content_sha256","kind","locator","object_sha","pr_number","repository","schema"]) and
      (.pr_number | positive_integer) and (.locator | safe_token)
    elif .kind == "issue" then
      exact_keys(["content_sha256","issue_number","kind","locator","object_sha","repository","schema"]) and
      (.issue_number | positive_integer) and (.locator | safe_token)
    elif .kind == "review_comment" then
      exact_keys(["comment_id","content_sha256","kind","line","locator","object_sha","path","pr_number","repository","schema","side"]) and
      (.pr_number | positive_integer) and (.comment_id | positive_integer) and (.path | safe_path) and
      (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
      (.line == null or (.line | positive_integer)) and (.locator | safe_token)
    else
      exact_keys(["content_sha256","kind","locator","object_sha","path","repository","schema"]) and
      (.path | safe_path) and (.locator | safe_token)
    end' "$1" >/dev/null 2>&1
}

review_runtime_github_repository_identity() {
  local repository_path="$1"
  local origin_url repository_identity
  origin_url="$(git -C "$repository_path" config --get remote.origin.url 2>/dev/null)" || return 1
  case "$origin_url" in
    https://github.com/*)
      repository_identity="${origin_url#https://github.com/}"
      ;;
    ssh://git@github.com/*)
      repository_identity="${origin_url#ssh://git@github.com/}"
      ;;
    git@github.com:*)
      repository_identity="${origin_url#git@github.com:}"
      ;;
    *)
      return 1
      ;;
  esac
  repository_identity="${repository_identity#/}"
  repository_identity="${repository_identity%.git}"
  [[ "$repository_identity" =~ ^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$ ]] || return 1
  printf '%s\n' "$repository_identity"
}

review_runtime_verify_evidence() (
  local pointer_file="$1"
  local repository_path="$2"
  local pointer_snapshot='' temp_file=''
  local pointer kind object_sha path expected_hash actual_hash
  local pointer_repository repository_identity object_type
  umask 077
  pointer_snapshot="$(mktemp)" || return
  trap '[ -z "$temp_file" ] || rm -f "$temp_file"; [ -z "$pointer_snapshot" ] || rm -f "$pointer_snapshot"' EXIT
  review_runtime_snapshot_regular_file "$pointer_file" "$pointer_snapshot" 'pointer JSON' || return
  review_runtime_evidence_pointer_valid "$pointer_snapshot" || {
    printf 'review-runtime: invalid evidence pointer\n' >&2
    return 2
  }
  pointer="$(jq -S -c . "$pointer_snapshot")" || return
  kind="$(printf '%s' "$pointer" | jq -r '.kind')"
  if [ "$kind" != 'git_blob' ]; then
    jq -S -c -n --arg kind "$kind" '{schema:"kc-pr-flow.evidence-verification/v1",status:"unavailable",kind:$kind,content_sha256:null}'
    return 3
  fi
  if [ ! -d "$repository_path" ] || [ -L "$repository_path" ] ||
    ! git -C "$repository_path" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf 'review-runtime: repository is not a safe local git worktree\n' >&2
    return 2
  fi
  pointer_repository="$(printf '%s' "$pointer" | jq -r '.repository')"
  repository_identity="$(review_runtime_github_repository_identity "$repository_path")" || {
    jq -S -c -n --arg kind "$kind" '{schema:"kc-pr-flow.evidence-verification/v1",status:"repository_unavailable",kind:$kind,content_sha256:null}'
    return 3
  }
  if [ "$repository_identity" != "$pointer_repository" ]; then
    jq -S -c -n --arg kind "$kind" '{schema:"kc-pr-flow.evidence-verification/v1",status:"repository_mismatch",kind:$kind,content_sha256:null}'
    return 1
  fi
  object_sha="$(printf '%s' "$pointer" | jq -r '.object_sha')"
  path="$(printf '%s' "$pointer" | jq -r '.path')"
  expected_hash="$(printf '%s' "$pointer" | jq -r '.content_sha256')"
  object_type="$(git -C "$repository_path" cat-file -t "$object_sha:$path" 2>/dev/null)" || {
    jq -S -c -n --arg kind "$kind" --arg expected "$expected_hash" '{schema:"kc-pr-flow.evidence-verification/v1",status:"unavailable",kind:$kind,content_sha256:$expected}'
    return 3
  }
  if [ "$object_type" != 'blob' ]; then
    jq -S -c -n --arg kind "$kind" --arg expected "$expected_hash" '{schema:"kc-pr-flow.evidence-verification/v1",status:"not_blob",kind:$kind,content_sha256:$expected}'
    return 3
  fi
  temp_file="$(mktemp)" || return
  if ! git -C "$repository_path" show "$object_sha:$path" >"$temp_file" 2>/dev/null; then
    jq -S -c -n --arg kind "$kind" --arg expected "$expected_hash" '{schema:"kc-pr-flow.evidence-verification/v1",status:"unavailable",kind:$kind,content_sha256:$expected}'
    return 3
  fi
  actual_hash="$(review_runtime_sha256 <"$temp_file")" || return
  rm -f "$temp_file"
  temp_file=''
  if [ "$actual_hash" != "$expected_hash" ]; then
    jq -S -c -n --arg kind "$kind" --arg expected "$expected_hash" --arg actual "$actual_hash" \
      '{schema:"kc-pr-flow.evidence-verification/v1",status:"hash_mismatch",kind:$kind,expected_content_sha256:$expected,actual_content_sha256:$actual}'
    return 1
  fi
  jq -S -c -n --arg kind "$kind" --arg content_sha256 "$actual_hash" \
    '{schema:"kc-pr-flow.evidence-verification/v1",status:"verified",kind:$kind,content_sha256:$content_sha256}'
)

review_runtime_usage_valid() {
  jq -e '
    type == "object" and
    (keys | sort) == ["input_tokens","output_tokens","provenance","provider_family","scope","total_tokens"] and
    (.provenance == "reported" or .provenance == "estimated" or .provenance == "unavailable") and
    (.scope == "lane" or .scope == "run") and
    (.provider_family == null or (.provider_family | type == "string" and test("^[a-z][a-z0-9._-]{0,63}$"))) and
    ([.input_tokens,.output_tokens,.total_tokens] | all(. == null or (type == "number" and floor == . and . >= 0))) and
    (if .provenance == "unavailable" then [.input_tokens,.output_tokens,.total_tokens] | all(. == null) else true end)' "$1" >/dev/null 2>&1
}

review_runtime_compare_usage() (
  local left_file="$1"
  local right_file="$2"
  local left_snapshot='' right_snapshot=''
  local left right usage_file comparable='false'
  umask 077
  left_snapshot="$(mktemp)" || return
  right_snapshot="$(mktemp)" || {
    rm -f "$left_snapshot"
    return 74
  }
  trap '[ -z "$left_snapshot" ] || rm -f "$left_snapshot"; [ -z "$right_snapshot" ] || rm -f "$right_snapshot"' EXIT
  review_runtime_snapshot_regular_file "$left_file" "$left_snapshot" 'left usage JSON' || return
  review_runtime_snapshot_regular_file "$right_file" "$right_snapshot" 'right usage JSON' || return
  for usage_file in "$left_snapshot" "$right_snapshot"; do
    review_runtime_usage_valid "$usage_file" || {
      printf 'review-runtime: invalid usage observation\n' >&2
      return 2
    }
  done
  left="$(jq -S -c . "$left_snapshot")" || return
  right="$(jq -S -c . "$right_snapshot")" || return
  if jq -e -n --argjson left "$left" --argjson right "$right" '
    $left.provenance == "reported" and $right.provenance == "reported" and
    $left.provider_family != null and $left.provider_family == $right.provider_family and
    $left.scope == $right.scope and
    all([$left.input_tokens,$left.output_tokens,$left.total_tokens,$right.input_tokens,$right.output_tokens,$right.total_tokens][]; . != null)' >/dev/null 2>&1; then
    comparable='true'
  fi
  if [ "$comparable" = 'true' ]; then
    jq -S -c -n --argjson left "$left" --argjson right "$right" '
      {schema:"kc-pr-flow.usage-comparison/v1",comparable:true,
       provider_family:$left.provider_family,scope:$left.scope,
       efficiency:{input_tokens_delta:($right.input_tokens-$left.input_tokens),output_tokens_delta:($right.output_tokens-$left.output_tokens),total_tokens_delta:($right.total_tokens-$left.total_tokens)}}'
  else
    jq -S -c -n '{schema:"kc-pr-flow.usage-comparison/v1",comparable:false,provider_family:null,scope:null,efficiency:null}'
  fi
)

review_runtime_replay() (
  local event_file="$1"
  local event_snapshot=''
  review_runtime_require_jq || return
  umask 077
  event_snapshot="$(mktemp)" || return
  trap '[ -z "$event_snapshot" ] || rm -f "$event_snapshot"' EXIT
  review_runtime_snapshot_regular_file "$event_file" "$event_snapshot" 'event file' || return
  review_runtime_validate_authoritative_log "$event_snapshot" >/dev/null || return
  if ! jq -e -s '
    reduce .[] as $event (
      {ok:true,synthesized:false,tasks:{},results:{},candidates:{}};
      if (.ok | not) then .
      elif .synthesized and
        ($event.event_type == "lane.started" or
         $event.event_type == "lane.finished" or
         $event.event_type == "finding.observed" or
         $event.event_type == "synthesis.finished") then
        .ok = false
      elif $event.event_type == "lane.started" then
        $event.payload.review_task as $task |
        if .tasks[$task.lane_id] != null then
          .ok = false
        else
          .tasks[$task.lane_id] = {capability:$task.capability,sequence:$event.sequence}
        end
      elif $event.event_type == "finding.observed" then
        $event.payload.candidate as $candidate |
        if .tasks[$candidate.lane_id] == null or
          .results[$candidate.lane_id] != null or
          .candidates[$candidate.candidate_id] != null then
          .ok = false
        else
          .candidates[$candidate.candidate_id] = {
            lane_id:$candidate.lane_id,
            sequence:$event.sequence,
            merge_key:([$candidate.path,$candidate.side,$candidate.anchor_sha256,$candidate.category,$candidate.claim_key] | join("|"))
          }
        end
      elif $event.event_type == "lane.finished" then
        $event.payload.lane_result as $result |
        ([.candidates | to_entries[] | select(.value.lane_id == $result.lane_id) | .key] | sort) as $observed_ids |
        ($result.candidates | sort) as $result_ids |
        if .tasks[$result.lane_id] == null or
          .results[$result.lane_id] != null or
          .tasks[$result.lane_id].capability != $result.capability or
          $observed_ids != $result_ids then
          .ok = false
        else
          .results[$result.lane_id] = {sequence:$event.sequence,candidate_ids:$result_ids}
        end
      elif $event.event_type == "synthesis.finished" then
        . as $state |
        ($event.payload.findings | map(.candidate_ids) | add // []) as $merged |
        $event.payload.findings as $findings |
        $event.payload.uncertain_candidate_ids as $uncertain |
        ($merged + $uncertain) as $combined |
        ($state.candidates | keys | sort) as $observed_ids |
        ($findings | map(.finding_id)) as $finding_ids |
        ($findings | map(.merge_key)) as $merge_keys |
        if
          (($combined | unique | length) != ($combined | length)) or
          (($combined | sort) != $observed_ids) or
          (($finding_ids | unique | length) != ($finding_ids | length)) or
          (($merge_keys | unique | length) != ($merge_keys | length)) or
          (all($combined[];
            . as $candidate_id | $state.candidates[$candidate_id] != null) | not) or
          (all($uncertain[];
            . as $candidate_id | ($merged | index($candidate_id)) == null) | not) or
          (all($findings[];
            . as $finding |
            all($finding.candidate_ids[];
              . as $candidate_id |
              $state.candidates[$candidate_id].merge_key == $finding.merge_key)) | not)
        then
          .ok = false
        else
          .synthesized = true
        end
      else . end
    ) | .ok' "$event_snapshot" >/dev/null 2>&1; then
    printf 'review-runtime: event relationships are inconsistent\n' >&2
    return 74
  fi
  jq -S -c -s '
    .[0] as $start |
    reduce .[1:][] as $event (
    {
      schema:"kc-pr-flow.review-projection/v1",
      run:{
        schema:$start.schema,
        run_id:$start.run_id,
        review_key:$start.review_key,
        repository:$start.repository,
        pr_number:$start.pr_number,
        base_sha:$start.base_sha,
        head_sha:$start.head_sha,
        config_hash:$start.config_hash
      },
      lanes:[],
      candidates:[],
      findings:[],
      uncertain_candidate_ids:[],
      usage_observations:[]
    };
      if $event.event_type == "lane.started" then
        .lanes += [{
          lane_id:$event.payload.review_task.lane_id,
          capability:$event.payload.review_task.capability,
          task:$event.payload.review_task,
          result:null
        }]
      elif $event.event_type == "lane.finished" then
        ($event.payload.lane_result) as $result |
        .lanes = [.lanes[] | if .lane_id == $result.lane_id then .result = $result else . end] |
        .usage_observations += [$result.usage]
      elif $event.event_type == "finding.observed" then
        .candidates += [$event.payload.candidate]
      elif $event.event_type == "synthesis.finished" then
        .findings = $event.payload.findings |
        .uncertain_candidate_ids = $event.payload.uncertain_candidate_ids
      else . end
    )' "$event_snapshot"
)

review_runtime_show() {
  local event_file="$1"
  local projection
  projection="$(review_runtime_replay "$event_file")" || return
  printf '%s' "$projection" | jq -S -c '
    {
      schema:"kc-pr-flow.review-summary/v1",
      run:.run,
      counts:{
        lanes:(.lanes | length),
        candidates:(.candidates | length),
        findings:(.findings | length),
        uncertain_candidates:(.uncertain_candidate_ids | length),
        usage_observations:(.usage_observations | length)
      }
    }'
}

review_runtime_main_event_file() {
  local operation="$1"
  shift
  local event_file=''
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --event-file)
        [ "$#" -ge 2 ] || {
          printf 'review-runtime: missing value for --event-file\n' >&2
          return 2
        }
        event_file="$2"
        shift 2
        ;;
      *)
        printf 'review-runtime: unknown %s option: %s\n' "$operation" "$1" >&2
        return 2
        ;;
    esac
  done
  [ -n "$event_file" ] || {
    printf 'review-runtime: --event-file is required\n' >&2
    return 2
  }
  case "$operation" in
    validate) review_runtime_validate_file "$event_file" ;;
    append) review_runtime_append_file "$event_file" ;;
    replay) review_runtime_replay "$event_file" ;;
    show) review_runtime_show "$event_file" ;;
  esac
}

review_runtime_main_verify_evidence() {
  local pointer_json=''
  local repository_path=''
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --pointer-json | --repo)
        [ "$#" -ge 2 ] || {
          printf 'review-runtime: missing value for %s\n' "$1" >&2
          return 2
        }
        case "$1" in
          --pointer-json) pointer_json="$2" ;;
          --repo) repository_path="$2" ;;
        esac
        shift 2
        ;;
      *)
        printf 'review-runtime: unknown verify-evidence option: %s\n' "$1" >&2
        return 2
        ;;
    esac
  done
  [ -n "$pointer_json" ] && [ -n "$repository_path" ] || {
    printf 'review-runtime: --pointer-json and --repo are required\n' >&2
    return 2
  }
  review_runtime_verify_evidence "$pointer_json" "$repository_path"
}

review_runtime_main_compare_usage() {
  local left_json=''
  local right_json=''
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --left-json | --right-json)
        [ "$#" -ge 2 ] || {
          printf 'review-runtime: missing value for %s\n' "$1" >&2
          return 2
        }
        case "$1" in
          --left-json) left_json="$2" ;;
          --right-json) right_json="$2" ;;
        esac
        shift 2
        ;;
      *)
        printf 'review-runtime: unknown compare-usage option: %s\n' "$1" >&2
        return 2
        ;;
    esac
  done
  [ -n "$left_json" ] && [ -n "$right_json" ] || {
    printf 'review-runtime: --left-json and --right-json are required\n' >&2
    return 2
  }
  review_runtime_compare_usage "$left_json" "$right_json"
}

review_runtime_usage() {
  printf '%s\n' 'usage: review-runtime.sh {start ...|validate --event-file FILE|append --event-file FILE|replay --event-file FILE|show --event-file FILE|verify-evidence ...|compare-usage ...}' >&2
}

review_runtime_main_start() {
  local repository='' pr_number='' base_sha='' head_sha='' config_hash=''
  local occurred_at='' predecessor_run_id='' successor_reason=''

  while [ "$#" -gt 0 ]; do
    case "$1" in
      --repo | --pr | --base | --head | --config-hash | --occurred-at | --predecessor-run-id | --successor-reason)
        [ "$#" -ge 2 ] || {
          printf 'review-runtime: missing value for %s\n' "$1" >&2
          return 2
        }
        case "$1" in
          --repo) repository="$2" ;;
          --pr) pr_number="$2" ;;
          --base) base_sha="$2" ;;
          --head) head_sha="$2" ;;
          --config-hash) config_hash="$2" ;;
          --occurred-at) occurred_at="$2" ;;
          --predecessor-run-id) predecessor_run_id="$2" ;;
          --successor-reason) successor_reason="$2" ;;
        esac
        shift 2
        ;;
      *)
        printf 'review-runtime: unknown start option: %s\n' "$1" >&2
        return 2
        ;;
    esac
  done

  if [ -z "$occurred_at" ]; then
    occurred_at="$(date -u '+%Y-%m-%dT%H:%M:%SZ')" || return
  fi
  review_runtime_start "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" "$occurred_at" "$predecessor_run_id" "$successor_reason"
}

review_runtime_main() {
  local command="${1:-}"
  [ "$#" -gt 0 ] && shift
  case "$command" in
    start) review_runtime_main_start "$@" ;;
    validate | append | replay | show) review_runtime_main_event_file "$command" "$@" ;;
    verify-evidence) review_runtime_main_verify_evidence "$@" ;;
    compare-usage) review_runtime_main_compare_usage "$@" ;;
    *)
      review_runtime_usage
      return 2
      ;;
  esac
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  review_runtime_main "$@"
fi
