#!/usr/bin/env bash
set -euo pipefail
EVIDENCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$EVIDENCE_DIR/acceptance.py" "${1:?code worktree}" "${2:?state checkout}" "${3:?kc-dev-flow-2 package}" "${4:?Spacedock package}"
