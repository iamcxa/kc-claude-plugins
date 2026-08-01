#!/usr/bin/env bash

set -u

usage() {
  echo "Usage: watch-pr-checks.sh <pr-number-or-url> [--repo <owner/repo>]" >&2
}

PR="${1:-}"
if [[ -z "$PR" ]]; then
  usage
  exit 2
fi
shift

REPO_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      [[ -n "${2:-}" ]] || { usage; exit 2; }
      REPO_ARGS=(--repo "$2")
      shift 2
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

command -v gh >/dev/null 2>&1 || {
  echo "CI watch: gh CLI is required" >&2
  exit 2
}

HEAD_BEFORE="$(gh pr view "$PR" "${REPO_ARGS[@]}" --json headRefOid --jq .headRefOid)" || {
  echo "CI watch: unable to resolve the PR head" >&2
  exit 1
}
[[ -n "$HEAD_BEFORE" ]] || {
  echo "CI watch: PR head is empty" >&2
  exit 1
}

if ! gh pr checks "$PR" "${REPO_ARGS[@]}" --watch --fail-fast; then
  echo "CI watch: checks failed for head $HEAD_BEFORE" >&2
  exit 1
fi

HEAD_AFTER="$(gh pr view "$PR" "${REPO_ARGS[@]}" --json headRefOid --jq .headRefOid)" || {
  echo "CI watch: unable to re-read the PR head" >&2
  exit 1
}
if [[ "$HEAD_BEFORE" != "$HEAD_AFTER" ]]; then
  echo "CI watch: PR head moved from $HEAD_BEFORE to $HEAD_AFTER; rerun the gate" >&2
  exit 1
fi

echo "CI watch: PASS at exact head $HEAD_AFTER"
