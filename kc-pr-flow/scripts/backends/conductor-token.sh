#!/bin/bash
# Store a Conductor API token for one GitHub organization.
#
# A Conductor token is scoped to a single organization, and the CLI takes no
# organization argument, so reviewing repos in a second organization needs a
# second token. The keychain token (conductor auth login) serves the default
# organization and needs no file here.
#
# Reads the token from a hidden prompt so it never reaches a shell history, a
# process list, an agent transcript, or a log. Refuses to run unattended for the
# same reason.

set -uo pipefail

CONDUCTOR="${CONDUCTOR:-$HOME/Library/Application Support/com.conductor.app/bin/conductor}"
CFG_DIR="${PR_LISTEN_CFG_DIR:-$HOME/.claude/kc-plugins-config/pr-flow}"

die() { printf '%s\n' "$*" >&2; exit 1; }

ORG_RAW="${1:-}"
[[ -n "$ORG_RAW" ]] || die "usage: conductor-token.sh <github-org>   (e.g. the owner in owner/repo)"
[[ -t 0 ]] || die "refusing to read a token from a pipe — run this in a terminal"
[[ -x "$CONDUCTOR" ]] || die "conductor CLI not found at $CONDUCTOR"

ORG=$(printf '%s' "$ORG_RAW" | tr '[:upper:]' '[:lower:]')
DEST="$CFG_DIR/orgs/$ORG.env"

if [[ -f "$DEST" ]]; then
  printf 'A token for %s already exists. Replace it? [y/N] ' "$ORG"
  read -r reply
  [[ "$reply" == [yY]* ]] || die "unchanged"
fi

printf 'Conductor API token for %s (input hidden): ' "$ORG"
IFS= read -rs TOKEN
printf '\n'
[[ -n "$TOKEN" ]] || die "no token entered"

# Verify before writing, so a typo fails here instead of at the first dispatch.
WHOAMI=$(CONDUCTOR_API_TOKEN="$TOKEN" "$CONDUCTOR" auth whoami 2>&1) || true
grep -q 'authenticated' <<<"$WHOAMI" || die "token rejected — nothing written. $(grep -i verification <<<"$WHOAMI" | head -1)"

ORG_ID=$(awk '/^Organization ID/{print $3}' <<<"$WHOAMI")

mkdir -p "$CFG_DIR/orgs"
(
  umask 077
  printf '# Conductor token for GitHub org: %s\n' "$ORG" >"$DEST"
  printf 'CONDUCTOR_API_TOKEN=%s\n' "$TOKEN" >>"$DEST"
)
chmod 600 "$DEST"

printf 'Stored.\n'
printf '  file          %s (mode 600)\n' "$DEST"
printf '  token length  %d chars\n' "${#TOKEN}"
printf '  organization  %s\n' "${ORG_ID:-unknown}"
printf '\nThe listener loads this automatically for any %s/* repository.\n' "$ORG"
