#!/bin/bash
# Rebuild one replay arm exactly as run on 2026-11-09.
# usage: build.sh <run dir> <kc-dev-flow-2-v0.36.0|revised> <e387a77b3 (amendment 4)|c934dfb11 (amendment 6)> <checklist file>
# Needs: PKGREPO (scratch repo with tags kc-dev-flow-2-v0.35.0, kc-dev-flow-2-v0.36.0, revised = v0.36.0 + pilot-revised.diff),
# QNOW (qnow-adopt-dev2 checkout), PKG (installed kc-dev-flow-2 0.36.0 root).
python3 "$PKG/scripts/replay_dispatch.py" build --run-dir "$1" --package-repo "$PKGREPO" --package-ref "$2" \
  --adopter-readme "$QNOW/docs/dev2/README.md" --readme-base-ref kc-dev-flow-2-v0.35.0 \
  --state-repo "$QNOW/docs/dev2/.spacedock-state" --state-commit "$3" --task owner-vehicle-kept-after-name \
  --code-repo "$QNOW" --code-commit 232344ce0b012c0b8899a3525d1707de7c4a8500 --stage ideation \
  --checklist "$4" --scope "$(dirname "$0")/scope.txt" --spacedock "$(command -v spacedock)"
# then: RUN_ROOT=<parent of run dir> run-codex.sh <run id>; extract.sh <run dir> <state commit> <out>; score.sh <out> <json>
