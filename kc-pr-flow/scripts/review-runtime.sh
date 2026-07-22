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

# T1 payloads are closed until their owning phase introduces a typed schema.
# run.started accepts either {} or exactly the predecessor_run_id +
# successor_reason pair. Every other recognized event type accepts {} only.
# Supported-v1 unknown optional *envelope* fields remain valid and are retained
# byte-for-byte; this incremental boundary does not pre-admit T2 evidence,
# provider, finding, lane, or replay payloads.
review_runtime_payload_matches_t1_schema() {
  local line="$1"
  local event_type="$2"
  if [ "$event_type" = 'run.started' ]; then
    printf '%s' "$line" | jq -e '
      (.payload == {}) or
      ((.payload | keys | sort) == ["predecessor_run_id","successor_reason"])' >/dev/null 2>&1
  else
    printf '%s' "$line" | jq -e '.payload == {}' >/dev/null 2>&1
  fi
}

review_runtime_validate_line() {
  local line="$1"
  local required field schema event_type run_id review_key repository pr_number
  local base_sha head_sha config_hash sequence occurred_at payload payload_sha256
  local expected_payload_sha256 expected_event_id expected_review_key
  local without_integrity expected_integrity_sha256 integrity_sha256
  local has_predecessor has_reason predecessor_run_id successor_reason

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

  if ! review_runtime_payload_matches_t1_schema "$line" "$event_type"; then
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
  esac
}

review_runtime_usage() {
  printf '%s\n' 'usage: review-runtime.sh {start ...|validate --event-file FILE|append --event-file FILE}' >&2
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
    validate | append) review_runtime_main_event_file "$command" "$@" ;;
    *)
      review_runtime_usage
      return 2
      ;;
  esac
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  review_runtime_main "$@"
fi
