#!/usr/bin/env bash
# Run the ops First Officer once on a GitHub-hosted runner (or locally with FO_LAUNCH set for rehearsal).
# env: OPS_APP_TOKEN (App installation token), REPO (owner/name), EVENT_FILE (repo-relative path),
#      one of ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN. Prints no credential value.
set -euo pipefail
: "${OPS_APP_TOKEN:?}" "${REPO:?}" "${EVENT_FILE:?}"
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)   # parent of slice/ and github-probe/
MODEL_VAR=ANTHROPIC_API_KEY; [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ] && MODEL_VAR=CLAUDE_CODE_OAUTH_TOKEN
FO_HOME=$(mktemp -d)
SLUG="relay-$(python3 -I -c 'import json,sys;d=json.load(open(sys.argv[1]));print(d["event"]+"-"+d["day"])' "$ROOT/$EVENT_FILE")"
REMOTE=${REMOTE_URL:-https://github.com/$REPO.git}

echo "== job environment, credential-shaped names only"
env | cut -d= -f1 | grep -E 'TOKEN|SECRET|PASSWORD|_KEY$' | sort | sed 's/^/  /'

if [ -z "${FO_LAUNCH:-}" ]; then
  echo "== install"
  curl -fsSL https://raw.githubusercontent.com/spacedock-dev/spacedock/main/install.sh | HOME="$FO_HOME" sh
  npm config set prefix "$FO_HOME/npm" && npm install -g @anthropic-ai/claude-code@2.1.303 >/dev/null
  export PATH="$FO_HOME/.local/bin:$FO_HOME/npm/bin:$PATH"
  spacedock --version; claude --version
  HOME="$FO_HOME" spacedock install --host claude && HOME="$FO_HOME" spacedock doctor --host claude
fi

cleanenv=(env -i PATH="$PATH" HOME="$FO_HOME" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0
  GIT_ASKPASS="$ROOT/github-probe/askpass.sh" PROBE_TOKEN="$OPS_APP_TOKEN" GH_TOKEN="$OPS_APP_TOKEN"
  "$MODEL_VAR=${!MODEL_VAR:-}" AUDIT_ALLOW="PROBE_TOKEN GH_TOKEN $MODEL_VAR")

"${cleanenv[@]}" sh -c "command -v spacedock" >/dev/null || { echo "spacedock is not on the First Officer PATH" >&2; exit 1; }
mkdir -p /tmp/spacedock-dispatch
WORK=$(mktemp -d)
"${cleanenv[@]}" git clone -q "$REMOTE" "$WORK/repo"
cd "$WORK/repo"
git config user.email "ops-fo@example.invalid"; git config user.name "ops-first-officer"

echo "== credential audit inside the First Officer's environment"
"${cleanenv[@]}" bash "$ROOT/github-probe/credential_audit.sh"

PROMPT=$(sed -e "s|__SLUG__|$SLUG|g" -e "s|__EVENT_FILE__|$EVENT_FILE|g" "$ROOT/slice/fo-prompt.md")
echo "== launch First Officer"
if [ -n "${FO_LAUNCH:-}" ]; then
  "${cleanenv[@]}" env SLUG="$SLUG" "$FO_LAUNCH"
else
  "${cleanenv[@]}" spacedock claude "$PROMPT" -- -p --model sonnet --max-budget-usd "${FO_MAX_BUDGET_USD:-5}" --permission-mode acceptEdits --permission-prompts none \
    --allowedTools "Bash(spacedock:*) Bash(git:*) Bash(gh pr create:*) Bash(ls:*) Bash(cat:*) Read Write Edit Grep Glob Agent Skill SendMessage" --add-dir /tmp/spacedock-dispatch
fi

echo "== verify"
OWNER_REPO="$REPO" SLUG="$SLUG" "$ROOT/slice/verify_slice.sh"
