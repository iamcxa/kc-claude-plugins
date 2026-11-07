#!/usr/bin/env bash
# validation-2 live number-guard command, verbatim from validation-2/evidence.md
set -euo pipefail
python3 -B /tmp/adr-reservation-validation-801-r2/candidate/kc-dev-flow-2/scripts/number_guards.py check --repo /tmp/adr-reservation-validation-801-r2/live.git --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 --task /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/adr-reservation-crosses-workflows.md --base ba055b8a7a55a787ac989c4cef52d07dd75661ad --head ef3ed3e05534e2a997acbdfb055a880fde1f484a
