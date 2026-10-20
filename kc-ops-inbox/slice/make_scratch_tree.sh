#!/usr/bin/env bash
# Assemble the file tree committed to the scratch repository. usage: make_scratch_tree.sh OUT_DIR
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/.." && pwd); OUT=${1:?}
mkdir -p "$OUT/docs/ops" "$OUT/.github/workflows" "$OUT/slice" "$OUT/github-probe"
cp "$ROOT/ops-workflow/README.md" "$OUT/docs/ops/README.md"
cp "$HERE/workflows/ops-fo.yml" "$HERE/workflows/ops-gate.yml" "$OUT/.github/workflows/"
cp "$HERE/run_fo.sh" "$HERE/launch_fo.sh" "$HERE/verify_slice.sh" "$HERE/record_gate_from_review.sh" "$HERE/fo-prompt.md" "$HERE/fixture-event.json" "$OUT/slice/"
cp "$ROOT/github-probe/askpass.sh" "$ROOT/github-probe/credential_audit.sh" "$OUT/github-probe/"
