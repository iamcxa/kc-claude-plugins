#!/usr/bin/env bash
# Replay the approved histories and falsifiers for the pinned implementation.
set -euo pipefail
SOURCE=${1:?pass the implementation worktree}
OUTPUT=${2:?pass a new evidence directory}
PACKAGE=${3:?pass the assigned kc-dev-flow-2 package root}
WORKFLOW=${4:?pass the adopted workflow directory}
SCRIPTS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
test "$(git -C "$SOURCE" rev-parse HEAD)" = 0a5c37f091daec6909a76d443219c655b17d534e
mkdir -p "$OUTPUT"
SCRATCH=$(mktemp -d /tmp/validation-rerun-acceptance.XXXXXX)
trap 'rm -rf -- "$SCRATCH"' EXIT
git -C "$SOURCE" archive --output="$SCRATCH/tag.tar" kc-dev-flow-2-v0.38.1 kc-dev-flow-2
mkdir "$SCRATCH/tag"
tar -xf "$SCRATCH/tag.tar" -C "$SCRATCH/tag"
while read -r key repo; do
  git clone --quiet --no-checkout --single-branch --branch spacedock-state/dev2 "https://github.com/$repo.git" "$SCRATCH/$key"
done <<'REPOS'
kcp iamcxa/kc-claude-plugins
qnow iamcxa/qnow
relay spacedock-dev/subspace-relay
web spacedock-dev/subspace-web
v0 spacedock-dev/subspace-v0
me iamcxa/me-company
REPOS
export PYTHONDONTWRITEBYTECODE=1
python3 -B "$SCRIPTS/replay.py" "$SCRATCH" "$SOURCE/kc-dev-flow-2/scripts/dispatch_records.py" "$OUTPUT/replay.json" > "$OUTPUT/replay.log" 2>&1
python3 -B "$SCRIPTS/verify_corpus.py" "$OUTPUT/replay.json" > "$OUTPUT/corpus-verification.log" 2>&1
python3 -B "$SCRIPTS/mutations.py" "$SOURCE" "$SCRATCH" "$OUTPUT" > "$OUTPUT/mutations.log" 2>&1
python3 -B "$SCRIPTS/extra_mutations.py" "$SOURCE" "$SCRATCH" "$OUTPUT" "$PACKAGE" > "$OUTPUT/extra-mutations.log" 2>&1
cd "$SOURCE"
python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p test_dispatch_records.py > "$OUTPUT/suite.log" 2>&1
python3 -B kc-dev-flow-2/scripts/lint-skills.py > "$OUTPUT/skill-lint.log" 2>&1
python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since 546a136386c94c58e430c91a6f3457b38bd73880 --require 0045 > "$OUTPUT/adr-lint.log" 2>&1
python3 -B "$PACKAGE/scripts/comment_ratio.py" 546a136386c94c58e430c91a6f3457b38bd73880 HEAD > "$OUTPUT/comment-ratio.log" 2>&1
python3 -B "$PACKAGE/scripts/number_guards.py" check --repo "$SOURCE" --workflow-dir "$WORKFLOW" --task "$WORKFLOW/.spacedock-state/validation-rerun-survives-repaired-history.md" --base 546a136386c94c58e430c91a6f3457b38bd73880 > "$OUTPUT/number-guards.log" 2>&1
python3 -B "$PACKAGE/scripts/design_surfaces.py" check "$WORKFLOW/.spacedock-state/validation-rerun-survives-repaired-history.md" > "$OUTPUT/design-surfaces.log" 2>&1
