#!/usr/bin/env bash
# Run the ops First Officer once, headless, in a clean environment that holds only the project token and the model token.
# env: PROMPT, PROJECT_DIR, OPS_GIT_TOKEN (project-scoped App token), one of CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY,
#      PATH with spacedock and claude. Prints no credential value.
set -euo pipefail
: "${PROMPT:?}" "${PROJECT_DIR:?}" "${OPS_GIT_TOKEN:?}"
HERE=$(cd "$(dirname "$0")" && pwd)
MODEL_VAR=ANTHROPIC_API_KEY; [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ] && MODEL_VAR=CLAUDE_CODE_OAUTH_TOKEN
FO_HOME=$(mktemp -d)
ASKPASS="$FO_HOME/askpass"
printf '#!/bin/sh\ncase "$1" in Username*) echo x-access-token ;; *) echo "$OPS_GIT_TOKEN" ;; esac\n' > "$ASKPASS"; chmod 700 "$ASKPASS"

clean=(env -i PATH="$PATH" HOME="$FO_HOME" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0
  GIT_ASKPASS="$ASKPASS" OPS_GIT_TOKEN="$OPS_GIT_TOKEN" GH_TOKEN="$OPS_GIT_TOKEN" "$MODEL_VAR=${!MODEL_VAR:-}"
  AUDIT_ALLOW="OPS_GIT_TOKEN GH_TOKEN $MODEL_VAR")

"${clean[@]}" spacedock install --host claude
"${clean[@]}" spacedock doctor --host claude
cd "$PROJECT_DIR"
echo "== credential audit inside the First Officer's environment"
"${clean[@]}" bash "$HERE/credential-audit.sh"
echo "== launch First Officer"
"${clean[@]}" spacedock claude "$PROMPT" -- -p \
  --allowedTools="Bash(spacedock:*) Bash(git:*) Bash(ls:*) Bash(cat:*) Read Write Edit Grep Glob Agent Skill SendMessage" \
  --add-dir=/tmp/spacedock-dispatch --model sonnet --max-budget-usd "${FO_MAX_BUDGET_USD:-5}" \
  --permission-mode acceptEdits --permission-prompts none
