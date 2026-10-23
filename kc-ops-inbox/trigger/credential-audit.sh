#!/usr/bin/env bash
# List, by name and presence only, every credential-shaped source in this process besides OPS_GIT_TOKEN
# and the names in AUDIT_ALLOW (space-separated).
# Exit 1 when any other source exists. Prints no value.
set -uo pipefail
bad=0
note() { echo "$1"; [ "$2" = present ] && bad=1; }
for v in $(env | cut -d= -f1 | grep -E 'TOKEN|SECRET|PASSWORD|_KEY$|GH_|GITHUB_|SSH_AUTH_SOCK|GIT_ASKPASS|GIT_CONFIG' | grep -vxE "OPS_GIT_TOKEN|TOKEN_FILE|GIT_ASKPASS|GIT_CONFIG_GLOBAL|GIT_CONFIG_NOSYSTEM|GIT_CONFIG_COUNT|GIT_CONFIG_KEY_[0-9]+|GIT_CONFIG_VALUE_[0-9]+|OPS_CREDENTIAL_HELPER$(for n in ${AUDIT_ALLOW:-}; do printf '|%s' "$n"; done)" | sort); do
  note "env $v present" present
done
[ -n "$(git config --show-origin --get-all credential.helper 2>/dev/null | grep -v -F -e "${OPS_CREDENTIAL_HELPER:-/nonexistent}" | grep -v -E "command line:[[:space:]]*$")" ] && note "git credential.helper present" present
[ -s "${GH_CONFIG_DIR:-$HOME/.config/gh}/hosts.yml" ] && note "gh login file present" present
ls "$HOME"/.ssh/id_* >/dev/null 2>&1 && note "ssh private key present" present
[ -f "$HOME/.netrc" ] && note ".netrc present" present
[ "$bad" = 0 ] && echo "no other GitHub credential source found"
exit "$bad"
