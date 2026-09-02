#!/usr/bin/env bash
# CLI e2e evidence: run a flow's `Execute external` steps at a pinned SHA.
# Usage: e2e-cli.sh <sha> <flow.yaml>
#
# Consumes e2e-pipeline's `action: "Execute external"` / `execute.cli`
# step shape only (docs in e2e-pipeline/CLAUDE.md "Draft flow template");
# it does not call into or depend on e2e-pipeline.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: e2e-cli.sh <sha> <flow.yaml>" >&2
  exit 2
fi

sha="$1"
flow="$2"
flow_abs="$(cd "$(dirname "$flow")" && pwd)/$(basename "$flow")"

if [ ! -f "$flow_abs" ]; then
  echo "e2e-cli: flow file not found: $flow_abs" >&2
  exit 2
fi

repo_root="$(git rev-parse --show-toplevel)"
worktree_dir="$(mktemp -d)"
rmdir "$worktree_dir"

cleanup() {
  git -C "$repo_root" worktree remove --force "$worktree_dir" >/dev/null 2>&1 || true
}
trap cleanup EXIT

git -C "$repo_root" worktree add --detach --quiet "$worktree_dir" "$sha"

timestamp() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }

echo "$(timestamp) e2e-cli: sha=$sha flow=$flow_abs worktree=$worktree_dir"

status=0
step_count=0
while IFS=$'\t' read -r quoted_run quoted_expect; do
  step_count=$((step_count + 1))
  run_cmd="$(eval "echo $quoted_run")"
  expect="$(eval "echo $quoted_expect")"
  expected_code="$(printf '%s' "$expect" | sed -n 's/^exit code \([0-9][0-9]*\)$/\1/p')"
  expected_code="${expected_code:-0}"

  echo "$(timestamp) step $step_count: $run_cmd (expect: $expect)"
  set +e
  (cd "$worktree_dir" && eval "$run_cmd")
  actual_code=$?
  set -e

  if [ "$actual_code" -ne "$expected_code" ]; then
    echo "$(timestamp) FAIL step $step_count: '$run_cmd' exited $actual_code, expected $expected_code"
    status=1
    break
  fi
  echo "$(timestamp) PASS step $step_count: '$run_cmd' exited $actual_code"
done < <(python3 "$(dirname "$0")/parse-execute-external.py" "$flow_abs")

if [ "$step_count" -eq 0 ]; then
  echo "$(timestamp) e2e-cli: no 'Execute external' steps found in $flow_abs" >&2
  status=1
fi

echo "$(timestamp) e2e-cli: exit $status"
exit "$status"
