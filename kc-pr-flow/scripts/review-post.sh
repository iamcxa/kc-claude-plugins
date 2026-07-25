#!/usr/bin/env bash
# Once-only GitHub review posting with crash-safe resume (increment 2.3).
#
# This is the ONLY kc-pr-flow component with posting / reconcile / network
# authority. review-runtime.sh stays network-free: it records and replays the
# five reserved receipt events but never posts. All GitHub mutation here is
# routed through an injectable transport (KC_PR_FLOW_POST_TRANSPORT), so CI can
# drive the exactly-once fault path against a recorded stub with no real PR
# mutation.
#
# Protocol (durable-before-mutate, reconcile-before-retry):
#   run.started -> head.observed -> authorization.granted -> post.intent
#     -> POST -> post.result{posted|failed}            (definite outcomes)
#     -> [ambiguous POST leaves the pending payload durable, no blind retry]
#   resume: GET reviews, match the embedded idempotency marker; a landed review
#     reconciles to post.result{posted_reconciled} with NO second POST.
#   A moved head or changed payload emits run.invalidated and never posts the
#   stale payload.
#
# Rollback / default-deny: KC_PR_FLOW_ONCE_ONLY_POST (default off) gates only
# `post` (fresh authorization + intent). Absence denies EVERY caller -- daemon
# or interactive alike, since neither sets it -- so "the daemon never takes
# the new posting path" holds by default with no daemon-specific code. `resume`
# and `gc` are never gated: rollback must never block reconciling or expiring
# evidence from a POST made while the flag was on.
set -uo pipefail

REVIEW_POST_MARKER_PREFIX='<!-- kc-pr-flow-post-receipt:'
REVIEW_POST_MARKER_SUFFIX='-->'
REVIEW_POST_DEFAULT_RETENTION_SECONDS=604800
# GitHub's review list is read-after-write eventually consistent: a review that
# just landed can be missing from `GET .../reviews` for a short window. Inside
# that window an absent marker proves nothing, so a retry must wait it out.
REVIEW_POST_DEFAULT_RECONCILE_CONFIRM_SECONDS=60

review_post_source_runtime() {
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || return 69
  # shellcheck source=/dev/null
  . "$here/review-runtime.sh" || return 69
}

review_post_now_utc() {
  date -u +%Y-%m-%dT%H:%M:%SZ
}

review_post_now_epoch() {
  date -u +%s
}

review_post_rfc3339_to_epoch() {
  local value="$1"
  python3 - "$value" <<'PY'
import datetime
import sys

value = sys.argv[1]
try:
    parsed = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
except ValueError:
    sys.exit(2)
parsed = parsed.replace(tzinfo=datetime.timezone.utc)
print(int(parsed.timestamp()))
PY
}

review_post_epoch_to_rfc3339() {
  local epoch="$1"
  python3 - "$epoch" <<'PY'
import datetime
import sys

try:
    epoch = int(sys.argv[1])
except ValueError:
    sys.exit(2)
moment = datetime.datetime.fromtimestamp(epoch, tz=datetime.timezone.utc)
print(moment.strftime("%Y-%m-%dT%H:%M:%SZ"))
PY
}

# The transport is the sole network boundary. A test injects a recorded stub;
# production defaults to a thin `gh` adapter. Ops: `head`, `list`, `post`.
review_post_transport() {
  local op="$1"
  shift
  local transport="${KC_PR_FLOW_POST_TRANSPORT:-}"
  if [ -n "$transport" ]; then
    if [ ! -x "$transport" ]; then
      printf 'review-post: transport is not executable: %s\n' "$transport" >&2
      return 69
    fi
    "$transport" "$op" "$@"
    return
  fi
  review_post_gh_transport "$op" "$@"
}

# Default production adapter. Never exercised by CI (network-free); the stub
# transport replaces it there.
review_post_gh_transport() {
  local op="$1"
  shift
  local repo='' pr=''
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --repo) repo="$2"; shift 2 ;;
      --pr) pr="$2"; shift 2 ;;
      # --self is part of the shared transport CLI (the stub uses it); the gh
      # adapter doesn't need it since the caller filters `list` by self login.
      --self) shift 2 ;;
      *) shift ;;
    esac
  done
  command -v gh >/dev/null 2>&1 || {
    printf 'review-post: gh CLI is unavailable for the default transport\n' >&2
    return 69
  }
  case "$op" in
    head)
      local head_sha
      head_sha="$(gh api "repos/$repo/pulls/$pr" --jq '.head.sha')" || return 74
      jq -cn --arg h "$head_sha" '{head_sha:$h}'
      ;;
    list)
      local reviews
      reviews="$(gh api "repos/$repo/pulls/$pr/reviews" --paginate \
        --jq '[.[] | {id, user: .user.login, body, commit_id}]')" || return 74
      jq -cn --argjson reviews "$reviews" '{reviews:$reviews}'
      ;;
    post)
      local body_json response remote_id
      body_json="$(cat)"
      local tmp
      tmp="$(mktemp)" || return 74
      printf '%s' "$body_json" >"$tmp"
      if response="$(gh api "repos/$repo/pulls/$pr/reviews" --method POST --input "$tmp" 2>/dev/null)"; then
        remote_id="$(jq -r '.id' <<<"$response")"
        rm -f "$tmp"
        jq -cn --argjson id "$remote_id" '{http_status:201,remote_review_id:$id}'
      else
        rm -f "$tmp"
        jq -cn '{http_status:0,remote_review_id:null}'
      fi
      ;;
    *)
      printf 'review-post: unknown transport op %s\n' "$op" >&2
      return 2
      ;;
  esac
}

review_post_marker() {
  printf '%s %s %s' "$REVIEW_POST_MARKER_PREFIX" "$1" "$REVIEW_POST_MARKER_SUFFIX"
}

review_post_body_with_marker() {
  local body="$1" idempotency_key="$2"
  printf '%s\n\n%s\n' "$body" "$(review_post_marker "$idempotency_key")"
}

review_post_payload_sha256() {
  # Canonical serialized review payload: the exact commit_id, event, body, and
  # comments. Any change yields a different payload hash, so a moved head or a
  # reworded body cannot collide with a prior post's idempotency key.
  local commit_id="$1" event="$2" body="$3" comments="$4"
  jq -S -c -n --arg commit_id "$commit_id" --arg event "$event" \
    --arg body "$body" --argjson comments "$comments" \
    '{body:$body,comments:$comments,commit_id:$commit_id,event:$event}' |
    review_runtime_sha256
}

review_post_canonical_payload() {
  local commit_id="$1" event="$2" body="$3" comments="$4"
  jq -S -c -n --arg commit_id "$commit_id" --arg event "$event" \
    --arg body "$body" --argjson comments "$comments" \
    '{body:$body,comments:$comments,commit_id:$commit_id,event:$event}'
}

review_post_gate_valid() {
  # Two authorizations are accepted, and only two.
  #
  # The interactive gate means a human confirmed at §6c; its shape is unchanged,
  # so `human_confirmed` keeps meaning exactly that and stays unforgeable by an
  # autonomous caller.
  #
  # The autonomous gate is for a caller with no human at that gate (the daemon).
  # It carries no `human_confirmed` field at all, and unlike the interactive gate
  # it must name the review it authorizes: a gate minted for another review key
  # or another head is refused here rather than trusted, which is what keeps a
  # replayed or copied authorization from posting to the wrong PR or an old head.
  local gate_json="$1" expected_event="$2" review_key="$3" head_sha="$4"
  local schema
  schema="$(jq -r 'if type == "object" then (.schema // empty) else empty end' \
    <<<"$gate_json" 2>/dev/null)" || return 1
  case "$schema" in
    kc-pr-flow.interactive-post-gate/v1)
      printf '%s' "$gate_json" | jq -e --arg event "$expected_event" '
        .human_confirmed == true and
        .effective_event == $event' >/dev/null 2>&1
      ;;
    kc-pr-flow.autonomous-post-gate/v1)
      printf '%s' "$gate_json" | jq -e \
        --arg event "$expected_event" --arg review_key "$review_key" \
        --arg head_sha "$head_sha" '
        (keys | sort) ==
          ["authorized_by","effective_event","head_sha","review_key","schema"] and
        .authorized_by == "daemon" and
        .effective_event == $event and
        .review_key == $review_key and
        .head_sha == $head_sha' >/dev/null 2>&1
      ;;
    *)
      return 1
      ;;
  esac
}

# Operator-level kill switch, layered above the per-call gate above. Off
# (the default) denies every caller with no daemon/interactive distinction.
review_post_rollback_enabled() {
  [ "${KC_PR_FLOW_ONCE_ONLY_POST:-off}" = on ]
}

review_post_run_dir() {
  local repository="$1" pr_number="$2" run_id="$3"
  local state_root repo_key
  state_root="$(review_runtime_prepare_state_root)" || return
  repo_key="$(review_runtime_repo_key "$repository")" || return
  printf '%s/%s/pr-%s/%s' "$state_root" "$repo_key" "$pr_number" "$run_id"
}

# Append one posting-lifecycle event to the run's accepted log. Reuses the
# runtime's durable append (locks, atomic rename, idempotent convergence).
review_post_append_event() {
  local run_id="$1" review_key="$2" repository="$3" pr_number="$4"
  local base_sha="$5" head_sha="$6" config_hash="$7" sequence="$8"
  local occurred_at="$9" event_type="${10}" payload="${11}"
  local event status
  event="$(review_runtime_build_event "$run_id" "$review_key" "$repository" \
    "$pr_number" "$base_sha" "$head_sha" "$config_hash" "$sequence" \
    "$occurred_at" "$event_type" "$payload")" || return 1
  status="$(review_runtime_append_line "$event")"
  local rc=$?
  case "$status" in
    appended | duplicate) return 0 ;;
    *) return "$rc" ;;
  esac
}

review_post_write_pending() {
  local run_dir="$1" pending_json="$2"
  local temp
  umask 077
  temp="$(mktemp "$run_dir/.pending.XXXXXX")" || return 74
  if ! printf '%s\n' "$pending_json" >"$temp" || ! chmod 0600 "$temp"; then
    rm -f "$temp"
    return 74
  fi
  if ! mv -f "$temp" "$run_dir/pending-post.json"; then
    rm -f "$temp"
    return 74
  fi
}

review_post_read_run_events() {
  local run_dir="$1"
  local events_file="$run_dir/events.jsonl"
  [ -f "$events_file" ] && [ ! -L "$events_file" ] || return 1
  review_runtime_validate_authoritative_log "$events_file" >/dev/null || return 1
  cat "$events_file"
}

review_post_terminal_result() {
  # Prints the terminal post.result outcome (posted/posted_reconciled/failed)
  # for the run, or empty if none exists.
  local events="$1"
  printf '%s\n' "$events" | jq -r 'select(.event_type=="post.result") | .payload.outcome' | head -n1
}

review_post_run_invalidated() {
  local events="$1"
  printf '%s\n' "$events" | jq -r 'select(.event_type=="run.invalidated") | .payload.reason' | head -n1
}

review_post_next_sequence() {
  # One past the last existing sequence number (sequences are 1-based), i.e.
  # the sequence a caller must use for the NEXT event it appends.
  local events="$1"
  printf '%s\n' "$events" | jq -s 'length + 1'
}

# A reconcile read is only trusted when it positively confirms remote state: an
# exit-0 body that is not a reviews array must never be read as "marker absent",
# which would license a blind retry of a payload that may already be live.
review_post_reviews_usable() {
  jq -e 'type == "object" and (.reviews | type == "array")' >/dev/null 2>&1 <<<"$1"
}

review_post_scan_marker() {
  # Emits the remote review id whose body carries the exact idempotency marker;
  # empty if none. Author identity is deliberately NOT part of the match: the
  # marker already pins this exact payload (sha256 over review_key, commit_id,
  # and payload_sha256), while the login a token actually posts under (user vs
  # bot vs app slug) is not knowable here — matching on it would turn an
  # identity mismatch into a duplicate review.
  local reviews_json="$1" marker="$2"
  jq -r --arg marker "$marker" '
    .reviews[] | select((.body // "") | contains($marker)) | .id' <<<"$reviews_json" | head -n1
}

review_post_head_sha() {
  # Prints the head sha only when the response positively carries one. A
  # shape-invalid head response must fail closed as a transport error, never be
  # compared against the reviewed head (which would silently misreport it as a
  # moved head and discard a postable review).
  local response="$1" sha
  sha="$(jq -r 'if type == "object" and ((.head_sha // "") | test("^[0-9a-f]{40}$"))
    then .head_sha else empty end' <<<"$response" 2>/dev/null)" || return 1
  [ -n "$sha" ] || return 1
  printf '%s' "$sha"
}

review_post_prior_attempt_state() {
  # What another run for this PR already knows about this exact payload's remote
  # fate, as `kind|remote_review_id`:
  #   posted|<id>   a terminal posted / posted_reconciled result — definitely live
  #   unsettled|    authorized but never settled — may be live, may be mid-POST
  # A prior run that ended `failed` or was invalidated landed nothing and prints
  # nothing, so it never blocks a fresh post. Only the caller's own run is
  # skipped, so this is the cross-run half of the exactly-once guarantee: the
  # remote marker scan can miss a landed review (list lag), and this cannot.
  #
  # Slurped deliberately: `jq -e`/`jq -r` over a stream reports per-line, so a
  # match followed by a non-match would misreport the run.
  local repository="$1" pr_number="$2" current_run_id="$3" idempotency_key="$4"
  local state_root repo_key pr_dir events_file verdict
  state_root="$(review_runtime_prepare_state_root)" || return 1
  repo_key="$(review_runtime_repo_key "$repository")" || return 1
  pr_dir="$state_root/$repo_key/pr-$pr_number"
  [ -d "$pr_dir" ] || return 1
  while IFS= read -r events_file; do
    [ -n "$events_file" ] || continue
    case "$events_file" in
      */"$current_run_id"/events.jsonl) continue ;;
    esac
    verdict="$(jq -r -s --arg key "$idempotency_key" '
      if (any(.[]; .event_type == "post.intent" and .payload.idempotency_key == $key) | not)
      then empty
      else
        ([.[] | select(.event_type == "post.result")] | last) as $result |
        (any(.[]; .event_type == "run.invalidated")) as $invalidated |
        if $result != null then
          if ($result.payload.outcome == "posted"
              or $result.payload.outcome == "posted_reconciled")
          then "posted|" + (($result.payload.remote_review_id // "") | tostring)
          else empty
          end
        elif $invalidated then empty
        else "unsettled|"
        end
      end' "$events_file" 2>/dev/null)"
    if [ -n "$verdict" ]; then
      printf '%s' "$verdict"
      return 0
    fi
  done < <(find "$pr_dir" -mindepth 2 -maxdepth 2 -type f -name events.jsonl 2>/dev/null)
  return 1
}

review_post_classify() {
  # Reads a transport `post` response and prints one of posted/failed/ambiguous.
  local response="$1" transport_rc="$2"
  if [ "$transport_rc" -ne 0 ]; then
    printf 'ambiguous'
    return
  fi
  local http remote
  http="$(jq -r '.http_status // 0' <<<"$response" 2>/dev/null)" || http=0
  remote="$(jq -r '.remote_review_id // "null"' <<<"$response" 2>/dev/null)" || remote=null
  case "$http" in
    200 | 201)
      if [ "$remote" = null ] || [ -z "$remote" ]; then
        printf 'ambiguous'
      else
        printf 'posted'
      fi
      ;;
    408 | 429)
      printf 'ambiguous'
      ;;
    4??)
      printf 'failed'
      ;;
    *)
      printf 'ambiguous'
      ;;
  esac
}

# Emit a compact status object and succeed.
review_post_emit() {
  jq -S -c -n \
    --arg status "$1" --arg run_id "$2" --arg idempotency_key "$3" \
    --arg reason "${4:-}" --arg remote_review_id "${5:-}" '
    {status:$status,run_id:$run_id,idempotency_key:$idempotency_key} +
    (if $reason == "" then {} else {reason:$reason} end) +
    (if $remote_review_id == "" then {} else {remote_review_id:($remote_review_id|tonumber)} end)'
}

review_post_cmd_post() {
  local request_file='' gate_file='' now_epoch='' occurred_at=''
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --request-file) request_file="$2"; shift 2 ;;
      --gate-file) gate_file="$2"; shift 2 ;;
      --now-epoch) now_epoch="$2"; shift 2 ;;
      --occurred-at) occurred_at="$2"; shift 2 ;;
      *) printf 'review-post: unknown post option %s\n' "$1" >&2; return 2 ;;
    esac
  done
  review_post_rollback_enabled || {
    printf 'review-post: once-only posting is disabled (set KC_PR_FLOW_ONCE_ONLY_POST=on to enable)\n' >&2
    return 3
  }
  if [ -z "$request_file" ] || [ ! -f "$request_file" ]; then
    printf 'review-post: --request-file is required\n' >&2
    return 2
  fi
  if [ -z "$gate_file" ] || [ ! -f "$gate_file" ]; then
    printf 'review-post: --gate-file is required\n' >&2
    return 2
  fi
  review_runtime_require_jq || return
  review_runtime_require_python || return

  local request gate
  request="$(cat "$request_file")" || return 74
  gate="$(cat "$gate_file")" || return 74

  local repository pr_number base_sha head_sha config_hash commit_id event
  local body comments self_login retention_seconds
  repository="$(jq -r '.repo' <<<"$request")"
  pr_number="$(jq -r '.pr' <<<"$request")"
  base_sha="$(jq -r '.base_sha' <<<"$request")"
  head_sha="$(jq -r '.head_sha' <<<"$request")"
  config_hash="$(jq -r '.config_hash' <<<"$request")"
  commit_id="$(jq -r '.commit_id' <<<"$request")"
  event="$(jq -r '.event' <<<"$request")"
  body="$(jq -r '.body' <<<"$request")"
  comments="$(jq -c '.comments' <<<"$request")"
  self_login="$(jq -r '.self_login' <<<"$request")"
  retention_seconds="$(jq -r '.retention_seconds // empty' <<<"$request")"
  [ -n "$retention_seconds" ] || retention_seconds="${KC_PR_FLOW_PENDING_RETENTION_SECONDS:-$REVIEW_POST_DEFAULT_RETENTION_SECONDS}"

  if [ "$commit_id" != "$head_sha" ]; then
    printf 'review-post: commit_id must equal the reviewed head\n' >&2
    return 3
  fi

  # The review key is derived before the gate check because an autonomous gate
  # names the review it authorizes, and that binding is only checkable against
  # the key this request actually resolves to.
  local review_key payload payload_sha256 idempotency_key
  review_key="$(review_runtime_review_key "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash")" || return 1
  if ! review_post_gate_valid "$gate" "$event" "$review_key" "$head_sha"; then
    printf 'review-post: invalid, event-mismatched, or unbound post gate\n' >&2
    return 3
  fi
  payload="$(review_post_canonical_payload "$commit_id" "$event" "$body" "$comments")" || return 1
  payload_sha256="$(review_post_payload_sha256 "$commit_id" "$event" "$body" "$comments")" || return 1
  idempotency_key="$(review_runtime_idempotency_key "$review_key" "$commit_id" "$payload_sha256")" || return 1

  [ -n "$now_epoch" ] || now_epoch="$(review_post_now_epoch)"
  [ -n "$occurred_at" ] || occurred_at="$(review_post_epoch_to_rfc3339 "$now_epoch")"
  local expires_at
  expires_at="$(review_post_epoch_to_rfc3339 "$((now_epoch + retention_seconds))")" || return 1

  # Start a fresh posting run (its own lifecycle, never a shadow receipt).
  local started run_id run_dir
  started="$(review_runtime_start "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" "$occurred_at")" || return 74
  run_id="$(jq -r '.run_id' <<<"$started")"
  run_dir="$(review_post_run_dir "$repository" "$pr_number" "$run_id")" || return 74

  # Fresh exact-head check before any mutation.
  local head_response current_head
  head_response="$(review_post_transport head --repo "$repository" --pr "$pr_number")" || return 74
  current_head="$(review_post_head_sha "$head_response")" || {
    printf 'review-post: head response carried no usable head sha\n' >&2
    return 74
  }
  if [ "$current_head" != "$commit_id" ]; then
    review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
      "$base_sha" "$head_sha" "$config_hash" 2 "$occurred_at" head.observed \
      "$(jq -cn --arg h "$current_head" '{head_sha:$h}')" || return 74
    review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
      "$base_sha" "$head_sha" "$config_hash" 3 "$occurred_at" run.invalidated \
      '{"reason":"head_moved"}' || return 74
    review_post_emit invalidated "$run_id" "$idempotency_key" head_moved ''
    return 0
  fi

  # Durable-before-mutate: head.observed, authorization.granted, post.intent,
  # and the pending payload all land before the network call.
  review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
    "$base_sha" "$head_sha" "$config_hash" 2 "$occurred_at" head.observed \
    "$(jq -cn --arg h "$current_head" '{head_sha:$h}')" || return 74
  review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
    "$base_sha" "$head_sha" "$config_hash" 3 "$occurred_at" authorization.granted \
    "$(jq -cn --arg commit_id "$commit_id" --arg event "$event" \
      --arg idempotency_key "$idempotency_key" --arg payload_sha256 "$payload_sha256" \
      '{commit_id:$commit_id,event:$event,idempotency_key:$idempotency_key,payload_sha256:$payload_sha256}')" || return 74
  review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
    "$base_sha" "$head_sha" "$config_hash" 4 "$occurred_at" post.intent \
    "$(jq -cn --arg commit_id "$commit_id" \
      --arg idempotency_key "$idempotency_key" --arg payload_sha256 "$payload_sha256" \
      '{commit_id:$commit_id,idempotency_key:$idempotency_key,payload_sha256:$payload_sha256}')" || return 74

  local pending
  pending="$(jq -S -c -n \
    --arg review_key "$review_key" --arg run_id "$run_id" --arg commit_id "$commit_id" \
    --arg event "$event" --argjson payload "$payload" --arg payload_sha256 "$payload_sha256" \
    --arg idempotency_key "$idempotency_key" --arg authorized_at "$occurred_at" \
    --arg expires_at "$expires_at" '
    {schema:"kc-pr-flow.pending-post/v1",review_key:$review_key,run_id:$run_id,
     commit_id:$commit_id,event:$event,payload:$payload,payload_sha256:$payload_sha256,
     idempotency_key:$idempotency_key,authorized_at:$authorized_at,expires_at:$expires_at}')" || return 1
  review_post_write_pending "$run_dir" "$pending" || return 74

  # Exactly-once must survive a re-invocation, not only a crash-resume: a prior
  # run's ambiguous POST may already be live remotely. Reconcile that instead of
  # posting the identical payload again. When the read cannot confirm remote
  # state, only a payload with no prior posting attempt may proceed.
  local marker reviews_json existing_id
  marker="$(review_post_marker "$idempotency_key")"
  reviews_json="$(review_post_transport list --repo "$repository" --pr "$pr_number" --self "$self_login")" || return 74
  if review_post_reviews_usable "$reviews_json"; then
    existing_id="$(review_post_scan_marker "$reviews_json" "$marker")"
    if [ -n "$existing_id" ]; then
      review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
        "$base_sha" "$head_sha" "$config_hash" 5 "$occurred_at" post.result \
        "$(jq -cn --argjson remote_review_id "$existing_id" --arg idempotency_key "$idempotency_key" \
          '{idempotency_key:$idempotency_key,outcome:"posted_reconciled",remote_review_id:$remote_review_id}')" || return 74
      rm -f "$run_dir/pending-post.json"
      review_post_emit posted_reconciled "$run_id" "$idempotency_key" '' "$existing_id"
      return 0
    fi
  fi
  # No confirmed remote copy — but "not visible" is not "not posted". Consult
  # local durable state for another run that authorized this exact payload: the
  # remote scan above can miss a landed review while the list lags, and this
  # cannot.
  local prior_state prior_kind prior_remote
  prior_state="$(review_post_prior_attempt_state "$repository" "$pr_number" "$run_id" "$idempotency_key")" || prior_state=''
  if [ -n "$prior_state" ]; then
    prior_kind="${prior_state%%|*}"
    prior_remote="${prior_state#*|}"
    if [ "$prior_kind" = posted ]; then
      # A prior run definitively landed this payload. Settle against it rather
      # than posting a second copy the lagging list simply cannot show us yet.
      review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
        "$base_sha" "$head_sha" "$config_hash" 5 "$occurred_at" post.result \
        "$(jq -cn --argjson remote_review_id "$prior_remote" --arg idempotency_key "$idempotency_key" \
          '{idempotency_key:$idempotency_key,outcome:"posted_reconciled",remote_review_id:$remote_review_id}')" || return 74
      rm -f "$run_dir/pending-post.json"
      review_post_emit posted_reconciled "$run_id" "$idempotency_key" '' "$prior_remote"
      return 0
    fi
    printf 'review-post: an unsettled prior attempt exists for this payload; resume it instead\n' >&2
    review_post_emit ambiguous "$run_id" "$idempotency_key" prior_attempt_unsettled ''
    return 0
  fi

  # POST the marker-bearing body; classify the (possibly ambiguous) outcome.
  local post_body response transport_rc classification
  post_body="$(review_post_body_with_marker "$body" "$idempotency_key")"
  response="$(printf '%s' "$(jq -cn --arg commit_id "$commit_id" --arg event "$event" \
    --arg body "$post_body" --argjson comments "$comments" \
    '{commit_id:$commit_id,event:$event,body:$body,comments:$comments}')" |
    review_post_transport post --repo "$repository" --pr "$pr_number")"
  transport_rc=$?
  classification="$(review_post_classify "$response" "$transport_rc")"

  review_post_finalize_outcome "$classification" "$response" "$run_id" "$review_key" \
    "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" "$occurred_at" \
    "$idempotency_key" "$run_dir" 5
}

# Given a classification, append the terminal post.result (or leave the pending
# payload durable for an ambiguous outcome) and emit status.
review_post_finalize_outcome() {
  local classification="$1" response="$2" run_id="$3" review_key="$4"
  local repository="$5" pr_number="$6" base_sha="$7" head_sha="$8" config_hash="$9"
  local occurred_at="${10}" idempotency_key="${11}" run_dir="${12}" sequence="${13}"
  local remote_id
  case "$classification" in
    posted)
      remote_id="$(jq -r '.remote_review_id' <<<"$response")"
      review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
        "$base_sha" "$head_sha" "$config_hash" "$sequence" "$occurred_at" post.result \
        "$(jq -cn --argjson remote_review_id "$remote_id" --arg idempotency_key "$idempotency_key" \
          '{idempotency_key:$idempotency_key,outcome:"posted",remote_review_id:$remote_review_id}')" || return 74
      rm -f "$run_dir/pending-post.json"
      review_post_emit posted "$run_id" "$idempotency_key" '' "$remote_id"
      ;;
    failed)
      review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
        "$base_sha" "$head_sha" "$config_hash" "$sequence" "$occurred_at" post.result \
        "$(jq -cn --arg idempotency_key "$idempotency_key" \
          '{idempotency_key:$idempotency_key,outcome:"failed"}')" || return 74
      review_post_emit failed "$run_id" "$idempotency_key" '' ''
      ;;
    *)
      # Ambiguous: leave the pending payload durable, do NOT blind-retry.
      review_post_emit ambiguous "$run_id" "$idempotency_key" '' ''
      ;;
  esac
}

review_post_cmd_resume() {
  local repository='' pr_number='' self_login='' run_id='' now_epoch=''
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --repo) repository="$2"; shift 2 ;;
      --pr) pr_number="$2"; shift 2 ;;
      --self) self_login="$2"; shift 2 ;;
      --run-id) run_id="$2"; shift 2 ;;
      --now-epoch) now_epoch="$2"; shift 2 ;;
      *) printf 'review-post: unknown resume option %s\n' "$1" >&2; return 2 ;;
    esac
  done
  if [ -z "$repository" ] || [ -z "$pr_number" ] || [ -z "$self_login" ] || [ -z "$run_id" ]; then
    printf 'review-post: resume requires --repo --pr --self --run-id\n' >&2
    return 2
  fi
  review_runtime_require_jq || return
  review_runtime_require_python || return

  local run_dir events pending
  run_dir="$(review_post_run_dir "$repository" "$pr_number" "$run_id")" || return 74
  events="$(review_post_read_run_events "$run_dir")" || {
    printf 'review-post: no replayable posting run for %s\n' "$run_id" >&2
    return 74
  }

  local terminal
  terminal="$(review_post_terminal_result "$events")"
  if [ -n "$terminal" ]; then
    local idk
    idk="$(printf '%s\n' "$events" | jq -r 'select(.event_type=="post.intent") | .payload.idempotency_key' | head -n1)"
    review_post_emit "$terminal" "$run_id" "$idk" '' ''
    return 0
  fi
  local invalidated
  invalidated="$(review_post_run_invalidated "$events")"
  if [ -n "$invalidated" ]; then
    local idk
    idk="$(printf '%s\n' "$events" | jq -r 'select(.event_type=="post.intent") | .payload.idempotency_key' | head -n1)"
    review_post_emit invalidated "$run_id" "$idk" "$invalidated" ''
    return 0
  fi

  if [ ! -f "$run_dir/pending-post.json" ] || [ -L "$run_dir/pending-post.json" ]; then
    printf 'review-post: no pending payload to resume for %s\n' "$run_id" >&2
    return 74
  fi
  pending="$(cat "$run_dir/pending-post.json")" || return 74

  local review_key commit_id event idempotency_key payload_sha256 body comments base_sha head_sha config_hash
  review_key="$(jq -r '.review_key' <<<"$pending")"
  commit_id="$(jq -r '.commit_id' <<<"$pending")"
  event="$(jq -r '.event' <<<"$pending")"
  idempotency_key="$(jq -r '.idempotency_key' <<<"$pending")"
  payload_sha256="$(jq -r '.payload_sha256' <<<"$pending")"
  body="$(jq -r '.payload.body' <<<"$pending")"
  comments="$(jq -c '.payload.comments' <<<"$pending")"
  base_sha="$(printf '%s\n' "$events" | jq -r 'select(.event_type=="run.started") | .base_sha' | head -n1)"
  head_sha="$(printf '%s\n' "$events" | jq -r 'select(.event_type=="run.started") | .head_sha' | head -n1)"
  config_hash="$(printf '%s\n' "$events" | jq -r 'select(.event_type=="run.started") | .config_hash' | head -n1)"

  local occurred_at next_seq
  occurred_at="$(review_post_now_utc)"
  next_seq="$(review_post_next_sequence "$events")"

  # Fresh exact-head check; a moved head invalidates and never posts the stale
  # payload.
  local head_response current_head
  head_response="$(review_post_transport head --repo "$repository" --pr "$pr_number")" || return 74
  current_head="$(review_post_head_sha "$head_response")" || {
    printf 'review-post: head response carried no usable head sha\n' >&2
    return 74
  }
  if [ "$current_head" != "$commit_id" ]; then
    review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
      "$base_sha" "$head_sha" "$config_hash" "$next_seq" "$occurred_at" head.observed \
      "$(jq -cn --arg h "$current_head" '{head_sha:$h}')" || return 74
    review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
      "$base_sha" "$head_sha" "$config_hash" "$((next_seq + 1))" "$occurred_at" run.invalidated \
      '{"reason":"head_moved"}' || return 74
    rm -f "$run_dir/pending-post.json"
    review_post_emit invalidated "$run_id" "$idempotency_key" head_moved ''
    return 0
  fi

  local marker
  marker="$(review_post_marker "$idempotency_key")"

  # Reconcile-before-retry: a landed review with our marker means the earlier
  # POST succeeded; record it and post NOTHING. A read that cannot positively
  # confirm remote state fails closed — the pending payload stays durable for a
  # later attempt rather than licensing a retry that could duplicate.
  local reviews_json remote_id
  reviews_json="$(review_post_transport list --repo "$repository" --pr "$pr_number" --self "$self_login")" || return 74
  review_post_reviews_usable "$reviews_json" || {
    printf 'review-post: reconcile list was unusable; keeping the pending payload\n' >&2
    review_post_emit ambiguous "$run_id" "$idempotency_key" reconcile_unavailable ''
    return 0
  }
  remote_id="$(review_post_scan_marker "$reviews_json" "$marker")"
  if [ -n "$remote_id" ]; then
    review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
      "$base_sha" "$head_sha" "$config_hash" "$next_seq" "$occurred_at" post.result \
      "$(jq -cn --argjson remote_review_id "$remote_id" --arg idempotency_key "$idempotency_key" \
        '{idempotency_key:$idempotency_key,outcome:"posted_reconciled",remote_review_id:$remote_review_id}')" || return 74
    rm -f "$run_dir/pending-post.json"
    review_post_emit posted_reconciled "$run_id" "$idempotency_key" '' "$remote_id"
    return 0
  fi

  # Marker absent on a usable list. That only proves "never landed" once the
  # read-after-write confirm window since post.intent has elapsed; inside it, an
  # absent marker is indistinguishable from GitHub lag and a retry would
  # duplicate a review that did land. Wait the window out instead.
  local intent_at intent_epoch confirm_seconds
  intent_at="$(printf '%s\n' "$events" | jq -r 'select(.event_type=="post.intent") | .occurred_at' | head -n1)"
  confirm_seconds="${KC_PR_FLOW_RECONCILE_CONFIRM_SECONDS:-$REVIEW_POST_DEFAULT_RECONCILE_CONFIRM_SECONDS}"
  # An unvalidated window would make the comparison below error out and read as
  # false — i.e. fail OPEN into the retry this window exists to prevent.
  case "$confirm_seconds" in
    '' | *[!0-9]*) confirm_seconds="$REVIEW_POST_DEFAULT_RECONCILE_CONFIRM_SECONDS" ;;
  esac
  [ -n "$now_epoch" ] || now_epoch="$(review_post_now_epoch)"
  case "$now_epoch" in
    '' | *[!0-9]*)
      printf 'review-post: --now-epoch must be a non-negative integer\n' >&2
      return 2
      ;;
  esac
  intent_epoch="$(review_post_rfc3339_to_epoch "$intent_at")" || intent_epoch=''
  if [ -z "$intent_epoch" ] || [ "$((now_epoch - intent_epoch))" -lt "$confirm_seconds" ]; then
    review_post_emit ambiguous "$run_id" "$idempotency_key" reconcile_unconfirmed ''
    return 0
  fi

  # Confirm window elapsed with the marker still absent: retry the exact same
  # payload once, then re-reconcile.
  local post_body response transport_rc classification
  post_body="$(review_post_body_with_marker "$body" "$idempotency_key")"
  response="$(printf '%s' "$(jq -cn --arg commit_id "$commit_id" --arg event "$event" \
    --arg body "$post_body" --argjson comments "$comments" \
    '{commit_id:$commit_id,event:$event,body:$body,comments:$comments}')" |
    review_post_transport post --repo "$repository" --pr "$pr_number")"
  transport_rc=$?
  classification="$(review_post_classify "$response" "$transport_rc")"
  if [ "$classification" = ambiguous ]; then
    reviews_json="$(review_post_transport list --repo "$repository" --pr "$pr_number" --self "$self_login")" || return 74
    remote_id=''
    if review_post_reviews_usable "$reviews_json"; then
      remote_id="$(review_post_scan_marker "$reviews_json" "$marker")"
    fi
    if [ -n "$remote_id" ]; then
      review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
        "$base_sha" "$head_sha" "$config_hash" "$next_seq" "$occurred_at" post.result \
        "$(jq -cn --argjson remote_review_id "$remote_id" --arg idempotency_key "$idempotency_key" \
          '{idempotency_key:$idempotency_key,outcome:"posted_reconciled",remote_review_id:$remote_review_id}')" || return 74
      rm -f "$run_dir/pending-post.json"
      review_post_emit posted_reconciled "$run_id" "$idempotency_key" '' "$remote_id"
      return 0
    fi
    review_post_emit ambiguous "$run_id" "$idempotency_key" '' ''
    return 0
  fi
  review_post_finalize_outcome "$classification" "$response" "$run_id" "$review_key" \
    "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" "$occurred_at" \
    "$idempotency_key" "$run_dir" "$next_seq"
}

review_post_cmd_gc() {
  local repository='' pr_number='' now_epoch=''
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --repo) repository="$2"; shift 2 ;;
      --pr) pr_number="$2"; shift 2 ;;
      --now-epoch) now_epoch="$2"; shift 2 ;;
      *) printf 'review-post: unknown gc option %s\n' "$1" >&2; return 2 ;;
    esac
  done
  if [ -z "$repository" ] || [ -z "$pr_number" ]; then
    printf 'review-post: gc requires --repo --pr\n' >&2
    return 2
  fi
  review_runtime_require_jq || return
  review_runtime_require_python || return
  [ -n "$now_epoch" ] || now_epoch="$(review_post_now_epoch)"
  # An unvalidated clock makes the within-window comparison below error out and
  # read as false, which would expire evidence that is still inside its window.
  case "$now_epoch" in
    '' | *[!0-9]*)
      printf 'review-post: --now-epoch must be a non-negative integer\n' >&2
      return 2
      ;;
  esac

  local state_root repo_key pr_dir removed=0 kept=0
  state_root="$(review_runtime_prepare_state_root)" || return 74
  repo_key="$(review_runtime_repo_key "$repository")" || return 74
  pr_dir="$state_root/$repo_key/pr-$pr_number"
  [ -d "$pr_dir" ] || {
    review_post_emit_gc 0 0
    return 0
  }

  local pending run_dir run_id events terminal pending_json expires_at expires_epoch
  local review_key idempotency_key occurred_at next_seq base_sha head_sha config_hash
  while IFS= read -r pending; do
    [ -n "$pending" ] || continue
    run_dir="$(dirname "$pending")"
    run_id="$(basename "$run_dir")"
    pending_json="$(cat "$pending" 2>/dev/null)" || continue
    expires_at="$(jq -r '.expires_at' <<<"$pending_json")"
    idempotency_key="$(jq -r '.idempotency_key' <<<"$pending_json")"
    review_key="$(jq -r '.review_key' <<<"$pending_json")"
    expires_epoch="$(review_post_rfc3339_to_epoch "$expires_at")" || continue

    # Fail-safe invariant: never GC a within-window pending payload — that is
    # exactly the evidence needed to reconcile an uncertain remote result.
    if [ "$now_epoch" -lt "$expires_epoch" ]; then
      kept=$((kept + 1))
      continue
    fi

    events="$(review_post_read_run_events "$run_dir")" || { kept=$((kept + 1)); continue; }
    terminal="$(review_post_terminal_result "$events")"
    if [ "$terminal" = posted ] || [ "$terminal" = posted_reconciled ]; then
      # A reconciled/landed post should not retain a pending payload; clean it.
      rm -f "$pending"
      removed=$((removed + 1))
      continue
    fi

    base_sha="$(printf '%s\n' "$events" | jq -r 'select(.event_type=="run.started") | .base_sha' | head -n1)"
    head_sha="$(printf '%s\n' "$events" | jq -r 'select(.event_type=="run.started") | .head_sha' | head -n1)"
    config_hash="$(printf '%s\n' "$events" | jq -r 'select(.event_type=="run.started") | .config_hash' | head -n1)"
    occurred_at="$(review_post_now_utc)"
    next_seq="$(review_post_next_sequence "$events")"
    if [ -z "$(review_post_run_invalidated "$events")" ]; then
      review_post_append_event "$run_id" "$review_key" "$repository" "$pr_number" \
        "$base_sha" "$head_sha" "$config_hash" "$next_seq" "$occurred_at" run.invalidated \
        '{"reason":"expired"}' || { kept=$((kept + 1)); continue; }
    fi
    rm -f "$pending"
    removed=$((removed + 1))
  done < <(find "$pr_dir" -mindepth 2 -maxdepth 2 -type f -name 'pending-post.json' 2>/dev/null)

  review_post_emit_gc "$removed" "$kept"
}

review_post_emit_gc() {
  jq -S -c -n --argjson removed "$1" --argjson kept "$2" \
    '{status:"gc",removed:$removed,kept:$kept}'
}

review_post_usage() {
  printf 'usage: review-post.sh (post|resume|gc) ...\n' >&2
}

review_post_main() {
  local command="${1:-}"
  [ "$#" -gt 0 ] && shift
  case "$command" in
    post) review_post_cmd_post "$@" ;;
    resume) review_post_cmd_resume "$@" ;;
    gc) review_post_cmd_gc "$@" ;;
    *)
      review_post_usage
      return 2
      ;;
  esac
}

review_post_source_runtime || {
  printf 'review-post: unable to load review-runtime.sh\n' >&2
  exit 69
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  review_post_main "$@"
fi
