#!/usr/bin/env bash
# Create the empty state branch spacedock-state/ops in the project repository.
# usage: make-state-branch.sh <owner/name>   (env OPS_GIT_BASE overrides https://github.com for a rehearsal)
set -euo pipefail
P=${1:?usage: make-state-branch.sh <owner/name>}
BASE=${OPS_GIT_BASE:-https://github.com}
T=$(mktemp -d)
git clone -q --depth 1 "$BASE/$P.git" "$T/p"
cd "$T/p"
ROOT=$(GIT_AUTHOR_NAME=ops GIT_AUTHOR_EMAIL=ops@users.noreply.github.com GIT_COMMITTER_NAME=ops GIT_COMMITTER_EMAIL=ops@users.noreply.github.com \
  git commit-tree "$(git hash-object -t tree -w /dev/null)" -m "ops state root")
git push origin "$ROOT:refs/heads/spacedock-state/ops"
echo "created spacedock-state/ops at $ROOT"
