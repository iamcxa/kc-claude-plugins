#!/usr/bin/env bash
set -euo pipefail
TASK_WORKTREE=${1:?usage: bash acceptance.sh /absolute/candidate/worktree}
EVIDENCE_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
python3 -B "$EVIDENCE_DIR/acceptance.py" "$TASK_WORKTREE" 139feeaee7ce037a0c6535568cd6bd103155cbae fef21735308e7e807d04a93a5506de5284dde436 "$EVIDENCE_DIR"
