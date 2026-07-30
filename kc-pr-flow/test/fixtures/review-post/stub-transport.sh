#!/usr/bin/env bash
# Source-safe recorded GitHub transport stub for review-post.sh tests (D2).
#
# It never touches the network or a real PR. All behavior is driven by files
# under $KC_STUB_DIR so a test can script a fault (ambiguous POST that still
# lands remotely — the "request reached GitHub, response lost" case) and then
# assert exactly-once reconciliation.
#
# Files (all under $KC_STUB_DIR):
#   head            single line: the PR's current head SHA (transport op `head`).
#   post-plan       one classification per POST attempt, consumed top-down:
#                     posted    -> record the review, return http_status 201
#                     ambiguous -> record the review, return http_status 0
#                     lost      -> do NOT record, return http_status 0
#                     failed    -> do NOT record, return http_status 422
#                   Missing/empty line defaults to `posted`.
#   list-plan       one behavior per `list` call, consumed top-down. Models the
#                   reconcile read failing to positively confirm remote state:
#                     faithful -> return the recorded store (default)
#                     lag      -> return {"reviews":[]} even though the store is
#                                 non-empty (GitHub read-after-write lag: a just
#                                 -created review is not visible yet)
#                     unusable -> return {"reviews":null} (exit 0, unusable body)
#                     scalar   -> append a scalar reviews[] element
#                     numeric-body
#                              -> append an object whose body is numeric
#                     numeric-body-first
#                              -> prepend that numeric-body object before the
#                                 recorded store (including any receipt marker)
#                   Missing/empty line defaults to `faithful`.
#   head-plan       one behavior per `head` call, consumed top-down:
#                     faithful  -> return {"head_sha": <head>} (default)
#                     malformed -> return {} (exit 0, no head_sha)
#   reviews.jsonl   append-only store of recorded reviews (the "remote" state).
#   self            the self login the stub attributes recorded reviews to.
#   post-count      internal counter of POST attempts.
#   list-count      internal counter of `list` calls.
#   head-count      internal counter of `head` calls.
set -uo pipefail

stub_dir="${KC_STUB_DIR:?KC_STUB_DIR must be set}"
op="${1:-}"
shift || true

# --repo/--pr/--self are part of the transport CLI contract but unused here:
# this stub is driven entirely by files under $stub_dir (including self, read
# from $stub_dir/self below), not by these arguments.
while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo | --pr | --self) shift 2 ;;
    *) shift ;;
  esac
done

# Consume the next line of a per-call plan file, defaulting when absent.
# $1 plan basename, $2 counter basename, $3 default behavior.
next_plan() {
  local plan_file="$stub_dir/$1" count_file="$stub_dir/$2" fallback="$3"
  local count=0 behavior
  [ -f "$count_file" ] && count="$(cat "$count_file")"
  behavior="$fallback"
  if [ -f "$plan_file" ]; then
    behavior="$(sed -n "$((count + 1))p" "$plan_file")"
    [ -n "$behavior" ] || behavior="$fallback"
  fi
  printf '%s\n' "$((count + 1))" >"$count_file"
  printf '%s' "$behavior"
}

case "$op" in
  head)
    case "$(next_plan head-plan head-count faithful)" in
      malformed) printf '{}\n' ;;
      *) printf '{"head_sha":%s}\n' "$(jq -Rn --arg h "$(cat "$stub_dir/head")" '$h')" ;;
    esac
    ;;
  list)
    case "$(next_plan list-plan list-count faithful)" in
      lag)
        printf '{"reviews":[]}\n'
        ;;
      unusable)
        printf '{"reviews":null}\n'
        ;;
      scalar)
        jq -s '{reviews: (. + [42])}' "$stub_dir/reviews.jsonl"
        ;;
      numeric-body)
        jq -s '{reviews: (. + [{id:9001,user:"malformed",body:42,commit_id:"0000000000000000000000000000000000000000"}])}' \
          "$stub_dir/reviews.jsonl"
        ;;
      numeric-body-first)
        jq -s '{reviews: ([{id:9001,user:"malformed",body:42,commit_id:"0000000000000000000000000000000000000000"}] + .)}' \
          "$stub_dir/reviews.jsonl"
        ;;
      *)
        if [ -f "$stub_dir/reviews.jsonl" ]; then
          jq -s '{reviews: .}' "$stub_dir/reviews.jsonl"
        else
          printf '{"reviews":[]}\n'
        fi
        ;;
    esac
    ;;
  post)
    body="$(cat)"
    count_file="$stub_dir/post-count"
    count=0
    [ -f "$count_file" ] && count="$(cat "$count_file")"
    plan="posted"
    if [ -f "$stub_dir/post-plan" ]; then
      plan="$(sed -n "$((count + 1))p" "$stub_dir/post-plan")"
      [ -n "$plan" ] || plan="posted"
    fi
    count=$((count + 1))
    printf '%s\n' "$count" >"$count_file"
    self_login="$(cat "$stub_dir/self" 2>/dev/null || printf 'self')"
    commit_id="$(jq -r '.commit_id' <<<"$body")"
    review_body="$(jq -r '.body' <<<"$body")"
    record_review() {
      jq -cn --argjson id "$count" --arg user "$self_login" \
        --arg body "$review_body" --arg commit_id "$commit_id" \
        '{id:$id,user:$user,body:$body,commit_id:$commit_id}' \
        >>"$stub_dir/reviews.jsonl"
    }
    case "$plan" in
      posted)
        record_review
        printf '{"http_status":201,"remote_review_id":%s}\n' "$count"
        ;;
      ambiguous)
        record_review
        printf '{"http_status":0,"remote_review_id":null}\n'
        ;;
      lost)
        printf '{"http_status":0,"remote_review_id":null}\n'
        ;;
      failed)
        printf '{"http_status":422,"remote_review_id":null}\n'
        ;;
      *)
        record_review
        printf '{"http_status":201,"remote_review_id":%s}\n' "$count"
        ;;
    esac
    ;;
  *)
    printf 'stub-transport: unknown op %s\n' "$op" >&2
    exit 2
    ;;
esac
