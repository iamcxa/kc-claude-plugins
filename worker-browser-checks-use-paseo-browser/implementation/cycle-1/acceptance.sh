#!/usr/bin/env bash
set -euo pipefail
TASK_WORKTREE=${1:?usage: bash acceptance.sh /absolute/candidate/worktree}
EVIDENCE_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
python3 -B "$EVIDENCE_DIR/acceptance.py" "$TASK_WORKTREE" 139feeaee7ce037a0c6535568cd6bd103155cbae 90192bb64db4614de9a7a94cc782ee5fa44748db "$EVIDENCE_DIR"
