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
#   reviews.jsonl   append-only store of recorded reviews (the "remote" state).
#   self            the self login the stub attributes recorded reviews to.
#   post-count      internal counter of POST attempts.
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

case "$op" in
  head)
    printf '{"head_sha":%s}\n' "$(jq -Rn --arg h "$(cat "$stub_dir/head")" '$h')"
    ;;
  list)
    if [ -f "$stub_dir/reviews.jsonl" ]; then
      jq -s '{reviews: .}' "$stub_dir/reviews.jsonl"
    else
      printf '{"reviews":[]}\n'
    fi
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
