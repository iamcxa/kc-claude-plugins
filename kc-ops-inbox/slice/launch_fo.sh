#!/usr/bin/env bash
# Launch the headless First Officer. env: PROMPT, optional FO_MAX_BUDGET_USD and FO_CLAUDE_EXTRA (extra claude args).
# The variadic options are name=value so they cannot swallow the task prompt that spacedock appends.
set -euo pipefail
# shellcheck disable=SC2086
exec spacedock claude "${PROMPT:?}" -- -p \
  --allowedTools="Bash(spacedock:*) Bash(git:*) Bash(gh pr create:*) Bash(ls:*) Bash(cat:*) Read Write Edit Grep Glob Agent Skill SendMessage" \
  --add-dir=/tmp/spacedock-dispatch --model sonnet --max-budget-usd "${FO_MAX_BUDGET_USD:-5}" \
  --permission-mode acceptEdits --permission-prompts none ${FO_CLAUDE_EXTRA:-}
