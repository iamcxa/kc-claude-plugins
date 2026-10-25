#!/usr/bin/env bash
# Lists, by name and presence only, every credential-shaped source reachable from this process besides the model
# credential (names in AUDIT_ALLOW, default CLAUDE_CODE_OAUTH_TOKEN ANTHROPIC_API_KEY) and the Hub-minted GitHub token (GH_TOKEN
# plus the git configuration Hub sets in the step environment). Prints no value. Exit 1 when any other source exists.
set -uo pipefail
ALLOW="${AUDIT_ALLOW:-CLAUDE_CODE_OAUTH_TOKEN ANTHROPIC_API_KEY}"
PASEO_HOME_DIR="${PASEO_HOME:-$HOME/.paseo}"
bad=0
note() { echo "$1"; bad=1; }

for v in $(env | cut -d= -f1 | grep -E 'TOKEN|SECRET|PASSWORD|_KEY$|GH_|GITHUB_|SSH_AUTH_SOCK|GIT_ASKPASS|GIT_CONFIG|API|CREDENTIAL' | sort); do
  echo "$v" | grep -Eq "^(GH_TOKEN|GIT_CONFIG_.*|GIT_TERMINAL_PROMPT$(for n in $ALLOW; do printf '|%s' "$n"; done))$" || note "env $v present"
done
[ -n "$(git config --show-origin --get-all credential.helper 2>/dev/null | grep -v -F 'gh auth git-credential' | grep -v -E 'command line:[[:space:]]*$')" ] && note "git credential.helper present (not gh)"
[ -s "${GH_CONFIG_DIR:-$HOME/.config/gh}/hosts.yml" ] && note "gh login file present"
ls "$HOME"/.ssh/id_* >/dev/null 2>&1 && note "ssh private key present"
[ -f "$HOME/.netrc" ] && note ".netrc present"
[ -f "$PASEO_HOME_DIR/hub-relationship.json" ] && note "daemon Hub relationship credential present: $PASEO_HOME_DIR/hub-relationship.json (readable by uid $(id -u))"
for f in "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.credentials.json" "$HOME/.claude.json" "${CODEX_HOME:-$HOME/.codex}/auth.json"; do
  [ -s "$f" ] && grep -Eq 'oauth|accessToken|refresh|api[_-]?key|OPENAI' "$f" 2>/dev/null && note "provider login file present: $f"
done
[ -S /var/run/docker.sock ] && note "docker socket present"
if [ "$bad" = 0 ]; then echo "no credential source besides the model credential and the Hub-provided GitHub token"; fi
exit "$bad"
