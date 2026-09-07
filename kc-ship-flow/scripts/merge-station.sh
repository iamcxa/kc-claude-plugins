#!/usr/bin/env bash
# Merge station: verify base and accepted head for every PR, mark every PR
# ready, wait each one clean, then squash-merge in the given order, stopping
# at the first refusal. See kc-ship-flow/references/stations/merge-station.md.
#
# Usage: merge-station.sh --trunk <branch> [--accepted <file>]
#                          [--override "<reason>"] [--repo owner/name]
#                          [--wait-seconds <n>] <pr>...
#
# Exit codes: 0 every PR merged, one `MERGED: #<pr> <mergeCommit>` line per
# PR printed in order; 2 a usage error, a PR whose baseRefName is not
# --trunk, or (absent --override) a PR whose headRefOid is not listed in
# --accepted; 3 a PR's mergeable/mergeStateStatus never reaches clean within
# --wait-seconds, or any statusCheckRollup entry reads conclusion FAILURE;
# 4 `gh pr merge` itself fails for a PR -- no later PR is touched; 5 the PR
# after a landing reads mergeStateStatus CONFLICTING (its base moved) --
# refuses to resolve it and stops.
set -euo pipefail

GH=${GH:-gh}

timestamp() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
log() { echo "$(timestamp) merge-station: $*" >&2; }
die() { local code="$1"; shift; echo "$*" >&2; exit "$code"; }

usage() {
  cat >&2 <<'EOF'
usage: merge-station.sh --trunk <branch> [--accepted <file>]
                         [--override "<reason>"] [--repo owner/name]
                         [--wait-seconds <n>] <pr>...
EOF
}

trunk=""
accepted_file=""
override_reason=""
repo=""
wait_seconds=600
poll_seconds="${MERGE_STATION_POLL_SECONDS:-5}"
prs=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --trunk)
      [ "$#" -ge 2 ] || die 2 "USAGE: --trunk requires a value"
      trunk="$2"; shift 2 ;;
    --accepted)
      [ "$#" -ge 2 ] || die 2 "USAGE: --accepted requires a value"
      accepted_file="$2"; shift 2 ;;
    --override)
      [ "$#" -ge 2 ] || die 2 "USAGE: --override requires a value"
      override_reason="$2"; shift 2 ;;
    --repo)
      [ "$#" -ge 2 ] || die 2 "USAGE: --repo requires a value"
      repo="$2"; shift 2 ;;
    --wait-seconds)
      [ "$#" -ge 2 ] || die 2 "USAGE: --wait-seconds requires a value"
      wait_seconds="$2"; shift 2 ;;
    -*)
      usage; die 2 "USAGE: unknown flag: $1" ;;
    *)
      prs+=("$1"); shift ;;
  esac
done

[ -n "$trunk" ] || { usage; die 2 "USAGE: --trunk is required"; }
[ "${#prs[@]}" -ge 1 ] || { usage; die 2 "USAGE: at least one PR is required"; }

repo_args=()
[ -z "$repo" ] || repo_args=(--repo "$repo")

gh_view_field() {
  local pr="$1" fields="$2"
  "$GH" pr view "$pr" "${repo_args[@]}" --json "$fields"
}

# (1) every PR's base must be --trunk, checked for every PR before any
# ready/merge call is made.
for pr in "${prs[@]}"; do
  base="$(gh_view_field "$pr" baseRefName | jq -r '.baseRefName')"
  [ "$base" = "$trunk" ] || die 2 "BASE_NOT_TRUNK: pr #$pr base=$base expected=$trunk"
done

# (2) every PR's current head must be listed in --accepted, unless
# --override is given.
if [ -n "$accepted_file" ]; then
  [ -f "$accepted_file" ] || die 2 "USAGE: --accepted file not found: $accepted_file"
  for pr in "${prs[@]}"; do
    head="$(gh_view_field "$pr" headRefOid | jq -r '.headRefOid')"
    if ! grep -qx "$head" "$accepted_file"; then
      if [ -n "$override_reason" ]; then
        echo "OVERRIDE: $override_reason"
      else
        die 2 "HEAD_NOT_ACCEPTED: pr #$pr head=$head"
      fi
    fi
  done
fi

# (3) mark every PR ready before merging any.
for pr in "${prs[@]}"; do
  log "marking ready: pr #$pr"
  "$GH" pr ready "$pr" "${repo_args[@]}"
done

wait_until_clean() {
  local pr="$1" start now elapsed resp mergeable state failures
  start="$(date +%s)"
  while true; do
    resp="$(gh_view_field "$pr" 'mergeable,mergeStateStatus,statusCheckRollup')"
    mergeable="$(echo "$resp" | jq -r '.mergeable')"
    state="$(echo "$resp" | jq -r '.mergeStateStatus')"
    failures="$(echo "$resp" | jq '[.statusCheckRollup[]? | select(.conclusion == "FAILURE")] | length')"
    [ "$failures" -eq 0 ] || die 3 "CHECK_FAILURE: pr #$pr has a statusCheckRollup entry with conclusion FAILURE"
    if [ "$mergeable" = "MERGEABLE" ] && { [ "$state" = "CLEAN" ] || [ "$state" = "UNSTABLE" ]; }; then
      return 0
    fi
    now="$(date +%s)"
    elapsed=$((now - start))
    if [ "$elapsed" -ge "$wait_seconds" ]; then
      die 3 "WAIT_TIMEOUT: pr #$pr not clean after ${wait_seconds}s (mergeable=$mergeable mergeStateStatus=$state)"
    fi
    sleep "$poll_seconds"
  done
}

# (4)-(7) wait each PR clean, merge it, then before touching the next PR
# re-read its state -- a base moved by the landing just ahead of it refuses
# rather than resolves.
first=true
for pr in "${prs[@]}"; do
  if [ "$first" = false ]; then
    state="$(gh_view_field "$pr" mergeStateStatus | jq -r '.mergeStateStatus')"
    if [ "$state" = "CONFLICTING" ]; then
      echo "MOVED_BASE: $pr — merge $trunk into its branch, then re-run"
      exit 5
    fi
  fi
  first=false

  wait_until_clean "$pr"

  log "merging: pr #$pr"
  "$GH" pr merge "$pr" "${repo_args[@]}" --squash --delete-branch \
    || die 4 "MERGE_FAILED: pr #$pr"

  mergeCommit="$(gh_view_field "$pr" mergeCommit | jq -r '.mergeCommit.oid // empty')"
  echo "MERGED: #$pr $mergeCommit"
done
