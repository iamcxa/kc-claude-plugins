#!/usr/bin/env bash
# Minimal-necessity without-it check: run one command retained, then again
# after a removed-variant is applied, and compare exit codes.
# Usage: without-it.sh <sha> <command> <removed-variant>
#
# <command> and <removed-variant> are each a single self-contained shell
# line, evaluated inside a worktree checked out at <sha>. <removed-variant>
# is expected to remove the candidate change (e.g. a `git checkout <base-sha>
# -- <file>` that restores the pre-change content) before <command> runs a
# second time.
#
# <command> runs with LINEAR_API_KEY, GH_TOKEN, GITHUB_TOKEN,
# CONDUCTOR_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY, and CODEX_API_KEY
# stripped from its environment (PATH, HOME, and TMPDIR are kept -- the
# contract test needs HOME). The worktree is reset to a clean checkout of
# <sha> before the removed-variant is applied and again after the removed
# run, so a mutation the retained run left behind (a written file, a staged
# change) cannot leak into the removed run or the caller.
#
# Exit codes: 0 retained passed (exit 0) and removed failed (exit != 0);
# 1 retained failed, or removed also passed -- the command does not
# distinguish the two variants; 2 usage error.
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: without-it.sh <sha> <command> <removed-variant>" >&2
  exit 2
fi

sha="$1"
command_line="$2"
removed_variant="$3"

timestamp() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }

run_stripped() {
  env -u LINEAR_API_KEY -u GH_TOKEN -u GITHUB_TOKEN -u CONDUCTOR_API_KEY \
    -u ANTHROPIC_API_KEY -u OPENAI_API_KEY -u CODEX_API_KEY \
    bash -c "$1"
}

reset_worktree() {
  git -C "$worktree_dir" checkout -q "$sha" -- .
  git -C "$worktree_dir" clean -fdq
}

repo_root="$(git rev-parse --show-toplevel)"
worktree_dir="$(mktemp -d)"
rmdir "$worktree_dir"

cleanup() {
  git -C "$repo_root" worktree remove --force "$worktree_dir" >/dev/null 2>&1 || true
}
trap cleanup EXIT

git -C "$repo_root" worktree add --detach --quiet "$worktree_dir" "$sha"

echo "$(timestamp) without-it: sha=$sha worktree=$worktree_dir"

set +e
(cd "$worktree_dir" && run_stripped "$command_line")
retained_code=$?
set -e
echo "$(timestamp) retained: '$command_line' exited $retained_code"

reset_worktree

set +e
(cd "$worktree_dir" && eval "$removed_variant")
removed_variant_code=$?
set -e
if [ "$removed_variant_code" -ne 0 ]; then
  echo "$(timestamp) without-it: removed-variant '$removed_variant' exited $removed_variant_code" >&2
  exit 2
fi

set +e
(cd "$worktree_dir" && run_stripped "$command_line")
removed_code=$?
set -e
echo "$(timestamp) removed: '$command_line' exited $removed_code"

reset_worktree

if [ "$retained_code" -eq 0 ] && [ "$removed_code" -ne 0 ]; then
  echo "$(timestamp) without-it: PASS (retained=$retained_code removed=$removed_code)"
  exit 0
fi
echo "$(timestamp) without-it: FAIL (retained=$retained_code removed=$removed_code)"
exit 1
