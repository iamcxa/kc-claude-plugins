#!/usr/bin/env bash
# CLI e2e evidence: run a flow's `Execute external` steps at a pinned SHA.
# Usage: e2e-cli.sh <sha> <flow.yaml>
#
# Consumes e2e-pipeline's `action: "Execute external"` / `execute.cli`
# step shape only (docs in e2e-pipeline/CLAUDE.md "Draft flow template");
# it does not call into or depend on e2e-pipeline.
#
# Exit codes: 0 every step's command exited with its declared code; 1 a
# step's command exited with an unexpected code; 2 usage/config error --
# bad args, missing flow, unparseable flow (including PyYAML unavailable),
# zero `Execute external` steps, or a step whose `expect` is not the
# recognized `exit code <N>` form. All `expect` values are validated before
# any step runs, so a config error never runs a command past it.
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

timestamp() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }

parsed_file="$(mktemp)"
parsed_err="$(mktemp)"
repo_root=""
worktree_dir=""

cleanup() {
  if [ -n "$worktree_dir" ]; then
    git -C "$repo_root" worktree remove --force "$worktree_dir" >/dev/null 2>&1 || true
  fi
  rm -f "$parsed_file" "$parsed_err"
}
trap cleanup EXIT

parser_status=0
python3 "$(dirname "$0")/parse-execute-external.py" "$flow_abs" >"$parsed_file" 2>"$parsed_err" || parser_status=$?
if [ "$parser_status" -ne 0 ]; then
  cat "$parsed_err" >&2
  echo "$(timestamp) e2e-cli: parsing $flow_abs failed (exit $parser_status)" >&2
  exit 2
fi

steps_run=()
steps_expect=()
while IFS=$'\t' read -r quoted_run quoted_expect; do
  steps_run+=("$(eval "echo $quoted_run")")
  steps_expect+=("$(eval "echo $quoted_expect")")
done < "$parsed_file"

if [ "${#steps_run[@]}" -eq 0 ]; then
  echo "$(timestamp) e2e-cli: no 'Execute external' steps found in $flow_abs" >&2
  exit 2
fi

for expect in "${steps_expect[@]}"; do
  if [[ ! "$expect" =~ ^exit\ code\ [0-9]+$ ]]; then
    echo "$(timestamp) e2e-cli: unrecognized expect '$expect' -- only 'exit code <N>' is supported" >&2
    exit 2
  fi
done

repo_root="$(git rev-parse --show-toplevel)"
worktree_dir="$(mktemp -d)"
rmdir "$worktree_dir"
git -C "$repo_root" worktree add --detach --quiet "$worktree_dir" "$sha"

echo "$(timestamp) e2e-cli: sha=$sha flow=$flow_abs worktree=$worktree_dir"

status=0
for i in "${!steps_run[@]}"; do
  step_num=$((i + 1))
  run_cmd="${steps_run[$i]}"
  expect="${steps_expect[$i]}"
  expected_code="${expect#exit code }"

  echo "$(timestamp) step $step_num: $run_cmd (expect: $expect)"
  set +e
  (cd "$worktree_dir" && eval "$run_cmd")
  actual_code=$?
  set -e

  if [ "$actual_code" -ne "$expected_code" ]; then
    echo "$(timestamp) FAIL step $step_num: '$run_cmd' exited $actual_code, expected $expected_code"
    status=1
    break
  fi
  echo "$(timestamp) PASS step $step_num: '$run_cmd' exited $actual_code"
done

echo "$(timestamp) e2e-cli: exit $status"
exit "$status"
