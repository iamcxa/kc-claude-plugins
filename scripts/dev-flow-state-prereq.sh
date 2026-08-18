#!/usr/bin/env bash
# Refuse to act on split-root workflow state from a workspace that does not hold
# the state checkout.
#
# Conductor runs many workspaces against one repository, and only one of them
# holds `<workflow>/.spacedock-state`. In the others the path is an ignored
# directory, and the degradation is silent to the end of the useful window:
# `spacedock new` reports created, `spacedock status` reads the entity back, and
# only `spacedock state commit` fails. An entity filed in that window exists
# nowhere but that workspace.
#
# The binary cannot currently tell the two apart -- `status` returns 0 and an
# empty table for a non-holder, which is what a healthy empty workflow returns.
# Reported upstream as spacedock-dev/spacedock#630; when that lands this file
# becomes a thin wrapper or goes away.
#
# This lived as 76 lines of shell inside docs/dev/README.md, where it could not
# be run as written, could not be tested, and could not fail. It already had
# exit codes; it was a program in a document.
#
# Usage: dev-flow-state-prereq.sh [workflow-dir]     (default: <repo>/docs/dev)
#
#   0   holder, clean, and equal to the observed remote tip
#   1   could not establish the repository, workflow, or holder
#   75  holder is dirty
#   76  holder is clean but local-ahead
#   77  holder and remote state diverged
#
# 75/76/77 each enter docs/dev/runbooks/state-recovery.md and must rerun this
# check to observed equality before normal lifecycle work resumes.
set -uo pipefail

REPO_DISCOVERED=$(git rev-parse --show-toplevel) || exit 1
REPO=$(cd "$REPO_DISCOVERED" && pwd -P) || exit 1
WORKFLOW_LITERAL="${1:-$REPO/docs/dev}"
WORKFLOW_DIR=$(cd "$WORKFLOW_LITERAL" && pwd -P) || exit 1
test "$WORKFLOW_DIR" = "$WORKFLOW_LITERAL" || exit 1
STATE="$WORKFLOW_DIR/.spacedock-state"

WORKTREES=$(git -C "$REPO" worktree list --porcelain) || exit 1
HOLDERS=$(printf '%s\n' "$WORKTREES" | awk '
  BEGIN { RS=""; FS="\n" }
  {
    path=""; branch=""
    for (i = 1; i <= NF; i++) {
      if ($i ~ /^worktree /) path=substr($i, 10)
      if ($i ~ /^branch /) branch=substr($i, 8)
    }
    if (branch == "refs/heads/spacedock-state/dev") print path
  }
')
HOLDER_COUNT=$(printf '%s\n' "$HOLDERS" |
  awk 'NF { count++ } END { print count + 0 }') || exit 1
if test "$HOLDER_COUNT" -ne 1 || test "$HOLDERS" != "$STATE"; then
  echo "lifecycle requires the registered state holder: ${HOLDERS:-<none>}" >&2
  exit 1
fi
if test -L "$STATE"; then
  echo "lifecycle state path must not be a symlink: $STATE" >&2
  exit 1
fi

STATE_TOP_DISCOVERED=$(git -C "$STATE" rev-parse --show-toplevel) || exit 1
STATE_TOP=$(cd "$STATE_TOP_DISCOVERED" && pwd -P) || exit 1
REPO_COMMON_DISCOVERED=$(git -C "$REPO" rev-parse \
  --path-format=absolute --git-common-dir) || exit 1
REPO_COMMON=$(cd "$REPO_COMMON_DISCOVERED" && pwd -P) || exit 1
STATE_COMMON_DISCOVERED=$(git -C "$STATE" rev-parse \
  --path-format=absolute --git-common-dir) || exit 1
STATE_COMMON=$(cd "$STATE_COMMON_DISCOVERED" && pwd -P) || exit 1
test "$STATE_TOP" = "$STATE" || exit 1
test "$STATE_COMMON" = "$REPO_COMMON" || exit 1
STATE_BRANCH=$(git -C "$STATE" symbolic-ref --quiet --short HEAD) || exit 1
test "$STATE_BRANCH" = spacedock-state/dev || exit 1
STATE_REF=refs/heads/spacedock-state/dev
git -C "$STATE" fetch --no-tags origin "$STATE_REF" || exit 1
REMOTE_TIP=$(git -C "$STATE" rev-parse 'FETCH_HEAD^{commit}') || exit 1
LOCAL_HEAD=$(git -C "$STATE" rev-parse 'HEAD^{commit}') || exit 1
if test "$LOCAL_HEAD" = "$REMOTE_TIP"; then
  STATE_RELATION=equal
elif git -C "$STATE" merge-base --is-ancestor "$REMOTE_TIP" "$LOCAL_HEAD"; then
  STATE_RELATION=ahead
elif git -C "$STATE" merge-base --is-ancestor "$LOCAL_HEAD" "$REMOTE_TIP"; then
  STATE_RELATION=behind
else
  STATE_RELATION=diverged
fi
STATE_DIRTY=$(git -C "$STATE" status --porcelain) || exit 1
if test -n "$STATE_DIRTY"; then
  echo "dirty holder ($STATE_RELATION); run attributable recovery" >&2
  exit 75
fi
case "$STATE_RELATION" in
  equal) ;;
  behind)
    git -C "$STATE" merge --ff-only "$REMOTE_TIP" || exit 1
    test "$(git -C "$STATE" rev-parse 'HEAD^{commit}')" = "$REMOTE_TIP" ||
      exit 1
    ;;
  ahead)
    echo "holder has unpushed commits; run outgoing recovery" >&2
    exit 76
    ;;
  diverged)
    echo "holder and remote state diverged; run outgoing recovery" >&2
    exit 77
    ;;
esac
